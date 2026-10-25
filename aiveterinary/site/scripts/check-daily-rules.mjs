// Checks the daily-check warning rules in src/data/daily-rules.ts against the articles.
//
//   node scripts/check-daily-rules.mjs
//
// For every rule and every language:
//   1. the article slug exists in that language (src/content/animals/<lang>/<slug>.md, EN at the root)
//   2. the anchor excerpt occurs verbatim in that article (markdown emphasis and links removed)
//   3. the label is not empty and names no source the site does not use (VCA)
// Also: species, questions and answers in each condition are ones the daily check actually asks,
// ids are unique, and a few evaluation cases behave as expected. Exits 1 with a list of problems.
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { RULES, ANSWERS, SPECIES_QUESTIONS, LEVEL_ORDER, QUESTION_LABELS, ANSWER_LABELS, evaluate } from '../src/data/daily-rules.ts';

const ROOT = 'src/content/animals';
const LANGS = ['en', 'it', 'de'];
const fileOf = (lang, slug) => join(ROOT, lang === 'en' ? '' : lang, `${slug}.md`);
const norm = (s) => s.replace(/\*+/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/[  ]/g, ' ').replace(/[’]/g, "'").replace(/\s+/g, ' ').toLowerCase();

const problems = [];
const ids = new Set();
let checked = 0;
for (const r of RULES) {
  if (ids.has(r.id)) problems.push(`${r.id}: duplicate id`); ids.add(r.id);
  if (!LEVEL_ORDER.includes(r.level)) problems.push(`${r.id}: unknown level "${r.level}"`);
  if (!r.species.length) problems.push(`${r.id}: no species`);
  if (!r.when.length) problems.push(`${r.id}: empty condition`);
  if (r.days !== undefined && (!Number.isInteger(r.days) || r.days < 1 || r.days > 14)) problems.push(`${r.id}: days must be 1–14`);
  for (const sp of r.species) {
    const qs = SPECIES_QUESTIONS[sp];
    if (!qs) { problems.push(`${r.id}: species "${sp}" has no daily-check questions`); continue; }
    for (const w of r.when) for (const [q, vals] of Object.entries(w)) {
      if (!qs.includes(q)) problems.push(`${r.id}: "${q}" is not asked for ${sp}`);
      for (const v of vals) if (!ANSWERS[q]?.includes(v)) problems.push(`${r.id}: "${v}" is not an answer to "${q}"`);
    }
  }
  for (const lang of LANGS) {
    const a = r.article?.[lang]; const label = r.label?.[lang];
    const where = `${r.id}.${lang}`;
    if (!a?.slug) { problems.push(`${where}: no article slug`); continue; }
    if (!label?.trim()) problems.push(`${where}: empty label`);
    if (/\bVCA\b/i.test(label ?? '') || /\bVCA\b/i.test(a.anchor ?? '')) problems.push(`${where}: VCA is not a source we use`);
    const f = fileOf(lang, a.slug);
    if (!existsSync(f)) { problems.push(`${where}: article "${a.slug}" does not exist (${f})`); continue; }
    const raw = readFileSync(f, 'utf8');
    const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
    const front = m ? m[1] : '';
    const lm = front.match(/^lang:\s*(\w+)/m);
    if ((lm ? lm[1] : 'en') !== lang) problems.push(`${where}: ${f} is not a "${lang}" article`);
    if (!norm(m ? m[2] : raw).includes(norm(a.anchor ?? ''))) problems.push(`${where} (${a.slug}): anchor not found in article: "${a.anchor}"`);
    checked++;
  }
}
for (const lang of LANGS) {
  for (const q of Object.keys(ANSWERS)) if (!QUESTION_LABELS[lang]?.[q]) problems.push(`question label missing: ${lang}.${q}`);
  for (const v of new Set(Object.values(ANSWERS).flat())) if (!ANSWER_LABELS[lang]?.[v]) problems.push(`answer label missing: ${lang}.${v}`);
}

// Behaviour: the examples the feature was specified with.
const day = (date, x) => ({ date, ...x });
const expect = (name, got, id) => { if (!got.some((r) => r.id === id)) problems.push(`evaluate: ${name} should trigger ${id} (got ${got.map((r) => r.id).join(', ') || 'nothing'})`); };
const expectNot = (name, got, id) => { if (got.some((r) => r.id === id)) problems.push(`evaluate: ${name} should not trigger ${id}`); };
expect('rabbit no droppings', evaluate('Rabbit', [day('2026-10-25', { eat: 'normal', poo: 'none' })], '2026-10-25'), 'rabbit-poo');
expect('guinea pig not eating', evaluate('Guinea pig', [day('2026-10-25', { eat: 'none' })], '2026-10-25'), 'guinea-eat-none');
expect('cat straining', evaluate('Cat', [day('2026-10-25', { strain: 'yes' })], '2026-10-25'), 'cat-urine');
expect('dog not eating two days', evaluate('Dog', [day('2026-10-24', { eat: 'none' }), day('2026-10-25', { eat: 'none' })], '2026-10-25'), 'dog-eat-2d');
expectNot('dog not eating one day', evaluate('Dog', [day('2026-10-25', { eat: 'none' })], '2026-10-25'), 'dog-eat-2d');
expectNot('dog not eating with a gap', evaluate('Dog', [day('2026-10-23', { eat: 'none' }), day('2026-10-25', { eat: 'none' })], '2026-10-25'), 'dog-eat-2d');
expect('dog vomiting several times', evaluate('Dog', [day('2026-10-25', { vomit: 'several' })], '2026-10-25'), 'dog-vomit-several');
expect('ferret collapsed', evaluate('Ferret', [day('2026-10-25', { energy: 'weak' })], '2026-10-25'), 'ferret-weak');
if (evaluate('Rabbit', [day('2026-10-25', { eat: 'normal', drink: 'normal', poo: 'normal', pee: 'normal', energy: 'normal' })], '2026-10-25').length) problems.push('evaluate: an all-normal rabbit should trigger nothing');
if (evaluate('Fish', [day('2026-10-25', { eat: 'none' })], '2026-10-25').length) problems.push('evaluate: fish have no rules');

if (problems.length) { console.error(`daily rules check: ${problems.length} problem(s)\n- ${problems.join('\n- ')}`); process.exit(1); }
console.log(`daily rules check: ${RULES.length} rules, ${checked} article anchors OK across ${LANGS.length} languages`);
