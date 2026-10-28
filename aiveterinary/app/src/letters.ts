import { z } from 'zod';
import type { Lang } from './render.js';

/**
 * Short documents that do not come from a consultation record: the note of a
 * phone call, the end-of-life record, and the condolence letter.
 *
 * Every field is typed by the vet or nurse. The renderers only lay out what was
 * entered and flag what is missing; they never add clinical content, and the
 * condolence letter uses only the names and the one personal line the vet wrote.
 */

const t = z.string().trim().min(1);
const opt = t.nullable().default(null);

export const PhoneNote = z.object({
  at: t, // ISO date-time of the call
  caller: opt, // name as given
  relation: z.enum(['owner', 'other_vet', 'lab', 'other']).default('owner'),
  patient: opt,
  reason: opt, // what the caller reported, in the vet's words
  advice: opt, // what the clinic told the caller
  outcome: z.enum(['no_action', 'book_visit', 'go_now', 'call_back', 'refer']).nullable().default(null),
  call_back_at: opt,
  taken_by: opt,
});
export type PhoneNote = z.infer<typeof PhoneNote>;

export const EndOfLife = z.object({
  date: t,
  patient: opt,
  owner: opt,
  consent: z.enum(['signed', 'verbal_witnessed', 'missing']).default('missing'),
  witness: opt, // required when consent is verbal
  owner_present: z.boolean().nullable().default(null),
  method_as_written: opt, // exactly as the vet wrote it; no dose calculation here
  aftercare: z.enum(['individual_cremation', 'communal_cremation', 'home_burial', 'owner_arranges', 'other']).nullable().default(null),
  aftercare_note: opt,
  vet: opt,
});
export type EndOfLife = z.infer<typeof EndOfLife>;

export const Condolence = z.object({
  owner: opt,
  patient: opt,
  personal_line: opt, // one sentence written by the vet; never generated
  vet: opt,
  clinic: opt,
});
export type Condolence = z.infer<typeof Condolence>;

const S = {
  en: {
    phoneTitle: 'Telephone note', when: 'Date and time', caller: 'Caller', patient: 'Patient', reason: 'Reported', advice: 'Advice given', outcome: 'Outcome', callBack: 'Call back', takenBy: 'Taken by',
    rel: { owner: 'owner', other_vet: 'another veterinarian', lab: 'laboratory', other: 'other' },
    out: { no_action: 'no action needed', book_visit: 'appointment to be booked', go_now: 'told to come in now', call_back: 'clinic to call back', refer: 'referred' },
    eolTitle: 'End-of-life record', date: 'Date', owner: 'Owner', consent: 'Consent', witness: 'Witness', present: 'Owner present', method: 'Procedure as recorded', aftercare: 'Aftercare', vet: 'Veterinarian',
    cons: { signed: 'signed by the owner', verbal_witnessed: 'verbal, witnessed', missing: 'not recorded' },
    care: { individual_cremation: 'individual cremation', communal_cremation: 'communal cremation', home_burial: 'burial at home (check local rules)', owner_arranges: 'arranged by the owner', other: 'other' },
    yes: 'yes', no: 'no', missing: 'Missing',
    mWho: 'who called', mAdvice: 'the advice given', mOutcome: 'the outcome', mCallBack: 'when to call back', mTakenBy: 'who took the call', mConsent: 'consent', mWitness: 'a witness for verbal consent', mMethod: 'the procedure as performed', mAftercare: 'aftercare', mVet: 'the responsible veterinarian',
    dear: (o: string | null) => (o ? `Dear ${o},` : 'Dear family,'), cTitle: 'With sympathy',
    cBody: (p: string | null) => `We were very sorry to say goodbye to ${p ?? 'your companion'} with you. Thank you for the trust you placed in us, and for the care you gave every day.`,
    cClose: 'With warm regards,', cHelp: 'If you would like to talk, or have any questions, please call us at any time.',
  },
  de: {
    phoneTitle: 'Telefonnotiz', when: 'Datum und Uhrzeit', caller: 'Anrufer', patient: 'Patient', reason: 'Geschildert', advice: 'Gegebener Rat', outcome: 'Ergebnis', callBack: 'Rückruf', takenBy: 'Aufgenommen von',
    rel: { owner: 'Besitzer', other_vet: 'andere Praxis', lab: 'Labor', other: 'sonstige' },
    out: { no_action: 'keine Maßnahme nötig', book_visit: 'Termin wird vereinbart', go_now: 'sofort einbestellt', call_back: 'Praxis ruft zurück', refer: 'überwiesen' },
    eolTitle: 'Dokumentation Euthanasie', date: 'Datum', owner: 'Besitzer', consent: 'Einwilligung', witness: 'Zeuge', present: 'Besitzer anwesend', method: 'Durchführung wie dokumentiert', aftercare: 'Verbleib', vet: 'Tierärztin/Tierarzt',
    cons: { signed: 'vom Besitzer unterschrieben', verbal_witnessed: 'mündlich, bezeugt', missing: 'nicht dokumentiert' },
    care: { individual_cremation: 'Einzelkremierung', communal_cremation: 'Sammelkremierung', home_burial: 'Bestattung auf eigenem Grundstück (örtliche Regeln prüfen)', owner_arranges: 'durch den Besitzer', other: 'sonstiges' },
    yes: 'ja', no: 'nein', missing: 'Fehlt',
    mWho: 'wer angerufen hat', mAdvice: 'der gegebene Rat', mOutcome: 'das Ergebnis', mCallBack: 'Rückrufzeitpunkt', mTakenBy: 'wer den Anruf angenommen hat', mConsent: 'Einwilligung', mWitness: 'Zeuge für mündliche Einwilligung', mMethod: 'Durchführung', mAftercare: 'Verbleib des Tieres', mVet: 'verantwortliche Tierärztin/verantwortlicher Tierarzt',
    dear: (o: string | null) => (o ? `Liebe Familie ${o},` : 'Liebe Familie,'), cTitle: 'In Anteilnahme',
    cBody: (p: string | null) => `Es hat uns sehr berührt, gemeinsam mit Ihnen Abschied von ${p ?? 'Ihrem Tier'} zu nehmen. Danke für Ihr Vertrauen und für die Fürsorge, die Sie jeden Tag geschenkt haben.`,
    cClose: 'Mit herzlichen Grüßen', cHelp: 'Wenn Sie sprechen möchten oder Fragen haben, rufen Sie uns jederzeit an.',
  },
  it: {
    phoneTitle: 'Nota telefonica', when: 'Data e ora', caller: 'Chiamante', patient: 'Paziente', reason: 'Riferito', advice: 'Indicazioni date', outcome: 'Esito', callBack: 'Richiamare', takenBy: 'Ricevuta da',
    rel: { owner: 'proprietario', other_vet: 'altro veterinario', lab: 'laboratorio', other: 'altro' },
    out: { no_action: 'nessuna azione necessaria', book_visit: 'da fissare una visita', go_now: 'invitato a venire subito', call_back: 'la clinica richiama', refer: 'inviato a struttura di riferimento' },
    eolTitle: 'Registrazione eutanasia', date: 'Data', owner: 'Proprietario', consent: 'Consenso', witness: 'Testimone', present: 'Proprietario presente', method: 'Procedura come registrata', aftercare: 'Destinazione della salma', vet: 'Medico veterinario',
    cons: { signed: 'firmato dal proprietario', verbal_witnessed: 'verbale, con testimone', missing: 'non registrato' },
    care: { individual_cremation: 'cremazione individuale', communal_cremation: 'cremazione collettiva', home_burial: 'sepoltura in terreno privato (verificare le norme locali)', owner_arranges: 'a cura del proprietario', other: 'altro' },
    yes: 'sì', no: 'no', missing: 'Mancante',
    mWho: 'chi ha chiamato', mAdvice: 'le indicazioni date', mOutcome: "l'esito", mCallBack: 'quando richiamare', mTakenBy: 'chi ha ricevuto la chiamata', mConsent: 'il consenso', mWitness: 'un testimone per il consenso verbale', mMethod: 'la procedura eseguita', mAftercare: 'la destinazione della salma', mVet: 'il medico veterinario responsabile',
    dear: (o: string | null) => (o ? `Gentile ${o},` : 'Gentile famiglia,'), cTitle: 'Con affetto',
    cBody: (p: string | null) => `Ci è dispiaciuto molto salutare ${p ?? 'il vostro compagno'} insieme a voi. Grazie per la fiducia e per le cure che gli avete dato ogni giorno.`,
    cClose: 'Un caro saluto,', cHelp: 'Se desiderate parlarne o avete domande, chiamateci quando volete.',
  },
} as const;

const flag = (x: string) => `▲ ${x}`;
const line = (k: string, v: string | null | undefined, missing: string) => `**${k}:** ${v ?? flag(missing)}`;
const missingBlock = (m: string[], label: string) => (m.length ? ['', `## ${flag(label)}`, ...m.map((x) => `- ${x}`)] : []);

export function renderPhoneNote(input: z.input<typeof PhoneNote>, lang: Lang = 'en'): { text: string; missing: string[] } {
  const n = PhoneNote.parse(input); const s = S[lang];
  const miss: string[] = [];
  if (!n.caller) miss.push(s.mWho);
  if (!n.advice) miss.push(s.mAdvice);
  if (!n.outcome) miss.push(s.mOutcome);
  if (n.outcome === 'call_back' && !n.call_back_at) miss.push(s.mCallBack);
  if (!n.taken_by) miss.push(s.mTakenBy);
  const out = [
    `# ${s.phoneTitle}`, '',
    `**${s.when}:** ${n.at}`,
    line(s.caller, n.caller && `${n.caller} (${s.rel[n.relation]})`, s.mWho),
    `**${s.patient}:** ${n.patient ?? '—'}`,
    `**${s.reason}:** ${n.reason ?? '—'}`,
    line(s.advice, n.advice, s.mAdvice),
    line(s.outcome, n.outcome && s.out[n.outcome], s.mOutcome),
    ...(n.outcome === 'call_back' ? [line(s.callBack, n.call_back_at, s.mCallBack)] : []),
    line(s.takenBy, n.taken_by, s.mTakenBy),
    ...missingBlock(miss, s.missing),
  ];
  return { text: out.join('\n'), missing: miss };
}

export function renderEndOfLife(input: z.input<typeof EndOfLife>, lang: Lang = 'en'): { text: string; missing: string[] } {
  const e = EndOfLife.parse(input); const s = S[lang];
  const miss: string[] = [];
  if (e.consent === 'missing') miss.push(s.mConsent);
  if (e.consent === 'verbal_witnessed' && !e.witness) miss.push(s.mWitness);
  if (!e.method_as_written) miss.push(s.mMethod);
  if (!e.aftercare) miss.push(s.mAftercare);
  if (!e.vet) miss.push(s.mVet);
  const out = [
    `# ${s.eolTitle}`, '',
    `**${s.date}:** ${e.date}`,
    `**${s.patient}:** ${e.patient ?? '—'}`,
    `**${s.owner}:** ${e.owner ?? '—'}`,
    `**${s.consent}:** ${e.consent === 'missing' ? flag(s.cons.missing) : s.cons[e.consent]}`,
    ...(e.consent === 'verbal_witnessed' ? [line(s.witness, e.witness, s.mWitness)] : []),
    `**${s.present}:** ${e.owner_present === null ? '—' : e.owner_present ? s.yes : s.no}`,
    line(s.method, e.method_as_written, s.mMethod),
    line(s.aftercare, e.aftercare && [s.care[e.aftercare], e.aftercare_note].filter(Boolean).join(' — '), s.mAftercare),
    line(s.vet, e.vet, s.mVet),
    ...missingBlock(miss, s.missing),
  ];
  return { text: out.join('\n'), missing: miss };
}

/** A short, warm letter. Only names and the vet's own sentence vary; no clinical detail is included. */
export function renderCondolence(input: z.input<typeof Condolence>, lang: Lang = 'en'): string {
  const c = Condolence.parse(input); const s = S[lang];
  return [
    `# ${s.cTitle}`, '',
    s.dear(c.owner), '',
    s.cBody(c.patient),
    ...(c.personal_line ? ['', c.personal_line] : []),
    '', s.cHelp, '',
    s.cClose,
    [c.vet, c.clinic].filter(Boolean).join(', ') || '—',
  ].join('\n');
}
