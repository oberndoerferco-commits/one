#!/usr/bin/env python3
"""A3 production sheet for the TraxNYC button: face, section, back.

The face goes down at 1:1 from the same geometry the STL is built from,
so the sheet and the model cannot drift apart. The section is computed,
not drawn: the cap profile is evaluated along the cut, so the curve on
the paper is the curve in the file.
"""
import argparse
import math
import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft import GREY, MM, dim_h, dim_v, line, note, title, witness   # noqa: E402
from trax_button import (_cap_height, cap_radius, post_spots,          # noqa: E402
                         roll_profile)
from trax_crest import SRC, pieces, prepare                            # noqa: E402

INK = (0.18, 0.18, 0.18)
HAIR = (0.62, 0.62, 0.62)
CUT = (0.85, 0.12, 0.42)


def draw_plan(pg, g, cx, cy, k, col, fill=None, width=0.5):
    sh = pg.new_shape()
    for s in pieces(g):
        for ring in [s.exterior] + list(s.interiors):
            sh.draw_polyline([pymupdf.Point(cx + x * k, cy - y * k)
                              for x, y in ring.coords])
        sh.finish(color=col, fill=fill, even_odd=True, closePath=True, width=width)
    sh.commit()


def chain(pg, cx, cy, r):
    for dx, dy in ((1, 0), (0, 1)):
        line(pg, (cx - dx * r, cy - dy * r), (cx + dx * r, cy + dy * r),
             0.3, GREY, '[6 2 1.5 2] 0')


def cut_spans(geom, half):
    """Where the diagonal cut crosses `geom`, as signed distances."""
    from shapely.geometry import LineString
    d = half * 1.5
    cut = LineString([(-d / math.sqrt(2), -d / math.sqrt(2)),
                      (d / math.sqrt(2), d / math.sqrt(2))])
    hit = geom.intersection(cut)
    out = []
    for seg in (hit.geoms if hasattr(hit, 'geoms') else [hit]):
        if seg.is_empty or seg.length < 1e-6:
            continue
        xs = [math.copysign(math.hypot(x, y), x + y) for x, y in seg.coords]
        out.append((min(xs), max(xs)))
    return sorted(out)


def section(pg, x0, y0, k, a, blank, rel, rmax):
    """Section on the diagonal that carries the posts.

    Computed, not drawn: the cap profile is evaluated along the cut and
    the relief is taken from where the cut actually crosses it, so the
    curve on the paper is the curve in the model rather than a sketch of
    it.
    """
    def z(r):
        return a.rim + _cap_height(min(abs(r), rmax), rmax, a.crown)

    def P(r, zz):
        return (x0 + r * k, y0 - zz * k)

    (lo, hi), = cut_spans(blank, a.width)
    n = 260
    face = [P(lo + (hi - lo) * i / n, z(lo + (hi - lo) * i / n)) for i in range(n + 1)]
    pg.draw_polyline([pymupdf.Point(*q) for q in face], color=INK, width=0.6)
    line(pg, P(lo, 0), P(hi, 0), 0.6, INK)
    line(pg, P(lo, 0), P(lo, z(lo)), 0.6, INK)
    line(pg, P(hi, 0), P(hi, z(hi)), 0.6, INK)

    prof = roll_profile(a.relief, a.roll, 8)
    for s0, s1 in cut_spans(rel, a.width):
        pts = []
        for d, h in reversed(prof):                 # up the near flank
            pts.append(P(s0 + d, z(s0 + d) + h))
        m = max(12, int((s1 - s0) * 6))
        for i in range(m + 1):                      # across the plateau
            r = s0 + a.roll + (s1 - a.roll - (s0 + a.roll)) * i / m
            pts.append(P(r, z(r) + a.relief))
        for d, h in prof:                           # down the far flank
            pts.append(P(s1 - d, z(s1 - d) + h))
        pg.draw_polyline([pymupdf.Point(*q) for q in pts], color=INK, width=0.6)

    for x, y in post_spots(a.posts, a.post_r):
        r = math.copysign(math.hypot(x, y), x + y)
        w, L, c = a.post_dia / 2, a.post_len, a.chamfer
        pg.draw_polyline([pymupdf.Point(*P(*q)) for q in
                          [(r - w, 0), (r - w, -L + c), (r - w + c, -L),
                           (r + w - c, -L), (r + w, -L + c), (r + w, 0)]],
                         color=INK, width=0.6)
    return lo, hi


def sheet(doc, a, blank, rel, rmax):
    pg = doc.new_page(width=1191, height=842)          # A3 landscape
    k = MM
    title(pg, 26 * MM, 20 * MM, 'TraxNYC crest - domed button, riveted',
          f'{a.width:g} mm across - face at 1:1 - all dimensions mm')

    # ---- face, 1:1 ------------------------------------------------------
    cx, cy = 92 * MM, 112 * MM
    pg.insert_text(pymupdf.Point(cx - a.width / 2 * k, cy - (a.width / 2 + 7) * k),
                   'FACE  1:1   relief shaded', fontname='Helvetica',
                   fontsize=7, color=GREY)
    draw_plan(pg, blank, cx, cy, k, INK, fill=(0.93, 0.93, 0.94), width=0.6)
    draw_plan(pg, rel, cx, cy, k, INK, fill=(0.62, 0.64, 0.66), width=0.35)
    chain(pg, cx, cy, (a.width / 2 + 5) * k)
    dim_h(pg, cx - a.width / 2 * k, cx + a.width / 2 * k,
          cy + (a.width / 2 + 9) * k, f'{a.width:g}')
    dim_v(pg, cy - a.width / 2 * k, cy + a.width / 2 * k,
          cx - (a.width / 2 + 9) * k, f'{a.width:g}', anchor='left')
    d = (a.width / 2 + 6) / math.sqrt(2)
    line(pg, (cx - d * k, cy + d * k), (cx + d * k, cy - d * k), 0.4, CUT,
         '[6 2 1.5 2] 0')
    for sgn, lab in ((-1, 'A'), (1, 'A')):
        pg.insert_text(pymupdf.Point(cx + sgn * (d + 1.5) * k,
                                     cy - sgn * (d - 1.5) * k), lab,
                       fontname='Helvetica-Bold', fontsize=8, color=CUT)

    # ---- back, with the posts ------------------------------------------
    bx, by = 232 * MM, 112 * MM
    pg.insert_text(pymupdf.Point(bx - a.width / 2 * k, by - (a.width / 2 + 7) * k),
                   'BACK  1:1   flat; post centres are the drilling pattern',
                   fontname='Helvetica', fontsize=7, color=GREY)
    draw_plan(pg, blank, bx, by, k, INK, fill=(0.96, 0.96, 0.97), width=0.6)
    chain(pg, bx, by, (a.width / 2 + 5) * k)
    spots = post_spots(a.posts, a.post_r)
    for x, y in spots:
        px, py = bx + x * k, by - y * k
        pg.draw_circle(pymupdf.Point(px, py), a.post_dia / 2 * k,
                       color=CUT, fill=None, width=0.6)
        chain(pg, px, py, 4 * MM)
    (x0, y0), (x1, y1) = spots[0], spots[1]
    witness(pg, (bx + x0 * k, by - y0 * k), (bx + x0 * k, by + (a.width / 2 + 6) * k))
    witness(pg, (bx + x1 * k, by - y1 * k), (bx + x1 * k, by + (a.width / 2 + 6) * k))
    dim_h(pg, bx + x1 * k, bx + x0 * k, by + (a.width / 2 + 9) * k,
          f'{abs(x0 - x1):.2f}')
    dim_v(pg, by - y0 * k, by - y1 * k, bx + (a.width / 2 + 9) * k,
          f'{abs(y0 - y1):.2f}', anchor='right')
    pg.insert_text(pymupdf.Point(bx + (a.width / 2 + 2) * k, by - (a.width / 2) * k),
                   f'{a.posts} x  {a.post_dia:g} dia post', fontname='Helvetica-Bold',
                   fontsize=6.5, color=CUT)

    # ---- section --------------------------------------------------------
    sx, sy = cx, 196 * MM
    pg.insert_text(pymupdf.Point(sx - a.width / 2 * k, sy - 19 * k),
                   'SECTION A-A  1:1   on the diagonal through both posts',
                   fontname='Helvetica', fontsize=7, color=GREY)
    lo, hi = section(pg, sx, sy, k, a, blank, rel, rmax)
    total = a.rim + a.crown + a.relief
    dim_v(pg, sy, sy - (a.rim + a.crown) * k, sx + (hi + 6) * k,
          f'{a.rim + a.crown:.2f} to the face', anchor='right')
    dim_v(pg, sy, sy - total * k, sx + (hi + 24) * k,
          f'{total:.2f} overall', anchor='right')
    dim_v(pg, sy, sy + a.post_len * k, sx + (lo - 6) * k,
          f'{a.post_len:g}', anchor='left')
    line(pg, (sx + (lo - 3) * k, sy), (sx + (hi + 3) * k, sy),
         0.3, GREY, '[6 2 1.5 2] 0')

    # ---- notes ----------------------------------------------------------
    rs = cap_radius(rmax, a.crown)
    note(pg, 232 * MM, 170 * MM, [
        'One piece. Cast or struck, then polished.',
        f'Face is a spherical cap, R {rs:.0f}, rising {a.crown:.2f} at the centre '
        f'over a {a.rim:.2f} edge at the star tips',
        f'and {a.rim + _cap_height(a.width / 2, rmax, a.crown):.2f} at the cardinals. '
        'The blank is not round, so the edge is not one thickness.',
        '',
        f'Relief {a.relief:.2f} above the face, top edge rolled R {a.roll:.2f}. '
        'It follows the cap, so the band',
        'stands the same height above the face at the rim as at the centre.',
        '',
        f'Tooling: nothing in the recess is narrower than {a.cutter:.2f} and no '
        f'ridge is thinner than {a.fill:.2f}.',
        'The drawing was opened with a disc of each size before the model was '
        'built, which is why the',
        'star points carry a small fillet and the eye reads as two corners and '
        'a dot rather than an iris.',
        '',
        f'{a.posts} posts, {a.post_dia:g} dia x {a.post_len:g} long, '
        f'{a.chamfer:g} break on the free end, on the diagonal at r {a.post_r:g}.',
        f'Drill {a.post_dia + 0.2:.1f} through the lid and rivet over, or supply '
        'with the posts plain for gluing.',
        '',
        'Eagle head is an island on the face and is not joined to the band - the '
        'blank under it carries it.',
    ], lead=4.4 * MM)
    return pg


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default=SRC)
    a.add_argument('--width', type=float, default=50.0)
    a.add_argument('--cutter', type=float, default=0.70)
    a.add_argument('--fill', type=float, default=0.50)
    a.add_argument('--rim', type=float, default=0.90)
    a.add_argument('--crown', type=float, default=2.00)
    a.add_argument('--relief', type=float, default=0.85)
    a.add_argument('--roll', type=float, default=0.25)
    a.add_argument('--posts', type=int, default=2)
    a.add_argument('--post-dia', type=float, default=2.5)
    a.add_argument('--post-len', type=float, default=4.0)
    a.add_argument('--post-r', type=float, default=14.0)
    a.add_argument('--chamfer', type=float, default=0.4)
    a.add_argument('--out', required=True)
    o = a.parse_args()
    blank, rel, rep = prepare(o.src, o.width, o.cutter, o.fill)
    rmax = max(math.hypot(*p) for p in blank.exterior.coords)
    doc = pymupdf.open()
    sheet(doc, o, blank, rel, rmax)
    doc.save(o.out, deflate=True)
    print(f'{o.out}: 1 sheet, A3')
