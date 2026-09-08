#!/usr/bin/env python3
"""Convert vector geometry in a PDF into DXF, at true physical size.

Written for artwork exported by design tools that paint shapes by clipping a
filled rectangle to an outline (Canva does this): the real geometry then lives
in the *clipping paths*, not in the fill operators, so naive extraction finds
only rectangles. This walks the content streams properly - graphics state,
nested Form XObjects, the full path operator set - and collects the clip paths
in device space.

Bezier curves are preserved exactly: each closed subpath becomes one cubic
B-spline (a chain of cubic Beziers is exactly representable as a cubic
B-spline with triple knots at the joins). A flattened LWPOLYLINE variant is
also written for CAM software that would rather not deal with splines.
"""

import argparse
import math
import re

import ezdxf
import pymupdf
from ezdxf.math import Bezier4P, Vec2, bezier_to_bspline, cubic_bezier_bbox

PT_TO_MM = 25.4 / 72.0

TOKEN = re.compile(rb"""
    (?P<num>[-+]?(?:\d+\.\d*|\.\d+|\d+))
  | (?P<name>/[^\s/\[\]<>(){}]*)
  | (?P<delim><<|>>|\[|\])
  | (?P<str>\((?:[^()\\]|\\.)*\))
  | (?P<op>[A-Za-z'"*]+)
""", re.X)


# ------------------------------------------------------------------ matrices


def mat_mul(a, b):
    """Compose transforms: apply `a`, then `b` (PDF row-vector convention)."""
    a0, a1, a2, a3, a4, a5 = a
    b0, b1, b2, b3, b4, b5 = b
    return (a0 * b0 + a1 * b2, a0 * b1 + a1 * b3,
            a2 * b0 + a3 * b2, a2 * b1 + a3 * b3,
            a4 * b0 + a5 * b2 + b4, a4 * b1 + a5 * b3 + b5)


def apply(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


# -------------------------------------------------------------- pdf traversal


def _xobjects(info):
    out = {}
    mo = re.search(r'/XObject\s*<<(.*?)>>', info, re.S)
    if mo:
        for name, num in re.findall(r'(/[\w.]+)\s+(\d+)\s+0\s+R', mo.group(1)):
            out[name] = int(num)
    return out


class ClipPathExtractor:
    """Collects clipping paths (the artwork) from a PDF's content streams."""

    def __init__(self, doc):
        self.doc = doc
        self.paths = []

    def run(self, data, ctm, resources, depth=0):
        if depth > 8:
            return
        stack, operands, path = [], [], []
        cur = None
        last = start_pt = (0.0, 0.0)
        pending_clip = False

        for m in TOKEN.finditer(data):
            kind = m.lastgroup
            if kind == 'num':
                operands.append(float(m.group()))
                continue
            if kind in ('name', 'str', 'delim'):
                operands.append(m.group().decode('latin-1'))
                continue
            op = m.group().decode('latin-1')

            if op == 'q':
                stack.append(ctm)
            elif op == 'Q':
                if stack:
                    ctm = stack.pop()
            elif op == 'cm' and len(operands) >= 6:
                ctm = mat_mul(tuple(operands[-6:]), ctm)
            elif op == 'm' and len(operands) >= 2:
                x, y = operands[-2:]
                cur = {'start': apply(ctm, x, y), 'segs': [], 'rect': False}
                path.append(cur)
                last = start_pt = (x, y)
            elif op == 'l' and len(operands) >= 2 and cur:
                x, y = operands[-2:]
                cur['segs'].append(('L', apply(ctm, x, y)))
                last = (x, y)
            elif op == 'c' and len(operands) >= 6 and cur:
                x1, y1, x2, y2, x3, y3 = operands[-6:]
                cur['segs'].append(('C', apply(ctm, x1, y1), apply(ctm, x2, y2),
                                    apply(ctm, x3, y3)))
                last = (x3, y3)
            elif op == 'v' and len(operands) >= 4 and cur:
                x2, y2, x3, y3 = operands[-4:]
                cur['segs'].append(('C', apply(ctm, *last), apply(ctm, x2, y2),
                                    apply(ctm, x3, y3)))
                last = (x3, y3)
            elif op == 'y' and len(operands) >= 4 and cur:
                x1, y1, x3, y3 = operands[-4:]
                cur['segs'].append(('C', apply(ctm, x1, y1), apply(ctm, x3, y3),
                                    apply(ctm, x3, y3)))
                last = (x3, y3)
            elif op == 're' and len(operands) >= 4:
                x, y, w, h = operands[-4:]
                cur = {'start': apply(ctm, x, y),
                       'segs': [('L', apply(ctm, x + w, y)),
                                ('L', apply(ctm, x + w, y + h)),
                                ('L', apply(ctm, x, y + h))],
                       'rect': True}
                path.append(cur)
                last = start_pt = (x, y)
            elif op == 'h' and cur:
                last = start_pt
            elif op in ('W', 'W*'):
                pending_clip = True
            elif op in ('n', 'f', 'F', 'f*', 'B', 'B*', 'b', 'b*', 'S', 's'):
                if pending_clip and path:
                    self.paths.append(path)
                pending_clip = False
                path, cur = [], None
            elif op == 'Do' and operands:
                xref = resources.get(operands[-1])
                if xref is not None:
                    info = self.doc.xref_object(xref, compressed=True)
                    if '/Subtype/Form' in info:
                        sub = ctm
                        mo = re.search(r'/Matrix\s*\[([^\]]+)\]', info)
                        if mo:
                            sub = mat_mul(tuple(float(v) for v in mo.group(1).split()), ctm)
                        self.run(self.doc.xref_stream(xref), sub, _xobjects(info), depth + 1)
            if kind == 'op':
                operands = []


# ------------------------------------------------------------------ geometry


def _line_bezier(p, q):
    """A straight segment as an exact cubic Bezier (collinear controls)."""
    return Bezier4P([Vec2(p),
                     Vec2((p[0] + (q[0] - p[0]) / 3, p[1] + (q[1] - p[1]) / 3)),
                     Vec2((p[0] + 2 * (q[0] - p[0]) / 3, p[1] + 2 * (q[1] - p[1]) / 3)),
                     Vec2(q)])


def subpath_beziers(sub, close=True):
    """Every segment of a subpath as an exact cubic Bezier."""
    curves = []
    p = sub['start']
    for seg in sub['segs']:
        if seg[0] == 'L':
            q = seg[1]
            curves.append(_line_bezier(p, q))
            p = q
        else:
            curves.append(Bezier4P([Vec2(p), Vec2(seg[1]), Vec2(seg[2]), Vec2(seg[3])]))
            p = seg[3]
    if close and math.dist(p, sub['start']) > 1e-9:
        curves.append(_line_bezier(p, sub['start']))
    return curves


def flatten_bezier(p0, p1, p2, p3, tol, depth=0):
    """Adaptive subdivision: chord deviation stays within tol."""
    if depth > 20:
        return [p3]
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    n = math.hypot(dx, dy)
    if n < 1e-12:
        d = max(math.dist(p1, p0), math.dist(p2, p0))
    else:
        ux, uy = dx / n, dy / n
        d = max(abs((p1[0] - p0[0]) * uy - (p1[1] - p0[1]) * ux),
                abs((p2[0] - p0[0]) * uy - (p2[1] - p0[1]) * ux))
    if d <= tol:
        return [p3]
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    p01, p12, p23 = mid(p0, p1), mid(p1, p2), mid(p2, p3)
    p012, p123 = mid(p01, p12), mid(p12, p23)
    c = mid(p012, p123)
    return (flatten_bezier(p0, p01, p012, c, tol, depth + 1)
            + flatten_bezier(c, p123, p23, p3, tol, depth + 1))


def flatten_subpath(sub, tol, close=True):
    pts = [sub['start']]
    for bez in subpath_beziers(sub, close):
        cp = [(p.x, p.y) for p in bez.control_points]
        pts.extend(flatten_bezier(cp[0], cp[1], cp[2], cp[3], tol))
    return pts


# --------------------------------------------------------------- dxf writing


def new_doc(layer):
    doc = ezdxf.new('R2000', setup=True)
    doc.header['$INSUNITS'] = 4          # millimetres
    doc.header['$MEASUREMENT'] = 1       # metric
    doc.header['$LUNITS'] = 2
    if layer not in doc.layers:
        doc.layers.add(layer, color=7)
    return doc


def write_spline_dxf(path, subpaths, xform, layer='LOGO'):
    doc = new_doc(layer)
    msp = doc.modelspace()
    for sub in subpaths:
        curves = [Bezier4P([Vec2(xform(p.x, p.y)) for p in b.control_points])
                  for b in subpath_beziers(sub)]
        bs = bezier_to_bspline(curves)
        spline = msp.add_spline(degree=bs.degree, dxfattribs={'layer': layer})
        spline.control_points = [(p.x, p.y, 0.0) for p in bs.control_points]
        spline.knots = list(bs.knots())
    doc.saveas(path)
    return sum(1 for _ in subpaths)


def write_polyline_dxf(path, subpaths, xform, tol_mm, layer='LOGO'):
    doc = new_doc(layer)
    msp = doc.modelspace()
    total = 0
    for sub in subpaths:
        pts = [xform(*p) for p in flatten_subpath(sub, tol_mm / PT_TO_MM)]
        if math.dist(pts[0], pts[-1]) < 1e-9:
            pts = pts[:-1]
        msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': layer})
        total += len(pts)
    doc.saveas(path)
    return total


# ------------------------------------------------------------------ pipeline


def extract_subpaths(pdf_path, page_no=0):
    """Artwork subpaths in PDF point coordinates, plus the page rectangle."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_no]
    ex = ClipPathExtractor(doc)
    info = doc.xref_object(page.xref, compressed=True)
    ex.run(page.read_contents(), (1, 0, 0, 1, 0, 0), _xobjects(info))

    subpaths = []
    for p in ex.paths:
        # Rectangles here are bounding-box clips wrapping each shape, plus the
        # page clip. The shapes themselves are the non-rectangular paths.
        if all(sp['rect'] for sp in p):
            continue
        subpaths.extend(p)
    return subpaths, page.mediabox


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input")
    ap.add_argument("outdir")
    ap.add_argument("--name", default="artwork")
    ap.add_argument("--tol", type=float, default=0.005,
                    help="chord tolerance in mm for the polyline variant")
    ap.add_argument("--layer", default="LOGO")
    args = ap.parse_args(argv)

    import os
    subpaths, mb = extract_subpaths(args.input)
    os.makedirs(args.outdir, exist_ok=True)
    base = os.path.join(args.outdir, args.name)

    # Page coordinates: origin at the artboard's lower-left corner, in mm.
    page = lambda x, y: ((x - mb.x0) * PT_TO_MM, (y - mb.y0) * PT_TO_MM)

    # Exact bounds from the Bezier extrema, not from a flattening.
    x0 = y0 = float('inf')
    x1 = y1 = float('-inf')
    for sub in subpaths:
        for bez in subpath_beziers(sub):
            bb = cubic_bezier_bbox(bez)
            x0, y0 = min(x0, bb.extmin.x), min(y0, bb.extmin.y)
            x1, y1 = max(x1, bb.extmax.x), max(y1, bb.extmax.y)
    tight = lambda x, y: ((x - x0) * PT_TO_MM, (y - y0) * PT_TO_MM)

    write_spline_dxf(base + "-splines.dxf", subpaths, page, args.layer)
    write_polyline_dxf(base + "-polylines.dxf", subpaths, page, args.tol, args.layer)
    write_spline_dxf(base + "-splines-trimmed.dxf", subpaths, tight, args.layer)
    write_polyline_dxf(base + "-polylines-trimmed.dxf", subpaths, tight, args.tol, args.layer)

    print(f"{len(subpaths)} closed contours")
    print(f"artboard {(mb.x1 - mb.x0) * PT_TO_MM:.4f} x {(mb.y1 - mb.y0) * PT_TO_MM:.4f} mm")
    print(f"artwork  {(x1 - x0) * PT_TO_MM:.4f} x {(y1 - y0) * PT_TO_MM:.4f} mm "
          f"at ({(x0 - mb.x0) * PT_TO_MM:.4f}, {(y0 - mb.y0) * PT_TO_MM:.4f}) mm")
    return base


if __name__ == "__main__":
    main()
