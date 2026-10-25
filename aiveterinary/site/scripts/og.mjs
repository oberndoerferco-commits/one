// Renders the social share images (public/og.png, og-it.png, og-de.png) with the site's own
// styles, the logo mark (public/logo-mark.svg) and the dog-and-cat illustration. Run with the
// preview server up:
//   npx astro preview &  node scripts/og.mjs
// Needs Playwright with a Chromium; PLAYWRIGHT_MODULE and CHROMIUM override the defaults.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const pw = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright');
const chromium = pw.chromium ?? pw.default.chromium;
const base = process.env.BASE_URL ?? 'http://localhost:4321';
const out = (f) => fileURLToPath(new URL(`../public/${f}`, import.meta.url));

// The mark, inline at 44 px, from the same file the site serves.
const mark = readFileSync(out('logo-mark.svg'), 'utf8')
  .replace(/<title>.*?<\/title>/, '')
  .replace(' role="img"', ' aria-hidden="true"')
  .replace(/width="\d+" height="\d+"/, 'width="44" height="44"');

// The dog and cat from src/components/HeroScene.astro (no page shows it since the home redesign,
// so the scene is drawn here); colours come from the site's CSS variables.
const eye = (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#fff"/><circle cx="${x + r * 0.12}" cy="${y + r * 0.12}" r="${r * 0.72}" fill="var(--art-ink)" stroke="none"/><circle cx="${x - r * 0.22}" cy="${y - r * 0.25}" r="${r * 0.26}" fill="#fff" stroke="none"/>`;
const sparkle = (x, y, s) => `<path d="M${x} ${y - s}C${x + s * 0.18} ${y - s * 0.18} ${x + s * 0.18} ${y - s * 0.18} ${x + s} ${y}C${x + s * 0.18} ${y + s * 0.18} ${x + s * 0.18} ${y + s * 0.18} ${x} ${y + s}C${x - s * 0.18} ${y + s * 0.18} ${x - s * 0.18} ${y + s * 0.18} ${x - s} ${y}C${x - s * 0.18} ${y - s * 0.18} ${x - s * 0.18} ${y - s * 0.18} ${x} ${y - s}Z" fill="var(--warm)" stroke="none"/>`;
const art = `<svg width="470" viewBox="60 50 420 330" fill="none" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M88 238C70 150 140 70 246 66c104-4 196 52 200 150 4 92-60 140-120 146H130C96 356 98 290 88 238Z" fill="var(--hs-blob)" stroke="none"/>
<circle cx="404" cy="96" r="24" fill="var(--ic-sun)" stroke="none"/>
${sparkle(120, 92, 11)}${sparkle(452, 168, 8)}${sparkle(96, 300, 7)}
<ellipse cx="292" cy="352" rx="178" ry="11" fill="var(--art-ink)" opacity=".08" stroke="none"/>
<path d="M276 330c38 6 62-14 58-52" stroke="var(--art-ink)" stroke-width="20"/><path d="M276 330c38 6 62-14 58-52" stroke="var(--hs-dog)" stroke-width="14"/>
<path d="M178 206c-26 34-36 94-28 144h140c8-50-2-110-28-144z" fill="var(--hs-dog)"/>
<path d="M220 222c-24 0-36 34-30 74 4 24 16 36 30 36s26-12 30-36c6-40-6-74-30-74z" fill="var(--hs-cream)" stroke="none"/>
<rect x="182" y="286" width="28" height="66" rx="14" fill="var(--hs-dog)"/>
<rect x="230" y="286" width="28" height="66" rx="14" fill="var(--hs-dog)"/>
<path d="M188 340h16M236 340h16" stroke-width="2.4"/>
<circle cx="220" cy="156" r="64" fill="var(--hs-dog)"/>
<path d="M168 112c-34 0-48 50-30 92 8 16 26 12 32-6 8-26 10-58-2-86z" fill="var(--hs-dog-2)"/>
<path d="M272 112c34 0 48 50 30 92-8 16-26 12-32-6-8-26-10-58 2-86z" fill="var(--hs-dog-2)"/>
<ellipse cx="220" cy="186" rx="30" ry="22" fill="var(--hs-cream)"/>
<ellipse cx="220" cy="175" rx="10" ry="7" fill="var(--art-ink)" stroke="none"/>
<path d="M220 182v6M208 190c6 7 18 7 24 0"/>
${eye(192, 152, 12.5)}${eye(248, 152, 12.5)}
<ellipse cx="180" cy="180" rx="10" ry="5.5" fill="var(--ic-blush)" stroke="none"/>
<ellipse cx="260" cy="180" rx="10" ry="5.5" fill="var(--ic-blush)" stroke="none"/>
<path d="M424 344c40 4 52-40 30-62" stroke="var(--art-ink)" stroke-width="18"/>
<path d="M424 344c40 4 52-40 30-62" stroke="var(--hs-cat)" stroke-width="12"/>
<path d="M348 248c-22 30-26 66-20 102h104c6-36 2-72-20-102z" fill="var(--hs-cat)"/>
<path d="M346 196l-6-50c0-6 6-8 10-4l32 30z" fill="var(--hs-cat)"/>
<path d="M410 196l6-50c0-6-6-8-10-4l-32 30z" fill="var(--hs-cat)"/>
<path d="M348 176l-2-18 14 12z M408 176l2-18-14 12z" fill="var(--ic-ear)" stroke="none"/>
<circle cx="378" cy="214" r="46" fill="var(--hs-cat)"/>
<rect x="352" y="300" width="22" height="52" rx="11" fill="var(--hs-cat)"/>
<rect x="382" y="300" width="22" height="52" rx="11" fill="var(--hs-cat)"/>
${eye(358, 214, 9.5)}${eye(398, 214, 9.5)}
<path d="M374 229h8l-4 4z" fill="var(--coral)" stroke-width="1.6"/>
<path d="M370 238c3 4 8 4 8-2 0 6 5 6 8 2"/>
<path d="M334 226l-16-3M334 234l-16 3M422 226l16-3M422 234l16 3" stroke-width="1.8"/>
<ellipse cx="346" cy="232" rx="7" ry="4" fill="var(--ic-blush)" stroke="none"/>
<ellipse cx="410" cy="232" rx="7" ry="4" fill="var(--ic-blush)" stroke="none"/>
</svg>`;

const T = {
  en: { file: 'og.png', h: 'Know what to do<br>for your animal.', sub: 'Plain answers from veterinary sources, a health booklet that stays on your phone, a one-page brief for the visit.', chips: ['EN · IT · DE', 'Free, no ads', 'Vet review shown'] },
  it: { file: 'og-it.png', h: 'Sapere cosa fare<br>per il tuo animale.', sub: 'Risposte chiare da fonti veterinarie, un libretto sanitario che resta sul telefono, un riepilogo di una pagina per la visita.', chips: ['IT · EN · DE', 'Gratis, senza pubblicità', 'Revisione indicata'] },
  de: { file: 'og-de.png', h: 'Wissen, was Ihrem<br>Tier jetzt hilft.', sub: 'Klare Antworten aus tierärztlichen Quellen, ein Gesundheitspass, der auf dem Handy bleibt, eine Seite für den Praxisbesuch.', chips: ['DE · EN · IT', 'Kostenlos, ohne Werbung', 'Prüfstatus sichtbar'] },
};

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: 'light' });
for (const t of Object.values(T)) {
  await page.goto(`${base}/`);
  await page.evaluate(({ t, mark, art }) => {
    document.body.innerHTML = `
      <div style="width:1200px;height:630px;box-sizing:border-box;padding:64px 72px;display:grid;grid-template-columns:1fr 470px;align-items:center;background:var(--bg);overflow:hidden">
        <div>
          <div style="display:flex;gap:14px;align-items:center;font-weight:700;font-size:28px;color:var(--ink)">${mark}AI Veterinary</div>
          <h1 style="font-size:66px;line-height:1.05;margin:44px 0 22px">${t.h}</h1>
          <p style="font-size:24px;line-height:1.45;color:var(--ink-2);margin:0 0 26px;max-width:600px">${t.sub}</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap">${t.chips.map((c) => `<span style="font-size:20px;font-weight:600;padding:8px 16px;border-radius:999px;background:var(--surface);border:1px solid var(--line)">${c}</span>`).join('')}</div>
          <p style="margin:40px 0 0;font-size:22px;font-weight:600;color:var(--ink-3)">aiveterinary.org</p>
        </div>
        <div style="width:470px">${art}</div>
      </div>`;
  }, { t, mark, art });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out(t.file) });
  console.log('wrote', t.file);
}
await browser.close();
