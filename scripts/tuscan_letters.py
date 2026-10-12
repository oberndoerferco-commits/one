#!/usr/bin/env python3
"""Draw Tuscan (French Clarendon) display capitals in the circus-woodtype style.

The reference art is ~90 px per letter, so its bifurcated serifs are below the
resolution at which they could be traced - a trace would only reproduce blur.
The letters are therefore *constructed* from the style's rules rather than
copied, which also means O and M come out consistent with each other even
though only M appears in the source word.

Style, read off the reference:
  * heavy slab stems, very slightly tapered towards the foot
  * wide flat top slabs, with a short spur turning down at the outer corners
  * at the baseline, the serif splits into curling claws that hang below it and
    terminate in balls - the signature of the genre
  * a thin inline following the stroke, inset from the outline
  * a drop shadow down and to the right

Everything is built in a 1000-unit cap height with the baseline at y=0, so the
glyphs can be scaled to any size.
"""

import argparse
import math

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

CAP = 1000.0


# ----------------------------------------------------------------- primitives


def curl(cx, cy, radius, a0, a1, w0, w1, ball=True, n=96):
    """A tapering arc band ending in a ball - one claw of a split serif."""
    ts = np.linspace(0.0, 1.0, n)
    ang = np.radians(a0 + (a1 - a0) * ts)
    wid = w0 + (w1 - w0) * ts
    outer = [(cx + (radius + w / 2) * math.cos(a), cy + (radius + w / 2) * math.sin(a))
             for a, w in zip(ang, wid)]
    inner = [(cx + (radius - w / 2) * math.cos(a), cy + (radius - w / 2) * math.sin(a))
             for a, w in zip(ang, wid)]
    poly = Polygon(outer + inner[::-1]).buffer(0)
    if ball:
        a = ang[-1]
        poly = poly.union(Point(cx + radius * math.cos(a),
                                cy + radius * math.sin(a)).buffer(wid[-1] * 0.62,
                                                                  quad_segs=64))
    return poly.buffer(0)


def top_slab(cx, stem, over, thick, spur=0.42):
    """Wide flat top serif with a short spur turning down at each outer corner."""
    half = stem / 2 + over
    slab = box(cx - half, CAP - thick, cx + half, CAP)
    sp = thick * spur
    for s in (-1, 1):
        x = cx + s * half
        slab = slab.union(Polygon([(x, CAP - thick),
                                   (x - s * thick * 0.78, CAP - thick),
                                   (x, CAP - thick - sp)]))
    return slab.buffer(0)


def claw_foot(cx, stem, over, thick, reach=1.0, drop=1.0):
    """Baseline serif: a slab whose ends split into claws hooking below it.

    The claw leaves the end of the slab heading downward, then hooks back
    inwards under the stem and finishes in a ball, so the ornament reads as a
    paw gripping the baseline rather than a scroll lying on its side.
    """
    half = stem / 2 + over
    foot = box(cx - half, 0.0, cx + half, thick)
    r = over * 0.92 * reach
    for s_ in (-1, 1):
        x = cx + s_ * half
        # centre of curvature inboard and level with the slab, so the sweep
        # starts at the slab end pointing down and curls under towards the stem
        foot = foot.union(spiral(x - s_ * r, thick * 0.52, r,
                                 0 if s_ > 0 else 180,
                                 -s_ * 152 if s_ > 0 else 180 + 152,
                                 thick * 1.02, thick * 0.34, s_, tighten=0.46))
    return foot.buffer(0)


def spiral(cx, cy, radius, a0, a1, w0, w1, side, tighten=0.42, n=120):
    """Tapering band on a tightening arc, finished with a ball terminal."""
    ts = np.linspace(0.0, 1.0, n)
    ang = np.radians(a0 + (a1 - a0) * ts)
    rad = radius * (1.0 - tighten * ts)
    wid = w0 + (w1 - w0) * ts
    outer, inner = [], []
    for a, rr, w in zip(ang, rad, wid):
        outer.append((cx + (rr + w / 2) * math.cos(a), cy + (rr + w / 2) * math.sin(a)))
        inner.append((cx + (rr - w / 2) * math.cos(a), cy + (rr - w / 2) * math.sin(a)))
    poly = Polygon(outer + inner[::-1]).buffer(0)
    a, rr, w = ang[-1], rad[-1], wid[-1]
    poly = poly.union(Point(cx + rr * math.cos(a), cy + rr * math.sin(a))
                      .buffer(w * 0.70, quad_segs=64))
    return poly.buffer(0)


def taper_stem(cx, top_w, bot_w, y0, y1):
    """A stem that narrows slightly towards the foot."""
    return Polygon([(cx - top_w / 2, y1), (cx + top_w / 2, y1),
                    (cx + bot_w / 2, y0), (cx - bot_w / 2, y0)])


# -------------------------------------------------------------------- glyphs


def glyph_M(stem=172.0, width=900.0, over=92.0, slab=132.0):
    """M: two upright outer stems, a V between them meeting near the baseline."""
    left, right = stem / 2 + 40, width - stem / 2 - 40
    parts = [taper_stem(left, stem, stem * 0.94, 0, CAP - slab * 0.2),
             taper_stem(right, stem, stem * 0.94, 0, CAP - slab * 0.2)]

    # the V: two diagonals from the inner top corners down to a point on the baseline
    apex = (left + right) / 2
    vy = CAP * 0.16
    dw = stem * 0.86
    for s, x_top in ((1, left), (-1, right)):
        dx = apex - x_top
        n = math.hypot(dx, vy - (CAP - slab))
        ox = abs((vy - (CAP - slab)) / n) * dw / 2
        parts.append(Polygon([(x_top - ox, CAP - slab * 0.1),
                              (x_top + ox, CAP - slab * 0.1),
                              (apex + ox * 0.35, vy),
                              (apex - ox * 0.35, vy)]))
    # inner peaks of the V meet the top slabs; outer tops get the wide slabs
    parts.append(top_slab(left, stem, over, slab))
    parts.append(top_slab(right, stem, over, slab))
    parts.append(claw_foot(left, stem, over, slab))
    parts.append(claw_foot(right, stem, over, slab))
    # a small foot where the V lands
    parts.append(claw_foot(apex, stem * 0.8, over * 0.52, slab * 0.82, reach=0.72))
    return unary_union(parts).buffer(0)


def glyph_O(side=215.0, tb=150.0, width=900.0, over=96.0, slab=128.0):
    """O: heavy ring, thick at the sides and lighter over the crown.

    The barb at the crown is a short spur, not a cap - in this genre the split
    serif reads as a small fork on the outer contour, and the weight of the
    ornament is carried by the claws at the foot, as it is on every other
    letter in the word.
    """
    cx, cy = width / 2, CAP / 2
    rx, ry = width / 2, CAP / 2
    outer = affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=256), rx, ry)
    inner = affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=256),
                           rx - side, ry - tb)
    parts = [outer.difference(inner)]

    # crown spur: a short forked barb sitting on the outer contour
    w = over * 0.78
    parts.append(Polygon([(cx - w, CAP - tb * 0.30), (cx + w, CAP - tb * 0.30),
                          (cx + w * 0.30, CAP + tb * 0.34),
                          (cx - w * 0.30, CAP + tb * 0.34)]))

    # claws hanging from the foot of the bowl, matching the other letters
    for s_ in (-1, 1):
        x = cx + s_ * (rx - side * 0.34)
        r = over * 1.05
        parts.append(spiral(x - s_ * r, ry * 0.26, r,
                            0 if s_ > 0 else 180,
                            -152 if s_ > 0 else 332,
                            slab * 1.00, slab * 0.34, s_, tighten=0.46))
    return unary_union(parts).buffer(0)


# -------------------------------------------------------------------- output


def inline_of(glyph, inset=34.0, weight=26.0):
    """The thin light line that runs inside the stroke."""
    a = glyph.buffer(-inset)
    b = glyph.buffer(-inset - weight)
    return a.difference(b).buffer(0)


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


def shadow_of(glyph, dx=48.0, dy=-54.0):
    """The offset drop shadow the reference lettering sits on."""
    return affinity.translate(glyph, dx, dy).difference(glyph).buffer(0)


def sheet(glyphs, gap=120.0, pad=110.0):
    """Lay glyphs out on a line; returns (placed, width, height)."""
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
    import os
    os.makedirs(a.outdir, exist_ok=True)
    hexes = lambda h: tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    ink, paper = hexes(a.ink), hexes(a.paper)

    letters = {'O': glyph_O(), 'M': glyph_M()}
    scale = a.size / CAP
    out = []
    for name, gl in list(letters.items()) + [('OM', None)]:
        for shaded in (False, True):
            gs = [letters['O'], letters['M']] if name == 'OM' else [gl]
            placed, w, h = sheet(gs)
            body = unary_union(placed)
            to = lambda p: (p[0] * scale, p[1] * scale)
            layers = []
            if shaded:
                layers.append((ink, unary_union([shadow_of(p) for p in placed])))
            layers.append((ink, body))
            layers.append((paper, unary_union([inline_of(p) for p in placed])))
            suffix = '-shadow' if shaded else ''
            f = os.path.join(a.outdir, f'tuscan-{name}{suffix}.pdf')
            write_pdf(f, layers, w * scale, h * scale, to)
            out.append((f, w * scale, h * scale))
    for f, w, h in out:
        print(f'  {os.path.basename(f):26s} {w:7.1f} x {h:7.1f} pt')
    return out


if __name__ == '__main__':
    main()
