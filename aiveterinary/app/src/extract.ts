import { ClinicalRecord, type PatientHeader } from './schema.js';
import { findAbbreviations, normalizeNotes, detectLanguage } from './normalize.js';

/**
 * Extraction: notes → ClinicalRecord. Behind an interface so the eval harness,
 * tests and the UI don't care which model (or fixture) produced the record.
 */
export interface Extractor {
  readonly name: string;
  extract(input: ExtractInput): Promise<ExtractResult>;
}
export type ExtractInput = { notes: string; header: PatientHeader; language?: string; abbreviations?: Record<string, string> };
export type ExtractResult = { record: ClinicalRecord; raw: unknown; model: string; usage?: { input_tokens: number; output_tokens: number; cache_read_input_tokens?: number; cost_usd?: number } };

export const PROMPT_VERSION = 'extract-v1';

export function systemPrompt(): string {
  return `You convert a veterinarian's rough consultation notes into a structured clinical record (ClinicalRecord v0.2).

Absolute rules:
1. Use ONLY information present in the notes. Never add a drug, dose, route, frequency, duration, number, test result, diagnosis or finding that the vet did not write. If something is implied but not written, leave the field null and list it under "missing" with a short reason.
2. Every item must carry "source_spans": [[start, end], ...] character offsets into the notes exactly as given (0-based, end exclusive). Spans must cover the text the item came from. An item with no supporting text must not exist.
3. Mark who said it: "owner_reported" for history the owner gave, "vet_observed" for examination findings, "vet_stated" for the vet's own statements. Mark status: planned, performed, declined, recommended, dispensed, prescribed. Never turn a plan into something performed.
4. Patient species, sex and neuter status come from the patient header supplied separately; only fill patient fields in the record if the notes state them, and never contradict the header. If the notes mention pregnancy, heat, or another animal, consider that it may refer to the owner or another pet and put it under "uncertain" rather than the patient.
5. Medication: structured fields only. "antiemetic" without a drug name → class_as_written: "antiemetic", drug: null, and a "missing" entry for the drug. Numbers in doses must appear verbatim in the notes.
6. Abbreviations: expand only using the supplied abbreviation hints or unambiguous standard veterinary usage. If an abbreviation is unclear, keep the original text and add an "uncertain" entry.
7. Do not diagnose. "assessment.text" is filled only when the vet wrote an assessment or diagnosis. Never propose differentials the vet did not write.
8. Keep wording close to the notes. Write in the language of the notes.
9. Output nothing but the JSON record.`;
}

export function userPrompt(input: ExtractInput): string {
  const notes = normalizeNotes(input.notes);
  const abbr = findAbbreviations(notes, input.abbreviations);
  const lang = input.language ?? detectLanguage(notes);
  return [
    `Patient header (authoritative): ${JSON.stringify(input.header)}`,
    `Language of notes: ${lang}`,
    abbr.length ? `Abbreviation hints (index → meaning): ${abbr.map((a) => `${a.abbr}@${a.index}=${a.meaning}`).join('; ')}` : 'Abbreviation hints: none',
    'Notes (offsets refer to this exact text):',
    '<notes>',
    notes,
    '</notes>',
  ].join('\n');
}

/** Extractor backed by fixture records (tests and offline eval). */
export class FixtureExtractor implements Extractor {
  readonly name = 'fixture';
  constructor(private fixtures: Record<string, unknown>) {}
  async extract(input: ExtractInput): Promise<ExtractResult> {
    const key = input.notes; const raw = this.fixtures[key];
    if (!raw) throw new Error('No fixture for these notes');
    return { record: ClinicalRecord.parse(raw), raw, model: 'fixture' };
  }
}

/* ------------------------------------------------------------------ */
/* Guards: spend cap and concurrency. Both live in the process that calls */
/* the model, so a runaway loop or a burst of requests cannot run up a    */
/* bill or trip rate limits.                                              */

/** USD per million tokens. Cache writes cost 1.25x input, cache reads 0.1x. Update when prices change. */
export const PRICES: Record<string, { input: number; output: number; cacheWrite: number; cacheRead: number }> = {
  'claude-opus-5-5': { input: 4, output: 20, cacheWrite: 5, cacheRead: 0.2 },
  'claude-opus-5': { input: 5, output: 25, cacheWrite: 6.25, cacheRead: 0.5 },
  'claude-opus-4-8': { input: 5, output: 25, cacheWrite: 6.25, cacheRead: 0.5 },
};

export type Usage = { input_tokens: number; output_tokens: number; cache_creation_input_tokens?: number | null; cache_read_input_tokens?: number | null };

export function costUsd(model: string, u: Usage): number {
  const p = PRICES[model] ?? PRICES['claude-opus-5'];
  return ((u.input_tokens ?? 0) * p.input + (u.output_tokens ?? 0) * p.output + (u.cache_creation_input_tokens ?? 0) * p.cacheWrite + (u.cache_read_input_tokens ?? 0) * p.cacheRead) / 1e6;
}

export class SpendLimitReached extends Error {
  constructor(public spentUsd: number, public limitUsd: number) { super(`Spend limit reached: $${spentUsd.toFixed(4)} of $${limitUsd.toFixed(2)}.`); }
}

/** Running total of what this process has spent; refuses new calls once the limit is reached. */
export class SpendGuard {
  spentUsd = 0;
  constructor(readonly limitUsd: number) {}
  assertRoom(): void { if (this.spentUsd >= this.limitUsd) throw new SpendLimitReached(this.spentUsd, this.limitUsd); }
  add(model: string, u: Usage): number { const c = costUsd(model, u); this.spentUsd += c; return c; }
}

/** At most `max` requests in flight; the rest wait their turn. */
export class Limiter {
  private active = 0; private queue: (() => void)[] = [];
  constructor(readonly max: number) {}
  async run<T>(fn: () => Promise<T>): Promise<T> {
    if (this.active >= this.max) await new Promise<void>((r) => this.queue.push(r));
    this.active++;
    try { return await fn(); } finally { this.active--; this.queue.shift()?.(); }
  }
}

export class ExtractionRefused extends Error {
  constructor(public category: string | null, public explanation: string | null) { super(`The model declined to structure these notes${category ? ` (${category})` : ''}.`); }
}
export class ExtractionIncomplete extends Error {
  constructor(public stopReason: string) { super(`The model stopped before finishing the record (${stopReason}).`); }
}

/**
 * Claude adapter. Loaded lazily so the package works without the SDK or a key.
 *
 * - Model: Claude Opus 5.5 by default (AIVET_MODEL overrides). Thinking is always on for this model;
 *   effort is set explicitly to "high" because extraction quality is what the product sells.
 * - Refusals: server-side fallback ("default") re-runs a declined request on Anthropic's recommended
 *   model inside the same call; a refusal that survives the chain raises ExtractionRefused.
 * - Output: structured output validated against the ClinicalRecord schema; a response cut off by
 *   max_tokens raises instead of returning a partial record.
 * - Cost: the system prompt is marked for caching; every call is priced and added to the SpendGuard,
 *   which refuses new calls past AIVET_MAX_USD (default $5 per process).
 * - Load: at most AIVET_MAX_CONCURRENT requests in flight (default 4); the SDK retries 429/5xx.
 */
export class ClaudeExtractor implements Extractor {
  readonly name = 'claude';
  readonly guard: SpendGuard;
  private limiter: Limiter;
  constructor(
    private model = process.env.AIVET_MODEL ?? 'claude-opus-5-5',
    opts: { maxUsd?: number; maxConcurrent?: number; effort?: 'low' | 'medium' | 'high' | 'xhigh' | 'max' } = {},
  ) {
    this.guard = new SpendGuard(opts.maxUsd ?? Number(process.env.AIVET_MAX_USD ?? 5));
    this.limiter = new Limiter(opts.maxConcurrent ?? Number(process.env.AIVET_MAX_CONCURRENT ?? 4));
    this.effort = opts.effort ?? 'high';
  }
  private effort: 'low' | 'medium' | 'high' | 'xhigh' | 'max';

  async extract(input: ExtractInput): Promise<ExtractResult> {
    this.guard.assertRoom();
    const [{ default: Anthropic }, { betaZodOutputFormat }] = await Promise.all([import('@anthropic-ai/sdk'), import('@anthropic-ai/sdk/helpers/beta/zod')]);
    const client = new Anthropic({ maxRetries: 3, timeout: 180_000 });
    const response = await this.limiter.run(() => client.beta.messages.parse({
      model: this.model,
      max_tokens: 16000,
      betas: ['server-side-fallback-2026-07-01'],
      fallbacks: 'default',
      system: [{ type: 'text', text: systemPrompt(), cache_control: { type: 'ephemeral' } }],
      messages: [{ role: 'user', content: userPrompt(input) }],
      output_config: { effort: this.effort, format: betaZodOutputFormat(ClinicalRecord) },
    }));
    const servedBy = response.model;
    const cost = this.guard.add(servedBy, response.usage);
    if (response.stop_reason === 'refusal') throw new ExtractionRefused(response.stop_details?.category ?? null, response.stop_details?.explanation ?? null);
    if (response.stop_reason !== 'end_turn') throw new ExtractionIncomplete(String(response.stop_reason));
    if (!response.parsed_output) throw new Error('Model output did not match the record schema');
    return {
      record: response.parsed_output,
      raw: response.parsed_output,
      model: servedBy,
      usage: { input_tokens: response.usage.input_tokens, output_tokens: response.usage.output_tokens, cache_read_input_tokens: response.usage.cache_read_input_tokens ?? 0, cost_usd: cost },
    };
  }
}
