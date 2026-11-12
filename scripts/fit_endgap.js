// Solve the frame's end gap so the ink keeps a given clearance.
//
//   node scripts/fit_endgap.js <serve-dir> <settings.json> <target-mm>
//
// The ends were too close to the O and the R, and the amount is not
// guessable: a flatter arch turns the end letters less, so their outer
// corners reach further along the plate than the centres the end gap
// is measured from. The viewer already walks every letter path into
// the plate's polar frame and reports the worst clearance, so bisect
// on that rather than nudging the number.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), http = require('http');
const SERVE = process.argv[2], SET = process.argv[3], TARGET = +process.argv[4];
const PORT = 8753;
const TYPES = { '.html':'text/html', '.json':'application/json', '.jpg':'image/jpeg' };
const serve = (dir, port) => new Promise(res => {
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

(async () => {
  const want = JSON.parse(fs.readFileSync(SET, 'utf8'));
  const server = await serve(SERVE, PORT);
  const b = await chromium.launch();
  const p = await (await b.newContext()).newPage();
  await p.goto(`http://localhost:${PORT}/index.html`, { waitUntil: 'load' });
  await p.waitForFunction(() => window.ready !== false, null, { timeout: 60000 });

  const clear = async eg => p.evaluate(w => {
    Object.assign(S, w); FIRST = {}; draw();
    return { mm: G.last.clear.mm, ch: G.last.clear.ch, w: G.last.w };
  }, Object.assign({}, want, { endgap: eg, ghost: false }));

  const before = await clear(want.endgap);
  let lo = 0, hi = 40;
  for (let i = 0; i < 40; i++){
    const mid = (lo + hi) / 2;
    const c = await clear(mid);
    if (c.mm < TARGET) lo = mid; else hi = mid;
  }
  const eg = (lo + hi) / 2;
  const after = await clear(eg);
  console.log(JSON.stringify({ endgap: +eg.toFixed(2),
    before: { endgap: want.endgap, clear: +before.mm.toFixed(2), ch: before.ch, w: +before.w.toFixed(1) },
    after: { clear: +after.mm.toFixed(2), ch: after.ch, w: +after.w.toFixed(1) } }));
  await b.close(); server.close();
})();
