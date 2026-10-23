import type { ClinicalRecord, PatientHeader } from './schema.js';
import type { VisitContext } from './country.js';
import type { Lang } from './render.js';

/**
 * Third-country animal health certificate pre-fill (see docs/22-third-country-certificate.md).
 *
 * Model: Annex III, Part 1 to Commission Implementing Regulation (EU) 2026/705, the
 * certificate required by Art. 18(1) of Commission Delegated Regulation (EU) 2026/131 for the
 * non-commercial movement of pet dogs, cats and ferrets into a Member State from a third
 * country or territory (both apply from 22 April 2026).
 *
 * This is a data sheet to transcribe, never the certificate. Only an official veterinarian of
 * the third country of dispatch, or a veterinarian authorised there whose certificate is then
 * endorsed by that country's competent authority, issues and signs it (Art. 19(a) 2026/131).
 * Nothing was sent or signed; `signed` and `sent` are always false.
 *
 * Rules:
 * - every value comes from the patient header, the visit context, the approved record
 *   (signalment fallback only) or what the vet typed (`opts`), and says so;
 * - nothing is inferred: no date of birth from the age, no colour, no validity period computed
 *   from the vaccination date, no 21-day / 90-day / 24–120-hour arithmetic, no judgement of
 *   whether the animal may travel, no choice of certificate option (titration or listed
 *   country; Echinococcus treated or not) on the vet's behalf, no rabies vaccine picked out of
 *   the record's medications (only a dispensing line the vet points at);
 * - everything the certificate asks for and is absent is null and listed in `missing`.
 */

export type TravelSource = `header.${string}` | `record.${string}` | `ctx.${string}` | `opts.${string}`;
export type TravelSourced<T> = { value: T; source: TravelSource };

export type TravelOpts = {
  approved?: boolean;
  /** Owner details beyond ctx.owner.name (Box I.1 consignor: name, address, telephone; Art. 18(2)(d)). */
  owner?: { name?: string | null; address?: string | null; phone?: string | null };
  /** Who carries out the movement and signs the non-commercial declaration (II.5; Annex V Parts 1–2). */
  declaration_by?: 'owner' | 'authorised_person' | null;
  /** Person authorised in writing by the owner (Art. 4 2026/131; Annex V Part 1). */
  authorised_person?: { name?: string | null; address?: string | null; phone?: string | null };
  /** Third country or territory of dispatch, as typed (Box I.7; II.b "of … (insert name …)"). */
  dispatch_country?: string | null;
  /** Member State of first destination, as typed (Box I.5 note; Box I.9). */
  destination_member_state?: string | null;
  animal?: {
    colour?: string | null;
    /** As stated by the owner (Box I.28 note). Never derived from the age. */
    date_of_birth?: string | null;
    /** Only when no transponder code is in ctx.microchip: a tattoo applied before 3 July 2011. */
    id_code?: string | null;
    id_system?: 'transponder' | 'tattoo' | null;
    /** Location of the transponder or tattoo on the animal (Art. 18(2)(a)). */
    id_location?: string | null;
    /** Date of implantation and/or reading (II.3 table, note 8). */
    id_date?: string | null;
  };
  rabies?: {
    /** Index into ctx.dispensings for the rabies vaccine the vet points at. Never searched for. */
    dispensing_index?: number | null;
    vaccination_date?: string | null;
    vaccine?: string | null;
    manufacturer?: string | null;
    batch?: string | null;
    valid_from?: string | null;
    valid_to?: string | null;
  };
  /** Which II.3.1 option the vet keeps: country listed in Annex II 2026/636, or titration test. Never chosen for them. */
  rabies_option?: 'listed_country' | 'titration' | null;
  titration?: {
    sample_date?: string | null;
    /** Not a box on the certificate: the lab report is attached (note 6). Kept for the attachment check. */
    laboratory?: string | null;
    result?: string | null;
  };
  /** Which II.4 option the vet keeps (dogs only). Never chosen for them. */
  echinococcus_option?: 'treated' | 'not_treated' | null;
  echinococcus?: {
    product?: string | null;
    manufacturer?: string | null;
    date?: string | null;
    time?: string | null;
    administering_vet?: string | null;
  };
  /** Role of the veterinarian who will issue the certificate (II.b). */
  vet_role?: 'official' | 'authorised' | null;
};

export type TravelFieldKey =
  | 'owner.name' | 'owner.address' | 'owner.phone'
  | 'authorised_person.name' | 'authorised_person.address' | 'authorised_person.phone'
  | 'movement.dispatch_country' | 'movement.destination_member_state'
  | 'animal.species' | 'animal.sex' | 'animal.colour' | 'animal.breed' | 'animal.id_code' | 'animal.id_system'
  | 'animal.id_location' | 'animal.id_date' | 'animal.date_of_birth' | 'animal.name'
  | 'rabies.option' | 'rabies.vaccination_date' | 'rabies.vaccine' | 'rabies.manufacturer' | 'rabies.batch'
  | 'rabies.valid_from' | 'rabies.valid_to'
  | 'titration.sample_date' | 'titration.laboratory' | 'titration.result'
  | 'echinococcus.option' | 'echinococcus.product' | 'echinococcus.manufacturer' | 'echinococcus.date'
  | 'echinococcus.time' | 'echinococcus.administering_vet'
  | 'declaration.by'
  | 'vet.name' | 'vet.role';

export type TravelField = {
  key: TravelFieldKey;
  value: TravelSourced<string> | null;
  required: boolean;
  /** Box on the model certificate (Annex III Part 1 to 2026/705), or "Annex V" for a declaration, or "—" (not a box). */
  box: string;
  /** Short legal basis. "DR" = Delegated Reg. (EU) 2026/131; "IR" = Implementing Reg. (EU) 2026/705. */
  basis: string;
};

export type TravelNote =
  | 'issuer_third_country'    // only the third country's official vet, or an authorised vet + endorsement, issues it
  | 'passport_alternative'    // Art. 20: EU passport on return; Annex II passport from Annex I countries
  | 'old_model_transition'    // IR Art. 6(3): 577/2013 Annex IV model issued before 1 Oct 2026, accepted until 31 Mar 2027
  | 'validity_rule'           // note (b): 10 days to entry; then 6 months or rabies expiry, whichever earlier — no date computed
  | 'authorised_vet_endorsement'
  | 'species_out_of_scope';   // the model covers dogs, cats and ferrets only

export type TravelAttachment =
  | 'id_vaccination_copy'     // note (4): certified copy of identification and vaccination details
  | 'lab_report'              // note (6): certified copy of the official lab report (titration option only)
  | 'non_commercial_declaration' // Art. 18(3) DR; Annex V Part 2 IR
  | 'owner_authorisation';    // Art. 4 DR; Annex V Part 1 IR

export type TravelCertificatePack = {
  model: 'EU 2026/705 Annex III';
  country: VisitContext['country'];
  approved: boolean;
  /** Always false: this is not a certificate and nothing was signed. */
  signed: false;
  /** Always false: nothing was sent to anyone. */
  sent: false;
  fields: TravelField[];
  missing: TravelFieldKey[];
  notes: TravelNote[];
  attachments: TravelAttachment[];
};

function s(value: string | null | undefined, source: TravelSource): TravelSourced<string> | null {
  if (value == null) return null;
  const v = value.trim();
  return v ? { value: v, source } : null;
}

const pick = (...xs: Array<TravelSourced<string> | null>): TravelSourced<string> | null => xs.find((x) => x != null) ?? null;

const PET_SPECIES = new Set(['dog', 'cat', 'ferret']);

/** Builds the pre-fill. Header values win over record values; typed values at this step win over the visit's dispensing line. */
export function buildTravelCertificate(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, opts: TravelOpts = {}): TravelCertificatePack {
  const p = record.patient;
  const o = opts.owner ?? {};
  const ap = opts.authorised_person ?? {};
  const a = opts.animal ?? {};
  const r = opts.rabies ?? {};
  const t = opts.titration ?? {};
  const e = opts.echinococcus ?? {};

  const di = r.dispensing_index;
  const disp = di != null && Number.isInteger(di) && di >= 0 ? ctx.dispensings[di] : undefined;
  const dsrc = (k: string) => `ctx.dispensings.${di}.${k}` as TravelSource;

  const values: Record<TravelFieldKey, TravelSourced<string> | null> = {
    'owner.name': pick(s(ctx.owner.name, 'ctx.owner.name'), s(o.name, 'opts.owner.name')),
    'owner.address': s(o.address, 'opts.owner.address'),
    'owner.phone': s(o.phone, 'opts.owner.phone'),
    'authorised_person.name': s(ap.name, 'opts.authorised_person.name'),
    'authorised_person.address': s(ap.address, 'opts.authorised_person.address'),
    'authorised_person.phone': s(ap.phone, 'opts.authorised_person.phone'),
    'movement.dispatch_country': s(opts.dispatch_country, 'opts.dispatch_country'),
    'movement.destination_member_state': s(opts.destination_member_state, 'opts.destination_member_state'),
    'animal.species': pick(s(header.species, 'header.species'), s(p.species, 'record.patient.species')),
    'animal.sex': pick(s(header.sex, 'header.sex'), s(p.sex, 'record.patient.sex')),
    'animal.colour': s(a.colour, 'opts.animal.colour'),
    'animal.breed': pick(s(header.breed, 'header.breed'), s(p.breed, 'record.patient.breed')),
    'animal.id_code': pick(s(ctx.microchip, 'ctx.microchip'), s(a.id_code, 'opts.animal.id_code')),
    'animal.id_system': s(a.id_system, 'opts.animal.id_system'), // never assumed "transponder" from a chip number
    'animal.id_location': s(a.id_location, 'opts.animal.id_location'),
    'animal.id_date': s(a.id_date, 'opts.animal.id_date'),
    'animal.date_of_birth': s(a.date_of_birth, 'opts.animal.date_of_birth'), // never from header.age
    'animal.name': pick(s(header.name, 'header.name'), s(p.name, 'record.patient.name')),
    'rabies.option': s(opts.rabies_option, 'opts.rabies_option'),
    'rabies.vaccination_date': s(r.vaccination_date, 'opts.rabies.vaccination_date'), // the record carries no dates
    'rabies.vaccine': pick(s(r.vaccine, 'opts.rabies.vaccine'), s(disp?.product, dsrc('product'))),
    'rabies.manufacturer': s(r.manufacturer, 'opts.rabies.manufacturer'),
    'rabies.batch': pick(s(r.batch, 'opts.rabies.batch'), s(disp?.batch, dsrc('batch'))),
    'rabies.valid_from': s(r.valid_from, 'opts.rabies.valid_from'), // never vaccination date + 21 days
    'rabies.valid_to': pick(s(r.valid_to, 'opts.rabies.valid_to'), s(disp?.valid_until, dsrc('valid_until'))), // never computed
    'titration.sample_date': s(t.sample_date, 'opts.titration.sample_date'),
    'titration.laboratory': s(t.laboratory, 'opts.titration.laboratory'),
    'titration.result': s(t.result, 'opts.titration.result'),
    'echinococcus.option': s(opts.echinococcus_option, 'opts.echinococcus_option'),
    'echinococcus.product': s(e.product, 'opts.echinococcus.product'),
    'echinococcus.manufacturer': s(e.manufacturer, 'opts.echinococcus.manufacturer'),
    'echinococcus.date': s(e.date, 'opts.echinococcus.date'),
    'echinococcus.time': s(e.time, 'opts.echinococcus.time'),
    'echinococcus.administering_vet': s(e.administering_vet, 'opts.echinococcus.administering_vet'),
    'declaration.by': s(opts.declaration_by, 'opts.declaration_by'),
    'vet.name': s(ctx.author.name, 'ctx.author.name'),
    'vet.role': s(opts.vet_role, 'opts.vet_role'),
  };

  const species = values['animal.species']?.value;
  const isDog = species === 'dog';
  const byAuthorised = opts.declaration_by === 'authorised_person';
  const titration = opts.rabies_option === 'titration';
  const treated = opts.echinococcus_option === 'treated';

  type Spec = [TravelFieldKey, boolean, string, string];
  const specs: Spec[] = [
    ['owner.name', true, 'I.1', 'DR Art. 18(2)(d)'],
    ['owner.address', true, 'I.1', 'DR Art. 18(2)(d)'],
    ['owner.phone', true, 'I.1', 'DR Art. 18(2)(d)'],
    ...(byAuthorised ? ([
      ['authorised_person.name', true, 'Annex V Part 1', 'DR Art. 4; IR Art. 5(1)'],
      ['authorised_person.address', false, 'Annex V Part 1', 'DR Art. 4'],
      ['authorised_person.phone', false, 'Annex V Part 1', 'DR Art. 4'],
    ] as Spec[]) : []),
    ['movement.dispatch_country', true, 'I.7; II.b', 'IR Annex III Part 1'],
    ['movement.destination_member_state', true, 'I.5; I.9', 'IR Annex III Part 1, note to Box I.5'],
    ['animal.species', true, 'I.28', 'DR Art. 18(2)(b)'],
    ['animal.sex', true, 'I.28', 'DR Art. 18(2)(b)'],
    ['animal.colour', true, 'I.28', 'DR Art. 18(2)(b)'],
    ['animal.breed', true, 'I.28', 'DR Art. 18(2)(b)'],
    ['animal.id_code', true, 'I.28; II.3', 'DR Art. 18(2)(a)'],
    ['animal.id_system', true, 'I.28', 'DR Art. 18(2)(a); note to Box I.28'],
    ['animal.id_location', true, 'I.28', 'DR Art. 18(2)(a)'],
    ['animal.id_date', true, 'II.3', 'DR Art. 18(2)(a); note (8)'],
    ['animal.date_of_birth', true, 'I.28', 'DR Art. 18(2)(b) (as stated by the owner)'],
    ['animal.name', false, '—', 'not a box on the model'],
    ['rabies.option', true, 'II.3.1', 'DR Art. 14(b)–(c), 17; IR note (1)'],
    ['rabies.vaccination_date', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['rabies.vaccine', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['rabies.manufacturer', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['rabies.batch', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['rabies.valid_from', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['rabies.valid_to', true, 'II.3', 'DR Art. 18(2)(f)'],
    ['titration.sample_date', titration, 'II.3', 'DR Art. 18(2)(g); IR note (6)'],
    ['titration.laboratory', false, '— (lab report attached)', 'IR note (6)'],
    ['titration.result', false, '— (lab report attached)', 'IR note (6)'],
    ...(isDog ? ([
      ['echinococcus.option', true, 'II.4', 'DR Art. 14(d), 18(2)(h); IR note (1)'],
      ['echinococcus.product', treated, 'II.4', 'DR Art. 18(2)(h); IR note (12)'],
      ['echinococcus.manufacturer', treated, 'II.4', 'DR Art. 18(2)(h)'],
      ['echinococcus.date', treated, 'II.4', 'DR Art. 18(2)(h)'],
      ['echinococcus.time', treated, 'II.4', 'DR Art. 18(2)(h)'],
      ['echinococcus.administering_vet', treated, 'II.4', 'DR Art. 18(2)(h)'],
    ] as Spec[]) : []),
    ['declaration.by', true, 'II.5', 'DR Art. 18(3); IR Annex V Parts 1–2'],
    ['vet.name', true, 'II', 'DR Art. 18(2)(e), 19(a)'],
    ['vet.role', true, 'II.b', 'DR Art. 19(a)'],
  ];

  const fields: TravelField[] = specs.map(([key, required, box, basis]) => ({ key, value: values[key], required, box, basis }));

  const notes: TravelNote[] = ['issuer_third_country', 'passport_alternative', 'old_model_transition', 'validity_rule'];
  if (opts.vet_role === 'authorised') notes.push('authorised_vet_endorsement');
  if (species && !PET_SPECIES.has(species)) notes.push('species_out_of_scope');

  const attachments: TravelAttachment[] = ['id_vaccination_copy', 'non_commercial_declaration'];
  if (titration) attachments.push('lab_report');
  if (byAuthorised) attachments.push('owner_authorisation');

  return {
    model: 'EU 2026/705 Annex III',
    country: ctx.country,
    approved: opts.approved === true,
    signed: false,
    sent: false,
    fields,
    missing: fields.filter((f) => f.required && f.value === null).map((f) => f.key),
    notes,
    attachments,
  };
}

/* ------------------------------------------------------------------ */
/* Checklist rendering. Labels are code; values are printed as typed.   */

type Section = 'owner' | 'authorised_person' | 'movement' | 'animal' | 'rabies' | 'titration' | 'echinococcus' | 'declaration' | 'vet';

type Labels = {
  title: string; notCertificate: string; nothingSent: string; draft: string; copy: string; dateFormat: string;
  sections: Record<Section, string>;
  f: Record<TravelFieldKey, string>;
  missing: string; missingIntro: string; optional: string; box: string;
  species: Record<string, string>; sex: Record<string, string>; idSystem: Record<string, string>;
  options: Record<string, string>;
  leftTitle: string; left: string[];
  attachTitle: string; attach: Record<TravelAttachment, string>;
  notesTitle: string; notes: Record<TravelNote, string>;
};

const SCI: Record<string, string> = { dog: 'Canis lupus familiaris', cat: 'Felis silvestris catus', ferret: 'Mustela putorius furo' };

const T: Record<Lang, Labels> = {
  en: {
    title: 'Pre-fill for the official certificate — not a certificate; must be completed and signed by an official/authorised veterinarian',
    notCertificate: 'Model: animal health certificate for non-commercial movements of pet dogs, cats or ferrets into a Member State from a third country or territory, Annex III Part 1 to Implementing Regulation (EU) 2026/705 (Art. 18(1) Delegated Regulation (EU) 2026/131). This sheet has no legal effect.',
    nothingSent: 'Nothing was signed, certified or sent. Transcribe each line into the official certificate in block letters; the issuing veterinarian checks every entry against the animal and the original documents.',
    draft: 'DRAFT — not yet approved by the veterinarian',
    copy: 'Tick each line once transcribed.',
    dateFormat: 'Dates are shown as entered; the certificate uses dd/mm/yyyy.',
    sections: { owner: 'Owner (Box I.1)', authorised_person: 'Authorised person (Annex V Part 1)', movement: 'Movement', animal: 'Animal (Box I.28)', rabies: 'Rabies vaccination (II.3)', titration: 'Rabies antibody titration test (II.3.1)', echinococcus: 'Echinococcus multilocularis treatment (II.4, dogs)', declaration: 'Non-commercial declaration (II.5)', vet: 'Issuing veterinarian' },
    f: {
      'owner.name': 'Name', 'owner.address': 'Address', 'owner.phone': 'Telephone',
      'authorised_person.name': 'Name', 'authorised_person.address': 'Address', 'authorised_person.phone': 'Telephone',
      'movement.dispatch_country': 'Third country or territory of dispatch', 'movement.destination_member_state': 'Member State of first destination',
      'animal.species': 'Species (scientific name)', 'animal.sex': 'Sex', 'animal.colour': 'Colour', 'animal.breed': 'Breed', 'animal.id_code': 'Identification number (transponder or tattoo)',
      'animal.id_system': 'Identification system', 'animal.id_location': 'Location of transponder or tattoo', 'animal.id_date': 'Date of implantation and/or reading',
      'animal.date_of_birth': 'Date of birth (as stated by the owner)', 'animal.name': 'Name of the animal',
      'rabies.option': 'Option kept in II.3.1', 'rabies.vaccination_date': 'Date of vaccination', 'rabies.vaccine': 'Name of vaccine', 'rabies.manufacturer': 'Manufacturer of vaccine', 'rabies.batch': 'Batch number',
      'rabies.valid_from': 'Validity of vaccination: from', 'rabies.valid_to': 'Validity of vaccination: to',
      'titration.sample_date': 'Date of the blood sampling', 'titration.laboratory': 'Laboratory (on the attached report)', 'titration.result': 'Result (on the attached report)',
      'echinococcus.option': 'Option kept in II.4', 'echinococcus.product': 'Name of the product', 'echinococcus.manufacturer': 'Manufacturer of the product', 'echinococcus.date': 'Date of treatment', 'echinococcus.time': 'Time of treatment', 'echinococcus.administering_vet': 'Administering veterinarian',
      'declaration.by': 'Declaration signed by',
      'vet.name': 'Name', 'vet.role': 'Capacity',
    },
    missing: 'Missing', missingIntro: 'Asked for by the certificate, not in the record and not entered:', optional: 'not a box on the certificate', box: 'box',
    species: { dog: 'dog', cat: 'cat', ferret: 'ferret', rabbit: 'rabbit', horse: 'horse', bird: 'bird', reptile: 'reptile', other: 'other' },
    sex: { female: 'female', male: 'male' }, idSystem: { transponder: 'transponder', tattoo: 'tattoo' },
    options: {
      listed_country: 'from a country listed in Annex II to Implementing Regulation (EU) 2026/636 (no titration test)', titration: 'rabies antibody titration test',
      treated: 'treated against Echinococcus multilocularis', not_treated: 'not treated against Echinococcus multilocularis',
      owner: 'the owner', authorised_person: 'the person authorised in writing by the owner',
      official: 'official veterinarian', authorised: 'veterinarian authorised by the competent authority',
    },
    leftTitle: 'Left for the issuing veterinarian and the authorities (not pre-filled)',
    left: [
      'Certificate reference number (I.2, II.a): issued by the competent authority of the country of dispatch.',
      'Other Part I boxes (I.3, I.4, I.6, I.8, I.10–I.27): as the competent authority requires.',
      'II.1 number of animals and, for more than five, the event evidence.',
      'II.2 clinical examination: "no disease symptoms and fit for the non-commercial movement on …": only after the vet examines the animal.',
      'Deleting the options not kept (note (1)); date of issue; signature (in a colour different from the print) and stamp.',
      'Endorsement by the competent authority, when an authorised veterinarian signs.',
      'Travellers\' point of entry block: completed by the official at entry into the EU.',
    ],
    attachTitle: 'To attach',
    attach: {
      id_vaccination_copy: 'Certified copy of the identification and vaccination details (note (4)).',
      lab_report: 'Certified copy of the official report of the designated laboratory on the rabies antibody titration test (note (6)).',
      non_commercial_declaration: 'Written declaration that the movement is non-commercial, signed by the owner or the authorised person (Art. 18(3) DR 2026/131; Annex V Part 2 IR 2026/705).',
      owner_authorisation: 'The owner\'s signed authorisation of the person carrying out the movement (Art. 4 DR 2026/131; Annex V Part 1 IR 2026/705).',
    },
    notesTitle: 'Notes',
    notes: {
      issuer_third_country: 'The certificate is issued in the third country or territory of dispatch, by its official veterinarian, or by a veterinarian it has authorised whose certificate is then endorsed by its competent authority (Art. 19(a) DR 2026/131). It must be issued or endorsed no more than 10 days before entry into the EU (Art. 19(b)).',
      passport_alternative: 'No certificate is needed for an animal returning with its EU pet passport that shows a valid rabies vaccination and, where required, a favourable titration test done before leaving the EU (Art. 20(b) DR 2026/131), or for an animal with the passport for countries listed in Annex I to IR 2026/636 (Art. 20(a)).',
      old_model_transition: 'A certificate on the old model (Annex IV Part 1 to Implementing Regulation (EU) No 577/2013) issued before 1 October 2026 is accepted until 31 March 2027 (Art. 6(3) IR 2026/705). New certificates use the 2026/705 model.',
      validity_rule: 'Validity as published (note (b)): 10 days from issue (or endorsement) to the checks at entry, extended by the duration of a sea journey; then six months from those checks for onward movement, or until the rabies vaccination expires if earlier. No date was calculated here.',
      authorised_vet_endorsement: 'Signed by an authorised veterinarian: the competent authority of the country of dispatch must endorse the certificate.',
      species_out_of_scope: 'This model covers pet dogs, cats and ferrets only (note (a)). Pet birds have their own model (Annex IV IR 2026/705).',
    },
  },
  de: {
    title: 'Vorausfüllung für die amtliche Bescheinigung — keine Bescheinigung; muss von einer amtlichen/ermächtigten Tierärztin bzw. einem amtlichen/ermächtigten Tierarzt ausgefüllt und unterzeichnet werden',
    notCertificate: 'Muster: Veterinärbescheinigung für Verbringungen von Heimtier-Hunden, -Katzen oder -Frettchen zu nichtkommerziellen Zwecken aus einem Drittland oder Gebiet in einen Mitgliedstaat, Anhang III Teil 1 der Durchführungsverordnung (EU) 2026/705 (Art. 18 Abs. 1 Delegierte Verordnung (EU) 2026/131). Dieses Blatt hat keine Rechtswirkung.',
    nothingSent: 'Es wurde nichts unterzeichnet, bescheinigt oder übermittelt. Jede Zeile in Großbuchstaben in die amtliche Bescheinigung übertragen; die ausstellende Tierärztin / der ausstellende Tierarzt prüft jeden Eintrag am Tier und an den Originaldokumenten.',
    draft: 'ENTWURF — noch nicht tierärztlich freigegeben',
    copy: 'Jede Zeile nach dem Übertragen abhaken.',
    dateFormat: 'Daten wie eingegeben; die Bescheinigung verwendet TT.MM.JJJJ.',
    sections: { owner: 'Eigentümer/in (Feld I.1)', authorised_person: 'Ermächtigte Person (Anhang V Teil 1)', movement: 'Verbringung', animal: 'Tier (Feld I.28)', rabies: 'Tollwutimpfung (II.3)', titration: 'Test zur Titrierung von Tollwutantikörpern (II.3.1)', echinococcus: 'Behandlung gegen Echinococcus multilocularis (II.4, Hunde)', declaration: 'Erklärung zur nichtkommerziellen Verbringung (II.5)', vet: 'Ausstellende Tierärztin / ausstellender Tierarzt' },
    f: {
      'owner.name': 'Name', 'owner.address': 'Anschrift', 'owner.phone': 'Telefon',
      'authorised_person.name': 'Name', 'authorised_person.address': 'Anschrift', 'authorised_person.phone': 'Telefon',
      'movement.dispatch_country': 'Versanddrittland oder -gebiet', 'movement.destination_member_state': 'Erster Bestimmungsmitgliedstaat',
      'animal.species': 'Art (wissenschaftliche Bezeichnung)', 'animal.sex': 'Geschlecht', 'animal.colour': 'Farbe', 'animal.breed': 'Rasse', 'animal.id_code': 'Identifikationsnummer (Transponder oder Tätowierung)',
      'animal.id_system': 'Identifizierungssystem', 'animal.id_location': 'Anbringungsstelle von Transponder oder Tätowierung', 'animal.id_date': 'Datum der Implantierung und/oder der Ablesung',
      'animal.date_of_birth': 'Geburtsdatum (nach Angabe des Eigentümers/der Eigentümerin)', 'animal.name': 'Name des Tieres',
      'rabies.option': 'Beibehaltene Option in II.3.1', 'rabies.vaccination_date': 'Datum der Impfung', 'rabies.vaccine': 'Name des Impfstoffs', 'rabies.manufacturer': 'Hersteller des Impfstoffs', 'rabies.batch': 'Chargennummer',
      'rabies.valid_from': 'Gültigkeitsdauer der Impfung: von', 'rabies.valid_to': 'Gültigkeitsdauer der Impfung: bis',
      'titration.sample_date': 'Datum der Blutentnahme', 'titration.laboratory': 'Labor (laut beigefügtem Bericht)', 'titration.result': 'Ergebnis (laut beigefügtem Bericht)',
      'echinococcus.option': 'Beibehaltene Option in II.4', 'echinococcus.product': 'Name des Mittels', 'echinococcus.manufacturer': 'Hersteller des Mittels', 'echinococcus.date': 'Datum der Behandlung', 'echinococcus.time': 'Uhrzeit der Behandlung', 'echinococcus.administering_vet': 'Behandelnde Tierärztin / behandelnder Tierarzt',
      'declaration.by': 'Erklärung unterzeichnet von',
      'vet.name': 'Name', 'vet.role': 'Funktion',
    },
    missing: 'Fehlt', missingIntro: 'Von der Bescheinigung verlangt, weder im Datensatz noch eingetragen:', optional: 'kein Feld der Bescheinigung', box: 'Feld',
    species: { dog: 'Hund', cat: 'Katze', ferret: 'Frettchen', rabbit: 'Kaninchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'anderes Tier' },
    sex: { female: 'weiblich', male: 'männlich' }, idSystem: { transponder: 'Transponder', tattoo: 'Tätowierung' },
    options: {
      listed_country: 'aus einem in Anhang II der Durchführungsverordnung (EU) 2026/636 gelisteten Land (kein Titrationstest)', titration: 'Test zur Titrierung von Tollwutantikörpern',
      treated: 'gegen Echinococcus multilocularis behandelt', not_treated: 'nicht gegen Echinococcus multilocularis behandelt',
      owner: 'Eigentümer/in', authorised_person: 'vom Eigentümer schriftlich ermächtigte Person',
      official: 'amtliche Tierärztin / amtlicher Tierarzt', authorised: 'von der zuständigen Behörde ermächtigte Tierärztin / ermächtigter Tierarzt',
    },
    leftTitle: 'Bleibt der ausstellenden Tierärztin / dem ausstellenden Tierarzt und den Behörden vorbehalten (nicht vorausgefüllt)',
    left: [
      'Bezugsnummer der Bescheinigung (I.2, II.a): vergibt die zuständige Behörde des Versandlands.',
      'Übrige Felder von Teil I (I.3, I.4, I.6, I.8, I.10–I.27): nach Vorgabe der zuständigen Behörde.',
      'II.1 Anzahl der Tiere und, bei mehr als fünf, der Nachweis zur Veranstaltung.',
      'II.2 klinische Untersuchung („keine Krankheitssymptome … transportfähig am …“): erst nach Untersuchung des Tieres.',
      'Streichen der nicht zutreffenden Optionen (Erläuterung (1)); Ausstellungsdatum; Unterschrift (in anderer Farbe als der Druck) und Stempel.',
      'Sichtvermerk der zuständigen Behörde, wenn eine ermächtigte Tierärztin / ein ermächtigter Tierarzt unterzeichnet.',
      'Feld für den Einreiseort für Reisende: füllt die Kontrollbehörde bei der Einreise in die EU aus.',
    ],
    attachTitle: 'Beizufügen',
    attach: {
      id_vaccination_copy: 'Beglaubigte Kopie der Angaben zur Identifizierung und zur Impfung (Erläuterung (4)).',
      lab_report: 'Beglaubigte Kopie des offiziellen Berichts des benannten Labors über den Tollwut-Antikörpertest (Erläuterung (6)).',
      non_commercial_declaration: 'Schriftliche Erklärung, dass die Verbringung nichtkommerziell ist, unterzeichnet von Eigentümer/in oder ermächtigter Person (Art. 18 Abs. 3 DelVO 2026/131; Anhang V Teil 2 DVO 2026/705).',
      owner_authorisation: 'Unterzeichnete Ermächtigung der Person, die die Verbringung durchführt (Art. 4 DelVO 2026/131; Anhang V Teil 1 DVO 2026/705).',
    },
    notesTitle: 'Hinweise',
    notes: {
      issuer_third_country: 'Die Bescheinigung wird im Versanddrittland oder -gebiet ausgestellt: von dessen amtlicher Tierärztin / amtlichem Tierarzt oder von einer dort ermächtigten Tierärztin / einem dort ermächtigten Tierarzt mit anschließendem Sichtvermerk der zuständigen Behörde (Art. 19 Buchst. a DelVO 2026/131). Ausstellung oder Sichtvermerk höchstens 10 Tage vor der Einreise in die EU (Art. 19 Buchst. b).',
      passport_alternative: 'Keine Bescheinigung nötig für ein Tier, das mit seinem EU-Heimtierausweis zurückkehrt, der eine gültige Tollwutimpfung und, wo verlangt, einen vor Verlassen der EU durchgeführten Titrationstest mit günstigem Ergebnis ausweist (Art. 20 Buchst. b DelVO 2026/131), oder für ein Tier mit dem Ausweis für die in Anhang I der DVO 2026/636 gelisteten Länder (Art. 20 Buchst. a).',
      old_model_transition: 'Eine Bescheinigung nach dem alten Muster (Anhang IV Teil 1 der Durchführungsverordnung (EU) Nr. 577/2013), ausgestellt vor dem 1. Oktober 2026, wird bis 31. März 2027 anerkannt (Art. 6 Abs. 3 DVO 2026/705). Neue Bescheinigungen folgen dem Muster 2026/705.',
      validity_rule: 'Gültigkeit wie veröffentlicht (Erläuterung (b)): 10 Tage ab Ausstellung (bzw. Sichtvermerk) bis zur Kontrolle bei der Einreise, verlängert um die Dauer einer Seereise; danach sechs Monate ab dieser Kontrolle für die Weiterreise, oder bis zum Ablauf der Tollwutimpfung, falls früher. Hier wurde kein Datum berechnet.',
      authorised_vet_endorsement: 'Unterzeichnet eine ermächtigte Tierärztin / ein ermächtigter Tierarzt, muss die zuständige Behörde des Versandlands den Sichtvermerk anbringen.',
      species_out_of_scope: 'Dieses Muster gilt nur für Hunde, Katzen und Frettchen (Erläuterung (a)). Für Heimvögel gilt ein eigenes Muster (Anhang IV DVO 2026/705).',
    },
  },
  it: {
    title: 'Precompilazione per il certificato ufficiale — non è un certificato; deve essere completato e firmato da un veterinario ufficiale/autorizzato',
    notCertificate: 'Modello: certificato sanitario per i movimenti a carattere non commerciale di cani, gatti o furetti da compagnia introdotti in uno Stato membro da un paese terzo o territorio, allegato III parte 1 del regolamento di esecuzione (UE) 2026/705 (art. 18, par. 1, regolamento delegato (UE) 2026/131). Questo foglio non ha valore legale.',
    nothingSent: 'Nulla è stato firmato, certificato o inviato. Trascrivere ogni riga nel certificato ufficiale in stampatello; il veterinario che lo rilascia verifica ogni dato sull\'animale e sui documenti originali.',
    draft: 'BOZZA — non ancora approvata dal veterinario',
    copy: 'Spuntare ogni riga una volta trascritta.',
    dateFormat: 'Date come inserite; il certificato usa gg/mm/aaaa.',
    sections: { owner: 'Proprietario (casella I.1)', authorised_person: 'Persona autorizzata (allegato V parte 1)', movement: 'Movimento', animal: 'Animale (casella I.28)', rabies: 'Vaccinazione antirabbica (II.3)', titration: 'Prova di titolazione degli anticorpi per la rabbia (II.3.1)', echinococcus: 'Trattamento contro l\'Echinococcus multilocularis (II.4, cani)', declaration: 'Dichiarazione di movimento non commerciale (II.5)', vet: 'Veterinario che rilascia il certificato' },
    f: {
      'owner.name': 'Nome', 'owner.address': 'Indirizzo', 'owner.phone': 'Telefono',
      'authorised_person.name': 'Nome', 'authorised_person.address': 'Indirizzo', 'authorised_person.phone': 'Telefono',
      'movement.dispatch_country': 'Paese terzo o territorio di spedizione', 'movement.destination_member_state': 'Stato membro di prima destinazione',
      'animal.species': 'Specie (nome scientifico)', 'animal.sex': 'Sesso', 'animal.colour': 'Colore', 'animal.breed': 'Razza', 'animal.id_code': 'Numero di identificazione (transponder o tatuaggio)',
      'animal.id_system': 'Sistema di identificazione', 'animal.id_location': 'Sede del transponder o del tatuaggio', 'animal.id_date': 'Data di impianto e/o di lettura',
      'animal.date_of_birth': 'Data di nascita (dichiarata dal proprietario)', 'animal.name': 'Nome dell\'animale',
      'rabies.option': 'Opzione mantenuta al punto II.3.1', 'rabies.vaccination_date': 'Data della vaccinazione', 'rabies.vaccine': 'Nome del vaccino', 'rabies.manufacturer': 'Fabbricante del vaccino', 'rabies.batch': 'Numero del lotto',
      'rabies.valid_from': 'Validità della vaccinazione: dal', 'rabies.valid_to': 'Validità della vaccinazione: al',
      'titration.sample_date': 'Data del prelievo del campione di sangue', 'titration.laboratory': 'Laboratorio (dal rapporto allegato)', 'titration.result': 'Risultato (dal rapporto allegato)',
      'echinococcus.option': 'Opzione mantenuta al punto II.4', 'echinococcus.product': 'Nome del prodotto', 'echinococcus.manufacturer': 'Fabbricante del prodotto', 'echinococcus.date': 'Data del trattamento', 'echinococcus.time': 'Ora del trattamento', 'echinococcus.administering_vet': 'Veterinario incaricato',
      'declaration.by': 'Dichiarazione firmata da',
      'vet.name': 'Nome e cognome', 'vet.role': 'Qualifica',
    },
    missing: 'Mancante', missingIntro: 'Richiesto dal certificato, non presente nella cartella e non inserito:', optional: 'non è una casella del certificato', box: 'casella',
    species: { dog: 'cane', cat: 'gatto', ferret: 'furetto', rabbit: 'coniglio', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' },
    sex: { female: 'femmina', male: 'maschio' }, idSystem: { transponder: 'transponder', tattoo: 'tatuaggio' },
    options: {
      listed_country: 'da un paese elencato nell\'allegato II del regolamento di esecuzione (UE) 2026/636 (senza titolazione)', titration: 'prova di titolazione degli anticorpi per la rabbia',
      treated: 'trattato contro l\'Echinococcus multilocularis', not_treated: 'non trattato contro l\'Echinococcus multilocularis',
      owner: 'il proprietario', authorised_person: 'la persona autorizzata per iscritto dal proprietario',
      official: 'veterinario ufficiale', authorised: 'veterinario autorizzato dall\'autorità competente',
    },
    leftTitle: 'Riservato al veterinario che rilascia il certificato e alle autorità (non precompilato)',
    left: [
      'Numero di riferimento del certificato (I.2, II.a): assegnato dall\'autorità competente del paese di spedizione.',
      'Altre caselle della parte I (I.3, I.4, I.6, I.8, I.10–I.27): secondo le indicazioni dell\'autorità competente.',
      'II.1 numero di animali e, se più di cinque, le prove relative all\'evento.',
      'II.2 esame clinico («non presentano sintomi di malattie e sono idonei … in data …»): solo dopo la visita dell\'animale.',
      'Cancellazione delle diciture non pertinenti (nota (1)); data di rilascio; firma (di colore diverso dalla stampa) e timbro.',
      'Visto dell\'autorità competente, se firma un veterinario autorizzato.',
      'Riquadro del punto di entrata dei viaggiatori: compilato dal funzionario all\'ingresso nell\'UE.',
    ],
    attachTitle: 'Da allegare',
    attach: {
      id_vaccination_copy: 'Copia certificata dei dati di identificazione e di vaccinazione (nota (4)).',
      lab_report: 'Copia certificata del rapporto ufficiale del laboratorio designato sulla prova degli anticorpi per la rabbia (nota (6)).',
      non_commercial_declaration: 'Dichiarazione scritta che il movimento non è commerciale, firmata dal proprietario o dalla persona autorizzata (art. 18, par. 3, reg. del. 2026/131; allegato V parte 2 reg. es. 2026/705).',
      owner_authorisation: 'Autorizzazione firmata dal proprietario per la persona che effettua il movimento (art. 4 reg. del. 2026/131; allegato V parte 1 reg. es. 2026/705).',
    },
    notesTitle: 'Note',
    notes: {
      issuer_third_country: 'Il certificato è rilasciato nel paese terzo o territorio di spedizione, dal suo veterinario ufficiale o da un veterinario da esso autorizzato con successivo visto dell\'autorità competente (art. 19, lett. a, reg. del. 2026/131), non più di 10 giorni prima dell\'ingresso nell\'UE (art. 19, lett. b).',
      passport_alternative: 'Il certificato non serve per un animale che rientra con il proprio passaporto UE che riporta una vaccinazione antirabbica valida e, se richiesta, una titolazione favorevole eseguita prima di lasciare l\'UE (art. 20, lett. b, reg. del. 2026/131), né per un animale con il passaporto per i paesi elencati nell\'allegato I del reg. es. 2026/636 (art. 20, lett. a).',
      old_model_transition: 'Un certificato secondo il vecchio modello (allegato IV parte 1 del regolamento di esecuzione (UE) n. 577/2013) rilasciato prima del 1º ottobre 2026 è accettato fino al 31 marzo 2027 (art. 6, par. 3, reg. es. 2026/705). I nuovi certificati seguono il modello 2026/705.',
      validity_rule: 'Validità come pubblicata (nota b): 10 giorni dal rilascio (o dal visto) fino ai controlli all\'ingresso, prorogati della durata di un viaggio via mare; poi sei mesi da tali controlli per gli ulteriori movimenti, o fino alla scadenza della vaccinazione antirabbica se anteriore. Nessuna data è stata calcolata qui.',
      authorised_vet_endorsement: 'Se firma un veterinario autorizzato, l\'autorità competente del paese di spedizione deve apporre il visto.',
      species_out_of_scope: 'Questo modello riguarda solo cani, gatti e furetti (nota a). Gli uccelli da compagnia hanno un modello proprio (allegato IV reg. es. 2026/705).',
    },
  },
};

const SECTION_OF = (k: TravelFieldKey) => k.split('.')[0] as Section;

function show(f: TravelField, t: Labels): string {
  const v = f.value!.value;
  if (f.key === 'animal.species') return SCI[v] ? `${t.species[v]} (${SCI[v]})` : (t.species[v] ?? v);
  if (f.key === 'animal.sex') return t.sex[v] ?? v;
  if (f.key === 'animal.id_system') return t.idSystem[v] ?? v;
  if (f.key === 'rabies.option' || f.key === 'echinococcus.option' || f.key === 'declaration.by' || f.key === 'vet.role') return t.options[v] ?? v;
  return v;
}

/** The transcription checklist in EN, DE or IT. */
export function renderTravelCertificate(pack: TravelCertificatePack, lang: Lang = 'en'): string {
  const t = T[lang] ?? T.en;
  const out: string[] = [];
  out.push(`# ${t.title}`);
  if (!pack.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${t.nothingSent}**`);
  out.push('');
  out.push(t.notCertificate);
  out.push('');
  out.push(`_${t.copy} ${t.dateFormat}_`);

  let section = '';
  for (const f of pack.fields) {
    const sec = SECTION_OF(f.key);
    if (sec !== section) {
      section = sec;
      out.push('');
      out.push(`## ${t.sections[sec]}`);
    }
    const where = f.box.startsWith('—') ? t.optional : `${t.box} ${f.box}`;
    const label = `${t.f[f.key]} (${where})`;
    if (f.value) out.push(`- [ ] ${label}: ${show(f, t)}`);
    else if (f.required) out.push(`- [ ] ${label}: ▲ ${t.missing}`);
    else out.push(`- [ ] ${label}: —`);
  }

  out.push('');
  out.push(`## ${t.attachTitle}`);
  for (const a of pack.attachments) out.push(`- [ ] ${t.attach[a]}`);

  out.push('');
  out.push(`## ${t.leftTitle}`);
  for (const l of t.left) out.push(`- ${l}`);

  out.push('');
  out.push(`## ${t.notesTitle}`);
  for (const n of pack.notes) out.push(`- ${t.notes[n]}`);

  if (pack.missing.length) {
    out.push('');
    out.push(`## ▲ ${t.missing}`);
    out.push(t.missingIntro);
    for (const k of pack.missing) out.push(`- ${t.sections[SECTION_OF(k)]}: ${t.f[k]}`);
  }
  return out.join('\n');
}
