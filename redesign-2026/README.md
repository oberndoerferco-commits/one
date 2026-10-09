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

## Explore: smaller tiles, studio brass stamp (7 October)
- The brass stamp photo was cut out and set on a pale grey studio ground, as in Bottega Veneta's own stamp photo (`tools/stamp.py`, file obm-2026-brass-stamp-studio.jpg).
- Explore tiles are smaller on phone (side margin 16%) and on desktop (side margin 10%, 3% gaps).
- index.json was rebuilt from the owner's theme-editor version before this change.

## Desktop header, Gallery Dept type, Trax lookbook (7 October)
- Type as on gallerydept.com: Courier New for text, menus, product names and prices, Helvetica for headings (system fonts, nothing copied; Android falls back to Courier Prime, SIL OFL, from Google Fonts). The EB Garamond italic headings are gone.
- Desktop header as on bottegaveneta.com: "Menu" at the left (opens the menu as a panel from the left over a dimmed page), logo centred, "Search", "Login" and "Cart" as words at the right. The menu bar is hidden; its links are in the panel.
- New section `obm-lookbook` for collaborations, modelled on Gallery Dept.'s "OTW by Vans x Gallery Dept." page; used on /collections/oberndoerfer-traxnyc (template collection.oberndoerfer-traxnyc.json). The product grid is still in the template but switched off.

## Transparent header on the home page (7 October)
- The header lies over the hero film, fully clear, with the logo and words in white (the photo's top is dark); after scrolling it turns white with the black logo, as on Bottega Veneta. Uses the theme's own "transparent header on home" setting plus rules in obm-style-2026.
- The draft had inherited `.header {background-color: #ffffff !important;}` as header custom CSS, which blocked any transparency; it now applies only when the header is not transparent or has scrolled. (The live theme's custom CSS uses a 75% cream tint, rgba(245, 242, 237, 0.75), instead.)
- Hero offsets set to 0 so the film fills the whole screen under the header.

## Where to find us (7 October)
- New section `obm-locations` and template page.where-to-find-us.json: a store locator in Bottega Veneta's manner. One entry per place (photo, kind of place, name, address, note, Directions / link / Write to us, and a grey map that fits the screen), then a band for online and appointments. The text is the page's own wording, split by place. The old page's map was wider than a phone screen.

## Site check (7 October)
- Crawled 41 pages on phone and desktop, 80 internal links, and the buying flow (menu, add to cart, cart, checkout button, search, sofa enquiry). All pages load, no broken images or links, no page wider than the screen.
- Fixed: on the home page the transparent header sat above the open menu, so its close cross could not be clicked; the menu and its shade now hang off <body>.
- Fixed: on phones the footer's "Shipping to" country list ran past the right edge.
- Not bugs: the 429 / "section not found" messages were Cloudflare rate-limiting the test itself; search counts are high because Shopify also matches descriptions.

## Findability (7 October, owner's go: "yes go ahead with the SEO and image descriptions")
Store-level changes, so they apply to the live site too:
- SEO title and description written for the Crocodile Passport Holder and the wine carrier, a description for the Chrome T-shirt, and titles for two trays. (productUpdate's seo input replaces both fields, so always send title and description together.)
- 99 first product photos (the ivory studio shots) had file-name descriptions such as "Oberndorfer 3p green ivory"; each now describes the piece from its own product facts.
- The 14 Ready to Wear products, and the blue alligator wallet on Meta, were not on the Google & YouTube or Facebook & Instagram channels; now all 138 active products are on both.
- The eco-leather blog article (365 visits in 90 days, no cart adds) now links to the leather care guide, the coasters, trays, a watch box and the bags.
- New collection /collections/gifts (33 pieces: coasters, 3-watch boxes, trays, caps), published to the online store, Google and Meta, as one link for posts and ads.
- index.json synced with the owner's edit: hero button to Bags, the Sac panel now "NEW IN" to New in.

## Watch box white cutout (7 October)
- The "Leather Watch Box" covers re-framed this morning (cognac, jeans, pastel blue, pastel pink, green, yellow, navy) carried a white rectangle round the box; fixed with `tools/ivory_corners.py` (background pixels lighter than the ivory are brought down to it). Black and cognac suede covers were never affected.
- Their other 27 photos (all nine colours) were on pure white and showed as white blocks on the ivory product-page panel; repainted to the ivory with `tools/ivory_ground.py` (background and enclosed clasp gaps only). Originals kept in the session scratchpad.
- Lesson: check CDN images with their ?v= version; the bare URL can serve an older copy.

## The Atelier, second pass (7 October, owner: "go for it")
- Opens with the working-bench photograph across the full width (new `hero_image` setting in obm-gallery; owner preferred it to the stitching shot, which went back into At the bench), then the title and one line.
- No chapter index, no captions; one sentence per chapter. New order: At the bench, Made once, Miramare Palace, Trax NYC (closing line linking to the collaboration page).
- Photos in rows of one or two; a "third" becomes a half on phones. The near-duplicate Miramare lobby shot at the end was dropped.
- Owner, later: stitching photo now leads At the bench full width; the hammering shot sits beside trimming. The Atelier and Work with us are no longer hidden from search engines (seo.hidden removed). The 11 sunglasses set to Draft (hidden everywhere, reversible). Explore shows all four tiles on desktop.
- Trax photos split (owner chose option 2): plate, red Alcantara and studs moved from the Trax page to The Atelier's Trax chapter; the Trax page keeps the product shots.

## Personalisation (8 October)
- page.bespoke.json rebuilt on the Work with us layout: Initials (stamped by hand, black, gold, silver or blind, on request), Made to order, Bespoke (link to The Atelier), then the enquiry form (Initials / Made to order / Bespoke / Something else, no company field, messages arrive as "Personalisation"). Jewellery removed (owner: no jewellery). Old template kept as page.bespoke.before-2026-10-08.json.
- obm-work-with-us gained settings: source, show_company, message_label.

## 8 October 2026: Notify me, chosen size and colour

- Sold-out pieces: "Notify me" replaces "Sold out" (button, card badge, sticky bar; DE "Benachrichtigen Sie mich", IT "Avvisami" via theme translations). The button opens an email field; the request goes through the Shopify contact form (Source "Notify me", product, variant link) to the store inbox. Code: theme/snippets/obm-notify-me.liquid, rendered by the custom-liquid block `obm_notify_me` after the buy buttons in product.json and product.ready-to-wear.json.
- Chosen size on ready-to-wear: filled with the add-to-cart button colour (black, white text); other sizes are outlined boxes. Chosen colour square: outline in the same black (obm-style-2026.liquid).

## 8 October 2026, after launch (live theme 207755444549 is now MAIN)

- New working draft: 208132407621 "REDESIGN 2026 - fixes (draft)" (copy of live, made by themeDuplicate). All fixes below are in it; the owner publishes it.
- Colour dots on ready-to-wear: the size-box style had also boxed the colour swatches. Sizes and colours are styled separately now; the chosen colour gets a round ring in the add-to-cart black (label overflow made visible so the ring is not clipped).
- Homepage "Ready to wear" tile: cap replaced by the black Chrome T-shirt (back), white label.
- Files replaced in place (live at once): obm-2026-mirror-sun-phone.jpg rebuilt by hero/phone.py with a smooth, dithered wall (the old extension had streaks and blocks that read as pixelation); obm-2026-brass-stamp-studio.jpg rebuilt by tools/stamp_extend.py from the original photograph, keeping its own shadow and table.
- Footer: dark grey with white writing over the owner's chosen leopard photograph (a fur print) turned into dark greys (assets/obm-leopard-grey.jpg, tools/leopard_grey.py), scaled to cover the footer at any width, no repeat. The logo is turned white with a CSS filter. In the fixes draft (an unused assets/obm-leopard-grey.svg from the first try is still in that theme; file deletes are blocked for the tools). tools/leopard_tile.py is kept for a print that must repeat.
- About us / Art of Living / Leather care: the owner chose the first mockup layout with new photographs (mockups-favourite-layout-new-photos.jpg); not built yet.
- (later, 8 October) The owner published "fixes (draft)" (208132407621 is now MAIN). New working draft: 208139747653 "REDESIGN 2026 - fixes 2 (draft)".
  - Phone hero still looked pixelated: the CDN's automatic WebP (144 KB at 1400px) broke the dark wall into blocks. obm-panels.liquid now asks for progressive JPEG (format: 'pjpg') for full-width panels only, and compares the column count as a number (the setting is a string, so `cols == 1` / `cols == 2` never matched).
  - Footer: the owner chose a "pop" leopard reference (thick open black C/U rings around light centres). Redrawn in greys after "doesn't look the same": stroked open rings with round ends, fatter in the middle, light grey centres, tightly packed, a few loose spots. Seamless vector tile assets/obm-leopard-pop.svg (tools/leopard_pop.py), 460px on phones, 560px on desktop. The earlier fur print (obm-leopard-grey.jpg) stays in the theme unused.
  - Footer, final: the owner's own pink "pop" leopard picture converted to greys (assets/obm-leopard-ref.jpg, tools/leopard_ref.py): spots, centres and ground separated by lightness and colour, doubled with crisp edges, and made seamless by lifting each spot out whole and placing it on a wrapping canvas (touching spots split by watershed, a 100px margin of the picture left out). Ground #3b3b3b, spots #121212, centres #666-#848484. 290px per tile on phones, 380px on desktop; a soft text shadow keeps the white writing readable. obm-leopard-pop.svg (the redrawn tries) stays unused.
  - Footer readability (owner, 9 October): a 38% black layer over the leopard (linear-gradient in front of the tile), the e-mail placeholder at 80% white, divider lines at 35%, copyright at 75%.

## 9 October 2026: About us, Art of Living, Leather care rebuilt (draft 208139747653 "fixes 2")

- New section sections/obm-story.liquid (blocks: photograph, title and text, small photo and line, two photographs, products, rule, question, links, button, space), the layout of the mockup the owner chose (mockups-favourite-layout-new-photos.jpg).
- templates/page.about-us.json: IMG_7337 (SAC on the striped armchair), "Oberndörfer Milano", Material IMG_7580 / Hand IMG_0815 / Time IMG_6449, links to The Atelier and Where to find us.
- templates/page.art-of-living.json: IMG_5628 (orange sofa, blue chairs, trunk table), pair IMG_0949 (Miramare from the pool) + IMG_5638 (tall blue armchair), products blue-leather-pouf, tabel-trunk-black, italian-leather-sofa-calf-leather-orange with their real prices, button to Work with us.
- templates/page.leather-care.json: IMG_7344 (SAC on red marble), seven care rules, all 14 questions folded, word for word as in snippets/oberndoerfer-care-schema.liquid (the FAQ structured data must match the page), button to Contact.
- The old versions of the three templates are still in the live theme 208132407621 until "fixes 2" is published.

## 9 October 2026 (later): new photographs everywhere (draft 208139747653 "fixes 2")

The owner: "definitely another picture ... especially the main hero. Find the best picture." Searched Google Drive (no photographs), Canva (200px previews only) and all 2006 files in Shopify (586 lifestyle photographs reviewed). Picks, none used twice:
- Homepage hero: IMG_4981 (navy vanity case on marble under a gilded mirror), one picture for phone and desktop, focus 50/55. Full-screen panels now have a deeper shade under the line (55% black at the bottom) and a light one under the header, so the white logo and line hold over the gold and the pale marble (sections/obm-panels.liquid).
- Ready to wear tile: the black tee on taupe, with white text (the ink text disappeared on the black tee).
- About us: 449EA146 (black studded watch trunk, olive tree, morning light); Material B4C40D7E_2 (choosing a hide from the colour cards), Hand MADE_IN_ITALY (cutting the pattern), Time IMG_7604 (trunks in the workshop).
- Art of Living: IMG_5077 (orange daybed under the arched window, Miramare); pair IMG_5344 (vanity case by the pool) + IMG_5638 (tall blue armchair).
- Leather care: Leather_Duffle_bag (close-up of grained black calf) in place of the busy workbench.
- The Atelier: the daybed slot now shows IMG_5628, as the daybed photograph moved to Art of Living.
- Range settings step by 5: a focus of 42 made the About us upload fail silently; now 40. Always compare checksums after an upload.
- Screens: new-photos-phone.jpg, new-photos-desktop.jpg.
- (owner, same day) "Why did you change the hero image": the homepage hero is back as live (IMG_3258_2 on desktop, obm-2026-mirror-sun-phone on phones, focus 50/80), and the extra hero shading in obm-panels.liquid is removed again.
- Ready to wear removed from the homepage; the tile is now Trunks (IMG_9745, the watch trunk in Central Park, focus 50/75) linking to /collections/trunks.
- Art of Living: the tall blue armchair (IMG_5638) replaced by the orange trunk table (IMG_5650_3); the owner likes the rest of the page.
- About us, small photographs: Material IMG_2653 (alligator wallets), Hand ecf41f42 (hands opening a red-lined case), Time IMG_4191 (brass studs, corners and mallet).
- Art of Living: the owner loves image 11 of the old Miramare page, IMG_7959 (hand on the turquoise tufted chair); it replaces the trunk table next to the vanity case. The Atelier's slot that used it now shows IMG_1566_2 (green alligator studded trunk).

## 9 October 2026 (evening): theme update broke six pages

The owner updated the theme; Shopify made "Updated copy of REDESIGN 2026" (208208363845, now MAIN). The update reset six page templates to the default Horizon page (title and body only): page.about-us, page.art-of-living, page.leather-care, page.where-to-find-us, page.work-with-us and page.bespoke (used by /pages/personalization). Everything else checked the same as the draft (homepage, product, FAQ, bags), apart from collection, product and FAQ templates, which differ only in the header comment Shopify adds on save (same settings; Ready to wear shows the same 14 products in both, the earlier 25 vs 29 was a counting error from infinite scroll). layout/theme.liquid is the new Horizon version, without `render 'fonts'`; fonts render the same.
Fix: MAIN duplicated to 208209281349 "REDESIGN 2026 - pages restored (draft)" and the six templates uploaded from redesign-2026/templates (checksums match). Screens: pages-restored.jpg. To publish by the owner.
- The owner published 208209281349 and deleted 208208363845.
- The update also reset "Notify me" to "Sold out" (card badges and the hidden buy button) in EN, DE and IT. Fixed in 208210886981 "REDESIGN 2026 - notify me (draft)" (copy of live): locales/en.default.json from the new Horizon version with content.product_badge_sold_out and products.product.sold_out = "Notify me" (redesign-2026/locales/en.default.json), DE/IT registered again. After any future theme update: check these two strings and the six page templates.
