import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { ClinicalRecord, PatientHeader, type Span } from '../src/schema.js';
import { normalizeNotes } from '../src/normalize.js';
import { validateAll, validateStatus, statusMarkers, type Finding } from '../src/validators.js';

/**
 * status_conflicts_source and owner_report_as_finding: the item's status (or the finding's role)
 * must not contradict a clear marker written in its own source span.
 */
type St = 'planned' | 'performed' | 'declined' | 'recommended' | 'dispensed' | 'prescribed';
const empty = () => ({
  schema_version: '0.2',
  patient: { name: null, species: null, breed: null, sex: null, neuter_status: null, age: null, weight: null },
  presenting_complaint: null, history: [],
  examination: { vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null }, findings: [] as any[] },
  diagnostics: [] as any[], assessment: { text: null, differentials: [], source_spans: [] }, treatments: [] as any[], medications: [] as any[],
  plan: { follow_up: null, instructions: [] }, missing: [], uncertain: [],
});
const whole = (notes: string): Span[] => [[0, notes.length]];
const statusFindings = (fs: Finding[]) => fs.filter((f) => f.rule === 'status_conflicts_source');
const diag = (notes: string, status: St) => { const r = empty(); r.diagnostics.push({ test: 'x', status, result: null, source_spans: whole(notes) }); return statusFindings(validateStatus(ClinicalRecord.parse(r), notes)); };
const treat = (notes: string, status: St) => { const r = empty(); r.treatments.push({ type: 'procedure', text: notes, status, source_spans: whole(notes) }); return statusFindings(validateStatus(ClinicalRecord.parse(r), notes)); };
const med = (notes: string, drug: string, status: St) => { const r = empty(); r.medications.push({ drug, class_as_written: null, dose: null, dose_unit: null, route: null, frequency: null, duration: null, status, source_spans: whole(notes) }); return statusFindings(validateStatus(ClinicalRecord.parse(r), notes)); };
const finding = (notes: string, role?: 'owner_reported' | 'vet_observed') => { const r = empty(); r.examination.findings.push({ system: 'x', text: notes, ...(role ? { source_role: role } : {}), source_spans: whole(notes) }); return validateStatus(ClinicalRecord.parse(r), notes).filter((f) => f.rule === 'owner_report_as_finding'); };
const sev = (fs: Finding[]) => fs.map((f) => f.severity);

describe('status_conflicts_source: declined written, done recorded → block', () => {
  it.each([
    ['en', 'bloods offered, owner declined'], ['en', 'owner declines radiographs'], ['en', 'O refused sedation'],
    ['de', 'Blutbild angeboten, Besitzer lehnt ab'], ['de', 'Besitzerin lehnt Narkose vorerst ab'], ['de', 'Röntgen abgelehnt'], ['de', 'Besitzer verweigert Röntgen'],
    ['it', 'esami del sangue proposti, il proprietario rifiuta'], ['it', 'radiografie rifiutate dalla proprietaria'], ['it', 'il proprietario non acconsente alla sedazione'],
  ])('%s: "%s" recorded as performed', (_l, notes) => { expect(sev(diag(notes, 'performed'))).toEqual(['block']); });
  it('a declined medication recorded as dispensed or prescribed blocks (EN/DE/IT)', () => {
    expect(sev(med('Apoquel offered, owner declined', 'Apoquel', 'dispensed'))).toEqual(['block']);
    expect(sev(med('Apoquel angeboten, Besitzerin lehnt ab', 'Apoquel', 'prescribed'))).toEqual(['block']);
    expect(sev(med('Apoquel proposto, la proprietaria rifiuta', 'Apoquel', 'dispensed'))).toEqual(['block']);
  });
  it('a performed procedure recorded as declined blocks (EN/DE/IT)', () => {
    expect(sev(treat('ear flush left performed', 'declined'))).toEqual(['block']);
    expect(sev(treat('Ohrspülung li. durchgeführt', 'declined'))).toEqual(['block']);
    expect(sev(treat('lavaggio auricolare sx eseguito', 'declined'))).toEqual(['block']);
    expect(sev(diag('prelievo effettuato oggi', 'declined'))).toEqual(['block']);
  });
});

describe('status_conflicts_source: planned vs performed → warn', () => {
  it.each([
    ['en', 'rads R stifle planned next week'], ['en', 'FNA scheduled for Monday'], ['en', 'ultrasound to be done at recheck'],
    ['de', 'Röntgen Knie re. nächste Woche geplant'], ['de', 'Ultraschall vorgesehen'], ['de', 'Hautgeschabsel bei der WV'],
    ['it', 'ecografia addome programmata la prossima settimana'], ['it', 'raschiato cutaneo previsto al controllo'], ['it', 'agoaspirato da fare'],
  ])('%s: "%s" recorded as performed', (_l, notes) => { expect(sev(diag(notes, 'performed'))).toEqual(['warn']); });
  it.each([['en', 'ear cytology done'], ['de', 'Zytologie durchgeführt'], ['it', 'citologia eseguita']])('%s: "%s" recorded as planned', (_l, notes) => {
    expect(sev(diag(notes, 'planned'))).toEqual(['warn']);
  });
  it('declined written, planned or recommended recorded → warn', () => {
    expect(sev(diag('bloods offered, owner declined', 'planned'))).toEqual(['warn']);
    expect(sev(treat('Zahnsanierung empfohlen, Besitzer lehnt ab', 'recommended'))).toEqual(['warn']);
  });
});

describe('status_conflicts_source: conservative', () => {
  it('agreeing status raises nothing', () => {
    expect(diag('bloods offered, owner declined', 'declined')).toEqual([]);
    expect(diag('Röntgen geplant', 'planned')).toEqual([]);
    expect(treat('lavaggio eseguito', 'performed')).toEqual([]);
  });
  it('markers of more than one status → no finding', () => {
    expect(diag('bloods done today, rads planned, owner declined urinalysis', 'performed')).toEqual([]);
    expect(diag('Zytologie durchgeführt, Röntgen geplant', 'declined')).toEqual([]);
    expect(diag('rx eseguita, ecografia rifiutata', 'performed')).toEqual([]);
    expect(med('Ohrspülung durchgeführt, WV in 10 Tagen', 'x', 'planned')).toEqual([]);
  });
  it('no marker → no finding', () => {
    expect(diag('bloods: ALT 120', 'declined')).toEqual([]);
    expect(med('Apoquel discussed, O prefers not to start yet', 'Apoquel', 'dispensed')).toEqual([]);
  });
  it('simple negation does not count as the marker', () => {
    expect(diag('rads not done', 'planned')).toEqual([]);
    expect(diag('Röntgen nicht durchgeführt', 'planned')).toEqual([]);
    expect(diag('rx non eseguita', 'planned')).toEqual([]);
    expect(diag('owner has not declined bloods', 'performed')).toEqual([]);
    expect(diag('not planned', 'performed')).toEqual([]);
  });
  it('the animal refusing food or tablets is not a declined status', () => {
    expect(med('Metacam prescribed, dog refuses tablets', 'Metacam', 'prescribed')).toEqual([]);
    expect(med('Metacam, Hund verweigert Futter', 'Metacam', 'dispensed')).toEqual([]);
    expect(med('Metacam, il gatto rifiuta il cibo', 'Metacam', 'dispensed')).toEqual([]);
    expect(diag('blood sample, refuses to eat since Monday', 'performed')).toEqual([]);
  });
  it('only the item\'s own span is read, not the rest of the notes', () => {
    const notes = 'bloods taken\nowner declined rads';
    const r = empty(); r.diagnostics.push({ test: 'bloods', status: 'performed', result: null, source_spans: [[0, 12]] });
    expect(statusFindings(validateStatus(ClinicalRecord.parse(r), notes))).toEqual([]);
  });
});

describe('owner_report_as_finding (warn)', () => {
  it.each([
    ['en', 'owner reports limping LF'], ['en', 'coughing at night per owner'],
    ['de', 'Besitzer berichtet Husten nachts'], ['de', 'laut Besitzerin lahmt er vorne links'],
    ['it', 'la proprietaria riferisce tosse notturna'], ['it', 'tosse notturna (riferito)'], ['it', 'secondo il proprietario zoppica'],
  ])('%s: "%s" recorded as a vet finding', (_l, notes) => {
    expect(sev(finding(notes))).toEqual(['warn']);
    expect(sev(finding(notes, 'vet_observed'))).toEqual(['warn']);
  });
  it('no warning when the finding is marked owner-reported, or the span is the vet\'s own', () => {
    expect(finding('owner reports limping LF', 'owner_reported')).toEqual([]);
    expect(finding('no lameness seen at walk or trot')).toEqual([]);
    expect(finding('dolore riferito alla palpazione lombare')).toEqual([]);
  });
});

describe('eval cases', () => {
  const casesDir = new URL('../eval/cases/', import.meta.url);
  const ids = readdirSync(casesDir).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, '')).sort();
  const prep = (id: string) => { const c = JSON.parse(readFileSync(new URL(`${id}.json`, casesDir), 'utf8')); return { c, notes: normalizeNotes(c.notes), header: PatientHeader.parse(c.header), record: c.fixture_record ? ClinicalRecord.parse(c.fixture_record) : null }; };

  it('no gold record raises either rule, not even as a warning', () => {
    for (const id of ids) {
      const { record, notes, header } = prep(id); if (!record) continue;
      expect(validateAll(record, notes, header).filter((f) => f.rule === 'status_conflicts_source' || f.rule === 'owner_report_as_finding'), id).toEqual([]);
    }
  });

  /** Swap each gold status whose span carries one clear marker; the swap must be caught with the right severity. */
  const SWAPS: Record<string, [St, 'block' | 'warn'][]> = {
    declined: [['performed', 'block'], ['dispensed', 'block'], ['prescribed', 'block'], ['planned', 'warn']],
    performed: [['declined', 'block'], ['planned', 'warn']],
    planned: [['performed', 'warn']],
  };
  it('every single-marker status in the gold records is caught when swapped (EN/DE/IT)', () => {
    let swapped = 0; const langs = new Set<string>();
    for (const id of ids) {
      const { c, record, notes, header } = prep(id); if (!record) continue;
      for (const k of ['diagnostics', 'treatments', 'medications'] as const) (record as any)[k].forEach((item: any, i: number) => {
        const marks = [...statusMarkers(item.source_spans.map(([a, b]: Span) => notes.slice(a, b)).join('\n'))];
        if (marks.length !== 1) return;
        for (const [to, severity] of SWAPS[marks[0]] ?? []) {
          const r = structuredClone(record) as any; r[k][i].status = to;
          const fs = statusFindings(validateAll(ClinicalRecord.parse(r), notes, header));
          expect(fs.map((f) => [f.field, f.severity]), `${id} ${k}[${i}] → ${to}`).toEqual([[`${k}[${i}].status`, severity]]);
          swapped++; langs.add(c.language);
        }
      });
    }
    expect(swapped).toBeGreaterThanOrEqual(50);
    expect([...langs].sort()).toEqual(['de', 'en', 'it']);
  });

  it('148–150: a history line moved into the examination findings is flagged', () => {
    for (const id of ['148-gen-owner-vs-vet-lameness-en', '149-gen-owner-vs-vet-lameness-de', '150-gen-owner-vs-vet-lameness-it']) {
      const { record, notes, header } = prep(id);
      const r = structuredClone(record) as any;
      const pc = r.presenting_complaint;
      r.examination.findings.push({ system: 'musculoskeletal', text: pc.text, source_role: 'vet_observed', source_spans: pc.source_spans });
      const fs = validateAll(ClinicalRecord.parse(r), notes, header).filter((f) => f.rule === 'owner_report_as_finding');
      expect(fs.map((f) => f.severity), id).toEqual(['warn']);
    }
  });
});
