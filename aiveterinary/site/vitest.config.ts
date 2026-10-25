import { defineConfig } from 'vitest/config';

// Unit tests for the pure modules (src/lib/ask-ai) and the /api/ask handler with a mock model client.
// Kept apart from astro.config.mjs: no Astro, no network, no API key needed.
export default defineConfig({
  test: { include: ['test/**/*.test.ts'], environment: 'node' },
});
