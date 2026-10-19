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

/** Fuzzy "does this word appear in the notes" (prefix of ≥5 chars tolerates plural/typo endings). Used for derived text only. */
function wordInNotes(word: string, notes: string): boolean {
  const w = norm(word); const n = ' ' + norm(notes) + ' ';
  if (!w) return true;
  if (n.includes(' ' + w + ' ')) return true;
  const stem = w.slice(0, Math.max(5, Math.ceil(w.length * 0.7)));
  return stem.length >= 5 && n.includes(' ' + stem);
}

function spanText(notes: string, spans: Span[]): string {
  return spans.map(([a, b]) => notes.slice(a, b)).join('\n');
}

/** The full lines of the notes that the spans touch (vitals are often written "T 38.6" with the span on the label). */
function spanLines(notes: string, spans: Span[]): string {
  return spans.map(([a, b]) => {
    while (a < b && notes[a] === '\n') a++;
    while (b > a && notes[b - 1] === '\n') b--;
    const s = notes.lastIndexOf('\n', a - 1) + 1;
    const e = notes.indexOf('\n', b);
    return notes.slice(s, e < 0 ? notes.length : e);
  }).join('\n');
}

const hasNum = (set: Set<string>, value: number | string) => { const s = num(String(value)); return set.has(s) || set.has(String(parseFloat(s))); };

/** Phrase match on whole tokens after normalisation (case, diacritics, dots and punctuation removed). */
const normPhrase = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/\./g, '').replace(/(\d)\s*x\b/g, '$1x').replace(/[^a-z0-9]+/g, ' ').trim();
const containsPhrase = (hay: string, needle: string) => { const n = normPhrase(needle); return !!n && (' ' + normPhrase(hay) + ' ').includes(' ' + n + ' '); };

/**
 * Explicit route equivalences (normalised: lower case, no diacritics, no dots). A route is supported
 * if it is written literally in the medication's source text, or if it and the source share a group.
 */
export const ROUTE_EQUIVALENTS: string[][] = [
  ['sc', 'sq', 'subcutaneous', 'subcutaneously', 'subkutan', 'sottocute', 'sottocutaneo', 'sottocutanea'],
  ['po', 'oral', 'orally', 'per os', 'by mouth', 'peroral', 'orale', 'per bocca'],
  ['iv', 'intravenous', 'intravenously', 'intravenos', 'ev', 'endovena', 'endovenoso'],
  ['im', 'intramuscular', 'intramuscularly', 'intramuskular', 'intramuscolare'],
  ['auricular', 'aurikular', 'auricolare', 'otic', 'ear drops', 'ohrentropfen', 'gocce auricolari'],
  ['topical', 'topically', 'topisch', 'topica', 'topico', 'uso topico'],
  ['ocular', 'okular', 'oculare', 'ophthalmic', 'eye drops', 'eye gel', 'eye ointment', 'augentropfen', 'augengel', 'augensalbe', 'collirio', 'gel oftalmico'],
];

/** Explicit frequency equivalences (normalised as above; "2 x" becomes "2x"). */
export const FREQUENCY_EQUIVALENTS: string[][] = [
  ['sid', 'q24h', 'once daily', 'once a day', 'daily', '1x daily', '1x a day', 'every 24 hours', 'einmal taglich', '1x taglich', '1x tgl', 'taglich', 'una volta al giorno', '1 volta al giorno'],
  ['bid', 'q12h', 'twice daily', 'twice a day', '2x daily', '2x a day', 'every 12 hours', 'zweimal taglich', '2x taglich', '2x tgl', 'due volte al giorno', '2 volte al giorno'],
  ['tid', 'q8h', 'three times daily', 'three times a day', '3x daily', '3x a day', 'every 8 hours', 'dreimal taglich', '3x taglich', '3x tgl', 'tre volte al giorno', '3 volte al giorno'],
  ['qid', 'q6h', 'four times daily', 'four times a day', '4x daily', '4x a day', 'every 6 hours', 'viermal taglich', '4x taglich', '4x tgl', 'quattro volte al giorno', '4 volte al giorno'],
  ['eod', 'every other day', 'alle 2 tage', 'jeden 2 tag', 'a giorni alterni'],
  ['weekly', 'once weekly', 'once a week', '1x weekly', 'wochentlich', '1x pro woche', 'einmal pro woche', 'settimanale', 'una volta a settimana', '1 volta a settimana'],
  ['twice weekly', 'twice a week', '2x weekly', '2x a week', '2x pro woche', 'zweimal pro woche', '2x wochentlich', 'due volte a settimana', '2 volte a settimana'],
  ['monthly', 'once a month', 'once monthly', 'monatlich', '1x monatlich', 'einmal im monat', 'mensile', 'una volta al mese'],
  ['prn', 'as needed', 'bei bedarf', 'al bisogno', 'secondo necessita'],
];

/** Is `value` written in `src`, literally or as an explicit equivalent from `table`? */
export function supportedBy(value: string, src: string, table: string[][]): boolean {
  if (containsPhrase(src, value)) return true;
  const v = normPhrase(value);
  return table.some((g) => g.includes(v) && g.some((alt) => containsPhrase(src, alt)));
}

function levenshtein1(a: string, b: string): boolean {
  if (a === b) return true;
  if (Math.abs(a.length - b.length) > 1) return false;
  let i = 0, j = 0, edits = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { i++; j++; continue; }
    if (++edits > 1) return false;
    if (a.length > b.length) i++; else if (b.length > a.length) j++; else { i++; j++; }
  }
  return edits + (a.length - i) + (b.length - j) <= 1;
}

/**
 * The drug name must be written in `src`: the same tokens after normalisation (case, diacritics,
 * punctuation). Only names of ≥ 8 characters tolerate a single-character edit (a typo in the notes).
 */
export function drugInText(drug: string, src: string): boolean {
  const d = norm(drug).split(' ').filter(Boolean); const t = norm(src).split(' ').filter(Boolean);
  if (!d.length) return true;
  const dj = d.join(' ');
  for (let k = d.length - 1; k <= d.length + 1; k++) {
    if (k < 1) continue;
    for (let i = 0; i + k <= t.length; i++) {
      const w = t.slice(i, i + k).join(' ');
      if (w === dj) return true;
      if (dj.replace(/ /g, '').length >= 8 && levenshtein1(dj, w)) return true;
    }
  }
  return false;
}

function checkSpans(field: string, spans: Span[] | undefined, notes: string, findings: Finding[]) {
  if (!spans || spans.length === 0) { findings.push({ rule: 'source_required', severity: 'block', field, message: 'No source in the notes for this item.' }); return; }
  for (const [a, b] of spans) {
    if (a >= b || b > notes.length) findings.push({ rule: 'span_invalid', severity: 'block', field, message: `Source span [${a},${b}] is outside the notes.`, span: [a, b] });
  }
}

/** Every fact must be supported by the notes, and each number by the text its own source points to. */
export function validateGrounding(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const nums = numbersIn(notes);
  /**
   * A number must be written in the item's own source text (`lines`: or on the same line, for vitals).
   * Not in the notes at all → number_not_in_notes; in the notes but elsewhere → number_not_in_source.
   * Only an item without spans falls back to the whole-note check.
   */
  const checkNumber = (field: string, value: number | string | null | undefined, spans?: Span[], opts: { lines?: boolean; rule?: string } = {}) => {
    if (value == null) return;
    if (!hasNum(nums, value)) { f.push({ rule: opts.rule === 'text_number_not_in_source' ? opts.rule : 'number_not_in_notes', severity: 'block', field, message: `The value ${value} does not appear in the notes.`, span: spans?.[0] }); return; }
    if (!spans || spans.length === 0) return;
    const src = opts.lines ? spanLines(notes, spans) : spanText(notes, spans);
    if (!hasNum(numbersIn(src), value)) f.push({ rule: opts.rule ?? 'number_not_in_source', severity: 'block', field, message: `The value ${value} is in the notes, but not in the text this item points to ("${spanText(notes, spans).trim()}").`, span: spans[0] });
  };
  const checkText = (field: string, text: string | null | undefined, spans: Span[]) => {
    if (!text) return;
    for (const m of text.matchAll(/\d+(?:[.,]\d+)?/g)) checkNumber(field, m[0], spans, { rule: 'text_number_not_in_source' });
  };

  if (record.presenting_complaint) { checkSpans('presenting_complaint', record.presenting_complaint.source_spans, notes, f); checkText('presenting_complaint.text', record.presenting_complaint.text, record.presenting_complaint.source_spans); }
  record.history.forEach((h, i) => { checkSpans(`history[${i}]`, h.source_spans, notes, f); checkText(`history[${i}].value`, h.value, h.source_spans); });
  const v = record.examination.vitals;
  for (const k of ['temperature', 'heart_rate', 'respiratory_rate', 'weight', 'crt_seconds'] as const) {
    const q = v[k]; if (!q) continue;
    checkSpans(`examination.vitals.${k}`, q.source_spans, notes, f); checkNumber(`examination.vitals.${k}`, q.value, q.source_spans, { lines: true });
  }
  record.examination.findings.forEach((x, i) => { checkSpans(`examination.findings[${i}]`, x.source_spans, notes, f); checkText(`examination.findings[${i}].text`, x.text, x.source_spans); });
  record.diagnostics.forEach((d, i) => {
    checkSpans(`diagnostics[${i}]`, d.source_spans, notes, f);
    if (d.result) for (const n of d.result.matchAll(/\d+(?:[.,]\d+)?/g)) checkNumber(`diagnostics[${i}].result`, n[0], d.source_spans);
  });
  record.treatments.forEach((t, i) => { checkSpans(`treatments[${i}]`, t.source_spans, notes, f); checkText(`treatments[${i}].text`, t.text, t.source_spans); });
  record.assessment.differentials.forEach((d, i) => { checkSpans(`assessment.differentials[${i}]`, d.source_spans, notes, f); checkText(`assessment.differentials[${i}].text`, d.text, d.source_spans); });
  if (record.assessment.text && record.assessment.source_spans.length === 0) f.push({ rule: 'source_required', severity: 'block', field: 'assessment.text', message: 'Assessment has no source in the notes. The AI must not add a diagnosis.' });
  else if (record.assessment.text) checkText('assessment.text', record.assessment.text, record.assessment.source_spans);
  if (record.plan.follow_up) {
    const fu = record.plan.follow_up;
    checkSpans('plan.follow_up', fu.source_spans, notes, f);
    checkText('plan.follow_up.text', fu.text, fu.source_spans);
    if (fu.interval) checkNumber('plan.follow_up.interval', fu.interval.value, fu.source_spans);
  }
  record.plan.instructions.forEach((x, i) => { checkSpans(`plan.instructions[${i}]`, x.source_spans, notes, f); checkText(`plan.instructions[${i}].text`, x.text, x.source_spans); });
  if (record.patient.weight) checkNumber('patient.weight', record.patient.weight.value, record.patient.weight.source_spans, { lines: true });
  // patient.age carries no source span in schema 0.2: whole-note check only
  if (record.patient.age) checkNumber('patient.age', record.patient.age.value);
  return f;
}

/** Drug, dose, route, frequency, duration: each must be in the medication's own source text. */
export function validateMedications(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const nums = numbersIn(notes);
  record.medications.forEach((m, i) => {
    const field = `medications[${i}]`;
    checkSpans(field, m.source_spans, notes, f);
    const spans = m.source_spans ?? [];
    const src = spanText(notes, spans);
    const srcNums = numbersIn(src);
    const quoted = `("${src.trim()}")`;
    if (m.drug && !drugInText(m.drug, src)) {
      const elsewhere = drugInText(m.drug, notes);
      f.push({ rule: elsewhere ? 'drug_not_in_source' : 'drug_not_in_notes', severity: 'block', field: `${field}.drug`, message: elsewhere ? `"${m.drug}" is in the notes, but not in the text this medication points to ${quoted}.` : `"${m.drug}" is not in the notes.` });
    }
    if (m.dose != null) {
      if (!hasNum(nums, m.dose)) f.push({ rule: 'dose_not_in_notes', severity: 'block', field: `${field}.dose`, message: `Dose ${m.dose} is not in the notes.` });
      else if (!hasNum(srcNums, m.dose)) f.push({ rule: 'dose_not_in_source', severity: 'block', field: `${field}.dose`, message: `Dose ${m.dose} is in the notes, but not in the text this medication points to ${quoted}.` });
    }
    if (m.dose_unit && !norm(notes).includes(norm(m.dose_unit)) && !/^(mg|ml|g|iu|mcg|µg|tablet|tablets|tab|tabs|capsule|drops|ml\/kg|mg\/kg)$/i.test(m.dose_unit)) f.push({ rule: 'unit_not_in_notes', severity: 'warn', field: `${field}.dose_unit`, message: `Unit "${m.dose_unit}" was not written in the notes.` });
    if (m.duration) for (const n of m.duration.matchAll(/\d+(?:[.,]\d+)?/g)) {
      if (!hasNum(nums, n[0])) f.push({ rule: 'duration_not_in_notes', severity: 'block', field: `${field}.duration`, message: `Duration "${m.duration}" contains a number not in the notes.` });
      else if (!hasNum(srcNums, n[0])) f.push({ rule: 'duration_not_in_source', severity: 'block', field: `${field}.duration`, message: `Duration "${m.duration}": ${n[0]} is not in the text this medication points to ${quoted}.` });
    }
    if (m.route && !supportedBy(m.route, src, ROUTE_EQUIVALENTS)) f.push({ rule: 'route_not_in_source', severity: 'block', field: `${field}.route`, message: `Route "${m.route}" is not written in the text this medication points to ${quoted}.` });
    if (m.frequency && !supportedBy(m.frequency, src, FREQUENCY_EQUIVALENTS)) f.push({ rule: 'frequency_not_in_source', severity: 'block', field: `${field}.frequency`, message: `Frequency "${m.frequency}" is not written in the text this medication points to ${quoted}.` });
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
