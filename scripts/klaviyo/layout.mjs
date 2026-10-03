// Shared layout for every Oberndörfer Milano email. Table-based, inline styles, 600px.
// Klaviyo tags ({% unsubscribe %}, {{ organization.full_address }}) stay literal in the output.
export const C = {
  page: '#eeede8', card: '#fbf9f6', band: '#e5e0d7', ink: '#1c1714', saddle: '#4a3f35',
  line: '#d3cabc', muted: '#6b6259', accent: '#7a2e2b',
};
export const SITE = 'https://www.oberndoerferco.com';
// The header logo (the site's own, rasterised in ink at 3x; see theme/assets-src/obm-email-logo.png).
export const LOGO = 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/obm-email-logo.png?width=780&v=1790937158';
const serif = "'Marcellus', Georgia, 'Times New Roman', serif";
const sans = "'Inter', Helvetica, Arial, sans-serif";

export const eyebrow = (t) => `<p style="margin:0 0 10px;font:500 11px/1.4 ${sans};letter-spacing:.22em;text-transform:uppercase;color:${C.muted};">${t}</p>`;
export const head = (t, size = 30) => `<h1 style="margin:0 0 18px;font:400 ${size}px/1.2 ${serif};color:${C.ink};">${t}</h1>`;
export const sub = (t) => `<h2 style="margin:0 0 14px;font:400 22px/1.3 ${serif};color:${C.ink};">${t}</h2>`;
export const p = (t) => `<p style="margin:0 0 16px;font:400 16px/1.6 ${sans};color:${C.ink};">${t}</p>`;
export const small = (t) => `<p style="margin:0 0 10px;font:400 13px/1.6 ${sans};color:${C.muted};">${t}</p>`;
export const link = (t, href) => `<a href="${href}" style="color:${C.ink};text-decoration:underline;text-underline-offset:3px;font:400 15px/1.6 ${sans};">${t}</a>`;
export const caption = (t) => `<p style="margin:8px 0 0;font:400 12px/1.5 ${sans};color:${C.muted};">${t}</p>`;
export const button = (t, href) => `
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 20px;"><tr>
<td style="background:${C.saddle};"><a href="${href}" style="display:inline-block;padding:15px 30px;font:500 13px/1 ${sans};letter-spacing:.14em;text-transform:uppercase;color:#fbf9f6;text-decoration:none;">${t}</a></td>
</tr></table>`;
export const photo = (src, alt, href = null, cap = null) => `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 22px;"><tr><td>
${href ? `<a href="${href}">` : ''}<img src="${src}" alt="${alt}" width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;" />${href ? '</a>' : ''}
${cap ? caption(cap) : ''}
</td></tr></table>`;
export const rule = () => `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-top:1px solid ${C.line};font-size:0;line-height:0;height:1px;">&nbsp;</td></tr></table>`;
// A row of two or three pieces: square studio photograph, name in serif, underlined link.
export const grid = (items) => {
  const n = items.length, cw = n === 2 ? 254 : 165, gap = n === 2 ? 12 : 12;
  const cells = items.map((it, i) => `
<td width="${cw}" valign="top" style="padding:0 ${i < n - 1 ? gap : 0}px 0 0;">
  <a href="${it.href}" style="text-decoration:none;"><img src="${it.src}" alt="${it.alt || it.title}" width="${cw}" style="display:block;width:100%;max-width:${cw}px;height:auto;border:0;background:#f5f2ed;" /></a>
  <p style="margin:10px 0 2px;font:400 ${n === 2 ? 17 : 15}px/1.3 ${serif};color:${C.ink};">${it.title}</p>
  ${it.note ? `<p style="margin:0 0 6px;font:400 12px/1.5 ${sans};color:${C.muted};">${it.note}</p>` : ''}
  <a href="${it.href}" style="font:400 13px/1.6 ${sans};color:${C.ink};text-decoration:underline;text-underline-offset:3px;">${it.cta || 'See the piece'}</a>
</td>`).join('');
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 26px;"><tr>${cells}</tr></table>`;
};
export const band = (inner) => `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 24px;"><tr>
<td style="background:${C.band};padding:28px 32px;">${inner}</td></tr></table>`;

export function layout({ title, preheader, body, plain = false }) {
  return `<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="x-apple-disable-message-reformatting" />
<title>${title}</title>
<link href="https://fonts.googleapis.com/css2?family=Marcellus&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
<style>
  body { margin:0; padding:0; background:${C.page}; -webkit-text-size-adjust:100%; }
  img { -ms-interpolation-mode:bicubic; }
  a { color:${C.ink}; }
  @media (max-width: 640px) {
    .wrap { width:100% !important; }
    .pad { padding-left:20px !important; padding-right:20px !important; }
    h1 { font-size:26px !important; }
  }
</style>
</head>
<body style="margin:0;padding:0;background:${C.page};">
<div style="display:none;max-height:0;overflow:hidden;font-size:1px;line-height:1px;color:${C.page};">${preheader}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.page};">
<tr><td align="center" style="padding:28px 12px 40px;">
<table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">
  <tr><td align="center" style="padding:18px 0 28px;">
    <a href="${SITE}" style="text-decoration:none;"><img src="${LOGO}" alt="Oberndörfer Milano" width="260" height="46" style="display:block;width:260px;height:auto;border:0;margin:0 auto;" /></a>
  </td></tr>
  <tr><td style="background:${plain ? C.page : C.card};">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td class="pad" style="padding:${plain ? '8px 36px 8px' : '36px 40px 20px'};">${body}</td></tr>
    </table>
  </td></tr>
  <tr><td class="pad" style="padding:30px 24px 0;text-align:center;">
    <p style="margin:0 0 6px;font:400 15px/1.5 ${serif};color:${C.ink};">Trunks, bags and objects for the home. Made by hand, around Milan.</p>
    <p style="margin:0 0 14px;font:400 12px/1.7 ${sans};color:${C.muted};">{{ organization.name }}, {{ organization.full_address }}</p>
    <p style="margin:0;font:400 12px/1.7 ${sans};color:${C.muted};">
      <a href="${SITE}/pages/contact" style="color:${C.muted};">Write to us</a> &nbsp;·&nbsp;
      {% manage_preferences %} &nbsp;·&nbsp; {% unsubscribe %}
    </p>
    <p style="margin:8px 0 0;font:400 11px/1.6 ${sans};color:${C.muted};">{% view_in_browser %}</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`;
}
