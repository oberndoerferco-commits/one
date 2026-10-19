import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader, type Medication } from '../src/schema.js';
import { requiredMissing, VACCINE_RE } from '../src/validators.js';

const dir = new URL('../eval/cases/', import.meta.url);
const load = (id: string) => JSON.parse(readFileSync(new URL(`${id}.json`, dir), 'utf8'));
const rec = (id: string) => ClinicalRecord.parse(load(id).fixture_record);
const hdr = (id: string) => PatientHeader.parse(load(id).header);

const med = (m: Partial<Medication>): Medication => ({ drug: 'meloxicam', class_as_written: null, dose: 0.1, dose_unit: 'mg/kg', route: 'po', frequency: 'sid', duration: '5 days', status: 'prescribed', source_spans: [[0, 1]], ...m } as Medication);
/** Case 002 record (no weight anywhere in the record) with its medications replaced. */
const withMeds = (...meds: Medication[]) => ({ ...rec('002-milo-otitis-de'), medications: meds });
const header = (weight_kg?: number) => PatientHeader.parse({ name: 'Rex', species: 'dog', ...(weight_kg != null ? { weight_kg } : {}) });

describe('requiredMissing: weight', () => {
  it('keeps the two-argument call working and still asks for weight without a header', () => {
    expect(requiredMissing(withMeds(med({})), 'consult_report')).toContain('patient.weight');
    expect(requiredMissing(withMeds(med({})), 'consult_report', header())).toContain('patient.weight');
  });
  it('does not ask for weight when the patient header has weight_kg (case 002)', () => {
    expect(hdr('002-milo-otitis-de').weight_kg).toBe(14);
    expect(requiredMissing(rec('002-milo-otitis-de'), 'consult_report', hdr('002-milo-otitis-de'))).not.toContain('patient.weight');
  });
  it('does not ask for weight when every dosed medication is declined (case 006)', () => {
    expect(requiredMissing(rec('006-adversarial-dose-not-given'), 'consult_report', hdr('006-adversarial-dose-not-given'))).not.toContain('patient.weight');
    expect(requiredMissing(withMeds(med({ status: 'declined' }), med({ dose: null, status: 'prescribed' })), 'consult_report')).not.toContain('patient.weight');
  });
  it('still asks for weight when a declined and a given dosed drug are both present', () => {
    expect(requiredMissing(withMeds(med({ status: 'declined' }), med({ status: 'dispensed' })), 'consult_report')).toContain('patient.weight');
  });
});

describe('requiredMissing: performed (given once in the clinic)', () => {
  it('needs no frequency or duration for a performed injection (case 007)', () => {
    const miss = requiredMissing(rec('007-adversarial-de-decimal-comma'), 'consult_report', hdr('007-adversarial-de-decimal-comma'));
    expect(miss).not.toContain('medications[0].frequency');
    const d = requiredMissing(withMeds(med({ status: 'performed', frequency: null, duration: null })), 'discharge');
    expect(d).not.toContain('medications[0].frequency');
    expect(d).not.toContain('medications[0].duration');
  });
  it('still needs a dose and route for a non-vaccine performed injection', () => {
    const miss = requiredMissing(withMeds(med({ drug: 'Metamizol-Natrium', status: 'performed', dose: null, route: null, frequency: null })), 'consult_report');
    expect(miss).toContain('medications[0].dose');
    expect(miss).toContain('medications[0].route');
  });
  it('still needs dose, frequency and duration for a prescribed or dispensed drug', () => {
    for (const status of ['prescribed', 'dispensed'] as const) {
      const miss = requiredMissing(withMeds(med({ status, dose: null, frequency: null, duration: null })), 'discharge');
      expect(miss).toEqual(expect.arrayContaining(['medications[0].dose', 'medications[0].frequency', 'medications[0].duration']));
    }
  });
});

describe('requiredMissing: vaccines given in the clinic', () => {
  it('needs no dose or frequency for a performed vaccine (case 010)', () => {
    const miss = requiredMissing(rec('010-vaccination-visit'), 'consult_report', hdr('010-vaccination-visit'));
    expect(miss).not.toContain('medications[0].dose');
    expect(miss).not.toContain('medications[0].frequency');
  });
  it('recognises vaccine names in EN, DE and IT, in the drug or the class text', () => {
    for (const drug of ['DHPPi + Lepto vaccine', 'RCP-Impfstoff', 'Staupeimpfstoff', 'Tollwutimpfung', 'Impfung Tollwut', 'vaccino cimurro', 'Vaccin RCP']) {
      expect(requiredMissing(withMeds(med({ drug, status: 'performed', dose: null, frequency: null })), 'consult_report'), drug).not.toContain('medications[0].dose');
    }
    expect(requiredMissing(withMeds(med({ drug: 'Nobivac', class_as_written: 'Impfstoff', status: 'performed', dose: null })), 'consult_report')).not.toContain('medications[0].dose');
    for (const drug of ['meloxicam', 'Metamizol-Natrium', 'Surolan']) expect(VACCINE_RE.test(drug), drug).toBe(false);
  });
  it('still needs a dose for a vaccine that is only prescribed or dispensed', () => {
    expect(requiredMissing(withMeds(med({ drug: 'RCP vaccine', status: 'dispensed', dose: null })), 'consult_report')).toContain('medications[0].dose');
  });
  it('still needs a route for a performed vaccine', () => {
    expect(requiredMissing(withMeds(med({ drug: 'RCP vaccine', status: 'performed', dose: null, route: null })), 'consult_report')).toContain('medications[0].route');
  });
});
