import { describe, it, expect } from 'vitest';
import { z } from 'zod';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { VisitContext } from '../src/country.js';
import { buildRevDraft, renderRevDraftText, REV_SOURCES, type RevDraft, type RevIssued } from '../src/rev.js';

const casesDir = new URL('../eval/cases/', import.meta.url);
const load = (id: string) => JSON.parse(readFileSync(new URL(`${id}.json`, casesDir), 'utf8'));
const prep = (id: string) => { const c = load(id); return { header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };
const ctx = (o: Partial<z.input<typeof VisitContext>> = {}) => VisitContext.parse({ country: 'IT', ...o });

/** Resolve a provenance path like `record.medications[0].dose` or `ctx.dispensings[1].quantity`. */
function resolve(root: Record<string, unknown>, path: string): unknown {
  return path.split('.').flatMap((p) => p.split(/\[(\d+)\]/).filter(Boolean)).reduce<unknown>((o, k) => (o == null ? undefined : (o as Record<string, unknown>)[k]), root);
}
const asText = (v: unknown) => (v && typeof v === 'object' && 'value' in v && 'unit' in v ? `${(v as { value: number }).value} ${(v as { unit: string }).unit}` : v);

/** Every non-null scalar in the draft's data fields, as [field path, value]. */
function filledValues(d: RevDraft): [string, unknown][] {
  const out: [string, unknown][] = [];
  const skip = new Set(['format', 'is_prescription', 'missing', 'warnings', 'provenance', 'escluse', 'medication_index']);
  const walk = (v: unknown, path: string) => {
    if (v == null) return;
    if (Array.isArray(v)) return v.forEach((x, i) => walk(x, `${path}[${i}]`));
    if (typeof v === 'object') return Object.entries(v).forEach(([k, x]) => { if (!skip.has(k)) walk(x, path ? `${path}.${k}` : k); });
    out.push([path, v]);
  };
  walk(d, '');
  return out;
}

function assertTraceable(d: RevDraft, roots: Record<string, unknown>) {
  for (const p of d.provenance) {
    const src = asText(resolve(roots, p.path));
    expect(src, `${p.field} ← ${p.path}`).toBeDefined();
    const fieldValue = resolve(d as unknown as Record<string, unknown>, p.field);
    if (p.field.endsWith('.posologia')) expect(String(fieldValue)).toContain(String(src));
    else { expect(src).toEqual(p.value); expect(fieldValue).toEqual(p.value); }
  }
  for (const [field, value] of filledValues(d)) {
    expect(d.provenance.some((p) => p.field === field), `${field}=${String(value)} has no provenance`).toBe(true);
  }
}

const fixturesWithMeds = readdirSync(casesDir).filter((f) => f.endsWith('.json')).map((f) => JSON.parse(readFileSync(new URL(f, casesDir), 'utf8')))
  .filter((c) => c.fixture_record?.medications?.length);

describe('REV draft', () => {
  it('nothing invented: every value on every fixture with medications traces back to record, header or context', () => {
    expect(fixturesWithMeds.length).toBeGreaterThan(10);
    for (const c of fixturesWithMeds) {
      const header = PatientHeader.parse(c.header), record = ClinicalRecord.parse(c.fixture_record);
      for (const v of [ctx(), ctx({ microchip: '380260000000001', owner: { name: 'Maria Rossi', tax_id: 'RSSMRA80A41H501X' }, author: { name: 'Dr.ssa Bianchi', registration: 'RM 1234' }, dispensings: record.medications.map((_, i) => ({ medication_index: i, product: `P${i}`, authorisation_number: '103458016', pack: '1 flacone 15 ml', quantity: { value: 1, unit: 'confezione' } })) })]) {
        const d = buildRevDraft(record, header, v);
        assertTraceable(d, { record, header, ctx: v, issued: {} });
        expect(d.is_prescription).toBe(false);
      }
    }
  });

  it('with an empty context the fields the sources require are null and listed as missing', () => {
    const { record, header } = prep('105-gen-otitis-cat-it');
    const d = buildRevDraft(record, header, ctx());
    expect(d.righe).toHaveLength(1);
    const r = d.righe[0];
    expect(r.farmaco_come_scritto).toBe('Surolan');
    expect([r.aic, r.denominazione, r.numero_confezioni, r.tipo_medicinale, r.ripetibile, r.deroga]).toEqual([null, null, null, null, null, null]);
    expect(d.proprietario.codice_fiscale).toBeNull();
    const fields = d.missing.map((m) => m.field);
    for (const f of ['tipo_ricetta', 'proprietario.codice_fiscale', 'veterinario.nome', 'animale.identificativo', 'righe[0].aic', 'righe[0].numero_confezioni', 'righe[0].tipo_medicinale', 'righe[0].deroga']) expect(fields).toContain(f);
    for (const m of d.missing) expect(REV_SOURCES[m.source]).toBeDefined();
  });

  it('no lookups or defaults: quantity in tablets is not turned into packs, and repeatability/deroga stay unset', () => {
    const { record, header } = prep('105-gen-otitis-cat-it');
    const d = buildRevDraft(record, header, ctx({ dispensings: [{ medication_index: 0, product: 'Surolan gocce', quantity: { value: 15, unit: 'ml' } }] }));
    expect(d.righe[0].numero_confezioni).toBeNull();
    expect(d.righe[0].quantita_come_scritta).toBe('15 ml');
    expect(d.righe[0].aic).toBeNull();
    expect(d.missing.map((m) => m.field)).toContain('righe[0].numero_confezioni');
    expect(d.tipo_ricetta).toBeNull();
  });

  it('declined medications are excluded', () => {
    const { record, header } = prep('153-gen-pruritus-declined-dispensed-it');
    const d = buildRevDraft(record, header, ctx());
    const declined = record.medications.findIndex((m) => m.status === 'declined');
    expect(declined).toBeGreaterThanOrEqual(0);
    expect(d.righe.some((r) => r.medication_index === declined)).toBe(false);
    expect(d.cessioni_da_scorta.some((r) => r.medication_index === declined)).toBe(false);
    expect(d.escluse.find((e) => e.medication_index === declined)?.status).toBe('declined');
    expect(renderRevDraftText(d)).not.toMatch(/\[ \] .*Apoquel/);
  });

  it('dispensed medications go to the stock-discharge list (art. 37 D.Lgs. 218/2023), not onto the prescription', () => {
    const { record, header } = prep('162-gen-full-vs-drug-only-meds-it');
    const d = buildRevDraft(record, header, ctx());
    expect(d.righe.map((r) => record.medications[r.medication_index].status)).toEqual(['prescribed']);
    expect(d.cessioni_da_scorta.map((r) => record.medications[r.medication_index].status)).toEqual(['dispensed']);
    expect(d.missing.some((m) => m.field === 'cessioni_da_scorta[0].motivo_scarico' && m.source === 'guida_ndpa')).toBe(true);
  });

  it('vaccines administered in the clinic are not put on a prescription', () => {
    for (const id of ['111-gen-cat-vaccine-it', '171-gen-ferret-vaccine-batch-it', '010-vaccination-visit']) {
      const { record, header } = prep(id);
      const d = buildRevDraft(record, header, ctx());
      const vaccines = record.medications.map((m, i) => ({ m, i })).filter(({ m }) => /vacc/i.test(`${m.drug} ${m.class_as_written}`) && m.status === 'performed');
      expect(vaccines.length, id).toBeGreaterThan(0);
      for (const { i } of vaccines) {
        expect(d.righe.some((r) => r.medication_index === i)).toBe(false);
        expect(d.escluse.find((e) => e.medication_index === i)?.source).toBe('guida_ndpa');
      }
    }
  });

  it('antibiotic: the vet\'s justification is carried, the prophylaxis/metaphylaxis code is left to the system', () => {
    const { record, header } = prep('105-gen-otitis-cat-it');
    const d = buildRevDraft(record, header, ctx({ dispensings: [{ medication_index: 0, is_antibiotic: true, antibiotic_justification: 'otite batterica, citologia' }] }));
    expect(d.righe[0].antimicrobico).toBe(true);
    expect(d.righe[0].giustificazione_note).toBe('otite batterica, citologia');
    expect(d.righe[0].profilassi_metafilassi).toBeNull();
    expect(d.missing.map((m) => m.field)).toContain('righe[0].profilassi_metafilassi');
  });

  it('horse: farm code is required for equidi NDPA', () => {
    const { record, header } = prep('174-gen-horse-colic-it');
    const d = buildRevDraft(record, header, ctx());
    expect(d.missing.map((m) => m.field)).toContain('animale.codice_azienda');
  });

  it('REV number and PIN are only what the vet types after issuing', () => {
    const { record, header } = prep('105-gen-otitis-cat-it');
    expect(buildRevDraft(record, header, ctx()).emessa).toEqual({ numero: null, pin: null });
    const issued: RevIssued = { numero: '1234567890123', pin: '4321' };
    const v = ctx();
    const d = buildRevDraft(record, header, v, issued);
    expect(d.emessa).toEqual({ numero: '1234567890123', pin: '4321' });
    assertTraceable(d, { record, header, ctx: v, issued });
    expect(renderRevDraftText(d)).toContain('PIN: 4321');
  });

  it('the checklist is headed as a draft, not a prescription, and flags what is missing', () => {
    const { record, header } = prep('105-gen-otitis-cat-it');
    const txt = renderRevDraftText(buildRevDraft(record, header, ctx()), 'it');
    expect(txt.split('\n')[0]).toBe('BOZZA DA TRASCRIVERE — NON È UNA RICETTA');
    expect(txt).toContain('Surolan');
    expect(txt).toContain('AIC: ▲ da inserire');
    expect(txt).toContain('Codice fiscale: ▲ da inserire');
  });

  it('refuses a non-Italian context', () => {
    const { record, header } = prep('002-milo-otitis-de');
    expect(() => buildRevDraft(record, header, VisitContext.parse({ country: 'DE' }))).toThrow();
  });
});
