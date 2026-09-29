#!/usr/bin/env node
// Damask monogram: the first reference (oval scroll medallions, small flowers,
// scroll clusters) redrawn as stamp-ready vector art, with the star-cross
// standing on its own where the reference had its big flower — no star frame.
//
//   node design/damask-pattern/generate.js
//
// Drawn in units on a 400-unit tile, written out in millimetres (TILE_MM).
// At the default 80 mm repeat, 5 units = 1 mm: every line and gap is kept at
// 5 units or more so it survives stamping into leather.
//   A (corners + centre)   logo
//   B (edge midpoints)     small flower with a pair of scrolls above and below
//   M (quarter points)     oval medallion with four mirrored C-scrolls

const fs = require('fs');
const path = require('path');

const S = 400;
const TILE_MM = 80;
const K = TILE_MM / S; // mm per unit
const f = (n) => +n.toFixed(2);
const pt = (p) => `${f(p[0])} ${f(p[1])}`;

// ---------- shapes ----------
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

// Closed outline around a centreline whose width tapers from w0 to w1.
function taperedStroke(points, w0, w1) {
  const n = points.length, left = [], right = [];
  for (let i = 0; i < n; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    tx /= len; ty /= len;
    const w = (w0 + (w1 - w0) * (i / (n - 1))) / 2;
    left.push([points[i][0] - ty * w, points[i][1] + tx * w]);
    right.push([points[i][0] + ty * w, points[i][1] - tx * w]);
  }
  return 'M' + [...left, ...right.reverse()].map(pt).join(' L') + ' Z';
}

function spiral(c, r0, r1, a0, sweep, n = 90) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const r = r0 * Math.pow(r1 / r0, t);
    out.push([c[0] + r * Math.cos(a0 + sweep * t), c[1] + r * Math.sin(a0 + sweep * t)]);
  }
  return out;
}

const circle = (c, r) =>
  `M${f(c[0] - r)} ${f(c[1])} a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0 a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0 Z`;

// C-scroll: rises from near the origin, rolls over to the right and curls
// down into a round terminal. Mirrored by callers.
function scroll(k = 1) {
  const pts = spiral([40 * k, -14 * k], 30 * k, 13 * k, Math.PI * 1.02, Math.PI * 1.38);
  const end = pts[pts.length - 1];
  return taperedStroke(pts, 10 * k, 6) + ' ' + circle(end, Math.max(6.5 * k, 5));
}

function leaf(base, tip, width) {
  const mx = (base[0] + tip[0]) / 2, my = (base[1] + tip[1]) / 2;
  const dx = tip[0] - base[0], dy = tip[1] - base[1];
  const len = Math.hypot(dx, dy), nx = -dy / len, ny = dx / len;
  const c1 = [mx + nx * width - dx * 0.1, my + ny * width - dy * 0.1];
  const c2 = [mx - nx * width - dx * 0.1, my - ny * width - dy * 0.1];
  return `M${pt(base)} Q${pt(c1)} ${pt(tip)} Q${pt(c2)} ${pt(base)} Z`;
}

const mirror4 = (d) =>
  [[1, 1], [-1, 1], [1, -1], [-1, -1]].map(([sx, sy]) => `<path transform="scale(${sx} ${sy})" d="${d}"/>`).join('');

// ---------- motifs (local coordinates) ----------
const LOGO_R = +(process.env.LOGO_R || 66);
const A_MOTIF = `<path d="${logoPath(LOGO_R)}"/>`;

const M_MOTIF = [
  `<ellipse rx="84" ry="58" fill="none" stroke="currentColor" stroke-width="5"/>`,
  mirror4(scroll(1)),
  `<path d="${leaf([0, -24], [0, -46], 7)} ${leaf([0, 24], [0, 46], 7)}"/>`,
  `<path d="${circle([0, 0], 6.5)} ${circle([74, 0], 5)} ${circle([-74, 0], 5)}"/>`,
].join('');

const flower = [0, 1, 2, 3].map((i) => {
  const a = (i * Math.PI) / 2;
  return circle([Math.sin(a) * 9.5, -Math.cos(a) * 9.5], 8.5);
}).join(' ');
const B_MOTIF = [
  `<path d="${flower}"/>`,
  `<circle r="3.4" class="cut"/>`,
  `<g transform="translate(0 -24)">${[1, -1].map((sx) => `<path transform="scale(${sx * 0.8} 0.8)" d="${scroll(1)}"/>`).join('')}</g>`,
  `<g transform="translate(0 24) scale(1 -1)">${[1, -1].map((sx) => `<path transform="scale(${sx * 0.8} 0.8)" d="${scroll(1)}"/>`).join('')}</g>`,
  `<path d="${leaf([24, 0], [48, 0], 7)} ${leaf([-24, 0], [-48, 0], 7)} ${circle([59, 0], 5)} ${circle([-59, 0], 5)}"/>`,
].join('');

// ---------- tile ----------
function placements() {
  const A = [[0, 0], [S / 2, S / 2]];
  const B = [[S / 2, 0], [0, S / 2]];
  const M = [[S / 4, S / 4], [3 * S / 4, S / 4], [S / 4, 3 * S / 4], [3 * S / 4, 3 * S / 4]];
  const out = [];
  const add = (list, motif) => {
    for (const [x, y] of list)
      for (const dx of [-S, 0, S]) for (const dy of [-S, 0, S]) {
        const X = x + dx, Y = y + dy;
        if (X < -S / 2 || X > 1.5 * S || Y < -S / 2 || Y > 1.5 * S) continue;
        out.push(`<g transform="translate(${X} ${Y})">${motif}</g>`);
      }
  };
  add(A, A_MOTIF);
  add(B, `<g transform="scale(1.2)">${B_MOTIF}</g>`);
  // ovals tilt along the diagonals; ORIENT=a points their tips at the logos
  const toLogo = (process.env.ORIENT || 'a') === 'a';
  for (const [x, y] of M) {
    const parity = Math.round((x - S / 4) / (S / 2) + (y - S / 4) / (S / 2)) % 2 === 0;
    const r = parity === toLogo ? 45 : -45;
    add([[x, y]], `<g transform="rotate(${r})">${M_MOTIF}</g>`);
  }
  return out.join('\n');
}

// Artwork group in mm: black shapes; `.cut` holes painted in the background colour.
const artMM = (ink = '#000', bg = '#fff') =>
  `<g transform="scale(${K})" fill="${ink}" color="${ink}"><style>.cut{fill:${bg}}</style>${placements()}</g>`;

const out = __dirname;
fs.writeFileSync(path.join(out, 'damask-tile.svg'),
  `<svg xmlns="http://www.w3.org/2000/svg" width="${TILE_MM}mm" height="${TILE_MM}mm" viewBox="0 0 ${TILE_MM} ${TILE_MM}">
<rect width="${TILE_MM}" height="${TILE_MM}" fill="#fff"/>
<clipPath id="c"><rect width="${TILE_MM}" height="${TILE_MM}"/></clipPath>
<g clip-path="url(#c)">${artMM()}</g>
</svg>
`);
const SW = 3 * TILE_MM, SH = 2 * TILE_MM;
fs.writeFileSync(path.join(out, `damask-sheet-${SW}x${SH}mm.svg`),
  `<svg xmlns="http://www.w3.org/2000/svg" width="${SW}mm" height="${SH}mm" viewBox="0 0 ${SW} ${SH}">
<defs><pattern id="p" width="${TILE_MM}" height="${TILE_MM}" patternUnits="userSpaceOnUse">
<rect width="${TILE_MM}" height="${TILE_MM}" fill="#fff"/>${artMM()}</pattern></defs>
<rect width="${SW}" height="${SH}" fill="url(#p)"/>
</svg>
`);
console.log(`wrote damask-tile.svg, damask-sheet-${SW}x${SH}mm.svg (repeat ${TILE_MM} mm, logo ${f(2 * LOGO_R * K)} mm)`);
