#!/usr/bin/env python3
"""Leather cutting die for the OM mark, with a backing layer under it.

Two things a steel rule cannot do: cut a notch narrower than it can be
bent, and leave a sliver of leather thin enough to tear off the die. So
the outline is closed at the minimum first, which fills the narrow
notches, then anything still thinner than the minimum is brought up to it,
then counters too small to cut are dropped.

The mark's own proportions set the smallest patch worth cutting: at 100 mm
wide the thinnest part of the blackletter measures 1.86 mm, and that
scales, so 2.00 mm arrives at about 108 mm. Rather than fatten the letters
to hit a minimum at a smaller size, which thickens the hairlines of a
blackletter and stops it looking like one, the die is sized to the mark.

The backing is the same outline offset outward. Where that offset is more
than half the gap between the O and the M, the two merge into one piece,
which is what holds a two-part mark together.
"""
import argparse, os, pathlib, sys
import numpy as np, pymupdf
from PIL import Image
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from skimage.morphology import medial_axis
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

PP = 14.0
MM = 72.0 / 25.4


def disc(r):
    n = int(np.ceil(r)); y, x = np.mgrid[-n:n+1, -n:n+1]
    return (x*x + y*y) <= r*r


def trace(src):
    d = pymupdf.open(src); p = d[0]
    k = PP*25.4/72.0
    pm = p.get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    a = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples))
    return a < 128


def to_poly(mask, ppmm=PP, tol=0.8):
    rs = []
    pad = np.pad(mask, 2, constant_values=False)
    for c in find_contours(pad.astype(float), 0.5):
        c = approximate_polygon(c, tolerance=tol)
        if len(c) < 4:
            continue
        q = Polygon([((x-2)/ppmm, (y-2)/ppmm) for y, x in c]).buffer(0)
        if q.area > 0.2:
            rs.append(q)
    rs.sort(key=lambda q: -q.area)
    out = []
    for i, r in enumerate(rs):
        depth = sum(1 for j, o in enumerate(rs) if j != i and o.contains(r))
        if depth % 2:
            continue
        holes = [o for j, o in enumerate(rs)
                 if j != i and r.contains(o)
                 and sum(1 for q in rs if q is not o and q.contains(o)) == depth+1]
        out.append(Polygon(r.exterior.coords, [h.exterior.coords for h in holes]))
    return unary_union(out)


def thinnest(geom, ppmm=60):
    """p5 of the stroke width, which is where a die would tear."""
    x0, y0, x1, y1 = geom.bounds
    W = int((x1-x0+4)*ppmm); H = int((y1-y0+4)*ppmm)
    doc = pymupdf.open(); pg = doc.new_page(width=W/ppmm*MM, height=H/ppmm*MM)
    sh = pg.new_shape()
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        for ring in [g.exterior]+list(g.interiors):
            pts = [pymupdf.Point((x-x0+2)*MM, (y-y0+2)*MM) for x, y in ring.coords]
            if len(pts) > 2:
                sh.draw_polyline(pts)
    sh.finish(color=None, fill=(0, 0, 0), even_odd=True, closePath=True)
    sh.commit()
    k = ppmm*25.4/72.0
    pm = doc[0].get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    m = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples)) < 128
    sk, dist = medial_axis(m, return_distance=True)
    w = 2*dist[sk]/ppmm
    return float(np.percentile(w[w > 0.05], 5)), m, ppmm, (x0-2, y0-2)


def gap_between(geom):
    """Smallest distance between separate pieces. geom.geoms hands back a new
    object each time, so pieces have to be compared by index or every piece
    is found to be zero away from itself."""
    gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    if len(gs) < 2:
        return 0.0
    return min(gs[i].distance(gs[j])
               for i in range(len(gs)) for j in range(i+1, len(gs)))


def fatten(geom, minimum, ppmm=60):
    """Bring anything under the minimum up to it, leave the rest alone."""
    _, m, _, origin = thinnest(geom, ppmm)
    r = minimum/2*ppmm
    sk, dist = medial_axis(m, return_distance=True)
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - sk
    ends = sk & (nb <= 1)
    far = ndimage.distance_transform_edt(~ends) > r*1.1
    thin = sk & (dist < r) & far
    if not thin.any():
        return geom, 0
    # dilation by a disc of radius r, done as a distance transform. The
    # structuring element would be 2r+1 square - at a 4 mm minimum and
    # 60 px/mm that is 241 x 241 over a 19 megapixel image, which runs
    # the machine out of memory. The distance transform is linear.
    grown = m | (ndimage.distance_transform_edt(~thin) <= r)
    g = to_poly(grown, ppmm, tol=max(0.6, 0.012*ppmm))
    return affinity.translate(g, origin[0], origin[1]), int(thin.sum())


def write_vec(layers, out, pad=6.0):
    xs = [l[1].bounds for l in layers]
    x0 = min(b[0] for b in xs); y0 = min(b[1] for b in xs)
    x1 = max(b[2] for b in xs); y1 = max(b[3] for b in xs)
    W, H = (x1-x0)+2*pad, (y1-y0)+2*pad
    doc = pymupdf.open(); pg = doc.new_page(width=W*MM, height=H*MM)
    for (name, geom, col) in layers:
        sh = pg.new_shape()
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            for ring in [g.exterior]+list(g.interiors):
                pts = [pymupdf.Point((x-x0+pad)*MM, (y-y0+pad)*MM) for x, y in ring.coords]
                if len(pts) > 2:
                    sh.draw_polyline(pts + [pts[0]])
        sh.finish(color=col, fill=None, width=0.5, closePath=True)
        sh.commit()
    doc.save(out)
    return W, H


def write_svg(layers, out, pad=6.0):
    xs = [l[1].bounds for l in layers]
    x0 = min(b[0] for b in xs); y0 = min(b[1] for b in xs)
    x1 = max(b[2] for b in xs); y1 = max(b[3] for b in xs)
    W, H = (x1-x0)+2*pad, (y1-y0)+2*pad
    out_s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.3f}mm" '
             f'height="{H:.3f}mm" viewBox="0 0 {W:.3f} {H:.3f}">']
    for name, geom, col in layers:
        c = '#%02x%02x%02x' % tuple(int(v*255) for v in col)
        out_s.append(f'<g id="{name}" fill="none" stroke="{c}" stroke-width="0.25">')
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            for ring in [g.exterior]+list(g.interiors):
                d = ' '.join(f'{"M" if i == 0 else "L"}{x-x0+pad:.3f},{y-y0+pad:.3f}'
                             for i, (x, y) in enumerate(ring.coords))
                out_s.append(f'<path d="{d} Z"/>')
        out_s.append('</g>')
    out_s.append('</svg>')
    pathlib.Path(out).write_text('\n'.join(out_s))


def write_dxf(layers, out):
    """R12 DXF with one closed POLYLINE per ring, which every die shop reads."""
    e = ['0', 'SECTION', '2', 'ENTITIES']
    for name, geom, _ in layers:
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            for ring in [g.exterior]+list(g.interiors):
                e += ['0', 'POLYLINE', '8', name, '66', '1', '70', '1',
                      '10', '0.0', '20', '0.0', '30', '0.0']
                for x, y in list(ring.coords)[:-1]:
                    e += ['0', 'VERTEX', '8', name,
                          '10', f'{x:.4f}', '20', f'{-y:.4f}', '30', '0.0']
                e += ['0', 'SEQEND', '8', name]
    e += ['0', 'ENDSEC', '0', 'EOF']
    pathlib.Path(out).write_text('\n'.join(e) + '\n')


def die_sheet(top, under, o, stats, out, got=None, gap=None,
              nu=1, clear=0.0):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paco_drawing import Sheet, THIN, MED, THICK, CHAIN, DASH
    s = Sheet()
    s.rect(10, 10, 410, 287, w=0.7)
    s.rect(14, 14, 406, 283, w=0.25)
    ux0, uy0, ux1, uy1 = under.bounds
    # the view has to fit between the left margin and the key block, so the
    # scale follows the part rather than the other way round
    ox, oy = 44, 40
    SC = min(1.6, 206.0/(ux1-ux0), 196.0/(uy1-uy0))
    SC = round(SC, 2)
    sc_txt = f'{SC:g}:1' if SC >= 1 else f'1:{1/SC:.2f}'
    def draw(geom, col, w):
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            for ring in [g.exterior]+list(g.interiors):
                s.poly([(ox+(x-ux0)*SC, oy+(y-uy0)*SC) for x, y in ring.coords],
                       col=col, w=w, close=True)
    s.text(ox, oy-7, 'CUTTING DIE', 3.4, font='hebo')
    s.text(ox+34, oy-7, f'SCALE {sc_txt}', 2.3, (.35, .35, .35))
    draw(under, (0, .45, .9), THICK)
    draw(top, (.85, 0, .3), THICK)
    W, H = (ux1-ux0)*SC, (uy1-uy0)*SC
    s.dim_h(ox, ox+W, oy+H+12, f'{ux1-ux0:.2f}', ext=oy+H, below=True)
    s.dim_v(oy, oy+H, ox-12, f'{uy1-uy0:.2f}', ext=ox)
    tx0, ty0, tx1, ty1 = top.bounds
    s.dim_h(ox+(tx0-ux0)*SC, ox+(tx1-ux0)*SC, oy-13, f'{tx1-tx0:.2f}',
            ext=oy+(ty0-uy0)*SC)
    # key
    kx, ky = 262, 40
    s.text(kx, ky-7, 'LAYERS', 3.4, font='hebo')
    for i, (lab, col, note) in enumerate([
            ('TOP', (.85, 0, .3), 'the mark itself, two pieces'),
            ('UNDER', (0, .45, .9), f'backing, +{o.offset:.1f} mm all round, '
             + ('one per letter' if o.separate else 'one piece'))]):
        s.line(kx, ky+i*9, kx+10, ky+i*9, col=col, w=THICK)
        s.text(kx+14, ky+i*9+1, lab, 2.8, font='hebo')
        s.text(kx+36, ky+i*9+1, note, 2.4, (.3, .3, .3))
    ty = ky+26
    s.text(kx, ty, 'MEASURED', 3.4, font='hebo'); ty += 7
    for k_, v_ in stats:
        s.text(kx, ty, k_, 2.4, (.35, .35, .35)); s.text(kx+62, ty, v_, 2.5); ty += 5.6
    ty += 6
    s.text(kx, ty, 'NOTES', 3.4, font='hebo'); ty += 6.5
    from paco_drawing import wrap
    for i, t in enumerate([
        'All dimensions in millimetres. Cut lines are the finished edge.',
        f'TOP cuts as two pieces, the O and the M. They are {gap:.2f} mm '
        'apart and must not be joined.',
        (f'UNDER is {nu} pieces, one per letter, {clear:.2f} mm apart. They '
         'must not be joined either.') if o.separate else
        ('UNDER is one piece. The two lobes merge because the offset is more '
         'than half that gap.'),
        f'Smallest feature on TOP is {got:.2f} mm. Nothing may be scaled '
        'down without checking it again: the figure scales with the mark.',
        f'Notches narrower than {o.min:.2f} mm have been closed so a rule '
        'can be bent to them.',
        'Counters too small to cut have been dropped. Those that remain are '
        'cut through.',
    ]):
        s.text(kx, ty, str(i+1), 2.4, font='hebo')
        for j, ln in enumerate(wrap(t, 46)):
            s.text(kx+4.5, ty+j*3.8, ln, 2.4)
        ty += 3.8*len(wrap(t, 46)) + 1.6
    TX0, TY0, TX1, TY1 = 256, 247, 406, 283
    s.rect(TX0, TY0, TX1, TY1, w=THICK)
    for yy in (TY0+12, TY0+19, TY0+26):
        s.line(TX0, yy, TX1, yy, w=MED)
    s.line(TX0+96, TY0, TX0+96, TY1, w=MED)
    s.text(TX0+3, TY0+8.5, 'OM  -  LEATHER CUTTING DIE', 4.0, font='hebo')
    def cell(x, y, k_, v_):
        s.text(x, y, k_, 2.0, (.4, .4, .4)); s.text(x+22, y, v_, 2.5)
    cell(TX0+3, TY0+16.5, 'MATERIAL', 'leather')
    cell(TX0+3, TY0+23.5, 'UNITS', 'mm')
    cell(TX0+3, TY0+30.5, 'TOP', f'{tx1-tx0:.2f} x {ty1-ty0:.2f}')
    cell(TX0+99, TY0+10.5, 'DWG NO.', 'OM-DIE-01')
    cell(TX0+99, TY0+17.5, 'SCALE', sc_txt)
    cell(TX0+99, TY0+24.5, 'UNDER', f'{ux1-ux0:.2f} x {uy1-uy0:.2f}')
    cell(TX0+99, TY0+31.5, 'SHEET', '1 OF 1')
    s.doc.save(out)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='/root/.claude/uploads/9a731093-06fb-50bc-9d28-75940e80fb3f/13c79434-tshirt_design-22.pdf')
    a.add_argument('--width', type=float, default=108.0,
                   help='width of the letters, mm')
    a.add_argument('--overall', type=float, default=None,
                   help='width of the FINISHED patch instead: the letters are '
                        'sized so that they plus the backing come to this')
    a.add_argument('--fatten', action='store_true',
                   help='thicken the thin parts until they reach --min, '
                        'instead of sizing the mark up until they do')
    a.add_argument('--separate', action='store_true',
                   help='keep the backing as one piece per letter; never let '
                        'the O and the M join')
    a.add_argument('--min', type=float, default=2.0, help='smallest feature a die can hold')
    a.add_argument('--offset', type=float, default=4.5, help='backing layer, mm bigger all round')
    a.add_argument('--outdir', default='assets/om-die')
    o = a.parse_args()
    os.makedirs(o.outdir, exist_ok=True)

    want = (o.overall - 2*o.offset) if o.overall else o.width
    if o.overall:
        print(f'finished patch {o.overall:.1f} mm wide, backing {o.offset:.1f} mm '
              f'all round, so the letters get {want:.2f} mm')

    def fit(q, w):
        b = q.bounds
        k = w/(b[2]-b[0])
        q = affinity.scale(q, k, k, origin=(b[0], b[1]))
        b = q.bounds
        return affinity.translate(q, -b[0], -b[1])

    r = o.min/2

    def close(q):
        # closing fills notches a rule cannot be bent into and takes nothing
        # off the letterforms; a counter the die cannot cut is not a counter
        t = q.buffer(r, join_style=1, quad_segs=16).buffer(-r, join_style=1,
                                                           quad_segs=16)
        return unary_union([
            Polygon(p_.exterior.coords,
                    [h.coords for h in p_.interiors
                     if Polygon(h).buffer(-r).area > 0])
            for p_ in (t.geoms if hasattr(t, 'geoms') else [t])])

    g = fit(to_poly(trace(o.src)), want)
    raw_min, _, _, _ = thinnest(g, 40)
    print(f'as supplied, scaled to {want:.2f} mm wide: thinnest {raw_min:.2f} mm, '
          f'{len(list(g.geoms))} pieces')

    top = close(g)
    got, _, _, _ = thinnest(top, 40)
    if o.fatten:
        # Thicken only what is under the minimum, along the medial axis. A
        # uniform swell reaches the same figure but costs far more: at 80 mm
        # it closed the gap between the O and the M from 6.50 to 3.88 and
        # took the counters from ten down to two. The letterform survives
        # being thickened where it is thin; it does not survive being
        # thickened everywhere.
        for i in range(5):
            if got >= o.min - 0.02:
                break
            top, npx = fatten(top, o.min, ppmm=40)
            top = close(fit(top, want))
            got, _, _, _ = thinnest(top, 40)
            print(f'   fattened round {i+1}: thinnest {got:.2f} mm')
    gap = gap_between(top)
    print(f'after closing at {o.min:.2f}: thinnest {got:.2f} mm, '
          f'{len(list(top.geoms)) if hasattr(top,"geoms") else 1} pieces, '
          f'{sum(len(p_.interiors) for p_ in (top.geoms if hasattr(top,"geoms") else [top]))} counters, '
          f'gap between pieces {gap:.2f} mm')
    if got < o.min - 0.02:
        need = o.width * o.min / got
        print(f'   NOTE: under the {o.min:.2f} minimum. This mark holds it at '
              f'{need:.0f} mm wide.')

    pieces = list(top.geoms) if hasattr(top, 'geoms') else [top]
    if o.separate:
        # one backing per letter, kept apart on purpose. Offsetting the two
        # together and unioning would weld them the moment the offset passed
        # half the gap, which is exactly what must not happen here.
        outs = [Polygon(
                    (q.exterior.coords if not hasattr(q, 'geoms') else
                     max(q.geoms, key=lambda z: z.area).exterior.coords))
                for q in (p_.buffer(o.offset, join_style=1, quad_segs=24)
                          for p_ in pieces)]
        clear = min((outs[i].distance(outs[j])
                     for i in range(len(outs)) for j in range(i+1, len(outs))),
                    default=0.0)
        hit = any(outs[i].intersects(outs[j])
                  for i in range(len(outs)) for j in range(i+1, len(outs)))
        under = unary_union(outs) if not hit else None
        nu = len(outs)
        print(f'backing at +{o.offset:.1f} mm, one per letter: {nu} piece(s), '
              + (f'{clear:.2f} mm between them' if not hit else
                 'THEY OVERLAP - the offset is more than half the gap'))
        if hit:
            raise SystemExit(f'offset {o.offset:.2f} mm overlaps; the gap is '
                             f'{gap:.2f} mm, so keep it under {gap/2:.2f} mm')
        under = unary_union(outs)
    else:
        under = top.buffer(o.offset, join_style=1, quad_segs=24)
        under = unary_union([Polygon(p_.exterior.coords)
                             for p_ in (under.geoms if hasattr(under, 'geoms') else [under])])
        nu = len(list(under.geoms)) if hasattr(under, 'geoms') else 1
        clear = gap_between(under)
        print(f'backing at +{o.offset:.1f} mm: {nu} piece(s)'
              + ('  (the O and M merge into one)' if nu == 1
                 else f'  (they merge from +{gap/2:.2f} mm)'))

    W, H = write_vec([('UNDER', under, (0, 0.45, 0.9)), ('TOP', top, (0.85, 0, 0.3))],
                     os.path.join(o.outdir, 'om-die-both.pdf'))
    write_vec([('TOP', top, (0.85, 0, 0.3))], os.path.join(o.outdir, 'om-die-top.pdf'))
    write_vec([('UNDER', under, (0, 0.45, 0.9))], os.path.join(o.outdir, 'om-die-under.pdf'))
    L = [('UNDER', under, (0, 0.45, 0.9)), ('TOP', top, (0.85, 0, 0.3))]
    write_svg(L, os.path.join(o.outdir, 'om-die-both.svg'))
    write_dxf(L, os.path.join(o.outdir, 'om-die-both.dxf'))
    tx0, ty0, tx1, ty1 = top.bounds
    ux0, uy0, ux1, uy1 = under.bounds
    die_sheet(top, under, o, [
        ('Top, overall', f'{tx1-tx0:.2f} x {ty1-ty0:.2f} mm'),
        ('Backing, overall', f'{ux1-ux0:.2f} x {uy1-uy0:.2f} mm'),
        ('Border all round', f'{o.offset:.2f} mm'),
        ('Smallest feature', f'{got:.2f} mm'),
        ('Gap, O to M', f'{gap:.2f} mm'),
        ('Backing to backing', f'{clear:.2f} mm'),
        ('Pieces', f'top {len(pieces)}, backing {nu}'),
    ], os.path.join(o.outdir, 'om-die-drawing.pdf'), got, gap, nu, clear)
    print(f'wrote {o.outdir}/: top.pdf under.pdf both.pdf both.svg both.dxf drawing.pdf '
          f'({W:.1f} x {H:.1f} mm)')
