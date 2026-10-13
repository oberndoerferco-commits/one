import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes, findAbbreviations, detectLanguage } from '../src/normalize.js';
import { validateAll, validateDerivedText, requiredMissing, numbersIn } from '../src/validators.js';
import { renderConsultReport, renderMedicationTable } from '../src/render.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { c, notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

describe('schema', () => {
  it('accepts a well-formed record', () => { expect(() => prep('001-luna-vomiting')).not.toThrow(); });
  it('rejects a fact without source spans', () => {
    const { c } = prep('001-luna-vomiting');
    const bad = structuredClone(c.fixture_record); bad.history[0].source_spans = [];
    expect(() => ClinicalRecord.parse(bad)).toThrow();
  });
});

describe('validators: nothing you did not write', () => {
  it('passes a grounded record', () => {
    const { record, notes, header } = prep('001-luna-vomiting');
    expect(validateAll(record, notes, header).filter((f) => f.severity === 'block')).toEqual([]);
  });
  it('blocks an invented drug, dose and diagnosis', () => {
    const { record, notes, header } = prep('005-hallucinated-fixture');
    const rules = validateAll(record, notes, header).map((f) => f.rule);
    expect(rules).toContain('drug_not_in_notes');
    expect(rules).toContain('dose_not_in_notes');
    expect(rules).toContain('source_required');
  });
  it('blocks a number that is not in the notes', () => {
    const { record, notes, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.examination.vitals.temperature!.value = 39.2;
    expect(validateAll(r, notes, header).some((f) => f.rule === 'number_not_in_notes')).toBe(true);
  });
  it('accepts German decimal commas', () => {
    expect(numbersIn('T 38,6')).toContain('38.6');
  });
  it('flags pregnancy on a male patient', () => {
    const { record, notes, header } = prep('004-adversarial-pregnant-owner');
    const r = structuredClone(record); r.history.push({ finding: 'reproductive', value: 'pregnant', source_role: 'owner_reported', source_spans: [[0, 14]] });
    expect(validateAll(r, notes, header).some((f) => f.rule === 'patient_conflict')).toBe(true);
    // the correct fixture keeps the pregnancy under 'uncertain', which is quarantined and does not trip the check
    expect(validateAll(record, notes, header).some((f) => f.rule === 'patient_conflict')).toBe(false);
  });
  it('warns on an implausible temperature', () => {
    const { record, notes, header } = prep('001-luna-vomiting');
    const r = structuredClone(record); r.examination.vitals.temperature!.value = 3; // typo for 39
    const f = validateAll(r, 'temp 3', header);
    expect(f.some((x) => x.rule === 'implausible_value')).toBe(true);
  });
  it('blocks a derived text that adds a number', () => {
    const { record, notes } = prep('002-milo-otitis-de');
    expect(validateDerivedText('Give Surolan, 5 drops twice daily for 7 days. Recheck in 10 days.', record, notes).some((f) => f.rule === 'derived_number_not_in_record')).toBe(true);
    expect(validateDerivedText('Give Surolan, 5 drops twice daily for 7 days.', record, notes).filter((f) => f.severity === 'block')).toEqual([]);
  });
});

describe('missing-information flags', () => {
  it('lists the drug and results as missing for Luna', () => {
    const { record } = prep('001-luna-vomiting');
    const miss = requiredMissing(record, 'consult_report');
    expect(miss).toContain('medications[0].drug');
    expect(miss).toContain('diagnostics[0].result');
  });
  it('asks for weight when a dose exists without one', () => {
    const { record } = prep('002-milo-otitis-de');
    expect(requiredMissing(record, 'discharge')).toContain('patient.weight');
  });
});

describe('render', () => {
  it('renders the Luna report with flags and no invented content', () => {
    const { record, header } = prep('001-luna-vomiting');
    const txt = renderConsultReport(record, header, 'en');
    expect(txt).toContain('Temperature 39.1 °C');
    expect(txt).toContain('▲ Missing: drug');
    expect(txt).toContain('DRAFT');
    expect(txt).not.toMatch(/maropitant|cerenia/i);
  });
  it('renders a German medication table from structured fields', () => {
    const { record } = prep('002-milo-otitis-de');
    const t = renderMedicationTable(record.medications, 'de');
    expect(t).toContain('| Surolan | 5 Tropfen |');
    expect(t).toContain('▲ Fehlt: applikation');
  });
});

describe('normalize', () => {
  it('finds abbreviations without rewriting the text', () => {
    const notes = 'T 39.1 HR 120 bloods + US done';
    const a = findAbbreviations(notes);
    expect(a.map((x) => x.abbr)).toEqual(['T', 'HR', 'US']);
    expect(normalizeNotes(notes)).toBe(notes);
  });
  it('detects language roughly', () => {
    expect(detectLanguage('seit gestern Erbrechen und kein Durchfall')).toBe('de');
    expect(detectLanguage('vomito da ieri, nessun appetito')).toBe('it');
    expect(detectLanguage('vomiting since yesterday, no diarrhea')).toBe('en');
  });
});
