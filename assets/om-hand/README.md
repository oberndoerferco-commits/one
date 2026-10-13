# OM — the hand-drawn mark, vectorised

Your drawing, traced. All three layers, as drawn.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `om-colour.pdf` / `.svg` | Full artwork — cyan hatch, cream keyline, black letters |
| `om-black.pdf` / `.svg` | One-colour: the letterforms, solid black |
| `om-black-shadow.pdf` / `.svg` | One-colour with the hatch, also black |
| `source-drawing.jpg` | The drawing as supplied |

```sh
python3 scripts/om_artwork.py assets/om-hand/source-drawing.jpg assets/om-hand --size 480
```

Colours sampled from the drawing: cyan `#6cd7e1`, cream `#f4c88b`.

Layer separation is by colour, which is clean here: the three are far apart in
RGB and separate with no overlap.

## The one change: the M is symmetrical

That is the only thing altered. The M is mirrored about its own axis, and the
axis is solved for rather than assumed — the centroid was 0.2 px off, which is
enough to ghost every edge if you average without checking.

Black and cream are mirrored **together**, so the keyline keeps hugging the
letter. The cyan is left alone: mirroring a 45° hatch folds it into a chevron.

Measured against the drawing, the traced black layer registers at **IoU 0.961**.

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
