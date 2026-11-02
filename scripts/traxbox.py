#!/usr/bin/env python3
"""Production drawings and stamping artwork for the TRAXNYC trunk box.

A rigid board carcass wrapped in black leatherette and tooled in the trunk
manner: a quarter-round cap worked into each corner with a domed stud in
it, a blind-debossed line running round every face inside the caps, and
the mark in gold foil on the lid.

Two things are drawn rather than described, because they are what the
tooling has to be cut to.

The debossed line is not a rounded rectangle. It runs straight, inset from
each edge, and turns on an arc struck from the corner itself -- the same
centre as the cap, so the two stay concentric. Where they meet follows
from that and is not a free choice: an arc of radius R crosses a line inset
b at sqrt(R^2 - b^2) along the edge, which is what fixes the straight runs.

And the deboss is laid out over the whole face and then cut by the lid.
The wrap is tooled flat before it goes on, so the line crosses the opening
and carries on; drawing lid and base as separate panels would put a seam
in the middle of a line that has none.
"""
import argparse, math, os, sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft import MM, GREY, line, dim_h, dim_v, witness, note, title  # noqa: E402

LEATHER = (0.13, 0.12, 0.12)
TOOL = (0.42, 0.40, 0.39)
GOLD = (0.76, 0.60, 0.29)
CUT = (0.90, 0.10, 0.45)
FOLD = (0.10, 0.55, 0.85)
INK = (0.08, 0.08, 0.08)

# corner, as (sign x, sign y, arc runs from, arc runs to) with 1 = the angle
# whose cosine is run/R and 2 = the angle whose cosine is b/R
CORNERS = [(0, 0, 1, 1, 2, 1), (1, 0, -1, 1, 1, 2),
           (1, 1, -1, -1, 2, 1), (0, 1, 1, -1, 1, 2)]


class Box:
    def __init__(self, L, W, H, lid, board, wrap, b, R, Rl, stud, stud_in,
                 medal, mark_w, mark_h, gap):
        self.L, self.W, self.H, self.lid = L, W, H, lid
        self.board, self.wrap = board, wrap
        self.b, self.R, self.Rl = b, R, Rl
        self.stud, self.stud_in = stud, stud_in
        self.medal, self.mark_w, self.mark_h, self.gap = medal, mark_w, mark_h, gap
        self.base = H - lid
        t = board + wrap
        self.in_L, self.in_W, self.in_H = L - 2 * t, W - 2 * t, H - 2 * t

    def run(self, b=None, R=None):
        """How far along the edge the debossed line meets its corner arc."""
        b = self.b if b is None else b
        R = self.Rl if R is None else R
        return math.sqrt(R * R - b * b)


def _arc(cx, cy, sx, sy, R, a_from, a_to, n=26):
    return [(cx + sx * R * math.cos(a_from + (a_to - a_from) * i / n),
             cy + sy * R * math.sin(a_from + (a_to - a_from) * i / n))
            for i in range(n + 1)]


def deboss(pg, x, y, w, h, b, R, col=TOOL, width=0.7):
    """The tooled line, in page units: straight runs plus corner arcs."""
    if R <= b:
        return
    run = math.sqrt(R * R - b * b)
    a1, a2 = math.asin(b / R), math.acos(b / R)
    pts = []
    for fx, fy, sx, sy, f, t in CORNERS:
        cx, cy = (w if fx else 0), (h if fy else 0)
        pts += _arc(cx, cy, sx, sy, R, a1 if f == 1 else a2, a1 if t == 1 else a2)
    pts.append(pts[0])
    pg.draw_polyline([pymupdf.Point(x + px, y + py) for px, py in pts],
                     color=col, width=width)


def caps(pg, x, y, w, h, R, col=TOOL, width=0.7):
    """The quarter-round cap at each corner."""
    for fx, fy, sx, sy, _, _ in CORNERS:
        cx, cy = (w if fx else 0), (h if fy else 0)
        pts = _arc(cx, cy, sx, sy, R, 0.0, math.pi / 2)
        pg.draw_polyline([pymupdf.Point(x + px, y + py) for px, py in pts],
                         color=col, width=width)


def studs(pg, x, y, w, h, inset, dia, col=TOOL, fill=None, width=0.6):
    for fx, fy, sx, sy, _, _ in CORNERS:
        cx, cy = (w if fx else 0), (h if fy else 0)
        pg.draw_circle(pymupdf.Point(x + cx + sx * inset, y + cy + sy * inset),
                       dia / 2, color=col, fill=fill, width=width)


def face(pg, x, y, fw, fh, c, k, fill=LEATHER, tool=TOOL):
    pg.draw_rect(pymupdf.Rect(x, y, x + fw * k, y + fh * k), color=None, fill=fill)
    deboss(pg, x, y, fw * k, fh * k, c.b * k, c.Rl * k, tool)
    caps(pg, x, y, fw * k, fh * k, c.R * k, tool)
    studs(pg, x, y, fw * k, fh * k, c.stud_in * k, c.stud * k, tool)


def mark(pg, cx, cy, c, k, col=GOLD, solid=True):
    """The medallion over the wordmark, centred as a block."""
    mh, mw = c.medal * k, c.mark_w * k
    tot = mh + c.gap * k + c.mark_h * k
    top = cy - tot / 2
    a = pymupdf.Rect(cx - mh / 2, top, cx + mh / 2, top + mh)
    b = pymupdf.Rect(cx - mw / 2, top + mh + c.gap * k, cx + mw / 2, top + tot)
    for r in (a, b):
        pg.draw_rect(r, color=col, fill=col if solid else None, width=0.7,
                     dashes=None if solid else '[2.5 2] 0')
    return a, b


# ----------------------------------------------------------------- sheets

def sheet_ga(doc, c, s):
    k = s * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box · general arrangement',
          f'{c.L:g} x {c.W:g} x {c.H:g} mm closed.  drawing at 1:{1/s:g}')
    x0, y0 = 24 * MM, 46 * MM
    face(pg, x0, y0, c.L, c.W, c, k)
    mark(pg, x0 + c.L * k / 2, y0 + c.W * k / 2, c, k)
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM), 'lid, from above',
                   fontname='Helvetica', fontsize=7)
    for xv in (0, c.L):
        witness(pg, (x0 + xv * k, y0 + c.W * k), (x0 + xv * k, y0 + c.W * k + 13 * MM))
    dim_h(pg, x0, x0 + c.L * k, y0 + c.W * k + 8 * MM, f'{c.L:g}')
    for yv in (0, c.W):
        witness(pg, (x0, y0 + yv * k), (x0 - 13 * MM, y0 + yv * k))
    dim_v(pg, y0, y0 + c.W * k, x0 - 8 * MM, f'{c.W:g}')

    # long side, with the lid line
    y1 = y0 + c.W * k + 26 * MM
    face(pg, x0, y1, c.L, c.H, c, k)
    line(pg, (x0, y1 + c.lid * k), (x0 + c.L * k, y1 + c.lid * k), 0.8, (1, 1, 1))
    pg.insert_text(pymupdf.Point(x0, y1 - 4 * MM), 'long side · the lid opens here',
                   fontname='Helvetica', fontsize=7)
    for yv in (0, c.lid, c.H):
        witness(pg, (x0 + c.L * k, y1 + yv * k), (x0 + c.L * k + 20 * MM, y1 + yv * k))
    dim_v(pg, y1, y1 + c.lid * k, x0 + c.L * k + 7 * MM, f'{c.lid:g} lid', anchor='right')
    dim_v(pg, y1 + c.lid * k, y1 + c.H * k, x0 + c.L * k + 7 * MM, f'{c.base:g} base',
          anchor='right')
    dim_v(pg, y1, y1 + c.H * k, x0 - 8 * MM, f'{c.H:g}')
    for yv in (0, c.H):
        witness(pg, (x0, y1 + yv * k), (x0 - 13 * MM, y1 + yv * k))

    # end
    x2 = x0 + c.L * k + 46 * MM
    face(pg, x2, y1, c.W, c.H, c, k)
    line(pg, (x2, y1 + c.lid * k), (x2 + c.W * k, y1 + c.lid * k), 0.8, (1, 1, 1))
    pg.insert_text(pymupdf.Point(x2, y1 - 4 * MM), 'end', fontname='Helvetica', fontsize=7)
    for xv in (0, c.W):
        witness(pg, (x2 + xv * k, y1 + c.H * k), (x2 + xv * k, y1 + c.H * k + 13 * MM))
    dim_h(pg, x2, x2 + c.W * k, y1 + c.H * k + 8 * MM, f'{c.W:g}')

    nx = x0 + c.L * k + 16 * MM
    y = note(pg, nx, y0 + 2 * MM, [
        'tooling, every face',
        f'debossed line {c.b:g} in from the edge',
        f'corner cap R{c.R:g}, line turns on R{c.Rl:g}',
        f'stud ø{c.stud:g}, {c.stud_in:g} in from both edges',
        f'line meets the cap {c.run():.1f} along the edge',
    ], bold_first=True)
    note(pg, nx, y + 4 * MM, [
        'gold foil, lid only',
        f'medallion {c.medal:g} x {c.medal:g}',
        f'wordmark {c.mark_w:g} x {c.mark_h:g}',
        f'{c.gap:g} between them, block centred',
    ], bold_first=True)
    return pg


def sheet_detail(doc, c):
    """One corner, at 2:1, with the tooling set out from the corner itself."""
    k = 2.0 * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box \u00b7 corner detail',
          'at 2:1.  every dimension is taken from the corner of the face')
    vw, vh = 42.0, 34.0                       # how much of the face is shown
    x0, y0 = 54 * MM, 66 * MM
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + vw * k, y0 + vh * k), color=None, fill=LEATHER)

    pale = (0.58, 0.56, 0.55)
    run = c.run()
    a1, a2 = math.asin(c.b / c.Rl), math.acos(c.b / c.Rl)
    # the cap, a full quarter round struck from the corner
    pg.draw_polyline([pymupdf.Point(x0 + px * k, y0 + py * k)
                      for px, py in _arc(0, 0, 1, 1, c.R, 0.0, math.pi / 2)],
                     color=pale, width=1.2)
    # the debossed line: its corner arc, then straight away on both sides
    pts = [(vw, c.b)] + _arc(0, 0, 1, 1, c.Rl, a1, a2) + [(c.b, vh)]
    pg.draw_polyline([pymupdf.Point(x0 + px * k, y0 + py * k) for px, py in pts],
                     color=pale, width=1.2)
    # the stud
    pg.draw_circle(pymupdf.Point(x0 + c.stud_in * k, y0 + c.stud_in * k),
                   c.stud * k / 2, color=pale, fill=None, width=1.0)

    # set out along the top edge
    for xv in (0, run, c.Rl, c.R):
        witness(pg, (x0 + xv * k, y0), (x0 + xv * k, y0 - 30 * MM))
    dim_h(pg, x0, x0 + c.R * k, y0 - 25 * MM, f'R{c.R:g}  cap')
    dim_h(pg, x0, x0 + c.Rl * k, y0 - 16 * MM, f'R{c.Rl:g}  line')
    dim_h(pg, x0, x0 + run * k, y0 - 7 * MM, f'{run:.1f}  line meets its arc')
    # down the left edge
    for yv in (0, c.b, c.R):
        witness(pg, (x0, y0 + yv * k), (x0 - 32 * MM, y0 + yv * k))
    dim_v(pg, y0, y0 + c.b * k, x0 - 10 * MM, f'{c.b:g}  line inset', anchor='left')
    dim_v(pg, y0, y0 + c.R * k, x0 - 28 * MM, f'R{c.R:g}', anchor='left')
    # the stud, off the bisector
    witness(pg, (x0 + c.stud_in * k, y0), (x0 + c.stud_in * k, y0 + c.stud_in * k))
    witness(pg, (x0, y0 + c.stud_in * k), (x0 + c.stud_in * k, y0 + c.stud_in * k))
    dim_h(pg, x0, x0 + c.stud_in * k, y0 + (c.stud_in + 9) * k, f'{c.stud_in:g}')
    dim_v(pg, y0, y0 + c.stud_in * k, x0 + (c.stud_in + 9) * k, f'{c.stud_in:g}')
    pg.insert_text(pymupdf.Point(x0 + (c.stud_in + 12) * k, y0 + (c.stud_in + 10) * k),
                   f'stud \u00f8{c.stud:g}, dome', fontname='Helvetica', fontsize=7)

    note(pg, x0, y0 + vh * k + 18 * MM, [
        'blind deboss: no ink, no foil, a tooled groove in the leatherette.',
        'groove about 0.35 deep and 0.8 wide, radiused, not a sharp vee.',
        f'the cap is a quarter round of R{c.R:g} struck from the corner, left slightly '
        'proud of the face.',
        f'the line turns on R{c.Rl:g} about the same centre, so the two stay '
        f'{c.R-c.Rl:g} apart the whole way round the corner.',
        f'the stud is a dome \u00f8{c.stud:g}, about 0.8 proud, sitting on the 45\u00b0 '
        f'bisector {c.stud_in*math.sqrt(2):.1f} from the corner.',
        'the same tooling runs on all six faces, and the lid opening cuts across it.',
        'the straight runs here carry on to the next corner; they are cut short for the '
        'detail only.',
    ])
    return pg


def sheet_build(doc, c, s):
    k = s * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box · construction',
          f'section on the length.  drawing at 1:{1/s:g}')
    x0, y0 = 30 * MM, 54 * MM
    t = (c.board + c.wrap) * k
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + c.L * k, y0 + c.H * k),
                 color=LEATHER, fill=(1, 1, 1), width=0.5)
    for r in (pymupdf.Rect(x0, y0, x0 + c.L * k, y0 + t),
              pymupdf.Rect(x0, y0 + c.H * k - t, x0 + c.L * k, y0 + c.H * k),
              pymupdf.Rect(x0, y0, x0 + t, y0 + c.H * k),
              pymupdf.Rect(x0 + c.L * k - t, y0, x0 + c.L * k, y0 + c.H * k)):
        pg.draw_rect(r, color=None, fill=LEATHER)
    pg.draw_rect(pymupdf.Rect(x0 + t, y0 + c.lid * k, x0 + c.L * k - t,
                              y0 + c.lid * k + 1.2 * k), color=None, fill=(0.75, 0.2, 0.2))
    pg.draw_rect(pymupdf.Rect(x0 + t, y0 + c.H * k - t - 1.2 * k, x0 + c.L * k - t,
                              y0 + c.H * k - t), color=None, fill=(0.75, 0.2, 0.2))
    line(pg, (x0, y0 + c.lid * k), (x0 + c.L * k, y0 + c.lid * k), 0.5, CUT)
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM), 'section on the length',
                   fontname='Helvetica', fontsize=7)
    witness(pg, (x0, y0), (x0 - 16 * MM, y0))
    witness(pg, (x0, y0 + c.lid * k), (x0 - 16 * MM, y0 + c.lid * k))
    witness(pg, (x0, y0 + c.H * k), (x0 - 16 * MM, y0 + c.H * k))
    dim_v(pg, y0, y0 + c.lid * k, x0 - 10 * MM, f'{c.lid:g}', anchor='left')
    dim_v(pg, y0 + c.lid * k, y0 + c.H * k, x0 - 10 * MM, f'{c.base:g}', anchor='left')

    rows = [
        ('carcass', f'{c.board:g} mm greyboard, mitred and taped'),
        ('wrap', f'{c.wrap:g} mm black leatherette, tooled flat then wrapped'),
        ('lining', 'black velvet over 1 mm card, floor and lid inner'),
        ('lid', f'{c.lid:g} mm deep, hinged on the back long edge'),
        ('hinge', 'two 25 mm brass butt hinges, 40 mm in from each end'),
        ('closure', 'magnetic catch at the centre of the front edge'),
        ('inside', f'{c.in_L:g} x {c.in_W:g} x {c.in_H:g} mm clear before lining'),
        ('foil', 'gold, hot stamped on the lid top only'),
        ('deboss', 'blind, all six faces, before assembly'),
    ]
    tx, ty = 30 * MM, y0 + c.H * k + 22 * MM
    for name, v in rows:
        pg.insert_text(pymupdf.Point(tx, ty), name, fontname='Helvetica-Bold', fontsize=7.5)
        pg.insert_text(pymupdf.Point(tx + 32 * MM, ty), v, fontname='Helvetica', fontsize=7.5)
        ty += 5.2 * MM
    return pg


def sheet_art(doc, c, which):
    """1:1 stamping artwork for one face."""
    k = MM
    fw, fh, label = which
    pg = doc.new_page(width=(fw + 90) * MM, height=(fh + 80) * MM)
    title(pg, 20 * MM, 18 * MM, f'TRAXNYC box · artwork · {label}',
          'full size.  magenta cuts, grey debosses, gold is foil')
    x0, y0 = 30 * MM, 40 * MM
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + fw * k, y0 + fh * k), color=CUT,
                 fill=None, width=0.6)
    for d in (3,):
        pg.draw_rect(pymupdf.Rect(x0 - d * k, y0 - d * k, x0 + (fw + d) * k,
                                  y0 + (fh + d) * k), color=CUT, fill=None,
                     width=0.4, dashes='[3 2] 0')
    deboss(pg, x0, y0, fw * k, fh * k, c.b * k, c.Rl * k, (0.45, 0.45, 0.45), 0.8)
    caps(pg, x0, y0, fw * k, fh * k, c.R * k, (0.45, 0.45, 0.45), 0.8)
    studs(pg, x0, y0, fw * k, fh * k, c.stud_in * k, c.stud * k, (0.45, 0.45, 0.45))
    if label.startswith('lid top'):
        a, b = mark(pg, x0 + fw * k / 2, y0 + fh * k / 2, c, k, solid=False)
        pg.insert_text(pymupdf.Point(a.x1 + 3 * MM, a.y0 + 4 * MM),
                       'medallion — your file, centred here',
                       fontname='Helvetica', fontsize=6.5, color=GOLD)
        pg.insert_text(pymupdf.Point(b.x1 + 3 * MM, b.y1 - 1 * MM),
                       'TRAXNYC — your file, centred here',
                       fontname='Helvetica', fontsize=6.5, color=GOLD)
        witness(pg, (x0 + fw * k / 2, y0), (x0 + fw * k / 2, y0 - 12 * MM))
        dim_h(pg, x0, x0 + fw * k / 2, y0 - 8 * MM, f'{fw/2:g} to centre')
        dim_v(pg, a.y0, a.y1, x0 - 9 * MM, f'{c.medal:g}', anchor='left')
        dim_v(pg, b.y0, b.y1, x0 - 9 * MM, f'{c.mark_h:g}', anchor='left')
        witness(pg, (x0, a.y0), (x0 - 11 * MM, a.y0))
        witness(pg, (x0, a.y1), (x0 - 11 * MM, a.y1))
        witness(pg, (x0, b.y0), (x0 - 11 * MM, b.y0))
        witness(pg, (x0, b.y1), (x0 - 11 * MM, b.y1))
    witness(pg, (x0, y0 + fh * k), (x0, y0 + fh * k + 16 * MM))
    witness(pg, (x0 + fw * k, y0 + fh * k), (x0 + fw * k, y0 + fh * k + 16 * MM))
    dim_h(pg, x0, x0 + fw * k, y0 + fh * k + 11 * MM, f'{fw:g}')
    dim_v(pg, y0, y0 + fh * k, x0 + fw * k + 11 * MM, f'{fh:g}', anchor='right')
    witness(pg, (x0 + fw * k, y0), (x0 + fw * k + 13 * MM, y0))
    witness(pg, (x0 + fw * k, y0 + fh * k), (x0 + fw * k + 13 * MM, y0 + fh * k))
    note(pg, x0, y0 + fh * k + 26 * MM, [
        'magenta solid = trim.  magenta dashed = 3 mm bleed on the wrap.',
        f'grey = blind deboss: line {c.b:g} in from trim turning on R{c.Rl:g}, '
        f'cap R{c.R:g}, stud \u00f8{c.stud:g}.',
        'nothing grey is printed or foiled; it is tooling only.',
    ])
    return pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--L', type=float, default=170.0)
    ap.add_argument('--W', type=float, default=70.0)
    ap.add_argument('--H', type=float, default=60.0)
    ap.add_argument('--lid', type=float, default=20.0)
    ap.add_argument('--board', type=float, default=2.0)
    ap.add_argument('--wrap', type=float, default=0.8)
    ap.add_argument('--border', type=float, default=7.0)
    ap.add_argument('--cap', type=float, default=22.0, help='corner cap radius')
    ap.add_argument('--line-r', type=float, default=17.0,
                    help='radius the debossed line turns on, about the same centre')
    ap.add_argument('--stud', type=float, default=3.5)
    ap.add_argument('--stud-in', type=float, default=9.0)
    ap.add_argument('--medal', type=float, default=26.0)
    ap.add_argument('--mark-w', type=float, default=52.0)
    ap.add_argument('--mark-h', type=float, default=8.0)
    ap.add_argument('--gap', type=float, default=4.0)
    ap.add_argument('--scale', type=float, default=0.5)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    c = Box(a.L, a.W, a.H, a.lid, a.board, a.wrap, a.border, a.cap, a.line_r,
            a.stud, a.stud_in, a.medal, a.mark_w, a.mark_h, a.gap)

    spec = pymupdf.open()
    sheet_ga(spec, c, a.scale)
    sheet_build(spec, c, a.scale)
    sheet_detail(spec, c)
    f1 = os.path.join(a.out_dir, 'traxnyc-box-production.pdf')
    spec.save(f1, garbage=4, deflate=True)

    art = pymupdf.open()
    sheet_art(art, c, (c.L, c.W, 'lid top · deboss + gold foil'))
    sheet_art(art, c, (c.L, c.H, 'long side · deboss only'))
    sheet_art(art, c, (c.W, c.H, 'end · deboss only'))
    f2 = os.path.join(a.out_dir, 'traxnyc-box-artwork.pdf')
    art.save(f2, garbage=4, deflate=True)

    print(f'{f1}  3 sheets\n{f2}  3 faces at 1:1\n'
          f'  outside {c.L:g} x {c.W:g} x {c.H:g}, inside {c.in_L:g} x {c.in_W:g} x {c.in_H:g}\n'
          f'  deboss {c.b:g} in, cap R{c.R:g}, line turns on R{c.Rl:g}, '
          f'meeting it {c.run():.1f} along the edge',
          file=sys.stderr)


if __name__ == '__main__':
    main()
