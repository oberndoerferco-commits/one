#!/usr/bin/env node
// Renders damask-v2-preview.html: the pattern blind-embossed white on white,
// like the reference photo, and flat black line art. Review only, not artwork.
const fs = require('fs');
const path = require('path');
const tile = fs.readFileSync(path.join(__dirname, 'damask-v2-tile.svg'), 'utf8');
const T = +tile.match(/viewBox="0 0 ([\d.]+)/)[1];
const art = tile.slice(tile.indexOf('>', tile.indexOf('<g clip-path')) + 1, tile.lastIndexOf('</g>'));
const view = (ink, bg, emboss) => {
  const uses = [];
  for (let x = -1; x <= 2; x++) for (let y = -1; y <= 2; y++) uses.push(`<use href="#t${emboss ? 1 : 0}" x="${x * T - T / 4}" y="${y * T - T / 4}"/>`);
  return `<svg width="720" height="720" viewBox="0 0 ${1.5 * T} ${1.5 * T}">
  <defs>
    <g id="t${emboss ? 1 : 0}">${art.replace(/fill="#000" color="#000"/, `fill="${ink}" color="${ink}"`).replace(/\.cut\{fill:#fff\}/, `.cut{fill:${bg}}`)}</g>
    <filter id="e${emboss ? 1 : 0}" filterUnits="userSpaceOnUse" x="0" y="0" width="${1.5 * T}" height="${1.5 * T}">
      <feGaussianBlur in="SourceAlpha" stdDeviation=".22" result="b"/>
      <feOffset in="b" dx=".3" dy=".35" result="so"/><feFlood flood-color="#6d6a60" flood-opacity=".6"/><feComposite in2="so" operator="in" result="s"/>
      <feOffset in="b" dx="-.25" dy="-.25" result="ho"/><feFlood flood-color="#fff"/><feComposite in2="ho" operator="in" result="h"/>
      <feMerge><feMergeNode in="s"/><feMergeNode in="h"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="${bg}"/>
  <g ${emboss ? 'filter="url(#e1)"' : ''}>${uses.join('')}</g>
</svg>`;
};
fs.writeFileSync(path.join(__dirname, 'damask-v2-preview.html'), `<!doctype html><meta charset="utf-8">
<body style="margin:0;padding:24px;background:#f4f1ec;display:flex;gap:24px">
${view('#e7e5df', '#e7e5df', true)}
${view('#000', '#fff', false)}
</body>`);
console.log('wrote damask-v2-preview.html');
