import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll } from '../src/validators.js';
import { wilson, scoreFacts, factPaths } from '../src/metrics.js';

const load = (f: string) => JSON.parse(readFileSync(new URL(`../eval/cases/${f}`, import.meta.url), 'utf8'));

describe('Wilson interval', () => {
  it('matches known values', () => {
    // 8/10 → 0.4902–0.9433 (standard Wilson 95 % interval)
    const r = wilson(8, 10);
    expect(r.lo).toBeCloseTo(0.4902, 3); expect(r.hi).toBeCloseTo(0.9433, 3);
  });
  it('does not collapse at 0 or n', () => {
    expect(wilson(0, 50).hi).toBeGreaterThan(0.05);
    expect(wilson(50, 50).lo).toBeLessThan(0.95);
    expect(wilson(0, 0).rate).toBeNull();
  });
});

describe('fact scoring', () => {
  it('a clean fixture has no unsupported facts', () => {
    const c = load('001-luna-vomiting.json');
    const notes = normalizeNotes(c.notes); const r = ClinicalRecord.parse(c.fixture_record);
    const s = scoreFacts(r, validateAll(r, notes, PatientHeader.parse(c.header)));
    expect(s.facts).toBe(factPaths(r).length); expect(s.unsupported).toBe(0);
  });
  it('the hallucinated fixture is counted as unsupported', () => {
    const c = load('005-hallucinated-fixture.json');
    const notes = normalizeNotes(c.notes); const r = ClinicalRecord.parse(c.fixture_record);
    const s = scoreFacts(r, validateAll(r, notes, PatientHeader.parse(c.header)));
    expect(s.unsupported).toBeGreaterThan(0);
  });
});
