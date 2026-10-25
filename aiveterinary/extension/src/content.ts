import { verifyExport, checkPatient, describe, TARGETS, mappingKey, type Mapping, type Target, type PasteResult, type Row } from './core.js';

/**
 * Injected into the PIMS tab only when the vet clicks in the popup (activeTab + scripting).
 * It maps fields, reads the patient header and fills the four SOAP boxes. It never
 * submits, clicks or saves anything: the vet saves in the PIMS.
 */

declare const chrome: any;
const msg = (k: string, subs?: string[]) => chrome.i18n.getMessage(k, subs) || k;

const w = window as any;
if (!w.__aivetHelper) {
  w.__aivetHelper = true;
  chrome.runtime.onMessage.addListener((m: any, _s: unknown, reply: (r: unknown) => void) => {
    if (m?.cmd === 'map') { startPicking(); reply({ ok: true }); }
    if (m?.cmd === 'paste') { paste(String(m.text)).then(reply); return true; }
    return false;
  });
}

// ---------- banner (shadow DOM, so page CSS cannot hide or restyle it) ----------
let host: HTMLElement | null = null;
function banner(html: string, tone: 'info' | 'ok' | 'block' = 'info', buttons: [string, () => void][] = []) {
  host?.remove();
  host = document.createElement('aivet-helper');
  const root = host.attachShadow({ mode: 'open' });
  const bg = { info: '#1f3b57', ok: '#1d5b3a', block: '#8a1c1c' }[tone];
  root.innerHTML = `<style>div{position:fixed;z-index:2147483647;top:12px;right:12px;max-width:420px;background:${bg};color:#fff;font:14px/1.4 system-ui,sans-serif;padding:12px 14px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.3)}button{margin:8px 8px 0 0;font:inherit;padding:4px 10px;border-radius:6px;border:0;cursor:pointer}ul{margin:6px 0 0;padding-left:18px}</style><div role="status" id="b">${html}</div>`;
  for (const [label, fn] of buttons) {
    const b = document.createElement('button'); b.textContent = label; b.addEventListener('click', fn);
    root.getElementById('b')!.append(b);
  }
  document.documentElement.append(host);
}
const closeBanner = () => { host?.remove(); host = null; };
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));

// ---------- mapping: click to pick ----------
const isTextBox = (el: Element) => el instanceof HTMLTextAreaElement || (el instanceof HTMLElement && el.isContentEditable);

/** A selector that finds this element again: a unique id, a unique name, or a path of nth-of-type steps. */
export function selectorFor(el: Element): string {
  const unique = (s: string) => document.querySelectorAll(s).length === 1;
  if (el.id && unique(`#${CSS.escape(el.id)}`)) return `#${CSS.escape(el.id)}`;
  const name = el.getAttribute('name');
  if (name && unique(`${el.localName}[name="${CSS.escape(name)}"]`)) return `${el.localName}[name="${CSS.escape(name)}"]`;
  const parts: string[] = [];
  for (let e: Element | null = el; e && e !== document.documentElement; e = e.parentElement) {
    if (e.id && unique(`#${CSS.escape(e.id)}`)) { parts.unshift(`#${CSS.escape(e.id)}`); break; }
    const same = e.parentElement ? [...e.parentElement.children].filter((c) => c.localName === e!.localName) : [e];
    parts.unshift(same.length > 1 ? `${e.localName}:nth-of-type(${same.indexOf(e) + 1})` : e.localName);
    if (unique(parts.join(' > '))) break;
  }
  return parts.join(' > ');
}

function startPicking() {
  const picked: Partial<Mapping> = {};
  let step = 0; let hovered: HTMLElement | null = null; let oldOutline = '';
  const ours = (e: Event) => e.composedPath().includes(host!);
  const unhover = () => { if (hovered) hovered.style.outline = oldOutline; hovered = null; };
  const prompt = (extra = '') => banner(`<strong>${esc(msg('pickTitle'))} (${step + 1}/6)</strong><br>${esc(msg('pick_' + TARGETS[step]))}${extra ? `<br><em>${esc(extra)}</em>` : ''}`, 'info', [[msg('cancel'), stop]]);
  const over = (e: MouseEvent) => {
    if (ours(e)) return;
    unhover(); hovered = e.target as HTMLElement; oldOutline = hovered.style.outline; hovered.style.outline = '3px solid #e8a33d';
  };
  const click = (e: MouseEvent) => {
    if (ours(e)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    const el = e.target as Element; const t: Target = TARGETS[step];
    if (step >= 2 && !isTextBox(el)) return prompt(msg('pickNotText'));
    if (step < 2 && !el.textContent?.trim()) return prompt(msg('pickEmpty'));
    picked[t] = selectorFor(el); step++;
    if (step < TARGETS.length) return prompt();
    stop();
    chrome.storage.local.set({ [mappingKey(location.origin)]: picked }).then(() => banner(esc(msg('mapSaved', [location.origin])), 'ok', [[msg('close'), closeBanner]]));
  };
  // Capture phase, so the page's own handlers (links, buttons) never see the picking click.
  const block = (e: Event) => { if (!ours(e)) { e.preventDefault(); e.stopImmediatePropagation(); } };
  function stop() {
    unhover();
    document.removeEventListener('mouseover', over, true); document.removeEventListener('click', click, true);
    for (const t of ['mousedown', 'mouseup', 'pointerdown', 'pointerup']) document.removeEventListener(t, block, true);
    closeBanner();
  }
  document.addEventListener('mouseover', over, true); document.addEventListener('click', click, true);
  for (const t of ['mousedown', 'mouseup', 'pointerdown', 'pointerup']) document.addEventListener(t, block, true);
  prompt();
}

// ---------- paste ----------
const readText = (el: Element) => (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement ? el.value : (el as HTMLElement).innerText ?? el.textContent ?? '');

/** Set the value through the native setter and fire input/change, so React/Angular/Vue state follows. No key events, no submit. */
function fill(el: HTMLElement, text: string) {
  el.focus();
  if (el instanceof HTMLTextAreaElement) Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')!.set!.call(el, text);
  else el.innerText = text;
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.blur();
}

async function paste(text: string): Promise<PasteResult> {
  const r = await doPaste(text);
  if (r.ok) banner(`<strong>${esc(msg('pastedTitle'))}</strong><ul>${r.rows.map((x) => `<li>${esc(x.label)} → <code>${esc(x.selector)}</code> · ${esc(msg(x.ok ? 'rowOk' : 'rowChanged', [String(x.chars)]))}</li>`).join('')}</ul>${esc(msg('saveYourself'))}`, r.rows.every((x) => x.ok) ? 'ok' : 'block', [[msg('close'), closeBanner]]);
  else banner(`<strong>${esc(msg('blockedTitle'))}</strong><br>${esc(describe(r, msg))}`, 'block', [[msg('cancel'), closeBanner]]);
  return r;
}

async function doPaste(text: string): Promise<PasteResult> {
  // Verified again here, so nothing reaches the page that has not passed the same checks as in the popup.
  const v = verifyExport(text);
  if (!v.ok) return { ok: false, reason: 'refused', detail: v.reason };
  const map: Mapping | undefined = (await chrome.storage.local.get(mappingKey(location.origin)))[mappingKey(location.origin)];
  if (!map) return { ok: false, reason: 'no_mapping', detail: location.origin };
  const els = {} as Record<Target, HTMLElement>;
  for (const t of TARGETS) {
    const el = document.querySelector<HTMLElement>(map[t]);
    if (!el) return { ok: false, reason: 'field_missing', detail: t };
    els[t] = el;
  }
  const mismatches = checkPatient(v.bundle.patient, { name: readText(els.name), species: readText(els.species) });
  if (mismatches.length) return { ok: false, reason: 'mismatch', mismatches };
  // Never overwrite what is already in the PIMS: the vet clears the box first.
  const full = v.bundle.soap.filter((f) => readText(els[f.key]).trim());
  if (full.length) return { ok: false, reason: 'not_empty', detail: full.map((f) => f.key).join(', ') };
  const rows: Row[] = v.bundle.soap.map((f) => {
    fill(els[f.key], f.text);
    return { key: f.key, label: f.label, selector: map[f.key], chars: f.text.length, ok: readText(els[f.key]) === f.text };
  });
  return { ok: true, rows };
}
