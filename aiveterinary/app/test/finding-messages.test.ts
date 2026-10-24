import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, validateDerivedText, type Finding } from '../src/validators.js';
import { makeConsultation, validateConsultation, setLine, SHARED } from '../src/multi-pet.js';
import { FINDING_RULES, FINDING_TEMPLATES, findingMessage } from '../src/finding-messages.js';
import type { Lang } from '../src/render.js';

const LANGS: Lang[] = ['en', 'de', 'it'];
const casesDir = fileURLToPath(new URL('../eval/cases/', import.meta.url));
const multiDir = fileURLToPath(new URL('../eval/cases-multi/', import.meta.url));
const readJson = (dir: string, f: string) => JSON.parse(readFileSync(join(dir, f), 'utf8'));
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));

/** Findings of every eval fixture (seeded-error cases included), keyed by case id. */
function fixtureFindings(): { id: string; f: Finding }[] {
  const out: { id: string; f: Finding }[] = [];
  for (const file of readdirSync(casesDir).filter((x) => x.endsWith('.json')).sort()) {
    const c = readJson(casesDir, file);
    if (!c.fixture_record) continue;
    for (const f of validateAll(ClinicalRecord.parse(c.fixture_record), normalizeNotes(c.notes), PatientHeader.parse(c.header))) out.push({ id: c.id, f });
  }
  return out;
}

/** Findings of every multi-pet case: the gold assignment, each patient's line moved to the other animal, a line cleared, a labelled line marked shared. */
function multiFindings(): { id: string; f: Finding }[] {
  const out: { id: string; f: Finding }[] = [];
  for (const file of readdirSync(multiDir).filter((x) => x.endsWith('.json')).sort()) {
    const c = readJson(multiDir, file);
    const notes = normalizeNotes(c.notes);
    const patients = c.patients.map((p: any) => ({ id: p.id, header: PatientHeader.parse(p.header), record: ClinicalRecord.parse(p.fixture_record) }));
    const gold = makeConsultation(notes, patients, c.assignment);
    const variants = [gold];
    for (const p of patients) {
      const own = Number(Object.entries(gold.assignment).find(([, t]) => t === p.id)![0]);
      const other = patients.find((x: any) => x.id !== p.id)!.id;
      variants.push({ ...gold, assignment: setLine(notes, patients, gold.assignment, own, other) });
      variants.push({ ...gold, assignment: setLine(notes, patients, gold.assignment, own, null) });
      variants.push({ ...gold, assignment: setLine(notes, patients, gold.assignment, own, SHARED) });
    }
    for (const v of variants) {
      const r = validateConsultation(v);
      for (const f of [...Object.values(r.byPatient).flat(), ...r.consultation]) out.push({ id: c.id, f });
    }
  }
  return out;
}

/** Planted errors on small records, so every rule fires at least once (including the ones no fixture raises). */
function plantedFindings(): Finding[] {
  const c = readJson(casesDir, '001-luna-vomiting.json');
  const notes = normalizeNotes(c.notes); const header = PatientHeader.parse(c.header); const base = ClinicalRecord.parse(c.fixture_record);
  const out: Finding[] = [];
  const run = (mut: (r: any, h: any) => void, n = notes) => { const r: any = clone(base); const h: any = clone(header); mut(r, h); out.push(...validateAll(r, n, h)); };
  run((r) => { r.history[0].source_spans = []; });
  run((r) => { r.assessment.text = 'Gastritis'; });
  run((r) => { r.history[0].source_spans = [[0, 9999]]; });
  run((r) => { r.examination.vitals.temperature.value = 39.2; });
  run((r) => { r.examination.vitals.temperature.source_spans = [[0, 8]]; });
  run((r) => { r.presenting_complaint.text = 'vomiting 7x since yesterday'; r.history[0].value = '39.1'; });
  run((r) => { r.patient.species = 'cat'; r.patient.sex = 'male'; });
  run((r, h) => { h.sex = 'male'; r.history[0].value = 'pregnant'; });
  run((r, h) => { h.neuter_status = 'neutered'; r.history[0].value = 'in heat'; });
  run((r) => { r.examination.vitals.temperature.value = 45; });
  run((r, h) => { h.species = 'cat'; r.patient.weight = { value: 20, unit: 'kg', source_spans: [[75, 84]] }; });
  const empty = (r: any) => { r.presenting_complaint = null; r.history = []; r.examination.vitals.temperature = null; r.examination.findings = []; r.diagnostics = []; r.treatments = []; r.plan.follow_up = null; };
  run((r) => { empty(r); r.examination.findings = [{ system: 'musculoskeletal', text: 'limping', source_role: 'vet_observed', source_spans: [[0, 21]] }]; }, 'owner reports limping\n');
  // Medications, on their own notes.
  const medNotes = 'Cerenia 1 mg/kg SC SID 5 days\nalso Metacam 10 days 3 tabs\n';
  const med = (m: any) => ({ drug: null, class_as_written: null, dose: null, dose_unit: null, route: null, frequency: null, duration: null, status: 'prescribed', source_spans: [[0, 29]], ...m });
  run((r) => {
    empty(r);
    r.medications = [
      med({ drug: 'Metacam', dose: 10, duration: '10 days' }),
      med({ drug: 'Zylkene', dose: 99, dose_unit: 'zz', duration: '77 days', route: 'IV', frequency: 'BID' }),
      med({ dose: 1 }),
      med({ drug: 'Cerenia', source_spans: [[29, 30]] }),
    ];
  }, medNotes);
  const derivedRec: any = clone(base); derivedRec.medications = [med({ drug: 'Cerenia' })];
  out.push(...validateDerivedText('Give 99 mg.', derivedRec, notes));
  return out;
}

describe('finding messages: templates', () => {
  it('every rule has a template in EN, DE and IT, and no template is for an unknown rule', () => {
    for (const lang of LANGS) {
      const t = FINDING_TEMPLATES[lang];
      for (const rule of FINDING_RULES) expect(typeof t[rule], `${lang}: ${rule}`).toBe('function');
      expect(Object.keys(t).sort()).toEqual([...FINDING_RULES].sort());
    }
  });
  it('every rule raised in validators.ts and multi-pet.ts is listed', () => {
    const src = ['validators.ts', 'multi-pet.ts'].map((f) => readFileSync(new URL(`../src/${f}`, import.meta.url), 'utf8')).join('\n');
    const literal = [...src.matchAll(/\brule: '([a-z_]+)'/g), ...src.matchAll(/'([a-z_]+_not_in_[a-z_]+)'/g)].map((m) => m[1]);
    for (const r of new Set(literal)) expect(FINDING_RULES, r).toContain(r);
  });
});

describe('finding messages: English is the validators\' message, unchanged', () => {
  const all = [...fixtureFindings().map((x) => x.f), ...multiFindings().map((x) => x.f), ...plantedFindings()];
  it('every rule fires at least once in this set', () => {
    const fired = new Set(all.map((f) => f.rule));
    for (const r of FINDING_RULES) expect(fired.has(r), r).toBe(true);
  });
  it('findingMessage(f, "en") equals f.message for every finding (eval fixtures, seeded, multi-pet, planted)', () => {
    expect(all.length).toBeGreaterThan(50);
    for (const f of all) {
      expect(f.params, `${f.rule}@${f.field}`).toBeDefined();
      expect(findingMessage(f, 'en')).toBe(f.message);
    }
  });
  it('DE and IT differ from English and keep the quoted note text as written', () => {
    for (const f of all) for (const lang of ['de', 'it'] as const) {
      const m = findingMessage(f, lang);
      expect(m, `${lang} ${f.rule}`).not.toBe(f.message);
      // English explanation words must not remain once the vet's own text (quotes, drug names, labels) is taken out.
      const own = Object.values(f.params!).flat().filter((v): v is string => typeof v === 'string' && v.length > 2);
      const rest = own.reduce((s, v) => s.split(v).join(''), m);
      expect(rest, `${lang} ${f.rule}: ${m}`).not.toMatch(/\b(the notes|points to|is not|Check|record|assigned|line)\b/);
      const q = (f.params as any).quote; if (q) expect(m).toContain(q);
    }
  });
  it('falls back to the English message for a finding without params', () => {
    const f: Finding = { rule: 'something_else', severity: 'warn', field: 'x', message: 'Plain English.' };
    expect(findingMessage(f, 'de')).toBe('Plain English.');
  });
});

describe('finding messages: DE/IT spot checks', () => {
  it('status conflict (seeded case)', () => {
    const c = readJson(casesDir, readdirSync(casesDir).find((x) => x.startsWith('200-seeded-status-conflict'))!);
    const f = validateAll(ClinicalRecord.parse(c.fixture_record), normalizeNotes(c.notes), PatientHeader.parse(c.header)).find((x) => x.rule === 'status_conflicts_source')!;
    const { status, said, quote } = f.params as any;
    expect(status).toBeTruthy();
    const de = findingMessage(f, 'de'); const it_ = findingMessage(f, 'it');
    expect(de).toMatch(/^Erfasst als „.+“, aber die Textstelle, auf die dieser Eintrag verweist, lautet: .+ \(„.+“\)\.$/);
    expect(it_).toMatch(/^Registrato come «.+», ma il testo a cui rimanda questa voce indica: .+ \(«.+»\)\.$/);
    expect(de).toContain(quote); expect(it_).toContain(quote);
    expect(de).not.toContain(`"${status}"`); expect(it_).not.toContain(` ${said} (`);
  });
  it('notes contradiction and wrong animal line', () => {
    const f: Finding = { rule: 'notes_contradiction', severity: 'warn', field: 'examination.vitals.temperature', message: '', params: { kept: '38.6', others: ['39.4'], vital: 'temperature' } };
    expect(findingMessage(f, 'de')).toBe('Die Notizen nennen für Temperatur 38.6 und 39.4; in der Dokumentation steht 38.6. Prüfen Sie, welcher Wert stimmt.');
    expect(findingMessage(f, 'it')).toBe('Per temperatura le note riportano 38.6 e 39.4; la cartella clinica riporta 38.6. Verifichi quale valore è corretto.');
    const w: Finding = { rule: 'wrong_animal_line', severity: 'block', field: 'medications[1]', message: '', params: { line: 10, quote: 'Felix: Milbemax 1 tablet PO once, dispensed', owner: 'Felix', patient: 'Bella' } };
    expect(findingMessage(w, 'de')).toBe('Dies stammt aus Zeile 10 („Felix: Milbemax 1 tablet PO once, dispensed“), die Felix zugeordnet ist. Es darf nicht in der Dokumentation von Bella stehen.');
    expect(findingMessage(w, 'it')).toBe('Questo proviene dalla riga 10 («Felix: Milbemax 1 tablet PO once, dispensed»), assegnata a Felix. Non può comparire nella cartella clinica di Bella.');
  });
  it('species and status enums are translated', () => {
    const f: Finding = { rule: 'patient_conflict', severity: 'block', field: 'patient.species', message: '', params: { kind: 'species', value: 'cat', expected: 'dog' } };
    expect(findingMessage(f, 'de')).toBe('Die Notizen deuten auf die Tierart „Katze“ hin, laut Patientendaten ist die Tierart jedoch Hund.');
    expect(findingMessage(f, 'it')).toBe('Le note indicano la specie «gatto», ma secondo i dati del paziente la specie è cane.');
    const l: Finding = { rule: 'label_mismatch', severity: 'warn', field: 'notes.line[9]', message: '', params: { line: 9, label: 'Felix', shared: true, target: '' } };
    expect(findingMessage(l, 'de')).toBe('Zeile 9 beginnt mit „Felix:“, ist aber allen Tieren (gemeinsam) zugeordnet. Prüfen Sie die Zuordnung.');
    expect(findingMessage(l, 'it')).toBe("La riga 9 inizia con «Felix:» ma è assegnata a tutti gli animali (comune). Verifichi l'assegnazione.");
  });
});
