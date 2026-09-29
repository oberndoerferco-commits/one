import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://aiveterinary.org',
  trailingSlash: 'never',
  build: { format: 'file' },
});
