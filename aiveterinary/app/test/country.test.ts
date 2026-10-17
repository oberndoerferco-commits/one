import { describe, it, expect } from 'vitest';
import { z } from 'zod';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { countryMissing, VisitContext, provenance } from '../src/country.js';
import { renderConsultReport } from '../src/render.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };
const ctx = (o: Partial<z.input<typeof VisitContext>>) => VisitContext.parse({ country: 'DE', author: { name: 'Dr. Test' }, ...o });
const rules = (f: { rule: string }[]) => f.map((x) => x.rule);

describe('country field packs', () => {
  it('a record with dispensed medication and no dispensing data is flagged in Germany', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications.forEach((m) => (m.status = 'dispensed'));
    const f = countryMissing(r, header, ctx({ country: 'DE' }));
    expect(rules(f)).toContain('de_taehav_abgabebeleg');
    expect(f.some((x) => x.field.endsWith('.authorisation_number'))).toBe(true);
  });
  it('the same record is satisfied once the vet enters the dispensing record', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications.forEach((m) => { m.status = 'dispensed'; m.dose ??= 1; m.route ??= 'oral'; m.duration ??= '7 days'; });
    const dispensings = r.medications.map((_, i) => ({ medication_index: i, product: 'P', authorisation_number: '123', batch: 'B1', quantity: { value: 1, unit: 'pack' } }));
    const f = countryMissing(r, header, ctx({ country: 'DE', dispensings }));
    expect(rules(f).filter((x) => x.startsWith('de_'))).toEqual([]);
  });
  it('antibiotic without justification blocks everywhere', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications[0].status = 'dispensed';
    for (const country of ['DE', 'IT', 'CH', 'AT'] as const) {
      const f = countryMissing(r, header, ctx({ country, dispensings: [{ medication_index: 0, is_antibiotic: true, product: 'X', authorisation_number: '1', batch: 'b', quantity: { value: 1, unit: 'pack' } }] }));
      expect(f.some((x) => x.rule.endsWith('antibiotic_justification') && x.severity === 'block')).toBe(true);
    }
  });
  it('Italy wants microchip, codice fiscale and a REV number for prescriptions', () => {
    const { record, header } = prep('001-luna-vomiting');
    const r = structuredClone(record); if (r.medications[0]) r.medications[0].status = 'prescribed';
    const f = rules(countryMissing(r, header, ctx({ country: 'IT' })));
    expect(f).toContain('it_microchip'); expect(f).toContain('it_codice_fiscale');
    if (r.medications[0]) expect(f).toContain('it_rev_number');
  });
  it('missing author blocks in every country', () => {
    const { record, header } = prep('001-luna-vomiting');
    const f = countryMissing(record, header, VisitContext.parse({ country: 'AT' }));
    expect(f.find((x) => x.rule === 'author_required')?.severity).toBe('block');
  });
  it('declined care without a consent entry is flagged', () => {
    const { record, header } = prep('001-luna-vomiting');
    const r = structuredClone(record); r.diagnostics.push({ test: 'x-ray', status: 'declined', result: null, source_spans: [[0, 1]] });
    expect(rules(countryMissing(r, header, ctx({ country: 'CH' })))).toContain('declined_care_documented');
  });
  it('the report prints a provenance line with zero AI-added facts', () => {
    const { record, header } = prep('001-luna-vomiting');
    const p = provenance(record);
    expect(p.ai_added).toBe(0); expect(p.facts).toBeGreaterThan(0);
    const md = renderConsultReport(record, header, 'en', { extraMissing: [{ field: 'microchip', reason: 'test' }] });
    expect(md).toContain('Added by AI: 0'); expect(md).toContain('microchip: test');
  });
  it('declined items get their own signed section in every language', () => {
    const { record, header } = prep('001-luna-vomiting');
    const r = structuredClone(record); r.diagnostics.push({ test: 'abdominal x-ray', status: 'declined', result: null, source_spans: [[0, 1]] });
    expect(renderConsultReport(r, header, 'en')).toContain('## Declined care');
    expect(renderConsultReport(r, header, 'de')).toContain('Abgelehnte Maßnahmen');
    expect(renderConsultReport(r, header, 'it')).toContain('Abdominal x-ray');
    expect(renderConsultReport(record, header, 'en')).not.toContain('Declined care');
  });
});
