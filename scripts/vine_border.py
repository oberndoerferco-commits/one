#!/usr/bin/env python3
"""Draw a vine border -- leaves, flowers, tendrils -- as true curves.

Tracing the photographed ornament reaches its limit well before this. At
ninety-six pixels across, a leaf is about a dozen pixels wide, which is
enough to say where the leaf is and not enough to say that it is a leaf:
the lobes close up, the veins fall below the noise, and what comes back
reads as a lump on a stalk. No amount of care in the tracing puts back
detail the pixels never held.

So this draws the motif instead of recovering it. Every part is built from
its own geometry -- the leaf from five pointed lobes on a cordate base, the
flower from six petals, the tendril from a logarithmic spiral, the stem
from a sine that closes on itself -- which means it is sharp at any size,
exactly periodic, and can be tuned where a trace can only be accepted.

Seamless by construction rather than by retouching: three periods are built
and the middle one is cut out. Whatever the cut crosses at the top is the
same thing it crosses at the bottom, because the pattern is periodic, so
the ends meet.
"""
import argparse, os, sys
import numpy as np, pymupdf
from scipy import ndimage as ndi
from skimage.morphology import medial_axis
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

MM = 72.0 / 25.4


def lobe(deg, length, half, point=0.55, n=90):
    """One lobe: broad off the base, running to a tip."""
    t = np.linspace(0, 1, n)
    w = half * np.sin(np.pi * t ** 0.78) ** 1.15 * (1 - t) ** point / 0.5 ** point
    ring = np.c_[np.r_[w, -w[::-1]], np.r_[t * length, (t * length)[::-1]]]
    return affinity.rotate(Polygon(ring).buffer(0), deg, origin=(0, 0))


def leaf():
    """Five lobes round a cordate base: a vine leaf, not a rosette."""
    ang = [0, 58, -58, 118, -118]
    ln = [1.0, 0.86, 0.86, 0.64, 0.64]
    hw = [0.34, 0.30, 0.30, 0.25, 0.25]
    parts = [lobe(a, l, h) for a, l, h in zip(ang, ln, hw)]
    parts.append(Point(0, 0.20).buffer(0.30, resolution=48))
    return unary_union(parts).buffer(0.012).buffer(-0.012)


def veins(w):
    """A midrib and four laterals, started a little apart.

    Run them all from one point and the five of them read as an asterisk
    rather than as the veining of a leaf.
    """
    ang = [0, 56, -56, 114, -114]
    ln = [0.50, 0.40, 0.40, 0.28, 0.28]
    start = [0.08, 0.16, 0.16, 0.18, 0.18]
    return unary_union([
        affinity.rotate(LineString([(0, s), (0, l)]).buffer(w / 2, cap_style=1),
                        a, origin=(0, 0))
        for a, l, s in zip(ang, ln, start)])


def ribbon(pts, w0, w1, n=160):
    """A band of changing width along a path."""
    pts = np.asarray(pts, float)
    t = np.linspace(0, 1, len(pts))
    ti = np.linspace(0, 1, n)
    pts = np.c_[np.interp(ti, t, pts[:, 0]), np.interp(ti, t, pts[:, 1])]
    d = np.gradient(pts, axis=0)
    nv = np.c_[-d[:, 1], d[:, 0]]
    nv /= np.maximum(np.linalg.norm(nv, axis=1)[:, None], 1e-9)
    w = (w0 + (w1 - w0) * np.linspace(0, 1, n))[:, None] / 2
    return Polygon(np.vstack([pts + nv * w, (pts - nv * w)[::-1]])).buffer(0)


def tendril(scale, sign=1, turns=1.6, r0=0.26, w0=0.085, w1=0.038, n=200):
    th = np.linspace(0, turns * 2 * np.pi, n)
    r = r0 * np.exp(-0.25 * th)
    pts = np.c_[sign * (r * np.cos(th) - r0), r * np.sin(th)]
    return affinity.scale(ribbon(pts, w0, w1), scale, scale, origin=(0, 0))


def flower(R, petals=6):
    ps = [affinity.rotate(
            affinity.translate(
                affinity.scale(Point(0, 0).buffer(1, resolution=36), R * 0.46, R * 0.74),
                0, R * 0.60),
            360 / petals * k, origin=(0, 0)) for k in range(petals)]
    return (unary_union(ps).buffer(R * 0.03).buffer(-R * 0.03),
            Point(0, 0).buffer(R * 0.24, resolution=24))


LEAF = leaf()


def one_period(y0, W, T, add, cut, vein_w):
    n = 900
    t = np.linspace(y0, y0 + T, n)
    x = 0.5 * W + 0.105 * W * np.sin(2 * np.pi * t / T)

    def at(u):
        i = int(round(u * (n - 1)))
        return x[i], t[i]

    def put_leaf(u, side, s, rot, out, up):
        cx, cy = at(u)
        lx, ly = cx + side * out * W, cy + up * W
        add.append(affinity.translate(
            affinity.rotate(affinity.scale(LEAF, s, s), rot, origin=(0, 0)), lx, ly))
        cut.append(affinity.translate(
            affinity.rotate(affinity.scale(veins(vein_w), s, s), rot, origin=(0, 0)), lx, ly))
        add.append(ribbon(np.c_[[cx, lx], [cy - 0.02 * W, ly - 0.02 * W]],
                          0.055 * W, 0.038 * W, n=40))

    put_leaf(0.08, 1, 0.370 * W, -38, 0.130, 0.085)
    put_leaf(0.53, -1, 0.370 * W, 38, 0.130, 0.085)
    put_leaf(0.72, 1, 0.215 * W, -66, 0.100, 0.055)
    put_leaf(0.28, -1, 0.215 * W, 66, 0.100, 0.055)

    cx, cy = at(0.42)
    add.append(affinity.translate(tendril(0.66 * W, sign=-1), cx - 0.02 * W, cy + 0.02 * W))

    cx, cy = at(0.90)
    R = 0.135 * W
    pet, ctr = flower(R)
    fx, fy = cx + 0.200 * W, cy + 0.030 * W
    add.append(affinity.translate(pet, fx, fy))
    cut.append(affinity.translate(ctr, fx, fy))
    add.append(ribbon(np.c_[[cx, fx], [cy - 0.01 * W, fy - 0.02 * W]],
                      0.050 * W, 0.036 * W, n=40))
    return np.c_[x, t]


def border(W, T, periods, vein_w, stem_w):
    add, cut, spine = [], [], []
    for i in range(periods):
        spine.append(one_period(i * T, W, T, add, cut, vein_w))
    add.append(ribbon(np.vstack(spine), stem_w * W, stem_w * W, n=900 * periods))
    art = unary_union(add)
    return art.difference(unary_union(cut)) if cut else art


def narrowest(geom, px=700, q=10.0, cap=4000):
    """How wide the thinnest part of the drawing comes to, in its own units.

    Measured along the medial axis of a fine raster of the shape, at a
    percentile rather than at the minimum: every pointed tip runs to zero
    width, so the minimum is zero for any shape with a point on it and says
    nothing about whether a die can hold the body of the thing. Shrinking
    the polygon until it vanishes answers the opposite question again --
    that finds the fattest part.
    """
    minx, miny, maxx, maxy = geom.bounds
    sc = px / (maxx - minx)
    h = int(round((maxy - miny) * sc))
    if h > cap:                       # the drawing repeats; one stretch tells all
        maxy = miny + cap / sc
        geom = geom.intersection(box(minx, miny, maxx, maxy))
        if geom.is_empty:
            return 0.0
        h = cap
    from PIL import Image, ImageDraw
    img = Image.new('1', (px, h), 0)
    d = ImageDraw.Draw(img)
    for g in ([geom] if geom.geom_type == 'Polygon' else geom.geoms):
        d.polygon([((x - minx) * sc, (y - miny) * sc) for x, y in g.exterior.coords], fill=1)
        for ring in g.interiors:
            d.polygon([((x - minx) * sc, (y - miny) * sc) for x, y in ring.coords], fill=0)
    m = np.array(img, dtype=bool)
    if not m.any():
        return 0.0
    spine, dist = medial_axis(m, return_distance=True)
    if not spine.any():
        return 0.0
    return float(np.percentile(dist[spine], q)) * 2 / sc


def emit(geom, path, W, H, reversed_=False):
    doc = pymupdf.open()
    page = doc.new_page(width=W, height=H)
    if reversed_:
        page.draw_rect(page.rect, color=None, fill=(0, 0, 0))
    col = (1, 1, 1) if reversed_ else (0, 0, 0)
    sh = page.new_shape()
    for g in ([geom] if geom.geom_type == 'Polygon' else geom.geoms):
        for ring in [g.exterior] + list(g.interiors):
            pts = [pymupdf.Point(p[0], H - p[1]) for p in ring.coords]
            sh.draw_polyline(pts)
    sh.finish(color=None, fill=col, even_odd=True, closePath=True)
    sh.commit()
    doc.save(path, garbage=4, deflate=True)
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--name', default='vine')
    ap.add_argument('--width-mm', type=float, default=25.0)
    ap.add_argument('--periods', type=int, default=1)
    ap.add_argument('--ratio', type=float, default=1.95, help='period / width')
    ap.add_argument('--vein', type=float, default=0.042, help='vein width, leaf units')
    ap.add_argument('--stem', type=float, default=0.098, help='stem width, border units')
    ap.add_argument('--blunt', type=float, default=0.006,
                    help='round every point to this radius, in border widths, so '
                         'no tip is sharper than a die can press')
    ap.add_argument('--invert', action='store_true')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    W = a.width_mm * MM
    T = W * a.ratio
    # three periods, then take the middle one: whatever the cut crosses at the
    # top it crosses at the bottom, so the ends meet
    art = border(W, T, a.periods + 2, a.vein, a.stem)
    if a.blunt:
        r = a.blunt * W
        art = art.buffer(-r, join_style=1, resolution=16).buffer(
            r, join_style=1, resolution=16)
    art = art.intersection(box(-W, T, 2 * W, T * (a.periods + 1)))
    art = affinity.translate(art, 0, -T)
    # fit the drawing to the width asked for; the period scales with it, so
    # the tiling is unaffected
    minx, _, maxx, _ = art.bounds
    k = W / (maxx - minx)
    art = affinity.scale(art, k, k, origin=(0, 0))
    art = affinity.translate(art, -minx * k, 0)
    page_w, page_h = W, T * k * a.periods

    thin = narrowest(art) * 25.4 / 72
    vein = a.vein * 0.370 * W * k * 25.4 / 72
    print(f'{a.name}: {a.periods} period(s), {page_w*25.4/72:.1f} x '
          f'{page_h*25.4/72:.1f} mm\n'
          f'  thinnest ink {thin:.2f} mm, veins {vein:.2f} mm, '
          f'tips rounded to {a.blunt*W*k*25.4/72:.2f} mm\n'
          f'  holds 0.30 mm down to {0.30/min(thin, vein)*page_w*25.4/72:.0f} mm wide',
          file=sys.stderr)

    f = os.path.join(a.out_dir, f'{a.name}.pdf')
    doc = emit(art, f, page_w, page_h)
    with open(f[:-4] + '.svg', 'w', encoding='utf-8') as fh:
        fh.write(doc[0].get_svg_image())
    print(f'  {f}', file=sys.stderr)
    if a.invert:
        g = os.path.join(a.out_dir, f'{a.name}-reversed.pdf')
        emit(art, g, page_w, page_h, reversed_=True)
        print(f'  {g}', file=sys.stderr)


if __name__ == '__main__':
    main()
