// Finds well-known sections in an article's rendered HTML at build time, so the layout can point to
// (or quote) them without touching the signed Markdown. Nothing here writes medical text.
type Lang = 'en' | 'it' | 'de';
export type Section = { id: string; text: string; html: string };

const decode = (s: string) => s
  .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
  .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
export const textOf = (h: string) => decode(h.replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim();

// Headings in priority order: the explicit "go now" section first, then the question-style "when should I go".
const PATTERNS: Record<'gonow' | 'ask', Record<Lang, RegExp[]>> = {
  gonow: {
    en: [/^(?!.*\bnever\b)(first\b.*\bnow\b|go (to a (vet|clinic) )?(now|today)\b|when to call the vet today|(contact|call) (a|your) vet (now|today))/i, /^first\b(?!.*\bnever\b)/i, /^when should i (take|call)\b/i],
    it: [/^(?!.*\bmai\b)(prima di tutto|vai (subito|dal veterinario oggi)|(chiama|porta|corri)\b.*\b(subito|oggi)\b)/i, /^quando (devo )?(portare|andare|chiamare)\b/i],
    de: [/^(zuerst\b(?!.*\bnie\b)|sofort\b|(gehen|rufen|fahren|lassen) sie\b.*\b(sofort|heute|rasch|zeitnah|praxis|klinik)\b)/i, /^wann (sollte|muss) ich\b.*(tierarzt|tierärzt|praxis)/i],
  },
  ask: {
    en: [/^what will the vet (want to know|ask)/i],
    it: [/^cosa (vorrà sapere|mi chiederà) il veterinario/i],
    de: [/^was wird die (praxis|tierärztin oder der tierarzt)\b.*wissen wollen/i, /^was fragt die (praxis|tierärztin)/i],
  },
};

export function sections(html: string): Section[] {
  const out: Section[] = [];
  const re = /<h2\b[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)<\/h2>/g;
  const marks: { id: string; text: string; start: number; end: number }[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) marks.push({ id: m[1], text: textOf(m[2]), start: m.index, end: re.lastIndex });
  marks.forEach((k, i) => out.push({ id: k.id, text: k.text, html: html.slice(k.end, i + 1 < marks.length ? marks[i + 1].start : html.length) }));
  return out;
}

export function findSection(html: string, lang: Lang, kind: 'gonow' | 'ask'): Section | null {
  const all = sections(html);
  for (const p of PATTERNS[kind][lang]) {
    const hit = all.find((s) => p.test(s.text));
    if (hit) return hit;
  }
  return null;
}

/** The section's first bullet list (balanced, so nested lists stay whole), plus the sentence that introduces it. */
export function firstList(sec: Section): { intro: string | null; html: string } | null {
  const start = sec.html.search(/<ul\b/);
  if (start < 0) return null;
  const tag = /<\/?ul\b[^>]*>/g;
  tag.lastIndex = start;
  let depth = 0, end = -1, t: RegExpExecArray | null;
  while ((t = tag.exec(sec.html))) {
    depth += t[0][1] === '/' ? -1 : 1;
    if (depth === 0) { end = tag.lastIndex; break; }
  }
  if (end < 0) return null;
  // Strip ids so the quoted copy never duplicates an anchor in the article.
  const list = sec.html.slice(start, end).replace(/\s(id|name)="[^"]*"/g, '');
  const before = sec.html.slice(0, start).trim();
  const lastBlock = before.match(/<(p|h3|h4)\b[^>]*>([\s\S]*?)<\/\1>\s*$/);
  const intro = lastBlock ? lastBlock[2].replace(/\s(id|name)="[^"]*"/g, '').trim() : null;
  return { intro, html: list };
}
