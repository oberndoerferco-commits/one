// Checks the curated Animal guide data in src/data/species.ts against the articles.
//
//   node scripts/check-species.mjs
//
// For every go-now sign, key fact and care item, in every language it is given for:
//   1. the article slug exists in that language (src/content/animals/<lang>/<slug>.md, EN at the root)
//   2. the anchor excerpt occurs verbatim in that article (markdown emphasis and links removed)
//   3. every named source occurs in that article (in the text, or in its references for via: 'ref')
// Also checks every "most read" and guinea-pig slug exists. Exits 1 with a list of problems.
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { PROFILES, GUINEA_PIG_ARTICLE, referencedSlugs } from '../src/data/species.ts';

const ROOT = 'src/content/animals';
const LANGS = ['en', 'it', 'de'];
const fileOf = (lang, slug) => join(ROOT, lang === 'en' ? '' : lang, `${slug}.md`);
const norm = (s) => s.replace(/\*+/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/[  ]/g, ' ').replace(/[’]/g, "'").replace(/\s+/g, ' ').toLowerCase();

const problems = [];
let checked = 0;
for (const lang of LANGS) {
  for (const slug of referencedSlugs(lang)) if (!existsSync(fileOf(lang, slug))) problems.push(`${lang}: article "${slug}" does not exist (${fileOf(lang, slug)})`);
}
for (const p of Object.values(PROFILES)) {
  for (const [section, items] of [['goNow', p.goNow], ['facts', p.facts], ['care', p.care]]) {
    items.forEach((item, i) => {
      if (!LANGS.some((l) => item[l])) problems.push(`${p.key}.${section}[${i}]: no language`);
      for (const lang of LANGS) {
        const c = item[lang]; if (!c) continue;
        const where = `${p.key}.${section}[${i}].${lang} (${c.slug})`;
        const f = fileOf(lang, c.slug);
        if (!existsSync(f)) { problems.push(`${where}: article missing`); continue; }
        const raw = readFileSync(f, 'utf8');
        const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
        const front = norm(m ? m[1] : ''), body = norm(m ? m[2] : raw);
        if (!c.text.trim()) problems.push(`${where}: empty text`);
        if (!c.sources.length) problems.push(`${where}: no source named`);
        if (!body.includes(norm(c.anchor))) problems.push(`${where}: anchor not found in article: "${c.anchor}"`);
        for (const s of c.sources) {
          const inBody = body.includes(norm(s)), inRefs = front.includes(norm(s));
          if (c.via === 'text' && !inBody) problems.push(`${where}: source "${s}" not named in the article text`);
          if (c.via === 'ref' && !inRefs && !inBody) problems.push(`${where}: source "${s}" not in the article's references`);
        }
        checked++;
      }
    });
  }
}
for (const lang of LANGS) if (!existsSync(fileOf(lang, GUINEA_PIG_ARTICLE[lang]))) problems.push(`guinea pig article missing in ${lang}`);

if (problems.length) { console.error(`species check: ${problems.length} problem(s)\n- ${problems.join('\n- ')}`); process.exit(1); }
console.log(`species check: ${checked} sourced entries OK across ${LANGS.length} languages`);
