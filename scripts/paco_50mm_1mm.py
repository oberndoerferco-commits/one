#!/usr/bin/env python3
"""PA & CO at 50 mm with every stroke at least 1 mm.

A plain outset cannot do this. It adds to a stroke exactly what it takes
from the gap beside it, and two gaps in the artwork are too small to pay:
the O sits 0.88 mm above its bar and 1.54 mm from the C, so raising the
0.248 mm hairline to 1 mm closes them to 0.13 mm and 0.79 mm, and the die
bridges both.

Only two things are in the way, so only two things move: the O and its bar
shift right until the C clears, and the bar drops until the O clears.
Everything else, the P, A, ampersand, C and the diamond, is the artwork
offset and nothing more. The result is scaled to exactly 50 mm at the end,
so the growth is set slightly over 1 mm to survive that reduction.
"""
import argparse, itertools, sys, os
import numpy as np, pymupdf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import subpaths, assemble, write, MM
from paco_unround import unround

MITRE = dict(join_style=2, mitre_limit=4.0)
DENOISE = 0.008


def split(page):
    rings = [unround(np.array(s)) for s in subpaths(page)]
    letters, bar, stem = [], None, None
    for r in rings:
        p = Polygon(r).buffer(0)
        x0, y0, x1, y1 = p.bounds
        if x0 > 41 and y0 > 33.4 and x1 - x0 > 4 and y1 - y0 < 1.0:
            bar = r
        elif x0 > 44 and 32.5 < y0 < 33.2 and x1 - x0 < 1.3:
            stem = r                      # the old connector, redrawn
        else:
            letters.append(r)
    return letters, bar


def build(src, grow, dx, dy, target_w, out, grow_diamond=0.012):
    """grow_diamond is separate: the diamond is drawn at 1.01 mm already and
    needs only enough to survive the final scaling, not the 0.75 mm the
    letters need. Growing everything by the same amount took it to 1.78 mm,
    which is why it came back looking heavy."""
    d = pymupdf.open(src); pg = d[0]
    letters, bar = split(pg)
    L = assemble(letters).simplify(DENOISE, preserve_topology=True)
    B = Polygon(bar).buffer(0).simplify(DENOISE, preserve_topology=True)

    parts = sorted(L.geoms, key=lambda s: s.bounds[0])
    diamond = max(parts, key=lambda s: s.area if s.bounds[3] < 20 else -1)
    letters = [s for s in parts if s is not diamond]
    O = letters[-1]                            # right-most letter is the O
    rest = unary_union(letters[:-1])

    Ob = affinity.translate(O.buffer(grow, **MITRE), dx, 0)
    Bb = affinity.translate(B.buffer(grow, **MITRE), dx, dy)
    Rb = unary_union([rest.buffer(grow, **MITRE),
                      diamond.buffer(grow_diamond, **MITRE)])

    ox0, oy0, ox1, oy1 = Ob.bounds
    low = [c for c in Ob.exterior.coords if c[1] > oy1 - 0.02]
    cx = float(np.mean([c[0] for c in low]))
    bx0, by0, bx1, by1 = Bb.bounds
    S = box(cx - (by1 - by0) / 2, oy1 - 0.25, cx + (by1 - by0) / 2, by0 + 0.25)

    g = unary_union([Rb, Ob, Bb, S])
    x0, y0, x1, y1 = g.bounds
    k = target_w / (x1 - x0)                   # scale to exactly 50 mm
    g = affinity.scale(affinity.translate(g, -x0, -y0), k, k, origin=(0, 0))
    x0, y0, x1, y1 = g.bounds
    n = write(g, x1, y1, out)

    shapes = sorted(g.geoms, key=lambda s: s.bounds[0])
    worst = min(a.distance(b) for a, b in itertools.combinations(shapes, 2))
    print(f'{out}   {x1:.2f} x {y1:.2f} mm   {len(shapes)} shapes, {n} rings')
    print(f'   scaled by {k:.4f};  closest two shapes {worst:.2f} mm')
    return g


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-joined.pdf')
    a.add_argument('--out', required=True)
    a.add_argument('--grow', type=float, default=0.395)
    a.add_argument('--dx', type=float, default=0.25)
    a.add_argument('--dy', type=float, default=0.95)
    a.add_argument('--width', type=float, default=50.0)
    a.add_argument('--grow-diamond', type=float, default=0.012)
    o = a.parse_args()
    build(o.src, o.grow, o.dx, o.dy, o.width, o.out, o.grow_diamond)
