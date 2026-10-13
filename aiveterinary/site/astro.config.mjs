import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://aiveterinary.org',
  trailingSlash: 'never',
  build: { format: 'file' },
  integrations: [sitemap()],
  vite: { server: { fs: { allow: ['..'] } }, optimizeDeps: { exclude: ['aiveterinary-app'] } },
});
