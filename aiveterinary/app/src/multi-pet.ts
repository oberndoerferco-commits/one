import type { ClinicalRecord, PatientHeader, Span } from './schema.js';
import { validateAll, factSpans, type Finding } from './validators.js';
import { factPaths } from './metrics.js';
import { renderOwnerSummary, headerLine, OWNER_LABELS, REPORT_LABELS, type Lang } from './render.js';
import { provenance } from './country.js';

/**
 * Multi-pet consultations: one set of notes, several patients.
 *
 * Each patient keeps its own locked header and its own ClinicalRecord; every record's spans point
 * into the same shared notes. The vet assigns each note line to one patient or to "shared" (said
 * for all animals, e.g. owner instructions). Nothing is assigned automatically: a line that starts
 * with a patient's name label ("Milo: …") is offered as a suggestion, and only the vet's
 * confirmation puts it into the assignment.
 *
 * Checks, per patient: the usual validateAll on that patient's record against its view of the shared
 * notes (patientView: other animals' lines blanked, offsets kept), plus
 *  - wrong_animal_line (block): a fact whose source lies on a line assigned to another patient;
 *  - unassigned_line_fact (block): a fact whose source lies on a line not assigned yet.
 * Facts on shared lines are allowed for every patient. other_animal_fact keeps running unchanged:
 * a sentence that names "the other dog" still warns, whoever the line is assigned to.
 * Consultation-level warnings: unassigned_line (a line not assigned to anyone) and label_mismatch
 * (a line labelled "Milo:" assigned to someone else).
 */

export const SHARED = 'shared' as const;
/** A patient id, or SHARED. */
export type LineTarget = string;
/** Line index (0-based, in the normalised notes) → patient id or SHARED. Absent = not assigned. */
export type Assignment = Readonly<Record<number, LineTarget>>;

export type ConsultationPatient = { id: string; header: PatientHeader; record: ClinicalRecord };
export type Consultation = { notes: string; patients: ConsultationPatient[]; assignment: Assignment };

export type NoteLine = { index: number; start: number; end: number; text: string; blank: boolean };

/** The lines of the notes with their offsets (end excludes the newline). */
export function noteLines(notes: string): NoteLine[] {
  const out: NoteLine[] = []; let start = 0;
  notes.split('\n').forEach((text, index) => { out.push({ index, start, end: start + text.length, text, blank: !text.trim() }); start += text.length + 1; });
  return out;
}

/** The line indices a span touches (leading/trailing newlines ignored; an empty span counts at its start). */
export function spanLineIndices(notes: string, [a, b]: Span, lines = noteLines(notes)): number[] {
  while (a < b && notes[a] === '\n') a++;
  while (b > a && notes[b - 1] === '\n') b--;
  return lines.filter((l) => (b > a ? a <= l.end && b > l.start : a >= l.start && a <= l.end)).map((l) => l.index);
}

const checkPatients = (patients: { id: string }[]) => {
  const ids = patients.map((p) => p.id);
  for (const id of ids) {
    if (!id || id === SHARED) throw new Error(`Invalid patient id "${id}".`);
  }
  if (new Set(ids).size !== ids.length) throw new Error('Patient ids must be unique.');
  return new Set(ids);
};

export type AssignedLine = NoteLine & { target: LineTarget | null };
export type LineAssignment = { assignment: Assignment; lines: AssignedLine[]; unassigned: number[] };

/**
 * The vet's assignment of note lines to patients, checked and normalised. `assignment` maps a line
 * index to a patient id or SHARED (`null` or absent = not assigned). Unknown patients, blank lines
 * and lines outside the notes are refused. Nothing is filled in: suggestions are not applied here.
 */
export function assignLines(notes: string, patients: { id: string }[], assignment: Record<number, LineTarget | null | undefined>): LineAssignment {
  const ids = checkPatients(patients);
  const lines = noteLines(notes);
  const out: Record<number, LineTarget> = {};
  for (const [k, target] of Object.entries(assignment)) {
    if (target == null) continue;
    const i = Number(k);
    if (!Number.isInteger(i) || i < 0 || i >= lines.length) throw new Error(`Line ${k} is not in the notes.`);
    if (lines[i].blank) throw new Error(`Line ${i + 1} is blank and cannot be assigned.`);
    if (target !== SHARED && !ids.has(target)) throw new Error(`Unknown patient "${target}".`);
    out[i] = target;
  }
  const assigned = lines.map((l) => ({ ...l, target: out[l.index] ?? null }));
  return { assignment: Object.freeze(out), lines: assigned, unassigned: assigned.filter((l) => !l.blank && l.target == null).map((l) => l.index) };
}

/** A new assignment with one line set (`null` clears it). Checked like assignLines. */
export function setLine(notes: string, patients: { id: string }[], assignment: Assignment, line: number, target: LineTarget | null): Assignment {
  return assignLines(notes, patients, { ...assignment, [line]: target }).assignment;
}

export type Suggestion = { line: number; target: string; label: string; reason: 'name_label' };

const fold = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');
const escRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** The patient a line's name label names ("Milo:", "- Milo:"), or null. Names shared by two patients name nobody. */
export function labelledPatient(text: string, patients: { id: string; header: PatientHeader }[]): { id: string; label: string } | null {
  const hits = patients.filter((p) => p.header.name?.trim() && new RegExp(`^\\s*(?:[-*•]\\s*)?${escRe(fold(p.header.name.trim()))}\\s*:`).test(fold(text)));
  if (hits.length !== 1) return null;
  const sameName = patients.filter((p) => fold(p.header.name.trim()) === fold(hits[0].header.name.trim()));
  if (sameName.length !== 1) return null;
  return { id: hits[0].id, label: hits[0].header.name.trim() };
}

/**
 * Suggestions only: unassigned, non-blank lines that start with exactly one patient's name label.
 * The vet confirms each (confirmSuggestion) or assigns the line differently; nothing is applied here.
 */
export function suggestAssignments(notes: string, patients: { id: string; header: PatientHeader }[], assignment: Assignment = {}): Suggestion[] {
  checkPatients(patients);
  return noteLines(notes).flatMap((l) => {
    if (l.blank || assignment[l.index] != null) return [];
    const hit = labelledPatient(l.text, patients);
    return hit ? [{ line: l.index, target: hit.id, label: hit.label, reason: 'name_label' as const }] : [];
  });
}

/** Applies one suggestion the vet confirmed. */
export function confirmSuggestion(notes: string, patients: { id: string }[], assignment: Assignment, s: Suggestion): Assignment {
  return setLine(notes, patients, assignment, s.line, s.target);
}

export function makeConsultation(notes: string, patients: ConsultationPatient[], assignment: Record<number, LineTarget | null | undefined> = {}): Consultation {
  return { notes, patients, assignment: assignLines(notes, patients, assignment).assignment };
}

const nameOf = (c: Consultation, id: string) => c.patients.find((p) => p.id === id)?.header.name ?? id;
const quote = (s: string) => (s.length > 80 ? s.slice(0, 77) + '…' : s).trim();

/** Facts of one patient's record whose source lies on another patient's line, or on a line not assigned yet. */
export function validateCrossPatient(c: Consultation, patientId: string): Finding[] {
  const p = c.patients.find((x) => x.id === patientId);
  if (!p) throw new Error(`Unknown patient "${patientId}".`);
  const lines = noteLines(c.notes);
  const f: Finding[] = [];
  for (const path of factPaths(p.record)) {
    let other: { line: number; owner: string; span: Span } | null = null; let open: { line: number; span: Span } | null = null;
    for (const span of factSpans(p.record, path)) for (const i of spanLineIndices(c.notes, span, lines)) {
      const t = c.assignment[i];
      if (t == null) open ??= { line: i, span };
      else if (t !== SHARED && t !== patientId) other ??= { line: i, owner: t, span };
    }
    if (other) f.push({ rule: 'wrong_animal_line', severity: 'block', field: path, message: `This comes from line ${other.line + 1} ("${quote(lines[other.line].text)}"), which is assigned to ${nameOf(c, other.owner)}. It cannot be in ${p.header.name}'s record.`, span: other.span, params: { line: other.line + 1, quote: quote(lines[other.line].text), owner: nameOf(c, other.owner), patient: p.header.name } });
    else if (open) f.push({ rule: 'unassigned_line_fact', severity: 'block', field: path, message: `This comes from line ${open.line + 1} ("${quote(lines[open.line].text)}"), which is not assigned to an animal yet. Assign the line first.`, span: open.span, params: { line: open.line + 1, quote: quote(lines[open.line].text) } });
  }
  return f;
}

export type ConsultationFindings = { byPatient: Record<string, Finding[]>; consultation: Finding[]; blocked: boolean };

/**
 * One patient's view of the shared notes: the lines assigned to another patient are blanked with
 * spaces, so offsets (and every span) stay the same. Own, shared and unassigned lines stay visible.
 * Without this, the cat's "T 38.4" would read as a second temperature in the dog's record
 * (notes_contradiction) on every two-pet visit.
 */
export function patientView(c: Consultation, patientId: string): string {
  return noteLines(c.notes).map((l) => { const t = c.assignment[l.index]; return t != null && t !== SHARED && t !== patientId ? ' '.repeat(l.text.length) : l.text; }).join('\n');
}

/**
 * Per patient: validateAll on that patient's record against its view of the shared notes (other
 * animals' lines blanked, offsets kept), then the cross-patient check; plus the consultation-level
 * warnings. A fact on another animal's line is therefore reported as wrong_animal_line first, and
 * its grounding findings say what is missing from this patient's view.
 */
export function validateConsultation(c: Consultation): ConsultationFindings {
  const { lines, unassigned } = assignLines(c.notes, c.patients, c.assignment);
  const byPatient: Record<string, Finding[]> = {};
  for (const p of c.patients) byPatient[p.id] = [...validateCrossPatient(c, p.id), ...validateAll(p.record, patientView(c, p.id), p.header)];
  const consultation: Finding[] = [];
  for (const i of unassigned) consultation.push({ rule: 'unassigned_line', severity: 'warn', field: `notes.line[${i + 1}]`, message: `Line ${i + 1} ("${quote(lines[i].text)}") is not assigned to an animal or marked shared.`, span: [lines[i].start, lines[i].end], params: { line: i + 1, quote: quote(lines[i].text) } });
  for (const l of lines) {
    if (l.target == null) continue;
    const named = labelledPatient(l.text, c.patients);
    if (named && named.id !== l.target) consultation.push({ rule: 'label_mismatch', severity: 'warn', field: `notes.line[${l.index + 1}]`, message: `Line ${l.index + 1} starts with "${named.label}:" but is assigned to ${l.target === SHARED ? 'all animals (shared)' : nameOf(c, l.target)}. Check the assignment.`, span: [l.start, l.end], params: { line: l.index + 1, label: named.label, shared: l.target === SHARED, target: l.target === SHARED ? '' : nameOf(c, l.target) } });
  }
  const blocked = Object.values(byPatient).some((fs) => fs.some((x) => x.severity === 'block')) || consultation.some((x) => x.severity === 'block');
  return { byPatient, consultation, blocked };
}

/** Each patient's own document from an existing single-patient renderer, called unchanged. */
export function renderPerPatient(c: Consultation, render: (record: ClinicalRecord, header: PatientHeader) => string): { id: string; name: string; text: string }[] {
  return c.patients.map((p) => ({ id: p.id, name: p.header.name, text: render(p.record, p.header) }));
}

export const MULTI_LABELS = {
  en: { and: 'and', shared: 'For all animals' },
  de: { and: 'und', shared: 'Für alle Tiere' },
  it: { and: 'e', shared: 'Per tutti gli animali' },
};

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const joinNames = (names: string[], lang: Lang) => (names.length < 2 ? names.join('') : `${names.slice(0, -1).join(', ')} ${MULTI_LABELS[lang].and} ${names[names.length - 1]}`);

/**
 * One owner letter for a multi-pet visit: one section per animal, built by renderOwnerSummary on
 * that animal's record (so each medication table and dose checklist is exactly the one the animal's
 * own summary prints; nothing is merged across animals), then the home instructions written on
 * shared lines once, then one provenance line for all records. Home instructions (plan instructions
 * and recommended advice) whose every source line is shared are moved to the shared section and
 * de-duplicated by text; everything else stays with its animal.
 */
export function renderOwnerLetterMulti(c: Consultation, lang: Lang = 'en', opts: { approved?: boolean } = {}): string {
  const t = REPORT_LABELS[lang], d = OWNER_LABELS[lang], m = MULTI_LABELS[lang];
  const lines = noteLines(c.notes);
  const onShared = (spans: Span[]) => spans.length > 0 && spans.every((s) => spanLineIndices(c.notes, s, lines).every((i) => c.assignment[i] === SHARED));
  const shared: string[] = [];
  const addShared = (text: string) => { const x = `- ${cap(text)}`; if (!shared.includes(x)) shared.push(x); };
  const out: string[] = [`# ${d.ownerTitle}`];
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${d.forOwner} ${joinNames(c.patients.map((p) => p.header.name), lang)}**`);
  for (const p of c.patients) {
    const r = p.record;
    const instructions = r.plan.instructions.filter((i) => { if (onShared(i.source_spans)) { addShared(i.text); return false; } return true; });
    const treatments = r.treatments.filter((x) => { if (x.status === 'recommended' && x.type === 'advice' && onShared(x.source_spans)) { addShared(x.text); return false; } return true; });
    const own: ClinicalRecord = { ...r, treatments, plan: { ...r.plan, instructions } };
    const body = renderOwnerSummary(own, p.header, lang, { approved: opts.approved }).split('\n');
    out.push('');
    out.push(`## ${headerLine(p.header, lang)}`);
    // Drop the summary's own title, its "for the owner of" line and its italic lines (draft, provenance,
    // disclosure: printed once for the whole letter); every heading moves one level down.
    for (const line of body.slice(1)) {
      if (/^_.*_$/.test(line) || line.startsWith(`**${d.forOwner} `)) continue;
      out.push(line.startsWith('#') ? `#${line}` : line);
    }
  }
  if (shared.length) { out.push(''); out.push(`## ${m.shared}`); out.push(`### ${d.home}`); out.push(...shared); }
  const facts = c.patients.reduce((n, p) => n + provenance(p.record).facts, 0);
  const notRecorded = c.patients.reduce((n, p) => n + provenance(p.record).not_recorded, 0);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(facts)).replace('{n}', String(notRecorded))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n').replace(/\n{3,}/g, '\n\n');
}
