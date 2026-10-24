import { describe, it, expect } from 'vitest';
import { z } from 'zod';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { countryMissing, isFoodProducing, VisitContext, provenance } from '../src/country.js';
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

describe('dispensing records per country (TAMG § 68, TAMV art. 25–27, D.Lgs. 218/2023 art. 37)', () => {
  const dispensed = () => { const { record, header } = prep('002-milo-otitis-de'); const r = structuredClone(record); r.medications.forEach((m) => (m.status = 'dispensed')); return { r, header }; };
  const fields = (f: { field: string; rule: string }[], rule: string) => f.filter((x) => x.rule === rule).map((x) => x.field.replace(/^dispensings\[\d+\]\./, ''));
  it('Austria asks for the authorisation number and keeps the batch, for a dog too', () => {
    const { r, header } = dispensed();
    expect(header.species).toBe('dog');
    const got = new Set(fields(countryMissing(r, header, ctx({ country: 'AT' })), 'at_tamg_abgabe'));
    expect([...got].sort()).toEqual(['authorisation_number', 'batch', 'product', 'quantity']);
    const full = r.medications.map((_, i) => ({ medication_index: i, product: 'P', authorisation_number: '8-001', batch: 'B1', quantity: { value: 1, unit: 'pack' } }));
    expect(rules(countryMissing(r, header, ctx({ country: 'AT', dispensings: full })))).not.toContain('at_tamg_abgabe');
  });
  it('Switzerland: no TAMV dispensing flag for a dog or cat, still flagged for a horse or a stated farm animal', () => {
    const { r, header } = dispensed();
    expect(rules(countryMissing(r, header, ctx({ country: 'CH' })))).not.toContain('ch_tamv_abgabe');
    expect(rules(countryMissing(r, { ...header, species: 'cat' }, ctx({ country: 'CH' })))).not.toContain('ch_tamv_abgabe');
    const horse = countryMissing(r, { ...header, species: 'horse' }, ctx({ country: 'CH' }));
    expect(new Set(fields(horse, 'ch_tamv_abgabe'))).toEqual(new Set(['product', 'quantity']));
    expect(horse.filter((x) => x.rule === 'ch_tamv_abgabe').every((x) => x.severity === 'warn')).toBe(true);
    expect(rules(countryMissing(r, { ...header, species: 'horse' }, ctx({ country: 'CH', food_producing: false })))).not.toContain('ch_tamv_abgabe');
    expect(rules(countryMissing(r, header, ctx({ country: 'CH', food_producing: true })))).toContain('ch_tamv_abgabe');
  });
  it('Switzerland keeps the IS ABV antibiotic flags for pets', () => {
    const { r, header } = dispensed();
    const f = countryMissing(r, header, ctx({ country: 'CH', dispensings: [{ medication_index: 0, is_antibiotic: true }] }));
    expect(rules(f)).toContain('ch_antibiotic_justification'); expect(rules(f)).toContain('ch_isabv_pack');
  });
  it('isFoodProducing: dogs, cats and ferrets never; horses unless the vet says otherwise', () => {
    expect(isFoodProducing({ species: 'dog' }, { food_producing: null })).toBe(false);
    expect(isFoodProducing({ species: 'ferret' }, { food_producing: null })).toBe(false);
    expect(isFoodProducing({ species: 'horse' }, { food_producing: null })).toBe(true);
    expect(isFoodProducing({ species: 'horse' }, { food_producing: false })).toBe(false);
    expect(VisitContext.parse({ country: 'CH' }).food_producing).toBeNull();
  });
  it('Italy flags the quantity handed over from stock (scarico within 7 days), not for a prescription', () => {
    const { r, header } = dispensed();
    const f = countryMissing(r, header, ctx({ country: 'IT' }));
    expect(f.filter((x) => x.rule === 'it_scarico_quantita').length).toBe(r.medications.length);
    expect(f.find((x) => x.rule === 'it_scarico_quantita')?.severity).toBe('warn');
    const withQty = r.medications.map((_, i) => ({ medication_index: i, quantity: { value: 1, unit: 'confezione' } }));
    expect(rules(countryMissing(r, header, ctx({ country: 'IT', dispensings: withQty })))).not.toContain('it_scarico_quantita');
    const rx = structuredClone(r); rx.medications.forEach((m) => (m.status = 'prescribed'));
    expect(rules(countryMissing(rx, header, ctx({ country: 'IT' })))).not.toContain('it_scarico_quantita');
  });
  it('the changed reasons exist in all three languages', () => {
    const { r, header } = dispensed();
    const c = ctx({ country: 'IT' });
    for (const lang of ['en', 'de', 'it'] as const) {
      const f = countryMissing(r, header, c, lang);
      expect(f.find((x) => x.rule === 'it_scarico_quantita')?.reason).toContain('218/2023');
      expect(f.find((x) => x.rule === 'it_codice_fiscale')?.reason).toContain('Sistema TS');
      const at = countryMissing(r, header, ctx({ country: 'AT' }), lang).find((x) => x.rule === 'at_tamg_abgabe')?.reason;
      expect(at).toContain('§ 68'); expect(at).toContain('103(3)');
      const ch = countryMissing(r, { ...header, species: 'horse' }, ctx({ country: 'CH' }), lang).find((x) => x.rule === 'ch_tamv_abgabe')?.reason;
      expect(ch).toContain('25–27'); expect(ch).toContain('Nutztiere');
    }
  });
});

describe('country flag language', () => {
  it('keeps the English reasons by default and translates them when asked, rule ids unchanged', () => {
    const { record: r, header } = prep('003-gatto-inappetenza-it');
    const ctxIT = VisitContext.parse({ country: 'IT' });
    const en = countryMissing(r, header, ctxIT);
    const it_ = countryMissing(r, header, ctxIT, 'it');
    const de = countryMissing(r, header, ctxIT, 'de');
    expect(it_.map((f) => [f.field, f.rule, f.severity])).toEqual(en.map((f) => [f.field, f.rule, f.severity]));
    expect(de.map((f) => f.rule)).toEqual(en.map((f) => f.rule));
    expect(en.find((f) => f.rule === 'it_codice_fiscale')?.reason).toBe('Codice fiscale of the owner (the person paying) is needed for the invoice, the REV and the Sistema TS expense data (D.M. MEF 1/9/2016 art. 2; D.M. RGS 16/9/2016 art. 2 c. 2)');
    expect(it_.find((f) => f.rule === 'it_codice_fiscale')?.reason).toBe('Il codice fiscale del proprietario (di chi paga) serve per la fattura, la REV e l\'invio delle spese al Sistema TS (D.M. MEF 1/9/2016 art. 2; D.M. RGS 16/9/2016 art. 2 c. 2)');
    for (const f of [...it_, ...de]) expect(f.reason).not.toBe(en.find((e) => e.rule === f.rule && e.field === f.field)?.reason);
  });
});
