#!/usr/bin/env python3
"""The TraxNYC crest as a domed button with the crest struck into the face.

Not the PA & CO construction. There the lockup was six separate pieces,
each one domed into a rounded rib and each attached on its own. Here the
crest is a single button: a quatrefoil blank, its face a shallow
spherical cap, the band and the eagle head standing proud of that cap,
and rivet posts on the flat back. The head does not have to be joined to
the band, because the blank underneath carries it.

    back        flat, z = 0, where the posts are
    rim         --rim thick at the edge of the blank
    face        a spherical cap rising --crown at the centre
    relief      --relief above the face, its top edge rolled over --roll
    posts       --posts of --post-dia, --post-len long, on a diagonal

The solid is built as a stack of level sets rather than by cutting a
prism with a sphere. At height z the plan is

    blank  n  disc(R(z - rim))      u       relief_j  n  disc(R(z - rim - p_j))

- the blank wherever the cap is still above z, plus each inset ring of
the relief wherever the cap plus that ring's own height is still above z.
Every term is a 2D operation, which is cheap and exact, and the only
boolean left is the union of the slabs. Cutting a prism with a sphere
would need a boolean per relief step instead, and three.js cannot be
handed the result either way: its bevel insets by pushing vertices along
their normals, which self-intersects as soon as the inset passes half a
ridge's width, so the rings are computed here and the viewer is given
them.
"""
import argparse
import json
import math
import os
import sys

from shapely.geometry import Point
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trax_crest import SRC, pieces, prepare                       # noqa: E402


def cap_radius(rmax, crown):
    """Sphere radius for a cap that rises `crown` over a disc of `rmax`."""
    return (rmax * rmax + crown * crown) / (2 * crown)


def cap_plan_radius(t, rmax, crown):
    """Plan radius at which the cap is still `t` above the rim."""
    if t <= 0:
        return rmax
    if t >= crown:
        return 0.0
    rs = cap_radius(rmax, crown)
    k = math.sqrt(max(0.0, rs * rs - rmax * rmax))
    return math.sqrt(max(0.0, rs * rs - (t + k) ** 2))


def _cap_height(r, rmax, crown):
    """How far the cap stands above the rim at plan radius r."""
    rs = cap_radius(rmax, crown)
    return math.sqrt(max(0.0, rs * rs - r * r)) - math.sqrt(max(0.0, rs * rs - rmax * rmax))


def roll_profile(relief, roll, steps):
    """[(inset, height)] up the relief, rolled over at the top.

    The plateau is one entry, not two: an entry at zero inset and zero
    height would repeat the plan of the blank's own top, and two solids
    with the same side wall are what a boolean engine fails on.

    Equal steps of inset, not of height. Equal steps of height put the
    widest inset where the profile is flattest, and on a sharp corner
    that last step overshoots the shape and throws a spike - the same
    correction the PA & CO dome needed.
    """
    roll = min(roll, relief)
    out = [(0.0, relief - roll)]
    for i in range(1, steps + 1):
        d = roll * i / steps
        out.append((d, relief - roll + math.sqrt(max(0.0, roll * roll - (roll - d) ** 2))))
    return out


def _domed(poly, rim, crown, rmax, lift, edge, bottom=0.0):
    """A prism over `poly` whose top is the spherical cap, raised by `lift`.

    A prism is subdivided until no edge is longer than `edge`, and every
    vertex on its top face is then dropped onto the sphere. The ring
    shared with the side wall moves too, so the wall height follows the
    cap - which is why the rim comes out thinner at the star tips, the
    points furthest from the centre, than at the cardinals. That is what
    a domed blank does.
    """
    import numpy as np
    import trimesh
    h = rim + crown + lift
    # Simplify first. The relief comes out of a chain of buffers with
    # thousands of vertices a few microns apart, and subdividing a prism
    # built on those runs to 300,000 triangles for a face fifty across.
    poly = poly.simplify(0.01, preserve_topology=True)
    m = trimesh.creation.extrude_polygon(poly, h - bottom)
    m.apply_translation([0, 0, bottom])
    m = m.subdivide_to_size(max_edge=edge)
    v = np.asarray(m.vertices).copy()
    rs = cap_radius(rmax, crown)
    k = math.sqrt(max(0.0, rs * rs - rmax * rmax))
    r = np.hypot(v[:, 0], v[:, 1])
    ztop = rim + lift + np.sqrt(np.maximum(0.0, rs * rs - r * r)) - k
    # Every vertex moves, scaled by how far up the prism it sits, not
    # just the ring on the top face. Subdividing puts vertices partway up
    # the side walls, and dropping the top ring onto the sphere while
    # leaving those behind folds each wall through itself - which is what
    # made the union report twenty-two open shells.
    v[:, 2] = bottom + (v[:, 2] - bottom) * (ztop - bottom) / (h - bottom)
    m.vertices = v
    m.process(validate=True)
    if not m.is_watertight:
        import trimesh.repair
        trimesh.repair.fill_holes(m)
        m.process(validate=True)
    return m


def solids(blank, relief, rim, crown, relief_h, roll, edge=2.5, steps=3):
    """The blank and each ring of the relief, all domed, none booleaned.

    The relief could be had by intersecting a prism with a copy of the
    blank raised to that ring's height, and that was the first build.
    It is half a million triangles and it does not close: six copies of
    a subdivided blank through six booleans is more than manifold will
    hold together here. Lifting each ring's own top onto the same sphere
    gives the identical surface with no boolean at all, and leaves one
    union at the end instead of seven.
    """
    rmax = max(math.hypot(*p) for p in blank.exterior.coords)
    out = [_domed(blank, rim, crown, rmax, 0.0, edge)]
    for d, h in roll_profile(relief_h, roll, steps):
        g = relief if d <= 0 else relief.buffer(-d, join_style=1, quad_segs=12)
        for piece in pieces(g):
            if piece.area < 1e-3:
                continue
            # start each ring inside the blank, not flush with its back.
            # Solids that meet exactly on a plane share a pair of
            # coincident faces, and a union across them does not close -
            # the same thing that stopped the PA & CO deboss plate from
            # being watertight when it was built as stacked slabs.
            out.append(_domed(piece, rim, crown, rmax, h, edge, bottom=rim / 2))
    return out, rmax


def post_spots(n, radius):
    """Where the posts go, in plan."""
    angles = ([45, 225] if n == 2 else [45, 135, 225, 315] if n == 4 else
              [90 + 360 * i / n for i in range(n)])
    return [(radius * math.cos(math.radians(a)), radius * math.sin(math.radians(a)))
            for a in angles]


def post_meshes(spots, dia, length, chamfer, into=0.3, sections=48):
    """A rivet post per spot: a plain shaft with its free end broken.

    The shaft starts `into` above the back rather than flush with it. Two
    solids that meet exactly on a plane share a pair of coincident faces,
    and a union across coincident faces does not close - the same thing
    that stopped the PA & CO deboss plate from being watertight when it
    was built as stacked slabs instead of a real subtraction.
    """
    import trimesh
    r = dia / 2
    out = []
    for x, y in spots:
        h = into + length - chamfer
        shaft = trimesh.creation.cylinder(radius=r, height=h, sections=sections)
        shaft.apply_translation([x, y, into - h / 2])
        tip = trimesh.creation.cylinder(radius=r, height=chamfer, sections=sections)
        v = tip.vertices.copy()
        v[v[:, 2] < 0, :2] *= (r - chamfer) / r       # break the free end
        tip.vertices = v
        tip.apply_translation([x, y, -(length - chamfer) - chamfer / 2])
        out += [shaft, tip]
    return out


def build(parts):
    import trimesh
    mesh = trimesh.boolean.union([p for p in parts if len(p.faces)],
                                 engine='manifold')
    # Not merge_vertices: manifold already returns a closed mesh, and
    # welding its vertices by distance pulls the seams together and
    # leaves dozens of open shells. What the union does leave is
    # degenerate triangles along those seams, and they survive the trip
    # through an STL as edges with one face on them - a mesh a supplier's
    # software calls open. validate drops them.
    mesh.process(validate=True)
    return mesh


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default=SRC)
    a.add_argument('--width', type=float, default=50.0)
    a.add_argument('--cutter', type=float, default=0.70)
    a.add_argument('--fill', type=float, default=0.50)
    a.add_argument('--rim', type=float, default=0.90, help='thickness at the tips')
    a.add_argument('--crown', type=float, default=2.00, help='dome height, centre')
    a.add_argument('--relief', type=float, default=0.85, help='relief above the face')
    a.add_argument('--roll', type=float, default=0.25, help='rolled edge on the relief')
    a.add_argument('--edge', type=float, default=2.5,
                   help='longest mesh edge, mm; the cap departs from a '
                        '2.5 mm chord by 0.003 mm, so finer buys nothing')
    a.add_argument('--posts', type=int, default=2)
    a.add_argument('--post-dia', type=float, default=2.5)
    a.add_argument('--post-len', type=float, default=4.0)
    a.add_argument('--post-r', type=float, default=14.0)
    a.add_argument('--chamfer', type=float, default=0.4)
    a.add_argument('--stl')
    o = a.parse_args()

    blank, rel, rep = prepare(o.src, o.width, o.cutter, o.fill)
    shells, rmax = solids(blank, rel, o.rim, o.crown, o.relief, o.roll, o.edge)
    rs = cap_radius(rmax, o.crown)
    spots = post_spots(o.posts, o.post_r)
    clear = min(blank.exterior.distance(Point(x, y)) for x, y in spots)
    print(f'button {o.width:.1f} mm across, blank radius {rmax:.2f} mm')
    print(f'  face: spherical cap R {rs:.1f} mm, crown {o.crown:.2f} over a '
          f'{o.rim:.2f} rim at the tips, {o.rim + _cap_height(25.0, rmax, o.crown):.2f} '
          f'at the cardinals')
    print(f'  relief {o.relief:.2f} with a {o.roll:.2f} rolled edge; '
          f'{len(pieces(rel))} island(s) on the face')
    print(f'  {o.posts} posts, {o.post_dia:.1f} dia x {o.post_len:.1f} long at '
          f'r {o.post_r:.1f}; {clear:.1f} mm of blank beyond each, '
          f'{o.rim + _cap_height(o.post_r, rmax, o.crown):.2f} mm of metal over it')
    if clear < o.post_dia / 2 + 1.0:
        sys.exit(f'posts at r {o.post_r} leave only {clear:.2f} mm to the edge')

    if o.stl:
        mesh = build(shells + post_meshes(spots, o.post_dia, o.post_len,
                                          o.chamfer))
        mesh.export(o.stl)
        # read the file back rather than report on the object in memory:
        # the export is what the supplier opens
        import trimesh
        back = trimesh.load(o.stl)
        e = back.extents
        print(f'  {o.stl}: {len(back.faces)} triangles, '
              f'{e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f} mm, '
              f'{len(back.split(only_watertight=False))} body(ies), '
              f'closed: {back.is_watertight}, volume {back.volume:.0f} mm3')
        for name, rho in (('brass', 8.5), ('zinc alloy', 6.6)):
            print(f'     {back.volume / 1000 * rho:.0f} g in {name}')
