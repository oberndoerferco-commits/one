#!/usr/bin/env node
// Generates the Oberndörfer monogram pattern: a seamless square repeat in the
// spirit of an embossed damask, with the brand star-cross in place of the
// classic four-petal flower.
//
//   node design/monogram-pattern/generate.js
//
// Writes SVGs next to this file. Geometry lives in one 400×400 tile:
//   A  (corners + centre)      the logo inside a concave star frame
//   B  (edge midpoints)        small quatrefoil flower with leaves
//   M  (quarter points)        oval medallion filled with mirrored scrolls
// The frames of A, B and M share their tips, forming one continuous lattice.

const fs = require('fs');
const path = require('path');

const S = 400;
const f = (n) => +n.toFixed(2);
const pt = (p) => `${f(p[0])} ${f(p[1])}`;

// ---------- logo (traced from the 2000px reference, centre 999,900, R 745) ----------
function logoPath(R) {
  const k = R / 745;
  // first octant, top tip → notch on the diagonal
  const oct = [
    ['M', [0, -745]],
    ['L', [143, -528]],
    ['L', [345, -419]],
    ['Q', [199, -273], [148, -146]],
  ];
  const refl = ([x, y]) => [-y, -x]; // mirror across the top-right diagonal
  // second octant: walk back out from the notch to the right tip
  const oct2 = [
    ['Q', refl([199, -273]), refl([345, -419])],
    ['L', refl([143, -528])],
    ['L', refl([0, -745])],
  ];
  const quad = [...oct, ...oct2];
  const rot = ([x, y], n) => {
    for (let i = 0; i < n; i++) [x, y] = [-y, x];
    return [x, y];
  };
  let d = '';
  for (let q = 0; q < 4; q++) {
    for (const [cmd, ...ps] of quad) {
      if (cmd === 'M' && q > 0) continue;
      d += cmd + ps.map((p) => pt(rot(p, q).map((v) => v * k))).join(' ') + ' ';
    }
  }
  return d + 'Z';
}

// ---------- helpers ----------
// Closed outline around a centreline with a width that tapers from w0 to w1.
function taperedStroke(points, w0, w1) {
  const n = points.length;
  const left = [], right = [];
  for (let i = 0; i < n; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    tx /= len; ty /= len;
    const t = i / (n - 1);
    const w = (w0 + (w1 - w0) * Math.pow(t, 0.8)) / 2;
    left.push([points[i][0] - ty * w, points[i][1] + tx * w]);
    right.push([points[i][0] + ty * w, points[i][1] - tx * w]);
  }
  const all = [...left, ...right.reverse()];
  return 'M' + all.map(pt).join(' L') + ' Z';
}

// Spiral centreline: starts at angle a0 with radius r0, turns `sweep` radians
// (sign = direction) while the radius shrinks to r1.
function spiral(c, r0, r1, a0, sweep, n = 90) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const r = r0 * Math.pow(r1 / r0, t);
    const a = a0 + sweep * t;
    out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]);
  }
  return out;
}

const circle = (c, r) =>
  `M${f(c[0] - r)} ${f(c[1])} a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0 a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0 Z`;

// A C-scroll curling into a dot, in local coordinates (mirrored by callers).
function scroll(scale = 1) {
  const s = (p) => [p[0] * scale, p[1] * scale];
  const c = s([34, -14]);
  const pts = spiral(c, 28 * scale, 7 * scale, Math.PI * 1.02, Math.PI * 1.55);
  const end = pts[pts.length - 1];
  return [taperedStroke(pts, 6.5 * scale, 2.6 * scale), circle(end, 4.6 * scale)];
}

// A pointed leaf / drop from base to tip.
function leaf(base, tip, width) {
  const mx = (base[0] + tip[0]) / 2, my = (base[1] + tip[1]) / 2;
  const dx = tip[0] - base[0], dy = tip[1] - base[1];
  const len = Math.hypot(dx, dy);
  const nx = -dy / len, ny = dx / len;
  const c1 = [mx + nx * width - dx * 0.15, my + ny * width - dy * 0.15];
  const c2 = [mx - nx * width - dx * 0.15, my - ny * width - dy * 0.15];
  return `M${pt(base)} Q${pt(c1)} ${pt(tip)} Q${pt(c2)} ${pt(base)} Z`;
}

const T = (d, tx, ty, rot = 0, sx = 1, sy = 1) =>
  `<path transform="translate(${f(tx)} ${f(ty)}) rotate(${rot}) scale(${sx} ${sy})" d="${d}"/>`;

// ---------- lattice ----------
const TIP_A = 126; // star tips around each logo
const TIP_B = S / 2 - TIP_A; // the B star shares those tips

// Concave four-point star, tips at distance r, sides bowed in through `pull`.
function concaveStar(r, pull) {
  const tips = [[0, -r], [r, 0], [0, r], [-r, 0]];
  const ctrl = [[pull, -pull], [pull, pull], [-pull, pull], [-pull, -pull]];
  let d = `M${pt(tips[0])}`;
  for (let i = 0; i < 4; i++) d += ` Q${pt(ctrl[i])} ${pt(tips[(i + 1) % 4])}`;
  return d + ' Z';
}

// ---------- tile content ----------
function tileMotifs() {
  const logo = logoPath(68);
  const logoInner = logoPath(57);
  const [sc, sd] = scroll(1);
  const [ssc, ssd] = scroll(0.5);
  const lines = []; // stroked lattice
  const solids = []; // filled motifs
  const logos = [], logoLines = []; // the logo gets its own, deeper relief

  const A = [[0, 0], [S, 0], [0, S], [S, S], [S / 2, S / 2]];
  const B = [[S / 2, 0], [0, S / 2], [S, S / 2], [S / 2, S]];
  const M = [[S / 4, S / 4], [3 * S / 4, S / 4], [S / 4, 3 * S / 4], [3 * S / 4, 3 * S / 4]];

  // copies shifted by one tile in every direction so the repeat is seamless
  const shifts = [];
  for (const dx of [-S, 0, S]) for (const dy of [-S, 0, S]) shifts.push([dx, dy]);
  const each = (list, fn) => {
    const seen = new Set();
    for (const [x, y] of list)
      for (const [dx, dy] of shifts) {
        const X = x + dx, Y = y + dy;
        if (X < -S / 2 || X > S * 1.5 || Y < -S / 2 || Y > S * 1.5) continue;
        const key = X + ',' + Y;
        if (seen.has(key)) continue;
        seen.add(key);
        fn(X, Y);
      }
  };

  // A: logo in a double concave star
  each(A, (x, y) => {
    logos.push(T(logo, x, y));
    logoLines.push(T(logoInner, x, y));
    lines.push(T(concaveStar(TIP_A, 16), x, y));
    // a bead and a small drop in each arm of the star, pointing out
    for (const r of [0, 90, 180, 270]) {
      solids.push(T(circle([0, -TIP_A + 34], 3), x, y, r));
      solids.push(T(leaf([0, -TIP_A + 28], [0, -TIP_A + 10], 3.4), x, y, r));
    }
  });

  // B: quatrefoil flower, four leaves, four small scrolls
  each(B, (x, y) => {
    let flower = '';
    for (const r of [0, 90, 180, 270]) {
      const a = (r * Math.PI) / 180;
      flower += circle([Math.sin(a) * 8.5, -Math.cos(a) * 8.5], 7) + ' ';
    }
    solids.push(`<path transform="translate(${x} ${y})" fill-rule="nonzero" d="${flower}"/>`);
    lines.push(`<circle cx="${x}" cy="${y}" r="3.2" class="cut"/>`);
    for (const r of [45, 135, 225, 315]) solids.push(T(leaf([0, -19], [0, -36], 6), x, y, r));
    for (const r of [0, 90, 180, 270]) {
      solids.push(T(ssc, x, y, r, 1, 1) + T(ssd, x, y, r, 1, 1));
      solids.push(T(ssc, x, y, r, -1, 1) + T(ssd, x, y, r, -1, 1));
    }
    lines.push(T(concaveStar(TIP_B, 22), x, y));
  });

  // M: oval medallion with four mirrored scrolls, oriented across the A–A diagonal
  each(M, (x, y) => {
    // x+y parity decides which diagonal points at the logos
    const r = Math.round((x - S / 4) / (S / 2) + (y - S / 4) / (S / 2)) % 2 === 0 ? -45 : 45;
    lines.push(`<ellipse transform="translate(${x} ${y}) rotate(${r})" rx="86" ry="63"/>`);
    for (const [sx, sy] of [[1, 1], [-1, 1], [1, -1], [-1, -1]]) {
      solids.push(`<g transform="translate(${x} ${y}) rotate(${r}) scale(${1.2 * sx} ${1.2 * sy})"><path d="${sc}"/><path d="${sd}"/>` +
        `<g transform="translate(40 14) scale(-1 -1)"><path d="${ssc}"/><path d="${ssd}"/></g>` +
        `<path d="${leaf([56, 2], [67, 0], 3)}"/></g>`);
    }
    solids.push(T(leaf([0, 3], [0, 26], 6), x, y, r + 90));
    solids.push(T(leaf([0, 3], [0, 26], 6), x, y, r - 90));
    solids.push(T(circle([0, 0], 4), x, y));
  });

  return { lines, solids, logos, logoLines };
}

// ---------- documents ----------
function tileSVG({ bg, ink, emboss, stroke = 2.2, size = S }) {
  const { lines, solids, logos, logoLines } = tileMotifs();
  // raised relief: shadow down-right, light up-left; a sunk line swaps them
  const relief = (id, blur, dx, dy, lx, ly) => `<filter id="${id}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="${blur}" result="b"/>
      <feOffset in="b" dx="${dx}" dy="${dy}" result="so"/>
      <feFlood flood-color="${emboss.shadow}" flood-opacity="${emboss.shadowOpacity}"/>
      <feComposite in2="so" operator="in" result="shadow"/>
      <feOffset in="b" dx="${lx}" dy="${ly}" result="ho"/>
      <feFlood flood-color="${emboss.light}" flood-opacity="${emboss.lightOpacity}"/>
      <feComposite in2="ho" operator="in" result="light"/>
      <feMerge><feMergeNode in="shadow"/><feMergeNode in="light"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>`;
  const defs = emboss
    ? relief('emb', 1.1, 1.6, 1.8, -1.2, -1.2) +
      relief('embLogo', 1.4, 2.4, 2.6, -1.5, -1.5) +
      relief('sunk', 0.7, -1, -1, 1, 1)
    : '';
  const fx = (id) => (emboss ? `filter="url(#${id})"` : '');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${S} ${S}">
  <defs>${defs}</defs>
  <rect width="${S}" height="${S}" fill="${bg}"/>
  <g ${fx('emb')}>
    <g fill="none" stroke="${ink}" stroke-width="${stroke}" stroke-linejoin="round">${lines.join('')}</g>
    <g fill="${ink}" stroke="none">${solids.join('')}</g>
  </g>
  <g fill="${ink}" ${fx('embLogo')}>${logos.join('')}</g>
  <g fill="none" stroke="${bg}" stroke-width="${stroke * 0.9}" stroke-linejoin="miter" ${fx('sunk')}>${logoLines.join('')}</g>
  <style>.cut{fill:${bg};stroke:none}</style>
</svg>
`;
}

const variants = {
  'tile-line.svg': { bg: '#ffffff', ink: '#1a1a1a' },
  'tile-embossed-ivory.svg': {
    bg: '#e9e7e1', ink: '#e9e7e1',
    emboss: { shadow: '#6d6a60', shadowOpacity: 0.55, light: '#ffffff', lightOpacity: 0.95 },
  },
  'tile-embossed-cognac.svg': {
    bg: '#7a4a2a', ink: '#7a4a2a',
    emboss: { shadow: '#2a1509', shadowOpacity: 0.7, light: '#c79068', lightOpacity: 0.8 },
  },
  'tile-navy-gold.svg': { bg: '#1c2638', ink: '#c8a96a' },
};

const out = __dirname;
for (const [name, v] of Object.entries(variants)) fs.writeFileSync(path.join(out, name), tileSVG(v));
fs.writeFileSync(
  path.join(out, 'logo.svg'),
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -60 120 120"><path d="${logoPath(56)}" fill="#1a1a1a"/></svg>\n`,
);
console.log('wrote', Object.keys(variants).join(', '), 'logo.svg');
