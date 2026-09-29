#!/usr/bin/env node
// Ten variations of the damask, all denser and closer to the reference than v2.
//
//   node design/damask-v2/variations.js
//
// Writes variations/<nn>-<name>-tile.svg (stamp artwork at true size) and
// variations/contact-sheet.html (all ten embossed white on white, for review).
// Every variant keeps the same layout (logo, sweeping frame, oval medallions,
// centre clusters) and changes one or two things about it.

const fs = require('fs');
const path = require('path');
const {
  S, LINE, pt, logoPath, circle, taper, bez, spiral, curl, paisley, leaf, quatrefoil,
  g, p, mirrorX, mirrorXY,
} = require('./generate.js');

// ---------- building blocks ----------
const quarterPts = (FH, FV) => bez([FH, 0], [150, 18], [40, 180], [0, FV], 60);
const QUADS = [[1, 1], [-1, 1], [1, -1], [-1, -1]];
const flip = ([x, y], [sx, sy]) => [x * sx, y * sy];

function frame(c) {
  const out = [];
  for (const q of QUADS) {
    const pts = quarterPts(c.FH, c.FV).map((v) => flip(v, q));
    const d = 'M' + pts.map(pt).join(' L');
    if (c.frame === 'beads') {
      for (let i = 2; i < pts.length - 2; i += 3) out.push(p(circle(pts[i], 7.5)));
    } else if (c.frame === 'double') {
      out.push(`<path d="${d}" fill="none" stroke="currentColor" stroke-width="24" stroke-linecap="round"/>`);
      out.push(`<path d="${d}" fill="none" class="cutline" stroke-width="9" stroke-linecap="round"/>`);
    } else {
      out.push(`<path d="${d}" fill="none" stroke="currentColor" stroke-width="${LINE}" stroke-linecap="round"/>`);
    }
    // crossed ogee: the curves run on past the tall tips and cross at the cluster
    if (c.crossed) {
      const [tx, ty] = flip([0, c.FV], q);
      const ext = bez([tx, ty], [q[0] * -6, ty + q[1] * 30], [q[0] * -28, ty + q[1] * 52], [q[0] * -60, ty + q[1] * 60], 12);
      out.push(`<path d="M${ext.map(pt).join(' L')}" fill="none" stroke="currentColor" stroke-width="${LINE}" stroke-linecap="round"/>`);
    }
    // sprouts: curls (or leaves) growing off each curve into the open space
    // inside the frame — they stay well clear of the logo
    if (c.sprouts) {
      for (const i of [13, 31, 49]) {
        const a = pts[i], b = pts[i + 1];
        let tx = b[0] - a[0], ty = b[1] - a[1];
        const L = Math.hypot(tx, ty); tx /= L; ty /= L;
        let nx = -ty, ny = tx; // normal; flip it to point towards the logo
        if (nx * a[0] + ny * a[1] > 0) { nx = -nx; ny = -ny; }
        const ang = (Math.atan2(ny, nx) * 180) / Math.PI;
        if (c.sprouts === 'leaves') {
          out.push(p(leaf(a, [a[0] + nx * 52 + tx * 22, a[1] + ny * 52 + ty * 22], 12)));
          out.push(p(leaf(a, [a[0] + nx * 44 - tx * 26, a[1] + ny * 44 - ty * 26], 10)));
        } else {
          const side = i === 31 ? -1 : 1;
          out.push(g(`translate(${pt(a)}) rotate(${ang}) scale(0.55 ${0.55 * side})`, p(curl(30, 34, 8, 1.7 * Math.PI, 20, 14, 14))));
        }
      }
    }
  }
  // a drop and a bead just inside each tip, pointing out — detail, not a frame
  if (c.tipDrops) {
    for (const [x, y, r] of [[0, -c.FV, 0], [0, c.FV, 180], [c.FH, 0, 90], [-c.FH, 0, -90]]) {
      const k = Math.abs(y) ? 1 : 0.8;
      out.push(g(`translate(${x} ${y}) rotate(${r})`,
        p(leaf([0, 58 * k], [0, 22 * k], 9) + ' ' + circle([0, 76 * k], 7))));
    }
  }
  return out.join('');
}

function medallion(c) {
  const [rx, ry] = c.oval;
  const out = [];
  if (c.ovalRim === 'lace') {
    out.push(`<ellipse rx="${rx}" ry="${ry}" fill="none" stroke="currentColor" stroke-width="${LINE}"/>`);
    const n = 30;
    for (let i = 0; i < n; i++) {
      const t = (i / n) * 2 * Math.PI;
      out.push(p(circle([(rx + 17) * Math.cos(t), (ry + 17) * Math.sin(t)], 6)));
    }
  } else if (c.ovalRim === 'double') {
    out.push(`<ellipse rx="${rx}" ry="${ry}" fill="none" stroke="currentColor" stroke-width="${LINE}"/>`);
    out.push(`<ellipse rx="${rx - 16}" ry="${ry - 16}" fill="none" stroke="currentColor" stroke-width="7"/>`);
  } else {
    out.push(`<ellipse rx="${rx}" ry="${ry}" fill="none" stroke="currentColor" stroke-width="${LINE}"/>`);
  }
  const k = c.paisleyScale * (c.ovalRim === 'double' ? 0.8 : 1);
  out.push(mirrorXY(g(`translate(${-rx * (c.ovalRim === 'double' ? 0.6 : 0.64)} ${-ry * 0.39}) scale(${k})`, p(paisley(130, 46)))));
  if (c.ovalCentre === 'logo') {
    out.push(p(logoPath(40)));
  } else {
    out.push(p([circle([0, 0], 9), circle([0, -26], 7), circle([0, 26], 7), circle([0, -46], 5.5), circle([0, 46], 5.5)].join(' ')));
    out.push(mirrorX(p(leaf([14, 0], [34, 0], 6))));
  }
  if (c.ovalCurls) {
    // small curls filling the gaps at the top and bottom of the oval, and at its ends
    out.push(mirrorXY(g(`translate(10 ${-ry * 0.7}) scale(0.3)`, p(curl(30, 30, 8, 1.7 * Math.PI, 24, 20, 18)))));
  }
  return out.join('');
}

function cluster(c) {
  const out = [
    p([circle([0, 0], 9), circle([0, -26], 8), circle([0, 26], 8), circle([-26, 0], 7), circle([26, 0], 7),
      circle([0, -48], 6), circle([0, 48], 6)].join(' ')),
    mirrorX(g('translate(118 0)', p(quatrefoil(14)) + '<circle r="5" class="cut"/>')),
    mirrorXY(g('translate(40 -20) rotate(-20)', p(curl(30, 34, 8, 1.7 * Math.PI, 15, 8, 9)))),
    mirrorXY(p(leaf([150, -40], [205, -95], 12))),
  ];
  if (c.clusterExtra) {
    // second, smaller horns curling outward past the small flowers, plus bead trails
    out.push(mirrorXY(g('translate(150 -8) rotate(-70) scale(0.55)', p(curl(30, 34, 8, 1.7 * Math.PI, 20, 15, 15)))));
    out.push(mirrorXY(p(circle([70, -52], 6) + ' ' + circle([90, -66], 5.5))));
  }
  return out.join('');
}

function tile(c) {
  const A = [[0, 0], [S / 2, S / 2]];
  const B = [[S / 2, 0], [0, S / 2]];
  const M = [[S / 4, S / 4], [3 * S / 4, S / 4], [S / 4, 3 * S / 4], [3 * S / 4, 3 * S / 4]];
  const logo = p(logoPath(c.logoR));
  const F = frame(c), Bm = cluster(c), Mm = medallion(c);
  const out = [];
  const place = (list, motif, tf = () => '') => {
    for (const [x, y] of list)
      for (const dx of [-S, 0, S]) for (const dy of [-S, 0, S]) {
        const X = x + dx, Y = y + dy;
        if (X < -S / 2 || X > 1.5 * S || Y < -S / 2 || Y > 1.5 * S) continue;
        out.push(`<g transform="translate(${X} ${Y})${tf(x, y)}">${motif}</g>`);
      }
  };
  place(A, F);
  place(A, logo);
  place(B, Bm);
  place(M, Mm, (x, y) => ` rotate(${((x < S / 2) === (y < S / 2)) ? -c.tilt : c.tilt})`);
  return out.join('\n');
}

// ---------- the ten variations ----------
const base = {
  mm: 150, logoR: 170, FH: 330, FV: 440, frame: 'line', crossed: false, sprouts: null, tipDrops: true,
  oval: [205, 118], ovalRim: 'single', paisleyScale: 0.84, ovalCentre: 'beads', ovalCurls: true,
  clusterExtra: true, tilt: 18,
};
const variants = [
  ['classic', 'Classic', 'Closest to the photo: every gap filled with curls, beads and drops.', {}],
  ['double-frame', 'Double frame', 'The sweeping frame drawn as a pair of parallel lines.', { frame: 'double' }],
  ['beaded-frame', 'Beaded frame', 'The frame made of beads instead of a line. Softer, more jewellery-like.', { frame: 'beads' }],
  ['grand-logo', 'Grand logo', 'Logo 20% larger; the frame widens to give it room.', { logoR: 205, FH: 360 }],
  ['crossed', 'Crossed ogee', 'Frame curves run past their points and cross, as in the photo.', { crossed: true }],
  ['curling-frame', 'Curling frame', 'Small curls grow off the outside of every frame curve.', { sprouts: 'curls' }],
  ['acanthus', 'Acanthus', 'Pairs of leaves grow off the frame curves instead of curls.', { sprouts: 'leaves' }],
  ['lace', 'Lace medallions', 'Each oval ringed with a row of beads, like lace edging.', { ovalRim: 'lace', oval: [190, 106], paisleyScale: 0.78 }],
  ['monogram', 'Monogram medallions', 'A small logo at the heart of every oval, with a double rim.', { ovalCentre: 'logo', ovalRim: 'double' }],
  ['level', 'Level ovals', 'Ovals sit level, as most of the photo\'s do; frame with curls.', { tilt: 0, oval: [196, 112], paisleyScale: 0.8, sprouts: 'curls' }],
];

const outDir = path.join(__dirname, 'variations');
fs.mkdirSync(outDir, { recursive: true });
const cards = [];
variants.forEach(([key, title, note, over], i) => {
  const c = { ...base, ...over };
  const art = tile(c);
  const K = c.mm / S;
  const name = `${String(i + 1).padStart(2, '0')}-${key}`;
  fs.writeFileSync(path.join(outDir, `${name}-tile.svg`),
    `<svg xmlns="http://www.w3.org/2000/svg" width="${c.mm}mm" height="${c.mm}mm" viewBox="0 0 ${c.mm} ${c.mm}">
<rect width="${c.mm}" height="${c.mm}" fill="#fff"/>
<clipPath id="c"><rect width="${c.mm}" height="${c.mm}"/></clipPath>
<g clip-path="url(#c)"><g transform="scale(${K})" fill="#000" color="#000"><style>.cut{fill:#fff}.cutline{stroke:#fff}</style>${art}</g></g>
</svg>
`);
  cards.push({ name, title, note, art, n: i + 1 });
});

// contact sheet: each variant embossed white on white, 1.5 × 1.5 repeats
const bg = '#e7e5df';
const card = ({ name, title, note, art, n }) => `<figure>
<svg viewBox="0 0 ${1.5 * S} ${1.5 * S}" width="440" height="440">
  <defs>
    <g id="t${n}"><g fill="${bg}" color="${bg}"><style>.cut{fill:${bg}}.cutline{stroke:${bg}}</style>${art}</g></g>
    <filter id="e${n}" filterUnits="userSpaceOnUse" x="0" y="0" width="${1.5 * S}" height="${1.5 * S}">
      <feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="b"/>
      <feOffset in="b" dx="2.2" dy="2.6" result="so"/><feFlood flood-color="#6d6a60" flood-opacity=".6"/><feComposite in2="so" operator="in" result="s"/>
      <feOffset in="b" dx="-1.8" dy="-1.8" result="ho"/><feFlood flood-color="#fff"/><feComposite in2="ho" operator="in" result="h"/>
      <feMerge><feMergeNode in="s"/><feMergeNode in="h"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="${bg}"/>
  <g filter="url(#e${n})">${[-1, 0, 1, 2].flatMap((x) => [-1, 0, 1, 2].map((y) => `<use href="#t${n}" x="${x * S - S / 4}" y="${y * S - S / 4}"/>`)).join('')}</g>
</svg>
<figcaption><b>${n}. ${title}</b><br>${note}<br><code>${name}-tile.svg</code></figcaption>
</figure>`;
fs.writeFileSync(path.join(outDir, 'contact-sheet.html'), `<!doctype html><meta charset="utf-8"><title>Damask variations</title>
<style>
  body{margin:0;padding:28px;background:#f4f1ec;font:14px/1.4 Georgia,serif;color:#2b2622}
  .grid{display:grid;grid-template-columns:repeat(5,440px);gap:22px 18px}
  figure{margin:0} figcaption{margin-top:6px;color:#5b534c} figcaption b{color:#2b2622;font-weight:normal;font-size:16px}
  code{font-size:11px;color:#8a8076}
</style>
<div class="grid">${cards.map(card).join('\n')}</div>
`);
console.log(`wrote ${cards.length} variations to variations/`);
