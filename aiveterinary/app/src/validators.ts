import type { ClinicalRecord, PatientHeader, Span } from './schema.js';
import { factPaths } from './metrics.js';

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

/**
 * A vaccine named in the drug or class text (EN/DE/IT: vaccine, vaccin*, Impf*, Impfstoff, vaccino).
 * A vaccine is given as one standard dose per the product and is recorded by product and batch,
 * not by a dose number; the batch requirement (vaccination entry) covers it.
 */
// German compounds put the vaccine word last (Staupeimpfstoff, Tollwutimpfung), so those match anywhere.
export const VACCINE_RE = /\b(vaccin|vakzin|impf)|impfstoff|impfung/i;
const isVaccine = (m: ClinicalRecord['medications'][number]) => VACCINE_RE.test(`${m.drug ?? ''} ${m.class_as_written ?? ''}`);

/**
 * Fields a document needs; returns what is missing so the UI can flag it. Does not invent.
 *
 * Rules for medications (status 'declined' needs nothing beyond the drug name):
 *  - dose and route are required for every non-declined medication, except that a vaccine given in
 *    the clinic (status 'performed') needs no dose number (see VACCINE_RE);
 *  - frequency and duration are not required for a medication given once in the clinic
 *    (status 'performed'); for prescribed/dispensed/other statuses frequency is required, and
 *    duration on discharge and owner-summary documents.
 * Weight is required when a non-declined medication carries a dose, unless the record or the
 * patient header (`header.weight_kg`) already has it.
 * Discharge (renderDischargeLetter) and owner summary also need a follow-up or a home-care
 * instruction in the plan, since those documents exist to tell the owner what happens next.
 * Referral also needs signalment (name, species, breed, sex, age; from the header or the record),
 * at least one history item and some clinical examination (a finding or a vital), the fields most
 * published referral forms ask for (docs/16-referral-fields.md).
 */
export function requiredMissing(record: ClinicalRecord, docType: 'consult_report' | 'discharge' | 'referral' | 'owner_summary', header?: PatientHeader): string[] {
  const miss: string[] = [];
  if (!record.presenting_complaint) miss.push('presenting_complaint');
  if (docType !== 'owner_summary' && !record.assessment.text && record.assessment.differentials.length === 0) miss.push('assessment');
  record.medications.forEach((m, i) => {
    if (!m.drug) miss.push(`medications[${i}].drug`);
    if (m.status !== 'declined') {
      const performed = m.status === 'performed';
      if (m.dose == null && !(performed && isVaccine(m))) miss.push(`medications[${i}].dose`);
      if (!m.route) miss.push(`medications[${i}].route`);
      if (!performed) {
        if (!m.frequency) miss.push(`medications[${i}].frequency`);
        if (docType === 'discharge' || docType === 'owner_summary') if (!m.duration) miss.push(`medications[${i}].duration`);
      }
    }
  });
  const dosed = record.medications.some((m) => m.dose != null && m.status !== 'declined');
  if (dosed && !record.patient.weight && !record.examination.vitals.weight && header?.weight_kg == null) miss.push('patient.weight');
  record.diagnostics.forEach((d, i) => { if (d.status === 'performed' && !d.result) miss.push(`diagnostics[${i}].result`); });
  if ((docType === 'discharge' || docType === 'owner_summary') && !record.plan.follow_up && record.plan.instructions.length === 0) miss.push('plan');
  if (docType === 'referral') {
    // Asked by most referral forms (docs/16-referral-fields.md): signalment, history, clinical findings.
    // Header (locked facts) or the record's own patient fields satisfy signalment; nothing is defaulted.
    const p = record.patient;
    if (!header?.name && !p.name) miss.push('patient.name');
    if (!header?.species && !p.species) miss.push('patient.species');
    if (!header?.breed && !p.breed) miss.push('patient.breed');
    if (!header?.sex && !p.sex) miss.push('patient.sex');
    if (!header?.age && !p.age) miss.push('patient.age');
    if (record.history.length === 0) miss.push('history');
    const v = record.examination.vitals;
    if (record.examination.findings.length === 0 && !v.temperature && !v.heart_rate && !v.respiratory_rate && !v.weight && !v.crt_seconds) miss.push('examination');
  }
  return miss;
}

/**
 * Status markers (EN/DE/IT), matched on the item's own source text after lower-casing and removing
 * diacritics ("durchgeführt" → "durchgefuhrt"). A marker preceded by a simple negation ("not done",
 * "nicht durchgeführt", "non eseguito", "not declined") does not count. "WV" (Wiedervorstellung) is
 * matched case-sensitively on the raw text.
 */
const NEG = String.raw`(?<!\bnot (?:yet )?)(?<!\bnicht (?:mehr )?)(?<!\bnoch nicht )(?<!\bnon (?:ancora )?)`;
/** The animal refusing food or tablets is not the owner declining care. */
const NOT_FOOD = String.raw`(?! (?:to )?(?:the |il |lo |la |le |i |das |die |den )?(?:food|eat|eating|feed|treats?|tablets?|pills?|meds|medication|cibo|pappa|mangiare|cibarsi|compresse|pastiglie|futter|fressen|nahrung|tabletten?)\b)`;
export const STATUS_MARKERS: Record<'declined' | 'planned' | 'performed', RegExp[]> = {
  declined: [
    new RegExp(String.raw`${NEG}\b(?:declined|declines)\b`),
    new RegExp(String.raw`${NEG}\b(?:refused|refuses)\b${NOT_FOOD}`),
    new RegExp(String.raw`${NEG}\babgelehnt\b`),
    /\blehnt\b(?:\s+\S+){0,3}?\s+ab\b/,
    new RegExp(String.raw`(?<!\b(?:futter|fressen|nahrung|tabletten?) )${NEG}\bverweigert?\b${NOT_FOOD}`),
    new RegExp(String.raw`\brifiut(?:a|ano|ato|ata|ati|ate)\b${NOT_FOOD}`),
    /\bnon acconsente\b/,
  ],
  planned: [
    new RegExp(String.raw`${NEG}\b(?:planned|scheduled)\b`),
    /\bto be (?:done|performed)\b/,
    new RegExp(String.raw`${NEG}\b(?:geplant|vorgesehen)\b`),
    /\bprogrammat[oaie]\b/,
    /\bda fare\b/,
    /\bprevist[oaie]\b/,
  ],
  performed: [
    new RegExp(String.raw`${NEG}(?<!\bto be )(?<!\bbe )\b(?:performed|done)\b`),
    new RegExp(String.raw`${NEG}\bdurchgefuhrt\b`),
    new RegExp(String.raw`${NEG}\b(?:eseguit|effettuat)[oaie]\b`),
  ],
};
const foldText = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ');

/** The status markers written in `src`. */
export function statusMarkers(src: string): Set<'declined' | 'planned' | 'performed'> {
  const t = foldText(src); const out = new Set<'declined' | 'planned' | 'performed'>();
  for (const [k, res] of Object.entries(STATUS_MARKERS) as [keyof typeof STATUS_MARKERS, RegExp[]][]) if (res.some((re) => re.test(t))) out.add(k);
  if (/\bWV\b/.test(src)) out.add('planned');
  return out;
}

/**
 * Owner-report markers (EN/DE/IT): "owner reports", "per owner", "Besitzer berichtet", "laut Besitzerin",
 * "la proprietaria riferisce", "riferito" (not "dolore riferito", referred pain).
 */
export const OWNER_REPORT_MARKERS: RegExp[] = [
  /\b(?:owner|o)\s+(?:reports?|reported|says|states|thinks|noticed)\b/,
  /\b(?:per|according to(?: the)?) owner\b/,
  /\bbesitzer(?:in)?\s+(?:berichtet|meint|sagt|erzahlt|hat bemerkt|bemerkt)\b/,
  /\blaut besitzer(?:in)?\b/,
  /\b(?:il |la )?proprietari[oa] riferisce\b/,
  /\bsecondo (?:il |la )?proprietari[oa]\b/,
  /(?<!\bdolore )\briferit[oaie]\b/,
];

/**
 * Status and role checks on each item's own source text (the span only, as for numbers):
 *  - status_conflicts_source: the span carries a clear marker of one other status
 *    (declined / planned / performed). Declined vs performed, prescribed or dispensed blocks
 *    (either direction); planned vs performed and declined vs planned/recommended warn.
 *    Spans with markers of more than one status are left alone.
 *  - owner_report_as_finding (warn): an examination finding recorded as the vet's own, whose
 *    span says the owner reported it.
 */
export function validateStatus(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const check = (field: string, status: string, spans: Span[]) => {
    if (!spans?.length) return;
    const src = spanText(notes, spans); const marks = statusMarkers(src);
    if (marks.size !== 1) return;
    const [said] = marks;
    const done = status === 'performed' || status === 'prescribed' || status === 'dispensed';
    let severity: Finding['severity'] | null = null;
    if (said === 'declined' && done) severity = 'block';
    else if (said === 'performed' && status === 'declined') severity = 'block';
    else if (said === 'declined' && (status === 'planned' || status === 'recommended')) severity = 'warn';
    else if (said === 'planned' && status === 'performed') severity = 'warn';
    else if (said === 'performed' && status === 'planned') severity = 'warn';
    if (severity) f.push({ rule: 'status_conflicts_source', severity, field: `${field}.status`, message: `Recorded as "${status}", but the text this item points to says ${said} ("${src.trim()}").`, span: spans[0] });
  };
  record.diagnostics.forEach((d, i) => check(`diagnostics[${i}]`, d.status, d.source_spans));
  record.treatments.forEach((t, i) => check(`treatments[${i}]`, t.status, t.source_spans));
  record.medications.forEach((m, i) => check(`medications[${i}]`, m.status, m.source_spans));
  record.examination.findings.forEach((x, i) => {
    if (x.source_role === 'owner_reported' || !x.source_spans?.length) return;
    const src = spanText(notes, x.source_spans); const t = foldText(src);
    if (OWNER_REPORT_MARKERS.some((re) => re.test(t))) f.push({ rule: 'owner_report_as_finding', severity: 'warn', field: `examination.findings[${i}].source_role`, message: `Recorded as the vet's finding, but the text it points to is the owner's report ("${src.trim()}"). Move it to history or mark it owner-reported.`, span: x.source_spans[0] });
  });
  return f;
}

type VitalKey = 'temperature' | 'heart_rate' | 'respiratory_rate' | 'weight' | 'crt_seconds';
/** A number with an optional comparator ("<2") and unit; ranges ("100-120") and ratios ("120/80") are not readings. */
const VITAL_NUM = String.raw`([<>≤≥~]\s*)?(\d+(?:[.,]\d+)?)(?![.,]?\d)(?!\s*[-–/]\s*\d)\s*(kg|g|°?\s?[CF]|°|s|sec|/min)?(?![\p{L}\d])`;
/**
 * Short labels are case-sensitive ("T", "HR", "KGW") and need a space or colon before the number, or a
 * decimal ("T38.5"), so "T4" (thyroid) is not a temperature. Word labels are case-insensitive.
 */
const vitalRes = (abbr: string, words: string): RegExp[] => [
  new RegExp(String.raw`(?<![\p{L}\d])(?:${abbr})\.?(?:\s*[:=]\s*|\s+|(?=\d+[.,]\d))${VITAL_NUM}`, 'gdu'),
  new RegExp(String.raw`(?<![\p{L}\d])(?:${words})\.?\s*[:=]?\s*${VITAL_NUM}`, 'gdiu'),
];
/** The vital labels the notes use (EN/DE/IT). */
export const VITAL_LABELS: Record<VitalKey, RegExp[]> = {
  temperature: vitalRes('T|TR|rT|Temp|TEMP', String.raw`temp|temperature|temperatur|temperatura(?:\s+rettale)?|(?:rektal)?temperatur(?:\s+rektal)?`),
  heart_rate: vitalRes('HR|HF|FC', 'heart rate|pulse|puls|herzfrequenz|frequenza cardiaca|polso'),
  respiratory_rate: vitalRes('RR|AF|FR', 'resp(?:iratory)? rate|resp|atemfrequenz|frequenza respiratoria'),
  weight: vitalRes('KGW|KG|BW|Wt|WT', String.raw`wt|weight|body weight|gewicht|k(?:ö|oe)rpergewicht|peso(?:\s+corporeo)?`),
  crt_seconds: vitalRes('CRT|KFZ|TRC', String.raw`capillary refill(?: time)?|kapill(?:ä|ae)re f(?:ü|ue)llungszeit|tempo di riempimento capillare`),
};
/** A bare weight ("4.2 kg") counts only on a line that holds nothing else (apart from "ca."/"approx" and a bracket). */
const BARE_WEIGHT = /(?<![\p{L}\d/.,])(\d+(?:[.,]\d+)?)\s*(kg|g)(?![\p{L}\d/])/gdu;
const bareWeightLine = (line: string, m: RegExpMatchArray) => !line.replace(m[0], '').replace(/\([^)]*\)/g, '').replace(/\b(?:ca|approx|approximately|about|circa|etwa|wt|weight|peso|kgw|gewicht)\b\.?/gi, '').replace(/[\s,;:.~]/g, '');
/**
 * Explicit other-animal markers (EN/DE/IT, matched on folded text): "other/another/second dog", "not our
 * patient", "next box"; "andere Katze", "nicht unser Patient", "Nachbarbox"; "altro gatto",
 * "non è nostra paziente", "box accanto". Singular nouns only, so "no other pets" does not match.
 */
export const OTHER_ANIMAL_MARKERS: RegExp[] = [
  /\b(?:other|another|second) (?:cat|dog|horse|pet|animal|rabbit|bird)\b|\bnot our patient\b|\bnext (?:box|stall)\b/,
  /\b(?:andere[nrs]?|zweite[nrs]?) (?:katze|hund|pferd|tier|kaninchen|vogel)\b|\bnicht unser(?:e)? patient(?:in)?\b|\bnachbarbox\b/,
  /\b(?:altr[oa]|second[oa]) (?:gatt[oa]|cane|cavall[oa]|animale|coniglio|uccello)\b|\bnon e (?:il |la )?nostr[oa] paziente\b|\bbox accanto\b/,
];
/**
 * A second value that is not a contradiction: an earlier or home measurement, a time course or a change
 * ("after fluids", "lost 2 g"), a target, or another animal (EN/DE/IT, matched on the folded line).
 */
export const NOT_SAME_READING: RegExp[] = [
  /\b(?:previous(?:ly)?|before|earlier|ago|last (?:visit|time|week|month|year|check)|at home|home scale|kitchen scale|owner'?s? scale|on arrival|after|then|repeat(?:ed)?|recheck|target|goal|ideal|lost|losing|gained?|loss)\b/,
  /\b(?:vorher|zuvor|fruher|letzte[nmrs]?|zu ?hause|daheim|vor \d|kuchenwaage|bei ankunft|nach|danach|spater|dann|wiederholt|kontrolle|ziel|idealgewicht|abgenommen|zugenommen|gewichtsverlust)\b/,
  /\b(?:precedente(?:mente)?|prima|a casa|ultim[ao] (?:visita|volta|controllo)|scors[oa]|fa|bilancia di casa|all.?arrivo|dopo|poi|ripetut[oa]|ricontroll\w*|obiettivo|ideale|pers[oi]|perde|calo|aumentat[oa])\b/,
  ...OTHER_ANIMAL_MARKERS,
];
const VITAL_NAMES: Record<VitalKey, string> = { temperature: 'temperature', heart_rate: 'heart rate', respiratory_rate: 'respiratory rate', weight: 'weight', crt_seconds: 'CRT' };

/** Every source span in the record (any item, any depth). */
function allSpans(x: unknown, out: Span[] = []): Span[] {
  if (Array.isArray(x)) x.forEach((y) => allSpans(y, out));
  else if (x && typeof x === 'object') for (const [k, v] of Object.entries(x)) { if (k === 'source_spans' && Array.isArray(v)) out.push(...(v as Span[])); else allSpans(v, out); }
  return out;
}

/**
 * notes_contradiction (warn): the notes give a recorded vital twice with different values and the
 * record keeps one without mentioning the other. Conservative: only labelled readings (or a line that
 * is only a weight) count; a comparator ("CRT<2"), a range, an earlier/home/time-course/other-animal
 * line, or a second value that lies in any other record item's source (history, uncertain …) is left alone.
 * Values are compared after decimal-comma and kg/g normalisation.
 */
export function validateNotesContradiction(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  const v = record.examination.vitals;
  const toG = (value: number, unit: string | undefined) => (unit?.toLowerCase() === 'g' ? value : unit?.toLowerCase() === 'kg' ? value * 1000 : NaN);
  for (const k of ['temperature', 'heart_rate', 'respiratory_rate', 'weight', 'crt_seconds'] as const) {
    const recs = (k === 'weight' ? [v.weight, record.patient.weight] : [v[k]]).filter((q): q is NonNullable<typeof q> => !!q);
    if (!recs.length) continue;
    const recUnit = recs[0].unit;
    /** Comparable value: grams for weight (unit from the mention, else the record's), the number otherwise. */
    const key = (value: number, unit?: string) => (k === 'weight' ? toG(value, unit || recUnit) : value);
    const kept = recs.map((q) => key(q.value, q.unit)).filter((x) => !Number.isNaN(x));
    if (!kept.length) continue;
    const own = recs.flatMap((q) => q.source_spans);
    const others = allSpans({ ...record, examination: { ...record.examination, vitals: { ...v, [k]: null } }, patient: k === 'weight' ? { ...record.patient, weight: null } : record.patient }).filter((s) => !own.some(([a, b]) => s[0] === a && s[1] === b));
    type Mention = { at: number; end: number; text: string; cmp?: string; value: number; unit?: string };
    const mentions = new Map<number, Mention>();
    for (const re of VITAL_LABELS[k]) for (const m of notes.matchAll(re)) {
      const [at, end] = m.indices![2]!; const unit = m[3]?.replace(/[\s°]/g, '');
      mentions.set(at, { at, end: m.indices![3]?.[1] ?? end, text: num(m[2]) + (unit && k === 'weight' ? ' ' + unit : ''), cmp: m[1], value: parseFloat(num(m[2])), unit });
    }
    if (k === 'weight') for (const m of notes.matchAll(BARE_WEIGHT)) {
      const [at] = m.indices![1]!; const s = notes.lastIndexOf('\n', at - 1) + 1; const e = notes.indexOf('\n', at);
      if (bareWeightLine(notes.slice(s, e < 0 ? notes.length : e), m)) mentions.set(at, { at, end: m.indices![2]![1], text: `${num(m[1])} ${m[2]}`, value: parseFloat(num(m[1])), unit: m[2] });
    }
    const valueOf = (x: Mention) => key(x.value, k === 'weight' ? x.unit : undefined);
    const diff: Mention[] = [];
    for (const x of [...mentions.values()].sort((a, b) => a.at - b.at)) {
      if (x.cmp) continue;
      if (k === 'temperature' && x.unit && /^[CF]$/i.test(x.unit) && x.unit.toUpperCase() !== recUnit.toUpperCase()[0]) continue;
      if (k === 'weight' && x.unit && !/^(kg|g)$/i.test(x.unit)) continue;
      const val = valueOf(x);
      if (Number.isNaN(val) || [...kept, ...diff.map(valueOf)].some((r) => Math.abs(r - val) < 1e-9)) continue;
      if (others.some(([a, b]) => x.at >= a && x.at < b)) continue;
      const s = notes.lastIndexOf('\n', x.at - 1) + 1; const e = notes.indexOf('\n', x.at);
      if (NOT_SAME_READING.some((re) => re.test(foldText(notes.slice(s, e < 0 ? notes.length : e))))) continue;
      diff.push(x);
    }
    if (!diff.length) continue;
    const q = recs[0]; const keptText = `${q.value}${k === 'weight' ? ' ' + q.unit : ''}`;
    const field = v[k] ? `examination.vitals.${k}` : 'patient.weight';
    f.push({ rule: 'notes_contradiction', severity: 'warn', field, message: `Notes give ${keptText} and ${diff.map((d) => d.text).join(' and ')} for ${VITAL_NAMES[k]}; the record keeps ${keptText}. Check which is right.`, span: [diff[0].at, diff[0].end] });
  }
  return f;
}

/** The spans of one fact, by its factPaths path ("assessment.text" uses the assessment's own spans). */
export function factSpans(record: ClinicalRecord, path: string): Span[] {
  if (path === 'assessment.text') return record.assessment.source_spans;
  let x: any = record;
  for (const [, key, idx] of path.matchAll(/([a-z_]+)(?:\[(\d+)\])?/g)) { x = x?.[key]; if (idx !== undefined) x = x?.[Number(idx)]; }
  return x?.source_spans ?? [];
}

/** The sentence(s) around [a, b]: from the last newline or sentence end (".", "!", "?" before a space) before a to the next one after b. */
function spanSentence(notes: string, [a, b]: Span): string {
  while (a < b && /\s/.test(notes[a])) a++;
  while (b > a && /\s/.test(notes[b - 1])) b--;
  let s = a; while (s > 0 && notes[s - 1] !== '\n' && !(/\s/.test(notes[s - 1]) && /[.!?]/.test(notes[s - 2] ?? ''))) s--;
  let e = b; while (e < notes.length && notes[e] !== '\n' && !(/[.!?]/.test(notes[e]) && /\s/.test(notes[e + 1] ?? '\n'))) e++;
  return notes.slice(s, e);
}

/**
 * other_animal_fact (warn): a record fact (any factPaths item) whose span sits in a line or sentence
 * that clearly names another animal (OTHER_ANIMAL_MARKERS). Conservative: only the sentence holding the
 * span is read, so a housemate mentioned on another line ("lives with another dog") is left alone;
 * uncertain items are not facts and are not checked.
 */
export function validateOtherAnimal(record: ClinicalRecord, notes: string): Finding[] {
  const f: Finding[] = [];
  for (const path of factPaths(record)) for (const span of factSpans(record, path)) {
    const sentence = spanSentence(notes, span);
    if (!OTHER_ANIMAL_MARKERS.some((re) => re.test(foldText(sentence)))) continue;
    f.push({ rule: 'other_animal_fact', severity: 'warn', field: path, message: `This comes from a line about another animal ("${sentence.trim()}"). Check it belongs to this patient.`, span });
    break;
  }
  return f;
}

export function validateAll(record: ClinicalRecord, notes: string, header: PatientHeader): Finding[] {
  return [
    ...validateGrounding(record, notes),
    ...validateMedications(record, notes),
    ...validateStatus(record, notes),
    ...validateNotesContradiction(record, notes),
    ...validateOtherAnimal(record, notes),
    ...validatePatient(record, header),
    ...validatePlausibility(record, header),
  ];
}
