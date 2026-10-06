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
| `theme/sections/obm-gallery.liquid` | "The Atelier" (`/pages/the-atelier`, template `page.atelier`): an editorial gallery of projects, chapters with an italic title, a sentence and photographs in rows of one, two or three. |
| `theme/sections/obm-work-with-us.liquid` | "Work with us" (`/pages/work-with-us`, template `page.work-with-us`): kinds of partnership with a photograph each, then an enquiry form through Shopify's contact form. |
| `theme/sections/obm-services.liquid` | Last row: photographs with a label under each; two by two on a phone, three (or four) in a row on a desktop. |
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

## Home page (third pass, 4 October): Bottega's structure

The owner: "bottega doesnt has the same structure on homepage, there is a video full screen (if you dont
find a nice video just put a full screen image) then two images, then full screen image and at the end 3
images, it all looks clean". The home page is now exactly that and nothing else:
1. Full-screen film: 20 seconds, muted, looping, slowed to 0.7x, cut from the 4K atelier video of the orange
   ostrich mini trunk (stitching, the handle hammered on, the finished bag). Desktop 1920x1080 and phone
   720x1280 versions are in Shopify Files (`obm-atelier-film-1920.mp4`, `obm-atelier-film-720x1280.mp4`,
   posters `obm-atelier-film-poster*.jpg`); recipe in `video/cut.sh`. Phones with reduced motion get the
   poster.
2. Two images: Bag Model 017 in the garden (`IMG_7399_2.heic`), the Mirror Handbag open in low sun
   (`IMG_3273.jpg`; closed version `IMG_3258_2.jpg` on phones).
3. Full-screen image: the Mirror Handbag carried in Tuscany (`hero-trunk-studio.jpg`), New in.
4. Three images: Trunks (`IMG_1546.heic`), Home (`obm-lane-sofa-orange-v2.jpg`), Ready to wear (hoodie).
The button row and "Our services" are gone from the home page (services stay in the footer).
`obm-panels` gained: three across, full-screen height (minus the header), a video per panel.

## Home page (fourth pass, 4 October): Bottega's exact layout and one palette

The owner, with four screenshots of Bottega's desktop home: "still not the same as Bottega's layout. Also,
the video looks off, and I like the part where the bag is being hammered instead of the stitching. If not,
take an image as the first pic instead of a video. Also, keep a color lane"; then "I actually loved the
zebra style picture". Now, top to bottom, all in one warm lane (cream, sand, chestnut, warm grey, the
zebra's black and white):
1. Header without the shipping line (Bottega has none): logo left, menu centred, icons right.
2. Full-screen film: one continuous take of the handle being hammered on (71.5-81.5 s of the 4K original),
   slowed to 0.75x, warmed and slightly desaturated, faded in and out for the loop
   (`obm-atelier-hammer-1920.mp4`, `obm-atelier-hammer-720x1280.mp4`, posters `obm-atelier-hammer-poster*.jpg`).
3. Two squares, 16px apart: the Mirror Handbag in Tuscany, and the zebra hide cut by hand.
4. Full width with two buttons (Bags, Trunks): the Mirror Handbag closed in low sun (`IMG_3260.jpg`).
5. "Our services": three still lifes on the same warm grey with the label underneath, as Bottega does
   (Book an appointment, Personalisation, The art of packaging); a swipe row on phones.
Model 017 is not on the home page any more (sold out); it is one tap away in Bags.

## Home page (fifth pass): a photograph as the hero

The owner, with screenshots of the earlier panels (Sac worn, Sac with spheres, the Mirror Handbag closed,
the buckle, the zebra, Model 017 in the garden): "from pics and coloring i really liked these, for the hero
image. I need something that looks good, mobile and website desktop." The film is off; the hero is a
photograph, chosen per screen so each crops well:
- desktop: the Mirror Handbag closed in low sun (`IMG_3258_2.jpg`, 6000x4000), framed low so the caption
  sits under the bag;
- phone: Bag Model 017 among palm leaves (`IMG_7399_2.heic`), which fills a tall screen.
Then the buckle on stone and the zebra hide (squares), the Mirror Handbag in Tuscany full width with Bags
and Trunks, and Our services. The hammering film stays in Shopify Files for later use.

### Captions matched to the owner's pictures (4 October)

The owner swapped pictures in the theme editor, then: "can you match description and collection to the
images (Eg. Cap pic has bags written, change it to ready to wear)". Each caption and link now follows its
picture:

| Place | Picture | Caption | Link |
|---|---|---|---|
| Hero | Mirror Handbag in low sun (phones too since 4 October) | Made by hand, around Milan · Discover the bags | Bags |
| Square 1 | The Sac worn | The Sac · Discover | Bags |
| Square 2 | Leopard cap | Ready to wear · Discover (ink text on the light grey) | Ready to Wear |
| Full width | Zebra hide cut by hand | Cut by hand in our atelier · Craftsmanship | Materials & Craftsmanship |
| Row of three, heading "Explore" | Brass emblem being brazed | Personalisation | Bespoke Products |
| | Navy Mirror Handbag carried in a garden | The Mirror Handbag | The Mirror Handbag - Blue |
| | Jewellery box on a studded case | Home accessories | Home Accessories |

The row is no longer services only, so its heading reads "Explore". Book an appointment and The art of
packaging are still in the footer.

Then the owner: "the mobile version should have the beige mirror bag shot as main hero image". The camera
original is landscape and a full-height phone panel is about 1:2, so a plain crop cut the bag at the sides.
`hero/phone.py` builds `obm-2026-mirror-sun-phone.jpg` (Shopify Files, 2400x5018): the same photograph with
the dark wall extended upward and the sunlit floor downward. It is the hero's phone image.

## The Atelier: a gallery of projects (4 October)

The owner: "the part of discover more, the atelier: dont put materials & craftsmanship, put a totally new
site that is like an elegant gallery of our projects, write a sentence explaining each". The zebra panel's
Discover more now opens `/pages/the-atelier`:
- Title in EB Garamond italic, a short introduction and a list of the four chapters.
- 01 Oberndörfer × Trax NYC (9 photographs), 02 Oberndörfer × Miramare Palace Sanremo (7), 03 Made once
  (6, custom pieces), 04 At the bench (9, the atelier at work). Each chapter: number, italic title, one
  sentence drawn from the existing Trax, Art of Living and Bespoke pages, a link, then its photographs
  with short captions.
- Ends with "Something you would like us to make?" and Begin a commission.
The page is a store page (published so the draft can show it, hidden from search engines with
`seo.hidden = 1`, linked from nowhere on the live site). On the live theme it would show only its title,
because the `page.atelier` template exists only in the draft. At go-live: publish the theme, then clear
`seo.hidden` on the page.

## Phone menu and header

`obm-mobile-menu-2026` (header group): Bottega's phone menu. Full-screen white; logo left; search, account,
bag and a close cross right; the main menu as rows with a chevron; then in grey Customer service, My
account, Where to find us and "Ship to:" with the country underlined (a country picker). It replaces the
theme drawer on screens under 990px. The phone header itself is laid out the same way (logo left, menu
icon last) by `obm-style-2026`.

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
