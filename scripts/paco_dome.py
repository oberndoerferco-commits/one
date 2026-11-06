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


# medial_axis thins in a randomised order unless it is handed a
# generator. Left to itself it returns a slightly different skeleton
# every run, which moved both the measured stroke widths and the
# triangle count of the exported mesh.
RNG = 20251106


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




def halfwidth(poly, inset, ppmm=80, smooth=0.18):
    """For every point, half the width of the stroke it belongs to.

    This is the quantity the old profile was missing. The dome was struck
    from the edge on a fixed radius, so a stroke narrower than twice that
    radius ran out of width before the profile had flattened and the two
    faces met at the centre still climbing - a knife edge down the middle
    of every narrow stroke. No mesh can smooth that away, because the
    surface really does have an edge there.

    Half the local width is the distance to the outline at the medial
    axis, carried out to the rest of the stroke: the nearest skeleton
    point to any interior point is the one whose disc that point sits in.
    scipy's EDT returns those indices for free. It is then blurred,
    because the raw field steps where one branch of the skeleton takes
    over from another, and nothing about a stroke's width should step.
    """
    from skimage.morphology import medial_axis
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paco_weights import _mask
    from scipy import ndimage
    m, (ox, oy) = _mask(poly, ppmm)
    sk, dist = medial_axis(m, return_distance=True, rng=RNG)
    if not sk.any():
        sk = m
    _, idx = ndimage.distance_transform_edt(~sk, return_indices=True)
    hw = dist[idx[0], idx[1]] / ppmm
    k = max(1.0, smooth * ppmm)
    hw = ndimage.gaussian_filter(hw, k, mode='nearest')
    return hw, (ox, oy), ppmm


def profile(d, hw, inset, height):
    """Height of the dome, given distance to the edge and half the width.

    Where a stroke is wide enough to carry the full radius the profile is
    exactly what it always was - rolled over `inset` and flat after, which
    already meets its plateau with zero slope.

    Where it is not, the same arc is fitted to the stroke's own half
    width instead. It reaches the identical crown the old profile reached
    there, so every figure in the crown table still holds, but it arrives
    at the centre horizontal rather than at a corner. Narrow ribs come
    out slightly fuller through the middle, which is what a round-topped
    rib looks like, and nowhere on the part is there an edge any more
    except the outline itself.
    """
    d = np.asarray(d, dtype=float)
    hw = np.maximum(np.asarray(hw, dtype=float), d)      # d/hw <= 1 always
    g = lambda t: np.sqrt(np.clip(2 * t - t * t, 0.0, None))   # arc, flat at t=1
    wide = hw >= inset
    out = np.empty_like(d)
    out[wide] = height * g(np.minimum(d[wide], inset) / inset)
    nw = ~wide
    if nw.any():
        crown = height * g(hw[nw] / inset)               # the crown it had before
        out[nw] = crown * g(d[nw] / np.maximum(hw[nw], 1e-9))
    return out


def _pslg(poly, step=0.12):
    V, S, holes = [], [], []
    for ring in [poly.exterior] + list(poly.interiors):
        c = _densify(list(ring.coords)[:-1] + [ring.coords[0]], step)[:-1]
        k = len(V)
        V += c
        S += [(k + a, k + (a + 1) % len(c)) for a in range(len(c))]
    for ring in poly.interiors:
        q = Polygon(ring).representative_point()
        holes.append((q.x, q.y))
    d = dict(vertices=np.array(V), segments=np.array(S))
    if holes:
        d['holes'] = np.array(holes)
    return d


def _height(poly, inset, height, base, soft=0.10, lo=0.15, hi=0.45, ppmm=80):
    """The dome, rounded where it would otherwise crease.

    Any height that is a function of distance-to-edge alone creases along
    the medial axis, because the distance field does: a stroke narrower
    than twice the inset arrives at its own centre still climbing. The
    previous answer was to fit the arc to each stroke's own half width.
    That removed the crease and introduced a worse fault, because half
    the local width is not a smooth quantity - it jumps wherever one
    branch of the medial axis takes over from another, and a jump of half
    a millimetre carried into the height gives surface normals sixty
    degrees out. Refining the mesh cannot help with that: the error was
    in the surface, not in the triangles, and it did not shrink when the
    triangle count tripled.

    So the crease is rounded instead of designed around. The dome is
    rastered, blurred with a small kernel - mask-normalised, so the
    outside cannot drag the inside down - and blended back over the exact
    profile with a weight that is zero at the rim and one well inside.
    The rim keeps the exact outline and its vertical tangent into the
    wall; the crest, which is the only place a crease can form, is
    entirely in the blurred part and comes out rounded over about
    `soft`. In between, both terms are smooth and so is the weight: the
    narrowest stroke here is 1.26 mm, so its crest sits at d = 0.63 and
    the blend has finished by 0.45.
    """
    import shapely
    from scipy import ndimage
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paco_weights import _mask
    m, (ox, oy) = _mask(poly, ppmm)
    din = ndimage.distance_transform_edt(m) / ppmm
    zr = base + dome_z(din, inset, height)
    k = soft * ppmm
    num = ndimage.gaussian_filter(np.where(m, zr, 0.0), k, mode='nearest')
    den = ndimage.gaussian_filter(m.astype(float), k, mode='nearest')
    zb = num / np.maximum(den, 1e-9)

    def z(xy):
        xy = np.atleast_2d(np.asarray(xy, dtype=float))
        d = shapely.distance(poly.boundary, shapely.points(xy))
        ze = base + dome_z(d, inset, height)
        zs = ndimage.map_coordinates(
            zb, [(xy[:, 1] - oy) * ppmm, (xy[:, 0] - ox) * ppmm],
            order=3, mode='nearest')
        t = np.clip((d - lo) / (hi - lo), 0.0, 1.0)
        w = t * t * (3.0 - 2.0 * t)
        return (1.0 - w) * ze + w * zs
    return z


def mesh_plan(poly, inset, height, base, target_deg=1.5, area0=0.01,
              rounds=6, floor=1.5e-4, step=0.12):
    """Triangulate the plan, sized by the error it actually makes.

    The first version seeded this by hand - contours packed along the rim,
    chains along the crease - to put triangles where the surface needed
    them. It put slivers there instead: sixteen per cent of the top faces
    came out with a minimum angle under ten degrees, and those faces
    missed the true normal by 13 degrees at the median against 1.3 for
    well shaped ones. The seeds were the defect. Handed the outline
    alone, the same mesher returns a minimum angle of 30 degrees and no
    slivers at all, instantly, at a quarter of the triangles.

    So nothing is placed by hand. `triangle` is asked for a quality mesh,
    no angle under 30 degrees, which is what keeps a normal honest, and
    is then told where to make it finer. The test needs no guess about
    curvature: over a triangle of size h a surface stands s = h^2 k / 8
    off the chord while the chord's normal misses by h k / 2, so the
    normal error is 4 s / h. Sample the height at the centroid, compare
    with the plane through the corners, quarter anything over target.

    `floor` stops it at the rim, where the profile is tangent to the side
    wall and the curvature is unbounded: no mesh can hold an angle there,
    and chasing it once cost three million triangles for one letter.
    """
    import triangle as tri
    pslg = _pslg(poly, step)
    z_of = _height(poly, inset, height, base)
    t = tri.triangulate(pslg, f'pq30a{area0}')
    tol = math.radians(target_deg)
    extra = {'holes': pslg['holes']} if 'holes' in pslg else {}
    for _ in range(rounds):
        V, F = t['vertices'], t['triangles']
        zv = z_of(V)
        T = V[F]
        a = np.abs(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])) / 2.0
        sag = np.abs(z_of(T.mean(axis=1)) - zv[F].mean(axis=1))
        need = (4.0 * sag / np.sqrt(np.maximum(a, 1e-18)) > tol) & (a > floor)
        if not need.any():
            break
        t = tri.triangulate(dict(vertices=V, segments=pslg['segments'], **extra,
                                 triangles=F,
                                 triangle_max_area=np.where(need, a / 4.0, -1.0)),
                            'rpq30a')
    return t['vertices'], t['triangles'], z_of


def solid(poly, inset, height, base, target_deg=1.5, step=0.12):
    """One body: the plan meshed to a normal-error target, lifted, closed."""
    v2, f, z_of = mesh_plan(poly, inset, height, base, target_deg, step=step)
    n = len(v2)
    VV = np.vstack([np.column_stack([v2, z_of(v2)]),
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


def _worker(src, dst):
    """Build one body, in this interpreter, and write the mesh out."""
    import shapely.wkb
    poly = shapely.wkb.loads(open(src + '.wkb', 'rb').read())
    a = json.load(open(src + '.json'))
    m = solid(poly, a['inset'], a['height'], a['base'],
              a['target_deg'], a['step'])
    np.savez(dst, v=np.asarray(m.vertices), f=np.asarray(m.faces))


def build_smooth(g, inset, height, base, target_deg=1.5, step=0.12):
    """The whole part, one body at a time, each in its own interpreter.

    The bodies are disjoint, so there is no boolean to do and none of the
    degenerate seam triangles a union leaves. They are built in separate
    processes for a less pleasant reason: `triangle` is a C library that
    carries state between calls. Run in sequence it returned a different
    triangle count for the same body depending on what had been
    triangulated before it, and segfaulted on the seventh. A result that
    depends on call history is not a result, whatever it looks like.

    A multiprocessing Pool was the tidy way to do that and it deadlocked
    - four workers idle at zero CPU, nothing to show for seven minutes.
    Plain subprocesses with the geometry on disk are duller and they
    finish, which is the only property that matters here.
    """
    import subprocess, tempfile
    ps = list(g.geoms) if hasattr(g, 'geoms') else [g]
    cfg = dict(inset=inset, height=height, base=base,
               target_deg=target_deg, step=step)
    me = os.path.abspath(__file__)
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, poly in enumerate(ps):
            src = os.path.join(tmp, f'b{i}')
            dst = os.path.join(tmp, f'b{i}.npz')
            open(src + '.wkb', 'wb').write(poly.wkb)
            json.dump(cfg, open(src + '.json', 'w'))
            r = subprocess.run([sys.executable, me, '--worker', src, dst],
                               capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(dst):
                raise SystemExit(f'body {i} failed ({r.returncode})\n'
                                 + r.stderr[-2000:])
            d = np.load(dst)
            out.append(trimesh.Trimesh(vertices=d['v'], faces=d['f'],
                                       process=False))
            print(f'   body {i}: {len(d["f"])} triangles', flush=True)
    return trimesh.util.concatenate(out)


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--worker':
        _worker(sys.argv[2], sys.argv[3])
        sys.exit(0)
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
    a.add_argument('--target', type=float, default=1.5,
                   help='largest angle, in degrees, by which a face may miss '
                        'the true surface normal; the mesh is refined until '
                        'it holds')
    a.add_argument('--step', type=float, default=0.12,
                   help='spacing the outline is densified to, mm')
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
                            target_deg=o.target, step=o.step)
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
