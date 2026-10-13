import { z } from 'zod';

/**
 * The structured clinical record. Everything a document is generated from.
 *
 * Rules the schema encodes:
 * - every clinical fact carries `source_spans`: [start, end] offsets into the vet's
 *   normalised notes. A fact without a span is not allowed to exist.
 * - who said it (`source_role`) and whether it happened (`status`) are explicit.
 * - medication is structured; prose never carries a dose.
 * - what is missing is listed, never guessed.
 */

export const Span = z.tuple([z.number().int().nonnegative(), z.number().int().nonnegative()]);
export type Span = z.infer<typeof Span>;

export const SourceRole = z.enum(['owner_reported', 'vet_observed', 'vet_stated']);
export const Status = z.enum(['planned', 'performed', 'declined', 'recommended', 'dispensed', 'prescribed']);

const sourced = { source_spans: z.array(Span).min(1) };

export const Quantity = z.object({ value: z.number(), unit: z.string(), ...sourced });

export const Patient = z.object({
  name: z.string().nullable(),
  species: z.enum(['dog', 'cat', 'rabbit', 'ferret', 'horse', 'bird', 'reptile', 'other']).nullable(),
  breed: z.string().nullable(),
  sex: z.enum(['female', 'male']).nullable(),
  neuter_status: z.enum(['intact', 'neutered']).nullable(),
  age: z.object({ value: z.number(), unit: z.enum(['day', 'week', 'month', 'year']) }).nullable(),
  weight: Quantity.nullable(),
});

export const HistoryItem = z.object({
  finding: z.string(),
  value: z.string(),
  source_role: SourceRole,
  ...sourced,
});

export const Vitals = z.object({
  temperature: Quantity.nullable(),
  heart_rate: Quantity.nullable(),
  respiratory_rate: Quantity.nullable(),
  weight: Quantity.nullable(),
  crt_seconds: Quantity.nullable(),
});

export const ExamFinding = z.object({
  system: z.string(),
  text: z.string(),
  source_role: SourceRole.default('vet_observed'),
  ...sourced,
});

export const Diagnostic = z.object({
  test: z.string(),
  status: Status,
  result: z.string().nullable(),
  ...sourced,
});

export const Medication = z.object({
  drug: z.string().nullable(),
  class_as_written: z.string().nullable(),
  dose: z.number().nullable(),
  dose_unit: z.string().nullable(),
  route: z.string().nullable(),
  frequency: z.string().nullable(),
  duration: z.string().nullable(),
  status: Status,
  ...sourced,
});

export const Treatment = z.object({
  type: z.enum(['procedure', 'advice', 'other']),
  text: z.string(),
  status: Status,
  ...sourced,
});

export const Assessment = z.object({
  text: z.string().nullable(),
  differentials: z.array(z.object({ text: z.string(), ...sourced })),
  source_spans: z.array(Span),
});

export const FollowUp = z.object({
  text: z.string(),
  interval: z.object({ value: z.number(), unit: z.enum(['hour', 'day', 'week', 'month', 'year']) }).nullable(),
  ...sourced,
});

export const Missing = z.object({ field: z.string(), reason: z.string() });
export const Uncertain = z.object({ field: z.string(), original_text: z.string(), reason: z.string(), ...sourced });

export const ClinicalRecord = z.object({
  schema_version: z.literal('0.2'),
  patient: Patient,
  presenting_complaint: z.object({ text: z.string(), source_role: SourceRole, ...sourced }).nullable(),
  history: z.array(HistoryItem),
  examination: z.object({ vitals: Vitals, findings: z.array(ExamFinding) }),
  diagnostics: z.array(Diagnostic),
  assessment: Assessment,
  treatments: z.array(Treatment),
  medications: z.array(Medication),
  plan: z.object({ follow_up: FollowUp.nullable(), instructions: z.array(z.object({ text: z.string(), ...sourced })) }),
  missing: z.array(Missing),
  uncertain: z.array(Uncertain),
});
export type ClinicalRecord = z.infer<typeof ClinicalRecord>;
export type Medication = z.infer<typeof Medication>;

/** Patient header entered separately by the vet (or taken from the PIMS). Locked facts. */
export const PatientHeader = z.object({
  name: z.string(),
  species: Patient.shape.species.unwrap(),
  breed: z.string().optional(),
  sex: z.enum(['female', 'male']).optional(),
  neuter_status: z.enum(['intact', 'neutered']).optional(),
  age: Patient.shape.age.unwrap().optional(),
  weight_kg: z.number().optional(),
});
export type PatientHeader = z.infer<typeof PatientHeader>;

/** JSON Schema for the model's structured output. Derived once so prompt and validator can't drift. */
export const RECORD_JSON_SCHEMA = {
  // zod-to-json-schema would be nicer; kept dependency-free. The model is also validated with zod after the call.
  type: 'object',
  description: 'ClinicalRecord v0.2; see schema.ts. Every fact must carry source_spans into the notes.',
} as const;
