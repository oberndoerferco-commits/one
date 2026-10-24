import type { ClinicalRecord, PatientHeader } from './schema.js';
import type { VisitContext } from './country.js';
import type { Lang } from './render.js';

/**
 * Dog-bite / dog-incident report letter (CH, IT). See docs/20-bite-report.md.
 *
 * CH: TSchV art. 78 para. 1 obliges vets to report to the competent cantonal
 * office any incident in which a dog injured people or animals significantly
 * or shows excessive aggression. IT: the ASL veterinary service receives bite
 * reports (O.M. 6 agosto 2013 as extended, art. 1 c. 6 and art. 3; regional
 * and ASL instructions). The vet signs the letter and sends it to the office
 * the vet names in `opts.to`; this module sends nothing and stores nothing.
 *
 * Values come only from the approved record, the locked patient header, the
 * VisitContext and what the vet typed at this step (`opts`). Each value says
 * where it came from. Absent values are null and listed in `missing`.
 *
 * What this module never does:
 * - classify severity (Bagatell/leicht/mittel/schwer; lieve/media/grave) or
 *   the dog's size class (klein … Riese): those boxes on the cantonal forms are
 *   ticked by the vet (`left_to_vet`); the vet's own description is printed;
 * - call a dog "dangerous", "aggressive" or "at risk": that is the office's
 *   decision (TSchV art. 79; O.M. 2013 art. 3);
 * - compute an observation end date from a start date, or a deadline;
 * - move a value from one animal to the other (the record's patient is the
 *   biting dog or the injured animal only as the vet states in `patient_role`).
 */

export type BiteSource = `header.${string}` | `record.${string}` | `ctx.${string}` | `opts.${string}`;
export type Sourced<T> = { value: T; source: BiteSource; spans?: [number, number][] };

/** Which animal the clinical record is about. Never derived from the notes. */
export type BitePatientRole = 'biting_dog' | 'injured_animal';
/** The reason box on the cantonal forms (ZH: Verletzung Mensch / Verletzung Tier / Aggressionsverhalten). */
export type BiteReason = 'injury_person' | 'injury_animal' | 'aggression';
export type AccountSource = 'vet_observed' | 'owner_reported' | 'injured_party_reported' | 'third_party_reported';

export type BiteReportOpts = {
  approved?: boolean;
  /** The competent office as the vet names it (e.g. "Veterinäramt Kanton Zürich", "ASL Roma 1 – Servizio veterinario"). */
  to?: string | null;
  reason?: BiteReason | null;
  patient_role?: BitePatientRole | null;
  /** Whether the vet personally examined each animal. Not derived from `patient_role`. */
  examined?: { biting_dog?: boolean | null; injured_animal?: boolean | null };
  incident?: {
    date?: string | null;          // ISO date
    time?: string | null;          // as typed
    place?: string | null;         // as typed
    municipality?: string | null;  // ZH: Gemeinde
    public_place?: boolean | null;
    police_report?: boolean | null;
    description?: string | null;   // the vet's words
    account_source?: AccountSource | null;
  };
  injury?: {
    description?: string | null;           // type and location, the vet's words
    severity_description?: string | null;  // the vet's words; never classified here
    treatment?: string | null;             // as typed (ZH: needs the injured party's consent)
  };
  injured?: {
    kind?: 'person' | 'animal' | null;
    /** Consent of the injured person / the injured animal's owner to pass on identity and treatment details (ZH form footnote, VD form). */
    consent?: boolean | null;
    name?: string | null;      // person, or the injured animal's owner
    address?: string | null;
    phone?: string | null;
    animal?: { species?: string | null; breed?: string | null; sex?: 'female' | 'male' | null; microchip?: string | null };
  };
  /** The biting dog when it is not the record's patient (typed from what the vet was told). */
  biting_dog?: { name?: string | null; breed?: string | null; sex?: 'female' | 'male' | null; microchip?: string | null; colour?: string | null };
  /** Keeper of the biting dog. Name falls back to ctx.owner.name when the biting dog is the patient. */
  keeper?: { name?: string | null; address?: string | null; phone?: string | null };
  /** Observation period as ordered/agreed; dates are only ever typed. */
  observation?: { start?: string | null; end?: string | null; place?: string | null; ordered_by?: string | null };
  practice?: { name?: string | null; address?: string | null; phone?: string | null };
};

export type BiteField =
  | 'to' | 'reason' | 'patient_role' | 'examined.biting_dog' | 'examined.injured_animal'
  | 'incident.date' | 'incident.time' | 'incident.place' | 'incident.municipality' | 'incident.public_place' | 'incident.police_report' | 'incident.description' | 'incident.account_source'
  | 'injury.description' | 'injury.severity_description'
  | 'injured.kind' | 'injured.consent' | 'injured.animal.species'
  | 'biting_dog.breed' | 'biting_dog.sex' | 'biting_dog.microchip'
  | 'keeper.name' | 'keeper.address'
  | 'observation.start' | 'observation.end'
  | 'reporter.vet_name' | 'reporter.practice_address';

/** Boxes on the official forms this module deliberately leaves to the vet. */
export type LeftToVet = 'severity_grade' | 'size_class' | 'injury_type_boxes';

/** Official sources. Accessed 2026-10-23; see docs/20-bite-report.md. */
export const BITE_SOURCES = {
  tschv_78: { title: 'TSchV (SR 455.1) art. 78–79, as of 1 Feb 2026', url: 'https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2008/416/20260201/de/html/fedlex-data-admin-ch-eli-cc-2008-416-20260201-de-html-2.html' },
  zh_form: { title: 'Kanton Zürich, Veterinäramt: Meldung von Vorfällen mit Hunden gemäss Art. 78 TSchV', url: 'https://www.zh.ch/de/umwelt-tiere/tiere/haustiere-heimtiere/hunde/vorfaelle-mit-hunden-melden.html' },
  be_form_tier: { title: 'Kanton Bern, AVET: Formular 771x22 Meldung von Hundebissverletzungen beim Tier (V260810)', url: 'https://www.weu.be.ch/content/dam/weu/dokumente/avet/de/hunde/771x22-FO-Meldung-Hundebissverletzung-Tier-de.pdf' },
  vd_form: { title: 'Canton de Vaud, DGAV: Formulaire annonce de blessures par morsure de chien chez l\'animal', url: 'https://www.vd.ch/fileadmin/user_upload/themes/vie_privee/animaux/fichiers_pdf/2022/Pol_chiens/DGAV_FORM_morsure_chien_cong%C3%A9n%C3%A8re.pdf' },
  om_2013: { title: 'O.M. 6 agosto 2013 (GU n. 209 del 6-9-2013), art. 1 c. 6, art. 3', url: 'https://www.izs.it/IZS/Engine/RAServeFile.php/f/pdf_normativa/Iuvene_normativa_nazionale_animali_affezione/Ordinanza_06_agosto_2013.pdf' },
  om_2026: { title: 'O.M. 16 luglio 2026, proroga di 12 mesi dal 5-9-2026 (GU SG n. 206 del 5-9-2026)', url: 'https://www.certifico.com/component/attachments/download/63512' },
  er_2026: { title: 'Regione Emilia-Romagna, nota 2026 sulla sorveglianza della rabbia (segnalazione delle morsicature; osservazione ≥ 10 giorni; sospetto rabbia entro 12 ore)', url: 'https://www.omceopr.it/wp-content/uploads/2026/07/Circolare-Ministero-della-Salute.pdf' },
} as const;
export const BITE_SOURCES_ACCESSED = '2026-10-23';

export type BiteReportPack = {
  format: 'aiveterinary.bite-report/1';
  country: 'CH' | 'IT';
  approved: boolean;
  to: Sourced<string> | null;
  reason: Sourced<BiteReason> | null;
  patient_role: Sourced<BitePatientRole> | null;
  examined: { biting_dog: Sourced<boolean> | null; injured_animal: Sourced<boolean> | null };
  incident: {
    date: Sourced<string> | null; time: Sourced<string> | null; place: Sourced<string> | null; municipality: Sourced<string> | null;
    public_place: Sourced<boolean> | null; police_report: Sourced<boolean> | null;
    description: Sourced<string> | null; account_source: Sourced<AccountSource> | null;
  };
  injury: { description: Sourced<string> | null; severity_description: Sourced<string> | null; treatment: Sourced<string> | null };
  injured: {
    kind: Sourced<'person' | 'animal'> | null;
    consent: Sourced<boolean> | null;
    name: Sourced<string> | null; address: Sourced<string> | null; phone: Sourced<string> | null;
    animal: {
      name: Sourced<string> | null; species: Sourced<string> | null; breed: Sourced<string> | null; sex: Sourced<'female' | 'male'> | null;
      neuter_status: Sourced<'intact' | 'neutered'> | null; age: Sourced<{ value: number; unit: string }> | null;
      weight_kg: Sourced<number> | null; microchip: Sourced<string> | null;
    };
  };
  biting_dog: {
    name: Sourced<string> | null; species: Sourced<string> | null; breed: Sourced<string> | null; sex: Sourced<'female' | 'male'> | null;
    neuter_status: Sourced<'intact' | 'neutered'> | null; age: Sourced<{ value: number; unit: string }> | null;
    weight_kg: Sourced<number> | null; microchip: Sourced<string> | null; colour: Sourced<string> | null;
  };
  keeper: { name: Sourced<string> | null; address: Sourced<string> | null; phone: Sourced<string> | null };
  observation: { start: Sourced<string> | null; end: Sourced<string> | null; place: Sourced<string> | null; ordered_by: Sourced<string> | null };
  /** The record's own sentences about the patient, with spans into the notes. */
  record_findings: {
    complaint: (Sourced<string> & { role: string }) | null;
    findings: (Sourced<string> & { role: string; system: string })[];
    assessment: Sourced<string> | null;
    treatments: Sourced<string>[];
  };
  reporter: { vet_name: Sourced<string> | null; vet_registration: Sourced<string> | null; practice_name: Sourced<string> | null; practice_address: Sourced<string> | null; practice_phone: Sourced<string> | null };
  missing: BiteField[];
  left_to_vet: LeftToVet[];
  warnings: { code: 'patient_not_dog' | 'consent_not_recorded' | 'observation_end_before_start'; source: keyof typeof BITE_SOURCES | null }[];
};

function s<T>(value: T | null | undefined, source: BiteSource, spans?: [number, number][]): Sourced<T> | null {
  if (value == null) return null;
  if (typeof value === 'string' && !value.trim()) return null;
  const v = (typeof value === 'string' ? value.trim() : value) as T;
  return spans && spans.length ? { value: v, source, spans } : { value: v, source };
}

export function buildBiteReport(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, opts: BiteReportOpts = {}): BiteReportPack {
  if (ctx.country !== 'CH' && ctx.country !== 'IT') throw new Error('The bite report applies to Switzerland and Italy only (ctx.country must be CH or IT).');
  const role = opts.patient_role ?? null;
  const o = opts;

  /** Patient identity: locked header first, then the record's signalment; chip from the context. */
  const patient = {
    name: s(header.name, 'header.name') ?? s(record.patient.name, 'record.patient.name'),
    species: s<string>(header.species, 'header.species') ?? s<string>(record.patient.species, 'record.patient.species'),
    breed: s(header.breed, 'header.breed') ?? s(record.patient.breed, 'record.patient.breed'),
    sex: s(header.sex, 'header.sex') ?? s(record.patient.sex, 'record.patient.sex'),
    neuter_status: s(header.neuter_status, 'header.neuter_status') ?? s(record.patient.neuter_status, 'record.patient.neuter_status'),
    age: s<{ value: number; unit: string }>(header.age, 'header.age') ?? s<{ value: number; unit: string }>(record.patient.age, 'record.patient.age'),
    weight_kg: s(header.weight_kg, 'header.weight_kg'),
    microchip: s(ctx.microchip, 'ctx.microchip'),
  };
  const none = { name: null, species: null, breed: null, sex: null, neuter_status: null, age: null, weight_kg: null, microchip: null };

  const biting_dog: BiteReportPack['biting_dog'] = role === 'biting_dog'
    ? { ...patient, colour: s(o.biting_dog?.colour, 'opts.biting_dog.colour') }
    : {
        ...none,
        name: s(o.biting_dog?.name, 'opts.biting_dog.name'),
        breed: s(o.biting_dog?.breed, 'opts.biting_dog.breed'),
        sex: s(o.biting_dog?.sex, 'opts.biting_dog.sex'),
        microchip: s(o.biting_dog?.microchip, 'opts.biting_dog.microchip'),
        colour: s(o.biting_dog?.colour, 'opts.biting_dog.colour'),
      };

  const injuredAnimal: BiteReportPack['injured']['animal'] = role === 'injured_animal'
    ? patient
    : {
        ...none,
        species: s(o.injured?.animal?.species, 'opts.injured.animal.species'),
        breed: s(o.injured?.animal?.breed, 'opts.injured.animal.breed'),
        sex: s(o.injured?.animal?.sex, 'opts.injured.animal.sex'),
        microchip: s(o.injured?.animal?.microchip, 'opts.injured.animal.microchip'),
      };

  const injured: BiteReportPack['injured'] = {
    kind: s(o.injured?.kind, 'opts.injured.kind'),
    consent: s(o.injured?.consent, 'opts.injured.consent'),
    // the injured animal's owner is the context owner only when that animal is the patient
    name: s(o.injured?.name, 'opts.injured.name') ?? (role === 'injured_animal' ? s(ctx.owner.name, 'ctx.owner.name') : null),
    address: s(o.injured?.address, 'opts.injured.address'),
    phone: s(o.injured?.phone, 'opts.injured.phone'),
    animal: injuredAnimal,
  };

  const keeper: BiteReportPack['keeper'] = {
    name: s(o.keeper?.name, 'opts.keeper.name') ?? (role === 'biting_dog' ? s(ctx.owner.name, 'ctx.owner.name') : null),
    address: s(o.keeper?.address, 'opts.keeper.address'),
    phone: s(o.keeper?.phone, 'opts.keeper.phone'),
  };

  const record_findings: BiteReportPack['record_findings'] = {
    complaint: record.presenting_complaint
      ? { ...(s(record.presenting_complaint.text, 'record.presenting_complaint.text', record.presenting_complaint.source_spans) as Sourced<string>), role: record.presenting_complaint.source_role }
      : null,
    findings: record.examination.findings.map((f, i) => ({ value: f.text, source: `record.examination.findings[${i}].text` as BiteSource, spans: f.source_spans, role: f.source_role, system: f.system })),
    assessment: s(record.assessment.text, 'record.assessment.text', record.assessment.source_spans),
    treatments: record.treatments.flatMap((t, i) => (t.status === 'performed' ? [{ value: t.text, source: `record.treatments[${i}].text` as BiteSource, spans: t.source_spans }] : [])),
  };

  const pack: BiteReportPack = {
    format: 'aiveterinary.bite-report/1',
    country: ctx.country,
    approved: o.approved === true,
    to: s(o.to, 'opts.to'),
    reason: s(o.reason, 'opts.reason'),
    patient_role: s(role, 'opts.patient_role'),
    examined: { biting_dog: s(o.examined?.biting_dog, 'opts.examined.biting_dog'), injured_animal: s(o.examined?.injured_animal, 'opts.examined.injured_animal') },
    incident: {
      date: s(o.incident?.date, 'opts.incident.date'),
      time: s(o.incident?.time, 'opts.incident.time'),
      place: s(o.incident?.place, 'opts.incident.place'),
      municipality: s(o.incident?.municipality, 'opts.incident.municipality'),
      public_place: s(o.incident?.public_place, 'opts.incident.public_place'),
      police_report: s(o.incident?.police_report, 'opts.incident.police_report'),
      description: s(o.incident?.description, 'opts.incident.description'),
      account_source: s(o.incident?.account_source, 'opts.incident.account_source'),
    },
    injury: {
      description: s(o.injury?.description, 'opts.injury.description'),
      severity_description: s(o.injury?.severity_description, 'opts.injury.severity_description'),
      treatment: s(o.injury?.treatment, 'opts.injury.treatment'),
    },
    injured,
    biting_dog,
    keeper,
    observation: {
      start: s(o.observation?.start, 'opts.observation.start'),
      end: s(o.observation?.end, 'opts.observation.end'),
      place: s(o.observation?.place, 'opts.observation.place'),
      ordered_by: s(o.observation?.ordered_by, 'opts.observation.ordered_by'),
    },
    record_findings,
    reporter: {
      vet_name: s(ctx.author.name, 'ctx.author.name'),
      vet_registration: s(ctx.author.registration, 'ctx.author.registration'),
      practice_name: s(o.practice?.name, 'opts.practice.name'),
      practice_address: s(o.practice?.address, 'opts.practice.address'),
      practice_phone: s(o.practice?.phone, 'opts.practice.phone'),
    },
    missing: [],
    left_to_vet: [],
    warnings: [],
  };

  pack.missing = listMissing(pack);
  if (pack.reason?.value !== 'aggression') pack.left_to_vet.push('injury_type_boxes', 'severity_grade');
  pack.left_to_vet.push('size_class');

  if (role === 'biting_dog' && patient.species && patient.species.value !== 'dog') pack.warnings.push({ code: 'patient_not_dog', source: 'tschv_78' });
  const identity = injured.name || injured.address || injured.phone || pack.injury.treatment;
  if (pack.country === 'CH' && identity && injured.consent?.value !== true) pack.warnings.push({ code: 'consent_not_recorded', source: 'vd_form' });
  if (pack.observation.start && pack.observation.end && pack.observation.end.value < pack.observation.start.value) pack.warnings.push({ code: 'observation_end_before_start', source: null });
  return pack;
}

/** Null fields that the official forms ask for, in form order. Conditional fields only when they apply. */
function listMissing(p: BiteReportPack): BiteField[] {
  const out: BiteField[] = [];
  const need = (f: BiteField, v: unknown) => { if (v == null) out.push(f); };
  need('to', p.to);
  need('reason', p.reason);
  need('patient_role', p.patient_role);
  need('examined.biting_dog', p.examined.biting_dog);
  const injury = p.reason == null || p.reason.value !== 'aggression';
  if (injury && p.reason?.value !== 'injury_person') need('examined.injured_animal', p.examined.injured_animal);
  need('incident.date', p.incident.date);
  need('incident.time', p.incident.time);
  need('incident.place', p.incident.place);
  if (p.country === 'CH') need('incident.municipality', p.incident.municipality);
  need('incident.public_place', p.incident.public_place);
  need('incident.police_report', p.incident.police_report);
  need('incident.description', p.incident.description);
  need('incident.account_source', p.incident.account_source);
  if (injury) {
    need('injury.description', p.injury.description);
    need('injury.severity_description', p.injury.severity_description);
    need('injured.kind', p.injured.kind);
    if (p.injured.kind?.value === 'animal' || p.reason?.value === 'injury_animal') need('injured.animal.species', p.injured.animal.species);
    if (p.country === 'CH' && (p.injured.name || p.injured.address || p.injured.phone || p.injury.treatment)) need('injured.consent', p.injured.consent);
  }
  need('biting_dog.breed', p.biting_dog.breed);
  need('biting_dog.sex', p.biting_dog.sex);
  need('biting_dog.microchip', p.biting_dog.microchip);
  need('keeper.name', p.keeper.name);
  need('keeper.address', p.keeper.address);
  if (p.country === 'IT') { need('observation.start', p.observation.start); need('observation.end', p.observation.end); }
  need('reporter.vet_name', p.reporter.vet_name);
  need('reporter.practice_address', p.reporter.practice_address);
  return out;
}

/* ------------------------------------------------------------------ */
/* Letter. Headings and labels are code; values are printed as found. */

const T = {
  en: {
    title: { CH: 'Report of an incident with a dog', IT: 'Report of a dog bite / dog aggression' },
    basis: { CH: 'Report under Art. 78 para. 1 Swiss Animal Welfare Ordinance (TSchV, SR 455.1)', IT: 'Report to the ASL veterinary service (O.M. 6 August 2013 as extended, art. 1 c. 6 and art. 3; regional and ASL instructions)' },
    banner: 'To be checked, signed and sent by the veterinarian to the competent office the veterinarian names below. Nothing has been sent. Prepared from the approved clinical record and the veterinarian\'s own entries; no severity grade, size class or risk judgement was added.',
    draft: 'DRAFT — not yet approved by the veterinarian',
    to: 'To', reason: 'Reason for the report', reason_: { injury_person: 'dog injured a person', injury_animal: 'dog injured an animal', aggression: 'excessive aggressive behaviour' } as Record<string, string>,
    incident: 'Incident', date: 'Date', time: 'Time', place: 'Place', municipality: 'Municipality', public: 'Public place', police: 'Reported to the police', description: 'What happened (veterinarian\'s words)', account: 'Account given by',
    account_: { vet_observed: 'observed by the veterinarian', owner_reported: 'reported by the dog\'s keeper', injured_party_reported: 'reported by the injured party', third_party_reported: 'reported by a third party' } as Record<string, string>,
    injury: 'Injury', injDesc: 'Injury (veterinarian\'s description)', severity: 'Severity (veterinarian\'s words)', treatment: 'Treatment',
    injured: 'Injured party', kind: 'Injured', kind_: { person: 'person', animal: 'animal' } as Record<string, string>, owner: 'Name (person or animal owner)', address: 'Address', phone: 'Phone', withheld: 'not printed: consent of the injured party / owner not recorded',
    injAnimal: 'Injured animal', bitingDog: 'Dog that bit / showed the behaviour', keeper: 'Keeper of the dog',
    name: 'Name', species: 'Species', breed: 'Breed', sex: 'Sex', neutered: 'Neutered', age: 'Age', weight: 'Weight', chip: 'Microchip', colour: 'Colour',
    examined: 'Examined by the reporting veterinarian', examinedDog: 'Biting dog', examinedInjured: 'Injured animal',
    patientIs: 'The clinical record is about', role_: { biting_dog: 'the dog that bit', injured_animal: 'the injured animal' } as Record<string, string>,
    findings: 'Findings in the clinical record', complaint: 'Reason for presentation', assessment: 'Assessment', treatments: 'Treatment performed', ownerReported: 'owner reported',
    observation: 'Observation period (as ordered)', start: 'From', end: 'To', obsPlace: 'Where', orderedBy: 'Ordered by',
    reporter: 'Reporting veterinarian', vet: 'Veterinarian', reg: 'Registration', practice: 'Practice',
    sign: 'Place, date, stamp and signature of the veterinarian',
    leftToVet: 'Boxes the official form asks for that the veterinarian ticks on it:', left_: { severity_grade: 'severity grade of the bite injury', size_class: 'size / weight class of the dog', injury_type_boxes: 'type and location of injury boxes' } as Record<string, string>,
    missing: 'Missing', missingIntro: 'Not in the record and not entered; to be completed before sending:',
    warn_: { patient_not_dog: 'The record\'s patient is marked as the biting dog but its species is not dog.', consent_not_recorded: 'Identity or treatment details of the injured party are entered but consent is not recorded; they are not printed (cantonal forms: only with consent).', observation_end_before_start: 'Observation end date is before the start date.' } as Record<string, string>,
    rabies: { CH: '', IT: 'Suspected rabies: notify the ASL veterinary service without delay and within 12 hours (Reg. (EU) 2016/429 art. 18; D.Lgs. 136/2022).' },
    yes: 'yes', no: 'no', species_: { dog: 'dog', cat: 'cat', rabbit: 'rabbit', ferret: 'ferret', horse: 'horse', bird: 'bird', reptile: 'reptile', other: 'other' } as Record<string, string>,
    sex_: { female: 'female', male: 'male' } as Record<string, string>, unit: { day: 'days', week: 'weeks', month: 'months', year: 'years' } as Record<string, string>,
  },
  de: {
    title: { CH: 'Meldung eines Vorfalls mit einem Hund', IT: 'Meldung eines Hundebisses / Vorfalls mit einem Hund' },
    basis: { CH: 'Meldung nach Art. 78 Abs. 1 Tierschutzverordnung (TSchV, SR 455.1)', IT: 'Meldung an den tierärztlichen Dienst der ASL (O.M. 6. August 2013 mit Verlängerungen, Art. 1 c. 6 und Art. 3; regionale und ASL-Vorgaben)' },
    banner: 'Von der Tierärztin / dem Tierarzt zu prüfen, zu unterschreiben und an die unten genannte zuständige Stelle zu senden. Es wurde nichts versandt. Erstellt aus dem freigegebenen Behandlungsdatensatz und den eigenen Eingaben der Tierärztin / des Tierarztes; es wurde kein Schweregrad, keine Grössenklasse und keine Gefährlichkeitsbeurteilung ergänzt.',
    draft: 'ENTWURF — noch nicht tierärztlich freigegeben',
    to: 'An', reason: 'Meldegrund', reason_: { injury_person: 'Verletzung Mensch', injury_animal: 'Verletzung Tier', aggression: 'Aggressionsverhalten' } as Record<string, string>,
    incident: 'Angaben zum Vorfall', date: 'Datum', time: 'Zeit', place: 'Ort', municipality: 'Gemeinde', public: 'Im öffentlichen Bereich', police: 'Anzeige bei der Polizei', description: 'Beschreibung des Vorfalls (Worte der Tierärztin / des Tierarztes)', account: 'Angaben von',
    account_: { vet_observed: 'eigene Beobachtung der Tierärztin / des Tierarztes', owner_reported: 'Halter/in des Hundes', injured_party_reported: 'verletzte / betroffene Partei', third_party_reported: 'Drittpersonen' } as Record<string, string>,
    injury: 'Verletzung', injDesc: 'Verletzung (Beschreibung der Tierärztin / des Tierarztes)', severity: 'Schwere (Worte der Tierärztin / des Tierarztes)', treatment: 'Behandlung',
    injured: 'Verletzte / betroffene Partei', kind: 'Verletzt', kind_: { person: 'Mensch', animal: 'Tier' } as Record<string, string>, owner: 'Name (Person bzw. Halter/in des verletzten Tieres)', address: 'Adresse', phone: 'Telefon', withheld: 'nicht abgedruckt: Einverständnis der verletzten Person / der Halterin bzw. des Halters nicht erfasst',
    injAnimal: 'Verletztes Tier', bitingDog: 'Hund, der gebissen bzw. das Verhalten gezeigt hat', keeper: 'Halter/in des Hundes',
    name: 'Name', species: 'Tierart', breed: 'Rasse', sex: 'Geschlecht', neutered: 'Kastriert', age: 'Alter', weight: 'Gewicht', chip: 'Mikrochip-Nr.', colour: 'Farbe',
    examined: 'Von der meldenden Tierärztin / dem meldenden Tierarzt untersucht', examinedDog: 'Hund, der gebissen hat', examinedInjured: 'Verletztes Tier',
    patientIs: 'Der Behandlungsdatensatz betrifft', role_: { biting_dog: 'den Hund, der gebissen hat', injured_animal: 'das verletzte Tier' } as Record<string, string>,
    findings: 'Befunde im Behandlungsdatensatz', complaint: 'Vorstellungsgrund', assessment: 'Beurteilung', treatments: 'Durchgeführte Behandlung', ownerReported: 'laut Besitzer',
    observation: 'Beobachtungszeit (wie angeordnet)', start: 'Von', end: 'Bis', obsPlace: 'Wo', orderedBy: 'Angeordnet von',
    reporter: 'Meldende Tierärztin / meldender Tierarzt', vet: 'Tierärztin / Tierarzt', reg: 'Registrierung', practice: 'Praxis',
    sign: 'Ort, Datum, Stempel und Unterschrift der Tierärztin / des Tierarztes',
    leftToVet: 'Felder des amtlichen Formulars, die die Tierärztin / der Tierarzt dort ankreuzt:', left_: { severity_grade: 'Schweregrad der Bissverletzung', size_class: 'Grösse / Gewicht des Hundes (Grössenklasse)', injury_type_boxes: 'Typ und Lokalisation der Verletzung' } as Record<string, string>,
    missing: 'Fehlt', missingIntro: 'Weder im Datensatz noch eingetragen; vor dem Versand ergänzen:',
    warn_: { patient_not_dog: 'Der Patient ist als beissender Hund angegeben, die Tierart ist aber nicht Hund.', consent_not_recorded: 'Angaben zur Person bzw. Behandlung der verletzten Partei sind eingetragen, das Einverständnis ist nicht erfasst; sie werden nicht abgedruckt (kantonale Formulare: nur mit Einverständnis).', observation_end_before_start: 'Das Ende der Beobachtungszeit liegt vor deren Beginn.' } as Record<string, string>,
    rabies: { CH: '', IT: 'Tollwutverdacht: unverzüglich, spätestens innert 12 Stunden dem tierärztlichen Dienst der ASL melden (VO (EU) 2016/429 Art. 18; D.Lgs. 136/2022).' },
    yes: 'ja', no: 'nein', species_: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'anderes Tier' } as Record<string, string>,
    sex_: { female: 'weiblich', male: 'männlich' } as Record<string, string>, unit: { day: 'Tage', week: 'Wochen', month: 'Monate', year: 'Jahre' } as Record<string, string>,
  },
  it: {
    title: { CH: 'Notifica di un incidente con un cane', IT: 'Segnalazione di morsicatura / aggressione da parte di un cane' },
    basis: { CH: 'Notifica secondo l\'art. 78 cpv. 1 dell\'ordinanza sulla protezione degli animali (OPAn, RS 455.1)', IT: 'Segnalazione al Servizio veterinario dell\'ASL (O.M. 6 agosto 2013 e successive proroghe, art. 1 c. 6 e art. 3; indicazioni regionali e dell\'ASL)' },
    banner: 'Da verificare, firmare e inviare a cura del medico veterinario all\'ufficio competente indicato qui sotto dal veterinario stesso. Nulla è stato inviato. Redatto dalla cartella clinica approvata e dai dati inseriti dal veterinario; non sono stati aggiunti gradi di gravità, classi di taglia né valutazioni di pericolosità.',
    draft: 'BOZZA — non ancora approvata dal veterinario',
    to: 'Destinatario', reason: 'Motivo della segnalazione', reason_: { injury_person: 'lesione a una persona', injury_animal: 'lesione a un animale', aggression: 'comportamento aggressivo' } as Record<string, string>,
    incident: 'Dati dell\'episodio', date: 'Data', time: 'Ora', place: 'Luogo', municipality: 'Comune', public: 'Luogo pubblico', police: 'Denuncia alla polizia', description: 'Descrizione dell\'episodio (parole del veterinario)', account: 'Fonte del racconto',
    account_: { vet_observed: 'osservato dal veterinario', owner_reported: 'riferito dal detentore del cane', injured_party_reported: 'riferito dalla parte lesa', third_party_reported: 'riferito da terzi' } as Record<string, string>,
    injury: 'Lesione', injDesc: 'Lesione (descrizione del veterinario)', severity: 'Gravità (parole del veterinario)', treatment: 'Trattamento',
    injured: 'Parte lesa', kind: 'Morsicato', kind_: { person: 'persona', animal: 'animale' } as Record<string, string>, owner: 'Nome (persona o proprietario dell\'animale)', address: 'Indirizzo', phone: 'Telefono', withheld: 'non riportato: consenso della parte lesa / del proprietario non registrato',
    injAnimal: 'Animale morsicato', bitingDog: 'Cane morsicatore / che ha mostrato il comportamento', keeper: 'Proprietario / detentore del cane',
    name: 'Nome', species: 'Specie', breed: 'Razza', sex: 'Sesso', neutered: 'Sterilizzato', age: 'Età', weight: 'Peso', chip: 'Microchip', colour: 'Mantello',
    examined: 'Visitato dal veterinario segnalante', examinedDog: 'Cane morsicatore', examinedInjured: 'Animale morsicato',
    patientIs: 'La cartella clinica riguarda', role_: { biting_dog: 'il cane morsicatore', injured_animal: 'l\'animale morsicato' } as Record<string, string>,
    findings: 'Rilievi nella cartella clinica', complaint: 'Motivo della visita', assessment: 'Valutazione', treatments: 'Prestazioni eseguite', ownerReported: 'riferito dal proprietario',
    observation: 'Periodo di osservazione (come disposto)', start: 'Dal', end: 'Al', obsPlace: 'Luogo', orderedBy: 'Disposto da',
    reporter: 'Medico veterinario segnalante', vet: 'Medico veterinario', reg: 'Iscrizione all\'Ordine', practice: 'Struttura',
    sign: 'Luogo, data, timbro e firma del medico veterinario',
    leftToVet: 'Caselle del modulo ufficiale che il veterinario barra direttamente sul modulo:', left_: { severity_grade: 'grado di gravità della lesione', size_class: 'taglia / peso del cane', injury_type_boxes: 'tipo e localizzazione della lesione' } as Record<string, string>,
    missing: 'Mancante', missingIntro: 'Non presente nella cartella e non inserito; da completare prima dell\'invio:',
    warn_: { patient_not_dog: 'Il paziente è indicato come cane morsicatore ma la specie non è cane.', consent_not_recorded: 'Sono inseriti dati identificativi o di trattamento della parte lesa senza consenso registrato; non vengono riportati (moduli cantonali: solo con consenso).', observation_end_before_start: 'La fine del periodo di osservazione è anteriore all\'inizio.' } as Record<string, string>,
    rabies: { CH: '', IT: 'Sospetto di rabbia: notifica senza ritardo ed entro 12 ore al Servizio veterinario dell\'ASL (Reg. (UE) 2016/429 art. 18; D.Lgs. 136/2022).' },
    yes: 'sì', no: 'no', species_: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' } as Record<string, string>,
    sex_: { female: 'femmina', male: 'maschio' } as Record<string, string>, unit: { day: 'giorni', week: 'settimane', month: 'mesi', year: 'anni' } as Record<string, string>,
  },
} satisfies Record<Lang, unknown>;

type Labels = (typeof T)['en'];

function fieldLabel(f: BiteField, t: Labels): string {
  const map: Record<BiteField, string> = {
    to: t.to, reason: t.reason, patient_role: t.patientIs, 'examined.biting_dog': `${t.examined}: ${t.examinedDog}`, 'examined.injured_animal': `${t.examined}: ${t.examinedInjured}`,
    'incident.date': `${t.incident}: ${t.date}`, 'incident.time': `${t.incident}: ${t.time}`, 'incident.place': `${t.incident}: ${t.place}`, 'incident.municipality': `${t.incident}: ${t.municipality}`,
    'incident.public_place': `${t.incident}: ${t.public}`, 'incident.police_report': `${t.incident}: ${t.police}`, 'incident.description': t.description, 'incident.account_source': t.account,
    'injury.description': t.injDesc, 'injury.severity_description': t.severity,
    'injured.kind': t.kind, 'injured.consent': t.withheld, 'injured.animal.species': `${t.injAnimal}: ${t.species}`,
    'biting_dog.breed': `${t.bitingDog}: ${t.breed}`, 'biting_dog.sex': `${t.bitingDog}: ${t.sex}`, 'biting_dog.microchip': `${t.bitingDog}: ${t.chip}`,
    'keeper.name': `${t.keeper}: ${t.name}`, 'keeper.address': `${t.keeper}: ${t.address}`,
    'observation.start': `${t.observation}: ${t.start}`, 'observation.end': `${t.observation}: ${t.end}`,
    'reporter.vet_name': t.vet, 'reporter.practice_address': `${t.practice}: ${t.address}`,
  };
  return map[f];
}

export function renderBiteReport(pack: BiteReportPack, lang: Lang = pack.country === 'IT' ? 'it' : 'de'): string {
  const t: Labels = T[lang] ?? T.en;
  const flagged = `▲ ${t.missing}`;
  const v = <X>(x: Sourced<X> | null, show: (val: X) => string = String) => (x ? show(x.value) : flagged);
  const yn = (b: boolean) => (b ? t.yes : t.no);
  const opt = <X>(label: string, x: Sourced<X> | null, show: (val: X) => string = String) => (x ? [`- ${label}: ${show(x.value)}`] : []);
  const out: string[] = [];
  const c = pack.country;

  out.push(`# ${t.title[c]}`);
  out.push(`_${t.basis[c]}_`);
  if (!pack.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${t.banner}**`);
  out.push('');
  out.push(`- ${t.to}: ${v(pack.to)}`);
  out.push(`- ${t.reason}: ${v(pack.reason, (r) => t.reason_[r] ?? r)}`);
  out.push(`- ${t.patientIs}: ${v(pack.patient_role, (r) => t.role_[r] ?? r)}`);
  const askInjured = pack.reason?.value !== 'aggression' && pack.reason?.value !== 'injury_person';
  out.push(`- ${t.examined}: ${t.examinedDog} ${v(pack.examined.biting_dog, yn)}${askInjured || pack.examined.injured_animal ? ` · ${t.examinedInjured} ${v(pack.examined.injured_animal, yn)}` : ''}`);
  out.push('');

  const i = pack.incident;
  out.push(`## ${t.incident}`);
  out.push(`- ${t.date}: ${v(i.date)} · ${t.time}: ${v(i.time)}`);
  out.push(`- ${t.place}: ${v(i.place)}${c === 'CH' || i.municipality ? ` · ${t.municipality}: ${v(i.municipality)}` : ''}`);
  out.push(`- ${t.public}: ${v(i.public_place, yn)} · ${t.police}: ${v(i.police_report, yn)}`);
  out.push(`- ${t.description}: ${v(i.description)}`);
  out.push(`- ${t.account}: ${v(i.account_source, (a) => t.account_[a] ?? a)}`);
  out.push('');

  const injuryCase = pack.reason?.value !== 'aggression';
  if (injuryCase) {
    out.push(`## ${t.injury}`);
    out.push(`- ${t.injDesc}: ${v(pack.injury.description)}`);
    out.push(`- ${t.severity}: ${v(pack.injury.severity_description)}`);
    out.push('');
    const inj = pack.injured;
    const consentOk = c !== 'CH' || inj.consent?.value === true;
    out.push(`## ${t.injured}`);
    out.push(`- ${t.kind}: ${v(inj.kind, (k) => t.kind_[k] ?? k)}`);
    if (inj.name || inj.address || inj.phone || pack.injury.treatment) {
      if (consentOk) out.push(...opt(t.owner, inj.name), ...opt(t.address, inj.address), ...opt(t.phone, inj.phone), ...opt(t.treatment, pack.injury.treatment));
      else out.push(`- ${t.owner}: ${t.withheld}`);
    }
    if (inj.kind?.value === 'animal' || pack.reason?.value === 'injury_animal' || pack.patient_role?.value === 'injured_animal') {
      const a = inj.animal;
      out.push(`- ${t.injAnimal}:`);
      out.push(...opt(t.name, a.name).map((l) => `  ${l}`));
      out.push(`  - ${t.species}: ${v(a.species, (x) => t.species_[x] ?? x)}`);
      out.push(...[...opt(t.breed, a.breed), ...opt(t.sex, a.sex, (x) => t.sex_[x] ?? x), ...opt(t.neutered, a.neuter_status, (x) => yn(x === 'neutered')), ...opt(t.age, a.age, (x) => `${x.value} ${t.unit[x.unit] ?? x.unit}`), ...opt(t.weight, a.weight_kg, (x) => `${x} kg`), ...opt(t.chip, a.microchip)].map((l) => `  ${l}`));
    }
    out.push('');
  }

  const d = pack.biting_dog;
  out.push(`## ${t.bitingDog}`);
  out.push(...opt(t.name, d.name));
  if (d.species) out.push(`- ${t.species}: ${t.species_[d.species.value] ?? d.species.value}`);
  out.push(`- ${t.breed}: ${v(d.breed)}`);
  out.push(`- ${t.sex}: ${v(d.sex, (x) => t.sex_[x] ?? x)}${d.neuter_status ? ` · ${t.neutered}: ${yn(d.neuter_status.value === 'neutered')}` : ''}`);
  out.push(...opt(t.age, d.age, (x) => `${x.value} ${t.unit[x.unit] ?? x.unit}`), ...opt(t.weight, d.weight_kg, (x) => `${x} kg`));
  out.push(`- ${t.chip}: ${v(d.microchip)}`);
  out.push(...opt(t.colour, d.colour));
  out.push(`- ${t.keeper}: ${v(pack.keeper.name)}${pack.keeper.address ? `, ${pack.keeper.address.value}` : ''}${pack.keeper.phone ? `, ${t.phone} ${pack.keeper.phone.value}` : ''}`);
  if (!pack.keeper.address) out.push(`  - ${t.address}: ${flagged}`);
  out.push('');

  const r = pack.record_findings;
  if (r.complaint || r.findings.length || r.assessment || r.treatments.length) {
    out.push(`## ${t.findings}`);
    if (r.complaint) out.push(`- ${t.complaint}: ${r.complaint.value}${r.complaint.role === 'owner_reported' ? ` (${t.ownerReported})` : ''}`);
    for (const f of r.findings) out.push(`- ${f.system}: ${f.value}${f.role === 'owner_reported' ? ` (${t.ownerReported})` : ''}`);
    if (r.assessment) out.push(`- ${t.assessment}: ${r.assessment.value}`);
    for (const x of r.treatments) out.push(`- ${t.treatments}: ${x.value}`);
    out.push('');
  }

  const ob = pack.observation;
  if (c === 'IT' || ob.start || ob.end) {
    out.push(`## ${t.observation}`);
    out.push(`- ${t.start}: ${v(ob.start)} · ${t.end}: ${v(ob.end)}`);
    out.push(...opt(t.obsPlace, ob.place), ...opt(t.orderedBy, ob.ordered_by));
    out.push('');
  }
  if (t.rabies[c]) { out.push(`_${t.rabies[c]}_`); out.push(''); }

  const rp = pack.reporter;
  out.push(`## ${t.reporter}`);
  out.push(`- ${t.vet}: ${v(rp.vet_name)}${rp.vet_registration ? ` (${t.reg}: ${rp.vet_registration.value})` : ''}`);
  out.push(`- ${t.practice}: ${rp.practice_name ? `${rp.practice_name.value}, ` : ''}${v(rp.practice_address)}${rp.practice_phone ? `, ${t.phone} ${rp.practice_phone.value}` : ''}`);
  out.push('');
  out.push(`${t.sign}: ______________________`);

  if (pack.warnings.length) {
    out.push('');
    for (const w of pack.warnings) out.push(`> ${t.warn_[w.code] ?? w.code}`);
  }
  if (pack.left_to_vet.length) {
    out.push('');
    out.push(t.leftToVet);
    for (const l of pack.left_to_vet) out.push(`- ${t.left_[l] ?? l}`);
  }
  if (pack.missing.length) {
    out.push('');
    out.push(`## ▲ ${t.missing}`);
    out.push(t.missingIntro);
    for (const f of pack.missing) out.push(`- ${fieldLabel(f, t)}`);
  }
  return out.join('\n');
}
