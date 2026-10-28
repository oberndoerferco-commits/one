import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord } from '../src/schema.js';
import { requiredMissing } from '../src/validators.js';
import { CLINIC_FIELDS, clinicMissing } from '../src/clinic-required.js';
import * as pkg from '../src/index.js';

const dir = new URL('../eval/cases/', import.meta.url);
const ids = readdirSync(dir).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, ''));
const rec = (id: string) => ClinicalRecord.parse(JSON.parse(readFileSync(new URL(`${id}.json`, dir), 'utf8')).fixture_record);
const ALL = CLINIC_FIELDS.map((f) => f.id);
const fields = (x: { field: string }[]) => x.map((m) => m.field);

describe('clinic-required fields', () => {
  it('is exported from the package entry point', () => {
    expect(pkg.clinicMissing).toBe(clinicMissing);
    expect(pkg.CLINIC_FIELDS.map((f) => f.id)).toEqual(['weight', 'temperature', 'heart_rate', 'respiratory_rate', 'assessment', 'follow_up']);
  });

  it('flags a required field only when it is absent', () => {
    const noTemp = rec('008-adversarial-it-performed-vs-planned');
    expect(noTemp.examination.vitals.temperature).toBeNull();
    expect(fields(clinicMissing(noTemp, ['temperature']))).toEqual(['examination.vitals.temperature']);
    const withTemp = rec('001-luna-vomiting');
    expect(withTemp.examination.vitals.temperature).not.toBeNull();
    expect(clinicMissing(withTemp, ['temperature'])).toEqual([]);
  });

  it('weight is satisfied by patient.weight or examination.vitals.weight', () => {
    const r = rec('121-gen-senior-weight-loss-en');
    expect(clinicMissing(r, ['weight'])).toEqual([]);
    const a = structuredClone(r); a.patient.weight = null; a.examination.vitals.weight = { value: 4, unit: 'kg', source_spans: [] } as any;
    expect(clinicMissing(a, ['weight'])).toEqual([]);
    const b = structuredClone(a); b.examination.vitals.weight = null;
    expect(fields(clinicMissing(b, ['weight']))).toEqual(['patient.weight']);
  });

  it('assessment is satisfied by text or any differential; follow-up by plan.follow_up', () => {
    const r = rec('118-gen-suture-removal-en');
    expect(r.plan.follow_up).toBeNull();
    expect(fields(clinicMissing(r, ['follow_up']))).toEqual(['plan.follow_up']);
    const noAssess = structuredClone(r); noAssess.assessment.text = null; noAssess.assessment.differentials = [];
    // consult_report already requires an assessment: not repeated
    expect(clinicMissing(noAssess, ['assessment'])).toEqual([]);
    // the owner summary does not, so the clinic setting adds it
    expect(fields(clinicMissing(noAssess, ['assessment'], { docType: 'owner_summary' }))).toEqual(['assessment']);
    const diffOnly = structuredClone(noAssess); diffOnly.assessment.differentials = [{ text: 'x', source_spans: [[0, 1]] } as any];
    expect(clinicMissing(diffOnly, ['assessment'], { docType: 'owner_summary' })).toEqual([]);
  });

  it('never duplicates what requiredMissing already flags', () => {
    for (const id of ids) {
      const r = rec(id);
      const base = new Set(requiredMissing(r, 'consult_report'));
      const extra = fields(clinicMissing(r, ALL));
      for (const f of extra) expect(base.has(f), `${id}: ${f}`).toBe(false);
      expect(new Set(extra).size).toBe(extra.length);
    }
    const dosed = rec('002-milo-otitis-de');
    expect(requiredMissing(dosed, 'consult_report')).toContain('patient.weight');
    expect(fields(clinicMissing(dosed, ['weight']))).not.toContain('patient.weight');
  });

  it('every flag is for a field that is really absent, across all fixtures', () => {
    for (const id of ids) {
      const r = rec(id);
      for (const m of clinicMissing(r, ALL)) {
        const def = CLINIC_FIELDS.find((f) => f.field === m.field)!;
        expect(def.present(r), `${id}: ${m.field}`).toBe(false);
        expect(m.reason).toBe('Required by your clinic settings');
      }
    }
  });

  it('never mutates the record', () => {
    for (const id of ids) {
      const r = rec(id); const before = JSON.stringify(r);
      clinicMissing(r, ALL); clinicMissing(r, ALL, { docType: 'owner_summary', lang: 'de' });
      expect(JSON.stringify(r)).toBe(before);
    }
  });

  it('ignores unknown ids and an empty selection', () => {
    const r = rec('008-adversarial-it-performed-vs-planned');
    expect(clinicMissing(r, [])).toEqual([]);
    expect(clinicMissing(r, ['blood_pressure', 'examination.vitals.temperature', '__proto__'])).toEqual([]);
    expect(fields(clinicMissing(r, ['nope', 'temperature']))).toEqual(['examination.vitals.temperature']);
  });

  it('localises the reason', () => {
    const r = rec('008-adversarial-it-performed-vs-planned');
    expect(clinicMissing(r, ['temperature'], { lang: 'it' })[0].reason).toBe('Richiesto dalle impostazioni della clinica');
    expect(clinicMissing(r, ['temperature'], { lang: 'de' })[0].reason).toBe('Von Ihren Praxiseinstellungen verlangt');
  });
});
