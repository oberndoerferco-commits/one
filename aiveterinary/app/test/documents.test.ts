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
  it('vaccination entry needs batch and validity from the dispensing record', async () => {
    const { renderVaccinationEntry } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('001-luna-vomiting');
    const r = structuredClone(record);
    r.medications.push({ drug: 'rabies vaccine', class_as_written: null, dose: 1, dose_unit: 'ml', route: 's.c.', frequency: null, duration: null, status: 'performed', source_spans: [[0, 1]] });
    const bare = renderVaccinationEntry(r, header, VisitContext.parse({ country: 'IT', author: { name: 'Dr. A' } }), 'it', { date: '2026-10-14' });
    expect(bare).toContain('| rabies vaccine | 2026-10-14 | ▲'); expect(bare).toContain('lotto'); expect(bare).toContain('microchip');
    const full = renderVaccinationEntry(r, header, VisitContext.parse({ country: 'IT', microchip: '380260000000001', author: { name: 'Dr. A', registration: 'Ordine MI 123' }, dispensings: [{ medication_index: r.medications.length - 1, product: 'Nobivac Rabies', batch: 'A123B', site: 'sc dx', valid_until: '2029-10-14' }] }), 'it', { date: '2026-10-14' });
    expect(full).toContain('| Nobivac Rabies | 2026-10-14 | A123B | sc dx | 2029-10-14 |'); expect(full).not.toContain('## ▲');
    expect(renderVaccinationEntry(record, header, VisitContext.parse({ country: 'DE', author: { name: 'x' }, microchip: '1' }), 'de')).toContain('keine Impfung');
  });
  it('consent form lists planned procedures and leaves risks and alternatives to the vet', async () => {
    const { renderConsentForm } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('008-adversarial-it-performed-vs-planned');
    const r = structuredClone(record); r.treatments.push({ type: 'procedure', text: 'artroscopia anca dx', status: 'planned', source_spans: [[0, 1]] });
    const md = renderConsentForm(r, header, VisitContext.parse({ country: 'IT', author: { name: 'Dr. B', registration: 'Ordine MI 9' } }), 'it', { date: '2026-10-14' });
    expect(md).toContain('- Artroscopia anca dx'); expect(md).toContain('## Rischi e possibili complicanze'); expect(md).toContain('Modi e tempi');
    expect(md).toContain('a cura del veterinario'); expect(md).not.toMatch(/infezione|emorragia/i);
    expect(renderConsentForm(record, header, VisitContext.parse({ country: 'DE' }), 'de')).toContain('Kein geplanter Eingriff');
  });
  it('cost estimate lists planned items with empty price cells and never a number', async () => {
    const { renderCostEstimate } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('008-adversarial-it-performed-vs-planned');
    const md = renderCostEstimate(record, header, VisitContext.parse({ country: 'IT' }), 'it', { date: '2026-10-14' });
    expect(md).toContain('| Ecografia addome | esame | | |'); expect(md).not.toContain('RX anca'); expect(md).toContain('art. 9 c. 4');
    const priced = md.split('\n').filter((l) => l.startsWith('| ') && !l.includes('Voce')).map((l) => l.split('|')[3].trim());
    expect(priced.every((p) => p === '' || p === '______')).toBe(true);
    const de = renderCostEstimate(record, header, VisitContext.parse({ country: 'DE' }), 'de');
    expect(de).toContain('GOT-Nr. | Faktor');
  });
  it('anaesthesia record flags ASA, protocol, monitoring, recovery, team and implant batch', async () => {
    const { renderAnaesthesiaRecord } = await import('../src/render.js');
    const { AnaesthesiaRecord } = await import('../src/country.js');
    const { header } = prep('002-milo-otitis-de');
    const empty = renderAnaesthesiaRecord(AnaesthesiaRecord.parse({}), header, 'de', { date: '2026-10-14' });
    for (const s of ['ASA-Status nicht erfasst', 'Narkoseprotokoll', 'keine Überwachungswerte', 'Aufwachphase nicht dokumentiert', 'Eingriff nicht benannt', 'Operateur/in nicht benannt']) expect(empty).toContain(s);
    const full = renderAnaesthesiaRecord(AnaesthesiaRecord.parse({ procedure: 'Ovariektomie', asa: '1', premedication: 'x', induction: 'y', maintenance: 'z', monitoring: [{ time: '10:00', hr: 90, rr: 14, temp: 37.8, spo2: 98 }], implants: [{ description: 'Naht', batch: 'B1' }], recovery: 'ruhig', anaesthetist: 'A', surgeon: 'B' }), header, 'de', { date: '2026-10-14' });
    expect(full).not.toContain('## ▲'); expect(full).toContain('| 10:00 | 90 | 14 | 37.8 | 98 |');
  });
  it('controlled-drugs entry lists only substances marked controlled and flags a missing quantity', async () => {
    const { renderControlledDrugsEntry } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('002-milo-otitis-de');
    expect(renderControlledDrugsEntry(record, header, VisitContext.parse({ country: 'DE' }), 'de')).toContain('kein Betäubungsmittel');
    const md = renderControlledDrugsEntry(record, header, VisitContext.parse({ country: 'DE', author: { name: 'Dr. V' }, dispensings: [{ medication_index: 0, product: 'Butorphanol 10 mg/ml', is_controlled: true }] }), 'de', { date: '2026-10-14' });
    expect(md).toContain('| 2026-10-14 | Butorphanol 10 mg/ml | ▲'); expect(md).toContain('Menge für das BtM-Buch');
  });
  it('lab explanation uses only the vet\'s own interpretation and flags results without one', async () => {
    const { renderLabExplanation } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('008-adversarial-it-performed-vs-planned');
    const bare = renderLabExplanation(record, header, VisitContext.parse({ country: 'IT' }), 'it');
    expect(bare).toContain('## RX anca'); expect(bare).toContain('displasia bilaterale, artrosi'); expect(bare).toContain('non ha ancora scritto'); expect(bare).toContain('programmato');
    const withText = renderLabExplanation(record, header, VisitContext.parse({ country: 'IT', interpretations: [{ diagnostic_index: 0, text: 'le anche mostrano usura; gestiamo il dolore e la mobilità' }] }), 'it');
    expect(withText).toContain('Cosa dice il tuo veterinario: Le anche mostrano usura'); expect(withText).not.toContain('## ▲');
  });
  it('antibiotic block lists marked antibiotics with justification and duration flags', async () => {
    const { renderAntibioticBlock } = await import('../src/render.js');
    const { VisitContext } = await import('../src/country.js');
    const { record, header } = prep('002-milo-otitis-de');
    expect(renderAntibioticBlock(record, header, VisitContext.parse({ country: 'DE' }), 'de')).toContain('kein Antibiotikum');
    const md = renderAntibioticBlock(record, header, VisitContext.parse({ country: 'DE', dispensings: [{ medication_index: 0, is_antibiotic: true, product: 'Surolan' }] }), 'de', { culture_done: true });
    expect(md).toContain('### Surolan'); expect(md).toContain('Antibiogramm: erstellt'); expect(md).toContain('Begründung der Antibiotika-Anwendung nicht erfasst');
  });
});
