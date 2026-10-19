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
  const bits = signalment(header, lang);
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
  en: { ownerTitle: 'What happened today, and what to do at home', forOwner: 'For the owner of', reason: 'Why you came', found: 'What we found', done: 'What we did', meds: 'Medication to give', home: 'At home', next: 'Next appointment', call: 'Call us if', declined: 'Discussed and declined', nothingNoted: 'Nothing further was noted.', referralTitle: 'Referral letter', dear: 'Dear colleague', referralIntro: 'I am referring the following patient to you.', referralReason: 'Reason for referral', historyHdr: 'History and findings', diagHdr: 'Diagnostics', treatHdr: 'Treatment so far', differentials: 'Differential diagnoses', thanks: 'Thank you for seeing this patient. Please send your findings back to us.', missingReason: 'Reason for referral not stated in the notes' },
  de: { ownerTitle: 'Was heute war, und was zu Hause zu tun ist', forOwner: 'Für die Halterin / den Halter von', reason: 'Warum Sie gekommen sind', found: 'Was wir festgestellt haben', done: 'Was wir gemacht haben', meds: 'Medikamente geben', home: 'Zu Hause', next: 'Nächster Termin', call: 'Rufen Sie an, wenn', declined: 'Besprochen und abgelehnt', nothingNoted: 'Weiteres wurde nicht notiert.', referralTitle: 'Überweisungsschreiben', dear: 'Liebe Kollegin, lieber Kollege', referralIntro: 'Ich überweise Ihnen folgenden Patienten.', referralReason: 'Überweisungsgrund', historyHdr: 'Vorbericht und Befunde', diagHdr: 'Diagnostik', treatHdr: 'Bisherige Behandlung', differentials: 'Differenzialdiagnosen', thanks: 'Vielen Dank für die Übernahme. Bitte senden Sie uns Ihre Befunde zurück.', missingReason: 'Überweisungsgrund in den Notizen nicht angegeben' },
  it: { ownerTitle: 'Cosa è successo oggi e cosa fare a casa', forOwner: 'Per il proprietario di', reason: 'Perché siete venuti', found: 'Cosa abbiamo trovato', done: 'Cosa abbiamo fatto', meds: 'Farmaci da somministrare', home: 'A casa', next: 'Prossimo appuntamento', call: 'Chiamateci se', declined: 'Discusso e rifiutato', nothingNoted: 'Non è stato annotato altro.', referralTitle: 'Lettera di riferimento', dear: 'Gentile collega', referralIntro: 'Le invio il seguente paziente.', referralReason: 'Motivo dell\'invio', historyHdr: 'Anamnesi e reperti', diagHdr: 'Esami', treatHdr: 'Trattamento finora', differentials: 'Diagnosi differenziali', thanks: 'Grazie per la presa in carico. La prego di inviarci i Suoi referti.', missingReason: 'Motivo dell\'invio non indicato nelle note' },
};

/** Signalment words in the document language. English keeps the raw schema values, so its output is unchanged. */
const SIG: Record<Lang, { species: Record<string, string>; sex: Record<string, string>; unit: Record<string, [string, string]>; num: (n: number) => string }> = {
  en: { species: {}, sex: {}, unit: { day: ['day', 'days'], week: ['week', 'weeks'], month: ['month', 'months'], year: ['year', 'years'] }, num: (n) => String(n) },
  de: {
    species: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'anderes Tier' },
    sex: { female: 'weiblich', male: 'männlich' },
    unit: { day: ['Tag', 'Tage'], week: ['Woche', 'Wochen'], month: ['Monat', 'Monate'], year: ['Jahr', 'Jahre'] },
    num: (n) => String(n).replace('.', ','),
  },
  it: {
    species: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' },
    sex: { female: 'femmina', male: 'maschio' },
    unit: { day: ['giorno', 'giorni'], week: ['settimana', 'settimane'], month: ['mese', 'mesi'], year: ['anno', 'anni'] },
    num: (n) => String(n).replace('.', ','),
  },
};
const signalment = (header: PatientHeader, lang: Lang = 'en') => {
  const g = SIG[lang] ?? SIG.en;
  const age = header.age ? `${g.num(header.age.value)} ${g.unit[header.age.unit]?.[header.age.value === 1 ? 0 : 1] ?? `${header.age.unit}${header.age.value === 1 ? '' : 's'}`}` : null;
  return [header.name, header.species && (g.species[header.species] ?? header.species), header.breed, header.sex && (g.sex[header.sex] ?? header.sex), age, header.weight_kg ? `${g.num(header.weight_kg)} kg` : null].filter(Boolean);
};
/** One-line signalment as every document prints it (exported for the template-only tests). */
export const headerLine = (header: PatientHeader, lang: Lang = 'en') => signalment(header, lang).join(' — ');

/** Owner summary: the same facts in the same words, grouped for the person who has to act at home. */
export function renderOwnerSummary(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; extraMissing?: Missing[] } = {}): string {
  const t = L[lang], d = D[lang];
  const out: string[] = [];
  out.push(`# ${d.ownerTitle}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${d.forOwner} ${header.name}** — ${headerLine(header, lang)}`);
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

/* Referral letter: who refers, the owner and a structured request, as the vet types them. */
/* Nothing in these blocks comes from the record or a default: an absent or blank field is   */
/* left out, and a block with no field is left out entirely (docs/16-referral-fields.md).   */

export type ReferralUrgency = 'emergency' | 'urgent' | 'routine';
/**
 * Vet-typed referral details outside the clinical record. `owner` is structurally compatible with
 * `VisitContext.owner` (only `name` is shared); `referrer` carries what `VisitContext.author` lacks
 * (practice, address/phone, email). The renderer does not take a whole `VisitContext` because a
 * referral needs no country pack.
 */
export type ReferralInput = {
  referrer?: { practice?: string | null; address?: string | null; email?: string | null; vet?: string | null; registration?: string | null };
  request?: { urgency?: ReferralUrgency | null; service?: string | null; question?: string | null };
  owner?: { name?: string | null; phone?: string | null; email?: string | null };
};

export const REFERRAL_LABELS = {
  en: { referrer: 'Referring practice', practice: 'Practice', address: 'Address and phone', email: 'Email', vet: 'Veterinarian', registration: 'Registration', owner: 'Owner', ownerName: 'Name', phone: 'Phone', request: 'Referral request', urgency: 'Urgency', service: 'Service requested', question: 'Clinical question', urgencies: { emergency: 'Emergency', urgent: 'Urgent', routine: 'Routine' } },
  de: { referrer: 'Überweisende Praxis', practice: 'Praxis', address: 'Adresse und Telefon', email: 'E-Mail', vet: 'Tierärztin / Tierarzt', registration: 'Kammer / Registrierung', owner: 'Tierhalter/in', ownerName: 'Name', phone: 'Telefon', request: 'Überweisungsauftrag', urgency: 'Dringlichkeit', service: 'Gewünschte Fachrichtung / Leistung', question: 'Fragestellung', urgencies: { emergency: 'Notfall', urgent: 'Dringend', routine: 'Routine' } },
  it: { referrer: 'Struttura inviante', practice: 'Struttura', address: 'Indirizzo e telefono', email: 'Email', vet: 'Medico veterinario', registration: 'Iscrizione all\'Ordine', owner: 'Proprietario', ownerName: 'Nome', phone: 'Telefono', request: 'Richiesta di riferimento', urgency: 'Urgenza', service: 'Servizio richiesto', question: 'Quesito clinico', urgencies: { emergency: 'Emergenza', urgent: 'Urgente', routine: 'Di routine' } },
};

const typed = (v: string | null | undefined): string | null => (typeof v === 'string' && v.trim() ? v.trim() : null);
/** "- Label: value" lines for the fields the vet typed; empty when none was. */
const fieldLines = (pairs: Array<[string, string | null | undefined]>): string[] => pairs.flatMap(([k, v]) => { const x = typed(v); return x ? [`- ${k}: ${x}`] : []; });

/** Referral letter: clinical, complete, with the referral reason flagged when the vet did not state one. */
export function renderReferralLetter(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; reason?: string | null; extraMissing?: Missing[]; referral?: ReferralInput } = {}): string {
  const t = L[lang], d = D[lang], rl = REFERRAL_LABELS[lang];
  const ref = opts.referral ?? {};
  // The clinical question: the structured field first, then the legacy free-text reason.
  const question = typed(ref.request?.question) ?? typed(opts.reason);
  const out: string[] = [];
  out.push(`# ${d.referralTitle}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  const r = ref.referrer ?? {};
  const referrer = fieldLines([[rl.practice, r.practice], [rl.address, r.address], [rl.email, r.email], [rl.vet, r.vet], [rl.registration, r.registration]]);
  if (referrer.length) { out.push(`## ${rl.referrer}`); out.push(...referrer); out.push(''); }
  out.push(`${d.dear},`);
  out.push('');
  // Signalment (breed, sex, age) is asked by nearly every referral form (docs/16-referral-fields.md):
  // the locked header first, then the record's own patient fields. Nothing is defaulted.
  const p0 = record.patient;
  const sig: PatientHeader = { ...header, breed: header.breed ?? p0.breed ?? undefined, sex: header.sex ?? p0.sex ?? undefined, age: header.age ?? p0.age ?? undefined };
  out.push(`${d.referralIntro} **${headerLine(sig, lang)}**`);
  out.push('');
  const o = ref.owner ?? {};
  const owner = fieldLines([[rl.ownerName, o.name], [rl.phone, o.phone], [rl.email, o.email]]);
  if (owner.length) { out.push(`## ${rl.owner}`); out.push(...owner); out.push(''); }
  const urgency = ref.request?.urgency && Object.hasOwn(rl.urgencies, ref.request.urgency) ? rl.urgencies[ref.request.urgency] : null;
  const request = fieldLines([[rl.urgency, urgency], [rl.service, ref.request?.service]]);
  if (request.length) {
    // Structured request: urgency and service as typed, then the question (or its flag).
    out.push(`## ${rl.request}`);
    out.push(...request);
    out.push(`- ${rl.question}: ${question ? cap(question) : flag(d.missingReason)}`);
  } else {
    out.push(`## ${d.referralReason}`);
    out.push(question ? cap(question) : flag(d.missingReason));
  }
  out.push('');
  out.push(`## ${d.historyHdr}`);
  out.push(record.presenting_complaint ? `- ${cap(record.presenting_complaint.text)}` : `- ${flag(t.missing)}`);
  for (const h of record.history) out.push(`- ${h.source_role === 'owner_reported' ? t.ownerReports + ': ' : ''}${h.finding}: ${h.value}`);
  const v = record.examination.vitals;
  const vitals = [v.temperature && `${t.temp} ${v.temperature.value} °${v.temperature.unit}`, v.heart_rate && `${t.hr} ${v.heart_rate.value}/min`, v.respiratory_rate && `${t.rr} ${v.respiratory_rate.value}/min`, v.weight && `${t.weight} ${v.weight.value} ${v.weight.unit}`].filter(Boolean);
  if (vitals.length) out.push(`- ${vitals.join('. ')}.`);
  for (const f of record.examination.findings) out.push(`- ${cap(f.system)}: ${f.text}`);
  if (record.assessment.text) out.push(`- ${t.assessment}: ${record.assessment.text}`);
  if (record.assessment.differentials.length) out.push(`- ${d.differentials}: ${record.assessment.differentials.map((x) => x.text).join('; ')}`);
  if (record.diagnostics.length) { out.push(''); out.push(`## ${d.diagHdr}`); for (const x of record.diagnostics) out.push(`- ${cap(x.test)} (${t[x.status] ?? x.status})${x.result ? `: ${x.result}` : x.status === 'performed' ? `: ${flag(`${t.missing}: result`)}` : ''}`); }
  if (record.treatments.length || record.medications.length) {
    out.push(''); out.push(`## ${d.treatHdr}`);
    for (const x of record.treatments) out.push(`- ${cap(x.text)} (${t[x.status] ?? x.status})`);
    if (record.medications.length) { out.push(''); out.push(renderMedicationTable(record.medications, lang)); }
  }
  out.push(''); out.push(d.thanks);
  const allMissing = [...record.missing, ...(opts.extraMissing ?? []), ...(question ? [] : [{ field: 'referral.reason', reason: d.missingReason }])];
  if (allMissing.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const m of allMissing) out.push(`- ${m.field}: ${m.reason}`); }
  const p = provenance(record, opts.extraMissing ?? []);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded + (question ? 0 : 1)))}_`);
  if (opts.approved) { out.push(''); out.push(`_${t.disclosure}_`); }
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Discharge letter (Entlassungsbrief / lettera di dimissione): what was */
/* done during the stay and what happens at home, from the approved     */
/* record only. A section with nothing in the record is left out; no    */
/* default advice, no default "call us if" list.                        */

export const DISCHARGE_LABELS = {
  en: { title: 'Discharge instructions', reason: 'Reason for the visit', done: 'Treatment during the stay', givenInClinic: 'Medication given in the clinic', diag: 'Diagnostics and results', assessment: 'Assessment', meds: 'Medication to give at home', home: 'Home care', next: 'Follow-up appointment', call: 'When to call the clinic', planned: 'Planned and recommended' },
  de: { title: 'Entlassungsbrief', reason: 'Vorstellungsgrund', done: 'Behandlung während des Aufenthalts', givenInClinic: 'In der Praxis verabreichte Medikamente', diag: 'Diagnostik und Ergebnisse', assessment: 'Beurteilung', meds: 'Medikamente für zu Hause', home: 'Pflege zu Hause', next: 'Kontrolltermin', call: 'Wann Sie die Praxis anrufen sollten', planned: 'Geplant und empfohlen' },
  it: { title: 'Lettera di dimissione', reason: 'Motivo della visita', done: 'Trattamenti durante la degenza', givenInClinic: 'Farmaci somministrati in clinica', diag: 'Esami e risultati', assessment: 'Valutazione', meds: 'Farmaci da somministrare a casa', home: 'Cure a casa', next: 'Controllo', call: 'Quando chiamare la clinica', planned: 'Pianificato e consigliato' },
};

/** Labels of the consultation report (status words, table headings, flags) that other documents reuse. */
export const REPORT_LABELS = L;

const fold = (s: string) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');
/**
 * A plan sentence is a "when to call the clinic" instruction when it asks the owner to make contact
 * (call, phone, contact us, come back / anrufen, melden, kommen / chiamare, contattare, tornare) and
 * names a condition (if, when, in case / wenn, falls, bei / se, in caso). "Call with results" or
 * "Anruf mit Ergebnissen" has no condition and is not one; a conditional recheck ("recheck if worse")
 * names no contact and stays a follow-up. Matching only sorts the vet's sentence; it is shown as written.
 */
export function isCallInstruction(text: string): boolean {
  const f = fold(text);
  const contact = /\b(call|phone|ring|contact (?:us|the clinic|the practice)|come back|return to (?:us|the clinic|the practice)|anruf|anrufen|rufen|telefonier\w*|melden|kontaktier\w*|kommen|vorbeikommen|chiama\w*|telefona\w*|contatta\w*|ricontatta\w*|tornare|tornate|riportare|riportate)\b/;
  const condition = /\b(if|when|in case|unless|wenn|falls|bei|sobald|se|qualora|in caso)\b/;
  return contact.test(f) && condition.test(f);
}

export function renderDischargeLetter(record: ClinicalRecord, header: PatientHeader, lang: Lang = 'en', opts: { approved?: boolean; extraMissing?: Missing[] } = {}): string {
  const t = L[lang], x = DISCHARGE_LABELS[lang];
  const out: string[] = [];
  const section = (title: string, lines: string[]) => { if (lines.length) { out.push(''); out.push(`## ${title}`); out.push(...lines); } };
  const st = (s: string) => (t as Record<string, string>)[s] ?? s;
  out.push(`# ${x.title}`);
  if (!opts.approved) out.push(`_${t.draft}_`);
  out.push('');
  out.push(`**${headerLine(header, lang)}**`);

  if (record.presenting_complaint) section(x.reason, [cap(record.presenting_complaint.text)]);

  const done = record.treatments.filter((y) => y.status === 'performed').map((y) => `- ${cap(y.text)}`);
  const givenHere = record.medications.filter((m) => m.status === 'performed');
  if (givenHere.length) { if (done.length) done.push(''); done.push(`### ${x.givenInClinic}`, renderMedicationTable(givenHere, lang)); }
  section(x.done, done);

  section(x.diag, record.diagnostics.filter((d) => d.status === 'performed').map((d) => `- ${cap(d.test)}: ${d.result ?? flag(`${t.missing}: result`)}`));

  const assess = record.assessment.text ? cap(record.assessment.text) : cap(record.assessment.differentials.map((d) => d.text).join(', '));
  if (assess) section(x.assessment, [assess]);

  const toGive = record.medications.filter((m) => m.status === 'dispensed' || m.status === 'prescribed');
  if (toGive.length) section(x.meds, [renderMedicationTable(toGive, lang)]);

  const fu = record.plan.follow_up;
  const fuIsCall = !!fu && isCallInstruction(fu.text);
  section(x.home, [
    ...record.plan.instructions.filter((i) => !isCallInstruction(i.text)).map((i) => `- ${cap(i.text)}`),
    ...record.treatments.filter((y) => y.status === 'recommended' && y.type === 'advice').map((y) => `- ${cap(y.text)}`),
  ]);
  if (fu && !fuIsCall) section(x.next, [cap(fu.text)]);
  section(x.call, [...(fu && fuIsCall ? [fu.text] : []), ...record.plan.instructions.filter((i) => isCallInstruction(i.text)).map((i) => i.text)].map((s) => `- ${cap(s)}`));

  const later = (s: string) => s === 'planned' || s === 'recommended';
  const planned = [
    ...record.diagnostics.filter((d) => later(d.status)).map((d) => `- ${cap(d.test)} (${st(d.status)})`),
    ...record.treatments.filter((y) => later(y.status) && y.type !== 'advice').map((y) => `- ${cap(y.text)} (${st(y.status)})`),
  ];
  const laterMeds = record.medications.filter((m) => later(m.status));
  if (laterMeds.length) { if (planned.length) planned.push(''); planned.push(renderMedicationTable(laterMeds, lang)); }
  section(x.planned, planned);

  section(t.declinedCare, [
    ...record.diagnostics.filter((d) => d.status === 'declined').map((d) => cap(d.test)),
    ...record.treatments.filter((y) => y.status === 'declined').map((y) => cap(y.text)),
    ...record.medications.filter((m) => m.status === 'declined').map((m) => m.drug ?? m.class_as_written ?? t.drug),
  ].map((s) => `- ${s} (${t.declined})`));

  const allMissing = [...record.missing, ...(opts.extraMissing ?? [])];
  if (allMissing.length) { out.push(''); out.push(`## ${flag(t.missing)}`); for (const m of allMissing) out.push(`- ${m.field}: ${m.reason}`); }
  const p = provenance(record, opts.extraMissing ?? []);
  out.push(''); out.push(`_${t.provenance.replace('{f}', String(p.facts)).replace('{n}', String(p.not_recorded))}_`);
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
  out.push(`**${p.animal}:** ${headerLine(header, lang)}${ctx.microchip ? ` · ${ctx.microchip}` : ` · ${flag(p.missingChip)}`}`);
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
  out.push(`**${headerLine(header, lang)}** · ${v.chip}: ${ctx.microchip ?? flag(v.missingChip)}`);
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
  out.push(`**${headerLine(header, lang)}**${ctx.microchip ? ` · ${ctx.microchip}` : ''}`);
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
  out.push(`**${headerLine(header, lang)}**${ctx.owner.name ? ` · ${ctx.owner.name}` : ''} · ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
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
  out.push(`**${headerLine(header, lang)}** · ${opts.date ?? new Date().toISOString().slice(0, 10)}`);
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
  out.push(''); out.push(`**${headerLine(header, lang)}**`); out.push(''); out.push(x.intro); out.push('');
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
  out.push(`**${headerLine(header, lang)}**`); out.push('');
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

/* ------------------------------------------------------------------ */
/* Text-first dental chart: typed findings with modified Triadan tooth  */
/* numbers become a quadrant chart. Only numbers and findings that are   */
/* in the text appear; nothing is assumed healthy.                       */

const DENT = {
  en: { title: 'Dental chart', upperRight: 'Upper right (1xx)', upperLeft: 'Upper left (2xx)', lowerLeft: 'Lower left (3xx)', lowerRight: 'Lower right (4xx)', none: 'No tooth-numbered findings in the notes.', legend: 'Only teeth named in the notes are marked; unmarked teeth are not recorded, not healthy.', tooth: 'Tooth', finding: 'Finding' },
  de: { title: 'Zahnschema', upperRight: 'Oben rechts (1xx)', upperLeft: 'Oben links (2xx)', lowerLeft: 'Unten links (3xx)', lowerRight: 'Unten rechts (4xx)', none: 'Keine zahnnummerierten Befunde in den Notizen.', legend: 'Nur in den Notizen genannte Zähne sind markiert; nicht markierte Zähne sind nicht erfasst, nicht gesund.', tooth: 'Zahn', finding: 'Befund' },
  it: { title: 'Schema dentale', upperRight: 'Superiore destro (1xx)', upperLeft: 'Superiore sinistro (2xx)', lowerLeft: 'Inferiore sinistro (3xx)', lowerRight: 'Inferiore destro (4xx)', none: 'Nessun reperto con numero di dente nelle note.', legend: 'Solo i denti citati nelle note sono segnati; i denti non segnati non sono registrati, non sani.', tooth: 'Dente', finding: 'Reperto' },
};

/** Finds "104 fractured", "309, 310 missing", "208: calculus 2/4" style entries. Returns tooth → finding, in text order. */
export function parseDentalFindings(text: string): { tooth: number; finding: string }[] {
  const out: { tooth: number; finding: string }[] = [];
  // a run of tooth numbers (modified Triadan: 101–111, 201–211, 301–311, 401–411; deciduous 5xx–8xx) followed by the finding until end of line or next tooth group
  const re = /\b((?:[1-8](?:0[1-9]|1[01]))(?:\s*[,/+&]\s*(?:[1-8](?:0[1-9]|1[01])))*)\s*[:\-–]?\s*([^\n;.]*?)(?=(?:\s*[;.]|\n|$|\s+(?:[1-8](?:0[1-9]|1[01]))\b))/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const teeth = m[1].split(/\s*[,/+&]\s*/).map(Number);
    const finding = m[2].trim();
    if (!finding) continue;
    for (const tooth of teeth) out.push({ tooth, finding });
  }
  return out;
}

export function renderDentalChart(text: string, lang: Lang = 'en'): string {
  const d = DENT[lang];
  const items = parseDentalFindings(text);
  const out: string[] = [`## ${d.title}`];
  if (!items.length) { out.push(d.none); return out.join('\n'); }
  const q = (n: number) => Math.floor(n / 100);
  const quadrants: [number, string][] = [[1, d.upperRight], [2, d.upperLeft], [3, d.lowerLeft], [4, d.lowerRight]];
  const marks = new Map<number, string[]>();
  for (const it of items) marks.set(it.tooth, [...(marks.get(it.tooth) ?? []), it.finding]);
  // chart row per quadrant: 11 positions, marked teeth shown with a dot, others as a faint number
  for (const [qn, label] of quadrants) {
    const perm = Array.from({ length: 11 }, (_, i) => qn * 100 + i + 1);
    const decid = (qn + 4) * 100;
    const cells = perm.map((n) => (marks.has(n) ? `**${n}●**` : marks.has(n - 100 + decid) ? `**${n - 100 + decid}●**` : `${n}`));
    out.push(`- ${label}: ${cells.join(' ')}`);
  }
  out.push('');
  out.push(`| ${d.tooth} | ${d.finding} |`); out.push('|---|---|');
  for (const [tooth, fs] of [...marks.entries()].sort((a, b) => a[0] - b[0])) out.push(`| ${tooth} | ${fs.join('; ')} |`);
  out.push('');
  out.push(`_${d.legend}_`);
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Bilingual owner letter and the cross-document identity check.       */
/* Headings and the medication table are code, so they exist in both    */
/* languages; the vet's own sentences stay as written. The check makes  */
/* sure every medication detail is identical in every document.         */

export function renderOwnerSummaryBilingual(record: ClinicalRecord, header: PatientHeader, first: Lang, second: Lang, opts: { approved?: boolean } = {}): string {
  const a = renderOwnerSummary(record, header, first, opts);
  const b = renderOwnerSummary(record, header, second, opts);
  return `${a}\n\n---\n\n${b}`;
}

/** Every medication's drug, dose, route, frequency and duration must appear in every document, character for character. */
export function crossDocumentMedicationCheck(record: ClinicalRecord, documents: Record<string, string>): { doc: string; medication: number; field: string; value: string }[] {
  const problems: { doc: string; medication: number; field: string; value: string }[] = [];
  record.medications.forEach((m, i) => {
    if (m.status === 'declined') return;
    const fields: [string, string | null][] = [['drug', m.drug], ['dose', m.dose != null ? `${m.dose} ${m.dose_unit ?? ''}`.trim() : null], ['route', m.route], ['frequency', m.frequency], ['duration', m.duration]];
    const name0 = m.drug ?? m.class_as_written;
    for (const [name, value] of Object.entries(documents)) {
      // Where the document has a medication table, the drug's own row must carry every value;
      // a matching value elsewhere in the text (a checklist, the follow-up) does not count.
      const rows = name0 ? value.split('\n').filter((l) => l.startsWith('|') && l.includes(name0)) : [];
      const haystacks = rows.length ? rows : [value];
      for (const [field, v] of fields) if (v && !haystacks.some((h) => h.includes(v))) problems.push({ doc: name, medication: i, field, value: v });
    }
  });
  return problems;
}
