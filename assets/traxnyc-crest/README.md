# TraxNYC crest — solid form

The crest rebuilt as a solid emblem: one continuous wide band around the
outside, no hairlines.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `traxnyc-crest-solid.pdf` | 22 pt band — the width implied by the original artwork |
| `traxnyc-crest-solid-connected.pdf` | 34 pt band — wide enough that the eagle joins the frame |
| `source-outlined.pdf` | The Illustrator original this was built from |

Both are 392.856 × 392.856 pt, 81 curve/line segments, ~5 KB, pure black fill.

Reproduce with:

```sh
python3 scripts/solidify_crest.py source-outlined.pdf out.pdf --lane 22
```

## What was wrong

The source is line art, not a solid shape. Measured around the perimeter:

| Element | In the source |
| --- | --- |
| Outer rim | continuous, uniform 8.0 pt (99.2% of 1,381 samples within 7.5–8.5 pt) |
| Inner lane | **four separate arcs**, each ~364 pt long and ~4 pt wide, each thickening to ~8.4 pt at one end |

So the outer rim was never the problem. The lane inside it is four hairline
arcs with abrupt 8 pt stubs at their ends — as a solid shape that reads as a
thin, broken ring rather than the wide continuous band on the real piece.

## How the solid form is built

Not by editing the traced outline — by rebuilding the frame from primitives.

**Symmetry.** The silhouette has exact 4-fold *rotational* symmetry and is
**not** mirror symmetric: mirroring mismatches by 2.70% of area, while a 90°
rotation mismatches by 0.00%. It is a pinwheel, the lobe centres sitting 0.6343°
off the cardinal axes. Mirroring it would corrupt the design, so only C4 is
enforced — by averaging the three structurally identical quadrants (they agree
to **0.003 pt**) and replicating one 90° sector.

**Circles.** The four lobes are true circles, r = **97.5226 pt**, centres
**86.9174 pt** from the crest centre, the four independent fits agreeing to
**0.0013 pt**. The band's inner edge is therefore emitted as exact circular arcs
(4/3·tan(θ/4) Béziers), not a traced approximation — they sit within **0.0033 pt**
of the true circles.

The band is the silhouette with a quatrefoil hole, so it is one continuous band
of uniform width the whole way round, star points included.

## Choosing the band width

22 pt is the width the original artwork implies: sweeping the width and
comparing the resulting inner shape against the source's own ring, 22.0 pt is
the minimum-mismatch fit (8.6%; the residual is the source ring bulging into the
star points, which is the thing being fixed).

There is one consequence worth knowing. At 22 pt the eagle sits entirely inside
the quatrefoil and the metal is **two separate pieces** — fine for a printed
logo, impossible to cast as one piece. The eagle only touches the frame at
≥32 pt, and even at 34 pt the necks are just 1.5–2.4 pt wide. Above ~36.07 pt
the lobes stop overlapping and the quatrefoil breaks into four circles.

Hence the two files: 22 pt for print, 34 pt if it has to be one connected piece.

## Verification

| Check | Result |
| --- | --- |
| Frame C4 symmetry, output geometry | 0.0000059% area mismatch under 90° rotation |
| Symmetrised silhouette vs. source | 0.00037% of area |
| Emitted arcs vs. true circles | max 0.0033 pt |
| Consolidated script vs. verified build | IoU 0.999997 at 432 dpi |
