#!/usr/bin/env node
// Writes preview-<style>.html: 1.5 × 1.5 repeats embossed white on white
// (like the reference photo). Screenshot each to compare. Review only.
const fs = require('fs');
const path = require('path');
const { tileArt } = require('./generate.js');
const S = 1000, bg = '#e7e5df';
for (const style of ['solid', 'outline']) {
  const art = tileArt(style);
  const uses = [];
  for (let x = -1; x <= 2; x++) for (let y = -1; y <= 2; y++) uses.push(`<use href="#t" x="${x * S - S / 4}" y="${y * S - S / 4}"/>`);
  fs.writeFileSync(path.join(__dirname, `preview-${style}.html`), `<!doctype html><body style="margin:0">
<svg width="900" height="900" viewBox="0 0 ${1.5 * S} ${1.5 * S}">
  <defs>
    <g id="t"><g fill="${bg}" color="${bg}"><style>.cut{fill:${bg}}.cutline{stroke:${bg}}</style>${art}</g></g>
    <filter id="e" filterUnits="userSpaceOnUse" x="0" y="0" width="${1.5 * S}" height="${1.5 * S}">
      <feGaussianBlur in="SourceAlpha" stdDeviation="1.8" result="b"/>
      <feOffset in="b" dx="2.6" dy="3" result="so"/><feFlood flood-color="#5f5c53" flood-opacity=".7"/><feComposite in2="so" operator="in" result="s"/>
      <feOffset in="b" dx="-2" dy="-2" result="ho"/><feFlood flood-color="#fff"/><feComposite in2="ho" operator="in" result="h"/>
      <feMerge><feMergeNode in="s"/><feMergeNode in="h"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="${bg}"/>
  <g filter="url(#e)">${uses.join('')}</g>
</svg></body>`);
}
console.log('wrote preview-solid.html, preview-outline.html');
