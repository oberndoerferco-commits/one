#!/usr/bin/env node
// Tote-bag mockup with the Signature pattern stamped at true scale.
//
//   node design/stamp-pattern/generate.js   (first, to refresh the tile)
//   node design/stamp-pattern/mockup.js
//
// Writes mockup-signature-tote.html (render it in a browser or screenshot it).
// Units are millimetres: the bag is 340 mm wide at the base and 280 mm tall,
// so the 36 mm repeat and 14 mm logo appear at their real size on the bag.

const fs = require('fs');
const path = require('path');

// usage: node mockup.js [tile.svg] [repeat mm] [name]
const tileFile = process.argv[2] || path.join(__dirname, 'signature-tile.svg');
const T = +(process.argv[3] || 36);
const name = process.argv[4] || 'signature';
const tile = fs.readFileSync(tileFile, 'utf8');
const art = tile.slice(tile.indexOf('>', tile.indexOf('<g clip-path')) + 1, tile.lastIndexOf('</g>'))
  .replace(/<style>[^<]*<\/style>/g, '')
  .replace(/ class="cut"/g, ' fill="#fff" fill-opacity="0"'); // holes: leave leather unpressed (approx.)
const title = name[0].toUpperCase() + name.slice(1);

// bag geometry (mm), front view, centred on x = 0
const W_TOP = 300, W_BOT = 340, H = 280, TOP = 0;
const body = `M${-W_TOP / 2} ${TOP} L${W_TOP / 2} ${TOP} L${W_BOT / 2} ${H - 14}
  Q${W_BOT / 2} ${H} ${W_BOT / 2 - 14} ${H} L${-W_BOT / 2 + 14} ${H} Q${-W_BOT / 2} ${H} ${-W_BOT / 2} ${H - 14} Z`;

function bag(id, { leather, trim, hardware, pressOpacity, rim }) {
  const uses = [];
  // centre the grid so a logo column runs down the middle of the bag
  for (let x = -Math.ceil(240 / T) * T; x <= 240; x += T)
    for (let y = -T; y <= 320; y += T) uses.push(`<use href="#art" x="${x}" y="${y + 20}"/>`);
  const handle = (x) => `
    <path d="M${x - 44} 6 C${x - 44} -150 ${x + 44} -150 ${x + 44} 6" fill="none" stroke="${trim}" stroke-width="15" stroke-linecap="round"/>
    <path d="M${x - 44} 6 C${x - 44} -150 ${x + 44} -150 ${x + 44} 6" fill="none" stroke="#fff" stroke-opacity=".10" stroke-width="3" transform="translate(-3 -2)"/>
    <path d="M${x - 44} 2 C${x - 44} -146 ${x + 44} -146 ${x + 44} 2" fill="none" stroke="#000" stroke-opacity=".35" stroke-width=".6" stroke-dasharray="3 2"/>`;
  const tab = (x) => `
    <rect x="${x - 11}" y="-4" width="22" height="42" rx="3" fill="${trim}"/>
    <rect x="${x - 8.5}" y="-1.5" width="17" height="37" rx="2" fill="none" stroke="#000" stroke-opacity=".35" stroke-width=".6" stroke-dasharray="3 2"/>
    <circle cx="${x}" cy="27" r="4.2" fill="url(#metal${id})"/><circle cx="${x}" cy="27" r="4.2" fill="none" stroke="#000" stroke-opacity=".3" stroke-width=".5"/>`;
  return `
  <defs>
    <clipPath id="clip${id}"><path d="${body}"/></clipPath>
    <linearGradient id="light${id}" x1="0" x2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset=".18" stop-color="#000" stop-opacity=".05"/>
      <stop offset=".42" stop-color="#fff" stop-opacity=".10"/><stop offset=".62" stop-color="#fff" stop-opacity=".03"/>
      <stop offset=".86" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".42"/>
    </linearGradient>
    <linearGradient id="vert${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".18"/><stop offset=".12" stop-color="#000" stop-opacity="0"/>
      <stop offset=".85" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/>
    </linearGradient>
    <radialGradient id="metal${id}" cx=".35" cy=".35" r=".8">
      <stop offset="0" stop-color="#fff6d8"/><stop offset=".45" stop-color="${hardware}"/><stop offset="1" stop-color="#5a4520"/>
    </radialGradient>
    <filter id="grain${id}" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="4"/>
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .28 0"/>
      <feComposite in2="SourceGraphic" operator="in"/>
      <feBlend in="SourceGraphic" mode="multiply"/>
    </filter>
    <filter id="press${id}" filterUnits="userSpaceOnUse" x="-200" y="-20" width="400" height="320">
      <feOffset in="SourceAlpha" dx="-.35" dy="-.35" result="o"/>
      <feComposite in="SourceAlpha" in2="o" operator="out" result="edge"/>
      <feFlood flood-color="#fff" flood-opacity="${rim}"/><feComposite in2="edge" operator="in" result="light"/>
      <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="light"/></feMerge>
    </filter>
  </defs>
  ${handle(-78)}${handle(78)}
  <path d="${body}" fill="${leather}" filter="url(#grain${id})"/>
  <g clip-path="url(#clip${id})">
    <g opacity="${pressOpacity}" fill="#000" filter="url(#press${id})">${uses.join('')}</g>
    <path d="${body}" fill="url(#light${id})"/>
    <path d="${body}" fill="url(#vert${id})"/>
    <!-- top band in smooth trim leather, with stitching -->
    <rect x="-200" y="${TOP}" width="400" height="18" fill="${trim}"/>
    <rect x="-200" y="${TOP}" width="400" height="18" fill="url(#light${id})"/>
    <line x1="-200" x2="200" y1="14" y2="14" stroke="#000" stroke-opacity=".35" stroke-width=".6" stroke-dasharray="3 2"/>
    <!-- base band -->
    <path d="M-200 ${H - 22} H200 V${H + 5} H-200 Z" fill="${trim}"/>
    <path d="M-200 ${H - 22} H200 V${H + 5} H-200 Z" fill="url(#light${id})"/>
    <line x1="-200" x2="200" y1="${H - 18}" y2="${H - 18}" stroke="#000" stroke-opacity=".35" stroke-width=".6" stroke-dasharray="3 2"/>
  </g>
  <!-- side piping -->
  <path d="M${-W_TOP / 2} ${TOP} L${-W_BOT / 2} ${H - 14}" stroke="${trim}" stroke-width="3"/>
  <path d="M${W_TOP / 2} ${TOP} L${W_BOT / 2} ${H - 14}" stroke="${trim}" stroke-width="3"/>
  ${tab(-122)}${tab(-34)}${tab(34)}${tab(122)}`;
}

const scene = (id, opts, label) => `
<figure>
  <svg viewBox="-230 -175 460 500" width="560" height="609">
    <defs>
      <radialGradient id="floor${id}" cx=".5" cy=".5" r=".5">
        <stop offset="0" stop-color="#000" stop-opacity=".32"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <ellipse cx="0" cy="${H + 6}" rx="210" ry="16" fill="url(#floor${id})"/>
    ${bag(id, opts)}
  </svg>
  <figcaption>${label}</figcaption>
</figure>`;

const html = `<!doctype html><meta charset="utf-8"><title>${title} tote</title>
<style>
  body{margin:0;padding:36px 40px;background:linear-gradient(#efe9e1,#e4dcd1);font:15px/1.4 Georgia,serif;color:#2b2622}
  h1{font-weight:normal;font-size:26px;margin:0 0 4px} p{margin:0 0 18px;color:#6b625a}
  .row{display:flex;gap:28px} figure{margin:0} figcaption{text-align:center;color:#6b625a;font-size:14px}
</style>
<svg width="0" height="0" style="position:absolute"><defs><g id="art">${art}</g></defs></svg>
<h1>${title} · tote</h1>
<p>Blind-stamped pattern at true size (${T} mm repeat). Smooth leather trim, brass rivets.</p>
<div class="row">
${scene('c', { leather: '#8a5634', trim: '#4a2a17', hardware: '#c9a258', pressOpacity: 0.28, rim: 0.35 }, 'Cognac with espresso trim')}
${scene('k', { leather: '#26221f', trim: '#141210', hardware: '#c9a258', pressOpacity: 0.55, rim: 0.22 }, 'Black on black')}
</div>
`;
fs.writeFileSync(path.join(path.dirname(tileFile), `mockup-${name}-tote.html`), html);
console.log(`wrote mockup-${name}-tote.html`);
