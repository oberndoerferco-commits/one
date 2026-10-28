import { describe, it, expect } from 'vitest';
import { renderPhoneNote, renderEndOfLife, renderCondolence } from '../src/letters.js';

describe('phone note', () => {
  it('lays out what was typed and flags what is missing', () => {
    const r = renderPhoneNote({ at: '2026-10-16T18:05', caller: 'Ms Rossi', reason: 'Luna vomited twice', outcome: 'call_back' }, 'en');
    expect(r.text).toContain('Ms Rossi (owner)');
    expect(r.text).toContain('Luna vomited twice');
    expect(r.missing).toEqual(['the advice given', 'when to call back', 'who took the call']);
  });
  it('is complete when everything is entered', () => {
    const r = renderPhoneNote({ at: '2026-10-16T18:05', caller: 'Herr Weber', advice: 'Futterpause, Wasser anbieten', outcome: 'book_visit', taken_by: 'TFA Müller' }, 'de');
    expect(r.missing).toEqual([]);
    expect(r.text).toContain('Termin wird vereinbart');
  });
});

describe('end-of-life record', () => {
  it('requires consent, a witness for verbal consent, procedure, aftercare and vet', () => {
    const r = renderEndOfLife({ date: '2026-10-16', consent: 'verbal_witnessed' }, 'it');
    expect(r.missing).toEqual(['un testimone per il consenso verbale', 'la procedura eseguita', 'la destinazione della salma', 'il medico veterinario responsabile']);
  });
  it('copies the procedure exactly as written and adds nothing', () => {
    const method = 'Sedation then IV as per clinic protocol';
    const r = renderEndOfLife({ date: '2026-10-16', consent: 'signed', method_as_written: method, aftercare: 'individual_cremation', vet: 'Dr. A' }, 'en');
    expect(r.missing).toEqual([]);
    expect(r.text).toContain(method);
    expect(r.text).not.toMatch(/\bmg\b|ml\/kg/);
  });
});

describe('condolence letter', () => {
  it('uses only names and the vet\'s own sentence', () => {
    const txt = renderCondolence({ owner: 'Anna', patient: 'Bruno', personal_line: 'Bruno always greeted us at the door.', vet: 'Dr. Bianchi', clinic: 'Clinica Navigli' }, 'en');
    expect(txt).toContain('Dear Anna,');
    expect(txt).toContain('Bruno always greeted us at the door.');
    expect(txt).toContain('Dr. Bianchi, Clinica Navigli');
  });
  it('works without a personal line', () => {
    expect(renderCondolence({ patient: 'Mimì' }, 'it')).toContain('Gentile famiglia,');
  });
});
