import type { ClinicalRecord } from './schema.js';
import type { Finding } from './validators.js';

/**
 * Published quality metrics, defined so anyone can recompute them from the eval output.
 *
 * - attribution rate: facts in the record whose source span points into the notes and
 *   that raised no blocking finding, over all facts.
 * - unsupported-content rate: facts with a blocking finding (not in the notes, number or
 *   dose not written, span outside the notes), over all facts.
 * - missing-field detection: fields the case expects to be flagged as missing that the
 *   record or the document check did flag, over all such expected fields.
 * - missing-flag precision: flags raised (the record's own `missing` fields plus the
 *   document check `requiredMissing`) that are also in the case's expected missing list,
 *   over all flags raised. A false "missing" flag costs the vet a click and erodes trust
 *   in the real ones, so it is measured, not just recall.
 *
 * Every rate is reported with a 95 % Wilson interval, because with a few dozen cases a
 * bare percentage overstates what is known.
 */

export type Rate = { k: number; n: number; rate: number | null; lo: number | null; hi: number | null };

/** Wilson score interval; behaves sensibly at 0 and n. */
export function wilson(k: number, n: number, z = 1.96): Rate {
  if (n === 0) return { k, n, rate: null, lo: null, hi: null };
  const p = k / n, z2 = z * z;
  const centre = (p + z2 / (2 * n)) / (1 + z2 / n);
  const half = (z * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / (1 + z2 / n);
  const r = (x: number) => Math.round(x * 10000) / 10000;
  return { k, n, rate: r(p), lo: r(Math.max(0, centre - half)), hi: r(Math.min(1, centre + half)) };
}

/** One path per fact, using the same field names as the validators. */
export function factPaths(record: ClinicalRecord): string[] {
  const out: string[] = [];
  if (record.presenting_complaint) out.push('presenting_complaint');
  record.history.forEach((_, i) => out.push(`history[${i}]`));
  const v = record.examination.vitals;
  for (const k of ['temperature', 'heart_rate', 'respiratory_rate', 'weight', 'crt_seconds'] as const) if (v[k]) out.push(`examination.vitals.${k}`);
  record.examination.findings.forEach((_, i) => out.push(`examination.findings[${i}]`));
  record.diagnostics.forEach((_, i) => out.push(`diagnostics[${i}]`));
  if (record.assessment.text) out.push('assessment.text');
  record.assessment.differentials.forEach((_, i) => out.push(`assessment.differentials[${i}]`));
  record.treatments.forEach((_, i) => out.push(`treatments[${i}]`));
  record.medications.forEach((_, i) => out.push(`medications[${i}]`));
  if (record.plan.follow_up) out.push('plan.follow_up');
  record.plan.instructions.forEach((_, i) => out.push(`plan.instructions[${i}]`));
  return out;
}

/** Facts in this record and how many of them carry a blocking finding. */
export function scoreFacts(record: ClinicalRecord, findings: Finding[]): { facts: number; unsupported: number; unsupported_paths: string[] } {
  const blocks = findings.filter((f) => f.severity === 'block');
  const paths = factPaths(record);
  const bad = paths.filter((p) => blocks.some((f) => f.field === p || f.field.startsWith(`${p}.`) || f.field.startsWith(`${p}[`)));
  return { facts: paths.length, unsupported: bad.length, unsupported_paths: bad };
}

/** Missing flags raised for one case, scored against the case's expected missing list. */
export function scoreMissingFlags(raised: Iterable<string>, expected: Iterable<string>): { raised: number; correct: number; false_flags: string[] } {
  const exp = new Set(expected); const r = [...new Set(raised)];
  const false_flags = r.filter((x) => !exp.has(x));
  return { raised: r.length, correct: r.length - false_flags.length, false_flags };
}

export const pct = (r: Rate) => (r.rate == null ? 'n/a' : `${(100 * r.rate).toFixed(1)} % (95 % CI ${(100 * r.lo!).toFixed(1)}–${(100 * r.hi!).toFixed(1)}, ${r.k}/${r.n})`);
