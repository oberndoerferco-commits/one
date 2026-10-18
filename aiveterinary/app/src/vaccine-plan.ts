/**
 * Puppy and kitten vaccination dates to discuss with the vet.
 *
 * Built only from two sources, read on 18 October 2026:
 * - WSAVA 2024 guidelines, vaccination tables for pet dogs and pet cats (non-shelter):
 *   core series "start no earlier than 6 weeks of age, revaccinate every 3–4 weeks until
 *   16 weeks", "consider revaccinating at about 6 months", then (dogs) "revaccinate at 3 years
 *   of age and thereafter no more frequently than every 3 years", (cats) the same for
 *   "low risk" cats and "up to annually" for cats at higher risk; leptospirosis "initial dose
 *   usually from 8 weeks … second dose 2–4 weeks later … annually"; FeLV "as early as 8 weeks
 *   … second dose 3–4 weeks later … revaccinate 1 year following the last dose", FeLV test first.
 * - EU non-commercial movement rules (European Commission): rabies vaccination at 12 weeks of
 *   age or older; validity starts 21 days after the primary vaccination.
 *
 * It returns suggestions, never a prescription: products, intervals and whether a vaccine
 * is needed at all are the vet's decision, and national law comes first for rabies.
 * Where WSAVA gives a range the upper interval (4 weeks) is used and the range is reported.
 */

export type PlanSpecies = 'dog' | 'cat';
export type PlanItem = { key: string; date: string; dose?: number; optional?: boolean; warn?: string };
export type PlanInput = { species: PlanSpecies; dob: string; firstDose?: string | null; higherRisk?: boolean; lepto?: boolean };

const DAY = 86400000;
const iso = (t: number) => new Date(t).toISOString().slice(0, 10);
const parse = (d: string) => Date.parse(`${d}T00:00:00Z`);
const addDays = (d: string, n: number) => iso(parse(d) + n * DAY);
const addYears = (d: string, n: number) => { const x = new Date(parse(d)); x.setUTCFullYear(x.getUTCFullYear() + n); return iso(x.getTime()); };
const ageDays = (dob: string, d: string) => Math.round((parse(d) - parse(dob)) / DAY);

export function planVaccines(input: PlanInput): PlanItem[] {
  const { species, dob } = input;
  if (isNaN(parse(dob))) throw new Error('Invalid date of birth');
  const out: PlanItem[] = [];

  // Core series: from the first dose every 4 weeks until a dose falls at 16 weeks of age or later.
  let dose = input.firstDose && !isNaN(parse(input.firstDose)) ? input.firstDose : addDays(dob, 8 * 7);
  const first: PlanItem = { key: 'core', date: dose, dose: 1 };
  if (ageDays(dob, dose) < 6 * 7) first.warn = 'before6w';
  out.push(first);
  let n = 1;
  while (ageDays(dob, dose) < 16 * 7 && n < 6) { dose = addDays(dose, 28); n++; out.push({ key: 'core', date: dose, dose: n }); }
  out.push({ key: 'core6m', date: addDays(dob, 26 * 7) });
  if (species === 'cat' && input.higherRisk) out.push({ key: 'coreYearly', date: addYears(addDays(dob, 26 * 7), 1) });
  else out.push({ key: 'core3y', date: addYears(dob, 3) });

  if (species === 'dog' && input.lepto) {
    const l1 = addDays(dob, 8 * 7), l2 = addDays(l1, 28);
    out.push({ key: 'lepto', date: l1, dose: 1, optional: true }, { key: 'lepto', date: l2, dose: 2, optional: true }, { key: 'leptoYearly', date: addYears(l2, 1), optional: true });
  }
  if (species === 'cat' && input.higherRisk) {
    const f1 = addDays(dob, 8 * 7), f2 = addDays(f1, 28);
    out.push({ key: 'felvTest', date: f1, optional: true }, { key: 'felv', date: f1, dose: 1, optional: true }, { key: 'felv', date: f2, dose: 2, optional: true }, { key: 'felv1y', date: addYears(f2, 1), optional: true });
  }

  // Rabies: earliest date for EU travel rules, and when the 21-day wait ends.
  const r = addDays(dob, 12 * 7);
  out.push({ key: 'rabies', date: r, optional: true }, { key: 'rabiesValid', date: addDays(r, 21), optional: true });

  // Same-day items keep a meaningful order: the FeLV test comes before the FeLV vaccination.
  const ORDER = ['felvTest', 'core', 'felv', 'lepto', 'rabies', 'rabiesValid', 'core6m', 'leptoYearly', 'felv1y', 'coreYearly', 'core3y'];
  return out.sort((a, b) => a.date.localeCompare(b.date) || ORDER.indexOf(a.key) - ORDER.indexOf(b.key));
}
