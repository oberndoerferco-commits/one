# Redesign 2026 (draft)

The owner asked on 4 October 2026 for the whole site to look like Hermès (hermes.com/it/it) and Bottega
Veneta (bottegaveneta.com/it-it), with Bottega's home page, on a separate draft and not on the live site.

- Draft theme: **REDESIGN 2026 - draft (Bottega + Hermès)**, id 207755444549 (copy of fix 17).
  Preview: https://oberndoerferco.com/?preview_theme_id=207755444549
- Mockup: https://claude.ai/artifact/Su7DMt9vDXn2os4grspuT6 (sources in `mockup/`).

## Files on the draft theme

| File | What it is |
|---|---|
| `theme/sections/obm-panels.liquid` | Full-bleed photo panels, one or two per row, eyebrow and boxed button. "Show on" hides a row on phone or desktop. |
| `theme/sections/obm-button-stack.liquid` | Outlined buttons, stacked on a phone, in a row on a desktop. |
| `theme/sections/obm-services.liquid` | "Our services": four photographs with labels. |
| `theme/sections/obm-announcement.liquid` | Black announcement line with a close button. |
| `theme/sections/obm-footer.liquid` | Newsletter, "Where to find us", four menus (accordions on phone, columns on desktop), country, Instagram, copyright. |
| `theme/sections/obm-collection-title.liquid` | Collection name in EB Garamond italic, centred on white. |
| `theme/sections/obm-style-2026.liquid` | Site-wide touches: font face, square colour chips and buttons, serif "You may also like". |
| `theme/assets/obm-eb-garamond-italic.woff2` | EB Garamond italic, latin subset (SIL Open Font Licence). |
| `templates/index.json` | The new home page. |
| `sections/header-group.json` | Announcement, header (logo left, `main-menu-2026`, white, sticky), style section. |
| `sections/footer-group.json` | The 2026 footer only. |
| `templates/collection*.json` | Title section instead of the photo header and editorial band, white grid, sentence-case names (the 11 non-RTW collection templates share `collection.json`). |
| `templates/product*.json` | The "story chapter" section removed. |

The section files live in `theme/sections/`; nothing on the live theme renders them. The JSON in this
folder is for the draft only and must not be copied onto the live theme by itself.

## Home page (second pass, 4 October)

The owner: "too much focus on the sac, its also sold out, what about the model 017, ready to wear, home
accessories". The Sac is gone from the home page. Order now: Bag Model 017 | The Mirror Handbag (in stock),
Ready to wear | Home accessories, the Miramare lobby (Art of Living), Trunks and watch boxes | Small leather
goods, the atelier | Limited editions; buttons New in, Bags, Travel. Panels take a "Text colour" setting
(white for dark photographs, ink for light product shots).

## Logo (draft only)

The current logo sets a bold MILANO under a light wordmark, with two outlined crosses that turn to grey
noise at header size. The 2026 versions keep the exact OBERNDÖRFER letterforms from the current SVG (the
glyph paths are reused, only re-spaced: `logo/build.py`) and drop the outlined crosses:

| File | Use |
|---|---|
| `logo/obm-logo-2026.svg` | Header (A): spaced wordmark, MILANO light and spaced beneath (EB Garamond Regular). Set as the draft's logo. |
| `logo/obm-logo-2026-stacked.svg` | Footer, packaging, Instagram (C): the solid cross above. In the draft footer. |
| `logo/obm-logo-2026-one-line.svg` | Thin headers, email (B). |
| `logo/obm-logo-2026-wordmark.svg` | Wordmark alone (D). |
| `logo/obm-mark-2026.svg` / `.png` | The solid cross alone: favicon (set in the draft), embossing. |

All are in Shopify Files under the same names. The draft's settings also square the corners of buttons,
badges, inputs and cards (`config/settings_data.json`).

## Store changes already made (none visible on the live site)

- Shopify Files: `obm-2026-sac-worn.jpg`, `obm-2026-buckle-stone.jpg`, `obm-2026-atelier-zebra.jpg`,
  `obm-2026-atelier-bench.jpg` (from the Instagram account).
- Shopify Files: `obm-logo-2026.svg`, `obm-logo-2026-stacked.svg`, `obm-mark-2026.svg`, `obm-mark-2026.png`.
- New menus: `main-menu-2026`, `footer-2026-help`, `footer-2026-services`, `footer-2026-house`,
  `footer-2026-legal`. The live `main-menu` and `footer` menus are untouched.

## When the owner publishes the draft

1. Publish the theme in Shopify admin (Online Store → Themes → REDESIGN 2026 → Publish).
2. Sunglasses: set the Eyewear collection (`sunglasses`) and its products to draft or unpublish them
   from the Online Store. Until then they stay live for the current theme.
3. Open the home page in the theme editor once: every photograph can be swapped there per panel.
