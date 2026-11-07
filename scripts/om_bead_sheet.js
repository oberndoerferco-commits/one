// Render every design in the viewer as a thumbnail, from two angles.
const { chromium } = require('playwright');
const out = process.argv[2];

(async () => {
  const b = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const c = await b.newContext({ viewport: { width: 760, height: 760 }, deviceScaleFactor: 1, colorScheme: 'dark' });
  const p = await c.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8731/wrapped.html', { waitUntil: 'load' });
  await p.waitForFunction(() => !!window.bead, null, { timeout: 60000 });
  await p.waitForTimeout(3000);
  await p.evaluate(() => window.bead.still());

  const n = await p.evaluate(() => window.bead.count());
  const rows = [];
  for (let i = 0; i < n; i++) {
    await p.evaluate(j => window.bead.show(j), i);
    await p.waitForTimeout(1800);
    // the view the brief describes: looking at the equator band
    await p.evaluate(() => window.bead.view(-55, 10, 24));
    await p.waitForTimeout(900);
    await p.locator('#view').screenshot({ path: `${out}/dz-${String(i).padStart(2, '0')}a.png` });
    // and from above, down the hole
    await p.evaluate(() => window.bead.view(-55, 62, 24));
    await p.waitForTimeout(900);
    await p.locator('#view').screenshot({ path: `${out}/dz-${String(i).padStart(2, '0')}b.png` });
    const info = await p.evaluate(j => ({ name: window.bead.name(j), note: window.bead.note(j), marks: window.bead.marks() }), i);
    rows.push(info);
    console.log(String(i).padStart(2, '0'), info.name, '-', info.marks, 'marks');
  }
  console.log('ERRORS', errs.slice(0, 5));
  require('fs').writeFileSync(`${out}/designs.json`, JSON.stringify(rows, null, 1));
  await b.close();
})();
