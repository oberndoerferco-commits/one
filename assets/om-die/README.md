# OM leather cutting die

Two layers, two letters. **TOP** is the mark, cut as the O and the M.
**UNDER** is the backing, one piece per letter, offset outward. Nothing
joins the O to the M on either layer.

| | |
| --- | --- |
| `om-die-both.dxf` | R12 DXF, layers TOP and UNDER — the production file |
| `om-die-drawing.pdf` | A3, dimensioned, for the die maker |
| `om-die-both.pdf` / `.svg` | both layers |
| `om-die-top.pdf`, `om-die-under.pdf` | one layer each |

## This set: 80 mm finished

| | |
| --- | --- |
| Finished patch | **80.00 × 67.46 mm** |
| Letters | 76.00 mm wide |
| Backing | +2.00 mm all round, one per letter |
| Thinnest line | **2.00 mm, held everywhere** |
| Ink added to get there | +6.2% |
| Counters | 9 |
| Gap, O to M | 6.09 mm |
| Backing to backing | 2.09 mm |

```sh
python3 scripts/om_die.py --overall 80 --min 2.0 --notch 0.8 \
        --offset 2.0 --fatten --separate
```

`../om-die-4mm/` is the same mark at a 4.00 mm minimum, which needs a
140 mm patch.

## What "thinnest line" has to mean

![what each minimum costs](how-thick-it-goes.png)

An earlier version of this die went out with the thin parts untouched at
0.03 mm and everything else 40% thicker. Two faults, and the second is
why the first shipped.

**The fattening skipped the thin parts on purpose.** It excluded
medial-axis points near the end of a branch — which is exactly where a
hairline serif lives. So it raised the medium strokes it could reach and
left the hairlines alone.

**The figure it reported was the 5th percentile of the stroke width.** A
percentile can say most of a shape is thicker than X. It cannot say
nothing is thinner. Three per cent of the mark sat under the minimum and
it measured as a pass.

The test now is: **does a disc of the minimum width reach every part of
the shape.** Not an average, a test — and it paid for itself at once by
catching a closing, newly written, that eroded the background instead of
the shape and doubled the ink.

What it still flags is acute inside corners, where a disc cannot get
into the angle although nothing there is thin. On this mark 425 of 427
such patches were five pixels or fewer and none had any medial axis
inside them. So what gets reported is the size of the worst patch, which
falls from **59.8 mm² as drawn to 0.23 mm² enforced** — and `--slack`
sits between the two.

## How the thickening works

The shape, unioned with a disc of radius r centred on every medial-axis
point whose own disc is smaller than r.

Every point of a shape lies inside some maximal disc of its medial axis.
If that disc is already r or bigger the point is fine; if it is smaller,
its centre is in the thin set, so the point lies within r of a thin
centre and the dilation covers it. That is the whole proof, and
excluding anything from the thin set breaks it.

Nothing already thick is enlarged — at 80 mm the thickest stroke does
not move while the ink grows 6.2%. Compare the alternatives: a uniform
swell reaches the same minimum but closes the gap between the O and the
M from 6.50 to 3.88 mm and takes the counters from ten to two; an
opening, which drops what is too thin instead of raising it, breaks the
O into separate arcs.

## Two more things worth keeping

**Notches and strokes are different constraints.** `--notch` fills gaps
a steel rule cannot be bent into; `--min` sets the thinnest ink. Tying
them together — which the first version did — fills the counters as
well, and the counters are what make an O an O.

**One bitmap, traced once.** The old pipeline went vector → raster →
vector for each operation and lost a little of the outline each time.
All the morphology runs on a single bitmap now.

**The backings are offset per letter and never unioned.** Offsetting the
pair together welds them the moment the offset passes half the gap,
which at 80 mm is 3.04 mm — inside the range anyone would reach for. The
script refuses an offset that would overlap and says what the limit is.
