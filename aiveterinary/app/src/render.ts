import type { ClinicalRecord, Medication, Missing, PatientHeader } from './schema.js';
import { provenance } from './country.js';

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
    temp: 'Temperature', hr: 'Heart rate', rr: 'Respiratory rate', weight: 'Weight', provenance: 'Facts from the notes: {f} · Not recorded: {n} · Added by AI: 0', declinedCare: 'Declined care', declinedIntro: 'The following recommended care was declined by the owner. Acknowledged by the owner:', signature: 'Signature / date', draft: 'DRAFT — AI-assisted, not yet reviewed', disclosure: 'Structured with AI assistance from the veterinarian\'s own notes; reviewed and approved by the veterinarian. No content was added by the AI.',
  },
  de: {
    title: 'Behandlungsbericht', patient: 'Patient', reason: 'Vorstellungsgrund', history: 'Anamnese', exam: 'Klinische Untersuchung',
    diagnostics: 'Diagnostik', assessment: 'Beurteilung', treatment: 'Behandlung', medication: 'Medikation', plan: 'Weiteres Vorgehen',
    notRecorded: 'Nicht erfasst', missing: 'Fehlt', ownerReports: 'Laut Besitzer', performed: 'durchgeführt', planned: 'geplant', declined: 'vom Besitzer abgelehnt',
    recommended: 'empfohlen', dispensed: 'abgegeben', prescribed: 'verschrieben', drug: 'Wirkstoff', dose: 'Dosis', route: 'Applikation', freq: 'Häufigkeit', dur: 'Dauer',
    temp: 'Temperatur', hr: 'Herzfrequenz', rr: 'Atemfrequenz', weight: 'Gewicht', provenance: 'Fakten aus den Notizen: {f} · Nicht erfasst: {n} · Von KI hinzugefügt: 0', declinedCare: 'Abgelehnte Maßnahmen', declinedIntro: 'Die folgenden empfohlenen Maßnahmen wurden vom Besitzer abgelehnt. Zur Kenntnis genommen durch den Besitzer:', signature: 'Unterschrift / Datum', draft: 'ENTWURF — KI-unterstützt, noch nicht geprüft', disclosure: 'Mit KI-Unterstützung aus den eigenen Notizen der Tierärztin/des Tierarztes strukturiert; tierärztlich geprüft und freigegeben. Die KI hat keine Inhalte hinzugefügt.',
  },
  it: {
    title: 'Referto di visita', patient: 'Paziente', reason: 'Motivo della visita', history: 'Anamnesi', exam: 'Esame clinico',
    diagnostics: 'Esami diagnostici', assessment: 'Valutazione', treatment: 'Trattamento', medication: 'Terapia farmacologica', plan: 'Controlli e piano',
    notRecorded: 'Non registrato', missing: 'Mancante', ownerReports: 'Il proprietario riferisce', performed: 'eseguito', planned: 'pianificato', declined: 'rifiutato dal proprietario',
    recommended: 'consigliato', dispensed: 'consegnato', prescribed: 'prescritto', drug: 'Farmaco', dose: 'Dose', route: 'Via', freq: 'Frequenza', dur: 'Durata',
    temp: 'Temperatura', hr: 'Frequenza cardiaca', rr: 'Frequenza respiratoria', weight: 'Peso', provenance: 'Fatti dalle note: {f} · Non registrato: {n} · Aggiunto dall\'IA: 0', declinedCare: 'Prestazioni rifiutate', declinedIntro: 'Le seguenti prestazioni consigliate sono state rifiutate dal proprietario. Preso atto dal proprietario:', signature: 'Firma / data', draft: 'BOZZA — assistita da IA, non ancora verificata', disclosure: 'Strutturato con assistenza IA a partire dalle note del veterinario; verificato e approvato dal veterinario. L\'IA non ha aggiunto contenuti.',
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

export function renderConsultReport(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; extraMissing?: Missing[] } = {}): string {
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
  const declined = [
    ...record.diagnostics.filter((d) => d.status === 'declined').map((d) => cap(d.test)),
    ...record.treatments.filter((x) => x.status === 'declined').map((x) => cap(x.text)),
    ...record.medications.filter((m) => m.status === 'declined').map((m) => m.drug ?? m.class_as_written ?? t.drug),
  ];
  if (declined.length) {
    out.push('');
    out.push(`## ${t.declinedCare}`);
    out.push(t.declinedIntro);
    for (const d of declined) out.push(`- ${d}`);
    out.push('');
    out.push(`${t.signature}: ______________________`);
  }
  const allMissing = [...record.missing, ...(opts.extraMissing ?? [])];
  if (allMissing.length) {
    out.push('');
    out.push(`## ${flag(t.missing)}`);
    for (const m of allMissing) out.push(`- ${m.field}: ${m.reason}`);
  }
  const p = provenance(record, opts.extraMissing ?? []);
  out.push('');
  out.push(`_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Documents derived from the approved record. Same rule as the report: */
/* headings are code, sentences are the record's own, nothing is added. */

const D = {
  en: { ownerTitle: 'What happened today, and what to do at home', forOwner: 'For the owner of', reason: 'Why you came', found: 'What we found', done: 'What we did', meds: 'Medication to give', home: 'At home', next: 'Next appointment', call: 'Call us if', declined: 'Discussed and declined', nothingNoted: 'Nothing further was noted.', referralTitle: 'Referral letter', dear: 'Dear colleague', referralIntro: 'I am referring the following patient to you.', referralReason: 'Reason for referral', historyHdr: 'History and findings', diagHdr: 'Diagnostics', treatHdr: 'Treatment so far', thanks: 'Thank you for seeing this patient. Please send your findings back to us.', missingReason: 'Reason for referral not stated in the notes' },
  de: { ownerTitle: 'Was heute war, und was zu Hause zu tun ist', forOwner: 'Für die Halterin / den Halter von', reason: 'Warum Sie gekommen sind', found: 'Was wir festgestellt haben', done: 'Was wir gemacht haben', meds: 'Medikamente geben', home: 'Zu Hause', next: 'Nächster Termin', call: 'Rufen Sie an, wenn', declined: 'Besprochen und abgelehnt', nothingNoted: 'Weiteres wurde nicht notiert.', referralTitle: 'Überweisungsschreiben', dear: 'Liebe Kollegin, lieber Kollege', referralIntro: 'Ich überweise Ihnen folgenden Patienten.', referralReason: 'Überweisungsgrund', historyHdr: 'Vorbericht und Befunde', diagHdr: 'Diagnostik', treatHdr: 'Bisherige Behandlung', thanks: 'Vielen Dank für die Übernahme. Bitte senden Sie uns Ihre Befunde zurück.', missingReason: 'Überweisungsgrund in den Notizen nicht angegeben' },
  it: { ownerTitle: 'Cosa è successo oggi e cosa fare a casa', forOwner: 'Per il proprietario di', reason: 'Perché siete venuti', found: 'Cosa abbiamo trovato', done: 'Cosa abbiamo fatto', meds: 'Farmaci da somministrare', home: 'A casa', next: 'Prossimo appuntamento', call: 'Chiamateci se', declined: 'Discusso e rifiutato', nothingNoted: 'Non è stato annotato altro.', referralTitle: 'Lettera di riferimento', dear: 'Gentile collega', referralIntro: 'Le invio il seguente paziente.', referralReason: 'Motivo dell\'invio', historyHdr: 'Anamnesi e reperti', diagHdr: 'Esami', treatHdr: 'Trattamento finora', thanks: 'Grazie per la presa in carico. La prego di inviarci i Suoi referti.', missingReason: 'Motivo dell\'invio non indicato nelle note' },
};

const headerLine = (header: PatientHeader) => [header.name, header.species, header.breed, header.sex, header.age ? `${header.age.value} ${header.age.unit}${header.age.value === 1 ? '' : 's'}` : null, header.weight_kg ? `${header.weight_kg} kg` : null].filter(Boolean).join(' — ');

/** Owner summary: the same facts in the same words, grouped for the person who has to act at home. */
export function renderOwnerSummary(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; extraMissing?: Missing[] } = {}): string {
  const t = L[lang], d = D[lang];
  const out: string[] = [];
  out.push(`# ${d.ownerTitle}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${d.forOwner} ${header.name}** — ${headerLine(header)}`);
  out.push('');
  out.push(`## ${d.reason}`);
  out.push(record.presenting_complaint ? cap(record.presenting_complaint.text) : flag(t.missing));
  out.push('');
  out.push(`## ${d.found}`);
  const found = [...record.examination.findings.map((f) => `- ${cap(f.system)}: ${f.text}`), ...record.diagnostics.filter((x) => x.status === 'performed').map((x) => `- ${cap(x.test)}: ${x.result ?? flag(`${t.missing}: result`)}`)];
  if (record.assessment.text) found.push(`- ${cap(record.assessment.text)}`);
  out.push(...(found.length ? found : [d.nothingNoted]));
  out.push('');
  out.push(`## ${d.done}`);
  const done = [...record.treatments.filter((x) => x.status === 'performed').map((x) => `- ${cap(x.text)}`), ...record.medications.filter((m) => m.status === 'performed').map((m) => `- ${m.drug ?? m.class_as_written ?? t.drug}`)];
  out.push(...(done.length ? done : [d.nothingNoted]));
  const toGive = record.medications.filter((m) => m.status === 'dispensed' || m.status === 'prescribed');
  if (toGive.length) { out.push(''); out.push(`## ${d.meds}`); out.push(renderMedicationTable(toGive, lang)); const cl = renderDoseChecklist(toGive, lang); if (cl) { out.push(''); out.push(cl); } }
  const home = [...record.plan.instructions.map((i) => `- ${cap(i.text)}`), ...record.treatments.filter((x) => x.status === 'recommended' && x.type === 'advice').map((x) => `- ${cap(x.text)}`)];
  if (home.length) { out.push(''); out.push(`## ${d.home}`); out.push(...home); }
  if (record.plan.follow_up) { out.push(''); out.push(`## ${d.next}`); out.push(cap(record.plan.follow_up.text)); }
  const declined = [...record.diagnostics.filter((x) => x.status === 'declined').map((x) => cap(x.test)), ...record.treatments.filter((x) => x.status === 'declined').map((x) => cap(x.text)), ...record.medications.filter((m) => m.status === 'declined').map((m) => m.drug ?? m.class_as_written ?? t.drug)];
  if (declined.length) { out.push(''); out.push(`## ${d.declined}`); out.push(...declined.map((x) => `- ${x}`)); }
  const allMissing = [...record.missing, ...(opts.extraMissing ?? [])];
  if (allMissing.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const m of allMissing) out.push(`- ${m.field}: ${m.reason}`); }
  const p = provenance(record, opts.extraMissing ?? []);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/** Referral letter: clinical, complete, with the referral reason flagged when the vet did not state one. */
export function renderReferralLetter(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; reason?: string | null; extraMissing?: Missing[] } = {}): string {
  const t = L[lang], d = D[lang];
  const out: string[] = [];
  out.push(`# ${d.referralTitle}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`${d.dear},`);
  out.push('');
  out.push(`${d.referralIntro} **${headerLine(header)}**`);
  out.push('');
  out.push(`## ${d.referralReason}`);
  out.push(opts.reason ? cap(opts.reason) : flag(d.missingReason));
  out.push('');
  out.push(`## ${d.historyHdr}`);
  out.push(record.presenting_complaint ? `- ${cap(record.presenting_complaint.text)}` : `- ${flag(t.missing)}`);
  for (const h of record.history) out.push(`- ${h.source_role === 'owner_reported' ? t.ownerReports + ': ' : ''}${h.finding}: ${h.value}`);
  const v = record.examination.vitals;
  const vitals = [v.temperature && `${t.temp} ${v.temperature.value} °${v.temperature.unit}`, v.heart_rate && `${t.hr} ${v.heart_rate.value}/min`, v.respiratory_rate && `${t.rr} ${v.respiratory_rate.value}/min`, v.weight && `${t.weight} ${v.weight.value} ${v.weight.unit}`].filter(Boolean);
  if (vitals.length) out.push(`- ${vitals.join('. ')}.`);
  for (const f of record.examination.findings) out.push(`- ${cap(f.system)}: ${f.text}`);
  if (record.assessment.text) out.push(`- ${t.assessment}: ${record.assessment.text}`);
  if (record.diagnostics.length) { out.push(''); out.push(`## ${d.diagHdr}`); for (const x of record.diagnostics) out.push(`- ${cap(x.test)} (${t[x.status] ?? x.status})${x.result ? `: ${x.result}` : x.status === 'performed' ? `: ${flag(`${t.missing}: result`)}` : ''}`); }
  if (record.treatments.length || record.medications.length) {
    out.push(''); out.push(`## ${d.treatHdr}`);
    for (const x of record.treatments) out.push(`- ${cap(x.text)} (${t[x.status] ?? x.status})`);
    if (record.medications.length) { out.push(''); out.push(renderMedicationTable(record.medications, lang)); }
  }
  out.push(''); out.push(d.thanks);
  const allMissing = [...record.missing, ...(opts.extraMissing ?? []), ...(opts.reason ? [] : [{ field: 'referral.reason', reason: d.missingReason }])];
  if (allMissing.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const m of allMissing) out.push(`- ${m.field}: ${m.reason}`); }
  const p = provenance(record, opts.extraMissing ?? []);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded + (opts.reason ? 0 : 1)))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Home-care dose checklist: a grid drawn from the medication table.    */
/* Only when frequency and duration parse unambiguously; otherwise the  */
/* medication is listed with a flag and no grid is invented.           */

const SLOTS = {
  en: ['morning', 'midday', 'evening', 'night'], de: ['morgens', 'mittags', 'abends', 'nachts'], it: ['mattina', 'mezzogiorno', 'sera', 'notte'],
};
const C = {
  en: { title: 'Dose checklist', day: 'Day', unparsed: 'Frequency or duration not clear enough for a checklist; follow the table above', once: 'once' },
  de: { title: 'Gabeplan zum Abhaken', day: 'Tag', unparsed: 'Häufigkeit oder Dauer nicht eindeutig genug für einen Plan; bitte Tabelle oben beachten', once: 'einmalig' },
  it: { title: 'Piano delle somministrazioni', day: 'Giorno', unparsed: 'Frequenza o durata non abbastanza chiare per un piano; seguire la tabella sopra', once: 'una volta' },
};

/** Parses "2x daily", "2x tgl", "BID", "q12h", "ogni 12 ore", "3 volte al giorno" → doses per day; returns null when unsure. */
export function parseDosesPerDay(frequency: string | null | undefined): number | null {
  if (!frequency) return null;
  const f = frequency.toLowerCase().replace(/\s+/g, ' ').trim();
  if (/\b(sid|od|once daily|once a day|1 ?x|1 ?mal|einmal|una volta|1 volta)\b/.test(f) && !/\b(bid|tid|qid)\b/.test(f)) return 1;
  if (/\bbid\b|\b2 ?x\b|\b2 ?mal\b|zweimal|twice|2 volte|due volte|q ?12 ?h|ogni 12|alle 12|every 12/.test(f)) return 2;
  if (/\btid\b|\b3 ?x\b|\b3 ?mal\b|dreimal|three times|3 volte|tre volte|q ?8 ?h|ogni 8|alle 8|every 8/.test(f)) return 3;
  if (/\bqid\b|\b4 ?x\b|\b4 ?mal\b|viermal|four times|4 volte|q ?6 ?h|ogni 6|alle 6|every 6/.test(f)) return 4;
  return null;
}

/** Parses "7 days", "7 Tage", "7 giorni", "7d", "1 week" → days; null when unsure. */
export function parseDurationDays(duration: string | null | undefined): number | null {
  if (!duration) return null;
  const d = duration.toLowerCase();
  const m = /(\d+)\s*(d|days?|tage?|tg|giorn[oi]|gg)\b/.exec(d); if (m) return Number(m[1]);
  const w = /(\d+)\s*(w|weeks?|wochen?|settimane?|sett)\b/.exec(d); if (w) return Number(w[1]) * 7;
  return null;
}

export function renderDoseChecklist(meds: Medication[], lang: Lang): string {
  const c = C[lang], slots = SLOTS[lang];
  const out: string[] = [];
  const give = meds.filter((m) => m.status === 'dispensed' || m.status === 'prescribed');
  if (!give.length) return '';
  out.push(`### ${c.title}`);
  for (const m of give) {
    const name = m.drug ?? m.class_as_written ?? '?';
    const perDay = parseDosesPerDay(m.frequency), days = parseDurationDays(m.duration);
    if (!perDay || !days || days > 60) { out.push(`- **${name}**: ${flag(c.unparsed)}`); continue; }
    const use = perDay === 1 ? [slots[0]] : perDay === 2 ? [slots[0], slots[2]] : perDay === 3 ? [slots[0], slots[1], slots[2]] : slots;
    out.push(''); out.push(`**${name}** — ${m.dose != null ? `${m.dose} ${m.dose_unit ?? ''}`.trim() + ', ' : ''}${perDay} × ${days} ${lang === 'en' ? 'days' : lang === 'de' ? 'Tage' : 'giorni'}`);
    out.push(`| ${c.day} | ${use.join(' | ')} |`); out.push(`|---|${use.map(() => '---').join('|')}|`);
    for (let i = 1; i <= days; i++) out.push(`| ${i} | ${use.map(() => '☐').join(' | ')} |`);
  }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Prescription per dispensed or prescribed medicine (Art. 105(5)       */
/* Reg. (EU) 2019/6 content). Every line comes from the record or the   */
/* vet-entered visit context; anything absent is a flag, never a guess. */

import type { VisitContext } from './country.js';

const P = {
  en: { title: 'Veterinary prescription', keeper: 'Animal keeper', animal: 'Animal', product: 'Medicinal product', dose: 'Dosage regimen', quantity: 'Quantity', duration: 'Duration of treatment', route: 'Route', date: 'Date', vet: 'Prescribing veterinarian', signature: 'Signature', withdrawal: 'Withdrawal period', notApplicable: 'not applicable (non food-producing animal)', nothing: 'No dispensed or prescribed medicine in this record.', missingKeeper: 'keeper name and address required on a prescription', missingProduct: 'product name as on the pack', missingQty: 'quantity to dispense', missingVet: 'prescribing veterinarian', missingChip: 'animal identification (microchip)' },
  de: { title: 'Tierärztliche Verschreibung', keeper: 'Tierhalterin / Tierhalter', animal: 'Tier', product: 'Arzneimittel', dose: 'Dosierung', quantity: 'Menge', duration: 'Anwendungsdauer', route: 'Applikation', date: 'Datum', vet: 'Verschreibende Tierärztin / verschreibender Tierarzt', signature: 'Unterschrift', withdrawal: 'Wartezeit', notApplicable: 'entfällt (kein Lebensmittel lieferndes Tier)', nothing: 'Keine abgegebenen oder verschriebenen Arzneimittel in diesem Datensatz.', missingKeeper: 'Name und Anschrift der Tierhalterin / des Tierhalters', missingProduct: 'Arzneimittelbezeichnung wie auf der Packung', missingQty: 'abzugebende Menge', missingVet: 'verschreibende Tierärztin / verschreibender Tierarzt', missingChip: 'Tieridentifikation (Chipnummer)' },
  it: { title: 'Prescrizione veterinaria', keeper: 'Proprietario / detentore', animal: 'Animale', product: 'Medicinale', dose: 'Posologia', quantity: 'Quantità', duration: 'Durata del trattamento', route: 'Via', date: 'Data', vet: 'Veterinario prescrittore', signature: 'Firma', withdrawal: 'Tempo di sospensione', notApplicable: 'non applicabile (animale non destinato alla produzione di alimenti)', nothing: 'Nessun medicinale consegnato o prescritto in questa cartella.', missingKeeper: 'nome e indirizzo del proprietario', missingProduct: 'nome del medicinale come sulla confezione', missingQty: 'quantità da consegnare', missingVet: 'veterinario prescrittore', missingChip: 'identificazione dell\'animale (microchip)' },
};

export function renderPrescription(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { approved?: boolean; date?: string } = {}): string {
  const t = L[lang], p = P[lang];
  const out: string[] = [];
  out.push(`# ${p.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  const miss: Missing[] = [];
  const keeper = [ctx.owner.name, ctx.owner.tax_id].filter(Boolean).join(' · ');
  if (!ctx.owner.name) miss.push({ field: 'owner.name', reason: p.missingKeeper });
  out.push(`**${p.keeper}:** ${keeper || flag(p.missingKeeper)}`);
  out.push(`**${p.animal}:** ${headerLine(header)}${ctx.microchip ? ` · ${ctx.microchip}` : ` · ${flag(p.missingChip)}`}`);
  if (!ctx.microchip) miss.push({ field: 'microchip', reason: p.missingChip });
  out.push(`**${p.date}:** ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
  out.push('');
  const give = record.medications.map((m, i) => ({ m, i })).filter(({ m }) => m.status === 'dispensed' || m.status === 'prescribed');
  if (!give.length) out.push(p.nothing);
  for (const { m, i } of give) {
    const d = ctx.dispensings.find((x) => x.medication_index === i);
    const product = d?.product ?? null;
    if (!product) miss.push({ field: `dispensings[${i}].product`, reason: p.missingProduct });
    if (!d?.quantity) miss.push({ field: `dispensings[${i}].quantity`, reason: p.missingQty });
    out.push(`## ${product ?? `${m.drug ?? m.class_as_written ?? t.drug} ${flag(p.missingProduct)}`}`);
    out.push(`- ${p.dose}: ${m.dose != null ? `${m.dose} ${m.dose_unit ?? ''}`.trim() : flag(`${t.missing}: ${t.dose.toLowerCase()}`)}${m.frequency ? `, ${m.frequency}` : ` ${flag(`${t.missing}: ${t.freq.toLowerCase()}`)}`}`);
    out.push(`- ${p.route}: ${m.route ?? flag(`${t.missing}: ${t.route.toLowerCase()}`)}`);
    out.push(`- ${p.duration}: ${m.duration ?? flag(`${t.missing}: ${t.dur.toLowerCase()}`)}`);
    out.push(`- ${p.quantity}: ${d?.quantity ? `${d.quantity.value} ${d.quantity.unit}` : flag(p.missingQty)}${d?.pack ? ` (${d.pack})` : ''}`);
    if (d?.authorisation_number || d?.batch) out.push(`- ${[d.authorisation_number && `Zul.-Nr./AIC ${d.authorisation_number}`, d.batch && `Lot ${d.batch}`].filter(Boolean).join(' · ')}`);
    out.push(`- ${p.withdrawal}: ${p.notApplicable}`);
    out.push('');
  }
  out.push(`**${p.vet}:** ${[ctx.author.name, ctx.author.registration].filter(Boolean).join(', ') || flag(p.missingVet)}`);
  if (!ctx.author.name) miss.push({ field: 'author.name', reason: p.missingVet });
  out.push(`${p.signature}: ______________________`);
  if (miss.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const x of miss) out.push(`- ${x.field}: ${x.reason}`); }
  const pr = provenance(record, miss);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(pr.facts)).replace('{n}', String(pr.not_recorded))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Vaccination entry: the booklet/passport page line for each vaccine  */
/* given today. Batch, site and validity come from the vet's dispensing */
/* record; absent values are flags so the booklet is never filled with  */
/* guesses.                                                            */

const V = {
  en: { title: 'Vaccination entry', vaccine: 'Vaccine', batch: 'Batch / lot', site: 'Site', date: 'Date given', valid: 'Valid until', vet: 'Veterinarian', chip: 'Microchip', none: 'No vaccine recorded as given today.', missingBatch: 'batch/lot number is required for every vaccination entry', missingValid: 'validity end not stated', missingChip: 'animal identification (microchip)', missingVet: 'veterinarian name and registration' },
  de: { title: 'Impfeintrag', vaccine: 'Impfstoff', batch: 'Charge', site: 'Applikationsort', date: 'Impfdatum', valid: 'Gültig bis', vet: 'Tierärztin / Tierarzt', chip: 'Chipnummer', none: 'Heute keine Impfung als durchgeführt erfasst.', missingBatch: 'Chargenbezeichnung ist für jeden Impfeintrag erforderlich', missingValid: 'Gültigkeitsende nicht angegeben', missingChip: 'Tieridentifikation (Chipnummer)', missingVet: 'Name und Kammer der Tierärztin / des Tierarztes' },
  it: { title: 'Registrazione vaccinale', vaccine: 'Vaccino', batch: 'Lotto', site: 'Sede', date: 'Data', valid: 'Valido fino al', vet: 'Veterinario', chip: 'Microchip', none: 'Nessun vaccino registrato come somministrato oggi.', missingBatch: 'il numero di lotto è obbligatorio per ogni registrazione vaccinale', missingValid: 'scadenza della validità non indicata', missingChip: 'identificazione dell\'animale (microchip)', missingVet: 'nome e iscrizione del veterinario' },
};
const isVaccineName = (m: Medication) => /vacc|impf|vakzin/i.test(`${m.drug ?? ''} ${m.class_as_written ?? ''}`);

export function renderVaccinationEntry(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { approved?: boolean; date?: string } = {}): string {
  const t = L[lang], v = V[lang];
  const out: string[] = [];
  out.push(`# ${v.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${headerLine(header)}** · ${v.chip}: ${ctx.microchip ?? flag(v.missingChip)}`);
  out.push('');
  const miss: Missing[] = [];
  if (!ctx.microchip) miss.push({ field: 'microchip', reason: v.missingChip });
  const given = record.medications.map((m, i) => ({ m, i })).filter(({ m }) => isVaccineName(m) && (m.status === 'performed' || m.status === 'dispensed'));
  if (!given.length) out.push(v.none);
  else {
    out.push(`| ${v.vaccine} | ${v.date} | ${v.batch} | ${v.site} | ${v.valid} |`);
    out.push('|---|---|---|---|---|');
    for (const { m, i } of given) {
      const d = ctx.dispensings.find((x) => x.medication_index === i);
      if (!d?.batch) miss.push({ field: `dispensings[${i}].batch`, reason: v.missingBatch });
      if (!d?.valid_until) miss.push({ field: `dispensings[${i}].valid_until`, reason: v.missingValid });
      out.push(`| ${d?.product ?? m.drug ?? m.class_as_written} | ${opts.date ?? new Date().toISOString().slice(0, 10)} | ${d?.batch ?? flag(v.missingBatch)} | ${d?.site ?? '—'} | ${d?.valid_until ?? flag(v.missingValid)} |`);
    }
  }
  out.push('');
  out.push(`**${v.vet}:** ${[ctx.author.name, ctx.author.registration].filter(Boolean).join(', ') || flag(v.missingVet)}`);
  if (!ctx.author.name) miss.push({ field: 'author.name', reason: v.missingVet });
  if (miss.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const x of miss) out.push(`- ${x.field}: ${x.reason}`); }
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}
