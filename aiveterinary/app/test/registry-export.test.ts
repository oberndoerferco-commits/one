import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { VisitContext } from '../src/country.js';
import { buildRegistryEntry, renderRegistryEntry, type RegistryOpts } from '../src/registry-export.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

// 010: Bruno, Beagle, male, 2 years, neutered; DHPPi + Lepto vaccine performed
const { record, header } = prep('010-vaccination-visit');
const ctxAT = VisitContext.parse({ country: 'AT', microchip: '040098100123456', owner: { name: 'Eva Gruber' }, author: { name: 'Dr. Paul Hofer', registration: 'ÖTK 1234' } });
const ctxIT = VisitContext.parse({ country: 'IT', microchip: '380260000123456', owner: { name: 'Rossi Maria', tax_id: 'RSSMRA80A41H501U' }, author: { name: 'Dott.ssa Giulia Bianchi', registration: 'Ordine UD 567' } });

const atFirst: RegistryOpts = {
  approved: true,
  event: 'first_registration',
  event_date: '2026-10-20',
  animal: { chip_type: 'ISO', date_of_birth: '2024', country_of_birth: 'Österreich' },
  owner: {
    id_document_type: 'Reisepass', id_document_number: 'P1234567', address: 'Hauptstraße 1, 8010 Graz', contact: '+43 660 1234567',
    date_of_birth: '1985-04-02', keeping_since: '2024-08-01', competence_certificate: 'Kursbestätigung Stmk 2026-07-10',
  },
};
const itFirst: RegistryOpts = {
  approved: true,
  event: 'first_registration',
  event_date: '2026-10-20',
  origin: 'acquisition',
  animal: { date_of_birth: '2024-06-01', size: 'media', coat: 'tricolore' },
  owner: { address: 'Via Roma 1, 33100 Udine' },
};

const roots = (opts: RegistryOpts, ctx: VisitContext) => ({ header, record, ctx, opts });
const resolve = (source: string, r: Record<string, unknown>) => source.split('.').reduce<unknown>((o, k) => (o as Record<string, unknown>)?.[k], r);

describe('registry entry: every value traceable', () => {
  it.each([
    ['AT-HDB', atFirst, ctxAT],
    ['IT-SINAC', itFirst, ctxIT],
  ] as const)('%s first registration: each value equals what its source path holds', (registry, opts, ctx) => {
    const e = buildRegistryEntry(record, header, ctx, opts, registry);
    const filled = e.fields.filter((f) => f.value);
    expect(filled.length).toBeGreaterThan(10);
    for (const f of filled) expect(resolve(f.value!.source, roots(opts, ctx)), `${f.key} <- ${f.value!.source}`).toEqual(f.value!.value);
  });

  it('signalment from the header, chip / owner / vet from the context, the rest from what the vet typed', () => {
    const e = buildRegistryEntry(record, header, ctxAT, atFirst, 'AT-HDB');
    const get = (k: string) => e.fields.find((f) => f.key === k)?.value;
    expect(get('animal.breed')).toEqual({ value: 'Beagle', source: 'header.breed' });
    expect(get('animal.sex')).toEqual({ value: 'male', source: 'header.sex' });
    expect(get('animal.microchip')).toEqual({ value: '040098100123456', source: 'ctx.microchip' });
    expect(get('owner.name')).toEqual({ value: 'Eva Gruber', source: 'ctx.owner.name' });
    expect(get('vet.name')).toEqual({ value: 'Dr. Paul Hofer', source: 'ctx.author.name' });
    expect(get('animal.date_of_birth')).toEqual({ value: '2024', source: 'opts.animal.date_of_birth' });
    expect(get('event.date')).toEqual({ value: '2026-10-20', source: 'opts.event_date' });
  });

  it('a complete AT dog registration and a complete IT one have nothing missing; never submitted', () => {
    const at = buildRegistryEntry(record, header, ctxAT, atFirst, 'AT-HDB');
    const it_ = buildRegistryEntry(record, header, ctxIT, itFirst, 'IT-SINAC');
    expect(at.missing).toEqual([]);
    expect(it_.missing).toEqual([]);
    expect(at.submitted).toBe(false);
    expect(at.notes).toContain('at_vet_first_chipping');
    expect(it_.notes).toContain('it_regional_rules');
  });
});

describe('registry entry: absent means null and listed', () => {
  it('AT first registration with only the visit context lists every § 24a field nobody typed', () => {
    const e = buildRegistryEntry(record, header, VisitContext.parse({ country: 'AT' }), { event: 'first_registration' }, 'AT-HDB');
    expect(e.missing).toEqual([
      'animal.microchip', 'animal.chip_type', 'animal.date_of_birth', 'animal.country_of_birth',
      'owner.name', 'owner.id_document_type', 'owner.id_document_number', 'owner.address', 'owner.contact', 'owner.date_of_birth', 'owner.keeping_since', 'owner.competence_certificate',
      'event.date', 'vet.name',
    ]);
    // optional fields are null but not "missing"
    expect(e.fields.find((f) => f.key === 'animal.pet_passport')?.value).toBeNull();
    expect(e.missing).not.toContain('animal.pet_passport');
    expect(e.approved).toBe(false);
  });

  it('IT change of owner needs both people and their tax codes', () => {
    const e = buildRegistryEntry(record, header, ctxIT, { event: 'change_of_owner', event_date: '2026-10-21', new_owner: { name: 'Verdi Luca' } }, 'IT-SINAC');
    expect(e.missing).toEqual(['new_owner.tax_id', 'new_owner.address']);
  });

  it('AT change of owner needs the current registration number and the new keeper\'s photo ID', () => {
    const e = buildRegistryEntry(record, header, ctxAT, { event: 'change_of_owner', event_date: '2026-10-21', animal: { chip_type: 'ISO' }, new_owner: { name: 'Karl Berger' } }, 'AT-HDB');
    expect(e.missing).toEqual(['animal.registration_number', 'new_owner.id_document_type', 'new_owner.id_document_number']);
    expect(e.notes).toContain('at_new_registration_number');
  });

  it('IT loss: the police report becomes required only when the vet marks a theft', () => {
    const loss = { event: 'loss', event_date: '2026-10-22', loss: { place: 'Tarcento' } } as const;
    expect(buildRegistryEntry(record, header, ctxIT, loss, 'IT-SINAC').missing).toEqual([]);
    const theft = buildRegistryEntry(record, header, ctxIT, { ...loss, loss: { place: 'Tarcento', theft: true } }, 'IT-SINAC');
    expect(theft.missing).toEqual(['event.police_report']);
  });

  it('AT loss: the entry says the registry has no loss field', () => {
    const e = buildRegistryEntry(record, header, ctxAT, { event: 'loss', event_date: '2026-10-22' }, 'AT-HDB');
    expect(e.notes).toContain('at_loss_no_field');
    expect(e.missing).toEqual(['animal.chip_type', 'owner.contact']);
  });
});

describe('registry entry: no inference', () => {
  it('no date of birth from the age, no neutering date from the neuter status', () => {
    const e = buildRegistryEntry(record, header, ctxAT, { event: 'first_registration' }, 'AT-HDB');
    expect(header.age).toEqual({ value: 2, unit: 'year' });
    expect(e.fields.find((f) => f.key === 'animal.date_of_birth')?.value).toBeNull();
    expect(e.missing).toContain('animal.date_of_birth');
    expect(e.fields.find((f) => f.key === 'animal.neutering_date')?.value).toBeNull();
    const md = renderRegistryEntry(e, 'de');
    expect(md).not.toMatch(/2024/);
  });

  it('no breed guessing: missing breed stays missing even when the notes look like a breed', () => {
    const r = structuredClone(record);
    r.history.push({ finding: 'description', value: 'looks like a Beagle mix', source_role: 'owner_reported', source_spans: [[0, 5]] });
    const e = buildRegistryEntry(r, { name: 'Bruno', species: 'dog' }, ctxAT, atFirst, 'AT-HDB');
    expect(e.fields.find((f) => f.key === 'animal.breed')?.value).toBeNull();
    expect(e.fields.find((f) => f.key === 'animal.sex')?.value).toBeNull();
    expect(e.missing).toEqual(['animal.breed', 'animal.sex']);
  });

  it('record signalment fills in only when the header lacks it, with its own source', () => {
    const r = structuredClone(record); r.patient.breed = 'Beagle';
    const e = buildRegistryEntry(r, { name: 'Bruno', species: 'dog' }, ctxAT, atFirst, 'AT-HDB');
    expect(e.fields.find((f) => f.key === 'animal.breed')?.value).toEqual({ value: 'Beagle', source: 'record.patient.breed' });
  });

  it('no rabies date from a vaccination in the record, no intervention from a procedure', () => {
    const r = structuredClone(record);
    r.medications.push({ drug: 'Rabies vaccine', class_as_written: null, dose: null, dose_unit: null, route: 's.c.', frequency: null, duration: null, status: 'performed', source_spans: [[0, 5]] });
    r.treatments.push({ type: 'procedure', text: 'tail amputation', status: 'performed', source_spans: [[0, 5]] });
    const e = buildRegistryEntry(r, header, ctxAT, atFirst, 'AT-HDB');
    for (const k of ['animal.rabies_vaccination_date', 'animal.rabies_vaccine', 'animal.interventions']) expect(e.fields.find((f) => f.key === k)?.value).toBeNull();
    const md = renderRegistryEntry(e, 'de');
    expect(md).not.toContain('Rabies vaccine');
    expect(md).not.toContain('tail amputation');
  });

  it('deadlines are printed as rules, never as computed dates', () => {
    const e = buildRegistryEntry(record, header, ctxIT, { event: 'loss', event_date: '2026-10-22', loss: { place: 'Udine' } }, 'IT-SINAC');
    const md = renderRegistryEntry(e, 'it');
    expect(md).toContain('entro quarantotto ore');
    expect(md).not.toContain('2026-10-24');
    expect(md.match(/2026-10-\d\d/g)).toEqual(['2026-10-22']);
  });

  it('species outside the registry\'s scope is flagged, not filtered', () => {
    const cat = prep('003-gatto-inappetenza-it');
    const e = buildRegistryEntry(cat.record, cat.header, ctxAT, atFirst, 'AT-HDB');
    expect(e.notes).toContain('at_cat_breeding_only');
    expect(buildRegistryEntry(cat.record, cat.header, ctxIT, itFirst, 'IT-SINAC').notes).toContain('it_species_scope');
    expect(buildRegistryEntry(record, header, ctxIT, atFirst, 'AT-HDB').notes).toContain('country_mismatch');
  });
});

describe('registry checklist in three languages', () => {
  const at = buildRegistryEntry(record, header, ctxAT, atFirst, 'AT-HDB');
  const it_ = buildRegistryEntry(record, header, ctxIT, itFirst, 'IT-SINAC');

  it('AT defaults to German, IT to Italian; both say nothing was sent', () => {
    const de = renderRegistryEntry(at);
    expect(de.split('\n')[0]).toBe('# Daten für die Eintragung in die Heimtierdatenbank');
    expect(de).toContain('Es wurde nichts an ein Register übermittelt');
    expect(de).toContain('- [ ] Rasse: Beagle');
    expect(de).toContain('- [ ] Geschlecht: männlich');
    expect(de).toContain('- [ ] Chiptyp: ISO');
    expect(de).toContain('Binnen eines Monats nach Kennzeichnung');
    const itMd = renderRegistryEntry(it_);
    expect(itMd.split('\n')[0]).toBe('# Dati da inserire in anagrafe (SINAC)');
    expect(itMd).toContain('Nulla è stato inviato');
    expect(itMd).toContain('- [ ] Codice fiscale: RSSMRA80A41H501U');
    expect(itMd).toContain('- [ ] Provenienza: acquisizione');
    expect(itMd).toContain('entro sessanta giorni dalla nascita');
  });

  it.each([
    ['en', 'Data to enter in the Austrian Heimtierdatenbank', 'Nothing was sent to any registry', '- [ ] Breed: Beagle'],
    ['de', 'Daten für die Eintragung in die Heimtierdatenbank', 'Es wurde nichts an ein Register übermittelt', '- [ ] Rasse: Beagle'],
    ['it', 'Dati da inserire nella Heimtierdatenbank austriaca', 'Nulla è stato inviato', '- [ ] Razza: Beagle'],
  ] as const)('%s: heading, not-sent notice, values verbatim', (lang, title, sent, breed) => {
    const md = renderRegistryEntry(at, lang);
    expect(md.split('\n')[0]).toBe(`# ${title}`);
    expect(md).toContain(sent);
    expect(md).toContain(breed);
    expect(md).toContain('Hauptstraße 1, 8010 Graz');
    expect(md).not.toMatch(/ENTWURF|DRAFT|BOZZA/);
  });

  it('missing fields are flagged inline and listed, in the checklist language; drafts say so', () => {
    const bare = buildRegistryEntry(record, header, VisitContext.parse({ country: 'IT' }), { event: 'first_registration' }, 'IT-SINAC');
    const md = renderRegistryEntry(bare, 'it');
    expect(md).toContain('BOZZA');
    expect(md).toContain('- [ ] Codice microchip: ▲ Mancante');
    expect(md).toContain('## ▲ Mancante');
    expect(md).toContain('- Proprietario / detentore: Codice fiscale');
    expect(renderRegistryEntry(bare, 'en')).toContain('- [ ] Microchip number: ▲ Missing');
  });
});
