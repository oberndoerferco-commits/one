// Copies the on-device OCR engine and the EN/IT/DE language data into dist/ocr,
// so the photo import loads everything from our own domain (no third-party CDN).
// Files come from node_modules at build time and are not committed.
import { cpSync, mkdirSync, existsSync } from 'node:fs';
const out = 'dist/ocr';
mkdirSync(`${out}/lang`, { recursive: true });
const copy = (from, to) => { if (!existsSync(from)) throw new Error(`OCR asset missing: ${from}`); cpSync(from, to); };
copy('node_modules/tesseract.js/dist/tesseract.esm.min.js', `${out}/tesseract.esm.min.js`);
copy('node_modules/tesseract.js/dist/worker.min.js', `${out}/worker.min.js`);
for (const f of ['tesseract-core-lstm.wasm.js', 'tesseract-core-simd-lstm.wasm.js']) copy(`node_modules/tesseract.js-core/${f}`, `${out}/${f}`);
for (const l of ['eng', 'ita', 'deu']) copy(`node_modules/@tesseract.js-data/${l}/4.0.0/${l}.traineddata.gz`, `${out}/lang/${l}.traineddata.gz`);
console.log('OCR assets copied to', out);
