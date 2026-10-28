import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader, type Medication } from '../src/schema.js';
import { renderDischargeLetter, renderMedicationTable, crossDocumentMedicationCheck, isCallInstruction, DISCHARGE_LABELS, REPORT_LABELS, headerLine as renderHeaderLine, type Lang } from '../src/render.js';
import { requiredMissing, validateDerivedText } from '../src/validators.js';
import { normalizeNotes } from '../src/normalize.js';
import { provenance } from '../src/country.js';

const load = (id: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${id}.json`, import.meta.url), 'utf8'));
const prep = (id: string) => { const c = load(id); return { notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: ClinicalRecord.parse(c.fixture_record), lang: c.language as Lang }; };
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/** Every sentence a record holds, in the form the renderer prints it (capitalised). */
function recordStrings(r: ClinicalRecord): Set<string> {
  const s = new Set<string>();
  if (r.presenting_complaint) s.add(r.presenting_complaint.text);
  for (const x of r.treatments) s.add(x.text);
  for (const x of r.diagnostics) { s.add(x.test); if (x.result) s.add(`${cap(x.test)}: ${x.result}`); }
  if (r.assessment.text) s.add(r.assessment.text);
  if (r.assessment.differentials.length) s.add(r.assessment.differentials.map((d) => d.text).join(', '));
  for (const m of r.medications) { if (m.drug) s.add(m.drug); if (m.class_as_written) s.add(m.class_as_written); }
  for (const i of r.plan.instructions) s.add(i.text);
  if (r.plan.follow_up) s.add(r.plan.follow_up.text);
  for (const m of r.missing) s.add(`${m.field}: ${m.reason}`);
  return new Set([...s].map((x) => cap(x)));
}

/**
 * Nothing added: every line of the letter is a fixed template label, the patient header, a code-built
 * medication table whose cells are the record's own values, or one of the record's own sentences
 * (optionally followed by a template status label in parentheses).
 */
function unexplainedLines(md: string, record: ClinicalRecord, header: PatientHeader, lang: Lang): string[] {
  const t = REPORT_LABELS[lang], x = DISCHARGE_LABELS[lang];
  const labels = new Set<string>([...Object.values(x), t.declinedCare, t.missing].map((l) => l));
  const statuses = new Set([t.performed, t.planned, t.declined, t.recommended, t.dispensed, t.prescribed]);
  const sentences = recordStrings(record);
  const meds = record.medications;
  const medCells = new Set<string>(['', '—', ...meds.flatMap((m) => [m.drug, m.class_as_written, m.route, m.frequency, m.duration, m.dose != null ? `${m.dose} ${m.dose_unit ?? ''}`.trim() : null].filter((v): v is string => !!v))]);
  const tableHead = renderMedicationTable(meds.length ? meds : [{ drug: 'x', class_as_written: null, dose: null, dose_unit: null, route: null, frequency: null, duration: null, status: 'performed', source_spans: [[0, 1]] } as Medication], lang).split('\n').slice(0, 2);
  const headerLine = renderHeaderLine(header, lang);
  const bad: string[] = [];
  for (const raw of md.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    if (line === `_${t.draft}_` || line === `_${t.disclosure}_`) continue;
    const p = provenance(record);
    if (line === `_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded))}_`) continue;
    if (line === `**${headerLine}**`) continue;
    const heading = /^#{1,3} (.*)$/.exec(line);
    if (heading) { if (!labels.has(heading[1].replace(/^▲ /, ''))) bad.push(line); continue; }
    if (line.startsWith('|')) {
      if (tableHead.includes(line)) continue;
      const cells = line.split('|').slice(1, -1).map((c) => c.trim());
      for (const c of cells) if (!medCells.has(c) && !statuses.has(c) && !c.includes('▲')) bad.push(`${line} [${c}]`);
      continue;
    }
    let body = line.replace(/^- /, '');
    const paren = / \(([^()]*)\)$/.exec(body);
    if (paren && statuses.has(paren[1])) body = body.slice(0, paren.index);
    body = body.replace(/: ▲ .*$/, '');
    if (!sentences.has(cap(body)) && !sentences.has(body)) bad.push(line);
  }
  return bad;
}

const CASES = ['001-luna-vomiting', '002-milo-otitis-de', '003-gatto-inappetenza-it', '106-gen-diarrhoea-declined-en', '107-gen-diarrhoea-declined-de', '108-gen-diarrhoea-declined-it', '130-gen-cystitis-cat-en', '131-gen-cystitis-cat-de', '132-gen-cystitis-cat-it', '151-gen-pruritus-declined-dispensed-en', '152-gen-pruritus-declined-dispensed-de', '153-gen-pruritus-declined-dispensed-it', '166-gen-rabbit-dental-declined-en', '167-gen-rabbit-dental-declined-de', '168-gen-rabbit-dental-declined-it', '010-vaccination-visit', '124-gen-dental-declined-en', '118-gen-suture-removal-en'];

describe('discharge letter', () => {
  it('renders in EN, DE and IT with the language\'s own template', () => {
    for (const [id, title, home] of [['112-gen-fleas-en', '# Discharge instructions', '## Home care'], ['113-gen-fleas-de', '# Entlassungsbrief', '## Pflege zu Hause'], ['114-gen-fleas-it', '# Lettera di dimissione', '## Cure a casa']] as const) {
      const { record, header, lang } = prep(id);
      const md = renderDischargeLetter(record, header, lang, { approved: true });
      expect(md.startsWith(title)).toBe(true);
      expect(md).toContain(home);
      expect(md).toContain(`## ${DISCHARGE_LABELS[lang].meds}`);
      expect(md).toContain(renderMedicationTable(record.medications.filter((m) => m.status === 'dispensed'), lang));
      expect(md).toContain(cap(record.plan.instructions[0].text));
      expect(md).toContain(`## ${DISCHARGE_LABELS[lang].next}\n${cap(record.plan.follow_up!.text)}`);
      expect(md).toContain(`_${REPORT_LABELS[lang].disclosure}_`);
      expect(md).not.toContain(REPORT_LABELS[lang].draft);
    }
  });

  it('shows the draft banner and no approval disclosure before approval, like the other documents', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const md = renderDischargeLetter(record, header, 'de');
    expect(md).toContain('_ENTWURF — KI-unterstützt, noch nicht geprüft_');
    expect(md).not.toContain(REPORT_LABELS.de.disclosure);
    expect(md).toContain('Von KI hinzugefügt: 0');
  });

  it('omits sections with nothing in the record instead of filling them', () => {
    const { record, header } = prep('118-gen-suture-removal-en');
    const md = renderDischargeLetter(record, header, 'en', { approved: true });
    expect(md).toContain('## Treatment during the stay\n- Sutures removed');
    for (const h of ['Medication to give at home', 'Home care', 'Follow-up appointment', 'When to call the clinic', 'Diagnostics and results', 'Planned and recommended', 'Declined care', 'Medication given in the clinic', '▲ Missing']) expect(md, h).not.toContain(`## ${h}`);
    expect(md.split('\n')).not.toContain(REPORT_LABELS.en.notRecorded);
    const empty: ClinicalRecord = { ...record, presenting_complaint: null, treatments: [], assessment: { text: null, differentials: [], source_spans: [] } };
    const bare = renderDischargeLetter(empty, header, 'en', { approved: true });
    expect(bare.split('\n').filter((l) => l.startsWith('## '))).toEqual([]);
  });

  it('shows "when to call the clinic" only when the plan says so, in the vet\'s words', () => {
    for (const id of ['106-gen-diarrhoea-declined-en', '107-gen-diarrhoea-declined-de', '108-gen-diarrhoea-declined-it', '130-gen-cystitis-cat-en', '131-gen-cystitis-cat-de', '132-gen-cystitis-cat-it']) {
      const { record, header, lang } = prep(id);
      const md = renderDischargeLetter(record, header, lang, { approved: true });
      expect(md, id).toContain(`## ${DISCHARGE_LABELS[lang].call}\n- ${cap(record.plan.follow_up!.text)}`);
      expect(md, id).not.toContain(`## ${DISCHARGE_LABELS[lang].next}`);
    }
    for (const id of ['121-gen-senior-weight-loss-en', '122-gen-senior-weight-loss-de', '123-gen-senior-weight-loss-it', '009-adversarial-other-pet', '143-gen-shorthand-gastro-de', '144-gen-shorthand-gastro-it', '112-gen-fleas-en']) {
      const { record, header, lang } = prep(id);
      const md = renderDischargeLetter(record, header, lang, { approved: true });
      expect(md, id).not.toContain(`## ${DISCHARGE_LABELS[lang].call}`);
    }
    expect(isCallInstruction('call with results')).toBe(false);
    expect(isCallInstruction('Anruf mit Ergebnissen')).toBe(false);
    expect(isCallInstruction('recheck if worse')).toBe(false);
    expect(isCallInstruction('avoid contact with other cats if possible')).toBe(false);
    expect(isCallInstruction('please phone us if she stops eating')).toBe(true);
    expect(isCallInstruction('bei Verschlechterung bitte sofort melden')).toBe(true);
    expect(isCallInstruction('contattateci in caso di vomito')).toBe(true);
  });

  it('shows declined care as declined and planned items as planned, never as done', () => {
    const { record, header } = prep('153-gen-pruritus-declined-dispensed-it');
    const md = renderDischargeLetter(record, header, 'it', { approved: true });
    expect(md).toContain('## Prestazioni rifiutate\n- Test allergologico su sangue (rifiutato dal proprietario)\n- Apoquel (rifiutato dal proprietario)');
    expect(md).toContain('- Raschiato cutaneo (pianificato)');
    const diag = md.split('## Esami e risultati')[1].split('\n## ')[0];
    expect(diag).not.toContain('Raschiato'); expect(diag).not.toContain('allergologico');
    const home = md.split('## Farmaci da somministrare a casa')[1].split('\n## ')[0];
    expect(home).not.toContain('Apoquel');
  });

  it('adds no text that is not in the record or the fixed template (all three languages)', () => {
    for (const id of CASES) {
      const { record, header, lang, notes } = prep(id);
      const md = renderDischargeLetter(record, header, lang, { approved: true });
      expect(unexplainedLines(md, record, header, lang), id).toEqual([]);
      // the check itself catches an added sentence, an added table value and an unknown heading
      expect(unexplainedLines(`${md}\n- Keep warm and quiet`, record, header, lang), id).toHaveLength(1);
      expect(unexplainedLines(`${md}\n## Diet`, record, header, lang), id).toHaveLength(1);
      expect(unexplainedLines(`${md}\n| Amoxicillin | 10 mg/kg | po | bid | 7 days | |`, record, header, lang).length, id).toBeGreaterThan(0);
      // the same numbers check the owner summary is held to
      const prose = md.split('\n## ▲')[0].split('\n').filter((l) => l && !l.startsWith('#') && !l.startsWith('_') && !l.startsWith('|') && !l.startsWith('**') && !l.includes('▲'));
      expect(validateDerivedText(prose.join('\n'), record, notes).filter((f) => f.severity === 'block'), id).toEqual([]);
    }
  });

  it('carries every medication detail identically to the other documents', () => {
    for (const id of ['002-milo-otitis-de', '160-gen-full-vs-drug-only-meds-en', '162-gen-full-vs-drug-only-meds-it', '007-adversarial-de-decimal-comma']) {
      const { record, header, lang } = prep(id);
      expect(crossDocumentMedicationCheck(record, { discharge: renderDischargeLetter(record, header, lang) }), id).toEqual([]);
    }
  });

  it('never computes a dose schedule: no checklist grid, values exactly as recorded', () => {
    const { record, header } = prep('002-milo-otitis-de');
    const md = renderDischargeLetter(record, header, 'de', { approved: true });
    expect(md).not.toContain('☐');
    const m = record.medications[0];
    const row = md.split('\n').find((l) => l.startsWith(`| ${m.drug}`))!;
    for (const v of [m.frequency, m.duration, m.route]) if (v) expect(row).toContain(v);
  });
});

describe('requiredMissing: discharge', () => {
  const med = (m: Partial<Medication>): Medication => ({ drug: 'meloxicam', class_as_written: null, dose: 0.1, dose_unit: 'mg/kg', route: 'po', frequency: 'sid', duration: '5 days', status: 'prescribed', source_spans: [[0, 1]], ...m } as Medication);
  const base = () => prep('002-milo-otitis-de');

  it('needs dose, route, frequency and duration for medication going home; the consult report does not need the duration', () => {
    const { record, header } = base();
    const r = { ...record, medications: [med({ dose: null, route: null, frequency: null, duration: null, status: 'dispensed' })] };
    expect(requiredMissing(r, 'discharge', header)).toEqual(expect.arrayContaining(['medications[0].dose', 'medications[0].route', 'medications[0].frequency', 'medications[0].duration']));
    expect(requiredMissing(r, 'consult_report', header)).not.toContain('medications[0].duration');
  });
  it('needs a follow-up or home-care instruction, and an assessment', () => {
    const { record, header } = base();
    const r = { ...record, plan: { follow_up: null, instructions: [] }, assessment: { text: null, differentials: [], source_spans: [] } };
    expect(requiredMissing(r, 'discharge', header)).toEqual(expect.arrayContaining(['plan', 'assessment']));
    expect(requiredMissing(r, 'consult_report', header)).not.toContain('plan');
    expect(requiredMissing(prep('112-gen-fleas-en').record, 'discharge')).not.toContain('plan');
  });
  it('keeps the vaccine exception: a vaccine given in the clinic needs no dose, frequency or duration (cases 010, 110, 111)', () => {
    for (const id of ['010-vaccination-visit', '110-gen-cat-vaccine-de', '111-gen-cat-vaccine-it']) {
      const { record, header } = prep(id);
      const miss = requiredMissing(record, 'discharge', header);
      for (const f of ['dose', 'frequency', 'duration']) expect(miss, id).not.toContain(`medications[0].${f}`);
    }
    const { record } = base();
    expect(requiredMissing({ ...record, medications: [med({ drug: 'RCP vaccine', status: 'dispensed', dose: null })] }, 'discharge')).toContain('medications[0].dose');
  });
  it('a complete fixture with medication going home needs nothing more for discharge (cases 103-105)', () => {
    for (const id of ['103-gen-otitis-cat-en', '104-gen-otitis-cat-de', '105-gen-otitis-cat-it']) {
      const { record, header } = prep(id);
      expect(requiredMissing(record, 'discharge', header), id).toEqual(requiredMissing(record, 'consult_report', header));
    }
  });
});
