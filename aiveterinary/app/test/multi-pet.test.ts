import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync, mkdtempSync, copyFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll } from '../src/validators.js';
import { renderOwnerSummary, renderConsultReport, renderDischargeLetter, renderMedicationTable, crossDocumentMedicationCheck, type Lang } from '../src/render.js';
import {
  SHARED, noteLines, spanLineIndices, assignLines, setLine, suggestAssignments, confirmSuggestion, makeConsultation,
  validateConsultation, validateCrossPatient, patientView, renderPerPatient, renderOwnerLetterMulti, type Consultation,
} from '../src/multi-pet.js';
import { runEval } from '../src/cli/eval.js';

const multiDir = fileURLToPath(new URL('../eval/cases-multi/', import.meta.url));
const files = readdirSync(multiDir).filter((f) => f.endsWith('.json')).sort();
const loadCase = (lang: Lang) => JSON.parse(readFileSync(join(multiDir, files.find((f) => f.endsWith(`-${lang}.json`))!), 'utf8'));
const patientsOf = (c: any) => c.patients.map((p: any) => ({ id: p.id, header: PatientHeader.parse(p.header), record: ClinicalRecord.parse(p.fixture_record) }));
/** The gold consultation of the EN/DE/IT two-pet case (dog first, cat second). */
const gold = (lang: Lang): Consultation => { const c = loadCase(lang); return makeConsultation(normalizeNotes(c.notes), patientsOf(c), c.assignment); };
const en = () => gold('en');
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x));

describe('note lines and spans', () => {
  it('lines carry offsets into the notes; blank lines are marked', () => {
    const ls = noteLines('a: x\n\nb: y');
    expect(ls.map((l) => [l.index, l.start, l.end, l.text, l.blank])).toEqual([[0, 0, 4, 'a: x', false], [1, 5, 5, '', true], [2, 6, 10, 'b: y', false]]);
  });
  it('a span maps to every line it touches, ignoring trailing newlines', () => {
    const n = 'one\ntwo\nthree';
    expect(spanLineIndices(n, [0, 3])).toEqual([0]);
    expect(spanLineIndices(n, [0, 4])).toEqual([0]);
    expect(spanLineIndices(n, [2, 6])).toEqual([0, 1]);
    expect(spanLineIndices(n, [8, 13])).toEqual([2]);
  });
});

describe('assignLines: the vet assigns, nothing else does', () => {
  const ps = [{ id: 'milo' }, { id: 'luna' }];
  const notes = 'Milo: T 38.5\n\nLuna: T 38.9\nboth: no walks today';
  it('normalises the assignment and lists unassigned non-blank lines', () => {
    const r = assignLines(notes, ps, { 0: 'milo', 3: SHARED, 2: null });
    expect(r.assignment).toEqual({ 0: 'milo', 3: SHARED });
    expect(r.unassigned).toEqual([2]);
    expect(r.lines.map((l) => l.target)).toEqual(['milo', null, null, SHARED]);
  });
  it('refuses unknown patients, blank lines and lines outside the notes', () => {
    expect(() => assignLines(notes, ps, { 0: 'rex' })).toThrow(/Unknown patient/);
    expect(() => assignLines(notes, ps, { 1: 'milo' })).toThrow(/blank/);
    expect(() => assignLines(notes, ps, { 9: 'milo' })).toThrow(/not in the notes/);
  });
  it('refuses duplicate or reserved patient ids', () => {
    expect(() => assignLines(notes, [{ id: 'a' }, { id: 'a' }], {})).toThrow(/unique/);
    expect(() => assignLines(notes, [{ id: SHARED }], {})).toThrow(/Invalid/);
  });
  it('setLine sets and clears one line, leaving the input untouched', () => {
    const a = { 0: 'milo' };
    const b = setLine(notes, ps, a, 2, 'luna');
    expect(b).toEqual({ 0: 'milo', 2: 'luna' });
    expect(setLine(notes, ps, b, 0, null)).toEqual({ 2: 'luna' });
    expect(a).toEqual({ 0: 'milo' });
  });
});

describe('suggestions: name labels are suggested, never applied', () => {
  const header = (name: string) => PatientHeader.parse({ name, species: 'dog' });
  const ps = [{ id: 'milo', header: header('Milo') }, { id: 'max', header: header('Max') }];
  const notes = 'Milo: ear red\n- Max: limping\nMaxi: not a patient\nrecheck Milo 7 days\nmilo : T 38.5';
  it('a line starting with exactly one patient\'s name label ("Milo:", "- Max:", case-insensitive) is suggested', () => {
    expect(suggestAssignments(notes, ps).map((s) => [s.line, s.target, s.reason])).toEqual([[0, 'milo', 'name_label'], [1, 'max', 'name_label'], [4, 'milo', 'name_label']]);
  });
  it('a name later in the line, or a longer word ("Maxi:"), is not a label', () => {
    const lines = suggestAssignments(notes, ps).map((s) => s.line);
    expect(lines).not.toContain(2); expect(lines).not.toContain(3);
  });
  it('suggestions are not applied: the assignment stays empty until the vet confirms', () => {
    const c = makeConsultation(notes, ps.map((p) => ({ ...p, record: ClinicalRecord.parse(en().patients[0].record) })));
    expect(c.assignment).toEqual({});
    expect(assignLines(notes, ps, c.assignment).unassigned).toEqual([0, 1, 2, 3, 4]);
    const [s0] = suggestAssignments(notes, ps);
    const a = confirmSuggestion(notes, ps, c.assignment, s0);
    expect(a).toEqual({ 0: 'milo' });
    expect(suggestAssignments(notes, ps, a).map((s) => s.line)).toEqual([1, 4]);
  });
  it('two patients with the same name: no suggestion', () => {
    expect(suggestAssignments('Milo: ear red', [{ id: 'a', header: header('Milo') }, { id: 'b', header: header('milo') }])).toEqual([]);
  });
  it.each(['en', 'de', 'it'] as Lang[])('%s case: every suggestion agrees with the gold assignment; the unlabelled line is not suggested', (lang) => {
    const c = gold(lang);
    const s = suggestAssignments(c.notes, c.patients);
    for (const x of s) expect(c.assignment[x.line]).toBe(x.target);
    const lines = noteLines(c.notes);
    expect(s.map((x) => x.line)).not.toContain(lines.length - 1); // "recheck Bella in 7 days": the vet assigns it
    expect(s.map((x) => x.line)).not.toContain(lines.length - 2); // "both: …": shared, by the vet
  });
});

describe('validation per patient and across patients', () => {
  it.each(['en', 'de', 'it'] as Lang[])('%s gold consultation: no finding at all', (lang) => {
    const v = validateConsultation(gold(lang));
    expect(v.consultation).toEqual([]);
    expect(Object.values(v.byPatient).flat()).toEqual([]);
    expect(v.blocked).toBe(false);
  });

  it('a fact on a line assigned to another patient blocks (wrong animal)', () => {
    const c = en(); const [dog, cat] = c.patients;
    // the cat's Milbemax line copied into the dog's record
    dog.record.medications.push(clone(cat.record.medications[0]));
    const v = validateConsultation(c);
    const f = v.byPatient[dog.id].filter((x) => x.rule === 'wrong_animal_line');
    expect(f).toHaveLength(1);
    expect(f[0]).toMatchObject({ severity: 'block', field: 'medications[1]' });
    expect(f[0].message).toMatch(/^This comes from line 10 \("Felix: Milbemax 1 tablet PO once, dispensed"\), which is assigned to Felix\. It cannot be in Bella's record\.$/);
    expect(v.blocked).toBe(true);
    expect(v.byPatient[cat.id]).toEqual([]);
  });

  it('reassigning one of a patient\'s lines to the other patient blocks that fact', () => {
    const c = en(); const [dog, cat] = c.patients;
    c.assignment = setLine(c.notes, c.patients, c.assignment, 1, cat.id); // "Bella: T 38.7" → Felix
    const v = validateConsultation(c);
    expect(v.byPatient[dog.id].map((x) => `${x.rule}@${x.field}`)).toContain('wrong_animal_line@examination.vitals.temperature');
    expect(v.consultation.map((x) => x.rule)).toEqual(['label_mismatch']);
  });

  it('facts on shared lines are allowed for every patient', () => {
    const c = en();
    const shared = Object.entries(c.assignment).filter(([, t]) => t === SHARED).map(([i]) => Number(i));
    expect(shared).toHaveLength(1);
    for (const p of c.patients) expect(p.record.plan.instructions.some((i) => i.source_spans.some((s) => spanLineIndices(c.notes, s).includes(shared[0])))).toBe(true);
    for (const p of c.patients) expect(validateCrossPatient(c, p.id)).toEqual([]);
  });

  it('a fact on a line not assigned yet blocks; the line itself is flagged', () => {
    const c = en(); const [dog] = c.patients;
    c.assignment = setLine(c.notes, c.patients, c.assignment, 11, null); // "recheck Bella in 7 days"
    const v = validateConsultation(c);
    expect(v.byPatient[dog.id].map((x) => `${x.rule}@${x.severity}@${x.field}`)).toEqual(['unassigned_line_fact@block@plan.follow_up']);
    expect(v.consultation.map((x) => `${x.rule}@${x.severity}@${x.field}`)).toEqual(['unassigned_line@warn@notes.line[12]']);
  });

  it('a labelled line assigned elsewhere warns (label_mismatch)', () => {
    const c = en();
    c.assignment = setLine(c.notes, c.patients, c.assignment, 8, SHARED); // "Felix: heart and lungs NAD" → shared
    const v = validateConsultation(c);
    expect(v.consultation.map((x) => [x.rule, x.severity])).toEqual([['label_mismatch', 'warn']]);
    expect(v.consultation[0].message).toBe('Line 9 starts with "Felix:" but is assigned to all animals (shared). Check the assignment.');
  });

  it('each patient is validated on its own view: the other animal\'s temperature is not a contradiction', () => {
    const c = en(); const [dog] = c.patients;
    // On the full notes, the cat's "T 38.4" reads as a second temperature for the dog.
    expect(validateAll(dog.record, c.notes, dog.header).map((x) => x.rule)).toEqual(['notes_contradiction']);
    const view = patientView(c, dog.id);
    expect(view.length).toBe(c.notes.length);
    expect(view).not.toContain('Felix');
    expect(view).toContain('both: flea treatment');
    expect(validateConsultation(c).byPatient[dog.id]).toEqual([]);
  });

  it('other_animal_fact keeps working inside a multi-pet consultation', () => {
    const notes = 'Bella: other dog at home has diarrhoea\nFelix: T 38.4';
    const base = en();
    const dog = { ...base.patients[0], record: ClinicalRecord.parse({ ...clone(base.patients[0].record), presenting_complaint: null, history: [{ finding: 'diarrhoea', value: 'has diarrhoea', source_role: 'owner_reported', source_spans: [[notes.indexOf('has diarrhoea'), notes.indexOf('has diarrhoea') + 13]] }], examination: { vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null }, findings: [] }, diagnostics: [], assessment: { text: null, differentials: [], source_spans: [] }, treatments: [], medications: [], plan: { follow_up: null, instructions: [] } }) };
    const cat = { ...base.patients[1], record: ClinicalRecord.parse({ ...clone(dog.record), history: [] }) };
    const c = makeConsultation(notes, [dog, cat], { 0: dog.id, 1: cat.id });
    expect(validateConsultation(c).byPatient[dog.id].map((x) => [x.rule, x.severity])).toEqual([['other_animal_fact', 'warn']]);
  });
});

describe('documents', () => {
  it.each(['en', 'de', 'it'] as Lang[])('%s: each patient gets its own documents from the unchanged renderers', (lang) => {
    const c = gold(lang);
    for (const render of [renderConsultReport, renderOwnerSummary, renderDischargeLetter]) {
      const docs = renderPerPatient(c, (r, h) => render(r, h, lang));
      expect(docs.map((d) => d.id)).toEqual(c.patients.map((p) => p.id));
      c.patients.forEach((p, i) => expect(docs[i].text).toBe(render(p.record, p.header, lang)));
    }
    // a patient's own report carries none of the other patient's medication
    const [dog, cat] = c.patients;
    expect(renderConsultReport(dog.record, dog.header, lang)).not.toContain('Milbemax');
    expect(renderConsultReport(cat.record, cat.header, lang)).not.toContain('Surolan');
  });

  const heads: Record<Lang, { shared: string; home: string; forOwner: string; and: string }> = {
    en: { shared: '## For all animals', home: '### At home', forOwner: '**For the owner of Bella and Felix**', and: 'and' },
    de: { shared: '## Für alle Tiere', home: '### Zu Hause', forOwner: '**Für die Halterin / den Halter von Lotte und Moritz**', and: 'und' },
    it: { shared: '## Per tutti gli animali', home: '### A casa', forOwner: '**Per il proprietario di Briciola e Tigro**', and: 'e' },
  };

  it.each(['en', 'de', 'it'] as Lang[])('%s: one owner letter, one section per animal, each medication table exactly as rendered individually', (lang) => {
    const c = gold(lang);
    const letter = renderOwnerLetterMulti(c, lang);
    expect(letter.match(/^# /gm)).toHaveLength(1);
    expect(letter).toContain(heads[lang].forOwner);
    for (const p of c.patients) {
      const give = p.record.medications.filter((m) => m.status === 'dispensed' || m.status === 'prescribed');
      const table = renderMedicationTable(give, lang);
      expect(table).not.toBe('');
      expect(renderOwnerSummary(p.record, p.header, lang)).toContain(table);
      expect(letter.split(table)).toHaveLength(2); // exactly once
      expect(crossDocumentMedicationCheck(p.record, { letter })).toEqual([]);
    }
    // animal sections in order, each before the next, each with its own table
    const [dog, cat] = c.patients;
    const iDog = letter.indexOf(`## ${dog.header.name} — `), iCat = letter.indexOf(`## ${cat.header.name} — `);
    expect(iDog).toBeGreaterThan(0); expect(iCat).toBeGreaterThan(iDog);
    expect(letter.indexOf('Surolan')).toBeGreaterThan(iDog); expect(letter.indexOf('Surolan')).toBeLessThan(iCat);
    expect(letter.indexOf('Milbemax')).toBeGreaterThan(iCat);
    // no medication table merged across animals: no table row holds both drugs, each table has one drug row
    for (const row of letter.split('\n').filter((l) => l.startsWith('|') && /Surolan|Milbemax/.test(l))) expect(/Surolan/.test(row) && /Milbemax/.test(row)).toBe(false);
  });

  it.each(['en', 'de', 'it'] as Lang[])('%s: the shared instruction is printed once, under "for all animals", not in an animal section', (lang) => {
    const c = gold(lang);
    const text = c.patients[0].record.plan.instructions[0].text;
    const letter = renderOwnerLetterMulti(c, lang);
    const shared = letter.indexOf(heads[lang].shared);
    expect(shared).toBeGreaterThan(letter.indexOf(`## ${c.patients[1].header.name} — `));
    expect(letter.slice(shared)).toContain(`${heads[lang].home}\n- ${text.charAt(0).toUpperCase() + text.slice(1)}`);
    expect(letter.toLowerCase().split(text.toLowerCase())).toHaveLength(2);
    // individually, each animal's summary still prints it under "At home"
    for (const p of c.patients) expect(renderOwnerSummary(p.record, p.header, lang)).toContain(text.charAt(0).toUpperCase() + text.slice(1));
  });

  it('a home instruction on an animal\'s own line stays in that animal\'s section', () => {
    const c = en();
    c.assignment = setLine(c.notes, c.patients, c.assignment, 10, c.patients[0].id); // the flea line → Bella only
    // (the cat's record still points at it, which validation blocks; the renderer just follows the assignment)
    const letter = renderOwnerLetterMulti(c, 'en');
    expect(letter).not.toContain('## For all animals');
  });

  it('draft and disclosure are printed once for the whole letter; provenance sums the records', () => {
    const c = en();
    const draft = renderOwnerLetterMulti(c, 'en');
    expect(draft.match(/DRAFT/g)).toHaveLength(1);
    const approved = renderOwnerLetterMulti(c, 'en', { approved: true });
    expect(approved).not.toContain('DRAFT');
    expect(approved.match(/reviewed and approved by the veterinarian/g)).toHaveLength(1);
    expect(approved.match(/^_Facts from the notes: \d+ · Not recorded: \d+ · Added by AI: 0_$/gm)).toHaveLength(1);
    // Bella 8 facts + Felix 5 (the shared flea instruction is a fact in both records)
    expect(approved).toContain('_Facts from the notes: 13 · Not recorded: 0 · Added by AI: 0_');
    expect(approved).not.toMatch(/\n{3,}/);
  });

  it('dose checklist headings move one level down with their animal', () => {
    const letter = renderOwnerLetterMulti(en(), 'en');
    expect(letter).toContain('#### Dose checklist');
    expect(letter).toContain('### Medication to give');
  });
});

describe('eval: multi-pet consultations', () => {
  it('each consultation in EN, DE and IT, two patients each, one shared line, in their own folder', () => {
    expect(files).toHaveLength(9);
    const langs = files.map((f) => JSON.parse(readFileSync(join(multiDir, f), 'utf8')).language);
    for (const l of ['en', 'de', 'it']) expect(langs.filter((x) => x === l), l).toHaveLength(files.length / 3);
    for (const f of files) {
      const c = JSON.parse(readFileSync(join(multiDir, f), 'utf8'));
      expect(c.multi_pet).toBe(true); expect(c.patients).toHaveLength(2);
      expect(Object.values(c.assignment).filter((t) => t === SHARED)).toHaveLength(1);
      expect(normalizeNotes(c.notes)).toBe(c.notes);
    }
  });
  it('the harness scores them apart: not in cases, per_case or any rate', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'aivet-multi-')); const cases = join(dir, 'cases'); const multi = join(dir, 'multi'); const out = join(dir, 'out');
    const { mkdirSync } = await import('node:fs'); mkdirSync(cases); mkdirSync(multi);
    copyFileSync(fileURLToPath(new URL('../eval/cases/001-luna-vomiting.json', import.meta.url)), join(cases, '001.json'));
    for (const f of files) copyFileSync(join(multiDir, f), join(multi, f));
    const failures = await runEval('fixture', false, { casesDir: cases, outDir: out, quiet: true, multiDir: multi });
    const r = JSON.parse(readFileSync(join(out, 'fixture.json'), 'utf8'));
    expect(failures).toBe(0);
    expect(r.cases).toBe(1);
    expect(r.per_case.map((p: any) => p.id)).toEqual(['001-luna-vomiting']);
    expect(r.metrics.cases_with_blocking_finding).toMatchObject({ n: 1 });
    expect(r.multi_pet).toMatchObject({ cases: files.length, failed: 0, patients: 2 * files.length, blocking: 0, warnings: 0, probes: 2 * files.length, probes_caught: 2 * files.length });
  });
  it('a custom cases folder without multiDir reads no multi-pet cases (other harness tests unchanged)', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'aivet-multi-')); const out = join(dir, 'out');
    copyFileSync(fileURLToPath(new URL('../eval/cases/001-luna-vomiting.json', import.meta.url)), join(dir, '001.json'));
    await runEval('fixture', false, { casesDir: dir, outDir: out, quiet: true });
    expect(JSON.parse(readFileSync(join(out, 'fixture.json'), 'utf8')).multi_pet).toBeUndefined();
  });
});
