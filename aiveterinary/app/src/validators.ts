import type { ClinicalRecord, PatientHeader, Span } from './schema.js';

/**
 * Validators run on every model output. They never "fix" anything: they report,
 * and the UI blocks approval until the vet resolves the report.
 *
 * severity:
 *  - block: approval impossible (invented drug/number, conflicting patient facts)
 *  - warn: shown to the vet (plausibility, style)
 */
export type Finding = { rule: string; severity: 'block' | 'warn'; field: string; message: string; span?: Span };

const num = (s: string) => s.replace(',', '.');

/** All numbers in the notes, normalised to '.' decimal, as strings and as values. */
export function numbersIn(text: string): Set<string> {
  const out = new Set<string>();
  for (const m of text.matchAll(/\d+(?:[.,]\d+)?/g)) {
    const v = num(m[0]);
    out.add(v); out.add(String(parseFloat(v)));
  }
  return out;
}

const norm = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

/** Fuzzy "does this word appear in the notes" (prefix of ≥5 chars tolerates plural/typo endings). */
function wordInNotes(word: string, notes: string): boolean {
  const w = norm(word); const n = ' ' + norm(notes) + ' ';
  if (!w) return true;
  if (n.includes(' ' + w + ' ')) return true;
  const stem = w.slice(0, Math.max(5, Math.ceil(w.length * 0.7)));
  return stem.length >= 5 && n.includes(' ' + stem);
}

function spanText(notes: string, spans: Span[]): string {
  return spans.map(([a, b]) => notes.slice(a, b)).join(' ');
}

function checkSpans(field: string, spans: Span[] | undefined, notes: string, findings: Finding[]) {
  if (!spans || spans.length === 0) { findings.push({ rule: 'source_required', severity: 'block', field, message: 'No source in the notes for this item.' }); return; }
  for (const [a, b] of spans) {
    if (a >= b || b > notes.length) findings.push({ rule: 'span_invalid', severity: 'block', field, message: `Source span [${a},${b}] is outside the notes.`, span: [a, b] });
  }
}

/** Every fact must be supported by the notes. */
export function validateGrounding(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const nums = numbersIn(notes);
  const checkNumber = (field: string, value: number | null | undefined, spans?: Span[]) => {
    if (value == null) return;
    const s = String(value);
    if (!nums.has(s) && !nums.has(String(parseFloat(s)))) f.push({ rule: 'number_not_in_notes', severity: 'block', field, message: `The value ${value} does not appear in the notes.`, span: spans?.[0] });
  };

  if (record.presenting_complaint) checkSpans('presenting_complaint', record.presenting_complaint.source_spans, notes, f);
  record.history.forEach((h, i) => checkSpans(`history[${i}]`, h.source_spans, notes, f));
  const v = record.examination.vitals;
  for (const k of ['temperature', 'heart_rate', 'respiratory_rate', 'weight', 'crt_seconds'] as const) {
    const q = v[k]; if (!q) continue;
    checkSpans(`examination.vitals.${k}`, q.source_spans, notes, f); checkNumber(`examination.vitals.${k}`, q.value, q.source_spans);
  }
  record.examination.findings.forEach((x, i) => checkSpans(`examination.findings[${i}]`, x.source_spans, notes, f));
  record.diagnostics.forEach((d, i) => {
    checkSpans(`diagnostics[${i}]`, d.source_spans, notes, f);
    if (d.result) for (const n of d.result.matchAll(/\d+(?:[.,]\d+)?/g)) if (!nums.has(num(n[0]))) f.push({ rule: 'number_not_in_notes', severity: 'block', field: `diagnostics[${i}].result`, message: `The value ${n[0]} does not appear in the notes.` });
  });
  record.treatments.forEach((t, i) => checkSpans(`treatments[${i}]`, t.source_spans, notes, f));
  record.assessment.differentials.forEach((d, i) => checkSpans(`assessment.differentials[${i}]`, d.source_spans, notes, f));
  if (record.assessment.text && record.assessment.source_spans.length === 0) f.push({ rule: 'source_required', severity: 'block', field: 'assessment.text', message: 'Assessment has no source in the notes. The AI must not add a diagnosis.' });
  if (record.plan.follow_up) {
    checkSpans('plan.follow_up', record.plan.follow_up.source_spans, notes, f);
    if (record.plan.follow_up.interval) checkNumber('plan.follow_up.interval', record.plan.follow_up.interval.value, record.plan.follow_up.source_spans);
  }
  record.plan.instructions.forEach((x, i) => checkSpans(`plan.instructions[${i}]`, x.source_spans, notes, f));
  if (record.patient.weight) checkNumber('patient.weight', record.patient.weight.value);
  if (record.patient.age) checkNumber('patient.age', record.patient.age.value);
  return f;
}

/** Drug, dose, route, frequency, duration: each must be in the notes, verbatim or near-verbatim. */
export function validateMedications(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const nums = numbersIn(notes);
  record.medications.forEach((m, i) => {
    const field = `medications[${i}]`;
    checkSpans(field, m.source_spans, notes, f);
    const src = spanText(notes, m.source_spans ?? []);
    if (m.drug && !wordInNotes(m.drug, notes)) f.push({ rule: 'drug_not_in_notes', severity: 'block', field: `${field}.drug`, message: `"${m.drug}" is not in the notes.` });
    if (m.dose != null && !nums.has(String(m.dose))) f.push({ rule: 'dose_not_in_notes', severity: 'block', field: `${field}.dose`, message: `Dose ${m.dose} is not in the notes.` });
    if (m.dose_unit && !norm(notes).includes(norm(m.dose_unit)) && !/^(mg|ml|g|iu|mcg|µg|tablet|tablets|tab|tabs|capsule|drops|ml\/kg|mg\/kg)$/i.test(m.dose_unit)) f.push({ rule: 'unit_not_in_notes', severity: 'warn', field: `${field}.dose_unit`, message: `Unit "${m.dose_unit}" was not written in the notes.` });
    if (m.duration) for (const n of m.duration.matchAll(/\d+/g)) if (!nums.has(n[0])) f.push({ rule: 'duration_not_in_notes', severity: 'block', field: `${field}.duration`, message: `Duration "${m.duration}" contains a number not in the notes.` });
    if (m.frequency && !/^(once|twice|three times|four times|every|daily|sid|bid|tid|qid|q\d+h|eod|prn|as needed|einmal|zweimal|dreimal|täglich|una volta|due volte|tre volte|al giorno)/i.test(m.frequency) && !wordInNotes(m.frequency, notes)) f.push({ rule: 'frequency_not_in_notes', severity: 'warn', field: `${field}.frequency`, message: `Frequency "${m.frequency}" was not written in the notes.` });
    if (m.dose != null && !m.drug) f.push({ rule: 'dose_without_drug', severity: 'block', field, message: 'A dose without a drug name.' });
    if (!src.trim()) f.push({ rule: 'empty_source', severity: 'block', field, message: 'Medication has an empty source.' });
  });
  return f;
}

/** Patient facts come from the header, never from prose. Conflicts block. */
export function validatePatient(record: ClinicalRecord, header: PatientHeader): Finding[] {
  const f: Finding[] = [];
  const p = record.patient;
  if (p.species && p.species !== header.species) f.push({ rule: 'patient_conflict', severity: 'block', field: 'patient.species', message: `Notes imply species "${p.species}" but the patient is a ${header.species}.` });
  if (p.sex && header.sex && p.sex !== header.sex) f.push({ rule: 'patient_conflict', severity: 'block', field: 'patient.sex', message: `Notes imply sex "${p.sex}" but the patient record says ${header.sex}.` });
  const text = JSON.stringify({ ...record, uncertain: [] }).toLowerCase();
  if (header.sex === 'male' && /pregnan|gravid|trächtig|incinta|gestante/.test(text)) f.push({ rule: 'patient_conflict', severity: 'block', field: 'patient', message: 'Pregnancy mentioned for a male patient. Check whether this refers to the owner or another animal.' });
  if (header.neuter_status === 'neutered' && /in heat|oestrus|estrus|läufig|in calore/.test(text)) f.push({ rule: 'patient_plausibility', severity: 'warn', field: 'patient', message: 'Heat/oestrus mentioned for a neutered patient.' });
  return f;
}

/** Species-aware plausibility: warnings only, never auto-corrected. */
export function validatePlausibility(record: ClinicalRecord, header: PatientHeader): Finding[] {
  const f: Finding[] = [];
  const t = record.examination.vitals.temperature;
  const ranges: Record<string, [number, number]> = { dog: [35, 42.5], cat: [35, 42.5], rabbit: [36, 42], horse: [35, 41], ferret: [35, 42], bird: [38, 44], reptile: [15, 40], other: [30, 45] };
  if (t && t.unit.toUpperCase().startsWith('C')) {
    const [lo, hi] = ranges[header.species] ?? ranges.other;
    if (t.value < lo || t.value > hi) f.push({ rule: 'implausible_value', severity: 'warn', field: 'examination.vitals.temperature', message: `Temperature ${t.value} °C is outside the usual range for a ${header.species}. Typo?` });
  }
  const w = record.patient.weight ?? record.examination.vitals.weight;
  if (w && w.unit === 'kg' && header.species === 'cat' && w.value > 15) f.push({ rule: 'implausible_value', severity: 'warn', field: 'weight', message: `${w.value} kg is unusually heavy for a cat.` });
  return f;
}

/** Owner-facing / derived text must not introduce facts beyond the approved record. */
export function validateDerivedText(text: string, record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const allowed = numbersIn(notes);
  // numbers that are part of medication rendering are allowed; everything else must be in notes
  for (const m of text.matchAll(/\d+(?:[.,]\d+)?/g)) {
    const v = num(m[0]);
    if (!allowed.has(v) && !allowed.has(String(parseFloat(v)))) f.push({ rule: 'derived_number_not_in_record', severity: 'block', field: 'derived', message: `"${m[0]}" is not in the approved record.` });
  }
  for (const med of record.medications) if (med.drug && !wordInNotes(med.drug, text)) f.push({ rule: 'medication_missing_in_derived', severity: 'warn', field: 'derived', message: `Medication "${med.drug}" from the record is not mentioned.` });
  return f;
}

/** Fields a document needs; returns what is missing so the UI can flag it. Does not invent. */
export function requiredMissing(record: ClinicalRecord, docType: 'consult_report' | 'discharge' | 'referral' | 'owner_summary'): string[] {
  const miss: string[] = [];
  if (!record.presenting_complaint) miss.push('presenting_complaint');
  if (docType !== 'owner_summary' && !record.assessment.text && record.assessment.differentials.length === 0) miss.push('assessment');
  record.medications.forEach((m, i) => {
    if (!m.drug) miss.push(`medications[${i}].drug`);
    if (m.status !== 'declined') {
      if (m.dose == null) miss.push(`medications[${i}].dose`);
      if (!m.route) miss.push(`medications[${i}].route`);
      if (!m.frequency) miss.push(`medications[${i}].frequency`);
      if (docType === 'discharge' || docType === 'owner_summary') if (!m.duration) miss.push(`medications[${i}].duration`);
    }
  });
  if (record.medications.some((m) => m.dose != null) && !record.patient.weight && !record.examination.vitals.weight) miss.push('patient.weight');
  record.diagnostics.forEach((d, i) => { if (d.status === 'performed' && !d.result) miss.push(`diagnostics[${i}].result`); });
  if ((docType === 'discharge' || docType === 'owner_summary') && !record.plan.follow_up && record.plan.instructions.length === 0) miss.push('plan');
  return miss;
}

export function validateAll(record: ClinicalRecord, notes: string, header: PatientHeader): Finding[] {
  return [
    ...validateGrounding(record, notes),
    ...validateMedications(record, notes),
    ...validatePatient(record, header),
    ...validatePlausibility(record, header),
  ];
}
