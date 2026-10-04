# Oberndörfer Milano — the identity, in one page

Read this before touching the live theme "OBERNDÖRFER MILANO 1" (id 205967393093, published
7 September evening; "OBERNDÖRFER MILANO" 205924630853 is the copy before it). It is the result of the
4 September 2026 comparison against Goyard, Moynat, Valextra, Serapian, Métier, Bennett
Winch, Globe-Trotter, Au Départ, Connolly, Ettinger and Brunello Cucinelli at desktop width,
and it is what every page of the theme now follows. Scripts: `scripts/house-style-pass*.py`
(story pages) and `scripts/identity-pass.py` (site-wide); both are re-runnable.

## What the house is

An independent house making trunks, bags, small leather goods and furniture by hand in
ateliers around Milan, to order, in small numbers, with one public interior (Miramare The
Palace, Sanremo) and one place in New York (Trax NYC). The one-line version, used in the
home hero: **Trunks, bags and objects for the home. Made by hand, around Milan.**

## What the field taught us

- Trunk houses (Goyard, Moynat, Globe-Trotter, Au Départ) open on one full-bleed photograph
  with a tracked eyebrow, a serif line and an underlined link, bottom left, in white.
- The best sites use one photographic mood (Valextra: amber interiors; Au Départ: sunlit
  Paris; Métier: a yellow set) and never a low-resolution file.
- Navigation is small tracked capitals; actions are underlined text, not boxes; a filled
  button appears only where money changes hands.
- Nobody explains themselves in adjectives. Métier: "Our Story" and three plain paragraphs.
  Globe-Trotter: eyebrow, serif head, one paragraph of fact.

## Visual rules

| Element | Rule |
| --- | --- |
| Ground | `#eeede8` page, `#e5e0d7` band, `#1c1714` ink, `#4a3f35` saddle (filled buttons), `#d3cabc` lines, `#7a2e2b` accent (sale badge). Riviera blue `#cfdbe3` on Art of Living only. |
| Type | Marcellus for every heading; Inter for body, eyebrows, navigation. |
| Hero (every page) | Full-bleed photograph ≥1800px, ink gradient from the bottom (`#1c171499`), bottom-left: eyebrow in `#e5e0d7`, Marcellus 40px title in `#fbf9f6`, optional one-line dek, optional underlined link in white. The title is the page's h1. |
| Eyebrow | Inter 12px, capitals, loose tracking. Names the page, a place, a material or a chapter. |
| Statement | Marcellus 32px, centred, one or two lines, once per section. |
| Chapter head | Marcellus 32px (h3 preset), sentence case, a sentence with a claim in it. |
| Body | Inter 16px, left beside a photograph, centred only under a statement. |
| Actions | One filled saddle button per page (Add to cart, Send, Begin a commission). Everything else is an underlined text link. |
| Cards | Eyebrow shows the family (Trunks, Bags…) in mixed grids; on a collection page only the exceptions: Made to order, Limited edition, Exotic leather. |
| Photographs | Product on the sand ground; places and hands in daylight. No file narrower than 1800px in a hero or a full-width row. Low-res files still in use are listed at the end. |
| Navigation | 12px tracked capitals; logo centred. |

## Writing rules

1. A heading is a sentence with a claim, in sentence case. Labels live in the eyebrow.
2. Second person where the reader acts (Bespoke, Care); "we" for what the house does; never the brand in the third person.
3. Concrete nouns and numbers instead of adjectives: "4–6 weeks", "solid brass galvanised in gold", "nothing is cut until you have approved it".
4. Say what happens next and what it costs. Process, lead time, returns, repairs.
5. Heads of seven words or fewer; paragraphs of fifty words or fewer; one idea each. No semicolons, no dash-lists inside sentences.
6. Captions say what is in the photograph and nothing more.

## Page by page (all in the Claude theme)

- Home: eyebrow / "Made by hand, around Milan." / Discover the collections. "Collections" (was SHOP BY CATEGORY). One filled button: Begin a commission.
  7 September (`scripts/home-copy-pass.py`, text only): the two blocks the owner disliked now
  speak in the About voice. Made to order: "Nothing is cut until it is yours." and what happens
  after you choose. The house: "It began with a journey through Italy." then two sentences
  ("We went looking for what lies behind the words Made in Italy…", rewritten once more the same
  evening at the owner's "this text can be improved"), pointing at About.
- About (`scripts/about-design.py`, 7 September): photograph-led, one paragraph per chapter,
  about 450 words where there were 900. Hero on the red daybed under the arched window above
  the sea, the owner's own pick in the theme editor (the terrace trunk bag was tried first and
  rejected because it is already the Bags collection hero, and a page hero is never a
  collection hero; the Miramare lobby was tried next and swapped by the owner). Then: the
  journey beside the brass emblem being
  brazed (`Custom.jpg`); three photographs of the hands with captions (studs being set, the
  bench, the Chesterfield being buttoned); the "set of habits" statement and the three values on
  the band colour; "The workshops are fewer every year." written over the trunks on the
  workbench; the making beside the olive trunk corner; Sanremo beside the lobby ensemble (the
  owner's pick);
  the house in brief; the close over the palace hall with the high-back chair (the lounge poufs
  and the calf hide macro were tried there and rejected by the owner). No product cut-outs and no generated
  images on this page. "The hide, accounted for" moved off to Materials & Craftsmanship.
  The story the owner settled on stays word for word where it matters: the journey through
  Italy, artisans who learned from their grandparents, what lies behind the words Made in
  Italy, stud by stud, heritage / quality / attention to detail, and standing behind those
  values before mass production makes them disappear.
- Bespoke: "Made to your measure." with a line and "How a commission works". Four-step process. One filled button: Send.
  7 September: a photograph-led redraw was proposed as a mockup only
  (https://claude.ai/code/artifact/aa00ee2e-8d89-422d-b01f-cc0e788f1f05) and the owner chose
  to keep the page as it is. Do not build it unless asked.
- Art of Living: "Furniture, made the way we make a trunk." / The Miramare commission.
  7 September: the owner rearranged this page in the theme editor (hero on the gallery
  photograph without the overlay, a new chapter with the Chesterfield being buttoned, a new
  photograph in the materials chapter). The repo copy is that version, synced verbatim.
  Leave it as it is.
- Custom & Limited Editions: hero on the Trax pieces (6,000px), the four pieces shown as a
  framed grid straight after the introduction instead of a button that sends the reader away,
  the taped workshop photograph removed from the second slideshow, one filled button (Send).
- Materials, Packaging, Custom, Contact, Leather Care: same hero grammar; Contact hero on the atelier bench (was a 1232px file).

## Ready to Wear (7 September, `scripts/ready-to-wear-pass.py`)

The theme went live as "OBERNDÖRFER MILANO" on 7 September (204228231493, then the Ready to
Wear copy 205924630853, then "OBERNDÖRFER MILANO 1" 205967393093 with the home text and the
tee chapter, each published by the owner the same evening). The MCP refuses
theme file writes to whichever theme is live, so a change is uploaded to an unpublished copy and
the owner publishes it.

- Store: automated collection "Ready to Wear" (handle ready-to-wear): product type T-Shirt, Cap
  or Jacket. Anything typed that way joins it by itself, so the section grows as products are
  added. Same three types added to the "Products" catch-all. Editorial line and image (the woven
  neck label). "Ready to Wear" in the main menu (Collections) and the footer. Published to the
  Online Store and Shop channels (a collection made through the API is not, by default).
- Products: one product per print, not one per colour (the owner, 7 Sept evening: "put the
  tshirts with the same print together"). The Embroidered T-Shirt (spelling corrected from
  "Embroided") is live with Colour (Black, White) and Size (S to XXL), the same price on every
  variant, each colour's photographs on its variants, one unit per size and colour tracked at the
  Schönblickweg 1 location. The old "- White" product is archived and both old handles redirect.
  The same merge was done on the draft prints (Crest, Wordmark, Star, Gothic, Serigraph, Short
  sleeved, Initials, Constellation, Lattice; Chrome exists in black only): the black product is
  the survivor, the white product archived, its two photographs copied over. The `custom.siblings`
  metafield is gone with the merge. Where the two colours had different craft notes (Initials,
  Constellation) the note now describes both. Prices: the four prints added on 7 Sept (Initials,
  Chrome, Constellation, Lattice) are 130 EUR at the owner's request; the six older drafts stay at
  0 until the owner prices them. The five caps are live. The four puffer jackets are untouched.
  Late on 7 Sept the four new prints went live too (the owner: "add the new tshirts we added
  today to the shop"): active, on the Online Store and Shop channels, the Ready to Wear product
  template, one unit per size and colour tracked at Schönblickweg. Chrome exists in black only,
  so the Ready to Wear page shows nine T-shirt cards: five black, four white.
- Back-print shirts lead with the back (the owner, on seeing four near-identical fronts: "show
  the back photograph on the cards"): the way Palm Angels, Off-White or Represent do it, the
  printed side is the first photograph and the plain front the second. Done by reordering each
  product's media (black back, black front, white back, white front) and pointing every variant
  at its colour's back photograph, on OM, OBERNDÖRFER MILANO, Star patch, with Logo, and on the
  four older back-print drafts (Star, Gothic, Serigraph, Short sleeved). Embroidered, Crest and
  Wordmark print on the front and keep the front first.
- Pre-order (8 Sept, the owner: "make the tshirts all preorder? their not avaible yet"). Shopify
  has no pre-order without an app, so: every T-shirt is tagged `preorder`, its stock is 0 with
  overselling allowed (inventory policy Continue), so it can still be bought; the Ready to Wear
  product page shows a "Pre-order" note above the button, the button itself reads Pre-order (a
  script swaps the label and keeps it swapped), and the Made to order row explains that the order
  is paid today, dispatched when the run arrives, and can be cancelled before dispatch; the card
  eyebrow on both collection templates reads Pre-order. To end the pre-order: remove the tag and
  set real stock. No shipping date is promised anywhere, since none was given. The note was
  reworded once ("write to you with the date" read oddly to the owner): "We will email you the
  shipping date."
- The gallery shows the chosen colour only (8 Sept, the owner: "in the white product page you can
  see a picture of the black tshirt front"). Horizon's "hide unselected variant media" only hides
  the other variants' own images, so the unattached fronts still showed. The snippet
  `snippets/product-media-gallery-content.liquid` is patched (kept in the repo): with that setting
  on, a colour's photographs are its variant image plus the unattached media that follow it, up to
  the next variant image; media before the first variant image belong to every colour. The setting
  is on for the Ready to Wear product template only.
- The size row (8 Sept, the owner: "the size section looks basic"): the way Jacquemus, Zegna and
  Loro Piana set it, sizes are plain letters in a row, the chosen one with a hairline under it,
  unavailable ones struck through, the option name a tracked eyebrow. Horizon's boxed buttons are
  restyled by CSS in a custom-liquid block on the Ready to Wear template; no theme file changed.
- Known weak files: the Embroidered T-Shirt photographs (`obm-tee-tonal-*`) are soft; the white
  pair was uploaded as 26 to 29 KB JPEGs and cannot be sharpened into a good file. Replace them
  with the originals when the owner has them.
- Collection image (the tile on the home tabs and the collections page): a real photograph of the
  black Embroidered T-Shirt composited onto the taupe studio ground the owner's other collection
  tiles use (`oberndoerfer-coll-ready-to-wear-tee.jpg`, made with PIL from
  `obm-tee-tonal-black-front.jpg` and the plate sampled from the Home Accessories tile; a cap
  version was made first and replaced at the owner's request). No AI generation: there is no ChatGPT or OpenAI
  connector in the claude.ai registry, and the Higgsfield account holds no credits.
- The owner set the Ready to Wear page's hero to `sewing-machine-in-use.jpg` with a 21svh band on
  the live theme's generic collection template (7 Sept 10:35), and later restyled its cards (no
  frame, #F5F2ED ground, 20px padding). Synced to the repo; collection.ready-to-wear.json clones
  that template rather than Trunks.
- Colour swatches on the cards (7 Sept evening, the owner: "show color swatches and different
  color of one object in the collection page"): the T-shirts' Colour option is linked to the
  store's Color metaobjects (Black #000000, White #FFFFFF, both already in the store), which is
  what Horizon needs to draw a swatch. The generic and Ready to Wear collection templates carry the
  same `swatches` card block Bags and Trunks already had; hovering a swatch shows that colour's
  photograph on the card and the click goes to that variant. The same link makes the product
  page's Colour picker a pair of swatches.
- One card per colour on the Ready to Wear page (the owner, later the same evening: "make it
  possible that also the white tee is seen in collection page"). Horizon has no setting for it,
  so a small script in the hero's css block (`theme/assets-src/obm-colour-cards.js`, inlined by
  `ready-to-wear-pass.py`) clones the card for each further colour swatch, moves that colour's
  photographs to the front of the card's slideshow, ticks its swatch and points every link at its
  variant. It rebuilds the overflow-list shadow root that cloneNode drops. Only the Ready to Wear
  template carries it; on the leather collections a bag in three colours stays one card.
- The owner renamed the draft prints on 7 Sept (T-Shirt OM, T-Shirt OBERNDÖRFER MILANO, T-Shirt
  with Logo; Constellation is now also called "The Star T-Shirt", the same title as the Star). The
  handles are unchanged, so the redirects still hold. Titles are the owner's.
- Theme: collection.ready-to-wear.json (hero on the sewing machine), product.ready-to-
  wear.json (the leather page rewritten for cotton: care, made-to-order line, the "Made in Italy"
  chapter with the sewing machine as its photograph, the eyebrow fixed to Ready to Wear, and no
  "Prefer a different leather" line; the same line is also skipped for cotton types on the generic
  product page), the Collections tab on the home page, the collections list page. Template
  suffixes are set on the collection and the T-shirt and cap products. The owner published the
  draft as "OBERNDÖRFER MILANO" (id 205924630853) on 7 Sept; the first live theme (204228231493)
  is the previous copy. The neck-label photograph was removed from every T-shirt product and from
  the chapter (the owner: "remove the picture of the neck label from all tshirts").

## T-shirt photographs rebuilt from the Canva layers (8 September, `scripts/tee-photos/`)

The owner, 8 Sept, on the five new prints: "the tag looks misplaced, the side of the tshirt is
cut out, quality looks so low". The cause was in the Canva mockups ("tshirt design", DAHScXV8dgY):
the base photographs are small (black shirt 848 x 1264 px with the shirt 558 px wide; the white
pair is one 1223 x 865 px image on a black ground), the Canva crop boxes cut the sleeves, a pasted
white label graphic sat on the collar, and both base photographs carry another maker's neck label.
Fix: a Canva copy (DAHUnEGcqlA, the original untouched) exports each page's print layers alone on
a transparent ground (`ov01`..`ov10.png`, 4x page size) and the three base photographs on their own
pages (11 black front, 12 black back, 13 white). `compose.py` upscales the bases with OpenCV EDSR
x3, paints an Oberndörfer Milano label inside the collar (Marcellus), lays the print back in the
photograph's own space with the folds showing through (multiply by luminance), keys the white
shirts off the black ground onto the same warm light ground with a soft shadow, and crops every
side to a 2400 px square with air around the whole shirt. Twenty files, `obm-tee-<print>-
<colour>-<side>.jpg`, uploaded with `upload.py` (staged targets from stagedUploadsCreate) and
attached with productCreateMedia; each colour's variants point at that colour's lead side (back
for the back prints, front for the Embroidered); the old media deleted. Chrome (T-Shirt
OBERNDÖRFER MILANO) gained its White colour and five white variants (130 EUR, pre-order settings
like the rest); the white Chrome print is Canva page 6. Page mapping: 1/2 Embroidered, 3/4 OM,
5/6 Chrome, 7/8 Star patch, 9/10 Logo (lattice); odd pages black, even white.
Limit: the base photographs are still small originals upscaled; real photographs of the sample
run are the proper replacement.

## Pre-order on the older theme (8 September evening, `scripts/preorder-old-theme.py`)

The owner put "NEW WEBSITE BUG FIX 1.2" (202859512133, Horizon 4.1.3) back live: "the old theme is
live again, we still need to fix things before our version goes live. could you make the tshirts
preorder option in the current theme". On that theme the T-shirts fall back to the generic
product and collection templates (no ready-to-wear suffix there), so the pre-order note, the
"Pre-order" button label and the "Pre-order" line above the card were added to those two
templates only, on a duplicate: "NEW WEBSITE BUG FIX 1.2 - pre-order (publish me)"
(206022738245). Nothing else on that theme was touched. Everything that made the newer theme
(MILANO 5, 205996556613: gallery by colour, one card per colour, swatches, size row) stays there
for when the owner is ready.

## Four pieces of the newer design carried to the live theme (10 September)

The owner, 10 Sept: "let's transfer some things I liked about the website design we created on
the current live page": the banner with the animated pattern of the logo, the collection heroes,
the pictures between the products, and the product page design. Live theme at the time: "NEW
WEBSITE BUG FIX 2" (206022738245, Horizon 4.1.3, the pre-order copy the owner published and
renamed). Source: "OBERNDÖRFER MILANO 5" (205996556613, Horizon 4.1.5). Built on a duplicate,
"NEW WEBSITE BUG FIX 3 - transfer (publish me)" (206129004869); the owner publishes it.

- The banner is the ornament reveal, `snippets/oberndoerfer-reveal.liquid`: a field of 96 house
  marks on the house ground that holds and dissolves, first page of a session only, `?reveal=1`
  forces it. Rendered first in the body from layout/theme.liquid (that file otherwise stays the
  older theme's own).
- Collections: all thirteen collection templates copied (hero photograph, eyebrow, title, line,
  the css block with the one-card-per-colour script), plus the lifestyle tiles inside the grid
  (`snippets/oberndoerfer-grid-lifestyle.liquid`, the six-line render in
  `sections/main-collection.liquid` after the 3rd and 15th product, from the collection's
  `custom.editorial_image` metafields) and `snippets/oberndoerfer-color-grouping.liquid` (swatches
  under same-model cards). `blocks/product-title.liquid` drops the " - Colour" suffix on
  collection pages only, so the home page cards of the older theme keep their full titles.
- Product pages: product.json, product.ready-to-wear.json, product.sunglasses.json,
  `blocks/_breadcrumbs.liquid`, `sections/oberndoerfer-recommendations.liquid`, and the
  gallery-by-colour patch re-applied to the older theme's own
  `snippets/product-media-gallery-content.liquid`. `{{ settings.color_palette.color2 }}` does not
  exist on the older palette, so the chapter band colour is written as #e5e0d7 in those templates.
- Type: none. The owner, 10 Sept: "I like the font used before on current live, don't change
  it". `snippets/oberndoerfer-transfer-styles.liquid` (head, after color-palette) no longer loads
  or sets any font; it keeps only the product-page heading sizes, the quieter price and the
  edge-to-edge card rows on product pages, plus the render of the colour-grouping swatches.
- Colour dots (10 Sept, the owner: "show color instead of mini product images"): the swatch
  under a card is the colour named in the title, from a table in
  `snippets/oberndoerfer-color-grouping.liquid` (dark/light modifiers honoured), and the average
  colour of the photograph when the name is not in the table. The photograph itself is the last
  resort. Same file on the copy and in the repo.
- Dots, second pass (10 Sept, the owner: "some color swatches look cut out and table trunk is
  missing color swatches"): the row keeps 6px under it and 2px at the sides so no ring is cut at
  the card edge; a two-tone name ("Black and Yellow", "White/Blue") shows a split dot; "pastel"
  reads as light and "jeans" as denim; a bare base title ("Table Trunk", handle
  orange-tabel-trunk) joins its family with the colour read from the handle, labelled Orange.
- The grid itself stays the live theme's (10 Sept, the owner with a screenshot of the live Bags
  page: "keep this design of product grid for collection pages"): every collection template on
  the copy carries the newer hero above the live theme's own `main` section from its
  collection.bags.json (tiles on the #F5F2ED band, uppercase 14px titles, uppercase filters,
  infinite scroll, 24 per page), with two blocks added to the card: the pre-order eyebrow and
  Shopify's colour swatches. The 4-across style rule from the newer css block is dropped, card
  titles keep their full " - Colour" names, and the price and card-fill rules in the transfer
  styles apply to product pages only. Those templates are in `theme/transfer-templates/`.
- Mobile menu (10 Sept, the owner: "I also liked how the menu was on mobile version"):
  `snippets/oberndoerfer-mobile-menu.liquid` copied as is and rendered at the foot of the
  transfer styles. Same drawer markup on both Horizon versions, so it lands unchanged: 16px
  tracked top-level rows, collapsed sections that open on tap, the collection thumbnails in a
  two-column grid at one crop, full-height drawer.
- Not carried: the home page beyond the reveal, the header, the footer voice, the page-enter
  animation, the global palette. The full file list is `scripts/transfer-old-theme-files.txt`.

## Structured data on the live theme (11 September, `scripts/seo-schemas.py`)

The owner published the transfer copy as "NEW WEBSITE BUG fix 3" (206153285957) and removed
the others. Checked on the live site, everything from the transfer works. What the newer theme
still had and the live one did not was structured data only, so a copy "NEW WEBSITE BUG fix 4 -
seo schema (publish me)" (206192443717) carries it: `snippets/meta-tags.liquid` is the live
theme's own file with the schema blocks appended (collection listing and breadcrumb trail on
collection pages, breadcrumb trail on product pages, the two FAQ pages, the Organization entity);
`blocks/_breadcrumbs.liquid` and the product breadcrumb schema now skip the catch-all "Products"
and "Featured products" collections so a T-shirt reads Home > Ready to Wear > T-shirt. Nothing
visible changes except that one breadcrumb word.

The owner, 11 Sept: "I prefer the writing style in NEW WEBSITE BUG FIX 3 rather than
oberndörfer milano 5". So the FAQ and care-guide schemas are generated from the live pages' own
accordion rows (`scripts/seo-schemas.py`, all-capital rows set in sentence case), never from the
older theme's answers, and the Organization description is the admin's shop description. The
Instagram profile is added as sameAs when the theme's social settings are empty. Shopify's own
Organization block and product schema stay as they are; the new entity is additive.

## Eyewear tile and hero (11 to 15 September)

The owner: "remove the picture of the glasses getting polished and replace it with something
free from Shopify that makes sense, even an ocean picture", then, on being shown the hero,
"i meant this picture": the polishing photograph was the lifestyle tile inside the Eyewear
grid (the collection metafield custom.editorial_image), not the hero. The tile is now a
secluded beach under cliffs from Shopify's Burst library (Burst licence, free for use on a
shop), uploaded to Files as obm-eyewear-sea-cliffs.jpg; the change is a product-data change
and is live. The hero was put back to the sunglasses photograph it had before
(Gemini_Generated_Image_bc4k18bc4k18bc4k.jpg) on "NEW WEBSITE BUG fix 5", which the owner has
since published. The coast-town photograph (obm-eyewear-riviera-coast.jpg) stays in Files,
unused.

## White T-shirt edge, "You may also like", CITES (15 September)

- The white T-shirt photographs had a dark line around the shirt: the mask kept the shirt's
  own dark photo edge. `scripts/tee-photos/compose.py` now cuts the mask a little inside the
  shirt, feathers it, blends the shirt straight over the ground and sharpens once; the ten
  white images were regenerated and swapped on the five products (media ids in the product,
  file names end in -v2).
- "You may also like" on product pages used the framed card; the owner wanted the collection
  grid's card. `theme/transfer-templates/product*.json` carry the collection card (pale tile,
  uppercase title, price, colour dots) into the recommendations section of all three product
  templates. The dots needed one fix in `oberndoerfer-color-grouping.liquid`: the snippet runs
  in the head, before document.body exists, so its MutationObserver never attached and the
  recommendation cards, which arrive after load, never got their row. It now attaches on
  DOMContentLoaded.
- The sunglasses product template carried the "Why Oberndörfer Milano" heading and the CITES
  paragraph from the leather goods; removed (owner: "makes no sense to talk about cites for a
  sunglass product").

## Hoodies (15 September)

Three hoodie designs from the owner's Canva PDF, as DRAFT products in Ready to Wear: Hoodie
OBERNDÖRFER MILANO (chest wordmark, hem lockup), Hoodie OM (the initials across the back),
Hoodie with Logo (the star lattice across the back). Each in Grey, Black and White, sizes S
to XXL, 250.00 as a placeholder price, pre-order tag and continue-selling like the T-shirts.
The PDF holds one 615x922 grey photograph per side and the prints as vectors, so
`scripts/hoodie-photos/compose.py` upscales the photograph 4x (EDSR), paints out the mockup's
own neck label, remaps the cloth to black or white on the garment only, keys it onto the same
light ground as the T-shirt photographs, and re-lays the prints from an 8x render of the page
with the page's white background rectangles removed (one of them sits inside a form object).
On the black hoodie the ink is inverted, so the print is white and the OM keyline dark. The
source photograph is small, so these are good draft images rather than final ones; a proper
photograph of a sample would replace them.

## Blank pages (15 September)

Five pages rendered header and footer only: the live theme's templates/page.json had its main
section disabled, so every page on the default template (Returns, Shipping) and every page
whose named template did not exist on this theme (Materials & Craftsmanship, The Art of
Packaging, Where to Find Us) fell through to nothing. On "NEW WEBSITE BUG fix 6 - blank pages
(publish me)": page.json enabled again, and the repo's page.materials-craftsmanship.json and
page.the-art-of-packaging.json (stock Horizon sections only, images already in Files) added.
Where to Find Us, Returns and Shipping show their own page body.

## Collection and product pages (commerce pass, 5 September)

- Collection pages: the layout is the original one — framed tiles touching, the grid full
  width, the card blocks and type as they were — with two pieces added back by the owner's
  choice (`scripts/collection-hero-grid.py`): a hero carrying a photograph of the house,
  "Collection" as the eyebrow, the collection title as the h1 and its own line beneath; and
  four tiles across on desktop, three between 750 and 989px, by a style rule, since Horizon's
  card sizes give three or five and nothing between. The fuller rebuild of these pages (cards
  on the page ground, no frames, centred grid, a closing band) was tried and rejected; its
  loop in `scripts/commerce-pass.py` stays commented out.
- **A collection hero is never a photograph of a product.** The grid below it is already a wall
  of cut-outs; another one on top repeats them, and where it is one of the pieces sold on that
  page it reads as the same picture twice — Bags opened on the ostrich case that was also its
  first tile. Heroes are material, hardware, the bench or a room, and each is checked against
  that collection's own products before it is used. The eleven in use are all different from
  one another: hide macro (Bags), brass emblem (Trunks), trunk corner (New in), bench
  (all products), brass fittings (Small leather goods), a coast town above the sea (Eyewear, from 11 Sept), Miramare
  terrace (Travel), piano hall (Home), gallery and daybed (the two catch-alls), gold clasp
  (Trax NYC).
- Product page: eyebrow (family and leather, or "Limited edition"), Marcellus title, price
  in body type, variant picker, quantity and one filled "Add to cart", an atelier line, the
  description, then six accordions from existing data only: Details, Delivery, Made to order,
  Repairs, Care, Packaging. A "Made by hand" chapter follows the product; "You may also like"
  shows four framed tiles and never a crochet bag.

## Product grid tiles (5 September, owner's note on the frame)

Cards are framed tiles, in the manner of Miu Miu's grid: one hairline (#d3cabc) around each
card, tiles touching with no gap so the frames read as a single ruled grid, the photograph
edge to edge inside it, text inset 12px. The collection pages already read this way and were left alone; the home
product rows, the four pieces on Custom & Limited Editions and "You may also like" were
brought into line with them. Colour swatches sit under the price wherever a piece has them.

"You may also like" is `sections/oberndoerfer-recommendations.liquid`, the theme's section
with two changes: the crochet handbags are never recommended, and when the filter leaves
fewer than four the row is filled from the product's own family.

## Files that are still too small (replace when new photographs exist)

`17.jpg` (780px, the model in the garden — a good picture, needs the original), `bag.jpg`
(772px), `IMG_0815.jpg` (1170px), `IMG_3640.jpg` (1232px), `oberndoerfer-hero-trunk-bag-amalfi.jpg`
(900px), `oberndoerfer-miramare-arch-terrace.jpg` (1001px), the three `oberndoerfer-ig-*` files.

## Do not

Change the home hero photograph; apply the proposed menu; merge colour families; touch the
journal drafts. The owner publishes the theme.

## First image on cards, sliding rows (18 September)

The owner: "all products have to always show the first image on product card (not carousel
still) but still give the option to slide right until the end of a collection". Horizon's
theme settings product_card_carousel and show_second_image_on_hover default to on, so every
card held up to five swipeable images; both are now off in config/settings_data.json, and a
card shows its first image everywhere (home rows, collection grids, "You may also like").
The six product rows on the home page are now carousels (layout_type carousel, 16 products,
two cards wide on a phone, arrows on desktop), so a row slides to the end of its collection
instead of stopping at four. On "NEW WEBSITE BUG fix 8 - first image cards, sliding rows
(publish me)", a duplicate of the live theme with only those two files changed. The mobile
pages themselves (home, collection, product) were checked at phone width and left as they
were: two columns, no sideways overflow.

## Product chapter text, home hero photograph (18 to 19 September)

The chapter under every product ("Made by hand / Cut, stitched and finished around Milan"
plus a four-sentence paragraph) was rewritten after the owner said the text did not sit
right and, shown what Serapian and Valextra write, chose Serapian's manner: short capitalised
label, one sentence in the third person, materials named. It now reads: HANDMADE IN MILAN.
"Every Oberndörfer Milano piece is cut, stitched and finished by hand in ateliers around
Milan, in full-grain leather from Italian, French and German tanneries." The middle heading
block was removed; label, sentence, link.

The second home banner (the SAC on stone spheres, oberndoerfer-ig-pouch-spheres.jpg) was a
480x640 Instagram export stretched across the desktop width and looked pixelated. The Files
library holds no larger copy of that frame (all 1,976 images were compared by picture), but
it does hold a sibling frame from the same shoot, Sac2.heic at 5016x3346. That frame is now
the banner: full width on desktop as obm-home-sac-spheres.jpg, and a 4:5 crop centred on
the bag for phones as obm-home-sac-spheres-mobile.jpg. Both on "NEW WEBSITE BUG fix 9 -
product chapter text (publish me)", a duplicate of the live theme with only
templates/product.json and templates/index.json changed.

## Twill Pants (19 September)

A fourth ready-to-wear piece from the owner's Canva design (pages 14 to 18, one colour per
page): a garment-dyed cotton twill pant with an elasticated drawcord waist, zip fly, inseam
gusset and a tool pocket, the woven label at the back pocket. The owner gave the maker's own
description (the same model as Carhartt WIP's Flint Pant: mid-weight garment-dyed twill, 100%
organic cotton, cotton pocket lining, wash 40°C, hang dry, iron 200°C, tumble 60°C, regular
tapered fit, sizes S to XXL by waist 29–30 / 31–32 / 33–34 / 36–38 / 40 in, model 185 cm in M).
Draft product "Twill Pants" in Ready to Wear, five colours named here as Navy, Slate, Steel,
Taupe and Sage (the owner has not named them), sizes S to XXL, 290.00, pre-order tag,
continue-selling. Photographs from `scripts/pants-photos/compose.py`: each Canva tile keyed
onto the house ground with a soft shadow, front and back per colour.

## Category metafields, one card per colour, hoodies and pants live (19 September)

The owner: "add Category metafields in pants and hoodie and tshirts and all are for preorder
like tshirts", then "make all different color visible on the collection page of ready to wear?
now i can just see black T-shirts. set pants and hoodie active when you are finished and make
all colors visible as product cards, also dont forget about color swatches".

- Category metafields (the `shopify.*` standard ones) on the five T-shirts, three hoodies and
  the Twill Pants: colour (the store's Color metaobjects; Slate #4D5E69, Steel #6E7B82, Taupe
  #57524B and Sage #6D7A76 created for the pants, sampled from the photographs; Navy, Grey,
  Black and White already existed), fabric (Cotton; Cotton and Twill on the pants), age group
  Adults, target gender Unisex, care (Machine washable; the pants also Tumble dry and Ironing
  instructions, from the maker's care note). Tops: sleeve length (Short / Long), neckline
  (Crew / Hooded), top length Medium. Pants: fit Tapered leg, waist rise Mid, length Long,
  waistband Elastic + Drawstring, pockets Utility. The pants attributes needed their standard
  metaobject and metafield definitions enabled first (`standardMetaobjectDefinitionEnable`,
  `standardMetafieldDefinitionEnable`; pinning is refused for these). Missing values (Long,
  Hooded, Machine washable, Tumble dry, Ironing instructions, Twill, Tapered leg, Mid, Long,
  Elastic, Drawstring, Utility) were created with `metaobjectCreate` on the `shopify--*` types
  with their taxonomy_reference.
- Swatches: the hoodies' and pants' Colour option is now linked to `shopify.color-pattern`
  (`productOptionUpdate` with linkedMetafield and one linkedMetafieldValue per value), as the
  T-shirts' already was. That is what Horizon needs to draw a swatch on the card and on the
  product page's Colour picker.
- Pre-order parity: hoodies and pants already matched the T-shirts (tag `preorder`, stock 0,
  inventory tracked, continue selling); nothing to change. They are now ACTIVE and on the
  Online Store and Shop channels. The Ready to Wear and Products collections' rules now also
  take product types Hoodie and Pants.
- The hoodie variants that carry a back print (OM, with Logo) now point at their colour's back
  photograph, so a card and the gallery lead with the print, as the T-shirts do.
- Why only black showed: the live theme is now Horizon 4.2.0 ("NEW WEBSITE BUG fix 9 ",
  206715027781), a theme update that replaced layout/theme.liquid, sections/main-collection.liquid
  and snippets/product-media-gallery-content.liquid with stock files. With the layout stock,
  nothing rendered `oberndoerfer-transfer-styles` any more, so the reveal, the mobile menu, the
  colour dots under same-model cards and the transfer styles were all silently off, and the
  owner's Ready to Wear template edit had already replaced the hero block that carried the
  one-card-per-colour script. On the copy "NEW WEBSITE BUG fix 10 - colour cards, hoodies &
  pants" (206726988101): the two render lines are back in layout/theme.liquid, the lifestyle
  tiles in main-collection.liquid, the gallery-by-colour block in
  product-media-gallery-content.liquid (all re-applied to the 4.2.0 files, not copied from the
  old ones), and the one-card-per-colour script now lives in
  `snippets/oberndoerfer-transfer-styles.liquid`, gated by `request.path` (a rendered snippet
  does not see `collection`, so `collection.handle` is blank there). Ready to Wear now shows
  29 cards: every T-shirt in black and white, every hoodie in grey, black and white, the pants
  in five colours, each with its swatch row. The owner publishes the copy. All four files are in
  `theme/`.

## Footer monogram (19 September)

The owner: "in the footer can you put my logo as a monogram in the background? show me a
mockup before doing it", then "go with option 1" of three mockups rendered on the live footer
(monogram field, fine monogram, one large mark). The house mark from the reveal, repeated on
a staggered 112px cell at 26px, 8.5% ink, sits behind the footer's first section (newsletter
and menu); the copyright row stays plain. The tile `obm-footer-monogram-tile.png` (336px, in
Files and in `theme/assets-src/`) is used as a CSS mask so the colour is set in CSS. The block
lives in `snippets/oberndoerfer-transfer-styles.liquid` on "NEW WEBSITE BUG fix 11 - footer monogram" (206735671621), a copy of fix 10, which the owner published while the mockups were being made. A denser first
pass (marks touching) read as a checkerboard and was dropped.
- Smaller card swatches (19 Sept, the owner: "can you make color swatches a bit smaller?"):
  Horizon derives the card swatch from the product-page swatch setting, capped at 32px, and
  the cards showed 28px dots. A rule in `snippets/oberndoerfer-transfer-styles.liquid` sets
  `product-swatches .swatch` to 12px on desktop and 10px on mobile (after "make them even smaller", on "NEW WEBSITE BUG fix 12 - smaller swatches", 206736556357, since fix 11 was published in the meantime); the selected ring scales
  with it. Product-page swatches are untouched (theme setting). On the fix 11 copy.

## White T-shirts, third pass (20 September)

The owner, with a screenshot of white blobs at the sleeve seam: "all of the white tshirts have
a black lane around, quality is low and color looks off in some point". Cause: the white
shirts are keyed off a black studio ground, and the old mask was a luminance threshold. The
dark seam and fold pixels inside the shirt fell out of it, so the lighter ground showed
through as white patches; the rim pixels kept the black they were blended with in the
photograph; and the shirt's own blue cast read lavender against the warm ground.
`scripts/tee-photos/compose.py` (`key_white`) now: fills the silhouette from the outside
(flood fill through the black ground, so seams stay shirt), takes the alpha of the outer
12px band from luminance (a shirt pixel over black is shirt x alpha), continues the rim's
colour outward from the shirt's interior by inpainting with the ground masked out (a plain
divide-by-alpha left a white halo, and inpainting from the ground pulled black in), and
neutralises the cast so the shirt's median is an even white. Ten new files, suffix -v3,
replaced the -v2 media on the five T-shirts; the white variants point at their colour's lead
side as before. Resolution is unchanged: the Canva mockup is 1223px wide for two shirts, so
the file is an EDSR x3 upscale reduced to 2400px, and no sharper original exists.
- Fourth pass, same day (the owner, with tshirt_design-5.pdf: "the white T-shirts still look
  too dark in some spots, here is my reference for comparison"). The reference's white shirt
  sits at a median of 245 with the deepest folds at 233; ours had a median of 241 and folds
  down to 175. `key_white` now compresses the shirt's darkness to match, fitted on the median
  and the 5th and 1st percentiles of both (d' = 0.039 (d/0.055)^0.47, never darkening a
  pixel). The reference PDF's embedded photograph is 1102px wide for two shirts, smaller than
  the Canva source, so the pipeline is unchanged. Ten -v4 files replaced the -v3 media.

## White hoodies lifted (21 September)

The owner: "can you do the same for the hoodies white ones?". The white hoodie was an
off-white grey (median 227, folds to 195). `scripts/hoodie-photos/compose.py` (`white_curve`)
now lifts the cloth to the T-shirt reference (median 245) and compresses the shading the same
way, keeping a little more depth than on the tee so the hood, cords and pocket still read
(d' = 0.039 (d/0.11)^0.7, never darkening a pixel). Six -v3 files replaced the white -v2
media on the three hoodies; the white variants point at their colour's lead side as before.

## Touch responsiveness (23 September)

The owner: "scrolling and tapping through the website I noticed that sometimes it doesn't
react to the first or second touch, for example in menu items, tapping on products". Measured
in a phone emulation on the live home page: 2,160 swatch rows added in five seconds, forever.
`snippets/oberndoerfer-color-grouping.liquid` removed every `.ob-swatches` row and appended new
ones on each pass; those are mutations on the card, not inside a row, so the observer's
own-output check never matched, and every pass scheduled the next, eight times a second. The
main thread was busy repainting rows under the shopper's finger, and taps were lost. The
observer now ignores mutations whose only added or removed nodes are our rows, a pass runs
only when a card lacks its `data-ob-swatched` mark (a new card, or one the theme re-rendered),
and the catalog's arrival forces one full pass. On "NEW WEBSITE BUG fix 13 - touch
responsiveness" (206998372677).

## Weekly site audit (23 September)

The owner: "we need an ai agent that does weekly checks on the website and searches for bugs
or issues, then we fix it". Two parts. `scripts/site-audit/audit.mjs` loads every main page on
desktop and in an iPhone emulation and checks status, script errors, failed requests, broken
images, sideways scroll, DOM churn and long tasks while idle, and the first tap on a product
card; samples product pages; answers every internal link; reads the catalogue feed for
products without photographs, descriptions or a price; checks the email DNS. It writes
`docs/audits/<date>.json` and prints a ranked list. A Routine, "Oberndörfer Milano weekly site
audit" (trig_01W5LGpHvampodQrRJaFDhm5), fires every Monday at 05:00 UTC into a fresh session
that checks out this branch, runs the script, verifies the findings by hand, writes
`docs/audits/<date>.md`, commits and pushes, and sends the three-line summary by push and
email. It is read-only on the store; the owner decides what gets fixed. The Routine carries no
connectors, so its store-side checks are skipped unless the owner attaches Shopify in the
Routines page. First run and report: `docs/audits/2026-09-23.md`. It also found a stock
Horizon 4.2.0 fault: `snippets/measure-header-heights.liquid` declared `const section` at the
top level of an inline script, so a page with several such sections threw "Identifier
'section' has already been declared"; the declaration is block-scoped on fix 13 (in `theme/`).

## 8-Place Watch Box sale (30 September)

The owner: "discount all of the 8-Place Watch Box 50 %". Done as sale pricing on the nine
colour variants: compare-at price set to the old price (€1,682 Black Stud, €1,490 the rest),
price halved (€841 / €745). Left alone: "8-Place XL Watch Box" (€3,389, a different line, out
of stock), flagged to the owner. To end the sale: set price back to the compare-at value and
clear compare-at.

## Email programme in Klaviyo (1 October)

Order #1003 shipped (DHL 5272725931 on the fulfilment), so the parked email work started at
the owner's "let's fix emails now". The six emails are written and rendered in
`scripts/klaviyo/` (see its README): Welcome 1 "Thank you for joining us." (who makes the
pieces, the monthly letter promised, the Welcome code 5% once), Welcome 2 "A trunk begins with
a drawing." (day 3), Welcome 3 "The pieces you can order today." (day 10, pre-order terms),
Checkout 1 "We have kept your pieces." (one hour, line items from the Checkout Started event,
the one filled button), Checkout 2 "A note from the atelier." (two days, plain, no photograph,
"nothing more will follow"), and the monthly letter as a template with bracketed placeholders.
Voice per the writing rules; photographs are the site's own (brass emblem brazing, workshop
trunks, hardware corner, white tee and hoodie, Miramare ensemble, atelier bench). Footer carries
Klaviyo's unsubscribe, preferences and view-in-browser tags and the organisation address.
Shopify Marketing automations are empty, so there is no double send. Waiting on the owner:
Klaviyo account + Shopify app install + a private API key; then `build.mjs` uploads the
templates and the flows are created switched off.

## One card per model on collection pages; SAC and MODEL 017 sold out; email logo (3 October)

- The owner: "in collection pages just show one color of the model instead of all colors".
  `snippets/oberndoerfer-color-grouping.liquid` now carries `OB_ONE_PER_MODEL`, true on
  collection pages other than Ready to Wear: each colour family keeps its first card in grid
  order and hides the rest (`data-ob-hidden-colour` on the grid item, cleared and rebuilt on
  every pass); the dots under the surviving card still link to each colour's page. Home rows
  and Ready to Wear are unchanged. On "NEW WEBSITE BUG fix 14 - one card per model"
  (207723233605, copy of fix 13), verified in the preview: Bags 24 cards, 10 shown, 14 hidden,
  0 errors; Ready to Wear 28 shown; home 68 shown with 54 dot rows. Owner publishes.
- The owner: "they are out of stock, i cant ship model 017 and Sac". Available set to 0 at
  Schönblickweg for SAC (Brown, Black, Blue, Grey), SAC Alligator (Yellow, Black, Blue, Green,
  Brown), SAC Himalaya Alligator, and BAG MODEL 017 (Black, Brown, Light Blue; Pink was
  already 0). Policy was already "deny", so all show Sold out. Reversible by setting stock back.
  The owner wants a "notify me when back in stock" button: Klaviyo's Back in Stock does this
  on sold-out variants once the app is installed; to be switched on with the email build.
- Email header: the owner chose between A (the site logo as it is) and D (wordmark without
  emblems); A at 260px is in, `obm-email-logo.png`. The stacked variant stays in Files unused.

## Fix 15: the other session's shipping and FAQ copy, and the Himalaya SAC (3 October)

The owner, after publishing fix 14: "did you also include fixes from 'fix 13 + shipping & FAQ
copy (Claude)'?" No: that theme (207641739589) was made by another session on 2 October and
fix 14 was copied from fix 13. A checksum comparison of every file found three that differ:
`locales/en.default.json` (the duties and taxes lines now read "Complimentary DHL Express
shipping worldwide. EU prices include VAT; duties outside the EU are paid on delivery."),
`templates/page.faq.json` (eleven new questions: where made, materials, shipping cost,
delivery time, duties, returns within 14 days, personalisation 4–6 weeks, bespoke 2–6
months, payment methods, leather care, contact) and `snippets/oberndoerfer-faq-schema.liquid`
(the matching search data). All three were copied, byte for byte, onto "NEW WEBSITE BUG fix
15 - with shipping & FAQ copy" (207723790661, a copy of the live fix 14) and into `theme/`.
Verified in the preview: FAQ shows the eleven questions, schema has eleven entries, 0 errors.
Owner publishes.

"SAC Himalaya Alligator" is retitled "SAC Alligator - Himalaya" (handle unchanged, so no
redirect needed) so it joins the SAC Alligator family: on Bags the family now shows one card
with six colour dots (four plus "+2"). The dot for Himalaya is the photograph's average
colour, since the name is not in the colour table.

## Colour dots on product pages (fix 16, 3 October)

The owner, after publishing fix 15: "why are there no color swatches on product pages? add
it". The earlier product-page row (rendered from `blocks/_product-details.liquid` on the
September themes) was lost in the Horizon 4.2.0 update. Rebuilt as
`snippets/oberndoerfer-pdp-color-swatches.liquid`, rendered from
`oberndoerfer-transfer-styles.liquid` on product pages only. It borrows everything from the
card script through `window.obColours` (title splitter, dot painter, family lookup from the
cached catalogue, with `family()` waiting for the catalogue when it is still loading), reads
the title from the h1 and the handle from the URL, and inserts under the title: "Colour Black
· 3 colours" and one dot per colour linking to that colour's page, the current one ringed.
Ready to Wear pages, whose colours are real variants with Horizon's own swatches, are left
alone since their titles do not match a family. On "NEW WEBSITE BUG fix 16 - colour dots on
product pages" (207725855045, copy of fix 15), verified in the preview: Briefcase 3 dots, SAC
Alligator 6, 8-Place Watch Box 8, the T-shirt page no row, Bags still 9 cards, 0 errors.
Owner publishes.

## Fix 17: colours back, alligator one card, Bottega-style menu and collection pages (4 October)

The owner, after fix 16: "remove this image from my website and i noticed that you did a big
mistake, you see no other color of any product anymore, i just wanted the sac and model 017.
take back all of the color options of the products, also the model 017 and sac, just show one
model of the alligator sac." Then, with screenshots of Bottega Veneta's phone site: "I want the
menu sidebar like in the bottega website (so remove all pictures of collection that are in the
current menu bar), i also like the layout of their collection pages, also remove color swatches
from collection pages and just show them in the product pages."

The 3 October one-card rule misread "sold out" as "collapse every family". Corrected on "NEW
WEBSITE BUG fix 17 - colours back, alligator one card" (207752692037, copy of the live fix 16):
- `oberndoerfer-color-grouping.liquid`: `OB_COLLAPSE_BASES = ['sac alligator']`, so only the
  six alligator SACs show as one card on collection pages; every other family, SAC calf and
  MODEL 017 included, shows all its colour cards again. `OB_CARD_SWATCHES` is false on
  collection pages: no dot rows under cards there. Home rows keep their dots; product pages keep
  the row under the title.
- The pool photograph (`A1603CD8-9169-4741-81AE-31BBD21B10CC.jpg`, Miramare terrace with the
  sign) was the hero `hero_eAhQMJ` on Art of Living; that section is removed from
  `templates/page.art-of-living.json`. The file stays in Shopify Files.
- Menu: the header menu block's style is "text" (`sections/header-group.json`), so the drawer
  renders no collection pictures; `oberndoerfer-mobile-menu.liquid` sets the rows like the
  reference (17px, sentence case, light weight, tall rows, chevron at the right). This reverses
  the 15 August decision to keep the thumbnails, at the owner's request.
- Collection pages (`oberndoerfer-transfer-styles.liquid`, collection pages only): the count
  ("39 products") at the left and an outlined "Filter & Sort" button at the right (locale
  `actions.show_filters`), the grid-density toggle hidden, two-column grid, names in sentence
  case at 15px with the price beneath, the "Sold out" badge a small plain word at the top-left.
  The lifestyle photographs between products are off (`sections/main-collection.liquid`, the
  render lines are in a comment for restoring).
Verified on the preview: Bags 24 cards, 19 shown, the 5 other alligator colours hidden, 0 dot
rows, 0 lifestyle tiles; drawer 0 images; Art of Living no longer loads the photograph; product
page 3 dots; home 54 dot rows; 0 errors. Owner publishes.

## Redesign 2026 draft: Bottega Veneta home, Hermès touches (4 October)

The owner: "okey we need to change the whole website design, i want it to look like
hermes.com/it/it and bottegaveneta.com/it-it … Take the best from each website and make mine look
like that. Also remove the sunglasses collection. Do me a mockup … I also noticed that hermes
removed the section of bespoke and the story on the website. Remove and add everything that is
necessary to achieve the same look, but create a separate draft; don't do it on the live site."
Then: "the homepage i like how bottega did it", "also desktop and use better picture", "also check
out all of my instagram images".

Mockup (phone home, menu, collection, product; desktop home): the design canvas artifact
https://claude.ai/artifact/Su7DMt9vDXn2os4grspuT6, sources in `redesign-2026/mockup/`.

Draft theme "REDESIGN 2026 - draft (Bottega + Hermès)" (207755444549, copy of fix 17). Nothing
on the live theme or the live menus changed. What it holds is listed in `redesign-2026/README.md`;
in short:
- Home: Bottega's column of full-bleed photographs, one uppercase line and one white boxed
  button on each (`obm-panels`, two side by side on a desktop), an outlined button row
  (`obm-button-stack`), "Our services" in four photographs (`obm-services`). No bespoke block and
  no story block on the home page, as Hermès now does; bespoke stays under "Our services" in the
  footer, which is where Hermès keeps "Su misura".
- Photographs: Instagram (@oberndoerferco) gave the strongest pictures: the Sac worn, the buckle
  on stone, the zebra leather cut by hand, the atelier bench. They are in Shopify Files as
  `obm-2026-*.jpg`. Logged out, Instagram shows only the twelve newest posts, so older posts were
  not reachable.
- Header: logo left, the new menu `main-menu-2026` inline on a desktop (New in, Bags, Trunks,
  Small leather goods, Home, Travel, Ready to wear, Limited editions; no Eyewear, About or
  Bespoke), white, sticky; the black announcement line above it (`obm-announcement`).
- Footer (`obm-footer`): newsletter with one underlined field, "Where to find us", then four
  sections on new menus `footer-2026-help`, `-services`, `-house`, `-legal`: plus-accordions on
  a phone, columns on a desktop.
- Collection pages: the dark photo header and the editorial bands are replaced by the name in
  EB Garamond italic, centred on white (`obm-collection-title`, font self-hosted in
  `assets/obm-eb-garamond-italic.woff2`, SIL Open Font Licence); grid background white; card
  names in sentence case.
- Product pages: the "story chapter" section (media-with-content) is removed; colour chips are
  square and the buttons square (`obm-style-2026`); "You may also like" in the italic serif.
Sunglasses: gone from the new menus and the home page. The collection and its products stay
published until the draft goes live, so the live site's Eyewear page keeps working until then.

## Redesign 2026: second pass, the logo (4 October)

The owner on the first draft: "too much focus on the sac, its also sold out, what about the model 017,
ready to wear, home accessories, also i dont like how my logo looks like, how can me make it look better
and in general what would you improve".
- Home page of the draft: no Sac. Bag Model 017 and the Mirror Handbag open it, then ready to wear and home
  accessories, the Miramare lobby, trunks and watch boxes, small leather goods, the atelier and limited
  editions. Panels can carry ink text for light product photographs.
- Logo: the exact OBERNDÖRFER letters from the current SVG, spaced wider, MILANO light and spaced (EB
  Garamond Regular) instead of bold, no outlined crosses in the header; the solid cross above the
  wordmark for the footer, packaging and Instagram; the cross alone as favicon. Applied to the draft
  only (header, footer, favicon). Options and reasoning: the "Logo options" board of the mockup and
  `redesign-2026/README.md`.
- Draft-wide: square corners on buttons, badges, inputs and cards.

## Redesign 2026: Bottega's home structure, the film, the phone menu (4 October)

The owner: "bottega doesnt has the same structure on homepage, there is a video full screen (if you dont
find a nice video just put a full screen image) then two images, then full screen image and at the end 3
images, it all looks clean, i want to reach the same cleaness, i still think there is nicer pictures to
use"; "for logo i like a"; "my menu also has to look exactly like that" (a screenshot of Bottega's phone
menu), "for mobile".
- Draft home page: full-screen film, two images, full-screen image, three images, then the footer. The film
  is cut from the shop's own 4K video of the orange ostrich mini trunk being made. The photographs are the
  strongest in the library: Model 017 in a garden, the Mirror Handbag open in low sun (6000px camera
  originals), the Mirror Handbag carried in Tuscany, the croc trunk, the orange sofa, the hoodie.
- Logo A confirmed by the owner (already in the draft header).
- Phone menu and phone header rebuilt like Bottega's. Details: `redesign-2026/README.md`.
- Fourth pass (owner: "still not the same as Bottega's layout … the video looks off, and I like the part
  where the bag is being hammered … keep a color lane"; "I actually loved the zebra style picture"): no
  shipping line, menu centred; the film is now one continuous hammering take, warmed; two squares
  (Tuscany, the zebra); full-width Mirror Handbag with two buttons; "Our services" as three warm-grey
  still lifes with labels underneath. One palette throughout: cream, sand, chestnut, warm grey.
- Fifth pass (owner: "from pics and coloring i really liked these, for the hero image … mobile and website
  desktop"): the hero is a photograph, the Mirror Handbag in low sun on desktop and Model 017 among palm
  leaves on phones; then the buckle and the zebra, Tuscany full width, Our services.
- Sixth pass: the owner swapped the buckle square for the Sac worn photo in the theme editor, then "put
  the zebra pic down where there is 3 images". The zebra is now the middle service picture
  (Personalisation); the squares are the Sac worn and the Sac with stone spheres, the pair from the
  owner's reference screenshot; the Sac square's caption reads "The Sac" and links to Bags.
- Seventh pass: the owner put the leopard cap in the second square, the zebra full width and new pictures
  in the row of three, then asked for the words to match the pictures. Cap: "Ready to wear", links to
  Ready to Wear. Zebra: "Cut by hand in our atelier", links to Materials & Craftsmanship. Row of three,
  now headed "Explore": Personalisation (brass emblem), The Mirror Handbag (the navy one carried in a
  garden, links to that product), Home accessories (jewellery box on a studded case).
- Eighth pass: the owner wants the cream Mirror Handbag in low sun as the phone hero too. A tall version of
  the same photograph (wall and floor extended, `redesign-2026/hero/phone.py`) replaces Model 017 there.
- Ready to Wear copy (owner: "there is no leather on our tshirts, in general I don't like it"): the
  collection's description and `custom.editorial_line` now read "T-shirts, hoodies, caps and twill pants,
  made in Italy." (was "…The house mark, cut in calf leather or stitched in thread."). Store-level text, so
  the live page shows it too. The owner approved the phone hero.
- Ninth pass: zebra panel reads "The Atelier" with a "Discover more" button (Materials & Craftsmanship).
  The owner said Bottega's last row has four pictures; their own 4 October screenshot of bottegaveneta.com
  shows three (Prenota un appuntamento, Personalizzazione, Certificate of Craft) and the site blocks
  automated visits, so it could not be re-checked. A fourth tile was added anyway, as the owner asked:
  the gift boxes, "The art of packaging". Kept the owner's own editor changes (Sac square to Travel, the
  stacked cases relabelled Trunks).
- Tenth pass, checked on Bottega's phone site (bottegaveneta.com/it-it opens on a phone, the desktop
  site refuses automated visits): their last row is four pictures two by two on a phone (Appuntamento in
  negozio, Personalizzazione, Certificate of Craft, Store locator), labels in sentence case; on a desktop
  the fourth is hidden. Our row now does the same. The fourth picture is the brown leather coaster stack,
  "Home accessories" (owner: "should be something connected to home accessories"); the gift boxes are out.
  "Pictures on a desktop" (3 or 4) in the theme editor shows it on desktop too.
- Whole phone page compared with bottegaveneta.com/it-it on a phone: same order (full-screen hero, two
  pictures stacked, one tall full-width picture with buttons, four services two by two). Zebra panel now
  700px tall on phones (Bottega's is nearly a full screen); row labels 13px as theirs. Bottega also runs a
  thin black promo line above its phone header; ours stays off (the owner asked for no top line).
- Phone header (owner: the bag "too close to the menu"): the four icons were unevenly spaced (bag 11px from
  the menu icon, 25px from account) because of Horizon's 44px boxes and an overlap on the account icon.
  Now evenly spaced, about 18px apart, as on Bottega's phone header (`obm-style-2026`).
