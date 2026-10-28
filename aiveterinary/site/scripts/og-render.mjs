// Share-image renderer for article and animal pages (1200×630 PNG), used by the build endpoint
// src/pages/og/[lang]/[slug].png.ts. Layout with satori (text is laid out with the real Fraunces and
// Plus Jakarta Sans metrics and drawn as vector paths), rasterised with resvg, so text stays crisp and
// accents and umlauts come from the fonts' latin and latin-ext subsets.
//
// Colours are read from the site's own light theme in src/styles.css (the :root tokens and the
// .tint-* card tints), the mark from public/logo-mark.svg. Results are cached in
// node_modules/.cache/og-cards by a hash of everything that goes into a card (card data, layout code,
// colours, mark and font files), so a rebuild only renders cards whose inputs changed.
//
// Rendering runs in worker threads (scripts/og-worker.mjs): satori and resvg are CPU-bound, and a pool
// of one worker per core keeps ~500 cards to seconds instead of a minute.
import { readFileSync, writeFileSync, mkdirSync, existsSync, renameSync } from 'node:fs';
import { threadId } from 'node:worker_threads';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { availableParallelism } from 'node:os';

const ROOT = process.cwd();
const require = createRequire(join(ROOT, 'package.json'));
const CACHE = join(ROOT, 'node_modules/.cache/og-cards');

// ---------------------------------------------------------------------------------------------------
// Inputs shared by every card.
const FONT_FILES = [
  ['Fraunces', 600, 'normal', '@fontsource/fraunces/files/fraunces-latin-600-normal.woff'],
  ['Fraunces', 600, 'normal', '@fontsource/fraunces/files/fraunces-latin-ext-600-normal.woff'],
  ['Fraunces', 400, 'italic', '@fontsource/fraunces/files/fraunces-latin-400-italic.woff'],
  ['Fraunces', 400, 'italic', '@fontsource/fraunces/files/fraunces-latin-ext-400-italic.woff'],
  ['Jakarta', 500, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-500-normal.woff'],
  ['Jakarta', 500, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-ext-500-normal.woff'],
  ['Jakarta', 700, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-normal.woff'],
  ['Jakarta', 700, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-ext-700-normal.woff'],
  ['Jakarta', 800, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-800-normal.woff'],
  ['Jakarta', 800, 'normal', '@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-ext-800-normal.woff'],
];

/** Light-theme tokens (--name → value) and card tints (key → colour) from src/styles.css. */
function theme() {
  const css = readFileSync(join(ROOT, 'src/styles.css'), 'utf8');
  const root = /:root\s*\{([^}]*)\}/.exec(css)?.[1] ?? '';
  const vars = Object.fromEntries([...root.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
  const tints = {};
  for (const m of css.matchAll(/\.tint-([\w-]+)\s*\{\s*--tint:\s*(#[0-9a-f]+)/gi)) tints[m[1]] = m[2];
  return { vars, tints };
}

let shared;
/** Fonts, colours and the mark, read once per process; `hash` changes when any of them does. */
export function inputs() {
  if (shared) return shared;
  const h = createHash('sha256');
  const fonts = FONT_FILES.map(([name, weight, style, spec]) => {
    const data = readFileSync(require.resolve(spec));
    h.update(spec).update(data);
    return { name, weight, style, data };
  });
  const { vars, tints } = theme();
  const mark = readFileSync(join(ROOT, 'public/logo-mark.svg'), 'utf8').replace(/<title>.*?<\/title>/, '');
  h.update(JSON.stringify(vars)).update(JSON.stringify(tints)).update(mark).update(layout.toString()).update(svgOf.toString()).update(heading.toString()).update(JSON.stringify(SIZES)).update(renderCard.toString());
  h.update(require('satori/package.json').version).update(require('@resvg/resvg-js/package.json').version);
  shared = { fonts, vars, tints, mark, hash: h.digest('hex') };
  return shared;
}

// ---------------------------------------------------------------------------------------------------
// Layout.
const el = (type, style, ...children) => ({ type, props: { style: { display: 'flex', ...style }, children: children.flat().filter((c) => c !== null && c !== false && c !== undefined) } });
const img = (src, w, h, style = {}) => ({ type: 'img', props: { src, width: w, height: h, style } });
const uri = (svg) => `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`;

/** An SVG with the site's CSS variables resolved (resvg has no CSS custom properties). */
function svgOf(markup, vars) {
  return markup.replace(/var\((--[\w-]+)\)/g, (m, v) => vars[v] ?? '#000');
}

const COL = 732; // text column: 1200 − 2 × 64 padding − 300 art − 40 gap

/** The title (article) or name (animal) in Fraunces, at `size`, clamped to `lines` lines (0: unclamped). */
function heading(text, size, lines, color) {
  return { type: 'div', props: { style: { display: 'block', width: COL, fontFamily: 'Fraunces', fontWeight: 600, fontSize: size, lineHeight: 1.08, letterSpacing: '-0.02em', color, wordBreak: 'break-word', ...(lines ? { lineClamp: lines } : {}) }, children: text } };
}
// Sizes tried from the largest down; the first at which the heading fits its lines wins.
const SIZES = { article: [[70, 3], [62, 3], [54, 3], [48, 3], [43, 3], [38, 3]], animal: [[104, 2], [88, 2], [72, 2], [60, 2]] };

const VERDICT = { emergency: ['--danger', '!'], today: ['--warn', '!'], 'this-week': ['--accent', '·'], routine: ['--ok', 'i'] };

/**
 * The card as a satori tree. `c`:
 *   kind 'article': title, urgency, verdict (localized label), icon (inner SVG on the 48 grid), tint, status
 *   kind 'animal':  name, scientific?, eyebrow?, icon, tint, status
 */
function layout(c, { vars, tints, mark }, size) {
  const v = (k) => vars[k];
  const tint = tints[c.tint] ?? tints.general ?? '#e6f1ef';
  const brand = el('div', { alignItems: 'center', gap: 16 },
    img(uri(mark), 56, 56),
    el('div', { fontFamily: 'Jakarta', fontWeight: 700, fontSize: 30, color: v('--ink'), letterSpacing: '-0.01em' }, 'AI Veterinary'));
  const icon = uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="${v('--art-ink')}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${svgOf(c.icon, vars)}</svg>`);
  const art = el('div', { width: 300, height: 300, borderRadius: 150, background: tint, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
    img(icon, 236, 236));
  const footer = el('div', { justifyContent: 'space-between', alignItems: 'center', fontFamily: 'Jakarta', fontWeight: 500, fontSize: 22, color: v('--ink-3') },
    el('div', {}, c.status),
    el('div', { fontWeight: 700 }, 'aiveterinary.org'));

  if (c.kind === 'article') {
    const [col, mk] = VERDICT[c.urgency] ?? VERDICT['this-week'];
    const label = c.verdict.toUpperCase();
    // The longest labels (IT/DE "watch and ask") stay on one line beside the mark.
    const pill = label.length <= 22 ? 30 : label.length <= 32 ? 26 : 23;
    return el('div', { width: 1200, height: 630, padding: '52px 64px 44px', flexDirection: 'column', background: v('--bg'), fontFamily: 'Jakarta' },
      brand,
      el('div', { flexGrow: 1, alignItems: 'center', gap: 40 },
        el('div', { flexDirection: 'column', flexShrink: 0, width: COL, gap: 30 },
          heading(c.title, size, 3, v('--ink')),
          el('div', { alignSelf: 'flex-start', alignItems: 'center', gap: 16, background: v(col), color: v('--surface'), borderRadius: 999, padding: `14px 30px 14px 16px` },
            el('div', { width: 44, height: 44, borderRadius: 22, background: v('--surface'), color: v(col), alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 28 },
              mk === '·' ? el('div', { width: 12, height: 12, borderRadius: 6, background: v(col) }) : mk),
            el('div', { fontWeight: 800, fontSize: pill, letterSpacing: '0.05em', whiteSpace: 'nowrap' }, label))),
        art),
      footer);
  }
  return el('div', { width: 1200, height: 630, padding: '52px 64px 44px', flexDirection: 'column', background: v('--bg'), fontFamily: 'Jakarta' },
    brand,
    el('div', { flexGrow: 1, alignItems: 'center', gap: 40 },
      el('div', { flexDirection: 'column', flexShrink: 0, width: COL },
        c.eyebrow ? el('div', { fontWeight: 700, fontSize: 26, letterSpacing: '0.08em', color: v('--accent'), marginBottom: 14 }, c.eyebrow.toUpperCase()) : null,
        heading(c.name, size, 2, v('--ink')),
        c.scientific ? el('div', { fontFamily: 'Fraunces', fontStyle: 'italic', fontWeight: 400, fontSize: 40, color: v('--ink-2'), marginTop: 16 }, c.scientific) : null),
      art),
    footer);
}

// ---------------------------------------------------------------------------------------------------
// Rendering (called in the workers).
let satori, Resvg;
export async function renderCard(card) {
  satori ??= (await import('satori')).default;
  Resvg ??= (await import('@resvg/resvg-js')).Resvg;
  const inp = inputs();
  // Fit the heading: lay it out alone (satori sizes the height to the content) and count its lines.
  const text = card.kind === 'article' ? card.title : card.name;
  const sizes = SIZES[card.kind === 'article' ? 'article' : 'animal'];
  const fits = async (t, s, lines) => {
    const probe = await satori(heading(t, s, 0, '#000'), { width: COL, fonts: inp.fonts });
    return Math.round(Number(/height="([\d.]+)"/.exec(probe)?.[1] ?? Infinity) / (s * 1.08)) <= lines;
  };
  let fit = null;
  for (const [s, lines] of sizes) if (await fits(text, s, lines)) { fit = { size: s, text }; break; }
  // Longer than the smallest size holds: cut at a word, with an ellipsis (satori's clamp cuts mid-word).
  if (!fit) {
    const [s, lines] = sizes.at(-1);
    const words = text.split(' ');
    while (words.length > 1 && !(await fits(`${words.join(' ')}…`, s, lines))) words.pop();
    fit = { size: s, text: `${words.join(' ').replace(/[\s,;:–-]+$/, '')}…` };
  }
  const c = card.kind === 'article' ? { ...card, title: fit.text } : { ...card, name: fit.text };
  const svg = await satori(layout(c, inp, fit.size), { width: 1200, height: 630, fonts: inp.fonts });
  return new Resvg(svg, { fitTo: { mode: 'width', value: 1200 }, font: { loadSystemFonts: false } }).render().asPng();
}

export const keyOf = (card) => createHash('sha256').update(inputs().hash).update(JSON.stringify(card)).digest('hex').slice(0, 32);

// ---------------------------------------------------------------------------------------------------
// Batch with cache and a worker pool (called once per build from the endpoint).
/**
 * Renders every card that is not cached yet. Returns Map id → cache file path.
 * `cards`: Map id → card data.
 */
export async function renderAll(cards) {
  mkdirSync(CACHE, { recursive: true });
  const out = new Map();
  const todo = [];
  for (const [id, card] of cards) {
    const file = join(CACHE, `${keyOf(card)}.png`);
    out.set(id, file);
    if (!existsSync(file)) todo.push({ file, card });
  }
  const t0 = Date.now();
  if (todo.length) {
    const { Worker } = await import('node:worker_threads');
    const n = Math.max(1, Math.min(availableParallelism(), todo.length, Number(process.env.OG_WORKERS) || 8));
    const chunks = Array.from({ length: n }, (_, i) => todo.filter((_, j) => j % n === i));
    await Promise.all(chunks.map((jobs) => new Promise((resolve, reject) => {
      const w = new Worker(join(ROOT, 'scripts/og-worker.mjs'), { workerData: jobs });
      w.once('message', resolve);
      w.once('error', reject);
      w.once('exit', (code) => code && reject(new Error(`og worker exited with ${code}`)));
    })));
  }
  return { files: out, rendered: todo.length, cached: cards.size - todo.length, ms: Date.now() - t0 };
}

/** Writes one card straight to a file (used by the worker). */
export async function renderTo(card, file) {
  // Write then rename, so an interrupted build never leaves a half-written file in the cache.
  const tmp = `${file}.${process.pid}.${threadId}.tmp`;
  writeFileSync(tmp, await renderCard(card));
  renameSync(tmp, file);
}
