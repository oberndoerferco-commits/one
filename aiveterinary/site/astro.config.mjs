import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';
import { readdirSync, readFileSync, existsSync } from 'node:fs';

// lastmod for article URLs, from each article's own `updated:` date.
const contentDir = fileURLToPath(new URL('./src/content/animals/', import.meta.url));
const updated = new Map();
for (const lang of ['', 'it', 'de']) {
  const dir = contentDir + lang;
  if (!existsSync(dir)) continue;
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.md'))) {
    const m = /^updated:\s*(\d{4}-\d{2}-\d{2})/m.exec(readFileSync(`${dir}/${f}`, 'utf8'));
    if (m) updated.set(`${lang ? `/${lang}` : ''}/animals/${f.replace(/\.md$/, '')}`, m[1]);
  }
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
    // Alternates are only emitted where the same path exists in another language.
    i18n: { defaultLocale: 'en', locales: { en: 'en', it: 'it', de: 'de' } },
    serialize(item) {
      const d = updated.get(new URL(item.url).pathname);
      if (d) item.lastmod = new Date(`${d}T00:00:00Z`).toISOString();
      return item;
    },
  })],
  vite: {
    server: { fs: { allow: ['..'] } },
    optimizeDeps: { exclude: ['aiveterinary-app'] },
    resolve: { alias: [{ find: /^zod$/, replacement: zod }] },
  },
});
