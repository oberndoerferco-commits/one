#!/usr/bin/env node
// Damask v3: the refined version. Same layout as v2 variation 4 ("Grand logo"),
// redrawn for elegance:
//   - calligraphic strokes: every curl swells in the middle, thins at the ends
//     and finishes in a teardrop
//   - clear weight order: ornaments boldest, frame lighter and tapered to points
//   - bigger paisleys that fill the ovals; about half the loose dots removed
//   - calmer clusters: fewer, larger pieces
// Two logo treatments: solid (like the photo's raised flower) and outline
// (like the mark itself, double line).
//
//   node design/damask-v3/generate.js
//
// Units: 1000-unit tile written out at 150 mm, so 6.7 units = 1 mm. The
// thinnest stroke anywhere is 7 units (1.05 mm).

const fs = require('fs');
const path = require('path');
const {
  S, f, pt, logoPath, circle, bez, spiral, leaf, quatrefoil, g, p, mirrorX, mirrorXY,
} = require('../damask-v2/generate.js');

const TILE_MM = +(process.env.TILE_MM || 150);
const MIN = 7; // thinnest stroke, units

// ---------- calligraphic stroke ----------
// Outline around a centreline whose width follows `wAt(t)` for t in [0, 1].
function stroke(points, wAt) {
  const n = points.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    tx /= len; ty /= len;
    const w = wAt(i / (n - 1)) / 2;
    L.push([points[i][0] - ty * w, points[i][1] + tx * w]);
    R.push([points[i][0] + ty * w, points[i][1] - tx * w]);
  }
  return 'M' + [...L, ...R.reverse()].map(pt).join(' L') + ' Z';
}
// thin → thick → thin, peaking a little before the middle
const swell = (lo, hi, peak = 0.4) => (t) =>
  lo + (hi - lo) * Math.pow(Math.sin(Math.PI * Math.min(1, t < peak ? t / peak * 0.5 : 0.5 + (t - peak) / (1 - peak) * 0.5)), 0.9);

// teardrop terminal: a drop whose point trails back along the stroke
function drop(at, from, r) {
  const dx = at[0] - from[0], dy = at[1] - from[1];
  const L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
  const tail = [at[0] - ux * r * 2.2, at[1] - uy * r * 2.2];
  const nx = -uy, ny = ux;
  const c = [at[0] + ux * r * 0.2, at[1] + uy * r * 0.2];
  return `M${pt(tail)} Q${pt([c[0] + nx * r * 1.6 - ux * r * 0.6, c[1] + ny * r * 1.6 - uy * r * 0.6])} ${pt([c[0] + ux * r, c[1] + uy * r])}` +
    ` Q${pt([c[0] - nx * r * 1.6 - ux * r * 0.6, c[1] - ny * r * 1.6 - uy * r * 0.6])} ${pt(tail)} Z ` + circle(c, r);
}

// C-scroll: lead-in that flows into a spiral, swelling, teardrop at the end.
function scroll({ len = 40, r0 = 34, r1 = 9, sweep = 1.7 * Math.PI, hi = 17, bulb = 9, bend = 0 } = {}) {
  const lead = bez([0, 0], [len * 0.35, bend], [len * 0.7, 0], [len, 0], 18);
  const sp = spiral([len, -r0], r0, r1, Math.PI / 2, -sweep, 70);
  const pts = [...lead.slice(0, -1), ...sp];
  return stroke(pts, swell(MIN, hi, 0.35)) + ' ' + drop(pts[pts.length - 1], pts[pts.length - 4], bulb);
}

// Paisley: swelling teardrop body whose tail rolls into a curl; a swelling
// inner curl in the head; one bead.
function paisley(L = 150, H = 54) {
  const tipX = L * 0.8;
  const body = [
    ...bez([L * 0.5, -H * 0.55], [L * 0.2, -H * 1.3], [-H * 1.15, -H * 1.15], [-H, 0]),
    ...bez([-H, 0], [-H * 0.85, H * 1.2], [L * 0.35, H * 1.05], [tipX, -H * 0.05]).slice(1),
  ];
  const tail = spiral([tipX - H * 0.1, -H * 0.55], H * 0.5, H * 0.15, Math.PI * 0.4, -1.75 * Math.PI, 50);
  const pts = [...body, ...tail.slice(1)];
  const inner = spiral([-H * 0.12, -H * 0.05], H * 0.5, H * 0.13, Math.PI, 1.55 * Math.PI, 40);
  return [
    stroke(pts, (t) => MIN + 8 * Math.pow(Math.sin(Math.PI * Math.min(1, t * 1.35)), 1.2) * (t < 0.74 ? 1 : 0.4)),
    drop(pts[pts.length - 1], pts[pts.length - 4], 7.5),
    stroke(inner, swell(MIN, 13, 0.3)), drop(inner[inner.length - 1], inner[inner.length - 4], 7),
    circle([L * 0.34, H * 0.22], 6.5),
  ].join(' ');
}

// ---------- motifs ----------
const LOGO_R = 205;
const FH = 360, FV = 440;

function logo(style) {
  const d = logoPath(LOGO_R);
  if (style === 'solid') return p(d);
  // outline: the mark as a line, with a smaller echo of it inside
  return `<path d="${d}" fill="none" stroke="currentColor" stroke-width="11" stroke-linejoin="miter" stroke-miterlimit="3"/>` +
    `<path d="${logoPath(LOGO_R * 0.66)}" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="miter" stroke-miterlimit="3"/>`;
}

// frame: tapered curves, fine at the points, 11 units at the widest
function frame() {
  const out = [];
  for (const [sx, sy] of [[1, 1], [-1, 1], [1, -1], [-1, -1]]) {
    const pts = bez([FH, 0], [150, 18], [40, 180], [0, FV], 70).map(([x, y]) => [x * sx, y * sy]);
    out.push(p(stroke(pts, (t) => MIN + 4 * Math.sin(Math.PI * t))));
  }
  // a single teardrop inside each point, pointing out
  for (const [x, y, r] of [[0, -FV, 0], [0, FV, 180], [FH, 0, 90], [-FH, 0, -90]])
    out.push(g(`translate(${x} ${y}) rotate(${r})`, p(leaf([0, 64], [0, 24], 10))));
  return out.join('');
}

const OVAL = [205, 118];
function medallion() {
  const [rx, ry] = OVAL;
  return [
    `<ellipse rx="${rx}" ry="${ry}" fill="none" stroke="currentColor" stroke-width="9"/>`,
    mirrorXY(g(`translate(${-rx * 0.6} ${-ry * 0.44}) scale(0.74)`, p(paisley(150, 50)))),
    // spine: three graded beads and two leaves
    p([circle([0, 0], 10), circle([0, -30], 7), circle([0, 30], 7)].join(' ')),
    mirrorX(p(leaf([16, 0], [44, 0], 8))),
  ].join('');
}

function cluster() {
  return [
    p(circle([0, 0], 11) + ' ' + circle([0, -32], 7.5) + ' ' + circle([0, 32], 7.5)),
    mirrorX(g('translate(122 0)', p(quatrefoil(15)) + '<circle r="5.5" class="cut"/>')),
    // one pair of big ram's-horn scrolls above and below
    mirrorXY(g('translate(24 -22) rotate(-24)', p(scroll({ len: 26, r0: 38, r1: 10, hi: 15, bulb: 8.5 })))),
    // a long leaf reaching towards each oval
    mirrorXY(p(leaf([150, -44], [215, -104], 15))),
  ].join('');
}

// ---------- tile ----------
function tileArt(logoStyle) {
  const A = [[0, 0], [S / 2, S / 2]];
  const B = [[S / 2, 0], [0, S / 2]];
  const M = [[S / 4, S / 4], [3 * S / 4, S / 4], [S / 4, 3 * S / 4], [3 * S / 4, 3 * S / 4]];
  const F = frame(), L = logo(logoStyle), Bm = cluster(), Mm = medallion();
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
  place(A, L);
  place(B, Bm);
  place(M, Mm, (x, y) => ` rotate(${((x < S / 2) === (y < S / 2)) ? -18 : 18})`);
  return out.join('\n');
}

module.exports = { tileArt, TILE_MM };

if (require.main === module) {
  const K = TILE_MM / S;
  for (const style of ['solid', 'outline']) {
    const file = path.join(__dirname, `damask-v3-${style}-tile.svg`);
    fs.writeFileSync(file,
      `<svg xmlns="http://www.w3.org/2000/svg" width="${TILE_MM}mm" height="${TILE_MM}mm" viewBox="0 0 ${TILE_MM} ${TILE_MM}">
<rect width="${TILE_MM}" height="${TILE_MM}" fill="#fff"/>
<clipPath id="c"><rect width="${TILE_MM}" height="${TILE_MM}"/></clipPath>
<g clip-path="url(#c)"><g transform="scale(${K})" fill="#000" color="#000"><style>.cut{fill:#fff}.cutline{stroke:#fff}</style>${tileArt(style)}</g></g>
</svg>
`);
  }
  console.log(`wrote damask-v3-solid-tile.svg, damask-v3-outline-tile.svg (repeat ${TILE_MM} mm, logo ${f(2 * LOGO_R * K)} mm)`);
}
