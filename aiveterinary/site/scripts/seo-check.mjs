// Checks the built site for search problems. Run after a build:
//
//   npm run build && npm run check:seo          (or: node scripts/seo-check.mjs <outDir>)
//
// Errors (exit 1): page without title or description, duplicate title, canonical not the page's own URL,
// internal link to a page that was not built, hreflang that points nowhere, is one-way or lacks the page
// itself or x-default, sitemap URL that is missing or noindex, indexable page missing from the sitemap,
// JSON-LD that does not parse, duplicate element ids, robots.txt or llms.txt missing.
// Warnings: titles over 70 characters (search results cut them by width, about 600 px), descriptions under
// 50 characters, pages with more than one h1.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const DIR = process.argv[2] ?? 'dist';
const SITE = 'https://aiveterinary.org';
const errors = [], warnings = [];
const dec = (s) => s.replace(/&#34;|&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

const pages = new Map();
const walk = (d) => {
  for (const f of readdirSync(d, { withFileTypes: true })) {
    const p = join(d, f.name);
    if (f.isDirectory()) { if (!/^(_astro|pagefind|ocr)$/.test(f.name)) walk(p); continue; }
    if (!f.name.endsWith('.html')) continue;
    const rel = p.slice(DIR.replace(/\/$/, '').length).replace(/\.html$/, '').replace(/\/index$/, '');
    const url = rel === '' || rel === '/index' ? '/' : rel;
    const h = readFileSync(p, 'utf8');
    const head = h.slice(0, h.indexOf('</head>'));
    const ids = [...h.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
    pages.set(url, {
      title: dec(/<title>([^<]*)<\/title>/.exec(head)?.[1] ?? ''),
      desc: dec(/<meta name="description" content="([^"]*)"/.exec(head)?.[1] ?? ''),
      canon: /<link rel="canonical" href="([^"]*)"/.exec(head)?.[1],
      noindex: /<meta name="robots" content="[^"]*noindex/.test(head),
      lang: /<html lang="([^"]+)"/.exec(h)?.[1],
      alts: [...head.matchAll(/<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"/g)].map((m) => [m[1], m[2]]),
      links: [...h.matchAll(/<a\b[^>]*\shref="(\/[^"#?]*)/g)].map((m) => m[1]).filter((x) => !x.startsWith('//')),
      ld: [...h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map((m) => m[1]),
      h1: (h.match(/<h1[\s>]/g) ?? []).length,
      dupIds: [...new Set(ids.filter((x, i) => ids.indexOf(x) !== i))],
    });
  }
};
if (!existsSync(DIR)) { console.error(`seo check: ${DIR} does not exist; build first`); process.exit(1); }
walk(DIR);

const titles = new Map();
for (const [u, p] of pages) {
  if (u === '/404') continue;
  if (p.dupIds.length) errors.push(`${u}: duplicate id ${p.dupIds.join(', ')}`);
  for (const l of p.ld) { try { JSON.parse(l); } catch { errors.push(`${u}: JSON-LD does not parse`); } }
  for (const l of new Set(p.links)) {
    const t = l.replace(/\/$/, '') || '/';
    if (!pages.has(t) && !existsSync(join(DIR, l))) errors.push(`${u}: link to ${l}, which was not built`);
  }
  if (p.noindex) continue;
  if (!p.title) errors.push(`${u}: no <title>`);
  if (!p.desc) errors.push(`${u}: no meta description`);
  titles.set(p.title, [...(titles.get(p.title) ?? []), u]);
  if (p.title.length > 70) warnings.push(`${u}: title ${p.title.length} characters: "${p.title}"`);
  if (p.desc && p.desc.length < 50) warnings.push(`${u}: description only ${p.desc.length} characters`);
  if (p.h1 !== 1) warnings.push(`${u}: ${p.h1} h1 elements`);
  const self = SITE + (u === '/' ? '/' : u);
  if (p.canon !== self) errors.push(`${u}: canonical is ${p.canon ?? 'missing'}`);
  if (p.alts.length) {
    if (!p.alts.some(([, h]) => h === self)) errors.push(`${u}: hreflang set does not include the page itself`);
    if (!p.alts.some(([l]) => l === 'x-default')) errors.push(`${u}: hreflang without x-default`);
    for (const [l, h] of p.alts) {
      const t = pages.get(h.replace(SITE, '') || '/');
      if (!t || t.noindex) { errors.push(`${u}: hreflang ${l} points to ${h}, which is ${t ? 'noindex' : 'not built'}`); continue; }
      if (l !== 'x-default' && t.lang !== l) errors.push(`${u}: hreflang ${l} points to a page in ${t.lang}`);
      if (!t.alts.some(([, b]) => b === self)) errors.push(`${u}: hreflang ${l} → ${h} does not link back`);
    }
  }
}
for (const [t, us] of titles) if (us.length > 1) errors.push(`duplicate title "${t}": ${us.join(', ')}`);

const sm = readdirSync(DIR).filter((f) => /^sitemap-\d+\.xml$/.test(f)).map((f) => readFileSync(join(DIR, f), 'utf8')).join('');
const locs = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]));
if (!locs.size) errors.push('sitemap: no URLs (sitemap-0.xml missing?)');
for (const l of locs) { const p = pages.get(l.replace(SITE, '') || '/'); if (!p) errors.push(`sitemap: ${l} was not built`); else if (p.noindex) errors.push(`sitemap: ${l} is noindex`); }
for (const [u, p] of pages) if (u !== '/404' && !p.noindex && !locs.has(SITE + (u === '/' ? '/' : u))) errors.push(`sitemap: ${u} is missing`);
for (const f of ['robots.txt', 'llms.txt']) if (!existsSync(join(DIR, f))) errors.push(`${f} missing`);

for (const w of warnings) console.warn(`warning: ${w}`);
for (const e of errors) console.error(`error: ${e}`);
console.log(`seo check: ${pages.size} pages, ${locs.size} sitemap URLs, ${errors.length} errors, ${warnings.length} warnings`);
process.exit(errors.length ? 1 : 0);
