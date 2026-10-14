import type { ClinicalRecord, Medication, PatientHeader } from './schema.js';

/**
 * Deterministic rendering of the record into a consultation report.
 * No model involved: headings, patient header, vitals, medication table and
 * missing flags are code. Prose sections are the record's own sentences.
 */

const L = {
  en: {
    title: 'Consultation report', patient: 'Patient', reason: 'Reason for presentation', history: 'History', exam: 'Clinical examination',
    diagnostics: 'Diagnostics', assessment: 'Assessment', treatment: 'Treatment', medication: 'Medication', plan: 'Follow-up and plan',
    notRecorded: 'Not recorded', missing: 'Missing', ownerReports: 'Owner reports', performed: 'performed', planned: 'planned', declined: 'declined by owner',
    recommended: 'recommended', dispensed: 'dispensed', prescribed: 'prescribed', drug: 'Drug', dose: 'Dose', route: 'Route', freq: 'Frequency', dur: 'Duration',
    temp: 'Temperature', hr: 'Heart rate', rr: 'Respiratory rate', weight: 'Weight', draft: 'DRAFT — AI-assisted, not yet reviewed', disclosure: 'Structured with AI assistance from the veterinarian\'s own notes; reviewed and approved by the veterinarian. No content was added by the AI.',
  },
  de: {
    title: 'Behandlungsbericht', patient: 'Patient', reason: 'Vorstellungsgrund', history: 'Anamnese', exam: 'Klinische Untersuchung',
    diagnostics: 'Diagnostik', assessment: 'Beurteilung', treatment: 'Behandlung', medication: 'Medikation', plan: 'Weiteres Vorgehen',
    notRecorded: 'Nicht erfasst', missing: 'Fehlt', ownerReports: 'Laut Besitzer', performed: 'durchgeführt', planned: 'geplant', declined: 'vom Besitzer abgelehnt',
    recommended: 'empfohlen', dispensed: 'abgegeben', prescribed: 'verschrieben', drug: 'Wirkstoff', dose: 'Dosis', route: 'Applikation', freq: 'Häufigkeit', dur: 'Dauer',
    temp: 'Temperatur', hr: 'Herzfrequenz', rr: 'Atemfrequenz', weight: 'Gewicht', draft: 'ENTWURF — KI-unterstützt, noch nicht geprüft', disclosure: 'Mit KI-Unterstützung aus den eigenen Notizen der Tierärztin/des Tierarztes strukturiert; tierärztlich geprüft und freigegeben. Die KI hat keine Inhalte hinzugefügt.',
  },
  it: {
    title: 'Referto di visita', patient: 'Paziente', reason: 'Motivo della visita', history: 'Anamnesi', exam: 'Esame clinico',
    diagnostics: 'Esami diagnostici', assessment: 'Valutazione', treatment: 'Trattamento', medication: 'Terapia farmacologica', plan: 'Controlli e piano',
    notRecorded: 'Non registrato', missing: 'Mancante', ownerReports: 'Il proprietario riferisce', performed: 'eseguito', planned: 'pianificato', declined: 'rifiutato dal proprietario',
    recommended: 'consigliato', dispensed: 'consegnato', prescribed: 'prescritto', drug: 'Farmaco', dose: 'Dose', route: 'Via', freq: 'Frequenza', dur: 'Durata',
    temp: 'Temperatura', hr: 'Frequenza cardiaca', rr: 'Frequenza respiratoria', weight: 'Peso', draft: 'BOZZA — assistita da IA, non ancora verificata', disclosure: 'Strutturato con assistenza IA a partire dalle note del veterinario; verificato e approvato dal veterinario. L\'IA non ha aggiunto contenuti.',
  },
};
export type Lang = keyof typeof L;

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const flag = (t: string) => `▲ ${t}`;

export function renderMedicationTable(meds: Medication[], lang: Lang): string {
  const t = L[lang];
  if (meds.length === 0) return '';
  const head = `| ${t.drug} | ${t.dose} | ${t.route} | ${t.freq} | ${t.dur} | |\n|---|---|---|---|---|---|`;
  const rows = meds.map((m) => {
    const c = (v: string | number | null | undefined, name: string) => (v == null || v === '' ? flag(`${t.missing}: ${name}`) : String(v));
    const dose = m.dose == null ? flag(`${t.missing}: ${t.dose.toLowerCase()}`) : `${m.dose} ${m.dose_unit ?? ''}`.trim();
    const drug = m.drug ?? (m.class_as_written ? `${m.class_as_written} ${flag(`${t.missing}: ${t.drug.toLowerCase()}`)}` : flag(`${t.missing}: ${t.drug.toLowerCase()}`));
    return `| ${drug} | ${dose} | ${c(m.route, t.route.toLowerCase())} | ${c(m.frequency, t.freq.toLowerCase())} | ${m.duration ?? '—'} | ${t[m.status] ?? m.status} |`;
  });
  return [head, ...rows].join('\n');
}

export function renderConsultReport(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean } = {}): string {
  const t = L[lang];
  const out: string[] = [];
  out.push(`# ${t.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`## ${t.patient}`);
  const bits = [header.name, header.species, header.breed, header.sex, header.age ? `${header.age.value} ${header.age.unit}${header.age.value === 1 ? '' : 's'}` : null, header.weight_kg ? `${header.weight_kg} kg` : null].filter(Boolean);
  out.push(bits.join(' — '));
  out.push('');
  out.push(`## ${t.reason}`);
  out.push(record.presenting_complaint ? cap(record.presenting_complaint.text) : flag(t.missing));
  out.push('');
  out.push(`## ${t.history}`);
  if (record.history.length === 0) out.push(t.notRecorded);
  for (const h of record.history) out.push(`- ${h.source_role === 'owner_reported' ? t.ownerReports + ': ' : ''}${h.finding}: ${h.value}`);
  out.push('');
  out.push(`## ${t.exam}`);
  const v = record.examination.vitals;
  const vitals = [v.temperature && `${t.temp} ${v.temperature.value} °${v.temperature.unit}`, v.heart_rate && `${t.hr} ${v.heart_rate.value}/min`, v.respiratory_rate && `${t.rr} ${v.respiratory_rate.value}/min`, v.weight && `${t.weight} ${v.weight.value} ${v.weight.unit}`].filter(Boolean);
  if (vitals.length) out.push(vitals.join('. ') + '.');
  for (const f of record.examination.findings) out.push(`- ${cap(f.system)}: ${f.text}`);
  if (!vitals.length && record.examination.findings.length === 0) out.push(t.notRecorded);
  out.push('');
  out.push(`## ${t.diagnostics}`);
  if (record.diagnostics.length === 0) out.push(t.notRecorded);
  for (const d of record.diagnostics) out.push(`- ${cap(d.test)} (${t[d.status] ?? d.status}): ${d.result ?? flag(`${t.missing}: result`)}`);
  out.push('');
  out.push(`## ${t.assessment}`);
  out.push(record.assessment.text ?? (record.assessment.differentials.length ? record.assessment.differentials.map((d) => d.text).join(', ') : flag(t.missing)));
  out.push('');
  out.push(`## ${t.treatment}`);
  if (record.treatments.length === 0 && record.medications.length === 0) out.push(t.notRecorded);
  for (const x of record.treatments) out.push(`- ${cap(x.text)} (${t[x.status] ?? x.status})`);
  if (record.medications.length) { out.push(''); out.push(`### ${t.medication}`); out.push(renderMedicationTable(record.medications, lang)); }
  out.push('');
  out.push(`## ${t.plan}`);
  if (record.plan.follow_up) out.push(`- ${cap(record.plan.follow_up.text)}`);
  for (const i of record.plan.instructions) out.push(`- ${cap(i.text)}`);
  if (!record.plan.follow_up && record.plan.instructions.length === 0) out.push(t.notRecorded);
  if (record.missing.length) {
    out.push('');
    out.push(`## ${flag(t.missing)}`);
    for (const m of record.missing) out.push(`- ${m.field}: ${m.reason}`);
  }
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}
