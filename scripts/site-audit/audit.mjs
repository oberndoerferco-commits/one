/*
  Oberndörfer Milano - weekly site audit (23 September 2026).
  Run: node scripts/site-audit/audit.mjs [--out docs/audits/YYYY-MM-DD.json]
  Needs Playwright with Chromium (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers on the cloud runner).

  What it checks, on desktop and on an iPhone emulation:
    - every page in PAGES plus every collection and the first products of each: HTTP status,
      console errors, page errors, failed requests, broken images, horizontal overflow on mobile,
      DOM churn and long tasks in a 5s idle window (the 23 Sept touch bug was 4,000+ nodes/5s),
      the first product-card tap navigating on the first tap
    - internal links on those pages: every unique href answered with HEAD/GET, 4xx/5xx reported
    - catalogue via /products.json: active products with no image, empty body, or price 0
    - email DNS: DMARC, Shopify DKIM, Zoho MX present
  Output: JSON with findings ranked by severity, and a short text summary on stdout.
*/
import { chromium, devices } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';

const ORIGIN = 'https://www.oberndoerferco.com';
const PAGES = ['/', '/collections', '/collections/ready-to-wear', '/collections/bags', '/collections/trunks',
  '/collections/small-leather-goods', '/collections/home-accessories', '/collections/travel', '/collections/sunglasses',
  '/pages/about-us', '/pages/personalization', '/pages/trax-nyc', '/pages/contact', '/pages/faq',
  '/pages/materials-craftsmanship', '/pages/the-art-of-packaging', '/pages/leather-care', '/search?q=bag', '/cart', '/this-page-does-not-exist'];
const outArg = process.argv.indexOf('--out');
const outPath = outArg > -1 ? process.argv[outArg + 1] : null;
const findings = [];
const add = (severity, area, page, message, detail) => findings.push({ severity, area, page, message, detail });

async function dns(name, type) {
  try { const r = await fetch(`https://dns.google/resolve?name=${name}&type=${type}`); const j = await r.json(); return (j.Answer || []).map(a => a.data); } catch { return null; }
}

async function auditPage(ctx, path, mobile, linkSet, productLinks) {
  const page = await ctx.newPage();
  const consoleErrors = [], pageErrors = [], failed = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 200)); });
  page.on('pageerror', e => pageErrors.push(String(e.message).slice(0, 200)));
  page.on('response', r => { const s = r.status(); if (s >= 400 && !/shop\.app|monorail|analytics|pixel/i.test(r.url())) failed.push(s + ' ' + r.url().slice(0, 140)); });
  let status = 0;
  try { const res = await page.goto(ORIGIN + path, { waitUntil: 'domcontentloaded', timeout: 60000 }); status = res ? res.status() : 0; } catch (e) { add('high', 'load', path, 'page did not load', e.message.slice(0, 200)); await page.close(); return; }
  if (path === '/this-page-does-not-exist') { if (status !== 404) add('medium', 'load', path, 'missing page does not answer 404', 'status ' + status); }
  else if (status >= 400) add('high', 'load', path, 'page answers ' + status, '');
  await page.waitForTimeout(2500);
  const m = await page.evaluate(async () => {
    const r = { churn: 0, longTasks: 0, longTaskMs: 0, brokenImages: [], overflow: false, cards: 0 };
    const mo = new MutationObserver(l => { for (const x of l) r.churn += x.addedNodes.length + x.removedNodes.length; });
    mo.observe(document.documentElement, { childList: true, subtree: true });
    let po; try { po = new PerformanceObserver(l => { for (const e of l.getEntries()) { r.longTasks++; r.longTaskMs += e.duration; } }); po.observe({ entryTypes: ['longtask'] }); } catch {}
    await new Promise(res => setTimeout(res, 3000)); mo.disconnect(); if (po) po.disconnect();
    for (const img of document.images) { const rect = img.getBoundingClientRect(); if (rect.width > 0 && img.complete && img.naturalWidth === 0 && img.currentSrc) r.brokenImages.push((img.currentSrc || '').slice(0, 140)); }
    r.overflow = document.documentElement.scrollWidth > window.innerWidth + 2;
    r.cards = document.querySelectorAll('product-card').length;
    r.links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => h && (h.startsWith('/') || h.startsWith(location.origin)) && !h.startsWith('/cart/') && !h.includes('#') && !h.startsWith('/account'));
    r.products = [...document.querySelectorAll('product-card a[href*="/products/"]')].map(a => a.getAttribute('href')).slice(0, 3);
    return r;
  });
  const dev = mobile ? 'mobile' : 'desktop';
  for (const l of m.links) linkSet.add(l.split('?')[0]);
  for (const p of m.products) productLinks.add(p.split('?')[0]);
  if (m.churn > 400) add('high', 'performance', path, `${dev}: page keeps changing while idle (${m.churn} DOM nodes in 3 s)`, 'a script is looping; taps and scrolling suffer');
  if (m.longTaskMs > 1000) add('medium', 'performance', path, `${dev}: main thread blocked ${Math.round(m.longTaskMs)} ms in 3 s idle`, `${m.longTasks} long tasks`);
  if (m.brokenImages.length) add('high', 'images', path, `${dev}: ${m.brokenImages.length} broken image(s)`, m.brokenImages.slice(0, 5).join('\n'));
  if (mobile && m.overflow) add('medium', 'layout', path, 'mobile: page scrolls sideways (content wider than the screen)', '');
  if (pageErrors.length) add('medium', 'javascript', path, `${dev}: ${pageErrors.length} script error(s)`, [...new Set(pageErrors)].slice(0, 5).join('\n'));
  const realConsole = consoleErrors.filter(t => !/shop\.app|frame-ancestors|403|favicon|net::ERR_BLOCKED/i.test(t));
  if (realConsole.length) add('low', 'javascript', path, `${dev}: ${realConsole.length} console error(s)`, [...new Set(realConsole)].slice(0, 5).join('\n'));
  if (failed.length) add('medium', 'network', path, `${dev}: ${failed.length} failed request(s)`, [...new Set(failed)].slice(0, 5).join('\n'));
  // first-tap test on mobile collection pages
  if (mobile && m.cards > 0 && path.startsWith('/collections/')) {
    const el = await page.$('product-card a[href*="/products/"]');
    if (el) { try { await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(500); const b = await el.boundingBox(); const before = page.url(); await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2); await page.waitForTimeout(2500); if (page.url() === before) add('high', 'touch', path, 'mobile: first tap on a product card did not open the product', ''); } catch (e) { add('low', 'touch', path, 'tap test could not run', e.message.slice(0, 120)); } }
  }
  await page.close();
}

async function auditProduct(ctx, path) {
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e.message).slice(0, 200)));
  try { const res = await page.goto(ORIGIN + path, { waitUntil: 'domcontentloaded', timeout: 60000 }); if (!res || res.status() >= 400) { add('high', 'load', path, 'product page answers ' + (res ? res.status() : 0), ''); await page.close(); return; } } catch (e) { add('high', 'load', path, 'product page did not load', e.message.slice(0, 150)); await page.close(); return; }
  await page.waitForTimeout(2500);
  const r = await page.evaluate(() => ({
    title: (document.querySelector('main h1') || {}).innerText || '',
    price: !!document.querySelector('main product-price, main .price'),
    buy: !!document.querySelector('main button[type="submit"], main add-to-cart-component button, main .add-to-cart-button, main [name="add"]'),
    images: [...document.querySelectorAll('main img')].filter(i => i.getBoundingClientRect().width > 50).length,
    broken: [...document.querySelectorAll('main img')].filter(i => i.getBoundingClientRect().width > 50 && i.complete && i.naturalWidth === 0).length,
    swatchesWithoutColour: [...document.querySelectorAll('main .swatch')].filter(s => !s.style.cssText && !s.getAttribute('style')).length,
  }));
  if (!r.title) add('medium', 'product', path, 'no product title rendered', '');
  if (!r.price) add('medium', 'product', path, 'no price rendered', '');
  if (!r.buy) add('high', 'product', path, 'no add-to-cart or pre-order button', '');
  if (r.images === 0) add('high', 'product', path, 'no product photographs rendered', '');
  if (r.broken) add('high', 'images', path, `${r.broken} broken product image(s)`, '');
  if (errs.length) add('medium', 'javascript', path, `${errs.length} script error(s)`, [...new Set(errs)].slice(0, 3).join('\n'));
  await page.close();
}

async function main() {
  const t0 = Date.now();
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const linkSet = new Set(), productLinks = new Set();
  async function pool(items, n, fn) { const q = [...items]; await Promise.all(Array.from({ length: n }, async () => { while (q.length) { const it = q.shift(); try { await fn(it); } catch (e) { add('low', 'audit', String(it), 'check crashed', e.message.slice(0, 120)); } } })); }
  for (const mobile of [false, true]) {
    const ctx = await browser.newContext(mobile ? { ...devices['iPhone 13'], locale: 'en-US' } : { viewport: { width: 1440, height: 1000 }, locale: 'en-US' });
    await pool(PAGES, 3, p => auditPage(ctx, p, mobile, linkSet, productLinks));
    await ctx.close();
  }
  // product pages (desktop only, a sample of each collection's first products)
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'en-US' });
  await pool([...productLinks].slice(0, 16), 3, p => auditProduct(ctx, p));
  await ctx.close();
  await browser.close();
  // link check
  let checked = 0;
  await pool([...linkSet].slice(0, 300), 6, async href => {
    const url = href.startsWith('http') ? href : ORIGIN + href;
    try { let r = await fetch(url, { method: 'HEAD', redirect: 'follow' }); if (r.status === 405 || r.status === 403) r = await fetch(url, { redirect: 'follow' }); checked++; if (r.status >= 400) add(r.status === 404 ? 'high' : 'medium', 'links', href, `link answers ${r.status}`, ''); } catch (e) { add('medium', 'links', href, 'link could not be fetched', e.message.slice(0, 100)); }
  });
  // catalogue
  try {
    const r = await fetch(ORIGIN + '/products.json?limit=250'); const j = await r.json();
    for (const p of j.products || []) {
      const price = Math.min(...p.variants.map(v => parseFloat(v.price)));
      if (!p.images || !p.images.length) add('high', 'catalogue', '/products/' + p.handle, 'active product without a photograph', p.title);
      if (!p.body_html || p.body_html.replace(/<[^>]+>/g, '').trim().length < 40) add('medium', 'catalogue', '/products/' + p.handle, 'active product with no or very short description', p.title);
      if (!(price > 0)) add('high', 'catalogue', '/products/' + p.handle, 'active product priced at 0', p.title);
      const avail = p.variants.some(v => v.available);
      if (!avail) add('low', 'catalogue', '/products/' + p.handle, 'no variant purchasable (sold out)', p.title);
    }
  } catch (e) { add('medium', 'catalogue', '/products.json', 'catalogue feed could not be read', e.message.slice(0, 100)); }
  // email DNS
  const dmarc = await dns('_dmarc.oberndoerferco.com', 'TXT');
  if (dmarc && !dmarc.some(d => /DMARC1/.test(d))) add('medium', 'email', 'DNS', 'DMARC record missing', '');
  const dkim = await dns('h3f._domainkey.oberndoerferco.com', 'CNAME');
  if (dkim && !dkim.length) add('medium', 'email', 'DNS', 'Shopify DKIM record missing', '');
  const mx = await dns('oberndoerferco.com', 'MX');
  if (mx && !mx.some(d => /zoho/.test(d))) add('high', 'email', 'DNS', 'Zoho MX records missing: the mailbox will not receive mail', '');

  const order = { high: 0, medium: 1, low: 2 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const report = { date: new Date().toISOString(), origin: ORIGIN, pagesChecked: PAGES.length * 2, productPagesChecked: Math.min(productLinks.size, 16), linksChecked: checked, seconds: Math.round((Date.now() - t0) / 1000), counts: { high: findings.filter(f => f.severity === 'high').length, medium: findings.filter(f => f.severity === 'medium').length, low: findings.filter(f => f.severity === 'low').length }, findings };
  if (outPath) { fs.mkdirSync(outPath.replace(/\/[^/]+$/, ''), { recursive: true }); fs.writeFileSync(outPath, JSON.stringify(report, null, 2)); }
  console.log(`Audit ${report.date}: ${report.pagesChecked} page loads, ${report.productPagesChecked} product pages, ${checked} links, ${report.seconds}s`);
  console.log(`high ${report.counts.high} · medium ${report.counts.medium} · low ${report.counts.low}`);
  for (const f of findings) console.log(`[${f.severity}] ${f.area} ${f.page}: ${f.message}${f.detail ? ' — ' + f.detail.split('\n')[0] : ''}`);
}
main().catch(e => { console.error('audit crashed:', e); process.exit(1); });
