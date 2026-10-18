// Shared layout for every Oberndörfer Milano email, in the REDESIGN 2026 style of the site
// (18 October 2026): white page, near-black ink, Courier New for text, bold uppercase Helvetica
// for headings, square black buttons, product photographs on the site's grey ground.
// Table-based, inline styles, 600px. Both fonts are system fonts, so every mail app shows them.
// Klaviyo tags ({% unsubscribe %}, {{ organization.full_address }}) stay literal in the output.
export const C = {
  page: '#ffffff', card: '#ffffff', band: '#f3f2ef', ink: '#1c1714', saddle: '#1c1714',
  line: '#e3e0da', muted: '#6b625b', ground: '#ebe9e4', accent: '#1c1714',
};
export const SITE = 'https://www.oberndoerferco.com';
// The header logo (the site's own, rasterised in ink at 3x; see theme/assets-src/obm-email-logo.png).
export const LOGO = 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/obm-email-logo.png?width=780&v=1790937158';
const mono = "'Courier New', Courier, monospace";
const display = "Helvetica, 'Helvetica Neue', Arial, sans-serif";

export const eyebrow = (t) => `<p style="margin:0 0 12px;font:400 12px/1.4 ${mono};letter-spacing:.12em;text-transform:uppercase;color:${C.muted};">${t}</p>`;
export const head = (t, size = 26) => `<h1 style="margin:0 0 18px;font:700 ${size}px/1.15 ${display};letter-spacing:.01em;text-transform:uppercase;color:${C.ink};">${t}</h1>`;
export const sub = (t) => `<h2 style="margin:0 0 12px;font:700 17px/1.3 ${display};letter-spacing:.02em;text-transform:uppercase;color:${C.ink};">${t}</h2>`;
export const p = (t) => `<p style="margin:0 0 16px;font:400 15px/1.65 ${mono};color:${C.ink};">${t}</p>`;
export const small = (t) => `<p style="margin:0 0 10px;font:400 13px/1.6 ${mono};color:${C.muted};">${t}</p>`;
export const link = (t, href) => `<a href="${href}" style="color:${C.ink};text-decoration:underline;text-underline-offset:3px;font:400 14px/1.6 ${mono};text-transform:uppercase;letter-spacing:.04em;">${t}</a>`;
export const caption = (t) => `<p style="margin:8px 0 0;font:400 12px/1.5 ${mono};color:${C.muted};">${t}</p>`;
// Square black button, full width on phones (class "btn").
export const button = (t, href) => `
<table role="presentation" cellpadding="0" cellspacing="0" border="0" class="btn" style="margin:8px 0 22px;"><tr>
<td align="center" style="background:${C.ink};"><a href="${href}" style="display:block;padding:16px 34px;font:400 14px/1 ${mono};letter-spacing:.12em;text-transform:uppercase;color:#ffffff;text-decoration:none;">${t}</a></td>
</tr></table>`;
export const photo = (src, alt, href = null, cap = null) => `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 22px;"><tr><td style="background:${C.ground};">
${href ? `<a href="${href}">` : ''}<img src="${src}" alt="${alt}" width="520" style="display:block;width:100%;max-width:520px;height:auto;border:0;" />${href ? '</a>' : ''}
</td></tr>${cap ? `<tr><td>${caption(cap)}</td></tr>` : ''}</table>`;
// A full-width photograph that runs to the edges of the 600px column (hero).
export const hero = (src, alt, href) => `<a href="${href}"><img src="${src}" alt="${alt}" width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;background:${C.ground};" /></a>`;
export const rule = () => `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-top:1px solid ${C.line};font-size:0;line-height:0;height:1px;">&nbsp;</td></tr></table>`;
// A row of two or three pieces, as on the site's product cards: photograph on the grey ground,
// name and price in Courier, the photograph and name are links. Stacks on phones (class "col").
export const grid = (items) => {
  const n = items.length, cw = n === 2 ? 254 : 165, gap = 12;
  const cells = items.map((it, i) => `
<td width="${cw}" valign="top" class="col" style="padding:0 ${i < n - 1 ? gap : 0}px 0 0;">
  <a href="${it.href}" style="text-decoration:none;"><img src="${it.src}" alt="${it.alt || it.title}" width="${cw}" style="display:block;width:100%;max-width:${cw}px;height:auto;border:0;background:${C.ground};" /></a>
  <p style="margin:10px 0 2px;font:400 13px/1.4 ${mono};color:${C.ink};"><a href="${it.href}" style="color:${C.ink};text-decoration:none;">${it.title}</a></p>
  ${it.price ? `<p style="margin:0 0 4px;font:400 13px/1.4 ${mono};color:${C.ink};">${it.price}</p>` : ''}
  ${it.note ? `<p style="margin:0 0 6px;font:400 12px/1.5 ${mono};color:${C.muted};">${it.note}</p>` : ''}
  ${it.cta ? `<a href="${it.href}" style="font:400 12px/1.6 ${mono};color:${C.ink};text-decoration:underline;text-underline-offset:3px;text-transform:uppercase;letter-spacing:.04em;">${it.cta}</a>` : ''}
  <div class="colgap" style="height:0;"></div>
</td>`).join('');
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 26px;"><tr>${cells}</tr></table>`;
};
export const band = (inner) => `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 24px;"><tr>
<td style="background:${C.band};padding:26px 28px;">${inner}</td></tr></table>`;

// The service line under every email: the same promises as the site's announcement bar.
const service = `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="border-top:1px solid ${C.line};border-bottom:1px solid ${C.line};padding:14px 10px;text-align:center;font:400 11px/1.7 ${mono};letter-spacing:.08em;text-transform:uppercase;color:${C.ink};">
Free DHL Standard worldwide &nbsp;·&nbsp; Free DHL Express from €300 &nbsp;·&nbsp; Made in Italy
</td></tr></table>`;

const nav = [['New in', '/collections/new-in'], ['Ready to wear', '/collections/ready-to-wear'], ['Bags', '/collections/bags'], ['Trunks', '/collections/trunks']]
  .map(([t, h]) => `<a href="${SITE}${h}" style="color:${C.ink};text-decoration:none;">${t}</a>`).join(' &nbsp;&nbsp; ');

export function layout({ title, preheader, body, plain = false, top = '' }) {
  return `<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="x-apple-disable-message-reformatting" />
<meta name="color-scheme" content="light only" />
<meta name="supported-color-schemes" content="light only" />
<title>${title}</title>
<style>
  :root { color-scheme: light only; supported-color-schemes: light only; }
  body { margin:0; padding:0; background:${C.page}; -webkit-text-size-adjust:100%; }
  img { -ms-interpolation-mode:bicubic; }
  a { color:${C.ink}; }
  @media (max-width: 640px) {
    .wrap { width:100% !important; }
    .pad { padding-left:20px !important; padding-right:20px !important; }
    .col { display:block !important; width:100% !important; padding:0 !important; }
    .col img { max-width:100% !important; }
    .colgap { height:22px !important; }
    .btn { width:100% !important; }
    h1 { font-size:22px !important; }
    .nav { font-size:11px !important; letter-spacing:.06em !important; }
  }
</style>
</head>
<body style="margin:0;padding:0;background:${C.page};">
<div style="display:none;max-height:0;overflow:hidden;font-size:1px;line-height:1px;color:${C.page};">${preheader}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.page};">
<tr><td align="center" style="padding:20px 0 36px;">
<table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">
  <tr><td align="center" style="padding:14px 0 18px;">
    <a href="${SITE}" style="text-decoration:none;"><img src="${LOGO}" alt="Oberndörfer Milano" width="220" height="39" style="display:block;width:220px;height:auto;border:0;margin:0 auto;" /></a>
  </td></tr>
  ${plain ? '' : `<tr><td align="center" class="nav" style="padding:0 10px 16px;font:400 12px/1.6 ${mono};letter-spacing:.1em;text-transform:uppercase;">${nav}</td></tr>`}
  <tr><td>${rule()}</td></tr>
  ${top ? `<tr><td>${top}</td></tr>` : ''}
  <tr><td class="pad" style="padding:${plain ? '30px 40px 10px' : '34px 40px 14px'};">${body}</td></tr>
  <tr><td class="pad" style="padding:8px 40px 0;">${service}</td></tr>
  <tr><td class="pad" style="padding:26px 24px 0;text-align:center;">
    <p style="margin:0 0 12px;font:400 12px/1.7 ${mono};color:${C.muted};">{{ organization.name }}, {{ organization.full_address }}</p>
    <p style="margin:0;font:400 11px/1.8 ${mono};letter-spacing:.06em;text-transform:uppercase;color:${C.muted};">
      <a href="${SITE}/pages/contact" style="color:${C.muted};">Write to us</a> &nbsp;·&nbsp;
      <a href="https://www.instagram.com/oberndoerferco/" style="color:${C.muted};">Instagram</a> &nbsp;·&nbsp;
      {% manage_preferences %} &nbsp;·&nbsp; {% unsubscribe %}
    </p>
    <p style="margin:8px 0 0;font:400 11px/1.6 ${mono};color:${C.muted};">{% view_in_browser %}</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`;
}
