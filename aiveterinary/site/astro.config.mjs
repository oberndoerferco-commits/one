import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';

// The site imports the app package's TypeScript sources directly (file:../app).
// Their own dependency (zod) must resolve from this package's node_modules so a
// site-only install (CI, Cloudflare Pages) builds without installing ../app.
const zod = fileURLToPath(new URL('./node_modules/zod', import.meta.url));

export default defineConfig({
  site: 'https://aiveterinary.org',
  trailingSlash: 'never',
  build: { format: 'file' },
  integrations: [sitemap()],
  vite: {
    server: { fs: { allow: ['..'] } },
    optimizeDeps: { exclude: ['aiveterinary-app'] },
    resolve: { alias: [{ find: /^zod$/, replacement: zod }] },
  },
});
