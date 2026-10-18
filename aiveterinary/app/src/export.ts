import type { ClinicalRecord, PatientHeader } from './schema.js';
import type { ApprovedVersion } from './versions.js';
import { fingerprint } from './versions.js';

/**
 * Output for any practice software, without an integration.
 *
 * Most PIMS have separate text boxes for S, O, A and P, so the approved record is
 * offered as four plain-text fields the vet pastes one by one, plus a JSON file
 * that carries the record and its provenance. Every line is the record's own
 * text or a code-generated label; a missing value is flagged, never filled.
 */

const T = {
  en: {
    S: 'Subjective', O: 'Objective', A: 'Assessment', P: 'Plan', reason: 'Reason', owner: 'Owner reports', vet: 'Vet', temp: 'Temperature', hr: 'Heart rate', rr: 'Respiratory rate', weight: 'Weight', crt: 'CRT',
    diff: 'Differentials', fu: 'Follow-up', missing: 'Missing', none: 'Not recorded', dose: 'dose', drug: 'drug', route: 'route', freq: 'frequency',
    status: { planned: 'planned', performed: 'performed', declined: 'declined by owner', recommended: 'recommended', dispensed: 'dispensed', prescribed: 'prescribed' },
    atApproval: 'Entered by the vet at approval',
    disclosure: "Structured with AI assistance from the veterinarian's own notes; reviewed and approved by the veterinarian. No content was added by the AI.",
  },
  de: {
    S: 'Anamnese (S)', O: 'Befund (O)', A: 'Beurteilung (A)', P: 'Plan (P)', reason: 'Vorstellungsgrund', owner: 'Laut Besitzer', vet: 'TA', temp: 'Temperatur', hr: 'Herzfrequenz', rr: 'Atemfrequenz', weight: 'Gewicht', crt: 'KFZ',
    diff: 'Differenzialdiagnosen', fu: 'Kontrolle', missing: 'Fehlt', none: 'Nicht erfasst', dose: 'Dosis', drug: 'Wirkstoff', route: 'Applikation', freq: 'Häufigkeit',
    status: { planned: 'geplant', performed: 'durchgeführt', declined: 'vom Besitzer abgelehnt', recommended: 'empfohlen', dispensed: 'abgegeben', prescribed: 'verschrieben' },
    atApproval: 'Bei der Freigabe tierärztlich ergänzt',
    disclosure: 'Mit KI-Unterstützung aus den eigenen Notizen der Tierärztin/des Tierarztes strukturiert; tierärztlich geprüft und freigegeben. Die KI hat keine Inhalte hinzugefügt.',
  },
  it: {
    S: 'Anamnesi (S)', O: 'Esame obiettivo (O)', A: 'Valutazione (A)', P: 'Piano (P)', reason: 'Motivo', owner: 'Il proprietario riferisce', vet: 'Vet', temp: 'Temperatura', hr: 'Frequenza cardiaca', rr: 'Frequenza respiratoria', weight: 'Peso', crt: 'TRC',
    diff: 'Diagnosi differenziali', fu: 'Controllo', missing: 'Mancante', none: 'Non registrato', dose: 'dose', drug: 'farmaco', route: 'via', freq: 'frequenza',
    status: { planned: 'pianificato', performed: 'eseguito', declined: 'rifiutato dal proprietario', recommended: 'consigliato', dispensed: 'consegnato', prescribed: 'prescritto' },
    atApproval: "Inserito dal veterinario all'approvazione",
    disclosure: "Strutturato con assistenza IA a partire dalle note del veterinario; verificato e approvato dal veterinario. L'IA non ha aggiunto contenuti.",
  },
} as const;
export type ExportLang = keyof typeof T;

export type SoapField = { key: 'S' | 'O' | 'A' | 'P'; label: string; text: string };

const unitText = (u: { value: number; unit: string }) => `${u.value} ${u.unit}`;
const flag = (t: string) => `▲ ${t}`;

/** Four plain-text fields, one per SOAP box. An empty section says "Not recorded" rather than being dropped. */
export function soapFields(record: ClinicalRecord, lang: ExportLang = 'en', resolutions: Record<string, string> = {}): SoapField[] {
  const t = T[lang];
  const S: string[] = [];
  if (record.presenting_complaint) S.push(`${t.reason}: ${record.presenting_complaint.text}`);
  for (const h of record.history) S.push(`${h.source_role === 'owner_reported' ? `${t.owner}: ` : ''}${h.finding}: ${h.value}`);

  const O: string[] = [];
  const v = record.examination.vitals;
  const vit = ([[t.temp, v.temperature], [t.hr, v.heart_rate], [t.rr, v.respiratory_rate], [t.weight, v.weight], [t.crt, v.crt_seconds]] as const)
    .filter(([, q]) => q).map(([l, q]) => `${l} ${unitText(q!)}`);
  if (vit.length) O.push(vit.join(' · '));
  for (const f of record.examination.findings) O.push(`${f.system}: ${f.text}`);
  for (const d of record.diagnostics) O.push(`${d.test} (${t.status[d.status]})${d.result ? `: ${d.result}` : ''}`);

  const A: string[] = [];
  if (record.assessment.text) A.push(record.assessment.text);
  if (record.assessment.differentials.length) A.push(`${t.diff}: ${record.assessment.differentials.map((d) => d.text).join('; ')}`);

  const P: string[] = [];
  for (const x of record.treatments) P.push(`${x.text} (${t.status[x.status]})`);
  for (const m of record.medications) {
    const drug = m.drug ?? (m.class_as_written ? `${m.class_as_written} ${flag(`${t.missing}: ${t.drug}`)}` : flag(`${t.missing}: ${t.drug}`));
    const dose = m.dose == null ? flag(`${t.missing}: ${t.dose}`) : `${m.dose} ${m.dose_unit ?? ''}`.trim();
    const parts = [drug, dose, m.route ?? flag(`${t.missing}: ${t.route}`), m.frequency ?? flag(`${t.missing}: ${t.freq}`), m.duration].filter(Boolean);
    P.push(`${parts.join(', ')} (${t.status[m.status]})`);
  }
  if (record.plan.follow_up) P.push(`${t.fu}: ${record.plan.follow_up.text}`);
  for (const i of record.plan.instructions) P.push(i.text);
  // What the vet typed (or marked as not recorded) for a missing field at approval is the vet's own text, labelled as such.
  for (const m of record.missing) if (!resolutions[m.field]) P.push(flag(`${t.missing}: ${m.field}`));
  const added = Object.entries(resolutions).filter(([, v]) => v.trim());
  if (added.length) P.push(`${t.atApproval}:`, ...added.map(([f, v]) => `${f}: ${v}`));

  const out = (key: SoapField['key'], lines: string[]): SoapField => ({ key, label: t[key], text: lines.length ? lines.join('\n') : t.none });
  return [out('S', S), out('O', O), out('A', A), out('P', P)];
}

export type ExportBundle = {
  format: 'aiveterinary.export/1';
  exported_at: string;
  patient: PatientHeader;
  provenance: {
    ai_assisted: true;
    content_added_by_ai: 0;
    disclosure: string;
    version: number;
    approved_by: string;
    approved_at: string;
    supersedes: number | null;
    amendment_reason: string | null;
    fingerprint: string;
  };
  soap: SoapField[];
  resolutions_at_approval: Record<string, string>;
  record: ClinicalRecord;
};

/**
 * The JSON file for import or archive. Only an approved version can be exported,
 * and the fingerprint is re-checked so a record changed after approval is refused.
 */
export function exportBundle(v: ApprovedVersion, header: PatientHeader, lang: ExportLang = 'en', at = new Date().toISOString(), resolutions: Record<string, string> = {}): ExportBundle {
  if (fingerprint(v.record) !== v.fingerprint) throw new Error('The record no longer matches its approval; export refused.');
  return {
    format: 'aiveterinary.export/1',
    exported_at: at,
    patient: header,
    provenance: {
      ai_assisted: true, content_added_by_ai: 0, disclosure: T[lang].disclosure,
      version: v.version, approved_by: v.approved_by, approved_at: v.approved_at, supersedes: v.supersedes, amendment_reason: v.amendment_reason, fingerprint: v.fingerprint,
    },
    soap: soapFields(v.record, lang, resolutions),
    resolutions_at_approval: { ...resolutions },
    record: v.record,
  };
}
