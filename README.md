# Oberndörfer Milano — store content

Working copy of content pulled from the Shopify store `oberndoerferco.com`.

## Art of Living page

- Page: `/pages/oberndorfer-x-miramare-sanremo` (titled "Art of Living")
- Template: `templates/page.art-of-living.json`
- Theme: **Claude** (unpublished, id `204228231493`)

| File | What it is |
| --- | --- |
| `theme/templates/page.art-of-living.BEFORE.json` | The template as it stood before the copy rewrite |
| `theme/templates/page.art-of-living.json` | The template as written back to the Claude theme |
| `docs/art-of-living-copy-review.html` | The copy review: diagnosis, section-by-section rewrite, voice rules |

Diff the two JSON files to see exactly which strings changed.

## Site design review

- `docs/website-design-review.html` — competitor research (nine houses), audit of the live
  store and the Claude theme, the finished blueprint, and the four decisions still open
  (merge colour families into variants, new main menu, repair promise, publishing).
- Applied to the Claude theme from that review: home page "Made to order" section
  (replaces the "Find your perfect fit" comparison slider), hero and close-band buttons,
  a "Write to the atelier" line under the product-page buy buttons, and the repair
  promise (home facts row, product facts and Delivery accordion, FAQ).

### Colour and photography (Claude theme)

- Product "lane" images (`obm-lane-*.jpg`, the first image on 128 of 129 products) all sit on
  the same warm ground, `#eeede8`. The theme's page background is set to that value so
  product tiles dissolve into the page; no product photos were recoloured.
- Palette: ink `#1c1714`, saddle `#4a3f35` (primary buttons), band `#e5e0d7`, lines and
  input borders `#d3cabc`, accent `#7a2e2b` (sale badge text only).
- Home hero is the garden photograph (`hamza-nahal-...-unsplash.jpg`), which the owner prefers.
- Home "Made to order" section carries the before/after slider of the Mirror bag in
  lavender and pink, with the exact block settings and images of the live theme (the
  owner found the lane images did not align at the divider).
- Art of Living opening band is a papery Riviera blue, `#cfdbe3`, the one place blue is
  used on the site.
- Leather Care (14 answers) and FAQ (10, headings in sentence case) are in the house
  voice; every fact from the previous versions is kept.
- `templates/page.the-art-of-packaging.json` is a sectioned template for The Art of
  Packaging; the page's template suffix points to it. The live theme has no such
  template, so it falls back to the plain page there.

### Product descriptions, cards and Materials page

- `scripts/product-descriptions.py` rewrote 58 of 129 product descriptions in the house
  voice (briefcases, sunglasses, coasters, poufs, the three-watch box, Bag 017, SAC in
  Togo and alligator, table trunks, sofas, the Trax NYC pieces, jewellery boxes). The
  other 71 were already in voice. Before/after are in `docs/product-descriptions-*.json`.
  Descriptions are store-level, so these are live.
- Product cards (collection page and the two home grids) carry an eyebrow line
  (Handmade in Italy / Made to order / Limited edition / Exotic leather) and colour dots
  linking to sibling listings, read from a `custom.siblings` JSON metafield set on the
  101 products that belong to a colour family. This gives the one-design-many-colours
  card without merging products.
- `templates/page.materials-craftsmanship.json` is now sectioned: hero on the ostrich
  trunk detail, opening chapter, four image chapters (leathers, exotics, hardware, the
  ateliers), made-to-order and care chapters, close.

### Galleries

- On every live product with three or more images, the white-background cut-out that
  sat second has been moved to the end of the gallery, so the second image is a
  different angle. 108 products; the moves are listed in `docs/media-reorder.json`.
  Store-level, so this is live.

### Decisions on record

- Colour families stay as separate products (owner declined the merge).
- The proposed main menu in the review is the agreed target. **Do not apply it** until
  the owner says so; menus are store-level and go live the moment they are saved.
- Repairs: yes, paid, quoted per piece once the atelier has seen a photograph.
- The owner publishes the Claude theme themself.

### Not applied

- Captions for the four full-bleed images in `section_aol_pieces` — drafted in the
  review, but they need checking against the actual photographs first.
- Optional hero line over `hero_eAhQMJ`.
- Moving "a byproduct of the meat industry" onto the Materials & Craftsmanship page.
- Changing the page handle to `art-of-living` with a redirect from the old one.
