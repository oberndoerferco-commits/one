/**
 * Suggestions from the OCR text of a paper pet passport, libretto or Impfpass.
 *
 * Runs on the owner's device. Everything returned is a suggestion the owner
 * must tick before it is saved; nothing here writes to the booklet. The rules
 * are deliberately narrow: a value is suggested only when the text contains it
 * literally (a 15-digit chip number, a date, a batch label), never inferred.
 */

export type ScanVaccination = { vaccine: string; date: string | null; validUntil: string | null; batch: string | null; line: string };
export type ScanResult = { microchip: string[]; vaccinations: ScanVaccination[]; dates: string[] };

/** Vaccine words as printed in EN/IT/DE passports and common abbreviations. Matching is case-insensitive. */
const VACCINE_WORDS: [RegExp, string][] = [
  [/\b(rabies|tollwut|rabbia|antirabbica|anti-?rabica)\b/i, 'Rabies'],
  [/\blepto\w*/i, 'Leptospirosis'],
  [/\b(DHPP?i?L?\d?|DAPP?i?|SHPP?i?|CHPP?i?)\b/i, 'Distemper/hepatitis/parvovirus combination'],
  [/\b(staupe|cimurro|distemper)\b/i, 'Distemper'],
  [/\b(parvo\w*)\b/i, 'Parvovirus'],
  [/\b(zwingerhusten|tosse dei canili|kennel cough|bordetella)\b/i, 'Kennel cough'],
  [/\b(RCP|RCPCh|katzenschnupfen|katzenseuche|panleu\w*|calici\w*|herpes\w*|rinotracheite)\b/i, 'Cat flu / panleukopenia combination'],
  [/\b(FeLV|leukose|leucemia felina)\b/i, 'FeLV'],
  [/\b(RHD\w*|myxomatose|mixomatosi|myxomatosis)\b/i, 'Rabbit RHD / myxomatosis'],
];

const pad = (n: number) => String(n).padStart(2, '0');

/** dd.mm.yyyy, dd/mm/yyyy, dd-mm-yyyy (also two-digit years ≥ 2000) → ISO yyyy-mm-dd; null when not a real date. */
export function toIsoDate(d: string, m: string, y: string): string | null {
  let year = Number(y); const month = Number(m), day = Number(d);
  if (y.length === 2) year = 2000 + year;
  if (year < 1990 || year > 2100 || month < 1 || month > 12 || day < 1 || day > 31) return null;
  const dt = new Date(Date.UTC(year, month - 1, day));
  if (dt.getUTCMonth() !== month - 1) return null;
  return `${year}-${pad(month)}-${pad(day)}`;
}

const DATE_RE = /\b(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4}|\d{2})\b/g;

function datesIn(line: string): string[] {
  const out: string[] = [];
  for (const m of line.matchAll(DATE_RE)) { const iso = toIsoDate(m[1], m[2], m[3]); if (iso) out.push(iso); }
  return out;
}

/** OCR often reads O for 0 and l/I for 1 inside long digit runs; only fix those inside a candidate of digits and spaces. */
function normaliseDigits(s: string): string {
  return s.replace(/[OoQ]/g, '0').replace(/[lI|]/g, '1').replace(/[Ss](?=\d)/g, '5');
}

/** 15-digit ISO 11784 chip numbers, allowing the spaces passports print in groups of 3. */
export function findMicrochips(text: string): string[] {
  const found = new Set<string>();
  const re = /(?:\d[\dOoQlI| ]{13,22}\d)/g;
  for (const m of text.matchAll(re)) {
    const digits = normaliseDigits(m[0]).replace(/\s+/g, '');
    if (/^\d{15}$/.test(digits)) found.add(digits);
  }
  return [...found];
}

const BATCH_RE = /\b(?:batch|lot|lotto|ch\.?-?\s?b\.?|charge|chargen?-?nr\.?|serial)\s*[:#.]?\s*([A-Z0-9][A-Z0-9\-\/]{2,})/i;

export function parseScan(text: string): ScanResult {
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const vaccinations: ScanVaccination[] = [];
  const at = new Map<ScanVaccination, number>(); // line index of each suggestion
  lines.forEach((line, i) => {
    const hit = VACCINE_WORDS.find(([re]) => re.test(line));
    if (!hit) return;
    // A sticker usually puts the product on one line and batch/dates on the next one or two.
    const window = [line, lines[i + 1] ?? '', lines[i + 2] ?? ''].join(' ');
    const ds = datesIn(window).sort();
    const batch = window.match(BATCH_RE)?.[1] ?? null;
    const v: ScanVaccination = { vaccine: hit[1], date: ds[0] ?? null, validUntil: ds.length > 1 ? ds[ds.length - 1] : null, batch, line };
    vaccinations.push(v); at.set(v, i);
  });
  // A heading such as "Impfung gegen Tollwut" names the vaccine but carries no data: drop it when a real entry exists.
  // A heading with no data on its own line whose window reaches the next entry for the same vaccine would repeat that
  // entry's dates without its batch: drop it too.
  const ownData = (v: ScanVaccination) => datesIn(v.line).length > 0 || BATCH_RE.test(v.line);
  const useful = vaccinations.filter((v) => (v.date || v.batch || !vaccinations.some((o) => o !== v && o.vaccine === v.vaccine && (o.date || o.batch)))
    && (ownData(v) || !vaccinations.some((o) => o !== v && o.vaccine === v.vaccine && (o.date || o.batch) && at.get(o)! > at.get(v)! && at.get(o)! <= at.get(v)! + 2)));
  const dates = [...new Set(lines.flatMap(datesIn))].sort();
  return { microchip: findMicrochips(text), vaccinations: useful, dates };
}
