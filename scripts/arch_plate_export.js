// Write the nameplate out at a given set of settings, as SVG and PDF.
//
// The geometry lives in the viewer, and it stays there: this drives the
// same page headlessly rather than carrying a second copy of the maths in
// another language, because two implementations of an arch is one more
// than can be kept in step. The settings are the ones the viewer's "Copy
// settings" button puts on the clipboard.
//
//   node scripts/arch_plate_export.js <serve-dir> <settings.json> <out-dir>
//
// The PDF comes from Chromium's own print path, so it is vector: the
// letters stay outlines, not a picture of outlines.

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

const SERVE = process.argv[2];
const SETTINGS = process.argv[3];
const OUT = process.argv[4] || SERVE;
const PORT = 8749;

const TYPES = { '.html': 'text/html', '.json': 'application/json',
                '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };

function serve(dir, port){
  return new Promise(function(res){
    const s = http.createServer(function(rq, rs){
      const f = path.join(dir, rq.url.split('?')[0].replace(/^\/+/, '') || 'index.html');
      fs.readFile(f, function(e, b){
        if (e) { rs.writeHead(404); rs.end(); return; }
        rs.writeHead(200, {'content-type': TYPES[path.extname(f)] || 'application/octet-stream'});
        rs.end(b);
      });
    });
    s.listen(port, function(){ res(s); });
  });
}

(async () => {
  const want = JSON.parse(fs.readFileSync(SETTINGS, 'utf8'));
  const server = await serve(SERVE, PORT);
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const p = await c.newPage();
  p.on('pageerror', e => { console.log('PAGE ERROR:', e.message); });
  await p.goto(`http://localhost:${PORT}/index.html`, { waitUntil: 'load' });
  await p.waitForFunction(() => window.ready !== false, null, { timeout: 60000 });
  if (await p.evaluate(() => window.ready) !== true)
    throw new Error('viewer did not come up');

  const out = await p.evaluate((w) => {
    Object.assign(S, w);
    FIRST = {};
    draw();
    // the ghost never belongs in an export, whatever the settings say
    var svg = buildSVG();
    return { svg: svg, w: G.last.w, h: G.last.h,
             R: G.last.lay.R, span: G.last.lay.span };
  }, Object.assign({}, want, { ghost: false }));

  fs.mkdirSync(OUT, { recursive: true });
  const svgFile = path.join(OUT, 'oberndorfer-nameplate.svg');
  fs.writeFileSync(svgFile, out.svg);

  // measure the page the SVG asks for, then print it at exactly that size
  const m = out.svg.match(/width="([\d.]+)mm"\s+height="([\d.]+)mm"/);
  const wmm = +m[1], hmm = +m[2];
  const page = await c.newPage();
  await page.setContent(
    '<!doctype html><meta charset="utf-8">' +
    '<style>@page{size:' + wmm + 'mm ' + hmm + 'mm;margin:0}' +
    'html,body{margin:0;padding:0}svg{display:block}</style>' +
    out.svg.replace(/<\?xml[^>]*\?>\s*/, ''),
    { waitUntil: 'load' });
  await page.pdf({ path: path.join(OUT, 'oberndorfer-nameplate.pdf'),
                   width: wmm + 'mm', height: hmm + 'mm',
                   printBackground: true, margin: {top:0,bottom:0,left:0,right:0} });

  console.log('plate ' + out.w.toFixed(1) + ' x ' + out.h.toFixed(1) + ' mm' +
              '  ·  arch radius ' + (out.R === null || !isFinite(out.R)
                 ? 'straight' : out.R.toFixed(0) + ' mm') +
              '  ·  letters ' + out.span.toFixed(1) + ' mm along the baseline');
  console.log('page ' + wmm.toFixed(2) + ' x ' + hmm.toFixed(2) + ' mm');
  for (const f of ['oberndorfer-nameplate.svg', 'oberndorfer-nameplate.pdf'])
    console.log('   ' + path.join(OUT, f) + ': ' +
                (fs.statSync(path.join(OUT, f)).size / 1024).toFixed(0) + ' KB');

  await b.close();
  server.close();
})();
