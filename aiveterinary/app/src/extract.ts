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
export type ExtractResult = { record: ClinicalRecord; raw: unknown; model: string; usage?: { input_tokens: number; output_tokens: number } };

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

/** Claude adapter. Loaded lazily so the package works without the SDK or a key. */
export class ClaudeExtractor implements Extractor {
  readonly name = 'claude';
  constructor(private model = process.env.AIVET_MODEL ?? 'claude-opus-5') {}
  async extract(input: ExtractInput): Promise<ExtractResult> {
    const [{ default: Anthropic }, { zodOutputFormat }] = await Promise.all([import('@anthropic-ai/sdk'), import('@anthropic-ai/sdk/helpers/zod')]);
    const client = new Anthropic();
    const response = await client.messages.parse({
      model: this.model,
      max_tokens: 16000,
      system: [{ type: 'text', text: systemPrompt(), cache_control: { type: 'ephemeral' } }],
      messages: [{ role: 'user', content: userPrompt(input) }],
      output_config: { format: zodOutputFormat(ClinicalRecord) },
    });
    if (!response.parsed_output) throw new Error('Model output did not match the record schema');
    return { record: response.parsed_output, raw: response.parsed_output, model: this.model, usage: { input_tokens: response.usage.input_tokens, output_tokens: response.usage.output_tokens } };
  }
}
