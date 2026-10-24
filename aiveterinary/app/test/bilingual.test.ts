import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { expandSnippets } from '../src/normalize.js';
import { renderOwnerSummaryBilingual, renderOwnerSummary, renderConsultReport, renderPrescription, crossDocumentMedicationCheck } from '../src/render.js';
import { VisitContext } from '../src/country.js';

const prep = (id: string) => { const c = JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8')); return { header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

describe('clinic snippets', () => {
  it('expands only typed triggers and records where the clinic text sits', () => {
    const r = expandSnippets('T 38.6\nrest .ou\nfu .wv1w', [{ trigger: '.ou', text: 'otherwise unremarkable' }, { trigger: '.wv1w', text: 'Wiedervorstellung in 1 Woche' }]);
    expect(r.text).toBe('T 38.6\nrest otherwise unremarkable\nfu Wiedervorstellung in 1 Woche');
    expect(r.used.map((u) => r.text.slice(u.start, u.end))).toEqual(['otherwise unremarkable', 'Wiedervorstellung in 1 Woche']);
  });
  it('never expands unknown triggers, decimals or words that merely contain a trigger', () => {
    const r = expandSnippets('T 38.6, dose 0.5 ml, file.ou, .xx', [{ trigger: '.ou', text: 'otherwise unremarkable' }]);
    expect(r.text).toBe('T 38.6, dose 0.5 ml, file.ou, .xx'); expect(r.used).toEqual([]);
  });
});

describe('bilingual owner letter', () => {
  it('has both languages and the medication details are identical in every document', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const r = structuredClone(record); r.medications.forEach((m) => (m.status = 'dispensed'));
    const bi = renderOwnerSummaryBilingual(r, header, 'de', 'it');
    expect(bi).toContain('Medikamente geben'); expect(bi).toContain('Farmaci da somministrare');
    const docs = { report: renderConsultReport(r, header, 'de'), owner_de: renderOwnerSummary(r, header, 'de'), owner_it: renderOwnerSummary(r, header, 'it'), rx: renderPrescription(r, header, VisitContext.parse({ country: 'DE' }), 'de') };
    expect(crossDocumentMedicationCheck(r, docs)).toEqual([]);
    // change the duration only in the table row; the same words elsewhere must not hide it
    const tampered = docs.owner_it.split('\n').map((l) => (l.startsWith('|') && l.includes('Surolan') ? l.replace('7 Tage', '5 Tage') : l)).join('\n');
    expect(tampered).toContain('7 Tage');
    expect(crossDocumentMedicationCheck(r, { tampered }).map((p) => p.field)).toEqual(['duration']);
  });
});
