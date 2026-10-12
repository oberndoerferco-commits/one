# OM ring mark — ✠ OM ✠

The lockup for stamping or engraving on a chain link: the two capitals traced
from the gold letters, flanked by the cross from the cliché.

![preview](preview.png)

| File | Mark height | Overall |
| --- | --- | --- |
| `om-lockup-3mm.pdf` / `.svg` | 3 mm cap | 11.511 × 3.074 mm |
| `om-lockup-4mm.pdf` / `.svg` | 4 mm cap | 15.349 × 4.099 mm |
| `om-lockup-5mm.pdf` / `.svg` | 5 mm cap | 19.186 × 5.124 mm |

Everything is **flat black and a single set of filled paths** — no strokes, no
gradients, nothing a laser or a steel stamp cannot hold. Sizes are quoted as the
cap height of the letters, because that is what has to fit the band.

Rebuild, at any sizes:

```sh
python3 scripts/om_lockup.py \
    assets/om-metal-letters/reference-gold-om.jpg \
    assets/cross-cliche/source-Cliche_15cm.pdf \
    assets/om-ring-mark --cap-mm 3 --cap-mm 4 --cap-mm 5
```

`--cross-ratio` (default 0.62) sets the cross height against the cap, `--gap`
(default 0.34) the space either side of the letters.

## What survives at this size

Two things can fail on a small mark: a stroke erodes through, or a gap fills in.
Both measured off the artwork, by eroding the black until a stroke breaks and by
measuring the closest approach between separate pieces.

**Thinnest black** — erode until a stroke breaks:

| | of cap | 3 mm | 4 mm | 5 mm |
| --- | --- | --- | --- | --- |
| O | 0.0907 | 0.272 | 0.363 | 0.453 |
| M | 0.1270 | 0.381 | 0.508 | 0.635 |
| **lockup** | **0.0969** | **0.291** | **0.388** | **0.485** |

The lockup's figure is the binding one, and it is the cross's arms rather than
anything in the letters.

**Gaps** — closest approach between the four separate pieces, and the O's
counter across its waist:

| | of cap | 3 mm | 4 mm | 5 mm |
| --- | --- | --- | --- | --- |
| tightest piece-to-piece gap | 0.1997 | 0.599 | 0.799 | 0.998 |
| O counter at its waist | 0.2310 | 0.693 | 0.924 | 1.155 |

Laser engraving generally holds about 0.10 mm; a steel stamp about 0.15–0.20 mm.

**So all three sizes clear both processes**, including 3 mm, where the tightest
feature in the whole mark is 0.291 mm — still well over a stamp's limit. The
only caveat is cosmetic: the cross tapers to true points, and those will round
over slightly at any of these sizes whatever the process. It is the first thing
that will soften, and nothing can be done about it short of blunting the points
on purpose.

## A note on weight

These letters are drawn at the weight the gold *reads*, not the weight of its
silhouette — see `../om-metal-letters/README.md`. That matters more here than it
does in print: stamping and engraving both spread, so starting from the heavier
silhouette would close the O's counter and the M's notches up at ring scale.
