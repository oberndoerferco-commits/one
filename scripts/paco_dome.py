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
import numpy as np, pymupdf
from shapely.geometry import Polygon
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


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-min1mm-FINAL.pdf')
    a.add_argument('--radius', type=float, default=1.25)
    a.add_argument('--steps', type=int, default=16)
    a.add_argument('--base', type=float, default=0.60)
    a.add_argument('--json')
    a.add_argument('--stl')
    o = a.parse_args()

    g, W, H = artwork(o.src)
    rs = rings(g, o.radius, o.steps)
    print(f'{len(rs)} levels, dome {rs[-1][0]:.3f} mm tall over a {o.base:.2f} mm base')

    if o.json:
        d = to_json(rs, W, H, o.base)
        json.dump(d, open(o.json, 'w'), separators=(',', ':'))
        print(f'   {o.json}: {os.path.getsize(o.json)/1024:.0f} KB')

    if o.stl:
        import trimesh
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
