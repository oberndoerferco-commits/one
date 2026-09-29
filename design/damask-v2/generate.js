#!/usr/bin/env node
// Damask v2: a close vector redraw of the embossed reference (reference.jpg),
// with the star-cross in place of the large flower and nothing behind it.
//
//   node design/damask-v2/generate.js
//
// Layout (units; one tile is 1000 × 1000 and repeats edge to edge):
//   A  corners + centre     logo
//   F  around each A         tall frame of four sweeping curves
//   M  quarter points        oval medallion with mirrored paisley scrolls
//   B  edge midpoints        small flowers, bead chain and C-scrolls
// Written out at TILE_MM (default 150 mm): 1 mm = 6.7 units. Lines ≥ 7 units.

const fs = require('fs');
const path = require('path');

const S = 1000;
const TILE_MM = +(process.env.TILE_MM || 150);
const f = (n) => +n.toFixed(2);
const pt = (p) => `${f(p[0])} ${f(p[1])}`;
const LINE = 9; // standard raised line

// ---------- primitives ----------
function logoPath(R) {
  const k = R / 745; // traced from design/monogram-pattern/logo-reference.png
  const P = (x, y) => [x * k, y * k];
  const refl = ([x, y]) => [-y, -x];
  const tip = P(0, -745), a = P(143, -528), b = P(345, -419), c = P(199, -273), n = P(148, -146);
  const rot = ([x, y], q) => { for (let i = 0; i < q; i++) [x, y] = [-y, x]; return [x, y]; };
  const s = (p, q) => pt(rot(p, q));
  let d = '';
  for (let q = 0; q < 4; q++) {
    d += `${q ? 'L' : 'M'}${s(tip, q)} L${s(a, q)} L${s(b, q)} Q${s(c, q)} ${s(n, q)} `;
    d += `Q${s(refl(c), q)} ${s(refl(b), q)} L${s(refl(a), q)} `;
  }
  return d + 'Z';
}

const circle = (c, r) =>
  `M${f(c[0] - r)} ${f(c[1])} a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0 a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0 Z`;

function taper(points, w0, w1) {
  const n = points.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    tx /= len; ty /= len;
    const w = (w0 + (w1 - w0) * (i / (n - 1))) / 2;
    L.push([points[i][0] - ty * w, points[i][1] + tx * w]);
    R.push([points[i][0] + ty * w, points[i][1] - tx * w]);
  }
  return 'M' + [...L, ...R.reverse()].map(pt).join(' L') + ' Z';
}

// cubic Bézier sampled to points
function bez(p0, p1, p2, p3, n = 40) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1), u = 1 - t;
    out.push([
      u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
      u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
    ]);
  }
  return out;
}

// spiral from angle a0 (radius r0) turning `sweep` while shrinking to r1
function spiral(c, r0, r1, a0, sweep, n = 70) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1), r = r0 * Math.pow(r1 / r0, t);
    out.push([c[0] + r * Math.cos(a0 + sweep * t), c[1] + r * Math.sin(a0 + sweep * t)]);
  }
  return out;
}

// A curl: a lead-in curve that flows tangentially into a spiral with a bulb.
// Local frame: starts at origin heading +x, curls counter-clockwise (upwards).
function curl(len = 60, r0 = 26, r1 = 8, sweep = 1.75 * Math.PI, w0 = 12, w1 = 8, bulb = 8) {
  const c = [len, -r0];
  const lead = bez([0, 0], [len * 0.4, 0], [len * 0.75, 0], [len, 0], 20);
  const sp = spiral(c, r0, r1, Math.PI / 2, -sweep);
  const pts = [...lead.slice(0, -1), ...sp];
  const end = pts[pts.length - 1];
  return taper(pts, w0, w1) + ' ' + circle(end, bulb);
}

// A paisley (boteh): round head at the origin, body tapering towards +x
// into a tail that rolls up into a spiral. A small inner curl sits in the head.
function paisley(L = 130, H = 46) {
  const tipX = L * 0.8;
  const body = [
    ...bez([L * 0.5, -H * 0.55], [L * 0.2, -H * 1.3], [-H * 1.15, -H * 1.15], [-H, 0]),
    ...bez([-H, 0], [-H * 0.85, H * 1.2], [L * 0.35, H * 1.05], [tipX, -H * 0.05]).slice(1),
  ];
  const tail = spiral([tipX - H * 0.1, -H * 0.55], H * 0.52, H * 0.16, Math.PI * 0.4, -1.75 * Math.PI, 50);
  const pts = [...body, ...tail.slice(1)];
  const end = pts[pts.length - 1];
  const inner = spiral([-H * 0.1, -H * 0.05], H * 0.5, H * 0.14, Math.PI, 1.5 * Math.PI, 40);
  return [
    taper(pts, 11, 7), circle(end, 7), circle(body[0], 5.5),
    taper(inner, 9, 7), circle(inner[inner.length - 1], 6.5),
    circle([L * 0.28, H * 0.3], 6), circle([L * 0.45, H * 0.12], 5),
  ].join(' ');
}

function leaf(base, tip, width) {
  const mx = (base[0] + tip[0]) / 2, my = (base[1] + tip[1]) / 2;
  const dx = tip[0] - base[0], dy = tip[1] - base[1];
  const len = Math.hypot(dx, dy), nx = -dy / len, ny = dx / len;
  const c1 = [mx + nx * width - dx * 0.1, my + ny * width - dy * 0.1];
  const c2 = [mx - nx * width - dx * 0.1, my - ny * width - dy * 0.1];
  return `M${pt(base)} Q${pt(c1)} ${pt(tip)} Q${pt(c2)} ${pt(base)} Z`;
}

const quatrefoil = (r = 15) =>
  [0, 1, 2, 3].map((i) => circle([Math.sin(i * Math.PI / 2) * r * 1.05, -Math.cos(i * Math.PI / 2) * r * 1.05], r)).join(' ');

const g = (tf, inner) => `<g transform="${tf}">${inner}</g>`;
const p = (d, extra = '') => `<path d="${d}"${extra}/>`;
const mirrorX = (inner) => inner + g('scale(-1 1)', inner);
const mirrorY = (inner) => inner + g('scale(1 -1)', inner);
const mirrorXY = (inner) => mirrorY(mirrorX(inner));

// ---------- motifs ----------
const LOGO_R = 170;
const A_MOTIF = p(logoPath(LOGO_R));

// frame: four sweeping curves, tall (tips at ±FV) and narrower (±FH)
const FV = 440, FH = 330;
const frameQuarter = (sx, sy) => {
  const q = ([x, y]) => [x * sx, y * sy];
  return `M${pt(q([FH, 0]))} C${pt(q([150, 18]))} ${pt(q([40, 180]))} ${pt(q([0, FV]))}`;
};
// the curves stop short of the logo's tips: nothing sits behind the logo
const F_MOTIF = `<path d="${[[1, 1], [-1, 1], [1, -1], [-1, -1]].map(([a, b]) => frameQuarter(a, b)).join(' ')}"
  fill="none" stroke="currentColor" stroke-width="${LINE}" stroke-linecap="round"/>`;

// oval medallion, tilted so its long axis runs with the frame curves
const MR = [205, 118];
const M_MOTIF = [
  `<ellipse rx="${MR[0]}" ry="${MR[1]}" fill="none" stroke="currentColor" stroke-width="${LINE}"/>`,
  mirrorXY(g('translate(-132 -46) scale(0.84)', p(paisley(130, 46)))),
  p([circle([0, 0], 9), circle([0, -26], 7), circle([0, 26], 7), circle([0, -46], 5.5), circle([0, 46], 5.5)].join(' ')),
  mirrorX(p(leaf([14, 0], [34, 0], 6))),
].join('');

// B cluster: bead cross, two small flowers, four big C-scrolls, leaves
const B_MOTIF = [
  p([circle([0, 0], 9), circle([0, -26], 8), circle([0, 26], 8), circle([-26, 0], 7), circle([26, 0], 7),
    circle([0, -48], 6), circle([0, 48], 6)].join(' ')),
  mirrorX(g('translate(118 0)', p(quatrefoil(14)) + `<circle r="5" class="cut"/>`)),
  // ram's-horn scrolls rising from the centre over the small flowers
  mirrorXY(g('translate(40 -20) rotate(-20)', p(curl(30, 34, 8, 1.7 * Math.PI, 15, 8, 9)))),
  mirrorXY(p(leaf([150, -40], [205, -95], 12))),
].join('');

// ---------- tile ----------
function tileArt() {
  const A = [[0, 0], [S / 2, S / 2]];
  const B = [[S / 2, 0], [0, S / 2]];
  const M = [[S / 4, S / 4], [3 * S / 4, S / 4], [S / 4, 3 * S / 4], [3 * S / 4, 3 * S / 4]];
  const out = [];
  const place = (list, motif, tf = () => '') => {
    for (const [x, y] of list)
      for (const dx of [-S, 0, S]) for (const dy of [-S, 0, S]) {
        const X = x + dx, Y = y + dy;
        if (X < -S / 2 || X > 1.5 * S || Y < -S / 2 || Y > 1.5 * S) continue;
        out.push(`<g transform="translate(${X} ${Y})${tf(x, y)}">${motif}</g>`);
      }
  };
  place(A, F_MOTIF);
  place(A, A_MOTIF);
  place(B, B_MOTIF);
  // medallions tilt along the channel they sit in (alternating ±)
  place(M, M_MOTIF, (x, y) => ` rotate(${((x < S / 2) === (y < S / 2)) ? -18 : 18})`);
  return out.join('\n');
}

const K = TILE_MM / S;
const artMM = (ink = '#000', bg = '#fff') =>
  `<g transform="scale(${K})" fill="${ink}" color="${ink}"><style>.cut{fill:${bg}}</style>${tileArt()}</g>`;

const out = __dirname;
fs.writeFileSync(path.join(out, 'damask-v2-tile.svg'),
  `<svg xmlns="http://www.w3.org/2000/svg" width="${TILE_MM}mm" height="${TILE_MM}mm" viewBox="0 0 ${TILE_MM} ${TILE_MM}">
<rect width="${TILE_MM}" height="${TILE_MM}" fill="#fff"/>
<clipPath id="c"><rect width="${TILE_MM}" height="${TILE_MM}"/></clipPath>
<g clip-path="url(#c)">${artMM()}</g>
</svg>
`);
const SW = 2 * TILE_MM, SH = 2 * TILE_MM;
fs.writeFileSync(path.join(out, `damask-v2-sheet-${SW}x${SH}mm.svg`),
  `<svg xmlns="http://www.w3.org/2000/svg" width="${SW}mm" height="${SH}mm" viewBox="0 0 ${SW} ${SH}">
<defs><pattern id="p" width="${TILE_MM}" height="${TILE_MM}" patternUnits="userSpaceOnUse">
<rect width="${TILE_MM}" height="${TILE_MM}" fill="#fff"/>${artMM()}</pattern></defs>
<rect width="${SW}" height="${SH}" fill="url(#p)"/>
</svg>
`);
console.log(`wrote damask-v2-tile.svg, damask-v2-sheet-${SW}x${SH}mm.svg (repeat ${TILE_MM} mm, logo ${f(2 * LOGO_R * K)} mm)`);
