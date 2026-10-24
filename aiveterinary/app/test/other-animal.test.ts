import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord, PatientHeader, type Span } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, validateOtherAnimal, OTHER_ANIMAL_MARKERS, NOT_SAME_READING, type Finding } from '../src/validators.js';

/**
 * other_animal_fact (warn): a record fact whose source line or sentence clearly names another animal
 * ("other dog", "not our patient", "Nachbarbox", "altro gatto" …).
 */
const empty = () => ({
  schema_version: '0.2',
  patient: { name: null, species: null, breed: null, sex: null, neuter_status: null, age: null, weight: null },
  presenting_complaint: null, history: [] as any[],
  examination: { vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null } as Record<string, any>, findings: [] as any[] },
  diagnostics: [] as any[], assessment: { text: null as string | null, differentials: [] as any[], source_spans: [] as Span[] }, treatments: [] as any[], medications: [] as any[],
  plan: { follow_up: null as any, instructions: [] as any[] }, missing: [], uncertain: [] as any[],
});
const at = (notes: string, text: string): Span => { const i = notes.indexOf(text); if (i < 0) throw new Error(`"${text}" not in notes`); return [i, i + text.length]; };
const run = (notes: string, r: any): Finding[] => validateOtherAnimal(ClinicalRecord.parse(r), notes);
/** A record with one history item pointing at `text`. */
const hist = (notes: string, text: string) => { const r = empty(); r.history.push({ finding: 'history', value: text, source_role: 'owner_reported', source_spans: [at(notes, text)] }); return run(notes, r); };

describe('other_animal_fact: a fact taken from a line about another animal → warn', () => {
  it.each([
    ['en', 'Rex, dog\nother dog in the house has diarrhoea\nT 38.6', 'has diarrhoea'],
    ['en', 'lame LH\ngrey mare in the next box coughing, not our patient', 'coughing'],
    ['en', 'eating well. Another cat vomited twice yesterday. T 38.6', 'vomited twice yesterday'],
    ['de', 'Bello, Hund\nder andere Hund hat Durchfall\nT 38,6', 'hat Durchfall'],
    ['de', 'Lahmheit hinten links\nStute in der Nachbarbox hustet, nicht unser Patient', 'hustet'],
    ['de', 'frisst gut. Die zweite Katze hat gestern erbrochen. T 38,6', 'hat gestern erbrochen'],
    ['it', 'Fido, cane\nl\'altro cane ha diarrea\nT 38,6', 'ha diarrea'],
    ['it', 'zoppia posteriore sinistra\nla cavalla nel box accanto tossisce, non è nostra paziente', 'tossisce'],
    ['it', 'mangia bene. L\'altro gatto ha vomitato ieri. T 38,6', 'ha vomitato ieri'],
  ])('%s: %j', (_l, notes, text) => {
    const fs = hist(notes, text);
    expect(fs.map((f) => [f.rule, f.severity, f.field])).toEqual([['other_animal_fact', 'warn', 'history[0]']]);
    expect(fs[0].message).toMatch(/^This comes from a line about another animal \(".+"\)\. Check it belongs to this patient\.$/);
    expect(fs[0].span).toEqual(at(notes, text));
  });

  it('message quotes the sentence the span sits in', () => {
    const notes = 'eating well. Another cat vomited twice yesterday. T 38.6';
    expect(hist(notes, 'vomited twice yesterday')[0].message).toBe('This comes from a line about another animal ("Another cat vomited twice yesterday"). Check it belongs to this patient.');
  });

  it('every fact kind is checked (vitals, findings, diagnostics, treatments, medications, assessment, plan)', () => {
    const notes = 'other dog: T 39.5, HR 140, cough, x-ray done, fluids given, amoxicillin given, pneumonia, recheck 3 days, rest';
    const s = (t: string) => [at(notes, t)];
    const r = empty();
    r.presenting_complaint = { text: 'cough', source_role: 'owner_reported', source_spans: s('cough') } as any;
    r.examination.vitals.temperature = { value: 39.5, unit: 'C', source_spans: s('T 39.5') };
    r.examination.findings.push({ system: 'respiratory', text: 'cough', source_role: 'vet_observed', source_spans: s('cough') });
    r.diagnostics.push({ test: 'x-ray', result: null, status: 'performed', source_spans: s('x-ray done') });
    r.treatments.push({ type: 'procedure', text: 'fluids', status: 'performed', source_spans: s('fluids given') });
    r.medications.push({ drug: 'amoxicillin', class_as_written: null, dose: null, dose_unit: null, route: null, frequency: null, duration: null, status: 'performed', source_spans: s('amoxicillin given') });
    r.assessment = { text: 'pneumonia', differentials: [{ text: 'pneumonia', source_spans: s('pneumonia') }], source_spans: s('pneumonia') };
    r.plan.follow_up = { text: 'recheck 3 days', interval: { value: 3, unit: 'day' }, source_spans: s('recheck 3 days') };
    r.plan.instructions.push({ text: 'rest', source_spans: s('rest') });
    expect(run(notes, r).map((f) => f.field)).toEqual([
      'presenting_complaint', 'examination.vitals.temperature', 'examination.findings[0]', 'diagnostics[0]', 'assessment.text',
      'assessment.differentials[0]', 'treatments[0]', 'medications[0]', 'plan.follow_up', 'plan.instructions[0]',
    ]);
  });
});

describe('other_animal_fact: conservative', () => {
  it.each([
    ['en', 'lives with another dog\nvomiting 2 days', 'vomiting 2 days'],
    ['en', 'lives with another dog. Vomiting 2 days.', 'Vomiting 2 days'],
    ['en', 'no contact with other dogs\nvomiting 2 days', 'vomiting 2 days'],
    ['en', 'no other pets\nvomiting 2 days', 'vomiting 2 days'],
    ['de', 'lebt mit einem anderen Hund\nerbricht seit 2 Tagen', 'erbricht seit 2 Tagen'],
    ['de', 'lebt mit einem anderen Hund. Erbricht seit 2 Tagen.', 'Erbricht seit 2 Tagen'],
    ['de', 'keine anderen Tiere im Haushalt\nerbricht seit 2 Tagen', 'erbricht seit 2 Tagen'],
    ['it', 'vive con un altro cane\nvomito da 2 giorni', 'vomito da 2 giorni'],
    ['it', 'vive con un altro cane. Vomito da 2 giorni.', 'Vomito da 2 giorni'],
    ['it', 'nessun altri animali in casa\nvomito da 2 giorni', 'vomito da 2 giorni'],
  ])('%s: a housemate on another line or sentence is left alone (%j)', (_l, notes, text) => {
    expect(hist(notes, text)).toEqual([]);
  });
  it('a decimal or an abbreviation does not end the sentence early, and the line is the limit', () => {
    expect(hist('other dog T 39.5 coughing', 'coughing').map((f) => f.rule)).toEqual(['other_animal_fact']);
    expect(hist('other dog fine\nT 39.5 coughing', 'coughing')).toEqual([]);
  });
  it('the markers are shared with notes_contradiction, not duplicated', () => {
    for (const re of OTHER_ANIMAL_MARKERS) expect(NOT_SAME_READING).toContain(re);
  });
});

describe('eval cases', () => {
  const casesDir = new URL('../eval/cases/', import.meta.url);
  const ids = readdirSync(casesDir).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, '')).sort();
  const prep = (id: string) => { const c = JSON.parse(readFileSync(new URL(`${id}.json`, casesDir), 'utf8')); return { c, notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: c.fixture_record && !c.expect?.must_flag ? ClinicalRecord.parse(c.fixture_record) : null }; }; // seeded-error records are not gold
  const fold = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');

  it('no gold record raises the rule, not even as a warning', () => {
    let n = 0;
    for (const id of ids) {
      const { record, notes, header } = prep(id); if (!record) continue; n++;
      expect(validateAll(record, notes, header).filter((f) => f.rule === 'other_animal_fact'), id).toEqual([]);
    }
    expect(n).toBeGreaterThanOrEqual(90);
  });

  it('a fact taken from an other-animal line in the gold notes is flagged (EN/DE/IT)', () => {
    let swapped = 0; const langs = new Set<string>();
    for (const id of ids) {
      const { c, record, notes, header } = prep(id); if (!record) continue;
      let off = 0;
      for (const line of notes.split('\n')) {
        const span: Span = [off, off + line.length]; off += line.length + 1;
        if (!OTHER_ANIMAL_MARKERS.some((re) => re.test(fold(line)))) continue;
        const r = structuredClone(record) as any;
        r.history.push({ finding: 'history', value: line, source_role: 'owner_reported', source_spans: [span] });
        r.examination.findings.push({ system: 'general', text: line, source_role: 'vet_observed', source_spans: [span] });
        const fs = validateAll(ClinicalRecord.parse(r), notes, header).filter((f) => f.rule === 'other_animal_fact');
        expect(fs.map((f) => [f.field, f.severity]), id).toEqual([[`history[${r.history.length - 1}]`, 'warn'], [`examination.findings[${r.examination.findings.length - 1}]`, 'warn']]);
        swapped++; langs.add(c.language);
      }
    }
    expect(swapped).toBeGreaterThanOrEqual(9);
    expect([...langs].sort()).toEqual(['de', 'en', 'it']);
  });

  it('181–183: the other horse\'s temperature kept as the patient\'s is flagged', () => {
    for (const id of ['181-gen-horse-vaccine-other-horse-en', '182-gen-horse-vaccine-other-horse-de', '183-gen-horse-vaccine-other-horse-it']) {
      const { record, notes, header } = prep(id);
      const r = structuredClone(record) as any;
      const i = notes.search(/T 39[.,]5/);
      r.examination.vitals.temperature = { value: 39.5, unit: 'C', source_spans: [[i, i + 6]] };
      const fs = validateAll(ClinicalRecord.parse(r), notes, header).filter((f) => f.rule === 'other_animal_fact');
      expect(fs.map((f) => [f.field, f.severity]), id).toEqual([['examination.vitals.temperature', 'warn']]);
    }
  });
});
