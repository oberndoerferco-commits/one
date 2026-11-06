# 8 mm monogram bead

Five marks from **page 101 of the tshirt design** — **OM**, the **cross
in a filled square**, **925**, the **cross in a circle** and the **cross
outline** — laid over a ball.

**[Turn it, and move the marks about →](https://claude.ai/artifact/1uiDqcXzDRe82fEYbc4pwq)**
The viewer runs the same placement maths as `scripts/om_bead.py` and
reports the spacing as you change it.

## The files

| | |
| --- | --- |
| `om-bead-8mm-pattern.stl` | even spread, marks raised 0.10 mm; ball 7.80 mm, overall **8.00 mm** |
| `om-bead-8mm-pattern-engraved.stl` | even spread, marks cut 0.10 mm in; ball **8.00 mm** |
| `om-bead-8mm-rings.stl` | the medallion composition in rings, embossed |
| `om-bead-8mm-rings-engraved.stl` | the same, engraved |

Each is one closed body of about 326,600 triangles.

```sh
python3 scripts/om_bead.py                  # even spread, embossed
python3 scripts/om_bead.py --cut            # even spread, engraved
python3 scripts/om_bead.py --rings          # the medallion
```

## The hole is blind

The bead sits on a post, so it is drilled **from one side only**: a
1.20 mm hole 4.00 mm deep, with the 118-degree point a twist drill
leaves under it. The far pole is solid metal and carries pattern like
any other part of the ball.

That is also why the spiral clears only the drilled pole. Clearing both
would put back the bald patch the spiral was chosen to avoid.

The cutter is **one revolved profile**, not a cylinder unioned with a
cone. Those two meet on a shared plane and the union leaves a sliver of
it behind — a 47-face disc of zero thickness, which was enough to cost
the engraved beads their watertightness.

## Spacing: what the two layouts actually measure

**Even spread** (`om-bead-8mm-pattern.stl`): 30 marks generated over the
whole sphere, the drilled cap dropped, **2.71 mm apart**.

**Rings** (`om-bead-8mm-rings.stl`): 28 marks, centre to centre
**1.44 to 3.06 mm**, and eight of them overlapping. The composition
reads from the poles, which is what the medallion reference wanted, but
it is not evenly spaced and the numbers say so.

A sphere has **no grid of rows that keeps one spacing**. Rows a fixed
arc apart hold a whole number of marks, so every row's spacing rounds to
a different value. A Fibonacci spiral does have the property that
matters: every point the same distance from its neighbours, poles
included.

**Order has to come from the marks, not from a cycle over the index.**
On that spiral, points that are neighbours *in space* are a Fibonacci
number apart *in index* — 5, 8 or 13 at this count — so a repeating
sequence of any of those lengths hands every neighbour the same kind.
Eight put the OMs in bands; nine broke the bands but not the clumps.
What works is colouring the neighbour graph: each mark takes the kind
none of its neighbours has and that is furthest behind its share.

## Why the square stayed square

The obvious way is to stamp into an equirectangular map and stretch by
1 / cos(latitude). That works for a mark small enough to sit at one
latitude. These do not: a 2.4 mm mark on a 4 mm ball spans about
thirty-five degrees, and cos(latitude) changes a long way across the
mark itself. One factor taken at the centre cannot straighten it, and
the square frame came out as a bowed trapezoid.

So each mark gets a frame on the sphere — east and north at its own
centre — and the map is carried into that frame by an **azimuthal
equidistant** projection, the one that keeps distance from the centre.
A square stays square because its sides stay the same length in
millimetres of arc, which is what a square means on a ball.

## Two more things a ball makes you get right

**Scale by the longer side.** The OM lockup is much wider than it is
tall. Sized by height at 2 mm it came out 6.8 mm across — most of the
way round an 8 mm ball.

**The marks are not at the page's relative sizes.** There the little
crosses are a third of the OM, which on an 8 mm ball puts them under a
millimetre and leaves gaps that read as bald. They are sized to look
equal instead.

## The profile is a laser mark, not a dome

The relief goes to full depth within 0.05 mm of the edge and stays flat
across the middle — crisp wall, flat floor, a slightly eased lip. The
domed profile used on the flat PA & CO part is wrong here; at 2.6 mm a
dome reads as a blister rather than a mark.

The square element arrives on the tile in reverse, as a filled square
with the cross knocked out of it, and it is used exactly as supplied —
a raised square panel with the cross sunk into it, which is how the
reference bracelet carries it too.

## Still open

The **minimum feature size** the supplier can hold. At 0.10 mm relief
the thin strokes of the OM and the cross outline are the parts at risk.

`renders/` holds stills of the earlier version, which was drilled all
the way through.
