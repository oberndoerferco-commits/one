import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord, PatientHeader, type Span } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, validateNotesContradiction, type Finding } from '../src/validators.js';

/**
 * notes_contradiction (warn): the notes give a recorded vital twice with different values and the
 * record silently keeps one.
 */
type K = 'temperature' | 'heart_rate' | 'respiratory_rate' | 'weight' | 'crt_seconds';
const empty = () => ({
  schema_version: '0.2',
  patient: { name: null, species: null, breed: null, sex: null, neuter_status: null, age: null, weight: null },
  presenting_complaint: null, history: [] as any[],
  examination: { vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null } as Record<K, any>, findings: [] as any[] },
  diagnostics: [], assessment: { text: null, differentials: [], source_spans: [] }, treatments: [], medications: [],
  plan: { follow_up: null, instructions: [] }, missing: [], uncertain: [] as any[],
});
/** A record keeping one vital, whose span is the first occurrence of `line` in the notes. */
const rec = (notes: string, k: K, value: number, unit: string, line: string) => {
  const r = empty(); const i = notes.indexOf(line); if (i < 0) throw new Error(`"${line}" not in notes`);
  r.examination.vitals[k] = { value, unit, source_spans: [[i, i + line.length]] };
  return r;
};
const run = (notes: string, r: any): Finding[] => validateNotesContradiction(ClinicalRecord.parse(r), notes);
const check = (notes: string, k: K, value: number, unit: string, line: string) => run(notes, rec(notes, k, value, unit, line));

describe('notes_contradiction: two values for the same vital → warn', () => {
  it.each([
    ['en', 'T 38.6\nabdomen soft\nT 39.4', 'temperature', 38.6, 'C', 'T 38.6', '39.4'],
    ['en', 'HR 120\nmurmur 2/6\nheart rate 140', 'heart_rate', 120, '/min', 'HR 120', '140'],
    ['en', 'wt 4.2 kg\nBW 4.6 kg', 'weight', 4.2, 'kg', 'wt 4.2 kg', '4.6 kg'],
    ['en', 'CRT 2 s\nmm pink\nCRT 3 s', 'crt_seconds', 2, 's', 'CRT 2 s', '3'],
    ['de', 'T 38,6\nAbdomen weich\nTemperatur 39,4', 'temperature', 38.6, 'C', 'T 38,6', '39.4'],
    ['de', 'AF 24\nLunge frei\nAF 36', 'respiratory_rate', 24, '/min', 'AF 24', '36'],
    ['de', 'KGW 4,2 kg\nGewicht 4500 g', 'weight', 4.2, 'kg', 'KGW 4,2 kg', '4500 g'],
    ['de', 'KFZ 2 s\nSH rosa\nKFZ 3 s', 'crt_seconds', 2, 's', 'KFZ 2 s', '3'],
    ['it', 'temperatura 38,6\naddome trattabile\nT 39,4', 'temperature', 38.6, 'C', 'temperatura 38,6', '39.4'],
    ['it', 'FC 120\nsoffio 2/6\nfrequenza cardiaca 140', 'heart_rate', 120, '/min', 'FC 120', '140'],
    ['it', 'FR 24\nFR 30', 'respiratory_rate', 24, '/min', 'FR 24', '30'],
    ['it', 'peso 4,2 kg\nmucose rosee\n4,6 kg', 'weight', 4.2, 'kg', 'peso 4,2 kg', '4.6 kg'],
    ['it', 'TRC 2 s\nTRC 3', 'crt_seconds', 2, 's', 'TRC 2 s', '3'],
  ] as const)('%s: %j', (_l, notes, k, value, unit, line, other) => {
    const fs = check(notes, k, value, unit, line);
    expect(fs.map((f) => [f.rule, f.severity, f.field])).toEqual([['notes_contradiction', 'warn', `examination.vitals.${k}`]]);
    expect(fs[0].message).toContain(` and ${other} for `);
    expect(fs[0].message).toMatch(/the record keeps .*\. Check which is right\.$/);
    const [a, b] = fs[0].span as Span;
    expect(notes.slice(a, b).replace(',', '.')).toContain(other.split(' ')[0]);
  });
  it('message names both values and the one kept', () => {
    expect(check('T 38.6\nT 39.4', 'temperature', 38.6, 'C', 'T 38.6')[0].message).toBe('Notes give 38.6 and 39.4 for temperature; the record keeps 38.6. Check which is right.');
    expect(check('wt 4.2 kg\nwt 4.6 kg', 'weight', 4.2, 'kg', 'wt 4.2 kg')[0].message).toBe('Notes give 4.2 kg and 4.6 kg for weight; the record keeps 4.2 kg. Check which is right.');
  });
  it('a weight kept in patient.weight is checked too', () => {
    const notes = 'Bella, Katze, 3,8 kg\nKGW 4,1 kg'; const r = empty();
    (r.patient as any).weight = { value: 3.8, unit: 'kg', source_spans: [[14, 20]] };
    expect(run(notes, r).map((f) => f.field)).toEqual(['patient.weight']);
  });
});

describe('notes_contradiction: conservative', () => {
  it('the same value written twice, with decimal comma or in another unit, is no contradiction', () => {
    expect(check('T 38.6\nT 38.6', 'temperature', 38.6, 'C', 'T 38.6')).toEqual([]);
    expect(check('KGW 4,2 kg\nGewicht 4,20 kg', 'weight', 4.2, 'kg', 'KGW 4,2 kg')).toEqual([]);
    expect(check('KGW 4,2 kg\nGewicht 4200 g', 'weight', 4.2, 'kg', 'KGW 4,2 kg')).toEqual([]);
    expect(check('wt 34 g\nwt 0.034 kg', 'weight', 34, 'g', 'wt 34 g')).toEqual([]);
  });
  it.each([
    ['en', 'wt 4.2 kg\nwt 4.6 kg at last visit'], ['en', 'wt 4.2 kg\npreviously wt 4.6 kg'], ['en', 'wt 4.2 kg\nowner weighed her at home: 4.6 kg'],
    ['de', 'KGW 4,2 kg\nletzte Woche KGW 4,6 kg'], ['de', 'KGW 4,2 kg\nvorher KGW 4,6 kg'], ['de', 'KGW 4,2 kg\nzu Hause gewogen: KGW 4,6 kg'],
    ['it', 'peso 4,2 kg\npeso 4,6 kg alla visita precedente'], ['it', 'peso 4,2 kg\nprima peso 4,6 kg'], ['it', 'peso 4,2 kg\npesata a casa: peso 4,6 kg'],
  ])('%s: an earlier or home value is not a contradiction (%j)', (_l, notes) => {
    expect(check(notes, 'weight', 4.2, 'kg', notes.split('\n')[0])).toEqual([]);
  });
  it.each([
    ['en', 'T 39.5 on arrival\nT 38.9 after fluids', 'T 38.9'], ['de', 'T 38,9\nzu Hause T 39,5 gemessen', 'T 38,9'], ['it', 'T 38,9\na casa T 39,5', 'T 38,9'],
  ])('%s: a time course or owner-measured temperature is left alone', (_l, notes, line) => {
    expect(check(notes, 'temperature', 38.9, 'C', line)).toEqual([]);
  });
  it.each([
    ['en', 'T 37.6\ngrey mare in the next box (Sky) coughing, T 39.5, not our patient'],
    ['de', 'T 37,6\nSchimmelstute in der Nachbarbox hustet, T 39,5, nicht unser Patient'],
    ['it', 'T 37,6\nla cavalla nel box accanto tossisce, T 39,5, non è nostra paziente'],
    ['en', 'T 37.6\nother dog at home: T 39.5'],
  ])('%s: another animal\'s value is left alone', (_l, notes) => {
    expect(check(notes, 'temperature', 37.6, 'C', notes.split('\n')[0])).toEqual([]);
  });
  it('unlabelled or non-reading numbers do not count', () => {
    expect(check('T 38.6\nbloods incl. T4 taken', 'temperature', 38.6, 'C', 'T 38.6')).toEqual([]);
    expect(check('HF 100\nLahmheit HR Grad 2/5', 'heart_rate', 100, '/min', 'HF 100')).toEqual([]);
    expect(check('AF 24\nRR 120/80', 'respiratory_rate', 24, '/min', 'AF 24')).toEqual([]);
    expect(check('HR 100\nHR 100-120 during exam', 'heart_rate', 100, '/min', 'HR 100')).toEqual([]);
    expect(check('CRT 2 s\nCRT <3', 'crt_seconds', 2, 's', 'CRT 2 s')).toEqual([]);
    expect(check('wt 3.8 kg\nPepper 5.1 kg, vaccinated last month', 'weight', 3.8, 'kg', 'wt 3.8 kg')).toEqual([]);
    expect(check('wt 34 g\nlost 2 g in a week', 'weight', 34, 'g', 'wt 34 g')).toEqual([]);
    expect(check('wt 12 kg\nmeloxicam 0.1 mg/kg', 'weight', 12, 'kg', 'wt 12 kg')).toEqual([]);
  });
  it('a second value the record already carries elsewhere (uncertain, history) is not silent', () => {
    const notes = 'T 38.6\nT 39.4';
    const r = rec(notes, 'temperature', 38.6, 'C', 'T 38.6');
    r.uncertain.push({ field: 'examination.vitals.temperature', original_text: 'T 38.6 / T 39.4', reason: 'two temperatures', source_spans: [[0, 6], [7, 13]] });
    expect(run(notes, r)).toEqual([]);
  });
});

describe('eval cases', () => {
  const casesDir = new URL('../eval/cases/', import.meta.url);
  const ids = readdirSync(casesDir).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, '')).sort();
  const prep = (id: string) => { const c = JSON.parse(readFileSync(new URL(`${id}.json`, casesDir), 'utf8')); return { c, notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: c.fixture_record && !c.expect?.must_flag ? ClinicalRecord.parse(c.fixture_record) : null }; }; // seeded-error records are not gold

  it('no gold record raises notes_contradiction', () => {
    for (const id of ids) {
      const { record, notes, header } = prep(id); if (!record) continue;
      expect(validateAll(record, notes, header).filter((f) => f.rule === 'notes_contradiction'), id).toEqual([]);
    }
  });

  /** Add a second, different reading of each recorded vital to the gold notes; it must be flagged. */
  const LABEL: Record<string, Record<K, string>> = {
    en: { temperature: 'T', heart_rate: 'HR', respiratory_rate: 'RR', weight: 'wt', crt_seconds: 'CRT' },
    de: { temperature: 'T', heart_rate: 'HF', respiratory_rate: 'AF', weight: 'KGW', crt_seconds: 'KFZ' },
    it: { temperature: 'T', heart_rate: 'FC', respiratory_rate: 'FR', weight: 'peso', crt_seconds: 'TRC' },
  };
  it('a second reading added to the gold notes is flagged for every recorded vital (EN/DE/IT)', () => {
    let added = 0; const langs = new Set<string>();
    for (const id of ids) {
      const { c, record, notes, header } = prep(id); if (!record) continue;
      for (const k of Object.keys(LABEL.en) as K[]) {
        const q = record.examination.vitals[k]; if (!q) continue;
        const other = String(Math.round((q.value + 1) * 10) / 10);
        const written = c.language === 'en' ? other : other.replace('.', ',');
        const line = `${LABEL[c.language][k]} ${written}${k === 'weight' ? ' ' + q.unit : ''}`;
        const fs = validateAll(record, notes + '\n' + line, header).filter((f) => f.rule === 'notes_contradiction');
        expect(fs.map((f) => [f.field, f.severity]), `${id} ${line}`).toEqual([[`examination.vitals.${k}`, 'warn']]);
        added++; langs.add(c.language);
      }
    }
    expect(added).toBeGreaterThanOrEqual(80);
    expect([...langs].sort()).toEqual(['de', 'en', 'it']);
  });
});
