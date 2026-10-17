/**
 * Clinic-owner analytics: how the documentation tool is used, never what was
 * documented. Input is a stream of metadata events (ids, kinds, timestamps,
 * counts); there is no field for clinical text, so none can leak into a report.
 *
 * Metrics per vet and for the clinic:
 *  - time from first draft to approval (median and 90th percentile, minutes)
 *  - edit ratio: share of generated sections the vet changed before approving
 *  - flags open at approval: missing-information flags the vet approved past
 *    (marked "not recorded") rather than filled
 *  - amendments after approval
 */

export type UsageEvent = Readonly<
  | { kind: 'draft_created'; record_id: string; vet_id: string; at: string }
  | { kind: 'approved'; record_id: string; vet_id: string; at: string; sections_generated: number; sections_edited: number; flags_raised: number; flags_open: number }
  | { kind: 'amended'; record_id: string; vet_id: string; at: string }
>;

export type UsageSummary = Readonly<{
  approved: number;
  minutes_to_approve: { median: number | null; p90: number | null };
  edit_ratio: number | null;
  flags_raised: number;
  flags_open_at_approval: number;
  amendments: number;
  amendment_rate: number | null;
}>;

/** Nearest-rank percentile on a sorted copy. */
function pct(xs: number[], p: number): number | null {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.max(0, Math.ceil((p / 100) * s.length) - 1))];
}

const round = (x: number | null, d = 2) => (x === null ? null : Math.round(x * 10 ** d) / 10 ** d);

function summarise(events: readonly UsageEvent[]): UsageSummary {
  const firstDraft = new Map<string, number>();
  for (const e of events) if (e.kind === 'draft_created') {
    const t = Date.parse(e.at); const prev = firstDraft.get(e.record_id);
    if (prev === undefined || t < prev) firstDraft.set(e.record_id, t);
  }
  const approvals = events.filter((e): e is Extract<UsageEvent, { kind: 'approved' }> => e.kind === 'approved');
  // first approval of each record counts; later ones are amendments' re-approvals
  const firstApproval = new Map<string, Extract<UsageEvent, { kind: 'approved' }>>();
  for (const a of approvals) { const p = firstApproval.get(a.record_id); if (!p || Date.parse(a.at) < Date.parse(p.at)) firstApproval.set(a.record_id, a); }
  const first = [...firstApproval.values()];
  const minutes = first.flatMap((a) => { const d = firstDraft.get(a.record_id); return d === undefined ? [] : [Math.max(0, (Date.parse(a.at) - d) / 60000)]; });
  const gen = first.reduce((s, a) => s + a.sections_generated, 0);
  const edited = first.reduce((s, a) => s + Math.min(a.sections_edited, a.sections_generated), 0);
  const amendments = events.filter((e) => e.kind === 'amended').length;
  return {
    approved: first.length,
    minutes_to_approve: { median: round(pct(minutes, 50), 1), p90: round(pct(minutes, 90), 1) },
    edit_ratio: gen ? round(edited / gen) : null,
    flags_raised: first.reduce((s, a) => s + a.flags_raised, 0),
    flags_open_at_approval: first.reduce((s, a) => s + a.flags_open, 0),
    amendments,
    amendment_rate: first.length ? round(amendments / first.length) : null,
  };
}

/** Clinic total plus one summary per vet. Optional [from, to) window on event time. */
export function usageReport(events: readonly UsageEvent[], window: { from?: string; to?: string } = {}): { clinic: UsageSummary; by_vet: Record<string, UsageSummary> } {
  const from = window.from ? Date.parse(window.from) : -Infinity, to = window.to ? Date.parse(window.to) : Infinity;
  const inWin = events.filter((e) => { const t = Date.parse(e.at); return t >= from && t < to; });
  const vets = [...new Set(inWin.map((e) => e.vet_id))].sort();
  return { clinic: summarise(inWin), by_vet: Object.fromEntries(vets.map((v) => [v, summarise(inWin.filter((e) => e.vet_id === v))])) };
}
