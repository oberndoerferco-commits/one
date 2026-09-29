#!/usr/bin/env node
// Stamp-ready monogram patterns for the star-cross logo.
//
//   node design/stamp-pattern/generate.js
//
// All geometry is in millimetres at final size. One tile is 36 × 36 mm and
// repeats edge to edge. Logos sit on a diagonal grid (tile corners + centre).
// Stamping rules the artwork keeps to (see README): solid shapes only,
// lines ≥ 1 mm, gaps ≥ 1 mm, no gradients, no hairlines.

const fs = require('fs');
const path = require('path');

const T = 36; // tile size, mm
const LOGO_R = 7; // logo tip radius → 14 mm across
const f = (n) => +n.toFixed(3);

// Star-cross, traced from design/monogram-pattern/logo-reference.png
// (centre 999,900; tip radius 745 px). D4-symmetric, built from one octant.
function logoPath(R) {
  const k = R / 745;
  const P = (x, y) => [x * k, y * k];
  const refl = ([x, y]) => [-y, -x];
  const tip = P(0, -745), a = P(143, -528), b = P(345, -419), c = P(199, -273), n = P(148, -146);
  const rot = ([x, y], q) => { for (let i = 0; i < q; i++) [x, y] = [-y, x]; return [x, y]; };
  const s = (p, q) => rot(p, q).map(f).join(' ');
  let d = '';
  for (let q = 0; q < 4; q++) {
    d += `${q ? 'L' : 'M'}${s(tip, q)} L${s(a, q)} L${s(b, q)} Q${s(c, q)} ${s(n, q)} `;
    d += `Q${s(refl(c), q)} ${s(refl(b), q)} L${s(refl(a), q)} `;
  }
  return d + 'Z';
}

// Small concave four-point spark, echoing the logo's notches.
function spark(r, pull = 0.18) {
  const p = r * pull;
  return `M0 ${-r} Q${p} ${-p} ${r} 0 Q${p} ${p} 0 ${r} Q${-p} ${p} ${-r} 0 Q${-p} ${-p} 0 ${-r} Z`;
}

const at = (x, y, d, extra = '') => `<path transform="translate(${f(x)} ${f(y)})" d="${d}"${extra}/>`;

// Every motif is placed at its grid points plus copies one tile away so the
// artwork continues across the tile edges.
function around(points, fn) {
  const out = [];
  for (const [x, y] of points)
    for (const dx of [-T, 0, T])
      for (const dy of [-T, 0, T]) {
        const X = x + dx, Y = y + dy;
        if (X < -T / 2 || X > T * 1.5 || Y < -T / 2 || Y > T * 1.5) continue;
        out.push(fn(X, Y));
      }
  return out;
}

const LOGOS = [[0, 0], [T / 2, T / 2]];
const BETWEEN = [[T / 2, 0], [0, T / 2]];
const logo = logoPath(LOGO_R);

// ---------- the three patterns ----------
const patterns = {
  // Quiet, sparse: logo + small spark on a diagonal grid.
  signature: {
    title: 'Signature',
    note: 'Logo and a small spark on a diagonal grid. Most open, easiest to stamp.',
    art: () => [
      ...around(LOGOS, (x, y) => at(x, y, logo)),
      ...around(BETWEEN, (x, y) => at(x, y, spark(2.6))),
    ],
  },
  // Tone-on-tone: rows alternate solid and outlined logo.
  tonal: {
    title: 'Tonal',
    note: 'Solid and outlined logos alternate, with a spark between them. Richer, still clean.',
    art: () => [
      ...around([[0, 0]], (x, y) => at(x, y, logo)),
      ...around([[T / 2, T / 2]], (x, y) =>
        at(x, y, logoPath(LOGO_R + 0.5), ' fill="none" stroke="currentColor" stroke-width="1" stroke-linejoin="miter" stroke-miterlimit="10"')),
      ...around(BETWEEN, (x, y) => at(x, y, spark(2.2))),
    ],
  },
  // Heritage canvas: diamond trellis, logo in every cell, stud at crossings.
  trellis: {
    title: 'Trellis',
    note: 'A 1 mm diamond trellis with the logo in every cell and a stud at each crossing.',
    art: () => {
      const lines = [];
      const gap = 2.8; // trellis stops short of each stud
      // lines x + y = T/2 + kT and x − y = T/2 + kT, cut into segments between studs
      for (let k = -2; k <= 2; k++) {
        const c = T / 2 + k * T;
        for (let i = -3; i <= 3; i++) {
          // studs sit where the two line families cross; draw the segment between two
          const x0 = (c + T / 2) / 2 + (i * T) / 2, x1 = x0 + T / 2;
          const d = gap / Math.SQRT2;
          lines.push(`M${f(x0 + d)} ${f(c - x0 - d)} L${f(x1 - d)} ${f(c - x1 + d)}`); // x + y = c
          lines.push(`M${f(x0 + d)} ${f(x0 + d - c)} L${f(x1 - d)} ${f(x1 - d - c)}`); // x − y = c
        }
      }
      return [
        `<path d="${lines.join(' ')}" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>`,
        ...around(LOGOS, (x, y) => at(x, y, logo)),
        ...around(BETWEEN, (x, y) => `<circle cx="${f(x)}" cy="${f(y)}" r="1.5"/>`),
      ];
    },
  },
};

// ---------- output ----------
const out = __dirname;
const svg = (w, h, body, extraDefs = '') =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}mm" height="${h}mm" viewBox="0 0 ${w} ${h}">\n${extraDefs}${body}\n</svg>\n`;

for (const [key, p] of Object.entries(patterns)) {
  const art = p.art().join('\n  ');
  // 1. production tile: pure black artwork, one repeat, for the plate maker
  fs.writeFileSync(path.join(out, `${key}-tile.svg`),
    svg(T, T, `<g fill="#000" color="#000">\n  ${art}\n</g>`, `<clipPath id="c"><rect width="${T}" height="${T}"/></clipPath>\n`)
      .replace('<g fill', '<g clip-path="url(#c)" fill'));
  // 2. sheet: 6 × 4 repeats (216 × 144 mm) as one seamless vector
  const pat = `<defs><pattern id="p" width="${T}" height="${T}" patternUnits="userSpaceOnUse"><g fill="#000" color="#000">${art}</g></pattern></defs>\n`;
  fs.writeFileSync(path.join(out, `${key}-sheet-216x144mm.svg`),
    svg(6 * T, 4 * T, `<rect width="${6 * T}" height="${4 * T}" fill="url(#p)"/>`, pat));
}
fs.writeFileSync(path.join(out, 'logo.svg'),
  svg(2 * LOGO_R + 2, 2 * LOGO_R + 2, `<path transform="translate(${LOGO_R + 1} ${LOGO_R + 1})" d="${logo}"/>`));

// 3. preview page: each pattern stamped into leather (for review only)
const leathers = [
  ['Cognac', '#8a5634'],
  ['Black', '#26221f'],
  ['Taupe', '#9d8c7b'],
];
const scale = 7; // px per mm in the preview
const swatch = (key, [name, colour], i) => {
  const art = patterns[key].art().join('');
  const id = `${key}${i}`;
  return `<figure>
  <svg width="${scale * 72}" height="${scale * 72}" viewBox="0 0 72 72">
    <defs>
      <filter id="grain${id}" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="3" seed="${i + 3}"/>
        <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.22 0"/>
        <feComposite in2="SourceGraphic" operator="in"/>
        <feBlend in="SourceGraphic" mode="multiply"/>
      </filter>
      <filter id="press${id}" filterUnits="userSpaceOnUse" x="-5" y="-5" width="82" height="82">
        <feOffset in="SourceAlpha" dx="-0.18" dy="-0.18" result="o"/>
        <feComposite in="SourceAlpha" in2="o" operator="out" result="rim"/>
        <feFlood flood-color="#fff" flood-opacity="0.9"/><feComposite in2="rim" operator="in" result="light"/>
        <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="light"/></feMerge>
      </filter>
      <g id="a${id}">${art}</g>
      <clipPath id="c${id}"><rect width="72" height="72"/></clipPath>
    </defs>
    <rect width="72" height="72" fill="${colour}" filter="url(#grain${id})"/>
    <g clip-path="url(#c${id})" opacity="0.3"><g fill="#000" color="#000" filter="url(#press${id})">
      ${[-T, 0, T, 2 * T].flatMap((x) => [-T, 0, T, 2 * T].map((y) => `<use href="#a${id}" x="${x + 9}" y="${y + 9}"/>`)).join('')}
    </g></g>
  </svg>
  <figcaption>${patterns[key].title} · ${name}</figcaption>
</figure>`;
};
const rows = Object.keys(patterns).map((key) => `<section>
  <h2>${patterns[key].title}</h2><p>${patterns[key].note}</p>
  <div class="row">${leathers.map((l, i) => swatch(key, l, i)).join('\n')}</div>
</section>`).join('\n');
fs.writeFileSync(path.join(out, 'preview.html'), `<!doctype html><meta charset="utf-8">
<style>
  body{margin:0;padding:32px;background:#f4f1ec;font:15px/1.4 Georgia,serif;color:#2b2622}
  h2{margin:24px 0 2px;font-weight:normal;font-size:22px} p{margin:0 0 12px;color:#6b625a}
  .row{display:flex;gap:20px} figure{margin:0} figcaption{font-size:13px;color:#6b625a;margin-top:6px}
  svg{display:block;border-radius:4px}
</style>
<body>${rows}</body>
`);
console.log('wrote', Object.keys(patterns).map((k) => `${k}-tile.svg, ${k}-sheet-216x144mm.svg`).join(', '), 'logo.svg, preview.html');
