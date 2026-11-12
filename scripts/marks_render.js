// Fit each generated SVG to its own ink and write PNG + PDF.
//   node scripts/marks_render.js <svg-dir> <out-dir>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const IN = process.argv[2], OUT = process.argv[3];
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({viewport:{width:1600,height:900}})).newPage();
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(IN).filter(x => x.endsWith('.svg')).sort()){
    const raw = fs.readFileSync(path.join(IN, f), 'utf8');
    const pad = +(raw.match(/data-pad="([\d.]+)"/) || [0, 5])[1];
    await p.setContent('<!doctype html><meta charset="utf-8"><body style="margin:0">'
      + raw.replace('<svg ', '<svg id="m" width="900" height="400" ') + '</body>',
      { waitUntil: 'load' });
    const bb = await p.evaluate(() => {
      const s = document.getElementById('m'); const r = s.getBBox();
      return { x: r.x, y: r.y, w: r.width, h: r.height };
    });
    const vb = [bb.x - pad, bb.y - pad, bb.w + 2*pad, bb.h + 2*pad];
    const fitted = raw.replace('<svg ',
      `<svg viewBox="${vb.join(' ')}" width="${(vb[2]).toFixed(2)}mm" `
      + `height="${(vb[3]).toFixed(2)}mm" `);
    const name = f.replace(/\.svg$/, '');
    fs.writeFileSync(path.join(OUT, name + '.svg'), fitted);
    await p.setContent('<!doctype html><meta charset="utf-8"><style>@page{size:'
      + vb[2].toFixed(2) + 'mm ' + vb[3].toFixed(2) + 'mm;margin:0}'
      + 'html,body{margin:0}svg{display:block}</style>' + fitted,
      { waitUntil: 'load' });
    await p.pdf({ path: path.join(OUT, name + '.pdf'),
      width: vb[2].toFixed(2) + 'mm', height: vb[3].toFixed(2) + 'mm',
      printBackground: true, margin:{top:0,bottom:0,left:0,right:0} });
  }
  console.log('rendered');
  await b.close();
})();
