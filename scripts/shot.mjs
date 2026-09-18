#!/usr/bin/env node
/**
 * Screenshot a live page so the house can actually SEE it.
 *
 *   node scripts/shot.mjs <url> <label> [width]
 *
 * width < 600 renders as an iPhone (390 is the default and the one that
 * matters — nobody has audited this store on a phone).
 *
 * Why the SPKI flag: this sandbox routes HTTPS through an interception proxy
 * whose CA is NOT in Chromium's trust store, so every request fails with
 * ERR_CERT_AUTHORITY_INVALID. We do not disable TLS verification. We compute
 * the SPKI hash of the proxy's own CA (the one the environment already
 * designates as trusted, at /root/.ccr/agent-proxy-ca.crt) and tell Chromium
 * to trust exactly that key and nothing else.
 */
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { execSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';

const CA = '/root/.ccr/agent-proxy-ca.crt';

function spkiList() {
  const out = execSync(
    `awk 'BEGIN{n=0} /BEGIN CERTIFICATE/{n++} {print > "/tmp/_ca-" n ".pem"}' ${CA} >/dev/null 2>&1;
     for f in /tmp/_ca-*.pem; do
       openssl x509 -in "$f" -pubkey -noout 2>/dev/null |
       openssl pkey -pubin -outform der 2>/dev/null |
       openssl dgst -sha256 -binary | openssl enc -base64;
     done; rm -f /tmp/_ca-*.pem`,
    { shell: '/bin/bash', encoding: 'utf8' }
  );
  return out.trim().split('\n').filter(Boolean).join(',');
}

const [url, label, widthArg] = process.argv.slice(2);
if (!url || !label) {
  console.error('usage: node scripts/shot.mjs <url> <label> [width]');
  process.exit(1);
}
const width = Number(widthArg || 390);
const mobile = width < 600;

mkdirSync('shots', { recursive: true });

const browser = await chromium.launch({
  args: [`--ignore-certificate-errors-spki-list=${spkiList()}`],
});
const ctx = await browser.newContext({
  viewport: { width, height: mobile ? 852 : 900 },
  deviceScaleFactor: 2,
  isMobile: mobile,
  hasTouch: mobile,
  locale: 'en-DE',
  userAgent: mobile
    ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
    : undefined,
});
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
await page.waitForTimeout(3000);
// let anything lazy-loaded below the fold actually load before the full shot
await page.evaluate(async () => {
  await new Promise((done) => {
    let y = 0;
    const t = setInterval(() => {
      window.scrollBy(0, 900);
      y += 900;
      if (y >= document.body.scrollHeight) { clearInterval(t); window.scrollTo(0, 0); done(); }
    }, 120);
  });
});
await page.waitForTimeout(1500);
await page.screenshot({ path: `shots/${label}.png` });
await page.screenshot({ path: `shots/${label}-full.png`, fullPage: true });
console.log(`${label}: ${await page.title()}`);
await browser.close();
