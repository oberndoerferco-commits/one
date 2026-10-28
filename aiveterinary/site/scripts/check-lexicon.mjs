// Checks the animal lexicon (src/content/lexicon: EN at the root, it/ and de/ with the same file names).
//
//   node scripts/check-lexicon.mjs        (part of npm run build)
//
// Errors, exit 1:
//   - a fact citing a source number the entry does not list (ref is 1-based into references)
//   - a dose in a fact value (mg, mcg/µg, ml/kg, IU/UI/I.E.): fact sheets describe the animal, doses are the vet's
//   - an entry whose `lang` does not match its folder (it would show up in the wrong language)
//   - a key that would take over another page's URL: an article in that language, a topic, or "all"
//   - a `parent` (breed entries: parent: dog) that names no entry in the same language, the entry itself,
//     or an entry that is itself a breed (breeds hang directly off their animal)
// Warnings (the build goes on):
//   - an entry missing in a language that has its twin
//   - an article whose `animals` names a key with no entry in that language
//   - a dose in an entry's body text
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'js-yaml';
import { DOSE, FIELDS } from '../src/lib/lexicon.ts';
import { ANIMALS } from '../src/lib/animals-i18n.ts';

const LEXICON = 'src/content/lexicon';
const ARTICLES = 'src/content/animals';
const LANGS = ['en', 'it', 'de'];
const dirOf = (root, lang) => join(root, lang === 'en' ? '' : lang);
const mdIn = (dir) => (existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith('.md')).sort() : []);
const parse = (file) => {
  const m = readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  return m ? { data: yaml.load(m[1]) ?? {}, body: m[2] } : null;
};

const errors = [];
const warnings = [];
const keys = Object.fromEntries(LANGS.map((l) => [l, new Set()]));
const parents = Object.fromEntries(LANGS.map((l) => [l, new Map()])); // key -> parent, per language
let nEntries = 0;
let nFacts = 0;

for (const lang of LANGS) {
  const articles = new Set(mdIn(dirOf(ARTICLES, lang)).map((f) => f.slice(0, -3)));
  for (const f of mdIn(dirOf(LEXICON, lang))) {
    const key = f.slice(0, -3);
    const where = `${lang}/${key}`;
    keys[lang].add(key);
    nEntries++;
    const entry = parse(join(dirOf(LEXICON, lang), f));
    if (!entry) { errors.push(`${where}: no frontmatter`); continue; }
    const d = entry.data;
    if (d.parent !== undefined) parents[lang].set(key, d.parent);
    if ((d.lang ?? 'en') !== lang) errors.push(`${where}: lang is "${d.lang ?? 'en (default)'}" but the file is in the ${lang.toUpperCase()} folder`);
    if (key === 'all' || key in ANIMALS.en.categories) errors.push(`${where}: /animals/${key} is already a page of its own; rename the entry`);
    if (articles.has(key)) errors.push(`${where}: the ${lang.toUpperCase()} article ${key}.md already uses /animals/${key}; rename the entry`);
    const nRefs = Array.isArray(d.references) ? d.references.length : 0;
    (Array.isArray(d.facts) ? d.facts : []).forEach((x, i) => {
      nFacts++;
      const at = `${where} facts[${i}]${x?.field ? ` (${x.field})` : ''}`;
      if (!FIELDS.includes(x?.field)) errors.push(`${at}: unknown field "${x?.field}" (one of ${FIELDS.join(', ')})`);
      if (!Number.isInteger(x?.ref) || x.ref < 1 || x.ref > nRefs) errors.push(`${at}: cites source ${x?.ref}, but the entry lists ${nRefs} source${nRefs === 1 ? '' : 's'}`);
      if (typeof x?.value === 'string' && DOSE.test(x.value)) errors.push(`${at}: "${x.value}" contains a dose; doses belong to the vet, not the fact sheet`);
    });
    const line = entry.body.split('\n').find((l) => DOSE.test(l));
    if (line) warnings.push(`${where}: the text mentions a dose ("${line.trim().slice(0, 80)}"); check that it belongs in a lexicon entry`);
  }
}

let nBreeds = 0;
for (const lang of LANGS) {
  for (const [key, parent] of parents[lang]) {
    nBreeds++;
    const where = `${lang}/${key}`;
    if (typeof parent !== 'string' || !parent) errors.push(`${where}: parent must be the file name of another entry (e.g. parent: dog)`);
    else if (parent === key) errors.push(`${where}: parent is the entry itself`);
    else if (!keys[lang].has(parent)) errors.push(`${where}: parent "${parent}" has no ${lang.toUpperCase()} lexicon entry`);
    else if (parents[lang].has(parent)) errors.push(`${where}: parent "${parent}" is itself a breed of "${parents[lang].get(parent)}"; name the animal instead`);
  }
}

for (const key of [...new Set(LANGS.flatMap((l) => [...keys[l]]))].sort()) {
  const has = LANGS.filter((l) => keys[l].has(key));
  const missing = LANGS.filter((l) => !keys[l].has(key));
  if (missing.length) warnings.push(`${key}: no ${missing.map((l) => l.toUpperCase()).join('/')} entry yet (has ${has.map((l) => l.toUpperCase()).join('/')})`);
}

for (const lang of LANGS) {
  for (const f of mdIn(dirOf(ARTICLES, lang))) {
    const named = parse(join(dirOf(ARTICLES, lang), f))?.data.animals ?? [];
    for (const k of named) if (!keys[lang].has(k)) warnings.push(`${lang}/${f}: animals names "${k}", which has no ${lang.toUpperCase()} lexicon entry`);
  }
}

if (warnings.length) console.warn(`lexicon check: ${warnings.length} warning(s)\n- ${warnings.join('\n- ')}`);
if (errors.length) { console.error(`lexicon check: ${errors.length} error(s)\n- ${errors.join('\n- ')}`); process.exit(1); }
console.log(`lexicon check: ${nEntries} entr${nEntries === 1 ? 'y' : 'ies'} (${nBreeds} breed${nBreeds === 1 ? '' : 's'}), ${nFacts} facts OK across ${LANGS.length} languages`);
