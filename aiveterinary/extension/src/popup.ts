import { verifyExport, describe, mappingKey, type Verified, type PasteResult } from './core.js';

declare const chrome: any;
const msg = (k: string, subs?: string[]) => chrome.i18n.getMessage(k, subs) || k;
const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;

for (const el of document.querySelectorAll<HTMLElement>('[data-i18n]')) el.textContent = msg(el.dataset.i18n!);
document.documentElement.lang = chrome.i18n.getUILanguage().slice(0, 2);

const box = $<HTMLTextAreaElement>('export');
let verified: Verified | null = null;
let tab: { id: number; url?: string } | null = null;
let mapped = false;

/** The tab the vet opened the popup on. `?tab=` exists only for the automated test, which cannot click the toolbar. */
async function targetTab() {
  const forced = Number(new URLSearchParams(location.search).get('tab'));
  if (forced) return chrome.tabs.get(forced);
  const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
  return t ?? null;
}
const origin = () => { try { return new URL(tab!.url!).origin; } catch { return null; } };

function check() {
  verified = box.value.trim() ? verifyExport(box.value) : null;
  const v = $('verdict');
  if (!verified) { v.textContent = ''; v.className = ''; }
  else if (verified.ok) {
    const { patient, provenance: p } = verified.bundle;
    v.textContent = msg('approvedOk', [patient.name, patient.species, String(p.version), p.approved_by, new Date(p.approved_at).toLocaleString()]);
    v.className = 'ok';
  } else { v.textContent = msg('refused_' + verified.reason); v.className = 'bad'; }
  $<HTMLButtonElement>('paste').disabled = !(verified?.ok && mapped);
  $('result').textContent = '';
}

async function refreshSite() {
  const o = origin();
  const map = $<HTMLButtonElement>('map');
  if (!o || !/^https?:/.test(o)) { $('site').textContent = msg('siteUnsupported'); map.disabled = true; map.textContent = msg('map'); return; }
  mapped = !!(await chrome.storage.local.get(mappingKey(o)))[mappingKey(o)];
  $('site').textContent = msg(mapped ? 'siteMapped' : 'siteNotMapped', [o]);
  map.textContent = msg(mapped ? 'remap' : 'map');
  $('forget').hidden = !mapped;
  check();
}

/** Injected only now, on the vet's click. */
async function inject() {
  await chrome.scripting.executeScript({ target: { tabId: tab!.id }, files: ['dist/content.js'] });
}

box.addEventListener('input', check);
$('clip').addEventListener('click', async () => {
  // Clipboard access is optional and asked for here, on the click, never at install.
  const granted = await chrome.permissions.request({ permissions: ['clipboardRead'] }).catch(() => false);
  if (!granted) { $('verdict').textContent = msg('clipboardDenied'); return; }
  try { box.value = await navigator.clipboard.readText(); } catch { $('verdict').textContent = msg('clipboardDenied'); return; }
  check();
});
$('map').addEventListener('click', async () => {
  await inject();
  await chrome.tabs.sendMessage(tab!.id, { cmd: 'map' });
  $('site').textContent = msg('pickStarted');
});
$('forget').addEventListener('click', async () => { await chrome.storage.local.remove(mappingKey(origin()!)); refreshSite(); });
$('paste').addEventListener('click', async () => {
  if (!verified?.ok) return;
  await inject();
  const r: PasteResult = await chrome.tabs.sendMessage(tab!.id, { cmd: 'paste', text: box.value });
  const out = $('result');
  if (r.ok) {
    out.className = r.rows.every((x) => x.ok) ? 'ok' : 'bad';
    out.innerHTML = '';
    const ul = document.createElement('ul');
    for (const x of r.rows) { const li = document.createElement('li'); li.textContent = `${x.label} → ${x.selector} · ${msg(x.ok ? 'rowOk' : 'rowChanged', [String(x.chars)])}`; ul.append(li); }
    out.append(ul, msg('saveYourself'));
  } else {
    out.className = 'bad';
    out.textContent = describe(r, msg);
    if (r.reason === 'mismatch') {
      // The only way forward is the right patient in the PIMS; there is no override.
      const b = document.createElement('button'); b.textContent = msg('cancel'); b.type = 'button';
      b.addEventListener('click', () => { box.value = ''; check(); });
      out.append(document.createElement('br'), b);
    }
  }
});
chrome.storage.onChanged.addListener(() => refreshSite());

targetTab().then((t) => { tab = t; refreshSite(); });
