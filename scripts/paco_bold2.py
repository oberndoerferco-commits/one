#!/usr/bin/env python3
"""Bold the PA & CO logo and rebuild the O-to-bar junction.

Two things defeat a plain offset here.

First, offsetting adds the offset to every radius already in the outline.
The bar's corners carry a 0.055 mm fillet, invisible at 50 mm; a 0.40 mm
outset returns it as 0.455 mm, a visibly rounded bar end. So fillets too
small to see are squared off first (paco_unround).

Second, the bar sits 0.88 mm below the bowl of the O. Raising the thinnest
stroke from 0.25 mm to 1 mm costs 0.75 mm of that gap from the two facing
edges, leaving 0.13 mm, which no die will form: the junction fills in and
reads as a blob. The gap cannot reach 1 mm at 50 mm by any amount of
bolding, because it starts under 1 mm. Either the bar moves down, or the
logo runs bigger. --drop does the first, --scale the second.

    python3 scripts/paco_bold2.py --grow 0.270 --scale 1.8 --out ...   (1.00 mm)
    python3 scripts/paco_bold2.py --grow 0.150            --out ...   (0.57 mm)

--drop exists only to record that lowering the bar does not work. It buys
back the O-to-bar gap and leaves every other gap exactly as short, so a
file built with it fails somewhere else: at --grow 0.40 --drop 0.95 the
O-to-bar gap reads 1.03 mm and the C-to-O gap reads 0.74 mm. Default 0.
"""
import argparse, sys, os
import numpy as np, pymupdf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import subpaths, assemble, write, MM
from paco_unround import unround

MITRE = dict(join_style=2, mitre_limit=6.0)


def classify(rings):
    """Split the artwork into the letters, the bar, and the old stem."""
    letters, bar, stem = [], None, None
    for r in rings:
        p = Polygon(r).buffer(0)
        x0, y0, x1, y1 = p.bounds
        w, h = x1 - x0, y1 - y0
        if x0 > 41 and y0 > 33.4 and w > 4 and h < 1.0:
            bar = r                      # the rule under the O
        elif x0 > 44 and 32.5 < y0 < 33.2 and w < 1.3 and h < 1.3:
            stem = r                     # the connector, redrawn below
        else:
            letters.append(r)
    return letters, bar, stem


def build(src, grow, drop, scale, stem_w, out):
    d = pymupdf.open(src); pg = d[0]
    w_mm, h_mm = pg.rect.width / MM, pg.rect.height / MM
    rings = [unround(np.array(s)) for s in subpaths(pg)]
    letters, bar, stem = classify(rings)
    if bar is None:
        raise SystemExit('bar not found')

    L = assemble(letters)
    B = Polygon(bar).buffer(0)
    if scale != 1.0:
        L = affinity.scale(L, scale, scale, origin=(0, 0))
        B = affinity.scale(B, scale, scale, origin=(0, 0))
        w_mm *= scale; h_mm *= scale
    # the growth is an absolute amount at final size: scaling the artwork
    # already thickens the strokes, so it must not be scaled again
    g = grow

    Lb = L.buffer(g, **MITRE)
    Bb = affinity.translate(B.buffer(g, **MITRE), 0, drop)

    # the O is the right-most shape; the stem drops from the low point of its bowl
    O = max(Lb.geoms, key=lambda s: s.bounds[2]) if hasattr(Lb, 'geoms') else Lb
    ox0, oy0, ox1, oy1 = O.bounds
    low = [c for c in O.exterior.coords if c[1] > oy1 - 0.02]
    cx = float(np.mean([c[0] for c in low]))
    bx0, by0, bx1, by1 = Bb.bounds
    # in the original the stem and the bar are the same weight (0.52 mm each),
    # so the stem follows the bar rather than taking a figure of its own
    if stem_w <= 0:
        stem_w = by1 - by0
    S = box(cx - stem_w / 2, oy1 - 0.25, cx + stem_w / 2, by0 + 0.25)

    geom = unary_union([Lb, Bb, S])
    H = max(h_mm, by1 + 0.0)
    n = write(geom, w_mm, H, out)
    shapes = len(list(geom.geoms)) if hasattr(geom, 'geoms') else 1
    print(f'{out}  {w_mm:.1f} x {H:.1f} mm   {shapes} shapes, {n} rings')
    print(f'   bar dropped {drop:.2f} mm   stem {stem_w:.2f} mm wide at x {cx:.2f}')
    print(f'   bowl underside {oy1:.2f}  bar top {by0:.2f}  '
          f'open gap {by0 - oy1:.2f} mm')
    return geom


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-joined.pdf')
    a.add_argument('--out', required=True)
    a.add_argument('--grow', type=float, default=0.40)
    a.add_argument('--drop', type=float, default=0.0)
    a.add_argument('--scale', type=float, default=1.0)
    a.add_argument('--stem-w', type=float, default=1.10)
    o = a.parse_args()
    build(o.src, o.grow, o.drop, o.scale, o.stem_w, o.out)
