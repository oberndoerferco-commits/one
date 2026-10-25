import { describe as group, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { verifyExport, checkPatient, describe, SPECIES_WORDS } from '../src/core.js';
import { ClinicalRecord } from '../../app/src/schema.js';
import { approve, amend } from '../../app/src/versions.js';
import { exportBundle } from '../../app/src/export.js';
import { lunaExport } from './fixture.js';

const good = () => structuredClone(lunaExport()) as any;
const txt = (b: unknown) => JSON.stringify(b);
/** An export whose approved record itself names the patient (the eval fixtures never do). */
const withPatient = () => {
  const b = good();
  const v = approve(ClinicalRecord.parse({ ...b.record, patient: { ...b.record.patient, name: 'Luna', species: 'dog' } }), 'Dr. X');
  return structuredClone(exportBundle(v, b.patient)) as any;
};

group('verifyExport', () => {
  it('accepts the approved export, and the checked-in fixture is current', () => {
    expect(verifyExport(txt(good()))).toMatchObject({ ok: true, lang: 'en' });
    expect(JSON.parse(readFileSync(new URL('fixtures/approved-luna.json', import.meta.url), 'utf8'))).toEqual(lunaExport());
  });
  it('accepts every eval case in every language, and amendments', () => {
    const dir = new URL('../../app/eval/cases/', import.meta.url);
    for (const f of readdirSync(dir).filter((x) => x.endsWith('.json'))) {
      const c = JSON.parse(readFileSync(new URL(f, dir), 'utf8'));
      if (!c.fixture_record || !c.header) continue;
      const v = approve(ClinicalRecord.parse(c.fixture_record), 'Dr. X');
      for (const lang of ['en', 'de', 'it'] as const) expect(verifyExport(txt(exportBundle(v, c.header, lang))), f).toMatchObject({ ok: true, lang });
    }
    const v1 = approve(ClinicalRecord.parse(good().record), 'Dr. X');
    const v2 = amend(v1, { ...v1.record, assessment: { ...v1.record.assessment, text: 'gastritis' } } as any, 'Dr. X', 'typo');
    expect(verifyExport(txt(exportBundle(v2, good().patient))).ok).toBe(true);
  });
  it.each([
    ['not JSON', () => '{nope', 'not_json'],
    ['another format', () => txt({ ...good(), format: 'other/1' }), 'wrong_format'],
    ['no approver', () => { const b = good(); delete b.provenance.approved_by; return txt(b); }, 'not_approved'],
    ['blank approver', () => { const b = good(); b.provenance.approved_by = ' '; return txt(b); }, 'not_approved'],
    ['no approval date', () => { const b = good(); b.provenance.approved_at = 'soon'; return txt(b); }, 'not_approved'],
    ['no provenance (a draft)', () => { const b = good(); delete b.provenance; return txt(b); }, 'not_approved'],
    ['amendment without a reason', () => { const b = good(); b.provenance.supersedes = 1; return txt(b); }, 'not_approved'],
    ['record edited after approval', () => { const b = good(); b.record.assessment.text = 'pancreatitis'; return txt(b); }, 'fingerprint'],
    ['fingerprint replaced', () => { const b = good(); b.provenance.fingerprint = '0000000000000000'; return txt(b); }, 'fingerprint'],
    ['SOAP text edited', () => { const b = good(); b.soap[3].text += '\nmeloxicam 0.1 mg/kg'; return txt(b); }, 'soap_changed'],
    ['SOAP field dropped', () => { const b = good(); b.soap.pop(); return txt(b); }, 'soap_changed'],
    ['header name differing from the record', () => { const b = withPatient(); b.patient.name = 'Max'; return txt(b); }, 'patient_changed'],
    ['header species differing from the record', () => { const b = withPatient(); b.patient.species = 'cat'; return txt(b); }, 'patient_changed'],
    ['no patient', () => { const b = good(); delete b.patient; return txt(b); }, 'patient_missing'],
  ])('refuses %s', (_n, make, reason) => expect(verifyExport(make())).toEqual({ ok: false, reason }));
});

group('known limit', () => {
  it('cannot detect an edited header when the record has no patient name (the header is outside the fingerprint)', () => {
    expect(verifyExport(txt(withPatient())).ok).toBe(true);
    const b = good(); b.patient.name = 'Max';
    expect(b.record.patient.name).toBeNull();
    expect(verifyExport(txt(b)).ok).toBe(true);
  });
});

group('checkPatient', () => {
  const luna = { name: 'Luna', species: 'dog' };
  it('passes the same patient, ignoring case and spacing only', () => {
    expect(checkPatient(luna, { name: '  LUNA ', species: 'Hund' })).toEqual([]);
    expect(checkPatient(luna, { name: 'luna', species: 'Cane' })).toEqual([]);
  });
  it('blocks a different name or species, with no similarity tolerance', () => {
    expect(checkPatient(luna, { name: 'Lunа', species: 'dog' })[0].field).toBe('name'); // Cyrillic a
    expect(checkPatient(luna, { name: 'Luna Rossi', species: 'dog' })[0].field).toBe('name');
    expect(checkPatient(luna, { name: 'Luna', species: 'Katze' })).toEqual([{ field: 'species', expected: 'dog', found: 'Katze' }]);
    expect(checkPatient(luna, { name: '', species: '' }).map((m) => m.field)).toEqual(['name', 'species']);
  });
  it('cannot lock species "other"', () => {
    expect(SPECIES_WORDS.other).toEqual([]);
    expect(checkPatient({ name: 'Rex', species: 'other' }, { name: 'Rex', species: 'other' })).toHaveLength(1);
  });
  it('describes a mismatch with the locale message', () => {
    const msgs = JSON.parse(readFileSync(new URL('../_locales/en/messages.json', import.meta.url), 'utf8'));
    const msg = (k: string, s: string[] = []) => msgs[k].message.replace(/\$(\d)/g, (_: string, i: string) => s[Number(i) - 1]);
    expect(describe({ ok: false, reason: 'mismatch', mismatches: checkPatient(luna, { name: 'Max', species: 'dog' }) }, msg))
      .toBe('The page shows patient "Max", the approved record is for "Luna". Open the right patient in your practice software, or cancel. Nothing was pasted.');
  });
});

group('locales and privacy', () => {
  const root = new URL('../', import.meta.url);
  it('EN, IT and DE have the same keys', () => {
    const keys = (l: string) => Object.keys(JSON.parse(readFileSync(new URL(`_locales/${l}/messages.json`, root), 'utf8'))).sort();
    expect(keys('it')).toEqual(keys('en')); expect(keys('de')).toEqual(keys('en'));
  });
  it('asks for no host permissions and only optional clipboard access', () => {
    const m = JSON.parse(readFileSync(new URL('manifest.json', root), 'utf8'));
    expect(m.permissions).toEqual(['activeTab', 'scripting', 'storage']);
    expect(m.optional_permissions).toEqual(['clipboardRead']);
    expect(m.host_permissions).toBeUndefined(); expect(m.content_scripts).toBeUndefined(); expect(m.background).toBeUndefined();
    expect(m.content_security_policy.extension_pages).toContain("connect-src 'none'");
  });
  it('has no network API in its source', () => {
    for (const f of readdirSync(new URL('src/', root))) {
      const s = readFileSync(new URL(`src/${f}`, root), 'utf8');
      expect(s, f).not.toMatch(/\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)\b|https?:\/\//);
    }
  });
  it('never submits or clicks in the page', () => {
    const s = readFileSync(new URL('src/content.ts', root), 'utf8');
    expect(s).not.toMatch(/\.submit\(|requestSubmit|\.click\(\)|KeyboardEvent|'keydown'/);
  });
});
