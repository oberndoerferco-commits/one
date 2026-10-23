import type { ClinicalRecord, PatientHeader } from './schema.js';
import type { VisitContext } from './country.js';
import type { Lang } from './render.js';

/**
 * Registry export: the data set a pet registry asks for when a vet chips and
 * registers an animal or records a change (see docs/21-registry-export.md),
 * as a checklist the vet copies into the registry by hand.
 *
 * We never submit anything to any registry. The entry says so, and so does
 * every rendering of it.
 *
 * Registries:
 * - AT-HDB: Austrian Heimtierdatenbank, TSchG § 24a (data list in § 24a(2),
 *   mandatory subset for dogs in § 24a(4), vet entry at first chipping § 24a(4c)).
 * - IT-SINAC: Italian Sistema di identificazione nazionale degli animali da
 *   compagnia (D.Lgs. 134/2022 art. 16, DM 2 novembre 2023). The national field
 *   list sits in ministerial "istruzioni" we could not open; the field set here
 *   follows the regional forms and pages that were opened (FVG Modello 1/2, Veneto).
 *
 * Rules:
 * - every value comes from the patient header, the visit context, the approved
 *   record (signalment fallback only) or what the vet typed (`opts`), and says so;
 * - nothing is inferred: no breed guessing, no date of birth from the age, no
 *   rabies date from a vaccination in the record, no intervention from a
 *   procedure in the record, no deadline date computed from the event date;
 * - everything a registry requires for this event and is absent is null and
 *   listed in `missing`.
 */

export type Registry = 'AT-HDB' | 'IT-SINAC';
export type RegistryEvent = 'first_registration' | 'change_of_owner' | 'death' | 'loss';

/** Where a value came from: header.*, record.*, ctx.* or opts.* (typed by the vet at the registry step). */
export type RegistrySource = `header.${string}` | `record.${string}` | `ctx.${string}` | `opts.${string}`;
export type RegistrySourced<T> = { value: T; source: RegistrySource };

export type RegistryPerson = {
  name?: string | null;
  tax_id?: string | null;              // IT codice fiscale
  id_document_type?: string | null;    // AT: Art des amtlichen Lichtbildausweises (e.g. "Reisepass")
  id_document_number?: string | null;  // AT: Nummer des Lichtbildausweises
  address?: string | null;             // AT Zustelladresse / IT residenza
  contact?: string | null;             // AT Kontaktdaten (phone / e-mail)
  email?: string | null;               // IT (FVG Modello 2, optional)
  date_of_birth?: string | null;       // AT: keeper's date of birth
};

export type RegistryOpts = {
  approved?: boolean;
  /** The event, as the vet chose it. Never derived. */
  event: RegistryEvent;
  /** ISO date of the event: chipping / identification, handover, death, loss. As typed. */
  event_date?: string | null;
  animal?: {
    chip_type?: 'ISO' | 'other' | null; // AT HDB: Chiptyp "ISO" / "Andere"
    date_of_birth?: string | null;      // as typed: ISO date or year (AT: "zumindest Jahr"; IT: "data o anno")
    country_of_birth?: string | null;   // AT § 24a(2) Z 2 lit f
    size?: string | null;               // IT taglia
    coat?: string | null;               // IT mantello
    marks?: string | null;              // IT note o segni particolari
    dam_chip?: string | null;           // AT: chip of the parents, if known
    sire_chip?: string | null;
    interventions?: string | null;      // AT § 24a(2) Z 2 lit e: reason + vet, as typed; only if any
    neutering_date?: string | null;     // AT § 24a(2) Z 2 lit j: date of the procedure, as typed
    pet_passport?: string | null;       // AT optional (lit g)
    rabies_vaccination_date?: string | null; // AT optional (lit h)
    rabies_vaccine?: string | null;     // AT optional (lit h)
    registration_number?: string | null; // AT: current Registrierungsnummer (needed for a handover)
  };
  /** The current keeper/owner beyond what the visit context holds (name and tax id come from ctx.owner). */
  owner?: RegistryPerson & {
    keeping_since?: string | null;          // AT: Datum der Aufnahme der Haltung
    competence_certificate?: string | null; // AT: Sachkundenachweis (§ 13(4)), as typed, incl. "not required"
  };
  /** The person taking the animal over (change of owner). */
  new_owner?: RegistryPerson;
  origin?: 'birth' | 'acquisition' | null; // IT Modello 1: nascita da proprio riproduttore / acquisizione
  loss?: { place?: string | null; theft?: boolean | null; police_report?: string | null };
  death_certificate?: string | null;       // IT: who issued the death certificate, as typed
};

export type RegistryFieldKey =
  | 'animal.microchip' | 'animal.chip_type' | 'animal.registration_number' | 'animal.species' | 'animal.name' | 'animal.breed' | 'animal.sex'
  | 'animal.date_of_birth' | 'animal.country_of_birth' | 'animal.size' | 'animal.coat' | 'animal.marks' | 'animal.dam_chip' | 'animal.sire_chip'
  | 'animal.interventions' | 'animal.neutering_date' | 'animal.pet_passport' | 'animal.rabies_vaccination_date' | 'animal.rabies_vaccine'
  | 'owner.name' | 'owner.tax_id' | 'owner.id_document_type' | 'owner.id_document_number' | 'owner.address' | 'owner.contact'
  | 'owner.date_of_birth' | 'owner.keeping_since' | 'owner.competence_certificate'
  | 'new_owner.name' | 'new_owner.tax_id' | 'new_owner.id_document_type' | 'new_owner.id_document_number' | 'new_owner.address' | 'new_owner.email'
  | 'event.date' | 'event.origin' | 'event.place' | 'event.theft' | 'event.police_report' | 'event.death_certificate'
  | 'vet.name' | 'vet.registration';

export type RegistryField = {
  key: RegistryFieldKey;
  value: RegistrySourced<string | boolean> | null;
  required: boolean;
  /** Short legal / documentary basis, cited as in docs/21-registry-export.md. */
  basis: string;
};

export type RegistryNote =
  | 'at_vet_first_chipping'   // § 24a(4c): the chipping vet enters the dog (keeper name + ID) for a fee
  | 'at_species_scope'        // HDB is for dogs and breeding cats only
  | 'at_cat_breeding_only'
  | 'at_new_registration_number' // handover: new keeper needs the current Registrierungsnummer; a new one is issued
  | 'at_death_deletion'       // death reported to the authority with a certificate: animal data deleted after 2 years
  | 'at_loss_no_field'        // § 24a and the HDB handbook describe no loss entry
  | 'it_regional_rules'       // regions add deadlines and forms; national field list not opened
  | 'it_species_scope'        // dogs mandatory everywhere; cats / ferrets per region
  | 'country_mismatch';       // ctx.country is not the registry's country

export type RegistryEntry = {
  registry: Registry;
  event: RegistryEvent;
  country: VisitContext['country'];
  approved: boolean;
  /** Always false: this module never sends anything anywhere. */
  submitted: false;
  fields: RegistryField[];
  missing: RegistryFieldKey[];
  notes: RegistryNote[];
};

function s<T extends string | boolean>(value: T | null | undefined, source: RegistrySource): RegistrySourced<T> | null {
  if (value == null) return null;
  if (typeof value === 'string') {
    const v = value.trim();
    return v ? { value: v as T, source } : null;
  }
  return { value, source };
}

type Spec = { key: RegistryFieldKey; required: boolean; basis: string };
const R = (key: RegistryFieldKey, basis: string): Spec => ({ key, required: true, basis });
const O = (key: RegistryFieldKey, basis: string): Spec => ({ key, required: false, basis });

/**
 * Field lists per registry and event, in the order the registry asks for them.
 * Bases: "§ 24a(2) Z 1 lit a" = TSchG; "HDB-HB" = Heimtierdatenbank Benutzerhandbuch v1.7;
 * "DM art. 3" = DM 2.11.2023; "FVG-M1"/"FVG-M2" = FVG Modello 1/2; "VEN" = Regione Veneto page.
 */
const SPECS: Record<Registry, Record<RegistryEvent, Spec[]>> = {
  'AT-HDB': {
    first_registration: [
      R('animal.microchip', '§ 24a(2) Z 2 lit d'), R('animal.chip_type', 'HDB-HB S. 7'), R('animal.species', 'HDB-HB S. 18/21'),
      R('animal.name', 'HDB-HB S. 8'), R('animal.breed', '§ 24a(2) Z 2 lit a'), R('animal.sex', '§ 24a(2) Z 2 lit b'),
      R('animal.date_of_birth', '§ 24a(2) Z 2 lit c'), R('animal.country_of_birth', '§ 24a(2) Z 2 lit f'),
      O('animal.dam_chip', '§ 24a(2) Z 2 lit d (sofern bekannt)'), O('animal.sire_chip', '§ 24a(2) Z 2 lit d (sofern bekannt)'),
      O('animal.interventions', '§ 24a(2) Z 2 lit e (im Falle)'), O('animal.neutering_date', '§ 24a(2) Z 2 lit j (allenfalls)'),
      O('animal.pet_passport', '§ 24a(2) Z 2 lit g (fakultativ)'), O('animal.rabies_vaccination_date', '§ 24a(2) Z 2 lit h (fakultativ)'), O('animal.rabies_vaccine', '§ 24a(2) Z 2 lit h (fakultativ)'),
      R('owner.name', '§ 24a(2) Z 1 lit a'), R('owner.id_document_type', '§ 24a(2) Z 1 lit b'), R('owner.id_document_number', '§ 24a(2) Z 1 lit b'),
      R('owner.address', '§ 24a(2) Z 1 lit c'), R('owner.contact', '§ 24a(2) Z 1 lit d'), R('owner.date_of_birth', '§ 24a(2) Z 1 lit e'),
      R('owner.keeping_since', '§ 24a(2) Z 1 lit f'), R('owner.competence_certificate', '§ 24a(2) Z 1 lit i, § 13(4)'),
      R('event.date', '§ 24a(4c) (Datum der erstmaligen Kennzeichnung)'), R('vet.name', '§ 24a(4) Z 3, (4c)'),
    ],
    change_of_owner: [
      R('animal.microchip', '§ 24a(2) Z 2 lit d'), R('animal.chip_type', 'HDB-HB S. 26'), R('animal.registration_number', 'HDB-HB S. 24/26, § 24a(5)'),
      R('owner.name', '§ 24a(2) Z 1 lit a'), R('event.date', '§ 24a(2) Z 1 lit g (Datum der Abgabe)'),
      R('new_owner.name', '§ 24a(2) Z 1 lit g'), R('new_owner.id_document_type', 'HDB-HB S. 24'), R('new_owner.id_document_number', '§ 24a(2) Z 1 lit g'),
    ],
    death: [
      R('animal.microchip', '§ 24a(2) Z 2 lit d'), R('animal.chip_type', 'HDB-HB S. 7'), R('owner.name', '§ 24a(2) Z 1 lit a'),
      R('event.date', '§ 24a(2) Z 1 lit g (Datum des Todes)'),
    ],
    loss: [
      R('animal.microchip', '§ 24a(2) Z 2 lit d'), R('animal.chip_type', 'HDB-HB S. 7'), R('owner.name', '§ 24a(2) Z 1 lit a'),
      R('owner.contact', '§ 24a(2) Z 1 lit d'), R('event.date', '—'),
    ],
  },
  'IT-SINAC': {
    first_registration: [
      R('animal.microchip', 'DM art. 3 c. 4; FVG-M1'), R('animal.species', 'VEN'), O('animal.name', '—'), R('animal.breed', 'FVG-M1; VEN'), R('animal.sex', 'FVG-M1; VEN'),
      R('animal.date_of_birth', 'FVG-M1 (data o anno); VEN'), R('animal.size', 'FVG-M1; VEN'), R('animal.coat', 'FVG-M1'), O('animal.marks', 'FVG-M1'),
      R('owner.name', 'FVG-M1; VEN'), R('owner.tax_id', 'FVG-M1'), R('owner.address', 'FVG-M1'),
      R('event.origin', 'FVG-M1'), R('event.date', 'FVG-M1 (luogo e data)'), R('vet.name', 'DM art. 3 c. 2, c. 4; FVG-M1'), O('vet.registration', '—'),
    ],
    change_of_owner: [
      R('animal.microchip', 'FVG-M2'), R('owner.name', 'FVG-M2'), R('owner.tax_id', 'FVG-M2'), R('event.date', 'DM art. 3 c. 3; FVG-M2'),
      R('new_owner.name', 'FVG-M2'), R('new_owner.tax_id', 'FVG-M2'), R('new_owner.address', 'FVG-M2'), O('new_owner.email', 'FVG-M2'),
    ],
    death: [
      R('animal.microchip', 'FVG-M2'), R('owner.name', 'FVG-M2'), R('owner.tax_id', 'FVG-M2'), R('event.date', 'DM art. 3 c. 3; FVG-M2'),
      R('event.death_certificate', 'FVG-M2 1.3'),
    ],
    loss: [
      R('animal.microchip', 'FVG-M2'), R('owner.name', 'FVG-M2'), R('owner.tax_id', 'FVG-M2'), R('event.date', 'DM art. 3 c. 3; FVG-M2'),
      R('event.place', 'FVG-M2 1.4'), O('event.theft', 'FVG-M2 1.5'), O('event.police_report', 'FVG page (sottrazione: copia della denuncia)'),
    ],
  },
};

const pick = <T extends string | boolean>(...xs: Array<RegistrySourced<T> | null>): RegistrySourced<T> | null => xs.find((x) => x != null) ?? null;

/** Builds the entry. Header values win over record values (locked facts); record signalment is the fallback. */
export function buildRegistryEntry(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, opts: RegistryOpts, registry: Registry): RegistryEntry {
  const a = opts.animal ?? {};
  const o = opts.owner ?? {};
  const n = opts.new_owner ?? {};
  const p = record.patient;

  const values: Record<RegistryFieldKey, RegistrySourced<string | boolean> | null> = {
    'animal.microchip': s(ctx.microchip, 'ctx.microchip'),
    'animal.chip_type': s(a.chip_type, 'opts.animal.chip_type'),
    'animal.registration_number': s(a.registration_number, 'opts.animal.registration_number'),
    'animal.species': pick(s(header.species, 'header.species'), s(p.species, 'record.patient.species')),
    'animal.name': pick(s(header.name, 'header.name'), s(p.name, 'record.patient.name')),
    'animal.breed': pick(s(header.breed, 'header.breed'), s(p.breed, 'record.patient.breed')),
    'animal.sex': pick(s(header.sex, 'header.sex'), s(p.sex, 'record.patient.sex')),
    'animal.date_of_birth': s(a.date_of_birth, 'opts.animal.date_of_birth'), // never from header.age
    'animal.country_of_birth': s(a.country_of_birth, 'opts.animal.country_of_birth'),
    'animal.size': s(a.size, 'opts.animal.size'),
    'animal.coat': s(a.coat, 'opts.animal.coat'),
    'animal.marks': s(a.marks, 'opts.animal.marks'),
    'animal.dam_chip': s(a.dam_chip, 'opts.animal.dam_chip'),
    'animal.sire_chip': s(a.sire_chip, 'opts.animal.sire_chip'),
    'animal.interventions': s(a.interventions, 'opts.animal.interventions'), // never from record.treatments
    'animal.neutering_date': s(a.neutering_date, 'opts.animal.neutering_date'), // never from header.neuter_status
    'animal.pet_passport': s(a.pet_passport, 'opts.animal.pet_passport'),
    'animal.rabies_vaccination_date': s(a.rabies_vaccination_date, 'opts.animal.rabies_vaccination_date'), // never from record.medications
    'animal.rabies_vaccine': s(a.rabies_vaccine, 'opts.animal.rabies_vaccine'),
    'owner.name': pick(s(ctx.owner.name, 'ctx.owner.name'), s(o.name, 'opts.owner.name')),
    'owner.tax_id': pick(s(ctx.owner.tax_id, 'ctx.owner.tax_id'), s(o.tax_id, 'opts.owner.tax_id')),
    'owner.id_document_type': s(o.id_document_type, 'opts.owner.id_document_type'),
    'owner.id_document_number': s(o.id_document_number, 'opts.owner.id_document_number'),
    'owner.address': s(o.address, 'opts.owner.address'),
    'owner.contact': s(o.contact, 'opts.owner.contact'),
    'owner.date_of_birth': s(o.date_of_birth, 'opts.owner.date_of_birth'),
    'owner.keeping_since': s(o.keeping_since, 'opts.owner.keeping_since'),
    'owner.competence_certificate': s(o.competence_certificate, 'opts.owner.competence_certificate'),
    'new_owner.name': s(n.name, 'opts.new_owner.name'),
    'new_owner.tax_id': s(n.tax_id, 'opts.new_owner.tax_id'),
    'new_owner.id_document_type': s(n.id_document_type, 'opts.new_owner.id_document_type'),
    'new_owner.id_document_number': s(n.id_document_number, 'opts.new_owner.id_document_number'),
    'new_owner.address': s(n.address, 'opts.new_owner.address'),
    'new_owner.email': s(n.email, 'opts.new_owner.email'),
    'event.date': s(opts.event_date, 'opts.event_date'),
    'event.origin': s(opts.origin, 'opts.origin'),
    'event.place': s(opts.loss?.place, 'opts.loss.place'),
    'event.theft': s(opts.loss?.theft, 'opts.loss.theft'),
    'event.police_report': s(opts.loss?.police_report, 'opts.loss.police_report'),
    'event.death_certificate': s(opts.death_certificate, 'opts.death_certificate'),
    'vet.name': s(ctx.author.name, 'ctx.author.name'),
    'vet.registration': s(ctx.author.registration, 'ctx.author.registration'),
  };

  const theft = opts.loss?.theft === true;
  const fields: RegistryField[] = SPECS[registry][opts.event].map((spec) => ({
    key: spec.key,
    value: values[spec.key],
    // a theft needs the police report (FVG); a plain loss does not
    required: spec.required || (spec.key === 'event.police_report' && theft),
    basis: spec.basis,
  }));

  const species = values['animal.species']?.value;
  const notes: RegistryNote[] = [];
  if (registry === 'AT-HDB') {
    if (ctx.country !== 'AT') notes.push('country_mismatch');
    if (opts.event === 'first_registration') notes.push('at_vet_first_chipping');
    if (species === 'cat') notes.push('at_cat_breeding_only');
    else if (species !== 'dog') notes.push('at_species_scope');
    if (opts.event === 'change_of_owner') notes.push('at_new_registration_number');
    if (opts.event === 'death') notes.push('at_death_deletion');
    if (opts.event === 'loss') notes.push('at_loss_no_field');
  } else {
    if (ctx.country !== 'IT') notes.push('country_mismatch');
    notes.push('it_regional_rules');
    if (species !== 'dog') notes.push('it_species_scope');
  }

  return {
    registry,
    event: opts.event,
    country: ctx.country,
    approved: opts.approved === true,
    submitted: false,
    fields,
    missing: fields.filter((f) => f.required && f.value === null).map((f) => f.key),
    notes,
  };
}

/* ------------------------------------------------------------------ */
/* Checklist rendering. Labels are code; values are printed as found.   */

type Labels = {
  title: Record<Registry, string>; sent: string; draft: string; copy: string;
  event: string; events: Record<RegistryEvent, string>; deadline: string; basis: string; notesTitle: string;
  sections: Record<'animal' | 'owner' | 'new_owner' | 'event' | 'vet', string>;
  f: Record<RegistryFieldKey, string>;
  missing: string; missingIntro: string; optional: string; yes: string; no: string;
  species: Record<string, string>; sex: Record<string, string>; chip: Record<string, string>; origin: Record<string, string>;
  deadlines: Record<Registry, Record<RegistryEvent, string>>;
  notes: Record<RegistryNote, string>;
};

const T: Record<Lang, Labels> = {
  en: {
    title: { 'AT-HDB': 'Data to enter in the Austrian Heimtierdatenbank', 'IT-SINAC': 'Data to enter in the Italian pet registry (SINAC)' },
    sent: 'Nothing was sent to any registry. Copy these details into the registry yourself (or through your registration office) and keep the confirmation.',
    draft: 'DRAFT — not yet approved by the veterinarian',
    copy: 'Tick each line once entered.',
    event: 'Event', events: { first_registration: 'first registration', change_of_owner: 'change of owner', death: 'death', loss: 'loss' },
    deadline: 'Deadline (rule as published; no date was calculated)', basis: 'basis', notesTitle: 'Notes',
    sections: { animal: 'Animal', owner: 'Owner / keeper', new_owner: 'New owner / keeper', event: 'Event', vet: 'Veterinarian' },
    f: {
      'animal.microchip': 'Microchip number', 'animal.chip_type': 'Chip type', 'animal.registration_number': 'Current registration number', 'animal.species': 'Species', 'animal.name': 'Name',
      'animal.breed': 'Breed', 'animal.sex': 'Sex', 'animal.date_of_birth': 'Date (or year) of birth', 'animal.country_of_birth': 'Country of birth', 'animal.size': 'Size', 'animal.coat': 'Coat',
      'animal.marks': 'Distinguishing marks', 'animal.dam_chip': 'Dam\'s chip number', 'animal.sire_chip': 'Sire\'s chip number', 'animal.interventions': 'Interventions for veterinary reasons (reason, vet)',
      'animal.neutering_date': 'Date of neutering', 'animal.pet_passport': 'Pet passport number', 'animal.rabies_vaccination_date': 'Last rabies vaccination', 'animal.rabies_vaccine': 'Rabies vaccine',
      'owner.name': 'Name', 'owner.tax_id': 'Tax code', 'owner.id_document_type': 'Photo ID: type', 'owner.id_document_number': 'Photo ID: number', 'owner.address': 'Address', 'owner.contact': 'Contact details',
      'owner.date_of_birth': 'Date of birth', 'owner.keeping_since': 'Keeping the animal since', 'owner.competence_certificate': 'Certificate of competence (Sachkundenachweis)',
      'new_owner.name': 'Name', 'new_owner.tax_id': 'Tax code', 'new_owner.id_document_type': 'Photo ID: type', 'new_owner.id_document_number': 'Photo ID: number', 'new_owner.address': 'Address', 'new_owner.email': 'E-mail',
      'event.date': 'Date', 'event.origin': 'Origin', 'event.place': 'Place lost', 'event.theft': 'Stolen', 'event.police_report': 'Police report', 'event.death_certificate': 'Death certificate issued by',
      'vet.name': 'Veterinarian', 'vet.registration': 'Registration',
    },
    missing: 'Missing', missingIntro: 'Required by the registry, not in the record and not entered:', optional: 'optional', yes: 'yes', no: 'no',
    species: { dog: 'dog', cat: 'cat', rabbit: 'rabbit', ferret: 'ferret', horse: 'horse', bird: 'bird', reptile: 'reptile', other: 'other' },
    sex: { female: 'female', male: 'male' }, chip: { ISO: 'ISO', other: 'other' }, origin: { birth: 'born from own breeding animal', acquisition: 'acquired' },
    deadlines: {
      'AT-HDB': {
        first_registration: 'Within one month of chipping, entry into Austria or taking the dog over, and in any case before passing it on (TSchG § 24a(4)). Puppies are chipped by 3 months of age and before the first handover (§ 24a(3)).',
        change_of_owner: 'Every change must be reported (§ 24a(6)); the law gives no day count. The new keeper needs the current registration number to take the animal over.',
        death: 'The death must be reported (§ 24a(2) Z 1 lit g, (6)); the law gives no day count.',
        loss: 'No deadline in § 24a.',
      },
      'IT-SINAC': {
        first_registration: 'Dogs, cats and ferrets: identified and registered by the veterinarian within 60 days of birth and in any case before any transfer (DM 2.11.2023 art. 3 c. 4). Regions may set shorter limits (e.g. Friuli Venezia Giulia: 10 days from acquisition).',
        change_of_owner: 'Within 7 days of the event (DM 2.11.2023 art. 3 c. 3). Regional rules may also apply (e.g. Friuli Venezia Giulia: 10 days to the municipality).',
        death: 'Within 7 days of the event (DM 2.11.2023 art. 3 c. 3). Regional rules may also apply (e.g. Friuli Venezia Giulia: 30 days, with the veterinary certificate).',
        loss: 'As soon as possible and in any case within 48 hours (DM 2.11.2023 art. 3 c. 3).',
      },
    },
    notes: {
      at_vet_first_chipping: 'At the first chipping the veterinarian must enter the dog (or breeding cat) with the keeper\'s name, photo ID and the chipping date, for a fee (TSchG § 24a(4c)). The registry issues a registration number; give it to the keeper (§ 24a(5)).',
      at_species_scope: 'The Heimtierdatenbank registers dogs and breeding cats (§ 24a(3), (3a)). Check whether this animal belongs there.',
      at_cat_breeding_only: 'Cats are registered only if used, or meant to be used, for breeding (§ 24a(4a)).',
      at_new_registration_number: 'A change of keeper creates a new registration number (§ 24a(6)); the old one stops being valid.',
      at_death_deletion: 'If the death is reported to the authority with a certificate of death, the animal data are deleted after two years (§ 24a(6)).',
      at_loss_no_field: 'Neither § 24a nor the Heimtierdatenbank user handbook describes a loss entry. Tell the police and the registration office; keep the keeper\'s contact details current.',
      it_regional_rules: 'Regions add their own deadlines, forms and fees, and some events go to the municipality. The national field list (ministerial instructions under DM 2.11.2023 art. 1 c. 3) was not available to us.',
      it_species_scope: 'Dogs must be registered everywhere; cats and ferrets depend on the region.',
      country_mismatch: 'The visit\'s country is not the registry\'s country: check that this is the right registry.',
    },
  },
  de: {
    title: { 'AT-HDB': 'Daten für die Eintragung in die Heimtierdatenbank', 'IT-SINAC': 'Daten für die Eintragung im italienischen Heimtierregister (SINAC)' },
    sent: 'Es wurde nichts an ein Register übermittelt. Diese Angaben selbst in die Datenbank (oder über die Meldestelle) eintragen und die Bestätigung aufbewahren.',
    draft: 'ENTWURF — noch nicht tierärztlich freigegeben',
    copy: 'Jede Zeile nach dem Eintragen abhaken.',
    event: 'Meldung', events: { first_registration: 'Erstregistrierung', change_of_owner: 'Halterwechsel', death: 'Tod', loss: 'Verlust' },
    deadline: 'Frist (Regel wie veröffentlicht; kein Datum berechnet)', basis: 'Grundlage', notesTitle: 'Hinweise',
    sections: { animal: 'Tier', owner: 'Halter/in', new_owner: 'Neue/r Halter/in', event: 'Ereignis', vet: 'Tierärztin / Tierarzt' },
    f: {
      'animal.microchip': 'Chipnummer', 'animal.chip_type': 'Chiptyp', 'animal.registration_number': 'Aktuelle Registrierungsnummer', 'animal.species': 'Tierart', 'animal.name': 'Name',
      'animal.breed': 'Rasse', 'animal.sex': 'Geschlecht', 'animal.date_of_birth': 'Geburtsdatum (zumindest Jahr)', 'animal.country_of_birth': 'Geburtsland', 'animal.size': 'Größe', 'animal.coat': 'Fellfarbe',
      'animal.marks': 'Besondere Kennzeichen', 'animal.dam_chip': 'Chipnummer Muttertier', 'animal.sire_chip': 'Chipnummer Vatertier', 'animal.interventions': 'Eingriffe aus veterinärmedizinischem Grund (Grund, Tierarzt)',
      'animal.neutering_date': 'Datum des Eingriffs zur Verhütung der Fortpflanzung', 'animal.pet_passport': 'Nummer des Heimtierausweises', 'animal.rabies_vaccination_date': 'Letzte Tollwutimpfung', 'animal.rabies_vaccine': 'Tollwutimpfstoff',
      'owner.name': 'Name', 'owner.tax_id': 'Steuernummer (codice fiscale)', 'owner.id_document_type': 'Amtlicher Lichtbildausweis: Art', 'owner.id_document_number': 'Amtlicher Lichtbildausweis: Nummer', 'owner.address': 'Zustelladresse', 'owner.contact': 'Kontaktdaten',
      'owner.date_of_birth': 'Geburtsdatum', 'owner.keeping_since': 'Datum der Aufnahme der Haltung', 'owner.competence_certificate': 'Sachkundenachweis (§ 13 Abs. 4 TSchG)',
      'new_owner.name': 'Name', 'new_owner.tax_id': 'Steuernummer (codice fiscale)', 'new_owner.id_document_type': 'Amtlicher Lichtbildausweis: Art', 'new_owner.id_document_number': 'Amtlicher Lichtbildausweis: Nummer', 'new_owner.address': 'Adresse', 'new_owner.email': 'E-Mail',
      'event.date': 'Datum', 'event.origin': 'Herkunft', 'event.place': 'Ort des Verlusts', 'event.theft': 'Gestohlen', 'event.police_report': 'Anzeige', 'event.death_certificate': 'Todesbescheinigung ausgestellt von',
      'vet.name': 'Tierärztin / Tierarzt', 'vet.registration': 'Registrierung',
    },
    missing: 'Fehlt', missingIntro: 'Vom Register verlangt, weder im Datensatz noch eingetragen:', optional: 'freiwillig', yes: 'ja', no: 'nein',
    species: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'anderes Tier' },
    sex: { female: 'weiblich', male: 'männlich' }, chip: { ISO: 'ISO', other: 'Andere' }, origin: { birth: 'aus eigener Zucht geboren', acquisition: 'erworben' },
    deadlines: {
      'AT-HDB': {
        first_registration: 'Binnen eines Monats nach Kennzeichnung, Einreise oder Übernahme, jedenfalls vor einer Weitergabe (TSchG § 24a Abs. 4). Welpen spätestens mit drei Monaten und vor der ersten Weitergabe kennzeichnen (§ 24a Abs. 3).',
        change_of_owner: 'Jede Änderung ist zu melden (§ 24a Abs. 6); eine Frist in Tagen nennt das Gesetz nicht. Die neue Halterin / der neue Halter braucht für die Übernahme die aktuelle Registrierungsnummer.',
        death: 'Der Tod ist zu melden (§ 24a Abs. 2 Z 1 lit. g, Abs. 6); eine Frist in Tagen nennt das Gesetz nicht.',
        loss: 'Keine Frist in § 24a.',
      },
      'IT-SINAC': {
        first_registration: 'Hunde, Katzen, Frettchen: Kennzeichnung und Registrierung durch die Tierärztin / den Tierarzt binnen 60 Tagen nach der Geburt, jedenfalls vor einer Abgabe (DM 2.11.2023 Art. 3 Abs. 4). Regionen können kürzere Fristen setzen.',
        change_of_owner: 'Binnen 7 Tagen nach dem Ereignis (DM 2.11.2023 Art. 3 Abs. 3); regionale Regeln können zusätzlich gelten.',
        death: 'Binnen 7 Tagen nach dem Ereignis (DM 2.11.2023 Art. 3 Abs. 3); regionale Regeln können zusätzlich gelten.',
        loss: 'So bald wie möglich, spätestens binnen 48 Stunden (DM 2.11.2023 Art. 3 Abs. 3).',
      },
    },
    notes: {
      at_vet_first_chipping: 'Bei der erstmaligen Kennzeichnung muss die Tierärztin / der Tierarzt den Hund (oder die Zuchtkatze) mit Name und Lichtbildausweis der Halterin / des Halters und dem Kennzeichnungsdatum gegen Entgelt erfassen (TSchG § 24a Abs. 4c). Die Datenbank vergibt eine Registrierungsnummer; diese der Halterin / dem Halter mitteilen (§ 24a Abs. 5).',
      at_species_scope: 'Die Heimtierdatenbank erfasst Hunde und Zuchtkatzen (§ 24a Abs. 3, 3a). Prüfen, ob dieses Tier dort hingehört.',
      at_cat_breeding_only: 'Katzen werden nur erfasst, wenn sie zur Zucht verwendet werden oder werden sollen (§ 24a Abs. 4a).',
      at_new_registration_number: 'Ein Halterwechsel erzeugt eine neue Registrierungsnummer (§ 24a Abs. 6); die alte gilt nicht mehr.',
      at_death_deletion: 'Wird der Tod der Behörde mit einer Bescheinigung gemeldet, werden die Tierdaten nach zwei Jahren gelöscht (§ 24a Abs. 6).',
      at_loss_no_field: 'Weder § 24a noch das Benutzerhandbuch der Heimtierdatenbank sehen eine Verlustmeldung vor. Polizei und Meldestelle verständigen; Kontaktdaten aktuell halten.',
      it_regional_rules: 'Die Regionen setzen eigene Fristen, Formulare und Gebühren; manche Meldungen gehen an die Gemeinde. Die nationale Feldliste (Anweisungen nach DM 2.11.2023 Art. 1 Abs. 3) lag uns nicht vor.',
      it_species_scope: 'Hunde sind überall zu registrieren; Katzen und Frettchen je nach Region.',
      country_mismatch: 'Das Land des Besuchs ist nicht das Land des Registers: prüfen, ob dies das richtige Register ist.',
    },
  },
  it: {
    title: { 'AT-HDB': 'Dati da inserire nella Heimtierdatenbank austriaca', 'IT-SINAC': 'Dati da inserire in anagrafe (SINAC)' },
    sent: 'Nulla è stato inviato ad alcuna anagrafe. Inserire questi dati personalmente nel sistema (o tramite l\'ufficio competente) e conservare la conferma.',
    draft: 'BOZZA — non ancora approvata dal veterinario',
    copy: 'Spuntare ogni riga una volta inserita.',
    event: 'Evento', events: { first_registration: 'prima iscrizione', change_of_owner: 'passaggio di proprietà', death: 'decesso', loss: 'smarrimento' },
    deadline: 'Termine (regola come pubblicata; nessuna data è stata calcolata)', basis: 'fonte', notesTitle: 'Note',
    sections: { animal: 'Animale', owner: 'Proprietario / detentore', new_owner: 'Nuovo proprietario / detentore', event: 'Evento', vet: 'Medico veterinario' },
    f: {
      'animal.microchip': 'Codice microchip', 'animal.chip_type': 'Tipo di chip', 'animal.registration_number': 'Numero di registrazione attuale', 'animal.species': 'Specie', 'animal.name': 'Nome',
      'animal.breed': 'Razza', 'animal.sex': 'Sesso', 'animal.date_of_birth': 'Data o anno di nascita', 'animal.country_of_birth': 'Paese di nascita', 'animal.size': 'Taglia', 'animal.coat': 'Mantello',
      'animal.marks': 'Note o segni particolari', 'animal.dam_chip': 'Microchip della madre', 'animal.sire_chip': 'Microchip del padre', 'animal.interventions': 'Interventi per motivi veterinari (motivo, veterinario)',
      'animal.neutering_date': 'Data della sterilizzazione', 'animal.pet_passport': 'Numero del passaporto', 'animal.rabies_vaccination_date': 'Ultima vaccinazione antirabbica', 'animal.rabies_vaccine': 'Vaccino antirabbico',
      'owner.name': 'Cognome e nome', 'owner.tax_id': 'Codice fiscale', 'owner.id_document_type': 'Documento d\'identità: tipo', 'owner.id_document_number': 'Documento d\'identità: numero', 'owner.address': 'Residenza', 'owner.contact': 'Recapiti',
      'owner.date_of_birth': 'Data di nascita', 'owner.keeping_since': 'Detenzione dal', 'owner.competence_certificate': 'Attestato di competenza (Sachkundenachweis)',
      'new_owner.name': 'Cognome e nome', 'new_owner.tax_id': 'Codice fiscale', 'new_owner.id_document_type': 'Documento d\'identità: tipo', 'new_owner.id_document_number': 'Documento d\'identità: numero', 'new_owner.address': 'Residenza', 'new_owner.email': 'E-mail',
      'event.date': 'Data', 'event.origin': 'Provenienza', 'event.place': 'Località dello smarrimento', 'event.theft': 'Sottratto', 'event.police_report': 'Denuncia', 'event.death_certificate': 'Certificato di decesso rilasciato da',
      'vet.name': 'Medico veterinario', 'vet.registration': 'Iscrizione all\'Ordine',
    },
    missing: 'Mancante', missingIntro: 'Richiesto dall\'anagrafe, non presente nella cartella e non inserito:', optional: 'facoltativo', yes: 'sì', no: 'no',
    species: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' },
    sex: { female: 'femmina', male: 'maschio' }, chip: { ISO: 'ISO', other: 'altro' }, origin: { birth: 'nascita da proprio riproduttore', acquisition: 'acquisizione' },
    deadlines: {
      'AT-HDB': {
        first_registration: 'Entro un mese dalla marcatura, dall\'ingresso in Austria o dalla presa in carico, e comunque prima di una cessione (TSchG § 24a c. 4).',
        change_of_owner: 'Ogni variazione va comunicata (§ 24a c. 6); la legge non indica un numero di giorni.',
        death: 'Il decesso va comunicato (§ 24a c. 2 n. 1 lett. g, c. 6); la legge non indica un numero di giorni.',
        loss: 'Nessun termine nel § 24a.',
      },
      'IT-SINAC': {
        first_registration: 'Cani, gatti e furetti: identificati e registrati dal medico veterinario entro sessanta giorni dalla nascita e comunque prima della cessione (DM 2.11.2023 art. 3 c. 4). Le regioni possono prevedere termini più brevi (es. Friuli Venezia Giulia: 10 giorni dall\'acquisto).',
        change_of_owner: 'Entro sette giorni dall\'evento (DM 2.11.2023 art. 3 c. 3). Possono valere anche regole regionali (es. Friuli Venezia Giulia: 10 giorni al Comune).',
        death: 'Entro sette giorni dall\'evento (DM 2.11.2023 art. 3 c. 3). Possono valere anche regole regionali (es. Friuli Venezia Giulia: 30 giorni, con certificato veterinario).',
        loss: 'Nel più breve tempo possibile e comunque entro quarantotto ore (DM 2.11.2023 art. 3 c. 3).',
      },
    },
    notes: {
      at_vet_first_chipping: 'Alla prima marcatura il veterinario deve registrare il cane (o il gatto da riproduzione) con nome e documento del detentore e data della marcatura, a pagamento (TSchG § 24a c. 4c).',
      at_species_scope: 'La Heimtierdatenbank registra cani e gatti da riproduzione (§ 24a c. 3, 3a).',
      at_cat_breeding_only: 'I gatti si registrano solo se usati o destinati alla riproduzione (§ 24a c. 4a).',
      at_new_registration_number: 'Un cambio di detentore genera un nuovo numero di registrazione (§ 24a c. 6).',
      at_death_deletion: 'Se il decesso è comunicato all\'autorità con certificato, i dati dell\'animale sono cancellati dopo due anni (§ 24a c. 6).',
      at_loss_no_field: 'Né il § 24a né il manuale della Heimtierdatenbank prevedono una registrazione dello smarrimento.',
      it_regional_rules: 'Le regioni aggiungono termini, moduli e tariffe propri, e alcune comunicazioni vanno al Comune. L\'elenco nazionale dei campi (istruzioni ministeriali di cui al DM 2.11.2023 art. 1 c. 3) non era a nostra disposizione.',
      it_species_scope: 'I cani vanno registrati ovunque; gatti e furetti secondo la regione.',
      country_mismatch: 'Il paese della visita non è quello dell\'anagrafe: verificare che sia l\'anagrafe giusta.',
    },
  },
};

const SECTION_OF = (k: RegistryFieldKey) => k.split('.')[0] as keyof Labels['sections'];

function show(f: RegistryField, t: Labels): string {
  const v = f.value!.value;
  if (typeof v === 'boolean') return v ? t.yes : t.no;
  if (f.key === 'animal.species') return t.species[v] ?? v;
  if (f.key === 'animal.sex') return t.sex[v] ?? v;
  if (f.key === 'animal.chip_type') return t.chip[v] ?? v;
  if (f.key === 'event.origin') return t.origin[v] ?? v;
  return v;
}

/** The checklist: default language DE for the Austrian registry, IT for SINAC. */
export function renderRegistryEntry(entry: RegistryEntry, lang: Lang = entry.registry === 'AT-HDB' ? 'de' : 'it'): string {
  const t = T[lang] ?? T.en;
  const out: string[] = [];
  out.push(`# ${t.title[entry.registry]}`);
  if (!entry.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${t.sent}**`);
  out.push('');
  out.push(`${t.event}: ${t.events[entry.event]}`);
  out.push('');
  out.push(`_${t.copy}_`);

  let section = '';
  for (const f of entry.fields) {
    const sec = SECTION_OF(f.key);
    if (sec !== section) {
      section = sec;
      out.push('');
      out.push(`## ${t.sections[sec]}`);
    }
    const label = `${t.f[f.key]}${f.required ? '' : ` (${t.optional})`}`;
    if (f.value) out.push(`- [ ] ${label}: ${show(f, t)}`);
    else if (f.required) out.push(`- [ ] ${label}: ▲ ${t.missing}`);
    else out.push(`- [ ] ${label}: —`);
  }

  out.push('');
  out.push(`## ${t.deadline}`);
  out.push(t.deadlines[entry.registry][entry.event]);

  if (entry.notes.length) {
    out.push('');
    out.push(`## ${t.notesTitle}`);
    for (const n of entry.notes) out.push(`- ${t.notes[n]}`);
  }

  if (entry.missing.length) {
    out.push('');
    out.push(`## ▲ ${t.missing}`);
    out.push(t.missingIntro);
    for (const k of entry.missing) out.push(`- ${t.sections[SECTION_OF(k)]}: ${t.f[k]}`);
  }
  return out.join('\n');
}
