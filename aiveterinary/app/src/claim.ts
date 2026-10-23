import type { ClinicalRecord, Medication, PatientHeader } from './schema.js';
import type { VisitContext } from './country.js';
import { renderMedicationTable, type Lang } from './render.js';

/**
 * Insurance claim pack: the fields pet-insurance claim forms and invoice rules
 * ask the practice for (see docs/18-insurance-claim-fields.md), filled only from
 * the approved record, the locked patient header, the visit context and what
 * the vet typed at the claim step. Every value says where it came from.
 *
 * What this module never does:
 * - compute a fee, a factor, a line total or an invoice total (amounts and
 *   factors are strings exactly as the practice typed them);
 * - infer a diagnosis or a diagnosis code (the diagnosis is the vet's own
 *   assessment sentence or the vet's typed text; differentials are not used);
 * - answer "pre-existing?", "accident or illness?" or "first symptoms on?"
 *   (vet-typed or null, never derived from history such as "for 5 days").
 * Everything absent is null and listed in `missing`.
 */

/** Where a value came from: header.*, record.*, ctx.* or opts.* (vet-typed at the claim step). */
export type Source = `header.${string}` | `record.${string}` | `ctx.${string}` | `opts.${string}`;
export type Sourced<T> = { value: T; source: Source };

/** One invoice line as typed by the practice. Nothing here is calculated. */
export type ClaimInvoiceLine = {
  date: string | null;               // ISO date of the service
  description: string;               // the service as on the invoice
  got_number?: string | null;        // DE: GOT Gebührenverzeichnis no. (§ 7(4) GOT: "laufende Nummer")
  factor?: string | null;            // DE: Satz/Faktor as typed, e.g. "2,0" (never multiplied here)
  quantity?: string | null;          // as typed
  amount?: string | null;            // as typed, e.g. "23,45 €" (never summed here)
};

export type ClaimOpts = {
  approved?: boolean;
  insurer?: string | null;
  policy_number?: string | null;
  date_of_birth?: string | null;      // ISO; the header only has an age, so DOB is typed
  condition_type?: 'illness' | 'accident' | null;
  first_symptom_date?: string | null; // ISO; only if the vet typed it
  diagnosis?: string | null;          // vet's wording for the insurer; overrides the assessment sentence
  pre_existing?: boolean | null;      // the vet's answer; never derived
  pre_existing_note?: string | null;
  surgery?: boolean | null;           // AGILA asks for "OP" to be marked on surgery invoices
  setting?: 'outpatient' | 'day_hospital' | 'inpatient' | null;
  visit_date?: string | null;         // ISO date of this consultation
  practice?: { name?: string | null; address?: string | null };
  invoice?: { number?: string | null; date?: string | null; lines?: ClaimInvoiceLine[]; total?: string | null; vat?: string | null };
};

export type ClaimField =
  | 'patient.name' | 'patient.species' | 'patient.breed' | 'patient.sex' | 'patient.neuter_status' | 'patient.date_of_birth' | 'patient.age' | 'patient.microchip'
  | 'owner.name' | 'insurer.name' | 'insurer.policy_number'
  | 'clinical.condition_type' | 'clinical.first_symptom_date' | 'clinical.presenting_complaint' | 'clinical.diagnosis' | 'clinical.treatment_dates'
  | 'clinical.pre_existing' | 'clinical.surgery' | 'clinical.setting'
  | 'invoice.number' | 'invoice.date' | 'invoice.lines' | 'invoice.total' | 'invoice.vat'
  | 'practice.vet_name' | 'practice.vet_registration' | 'practice.name' | 'practice.address'
  | `invoice.lines[${number}].${'date' | 'got_number' | 'factor' | 'amount'}`;

export type ClaimPack = {
  country: VisitContext['country'];
  approved: boolean;
  patient: {
    name: Sourced<string> | null;
    species: Sourced<NonNullable<PatientHeader['species']>> | null;
    breed: Sourced<string> | null;
    sex: Sourced<'female' | 'male'> | null;
    neuter_status: Sourced<'intact' | 'neutered'> | null;
    date_of_birth: Sourced<string> | null;
    age: Sourced<{ value: number; unit: 'day' | 'week' | 'month' | 'year' }> | null;
    microchip: Sourced<string> | null;
  };
  owner: { name: Sourced<string> | null };
  insurer: { name: Sourced<string> | null; policy_number: Sourced<string> | null };
  clinical: {
    condition_type: Sourced<'illness' | 'accident'> | null;
    first_symptom_date: Sourced<string> | null;
    presenting_complaint: Sourced<string> | null;
    diagnosis: Sourced<string> | null;
    treatment_dates: Sourced<string[]> | null;
    treatments: Sourced<string>[];      // performed treatments, record wording
    diagnostics: Sourced<string>[];     // performed diagnostics with result, record wording
    medications: Medication[];          // given today (dispensed / prescribed / performed), record items
    pre_existing: Sourced<boolean> | null;
    pre_existing_note: Sourced<string> | null;
    surgery: Sourced<boolean> | null;
    setting: Sourced<'outpatient' | 'day_hospital' | 'inpatient'> | null;
  };
  invoice: {
    number: Sourced<string> | null;
    date: Sourced<string> | null;
    lines: Sourced<ClaimInvoiceLine[]> | null;
    total: Sourced<string> | null;
    vat: Sourced<string> | null;
  };
  practice: {
    vet_name: Sourced<string> | null;
    vet_registration: Sourced<string> | null;
    name: Sourced<string> | null;
    address: Sourced<string> | null;
  };
  missing: ClaimField[];
};

const typed = (v: string | null | undefined): string | null => (typeof v === 'string' && v.trim() ? v.trim() : null);
function s<T>(value: T | null | undefined, source: Source): Sourced<T> | null {
  if (value == null) return null;
  if (typeof value === 'string' && !value.trim()) return null;
  return { value: (typeof value === 'string' ? value.trim() : value) as T, source };
}
const dateSource = (visit: boolean, lines: boolean): Source => (visit && lines ? 'opts.visit_date+opts.invoice.lines[].date' : lines ? 'opts.invoice.lines[].date' : 'opts.visit_date');
const given = (m: Medication) => m.status === 'dispensed' || m.status === 'prescribed' || m.status === 'performed';

/** Builds the claim pack. Header values win over record values (locked facts); record signalment is the fallback. */
export function buildClaimPack(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, opts: ClaimOpts = {}): ClaimPack {
  const lines = (opts.invoice?.lines ?? []).filter((l) => typed(l.description));
  const dates = [...new Set([typed(opts.visit_date), ...lines.map((l) => typed(l.date))].filter((d): d is string => d != null))].sort();

  const pack: ClaimPack = {
    country: ctx.country,
    approved: opts.approved === true,
    patient: {
      name: s(header.name, 'header.name') ?? s(record.patient.name, 'record.patient.name'),
      species: s(header.species, 'header.species') ?? s(record.patient.species, 'record.patient.species'),
      breed: s(header.breed, 'header.breed') ?? s(record.patient.breed, 'record.patient.breed'),
      sex: s(header.sex, 'header.sex') ?? s(record.patient.sex, 'record.patient.sex'),
      neuter_status: s(header.neuter_status, 'header.neuter_status') ?? s(record.patient.neuter_status, 'record.patient.neuter_status'),
      date_of_birth: s(opts.date_of_birth, 'opts.date_of_birth'),
      age: s(header.age, 'header.age') ?? s(record.patient.age, 'record.patient.age'),
      microchip: s(ctx.microchip, 'ctx.microchip'),
    },
    owner: { name: s(ctx.owner.name, 'ctx.owner.name') },
    insurer: { name: s(opts.insurer, 'opts.insurer'), policy_number: s(opts.policy_number, 'opts.policy_number') },
    clinical: {
      condition_type: s(opts.condition_type, 'opts.condition_type'),
      first_symptom_date: s(opts.first_symptom_date, 'opts.first_symptom_date'),
      presenting_complaint: s(record.presenting_complaint?.text, 'record.presenting_complaint.text'),
      // the vet's typed wording, else the vet's own assessment sentence; differentials are never promoted
      diagnosis: s(opts.diagnosis, 'opts.diagnosis') ?? s(record.assessment.text, 'record.assessment.text'),
      treatment_dates: dates.length ? { value: dates, source: dateSource(typed(opts.visit_date) != null, lines.some((l) => typed(l.date))) } : null,
      treatments: record.treatments.flatMap((t, i) => (t.status === 'performed' ? [{ value: t.text, source: `record.treatments[${i}].text` as Source }] : [])),
      diagnostics: record.diagnostics.flatMap((d, i) => (d.status === 'performed' ? [{ value: d.result ? `${d.test}: ${d.result}` : d.test, source: `record.diagnostics[${i}]` as Source }] : [])),
      medications: record.medications.filter(given),
      pre_existing: s(opts.pre_existing, 'opts.pre_existing'),
      pre_existing_note: s(opts.pre_existing_note, 'opts.pre_existing_note'),
      surgery: s(opts.surgery, 'opts.surgery'),
      setting: s(opts.setting, 'opts.setting'),
    },
    invoice: {
      number: s(opts.invoice?.number, 'opts.invoice.number'),
      date: s(opts.invoice?.date, 'opts.invoice.date'),
      lines: lines.length ? { value: lines.map((l) => ({ ...l, description: l.description.trim() })), source: 'opts.invoice.lines' } : null,
      total: s(opts.invoice?.total, 'opts.invoice.total'),
      vat: s(opts.invoice?.vat, 'opts.invoice.vat'),
    },
    practice: {
      vet_name: s(ctx.author.name, 'ctx.author.name'),
      vet_registration: s(ctx.author.registration, 'ctx.author.registration'),
      name: s(opts.practice?.name, 'opts.practice.name'),
      address: s(opts.practice?.address, 'opts.practice.address'),
    },
    missing: [],
  };
  pack.missing = listMissing(pack);
  return pack;
}

/** Every null field, in form order; per invoice line the date and amount, and in DE the GOT number and factor (§ 7(4) GOT, insurer AVB). */
function listMissing(p: ClaimPack): ClaimField[] {
  const out: ClaimField[] = [];
  const groups = { patient: p.patient, owner: p.owner, insurer: p.insurer, clinical: p.clinical, invoice: p.invoice, practice: p.practice } as const;
  for (const [g, obj] of Object.entries(groups)) {
    for (const [k, v] of Object.entries(obj)) {
      if (k === 'pre_existing_note') continue; // only meaningful with a "yes"
      if (v === null) out.push(`${g}.${k}` as ClaimField);
    }
  }
  (p.invoice.lines?.value ?? []).forEach((l, i) => {
    if (!typed(l.date)) out.push(`invoice.lines[${i}].date`);
    if (p.country === 'DE' && !typed(l.got_number)) out.push(`invoice.lines[${i}].got_number`);
    if (p.country === 'DE' && !typed(l.factor)) out.push(`invoice.lines[${i}].factor`);
    if (!typed(l.amount)) out.push(`invoice.lines[${i}].amount`);
  });
  return out;
}

/* ------------------------------------------------------------------ */
/* One-page summary for the insurer. Headings and labels are code; every */
/* value is printed as found in the pack; absent values are flags.       */

const T = {
  en: {
    title: 'Information for the pet insurer', draft: 'DRAFT — not yet approved by the veterinarian',
    note: 'Prepared from the approved clinical record and the veterinarian\'s own entries. The veterinarian checks and confirms these details with stamp and signature. This is not an invoice: amounts, GOT numbers and factors are shown exactly as the practice entered them; nothing was calculated.',
    patient: 'Animal', owner: 'Owner', insurer: 'Insurer', policy: 'Policy number', name: 'Name', species: 'Species', breed: 'Breed', sex: 'Sex', neuter: 'Neutered', dob: 'Date of birth', age: 'Age', chip: 'Microchip',
    clinical: 'Clinical details', type: 'Accident or illness', first: 'First symptoms on', complaint: 'Reason for presentation', diagnosis: 'Diagnosis', dates: 'Treatment dates', treatments: 'Treatment performed', diagnostics: 'Diagnostics performed', meds: 'Medication', pre: 'Pre-existing condition (veterinarian\'s statement)', surgery: 'Surgery', setting: 'Setting',
    invoice: 'Invoice', invNo: 'Invoice number', invDate: 'Invoice date', date: 'Date', service: 'Service', got: 'GOT no.', factor: 'Factor', qty: 'Qty', amount: 'Amount', total: 'Invoice total (as entered)', vat: 'VAT (as entered)',
    practice: 'Practice', vet: 'Treating veterinarian', reg: 'Registration', pname: 'Practice', address: 'Address', stamp: 'Practice stamp and signature of the veterinarian', place: 'Place, date',
    missing: 'Missing', missingIntro: 'Not in the record and not entered; to be completed before sending:',
    yes: 'yes', no: 'no', illness: 'illness', accident: 'accident', outpatient: 'outpatient', day_hospital: 'day hospital', inpatient: 'inpatient',
    species_: { dog: 'dog', cat: 'cat', rabbit: 'rabbit', ferret: 'ferret', horse: 'horse', bird: 'bird', reptile: 'reptile', other: 'other' } as Record<string, string>,
    sex_: { female: 'female', male: 'male' } as Record<string, string>, unit: { day: 'days', week: 'weeks', month: 'months', year: 'years' } as Record<string, string>,
  },
  de: {
    title: 'Angaben für die Tierversicherung', draft: 'ENTWURF — noch nicht tierärztlich freigegeben',
    note: 'Erstellt aus dem freigegebenen Behandlungsdatensatz und den eigenen Eingaben der Tierärztin / des Tierarztes. Die Tierärztin / der Tierarzt prüft und bestätigt diese Angaben mit Praxisstempel und Unterschrift. Dies ist keine Rechnung: Beträge, GOT-Nummern und Faktoren stehen hier genau so, wie die Praxis sie eingetragen hat; nichts wurde berechnet.',
    patient: 'Tier', owner: 'Tierhalter/in', insurer: 'Versicherer', policy: 'Versicherungsnummer', name: 'Name', species: 'Tierart', breed: 'Rasse', sex: 'Geschlecht', neuter: 'Kastriert', dob: 'Geburtsdatum', age: 'Alter', chip: 'Chipnummer',
    clinical: 'Medizinische Angaben', type: 'Unfall oder Krankheit', first: 'Erste Symptome am', complaint: 'Vorstellungsgrund', diagnosis: 'Diagnose', dates: 'Behandlungsdaten', treatments: 'Durchgeführte Behandlung', diagnostics: 'Durchgeführte Diagnostik', meds: 'Medikation', pre: 'Vorerkrankung (Angabe der Tierärztin / des Tierarztes)', surgery: 'Operation (OP)', setting: 'Behandlungsform',
    invoice: 'Rechnung', invNo: 'Rechnungsnummer', invDate: 'Rechnungsdatum', date: 'Datum', service: 'Leistung', got: 'GOT-Nr.', factor: 'Faktor', qty: 'Menge', amount: 'Betrag', total: 'Rechnungsbetrag (wie eingetragen)', vat: 'USt. (wie eingetragen)',
    practice: 'Praxis', vet: 'Behandelnde Tierärztin / behandelnder Tierarzt', reg: 'Registrierung', pname: 'Praxis', address: 'Anschrift', stamp: 'Praxisstempel und Unterschrift der Tierärztin / des Tierarztes', place: 'Ort, Datum',
    missing: 'Fehlt', missingIntro: 'Weder im Datensatz noch eingetragen; vor dem Versand ergänzen:',
    yes: 'ja', no: 'nein', illness: 'Krankheit', accident: 'Unfall', outpatient: 'ambulant', day_hospital: 'tagesstationär', inpatient: 'stationär',
    species_: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'anderes Tier' } as Record<string, string>,
    sex_: { female: 'weiblich', male: 'männlich' } as Record<string, string>, unit: { day: 'Tage', week: 'Wochen', month: 'Monate', year: 'Jahre' } as Record<string, string>,
  },
  it: {
    title: 'Dati per l\'assicurazione', draft: 'BOZZA — non ancora approvata dal veterinario',
    note: 'Redatto dalla cartella clinica approvata e dai dati inseriti dal veterinario. Il veterinario verifica e conferma questi dati con timbro e firma. Questo non è una fattura: importi, codici e fattori sono riportati esattamente come inseriti dalla struttura; nulla è stato calcolato.',
    patient: 'Animale', owner: 'Proprietario', insurer: 'Compagnia', policy: 'Numero di polizza', name: 'Nome', species: 'Specie', breed: 'Razza', sex: 'Sesso', neuter: 'Sterilizzato', dob: 'Data di nascita', age: 'Età', chip: 'Microchip',
    clinical: 'Dati clinici', type: 'Infortunio o malattia', first: 'Insorgenza dei sintomi il', complaint: 'Motivo della visita', diagnosis: 'Diagnosi', dates: 'Date delle prestazioni', treatments: 'Prestazioni eseguite', diagnostics: 'Esami eseguiti', meds: 'Terapia farmacologica', pre: 'Patologia preesistente (dichiarazione del veterinario)', surgery: 'Intervento chirurgico', setting: 'Regime',
    invoice: 'Fattura', invNo: 'Numero fattura', invDate: 'Data fattura', date: 'Data', service: 'Prestazione', got: 'Codice', factor: 'Fattore', qty: 'Q.tà', amount: 'Importo', total: 'Totale fattura (come inserito)', vat: 'IVA (come inserita)',
    practice: 'Struttura', vet: 'Medico veterinario curante', reg: 'Iscrizione all\'Ordine', pname: 'Struttura', address: 'Indirizzo', stamp: 'Timbro della struttura e firma del medico veterinario', place: 'Luogo, data',
    missing: 'Mancante', missingIntro: 'Non presente nella cartella e non inserito; da completare prima dell\'invio:',
    yes: 'sì', no: 'no', illness: 'malattia', accident: 'infortunio', outpatient: 'ambulatoriale', day_hospital: 'day hospital', inpatient: 'ricovero',
    species_: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' } as Record<string, string>,
    sex_: { female: 'femmina', male: 'maschio' } as Record<string, string>, unit: { day: 'giorni', week: 'settimane', month: 'mesi', year: 'anni' } as Record<string, string>,
  },
};

/** Field label for the "missing" list, in the summary language. */
function fieldLabel(f: ClaimField, t: (typeof T)['en']): string {
  const m = /^invoice\.lines\[(\d+)\]\.(\w+)$/.exec(f);
  if (m) {
    const col: Record<string, string> = { date: t.date, got_number: t.got, factor: t.factor, amount: t.amount };
    return `${t.invoice} ${t.service.toLowerCase()} ${Number(m[1]) + 1}: ${col[m[2]] ?? m[2]}`;
  }
  const map: Record<string, string> = {
    'patient.name': t.name, 'patient.species': t.species, 'patient.breed': t.breed, 'patient.sex': t.sex, 'patient.neuter_status': t.neuter, 'patient.date_of_birth': t.dob, 'patient.age': t.age, 'patient.microchip': t.chip,
    'owner.name': t.owner, 'insurer.name': t.insurer, 'insurer.policy_number': t.policy,
    'clinical.condition_type': t.type, 'clinical.first_symptom_date': t.first, 'clinical.presenting_complaint': t.complaint, 'clinical.diagnosis': t.diagnosis, 'clinical.treatment_dates': t.dates,
    'clinical.pre_existing': t.pre, 'clinical.surgery': t.surgery, 'clinical.setting': t.setting,
    'invoice.number': t.invNo, 'invoice.date': t.invDate, 'invoice.lines': `${t.invoice}: ${t.service}`, 'invoice.total': t.total, 'invoice.vat': t.vat,
    'practice.vet_name': t.vet, 'practice.vet_registration': t.reg, 'practice.name': t.pname, 'practice.address': t.address,
  };
  return map[f] ?? f;
}

export function renderClaimSummary(pack: ClaimPack, lang: Lang = 'en'): string {
  const t = T[lang] ?? T.en;
  const flagged = `▲ ${t.missing}`;
  const v = <X>(x: Sourced<X> | null, show: (val: X) => string = String) => (x ? show(x.value) : flagged);
  const yn = (b: boolean) => (b ? t.yes : t.no);
  const out: string[] = [];
  out.push(`# ${t.title}`);
  if (!pack.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`_${t.note}_`);
  out.push('');

  const p = pack.patient;
  out.push(`## ${t.patient}`);
  out.push(`- ${t.name}: ${v(p.name)}`);
  out.push(`- ${t.species}: ${v(p.species, (x) => t.species_[x] ?? x)}`);
  out.push(`- ${t.breed}: ${v(p.breed)}`);
  out.push(`- ${t.sex}: ${v(p.sex, (x) => t.sex_[x] ?? x)}${p.neuter_status ? ` · ${t.neuter}: ${yn(p.neuter_status.value === 'neutered')}` : ''}`);
  out.push(`- ${t.dob}: ${v(p.date_of_birth)}${p.age ? ` (${t.age}: ${p.age.value.value} ${t.unit[p.age.value.unit] ?? p.age.value.unit})` : ''}`);
  out.push(`- ${t.chip}: ${v(p.microchip)}`);
  out.push(`- ${t.owner}: ${v(pack.owner.name)}`);
  out.push(`- ${t.insurer}: ${v(pack.insurer.name)} · ${t.policy}: ${v(pack.insurer.policy_number)}`);
  out.push('');

  const c = pack.clinical;
  out.push(`## ${t.clinical}`);
  out.push(`- ${t.type}: ${v(c.condition_type, (x) => t[x])}`);
  out.push(`- ${t.first}: ${v(c.first_symptom_date)}`);
  out.push(`- ${t.complaint}: ${v(c.presenting_complaint)}`);
  out.push(`- ${t.diagnosis}: ${v(c.diagnosis)}`);
  out.push(`- ${t.dates}: ${v(c.treatment_dates, (d) => d.join(', '))}`);
  out.push(`- ${t.surgery}: ${v(c.surgery, yn)}${c.setting ? ` · ${t.setting}: ${t[c.setting.value]}` : ''}`);
  out.push(`- ${t.pre}: ${v(c.pre_existing, yn)}${c.pre_existing?.value && c.pre_existing_note ? ` — ${c.pre_existing_note.value}` : ''}`);
  if (c.treatments.length) { out.push(`- ${t.treatments}:`); for (const x of c.treatments) out.push(`  - ${x.value}`); }
  if (c.diagnostics.length) { out.push(`- ${t.diagnostics}:`); for (const x of c.diagnostics) out.push(`  - ${x.value}`); }
  if (c.medications.length) { out.push(''); out.push(`### ${t.meds}`); out.push(renderMedicationTable(c.medications, lang)); }
  out.push('');

  const inv = pack.invoice;
  out.push(`## ${t.invoice}`);
  out.push(`- ${t.invNo}: ${v(inv.number)} · ${t.invDate}: ${v(inv.date)}`);
  if (inv.lines) {
    const showGot = pack.country === 'DE' || inv.lines.value.some((l) => typed(l.got_number) || typed(l.factor));
    const cell = (x: string | null | undefined, required: boolean) => typed(x) ?? (required ? `▲` : '');
    out.push('');
    out.push(showGot ? `| ${t.date} | ${t.service} | ${t.got} | ${t.factor} | ${t.qty} | ${t.amount} |` : `| ${t.date} | ${t.service} | ${t.qty} | ${t.amount} |`);
    out.push(showGot ? '|---|---|---|---|---|---|' : '|---|---|---|---|');
    for (const l of inv.lines.value) {
      const de = pack.country === 'DE';
      out.push(showGot
        ? `| ${cell(l.date, true)} | ${l.description} | ${cell(l.got_number, de)} | ${cell(l.factor, de)} | ${cell(l.quantity, false)} | ${cell(l.amount, true)} |`
        : `| ${cell(l.date, true)} | ${l.description} | ${cell(l.quantity, false)} | ${cell(l.amount, true)} |`);
    }
    out.push('');
  } else {
    out.push(`- ${t.service}: ${flagged}`);
  }
  out.push(`- ${t.total}: ${v(inv.total)}`);
  out.push(`- ${t.vat}: ${v(inv.vat)}`);
  out.push('');

  const pr = pack.practice;
  out.push(`## ${t.practice}`);
  out.push(`- ${t.vet}: ${v(pr.vet_name)}${pr.vet_registration ? ` (${t.reg}: ${pr.vet_registration.value})` : ''}`);
  out.push(`- ${t.pname}: ${v(pr.name)}${pr.address ? `, ${pr.address.value}` : ''}`);
  out.push('');
  out.push(`${t.place}: ______________________`);
  out.push('');
  out.push(`${t.stamp}: ______________________`);

  if (pack.missing.length) {
    out.push('');
    out.push(`## ▲ ${t.missing}`);
    out.push(t.missingIntro);
    for (const f of pack.missing) out.push(`- ${fieldLabel(f, t)}`);
  }
  return out.join('\n');
}
