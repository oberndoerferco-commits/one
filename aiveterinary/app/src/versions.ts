import type { ClinicalRecord } from './schema.js';

/**
 * Approved versions and amendment propagation.
 *
 * An approved record is never edited. A correction creates the next version,
 * which keeps a pointer to the one it replaces and the reason. Every document
 * remembers the version it was generated from, so after an amendment the
 * clinic sees exactly which documents are now stale.
 *
 * The fingerprint is for change detection inside the app. Tamper evidence
 * comes from append-only storage on the server, not from this hash.
 */

export type ApprovedVersion = Readonly<{
  version: number;
  record: ClinicalRecord;
  approved_by: string;
  approved_at: string;
  fingerprint: string;
  supersedes: number | null;
  amendment_reason: string | null;
}>;

export type GeneratedDocument = Readonly<{ id: string; kind: string; lang: string; from_version: number; from_fingerprint: string }>;

/** Stable JSON: keys sorted, so the same record always gives the same fingerprint. */
function stable(v: unknown): string {
  if (Array.isArray(v)) return `[${v.map(stable).join(',')}]`;
  if (v && typeof v === 'object') return `{${Object.keys(v as object).sort().map((k) => `${JSON.stringify(k)}:${stable((v as any)[k])}`).join(',')}}`;
  return JSON.stringify(v);
}

/** FNV-1a 64-bit over the stable JSON, hex. Pure JS so it runs in the browser too. */
export function fingerprint(record: ClinicalRecord): string {
  let h = 0xcbf29ce484222325n; const p = 0x100000001b3n; const m = 0xffffffffffffffffn;
  for (const ch of stable(record)) { h ^= BigInt(ch.codePointAt(0)!); h = (h * p) & m; }
  return h.toString(16).padStart(16, '0');
}

function deepFreeze<T>(o: T): T {
  if (o && typeof o === 'object' && !Object.isFrozen(o)) { Object.freeze(o); for (const v of Object.values(o as object)) deepFreeze(v); }
  return o;
}

export function approve(record: ClinicalRecord, by: string, at = new Date().toISOString()): ApprovedVersion {
  const copy = structuredClone(record);
  return deepFreeze({ version: 1, record: copy, approved_by: by, approved_at: at, fingerprint: fingerprint(copy), supersedes: null, amendment_reason: null });
}

/** A correction never touches the previous version; it returns the next one. A reason is required. */
export function amend(previous: ApprovedVersion, corrected: ClinicalRecord, by: string, reason: string, at = new Date().toISOString()): ApprovedVersion {
  if (!reason.trim()) throw new Error('An amendment needs a reason.');
  const copy = structuredClone(corrected);
  const fp = fingerprint(copy);
  if (fp === previous.fingerprint) throw new Error('Nothing changed; no new version created.');
  return deepFreeze({ version: previous.version + 1, record: copy, approved_by: by, approved_at: at, fingerprint: fp, supersedes: previous.version, amendment_reason: reason.trim() });
}

export function documentFrom(v: ApprovedVersion, kind: string, lang: string, id = `${kind}-${lang}-v${v.version}`): GeneratedDocument {
  return Object.freeze({ id, kind, lang, from_version: v.version, from_fingerprint: v.fingerprint });
}

/** Which sections differ between two versions, by top-level field, for the amendment banner. */
export function changedSections(a: ClinicalRecord, b: ClinicalRecord): string[] {
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  return [...keys].filter((k) => stable((a as any)[k]) !== stable((b as any)[k])).sort();
}

/** After an amendment: every document generated from an older version is stale and listed for regeneration. */
export function propagationMap(current: ApprovedVersion, docs: GeneratedDocument[]): { stale: GeneratedDocument[]; current: GeneratedDocument[] } {
  const stale = docs.filter((d) => d.from_fingerprint !== current.fingerprint);
  return { stale, current: docs.filter((d) => d.from_fingerprint === current.fingerprint) };
}
