#!/usr/bin/env python3
"""Build the badges from the logo's own vector outline.

Nothing is traced. The cross is the curve out of the logo file, the square
and circle and centre dot are drawn as a rect, an oval and a circle, and
the band round the cross is a true parallel offset of the same curve. Only
numbers are read off the artwork: the colours, the cross's share of the
badge, the weight of the band and the keyline, the dot's radius.
"""
import argparse, json, os, sys, tempfile
import numpy as np, pymupdf
from scipy import ndimage as ndi
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from badges import badges_of                                   # noqa: E402
from badges_vector import measure                              # noqa: E402

MM = 72.0 / 25.4


def bez(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def flatten(chain, step=0.4):
    """The chained outline as a dense polygon, in the logo's own units."""
    pts = []
    for kind, p in chain:
        q = [np.array(v, float) for v in p]
        if kind == 'l':
            pts.append(q[0]); pts.append(q[1])
        else:
            n = max(int(np.hypot(*(q[3] - q[0])) / step), 8)
            pts.extend(bez(q[0], q[1], q[2], q[3], n))
    out = [pts[0]]
    for v in pts[1:]:
        if np.hypot(*(v - out[-1])) > 1e-6:
            out.append(v)
    return np.array(out)


def draw(page, ring, col, key, kw):
    sh = page.new_shape()
    sh.draw_polyline([pymupdf.Point(*p) for p in ring])
    sh.finish(color=[v / 255 for v in key] if kw else None,
              fill=[v / 255 for v in col], width=kw, closePath=True,
              lineJoin=1, even_odd=True)
    sh.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('logo_json')
    ap.add_argument('out_dir')
    ap.add_argument('--width-mm', type=float, default=30.0)
    ap.add_argument('--dpi', type=int, default=600)
    ap.add_argument('--pre-scale', type=int, default=2)
    ap.add_argument('--sigma', type=float, default=1.1)
    ap.add_argument('--min-area', type=float, default=0.0006)
    ap.add_argument('--merge', type=float, default=26.0)
    ap.add_argument('--blend-tol', type=float, default=0.18)
    ap.add_argument('--min-blob', type=float, default=0.002)
    ap.add_argument('--outline-lum', type=float, default=90.0)
    ap.add_argument('--corner', type=int, default=60)
    ap.add_argument('--band-scale', type=float, default=0.88,
                    help='trim the coloured band by this factor')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    L = json.load(open(a.logo_json))
    poly = flatten(L['chain'])
    bb = L['bbox']
    poly -= np.array([bb[0], bb[1]])
    logo_side = max(bb[2] - bb[0], bb[3] - bb[1])
    poly /= logo_side                       # unit square, cross filling it
    # a raster of the same outline, only so the measuring step can register
    # it against the artwork; nothing drawn comes from it
    from PIL import Image, ImageDraw
    R = 512
    im = Image.new('L', (R, R), 0)
    ImageDraw.Draw(im).polygon([tuple(v) for v in (poly * (R - 1))], fill=255)
    ref = np.asarray(im) > 127
    print(f'logo outline: {len(poly)} points, {logo_side:.1f} pt square',
          file=sys.stderr)

    W = a.width_mm * MM
    made = []
    for n, img in enumerate(badges_of(a.src, a.dpi, a.width_mm, a.pre_scale), 1):
        g = measure(img, ref, a)
        kd, bd = g['key_w'] * W, g['band_w'] * W
        dark = g['key'] is not None and kd >= bd
        key = g['key'] if dark else g['band']
        kw = kd if dark else 0.0
        band = 0.0 if dark else bd * a.band_scale

        out = pymupdf.open()
        page = out.new_page(width=W, height=W)

        if g['ground'] is not None:
            sh = page.new_shape()
            r = pymupdf.Rect(kw, kw, W - kw, W - kw)
            sh.draw_rect(r) if g['shape'] == 'square' else sh.draw_oval(r)
            sh.finish(color=[v / 255 for v in key] if kw else None,
                      fill=[v / 255 for v in g['ground']], width=kw,
                      closePath=True, lineJoin=1)
            sh.commit()

        # the cross: the logo's curve, sized to the badge, centred
        side = g['cross_w'] * (W - 2 * (kw + band))
        P = poly * side + np.array([(W - side) / 2, (W - side) / 2])
        draw(page, P, g['band'] if band else g['fill'], key, kw)

        if band > 0:
            # a true parallel offset, not a stroke: the band belongs inside
            # the silhouette, and a stroke would straddle it
            inner = Polygon(P).buffer(0).buffer(-band, join_style=1, resolution=32)
            for geo in ([inner] if inner.geom_type == 'Polygon' else inner.geoms):
                if not geo.is_empty:
                    draw(page, np.array(geo.exterior.coords), g['fill'], key, 0)

        if g['dot_r'] > 0:
            sh = page.new_shape()
            sh.draw_circle(pymupdf.Point(W / 2, W / 2), g['dot_r'] * W)
            sh.finish(color=[v / 255 for v in key] if kw else None,
                      fill=[v / 255 for v in g['dot']], width=kw, closePath=True)
            sh.commit()

        f = os.path.join(a.out_dir, f'badge-{n}.pdf')
        out.save(f, garbage=4, deflate=True)
        made.append((f, W, W))
        print(f"badge {n}: {g['shape'] or 'no ground'}, cross "
              f"#{'%02x%02x%02x' % g['fill']}, "
              f"{'keyline' if dark else 'band'} #{'%02x%02x%02x' % key} "
              f"{(kw or band):.2f} pt, dot r {g['dot_r']*W:.2f} pt", file=sys.stderr)

    gap = pad = 6 * MM
    tw = sum(w for _, w, _ in made) + gap * (len(made) - 1) + 2 * pad
    th = max(h for _, _, h in made) + 2 * pad
    sheet = pymupdf.open(); pg = sheet.new_page(width=tw, height=th)
    x = pad
    for f, w, h in made:
        pg.show_pdf_page(pymupdf.Rect(x, pad, x + w, pad + h), pymupdf.open(f), 0)
        x += w + gap
    sheet.save(os.path.join(a.out_dir, 'badges-30mm.pdf'), garbage=4, deflate=True)
    print(f'sheet {tw:.1f} x {th:.1f} pt', file=sys.stderr)


if __name__ == '__main__':
    main()
