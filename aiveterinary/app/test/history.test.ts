import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord } from '../src/schema.js';
import { approve, amend } from '../src/versions.js';
import { renderHistoryRecap, latestPerVisit } from '../src/history.js';

const rec = (f: string) => ClinicalRecord.parse(JSON.parse(readFileSync(new URL(`../eval/cases/${f}`, import.meta.url), 'utf8')).fixture_record);

describe('history recap', () => {
  const r1 = rec('002-milo-otitis-de.json');
  const v1 = approve(r1, 'Dr. A', '2026-03-01T09:00:00Z');
  const fixed = rec('002-milo-otitis-de.json'); fixed.medications[0].route = 'aurikulär';
  const v2 = amend(v1, fixed, 'Dr. A', 'Applikationsweg ergänzt');
  const visits = [{ visit_id: 'k2', date: '2026-03-01', versions: [v1, v2] }];

  it('uses only the latest approved version of each visit', () => {
    expect(latestPerVisit(visits)[0].v.version).toBe(2);
    const md = renderHistoryRecap(visits, 'de');
    expect(md).toContain('aurikulär');
    expect(md).not.toContain('v1]');
  });
  it('every content line points to a visit and version', () => {
    const md = renderHistoryRecap(visits, 'en');
    for (const line of md.split('\n').filter((l) => l.startsWith('- '))) expect(line).toMatch(/\[\d{4}-\d{2}-\d{2} · k2 v2\]$/);
  });
  it('adds no text that is not in the record', () => {
    const md = renderHistoryRecap(visits, 'en');
    const body = md.split('\n').filter((l) => l.startsWith('- ')).map((l) => l.replace(/\s*\[[^\]]+\]$/, '').replace(/^- /, ''));
    const json = JSON.stringify(v2.record);
    for (const line of body) for (const part of line.split(/ — | · |: | \(|\)/).map((s) => s.trim()).filter((s) => s && !/^(Reason|Assessment|Follow-up|given|planned|recommended|dispensed|prescribed)$/.test(s)))
      expect(json.includes(part) || /^[\d.]+ ?\w*$/.test(part), part).toBe(true);
  });
  it('says so when there is nothing', () => {
    expect(renderHistoryRecap([], 'it')).toContain('Nessuna cartella approvata');
  });
});
