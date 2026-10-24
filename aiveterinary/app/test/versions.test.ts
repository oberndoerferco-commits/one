import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord } from '../src/schema.js';
import { approve, amend, documentFrom, propagationMap, changedSections, fingerprint } from '../src/versions.js';

const rec = () => ClinicalRecord.parse(JSON.parse(readFileSync(new URL('../eval/cases/002-milo-otitis-de.json', import.meta.url), 'utf8')).fixture_record);

describe('approved versions', () => {
  it('an approved version cannot be edited', () => {
    const v1 = approve(rec(), 'Dr. A', '2026-10-16T09:00:00Z');
    expect(Object.isFrozen(v1.record)).toBe(true);
    expect(() => { (v1.record.medications as any)[0].dose = 99; }).toThrow();
  });
  it('the fingerprint is stable and ignores key order', () => {
    const a = rec();
    const reorder = (v: any): any => Array.isArray(v) ? v.map(reorder) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).reverse().map((k) => [k, reorder(v[k])])) : v;
    const b = reorder(a);
    expect(Object.keys(b)[0]).not.toBe(Object.keys(a)[0]);
    expect(fingerprint(b)).toBe(fingerprint(a));
    const c = rec(); c.examination.vitals.temperature!.value = 38.7;
    expect(fingerprint(c)).not.toBe(fingerprint(a));
  });
  it('an amendment needs a reason and a real change, and points back', () => {
    const v1 = approve(rec(), 'Dr. A');
    expect(() => amend(v1, rec(), 'Dr. A', 'typo')).toThrow('Nothing changed');
    const fixed = rec(); fixed.medications[0].route = 'aurikulär';
    expect(() => amend(v1, fixed, 'Dr. A', '  ')).toThrow('reason');
    const v2 = amend(v1, fixed, 'Dr. A', 'Applikationsweg ergänzt');
    expect(v2.version).toBe(2); expect(v2.supersedes).toBe(1); expect(v1.record.medications[0].route).toBeNull();
    expect(changedSections(v1.record, v2.record)).toEqual(['medications']);
  });
  it('documents from the old version are listed for regeneration', () => {
    const v1 = approve(rec(), 'Dr. A');
    const docs = [documentFrom(v1, 'report', 'de'), documentFrom(v1, 'owner', 'de'), documentFrom(v1, 'rx', 'de')];
    const fixed = rec(); fixed.medications[0].route = 'aurikulär';
    const v2 = amend(v1, fixed, 'Dr. A', 'Applikationsweg ergänzt');
    const regenerated = documentFrom(v2, 'report', 'de');
    const map = propagationMap(v2, [...docs, regenerated]);
    expect(map.stale.map((d) => d.kind)).toEqual(['report', 'owner', 'rx']);
    expect(map.current.map((d) => d.id)).toEqual(['report-de-v2']);
  });
});
