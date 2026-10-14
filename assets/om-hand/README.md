# OM — the hand-drawn mark, redrawn clean

Your iPad drawing is the design. This is that design drawn properly.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `om-colour.pdf` / `.svg` | Full artwork — cyan hatch, cream keyline, black letters |
| `om-black.pdf` / `.svg` | One-colour: letters **and halo**, all black |
| `om-black-letters.pdf` / `.svg` | Letters only — for stamping or engraving small |
| `source-drawing.jpg` | The drawing as supplied |

```sh
python3 scripts/om_clean.py assets/om-hand/source-drawing.jpg assets/om-hand
```

Colours sampled from the drawing: cyan `#6cd7e1`, cream `#f4c88b`.

## Why this is not a trace

Earlier versions traced the drawing as exactly as possible and were checked by
how closely they matched it. That was the wrong target, and it guaranteed the
faults: a pen edge wobbles, a hatch stroke stops wherever the hand lifted, and
the keyline strays over an outline and takes a bite out of it. Reproducing all
of that accurately still produces a rough sketch. Every defect marked on those
versions was a faithfully reproduced feature of the drawing.

So nothing here is traced for its own sake. The drawing is **measured**, and the
measurements are drawn clean.

### The letters

The outline is rebuilt on structural nodes only — corners, and the extremes in x
and y — with **one cubic per span**, which cannot dent in the middle because it
has no interior control of its own. That took the two letters from 299 traced
segments to **116 nodes**, which is a type-design node count rather than a
tracing one.

A span is split and refitted when its single cubic strays more than 8 px from
the traced run. One cubic cannot dent, which is the point of it, but for the
same reason it cannot follow a span that genuinely bends twice — it bows
instead. On the O's flourish that bowed the thin slit between bowl and tail
into a leaf, leaving the slit at **0.73× the drawing's**; splitting brings it to
**0.96×**. The tolerance matters in both directions: at 1.6 px the splits chase
the pen wobble the rebuild exists to remove, and the O's flank goes lumpy.

The M is drawn as one half and reflected. Symmetrising the *mask* is not enough:
rebuilding on structural nodes does not place those nodes symmetrically even when
the shape is, so the M was symmetrical as pixels and not as curves. Drawing one
half and mirroring it took the M from **self-IoU 0.9719 to 0.9992**. The seam
nodes — the top notch and the centre vertex — are snapped onto the axis, where
they belong.

**The O is mirrored too.** This was the last thing to fix and the one that
mattered most. Everything before it chased agreement with the drawing, and that
is the wrong target for a finished letter: a sketch reproduced faithfully is
still a sketch, and the O's bowl read as uneven because your hand did not draw a
symmetrical one. The left half is mirrored onto the right, about an axis solved
for rather than assumed — the flourish drags the centroid right, so the axis is
found by scoring the left half alone.

The flourish is then put back. It is a **slit cut into** the bowl, not a spur
sticking out of it, so it shows up as ink the mirrored bowl has and the drawing
does not; that region in the upper right is cut away again.

The slit **stops above the flares**. In the drawing it runs down into the
right-hand flare, which leaves that flare a different shape from its mirror on
the left — they matched at only **IoU 0.57**. On a finished letter the two
flares are one shape used twice; stopping the slit above them brings the match
to **0.96**.

Neither letter's counter is an enclosed hole. The O's opens through the channel
beside its flourish and the M's open at the bottom, so the two letters are two
closed contours and no more.

### The halo

Measured off the drawing's 136 strokes:

| | drawing | drawn clean |
| --- | --- | --- |
| angle | 135.0° ± 2.65° | **135.00° ± 0.016°** |
| width | 14.3–15.7 px (two methods) | **15.0 px ± 1.4%** |
| pitch | 21.4 px between neighbours | **21.0 px** |
| white gap | 5.7–7.1 px | **6.0 px** |
| stroke count | 136 | **136** |
| median length | 85.6 px | **83.5 px** |
| total ink | — | **93% of the drawing's** |

The angle and the width are plainly meant to be constant, so they are made
constant. At exactly 135° the strokes are the anti-diagonals `x + y = c`, so the
hatch is generated as one true parallel family — even pitch everywhere, no
accumulated drift — and clipped to the band the drawing's own strokes imply.
Each stroke is a real stadium: a rectangle closed by two semicircular caps built
from quarter-circle cubics.

Length is **not** regularised: it varies 1.4× across the deciles because the halo
is deeper in some places than others, and that is the shape of the thing.

Three details that matter:

- **The band is not eroded in all directions.** Doing that eats the places where
  the halo is only one stroke deep — the O's upper left — and shortens every
  stroke besides. A stroke only has to clear the letters along its own length,
  which the dilation below guarantees.
- **The envelope is thresholded below its midpoint** (0.30, not 0.50). Smoothing
  the band's edge at the midpoint settles it on the *mean* of the drawing's
  stroke tips, so every stroke that reached past that mean loses the difference.
  The first version of this did exactly that and came out **33% short of the
  drawing's halo ink**, with every stroke 18% too short. Smoothing at a lower
  threshold keeps the edge smooth without pulling it in: the halo is now within
  **11%** on ink and **2.5%** on median stroke length.
- **The letters are cleared by construction**, not patched afterwards: the band
  has the letters-plus-gap dilated out of it before any stroke is cut, so a
  stroke cannot touch a letter. Measured clearance in the finished file: 24 px
  minimum at 400 dpi.
- **Orphan-dropping is off.** A stroke with no near neighbour looked like a
  speck the band had tapered down to, so it was dropped. It is not: wherever the
  halo is genuinely one stroke deep the rule ate it, and it emptied the O's
  upper left completely — 0 px there against the drawing's 18,163. With it off
  the halo is **136 strokes, exactly the drawing's count**, and 93% of its ink.
  The minimum stroke length already removes real specks.

### The keyline

An even ring: the letters grown and rebuilt the same way, painted under the
letters so only the ring shows. The drawing's cream measures 6.0 px, but
rebuilding the grown outline on structural nodes rounds it back in, so 6 px of
growth lands a ring only 0.63× the right weight. 10 px of growth is what
measures correctly — **0.345% of the letters box against the drawing's 0.360%**. In
the one-colour version it is dropped and the hatch's constant 9 px standoff does
its job, so there is no hand-drawn white channel to go ragged.

## Checked

At 400 dpi, with the mark 6926 px wide:

- hatch angle **135.00° ± 0.016°**, width ± 1.4%
- **127 strokes**, none touching a letter
- M mirror self-IoU **0.9992**
- two letter contours, 108 nodes

And against the drawing, at matched letter size:

- O IoU **0.974**, M IoU **0.963**
- the O's flourish slit **0.96×** the drawing's
- edge turn per step: the drawing 6.12°, this **0.00°** — straight runs stay
  straight, while the 99th percentile keeps the corners
- halo **−7%** of its ink, 136 strokes against 136
- keyline **0.345%** of the letters box against **0.360%**
