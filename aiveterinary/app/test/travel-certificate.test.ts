import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { VisitContext } from '../src/country.js';
import { buildTravelCertificate, renderTravelCertificate, type TravelOpts } from '../src/travel-certificate.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record) }; };

// 010: Bruno, Beagle, male, 2 years, neutered; DHPPi + Lepto vaccine performed (no rabies vaccine in the record)
const { record, header } = prep('010-vaccination-visit');
const ctx = VisitContext.parse({
  country: 'CH',
  microchip: '756098100123456',
  owner: { name: 'Anna Keller' },
  author: { name: 'Dr. Lukas Meier' },
  dispensings: [{ medication_index: 0, product: 'Rabisin', batch: 'L12345', valid_until: '2029-05-01' }],
});

const full: TravelOpts = {
  approved: true,
  owner: { address: 'Bahnhofstrasse 1, 8001 Zürich', phone: '+41 79 123 45 67' },
  declaration_by: 'owner',
  dispatch_country: 'Switzerland',
  destination_member_state: 'Ireland',
  animal: { colour: 'tricolour', date_of_birth: '2024-03-15', id_system: 'transponder', id_location: 'left side of the neck', id_date: '2024-06-01' },
  rabies: { dispensing_index: 0, vaccination_date: '2026-05-01', manufacturer: 'Boehringer Ingelheim', valid_from: '2026-05-22' },
  rabies_option: 'listed_country',
  echinococcus_option: 'treated',
  echinococcus: { product: 'Droncit', manufacturer: 'Elanco', date: '2026-10-21', time: '09:30', administering_vet: 'Dr. Lukas Meier' },
  vet_role: 'authorised',
};

const roots = (opts: TravelOpts, c: VisitContext = ctx) => ({ header, record, ctx: c, opts });
const resolve = (source: string, r: Record<string, unknown>) => source.split('.').reduce<unknown>((o, k) => (o as Record<string, unknown>)?.[k], r);

describe('travel certificate pre-fill: every value traceable', () => {
  it('each filled value equals what its source path holds', () => {
    const p = buildTravelCertificate(record, header, ctx, full);
    const filled = p.fields.filter((f) => f.value);
    expect(filled.length).toBeGreaterThan(25);
    for (const f of filled) expect(resolve(f.value!.source, roots(full)), `${f.key} <- ${f.value!.source}`).toEqual(f.value!.value);
  });

  it('signalment from the header, chip / owner / vet from the context, vaccine from the dispensing line the vet points at', () => {
    const p = buildTravelCertificate(record, header, ctx, full);
    const get = (k: string) => p.fields.find((f) => f.key === k)?.value;
    expect(get('animal.species')).toEqual({ value: 'dog', source: 'header.species' });
    expect(get('animal.breed')).toEqual({ value: 'Beagle', source: 'header.breed' });
    expect(get('animal.sex')).toEqual({ value: 'male', source: 'header.sex' });
    expect(get('animal.id_code')).toEqual({ value: '756098100123456', source: 'ctx.microchip' });
    expect(get('owner.name')).toEqual({ value: 'Anna Keller', source: 'ctx.owner.name' });
    expect(get('vet.name')).toEqual({ value: 'Dr. Lukas Meier', source: 'ctx.author.name' });
    expect(get('rabies.vaccine')).toEqual({ value: 'Rabisin', source: 'ctx.dispensings.0.product' });
    expect(get('rabies.batch')).toEqual({ value: 'L12345', source: 'ctx.dispensings.0.batch' });
    expect(get('rabies.valid_to')).toEqual({ value: '2029-05-01', source: 'ctx.dispensings.0.valid_until' });
    expect(get('rabies.vaccination_date')).toEqual({ value: '2026-05-01', source: 'opts.rabies.vaccination_date' });
  });

  it('a value typed at this step wins over the visit\'s dispensing line', () => {
    const p = buildTravelCertificate(record, header, ctx, { ...full, rabies: { ...full.rabies, batch: 'X999' } });
    expect(p.fields.find((f) => f.key === 'rabies.batch')?.value).toEqual({ value: 'X999', source: 'opts.rabies.batch' });
  });

  it('complete pre-fill has nothing missing; never signed or sent; attachments and notes listed', () => {
    const p = buildTravelCertificate(record, header, ctx, full);
    expect(p.missing).toEqual([]);
    expect(p.signed).toBe(false);
    expect(p.sent).toBe(false);
    expect(p.model).toBe('EU 2026/705 Annex III');
    expect(p.attachments).toEqual(['id_vaccination_copy', 'non_commercial_declaration']);
    expect(p.notes).toEqual(expect.arrayContaining(['issuer_third_country', 'passport_alternative', 'old_model_transition', 'validity_rule', 'authorised_vet_endorsement']));
  });
});

describe('travel certificate pre-fill: absent means null and listed', () => {
  it('with only the header and an empty context, every identification and vaccination field is missing', () => {
    const p = buildTravelCertificate(record, header, VisitContext.parse({ country: 'DE' }));
    expect(p.missing).toEqual([
      'owner.name', 'owner.address', 'owner.phone',
      'movement.dispatch_country', 'movement.destination_member_state',
      'animal.colour', 'animal.id_code', 'animal.id_system', 'animal.id_location', 'animal.id_date', 'animal.date_of_birth',
      'rabies.option', 'rabies.vaccination_date', 'rabies.vaccine', 'rabies.manufacturer', 'rabies.batch', 'rabies.valid_from', 'rabies.valid_to',
      'echinococcus.option',
      'declaration.by',
      'vet.name', 'vet.role',
    ]);
    expect(p.approved).toBe(false);
    // the animal's name is no box on the model: null but not missing
    expect(p.missing).not.toContain('animal.name');
  });

  it('titration option makes the sampling date required and asks for the lab report; lab and result stay optional', () => {
    const p = buildTravelCertificate(record, header, ctx, { ...full, rabies_option: 'titration' });
    expect(p.missing).toEqual(['titration.sample_date']);
    expect(p.attachments).toContain('lab_report');
    const ok = buildTravelCertificate(record, header, ctx, { ...full, rabies_option: 'titration', titration: { sample_date: '2026-06-15' } });
    expect(ok.missing).toEqual([]);
  });

  it('Echinococcus "treated" needs the treatment details; "not treated" does not', () => {
    const treated = buildTravelCertificate(record, header, ctx, { ...full, echinococcus: {} });
    expect(treated.missing).toEqual(['echinococcus.product', 'echinococcus.manufacturer', 'echinococcus.date', 'echinococcus.time', 'echinococcus.administering_vet']);
    const not = buildTravelCertificate(record, header, ctx, { ...full, echinococcus_option: 'not_treated', echinococcus: {} });
    expect(not.missing).toEqual([]);
  });

  it('a cat has no Echinococcus section; an authorised person must be named and authorised in writing', () => {
    const cat = PatientHeader.parse({ ...header, species: 'cat', breed: 'European Shorthair' });
    const p = buildTravelCertificate(record, cat, ctx, { ...full, echinococcus_option: undefined, echinococcus: undefined, declaration_by: 'authorised_person' });
    expect(p.fields.some((f) => f.key.startsWith('echinococcus.'))).toBe(false);
    expect(p.missing).toEqual(['authorised_person.name']);
    expect(p.attachments).toContain('owner_authorisation');
  });

  it('a species outside dogs, cats and ferrets is flagged, not refused', () => {
    const rabbit = PatientHeader.parse({ ...header, species: 'rabbit' });
    expect(buildTravelCertificate(record, rabbit, ctx, full).notes).toContain('species_out_of_scope');
  });

  it('a dispensing index that points nowhere fills nothing', () => {
    const p = buildTravelCertificate(record, header, ctx, { ...full, rabies: { ...full.rabies, dispensing_index: 5 } });
    expect(p.missing).toEqual(expect.arrayContaining(['rabies.vaccine', 'rabies.batch', 'rabies.valid_to']));
  });
});

describe('travel certificate pre-fill: no inference', () => {
  const isoDates = (s: string) => new Set(s.match(/\b\d{4}-\d{2}-\d{2}\b|\b\d{2}[./]\d{2}[./]\d{4}\b/g) ?? []);

  it('no date of birth from the age, no colour, no option chosen, no vaccine picked out of the record', () => {
    expect(header.age).toEqual({ value: 2, unit: 'year' });
    expect(record.medications.length).toBeGreaterThan(0);
    const p = buildTravelCertificate(record, header, VisitContext.parse({ country: 'AT', microchip: '040098100123456' }), {});
    const get = (k: string) => p.fields.find((f) => f.key === k)?.value;
    for (const k of ['animal.date_of_birth', 'animal.colour', 'animal.id_system', 'rabies.option', 'echinococcus.option', 'rabies.vaccine', 'rabies.batch', 'rabies.vaccination_date']) {
      expect(get(k), k).toBeNull();
    }
    expect(renderTravelCertificate(p, 'en')).not.toMatch(/2024/);
  });

  it('no validity start / end computed from the vaccination date, no 21-day or 24–120 h dates: every rendered date was typed', () => {
    const opts: TravelOpts = { ...full, rabies: { vaccination_date: '2026-05-01' }, echinococcus: { date: '2026-10-21' } };
    const p = buildTravelCertificate(record, header, VisitContext.parse({ country: 'IT' }), opts);
    expect(p.fields.find((f) => f.key === 'rabies.valid_from')?.value).toBeNull();
    expect(p.fields.find((f) => f.key === 'rabies.valid_to')?.value).toBeNull();
    expect(p.missing).toEqual(expect.arrayContaining(['rabies.valid_from', 'rabies.valid_to']));
    const typed = new Set(['2026-05-01', '2026-10-21', '2024-03-15', '2024-06-01']);
    for (const lang of ['en', 'de', 'it'] as const) {
      const md = renderTravelCertificate(p, lang);
      for (const d of isoDates(md)) expect(typed.has(d), `${lang}: ${d} was not typed`).toBe(true);
      expect(md).not.toMatch(/2026-05-22|2027-05-01|2029/); // vaccination + 21 days / + 1 year / + 3 years
      expect(md).not.toMatch(/eligible|may travel|darf reisen|può viaggiare|idoneo a viaggiare/i);
    }
  });
});

describe('travel certificate pre-fill: three languages', () => {
  const p = buildTravelCertificate(record, header, ctx, { ...full, approved: false, rabies_option: undefined });

  it.each([
    ['en', 'Pre-fill for the official certificate — not a certificate; must be completed and signed by an official/authorised veterinarian', 'Nothing was signed, certified or sent', 'Canis lupus familiaris', 'Batch number (box II.3): L12345', 'Missing'],
    ['de', 'Vorausfüllung für die amtliche Bescheinigung — keine Bescheinigung', 'Es wurde nichts unterzeichnet, bescheinigt oder übermittelt', 'Hund (Canis lupus familiaris)', 'Chargennummer (Feld II.3): L12345', 'Fehlt'],
    ['it', 'Precompilazione per il certificato ufficiale — non è un certificato', 'Nulla è stato firmato, certificato o inviato', 'cane (Canis lupus familiaris)', 'Numero del lotto (casella II.3): L12345', 'Mancante'],
  ] as const)('%s', (lang, title, nothing, species, batch, missing) => {
    const md = renderTravelCertificate(p, lang);
    expect(md.startsWith(`# ${title}`)).toBe(true);
    expect(md).toContain(nothing);
    expect(md).toContain(species);
    expect(md).toContain(batch);
    expect(md).toContain(`## ▲ ${missing}`);
    expect(md).toContain('2026/705');
    expect(md).toContain('Rabisin');
  });

  it('the draft marker shows until the vet approves', () => {
    expect(renderTravelCertificate(p, 'en')).toContain('DRAFT');
    expect(renderTravelCertificate(buildTravelCertificate(record, header, ctx, full), 'en')).not.toContain('DRAFT');
  });
});
