// Checks the "Can my pet eat …?" lexicon in src/data/foods.ts.
//
//   node scripts/check-foods.mjs
//
// For every entry:
//   1. key is a unique slug; name and an aliases list exist in en, it and de
//   2. every verdict is toxic/avoid/treat/ok, has a note in en, it and de, and refs that point at existing references
//   3. every reference has a title and an https URL, and is used by at least one verdict
//   4. no dose patterns in any text (mg/kg, ml/kg, g/kg, "per kg", IU/UI/IE units)
//   5. no search word (name or alias, any language) belongs to two different foods; anchors are unique per language
// Prints counts per species and verdict. Exits 1 with a list of problems.
import { FOODS, LANGS, SPECIES, VERDICTS, anchorOf, fold } from '../src/data/foods.ts';

const problems = [];
const DOSE = [
  /\b(?:mg|ml|g|mcg|µg|ug)\s*\/\s*kg\b/i,
  /\bper\s+kg\b/i, /\bpro\s+kg\b/i, /\bal\s+kg\b/i, /\bkg\s+(?:of\s+)?body\s*weight\b/i, /\bkg\s+(?:di\s+)?peso\b/i, /\bkg\s+Körpergewicht\b/i,
  /\b\d[\d.,]*\s*(?:IU|I\.U\.|UI|U\.I\.|IE|I\.E\.)\b/,
  /\bmg\s*\/\s*kg\b/i, /\bml\s*\/\s*kg\b/i,
];
const textsOf = (f) => [...Object.values(f.name), ...Object.values(f.verdicts).flatMap((v) => Object.values(v.note)), ...f.references.map((r) => r.title)];

const keys = new Set();
const words = new Map(); // folded word -> key
const anchors = Object.fromEntries(LANGS.map((l) => [l, new Map()]));
const counts = Object.fromEntries(SPECIES.map((s) => [s, Object.fromEntries(VERDICTS.map((v) => [v, 0]))]));

for (const f of FOODS) {
  const at = `"${f.key}"`;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(f.key)) problems.push(`${at}: key must be a lower-case slug`);
  if (keys.has(f.key)) problems.push(`${at}: duplicate key`);
  keys.add(f.key);
  for (const l of LANGS) {
    if (!f.name?.[l]?.trim()) problems.push(`${at}: no ${l} name`);
    if (!Array.isArray(f.aliases?.[l])) problems.push(`${at}: no ${l} aliases list`);
    const a = anchorOf(f, l);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(a)) problems.push(`${at}: ${l} anchor "${a}" is not a slug`);
    if (anchors[l].has(a)) problems.push(`${at}: ${l} anchor #${a} also used by "${anchors[l].get(a)}"`);
    anchors[l].set(a, f.key);
    for (const w of [f.name[l], ...(f.aliases?.[l] ?? [])]) {
      const k = fold(w);
      if (!k) { problems.push(`${at}: empty ${l} alias`); continue; }
      if (words.has(k) && words.get(k) !== f.key) problems.push(`${at}: search word "${w}" also belongs to "${words.get(k)}"`);
      words.set(k, f.key);
    }
  }
  const vs = Object.entries(f.verdicts ?? {});
  if (!vs.length) problems.push(`${at}: no verdicts`);
  if (!f.references?.length) problems.push(`${at}: no references`);
  const used = new Set();
  for (const [s, v] of vs) {
    const where = `${at}.${s}`;
    if (!SPECIES.includes(s)) problems.push(`${where}: unknown species`);
    if (!VERDICTS.includes(v.v)) problems.push(`${where}: unknown verdict "${v.v}"`);
    else if (counts[s]) counts[s][v.v]++;
    for (const l of LANGS) if (!v.note?.[l]?.trim()) problems.push(`${where}: no ${l} note`);
    if (!v.refs?.length) problems.push(`${where}: no refs`);
    for (const i of v.refs ?? []) {
      if (!Number.isInteger(i) || i < 0 || i >= f.references.length) problems.push(`${where}: ref ${i} does not exist (${f.references.length} references)`);
      else used.add(i);
    }
  }
  f.references.forEach((r, i) => {
    if (!r.title?.trim()) problems.push(`${at}: reference ${i} has no title`);
    let u; try { u = new URL(r.url); } catch { problems.push(`${at}: reference ${i} URL is not valid: ${r.url}`); return; }
    if (u.protocol !== 'https:') problems.push(`${at}: reference ${i} is not https: ${r.url}`);
    if (!used.has(i)) problems.push(`${at}: reference ${i} (${r.title}) is not used by any verdict`);
  });
  for (const s of textsOf(f)) for (const re of DOSE) if (re.test(s)) problems.push(`${at}: dose-like text ${re} in "${s.slice(0, 80)}…"`);
}

if (problems.length) { console.error(`foods check: ${problems.length} problem(s)\n- ${problems.join('\n- ')}`); process.exit(1); }
const urls = new Set(FOODS.flatMap((f) => f.references.map((r) => r.url)));
console.log(`foods check: ${FOODS.length} foods, ${urls.size} distinct sources, all OK`);
console.log(['species'.padEnd(11), ...VERDICTS.map((v) => v.padStart(6)), ' total'].join(''));
for (const s of SPECIES) {
  const c = counts[s];
  console.log([s.padEnd(11), ...VERDICTS.map((v) => String(c[v]).padStart(6)), String(Object.values(c).reduce((a, b) => a + b, 0)).padStart(6)].join(''));
}
