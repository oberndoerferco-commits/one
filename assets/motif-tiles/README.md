# Motif tiles — vectorised

The five colourways, vectorised from the 2048 × 2048 px PNGs.

![preview](preview.png)

| Colourway | Files | Palette |
| --- | --- | --- |
| Brown | `motif-brown.svg` / `.pdf` | `#4b360d` on white, `#4e5769` rule |
| Blue / pink | `motif-blue-pink.svg` / `.pdf` | `#6cb8e2`, `#fedff4`, black outline |
| Magenta / pink | `motif-magenta-pink.svg` / `.pdf` | `#c20063`, `#fedff4`, black outline |
| Pink / yellow | `motif-pink-yellow.svg` / `.pdf` | `#d22fa1`, `#f1e078`, black outline |
| Magenta / blue | `motif-magenta-blue.svg` / `.pdf` | `#c20063`, `#6cb8e2`, black outline |

SVGs carry `viewBox="0 0 2048 2048"` so they scale to anything; the PDFs are
512 × 512 pt. Backgrounds are transparent — the paper is not painted. Each file
is ~86–93 KB, about 2,150–2,255 curve and line segments.

Reproduce with:

```sh
python3 scripts/vectorize_flat_art.py source-brown.png . --name motif-brown
```

## How they were traced

The sources are flat colour with anti-aliased edges. The obvious approach —
trace each colour separately — leaves hairline gaps wherever two regions share
an edge, because the two traces never agree exactly. So regions are painted as
nested shapes instead:

1. Quantise to the image's own palette, merging entries within a small RGB
   distance so 254-white and 255-white do not become separate layers.
2. Take connected regions per colour and **fill their holes**, so each region is
   simply connected with exactly one outline.
3. Paint them **largest first**. A hole in a region is by construction covered
   by regions nested inside it, which are smaller and so painted later.

Nothing can gap, because whatever sits on top is drawn over a parent that
already extends underneath it. Thin drawn outlines fall out of the same rule:
an outline's filled extent is the whole enclosed shape, painted first, with the
fill painted over the middle leaving the outline showing.

Outlines are fitted with the corner-preserving line/curve fitter in
`scripts/vectorize_lineart.py`, so the straight edges of the cross stay straight,
the circle stays a smooth curve, and the spike tips stay sharp.

## Verification

Each PDF was rasterised back to 2048 px and compared against its source:

| | pixels differing by >32/255 | of those, on an edge |
| --- | --- | --- |
| Brown | 0.392% | 100% |
| Blue / pink | 0.415% | 100% |
| Magenta / pink | 0.453% | 100% |
| Pink / yellow | 0.423% | 100% |
| Magenta / blue | 0.440% | 100% |

**Every** disagreeing pixel lies on a region boundary — the differences are
anti-aliasing along edges, not shape error. No interior pixel of any region
disagrees, which is the result you want: the shapes are right and only the
one-pixel edge blend differs, as it must when replacing pixels with curves.

The three compositions are not identical to each other, so each was traced
separately rather than recoloured from one master: the brown and blue/pink
layouts match (edge IoU 0.975) as do magenta/pink and magenta/blue (0.992), but
pink/yellow differs from both, and the two groups differ from each other
(~0.68).
