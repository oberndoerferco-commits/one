import type { ClinicalRecord, Medication, Missing, PatientHeader } from './schema.js';
import { z } from 'zod';

/**
 * Country field packs. Facts the vet enters at the dispensing / sign-off step
 * (never extracted from prose), and the per-country checks that turn a
 * missing one into a flag. Nothing here fills a value in: a pack only says
 * what is absent and which rule wants it.
 */

export const Country = z.enum(['DE', 'IT', 'CH', 'AT']);
export type Country = z.infer<typeof Country>;

export const Dispensing = z.object({
  medication_index: z.number().int().nonnegative(),
  product: z.string().nullable().default(null),             // trade name as on the pack
  authorisation_number: z.string().nullable().default(null), // DE Zul.-Nr., IT AIC, CH Swissmedic no., AT Zul.-Nr.
  batch: z.string().nullable().default(null),
  pack: z.string().nullable().default(null),                 // e.g. "20 tablets"
  quantity: z.object({ value: z.number(), unit: z.string() }).nullable().default(null),
  is_antibiotic: z.boolean().default(false),
  antibiotic_justification: z.string().nullable().default(null),
  valid_until: z.string().nullable().default(null),   // vaccines: validity end as the vet states it (ISO date)
  site: z.string().nullable().default(null),          // vaccines: injection site
});
export type Dispensing = z.infer<typeof Dispensing>;

export const VisitContext = z.object({
  country: Country,
  microchip: z.string().nullable().default(null),
  owner: z.object({ name: z.string().nullable().default(null), tax_id: z.string().nullable().default(null) }).default({}),
  author: z.object({ name: z.string().nullable().default(null), registration: z.string().nullable().default(null) }).default({}),
  consent: z.object({ obtained: z.boolean(), scope: z.string().nullable().default(null), method: z.enum(['written', 'verbal', 'electronic']).nullable().default(null) }).nullable().default(null),
  prescription_number: z.string().nullable().default(null), // IT REV number
  dispensings: z.array(Dispensing).default([]),
});
export type VisitContext = z.infer<typeof VisitContext>;

export type CountryFlag = Missing & { rule: string; severity: 'block' | 'warn' };

const F = (field: string, reason: string, rule: string, severity: 'block' | 'warn' = 'warn'): CountryFlag => ({ field, reason, rule, severity });

const isVaccine = (m: Medication) => /vacc|impf|vakzin|vaccin/i.test(`${m.drug ?? ''} ${m.class_as_written ?? ''}`);
const given = (m: Medication) => m.status === 'dispensed' || m.status === 'prescribed' || m.status === 'performed';

/** Checks common to all four countries. */
function common(record: ClinicalRecord, ctx: VisitContext): CountryFlag[] {
  const out: CountryFlag[] = [];
  if (!ctx.author.name) out.push(F('author.name', 'Every clinical document needs the responsible veterinarian', 'author_required', 'block'));
  const procedures = record.treatments.filter((t) => t.type === 'procedure' && t.status === 'performed');
  if (procedures.length && !ctx.consent) out.push(F('consent', 'A procedure was performed; record whether consent was obtained and how', 'consent_for_procedure'));
  const declined = [...record.treatments, ...record.diagnostics, ...record.medications].filter((x) => x.status === 'declined');
  if (declined.length && !ctx.consent) out.push(F('consent', 'Care was declined; document the informed refusal (declined-care register)', 'declined_care_documented'));
  record.medications.forEach((m, i) => {
    if (given(m) && isVaccine(m)) {
      const d = ctx.dispensings.find((x) => x.medication_index === i);
      if (!d?.batch) out.push(F(`dispensings[${i}].batch`, 'Vaccine batch/lot number must be recorded', 'vaccine_batch', 'block'));
      if (!ctx.microchip) out.push(F('microchip', 'Vaccination entries need the animal\'s identification', 'microchip_for_vaccine'));
    }
  });
  return out;
}

/** Per-medication dispensing record fields: which ones a country requires. */
const dispensingFields: Record<Country, { fields: Array<keyof Dispensing>; rule: string; reason: string }> = {
  DE: { fields: ['product', 'authorisation_number', 'batch', 'quantity'], rule: 'de_taehav_abgabebeleg', reason: 'TÄHAV §15 with Art. 103(3) Reg. (EU) 2019/6: dispensing record requires product, authorisation no., batch and quantity' },
  AT: { fields: ['product', 'batch', 'quantity'], rule: 'at_tamg_abgabe', reason: 'TAMG dispensing documentation requires product, batch and quantity' },
  CH: { fields: ['product', 'quantity'], rule: 'ch_tamv_abgabe', reason: 'TAMV requires product and quantity for dispensed medicines' },
  IT: { fields: ['product'], rule: 'it_rev_prodotto', reason: 'The electronic prescription (REV) is issued per product' },
};

export function countryMissing(record: ClinicalRecord, _header: PatientHeader, ctx: VisitContext): CountryFlag[] {
  const out = common(record, ctx);
  const pack = dispensingFields[ctx.country];
  record.medications.forEach((m, i) => {
    if (!given(m)) return;
    const d = ctx.dispensings.find((x) => x.medication_index === i);
    for (const f of pack.fields) {
      if (!d || d[f] == null) out.push(F(`dispensings[${i}].${f}`, pack.reason, pack.rule));
    }
    if (ctx.country === 'DE' && (m.dose == null || !m.route || !m.duration)) out.push(F(`medications[${i}]`, 'TÄHAV §15(3) with Art. 105(5) Reg. (EU) 2019/6: dosage regimen must be on the dispensing record', 'de_taehav_anwendung'));
    if (d?.is_antibiotic && !d.antibiotic_justification) {
      const why = { DE: 'TÄHAV §13: antibiogram for the listed cases in dogs and cats, otherwise documented reasons for antibiotic use', IT: 'Antibiotic use must be justified on the REV', CH: 'IS ABV: indication required for every antibiotic dispensed', AT: 'TAMG: justification required for antibiotic use' }[ctx.country];
      out.push(F(`dispensings[${i}].antibiotic_justification`, why, `${ctx.country.toLowerCase()}_antibiotic_justification`, 'block'));
    }
    if (ctx.country === 'CH' && d?.is_antibiotic && !d.pack) out.push(F(`dispensings[${i}].pack`, 'IS ABV reporting needs the pack size', 'ch_isabv_pack'));
  });
  if (ctx.country === 'IT') {
    if (record.medications.some((m) => m.status === 'prescribed') && !ctx.prescription_number) out.push(F('prescription_number', 'Prescribed medicines in Italy go through the REV; record its number', 'it_rev_number'));
    if (!ctx.microchip) out.push(F('microchip', 'Anagrafe degli animali d\'affezione: identification on every record', 'it_microchip'));
    if (!ctx.owner.tax_id) out.push(F('owner.tax_id', 'Codice fiscale of the owner is needed for the invoice and the REV', 'it_codice_fiscale'));
    const procedures = record.treatments.filter((t) => t.type === 'procedure' && t.status === 'performed');
    if (procedures.length && ctx.consent && !ctx.consent.scope) out.push(F('consent.scope', 'Consenso informato must state modi e tempi of the procedure', 'it_consenso_modi_tempi'));
  }
  if (ctx.country === 'DE' && record.medications.some((m) => m.status === 'prescribed') && !ctx.owner.name) out.push(F('owner.name', 'A prescription (Art. 105 Reg. 2019/6) names the animal keeper', 'de_rezept_halter'));
  return dedupe(out);
}

function dedupe(flags: CountryFlag[]): CountryFlag[] {
  const seen = new Set<string>();
  return flags.filter((f) => { const k = `${f.field}|${f.rule}`; if (seen.has(k)) return false; seen.add(k); return true; });
}

/** Provenance counts for the badge printed on every document. The AI-added count is 0 by construction: every fact carries a span. */
export function provenance(record: ClinicalRecord, extra: Missing[] = []): { facts: number; not_recorded: number; ai_added: 0 } {
  const facts = record.history.length + record.examination.findings.length + record.diagnostics.length + record.treatments.length + record.medications.length
    + record.plan.instructions.length + (record.plan.follow_up ? 1 : 0) + (record.presenting_complaint ? 1 : 0) + (record.assessment.text ? 1 : 0)
    + Object.values(record.examination.vitals).filter(Boolean).length;
  return { facts, not_recorded: record.missing.length + extra.length, ai_added: 0 };
}

/** Anaesthesia / surgery record as the team enters it during the procedure. Nothing here is extracted from prose. */
export const AnaesthesiaRecord = z.object({
  procedure: z.string().nullable().default(null),
  asa: z.enum(['1', '2', '3', '4', '5', 'E']).nullable().default(null),
  fasted_hours: z.number().nullable().default(null),
  premedication: z.string().nullable().default(null),
  induction: z.string().nullable().default(null),
  maintenance: z.string().nullable().default(null),
  airway: z.string().nullable().default(null),
  iv_access: z.boolean().nullable().default(null),
  fluids: z.string().nullable().default(null),
  monitoring: z.array(z.object({ time: z.string(), hr: z.number().nullable().default(null), rr: z.number().nullable().default(null), temp: z.number().nullable().default(null), spo2: z.number().nullable().default(null), map: z.number().nullable().default(null), note: z.string().nullable().default(null) })).default([]),
  implants: z.array(z.object({ description: z.string(), batch: z.string().nullable().default(null) })).default([]),
  complications: z.string().nullable().default(null),
  recovery: z.string().nullable().default(null),
  anaesthetist: z.string().nullable().default(null),
  surgeon: z.string().nullable().default(null),
  start: z.string().nullable().default(null),
  end: z.string().nullable().default(null),
});
export type AnaesthesiaRecord = z.infer<typeof AnaesthesiaRecord>;
