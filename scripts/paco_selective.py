#!/usr/bin/env python3
"""PA & CO at 50 mm, raising only what is under 1 mm and leaving the rest.

Growing every edge by the same amount is wrong here. The diamond is drawn
at 1.01 mm and already passes; a uniform offset took it to 1.78 mm, and the
letters' stems went with it, so the whole mark came back heavy and the
thick-to-thin contrast the logo is built on was flattened.

Along the medial axis each point carries the radius of the largest disc
that fits, which is half the local stroke width. Clamp that radius to the
minimum and union those discs with the original: a stroke already at the
minimum contributes a disc that was inside the shape anyway and does not
move, while a hairline grows to exactly the minimum. Stems, the diamond and
the silhouette stay as drawn.

A disc centred on a spine endpoint would stand past the tip by its whole
radius and cap every serif with a dome, so the spine within one radius of
an endpoint is held back: the stroke behind a terminal thickens, the
terminal keeps the taper it was drawn with.
"""
import argparse, itertools, sys, os
import numpy as np, pymupdf
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from skimage.morphology import medial_axis
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import subpaths, assemble, write, MM
from paco_unround import unround

PPMM = 90
MITRE = dict(join_style=2, mitre_limit=4.0)
DENOISE = 0.008


def disc(r):
    n = int(np.ceil(r)); y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return (x * x + y * y) <= r * r


def prepare(src, dx, dy):
    """Clean the outlines, then move only the O and its bar."""
    d = pymupdf.open(src); pg = d[0]
    rings = [unround(np.array(s)) for s in subpaths(pg)]
    letters, bar = [], None
    for r in rings:
        p = Polygon(r).buffer(0); x0, y0, x1, y1 = p.bounds
        if x0 > 41 and y0 > 33.4 and x1 - x0 > 4 and y1 - y0 < 1.0:
            bar = r
        elif not (x0 > 44 and 32.5 < y0 < 33.2 and x1 - x0 < 1.3):
            letters.append(r)
    L = assemble(letters).simplify(DENOISE, preserve_topology=True)
    B = Polygon(bar).buffer(0).simplify(DENOISE, preserve_topology=True)
    parts = sorted(L.geoms, key=lambda s: s.bounds[0])
    O = parts[-1]
    rest = unary_union(parts[:-1])
    O = affinity.translate(O, dx, 0)
    B = affinity.translate(B, dx, dy)
    ox0, oy0, ox1, oy1 = O.bounds
    low = [c for c in O.exterior.coords if c[1] > oy1 - 0.02]
    cx = float(np.mean([c[0] for c in low]))
    bx0, by0, bx1, by1 = B.bounds
    # the stem is drawn at the minimum, not at the bar's thinner weight
    return unary_union([rest, O, B]), (cx, oy1, by0)


def raster(geom, pad=2.0):
    x0, y0, x1, y1 = geom.bounds
    W = int((x1 - x0 + 2 * pad) * PPMM); H = int((y1 - y0 + 2 * pad) * PPMM)
    doc = pymupdf.open(); pg = doc.new_page(width=W / PPMM * MM, height=H / PPMM * MM)
    sh = pg.new_shape()
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        for ring in [g.exterior] + list(g.interiors):
            pts = [pymupdf.Point((x - x0 + pad) * MM, (y - y0 + pad) * MM)
                   for x, y in ring.coords]
            if len(pts) > 2:
                sh.draw_polyline(pts)
    sh.finish(color=None, fill=(0, 0, 0), even_odd=True, closePath=True)
    sh.commit()
    k = PPMM * 25.4 / 72.0
    pm = doc[0].get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    from PIL import Image
    a = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples))
    return a < 128, (x0 - pad, y0 - pad)


def thicken(mask, target):
    r = target / 2.0 * PPMM
    skel, dist = medial_axis(mask, return_distance=True)
    nb = ndimage.convolve(skel.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - skel
    ends = skel & (nb <= 1)
    far = ndimage.distance_transform_edt(~ends) > r * 1.15
    thin = skel & (dist < r) & far
    if not thin.any():
        return mask, 0
    return mask | ndimage.binary_dilation(thin, disc(r)), int(thin.sum())


def vectorise(mask, origin, tol_mm=0.010):
    pad = np.pad(mask, 2, constant_values=False)
    polys = []
    for c in find_contours(pad.astype(float), 0.5):
        c = approximate_polygon(c, tolerance=max(0.5, tol_mm * PPMM))
        if len(c) < 4:
            continue
        polys.append(Polygon([(origin[0] + (x - 2) / PPMM,
                               origin[1] + (y - 2) / PPMM) for y, x in c]).buffer(0))
    polys = [p for p in polys if p.area > 1e-6]
    polys.sort(key=lambda p: -p.area)
    out = []
    for i, r in enumerate(polys):
        depth = sum(1 for j, o in enumerate(polys) if j != i and o.contains(r))
        if depth % 2:
            continue
        holes = [o for j, o in enumerate(polys)
                 if j != i and r.contains(o)
                 and sum(1 for q in polys if q is not o and q.contains(o)) == depth + 1]
        out.append(Polygon(r.exterior.coords, [h.exterior.coords for h in holes]))
    return unary_union(out)


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-joined.pdf')
    a.add_argument('--out', required=True)
    a.add_argument('--min-mm', type=float, default=1.045)
    a.add_argument('--dx', type=float, default=0.0)
    a.add_argument('--dy', type=float, default=0.70)
    a.add_argument('--width', type=float, default=50.0)
    o = a.parse_args()

    geom, (cx, oy1, by0) = prepare(o.src, o.dx, o.dy)
    stem = box(cx - o.min_mm / 2, oy1 - 0.25, cx + o.min_mm / 2, by0 + 0.25)
    geom = unary_union([geom, stem])
    mask, origin = raster(geom)
    grown, n = thicken(mask, o.min_mm)
    g = vectorise(grown, origin)
    x0, y0, x1, y1 = g.bounds
    k = o.width / (x1 - x0)
    g = affinity.scale(affinity.translate(g, -x0, -y0), k, k, origin=(0, 0))
    x0, y0, x1, y1 = g.bounds
    rings = write(g, x1, y1, o.out)
    shapes = sorted(g.geoms, key=lambda s: s.bounds[0])
    worst = min(p.distance(q) for p, q in itertools.combinations(shapes, 2))
    print(f'{o.out}  {x1:.2f} x {y1:.2f} mm  {len(shapes)} shapes, {rings} rings')
    print(f'   raised {n} spine points;  scaled {k:.4f};  closest shapes {worst:.2f} mm')


if __name__ == '__main__':
    main()
