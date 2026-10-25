import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';

// lastmod for article URLs, from each article's own `updated:` date.
const contentDir = fileURLToPath(new URL('./src/content/animals/', import.meta.url));
const updated = new Map();
for (const lang of ['', 'it', 'de']) {
  const dir = contentDir + lang;
  if (!existsSync(dir)) continue;
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.md'))) {
    const m = /^updated:\s*['"]?(\d{4}-\d{2}-\d{2})/m.exec(readFileSync(`${dir}/${f}`, 'utf8'));
    if (m) updated.set(`${lang ? `/${lang}` : ''}/animals/${f.replace(/\.md$/, '')}`, m[1]);
  }
}

// Runs after @astrojs/sitemap. Makes the hreflang tags, the sitemap and llms.txt agree with the pages that
// were actually built, so routes added later (lexicon entries, food lists, new species) are covered without
// a hand-kept list:
//  - hreflang: an alternate is kept only if its page exists, is indexable and links back (Google ignores
//    one-way pairs); otherwise it is removed from the page, with a warning.
//  - sitemap: pages that are missing or noindex (404, empty listings) are removed; each URL gets the
//    alternates of its page; lastmod comes from the article's `updated` date or the page's dateModified.
//  - llms.txt: lines linking to pages that were not built are dropped; indexable pages it does not mention
//    yet (in any language) are listed under "More pages" with their title and description.
function seoAfterBuild() {
  return {
    name: 'seo-after-build',
    hooks: {
      'astro:build:done': ({ dir, logger }) => {
        const out = fileURLToPath(dir).replace(/\/$/, '');
        const SITE = 'https://aiveterinary.org';
        const attr = (tag, name) => new RegExp(`\\s${name}="([^"]*)"`).exec(tag)?.[1];
        const dec = (x) => x.replace(/&#34;|&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
        // Every built page: URL → its head facts.
        const pages = new Map();
        const walk = (d) => {
          for (const f of readdirSync(d, { withFileTypes: true })) {
            const p = `${d}/${f.name}`;
            if (f.isDirectory()) { if (!/^(_astro|pagefind|ocr)$/.test(f.name)) walk(p); continue; }
            if (!f.name.endsWith('.html')) continue;
            const rel = p.slice(out.length).replace(/\.html$/, '').replace(/\/index$/, '');
            const url = SITE + (rel === '' || rel === '/index' ? '/' : rel);
            const html = readFileSync(p, 'utf8');
            const head = html.slice(0, html.indexOf('</head>'));
            const alts = (head.match(/<link\b[^>]*>/g) ?? []).filter((t) => attr(t, 'rel') === 'alternate' && attr(t, 'hreflang')).map((t) => ({ tag: t, lang: attr(t, 'hreflang'), href: attr(t, 'href') }));
            pages.set(url, {
              file: p, html, alts,
              noindex: /<meta name="robots" content="[^"]*noindex/.test(head),
              title: dec(/<title>([^<]*)<\/title>/.exec(head)?.[1] ?? '').replace(/ · AI Veterinary$/, ''),
              desc: dec(/<meta name="description" content="([^"]*)"/.exec(head)?.[1] ?? ''),
              modified: /"dateModified":"(\d{4}-\d{2}-\d{2})/.exec(html)?.[1],
            });
          }
        };
        walk(out);
        const indexable = (u) => pages.has(u) && !pages.get(u).noindex;
        // hreflang: drop alternates that point nowhere, to noindex pages, or are not returned; repeat until stable.
        let fixedPages = 0;
        for (let pass = 0; pass < 5; pass++) {
          let changed = false;
          for (const [u, pg] of pages) {
            if (!pg.alts.length) continue;
            const langs = pg.alts.filter((a) => a.lang !== 'x-default');
            const ok = langs.filter((a) => a.href === u || (indexable(a.href) && pages.get(a.href).alts.some((b) => b.href === u)));
            const xd = pg.alts.find((a) => a.lang === 'x-default');
            const keep = ok.length >= 2 && ok.some((a) => a.href === u) ? [...ok, ...(xd && ok.some((a) => a.href === xd.href) ? [xd] : [])] : [];
            if (keep.length !== pg.alts.length) {
              for (const a of pg.alts) {
                if (keep.includes(a)) continue;
                pg.html = pg.html.replace(a.tag, '');
                // A translation that was not built: the language switcher and the "also available in" banner
                // use the same path, so point them at that language's home instead of a 404.
                if (!pages.has(a.href) && a.lang !== 'x-default') pg.html = pg.html.split(`"${a.href.slice(SITE.length)}"`).join(`"${a.lang === 'en' ? '/' : `/${a.lang}`}"`);
              }
              logger.warn(`hreflang: ${u} kept ${keep.length} of ${pg.alts.length} alternates`);
              pg.alts = keep; pg.dirty = true; changed = true;
            }
          }
          if (!changed) break;
        }
        for (const pg of pages.values()) if (pg.dirty) { writeFileSync(pg.file, pg.html); fixedPages++; }
        // Sitemap.
        let dropped = 0, kept = 0;
        const inSitemap = [];
        for (const f of readdirSync(out).filter((x) => /^sitemap-\d+\.xml$/.test(x))) {
          const xml = readFileSync(`${out}/${f}`, 'utf8');
          const next = xml.replace(/<url>([\s\S]*?)<\/url>/g, (block, inner) => {
            const loc = /<loc>([^<]+)<\/loc>/.exec(inner)?.[1] ?? '';
            if (!indexable(loc)) { dropped++; return ''; }
            kept++; inSitemap.push(loc);
            const pg = pages.get(loc);
            let body = inner.replace(/<xhtml:link\b[^>]*\/>/g, '');
            if (!/<lastmod>/.test(body) && pg.modified) body = body.replace('</loc>', `</loc><lastmod>${new Date(`${pg.modified}T00:00:00Z`).toISOString()}</lastmod>`);
            return `<url>${body}${pg.alts.map((a) => `<xhtml:link rel="alternate" hreflang="${a.lang}" href="${a.href}"/>`).join('')}</url>`;
          });
          writeFileSync(`${out}/${f}`, next);
        }
        // llms.txt.
        const llmsFile = `${out}/llms.txt`;
        let added = 0, removed = 0;
        if (existsSync(llmsFile)) {
          const original = readFileSync(llmsFile, 'utf8');
          const linked = new Set([...original.matchAll(/\]\((https:\/\/aiveterinary\.org[^)\s]*)\)/g)].map((m) => m[1]));
          const lines = original.split('\n').filter((line) => {
            const m = /^- \[[^\]]*\]\((https:\/\/aiveterinary\.org[^)\s]*)\)/.exec(line);
            if (m && !indexable(m[1]) && !/\.(txt|xml|json)$/.test(m[1])) { removed++; logger.warn(`llms.txt: dropped ${m[1]} (not built or noindex)`); return false; }
            return true;
          });
          const strip = (u) => u.replace(/^(https:\/\/aiveterinary\.org)\/(it|de)(?=\/|$)/, '$1');
          const extra = inSitemap.filter((u) => !linked.has(u) && !linked.has(strip(u)) && strip(u).replace(/\/$/, '') !== SITE);
          if (extra.length) {
            const names = { en: 'English', it: 'Italiano', de: 'Deutsch' };
            const more = ['## More pages'];
            for (const l of ['en', 'it', 'de']) {
              const list = extra.filter((u) => (/^https:\/\/aiveterinary\.org\/(it|de)(?=\/|$)/.exec(u)?.[1] ?? 'en') === l).sort();
              for (const u of list) { const pg = pages.get(u); more.push(`- [${pg.title} (${names[l]})](${u}): ${pg.desc}`); added++; }
            }
            const at = lines.indexOf('## Optional');
            lines.splice(at >= 0 ? at : lines.length, 0, ...more, '');
          }
          writeFileSync(llmsFile, lines.join('\n').replace(/\n{3,}/g, '\n\n'));
        }
        logger.info(`sitemap: ${kept} URLs, ${dropped} removed (missing or noindex); hreflang fixed on ${fixedPages} pages; llms.txt: ${added} pages added, ${removed} lines dropped`);
      },
    },
  };
}

// The site imports the app package's TypeScript sources directly (file:../app).
// Their own dependency (zod) must resolve from this package's node_modules so a
// site-only install (CI, Cloudflare Pages) builds without installing ../app.
const zod = fileURLToPath(new URL('./node_modules/zod', import.meta.url));

export default defineConfig({
  site: 'https://aiveterinary.org',
  trailingSlash: 'never',
  build: { format: 'file' },
  integrations: [sitemap({
    serialize(item) {
      const d = updated.get(new URL(item.url).pathname);
      if (d) item.lastmod = new Date(`${d}T00:00:00Z`).toISOString();
      return item;
    },
  }), seoAfterBuild()],
  vite: {
    server: { fs: { allow: ['..'] } },
    optimizeDeps: { exclude: ['aiveterinary-app'] },
    resolve: { alias: [{ find: /^zod$/, replacement: zod }] },
  },
});
