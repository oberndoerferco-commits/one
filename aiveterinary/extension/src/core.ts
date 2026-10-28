import { soapFields, type ExportBundle, type ExportLang, type SoapField } from '../../app/src/export.js';
import { fingerprint } from '../../app/src/versions.js';

/**
 * The extension's rules, kept free of browser APIs so they run in vitest too.
 *
 * Input is only the JSON from app/src/export.ts. There is no signature in that
 * format, so "approved and untampered" means: the approval fields are present,
 * the record still hashes to the approval fingerprint (the same FNV-1a function
 * the app uses), the four SOAP texts are exactly what the app derives from that
 * record, and the patient header agrees with the record's own patient facts.
 */

export type Refusal = 'not_json' | 'wrong_format' | 'not_approved' | 'fingerprint' | 'soap_changed' | 'patient_missing' | 'patient_changed';
export type Verified = { ok: true; bundle: ExportBundle; lang: ExportLang } | { ok: false; reason: Refusal };

export const SPECIES = ['dog', 'cat', 'rabbit', 'ferret', 'horse', 'bird', 'reptile', 'other'] as const;
const LANGS: ExportLang[] = ['en', 'de', 'it'];

const no = (reason: Refusal): Verified => ({ ok: false, reason });
const isText = (s: unknown): s is string => typeof s === 'string' && s.trim() !== '';
const sameSoap = (a: SoapField[], b: unknown) => Array.isArray(b) && b.length === a.length
  && a.every((f, i) => b[i] && b[i].key === f.key && b[i].label === f.label && b[i].text === f.text);

/** Case and spacing only; no other normalisation, no similarity score. */
export const norm = (s: string) => s.normalize('NFC').replace(/\s+/g, ' ').trim().toLocaleLowerCase();

export function verifyExport(text: string): Verified {
  let b: any;
  try { b = JSON.parse(text); } catch { return no('not_json'); }
  if (!b || typeof b !== 'object' || b.format !== 'aiveterinary.export/1') return no('wrong_format');

  const p = b.provenance;
  if (!p || !isText(p.approved_by) || !isText(p.approved_at) || Number.isNaN(Date.parse(p.approved_at))
    || !Number.isInteger(p.version) || p.version < 1 || p.ai_assisted !== true || p.content_added_by_ai !== 0
    || !isText(p.fingerprint) || !b.record || typeof b.record !== 'object') return no('not_approved');
  // An amendment is only valid with its reason, as in versions.ts.
  if (p.supersedes !== null && !isText(p.amendment_reason)) return no('not_approved');

  let fp: string;
  try { fp = fingerprint(b.record); } catch { return no('fingerprint'); }
  if (fp !== p.fingerprint) return no('fingerprint');

  const h = b.patient;
  if (!h || !isText(h.name) || !SPECIES.includes(h.species)) return no('patient_missing');
  const rp = b.record.patient ?? {};
  if ((rp.name && norm(rp.name) !== norm(h.name)) || (rp.species && rp.species !== h.species)) return no('patient_changed');

  // Resolutions are typed by the vet at approval and are not inside the fingerprint; they must at least be plain strings.
  const res = b.resolutions_at_approval ?? {};
  if (typeof res !== 'object' || Object.values(res).some((v) => typeof v !== 'string')) return no('soap_changed');
  for (const lang of LANGS) {
    try { if (sameSoap(soapFields(b.record, lang, res), b.soap)) return { ok: true, bundle: b as ExportBundle, lang }; } catch { return no('soap_changed'); }
  }
  return no('soap_changed');
}

/** Words a PIMS may show for each species (EN/DE/IT, plus Latin and common clinical terms). "other" cannot be locked. */
export const SPECIES_WORDS: Record<string, string[]> = {
  dog: ['dog', 'canine', 'canis', 'canis lupus familiaris', 'hund', 'hündin', 'rüde', 'cane', 'cagna'],
  cat: ['cat', 'feline', 'felis catus', 'katze', 'kater', 'gatto', 'gatta'],
  rabbit: ['rabbit', 'kaninchen', 'coniglio'],
  ferret: ['ferret', 'frettchen', 'furetto'],
  horse: ['horse', 'equine', 'pferd', 'cavallo'],
  bird: ['bird', 'avian', 'vogel', 'uccello'],
  reptile: ['reptile', 'reptil', 'rettile'],
  other: [],
};

export type PageHeader = { name: string; species: string };
export type Mismatch = { field: 'name' | 'species'; expected: string; found: string };

/** Exact comparison of what the PIMS shows against the export. Any mismatch blocks the paste. */
export function checkPatient(patient: { name: string; species: string }, page: PageHeader): Mismatch[] {
  const out: Mismatch[] = [];
  if (!page.name.trim() || norm(page.name) !== norm(patient.name)) out.push({ field: 'name', expected: patient.name, found: page.name.trim() });
  if (!(SPECIES_WORDS[patient.species] ?? []).includes(norm(page.species))) out.push({ field: 'species', expected: patient.species, found: page.species.trim() });
  return out;
}

export const TARGETS = ['name', 'species', 'S', 'O', 'A', 'P'] as const;
export type Target = (typeof TARGETS)[number];
export type Mapping = Record<Target, string>;
export const mappingKey = (origin: string) => `map:${origin}`;

export type Row = { key: 'S' | 'O' | 'A' | 'P'; label: string; selector: string; chars: number; ok: boolean };
export type PasteResult =
  | { ok: true; rows: Row[] }
  | { ok: false; reason: 'refused'; detail: Refusal }
  | { ok: false; reason: 'no_mapping' | 'field_missing' | 'not_empty'; detail: string }
  | { ok: false; reason: 'mismatch'; mismatches: Mismatch[] };

/** The message for a blocked paste; `msg` is chrome.i18n.getMessage in the browser. */
export function describe(r: Exclude<PasteResult, { ok: true }>, msg: (k: string, subs?: string[]) => string): string {
  if (r.reason === 'mismatch') return [...r.mismatches.map((m) => msg(m.field === 'name' ? 'mismatchName' : 'mismatchSpecies', [m.found || '—', m.expected])), msg('mismatchHelp')].join(' ');
  if (r.reason === 'refused') return msg('refused_' + r.detail);
  return msg(r.reason, [r.detail]);
}
