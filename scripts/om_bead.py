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


PAGE = 'assets/om-monogram/om-pattern-page.pdf'

# One repeat of the pattern, read off the page it comes from. Positions
# are fractions of the cell, sizes are the marks' real millimetres on
# that page, and the cell is 89.0 x 84.7 mm there - so the whole block
# scales to the ball by one number and keeps its proportions.
CELL_MM = (89.0, 84.7)
PATTERN = [
    # name  crop box on the page            u       v      long side mm
    ('om',   (0.1038, 0.0940, 0.2140, 0.2420),  0.000,  0.000, 26.7),
    ('sq',   (0.2858, 0.1030, 0.3432, 0.1825),  0.531, -0.063, 14.5),
    ('n925', (0.2532, 0.2667, 0.3432, 0.3379),  0.471,  0.329, 21.9),
    ('circ', (0.1197, 0.3129, 0.1830, 0.4050), -0.014,  0.475, 15.5),
    ('outl', (0.2443, 0.3910, 0.3106, 0.4806),  0.402,  0.663, 14.0),
]


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


def tiles(radius, cw, cap_deg, mark=1.0):
    """The repeat laid over the ball: whole cells, each with its five marks.

    The pattern is not five motifs taking turns, it is one block of five
    that repeats, and the block has to stay together or the thing stops
    reading as a pattern. So the cells are placed, not the marks: rows a
    cell-height apart, each row holding as many whole cells as its own
    circumference takes, and the five marks dropped into each cell at the
    fractions they sit at on the page.

    Row spacing is an arc, so the step in latitude is the cell height
    over the radius. Within a row the step in longitude is the cell width
    over the radius, divided by cos(latitude), because a degree of
    longitude is shorter the further from the equator it is.
    """
    ch = cw * CELL_MM[1] / CELL_MM[0]
    k = cw / CELL_MM[0]                       # page millimetres to ball
    deg = 180.0 / (math.pi * radius)
    out = []
    rows = int(math.floor(cap_deg / (ch * deg)))
    for r in range(-rows, rows + 1):
        lat0 = r * ch * deg
        n = max(1, int(round(2 * math.pi * radius
                             * math.cos(math.radians(lat0)) / cw)))
        for c in range(n):
            lon0 = -180.0 + 360.0 * c / n
            for i, (_, _, u, v, long_mm) in enumerate(PATTERN):
                lat = lat0 - v * ch * deg
                cl = max(math.cos(math.radians(lat)), 0.30)
                lon = lon0 + u * cw * deg / cl
                out.append((((lon + 180.0) % 360.0) - 180.0, lat, i,
                            long_mm * k * mark))
    return out


def paint(stamps, places, radius, W, Hh):
    """Equirectangular ink map, stretched for latitude, wrapped in longitude."""
    ink = np.zeros((Hh, W), bool)
    deg_per_mm = 180.0 / (math.pi * radius)        # along a great circle
    for lon, lat, which, long_mm in places:
        s = stamps[which]
        # size by the LONGER side, or a wide mark comes out three times
        # the width of the ball it is sitting on
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


def build(stamps, out, dia=8.0, bore=1.2, cell=5.0, mark=1.3, height=0.10,
          inset=0.05, cap=76.0, sub=7, W=3600, Hh=1800, cut=False):
    # embossed, the marks stand proud and the ball under them is
    # smaller by that much; engraved, the ball is the full size and the
    # marks go into it. Either way the bead measures the 8 mm it is
    # called.
    r = dia / 2.0 if cut else (dia - 2 * height) / 2.0
    places = tiles(r, cell, cap, mark)
    ink = paint(stamps, places, r, W, Hh)
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
    print(f'   {len(places)//len(PATTERN)} cells of {len(PATTERN)} = '
          f'{len(places)} marks, cell {cell:.2f} x '
          f'{cell*CELL_MM[1]/CELL_MM[0]:.2f} mm, '
          f'marks x{mark:.2f}, relief {height:.2f} mm, bore {bore:.2f} mm')
    return m, ink, rel


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--dia', type=float, default=8.0)
    a.add_argument('--bore', type=float, default=1.2)
    a.add_argument('--cell', type=float, default=5.0,
                   help='width of one repeat of the pattern, mm')
    a.add_argument('--simple', action='store_true',
                   help='two marks to the cell, OM and the framed cross, '
                        'staggered - the page pattern thinned for a ball '
                        'this small')
    a.add_argument('--mark', type=float, default=1.3,
                   help='scale the marks within the cell; the page '
                        'proportions are thin for an 8 mm ball')
    a.add_argument('--relief', type=float, default=0.10)
    a.add_argument('--cut', action='store_true',
                   help='engrave the marks into the ball instead of '
                        'raising them off it')
    a.add_argument('--sub', type=int, default=7)
    a.add_argument('--out', default='assets/om-bead/om-bead-8mm.stl')
    o = a.parse_args()
    os.makedirs(os.path.dirname(o.out), exist_ok=True)
    if o.simple:
        keep = {'om': (0.00, 0.00, 26.7), 'sq': (0.50, 0.50, 14.5)}
        PATTERN[:] = [(n, b, *keep[n]) for n, b, _, _, _ in PATTERN
                      if n in keep]
    stamps = [stamp_from_pdf(PAGE, box=b, px=2200) for _, b, _, _, _ in PATTERN]
    for (nm, _, u, v, mm), st in zip(PATTERN, stamps):
        print(f'   {nm:5s} {st.shape[1]:4d} x {st.shape[0]:4d} px   '
              f'cell ({u:+.3f},{v:+.3f})   {mm:.1f} mm on the page')
    build(stamps, o.out, dia=o.dia, bore=o.bore, cell=o.cell, mark=o.mark,
          height=o.relief, sub=o.sub, cut=o.cut)
