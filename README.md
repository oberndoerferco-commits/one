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

## T-shirt lane copy study

- `docs/the-six-shirts.html`: "The Six Shirts", the T-shirt lane read against Loro
  Piana, Hermès and Brunello Cucinelli. Four findings, two proposed renames (Gothic
  to Duomo, Serigraph to Overprint), and all six descriptions rewritten with a shared
  facts block.

Blocked on one external answer: the cloth spec from the maker (gram weight, combed or
carded, jersey type). The gram weights in the rewrites are placeholders.

## Product naming and description study (wider, superseded for the T-shirt lane)

- `docs/reading-the-houses.html`: "Reading the Houses", how Loro Piana, Hermès and
  Brunello Cucinelli name and describe products, read from their live copy, with the
  naming grammar and description skeleton extracted for the store, an audit of the
  267 published titles, four applied rewrites and a proposed model-name library.

Published as an Artifact. Jewellery is out of scope per the house standard; the
misspellings it flags (Rubin, Saphire, Nabuk, Valneza) are the one jewellery item
raised, because they sit in customer-facing titles.
