#!/usr/bin/env node
// Builds shortlist.pdf: one A4 page per chosen variation, pattern at true
// scale (the swatch is 170 x 220 mm of real pattern), vector throughout.
//   node design/monogram-variations/shortlist.js 3 15 33 41
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const pick = process.argv.slice(2).map(Number);
const rows = fs.readFileSync(path.join(dir, 'tiles', 'index.tsv'), 'utf8').trim().split('\n')
  .map((l) => l.split('\t')).filter((r) => pick.includes(+r[0]))
  .sort((a, b) => pick.indexOf(+a[0]) - pick.indexOf(+b[0]));
// inline each tile so the PDF carries the vector art itself
const pages = rows.map(([n, title, file, W, H]) => {
  const svg = fs.readFileSync(path.join(dir, 'tiles', file), 'utf8');
  const uri = 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64');
  return `<section>
  <header><span class="n">${n}</span><span class="t">${title}</span></header>
  <div class="sw" style="background-image:url(${uri});background-size:${W}mm ${H}mm"></div>
  <footer>Shown at true size · repeat ${W} × ${H} mm · artwork file tiles/${file}</footer>
</section>`;
}).join('');
const html = `<!doctype html><meta charset="utf-8"><style>
@page{size:A4;margin:0}
body{margin:0;font:14px/1.3 Georgia,serif;color:#2b2622}
section{width:210mm;height:297mm;box-sizing:border-box;padding:18mm 20mm;page-break-after:always;background:#f6f3ee}
header{display:flex;align-items:baseline;gap:5mm;margin-bottom:7mm}
.n{font-size:30pt}.t{font-size:16pt}
.sw{width:170mm;height:220mm;background-repeat:repeat;border-radius:1.5mm}
footer{margin-top:5mm;font-size:9pt;color:#6b625a}
</style>${pages}`;
(async () => {
  const f = path.join(dir, '.tmp-shortlist.html');
  fs.writeFileSync(f, html);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + f);
  await p.waitForTimeout(800);
  await p.pdf({ path: path.join(dir, 'shortlist.pdf'), format: 'A4', printBackground: true });
  await b.close();
  fs.unlinkSync(f);
  console.log('wrote shortlist.pdf', rows.map((r) => r[0]).join(', '));
})();
