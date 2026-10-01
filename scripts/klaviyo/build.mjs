// Writes every email to out/*.html (for review) and, with KLAVIYO_API_KEY set, creates or
// updates the templates in Klaviyo by name and prints their ids. Nothing is sent.
import { writeFileSync, mkdirSync } from 'node:fs';
import { emails } from './emails.mjs';

mkdirSync(new URL('./out/', import.meta.url), { recursive: true });
for (const e of emails) writeFileSync(new URL(`./out/${e.key}.html`, import.meta.url), e.html);
console.log(`wrote ${emails.length} files to scripts/klaviyo/out/`);

const KEY = process.env.KLAVIYO_API_KEY;
if (!KEY) { console.log('KLAVIYO_API_KEY not set: skipped the Klaviyo upload.'); process.exit(0); }

const REV = '2025-07-15';
async function k(method, path, body) {
  const r = await fetch('https://a.klaviyo.com/api' + path, {
    method, headers: { Authorization: `Klaviyo-API-Key ${KEY}`, revision: REV, accept: 'application/vnd.api+json', 'content-type': 'application/vnd.api+json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${method} ${path} ${r.status}: ${text.slice(0, 600)}`);
  return text ? JSON.parse(text) : null;
}

const existing = await k('GET', '/templates?page[size]=100');
const byName = new Map(existing.data.map((t) => [t.attributes.name, t.id]));
const ids = {};
for (const e of emails) {
  const attrs = { name: e.name, editor_type: 'CODE', html: e.html, text: `${e.subject}\n\nOpen this email in a browser: {% view_in_browser %}\n\n{% unsubscribe %}` };
  let id = byName.get(e.name);
  if (id) { await k('PATCH', `/templates/${id}`, { data: { type: 'template', id, attributes: { html: attrs.html, text: attrs.text } } }); console.log('updated', e.name, id); }
  else { const res = await k('POST', '/templates', { data: { type: 'template', attributes: attrs } }); id = res.data.id; console.log('created', e.name, id); }
  ids[e.key] = id;
  await new Promise((r) => setTimeout(r, 300));
}
writeFileSync(new URL('./out/template-ids.json', import.meta.url), JSON.stringify(ids, null, 2));
console.log(ids);
