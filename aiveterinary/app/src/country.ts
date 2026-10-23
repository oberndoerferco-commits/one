import type { ClinicalRecord, Medication, Missing, PatientHeader } from './schema.js';
import { z } from 'zod';
import type { Lang } from './render.js';

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
  is_controlled: z.boolean().default(false),           // narcotics / controlled substances (BtMVV, Tab. II etc.)
  valid_until: z.string().nullable().default(null),   // vaccines: validity end as the vet states it (ISO date)
  site: z.string().nullable().default(null),          // vaccines: injection site
});
export type Dispensing = z.infer<typeof Dispensing>;

export const VisitContext = z.object({
  country: Country,
  microchip: z.string().nullable().default(null),
  owner: z.object({ name: z.string().nullable().default(null), tax_id: z.string().nullable().default(null) }).prefault({}),
  author: z.object({ name: z.string().nullable().default(null), registration: z.string().nullable().default(null) }).prefault({}),
  consent: z.object({ obtained: z.boolean(), scope: z.string().nullable().default(null), method: z.enum(['written', 'verbal', 'electronic']).nullable().default(null) }).nullable().default(null),
  prescription_number: z.string().nullable().default(null), // IT REV number
  /**
   * Whether the treated animal is kept for food production, as the vet states it. `null` = not
   * stated: derived from the species (see `isFoodProducing`). Needed where the law depends on it,
   * e.g. CH TAMV art. 25–27 (Nutztiere only); a horse, rabbit or bird is a Heimtier only when
   * kept as a companion (TAMV art. 3 para. 1 let. b), which the species alone cannot say.
   */
  food_producing: z.boolean().nullable().default(null),
  interpretations: z.array(z.object({ diagnostic_index: z.number().int().nonnegative(), text: z.string() })).default([]), // vet's own words per result, for the owner explanation
  dispensings: z.array(Dispensing).default([]),
});
export type VisitContext = z.infer<typeof VisitContext>;

export type CountryFlag = Missing & { rule: string; severity: 'block' | 'warn' };

/**
 * Flag reasons per rule, in the workspace / document language. Law names and
 * article numbers stay as cited; only the explanation is translated.
 */
const REASON: Record<Lang, Record<string, string>> = {
  en: {
    author_required: 'Every clinical document needs the responsible veterinarian',
    consent_for_procedure: 'A procedure was performed; record whether consent was obtained and how',
    declined_care_documented: 'Care was declined; document the informed refusal (declined-care register)',
    vaccine_batch: 'Vaccine batch/lot number must be recorded',
    microchip_for_vaccine: 'Vaccination entries need the animal\'s identification',
    de_taehav_abgabebeleg: 'TÄHAV §15 with Art. 103(3) Reg. (EU) 2019/6: dispensing record requires product, authorisation no., batch and quantity',
    at_tamg_abgabe: 'TAMG § 68(1): dispensing from the practice pharmacy requires product with authorisation no. and quantity; batch no. under Art. 103(3) Reg. (EU) 2019/6 (prescription-only products) and § 68(2) (food-producing animals)',
    ch_tamv_abgabe: 'TAMV art. 25–27: dispensing for farm animals (Nutztiere) requires product and quantity',
    it_rev_prodotto: 'The electronic prescription (REV) is issued per product',
    de_taehav_anwendung: 'TÄHAV §15(3) with Art. 105(5) Reg. (EU) 2019/6: dosage regimen must be on the dispensing record',
    de_antibiotic_justification: 'TÄHAV §13: antibiogram for the listed cases in dogs and cats, otherwise documented reasons for antibiotic use',
    it_antibiotic_justification: 'Antibiotic use must be justified on the REV',
    ch_antibiotic_justification: 'IS ABV: indication required for every antibiotic dispensed',
    at_antibiotic_justification: 'TAMG: justification required for antibiotic use',
    ch_isabv_pack: 'IS ABV reporting needs the pack size',
    it_rev_number: 'Prescribed medicines in Italy go through the REV; record its number',
    it_microchip: 'Anagrafe degli animali d\'affezione: identification on every record',
    it_codice_fiscale: 'Codice fiscale of the owner (the person paying) is needed for the invoice, the REV and the Sistema TS expense data (D.M. MEF 1/9/2016 art. 2; D.M. RGS 16/9/2016 art. 2 c. 2)',
    it_scarico_quantita: 'D.Lgs. 218/2023 art. 37 c. 2: record the packs or fractions handed over from stock; the scarico is due within 7 days',
    it_consenso_modi_tempi: 'Consenso informato must state modi e tempi of the procedure',
    de_rezept_halter: 'A prescription (Art. 105 Reg. 2019/6) names the animal keeper',
  },
  de: {
    author_required: 'Jedes klinische Dokument muss die verantwortliche Tierärztin bzw. den verantwortlichen Tierarzt nennen',
    consent_for_procedure: 'Ein Eingriff wurde durchgeführt; dokumentieren, ob und wie die Einwilligung eingeholt wurde',
    declined_care_documented: 'Eine Behandlung wurde abgelehnt; die Ablehnung nach Aufklärung dokumentieren (Register abgelehnter Behandlungen)',
    vaccine_batch: 'Die Chargennummer des Impfstoffs muss erfasst werden',
    microchip_for_vaccine: 'Impfeinträge brauchen die Kennzeichnung des Tieres',
    de_taehav_abgabebeleg: 'TÄHAV §15 i. V. m. Art. 103(3) VO (EU) 2019/6: der Abgabebeleg erfordert Präparat, Zulassungsnummer, Charge und Menge',
    at_tamg_abgabe: 'TAMG § 68(1): die Abgabe aus der Hausapotheke erfordert Präparat mit Zulassungsnummer und Menge; Chargennummer nach Art. 103(3) VO (EU) 2019/6 (verschreibungspflichtige Präparate) und § 68(2) (Lebensmittel liefernde Tiere)',
    ch_tamv_abgabe: 'TAMV Art. 25–27: bei der Abgabe für Nutztiere sind Präparat und Menge erforderlich',
    it_rev_prodotto: 'Das elektronische Rezept (REV) wird je Präparat ausgestellt',
    de_taehav_anwendung: 'TÄHAV §15(3) i. V. m. Art. 105(5) VO (EU) 2019/6: das Dosierungsschema muss auf dem Abgabebeleg stehen',
    de_antibiotic_justification: 'TÄHAV §13: Antibiogramm in den genannten Fällen bei Hund und Katze, sonst dokumentierte Gründe für den Antibiotikaeinsatz',
    it_antibiotic_justification: 'Der Antibiotikaeinsatz muss auf dem REV begründet werden',
    ch_antibiotic_justification: 'IS ABV: für jedes abgegebene Antibiotikum ist die Indikation erforderlich',
    at_antibiotic_justification: 'TAMG: Begründung für den Antibiotikaeinsatz erforderlich',
    ch_isabv_pack: 'Die Meldung an IS ABV braucht die Packungsgröße',
    it_rev_number: 'Verschriebene Arzneimittel laufen in Italien über das REV; dessen Nummer erfassen',
    it_microchip: 'Anagrafe degli animali d\'affezione: Kennzeichnung auf jedem Eintrag',
    it_codice_fiscale: 'Der Codice fiscale des Halters (der zahlenden Person) wird für die Rechnung, das REV und die Ausgabendaten an Sistema TS benötigt (D.M. MEF 1/9/2016 Art. 2; D.M. RGS 16/9/2016 Art. 2 c. 2)',
    it_scarico_quantita: 'D.Lgs. 218/2023 Art. 37 c. 2: die aus dem Bestand abgegebenen Packungen oder Teilmengen erfassen; das scarico ist binnen 7 Tagen fällig',
    it_consenso_modi_tempi: 'Der Consenso informato muss modi e tempi (Art und Zeitpunkt) des Eingriffs angeben',
    de_rezept_halter: 'Ein Rezept (Art. 105 VO 2019/6) nennt den Tierhalter',
  },
  it: {
    author_required: 'Ogni documento clinico deve indicare il veterinario responsabile',
    consent_for_procedure: 'È stata eseguita una procedura; registrare se e come è stato ottenuto il consenso',
    declined_care_documented: 'Le cure sono state rifiutate; documentare il rifiuto informato (registro delle cure rifiutate)',
    vaccine_batch: 'Il numero di lotto del vaccino deve essere registrato',
    microchip_for_vaccine: 'Le registrazioni delle vaccinazioni richiedono l\'identificazione dell\'animale',
    de_taehav_abgabebeleg: 'TÄHAV §15 in combinato disposto con art. 103(3) Reg. (UE) 2019/6: il documento di cessione richiede prodotto, n. di autorizzazione, lotto e quantità',
    at_tamg_abgabe: 'TAMG § 68(1): la cessione dalla farmacia dell\'ambulatorio richiede prodotto con n. di autorizzazione e quantità; n. di lotto ai sensi dell\'art. 103(3) Reg. (UE) 2019/6 (prodotti soggetti a prescrizione) e del § 68(2) (animali destinati alla produzione di alimenti)',
    ch_tamv_abgabe: 'TAMV art. 25–27: per la cessione per animali da reddito (Nutztiere) servono prodotto e quantità',
    it_rev_prodotto: 'La ricetta elettronica veterinaria (REV) si emette per singolo prodotto',
    de_taehav_anwendung: 'TÄHAV §15(3) in combinato disposto con art. 105(5) Reg. (UE) 2019/6: lo schema posologico deve figurare nel documento di cessione',
    de_antibiotic_justification: 'TÄHAV §13: antibiogramma nei casi previsti per cani e gatti, altrimenti motivazioni documentate per l\'uso dell\'antibiotico',
    it_antibiotic_justification: 'L\'uso dell\'antibiotico deve essere motivato nella REV',
    ch_antibiotic_justification: 'IS ABV: indicazione obbligatoria per ogni antibiotico ceduto',
    at_antibiotic_justification: 'TAMG: è richiesta la motivazione dell\'uso dell\'antibiotico',
    ch_isabv_pack: 'La segnalazione a IS ABV richiede la dimensione della confezione',
    it_rev_number: 'In Italia i medicinali prescritti passano dalla REV; registrarne il numero',
    it_microchip: 'Anagrafe degli animali d\'affezione: identificazione su ogni registrazione',
    it_codice_fiscale: 'Il codice fiscale del proprietario (di chi paga) serve per la fattura, la REV e l\'invio delle spese al Sistema TS (D.M. MEF 1/9/2016 art. 2; D.M. RGS 16/9/2016 art. 2 c. 2)',
    it_scarico_quantita: 'D.Lgs. 218/2023 art. 37 c. 2: registrare le confezioni o frazioni consegnate dalla scorta; lo scarico va fatto entro 7 giorni',
    it_consenso_modi_tempi: 'Il consenso informato deve indicare modi e tempi della procedura',
    de_rezept_halter: 'Una ricetta (art. 105 Reg. 2019/6) indica il detentore dell\'animale',
  },
};

const flagger = (lang: Lang) => (field: string, rule: string, severity: 'block' | 'warn' = 'warn'): CountryFlag =>
  ({ field, reason: (REASON[lang] ?? REASON.en)[rule] ?? REASON.en[rule], rule, severity });

const isVaccine = (m: Medication) => /vacc|impf|vakzin|vaccin/i.test(`${m.drug ?? ''} ${m.class_as_written ?? ''}`);
const given = (m: Medication) => m.status === 'dispensed' || m.status === 'prescribed' || m.status === 'performed';

/** Checks common to all four countries. */
function common(record: ClinicalRecord, ctx: VisitContext, F: ReturnType<typeof flagger>): CountryFlag[] {
  const out: CountryFlag[] = [];
  if (!ctx.author.name) out.push(F('author.name', 'author_required', 'block'));
  const procedures = record.treatments.filter((t) => t.type === 'procedure' && t.status === 'performed');
  if (procedures.length && !ctx.consent) out.push(F('consent', 'consent_for_procedure'));
  const declined = [...record.treatments, ...record.diagnostics, ...record.medications].filter((x) => x.status === 'declined');
  if (declined.length && !ctx.consent) out.push(F('consent', 'declined_care_documented'));
  record.medications.forEach((m, i) => {
    if (given(m) && isVaccine(m)) {
      const d = ctx.dispensings.find((x) => x.medication_index === i);
      if (!d?.batch) out.push(F(`dispensings[${i}].batch`, 'vaccine_batch', 'block'));
      if (!ctx.microchip) out.push(F('microchip', 'microchip_for_vaccine'));
    }
  });
  return out;
}

/** Per-medication dispensing record fields: which ones a country requires. */
const dispensingFields: Record<Country, { fields: Array<keyof Dispensing>; rule: string; foodProducingOnly?: true }> = {
  DE: { fields: ['product', 'authorisation_number', 'batch', 'quantity'], rule: 'de_taehav_abgabebeleg' },
  // TAMG § 68(1) Z 4–5: quantity, product and authorisation no. for every dispensing, pets included.
  // Batch: § 68(2) Z 8 for food-producing animals, and § 68(1) is "unbeschadet des Art. 103" Reg. 2019/6,
  // whose para. 3 lit. c wants the batch for every prescription-only transaction, so it stays for all species.
  AT: { fields: ['product', 'authorisation_number', 'batch', 'quantity'], rule: 'at_tamg_abgabe' },
  // TAMV art. 25 (bookkeeping duty) and art. 27 para. 1 ("bei jeder Abgabe von Arzneimitteln für Nutztiere").
  CH: { fields: ['product', 'quantity'], rule: 'ch_tamv_abgabe', foodProducingOnly: true },
  IT: { fields: ['product'], rule: 'it_rev_prodotto' },
};

/**
 * Species that are never food-producing under the packs' laws (dogs, cats, ferrets). Every other
 * species (horse, rabbit, bird, reptile, other) can be: in the EU an equine is food-producing unless
 * its passport declares it not intended for slaughter (Art. 112(4) Reg. 2019/6, TAMG § 57(3)); in CH
 * equids, domestic rabbits and poultry, farmed reptiles etc. are Heimtiere only when kept as companions
 * (TAMV art. 3 para. 1 let. b). Without the vet's statement those count as food-producing, so the
 * stricter record is asked for.
 */
const NEVER_FOOD_PRODUCING: ReadonlySet<PatientHeader['species']> = new Set(['dog', 'cat', 'ferret']);
export const isFoodProducing = (header: Pick<PatientHeader, 'species'>, ctx: Pick<VisitContext, 'food_producing'>): boolean =>
  ctx.food_producing ?? !NEVER_FOOD_PRODUCING.has(header.species);

export function countryMissing(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en'): CountryFlag[] {
  const F = flagger(lang);
  const out = common(record, ctx, F);
  const pack = dispensingFields[ctx.country];
  const packApplies = !pack.foodProducingOnly || isFoodProducing(header, ctx);
  record.medications.forEach((m, i) => {
    if (!given(m)) return;
    const d = ctx.dispensings.find((x) => x.medication_index === i);
    if (packApplies) {
      for (const f of pack.fields) {
        if (!d || d[f] == null) out.push(F(`dispensings[${i}].${f}`, pack.rule));
      }
    }
    // IT: a medicine handed over from the vet's own stock is unloaded (scarico) in the traceability system within 7 days.
    if (ctx.country === 'IT' && m.status === 'dispensed' && !d?.quantity) out.push(F(`dispensings[${i}].quantity`, 'it_scarico_quantita'));
    if (ctx.country === 'DE' && (m.dose == null || !m.route || !m.duration)) out.push(F(`medications[${i}]`, 'de_taehav_anwendung'));
    if (d?.is_antibiotic && !d.antibiotic_justification) {
      out.push(F(`dispensings[${i}].antibiotic_justification`, `${ctx.country.toLowerCase()}_antibiotic_justification`, 'block'));
    }
    if (ctx.country === 'CH' && d?.is_antibiotic && !d.pack) out.push(F(`dispensings[${i}].pack`, 'ch_isabv_pack'));
  });
  if (ctx.country === 'IT') {
    if (record.medications.some((m) => m.status === 'prescribed') && !ctx.prescription_number) out.push(F('prescription_number', 'it_rev_number'));
    if (!ctx.microchip) out.push(F('microchip', 'it_microchip'));
    if (!ctx.owner.tax_id) out.push(F('owner.tax_id', 'it_codice_fiscale'));
    const procedures = record.treatments.filter((t) => t.type === 'procedure' && t.status === 'performed');
    if (procedures.length && ctx.consent && !ctx.consent.scope) out.push(F('consent.scope', 'it_consenso_modi_tempi'));
  }
  if (ctx.country === 'DE' && record.medications.some((m) => m.status === 'prescribed') && !ctx.owner.name) out.push(F('owner.name', 'de_rezept_halter'));
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
