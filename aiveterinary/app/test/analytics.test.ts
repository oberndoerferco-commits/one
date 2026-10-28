import { describe, it, expect } from 'vitest';
import { usageReport, type UsageEvent } from '../src/analytics.js';

const ev: UsageEvent[] = [
  { kind: 'draft_created', record_id: 'r1', vet_id: 'a', at: '2026-10-16T09:00:00Z' },
  { kind: 'approved', record_id: 'r1', vet_id: 'a', at: '2026-10-16T09:04:00Z', sections_generated: 6, sections_edited: 1, flags_raised: 2, flags_open: 1 },
  { kind: 'draft_created', record_id: 'r2', vet_id: 'a', at: '2026-10-16T10:00:00Z' },
  { kind: 'approved', record_id: 'r2', vet_id: 'a', at: '2026-10-16T10:10:00Z', sections_generated: 4, sections_edited: 3, flags_raised: 0, flags_open: 0 },
  { kind: 'amended', record_id: 'r2', vet_id: 'a', at: '2026-10-16T12:00:00Z' },
  { kind: 'approved', record_id: 'r2', vet_id: 'a', at: '2026-10-16T12:01:00Z', sections_generated: 4, sections_edited: 4, flags_raised: 0, flags_open: 0 },
  { kind: 'draft_created', record_id: 'r3', vet_id: 'b', at: '2026-10-17T09:00:00Z' },
  { kind: 'approved', record_id: 'r3', vet_id: 'b', at: '2026-10-17T09:02:00Z', sections_generated: 5, sections_edited: 0, flags_raised: 1, flags_open: 0 },
];

describe('usage report', () => {
  it('summarises the clinic', () => {
    const { clinic } = usageReport(ev);
    expect(clinic.approved).toBe(3);
    expect(clinic.minutes_to_approve).toEqual({ median: 4, p90: 10 });
    expect(clinic.edit_ratio).toBe(0.27); // (1+3+0)/(6+4+5)
    expect(clinic.flags_open_at_approval).toBe(1);
    expect(clinic.amendments).toBe(1);
    expect(clinic.amendment_rate).toBe(0.33);
  });
  it('splits by vet and honours the window', () => {
    const r = usageReport(ev, { from: '2026-10-17T00:00:00Z' });
    expect(Object.keys(r.by_vet)).toEqual(['b']);
    expect(r.clinic.approved).toBe(1);
  });
  it('has no place for clinical text', () => {
    const json = JSON.stringify(usageReport(ev));
    expect(json).not.toMatch(/vomit|dose|diagnos/i);
  });
  it('handles an empty period', () => {
    const { clinic } = usageReport([]);
    expect(clinic.approved).toBe(0);
    expect(clinic.minutes_to_approve.median).toBeNull();
    expect(clinic.edit_ratio).toBeNull();
  });
});
