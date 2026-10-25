// End-to-end: loads the unpacked extension in Chromium and drives it against test/fake-pims.html.
// Run: node build.mjs && node --test test/e2e.mjs
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash, generateKeyPairSync } from 'node:crypto';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const root = new URL('..', import.meta.url).pathname;
const PIMS = 'http://pims.test/fake-pims.html';
const fixture = readFileSync(join(root, 'test/fixtures/approved-luna.json'), 'utf8');
const bundle = JSON.parse(fixture);

let ctx, extId, work;
const requests = [];

before(async () => {
  // A copy of the extension with two test-only changes: a fixed key (so the ID is known) and a host
  // permission for the fake PIMS. Playwright cannot click the toolbar button, which is what grants
  // activeTab in real use; the shipped manifest has no host permissions.
  work = mkdtempSync(join(tmpdir(), 'aivet-ext-'));
  const ext = join(work, 'ext');
  for (const p of ['manifest.json', 'popup.html', 'popup.css', '_locales', 'dist']) cpSync(join(root, p), join(ext, p), { recursive: true });
  const { publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
  const der = publicKey.export({ type: 'spki', format: 'der' });
  extId = [...createHash('sha256').update(der).digest('hex').slice(0, 32)].map((c) => String.fromCharCode(97 + parseInt(c, 16))).join('');
  const m = JSON.parse(readFileSync(join(ext, 'manifest.json'), 'utf8'));
  writeFileSync(join(ext, 'manifest.json'), JSON.stringify({ ...m, key: der.toString('base64'), host_permissions: ['http://pims.test/*'] }));

  ctx = await chromium.launchPersistentContext(join(work, 'profile'), {
    channel: 'chromium', headless: true, locale: 'en-US',
    args: [`--disable-extensions-except=${ext}`, `--load-extension=${ext}`],
  });
  ctx.on('request', (r) => requests.push(r.url()));
  // The only thing served is the fake PIMS page; any other http(s) request is aborted and fails the network test.
  await ctx.route('**/*', (route) => {
    const u = route.request().url();
    if (u.startsWith(PIMS)) return route.fulfill({ contentType: 'text/html', body: readFileSync(join(root, 'test/fake-pims.html')) });
    if (u.startsWith(`chrome-extension://${extId}/`)) return route.continue(); // the extension's own files
    return route.abort();
  });
});
after(async () => { await ctx?.close(); rmSync(work, { recursive: true, force: true }); });

/** Opens the fake PIMS with the given query and the popup aimed at that tab. */
let n = 0;
async function open(query = '') {
  const url = `${PIMS}${query || '?'}&tab=${++n}`; // unique, so the popup finds this tab and no other
  const pims = await ctx.newPage();
  await pims.goto(url);
  const popup = await ctx.newPage();
  await popup.goto(`chrome-extension://${extId}/popup.html`);
  const tab = await popup.evaluate(async (u) => (await chrome.tabs.query({})).find((t) => t.url === u).id, url);
  await popup.goto(`chrome-extension://${extId}/popup.html?tab=${tab}`);
  return { pims, popup, tab };
}
const soap = (pims) => pims.evaluate(() => ['#soap-s', 'textarea[name=objective]', '.box textarea', '#soap-p'].map((s) => document.querySelector(s).value));
const banner = (pims) => pims.locator('aivet-helper #b');

test('maps the fields by clicking, then pastes the exact approved text', async () => {
  const { pims, popup } = await open();
  // Control: a naive `el.value = x` from page script is wiped by the React-like component.
  assert.equal(await pims.evaluate(() => { const p = document.querySelector('#soap-p'); p.value = 'naive'; p.dispatchEvent(new Event('input', { bubbles: true })); return p.value; }), '');
  await popup.fill('#export', fixture);
  assert.match(await popup.textContent('#verdict'), /^Approved: Luna \(dog\), version 1, by Dr\. Anna Test/);
  assert.match(await popup.textContent('#site'), /No fields mapped yet for http:\/\/pims\.test/);

  await popup.click('#map');
  await banner(pims).waitFor();
  assert.match(await banner(pims).textContent(), /\(1\/6\).*patient name/);
  await pims.click('#pt-name');
  await pims.click('.pt-species');
  await pims.click('#pt-id'); // not a text box: refused, still on step 3
  assert.match(await banner(pims).textContent(), /\(3\/6\).*not a multi-line text box/);
  for (const s of ['#soap-s', 'textarea[name=objective]', '.box textarea', '#soap-p']) await pims.click(s);
  await pims.waitForFunction(() => document.querySelector('aivet-helper')?.shadowRoot.textContent.includes('Mapping saved'));
  assert.equal(await pims.evaluate(() => window.__submits), 0, 'picking clicks never reach the page');

  const map = await popup.evaluate(async () => (await chrome.storage.local.get('map:http://pims.test'))['map:http://pims.test']);
  assert.deepEqual(Object.keys(map).sort(), ['A', 'O', 'P', 'S', 'name', 'species']);
  assert.equal(map.S, '#soap-s'); assert.equal(map.O, 'textarea[name="objective"]');

  await popup.waitForFunction(() => !document.querySelector('#paste').disabled);
  await popup.click('#paste');
  await popup.locator('#result li').nth(3).waitFor();
  const rows = await popup.locator('#result li').allTextContents();
  assert.equal(rows.length, 4);
  assert.match(rows[0], /^Subjective → #soap-s · \d+ characters, exact$/);
  assert.match(await popup.textContent('#result'), /Nothing was saved or submitted\./);

  assert.deepEqual(await soap(pims), bundle.soap.map((f) => f.text));
  assert.equal(await pims.textContent('#react-state'), bundle.soap[3].text, 'the React-like component state took the value');
  assert.equal(await pims.evaluate(() => window.__submits), 0, 'nothing was submitted');
  assert.match(await banner(pims).textContent(), /Pasted\. Check and save/);
  await pims.close(); await popup.close();
});

test('blocks a different patient, with no way to override', async () => {
  for (const [q, re] of [['?patient=Max', /The page shows patient "Max", the approved record is for "Luna"/], ['?species=Katze', /The page shows species "Katze", the approved record is for a dog/]]) {
    const { pims, popup } = await open(q);
    await popup.fill('#export', fixture);
    await popup.waitForFunction(() => !document.querySelector('#paste').disabled);
    await popup.click('#paste');
    await popup.locator('#result.bad').waitFor();
    assert.match(await popup.textContent('#result'), re);
    assert.match(await banner(pims).textContent(), /Paste blocked/);
    assert.deepEqual(await soap(pims), ['', '', '', '']);
    assert.deepEqual(await popup.locator('#result button').allTextContents(), ['Cancel'], 'the only choice is Cancel');
    await popup.click('#result button');
    assert.equal(await popup.inputValue('#export'), '');
    assert.equal(await popup.isDisabled('#paste'), true);
    await pims.close(); await popup.close();
  }
});

test('never overwrites text already in the PIMS', async () => {
  const { pims, popup } = await open();
  await pims.fill('textarea[name=objective]', 'typed by the nurse');
  await popup.fill('#export', fixture);
  await popup.waitForFunction(() => !document.querySelector('#paste').disabled);
  await popup.click('#paste');
  await popup.locator('#result.bad').waitFor();
  assert.match(await popup.textContent('#result'), /already contain text: O/);
  assert.deepEqual(await soap(pims), ['', 'typed by the nurse', '', '']);
  await pims.close(); await popup.close();
});

test('refuses an unapproved or tampered export, in the popup and in the page', async () => {
  const { pims, popup, tab } = await open();
  const unapproved = structuredClone(bundle); delete unapproved.provenance.approved_by;
  const edited = structuredClone(bundle); edited.soap[3].text += '\nmeloxicam 0.2 mg/kg';
  for (const [b, re] of [[unapproved, /approval details are missing/], [edited, /not the ones generated from the approved record/]]) {
    await popup.fill('#export', JSON.stringify(b));
    assert.match(await popup.textContent('#verdict'), re);
    assert.equal(await popup.isDisabled('#paste'), true);
  }
  // Bypassing the popup's check: the content script verifies again and refuses.
  const r = await popup.evaluate(async ({ tab, text }) => {
    await chrome.scripting.executeScript({ target: { tabId: tab }, files: ['dist/content.js'] });
    return chrome.tabs.sendMessage(tab, { cmd: 'paste', text });
  }, { tab, text: JSON.stringify(unapproved) });
  assert.deepEqual(r, { ok: false, reason: 'refused', detail: 'not_approved' });
  assert.deepEqual(await soap(pims), ['', '', '', '']);
  await pims.close(); await popup.close();
});

test('makes no network requests', () => {
  const pages = requests.filter((u) => u.startsWith(PIMS));
  assert.ok(pages.length >= 5, 'interception saw the fake PIMS loads');
  assert.deepEqual(requests.filter((u) => !u.startsWith(PIMS) && !u.startsWith(`chrome-extension://${extId}/`)), []);
});
