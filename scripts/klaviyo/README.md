# Klaviyo emails

`emails.mjs` holds the six emails (three welcome notes, two checkout follow-ups, the monthly
letter template) as content; `layout.mjs` is the shared frame in the house style. `node
build.mjs` writes them to `out/*.html` and, with `KLAVIYO_API_KEY` set, creates or updates the
templates in Klaviyo by name and writes `out/template-ids.json`. `node preview.mjs` renders
`out/*.png` with sample values for review. Nothing here sends an email: flows are created
switched off and the owner turns them on in Klaviyo.

## 18 October 2026: the template in the REDESIGN 2026 style

`layout.mjs` now matches the site: white page, near-black ink, Courier New for text, bold uppercase
Helvetica for headings, square black button, product photographs on the site's grey ground, a menu
row (New in, Ready to wear, Bags, Trunks) under the logo, and the service line (free DHL Standard,
free Express from €300) above the footer. All system fonts, so every mail app shows them; light
mode only, product rows stack on phones.

New: `launch-rtw` (campaign: the Ready to Wear is in stock, with prices) and `template` (every
block with placeholder text, to copy for each new campaign). Welcome 3 rewritten (no more
pre-order), checkout 1 states the shipping terms. Preview: docs/emails/2026-template-preview.jpg.

To load into Klaviyo: `KLAVIYO_API_KEY=pk_... node build.mjs` (private key with Templates
write), or paste `out/<name>.html` into Klaviyo > Templates > Create > Import HTML. Nothing is
sent from here.
