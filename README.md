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
- Home hero uses `Artisan.jpg` (the atelier) instead of the Unsplash stock photograph.
- Home "Made to order" section carries the before/after slider of the Mirror bag in
  lavender and pink (the lane images, so the two frames align).
- `templates/page.the-art-of-packaging.json` is a sectioned template for The Art of
  Packaging; the page's template suffix points to it. The live theme has no such
  template, so it falls back to the plain page there.

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
