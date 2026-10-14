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
});
