// Shoot the bead from several angles, from the STL itself.
//   node bead_shoot.js <serve-dir> <out-dir> <stl-name> [tag] [dia] [cut]
const { chromium } = require('playwright');
const path = require('path');

const SERVE = process.argv[2];
const OUT = process.argv[3];
const STL = process.argv[4];
const TAG = process.argv[5] || 'bead';
const DIA = process.argv[6] || '7';
const CUT = process.argv[7] || '1';

// yaw, pitch, zoom, name
// yaw and pitch are longitude and latitude, so a mark's own coordinates
// aim the camera straight at it: the circled cross sits at lon 0 lat 45,
// the small OM at lon 45 lat 45, the big one on the equator.
const VIEWS = [
  [-38, 14, 1.00, 'hero'],
  [0, 4, 1.00, 'front'],
  [-38, 62, 1.00, 'top'],
  [-120, -22, 1.30, 'under'],
  [-38, 14, 2.30, 'macro'],
  [0, 45, 2.70, 'circle'],
  [45, 45, 2.90, 'smallom'],
];

(async () => {
  const b = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  // render big, then let the screenshot downsample: cheap supersampling
  const c = await b.newContext({ viewport: { width: 1100, height: 1100 }, deviceScaleFactor: 2 });
  const p = await c.newPage();
  p.on('pageerror', e => console.log('ERR', e.message));
  for (const [yaw, pitch, zoom, name] of VIEWS) {
    const q = `?stl=${encodeURIComponent(STL)}&dia=${DIA}&cut=${CUT}` +
              `&yaw=${yaw}&pitch=${pitch}&zoom=${zoom}`;
    await p.goto(`http://localhost:8731/bead-render.html${q}`, { waitUntil: 'load' });
    await p.waitForFunction(() => window.ready !== false, null, { timeout: 180000 });
    const st = await p.evaluate(() => window.ready);
    if (st !== true) { console.log(name, 'FAILED', st); continue; }
    await p.waitForTimeout(400);
    const file = path.join(OUT, `${TAG}-${name}.png`);
    await p.screenshot({ path: file });
    console.log(name, '->', file);
  }
  await b.close();
})();
