// Bundles src/*.ts (and the app's export/fingerprint code they import) into dist/. Uses the app's esbuild.
import { build } from '../app/node_modules/esbuild/lib/main.js';

await build({
  entryPoints: { popup: 'src/popup.ts', content: 'src/content.ts' },
  outdir: new URL('dist', import.meta.url).pathname,
  absWorkingDir: new URL('.', import.meta.url).pathname,
  bundle: true, format: 'iife', target: 'es2022', charset: 'utf8', legalComments: 'none', logLevel: 'info',
});
