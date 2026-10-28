import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { renderConsultReport, renderOwnerSummary, renderReferralLetter, renderDischargeLetter, renderPrescription, crossDocumentMedicationCheck } from '../src/render.js';
import { VisitContext } from '../src/country.js';
import { buildClaimPack, renderClaimSummary } from '../src/claim.js';

const prep = (id: string) => { const c = JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8')); return { lang: c.language, header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };
const docsOf = (id: string) => {
  const { lang, header, record } = prep(id);
  const ctx = VisitContext.parse({ country: 'DE' });
  return { record, header, docs: { report: renderConsultReport(record, header, lang), owner: renderOwnerSummary(record, header, lang), referral: renderReferralLetter(record, header, lang), discharge: renderDischargeLetter(record, header, lang), rx: renderPrescription(record, header, ctx, lang) } };
};

describe('cross-document medication check, medications given in the clinic', () => {
  // A "performed" injection is named without details in the owner letter and is not on the prescription by design.
  it.each(['007-adversarial-de-decimal-comma', '010-vaccination-visit', '173-gen-horse-colic-de'])('%s can be approved', (id) => {
    const { record, docs } = docsOf(id);
    expect(record.medications.some((m) => m.status === 'performed')).toBe(true);
    expect(crossDocumentMedicationCheck(record, docs)).toEqual([]);
  });
  it('still catches a changed value in a table row of a performed medication', () => {
    const { record, docs } = docsOf('007-adversarial-de-decimal-comma');
    const m = record.medications.find((x) => x.status === 'performed')!;
    const tampered = docs.report.split('\n').map((l) => (l.startsWith('|') && l.includes(m.drug!) ? l.replace(m.route!, 'i.m.') : l)).join('\n');
    expect(tampered).not.toBe(docs.report);
    expect(crossDocumentMedicationCheck(record, { report: tampered }).map((p) => p.field)).toEqual(['route']);
  });
  it('still requires a dispensed medication on the prescription', () => {
    const { record, docs } = docsOf('007-adversarial-de-decimal-comma');
    const r = structuredClone(record); r.medications.forEach((x) => (x.status = 'dispensed'));
    expect(crossDocumentMedicationCheck(r, { rx: 'nothing here' }).length).toBeGreaterThan(0);
    void docs;
  });
});

describe('claim invoice lines', () => {
  it('keeps a typed pipe inside its cell', () => {
    const { record, header } = prep('001-luna-vomiting');
    const pack = buildClaimPack(record, header, VisitContext.parse({ country: 'IT' }), { invoice: { lines: [{ date: '2026-10-20', description: 'Visit | follow-up', amount: '45,00' }] } } as any);
    const row = renderClaimSummary(pack, 'en').split('\n').find((l) => l.includes('Visit'))!;
    expect(row).toContain('Visit \\| follow-up');
    expect(row.split(/(?<!\\)\|/).length).toBe(row.startsWith('|') ? 6 : 5);
  });
});
