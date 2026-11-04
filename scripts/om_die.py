#!/usr/bin/env python3
"""Leather cutting die for the OM mark, with a backing layer under it.

Two things a steel rule cannot do: cut a notch narrower than it can be
bent, and leave a sliver of leather thin enough to tear off the die. So
the outline is closed at the minimum first, which fills the narrow
notches, then anything still thinner than the minimum is brought up to it,
then counters too small to cut are dropped.

The mark's own proportions set the smallest patch worth cutting. At the
size it arrives the thinnest part measures 2.61 mm, so it scales to the
minimum at 190 x (2.00 / 2.61) = 146 mm wide. Below that the blackletter
has to be fattened, and the sheet says by how much.

The backing is the same outline offset outward. Where that offset is more
than half the gap between the O and the M, the two merge into one piece,
which is what holds a two-part mark together.
"""
import argparse, os, sys
import numpy as np, pymupdf
from PIL import Image
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from skimage.morphology import medial_axis
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

PP = 14.0
MM = 72.0 / 25.4


def disc(r):
    n = int(np.ceil(r)); y, x = np.mgrid[-n:n+1, -n:n+1]
    return (x*x + y*y) <= r*r


def trace(src):
    d = pymupdf.open(src); p = d[0]
    k = PP*25.4/72.0
    pm = p.get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    a = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples))
    return a < 128


def to_poly(mask, ppmm=PP, tol=0.8):
    rs = []
    pad = np.pad(mask, 2, constant_values=False)
    for c in find_contours(pad.astype(float), 0.5):
        c = approximate_polygon(c, tolerance=tol)
        if len(c) < 4:
            continue
        q = Polygon([((x-2)/ppmm, (y-2)/ppmm) for y, x in c]).buffer(0)
        if q.area > 0.2:
            rs.append(q)
    rs.sort(key=lambda q: -q.area)
    out = []
    for i, r in enumerate(rs):
        depth = sum(1 for j, o in enumerate(rs) if j != i and o.contains(r))
        if depth % 2:
            continue
        holes = [o for j, o in enumerate(rs)
                 if j != i and r.contains(o)
                 and sum(1 for q in rs if q is not o and q.contains(o)) == depth+1]
        out.append(Polygon(r.exterior.coords, [h.exterior.coords for h in holes]))
    return unary_union(out)


def thinnest(geom, ppmm=60):
    """p5 of the stroke width, which is where a die would tear."""
    x0, y0, x1, y1 = geom.bounds
    W = int((x1-x0+4)*ppmm); H = int((y1-y0+4)*ppmm)
    doc = pymupdf.open(); pg = doc.new_page(width=W/ppmm*MM, height=H/ppmm*MM)
    sh = pg.new_shape()
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        for ring in [g.exterior]+list(g.interiors):
            pts = [pymupdf.Point((x-x0+2)*MM, (y-y0+2)*MM) for x, y in ring.coords]
            if len(pts) > 2:
                sh.draw_polyline(pts)
    sh.finish(color=None, fill=(0, 0, 0), even_odd=True, closePath=True)
    sh.commit()
    k = ppmm*25.4/72.0
    pm = doc[0].get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    m = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples)) < 128
    sk, dist = medial_axis(m, return_distance=True)
    w = 2*dist[sk]/ppmm
    return float(np.percentile(w[w > 0.05], 5)), m, ppmm, (x0-2, y0-2)


def fatten(geom, minimum, ppmm=60):
    """Bring anything under the minimum up to it, leave the rest alone."""
    _, m, _, origin = thinnest(geom, ppmm)
    r = minimum/2*ppmm
    sk, dist = medial_axis(m, return_distance=True)
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - sk
    ends = sk & (nb <= 1)
    far = ndimage.distance_transform_edt(~ends) > r*1.1
    thin = sk & (dist < r) & far
    if not thin.any():
        return geom, 0
    grown = m | ndimage.binary_dilation(thin, disc(r))
    g = to_poly(grown, ppmm, tol=max(0.6, 0.012*ppmm))
    return affinity.translate(g, origin[0], origin[1]), int(thin.sum())


def write_vec(layers, out, pad=6.0):
    xs = [l[1].bounds for l in layers]
    x0 = min(b[0] for b in xs); y0 = min(b[1] for b in xs)
    x1 = max(b[2] for b in xs); y1 = max(b[3] for b in xs)
    W, H = (x1-x0)+2*pad, (y1-y0)+2*pad
    doc = pymupdf.open(); pg = doc.new_page(width=W*MM, height=H*MM)
    for (name, geom, col) in layers:
        sh = pg.new_shape()
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            for ring in [g.exterior]+list(g.interiors):
                pts = [pymupdf.Point((x-x0+pad)*MM, (y-y0+pad)*MM) for x, y in ring.coords]
                if len(pts) > 2:
                    sh.draw_polyline(pts + [pts[0]])
        sh.finish(color=col, fill=None, width=0.5, closePath=True)
        sh.commit()
    doc.save(out)
    return W, H


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='/root/.claude/uploads/9a731093-06fb-50bc-9d28-75940e80fb3f/13c79434-tshirt_design-22.pdf')
    a.add_argument('--width', type=float, default=100.0, help='overall width, mm')
    a.add_argument('--min', type=float, default=2.0, help='smallest feature a die can hold')
    a.add_argument('--offset', type=float, default=3.0, help='backing layer, mm bigger all round')
    a.add_argument('--outdir', default='assets/om-die')
    o = a.parse_args()
    os.makedirs(o.outdir, exist_ok=True)

    g = to_poly(trace(o.src))
    x0, y0, x1, y1 = g.bounds
    k = o.width/(x1-x0)
    g = affinity.scale(g, k, k, origin=(x0, y0))
    g = affinity.translate(g, -x0*k, -y0*k)
    raw_min, _, _, _ = thinnest(g)
    print(f'as supplied, scaled to {o.width:.0f} mm wide: thinnest {raw_min:.2f} mm, '
          f'{len(list(g.geoms))} pieces')

    r = o.min/2
    closed = g.buffer(r, join_style=1, quad_segs=16).buffer(-r, join_style=1, quad_segs=16)
    top, n = fatten(closed, o.min)
    # a counter the die cannot cut is not a counter
    cleaned = []
    for p_ in (top.geoms if hasattr(top, 'geoms') else [top]):
        keep = [h for h in p_.interiors
                if Polygon(h).buffer(-o.min/2).area > 0]
        cleaned.append(Polygon(p_.exterior.coords, [h.coords for h in keep]))
    top = unary_union(cleaned)
    got, _, _, _ = thinnest(top)
    print(f'after closing and fattening: thinnest {got:.2f} mm, '
          f'{len(list(top.geoms)) if hasattr(top,"geoms") else 1} pieces, '
          f'{sum(len(p_.interiors) for p_ in (top.geoms if hasattr(top,"geoms") else [top]))} counters')

    under = top.buffer(o.offset, join_style=1, quad_segs=24)
    under = unary_union([Polygon(p_.exterior.coords)
                         for p_ in (under.geoms if hasattr(under, 'geoms') else [under])])
    nu = len(list(under.geoms)) if hasattr(under, 'geoms') else 1
    print(f'backing at +{o.offset:.1f} mm: {nu} piece(s)'
          + ('  (the O and M merge into one)' if nu == 1 else ''))

    W, H = write_vec([('UNDER', under, (0, 0.45, 0.9)), ('TOP', top, (0.85, 0, 0.3))],
                     os.path.join(o.outdir, 'om-die-both.pdf'))
    write_vec([('TOP', top, (0.85, 0, 0.3))], os.path.join(o.outdir, 'om-die-top.pdf'))
    write_vec([('UNDER', under, (0, 0.45, 0.9))], os.path.join(o.outdir, 'om-die-under.pdf'))
    print(f'wrote {o.outdir}/om-die-top.pdf, om-die-under.pdf, om-die-both.pdf '
          f'({W:.1f} x {H:.1f} mm)')
