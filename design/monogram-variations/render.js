#!/usr/bin/env node
// Renders each tile as a 150 × 150 mm swatch (4 px/mm) and assembles numbered
// comparison sheets of ten (two per row) plus one overview of all fifty.
//   node design/monogram-variations/render.js
// Needs Playwright (Chromium); writes previews/ and sheet-*.jpg via sharp-free
// HTML screenshots.
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const rows = fs.readFileSync(path.join(dir, 'tiles', 'index.tsv'), 'utf8').trim().split('\n').map((l) => l.split('\t'));
const PX = 4, VIEW = 150 * PX;
const cell = ([n, title, file, W, H], size) => `<figure><div style="width:${size}px;height:${size}px;background:url(tiles/${file}) center/${W * PX * size / VIEW}px ${H * PX * size / VIEW}px repeat"></div><figcaption><b>${n}</b> ${title}</figcaption></figure>`;
const page = (cells, cols, size) => `<!doctype html><meta charset="utf-8"><style>
body{margin:0;padding:24px;background:#f1ede6;font:600 ${size > 300 ? 26 : 15}px/1.25 system-ui,sans-serif;color:#2b2622}
.g{display:grid;grid-template-columns:repeat(${cols},${size}px);gap:${size > 300 ? 26 : 12}px}
figure{margin:0} figcaption{margin-top:6px} b{display:inline-block;min-width:1.6em}
h1{margin:0 0 18px;font-size:${size > 300 ? 34 : 22}px}
</style><h1>__T__</h1><div class="g">${cells}</div>`;
(async () => {
  const b = await chromium.launch();
  const shoot = async (html, out, width) => {
    const f = path.join(dir, '.tmp-sheet.html');
    fs.writeFileSync(f, html);
    const p = await b.newPage({ viewport: { width, height: 800 } });
    await p.goto('file://' + f);
    await p.waitForTimeout(1500);
    await p.screenshot({ path: out, fullPage: true, type: 'jpeg', quality: 86 });
    await p.close();
    fs.unlinkSync(f);
  };
  for (let s = 0; s < 5; s++) {
    const part = rows.slice(s * 10, s * 10 + 10);
    const html = page(part.map((r) => cell(r, 520)).join(''), 2, 520).replace('__T__', `Monogram variations ${s * 10 + 1}–${s * 10 + 10}`);
    await shoot(html, path.join(dir, `sheet-${s + 1}.jpg`), 2 * 520 + 26 + 48);
  }
  const all = page(rows.map((r) => cell(r, 220)).join(''), 5, 220).replace('__T__', 'All 50 monogram variations');
  await shoot(all, path.join(dir, 'overview-all-50.jpg'), 5 * 220 + 4 * 12 + 48);
  await b.close();
  console.log('wrote sheet-1..5.jpg and overview-all-50.jpg');
})();
