// Checks the seasonal alerts in src/data/seasonal.ts.
//
//   node scripts/check-seasonal.mjs
//
// For every alert:
//   1. id is a unique slug; months are integers 1–12 without repeats; countries, level and species are known
//   2. title and text exist in en, it and de (text: at most two or three sentences)
//   3. at least one reference, each with a title and an https URL; no VCA anywhere
//   4. every linked article exists in that language (src/content/animals/<lang>/<slug>.md, EN at the root)
//      and every tool page exists (src/pages/<tool>.astro and the it/ and de/ versions)
//   5. no dose patterns in any text (mg/kg, ml, tablets, "dose"/"dosi"/"Dosis", teaspoons …)
// Also: every month has at least one alert for every country. Exits 1 with a list of problems.
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { SEASONAL, COUNTRIES, showsIn } from '../src/data/seasonal.ts';

const LANGS = ['en', 'it', 'de'];
const LEVELS = ['danger', 'caution'];
const SPECIES = ['dog', 'cat', 'rabbit', 'guinea-pig', 'ferret', 'horse', 'bird', 'reptile'];
const ROOT = 'src/content/animals';
const fileOf = (lang, slug) => join(ROOT, lang === 'en' ? '' : lang, `${slug}.md`);
const DOSE = [
  /\b\d[\d.,]*\s*(?:mg|ml|mcg|µg|ug|IU|UI|IE)\b/i,
  /\b(?:mg|ml|g)\s*\/\s*kg\b/i, /\bper\s+kg\b/i, /\bpro\s+kg\b/i, /\bal\s+kg\b/i,
  /\bdos(?:e|es|age|aggio|aggi|i|is|ierung|ierungen)\b/i,
  /\b(?:teaspoons?|tablespoons?|cucchiai(?:ni|no|o)?|Teelöffel|Esslöffel|tablets?|compress[ae]|Tabletten?)\b/i,
];
const VCA = /\bVCA\b|vcahospitals|vca\.com/i;

const problems = [];
const ids = new Set();
let refs = 0, links = 0;
for (const a of SEASONAL) {
  const at = `"${a.id}"`;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(a.id)) problems.push(`${at}: id must be a lower-case slug`);
  if (ids.has(a.id)) problems.push(`${at}: duplicate id`); ids.add(a.id);
  if (!a.months?.length) problems.push(`${at}: no months`);
  for (const m of a.months ?? []) if (!Number.isInteger(m) || m < 1 || m > 12) problems.push(`${at}: month ${m} is not 1–12`);
  if (new Set(a.months).size !== a.months.length) problems.push(`${at}: repeated month`);
  if (!a.countries?.length) problems.push(`${at}: no countries`);
  for (const c of [...(a.countries ?? []), ...(a.except ?? [])]) if (!COUNTRIES.includes(c)) problems.push(`${at}: unknown country "${c}"`);
  if (a.except && !a.countries.includes('all')) problems.push(`${at}: "except" only makes sense with countries: ['all']`);
  if (!LEVELS.includes(a.level)) problems.push(`${at}: unknown level "${a.level}"`);
  if (!a.species?.length) problems.push(`${at}: no species`);
  for (const s of a.species ?? []) if (!SPECIES.includes(s)) problems.push(`${at}: unknown species "${s}"`);
  for (const l of LANGS) {
    if (!a.title?.[l]?.trim()) problems.push(`${at}: title missing in ${l}`);
    if (!a.text?.[l]?.trim()) problems.push(`${at}: text missing in ${l}`);
    const sentences = (a.text?.[l] ?? '').split(/(?<=[.!?])\s+(?=[A-ZÄÖÜÀÈÉÌÒÙ])/).filter(Boolean).length;
    if (sentences > 3) problems.push(`${at}.${l}: text has ${sentences} sentences (keep it to 1–2, at most 3)`);
    for (const s of [a.title?.[l] ?? '', a.text?.[l] ?? '']) {
      for (const re of DOSE) if (re.test(s)) problems.push(`${at}.${l}: looks like a dose (${re}): "${s.match(re)[0]}"`);
      if (VCA.test(s)) problems.push(`${at}.${l}: VCA is not a source we use`);
    }
  }
  if (!a.references?.length) problems.push(`${at}: no references`);
  for (const r of a.references ?? []) {
    refs++;
    if (!r.title?.trim()) problems.push(`${at}: reference without a title`);
    let u; try { u = new URL(r.url); } catch { problems.push(`${at}: reference URL is not a URL: "${r.url}"`); continue; }
    if (u.protocol !== 'https:') problems.push(`${at}: reference is not https: ${r.url}`);
    if (VCA.test(r.url) || VCA.test(r.title)) problems.push(`${at}: VCA is not a source we use (${r.url})`);
  }
  for (const [l, slug] of Object.entries(a.article ?? {})) {
    if (!LANGS.includes(l)) { problems.push(`${at}: article for unknown language "${l}"`); continue; }
    const f = fileOf(l, slug);
    if (!existsSync(f)) { problems.push(`${at}.${l}: article "${slug}" does not exist (${f})`); continue; }
    const lm = readFileSync(f, 'utf8').match(/^lang:\s*(\w+)/m);
    if ((lm ? lm[1] : 'en') !== l) problems.push(`${at}.${l}: ${f} is not a "${l}" article`);
    links++;
  }
  if (a.tool) for (const l of LANGS) {
    const f = join('src/pages', l === 'en' ? '' : l, `${a.tool.replace(/^\//, '')}.astro`);
    if (!existsSync(f)) problems.push(`${at}: tool page ${f} does not exist`);
  }
}
for (const c of COUNTRIES) for (let m = 1; m <= 12; m++) {
  if (!SEASONAL.some((a) => a.months.includes(m) && showsIn(a, c))) problems.push(`month ${m}: no alert for country "${c}"`);
}

if (problems.length) { console.error(`seasonal check: ${problems.length} problem(s)\n- ${problems.join('\n- ')}`); process.exit(1); }
console.log(`seasonal check: ${SEASONAL.length} alerts, ${refs} references, ${links} article links OK in ${LANGS.length} languages`);
