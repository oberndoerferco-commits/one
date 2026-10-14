import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { renderConsultReport, renderOwnerSummary, renderReferralLetter, renderMedicationTable } from '../src/render.js';
import { validateDerivedText } from '../src/validators.js';
import { normalizeNotes } from '../src/normalize.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

describe('documents from the approved record', () => {
  it('owner summary carries the identical medication table as the report', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications.forEach((m) => (m.status = 'dispensed'));
    const table = renderMedicationTable(r.medications, 'de');
    expect(renderOwnerSummary(r, header, 'de')).toContain(table);
    expect(renderConsultReport(r, header, 'de')).toContain(table);
  });
  it('owner summary adds no sentence that is not in the record', () => {
    const { record, header, notes } = prep('001-luna-vomiting');
    const md = renderOwnerSummary(record, header, 'en');
    // strip headings, flags and italics (code-owned), then every remaining line must be grounded
    const body = md.split('\n## ▲')[0];
    const prose = body.split('\n').filter((l) => l && !l.startsWith('#') && !l.startsWith('_') && !l.startsWith('|') && !l.startsWith('**') && !l.includes('▲'));
    const findings = validateDerivedText(prose.join('\n'), record, notes);
    expect(prose.length).toBeGreaterThan(2);
    expect(findings.filter((f) => f.severity === 'block')).toEqual([]);
  });
  it('referral letter flags a missing referral reason and accepts a stated one', () => {
    const { record, header } = prep('008-adversarial-it-performed-vs-planned');
    const without = renderReferralLetter(record, header, 'it');
    expect(without).toContain('Motivo dell\'invio non indicato');
    const withReason = renderReferralLetter(record, header, 'it', { reason: 'valutazione ortopedica per displasia' });
    expect(withReason).toContain('Valutazione ortopedica per displasia');
    expect(withReason).not.toContain('non indicato nelle note');
  });
  it('declined items appear under their own heading in the owner summary', () => {
    const { record, header } = prep('006-adversarial-dose-not-given');
    const md = renderOwnerSummary(record, header, 'en');
    expect(md).toContain('## Discussed and declined');
    expect(md).toContain('meloxicam');
    expect(md).not.toContain('## Medication to give');
  });
  it('dose checklist parses common frequency and duration forms and refuses unclear ones', async () => {
    const { parseDosesPerDay, parseDurationDays, renderDoseChecklist } = await import('../src/render.js');
    expect(parseDosesPerDay('2x tgl')).toBe(2); expect(parseDosesPerDay('BID')).toBe(2); expect(parseDosesPerDay('ogni 8 ore')).toBe(3); expect(parseDosesPerDay('once daily')).toBe(1); expect(parseDosesPerDay('as needed')).toBeNull();
    expect(parseDurationDays('7 Tage')).toBe(7); expect(parseDurationDays('10 giorni')).toBe(10); expect(parseDurationDays('2 weeks')).toBe(14); expect(parseDurationDays('until recheck')).toBeNull();
    const meds: any = [{ drug: 'Surolan', class_as_written: null, dose: 5, dose_unit: 'drops', route: 'ear', frequency: '2x tgl', duration: '7 Tage', status: 'dispensed', source_spans: [[0, 1]] }, { drug: 'X', class_as_written: null, dose: null, dose_unit: null, route: null, frequency: 'as needed', duration: null, status: 'prescribed', source_spans: [[0, 1]] }];
    const md = renderDoseChecklist(meds, 'de');
    expect(md).toContain('| Tag | morgens | abends |'); expect((md.match(/☐/g) ?? []).length).toBe(14); expect(md).toContain('nicht eindeutig');
  });
  it('prescription lists each dispensed medicine and flags what the keeper record lacks', async () => {
    const { renderPrescription } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications.forEach((m) => (m.status = 'dispensed'));
    const bare = renderPrescription(r, header, VisitContext.parse({ country: 'DE' }), 'de', { date: '2026-10-14' });
    expect(bare).toContain('# Tierärztliche Verschreibung');
    expect(bare).toContain('Name und Anschrift'); expect(bare).toContain('abzugebende Menge'); expect(bare).toContain('verschreibende');
    const full = renderPrescription(r, header, VisitContext.parse({ country: 'DE', microchip: '276000000000001', owner: { name: 'Anna Beispiel, Musterstraße 1, Berlin' }, author: { name: 'Dr. Vet', registration: 'TÄK Berlin' }, dispensings: [{ medication_index: 0, product: 'Surolan Ohrentropfen', quantity: { value: 1, unit: 'Flasche' }, authorisation_number: '12345.00.00', batch: 'L123' }] }), 'de', { date: '2026-10-14' });
    expect(full).toContain('## Surolan Ohrentropfen'); expect(full).toContain('1 Flasche'); expect(full).toContain('Lot L123'); expect(full).not.toContain('## ▲');
    const luna = prep('001-luna-vomiting');
    expect(renderPrescription(luna.record, luna.header, VisitContext.parse({ country: 'IT' }), 'it')).toContain('Nessun medicinale');
  });
});
