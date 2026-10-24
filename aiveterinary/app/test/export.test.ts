import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord } from '../src/schema.js';
import { approve } from '../src/versions.js';
import { soapFields, exportBundle } from '../src/export.js';

const dir = new URL('../eval/cases/', import.meta.url);
const cases = readdirSync(dir).filter((f) => f.endsWith('.json')).map((f) => JSON.parse(readFileSync(new URL(f, dir), 'utf8'))).filter((c) => c.fixture_record);
const rec = (c: any) => ClinicalRecord.parse(c.fixture_record);
const header = { name: 'Test', species: 'dog' as const };
const LABELS = /^(Reason|Owner reports|Temperature|Heart rate|Respiratory rate|Weight|CRT|Differentials|Follow-up|Missing|Not recorded|planned|performed|declined by owner|recommended|dispensed|prescribed|▲)$/;

describe('SOAP fields', () => {
  it('always gives four fields in S, O, A, P order', () => {
    for (const c of cases) expect(soapFields(rec(c)).map((f) => f.key)).toEqual(['S', 'O', 'A', 'P']);
  });
  it('adds no text that is not in the record', () => {
    for (const c of cases) {
      const r = rec(c); const json = JSON.stringify(r);
      for (const f of soapFields(r, 'en')) for (const line of f.text.split('\n'))
        for (const part of line.split(/ · |: |; |, | \(|\)|▲ /).map((s) => s.trim()).filter((s) => s && !LABELS.test(s)))
          expect(json.includes(part) || /^(Temperature|Heart rate|Respiratory rate|Weight|CRT) -?\d+(\.\d+)? \S+$/.test(part) || /^-?\d+(\.\d+)? \S+$/.test(part), `"${part}"`).toBe(true);
    }
  });
  it('flags a missing dose instead of filling it', () => {
    const r = rec(cases.find((c) => c.fixture_record.medications?.some((m: any) => m.dose == null)));
    expect(soapFields(r, 'en').find((f) => f.key === 'P')!.text).toContain('▲ Missing: dose');
  });
  it('shows what the vet entered at approval instead of the missing flag', () => {
    const c = cases.find((x) => x.fixture_record.missing?.length);
    const r = rec(c); const f = r.missing[0].field;
    const p = soapFields(r, 'en', { [f]: 'Not recorded' }).find((x) => x.key === 'P')!.text;
    expect(p).not.toContain(`▲ Missing: ${f}`);
    expect(p).toContain(`Entered by the vet at approval:\n${f}: Not recorded`);
  });
  it('localises labels', () => {
    expect(soapFields(rec(cases[0]), 'de')[0].label).toBe('Anamnese (S)');
    expect(soapFields(rec(cases[0]), 'it')[3].label).toBe('Piano (P)');
  });
});

describe('export bundle', () => {
  it('carries provenance from the approved version', () => {
    const v = approve(rec(cases[0]), 'Dr. A', '2026-10-18T10:00:00Z');
    const b = exportBundle(v, header, 'en', '2026-10-18T10:05:00Z');
    expect(b.provenance).toMatchObject({ ai_assisted: true, content_added_by_ai: 0, version: 1, approved_by: 'Dr. A', fingerprint: v.fingerprint });
    expect(b.soap).toHaveLength(4);
    expect(JSON.parse(JSON.stringify(b)).record).toEqual(v.record);
  });
  it('refuses a record that changed after approval', () => {
    const v = approve(rec(cases[0]), 'Dr. A');
    const tampered = { ...v, record: { ...v.record, missing: [] , uncertain: [{ field: 'x', original_text: 'x', reason: 'x', source_spans: [[0, 1]] }] } } as any;
    expect(() => exportBundle(tampered, header)).toThrow(/export refused/);
  });
});
