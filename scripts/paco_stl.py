#!/usr/bin/env python3
"""Solid model of the PA & CO logo, for tooling or printing.

By default the parts are the logo itself: P, A, ampersand, C, the O with
its bar, and the diamond, each extruded to the given thickness and nothing
underneath them. --plate instead sinks the logo into a slab, which is what
a debossing die has to produce. Dimensions are millimetres, which is what
STL consumers assume.

    python3 scripts/paco_stl.py --thickness 1.5 --out assets/paco/paco-logo.stl
    python3 scripts/paco_stl.py --plate --depth 0.30 --out .../paco-deboss.stl
"""
import argparse, math, sys, os
import numpy as np, pymupdf, trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import subpaths, assemble, MM


def logo(src):
    d = pymupdf.open(src); p = d[0]
    g = assemble([np.array(r) for r in subpaths(p)])
    W, H = p.rect.width / MM, p.rect.height / MM
    # flip to a right-handed frame and centre it
    from shapely import affinity
    g = affinity.scale(g, 1, -1, origin=(0, 0))
    g = affinity.translate(g, -W / 2, H / 2)
    return g, W, H


def rolled(poly, thickness, roll, steps):
    """Extrude with the edge rolled over, as a stack of inset slices.

    A flat extrusion plus a chamfer reads as a cut-off edge. Rolling it
    means the inset follows a circle: at height z into the roll the polygon
    is pulled in by r - sqrt(r^2 - (r - z)^2), which is the same profile
    the viewer draws, so the printed part matches what was approved.
    """
    if roll <= 0.001:
        return trimesh.creation.extrude_polygon(poly, thickness)
    roll = min(roll, thickness / 2 - 1e-3)
    zs, insets = [], []
    for i in range(steps + 1):                      # bottom roll, rising
        z = roll * i / steps
        zs.append(z); insets.append(roll - math.sqrt(max(0.0, roll*roll - (roll - z)**2)))
    zs.append(thickness - roll); insets.append(0.0)  # straight waist
    for i in range(1, steps + 1):                    # top roll, falling
        z = thickness - roll + roll * i / steps
        d = roll - math.sqrt(max(0.0, roll*roll - (roll - (thickness - z))**2))
        zs.append(z); insets.append(d)
    rings = []
    for z, d in zip(zs, insets):
        q = poly if d <= 0 else poly.buffer(-d, join_style=2, mitre_limit=4)
        if q.is_empty:
            q = poly.buffer(-d * 0.98, join_style=2, mitre_limit=4)
        rings.append((z, q))
    slabs = []
    for (z0, q0), (z1, q1) in zip(rings[:-1], rings[1:]):
        if z1 - z0 < 1e-6:
            continue
        use = q0 if q0.area >= q1.area else q1      # the wider of the pair
        for piece in (use.geoms if hasattr(use, 'geoms') else [use]):
            m = trimesh.creation.extrude_polygon(piece, z1 - z0)
            m.apply_translation([0, 0, z0])
            slabs.append(m)
    return trimesh.boolean.union(slabs, engine='manifold') if len(slabs) > 1 else slabs[0]


def build(src, depth, margin, thickness, emboss, plate_on=True, roll=0.0, steps=6):
    L, W, H = logo(src)
    if not plate_on:
        parts = []
        for g in L.geoms:
            parts.append(rolled(g, thickness, roll, steps))
        mesh = trimesh.util.concatenate(parts)
        mesh.merge_vertices()
        return mesh, W, H, thickness
    plate = box(-(W + 2 * margin) / 2, -(H + 2 * margin) / 2,
                (W + 2 * margin) / 2, (H + 2 * margin) / 2)
    parts = []
    if emboss:
        parts.append(trimesh.creation.extrude_polygon(plate, thickness))
        for g in L.geoms:
            m = trimesh.creation.extrude_polygon(g, depth)
            m.apply_translation([0, 0, thickness])
            parts.append(m)
        total = thickness + depth
    else:
        # a real subtraction, not two slabs stacked: stacking leaves coincident
        # faces at the interface and the result is not a closed solid, which a
        # toolmaker's software will reject
        slab = trimesh.creation.extrude_polygon(plate, thickness)
        cutters = []
        for g in L.geoms:
            c = trimesh.creation.extrude_polygon(g, depth + 1.0)
            c.apply_translation([0, 0, thickness - depth])
            cutters.append(c)
        mesh = trimesh.boolean.difference(
            [slab, trimesh.util.concatenate(cutters)], engine='manifold')
        mesh.merge_vertices()
        return mesh, W, H, thickness
    mesh = trimesh.util.concatenate(parts)
    mesh.merge_vertices()
    return mesh, W, H, total


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-min1mm-FINAL.pdf')
    a.add_argument('--out', required=True)
    a.add_argument('--depth', type=float, default=0.30)
    a.add_argument('--margin', type=float, default=7.0)
    a.add_argument('--thickness', type=float, default=1.5)
    a.add_argument('--emboss', action='store_true')
    a.add_argument('--plate', action='store_true',
                   help='sink the logo into a slab instead of standing alone')
    a.add_argument('--roll', type=float, default=0.0,
                   help='radius of the rolled-over edge, mm')
    a.add_argument('--steps', type=int, default=6)
    o = a.parse_args()
    m, W, H, T = build(o.src, o.depth, o.margin, o.thickness, o.emboss, o.plate,
                       o.roll, o.steps)
    m.export(o.out)
    e = m.extents
    print(f'{o.out}: {len(m.faces)} triangles, {len(m.vertices)} vertices')
    print(f'   extent {e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f} mm   '
          f'logo {W:.2f} x {H:.2f} mm')
    bodies = m.split(only_watertight=False)
    print(f'   {len(bodies)} bodies, all closed: '
          f'{all(b.is_watertight for b in bodies)}   volume {m.volume:.1f} mm3')
