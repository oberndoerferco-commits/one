// The house plate, in the house letters, with the umlaut device on it.
//   node scripts/house_umlaut.js <serve-dir> <settings.json> <out-dir>
// The letters come from the viewer (traced from the artwork), so the
// device has to be added to its output rather than drawn beside it:
// the crown dots and the monogram are placed from the plate's own
// radius and cap height, which the viewer already knows.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), http = require('http');
const SERVE = process.argv[2], SET = process.argv[3], OUT = process.argv[4];
const PORT = 8756;
const T = {'.html':'text/html','.json':'application/json','.jpg':'image/jpeg'};
const DOT = 0.210, SPREAD = 0.340, ABOVE = 0.200, STROKE = 0.295;

(async () => {
  const want = JSON.parse(fs.readFileSync(SET,'utf8'));
  const srv = http.createServer((rq,rs)=>{
    const f = path.join(SERVE, rq.url.split('?')[0].replace(/^\/+/,'')||'index.html');
    fs.readFile(f,(e,b)=>{ if(e){rs.writeHead(404);rs.end();return;}
      rs.writeHead(200,{'content-type':T[path.extname(f)]||'application/octet-stream'});rs.end(b);});
  });
  await new Promise(r=>srv.listen(PORT,r));
  const b = await chromium.launch();
  const c = await b.newContext({viewport:{width:1400,height:900}});
  const p = await c.newPage();
  await p.goto(`http://localhost:${PORT}/index.html`,{waitUntil:'load'});
  await p.waitForFunction(()=>window.ready!==false,null,{timeout:60000});
  fs.mkdirSync(OUT,{recursive:true});

  for (const mode of ['crowned','crowned-knock','crowned-rule','lockup']){
    const w = Object.assign({}, want, {ghost:false});
    if (mode==='crowned-knock') w.invert = true;
    if (mode==='crowned-rule') { w.rule = 1.5; w.rulew = 0.38; }
    const got = await p.evaluate(ww=>{
      Object.assign(S,ww); FIRST={}; draw();
      return { svg: buildSVG(), R: G.last.lay.R, rt: G.last.r.rt, cap: S.cap };
    }, w);
    const D = got.cap*1.55, r = DOT*D/2, x = SPREAD*D/2;
    const cy = got.R - got.rt - got.cap*ABOVE*1.15;
    let add = `<g fill="#000"><circle cx="${-x}" cy="${cy}" r="${r}"/>`
            + `<circle cx="${x}" cy="${cy}" r="${r}"/></g>`;
    if (mode==='lockup'){
      const Dm = got.cap*2.9, ro = Dm/2, ri = Dm/2 - STROKE*Dm;
      const rr = DOT*Dm/2, xx = SPREAD*Dm/2;
      const off = got.R - got.rt - Dm*(0.5+ABOVE+DOT/2) - 2.4;
      add = `<g transform="translate(0 ${off})" fill="#000">`
          + `<path fill-rule="evenodd" d="M${-ro} 0A${ro} ${ro} 0 1 0 ${ro} 0`
          + `A${ro} ${ro} 0 1 0 ${-ro} 0ZM${-ri} 0A${ri} ${ri} 0 1 1 ${ri} 0`
          + `A${ri} ${ri} 0 1 1 ${-ri} 0Z"/>`
          + `<circle cx="${-xx}" cy="${-ro-ABOVE*Dm}" r="${rr}"/>`
          + `<circle cx="${xx}" cy="${-ro-ABOVE*Dm}" r="${rr}"/></g>`;
    }
    let svg = got.svg.replace('</svg>', add + '</svg>');
    // refit the box around everything, including what was just added
    const vb = await p.evaluate(s=>{
      const d=document.createElement('div'); d.innerHTML=s; document.body.appendChild(d);
      const el=d.querySelector('svg'); const r=el.getBBox(); d.remove();
      return [r.x,r.y,r.width,r.height];
    }, svg);
    const pad = Math.max(vb[2],vb[3])*0.05;
    const box = [vb[0]-pad, vb[1]-pad, vb[2]+2*pad, vb[3]+2*pad];
    svg = svg.replace(/viewBox="[^"]*"/, `viewBox="${box.join(' ')}"`)
             .replace(/width="[\d.]+mm"/, `width="${box[2].toFixed(2)}mm"`)
             .replace(/height="[\d.]+mm"/, `height="${box[3].toFixed(2)}mm"`);
    fs.writeFileSync(path.join(OUT, mode+'.svg'), svg);
    const pg = await c.newPage();
    await pg.setContent('<!doctype html><meta charset="utf-8"><style>@page{size:'
      + box[2].toFixed(2)+'mm '+box[3].toFixed(2)+'mm;margin:0}html,body{margin:0}'
      + 'svg{display:block}</style>'+svg.replace(/<\?xml[^>]*\?>\s*/,''),{waitUntil:'load'});
    await pg.pdf({path: path.join(OUT, mode+'.pdf'), width: box[2].toFixed(2)+'mm',
      height: box[3].toFixed(2)+'mm', printBackground:true,
      margin:{top:0,bottom:0,left:0,right:0}});
    await pg.close();
    console.log(mode+'  '+box[2].toFixed(1)+' x '+box[3].toFixed(1)+' mm');
  }
  await b.close(); srv.close();
})();
