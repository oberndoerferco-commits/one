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
  (all products), brass fittings (Small leather goods), polishing wheel (Eyewear), Miramare
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
