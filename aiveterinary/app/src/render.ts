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

/* ------------------------------------------------------------------ */
/* Consent form for a planned procedure. The elements FNOVI and the     */
/* German/Austrian chambers expect are the headings; the content under  */
/* them is the vet's to write. The form never pre-writes risks or       */
/* alternatives.                                                        */

const K = {
  en: { title: 'Informed consent', procedure: 'Procedure', planned: 'Planned procedures in this record', noProcedure: 'No planned procedure in this record; name the procedure yourself.', diagnosis: 'Diagnosis or reason', what: 'What will be done', alternatives: 'Alternatives, including doing nothing', risks: 'Risks and possible complications', anaesthesia: 'Anaesthesia and its risks', cost: 'Estimated cost and what it covers', timing: 'When and how the information was given', contact: 'Who to contact afterwards', declaration: 'I have understood the above, my questions were answered, and I consent to the procedure described. I know I can withdraw consent before it starts.', owner: 'Owner / keeper', vet: 'Veterinarian', date: 'Date', signature: 'Signature', fill: 'to be completed by the veterinarian' },
  de: { title: 'Einwilligung nach Aufklärung', procedure: 'Eingriff', planned: 'Geplante Eingriffe in diesem Datensatz', noProcedure: 'Kein geplanter Eingriff im Datensatz; bitte den Eingriff benennen.', diagnosis: 'Diagnose oder Grund', what: 'Was gemacht wird', alternatives: 'Alternativen, einschließlich Abwarten', risks: 'Risiken und mögliche Komplikationen', anaesthesia: 'Narkose und ihre Risiken', cost: 'Voraussichtliche Kosten und was sie umfassen', timing: 'Wann und wie die Aufklärung erfolgte', contact: 'Ansprechpartner danach', declaration: 'Ich habe das Vorstehende verstanden, meine Fragen wurden beantwortet, und ich willige in den beschriebenen Eingriff ein. Ich weiß, dass ich die Einwilligung vor Beginn widerrufen kann.', owner: 'Halterin / Halter', vet: 'Tierärztin / Tierarzt', date: 'Datum', signature: 'Unterschrift', fill: 'von der Tierärztin / dem Tierarzt auszufüllen' },
  it: { title: 'Consenso informato', procedure: 'Procedura', planned: 'Procedure pianificate in questa cartella', noProcedure: 'Nessuna procedura pianificata nella cartella; indicare la procedura.', diagnosis: 'Diagnosi o motivo', what: 'In cosa consiste', alternatives: 'Alternative, compreso non intervenire', risks: 'Rischi e possibili complicanze', anaesthesia: 'Anestesia e relativi rischi', cost: 'Costo previsto e cosa comprende', timing: 'Modi e tempi dell\'informazione fornita', contact: 'Chi contattare dopo', declaration: 'Ho compreso quanto sopra, le mie domande hanno avuto risposta e acconsento alla procedura descritta. So di poter revocare il consenso prima dell\'inizio.', owner: 'Proprietario / detentore', vet: 'Veterinario', date: 'Data', signature: 'Firma', fill: 'a cura del veterinario' },
};

export function renderConsentForm(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { procedure?: string | null; date?: string } = {}): string {
  const t = L[lang], k = K[lang];
  const out: string[] = [];
  out.push(`# ${k.title}`);
  out.push('');
  out.push(`**${headerLine(header)}**${ctx.microchip ? ` · ${ctx.microchip}` : ''}`);
  out.push(`**${k.owner}:** ${ctx.owner.name ?? '______________________'}`);
  out.push(`**${k.date}:** ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
  out.push('');
  const planned = record.treatments.filter((x) => x.type === 'procedure' && x.status === 'planned').map((x) => cap(x.text));
  out.push(`## ${k.procedure}`);
  if (opts.procedure) out.push(cap(opts.procedure));
  else if (planned.length) { out.push(`${k.planned}:`); for (const p of planned) out.push(`- ${p}`); }
  else out.push(flag(k.noProcedure));
  out.push('');
  out.push(`## ${k.diagnosis}`);
  out.push(record.assessment.text ? cap(record.assessment.text) : `_${k.fill}_`);
  for (const h of [k.what, k.alternatives, k.risks, k.anaesthesia, k.cost, k.timing, k.contact]) { out.push(''); out.push(`## ${h}`); out.push(`_${k.fill}_`); out.push(''); out.push('______________________________________________'); }
  out.push('');
  out.push(k.declaration);
  out.push('');
  out.push(`${k.owner} — ${k.signature}: ______________________   ${k.date}: ____________`);
  out.push(`${k.vet} — ${[ctx.author.name, ctx.author.registration].filter(Boolean).join(', ') || '______________________'} — ${k.signature}: ______________________`);
  out.push('');
  out.push(`_${t.provenance.replace('{f}', String(provenance(record).facts)).replace('{n}', String(record.missing.length))}_`);
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Cost estimate skeleton: planned items from the record as rows, price */
/* columns empty for the clinic's own list. Nothing priced by code.     */

const E = {
  en: { title: 'Cost estimate', intro: 'Planned items from today\'s record. Prices come from the clinic\'s own price list; this document contains none until the clinic fills them in.', item: 'Item', kind: 'Type', price: 'Price', note: 'Note', none: 'No planned items in this record.', total: 'Estimated total', validity: 'This estimate is valid for', legal: '', diagnostics: 'diagnostic', procedure: 'procedure', medication: 'medication', advice: 'advice' },
  de: { title: 'Kostenvoranschlag', intro: 'Geplante Positionen aus dem heutigen Datensatz. Die Preise stammen aus der Preisliste der Praxis; dieses Dokument enthält keine, bis die Praxis sie einträgt.', item: 'Position', kind: 'Art', price: 'Preis', note: 'Hinweis', none: 'Keine geplanten Positionen im Datensatz.', total: 'Voraussichtliche Summe', validity: 'Gültig für', legal: 'GOT: Nummer des Gebührenverzeichnisses und Faktor (1- bis 3-fach, §2 GOT) je Position; Angaben nach §7 Abs. 4 GOT auf der Rechnung.', diagnostics: 'Diagnostik', procedure: 'Eingriff', medication: 'Arzneimittel', advice: 'Beratung' },
  it: { title: 'Preventivo', intro: 'Voci pianificate dalla cartella di oggi. I prezzi provengono dal listino della clinica; questo documento non ne contiene finché la clinica non li inserisce.', item: 'Voce', kind: 'Tipo', price: 'Prezzo', note: 'Nota', none: 'Nessuna voce pianificata nella cartella.', total: 'Totale stimato', validity: 'Validità del preventivo', legal: 'Preventivo di massima in forma scritta o digitale (art. 9 c. 4 D.L. 1/2012, L. 124/2017); importi IVA inclusa o esclusa da indicare; estremi della polizza RC professionale.', diagnostics: 'esame', procedure: 'procedura', medication: 'farmaco', advice: 'consulenza' },
};

export function renderCostEstimate(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { date?: string } = {}): string {
  const e = E[lang];
  const out: string[] = [];
  out.push(`# ${e.title}`);
  out.push('');
  out.push(`**${headerLine(header)}**${ctx.owner.name ? ` · ${ctx.owner.name}` : ''} · ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
  out.push('');
  out.push(e.intro);
  out.push('');
  const rows: string[] = [];
  for (const d of record.diagnostics) if (d.status === 'planned' || d.status === 'recommended') rows.push(`| ${cap(d.test)} | ${e.diagnostics} | | |`);
  for (const x of record.treatments) if (x.status === 'planned' || x.status === 'recommended') rows.push(`| ${cap(x.text)} | ${x.type === 'procedure' ? e.procedure : e.advice} | | |`);
  for (const m of record.medications) if (m.status === 'prescribed' || m.status === 'recommended') rows.push(`| ${m.drug ?? m.class_as_written ?? '?'} | ${e.medication} | | |`);
  if (!rows.length) out.push(e.none);
  else {
    const extra = lang === 'de' ? ' GOT-Nr. | Faktor |' : '';
    out.push(`| ${e.item} | ${e.kind} |${extra} ${e.price} | ${e.note} |`);
    out.push(`|---|---|${lang === 'de' ? '---|---|' : ''}---|---|`);
    for (const r of rows) out.push(lang === 'de' ? r.replace(' | | |', ' | | | | |') : r);
    out.push(`| **${e.total}** | | ${lang === 'de' ? '| | ' : ''}______ | |`);
  }
  out.push('');
  out.push(`${e.validity}: ______________`);
  if (e.legal) { out.push(''); out.push(`_${e.legal}_`); }
  out.push('');
  out.push(`_${L[lang].provenance.replace('{f}', String(provenance(record).facts)).replace('{n}', String(record.missing.length))}_`);
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Anaesthesia and surgery record: the team's entries as a table, with  */
/* the fields a complete record needs flagged when absent.              */

import type { AnaesthesiaRecord } from './country.js';

const A = {
  en: { title: 'Anaesthesia and surgery record', procedure: 'Procedure', asa: 'ASA status', fasted: 'Fasted (hours)', premed: 'Premedication', induction: 'Induction', maintenance: 'Maintenance', airway: 'Airway', iv: 'IV access', fluids: 'Fluids', monitoring: 'Monitoring', time: 'Time', implants: 'Implants and materials', batch: 'batch', complications: 'Complications', recovery: 'Recovery', team: 'Team', anaesthetist: 'Anaesthetist', surgeon: 'Surgeon', times: 'Start / end', none: 'none recorded', yes: 'yes', no: 'no', missingAsa: 'ASA status not recorded', missingProtocol: 'anaesthetic protocol (premedication, induction, maintenance) incomplete', missingMonitoring: 'no monitoring values recorded', missingRecovery: 'recovery not documented', missingProcedure: 'procedure not named', missingTeam: 'anaesthetist or surgeon not named', missingImplantBatch: 'implant without batch number' },
  de: { title: 'Narkose- und OP-Protokoll', procedure: 'Eingriff', asa: 'ASA-Status', fasted: 'Nüchtern (Stunden)', premed: 'Prämedikation', induction: 'Einleitung', maintenance: 'Erhaltung', airway: 'Atemweg', iv: 'Venenzugang', fluids: 'Infusion', monitoring: 'Überwachung', time: 'Zeit', implants: 'Implantate und Material', batch: 'Charge', complications: 'Komplikationen', recovery: 'Aufwachphase', team: 'Team', anaesthetist: 'Narkoseführung', surgeon: 'Operateur/in', times: 'Beginn / Ende', none: 'nichts erfasst', yes: 'ja', no: 'nein', missingAsa: 'ASA-Status nicht erfasst', missingProtocol: 'Narkoseprotokoll (Prämedikation, Einleitung, Erhaltung) unvollständig', missingMonitoring: 'keine Überwachungswerte erfasst', missingRecovery: 'Aufwachphase nicht dokumentiert', missingProcedure: 'Eingriff nicht benannt', missingTeam: 'Narkoseführung oder Operateur/in nicht benannt', missingImplantBatch: 'Implantat ohne Chargenbezeichnung' },
  it: { title: 'Cartella anestesiologica e chirurgica', procedure: 'Procedura', asa: 'Stato ASA', fasted: 'Digiuno (ore)', premed: 'Premedicazione', induction: 'Induzione', maintenance: 'Mantenimento', airway: 'Vie aeree', iv: 'Accesso venoso', fluids: 'Fluidi', monitoring: 'Monitoraggio', time: 'Ora', implants: 'Impianti e materiali', batch: 'lotto', complications: 'Complicanze', recovery: 'Risveglio', team: 'Équipe', anaesthetist: 'Anestesista', surgeon: 'Chirurgo', times: 'Inizio / fine', none: 'nulla registrato', yes: 'sì', no: 'no', missingAsa: 'stato ASA non registrato', missingProtocol: 'protocollo anestesiologico (premedicazione, induzione, mantenimento) incompleto', missingMonitoring: 'nessun valore di monitoraggio registrato', missingRecovery: 'risveglio non documentato', missingProcedure: 'procedura non indicata', missingTeam: 'anestesista o chirurgo non indicati', missingImplantBatch: 'impianto senza numero di lotto' },
};

export function renderAnaesthesiaRecord(an: AnaesthesiaRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; date?: string } = {}): string {
  const t = L[lang], a = A[lang];
  const out: string[] = []; const miss: Missing[] = [];
  const v = (x: string | number | null | undefined, missingField?: string, reason?: string) => { if (x == null || x === '') { if (missingField && reason) miss.push({ field: missingField, reason }); return flag(t.missing); } return String(x); };
  out.push(`# ${a.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${headerLine(header)}** · ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
  out.push('');
  out.push(`- ${a.procedure}: ${v(an.procedure, 'procedure', a.missingProcedure)}`);
  out.push(`- ${a.asa}: ${v(an.asa, 'asa', a.missingAsa)}`);
  out.push(`- ${a.fasted}: ${an.fasted_hours ?? '—'}`);
  out.push(`- ${a.times}: ${an.start ?? '—'} / ${an.end ?? '—'}`);
  out.push('');
  out.push(`## ${a.premed} · ${a.induction} · ${a.maintenance}`);
  const protoMissing = !an.premedication || !an.induction || !an.maintenance;
  if (protoMissing) miss.push({ field: 'protocol', reason: a.missingProtocol });
  out.push(`- ${a.premed}: ${an.premedication ?? flag(t.missing)}`);
  out.push(`- ${a.induction}: ${an.induction ?? flag(t.missing)}`);
  out.push(`- ${a.maintenance}: ${an.maintenance ?? flag(t.missing)}`);
  out.push(`- ${a.airway}: ${an.airway ?? '—'} · ${a.iv}: ${an.iv_access == null ? '—' : an.iv_access ? a.yes : a.no} · ${a.fluids}: ${an.fluids ?? '—'}`);
  out.push('');
  out.push(`## ${a.monitoring}`);
  if (!an.monitoring.length) { miss.push({ field: 'monitoring', reason: a.missingMonitoring }); out.push(flag(a.missingMonitoring)); }
  else {
    out.push(`| ${a.time} | HR | RR | T | SpO₂ | MAP | |`); out.push('|---|---|---|---|---|---|---|');
    for (const m of an.monitoring) out.push(`| ${m.time} | ${m.hr ?? ''} | ${m.rr ?? ''} | ${m.temp ?? ''} | ${m.spo2 ?? ''} | ${m.map ?? ''} | ${m.note ?? ''} |`);
  }
  out.push('');
  out.push(`## ${a.implants}`);
  if (!an.implants.length) out.push(a.none);
  for (const im of an.implants) { if (!im.batch) miss.push({ field: 'implants.batch', reason: a.missingImplantBatch }); out.push(`- ${im.description} (${a.batch}: ${im.batch ?? flag(t.missing)})`); }
  out.push('');
  out.push(`## ${a.complications}`); out.push(an.complications ?? a.none);
  out.push('');
  out.push(`## ${a.recovery}`); out.push(v(an.recovery, 'recovery', a.missingRecovery));
  out.push('');
  out.push(`## ${a.team}`);
  if (!an.anaesthetist || !an.surgeon) miss.push({ field: 'team', reason: a.missingTeam });
  out.push(`- ${a.anaesthetist}: ${an.anaesthetist ?? flag(t.missing)}`); out.push(`- ${a.surgeon}: ${an.surgeon ?? flag(t.missing)}`);
  if (miss.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const x of miss) out.push(`- ${x.field}: ${x.reason}`); }
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Controlled-drugs register entry: one line per controlled substance   */
/* dispensed or administered today, from the dispensing record only.    */

const B = {
  en: { title: 'Controlled-drugs register entry', date: 'Date', product: 'Product', quantity: 'Quantity', balance: 'Balance after', patient: 'Patient / keeper', vet: 'Veterinarian', none: 'No controlled substance marked in today\'s dispensing record.', missingQty: 'quantity required for the register', missingVet: 'responsible veterinarian required', fill: 'to be entered from the register', note: 'Entries are made in the clinic\'s own register; this line is prepared from the record so nothing is retyped.' },
  de: { title: 'Eintrag Betäubungsmittelbuch', date: 'Datum', product: 'Betäubungsmittel', quantity: 'Menge (Zugang/Abgang)', balance: 'Bestand danach', patient: 'Patient / Halter', vet: 'Tierärztin / Tierarzt', none: 'Heute kein Betäubungsmittel im Abgabe-Nachweis markiert.', missingQty: 'Menge für das BtM-Buch erforderlich', missingVet: 'verantwortliche Tierärztin / verantwortlicher Tierarzt erforderlich', fill: 'aus dem BtM-Buch zu übernehmen', note: 'Die Eintragung erfolgt im BtM-Buch der Praxis (§13 BtMVV); diese Zeile wird aus dem Datensatz vorbereitet, damit nichts abgetippt wird.' },
  it: { title: 'Registro stupefacenti: voce', date: 'Data', product: 'Sostanza', quantity: 'Quantità (carico/scarico)', balance: 'Giacenza dopo', patient: 'Paziente / proprietario', vet: 'Veterinario', none: 'Nessuna sostanza stupefacente segnata nel registro di consegna di oggi.', missingQty: 'quantità necessaria per il registro', missingVet: 'veterinario responsabile necessario', fill: 'da riportare dal registro', note: 'La registrazione avviene nel registro di carico e scarico della clinica (D.P.R. 309/1990); questa voce è preparata dalla cartella per non ribattere nulla.' },
};

export function renderControlledDrugsEntry(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { date?: string } = {}): string {
  const t = L[lang], b = B[lang];
  const out: string[] = []; const miss: Missing[] = [];
  out.push(`# ${b.title}`); out.push('');
  const rows = ctx.dispensings.filter((d) => d.is_controlled);
  if (!rows.length) out.push(b.none);
  else {
    out.push(`| ${b.date} | ${b.product} | ${b.quantity} | ${b.balance} | ${b.patient} | ${b.vet} |`); out.push('|---|---|---|---|---|---|');
    for (const d of rows) {
      const m = record.medications[d.medication_index];
      if (!d.quantity) miss.push({ field: `dispensings[${d.medication_index}].quantity`, reason: b.missingQty });
      out.push(`| ${opts.date ?? new Date().toISOString().slice(0, 10)} | ${d.product ?? m?.drug ?? '?'} | ${d.quantity ? `−${d.quantity.value} ${d.quantity.unit}` : flag(b.missingQty)} | _${b.fill}_ | ${header.name}${ctx.owner.name ? ` / ${ctx.owner.name}` : ''} | ${ctx.author.name ?? flag(b.missingVet)} |`);
    }
    if (!ctx.author.name) miss.push({ field: 'author.name', reason: b.missingVet });
  }
  out.push(''); out.push(`_${b.note}_`);
  if (miss.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const x of miss) out.push(`- ${x.field}: ${x.reason}`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Lab-result explanation for the owner: the test, the result as        */
/* recorded, and the vet's own interpretation. No interpretation, no     */
/* explanation; the line is flagged instead.                            */

const X = {
  en: { title: 'Your animal\'s test results, explained', intro: 'Each result below is followed by what your veterinarian concluded from it, in their own words.', test: 'Test', result: 'Result', says: 'What your vet says', none: 'No test results were recorded at this visit.', missingInterp: 'the veterinarian has not yet written an explanation for this result', pending: 'result not yet available', planned: 'planned', close: 'If anything here is unclear, ask your vet; these are the words to use.' },
  de: { title: 'Die Untersuchungsergebnisse Ihres Tieres, erklärt', intro: 'Auf jedes Ergebnis folgt, was Ihre Tierärztin oder Ihr Tierarzt daraus schließt, in eigenen Worten.', test: 'Untersuchung', result: 'Ergebnis', says: 'Was Ihre Praxis dazu sagt', none: 'Bei diesem Besuch wurden keine Ergebnisse erfasst.', missingInterp: 'die Praxis hat zu diesem Ergebnis noch keine Erklärung geschrieben', pending: 'Ergebnis noch nicht verfügbar', planned: 'geplant', close: 'Wenn etwas unklar ist, fragen Sie in der Praxis nach; das sind die Begriffe, die Sie verwenden können.' },
  it: { title: 'I risultati degli esami del tuo animale, spiegati', intro: 'Ogni risultato è seguito da ciò che il tuo veterinario ne ha concluso, con parole sue.', test: 'Esame', result: 'Risultato', says: 'Cosa dice il tuo veterinario', none: 'In questa visita non sono stati registrati risultati.', missingInterp: 'il veterinario non ha ancora scritto una spiegazione per questo risultato', pending: 'risultato non ancora disponibile', planned: 'programmato', close: 'Se qualcosa non è chiaro, chiedi al tuo veterinario: queste sono le parole da usare.' },
};

export function renderLabExplanation(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { approved?: boolean } = {}): string {
  const t = L[lang], x = X[lang];
  const out: string[] = []; const miss: Missing[] = [];
  out.push(`# ${x.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push(''); out.push(`**${headerLine(header)}**`); out.push(''); out.push(x.intro); out.push('');
  if (!record.diagnostics.length) out.push(x.none);
  record.diagnostics.forEach((d, i) => {
    out.push(`## ${cap(d.test)}`);
    const interp = ctx.interpretations.find((p) => p.diagnostic_index === i)?.text ?? null;
    if (d.status === 'planned' || d.status === 'recommended') { out.push(`- ${x.result}: ${x.planned}`); out.push(''); return; }
    if (d.status === 'declined') { out.push(`- ${x.result}: ${t.declined}`); out.push(''); return; }
    out.push(`- ${x.result}: ${d.result ?? x.pending}`);
    if (interp) out.push(`- ${x.says}: ${cap(interp)}`);
    else { out.push(`- ${x.says}: ${flag(x.missingInterp)}`); miss.push({ field: `interpretations[${i}]`, reason: x.missingInterp }); }
    out.push('');
  });
  out.push(x.close);
  if (miss.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const m of miss) out.push(`- ${m.field}: ${m.reason}`); }
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(provenance(record).facts)).replace('{n}', String(record.missing.length + miss.length))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Antibiotic use block: the structured entry stewardship rules and     */
/* registries (TÄHAV §13, IS ABV, REV) ask for, per antibiotic given or */
/* prescribed today. Nothing inferred: agent from the record, the rest  */
/* from the dispensing record.                                          */

const AB = {
  en: { title: 'Antibiotic use', agent: 'Agent', product: 'Product', indication: 'Indication / justification', culture: 'Culture and sensitivity', route: 'Route', dose: 'Dose and frequency', duration: 'Duration', quantity: 'Quantity dispensed', none: 'No antibiotic marked in today\'s dispensing record.', missingJust: 'indication or justification for antibiotic use not recorded', missingDur: 'duration of the course not recorded', notDone: 'not done', done: 'done', rec: 'result pending or recorded elsewhere' },
  de: { title: 'Antibiotika-Anwendung', agent: 'Wirkstoff', product: 'Präparat', indication: 'Indikation / Begründung', culture: 'Antibiogramm', route: 'Applikation', dose: 'Dosis und Häufigkeit', duration: 'Dauer', quantity: 'Abgegebene Menge', none: 'Heute kein Antibiotikum im Abgabe-Nachweis markiert.', missingJust: 'Indikation oder Begründung der Antibiotika-Anwendung nicht erfasst', missingDur: 'Behandlungsdauer nicht erfasst', notDone: 'nicht erstellt', done: 'erstellt', rec: 'Ergebnis ausstehend oder andernorts dokumentiert' },
  it: { title: 'Uso di antibiotici', agent: 'Principio attivo', product: 'Prodotto', indication: 'Indicazione / motivazione', culture: 'Antibiogramma', route: 'Via', dose: 'Dose e frequenza', duration: 'Durata', quantity: 'Quantità consegnata', none: 'Nessun antibiotico segnato nel registro di consegna di oggi.', missingJust: 'indicazione o motivazione dell\'uso di antibiotici non registrata', missingDur: 'durata del trattamento non registrata', notDone: 'non eseguito', done: 'eseguito', rec: 'risultato in attesa o registrato altrove' },
};

export function renderAntibioticBlock(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, lang: Lang = 'en', opts: { culture_done?: boolean | null } = {}): string {
  const t = L[lang], a = AB[lang];
  const out: string[] = []; const miss: Missing[] = [];
  out.push(`## ${a.title}`);
  const rows = ctx.dispensings.filter((d) => d.is_antibiotic);
  if (!rows.length) { out.push(a.none); return out.join('\n'); }
  out.push(`**${headerLine(header)}**`); out.push('');
  for (const d of rows) {
    const m = record.medications[d.medication_index];
    if (!m) continue;
    out.push(`### ${m.drug ?? m.class_as_written ?? '?'}`);
    out.push(`- ${a.product}: ${d.product ?? flag(`${t.missing}: ${a.product.toLowerCase()}`)}`);
    out.push(`- ${a.indication}: ${d.antibiotic_justification ?? flag(a.missingJust)}`);
    if (!d.antibiotic_justification) miss.push({ field: `dispensings[${d.medication_index}].antibiotic_justification`, reason: a.missingJust });
    out.push(`- ${a.culture}: ${opts.culture_done == null ? a.rec : opts.culture_done ? a.done : a.notDone}`);
    out.push(`- ${a.dose}: ${m.dose != null ? `${m.dose} ${m.dose_unit ?? ''}`.trim() : flag(`${t.missing}: ${t.dose.toLowerCase()}`)}${m.frequency ? `, ${m.frequency}` : ''}`);
    out.push(`- ${a.route}: ${m.route ?? flag(`${t.missing}: ${t.route.toLowerCase()}`)}`);
    out.push(`- ${a.duration}: ${m.duration ?? flag(a.missingDur)}`);
    if (!m.duration) miss.push({ field: `medications[${d.medication_index}].duration`, reason: a.missingDur });
    out.push(`- ${a.quantity}: ${d.quantity ? `${d.quantity.value} ${d.quantity.unit}` : '—'}`);
    out.push('');
  }
  if (miss.length) { out.push(`### ${flag(t.missing)}`); for (const x of miss) out.push(`- ${x.field}: ${x.reason}`); }
  return out.join('\n');
}
