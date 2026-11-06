#!/usr/bin/env python3
"""An 8 mm bead carrying the marks as a monogram pattern.

The motifs are not drawn onto the sphere one by one. They are painted
into an equirectangular map, the map is turned into a relief by the same
rule the PA & CO part uses - height from distance to the edge of the
mark - and an icosphere is displaced radially through it. Two details
matter and both are about the map being a map:

A stamp near the equator and the same stamp near the pole cover very
different spans of longitude for the same width on the ball, so each one
is stretched by 1 / cos(latitude) as it is painted. Without that the
marks come out pinched at the top and bottom.

The map wraps, so a mark crossing the date line has to be painted on
both sides of it. Painting is done with modular indexing, which costs
nothing and removes the seam.
"""
import argparse, math, os, sys
import numpy as np, pymupdf, trimesh
from scipy import ndimage

MM = 72.0 / 25.4


def stamp_from_pdf(path, box=None, px=900, pad=6):
    """A mark as a binary stamp, trimmed to its own ink."""
    d = pymupdf.open(path)
    p = d[0]
    zoom = px / max(p.rect.width, p.rect.height)
    pm = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    m = a.mean(2) < 128
    if box:
        x0, y0, x1, y1 = box
        m = m[int(y0 * m.shape[0]):int(y1 * m.shape[0]),
              int(x0 * m.shape[1]):int(x1 * m.shape[1])]
    ys, xs = np.nonzero(m)
    if not len(ys):
        raise SystemExit(f'no ink in {path} {box}')
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.pad(m, pad)


def rotate(mask, deg):
    return ndimage.rotate(mask.astype(float), deg, order=1,
                          reshape=True, mode='constant', cval=0.0) > 0.5


def fibonacci(n, cap_deg):
    """Points spread evenly over the ball, poles left clear for the hole.

    The golden spiral only spreads evenly if z steps uniformly over the
    whole sphere, so the band is taken out of a full spiral rather than
    the spiral being restricted to the band. A sphere's area between two
    latitudes is proportional to the span in z, which is what makes that
    work and what makes the count come out right.
    """
    lim = math.sin(math.radians(cap_deg))
    M = max(n, int(math.ceil(n / max(lim, 0.05))))
    ga = math.pi * (3 - math.sqrt(5))
    out = []
    for i in range(M):
        z = 1 - 2 * (i + 0.5) / M
        if abs(z) > lim:
            continue
        out.append((math.degrees((i * ga) % (2 * math.pi)) - 180,
                    math.degrees(math.asin(z))))
    return out


def paint(stamps, places, size_mm, radius, W, Hh, rng):
    """Equirectangular ink map, stretched for latitude, wrapped in longitude."""
    ink = np.zeros((Hh, W), bool)
    deg_per_mm = 180.0 / (math.pi * radius)        # along a great circle
    for n, (lon, lat) in enumerate(places):
        s, k = stamps[n % len(stamps)]
        s = rotate(s, rng.uniform(-12, 12))   # upright, like a monogram
        # size by the LONGER side, or a wide mark comes out three times
        # the width of the ball it is sitting on
        long_mm = size_mm * k
        if s.shape[1] >= s.shape[0]:
            w_mm, h_mm = long_mm, long_mm * s.shape[0] / s.shape[1]
        else:
            h_mm, w_mm = long_mm, long_mm * s.shape[1] / s.shape[0]
        h_deg = h_mm * deg_per_mm
        w_deg = w_mm * deg_per_mm / max(math.cos(math.radians(lat)), 0.25)
        ph = max(3, int(round(h_deg / 180.0 * Hh)))
        pw = max(3, int(round(w_deg / 360.0 * W)))
        z = np.array(ndimage.zoom(s.astype(float), (ph / s.shape[0], pw / s.shape[1]),
                                  order=1) > 0.5)
        r0 = int(round((90 - lat) / 180.0 * Hh)) - z.shape[0] // 2
        c0 = int(round((lon + 180) / 360.0 * W)) - z.shape[1] // 2
        rr = np.clip(np.arange(r0, r0 + z.shape[0]), 0, Hh - 1)
        cc = np.arange(c0, c0 + z.shape[1]) % W          # wraps, so no seam
        ink[np.ix_(rr, cc)] |= z
    return ink


def relief(ink, radius, W, Hh, height, inset):
    """Depth or height from distance to the edge of the mark.

    A laser mark is not a dome. It goes to its full depth within a few
    hundredths of a millimetre of the edge and stays flat across the
    middle, so the profile here is a smoothstep over `inset` rather than
    an arc over half the stroke - flat floor, crisp wall, a slightly
    eased lip so it does not read as a stamped-out hole.
    """
    mm_per_px_lat = math.pi * radius / Hh
    d = ndimage.distance_transform_edt(ink) * mm_per_px_lat
    t = np.clip(d / max(inset, 1e-9), 0.0, 1.0)
    return height * (t * t * (3.0 - 2.0 * t))


def framed(mask, border=0.055):
    """A mark the right way round, inside its own square.

    The tile carries this element in reverse - a filled square with the
    cross knocked out of it - so used as it comes the square is the mark
    and the cross is the gap. Inverted, the cross is the mark; the square
    is then drawn back round it as a rule, which is what it is on the
    tile.
    """
    m = ~mask
    b = max(2, int(round(border * min(m.shape))))
    m[:b, :] = m[-b:, :] = True
    m[:, :b] = m[:, -b:] = True
    return m


def build(stamps, out, dia=8.0, bore=1.2, n=30, size=2.6, height=0.10,
          inset=0.05, cap=74.0, sub=7, W=3600, Hh=1800, seed=7,
          cut=False):
    # embossed, the marks stand proud and the ball under them is
    # smaller by that much; engraved, the ball is the full size and the
    # marks go into it. Either way the bead measures the 8 mm it is
    # called.
    r = dia / 2.0 if cut else (dia - 2 * height) / 2.0
    rng = np.random.default_rng(seed)
    places = fibonacci(n, cap)
    ink = paint(stamps, places, size, r, W, Hh, rng)
    rel = relief(ink, r, W, Hh, height, inset)
    if cut:
        rel = -rel
    rel = ndimage.gaussian_filter(rel, 1.2, mode='wrap')     # kill the pixel step
    ball = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    v = ball.vertices.view(np.ndarray).copy()
    n_ = np.linalg.norm(v, axis=1)
    lat = np.degrees(np.arcsin(np.clip(v[:, 2] / n_, -1, 1)))
    lon = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
    rr = (90 - lat) / 180.0 * Hh
    cc = (lon + 180) / 360.0 * W
    dr = ndimage.map_coordinates(rel, [rr, cc], order=1, mode='wrap')
    v *= ((r + dr) / n_)[:, None]
    m = trimesh.Trimesh(vertices=v, faces=ball.faces.view(np.ndarray).copy(),
                        process=False)
    m.process(validate=True)
    if bore:
        cyl = trimesh.creation.cylinder(radius=bore / 2.0, height=dia * 2.0,
                                        sections=96)
        m = trimesh.boolean.difference([m, cyl], engine='manifold')
    m.merge_vertices()
    m.process(validate=True)
    m.fix_normals()
    m.export(out)
    back = trimesh.load(out)
    b = back.split(only_watertight=False)
    print(f'{out}: {len(back.faces)} triangles, '
          f'{back.extents[0]:.2f} x {back.extents[1]:.2f} x {back.extents[2]:.2f} mm, '
          f'{len(b)} bodies, closed: {all(x.is_watertight for x in b)}, '
          f'{os.path.getsize(out)/1e6:.1f} MB')
    print(f'   {len(places)} marks, {size:.2f} mm each, relief {height:.2f} mm, '
          f'bore {bore:.2f} mm')
    return m, ink, rel


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--dia', type=float, default=8.0)
    a.add_argument('--bore', type=float, default=1.2)
    a.add_argument('--marks', type=int, default=30)
    a.add_argument('--size', type=float, default=2.6)
    a.add_argument('--relief', type=float, default=0.10)
    a.add_argument('--cut', action='store_true',
                   help='engrave the marks into the ball instead of '
                        'raising them off it')
    a.add_argument('--sub', type=int, default=7)
    a.add_argument('--out', default='assets/om-bead/om-bead-8mm.stl')
    o = a.parse_args()
    os.makedirs(os.path.dirname(o.out), exist_ok=True)
    T = 'assets/motif-tiles/motif-black-white.pdf'
    stamps = [
        (stamp_from_pdf('assets/om-mark/om-lockup-4mm.pdf'), 1.35),
        (stamp_from_pdf(T, box=(0.02, 0.02, 0.50, 0.50)), 0.80),   # cross in a circle
        (framed(stamp_from_pdf(T, box=(0.47, 0.52, 0.97, 0.97), pad=0)),
         0.72),                                                    # cross in a square
    ]
    for i, (s, k) in enumerate(stamps):
        print(f'   stamp {i}: {s.shape[1]} x {s.shape[0]} px, x{k:.2f}')
    build(stamps, o.out, dia=o.dia, bore=o.bore, n=o.marks, size=o.size,
          height=o.relief, sub=o.sub, cut=o.cut)
