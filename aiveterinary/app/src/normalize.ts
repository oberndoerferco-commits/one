/**
 * Normalise the vet's raw notes before extraction.
 * - unify line endings and whitespace (offsets in the record refer to THIS text)
 * - expand known clinic abbreviations in a side table (the text itself is NOT rewritten,
 *   so source spans stay honest; expansions are passed to the model as hints)
 * - detect language (very rough; the model confirms)
 */

export type Expansion = { abbr: string; meaning: string; index: number };

export const DEFAULT_ABBREVIATIONS: Record<string, string> = {
  // frequency / route (EN, Latin)
  sid: 'once daily', bid: 'twice daily', tid: 'three times daily', qid: 'four times daily',
  q12h: 'every 12 hours', q8h: 'every 8 hours', q24h: 'every 24 hours', eod: 'every other day',
  po: 'by mouth', sc: 'subcutaneous', sq: 'subcutaneous', im: 'intramuscular', iv: 'intravenous', prn: 'as needed',
  // exam
  t: 'temperature', hr: 'heart rate', rr: 'respiratory rate', mm: 'mucous membranes', crt: 'capillary refill time',
  bcs: 'body condition score', nad: 'no abnormality detected', wnl: 'within normal limits', bar: 'bright, alert, responsive',
  qar: 'quiet, alert, responsive', lns: 'lymph nodes', abd: 'abdomen', ausc: 'auscultation',
  // diagnostics
  us: 'ultrasound', cbc: 'complete blood count', chem: 'biochemistry', ua: 'urinalysis', rads: 'radiographs', xray: 'radiographs',
  // misc
  v: 'vomiting', d: 'diarrhoea', 'v/d': 'vomiting / diarrhoea', hx: 'history', dx: 'diagnosis', ddx: 'differential diagnoses',
  tx: 'treatment', rx: 'prescription', fu: 'follow-up', recheck: 'recheck appointment', o: 'owner', p: 'patient',
  // German
  'bd': 'Befund', 'th': 'Therapie', 'anam': 'Anamnese', 'kgw': 'Körpergewicht', 'ggr': 'geringgradig', 'mgr': 'mittelgradig', 'hgr': 'hochgradig',
  'obb': 'ohne besonderen Befund', 'wv': 'Wiedervorstellung',
  // Italian
  'eo': 'esame obiettivo', 'tr': 'temperatura rettale', 'fc': 'frequenza cardiaca', 'fr': 'frequenza respiratoria', 'anamn': 'anamnesi',
};

export function normalizeNotes(raw: string): string {
  return raw.replace(/\r\n?/g, '\n').replace(/[ \t]+\n/g, '\n').replace(/ /g, ' ').trim();
}

/** Find abbreviations as whole tokens; returns expansions with their offsets (never rewrites the text). */
export function findAbbreviations(text: string, table: Record<string, string> = DEFAULT_ABBREVIATIONS): Expansion[] {
  const out: Expansion[] = [];
  const re = /[A-Za-zÄÖÜäöüß\/]+(?=\b)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const key = m[0].toLowerCase();
    // "t" alone is only an abbreviation when followed by a number (T 39.1); same for v/d-style single letters
    if (key.length === 1 && !/^\s*[\d<>]/.test(text.slice(m.index + 1, m.index + 4))) continue;
    if (table[key]) out.push({ abbr: m[0], meaning: table[key], index: m.index });
  }
  return out;
}

export function detectLanguage(text: string): 'en' | 'de' | 'it' | 'unknown' {
  const t = ' ' + text.toLowerCase() + ' ';
  const score = (words: string[]) => words.reduce((n, w) => n + (t.split(' ' + w + ' ').length - 1), 0);
  const de = score(['und', 'seit', 'nicht', 'kein', 'keine', 'gestern', 'erbrechen', 'durchfall', 'heute', 'mit']);
  const it = score(['da', 'ieri', 'non', 'vomito', 'diarrea', 'con', 'oggi', 'nessun', 'nessuna', 'appetito']);
  const en = score(['since', 'no', 'and', 'yesterday', 'vomiting', 'diarrhea', 'diarrhoea', 'today', 'with', 'normal']);
  const best = Math.max(de, it, en);
  if (best === 0) return 'unknown';
  return best === de ? 'de' : best === it ? 'it' : 'en';
}
