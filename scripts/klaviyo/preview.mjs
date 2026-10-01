// Renders each email to a PNG with sample values in place of the Klaviyo tags, for review.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, readdirSync } from 'node:fs';
const dir = new URL('./out/', import.meta.url);
const sample = (h) => h
  .replace(/\{% if first_name %\}\{\{ first_name \}\},\{% else %\}Good day,\{% endif %\}/g, 'Good day,')
  .replace(/\{% for item in event\.extra\.line_items %\}([\s\S]*?)\{% endfor %\}/g, (_, inner) => inner
    .replace(/\{% if item\.product\.images\.0\.src %\}/g, '').replace(/\{% endif %\}/g, '')
    .replace(/\{\{ item\.product\.images\.0\.src \}\}/g, 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/obm-lane-ostrich-mini-trunk.jpg?width=400&v=1787069119')
    .replace(/\{\{ item\.product\.title \}\}/g, 'Ostrich Mini Trunk Handbag')
    .replace(/\{% if item\.variant_title and item\.variant_title != 'Default Title' %\}/g, '')
    .replace(/\{\{ item\.variant_title \}\}/g, 'Navy')
    .replace(/\{\{ item\.quantity \}\}/g, '1').replace(/\{\{ item\.line_price\|floatformat:2 \}\}/g, '4,950.00')
    .replace(/\{\{ event\.extra\.presentment_currency\|default:'EUR' \}\}/g, 'EUR'))
  .replace(/\{\{ event\.extra\.line_items\.0\.product\.title \}\}/g, 'the Ostrich Mini Trunk Handbag')
  .replace(/\{% if event\.extra\.line_items\|length > 1 %\}[\s\S]*?\{% endif %\}\{% endif %\}/g, '')
  .replace(/\{\{ event\.extra\.checkout_url \}\}/g, '#')
  .replace(/\{\{ organization\.name \}\}/g, 'Oberndörfer Milano').replace(/\{\{ organization\.full_address \}\}/g, 'Via [street], Milano, Italy')
  .replace(/\{% manage_preferences %\}/g, '<a href="#" style="color:#6b6259">Preferences</a>')
  .replace(/\{% unsubscribe %\}/g, '<a href="#" style="color:#6b6259">Unsubscribe</a>')
  .replace(/\{% view_in_browser %\}/g, '<a href="#" style="color:#6b6259">View in browser</a>');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const f of readdirSync(dir).filter((f) => f.endsWith('.html'))) {
  const page = await b.newPage({ viewport: { width: 720, height: 900 }, deviceScaleFactor: 1 });
  await page.setContent(sample(readFileSync(new URL(f, dir), 'utf8')), { waitUntil: 'networkidle' });
  await page.screenshot({ path: new URL(f.replace('.html', '.png'), dir).pathname, fullPage: true });
  console.log('rendered', f);
  await page.close();
}
await b.close();
