import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { ClinicalRecord, PatientHeader } from '../src/schema.js';
import { renderReferralLetter, REFERRAL_LABELS, type Lang, type ReferralInput } from '../src/render.js';
import { VisitContext } from '../src/country.js';

const c = JSON.parse(readFileSync(new URL('../eval/cases/008-adversarial-it-performed-vs-planned.json', import.meta.url), 'utf8'));
const header = PatientHeader.parse(c.header);
const record = ClinicalRecord.parse(c.fixture_record);
const langs: Lang[] = ['en', 'de', 'it'];

const full: ReferralInput = {
  referrer: { practice: 'Praxis Am Hang', address: 'Hangweg 3, 12345 Musterstadt · 0123 456', email: 'praxis@example.org', vet: 'Dr. A. Muster', registration: 'TK-4711' },
  request: { urgency: 'urgent', service: 'Orthopaedics', question: 'cruciate ligament rupture?' },
  owner: { name: 'M. Rossi', phone: '+39 06 123', email: 'rossi@example.org' },
};

describe('referral letter: vet-typed referrer, owner and request blocks', () => {
  for (const lang of langs) {
    const l = REFERRAL_LABELS[lang];
    it(`${lang}: renders all three blocks with every typed field`, () => {
      const md = renderReferralLetter(record, header, lang, { referral: full });
      expect(md).toContain(`## ${l.referrer}\n- ${l.practice}: Praxis Am Hang\n- ${l.address}: Hangweg 3, 12345 Musterstadt · 0123 456\n- ${l.email}: praxis@example.org\n- ${l.vet}: Dr. A. Muster\n- ${l.registration}: TK-4711`);
      expect(md).toContain(`## ${l.owner}\n- ${l.ownerName}: M. Rossi\n- ${l.phone}: +39 06 123\n- ${l.email}: rossi@example.org`);
      expect(md).toContain(`## ${l.request}\n- ${l.urgency}: ${l.urgencies.urgent}\n- ${l.service}: Orthopaedics\n- ${l.question}: Cruciate ligament rupture?`);
      expect(md).not.toContain('referral.reason');
    });
    it(`${lang}: renders none of the blocks when nothing is provided (no defaults)`, () => {
      for (const md of [renderReferralLetter(record, header, lang), renderReferralLetter(record, header, lang, { referral: {} }), renderReferralLetter(record, header, lang, { referral: { referrer: { practice: '  ', email: null }, owner: { name: '' }, request: { urgency: null, service: ' ' } } })]) {
        expect(md).not.toContain(`## ${l.referrer}`);
        expect(md).not.toContain(`## ${l.owner}`);
        expect(md).not.toContain(`## ${l.request}`);
        expect(md).not.toContain(`${l.urgency}:`);
        for (const u of Object.values(l.urgencies)) expect(md).not.toContain(`: ${u}`);
        expect(md).toContain('referral.reason'); // the question is still flagged
      }
    });
    it(`${lang}: each block alone, only with the fields given`, () => {
      const onlyEmail = renderReferralLetter(record, header, lang, { referral: { referrer: { email: 'a@b.c' } } });
      expect(onlyEmail).toContain(`## ${l.referrer}\n- ${l.email}: a@b.c\n\n`);
      expect(onlyEmail).not.toContain(`${l.practice}:`); expect(onlyEmail).not.toContain(`## ${l.owner}`); expect(onlyEmail).not.toContain(`## ${l.request}`);
      const onlyOwner = renderReferralLetter(record, header, lang, { referral: { owner: { phone: '555' } } });
      expect(onlyOwner).toContain(`## ${l.owner}\n- ${l.phone}: 555\n\n`);
      expect(onlyOwner).not.toContain(`${l.ownerName}:`); expect(onlyOwner).not.toContain(`## ${l.referrer}`);
      const onlyUrgency = renderReferralLetter(record, header, lang, { referral: { request: { urgency: 'emergency' } } });
      expect(onlyUrgency).toContain(`## ${l.request}\n- ${l.urgency}: ${l.urgencies.emergency}\n- ${l.question}: ▲`);
      expect(onlyUrgency).not.toContain(`${l.service}:`);
      expect(onlyUrgency).toContain('referral.reason');
    });
  }
  it('a question alone keeps the legacy reason section, and opts.reason is the fallback question', () => {
    const q = renderReferralLetter(record, header, 'en', { referral: { request: { question: 'second opinion' } } });
    expect(q).toContain('## Reason for referral\nSecond opinion');
    expect(q).not.toContain('## Referral request');
    const legacy = renderReferralLetter(record, header, 'en', { reason: 'second opinion' });
    expect(legacy).toBe(q);
    const both = renderReferralLetter(record, header, 'en', { reason: 'old', referral: { request: { question: 'new', service: 'Cardiology' } } });
    expect(both).toContain('- Clinical question: New'); expect(both).not.toContain('Old');
    const fallback = renderReferralLetter(record, header, 'de', { reason: 'Kreuzband?', referral: { request: { service: 'Orthopädie' } } });
    expect(fallback).toContain('- Fragestellung: Kreuzband?');
  });
  it('an unknown urgency value is not rendered', () => {
    const md = renderReferralLetter(record, header, 'en', { referral: { request: { urgency: 'asap' as any } } });
    expect(md).not.toContain('## Referral request'); expect(md).not.toContain('asap');
  });
  it('accepts VisitContext.owner as the owner block', () => {
    const ctx = VisitContext.parse({ country: 'IT', owner: { name: 'M. Rossi', tax_id: 'RSSMRA80A01H501U' } });
    const md = renderReferralLetter(record, header, 'it', { referral: { owner: ctx.owner } });
    expect(md).toContain('## Proprietario\n- Nome: M. Rossi\n');
    expect(md).not.toContain('RSSMRA80A01H501U');
  });
});
