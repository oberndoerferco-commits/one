const {chromium} = require('playwright');
const fs = require('fs');

const VIEWS = {
  hero:    {pos:[-27,-53,57],  at:[0,-0.5,0.9],     fov:30, fill:0.80},
  three:   {pos:[-40,-60,34],  at:[0,-1,0.9],       fov:30, fill:0.82},
  plan:    {pos:[0,-16,70],    at:[0,-0.5,0.9],     fov:30, fill:0.84},
  rake:    {pos:[-16,-52,10],  at:[-2,-3,0.8],      fov:26, fill:0.90},
  detail:  {pos:[-7,-30,18],   at:[-1.6,-10.7,1.2], fov:20, dist:26},
  diamond: {pos:[8,-28,23],    at:[0,9.5,1.2],      fov:22, dist:30},
  // low and close, across the strokes - the angle that shows a stepped
  // top surface for what it is
  raking:  {pos:[-3,-24,6.5],  at:[-0.6,-8.5,1.0],  fov:24, dist:22},
};

(async () => {
  const dark = process.argv[2] === 'dark';
  const tag  = process.argv[3] || (dark ? 'dark' : 'light');
  const b64 = fs.readFileSync('logo.bin').toString('base64');
  let html = fs.readFileSync('studio.html', 'utf8');
  html = html.replace('window.READY = false;', `
    (function(){
      const s = "${b64}";
      const bin = atob(s); const buf = new ArrayBuffer(bin.length);
      const u8 = new Uint8Array(buf);
      for (let i=0;i<bin.length;i++) u8[i] = bin.charCodeAt(i);
      window.GEO = loadBlob(buf);
      window.READY = true;
    })();`);
  fs.writeFileSync('_r.html', html);

  const br = await chromium.launch();
  const p = await br.newPage({viewport:{width:1800,height:1350}});
  const errs = [];
  p.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  await p.goto('file://' + process.cwd() + '/_r.html');
  await p.waitForFunction(() => window.READY === true, {timeout:60000});
  await p.evaluate(d => window.setup({dark:d, brush:3.0}), dark);
  await p.waitForTimeout(600);
  for (const [name, v] of Object.entries(VIEWS)) {
    await p.evaluate(x => window.shoot(x), v);
    await p.waitForTimeout(250);
    await p.locator('canvas').screenshot({path:`${tag}_${name}.png`});

  }
  console.log(errs.length ? 'ERRORS:\n'+errs.join('\n') : 'ok ' + tag);
  await br.close();
})();
