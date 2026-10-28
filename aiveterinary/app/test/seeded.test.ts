import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync, mkdtempSync, writeFileSync, copyFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, type Finding } from '../src/validators.js';
import { scoreSeeded } from '../src/metrics.js';
import { runEval } from '../src/cli/eval.js';

const casesDir = fileURLToPath(new URL('../eval/cases/', import.meta.url));
const seededFiles = readdirSync(casesDir).filter((f) => /^2\d\d-seeded-.*\.json$/.test(f)).sort();
const load = (f: string) => JSON.parse(readFileSync(join(casesDir, f), 'utf8'));
const finding = (rule: string, severity: Finding['severity'] = 'warn', field = 'x'): Finding => ({ rule, severity, field, message: '' } as Finding);

describe('scoreSeeded', () => {
  it('counts each must_flag rule as one seeded error, caught when raised', () => {
    expect(scoreSeeded(['a', 'b'], [finding('a')])).toEqual({ seeded: 2, caught: 1, missed: ['b'], stray_blocks: [] });
    expect(scoreSeeded(['a'], [finding('a', 'block'), finding('a')])).toEqual({ seeded: 1, caught: 1, missed: [], stray_blocks: [] });
  });
  it('reports blocking findings from other rules as strays, but not warnings', () => {
    const s = scoreSeeded(['a'], [finding('a'), finding('c', 'block', 'meds[0]'), finding('d', 'warn')]);
    expect(s.stray_blocks).toEqual(['c@meds[0]']);
  });
});

describe('seeded-error cases on disk', () => {
  it('one case per rule and language', () => {
    const byRule: Record<string, string[]> = {};
    for (const f of seededFiles) { const c = load(f); for (const r of c.expect.must_flag) (byRule[r] ??= []).push(c.language); }
    for (const r of ['status_conflicts_source', 'notes_contradiction', 'other_animal_fact', 'owner_report_as_finding', 'dose_not_in_notes', 'source_required']) expect(byRule[r]?.sort()).toEqual(['de', 'en', 'it']);
    expect(seededFiles).toHaveLength(18);
  });
  it.each(seededFiles)('%s raises its must_flag rule and nothing else', (f) => {
    const c = load(f);
    const findings = validateAll(ClinicalRecord.parse(c.fixture_record), normalizeNotes(c.notes), PatientHeader.parse(c.header));
    expect([...new Set(findings.map((x) => x.rule))].sort()).toEqual([...c.expect.must_flag].sort());
  });
});

describe('harness on seeded cases', () => {
  const run = async (mutate?: (c: any) => void) => {
    const dir = mkdtempSync(join(tmpdir(), 'aivet-seeded-')); const out = join(dir, 'out');
    copyFileSync(join(casesDir, '001-luna-vomiting.json'), join(dir, '001.json'));
    const c = load('200-seeded-status-conflict-en.json'); mutate?.(c);
    writeFileSync(join(dir, '200.json'), JSON.stringify(c));
    const failures = await runEval('fixture', false, { casesDir: dir, outDir: out, quiet: true });
    return { failures, result: JSON.parse(readFileSync(join(out, 'fixture.json'), 'utf8')) };
  };
  it('passes a caught seeded error and keeps its findings out of the other counts', async () => {
    const { failures, result } = await run();
    expect(failures).toBe(0);
    expect(result.metrics.seeded_error_detection).toMatchObject({ k: 1, n: 1 });
    expect(result.metrics.cases_with_blocking_finding).toMatchObject({ k: 0, n: 1 });
    expect(result.blocking).toBe(0);
    expect(result.seeded).toMatchObject({ cases: 1, errors: 1, caught: 1, blocking: 1 });
    expect(result.cases).toBe(2);
    expect(result.per_case.map((p: any) => p.id)).toContain('200-seeded-status-conflict-en');
  });
  it('fails the case when the named rule is not raised', async () => {
    const { failures, result } = await run((c) => (c.fixture_record.diagnostics[0].status = 'declined'));
    expect(failures).toBe(1);
    expect(result.metrics.seeded_error_detection).toMatchObject({ k: 0, n: 1 });
    expect(result.per_case.find((p: any) => p.id.startsWith('200')).pass).toBe(false);
  });
  it('fails the case on a blocking finding besides the seeded error', async () => {
    const { failures } = await run((c) => c.fixture_record.medications.push({ drug: 'Doxycycline', class_as_written: null, dose: null, dose_unit: null, route: null, frequency: null, duration: null, status: 'prescribed', source_spans: [[0, 5]] }));
    expect(failures).toBe(1);
  });
});
