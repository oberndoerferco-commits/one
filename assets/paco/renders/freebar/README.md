# PA & CO — letters +0.12, diamond +0.50, bar freed

`paco-50mm-freebar.pdf` and `paco-logo-freebar-dome1.20-base0.45.stl`.
50.25 × 35.96 × 1.65 mm, **seven** pieces, 650.8 mm³.

| | |
| --- | --- |
| `paco-freebar-plan.png` | near plan — the lockup as it reads |
| `paco-freebar-hero.png` | three-quarter |
| `paco-freebar-rake.png` | across the light, for the 1.65 mm profile |
| `paco-freebar-diamond.png` | the diamond, close — the tight facets |

Rebuild with:

```sh
python3 scripts/paco_weights.py --letter-grow 0.12 --diamond-scale 1.00 \
        --diamond-grow 0.50 --gap 3.48 --free-bar --out paco-50mm-freebar.pdf
python3 scripts/paco_dome.py --src paco-50mm-freebar.pdf \
        --radius 1.25 --height 1.20 --base 0.45 --stl paco-logo-freebar....stl
python3 scripts/studio/smooth_normals.py <stl> logo.bin 0.45
node scripts/studio/render.js dark grey
```

## Measured, not predicted

| | as drawn | built |
| --- | --- | --- |
| letter stroke | 0.98 | **1.22** |
| letter white | 1.04 | **0.83** |
| diamond stroke | 0.98 | **1.63** |
| smallest facet | 2.07 | **1.12** |
| diamond white | 0.67 | **0.61** |
| O to its bar | 1.05 | **0.81** |

The bench predicts the diamond at 1.98. It is 1.63. The linear rule
`stroke = size × 0.98 + 2 × weight` holds to about +0.30 of weight and
then stops: the strokes have run out of room to widen while the facets
go on closing.

| weight | predicted | measured | facet |
| --- | --- | --- | --- |
| +0.15 | 1.28 | 1.29 | 1.78 |
| +0.25 | 1.48 | 1.49 | 1.59 |
| +0.35 | 1.68 | 1.59 | 1.40 |
| +0.50 | 1.98 | **1.63** | **1.12** |

+0.35 buys all but 0.04 mm of the stroke and keeps 0.28 mm more facet.

## The bar

The O arrived tied to its bar by a 1.30 × 1.09 mm stem, all one ring.
The stem is a plain rectangle with its own vertices, so the cut is exact
rather than fitted: its two sides are the highest-reaching vertical edges
in the glyph, and the run of the ring between them is the stem and the
bar together. Dropping that run leaves the bar, closed on itself, as a
seventh piece.

Closing the bowl across the two stem roots with a straight chord would
leave a 1.30 mm flat at the lowest point of a 10 mm O. The flat is only
0.03 mm shallower than the curve — nothing would ever measure it — but
the outline is the drawing, so the bowl is drawn back in from a quadratic
through three vertices either side, corrected linearly to meet the roots
exactly rather than trading a flat for a kink.

The bar is 6.83 × 1.54 mm and 1.56 mm tall, not 1.65: at 1.54 mm wide it
runs out of width before the top of the dome and closes into a rounded
rib, which is what the dome does to every stroke narrower than 2.50 mm.
