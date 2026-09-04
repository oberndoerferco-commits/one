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

### Not applied

- Captions for the four full-bleed images in `section_aol_pieces` — drafted in the
  review, but they need checking against the actual photographs first.
- Optional hero line over `hero_eAhQMJ`.
- Moving "a byproduct of the meat industry" onto the Materials & Craftsmanship page.
- Changing the page handle to `art-of-living` with a redirect from the old one.

## AI & growth review

- `docs/ai-growth-review.html` — where AI actually pays for the store, read off live
  Shopify, GA4, Search Console and Merchant Center data (pulled 4 September 2026).

Headline findings: the store took one order (€10) in twelve months against 7,877
sessions; 134 sessions reached checkout and one completed. German and Italian
commercial queries for products we actually make are drawing ~8,400 impressions a
quarter at average positions 25–48. The catalogue is indexed under up to nine
locale paths, so product pages compete with each other.
