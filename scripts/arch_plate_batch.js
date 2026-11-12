// Export many settings files in one browser, instead of one browser each.
//
//   node scripts/arch_plate_batch.js <serve-dir> <json-dir> <out-dir>
//
// Fifty marks through the single-shot exporter is fifty Chromium starts
// and about four minutes of launching browsers. The page is the same
// page every time; only the settings change.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), http = require('http');
const SERVE = process.argv[2], JSONS = process.argv[3], OUT = process.argv[4];
const PORT = 8752;
const TYPES = { '.html':'text/html', '.json':'application/json', '.jpg':'image/jpeg' };

function serve(dir, port){
  return new Promise(res => {
    const s = http.createServer((rq, rs) => {
      const f = path.join(dir, rq.url.split('?')[0].replace(/^\/+/,'') || 'index.html');
      fs.readFile(f, (e, b) => {
        if (e){ rs.writeHead(404); rs.end(); return; }
        rs.writeHead(200, {'content-type': TYPES[path.extname(f)] || 'application/octet-stream'});
        rs.end(b);
      });
    });
    s.listen(port, () => res(s));
  });
}

(async () => {
  const files = fs.readdirSync(JSONS).filter(f => f.endsWith('.json')).sort();
  const server = await serve(SERVE, PORT);
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const p = await c.newPage();
  await p.goto(`http://localhost:${PORT}/index.html`, { waitUntil: 'load' });
  await p.waitForFunction(() => window.ready !== false, null, { timeout: 60000 });
  const page = await c.newPage();
  fs.mkdirSync(OUT, { recursive: true });

  for (const f of files){
    const name = path.basename(f, '.json');
    const want = JSON.parse(fs.readFileSync(path.join(JSONS, f), 'utf8'));
    const out = await p.evaluate(w => {
      Object.assign(S, w); FIRST = {}; draw();
      return { svg: buildSVG(), w: G.last.w, h: G.last.h };
    }, Object.assign({}, want, { ghost: false }));
    fs.writeFileSync(path.join(OUT, name + '.svg'), out.svg);
    const m = out.svg.match(/width="([\d.]+)mm"\s+height="([\d.]+)mm"/);
    const wmm = +m[1], hmm = +m[2];
    await page.setContent(
      '<!doctype html><meta charset="utf-8"><style>@page{size:' + wmm + 'mm ' +
      hmm + 'mm;margin:0}html,body{margin:0;padding:0}svg{display:block}</style>' +
      out.svg.replace(/<\?xml[^>]*\?>\s*/, ''), { waitUntil: 'load' });
    await page.pdf({ path: path.join(OUT, name + '.pdf'), width: wmm + 'mm',
                     height: hmm + 'mm', printBackground: true,
                     margin: {top:0,bottom:0,left:0,right:0} });
    console.log(name + '  ' + wmm.toFixed(0) + ' x ' + hmm.toFixed(0) + ' mm');
  }
  await b.close(); server.close();
})();
