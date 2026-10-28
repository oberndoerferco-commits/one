import { describe, expect, it } from 'vitest';
import { dueForDeletion, DEFAULT_POLICY, type StoredItem } from '../src/retention.js';

const now = new Date('2026-10-16T12:00:00Z');
const items: StoredItem[] = [
  { id: 'n1', kind: 'raw_notes', record_id: 'r1', created_at: '2026-10-14T09:00:00Z' },
  { id: 'n2', kind: 'raw_notes', record_id: 'r2', created_at: '2026-10-16T09:00:00Z' },
  { id: 'd2', kind: 'draft', record_id: 'r2', updated_at: '2026-09-20T09:00:00Z' },
  { id: 'd1', kind: 'draft', record_id: 'r1', updated_at: '2026-10-14T09:30:00Z' },
  { id: 'a1', kind: 'attachment', record_id: 'r1', uploaded_at: '2026-09-01T09:00:00Z', linked_version: 1 },
  { id: 'a3', kind: 'attachment', record_id: 'r3', uploaded_at: '2026-09-01T09:00:00Z', linked_version: null },
  { id: 'v1', kind: 'approved_version', record_id: 'r1', created_at: '2016-01-01T09:00:00Z' },
  { id: 'doc1', kind: 'document', record_id: 'r1', created_at: '2016-01-01T09:00:00Z' },
  { id: 'n4', kind: 'raw_notes', record_id: 'r4', created_at: '2026-01-01T09:00:00Z' },
];
const records = {
  r1: { approved_at: '2026-10-14T10:00:00Z', legal_hold: false },
  r2: { approved_at: null, legal_hold: false },
  r3: { approved_at: null, legal_hold: false },
  r4: { approved_at: '2026-01-01T10:00:00Z', legal_hold: true },
};

describe('retention', () => {
  it('deletes only working material that is past its window', () => {
    const ids = dueForDeletion(items, records, DEFAULT_POLICY, now).map((d) => d.id).sort();
    expect(ids).toEqual(['a3', 'd1', 'd2', 'n1']);
  });
  it('never returns approved versions or documents, whatever the policy', () => {
    const zero = { raw_notes_after_approval_hours: 0, unapproved_draft_days: 0, unlinked_attachment_days: 0 };
    const kinds = dueForDeletion(items, records, zero, now).map((d) => d.kind);
    expect(kinds).not.toContain('approved_version');
    expect(kinds).not.toContain('document');
  });
  it('keeps raw notes of unapproved records and everything under legal hold', () => {
    const ids = dueForDeletion(items, records, DEFAULT_POLICY, now).map((d) => d.id);
    expect(ids).not.toContain('n2');
    expect(ids).not.toContain('n4');
  });
  it('null keeps raw notes', () => {
    const ids = dueForDeletion(items, records, { ...DEFAULT_POLICY, raw_notes_after_approval_hours: null }, now).map((d) => d.id);
    expect(ids).not.toContain('n1');
  });
  it('rejects negative values', () => {
    expect(() => dueForDeletion(items, records, { ...DEFAULT_POLICY, unapproved_draft_days: -1 }, now)).toThrow();
  });
});
