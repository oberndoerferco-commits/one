import { describe, it, expect, expectTypeOf } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { VisitContext } from '../src/country.js';
import { renderMedicationTable } from '../src/render.js';
import { buildClaimPack, renderClaimSummary, type ClaimInvoiceLine, type ClaimOpts } from '../src/claim.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

// 002: Milo, Cocker Spaniel, "seit 5 Tagen Kopfschütteln li", assessment "Otitis externa li", Surolan prescribed
const full: ClaimOpts = {
  approved: true,
  insurer: 'AGILA', policy_number: '1234567',
  date_of_birth: '2022-03-14',
  condition_type: 'illness', first_symptom_date: '2026-10-10',
  pre_existing: false, surgery: false, setting: 'outpatient',
  visit_date: '2026-10-15',
  practice: { name: 'Tierarztpraxis am Park', address: 'Parkstr. 1, 30159 Hannover' },
  invoice: {
    number: 'R-2026-0815', date: '2026-10-15', total: '61,23 €', vat: '9,78 €',
    lines: [
      { date: '2026-10-15', description: 'Allgemeine Untersuchung mit Beratung, Hund', got_number: '10', factor: '1,0', amount: '23,62 €' },
      { date: '2026-10-15', description: 'Zytologie Ohr', got_number: '346', factor: '2,0', amount: '27,83 €' },
    ],
  },
};
const ctxDE = VisitContext.parse({ country: 'DE', microchip: '276098106543210', owner: { name: 'Anna Weber' }, author: { name: 'Dr. Lena Hoff', registration: 'TÄK Nds 4711' } });

describe('claim pack: values traceable to the record, header, context or vet-typed opts', () => {
  const { record, header } = prep('002-milo-otitis-de');
  const pack = buildClaimPack(record, header, ctxDE, full);

  it('takes signalment from the header, chip/owner/vet from the context, and says so', () => {
    expect(pack.patient.name).toEqual({ value: 'Milo', source: 'header.name' });
    expect(pack.patient.breed).toEqual({ value: 'Cocker Spaniel', source: 'header.breed' });
    expect(pack.patient.age?.source).toBe('header.age');
    expect(pack.patient.microchip).toEqual({ value: '276098106543210', source: 'ctx.microchip' });
    expect(pack.owner.name?.source).toBe('ctx.owner.name');
    expect(pack.practice.vet_name).toEqual({ value: 'Dr. Lena Hoff', source: 'ctx.author.name' });
    expect(pack.patient.date_of_birth).toEqual({ value: '2022-03-14', source: 'opts.date_of_birth' });
  });

  it('diagnosis is the vet\'s assessment sentence; the clinical lists are the record\'s own items', () => {
    expect(pack.clinical.diagnosis).toEqual({ value: 'Otitis externa li', source: 'record.assessment.text' });
    expect(pack.clinical.presenting_complaint).toEqual({ value: 'seit 5 Tagen Kopfschütteln li', source: 'record.presenting_complaint.text' });
    expect(pack.clinical.treatments).toEqual([{ value: 'Ohrreinigung durchgeführt', source: 'record.treatments[0].text' }]);
    expect(pack.clinical.diagnostics.map((d) => d.source)).toEqual(['record.diagnostics[0]']);
    expect(pack.clinical.medications).toEqual(record.medications.filter((m) => m.status === 'prescribed'));
  });

  it('every sourced value resolves to the object it names', () => {
    const roots: Record<string, unknown> = { header, record, ctx: ctxDE, opts: full };
    const walk = (o: unknown): Array<{ value: unknown; source: string }> =>
      o && typeof o === 'object'
        ? ('source' in (o as object) && 'value' in (o as object) ? [o as { value: unknown; source: string }] : Object.values(o as object).flatMap(walk))
        : [];
    const found = walk({ ...pack, clinical: { ...pack.clinical, medications: [] } });
    expect(found.length).toBeGreaterThan(20);
    for (const { value, source } of found) {
      if (source.includes('[]') || source.includes('+') || /\[\d+\]$/.test(source)) continue; // list-derived; checked above
      const at = source.split('.').reduce<unknown>((o, k) => {
        const m = /^(\w+)\[(\d+)\]$/.exec(k);
        return m ? (o as Record<string, unknown[]>)[m[1]][Number(m[2])] : (o as Record<string, unknown>)?.[k];
      }, roots);
      expect(at, source).toEqual(value);
    }
  });

  it('a complete DE claim has nothing missing', () => {
    expect(pack.missing).toEqual([]);
  });

  it('treatment dates are the typed dates, de-duplicated, never derived', () => {
    expect(pack.clinical.treatment_dates?.value).toEqual(['2026-10-15']);
  });
});

describe('claim pack: absent means null and listed', () => {
  const { record, header } = prep('002-milo-otitis-de');
  const bare = buildClaimPack(record, header, VisitContext.parse({ country: 'DE' }));

  it('lists what the forms ask for and nobody typed', () => {
    for (const f of ['patient.date_of_birth', 'patient.microchip', 'owner.name', 'clinical.first_symptom_date', 'clinical.pre_existing', 'clinical.condition_type', 'clinical.treatment_dates', 'invoice.lines', 'practice.vet_name'] as const) {
      expect(bare.missing).toContain(f);
    }
    expect(bare.patient.microchip).toBeNull();
    expect(bare.missing).not.toContain('clinical.diagnosis');
    expect(bare.missing).not.toContain('patient.breed');
  });

  it('prints the vet\'s "unknown" answer to pre-existing as a statement, not as missing', () => {
    const p = buildClaimPack(record, header, ctxDE, { pre_existing: 'unknown', pre_existing_note: 'ignored without a yes' });
    expect(p.clinical.pre_existing).toEqual({ value: 'unknown', source: 'opts.pre_existing' });
    expect(p.missing).not.toContain('clinical.pre_existing');
    expect(renderClaimSummary(p, 'de')).toContain('Vorerkrankung (Angabe der Tierärztin / des Tierarztes): der Tierärztin / dem Tierarzt nicht bekannt');
    expect(renderClaimSummary(p, 'it')).toContain('non noto al veterinario');
    expect(renderClaimSummary(p, 'en')).not.toContain('ignored without a yes');
  });

  it('never derives the first-symptom date from "seit 5 Tagen", nor pre-existing from history', () => {
    const p = buildClaimPack(record, header, ctxDE, { visit_date: '2026-10-15' });
    expect(p.clinical.first_symptom_date).toBeNull();
    expect(p.clinical.pre_existing).toBeNull();
    expect(p.missing).toEqual(expect.arrayContaining(['clinical.first_symptom_date', 'clinical.pre_existing']));
    const md = renderClaimSummary(p, 'de');
    expect(md).not.toContain('2026-10-10');
    expect(md).toMatch(/Vorerkrankung \(Angabe der Tierärztin \/ des Tierarztes\): ▲ Fehlt/);
  });

  it('does not promote differentials to a diagnosis', () => {
    const r = structuredClone(record);
    r.assessment.text = null;
    r.assessment.differentials = [{ text: 'Otitis media', source_spans: [[0, 1]] }];
    const p = buildClaimPack(r, header, ctxDE, full);
    expect(p.clinical.diagnosis).toBeNull();
    expect(p.missing).toContain('clinical.diagnosis');
    expect(renderClaimSummary(p, 'en')).not.toContain('Otitis media');
    const typed = buildClaimPack(r, header, ctxDE, { ...full, diagnosis: 'Otitis externa links, Malassezien' });
    expect(typed.clinical.diagnosis).toEqual({ value: 'Otitis externa links, Malassezien', source: 'opts.diagnosis' });
  });

  it('DE: every invoice line needs a GOT number and factor; IT does not', () => {
    const lines: ClaimInvoiceLine[] = [{ date: '2026-10-15', description: 'Untersuchung', amount: '23,62 €' }, { date: null, description: 'Zytologie', got_number: '346' }];
    const de = buildClaimPack(record, header, ctxDE, { ...full, invoice: { ...full.invoice, lines } });
    expect(de.missing).toEqual(['invoice.lines[0].got_number', 'invoice.lines[0].factor', 'invoice.lines[1].date', 'invoice.lines[1].factor', 'invoice.lines[1].amount']);
    const itPack = buildClaimPack(record, header, VisitContext.parse({ ...ctxDE, country: 'IT' }), { ...full, invoice: { ...full.invoice, lines } });
    expect(itPack.missing).toEqual(['invoice.lines[1].date', 'invoice.lines[1].amount']);
  });

  it('record signalment fills in only when the header lacks it, with its own source', () => {
    const r = structuredClone(record); r.patient.breed = 'Cocker';
    const p = buildClaimPack(r, { name: 'Milo', species: 'dog' }, ctxDE, full);
    expect(p.patient.breed).toEqual({ value: 'Cocker', source: 'record.patient.breed' });
    expect(p.patient.sex).toBeNull();
    expect(p.missing).toContain('patient.sex');
  });
});

describe('claim summary in three languages', () => {
  const { record, header } = prep('002-milo-otitis-de');
  const pack = buildClaimPack(record, header, ctxDE, full);
  const meds = renderMedicationTable(record.medications.filter((m) => m.status === 'prescribed'), 'de');

  it.each([
    ['en', 'Information for the pet insurer', 'The veterinarian checks and confirms these details with stamp and signature', 'Diagnosis: Otitis externa li'],
    ['de', 'Angaben für die Tierversicherung', 'bestätigt diese Angaben mit Praxisstempel und Unterschrift', 'Diagnose: Otitis externa li'],
    ['it', 'Dati per l\'assicurazione', 'Il veterinario verifica e conferma questi dati con timbro e firma', 'Diagnosi: Otitis externa li'],
  ] as const)('%s: title, confirmation note, values verbatim', (lang, title, note, diag) => {
    const md = renderClaimSummary(pack, lang);
    expect(md.startsWith(`# ${title}`)).toBe(true);
    expect(md).toContain(note);
    expect(md).toContain(diag);
    expect(md).toContain('276098106543210');
    const table = renderMedicationTable(pack.clinical.medications, lang);
    expect(md).toContain(table);
    expect(md.replace(table, '')).not.toContain('▲'); // the only flag is the record's own missing route, inside the reused table
  });

  it('reuses the report\'s medication table verbatim', () => {
    expect(renderClaimSummary(pack, 'de')).toContain(meds);
  });

  it('DE prints GOT number and factor columns exactly as typed', () => {
    const md = renderClaimSummary(pack, 'de');
    expect(md).toContain('| Datum | Leistung | GOT-Nr. | Faktor | Menge | Betrag |');
    expect(md).toContain('| 2026-10-15 | Zytologie Ohr | 346 | 2,0 |  | 27,83 € |');
  });

  it('marks a draft and lists the missing fields in the summary language', () => {
    const p = buildClaimPack(record, header, VisitContext.parse({ country: 'IT' }));
    const md = renderClaimSummary(p, 'it');
    expect(md).toContain('BOZZA');
    expect(md).toContain('## ▲ Mancante');
    expect(md).toContain('- Microchip');
    expect(md).toContain('- Insorgenza dei sintomi il');
    expect(md).toContain('- Patologia preesistente (dichiarazione del veterinario)');
  });
});

describe('no fee arithmetic anywhere', () => {
  const { record, header } = prep('002-milo-otitis-de');

  it('amounts and factors are strings; nothing is a number to compute with', () => {
    expectTypeOf<ClaimInvoiceLine['amount']>().toEqualTypeOf<string | null | undefined>();
    expectTypeOf<ClaimInvoiceLine['factor']>().toEqualTypeOf<string | null | undefined>();
  });

  it('prints no total, fee or factor it was not given', () => {
    const lines: ClaimInvoiceLine[] = [
      { date: '2026-10-15', description: 'A', got_number: '10', factor: '2,0', amount: '10,00 €' },
      { date: '2026-10-15', description: 'B', got_number: '11', factor: '3,0', amount: '20,00 €' },
    ];
    const p = buildClaimPack(record, header, ctxDE, { ...full, invoice: { lines } });
    const md = renderClaimSummary(p, 'de');
    expect(md).not.toMatch(/30[,.]00/);   // the sum of the lines
    expect(md).not.toMatch(/\b(20|60)[,.]00\b.*\b(20|60)[,.]00\b/); // no factor × amount
    expect(md).toContain('Rechnungsbetrag (wie eingetragen): ▲ Fehlt');
    expect(p.missing).toContain('invoice.total');
  });

  it('the module source contains no number parsing or rounding of amounts', () => {
    const src = readFileSync(new URL('../src/claim.ts', import.meta.url), 'utf8');
    expect(src).not.toMatch(/parseFloat|toFixed|Math\.|Intl\.NumberFormat|reduce\(/);
    expect(src).not.toMatch(/(amount|factor|total|vat)\S*\s*[*/+-]\s*[\w(]/);
  });
});
