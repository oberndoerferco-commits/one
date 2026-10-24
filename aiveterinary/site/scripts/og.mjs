// Renders the social share images (public/og.png, og-it.png, og-de.png) with the site's own
// styles and hero illustration. Run with the preview server up:
//   npx astro preview &  node scripts/og.mjs
// Needs Playwright with a Chromium; PLAYWRIGHT_MODULE and CHROMIUM override the defaults.
import { fileURLToPath } from 'node:url';

const pw = await import(process.env.PLAYWRIGHT_MODULE ?? 'playwright');
const chromium = pw.chromium ?? pw.default.chromium;
const base = process.env.BASE_URL ?? 'http://localhost:4321';
const out = (f) => fileURLToPath(new URL(`../public/${f}`, import.meta.url));

const T = {
  en: { file: 'og.png', h: 'Know what to do<br>for your animal.', sub: 'Plain answers from veterinary sources, a health booklet that stays on your phone, a one-page brief for the visit.', chips: ['EN · IT · DE', 'Free, no ads', 'Vet review shown'] },
  it: { file: 'og-it.png', h: 'Sapere cosa fare<br>per il tuo animale.', sub: 'Risposte chiare da fonti veterinarie, un libretto sanitario che resta sul telefono, un riepilogo di una pagina per la visita.', chips: ['IT · EN · DE', 'Gratis, senza pubblicità', 'Revisione indicata'] },
  de: { file: 'og-de.png', h: 'Wissen, was Ihrem<br>Tier jetzt hilft.', sub: 'Klare Antworten aus tierärztlichen Quellen, ein Gesundheitspass, der auf dem Handy bleibt, eine Seite für den Praxisbesuch.', chips: ['DE · EN · IT', 'Kostenlos, ohne Werbung', 'Prüfstatus sichtbar'] },
};

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: 'light' });
for (const t of Object.values(T)) {
  await page.goto(`${base}/`);
  await page.evaluate((t) => {
    const art = document.querySelector('.h3ro-art svg').outerHTML;
    document.body.innerHTML = `
      <div style="width:1200px;height:630px;box-sizing:border-box;padding:64px 72px;display:grid;grid-template-columns:1fr 470px;align-items:center;background:var(--bg);overflow:hidden">
        <div>
          <div style="display:flex;gap:14px;align-items:center;font-weight:700;font-size:28px;color:var(--ink)"><span style="width:40px;height:40px;border-radius:50%;background:var(--accent)"></span>AI Veterinary</div>
          <h1 style="font-size:66px;line-height:1.05;margin:44px 0 22px">${t.h}</h1>
          <p style="font-size:24px;line-height:1.45;color:var(--ink-2);margin:0 0 26px;max-width:600px">${t.sub}</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap">${t.chips.map((c) => `<span style="font-size:20px;font-weight:600;padding:8px 16px;border-radius:999px;background:var(--surface);border:1px solid var(--line)">${c}</span>`).join('')}</div>
          <p style="margin:40px 0 0;font-size:22px;font-weight:600;color:var(--ink-3)">aiveterinary.org</p>
        </div>
        <div style="width:470px">${art.replace(/width="\d+"/, 'width="470"').replace(/height="[\d.]+"/, '')}</div>
      </div>`;
    document.querySelectorAll('.hs-eye, .hs-tail').forEach((el) => (el.style.animation = 'none'));
  }, t);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out(t.file) });
  console.log('wrote', t.file);
}
await browser.close();
