#!/usr/bin/env python3
"""Draw Tuscan (French Clarendon) display capitals matching the 1936 "PREMIUM".

M is in the source word and every proportion below was measured off it.  It is
redrawn rather than auto-traced: at 245 px cap height the scan's point spread
closes the counters, so a threshold-and-trace of the silhouette comes out as a
solid slab (see assets/tuscan-letters/README.md).  The measurements are the
copy; the drawing just reopens what the blur shut.

Frame: cap height 1000 units, y = 0 at the foot of the ornaments, letter
centred on x = 0.  Measured from the word's M (cap = 245 px in the scan):

    letter width     1550      stem centres      +/-497
    stem width        310      top slabs         y 755..1000, |x| 45..775
    inner strokes    near-vertical, counters a sliver 100-140 wide
    ornament band    the three feet merge into one bar at y 330..490
    claws            y 0..490

The claw is the signature of the genre and is built in four pieces per side:
a shouldered flare off the stem, a waist, a volute that sweeps out and curls
back under itself far enough to leave an open eye, and a ball toe - with a
pendant drop hanging on the axis between the two volutes.
"""

import argparse
import math
import os

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

CAP = 1000.0


# ----------------------------------------------------------------- primitives


def band(P, w, caps=True):
    """Polygon following a centreline with a varying width."""
    P = np.asarray(P, float)
    w = np.asarray(w, float)
    d = np.gradient(P, axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    poly = Polygon(np.vstack([P + n * (w[:, None] / 2),
                              (P - n * (w[:, None] / 2))[::-1]])).buffer(0)
    if caps:
        for q, ww in ((P[0], w[0]), (P[-1], w[-1])):
            poly = poly.union(Point(q).buffer(ww / 2, quad_segs=48))
    return poly.buffer(0)


def volute(cx, cy, r0, r1, a0, a1, w0, w1, n=240):
    """A scroll: a band on a tightening arc.  Sweeping past ~270 deg leaves an eye."""
    t = np.linspace(0, 1, n)
    a = np.radians(a0 + (a1 - a0) * t)
    r = r0 + (r1 - r0) * t
    w = w0 + (w1 - w0) * t
    return band(np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1), w)


def taper(cx, prof, C=CAP):
    """Closed symmetric outline from (height, half-width) pairs, both as
    fractions of the cap height."""
    return Polygon([(cx - w * C, h * C) for h, w in prof] +
                   [(cx + w * C, h * C) for h, w in prof[::-1]]).buffer(0)


# -------------------------------------------------------------------- ornament


def claw(cx, k=1.0, top=0.490, C=CAP):
    """The clawed foot: the stem flares into a shelf, then swells into a solid
    lobed bracket with a pendant drop hanging lowest on the axis.

    The lobes are solid.  What makes the ornament read as scrollwork is the
    inline curling inside each one (see `scrolls_of`) - in the source those light
    spirals are the inline, not holes in the letter, which is why an earlier
    drawing that cut them as holes came out looking like jewellery.
    """
    R, P = k * C, []
    P.append(taper(cx, [(top, 0.150 * k), (0.448, 0.182 * k), (0.410, 0.238 * k),
                        (0.374, 0.250 * k), (0.340, 0.238 * k),
                        (0.312, 0.206 * k), (0.298, 0.188 * k)], C))
    P.append(band([(cx, 0.330 * C), (cx, 0.210 * R), (cx, 0.068 * R)],
                  [0.124 * R, 0.100 * R, 0.072 * R]))
    for s in (-1, 1):
        P.append(Point(cx + s * 0.116 * R, 0.168 * R)
                 .buffer(0.108 * R, quad_segs=96))
        P.append(band([(cx + s * 0.060 * R, 0.330 * C),
                       (cx + s * 0.116 * R, 0.248 * R)],
                      [0.146 * R, 0.132 * R]))
    return unary_union(P).buffer(0)


def scrolls_of(cx, k=1.0, C=CAP):
    """The inline's spirals inside a claw's two lobes."""
    R, P = k * C, []
    for s in (-1, 1):
        P.append(volute(cx + s * 0.116 * R, 0.166 * R, 0.064 * R, 0.014 * R,
                        115 if s > 0 else 65, (115 - 335) if s > 0 else (65 + 335),
                        0.022 * R, 0.017 * R))
    return unary_union(P).buffer(0)


def barb(cx, cy, s, reach=0.130, C=CAP):
    """A small outward scroll perched on the side of a stroke, as on the P and R."""
    return volute(cx + s * reach * 0.42 * C, cy, reach * 0.54 * C, reach * 0.17 * C,
                  120 if s > 0 else 60, (120 - 300) if s > 0 else (60 + 300),
                  reach * 0.52 * C, reach * 0.26 * C)


def hook(x, s, y, drop=0.100, C=CAP):
    """The short spur that turns down, then inwards, under a slab's outer end."""
    return band([(x - s * 0.040 * C, y + 0.008 * C),
                 (x - s * 0.046 * C, y - drop * C * 0.52),
                 (x - s * 0.078 * C, y - drop * C * 0.86),
                 (x - s * 0.124 * C, y - drop * C * 0.94)],
                [0.072 * C, 0.064 * C, 0.054 * C, 0.044 * C])


# -------------------------------------------------------------------- glyphs


def glyph_M():
    """M: two slabbed outer stems, two near-vertical inner strokes closing on a
    thin wedge, and three clawed feet merging into one ornamental band."""
    C = CAP
    sx, sw = 0.497 * C, 0.310 * C
    y_sl, y_bd = 0.755 * C, 0.490 * C       # slab underside / top of the band
    out, inn = 0.775 * C, 0.045 * C         # slab outer / inner edge at y_sl
    ch = 0.038 * C                          # top-corner chamfer
    parts = []
    for s in (-1, 1):
        # top slab, chamfered outside, its inner edge raking in towards the wedge
        parts.append(Polygon([(s * out, C - ch), (s * (out - ch), C),
                              (s * 0.098 * C, C), (s * inn, y_sl),
                              (s * out, y_sl)]).buffer(0))
        parts.append(hook(s * out, s, y_sl))
        # outer stem
        parts.append(Polygon([(s * (sx + sw / 2), y_sl + 0.01 * C),
                              (s * (sx - sw / 2), y_sl + 0.01 * C),
                              (s * (sx - sw / 2 + 0.010 * C), y_bd),
                              (s * (sx + sw / 2), y_bd)]).buffer(0))
        # inner stroke: leans in, leaving a sliver counter beside the stem
        parts.append(Polygon([(s * 0.240 * C, y_sl + 0.01 * C),
                              (s * inn, y_sl + 0.01 * C),
                              (0.0, y_bd), (s * 0.185 * C, y_bd)]).buffer(0))
        parts.append(claw(s * sx))
    # the three feet are tied together by one ornamental bar, as in the source
    parts.append(taper(0.0, [(0.495, 0.690), (0.470, 0.716), (0.430, 0.728),
                             (0.395, 0.724), (0.360, 0.702), (0.336, 0.668)]))
    parts.append(claw(0.0, 0.88))
    return unary_union(parts).buffer(0)


def detail_M():
    sx = 0.497 * CAP
    return unary_union([scrolls_of(-sx), scrolls_of(0.0, 0.88),
                        scrolls_of(sx)]).buffer(0)


def glyph_O(width=1.090, side=0.300, crown=0.220, rise=0.215):
    """O: a heavy ring on the M's weights - the side stroke is the M's stem, the
    crown lighter - standing on the same clawed foot, with a forked spur at the
    crown and the small side scrolls the P and R wear at mid height."""
    C = CAP
    rx = width / 2 * C
    ry = (1.0 - rise) / 2 * C
    cy = rise * C + ry
    outer = affinity.scale(Point(0, cy).buffer(1.0, quad_segs=360), rx, ry)
    inner = affinity.scale(Point(0, cy).buffer(1.0, quad_segs=360),
                           rx - side * C, ry - crown * C)
    parts = [outer.difference(inner)]
    w = 0.112 * C
    parts.append(Polygon([(-w, C - crown * C * 0.78), (w, C - crown * C * 0.78),
                          (w * 0.52, C + 0.050 * C),
                          (-w * 0.52, C + 0.050 * C)]).buffer(0))
    for s in (-1, 1):
        parts.append(Point(s * w * 0.54, C + 0.044 * C)
                     .buffer(0.032 * C, quad_segs=48))
    parts.append(claw(0.0, 0.98, top=0.345))
    return unary_union(parts).buffer(0)


def detail_O():
    return scrolls_of(0.0, 0.98)


# -------------------------------------------------------------------- output


def inline_of(glyph, inset=0.034 * CAP, weight=0.019 * CAP):
    """The thin light line that runs inside the stroke."""
    return glyph.buffer(-inset).difference(glyph.buffer(-inset - weight)).buffer(0)


def shadow_of(glyph, dx=0.048 * CAP, dy=-0.054 * CAP):
    return affinity.translate(glyph, dx, dy).difference(glyph).buffer(0)


def _poly_list(geom):
    gs = geom.geoms if hasattr(geom, 'geoms') else [geom]
    return [g for g in gs if g.geom_type == 'Polygon' and not g.is_empty]


def pdf_paths(geom, to_xy, prec=2):
    f = lambda v: (f"{v:.{prec}f}".rstrip('0').rstrip('.')) or '0'
    ops = []
    for g in _poly_list(geom):
        for ring in [g.exterior] + list(g.interiors):
            pts = [to_xy(p) for p in ring.coords[:-1]]
            if len(pts) < 3:
                continue
            ops.append(f"{f(pts[0][0])} {f(pts[0][1])} m " +
                       " ".join(f"{f(x)} {f(y)} l" for x, y in pts[1:]) + " h")
    return ops


def write_pdf(path, layers, w, h, to_xy):
    body = []
    for rgb, geom in layers:
        if geom.is_empty:
            continue
        r, g, b = [v / 255.0 for v in rgb]
        body.append(f"{r:.4f} {g:.4f} {b:.4f} rg")
        body.append("\n".join(pdf_paths(geom, to_xy)))
        body.append("f*")
    content = ("\n".join(body) + "\n").encode('latin-1')
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.3f} {h:.3f}] "
             f"/Contents 4 0 R /Resources << >> >>").encode(),
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
            + content + b"endstream"]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offs = []
    for i, bb in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + bb + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs)+1}\n".encode() + b"0000000000 65535 f \n"
    for o in offs:
        out += f"{o:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\n"
            f"startxref\n{x}\n%%EOF\n").encode()
    open(path, 'wb').write(bytes(out))


def sheet(glyphs, gap=0.120 * CAP, pad=0.110 * CAP):
    placed, x = [], pad
    for g in glyphs:
        b = g.bounds
        placed.append(affinity.translate(g, x - b[0], pad - b[1]))
        x += (b[2] - b[0]) + gap
    width = x - gap + pad
    height = max(p.bounds[3] for p in placed) + pad
    return placed, width, height


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument('outdir')
    ap.add_argument('--size', type=float, default=480.0,
                    help='cap height in points for the output PDFs')
    ap.add_argument('--ink', default='2b2218')
    ap.add_argument('--paper', default='f2ece0')
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    hexes = lambda h: tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    ink, paper = hexes(a.ink), hexes(a.paper)

    letters = {'O': glyph_O(), 'M': glyph_M()}
    details = {'O': detail_O(), 'M': detail_M()}
    scale = a.size / CAP
    out = []
    for name in ('O', 'M', 'OM'):
        for shaded in (False, True):
            keys = ['O', 'M'] if name == 'OM' else [name]
            gs = [letters[q] for q in keys]
            placed, w, h = sheet(gs)
            shifted = [affinity.translate(details[q], p.bounds[0] - g.bounds[0],
                                          p.bounds[1] - g.bounds[1])
                       for q, g, p in zip(keys, gs, placed)]
            to = lambda p: (p[0] * scale, p[1] * scale)
            layers = []
            if shaded:
                layers.append((ink, unary_union([shadow_of(p) for p in placed])))
            layers.append((ink, unary_union(placed)))
            layers.append((paper, unary_union(
                [inline_of(p) for p in placed] + shifted).buffer(0)))
            f = os.path.join(a.outdir,
                             f"tuscan-{name}{'-shadow' if shaded else ''}.pdf")
            write_pdf(f, layers, w * scale, h * scale, to)
            out.append((f, w * scale, h * scale))
    for f, w, h in out:
        print(f'  {os.path.basename(f):26s} {w:7.1f} x {h:7.1f} pt')
    return out


if __name__ == '__main__':
    main()
