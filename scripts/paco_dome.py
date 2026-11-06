#!/usr/bin/env python3
"""Dome the top surface of the logo: every stroke a rounded rib.

A bevel only rolls the corner and leaves the middle of a stroke flat. To
curve the whole surface, the outline is inset over and over on a circular
profile and the results stacked: at angle t the shape is pulled in by
R(1 - cos t) and sits at height R sin t. A stroke narrower than 2R runs out
of width before the top and closes into a rounded rib; the thickest stroke
here is 2.37 mm, so R = 1.25 mm domes all of them.

three.js cannot do this with ExtrudeGeometry: its bevel insets by pushing
vertices along their normals, which self-intersects once the inset passes
half the stroke width. A real polygon offset collapses correctly instead,
so the rings are computed here and the viewer is handed the result.
"""
import argparse, json, math, os, sys
import numpy as np, pymupdf, trimesh
from shapely.geometry import Polygon, Point as ShPoint
from shapely import affinity

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import subpaths, assemble, MM


def artwork(src):
    d = pymupdf.open(src); p = d[0]
    g = assemble([np.array(r) for r in subpaths(p)])
    W, H = p.rect.width / MM, p.rect.height / MM
    g = affinity.scale(g, 1, -1, origin=(0, 0))          # PDF y runs down
    return affinity.translate(g, -W / 2, H / 2), W, H


def rings(geom, R, steps):
    """(height, shape) up the dome, in equal steps of inset.

    Equal steps of arc put the widest inset at the top, where the profile is
    flattest, and on a sharp corner that last step overshoots the shape and
    throws a spike. Stepping the inset evenly keeps every step the same
    distance in plan, which is the quantity that has to stay small.
    """
    out = []
    for i in range(steps + 1):
        inset = R * i / steps
        z = math.sqrt(max(0.0, R * R - (R - inset) ** 2))
        g = geom if inset <= 1e-9 else geom.buffer(-inset, join_style=1,
                                                   quad_segs=8)
        if g.is_empty:
            break
        out.append((z, g.simplify(0.006, preserve_topology=True)))
    return out


def to_json(rs, W, H, base):
    lv = []
    for z, g in rs:
        polys = []
        for s in (g.geoms if hasattr(g, 'geoms') else [g]):
            polys.append({'o': [[round(x, 3), round(y, 3)] for x, y in s.exterior.coords],
                          'h': [[[round(x, 3), round(y, 3)] for x, y in r.coords]
                                for r in s.interiors]})
        lv.append({'z': round(z, 4), 'p': polys})
    return {'w': round(W, 3), 'h': round(H, 3), 'base': base, 'levels': lv}


# --------------------------------------------------------------- true dome
def dome_z(d, inset, height):
    """Height of the dome `d` mm in from the edge of a stroke."""
    u = np.minimum(d, inset) / inset
    return height * np.sqrt(np.maximum(0.0, 1.0 - (1.0 - u) ** 2))


def _densify(coords, step):
    out = []
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        for k in range(n):
            out.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    out.append(coords[-1])
    return out


def _graded(poly, inset, height, rings_at, step, fine=0.05):
    """Seed points on inset contours, packed where the surface is steep.

    The dome meets the side wall with a vertical tangent, so near the
    outline a little inset buys a lot of height: the first 0.1 mm of
    inset is 8 per cent of the way in and 44 per cent of the way up. A
    mesh of one size everywhere therefore cuts the corner at the rim and
    nowhere else. These contours are placed at equal steps of HEIGHT, not
    of inset, which puts the triangles where the curvature is.
    """
    pts = []
    prev = 0.0
    for d in rings_at:
        inner = poly.buffer(-d, join_style=1)
        prev, band = d, d - prev
        if inner.is_empty:
            continue
        # keep the triangles from going too long and thin: a band 0.02 mm
        # wide seeded every 0.12 mm is a sliver, and a sliver spanning
        # from the outline to the next contour is where the rim error is
        st = max(fine, min(step, 4 * band))
        for q in (inner.geoms if hasattr(inner, 'geoms') else [inner]):
            for ring in [q.exterior] + list(q.interiors):
                pts += _densify(list(ring.coords), st)
    return pts


def solid(poly, inset, height, base, area=0.010, step=0.12,
          nrings=10, fine=0.05):
    """One body as a real dome, not a stack of level sets.

    Stacking inset outlines makes the top a staircase, and the worst
    tread is the first: the profile is vertical where it meets the edge
    of a stroke, so the opening step is a 0.42 mm wall 0.08 mm in from
    every outline - a third of the dome height. More levels do not fix
    it cheaply, because the error sits exactly where the surface is
    steepest.

    So the plan is meshed once, properly. The outline goes in as fixed
    segments, so the drawn outline stays the drawn outline - no serif or
    diamond tip is rounded off by a sampling grid. Inset contours at
    equal steps of height seed the rim, where the surface is steep.
    `triangle` fills the rest under a maximum-area rule, and every vertex
    is lifted to the exact profile at its own distance from the outline.
    Outline vertices are at distance zero and stay where the side wall
    meets them, so nothing can crack, and the same triangulation laid
    flat is the underside.

    Uniform subdivision was the obvious alternative and is the wrong
    tool: it quarters every triangle at once starting from triangles that
    span the whole glyph, so a 0.1 mm edge cost 280,000 triangles for one
    letter - seventeen times what the surface needs - and still left the
    rim coarse.
    """
    import shapely, triangle as tri
    rings_at = [inset * (1 - math.sqrt(max(0.0, 1 - (i / nrings) ** 2)))
                for i in range(1, nrings + 1)]
    V, S, holes = [], [], []
    for ring in [poly.exterior] + list(poly.interiors):
        c = _densify(list(ring.coords)[:-1] + [ring.coords[0]], step)[:-1]
        k = len(V)
        V += c
        S += [(k + a, k + (a + 1) % len(c)) for a in range(len(c))]
    for ring in poly.interiors:
        q = Polygon(ring).representative_point()
        holes.append((q.x, q.y))
    nfix = len(V)
    V += _graded(poly, inset, height, rings_at, step, fine)
    pslg = dict(vertices=np.array(V), segments=np.array(S))
    if holes:
        pslg['holes'] = np.array(holes)
    t = tri.triangulate(pslg, f'pa{area}')
    v2, f = t['vertices'], t['triangles']
    d = shapely.distance(poly.boundary, shapely.points(v2))
    d[:nfix] = 0.0                       # the outline is the outline
    n = len(v2)
    VV = np.vstack([np.column_stack([v2, base + dome_z(d, inset, height)]),
                    np.column_stack([v2, np.zeros(n)])])
    de = f[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2)
    _, idx, cnt = np.unique(np.sort(de, axis=1), axis=0,
                            return_index=True, return_counts=True)
    rim = de[idx[cnt == 1]]
    a, b = rim[:, 0], rim[:, 1]
    wall = np.vstack([np.column_stack([a, b, b + n]),
                      np.column_stack([a, b + n, a + n])])
    m = trimesh.Trimesh(vertices=VV,
                        faces=np.vstack([f, f[:, ::-1] + n, wall]),
                        process=False)
    m.process(validate=True)
    m.fix_normals()
    return m


def build_smooth(g, inset, height, base, area=0.010, step=0.12,
                 nrings=10, fine=0.05):
    """The whole part. The bodies are disjoint, so no boolean is needed -
    which also removes the degenerate seam triangles a union leaves."""
    ps = list(g.geoms) if hasattr(g, 'geoms') else [g]
    return trimesh.util.concatenate(
        [solid(p, inset, height, base, area, step, nrings, fine)
         for p in ps])


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-min1mm-FINAL.pdf')
    a.add_argument('--radius', type=float, default=1.25)
    a.add_argument('--steps', type=int, default=16)
    a.add_argument('--base', type=float, default=0.60)
    a.add_argument('--height', type=float,
                   help='stretch the dome to this height; the inset still '
                        'reaches --radius, which is what the viewer\'s slider '
                        'does, so the profile turns elliptical rather than '
                        'biting further into the strokes')
    a.add_argument('--json')
    a.add_argument('--stl')
    a.add_argument('--smooth', action='store_true',
                   help='build the top as a real dome instead of a stack '
                        'of level sets')
    a.add_argument('--area', type=float, default=0.012,
                   help='largest triangle in the plan mesh, mm2')
    a.add_argument('--rim', type=int, default=12,
                   help='inset contours seeded near the edge, where the '
                        'profile is steep')
    a.add_argument('--fine', type=float, default=0.05,
                   help='closest spacing along a rim contour, mm')
    o = a.parse_args()

    g, W, H = artwork(o.src)
    rs = rings(g, o.radius, o.steps)
    if o.height:
        k = o.height / o.radius
        rs = [(z * k, poly) for z, poly in rs]
    print(f'{len(rs)} levels, dome {rs[-1][0]:.3f} mm tall over a {o.base:.2f} mm base')

    if o.json:
        d = to_json(rs, W, H, o.base)
        json.dump(d, open(o.json, 'w'), separators=(',', ':'))
        print(f'   {o.json}: {os.path.getsize(o.json)/1024:.0f} KB')

    if o.stl and o.smooth:
        mesh = build_smooth(g, o.radius, o.height or o.radius, o.base,
                            area=o.area, nrings=o.rim, fine=o.fine)
        mesh.export(o.stl)
        back = trimesh.load(o.stl)            # report on the file, not the object
        b = back.split(only_watertight=False)
        e = back.extents
        print(f'   {o.stl}: {len(back.faces)} triangles, '
              f'{e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f} mm, '
              f'{len(b)} bodies, all closed: {all(x.is_watertight for x in b)}, '
              f'{os.path.getsize(o.stl)/1e6:.1f} MB')
    elif o.stl:
        parts = [trimesh.creation.extrude_polygon(p, o.base)
                 for p in (g.geoms if hasattr(g, 'geoms') else [g])]
        for (z0, g0), (z1, _) in zip(rs[:-1], rs[1:]):
            if z1 - z0 < 1e-5:
                continue
            for p in (g0.geoms if hasattr(g0, 'geoms') else [g0]):
                m = trimesh.creation.extrude_polygon(p, z1 - z0)
                m.apply_translation([0, 0, o.base + z0])
                parts.append(m)
        mesh = trimesh.boolean.union(parts, engine='manifold')
        mesh.merge_vertices()
        mesh.export(o.stl)
        e = mesh.extents
        b = mesh.split(only_watertight=False)
        print(f'   {o.stl}: {len(mesh.faces)} triangles, '
              f'{e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f} mm, '
              f'{len(b)} bodies, all closed: {all(x.is_watertight for x in b)}')
