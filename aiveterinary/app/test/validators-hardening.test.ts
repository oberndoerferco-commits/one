import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, drugInText, supportedBy, ROUTE_EQUIVALENTS, FREQUENCY_EQUIVALENTS, type Finding } from '../src/validators.js';

/**
 * Hardening of the anti-hallucination validators (audit gaps A–D). Each test loads a real
 * eval case, mutates its gold record the way a model could, and expects a block.
 */
const casesDir = new URL('../eval/cases/', import.meta.url);
const load = (id: string) => JSON.parse(readFileSync(new URL(`${id}.json`, casesDir), 'utf8'));
const prep = (id: string) => { const c = load(id); return { c, notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };
const blocks = (fs: Finding[]) => fs.filter((f) => f.severity === 'block');
/** Mutate the gold record of `id` and return the blocking findings. */
const mutate = (id: string, fn: (r: any, notes: string) => void) => {
  const { record, notes, header } = prep(id);
  const r = structuredClone(record); fn(r, notes);
  return blocks(validateAll(ClinicalRecord.parse(r), notes, header));
};
const spanOf = (notes: string, text: string): [number, number] => { const i = notes.indexOf(text); if (i < 0) throw new Error(`"${text}" not in notes`); return [i, i + text.length]; };
const has = (fs: Finding[], rule: string, field?: string) => fs.some((f) => f.rule === rule && (field == null || f.field === field));

const NEW_RULES = ['number_not_in_source', 'text_number_not_in_source', 'dose_not_in_source', 'duration_not_in_source', 'route_not_in_source', 'frequency_not_in_source', 'drug_not_in_source'];

describe('gold records stay clean', () => {
  const ids = readdirSync(casesDir).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, '')).sort();
  it('covers all 98 cases', () => { expect(ids.length).toBe(98); });
  for (const id of ids) {
    const { c, record, notes, header } = prep(id);
    if (c.expect?.fixture_must_fail) continue;
    it(`${id}: no blocking finding`, () => { expect(blocks(validateAll(record, notes, header))).toEqual([]); });
  }
  it('the must-fail fixture 005 still fails for its original reasons', () => {
    const { record, notes, header } = prep('005-hallucinated-fixture');
    const rules = validateAll(record, notes, header).map((f) => f.rule);
    for (const r of ['drug_not_in_notes', 'dose_not_in_notes', 'source_required']) expect(rules).toContain(r);
  });
  it('no gold record (005 aside) raises any of the new rules, not even as a warning', () => {
    for (const id of ids) {
      const { c, record, notes, header } = prep(id);
      if (c.expect?.fixture_must_fail) continue;
      expect(validateAll(record, notes, header).filter((f) => NEW_RULES.includes(f.rule)), id).toEqual([]);
    }
  });
});

describe('A. numbers must be in the text the fact points to', () => {
  it('follow-up "recheck next week" given interval 1 week blocks, although "1 week" is elsewhere', () => {
    const b = mutate('148-gen-owner-vs-vet-lameness-en', (r, notes) => { expect(notes).toContain('for 1 week'); r.plan.follow_up.interval = { value: 1, unit: 'week' }; });
    expect(has(b, 'number_not_in_source', 'plan.follow_up.interval')).toBe(true);
  });
  it("another horse's temperature (39.5) as the patient's blocks", () => {
    const b = mutate('181-gen-horse-vaccine-other-horse-en', (r) => { r.examination.vitals.temperature.value = 39.5; });
    expect(has(b, 'number_not_in_source', 'examination.vitals.temperature')).toBe(true);
  });
  it("another cat's weight (5.1 kg) as the patient's blocks, in vitals and in patient.weight", () => {
    expect(has(mutate('154-gen-other-cat-household-en', (r) => { r.examination.vitals.weight.value = 5.1; }), 'number_not_in_source', 'examination.vitals.weight')).toBe(true);
    const b = mutate('154-gen-other-cat-household-en', (r) => { r.patient.weight = { value: 5.1, unit: 'kg', source_spans: r.examination.vitals.weight.source_spans }; });
    expect(has(b, 'number_not_in_source', 'patient.weight')).toBe(true);
  });
  it('German decimal comma in the span still matches (KGW 3,8 kg → 3.8)', () => {
    const { record, notes, header } = prep('155-gen-other-cat-household-de');
    expect(record.examination.vitals.weight!.value).toBe(3.8);
    expect(blocks(validateAll(record, notes, header))).toEqual([]);
  });
  it('a vital whose span covers only the label still passes when the number is on the same line', () => {
    const b = mutate('181-gen-horse-vaccine-other-horse-en', (r, notes) => { const [a] = spanOf(notes, 'T 37.6'); r.examination.vitals.temperature.source_spans = [[a, a + 1]]; });
    expect(b).toEqual([]);
  });
  it('a diagnostic result number taken from elsewhere blocks', () => {
    const b = mutate('103-gen-otitis-cat-en', (r) => { r.diagnostics[0].result = 'yeast ++, 7 per field'; });
    expect(has(b, 'number_not_in_source', 'diagnostics[0].result')).toBe(true);
  });
  it('a medication dose or duration taken from elsewhere blocks', () => {
    expect(has(mutate('103-gen-otitis-cat-en', (r) => { r.medications[0].dose = 10; r.medications[0].dose_unit = 'drops'; }), 'dose_not_in_source', 'medications[0].dose')).toBe(true);
    expect(has(mutate('103-gen-otitis-cat-en', (r) => { r.medications[0].duration = '10 days'; }), 'duration_not_in_source', 'medications[0].duration')).toBe(true);
  });
  it('a number not in the notes at all still reports number_not_in_notes', () => {
    expect(has(mutate('002-milo-otitis-de', (r) => { r.examination.vitals.temperature.value = 39.2; }), 'number_not_in_notes')).toBe(true);
  });
});

describe('B. numbers inside free text must be in the item\'s own span', () => {
  it('"about two weeks" rewritten as "14 days" blocks', () => {
    const b = mutate('178-gen-dictated-cough-murmur-en', (r) => { r.presenting_complaint.text = 'coughing at night for 14 days'; });
    expect(has(b, 'text_number_not_in_source', 'presenting_complaint.text')).toBe(true);
  });
  it('a number borrowed from another line blocks in history, findings, treatments, instructions and differentials', () => {
    // case 100: "since 3 days" is in the complaint, "14" in the follow-up
    const id = '100-gen-lameness-en';
    expect(has(mutate(id, (r) => { r.history[0].value = 'eating normally for 3 days'; }), 'text_number_not_in_source', 'history[0].value')).toBe(true);
    expect(has(mutate(id, (r) => { r.examination.findings[0].text = 'RH lameness grade 3/5, pain on stifle extension'; }), 'text_number_not_in_source', 'examination.findings[0].text')).toBe(true);
    expect(has(mutate(id, (r) => { r.treatments[0].text = 'strict rest 14 days, lead walks only'; }), 'text_number_not_in_source', 'treatments[0].text')).toBe(true);
    expect(has(mutate('106-gen-diarrhoea-declined-en', (r) => { r.plan.instructions[0].text = 'bland diet 48 hours, water always available'; }), 'text_number_not_in_source', 'plan.instructions[0].text')).toBe(true);
    expect(has(mutate('115-gen-rabbit-anorexia-en', (r) => { r.assessment.differentials[0].text = 'gastrointestinal stasis 38'; }), 'text_number_not_in_source', 'assessment.differentials[0].text')).toBe(true);
  });
  it('numbers written in the span itself pass (Triadan numbers, grades)', () => {
    const { record, notes, header } = prep('011-dental-de-triadan');
    expect(blocks(validateAll(record, notes, header))).toEqual([]);
  });
});

describe('C. route and frequency must be supported by the medication\'s span', () => {
  it('an invented "s.c." on a drug-only medication blocks', () => {
    const b = mutate('142-gen-shorthand-gastro-en', (r) => { r.medications[0].route = 's.c.'; });
    expect(has(b, 'route_not_in_source', 'medications[0].route')).toBe(true);
  });
  it('a route that contradicts the span blocks (po for an s.c. vaccine)', () => {
    expect(has(mutate('109-gen-cat-vaccine-en', (r) => { r.medications[0].route = 'po'; }), 'route_not_in_source')).toBe(true);
  });
  it('explicit route equivalents pass', () => {
    for (const route of ['subcutaneous', 'sc', 'SC', 'subkutan', 'sottocute']) expect(mutate('109-gen-cat-vaccine-en', (r) => { r.medications[0].route = route; }), route).toEqual([]);
    expect(mutate('163-gen-typos-drug-finding-en', (r) => { r.medications[0].route = 'oral'; })).toEqual([]);
    expect(mutate('105-gen-otitis-cat-it', (r) => { r.medications[0].route = 'auricular'; })).toEqual([]);
    expect(supportedBy('i.v.', 'Buscopan iv given', ROUTE_EQUIVALENTS)).toBe(true);
    expect(supportedBy('intramuscular', 'vaccine given i.m. left neck', ROUTE_EQUIVALENTS)).toBe(true);
    expect(supportedBy('topical', 'Floh-Spot-on abgegeben, topisch, monatlich', ROUTE_EQUIVALENTS)).toBe(true);
    expect(supportedBy('iv', 'Buscopan im given', ROUTE_EQUIVALENTS)).toBe(false);
  });
  it('a frequency not in the span blocks (was a warning)', () => {
    expect(has(mutate('103-gen-otitis-cat-en', (r) => { r.medications[0].frequency = 'three times daily'; }), 'frequency_not_in_source')).toBe(true);
    expect(has(mutate('142-gen-shorthand-gastro-en', (r) => { r.medications[0].frequency = 'once daily'; }), 'frequency_not_in_source')).toBe(true);
  });
  it('explicit frequency equivalents pass', () => {
    for (const fq of ['bid', 'BID', 'b.i.d.', 'twice daily', '2x täglich', 'due volte al giorno', 'q12h']) expect(mutate('103-gen-otitis-cat-en', (r) => { r.medications[0].frequency = fq; }), fq).toEqual([]);
    expect(supportedBy('twice daily', 'Surolan 5 Tropfen 2x tgl 7 Tage', FREQUENCY_EQUIVALENTS)).toBe(true);
    expect(supportedBy('bid', 'Surolan 3x täglich', FREQUENCY_EQUIVALENTS)).toBe(false);
  });
});

describe('D. drug names must match the span, not just a prefix', () => {
  it('"Surolan" → "Surolam" blocks', () => {
    expect(has(mutate('103-gen-otitis-cat-en', (r) => { r.medications[0].drug = 'Surolam'; }), 'drug_not_in_notes', 'medications[0].drug')).toBe(true);
  });
  it('a real drug from another line of the notes blocks', () => {
    const b = mutate('160-gen-full-vs-drug-only-meds-en', (r) => { r.medications[1].drug = 'Surolan'; });
    expect(has(b, 'drug_not_in_source', 'medications[1].drug')).toBe(true);
  });
  it('case, diacritics and punctuation are ignored; one edit is tolerated only for names of ≥ 8 characters', () => {
    expect(drugInText('surolan', 'Surolan auricular twice daily 7 days')).toBe(true);
    expect(drugInText('Floh Spot-on', 'Floh-Spot-on abgegeben')).toBe(true);
    expect(drugInText('Metamizol Natrium', 'Metamizol-Natrium 0,5 ml s.c. gegeben')).toBe(true);
    expect(drugInText('Surolam', 'Surolan auricular')).toBe(false);
    expect(drugInText('Metcam', 'Metacam po prescribed')).toBe(false);
    expect(drugInText('Doxycyclin', 'Doxycycline 10 mg/kg')).toBe(true);
    expect(drugInText('Meloxicam', 'Meloxicamm')).toBe(true);
    expect(drugInText('Mel', 'meloxicam')).toBe(false);
  });
});
