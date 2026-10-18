import { describe, it, expect } from 'vitest';
import { planVaccines } from '../src/vaccine-plan.js';

const ageWeeks = (dob: string, d: string) => (Date.parse(d) - Date.parse(dob)) / (7 * 86400000);

describe('vaccine planner', () => {
  it('core series runs every 4 weeks and its last dose is at 16 weeks or later', () => {
    const p = planVaccines({ species: 'dog', dob: '2026-01-01' });
    const core = p.filter((x) => x.key === 'core');
    expect(core.map((c) => ageWeeks('2026-01-01', c.date))).toEqual([8, 12, 16]);
    expect(core.map((c) => c.dose)).toEqual([1, 2, 3]);
  });
  it('starting at 9 weeks ends at 17 weeks, not before 16', () => {
    const core = planVaccines({ species: 'cat', dob: '2026-01-01', firstDose: '2026-03-05' }).filter((x) => x.key === 'core');
    const last = core[core.length - 1];
    expect(ageWeeks('2026-01-01', last.date)).toBeGreaterThanOrEqual(16);
    expect(ageWeeks('2026-01-01', core[core.length - 2].date)).toBeLessThan(16);
  });
  it('flags a first dose before 6 weeks instead of moving it', () => {
    const p = planVaccines({ species: 'dog', dob: '2026-01-01', firstDose: '2026-01-29' });
    expect(p.find((x) => x.key === 'core' && x.dose === 1)).toMatchObject({ date: '2026-01-29', warn: 'before6w' });
  });
  it('adds the 6-month booster and the 3-year booster for dogs and low-risk cats', () => {
    for (const species of ['dog', 'cat'] as const) {
      const p = planVaccines({ species, dob: '2026-01-01' });
      expect(p.find((x) => x.key === 'core6m')?.date).toBe('2026-07-02');
      expect(p.find((x) => x.key === 'core3y')?.date).toBe('2029-01-01');
    }
  });
  it('higher-risk cats get yearly core boosters and FeLV with a test first', () => {
    const p = planVaccines({ species: 'cat', dob: '2026-01-01', higherRisk: true });
    expect(p.some((x) => x.key === 'core3y')).toBe(false);
    expect(p.find((x) => x.key === 'coreYearly')?.date).toBe('2027-07-02');
    expect(p.filter((x) => x.key === 'felv')).toHaveLength(2);
    expect(p.find((x) => x.key === 'felvTest')?.date).toBe(p.find((x) => x.key === 'felv')?.date);
    expect(p.findIndex((x) => x.key === 'felvTest')).toBeLessThan(p.findIndex((x) => x.key === 'felv'));
  });
  it('rabies is not before 12 weeks and travel validity starts 21 days later', () => {
    const p = planVaccines({ species: 'dog', dob: '2026-01-01' });
    const r = p.find((x) => x.key === 'rabies')!, v = p.find((x) => x.key === 'rabiesValid')!;
    expect(ageWeeks('2026-01-01', r.date)).toBe(12);
    expect((Date.parse(v.date) - Date.parse(r.date)) / 86400000).toBe(21);
  });
  it('lepto only when asked, dogs only', () => {
    expect(planVaccines({ species: 'dog', dob: '2026-01-01' }).some((x) => x.key.startsWith('lepto'))).toBe(false);
    expect(planVaccines({ species: 'dog', dob: '2026-01-01', lepto: true }).filter((x) => x.key === 'lepto')).toHaveLength(2);
    expect(planVaccines({ species: 'cat', dob: '2026-01-01', lepto: true }).some((x) => x.key.startsWith('lepto'))).toBe(false);
  });
  it('rejects an invalid date of birth', () => {
    expect(() => planVaccines({ species: 'dog', dob: 'x' })).toThrow();
  });
});
