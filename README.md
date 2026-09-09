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

## Assets

| File | What it is |
| --- | --- |
| `assets/tshirt-back-folded-cross/` | Vectorised folded-cross T-shirt back print (SVG/PDF/EPS, full-page and trimmed) traced from the raster original |
| `scripts/vectorize_lineart.py` | The tracer that produced it — fits straight lines to straight edges instead of tracing JPEG noise |
| `assets/logo-crest/` | Oberndörfer crest as DXF (exact splines and flattened polylines, mm, 13.229 cm artboard) |
| `scripts/pdf_to_dxf.py` | PDF→DXF converter — reads geometry out of clipping paths, keeps Béziers exact |
| `assets/traxnyc-crest/` | TraxNYC crest rebuilt as a solid emblem with one continuous wide band |
| `scripts/solidify_crest.py` | Rebuilds that crest's frame from exact circles with enforced 4-fold symmetry |
