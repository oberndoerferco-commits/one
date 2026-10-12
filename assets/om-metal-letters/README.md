# OM — a font from the cast gold letters

Two capitals traced from the photograph of the gold O and M on black velvet,
built into a working font and vector artwork.

![preview](preview.png)

Two styles: **Inline**, which carries the groove the metal is cast with, and
**Regular**, the plain silhouette.

| File | What it is |
| --- | --- |
| `OberndorferOM-Inline.otf` | The font with the groove — installs, maps to O and M, sets and spaces |
| `OberndorferOM-Regular.otf` | The same letters, solid |
| `*-Inline.woff2`, `*-Regular.woff2` | Same outlines for the web, 1–3 kB, for `@font-face` |
| `om-o-inline.pdf`, `om-m-inline.pdf`, `om-om-inline.pdf` | Vector artwork, 480 pt cap height |
| `om-o.pdf`, `om-m.pdf`, `om-om.pdf` | The solid versions |
| `om-*.svg` | All of the above as SVG |
| `specimen.pdf` | A specimen set in both styles |
| `serif-check.png` | The M's top serifs, photo above, traced glyph below, on the photo's own pixel grid |
| `reference-gold-om.jpg` | The source photograph |

Rebuild with:

```sh
python3 scripts/metal_letters_font.py \
    assets/om-metal-letters/reference-gold-om.jpg assets/om-metal-letters --size 480
```

## How the letters were lifted off the photograph

A luminance threshold does not work here: the letters' own shadowed sides are as
dark as the velvet, so it cuts them off. The velvet is **neutral**, though, and
cast gold is not — thresholding **chroma** (max minus min of RGB) gives exactly
two components, with no holes and no spill, and is stable anywhere between 18
and 40. The outline is then taken from the chroma image's own anti-aliased edge
rather than from the binary mask, so edge positions are sub-pixel; interior and
exterior are forced solid three pixels either side of the boundary so the
hammered texture inside the metal cannot raise a contour of its own.

## What was smoothed, and what was kept

Very little. The hammering is *inside* the metal; the cast **outline** is crisp,
and it has real corners — the sharpest being where each serif's tip turns into
its bracket. An earlier version of this smoothed hard enough to erase the
outline's small irregularities, and that rounded those corners off; the serifs
stopped reading as serifs. The tolerances are now tight (`sigma 0.8`,
`line-tol 0.6`, `curve-tol 0.4`) and the corner-preserving fit does the work.
The M comes out as 22 straight segments and 127 curves, the O as 4 and 90.

Checked by round-trip rather than by eye: rasterising the finished PDF back onto
the photograph's own pixel grid and comparing against the mask gives an **IoU of
0.991 for the M and 0.972 for the O**. The O's residual is the left-right mirror
below, which is deliberate.

The fit also keeps what is real. The **O is not an oval**: each flank has a
genuine angular vertex, clearly there in the casting.

The **O is mirrored left-right**. It is drawn with a vertical stress and
measures symmetric to within 1–2 px across, so that residual is camera rather
than design (mean mirror residual 0.011 px). It is **not** mirrored
top-to-bottom: doing that costs it 3.8 px of height, and that height is its
overshoot — the amount a round letter has to exceed the cap line by to look the
same size as a flat-topped one. As cast it overshoots by 1.05% of the cap height
at each end, which is right where a type designer would put it.

The **M is left alone entirely**: its V is deliberately thick on the left stroke
and thin on the right, and mirroring would destroy that.

## The inline

The castings are bevelled, and the bevel leaves a groove running parallel to the
whole outline — counters included. Measuring it rather than guessing: take the
luminance inside each letter, divide out the lighting gradient with a heavily
blurred copy of itself, and plot the result against distance from the outline.
The profile is unambiguous — a bright peak at 3–4 px (the raised rim catching
the light), then a trough bottoming out at 17–20 px (the groove), then back to
field level by 26 px.

So the groove is cut at **18 px inset, 8 px wide** — 39 and 18 units at a cap
height of 700. It is a constant offset because the casting's is: the groove is a
moulded chamfer, not a drawn line, which is why it holds its distance around
every bracket and serif.

The inline nests four contours deep — outline, groove outside, groove inside,
counter — so contour direction has to alternate with nesting depth rather than
simply "biggest one is the outer". Getting that wrong fills the counters in.

## Font metrics

| | |
| --- | --- |
| Units per em | 1000 |
| Cap height | 700 (set by the M's flat top and foot) |
| O | 687 units wide, overshooting the cap band by 7 units top and bottom |
| M | 755 units wide |
| Sidebearings | 45 units a side — half the letter gap in the photograph |
| Space | 300 units |

The O's overshoot is what it was cast with, centred on the same cap band as the
M rather than copied from where the letter happened to lie on the velvet.

The family name is a default. Pass `--family "Your Name"` to change it; the
PostScript name, full name and unique identifier all follow from it.

`--inset` and `--groove` move the inline, in source pixels. `--sigma`,
`--line-tol` and `--curve-tol` set how closely the outline follows the metal;
raising them smooths more, at the cost of the serif corners. `--symmetry`
takes `x` (the default), `xy` or `none`.
