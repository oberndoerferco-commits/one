/**
 * Retention: what may be deleted automatically, and when.
 *
 * Only working material is ever deleted by this module: the raw notes a vet
 * typed, model drafts that were never approved, and uploaded attachments not
 * linked to an approved version. Approved versions and the documents generated
 * from them are clinical records; how long they must be kept is set by national
 * law and professional rules, so this module never deletes them. The clinic's
 * own records policy, checked by its lawyer, decides that.
 *
 * Pure function over metadata, so the server job and the tests use the same
 * rule. No clinical text is needed to decide.
 */

export type RetentionPolicy = Readonly<{
  /** Raw notes are deleted this many hours after the record they belong to is approved. null keeps them. */
  raw_notes_after_approval_hours: number | null;
  /** Drafts never approved are deleted this many days after their last edit. */
  unapproved_draft_days: number;
  /** Attachments not linked to an approved version, days after upload. */
  unlinked_attachment_days: number;
}>;

export const DEFAULT_POLICY: RetentionPolicy = {
  raw_notes_after_approval_hours: 24,
  unapproved_draft_days: 14,
  unlinked_attachment_days: 14,
};

export type StoredItem = Readonly<
  | { id: string; kind: 'raw_notes'; record_id: string; created_at: string }
  | { id: string; kind: 'draft'; record_id: string; updated_at: string }
  | { id: string; kind: 'attachment'; record_id: string; uploaded_at: string; linked_version: number | null }
  | { id: string; kind: 'approved_version' | 'document'; record_id: string; created_at: string }
>;

export type RecordState = Readonly<{ approved_at: string | null; legal_hold: boolean }>;

export type Deletion = Readonly<{ id: string; kind: StoredItem['kind']; reason: string }>;

const HOUR = 3_600_000;
const DAY = 24 * HOUR;

function check(policy: RetentionPolicy) {
  const n = [policy.unapproved_draft_days, policy.unlinked_attachment_days, policy.raw_notes_after_approval_hours ?? 0];
  if (n.some((x) => !Number.isFinite(x) || x < 0)) throw new Error('retention: policy values must be zero or positive numbers');
}

/**
 * Items due for deletion at `now`. Records under legal hold are skipped
 * entirely. Approved versions and documents are never returned.
 */
export function dueForDeletion(items: readonly StoredItem[], records: Readonly<Record<string, RecordState>>, policy: RetentionPolicy = DEFAULT_POLICY, now: Date = new Date()): Deletion[] {
  check(policy);
  const t = now.getTime();
  const out: Deletion[] = [];
  for (const it of items) {
    const rec = records[it.record_id];
    if (!rec || rec.legal_hold) continue;
    if (it.kind === 'raw_notes') {
      if (policy.raw_notes_after_approval_hours === null || !rec.approved_at) continue;
      if (t - Date.parse(rec.approved_at) >= policy.raw_notes_after_approval_hours * HOUR)
        out.push({ id: it.id, kind: it.kind, reason: `raw notes, record approved more than ${policy.raw_notes_after_approval_hours} h ago` });
    } else if (it.kind === 'draft') {
      if (rec.approved_at) {
        // superseded by the approved version: same window as the raw notes
        if (policy.raw_notes_after_approval_hours !== null && t - Date.parse(rec.approved_at) >= policy.raw_notes_after_approval_hours * HOUR)
          out.push({ id: it.id, kind: it.kind, reason: `draft superseded by an approval more than ${policy.raw_notes_after_approval_hours} h ago` });
        continue;
      }
      if (t - Date.parse(it.updated_at) >= policy.unapproved_draft_days * DAY)
        out.push({ id: it.id, kind: it.kind, reason: `draft never approved, untouched for ${policy.unapproved_draft_days} days` });
    } else if (it.kind === 'attachment') {
      if (it.linked_version !== null) continue;
      if (t - Date.parse(it.uploaded_at) >= policy.unlinked_attachment_days * DAY)
        out.push({ id: it.id, kind: it.kind, reason: `attachment not linked to an approved version for ${policy.unlinked_attachment_days} days` });
    }
  }
  return out;
}
