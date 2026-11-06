#!/usr/bin/env python3
"""Re-weight the PA & CO lockup: letters and diamond, separately.

The diamond was always the weak part. At 50 mm the letters carry a
1.08 mm thinnest stroke and a 2.05 mm median; the diamond sits at 1.00
and 1.01, because it arrived as a line drawing and a plain outset could
not thicken it - the white facets inside it were already at the 1 mm
limit, and an outset adds to a stroke exactly what it takes from the gap
beside it.

That is the whole arithmetic of this script, and it is why thickening
and enlarging have to be done together:

    stroke = scale * stroke0 + 2 * grow
    white  = scale * white0  - 2 * grow

Outset alone buys weight out of the facets. Scale alone keeps the ratio
and buys nothing. Together they can hold any stroke at any white, and
the pair that does it is solvable - see --target-stroke.

The diamond keeps its horizontal centre on the letters and its drawn
gap above them, so the lockup stays composed whatever it is set to.
"""
import argparse
import math
import os
import sys

import numpy as np
import pymupdf
from scipy import ndimage
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import unary_union
from skimage.morphology import medial_axis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import MM, assemble, subpaths, write              # noqa: E402

SRC = 'assets/paco/paco-50mm-min1mm-FINAL.pdf'
MITRE = dict(join_style=2, mitre_limit=4.0)


def load(src):
    """(diamond, letters, page height) from the 50 mm artwork."""
    pg = pymupdf.open(src)[0]
    g = assemble([np.array(r) for r in subpaths(pg)])
    ps = sorted((g.geoms if hasattr(g, 'geoms') else [g]), key=lambda s: -s.area)
    return ps[0], unary_union(ps[1:]), pg.rect.height / MM


def _ends(sk):
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - sk
    return sk & (nb <= 1)


def _mask(poly, ppmm, pad=2.5):
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = poly.bounds
    w = int((x1 - x0 + 2 * pad) * ppmm) + 2
    h = int((y1 - y0 + 2 * pad) * ppmm) + 2
    im = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(im)
    for p in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
        dr.polygon([((x - x0 + pad) * ppmm, (y - y0 + pad) * ppmm)
                    for x, y in p.exterior.coords], fill=255)
        for r in p.interiors:
            dr.polygon([((x - x0 + pad) * ppmm, (y - y0 + pad) * ppmm)
                        for x, y in r.coords], fill=0)
    return np.asarray(im) > 127, (x0 - pad, y0 - pad)


def gauge(poly, ppmm=60, skip=0.8, white_cap=6.0):
    """What the drawing is: thinnest stroke, tightest channel, facets.

    The stroke is a minimum and it settles: terminals excluded at 0.5 mm
    it reads 0.90, at 0.8 and beyond it is 0.98 and stays there, which is
    the stroke this artwork was engineered to.

    The white is not a minimum and never settles. Every facet of the
    diamond is a triangle and every counter in the letters is a wedge, so
    the white runs into a sharp corner over and over; widen the terminal
    exclusion and the answer just keeps climbing. paco_verify recorded
    the same thing the first time round. So the white is read as a 2nd
    percentile of the channels, and the question a facet actually poses -
    does it survive at all - is answered separately, by the largest disc
    that fits in the smallest one.

    The terminal exclusion is a maximum filter, not binary_dilation: the
    square kernel is the same, but a 97 x 97 structuring element on a
    60 px/mm raster does not finish, and a maximum filter is separable.
    """
    m, _ = _mask(poly, ppmm)
    r = max(1, int(round(skip * ppmm)))
    out = []
    for i, mask in enumerate((m, ~m)):
        sk, dist = medial_axis(mask, return_distance=True)
        near = ndimage.maximum_filter(_ends(sk).astype(np.uint8), size=2 * r + 1)
        keep = sk & (near == 0)
        if i == 1:
            keep &= (2 * dist / ppmm < white_cap)     # not the open field
        w = 2 * dist[keep] / ppmm if keep.any() else np.array([9.99])
        out.append(float(w.min()) if i == 0 else float(np.percentile(w, 2)))
    return out[0], out[1]


def facets(poly):
    """(count, smallest facet's widest inscribed disc) for the white holes."""
    from shapely.geometry import Polygon
    holes = [Polygon(r) for p in (poly.geoms if hasattr(poly, 'geoms') else [poly])
             for r in p.interiors]
    if not holes:
        return 0, 0.0
    best = min(2 * max(h.exterior.distance(h.representative_point()),
                       _inradius(h)) for h in holes)
    return len(holes), best


def _inradius(poly, steps=240):
    """Largest disc that fits, found on the polygon's own medial scale."""
    x0, y0, x1, y1 = poly.bounds
    n = int(math.sqrt(steps))
    best = 0.0
    for i in range(n + 1):
        for j in range(n + 1):
            from shapely.geometry import Point
            p = Point(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * j / n)
            if poly.contains(p):
                best = max(best, p.distance(poly.exterior))
    return best


def solve(stroke0, white0, want_stroke, want_white):
    """The (scale, grow) that holds both at once.

        scale * stroke0 + 2g = want_stroke
        scale * white0  - 2g = want_white
    """
    scale = (want_stroke + want_white) / (stroke0 + white0)
    grow = (want_stroke - scale * stroke0) / 2
    return scale, grow


def place(diamond, letters, scale, grow, gap):
    """Scale, thicken and re-seat the diamond over the letters."""
    cx = (letters.bounds[0] + letters.bounds[2]) / 2
    d = affinity.scale(diamond, scale, scale, origin='centroid')
    if grow:
        d = d.buffer(grow, **MITRE)
    # PDF y runs down here: the letters' top edge is their smaller y
    dx = cx - (d.bounds[0] + d.bounds[2]) / 2
    dy = (letters.bounds[1] - gap) - d.bounds[3]
    return affinity.translate(d, dx, dy)


def _bowl(c, i, j, n=9):
    """The O's bottom, drawn back in after the stem is cut out.

    Joining the two stem roots with a straight chord would leave a 1.30 mm
    flat across the lowest point of a 10 mm bowl. The flat is only 0.03 mm
    shallower than the curve, so nothing would ever measure it, but the
    outline is the drawing and the drawing should be round. A quadratic
    through three bowl vertices either side gives the curvature; it is
    then corrected linearly so it meets the two roots exactly, which keeps
    the join continuous instead of trading a flat for a kink.
    """
    pts = [c[(i - k) % len(c)] for k in (3, 2, 1)] + [c[(j + k) % len(c)]
                                                      for k in (0, 1, 2)]
    q = np.polyfit([x for x, _ in pts], [y for _, y in pts], 2)
    (xa, ya), (xb, yb) = c[i], c[j]
    # the fit need not pass through the roots; take only its sag from its
    # own chord and lay that on the real one
    f = lambda x: np.polyval(q, x)
    lin = lambda x, x0, y0, x1, y1: y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    out = []
    for k in range(1, n + 1):
        x = xa + (xb - xa) * k / (n + 1)
        sag = f(x) - lin(x, xa, f(xa), xb, f(xb))
        out.append((x, lin(x, xa, ya, xb, yb) + sag))
    return out


def detach_bar(letters):
    """Free the bar under the O by cutting out the stem that ties them.

    The O, the stem and the bar arrive as a single ring. The stem is a
    plain rectangle, so the cut is exact rather than approximate: its two
    sides are the highest-reaching vertical edges in the glyph, and the
    run of the ring between them is the stem and the bar together. Drop
    that run and close the bowl, and what was removed, closed on itself,
    is the bar.
    """
    ps = list(letters.geoms) if hasattr(letters, 'geoms') else [letters]
    k = max(range(len(ps)), key=lambda i: ps[i].bounds[3])      # reaches lowest
    c = list(ps[k].exterior.coords)[:-1]
    m = len(c)
    # vertical edges in the lower half, by how high they reach
    mid = (ps[k].bounds[1] + ps[k].bounds[3]) / 2
    v = [e for e in range(m)
         if abs(c[e][0] - c[(e + 1) % m][0]) < 1e-6
         and abs(c[e][1] - c[(e + 1) % m][1]) > 0.5
         and min(c[e][1], c[(e + 1) % m][1]) > mid]
    if len(v) < 2:
        raise SystemExit('no stem found under the O')
    v.sort(key=lambda e: min(c[e][1], c[(e + 1) % m][1]))
    i, j = sorted(v[:2])                       # stem left root, stem right edge
    j = (j + 1) % m                            # ... its upper end: the other root
    run = [c[(i + 1 + t) % m] for t in range((j - i - 1) % m)]
    O = Polygon(c[:i + 1] + _bowl(c, i, j) + c[j:],
                [r.coords for r in ps[k].interiors])
    bar = Polygon(run)
    if not (O.is_valid and bar.is_valid):
        raise SystemExit('the cut did not close')
    out = [p for t, p in enumerate(ps) if t != k] + [O, bar]
    return unary_union(out), O, bar


def build(src, letter_grow, scale, grow, gap=None, free_bar=False):
    diamond, letters, _ = load(src)
    if free_bar:
        letters = detach_bar(letters)[0]
    if gap is None:
        gap = letters.bounds[1] - diamond.bounds[3]
    L = letters.buffer(letter_grow, **MITRE) if letter_grow else letters
    D = place(diamond, L, scale, grow, gap)
    art = unary_union([L, D])
    x0, y0, x1, y1 = art.bounds
    return affinity.translate(art, -x0, -y0), (x1 - x0, y1 - y0), L, D


def sdf(poly, ppmm, margin=6.0):
    """Signed distance to the outline, mm, positive outside.

    One field answers every weight and the whole dome. Growing by g is
    the level set {D <= g}; the distance from a point to the grown
    outline, which is what the dome profile is a function of, is g - D.
    So the viewer never has to offset a polygon - which browsers cannot
    do - and gets the rib dome for free from the same array.
    """
    m, (ox, oy) = _mask(poly, ppmm, pad=margin)
    din = ndimage.distance_transform_edt(m) / ppmm
    dout = ndimage.distance_transform_edt(~m) / ppmm
    return (dout - din).astype(np.float32), (ox, oy), m.shape


def export(src, path, ppmm=12.0, free_bar=False):
    """Both fields plus the numbers the viewer reads off them."""
    diamond, letters, _ = load(src)
    if free_bar:
        letters = detach_bar(letters)[0]
    ls, lw = gauge(letters)
    ds, dw = gauge(diamond)
    nf, sf = facets(diamond)
    dcx = (diamond.bounds[0] + diamond.bounds[2]) / 2
    dcy = (diamond.bounds[1] + diamond.bounds[3]) / 2
    # the diamond's field is stored about its own centre so that scaling
    # is a lookup at p/s, with the result multiplied by s
    local = affinity.translate(diamond, -dcx, -dcy)
    fields, meta = [], []
    for name, poly in (('letters', letters), ('diamond', local)):
        f, (ox, oy), shape = sdf(poly, ppmm)
        fields.append(np.clip(np.rint(f * 100), -32000, 32000).astype('<i2'))
        meta.append(dict(name=name, w=shape[1], h=shape[0], ox=ox, oy=oy))
    head = dict(
        ppmm=ppmm, fields=meta,
        letters=dict(stroke=round(ls, 3), white=round(lw, 3),
                     x0=letters.bounds[0], y0=letters.bounds[1],
                     x1=letters.bounds[2], y1=letters.bounds[3]),
        diamond=dict(stroke=round(ds, 3), white=round(dw, 3),
                     facet=round(sf, 3), facets=nf,
                     w=diamond.bounds[2] - diamond.bounds[0],
                     h=diamond.bounds[3] - diamond.bounds[1],
                     cx=dcx, cy=dcy),
        gap=letters.bounds[1] - diamond.bounds[3])
    import json
    blob = json.dumps(head).encode()
    with open(path, 'wb') as fh:
        fh.write(np.array([len(blob)], dtype='<u4').tobytes())
        fh.write(blob)
        for f in fields:
            fh.write(f.tobytes())
    return head, os.path.getsize(path)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default=SRC)
    a.add_argument('--letter-grow', type=float, default=0.0)
    a.add_argument('--diamond-scale', type=float, default=1.0)
    a.add_argument('--diamond-grow', type=float, default=0.0)
    a.add_argument('--gap', type=float, help='diamond bottom to letter top, mm')
    a.add_argument('--target-stroke', type=float,
                   help='solve for the scale and grow that reach this stroke '
                        'while holding --target-white')
    a.add_argument('--target-white', type=float, default=1.0)
    a.add_argument('--free-bar', action='store_true',
                   help="cut the stem under the O so the bar "
                        "stands on its own")
    a.add_argument('--out')
    a.add_argument('--data', help='fields for the browser mockup')
    o = a.parse_args()

    diamond, letters, _ = load(o.src)
    ds, dw = gauge(diamond)
    ls, lw = gauge(letters)
    nf, sf = facets(diamond)
    print(f'as drawn   letters  stroke {ls:.2f}  white {lw:.2f}')
    print(f'           diamond  stroke {ds:.2f}  white {dw:.2f}  '
          f'{diamond.bounds[2]-diamond.bounds[0]:.2f} mm wide, '
          f'{nf} facets, smallest takes a {sf:.2f} mm disc')

    if o.target_stroke:
        o.diamond_scale, o.diamond_grow = solve(ds, dw, o.target_stroke,
                                                o.target_white)
        print(f'  to reach stroke {o.target_stroke:.2f} at white '
              f'{o.target_white:.2f}: scale {o.diamond_scale:.3f}, '
              f'grow {o.diamond_grow:.3f}')

    art, (w, h), L, D = build(o.src, o.letter_grow, o.diamond_scale,
                              o.diamond_grow, o.gap, o.free_bar)
    ls2, lw2 = gauge(L)
    ds2, dw2 = gauge(D)
    nf2, sf2 = facets(D)
    print(f'built      letters  stroke {ls2:.2f}  white {lw2:.2f}')
    print(f'           diamond  stroke {ds2:.2f}  white {dw2:.2f}  '
          f'{D.bounds[2]-D.bounds[0]:.2f} mm wide, '
          f'{nf2} facets, smallest takes a {sf2:.2f} mm disc')
    print(f'           clearance diamond to letters {L.distance(D):.2f} mm')
    print(f'           lockup {w:.2f} x {h:.2f} mm')
    worst = min(ls2, lw2, ds2, dw2)
    print(f'           {"OK  " if worst >= 0.97 else "under"} smallest '
          f'feature anywhere {worst:.2f} mm')
    if o.data:
        head, size = export(o.src, o.data, free_bar=o.free_bar)
        print(f'  {o.data}: {size/1024:.0f} KB, ' +
              ', '.join(f'{m["name"]} {m["w"]}x{m["h"]}' for m in head['fields']))
    if o.out:
        n = write(art, w, h, o.out)
        print(f'  {o.out}: {n} rings, {w:.2f} x {h:.2f} mm')
