import type { ClinicalRecord } from './schema.js';
import { requiredMissing } from './validators.js';

/**
 * Clinic-required fields. A clinic can decide that some fields must be present
 * on every consultation record (e.g. "always record the temperature"). This
 * never fills anything in: a setting can only ADD a flag for a field that is
 * absent from the record. The vet then types the value or marks it
 * "not recorded".
 */

export type ClinicFieldId = 'weight' | 'temperature' | 'heart_rate' | 'respiratory_rate' | 'assessment' | 'follow_up';

type ClinicField = {
  id: ClinicFieldId;
  /** Field name used in the missing list (matches the workspace / requiredMissing names). */
  field: string;
  /** Record paths that satisfy the requirement; any one present is enough. */
  paths: string[];
  present: (r: ClinicalRecord) => boolean;
};

export const CLINIC_FIELDS: readonly ClinicField[] = [
  { id: 'weight', field: 'patient.weight', paths: ['patient.weight', 'examination.vitals.weight'], present: (r) => !!(r.patient.weight || r.examination.vitals.weight) },
  { id: 'temperature', field: 'examination.vitals.temperature', paths: ['examination.vitals.temperature'], present: (r) => !!r.examination.vitals.temperature },
  { id: 'heart_rate', field: 'examination.vitals.heart_rate', paths: ['examination.vitals.heart_rate'], present: (r) => !!r.examination.vitals.heart_rate },
  { id: 'respiratory_rate', field: 'examination.vitals.respiratory_rate', paths: ['examination.vitals.respiratory_rate'], present: (r) => !!r.examination.vitals.respiratory_rate },
  { id: 'assessment', field: 'assessment', paths: ['assessment.text', 'assessment.differentials'], present: (r) => !!r.assessment.text || r.assessment.differentials.length > 0 },
  { id: 'follow_up', field: 'plan.follow_up', paths: ['plan.follow_up'], present: (r) => !!r.plan.follow_up },
] as const;

export const CLINIC_REASON = {
  en: 'Required by your clinic settings',
  it: 'Richiesto dalle impostazioni della clinica',
  de: 'Von Ihren Praxiseinstellungen verlangt',
} as const;

export type ClinicMissingOptions = {
  /** Document whose built-in requirements are already flagged (default consult_report). */
  docType?: Parameters<typeof requiredMissing>[1];
  lang?: keyof typeof CLINIC_REASON;
};

/**
 * One entry per clinic-required field that is absent from the record.
 * Unknown ids are ignored; fields requiredMissing already flags are not repeated.
 * Read-only: the record is never modified.
 */
export function clinicMissing(record: ClinicalRecord, required: string[], opts: ClinicMissingOptions = {}): { field: string; reason: string }[] {
  const already = new Set(requiredMissing(record, opts.docType ?? 'consult_report'));
  const reason = CLINIC_REASON[opts.lang ?? 'en'];
  const want = new Set(required);
  const out: { field: string; reason: string }[] = [];
  for (const f of CLINIC_FIELDS) {
    if (!want.has(f.id) || f.present(record) || already.has(f.field)) continue;
    out.push({ field: f.field, reason });
  }
  return out;
}
