# OM — the hand-drawn mark, vectorised

Your drawing, traced. All three layers, as drawn.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `om-colour.pdf` / `.svg` | Full artwork — cyan hatch, cream keyline, black letters |
| `om-black.pdf` / `.svg` | One-colour: letters **and halo**, all black |
| `om-black-letters.pdf` / `.svg` | Letters only — for stamping or engraving small |
| `source-drawing.jpg` | The drawing as supplied |

```sh
python3 scripts/om_artwork.py assets/om-hand/source-drawing.jpg assets/om-hand --size 480
```

Colours sampled from the drawing: cyan `#6cd7e1`, cream `#f4c88b`.

Layer separation is by colour, which is clean here: the three are far apart in
RGB and separate with no overlap.

## How the one-colour version keeps its gap

In the black version the halo is the same hatch, painted black, and the keyline
is simply dropped — its area stays white, which is what separates the letters
from the halo. That works because **no hatch stroke touches a letter anywhere in
the drawing** (0 px of contact, measured), so the gap is already there in the
artwork and does not have to be manufactured.

`om-black-letters.pdf` drops the halo as well. At ring scale the hatch is far
too fine to survive being struck, so that is the one to send a jeweller.

## The one change: the M is symmetrical

That is the only thing altered. The M is mirrored about its own axis, and the
axis is solved for rather than assumed — the centroid was 0.2 px off, which is
enough to ghost every edge if you average without checking.

Black and cream are mirrored **together**, so the keyline keeps hugging the
letter. The cyan is left alone: mirroring a 45° hatch folds it into a chevron.

## Checked against the drawing

Every layer rendered back out at 300 dpi, re-separated by the same colour rules
and laid over the drawing, scaled so the black bounding boxes match:

| Layer | Stroke width | IoU | Median deviation | 90th pct |
| --- | --- | --- | --- | --- |
| black | 134 px | **0.971** | 0.0 px | 1.0 px |
| cyan hatch | 22 px | **0.860** | 0.0 px | 1.0 px |
| cream keyline | 13 px | **0.740** | 0.0 px | 1.0 px |

The three IoUs look very different and the deviations are identical, because
IoU on a thin band is mostly a measure of how thin the band is: a 1 px edge
placement on a 13 px keyline costs ~15% of its area and on a 134 px letter
stroke costs ~1.5%. The deviation columns are the honest figure — **the median
distance from any point on a traced edge to the drawing's own edge is 0 px, and
the 90th percentile is 1 px**, at a scale where the mark is 4780 px wide. 1 px
there is 0.02% of the width.

Two places deviate by more than 25 px. Both are at the M's right-hand terminal,
which is where making the M symmetrical moves the edge off the hand-drawn
original. That is the requested change, not a tracing error.

Smoothness, measured as the turn angle between successive steps along an edge:
the drawing's black outline turns a median of 6.1° per step, the trace 0.0° —
straight runs come out straight. The 99th percentile is unchanged (26.6° vs
25.8°), so the real corners survive: the wobble is removed and the structure is
not.

### The hatch is traced less smoothed than the letters

The letters and keyline are traced at σ 1.2, the hatch at σ 0.7, which is the
one genuine defect this check turned up. At σ 1.2 the blur closed the narrow
white gaps where two hatch strokes nearly touch and **fused three strokes into
one** — the largest connected stroke came out at 45767 px against the drawing's
21011. At σ 0.7 the count is 125 strokes against the drawing's 124 and the
largest is 21382, with the total hatch area unchanged. The lower σ also traces
the hatch *smoother* (median turn 20.9° → 14.7°), because the fused strokes had
sharp necks where they bridged.

The letters are not traced at the lower σ: there it adds nodes without adding
shape — the keyline goes from 622 to 850 segments chasing pen wobble.

## What an earlier version of this got wrong

It traced the letterforms but **rebuilt** the keyline and the hatch from
measurements, which was not asked for. Worse, it modelled the hatch as a drop
shadow — the letters translated by a fitted offset — when the drawing's hatch is
a **halo that follows the letter all the way round**. The result threw a blob
down-left and left the top-right bare, which changed the design completely.

The fitted offset came from a correlation that looked convincing: a halo
correlates well enough with a translated copy to produce a confident number. The
check that would have caught it is the one now in this file — render both at
matched scale and look. That took the black layer from IoU 0.924 to 0.961 and
fixed the shadow entirely.

`scripts/om_hand.py` keeps only the layer separation and the file writers; the
rebuild code has been deleted so it cannot be run by accident.
