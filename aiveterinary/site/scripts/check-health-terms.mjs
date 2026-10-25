// Checks the Health A–Z in src/data/health-terms.ts.
//
//   node scripts/check-health-terms.mjs          (add --verbose to print every sentence's score)
//
// For every term and language:
//   1. key is a unique slug; kind is symptom/condition; species (if given) are known animals
//   2. name, synonyms list, text and at least one article slug; anchor is a unique slug that no page element uses
//   3. every slug is an article in that language (src/content/animals/<lang>/<slug>.md, EN at the root), not a draft
//      that was removed, and the term ends up with at least one animal (from the articles or `species`)
//   4. text is one or two sentences, and each sentence is close to the linked articles: at least 75% of its
//      content words (stems) occur in their title, description or body (a quote or a paraphrase, nothing added)
//   5. no dose patterns (mg, ml, mg/kg, "dose", tablets, teaspoons …) and no VCA anywhere
//   6. no search word (name or synonym) belongs to two terms in the same language
// Prints counts per language (aim: 60–100). Exits 1 with a list of problems.
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'js-yaml';
import { TERMS, LANGS, ANIMALS, anchorOf, fold } from '../src/data/health-terms.ts';

const VERBOSE = process.argv.includes('--verbose');
const ROOT = 'src/content/animals';
const fileOf = (lang, slug) => join(ROOT, lang === 'en' ? '' : lang, `${slug}.md`);
const DOSE = [
  /\b\d[\d.,]*\s*(?:mg|ml|mcg|µg|ug|IU|UI|IE|g)\b/i,
  /\b(?:mg|ml|g)\s*\/\s*kg\b/i, /\bper\s+kg\b/i, /\bpro\s+kg\b/i, /\bal\s+kg\b/i,
  /\bdos(?:e|es|age|aggio|aggi|i|is|ierung|ierungen)\b/i,
  /\b(?:teaspoons?|tablespoons?|cucchiai(?:ni|no|o)?|Teelöffel|Esslöffel|tablets?|compress[ae]|Tabletten?)\b/i,
];
const VCA = /\bVCA\b|vcahospitals|vca\.com/i;
// Ids the layout and the page itself use: an entry anchor must not collide with them.
const RESERVED = new Set(['main', 'hn-checks', 'hn-checks-h', 'hn-sheet', 'lang-suggest', 'lang-suggest-close', 'lang-suggest-link', 'lang-suggest-text', 'pwa-later', 'pwa-reload', 'pwa-toast']);
const STOP = new Set(('also more most with that this from your they them when what which while into over only even than then have does were been just like very much some such each other there their about after before could would should these those where whose until often usually '
  + 'della delle dello degli nella nelle negli sono come anche quando quale quali molto spesso dopo prima ancora oppure senza sempre solo tutto tutti tutte questo questa perche puoi deve devi '
  + 'oder eine einer einen einem eines sich sind wird werden kann können konnen nicht auch wenn dass oder aber noch nach beim beide schon sehr immer meist ihre ihren ihrem ihrer ihr sein seine dies diese dieser dann etwa').split(/\s+/));

const articles = new Map(); // `${lang}/${slug}` -> { data, text }
const article = (lang, slug) => {
  const k = `${lang}/${slug}`;
  if (articles.has(k)) return articles.get(k);
  const f = fileOf(lang, slug);
  let v = null;
  if (existsSync(f)) {
    const m = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/.exec(readFileSync(f, 'utf8'));
    const data = m ? yaml.load(m[1]) : {};
    v = { data, text: fold(`${data.title ?? ''} ${data.description ?? ''} ${m ? m[2] : ''}`) };
  }
  articles.set(k, v);
  return v;
};
const words = (s) => fold(s).replace(/[^a-z0-9äöü]+/g, ' ').split(' ').filter((w) => w.length >= 4 && !STOP.has(w) && !/^\d+$/.test(w));
const sentencesOf = (s) => s.split(/(?<=[.!?])\s+(?=[A-ZÄÖÜÀÈÉÌÒÙ"«„])/).filter(Boolean);

const problems = [];
const warnings = [];
const keys = new Set();
const counts = Object.fromEntries(LANGS.map((l) => [l, 0]));
const anchors = Object.fromEntries(LANGS.map((l) => [l, new Map()]));
const searchWord = Object.fromEntries(LANGS.map((l) => [l, new Map()]));
let links = 0, sentences = 0, low = 1;

for (const term of TERMS) {
  const at = `"${term.key}"`;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(term.key)) problems.push(`${at}: key must be a lower-case slug`);
  if (keys.has(term.key)) problems.push(`${at}: duplicate key`);
  keys.add(term.key);
  if (!['symptom', 'condition'].includes(term.kind)) problems.push(`${at}: kind must be symptom or condition`);
  for (const s of term.species ?? []) if (!ANIMALS.includes(s)) problems.push(`${at}: unknown species "${s}"`);
  if (!LANGS.some((l) => term[l])) problems.push(`${at}: no language`);
  for (const l of LANGS) {
    const x = term[l];
    if (!x) continue;
    const al = `${at}.${l}`;
    counts[l]++;
    if (!x.name?.trim()) problems.push(`${al}: no name`);
    if (!Array.isArray(x.synonyms)) problems.push(`${al}: no synonyms list`);
    if (!x.text?.trim()) problems.push(`${al}: no text`);
    if (!x.slugs?.length) problems.push(`${al}: no article`);
    const a = anchorOf(term, l);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(a)) problems.push(`${al}: anchor "${a}" is not a slug`);
    if (RESERVED.has(a) || a.startsWith('az-') || a.startsWith('ht-')) problems.push(`${al}: anchor #${a} collides with a page id`);
    if (anchors[l].has(a)) problems.push(`${al}: anchor #${a} also used by "${anchors[l].get(a)}"`);
    anchors[l].set(a, term.key);
    for (const w of [x.name, ...(x.synonyms ?? [])]) {
      const f = fold(w);
      if (searchWord[l].has(f) && searchWord[l].get(f) !== term.key) problems.push(`${al}: search word "${w}" also belongs to "${searchWord[l].get(f)}"`);
      searchWord[l].set(f, term.key);
    }
    // Articles
    const found = [];
    for (const slug of new Set(x.slugs ?? [])) {
      const art = article(l, slug);
      if (!art) { problems.push(`${al}: article "${slug}" does not exist (${fileOf(l, slug)})`); continue; }
      if ((art.data.lang ?? 'en') !== l) problems.push(`${al}: ${fileOf(l, slug)} is not a "${l}" article`);
      found.push(art);
      links++;
    }
    if ((x.slugs ?? []).length !== new Set(x.slugs ?? []).size) problems.push(`${al}: an article is listed twice`);
    const animals = new Set(term.species ?? []);
    for (const art of found) {
      if (ANIMALS.includes(art.data.species)) animals.add(art.data.species);
      for (const k of art.data.animals ?? []) if (ANIMALS.includes(k)) animals.add(k);
    }
    if (found.length && !animals.size) problems.push(`${al}: no animal (its articles are all "general": add species)`);
    // Text: 1–2 sentences, each close to the linked articles
    const ss = sentencesOf(x.text ?? '');
    if (ss.length > 2) problems.push(`${al}: text has ${ss.length} sentences (keep it to 1–2)`);
    const corpus = found.map((f) => f.text).join(' ');
    for (const s of ss) {
      sentences++;
      const ws = words(s);
      if (!ws.length) continue;
      const hit = ws.filter((w) => corpus.includes(w.slice(0, Math.min(w.length, 5))));
      const score = hit.length / ws.length;
      low = Math.min(low, score);
      const miss = ws.filter((w) => !hit.includes(w));
      if (VERBOSE) console.log(`${score.toFixed(2)} ${al}: ${s}${miss.length ? `  [missing: ${miss.join(', ')}]` : ''}`);
      if (found.length && score < 0.75) problems.push(`${al}: sentence not close to its article (${Math.round(score * 100)}% of words found; missing: ${miss.join(', ')}): "${s}"`);
    }
    for (const s of [x.name, x.text, ...(x.synonyms ?? [])]) {
      for (const re of DOSE) if (re.test(s ?? '')) problems.push(`${al}: looks like a dose (${re}): "${(s ?? '').match(re)[0]}"`);
      if (VCA.test(s ?? '')) problems.push(`${al}: VCA is not a source we use`);
    }
  }
}
for (const l of LANGS) if (counts[l] < 60 || counts[l] > 100) warnings.push(`${l}: ${counts[l]} terms (aim for 60–100)`);

for (const w of warnings) console.warn(`warning: ${w}`);
if (problems.length) { console.error(`health terms check: ${problems.length} problem(s)\n- ${problems.join('\n- ')}`); process.exit(1); }
console.log(`health terms check: ${TERMS.length} terms (${LANGS.map((l) => `${l} ${counts[l]}`).join(', ')}), ${links} article links, ${sentences} sentences (lowest match ${Math.round(low * 100)}%) OK`);
