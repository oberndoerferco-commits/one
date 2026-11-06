#!/usr/bin/env python3
"""Engineering drawing for the PA & CO logo, two A3 landscape sheets.

Sheet 1 is the part: plan, a real section on a marked cutting plane, an
isometric, the dome profile the whole top surface is struck from, crown
height against stroke width, and the notes.

Sheet 2 is the numbers. A seven-piece assembly cannot be made from
overall width and height: every piece needs a position, and every gap
between pieces is a feature the tooling has to hold. So sheet 2 carries
an ordinate schedule from a datum at the bottom-left of the artwork, the
clearance between every pair of pieces that comes within 4 mm, and the
thinnest and thickest stroke in each piece with the crown each reaches.

Nothing here is typed in. Every figure is measured off the artwork that
the STL was built from, so the sheet cannot drift away from the part the
way a hand-kept drawing does.
"""
import argparse, itertools, json, math, os, sys
import numpy as np, pymupdf
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_dome import artwork, halfwidth, profile
from paco_drawing import (MM, THIN, MED, THICK, CHAIN, DASH, Sheet,
                          runs, wrap)
from paco_weights import _mask, _ends
from skimage.morphology import medial_axis

# medial_axis thins in a randomised order unless it is given a
# generator. Left to itself it returns a slightly different
# skeleton every run, which moved both the measured stroke widths
# and the triangle count of the exported mesh.
RNG = 20251106
from scipy import ndimage


# ---------------------------------------------------------------- measuring
def strokes(poly, ppmm=60, skip=0.8):
    """(thinnest, thickest) stroke in a shape, mm.

    Both read off the medial axis, where the distance to the boundary is
    half the local stroke. Terminals are cut back by `skip`: a stroke end
    tapers to nothing, so without that the minimum is always zero and
    says nothing about the stroke. maximum_filter does the cutting back
    because it separates; a 97 x 97 structuring element does not finish.
    """
    m, _ = _mask(poly, ppmm)
    sk, dist = medial_axis(m, return_distance=True, rng=RNG)
    e = _ends(sk)
    if e.any():
        k = int(skip * ppmm) * 2 + 1
        near = ndimage.maximum_filter(e, size=k)
        sk = sk & ~near
    if not sk.any():                      # a piece shorter than the skip
        sk = medial_axis(m, rng=RNG)
    d = dist[sk] / ppmm * 2
    return float(d.min()), float(d.max())


def surface(g, inset, height, base):
    """Height of the finished part at any point, from the same function
    the mesh is lifted by. The drawing cannot describe one profile while
    the STL is built to another, so it does not get its own copy."""
    import shapely
    from scipy import ndimage
    hwf, (hx, hy), pp = halfwidth(g, inset)

    def h(xy):
        xy = np.atleast_2d(xy)
        inside = shapely.contains_xy(g, xy[:, 0], xy[:, 1])
        d = shapely.distance(g.boundary, shapely.points(xy))
        hw = ndimage.map_coordinates(
            hwf, [(xy[:, 1] - hy) * pp, (xy[:, 0] - hx) * pp],
            order=1, mode='nearest')
        z = base + profile(d, hw, inset, height)
        z[~inside] = 0.0
        return z, inside
    return h


def crown_of(w, inset, height, base):
    """What a stroke `w` wide reaches, base included."""
    return base + float(profile(np.array([w / 2.0]), np.array([w / 2.0]),
                                inset, height)[0])


def measure(src, inset, height, base):
    g, W, H = artwork(src)                       # centred, y up
    ps = list(g.geoms) if hasattr(g, 'geoms') else [g]
    dia = max(ps, key=lambda p: len(p.interiors) + p.area / 1e3)
    letters = sorted((p for p in ps if p is not dia), key=lambda p: p.bounds[0])
    bar = min(letters, key=lambda p: p.area)
    order = [p for p in letters if p is not bar]
    names = ['P', 'A', 'AMPERSAND', 'C', 'O'][:len(order)]
    items = ([(n, p) for n, p in zip(names, order)]
             + [('BAR UNDER O', bar), ('DIAMOND', dia)])

    x0, y0 = g.bounds[0], g.bounds[1]            # datum: bottom-left of artwork
    rows = []
    for n, p in items:
        a, b, c, d = p.bounds
        tmin, tmax = strokes(p)
        rows.append(dict(name=n, x=a - x0, y=b - y0, w=c - a, h=d - b,
                         counters=len(p.interiors), area=p.area,
                         thin=tmin, thick=tmax,
                         crown=crown_of(tmax, inset, height, base)))
    gaps = []
    for (i, (ni, pi)), (j, (nj, pj)) in itertools.combinations(
            enumerate(items), 2):
        s = pi.distance(pj)
        if s < 4.0:
            gaps.append(dict(a=i + 1, b=j + 1, na=ni, nb=nj, d=s))
    gaps.sort(key=lambda q: q['d'])
    return g, W, H, rows, gaps, items, (x0, y0)


# ---------------------------------------------------------------- sheet one
def sheet_one(s, src, g, W, H, rows, gaps, inset, height, base, iso, stl):
    total = base + height
    H_of = surface(g, inset, height, base)

    s.rect(10, 10, 410, 287, w=0.7)
    s.rect(14, 14, 406, 283, w=0.25)

    SC, px, py = 2.0, 42, 32
    pw, ph = W * SC, H * SC
    s.text(px, py - 5.5, 'VIEW A    PLAN', 3.1, font='hebo')
    s.text(px + 36, py - 5.5, 'SCALE 2:1', 2.3, (.35, .35, .35))
    doc = pymupdf.open(src)
    s.pg.show_pdf_page(pymupdf.Rect(s.P(px, py), s.P(px + pw, py + ph)), doc, 0)
    s.line(px - 5, py + ph / 2, px + pw + 5, py + ph / 2, (0, 0, 0), THIN, CHAIN)
    s.line(px + pw / 2, py - 5, px + pw / 2, py + ph + 5, (0, 0, 0), THIN, CHAIN)
    s.dim_h(px, px + pw, py + ph + 10, f'{W:.2f}', ext=py + ph, below=True)
    s.dim_v(py, py + ph, px - 17, f'{H:.2f}', ext=px)

    # cut where the plane meets the most strokes: a section has to show
    # the part, and the widest row of the lockup is the one worth cutting
    best, Y_CUT = -1.0, -9.5
    for yc in np.arange(-H / 2 + 0.5, H / 2 - 0.5, 0.2):
        cut = g.intersection(LineString([(-W, yc), (W, yc)]))
        if cut.is_empty:
            continue
        parts = list(cut.geoms) if hasattr(cut, 'geoms') else [cut]
        # material on the plane, but a cut that meets more strokes says
        # more about the part than one long run through a single bowl
        score = cut.length + 1.2 * len(parts)
        if score > best:
            best, Y_CUT = score, float(yc)
    sy = py + (H / 2 - Y_CUT) * SC
    s.line(px - 9, sy, px + pw + 9, sy, (0, 0, 0), THICK, CHAIN)
    s.arrow(px - 9, sy + 4.5, 0, -1, 2.2); s.line(px - 9, sy, px - 9, sy + 4.5, w=THICK)
    s.arrow(px + pw + 9, sy + 4.5, 0, -1, 2.2)
    s.line(px + pw + 9, sy, px + pw + 9, sy + 4.5, w=THICK)
    s.text(px - 11.5, sy + 8, 'A', 3.2, font='hebo')
    s.text(px + pw + 7.5, sy + 8, 'A', 3.2, font='hebo')

    ax0, ay0 = px, py + ph + 30
    s.text(ax0, ay0 - 6, 'SECTION A-A', 3.1, font='hebo')
    s.text(ax0 + 30, ay0 - 6, 'SCALE 2:1', 2.3, (.35, .35, .35))
    s.text(ax0 + 56, ay0 - 6,
           f'the strokes the plane passes through, cut at y = {Y_CUT:+.2f}',
           2.3, (.35, .35, .35))
    xs = np.linspace(-W / 2, W / 2, 1400)
    hs, on = H_of(np.column_stack([xs, np.full(len(xs), Y_CUT)]))
    base_line = ay0 + 14
    for i, j in runs(xs, on):
        seg = [(ax0 + (xs[q] + W / 2) * SC, base_line - hs[q] * SC)
               for q in range(i, j + 1)]
        ring = [(seg[0][0], base_line)] + seg + [(seg[-1][0], base_line)]
        s.hatch(Polygon(ring), step=0.9, ang=45)
        s.poly(ring, w=THICK, close=True)
    s.line(ax0, base_line, ax0 + pw, base_line, w=THIN, dash=DASH)
    s.dim_v(base_line - total * SC, base_line, ax0 + pw + 9, f'{total:.2f}',
            ext=ax0 + pw, left=False)
    s.text(ax0, base_line + 7,
           'Crown varies with the width of the stroke the plane meets. '
           'See DETAIL C and the schedule on sheet 2.', 2.3, (.3, .3, .3))

    ix, iy, iw = 158, 30, 118
    img = pymupdf.open(iso); r = img[0].rect
    ih = iw * r.height / r.width
    s.pg.insert_image(pymupdf.Rect(s.P(ix, iy), s.P(ix + iw, iy + ih)), filename=iso)
    s.text(ix + iw / 2, iy + ih + 6, 'ISOMETRIC VIEW', 3.1, font='hebo', align=1)

    # DETAIL C : the two extremes actually present in the artwork
    thin = min(r['thin'] for r in rows)
    thick = max(r['thick'] for r in rows)
    SS = 20.0
    cx, cy = 158, iy + ih + 26
    s.text(cx, cy, 'DETAIL C', 3.1, font='hebo')
    s.text(cx + 22, cy, 'STROKE PROFILES', 2.6, (.35, .35, .35))
    s.text(cx + 56, cy, 'SCALE 20:1', 2.3, (.35, .35, .35))
    s.text(cx, cy + 4.5, 'the thinnest stroke in the artwork, and the width '
           'from which the dome is full height', 2.3, (.35, .35, .35))
    s.text(cx, cy + 8.5, 'each stroke is domed to its own width, so both '
           'close horizontal at the centre', 2.3, (.35, .35, .35))
    base_y = cy + 66
    for n_, (wid, lab) in enumerate([(thin, f'THINNEST  {thin:.2f}'),
                                     (2 * inset, f'FULL HEIGHT  {2*inset:.2f}')]):
        mid = cx + 20 + n_ * 62
        half = wid / 2 * SS
        bz = base * SS
        ch = crown_of(wid, inset, height, base) - base
        dd = np.linspace(0.0, wid / 2, 61)
        zz = profile(dd, np.full(61, wid / 2), inset, height)
        prof = list(zip(dd, zz))
        ring = ([(mid - half, base_y), (mid - half, base_y - bz)]
                + [(mid - half + d * SS, base_y - bz - z * SS) for d, z in prof]
                + [(mid + half - d * SS, base_y - bz - z * SS) for d, z in reversed(prof)]
                + [(mid + half, base_y - bz), (mid + half, base_y)])
        s.hatch(Polygon(ring), step=1.4, ang=45)
        s.poly(ring, w=THICK, close=True)
        s.line(mid - half, base_y - bz, mid + half, base_y - bz, (0, 0, 0), THIN, DASH)
        s.line(mid, base_y + 4, mid, base_y - bz - ch * SS - 5, (0, 0, 0), THIN, CHAIN)
        s.dim_h(mid - half, mid + half, base_y + 11, f'{wid:.2f}', ext=base_y, below=True)
        s.dim_v(base_y - bz - ch * SS, base_y, mid + half + 9, f'{bz / SS + ch:.2f}',
                ext=mid + half, left=False)
        s.text(mid, base_y + 17, lab, 2.4, font='hebo', align=1)
    s.dim_v(base_y - base * SS, base_y, cx + 4, f'{base:.2f}', ext=cx + 20 - thin / 2 * SS)
    for i, t in enumerate([
            'The dome is fitted to the width of the stroke it is on, not struck',
            'on one radius for the whole part. A narrow stroke reaches a lower',
            'crown, but it still arrives at its own centre horizontal, so the',
            'top surface is continuous everywhere. There is no ridge, and no',
            'edge anywhere on the part except the outline itself.']):
        s.text(cx, base_y + 26 + i * 4, t, 2.3, (.3, .3, .3))

    # DETAIL B : the dome profile, now one per stroke width
    dx0, dy0 = 292, 30
    s.text(dx0, dy0, 'DETAIL B', 3.1, font='hebo')
    s.text(dx0 + 22, dy0, 'DOME PROFILE', 2.6, (.35, .35, .35))
    s.text(dx0, dy0 + 4.5, 'fitted to the width of the stroke it is on',
           2.3, (.35, .35, .35))
    PS = 21.0
    gx, gy = dx0 + 8, dy0 + 54
    s.line(gx - 4, gy, gx + inset * PS + 12, gy, (0, 0, 0), THIN, CHAIN)
    s.line(gx, gy + 5, gx, gy - height * PS - 7, (0, 0, 0), THIN, CHAIN)
    for m_, lab, wt in ((inset, f'm >= {inset:.2f}', THICK),
                        (thin / 2, f'm = {thin/2:.2f}', MED)):
        dd = np.linspace(0.0, m_, 90)
        zz = profile(dd, np.full(90, m_), inset, height)
        s.poly([(gx + x_ * PS, gy - z_ * PS) for x_, z_ in zip(dd, zz)], w=wt)
        s.text(gx + m_ * PS + 1.5, gy - zz[-1] * PS - 1.0, lab, 2.2, (.35, .35, .35))
    s.line(gx, gy - height * PS, gx + inset * PS, gy - height * PS,
           (0, 0, 0), THIN, DASH)
    s.dim_h(gx, gx + inset * PS, gy + 11, f'{inset:.2f}', ext=gy, below=True)
    s.text(gx + inset * PS / 2, gy + 15, 'HALF WIDTH m', 2.2, (.35, .35, .35), align=1)
    s.dim_v(gy - height * PS, gy, gx + inset * PS + 13, f'{height:.2f}',
            ext=gx + inset * PS, left=False)
    s.text(gx - 2, gy + 4.5, 'EDGE OF STROKE', 2.2, (.35, .35, .35))
    s.text(dx0, gy + 21, 'z = C x sqrt( 2t - t^2 ),   t = d / m', 2.6)
    for i, t in enumerate([
            f'C = {height:.2f} for m >= {inset:.2f}, otherwise '
            f'C = {height:.2f} x sqrt( 2u - u^2 ), u = m / {inset:.2f}.',
            'd is measured in plan from the edge of the stroke and m is half',
            'the width of that stroke, so every stroke reaches its centre',
            'with the surface horizontal. One radius for the whole part put',
            'a ridge down the middle of every narrow stroke; this does not.']):
        s.text(dx0, gy + 25.5 + i * 3.7, t, 2.3, (.3, .3, .3))

    tx, ty = 292, gy + 48
    s.text(tx, ty - 4.5, 'CROWN HEIGHT BY STROKE WIDTH', 3.1, font='hebo')
    s.rect(tx, ty, tx + 114, ty + 5.8, w=MED, fill=(.9, .9, .9))
    for dxx, t in ((2.5, 'STROKE WIDTH'), (42, 'CROWN'), (66, 'NOTE')):
        s.text(tx + dxx, ty + 4, t, 2.3, font='hebo')
    yy = ty + 5.8
    table = [(thin, 'thinnest in artwork'), (1.50, ''), (2.00, ''),
             (2 * inset, 'full height from here'),
             (thick, 'widest point in artwork')]
    for w_, note in sorted(table):
        s.rect(tx, yy, tx + 114, yy + 5.4, w=THIN)
        s.text(tx + 2.5, yy + 3.8, f'{w_:.2f}', 2.3)
        s.text(tx + 42, yy + 3.8, f'{crown_of(w_, inset, height, base):.2f}', 2.3)
        s.text(tx + 66, yy + 3.8, note, 2.2, (.35, .35, .35))
        yy += 5.4
    s.text(tx, yy + 4, 'Crown figures include the '
           f'{base:.2f} mm base.', 2.2, (.35, .35, .35))

    ny = yy + 8
    s.text(tx, ny, 'NOTES', 3.1, font='hebo'); ny += 5.2
    tight = min(g_['d'] for g_ in gaps)
    for i, t in enumerate([
            'All dimensions in millimetres. Do not scale from this drawing.',
            f'{len(rows)} separate bodies. They do not touch and must not '
            'be joined. Positions and gaps on sheet 2.',
            f'Outline is fixed. No stroke may be thinned; {thin:.2f} mm is '
            'the minimum and is already at the limit.',
            f'Tightest gap between bodies is {tight:.2f} mm. See sheet 2.',
            'Top surface domed per DETAIL B, fitted to each stroke width. '
            'No ridges. Underside flat, no draft.',
            'Finish satin silver, uniform. No polished or mirror areas.',
            f'Geometry of record is the STL: {stl}',
            'General tolerance +/-0.05. Crown height +/-0.10.']):
        s.text(tx, ny, str(i + 1), 2.3, font='hebo')
        for j, ln in enumerate(wrap(t, 56)):
            s.text(tx + 4.5, ny + j * 3.6, ln, 2.3)
        ny += 3.6 * len(wrap(t, 56)) + 1.1
    return total, thin, thick


# ---------------------------------------------------------------- sheet two
def sheet_two(s, src, W, H, rows, gaps, items, datum, inset, height, base):
    s.rect(10, 10, 410, 287, w=0.7)
    s.rect(14, 14, 406, 283, w=0.25)

    SC, px, py = 3.0, 26, 40
    pw, ph = W * SC, H * SC
    s.text(px, py - 9, 'VIEW D    PLAN, ITEM NUMBERS AND DATUM', 3.1, font='hebo')
    s.text(px + 96, py - 9, 'SCALE 3:1', 2.3, (.35, .35, .35))
    doc = pymupdf.open(src)
    s.pg.show_pdf_page(pymupdf.Rect(s.P(px, py), s.P(px + pw, py + ph)), doc, 0)
    s.rect(px, py, px + pw, py + ph, w=THIN, col=(.6, .6, .6))

    # datum at the bottom-left of the artwork, X right, Y up
    dxp, dyp = px, py + ph
    s.line(dxp - 7, dyp, dxp + pw + 4, dyp, (0, 0, 0), THIN, CHAIN)
    s.line(dxp, dyp + 7, dxp, dyp - ph - 1, (0, 0, 0), THIN, CHAIN)
    s.circle(dxp, dyp, 2.1, w=MED)
    s.text(dxp - 9.5, dyp + 7.5, 'DATUM', 2.4, font='hebo')
    s.text(dxp - 9.5, dyp + 11, 'X = 0, Y = 0', 2.2, (.35, .35, .35))
    s.arrow(dxp + pw + 4, dyp, 1, 0); s.text(dxp + pw + 5.5, dyp - 1.6, 'X', 2.6, font='hebo')
    s.arrow(dxp, dyp - ph - 1, 0, -1); s.text(dxp + 1.8, dyp - ph - 2, 'Y', 2.6, font='hebo')

    # balloons on each body
    for i, (n, p) in enumerate(items):
        a, b, c, d = p.bounds
        bx = px + (a + c) / 2 - datum[0] * 0 - (W / 2 + (a + c) / 2) * 0
        bx = px + ((a + c) / 2 - (-W / 2)) * SC
        by = py + (H / 2 - (b + d) / 2) * SC
        off = -11 if n == 'DIAMOND' else (9 if n == 'BAR UNDER O' else 0)
        s.circle(bx, by + off, 3.0, w=MED, col=(0, 0, 0))
        s.pg.draw_circle(s.P(bx, by + off), 3.0 * MM, color=None, fill=(1, 1, 1))
        s.circle(bx, by + off, 3.0, w=MED)
        s.text(bx, by + off + 1.1, str(i + 1), 2.8, font='hebo', align=1)

    s.dim_h(px, px + pw, py + ph + 11, f'{W:.2f}', ext=py + ph, below=True)
    s.dim_v(py, py + ph, px - 13, f'{H:.2f}', ext=px)

    # ---- ordinate schedule
    bx, by = 196, 32
    s.text(bx, by - 5, 'ORDINATE SCHEDULE', 3.1, font='hebo')
    s.text(bx + 52, by - 5, 'X and Y to the lower-left corner of each body, '
           'from the datum', 2.2, (.35, .35, .35))
    cols = [(0, 'ITEM', 2.5), (11, 'BODY', 2.5), (44, 'X', 2.5), (62, 'Y', 2.5),
            (80, 'WIDTH', 2.5), (101, 'HEIGHT', 2.5), (124, 'CTR', 2.5),
            (136, 'CROWN', 2.5)]
    TW = 152
    s.rect(bx, by, bx + TW, by + 5.8, w=MED, fill=(.9, .9, .9))
    for dxx, t, _ in cols:
        s.text(bx + 2.5 + dxx, by + 4, t, 2.3, font='hebo')
    yy = by + 5.8
    for i, r in enumerate(rows):
        s.rect(bx, yy, bx + TW, yy + 5.4, w=THIN)
        for dxx, t in zip([q[0] for q in cols],
                          [str(i + 1), r['name'], f"{r['x']:.2f}", f"{r['y']:.2f}",
                           f"{r['w']:.2f}", f"{r['h']:.2f}", str(r['counters']),
                           f"{r['crown']:.2f}"]):
            s.text(bx + 2.5 + dxx, yy + 3.8, t, 2.3)
        yy += 5.4
    s.text(bx, yy + 4.5, 'CTR is the number of enclosed counters in the body '
           '(the diamond\'s facets, the bowl of a P).', 2.2, (.35, .35, .35))
    s.text(bx, yy + 8.3, 'CROWN is the full height that body reaches, base '
           'included; a body narrower than '
           f'{2*inset:.2f} mm cannot reach {base+height:.2f}.', 2.2, (.35, .35, .35))

    # ---- clearance schedule
    cy = yy + 20
    s.text(bx, cy - 5, 'CLEARANCE SCHEDULE', 3.1, font='hebo')
    s.text(bx + 54, cy - 5, 'every pair of bodies within 4 mm, closest first',
           2.2, (.35, .35, .35))
    s.rect(bx, cy, bx + TW, cy + 5.8, w=MED, fill=(.9, .9, .9))
    for dxx, t in ((0, 'FROM'), (11, ''), (56, 'TO'), (67, ''), (118, 'GAP')):
        if t:
            s.text(bx + 2.5 + dxx, cy + 4, t, 2.3, font='hebo')
    yy = cy + 5.8
    for q in gaps:
        s.rect(bx, yy, bx + TW, yy + 5.4, w=THIN)
        s.text(bx + 2.5, yy + 3.8, str(q['a']), 2.3)
        s.text(bx + 13.5, yy + 3.8, q['na'], 2.3)
        s.text(bx + 58.5, yy + 3.8, str(q['b']), 2.3)
        s.text(bx + 69.5, yy + 3.8, q['nb'], 2.3)
        s.text(bx + 120.5, yy + 3.8, f"{q['d']:.2f}", 2.3,
               font='hebo' if q is gaps[0] else 'helv')
        yy += 5.4
    s.text(bx, yy + 4.5, 'These are gaps in the artwork, not assembly '
           'tolerances. The tightest one sets what the tooling has to hold.',
           2.2, (.35, .35, .35))

    # ---- stroke schedule
    sy = yy + 20
    s.text(bx, sy - 5, 'STROKE SCHEDULE', 3.1, font='hebo')
    s.text(bx + 46, sy - 5, 'measured on the medial axis of each body, '
           'terminals excluded', 2.2, (.35, .35, .35))
    s.text(bx + 46, sy - 1.6, 'WIDEST is a pool where strokes meet, not a '
           'stroke; anything over '
           f'{2*inset:.2f} is at full height.', 2.2, (.35, .35, .35))
    s.rect(bx, sy, bx + TW, sy + 5.8, w=MED, fill=(.9, .9, .9))
    for dxx, t in ((0, 'ITEM'), (11, 'BODY'), (60, 'THINNEST'),
                   (92, 'WIDEST'), (124, 'AREA')):
        s.text(bx + 2.5 + dxx, sy + 4, t, 2.3, font='hebo')
    yy = sy + 5.8
    thinnest = min(r['thin'] for r in rows)
    for i, r in enumerate(rows):
        s.rect(bx, yy, bx + TW, yy + 5.4, w=THIN)
        hit = abs(r['thin'] - thinnest) < 5e-3
        for dxx, t, bold in ((0, str(i + 1), 0), (11, r['name'], 0),
                             (62, f"{r['thin']:.2f}", hit),
                             (94, f"{r['thick']:.2f}", 0),
                             (124, f"{r['area']:.1f}", 0)):
            s.text(bx + 2.5 + dxx, yy + 3.8, t, 2.3,
                   font='hebo' if bold else 'helv')
        yy += 5.4
    s.text(bx, yy + 4.5, 'AREA is the plan area of the body in mm2, counters '
           'deducted. Total '
           f"{sum(r['area'] for r in rows):.1f} mm2.", 2.2, (.35, .35, .35))
    detail_e(s, items, gaps, 30, 176, 155, 96)
    return


def detail_e(s, items, gaps, ex, ey, bw, bh, show_n=2):
    """The three tightest gaps, drawn where they are.

    A schedule says 0.79 mm; it does not say which edge of the C and
    which edge of the O, and that is the thing a toolmaker has to hold.
    Here the bodies are drawn at 7:1 and each gap is dimensioned between
    the two points that are actually closest."""
    show = gaps[:show_n]
    if not show:
        return
    ids = sorted({q['a'] for q in show} | {q['b'] for q in show})
    polys = [(i, items[i - 1][1]) for i in ids]
    xs = [p.bounds[0] for _, p in polys] + [p.bounds[2] for _, p in polys]
    ys = [p.bounds[1] for _, p in polys] + [p.bounds[3] for _, p in polys]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = min(bw / (x1 - x0), bh / (y1 - y0))
    ex += (bw - (x1 - x0) * scale) / 2
    s.text(ex, ey - 5, 'DETAIL E', 3.1, font='hebo')
    s.text(ex + 22, ey - 5, 'THE TIGHTEST GAPS', 2.6, (.35, .35, .35))
    s.text(ex + 62, ey - 5, f'SCALE {scale:.1f}:1', 2.3, (.35, .35, .35))
    s.text(ex, ey - 1, 'dimensioned between the two points that are '
           'actually closest, not between bounding boxes', 2.2, (.35, .35, .35))
    X = lambda x: ex + (x - x0) * scale
    Y = lambda y: ey + 6 + (y1 - y) * scale
    for i, p in polys:
        for ring in [p.exterior] + list(p.interiors):
            s.poly([(X(a), Y(b)) for a, b in ring.coords], w=MED, close=True)
        a, b, c, d = p.bounds
        s.circle(X((a + c) / 2), Y((b + d) / 2), 2.6, w=MED)
        s.text(X((a + c) / 2), Y((b + d) / 2) + 1.0, str(i), 2.4,
               font='hebo', align=1)
    for q in show:
        pa, pb = nearest_points(items[q['a'] - 1][1], items[q['b'] - 1][1])
        ax, ay, bx_, by_ = X(pa.x), Y(pa.y), X(pb.x), Y(pb.y)
        mx, my = (ax + bx_) / 2, (ay + by_) / 2
        dx, dy = bx_ - ax, by_ - ay
        n = math.hypot(dx, dy) or 1
        s.line(ax - dx / n * 7, ay - dy / n * 7,
               bx_ + dx / n * 7, by_ + dy / n * 7, (0, 0, 0), THIN, DASH)
        s.arrow(ax, ay, -dx, -dy, 1.5); s.arrow(bx_, by_, dx, dy, 1.5)
        lx, ly = mx - dy / n * 9, my + dx / n * 9
        s.line(mx, my, lx, ly, w=THIN)
        s.text(lx, ly - 1.2, f"{q['d']:.2f}", 2.6, align=1, font='hebo')


def title(s, W, H, total, thin, n, sheet, of, dwg='PACO-3D-02'):
    TX0, TY0, TX1, TY1 = 256, 247, 406, 283
    s.rect(TX0, TY0, TX1, TY1, w=THICK)
    for yy_ in (TY0 + 12, TY0 + 19, TY0 + 26):
        s.line(TX0, yy_, TX1, yy_, w=MED)
    s.line(TX0 + 96, TY0, TX0 + 96, TY1, w=MED)
    s.line(TX0 + 96, TY0 + 6, TX1, TY0 + 6, w=MED)
    s.text(TX0 + 3, TY0 + 8.5, 'PA & CO   LOGO, DOMED', 4.4, font='hebo')

    def cell(x, y, k, v, kw=2.0, vw=2.5):
        s.text(x, y, k, kw, (.4, .4, .4))
        s.text(x + 20, y, v, vw)
    cell(TX0 + 3, TY0 + 16.5, 'MATERIAL', 'per supplier')
    cell(TX0 + 3, TY0 + 23.5, 'FINISH', 'satin silver')
    cell(TX0 + 3, TY0 + 30.5, 'OVERALL', f'{W:.2f} x {H:.2f} x {total:.2f}')
    cell(TX0 + 56, TY0 + 16.5, 'UNITS', 'mm')
    cell(TX0 + 56, TY0 + 23.5, 'MIN STROKE', f'{thin:.2f}')
    cell(TX0 + 56, TY0 + 30.5, 'BODIES', str(n))
    s.text(TX0 + 99, TY0 + 4.3, 'THIRD ANGLE', 2.0, (.4, .4, .4))
    cell(TX0 + 99, TY0 + 10.5, 'DWG NO.', dwg, 2.0, 2.4)
    cell(TX0 + 99, TY0 + 16.5, 'SCALE', 'AS NOTED', 2.0, 2.4)
    cell(TX0 + 99, TY0 + 23.5, 'SHEET', f'{sheet} OF {of}', 2.0, 2.4)
    cell(TX0 + 99, TY0 + 30.5, 'REV', 'A', 2.0, 2.4)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-freebar.pdf')
    a.add_argument('--iso', required=True)
    a.add_argument('--inset', type=float, default=1.25)
    a.add_argument('--height', type=float, default=1.20)
    a.add_argument('--base', type=float, default=0.45)
    a.add_argument('--stl', default='paco-logo-freebar-dome1.20-base0.45.stl')
    a.add_argument('--out', default='assets/paco/paco-engineering-sheet.pdf')
    a.add_argument('--png')
    o = a.parse_args()

    g, W, H, rows, gaps, items, datum = measure(o.src, o.inset, o.height, o.base)
    print(f'{len(rows)} bodies, {len(gaps)} clearances under 4 mm, '
          f'tightest {min(q["d"] for q in gaps):.2f} mm')

    s1 = Sheet()
    total, thin, thick = sheet_one(s1, o.src, g, W, H, rows, gaps,
                                   o.inset, o.height, o.base, o.iso, o.stl)
    title(s1, W, H, total, thin, len(rows), 1, 2)
    s2 = Sheet()
    sheet_two(s2, o.src, W, H, rows, gaps, items, datum, o.inset, o.height, o.base)
    title(s2, W, H, total, thin, len(rows), 2, 2)
    s1.doc.insert_pdf(s2.doc)
    s1.doc.save(o.out)
    print(f'{o.out}: 2 x A3 landscape, part {total:.2f} mm thick, '
          f'stroke {thin:.2f} to {thick:.2f}')
    if o.png:
        for i in range(2):
            s1.doc[i].get_pixmap(matrix=pymupdf.Matrix(2.4, 2.4)).save(
                o.png.replace('.png', f'-{i+1}.png'))
        print('   previews', o.png.replace('.png', '-1/2.png'))
