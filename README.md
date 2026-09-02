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
  and a "Write to the atelier" line under the product-page buy buttons.

### Not applied

- Captions for the four full-bleed images in `section_aol_pieces` — drafted in the
  review, but they need checking against the actual photographs first.
- Optional hero line over `hero_eAhQMJ`.
- Moving "a byproduct of the meat industry" onto the Materials & Craftsmanship page.
- Changing the page handle to `art-of-living` with a redirect from the old one.
