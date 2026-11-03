#!/usr/bin/env python3
"""Embolden the PA & CO logo from its own vector outlines.

Not traced from a raster: the curves come straight out of the PDF's path
items, so the only approximation is how finely a bezier is flattened, at
5 microns. The outlines are then offset outward with mitred joins, which
is what emboldening a drawn letterform means: each pair of edges carries
out until they meet again, so a serif corner stays a corner instead of
being domed over by a round brush.
"""
import sys, numpy as np, pymupdf
from shapely.geometry import Polygon
from shapely.ops import unary_union

MM = 72.0 / 25.4
FLAT = 0.005          # bezier flattening tolerance, mm


def bez(p0, p1, p2, p3):
    ctrl = sum(np.hypot(*(np.subtract(b, a))) for a, b in
               zip([p0, p1, p2], [p1, p2, p3]))
    n = max(4, int(np.ceil(np.sqrt(ctrl / FLAT))))
    t = np.linspace(0, 1, n + 1)[1:, None]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def subpaths(page):
    """Every closed outline in the file, in mm, as point lists."""
    k = 25.4 / 72.0
    P = lambda q: np.array([q.x * k, q.y * k])
    out = []
    for g in page.get_drawings():
        cur = []
        for it in g['items']:
            if it[0] == 'l':
                a, b = P(it[1]), P(it[2])
                if not cur:
                    cur = [a]
                cur.append(b)
            elif it[0] == 'c':
                a = P(it[1])
                if not cur:
                    cur = [a]
                cur.extend(bez(a, P(it[2]), P(it[3]), P(it[4])))
            elif it[0] == 're':
                if cur:
                    out.append(cur); cur = []
                r = it[1]
                out.append([np.array([r.x0 * k, r.y0 * k]),
                            np.array([r.x1 * k, r.y0 * k]),
                            np.array([r.x1 * k, r.y1 * k]),
                            np.array([r.x0 * k, r.y1 * k])])
            # a new subpath starts where the pen jumps
            if len(cur) > 2 and np.hypot(*(cur[-1] - cur[0])) < 1e-9:
                out.append(cur); cur = []
        if len(cur) > 2:
            out.append(cur)
    return out


def assemble(paths):
    """Nest the rings; a ring inside an odd number of others is a hole."""
    rs = [Polygon(p).buffer(0) for p in paths if len(p) > 2]
    rs = [r for r in rs if r.area > 1e-6]
    rs.sort(key=lambda p: -p.area)
    polys = []
    for i, r in enumerate(rs):
        depth = sum(1 for j, o in enumerate(rs) if j != i and o.contains(r))
        if depth % 2:
            continue
        holes = [o for j, o in enumerate(rs)
                 if j != i and r.contains(o)
                 and sum(1 for q in rs if q is not o and q.contains(o)) == depth + 1]
        polys.append(Polygon(r.exterior.coords,
                             [h.exterior.coords for h in holes]))
    return unary_union(polys)


def write(geom, w_mm, h_mm, out):
    doc = pymupdf.open(); pg = doc.new_page(width=w_mm * MM, height=h_mm * MM)
    sh = pg.new_shape(); n = 0
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        for ring in [g.exterior] + list(g.interiors):
            pts = [pymupdf.Point(x * MM, y * MM) for x, y in ring.coords]
            if len(pts) > 2:
                sh.draw_polyline(pts); n += 1
    sh.finish(color=None, fill=(0, 0, 0), even_odd=True, closePath=True)
    sh.commit(); doc.save(out, deflate=True)
    return n


def scaled(src, out, factor):
    """Same artwork, larger page: every stroke grows with it."""
    d = pymupdf.open(src); p = d[0]
    o = pymupdf.open()
    q = o.new_page(width=p.rect.width * factor, height=p.rect.height * factor)
    q.show_pdf_page(q.rect, d, 0)       # stays vector
    o.save(out, deflate=True)


if __name__ == '__main__':
    src, out, grow = sys.argv[1], sys.argv[2], float(sys.argv[3])
    d = pymupdf.open(src); p = d[0]
    w, h = p.rect.width / MM, p.rect.height / MM
    sp = subpaths(p)
    g = assemble(sp)
    print(f'{src}  {w:.1f} x {h:.1f} mm   {len(sp)} outlines -> '
          f'{len(list(g.geoms)) if hasattr(g,"geoms") else 1} shapes, {g.area:.1f} mm2')
    b = g.buffer(grow, join_style=2, mitre_limit=6.0, quad_segs=48)
    b = b.simplify(0.002, preserve_topology=True)
    print(f'  outset +{grow:g} mm mitred -> '
          f'{len(list(b.geoms)) if hasattr(b,"geoms") else 1} shapes, {b.area:.1f} mm2, '
          f'{write(b, w, h, out)} rings -> {out}')
