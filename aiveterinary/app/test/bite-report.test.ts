import { describe, it, expect } from 'vitest';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { VisitContext } from '../src/country.js';
import { buildBiteReport, renderBiteReport, BITE_SOURCES, type BiteReportOpts, type BiteReportPack } from '../src/bite-report.js';

// Notes of a dog presented after biting another dog; the vet examined the biting dog.
const notes = 'Rex, DSH. Halterin: hat gestern im Park Nachbarshund gebissen. AZ ungestört, Lefze li kleine Schürfung. Kein Hinweis auf Schmerzen. Verhalten in Praxis ruhig. Wunde gereinigt.';
const at = (frag: string): [number, number] => { const i = notes.indexOf(frag); if (i < 0) throw new Error(frag); return [i, i + frag.length]; };
const record = ClinicalRecord.parse({
  schema_version: '0.2',
  patient: { name: 'Rex', species: 'dog', breed: 'DSH', sex: null, neuter_status: null, age: null, weight: null },
  presenting_complaint: { text: 'hat gestern im Park Nachbarshund gebissen', source_role: 'owner_reported', source_spans: [at('hat gestern im Park Nachbarshund gebissen')] },
  history: [],
  examination: {
    vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null },
    findings: [
      { system: 'Allgemein', text: 'AZ ungestört', source_role: 'vet_observed', source_spans: [at('AZ ungestört')] },
      { system: 'Haut', text: 'Lefze li kleine Schürfung', source_role: 'vet_observed', source_spans: [at('Lefze li kleine Schürfung')] },
      { system: 'Verhalten', text: 'Verhalten in Praxis ruhig', source_role: 'vet_observed', source_spans: [at('Verhalten in Praxis ruhig')] },
    ],
  },
  diagnostics: [],
  assessment: { text: null, differentials: [], source_spans: [] },
  treatments: [{ type: 'procedure', text: 'Wunde gereinigt', status: 'performed', source_spans: [at('Wunde gereinigt')] }],
  medications: [],
  plan: { follow_up: null, instructions: [] },
  missing: [],
  uncertain: [],
});
const header = PatientHeader.parse({ name: 'Rex', species: 'dog', breed: 'Deutscher Schäferhund', sex: 'male', neuter_status: 'intact', age: { value: 4, unit: 'year' }, weight_kg: 38 });
const ctxCH = VisitContext.parse({ country: 'CH', microchip: '756098100123456', owner: { name: 'Petra Keller' }, author: { name: 'Dr. med. vet. Urs Frei', registration: 'GLN 7601000000000' } });
const ctxIT = VisitContext.parse({ country: 'IT', microchip: '380260000123456', owner: { name: 'Marco Rossi' }, author: { name: 'Dott.ssa Anna Bianchi', registration: 'Ordine MI 1234' } });

const full: BiteReportOpts = {
  approved: true,
  to: 'Veterinäramt Kanton Zürich',
  reason: 'injury_animal',
  patient_role: 'biting_dog',
  examined: { biting_dog: true, injured_animal: false },
  incident: { date: '2026-10-21', time: '17:30', place: 'Hundewiese Irchelpark', municipality: 'Zürich', public_place: true, police_report: false, description: 'Laut Halterin Rauferei an der Leine, ein Biss in den Nacken des anderen Hundes.', account_source: 'owner_reported' },
  injury: { description: 'Laut Halterin Bisswunde Nacken beim anderen Hund, nicht selbst gesehen.', severity_description: 'Nach Angabe der Halterin tierärztlich versorgt; Ausmass mir nicht bekannt.' },
  injured: { kind: 'animal', animal: { species: 'Hund', breed: 'Labrador Retriever' } },
  biting_dog: { colour: 'schwarz-braun' },
  keeper: { address: 'Musterweg 3, 8057 Zürich', phone: '079 000 00 00' },
  practice: { name: 'Kleintierpraxis Irchel', address: 'Irchelstrasse 1, 8057 Zürich' },
};

/** Every { value, source } in the pack, with the object it should resolve against. */
const sourced = (o: unknown): Array<{ value: unknown; source: string; spans?: [number, number][] }> =>
  o && typeof o === 'object'
    ? ('source' in (o as object) && 'value' in (o as object) ? [o as { value: unknown; source: string }] : Object.values(o as object).flatMap(sourced))
    : [];
const resolve = (roots: Record<string, unknown>, path: string): unknown =>
  path.split('.').flatMap((p) => p.split(/\[(\d+)\]/).filter(Boolean)).reduce<unknown>((acc, k) => (acc as Record<string, unknown>)?.[k], roots);
const norm = (x: unknown) => (typeof x === 'string' ? x.trim() : x);

describe('bite report: every value traces to header, record, context or vet-typed opts', () => {
  const pack = buildBiteReport(record, header, ctxCH, full);

  it('identity of the patient (the biting dog) comes from the header and context, not the notes', () => {
    expect(pack.biting_dog.breed).toEqual({ value: 'Deutscher Schäferhund', source: 'header.breed' });
    expect(pack.biting_dog.microchip).toEqual({ value: '756098100123456', source: 'ctx.microchip' });
    expect(pack.biting_dog.sex).toEqual({ value: 'male', source: 'header.sex' });
    expect(pack.biting_dog.colour).toEqual({ value: 'schwarz-braun', source: 'opts.biting_dog.colour' });
    expect(pack.keeper.name).toEqual({ value: 'Petra Keller', source: 'ctx.owner.name' });
    expect(pack.reporter.vet_name?.source).toBe('ctx.author.name');
  });

  it('every sourced value equals what its path names; record values carry spans into the notes', () => {
    const roots = { header, record, ctx: ctxCH, opts: full };
    const all = sourced(pack);
    expect(all.length).toBeGreaterThan(25);
    for (const x of all) expect(norm(resolve(roots, x.source))).toEqual(x.value);
    for (const x of all.filter((y) => y.source.startsWith('record.') && y.source !== 'record.assessment.text')) {
      expect(x.spans?.length).toBeGreaterThan(0);
      for (const [a, b] of x.spans!) expect(notes.slice(a, b)).toBe(x.value);
    }
  });

  it('record findings are the record\'s own items, owner-reported ones marked', () => {
    expect(pack.record_findings.findings.map((f) => f.value)).toEqual(['AZ ungestört', 'Lefze li kleine Schürfung', 'Verhalten in Praxis ruhig']);
    expect(pack.record_findings.complaint?.role).toBe('owner_reported');
    expect(pack.record_findings.treatments).toEqual([{ value: 'Wunde gereinigt', source: 'record.treatments[0].text', spans: [at('Wunde gereinigt')] }]);
    expect(pack.record_findings.assessment).toBeNull();
  });

  it('a complete CH entry leaves nothing missing', () => {
    expect(pack.missing).toEqual([]);
  });
});

describe('bite report: missing list', () => {
  it('empty opts: everything the forms ask for is listed, nothing filled in', () => {
    const p = buildBiteReport(record, header, ctxCH, {});
    expect(p.missing).toEqual([
      'to', 'reason', 'patient_role', 'examined.biting_dog', 'examined.injured_animal',
      'incident.date', 'incident.time', 'incident.place', 'incident.municipality', 'incident.public_place', 'incident.police_report', 'incident.description', 'incident.account_source',
      'injury.description', 'injury.severity_description', 'injured.kind',
      'biting_dog.breed', 'biting_dog.sex', 'biting_dog.microchip', 'keeper.name', 'keeper.address',
      'reporter.practice_address',
    ]);
    expect(p.to).toBeNull();
    expect(p.incident.date).toBeNull();
  });

  it('IT asks for the observation dates and not the Swiss municipality box', () => {
    const p = buildBiteReport(record, header, ctxIT, { ...full, to: 'ASL Milano – Servizio veterinario', incident: { ...full.incident, municipality: null } });
    expect(p.missing).toEqual(['observation.start', 'observation.end']);
  });

  it('aggression report: no injury fields required', () => {
    const p = buildBiteReport(record, header, ctxCH, { ...full, reason: 'aggression', injury: {}, injured: {} });
    expect(p.missing).not.toContain('injury.description');
    expect(p.missing).not.toContain('injured.kind');
    expect(p.missing).not.toContain('examined.injured_animal');
  });

  it('CH: identity of the injured party without consent is flagged and not printed', () => {
    const p = buildBiteReport(record, header, ctxCH, { ...full, injured: { ...full.injured, name: 'Hans Muster', address: 'Weg 1' } });
    expect(p.missing).toContain('injured.consent');
    expect(p.warnings.map((w) => w.code)).toContain('consent_not_recorded');
    const txt = renderBiteReport(p, 'de');
    expect(txt).not.toContain('Hans Muster');
    const ok = renderBiteReport(buildBiteReport(record, header, ctxCH, { ...full, injured: { ...full.injured, name: 'Hans Muster', consent: true } }), 'de');
    expect(ok).toContain('Hans Muster');
  });

  it('rejects countries without a bite-report module', () => {
    expect(() => buildBiteReport(record, header, VisitContext.parse({ country: 'DE' }), full)).toThrow(/CH or IT/);
  });
});

describe('bite report: nothing inferred', () => {
  it('without patient_role the patient\'s identity goes to neither animal', () => {
    const p = buildBiteReport(record, header, ctxCH, { ...full, patient_role: null });
    expect(p.biting_dog.breed).toBeNull();
    expect(p.biting_dog.microchip).toBeNull();
    expect(p.injured.animal.microchip).toBeNull();
    expect(p.keeper.name).toBeNull();
    expect(p.missing).toEqual(expect.arrayContaining(['patient_role', 'biting_dog.breed', 'biting_dog.microchip', 'keeper.name']));
  });

  it('when the patient is the injured animal, the chip and owner go to that side; the biting dog is only what the vet typed', () => {
    const p = buildBiteReport(record, header, ctxCH, { ...full, patient_role: 'injured_animal', biting_dog: { breed: 'Mischling' } });
    expect(p.injured.animal.microchip).toEqual({ value: '756098100123456', source: 'ctx.microchip' });
    expect(p.injured.name).toEqual({ value: 'Petra Keller', source: 'ctx.owner.name' });
    expect(p.biting_dog.microchip).toBeNull();
    expect(p.biting_dog.breed).toEqual({ value: 'Mischling', source: 'opts.biting_dog.breed' });
    expect(p.keeper.name).toBeNull();
  });

  it('no severity grade, size class or risk judgement; observation end is never computed', () => {
    const p = buildBiteReport(record, header, ctxIT, { ...full, observation: { start: '2026-10-21' } });
    expect(p.observation.end).toBeNull();
    expect(p.missing).toContain('observation.end');
    expect(p.left_to_vet).toEqual(['injury_type_boxes', 'severity_grade', 'size_class']);
    const keys = JSON.stringify(Object.keys(p)) + JSON.stringify(p.biting_dog) + JSON.stringify(p.injury);
    expect(keys).not.toMatch(/danger|pericol|gefähr|risk|rischio|grade|size_class"/i);
    for (const lang of ['de', 'it', 'en'] as const) {
      const txt = renderBiteReport(p, lang);
      expect(txt).not.toMatch(/\b(Bagatell|leichtgradig|mittelgradig|schwere Bissverletzung|Riese|gefährlich|pericoloso|rischio elevato|dangerous)\b/i);
      expect(txt).not.toContain('2026-10-31');
    }
  });

  it('opts for the patient side do not override locked header facts', () => {
    const p = buildBiteReport(record, header, ctxCH, { ...full, biting_dog: { breed: 'Rottweiler', microchip: '999' } });
    expect(p.biting_dog.breed?.value).toBe('Deutscher Schäferhund');
    expect(p.biting_dog.microchip?.value).toBe('756098100123456');
  });

  it('species mismatch is a warning, not a correction', () => {
    const p = buildBiteReport(record, PatientHeader.parse({ ...header, species: 'cat' }), ctxCH, full);
    expect(p.biting_dog.species?.value).toBe('cat');
    expect(p.warnings.map((w) => w.code)).toContain('patient_not_dog');
  });
});

describe('bite report: languages', () => {
  const ch = buildBiteReport(record, header, ctxCH, full);
  const it_ = buildBiteReport(record, header, ctxIT, { ...full, to: 'ASL Città di Milano – Dipartimento Veterinario', observation: { start: '2026-10-21', end: '2026-10-31', place: 'domicilio del proprietario', ordered_by: 'ASL' } });

  it('CH defaults to German with the TSchV art. 78 basis and the vet-named recipient', () => {
    const txt = renderBiteReport(ch);
    expect(txt).toMatch(/^# Meldung eines Vorfalls mit einem Hund/);
    expect(txt).toContain('Art. 78 Abs. 1 Tierschutzverordnung');
    expect(txt).toContain('- An: Veterinäramt Kanton Zürich');
    expect(txt).toContain('zu unterschreiben und an die unten genannte zuständige Stelle zu senden');
    expect(txt).toContain('Mikrochip-Nr.: 756098100123456');
    expect(txt).toContain('Lefze li kleine Schürfung');
    expect(txt).toContain('Meldegrund: Verletzung Tier');
    expect(txt).not.toContain('▲');
  });

  it('CH in Italian (Ticino) cites the OPAn', () => {
    const txt = renderBiteReport(ch, 'it');
    expect(txt).toMatch(/^# Notifica di un incidente con un cane/);
    expect(txt).toContain('art. 78 cpv. 1 dell\'ordinanza sulla protezione degli animali (OPAn');
  });

  it('IT defaults to Italian, addressed to the ASL the vet named, with the typed observation dates and the rabies note', () => {
    const txt = renderBiteReport(it_);
    expect(txt).toMatch(/^# Segnalazione di morsicatura/);
    expect(txt).toContain('Destinatario: ASL Città di Milano – Dipartimento Veterinario');
    expect(txt).toContain('Dal: 2026-10-21 · Al: 2026-10-31');
    expect(txt).toContain('entro 12 ore');
    expect(txt).toContain('Microchip: 380260000123456');
  });

  it('EN reference rendering; missing values are flagged in the document language', () => {
    const txt = renderBiteReport(buildBiteReport(record, header, ctxCH, {}), 'en');
    expect(txt).toContain('Report under Art. 78 para. 1 Swiss Animal Welfare Ordinance');
    expect(txt).toContain('DRAFT — not yet approved');
    expect(txt).toContain('- To: ▲ Missing');
    expect(txt).toContain('## ▲ Missing');
    const de = renderBiteReport(buildBiteReport(record, header, ctxCH, {}), 'de');
    expect(de).toContain('- An: ▲ Fehlt');
  });

  it('no address of a cantonal office or ASL is printed unless the vet typed it', () => {
    const txt = renderBiteReport(buildBiteReport(record, header, ctxCH, { ...full, to: null }), 'de');
    expect(txt).not.toMatch(/Waltersbachstrasse|Herrengasse|Marquisat|veta\.zh\.ch|avet@be\.ch/);
  });

  it('cites only sources listed in BITE_SOURCES', () => {
    for (const w of [...ch.warnings, ...it_.warnings]) if (w.source) expect(BITE_SOURCES[w.source]).toBeDefined();
  });

  it('pack type is stable', () => {
    const p: BiteReportPack = ch;
    expect(p.format).toBe('aiveterinary.bite-report/1');
  });
});
