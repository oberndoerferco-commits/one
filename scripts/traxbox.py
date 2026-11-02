#!/usr/bin/env python3
"""Exterior drawings and stamping artwork for the TRAXNYC trunk box.

A rigid board carcass wrapped in black leatherette, tooled in the trunk
manner: a quarter-round cap worked into each corner with a domed stud in
it, and a blind-debossed line inside the caps. Gold foil on the lid top.
Exterior only -- nothing here about fittings or lining.

THREE PARTS, read off the client's sample.

  plinth   the bottom 15 mm band, on all four sides. It never moves. It
           carries the four BOTTOM corner caps.
  lap      the 40 mm front panel, hinged along the top of the plinth. It
           drops forward and the magnetic catch holds it shut. It carries
           NO corner caps: the caps a closed box shows near the front are
           the lid's, above it, and the plinth's, below it. Nothing is
           worked into the lap itself.
  lid      the top, plus a 40 mm skirt on the back and both ends, hinged
           at the back. It carries the four TOP corner caps and the foil.

15 + 40 + 5 = 60. The last 5 mm is the rolled top edge, which is why a
tape laid down the front face reads 40 and not 45.

The debossed line stops at the cap and does not go round it. An arc of
radius R struck from the corner crosses a line inset b from the edge at
sqrt(R^2 - b^2) along that edge, so the straight run ends there and the
two marks meet without one crossing the other. R is tied to the plinth:
at R20 a lower cap reaches exactly as far along the vertical edge as the
plinth is tall, so no cap ever straddles the opening line.
"""
import argparse, math, os, sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft import MM, GREY, line, dim_h, dim_v, witness, note, title  # noqa: E402

LEATHER = (0.13, 0.12, 0.12)
TOOL = (0.42, 0.40, 0.39)
GOLD = (0.76, 0.60, 0.29)
CUT = (0.90, 0.10, 0.45)
HID = (0.20, 0.45, 0.85)
FOLDC = (0.10, 0.35, 0.80)

# corner keys, in face coordinates with y down
TL, TR, BR, BL = 'tl', 'tr', 'br', 'bl'
ALL4 = (TL, TR, BR, BL)
TOP2 = (TL, TR)
BOT2 = (BL, BR)


class Box:
    def __init__(self, L, W, H, plinth, lap, board, wrap, b, R, stud,
                 stud_in, magnet, medal, mark_w, mark_h, gap):
        self.L, self.W, self.H = L, W, H
        self.plinth, self.lap = plinth, lap
        self.board, self.wrap = board, wrap
        self.b, self.R, self.stud, self.stud_in = b, R, stud, stud_in
        self.magnet = magnet
        self.medal, self.mark_w, self.mark_h, self.gap = medal, mark_w, mark_h, gap

    @property
    def roll(self):
        """The rolled top edge: what is left of the height."""
        return self.H - self.plinth - self.lap

    @property
    def skirt(self):
        """Depth of the lid's skirt on the back and both ends."""
        return self.lap

    @property
    def run(self):
        """Where a debossed line meets a cap, measured along the edge."""
        return math.sqrt(max(0.0, self.R ** 2 - self.b ** 2))


# ------------------------------------------------------------- primitives

def _arc(cx, cy, sx, sy, R, a0, a1, n=28):
    return [(cx + sx * R * math.cos(a0 + (a1 - a0) * i / n),
             cy + sy * R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _corner(w, h, key):
    """Corner origin and the signs that point inboard from it."""
    cx = 0.0 if key[1] == 'l' else w
    cy = 0.0 if key[0] == 't' else h
    return cx, cy, (1 if key[1] == 'l' else -1), (1 if key[0] == 't' else -1)


def deboss(pg, x, y, w, h, b, R, which=ALL4, col=TOOL, width=0.7):
    """Four straight runs. A run stops short only at a corner that has a cap."""
    r = math.sqrt(max(0.0, R * R - b * b)) if R > b else 0.0

    def inx(key):
        return r if key in which else b

    segs = [((inx(TL), b), (w - inx(TR), b)),
            ((w - b, inx(TR)), (w - b, h - inx(BR))),
            ((inx(BL), h - b), (w - inx(BR), h - b)),
            ((b, inx(TL)), (b, h - inx(BL)))]
    for p0, p1 in segs:
        if (p1[0] - p0[0]) + (p1[1] - p0[1]) <= 0.2:
            continue                       # the face is too small for a run
        line(pg, (x + p0[0], y + p0[1]), (x + p1[0], y + p1[1]), width, col)


def caps(pg, x, y, w, h, R, which=ALL4, col=TOOL, width=0.7):
    """Quarter-round cap arcs, clipped to the face if it is shallower than R."""
    for key in which:
        cx, cy, sx, sy = _corner(w, h, key)
        pts = [(px, py) for px, py in _arc(cx, cy, sx, sy, R, 0.0, math.pi / 2)
               if -0.01 <= px <= w + 0.01 and -0.01 <= py <= h + 0.01]
        if len(pts) > 1:
            pg.draw_polyline([pymupdf.Point(x + px, y + py) for px, py in pts],
                             color=col, width=width)


def studs(pg, x, y, w, h, inset, dia, which=ALL4, col=TOOL, width=0.6):
    for key in which:
        cx, cy, sx, sy = _corner(w, h, key)
        pg.draw_circle(pymupdf.Point(x + cx + sx * inset, y + cy + sy * inset),
                       dia / 2, color=col, fill=None, width=width)


def face(pg, x, y, fw, fh, c, k, which=ALL4, border=True, fill=LEATHER,
         tool=TOOL, width=0.7):
    """One decorated exterior panel, fw x fh mm, top-left at (x, y)."""
    if fill:
        pg.draw_rect(pymupdf.Rect(x, y, x + fw * k, y + fh * k), color=None, fill=fill)
    if border:
        deboss(pg, x, y, fw * k, fh * k, c.b * k, c.R * k, which, tool, width)
    if which:
        caps(pg, x, y, fw * k, fh * k, c.R * k, which, tool, width)
        studs(pg, x, y, fw * k, fh * k, c.stud_in * k, c.stud * k, which, tool)


def mark(pg, cx, cy, c, k, col=GOLD, solid=True):
    """Foil: the medallion over the wordmark, drawn as placeholder blocks."""
    mh, mw = c.medal * k, c.mark_w * k
    tot = mh + c.gap * k + c.mark_h * k
    top = cy - tot / 2
    a = pymupdf.Rect(cx - mh / 2, top, cx + mh / 2, top + mh)
    b = pymupdf.Rect(cx - mw / 2, top + mh + c.gap * k, cx + mw / 2, top + tot)
    for r in (a, b):
        pg.draw_rect(r, color=col, fill=col if solid else None, width=0.7,
                     dashes=None if solid else '[2.5 2] 0')
    return a, b


def magnets(pg, x, y, w, k, c, col=CUT):
    """The catch pair, centred on the lap's free edge."""
    for sx in (-1, 1):
        pg.draw_circle(pymupdf.Point(x + w * k / 2 + sx * c.magnet / 2 * k, y),
                       2.0 * MM, color=col, fill=None, width=0.6)


# ------------------------------------------------------------------ sheets

def _page(doc, land=True):
    return doc.new_page(width=842 if land else 595, height=595 if land else 842)


def sheet_ga(doc, c, s):
    """General arrangement: the three faces a buyer sees, closed."""
    k = s * MM
    pg = _page(doc)
    title(pg, 24 * MM, 20 * MM, 'TRAXNYC trunk box — general arrangement',
          f'closed {c.L:g} x {c.W:g} x {c.H:g} mm · scale 1:{1 / s:g} · '
          f'exterior only · all dimensions mm')

    x0, y1 = 30 * MM, 52 * MM

    # --- front elevation: plinth, lap, roll -------------------------------
    pg.insert_text(pymupdf.Point(x0, y1 - 4 * MM),
                   'front — the lap drops forward off the plinth line',
                   fontname='Helvetica', fontsize=7, color=GREY)
    y_lap = y1 + c.roll * k
    y_pl = y_lap + c.lap * k
    # roll (part of the lid, seen edge on)
    pg.draw_rect(pymupdf.Rect(x0, y1, x0 + c.L * k, y_lap), color=None, fill=LEATHER)
    face(pg, x0, y_lap, c.L, c.lap, c, k, which=(), border=True)      # the lap
    face(pg, x0, y_pl, c.L, c.plinth, c, k, which=BOT2, border=False)  # plinth
    for yy, lab in ((y_lap, 'lid edge / lap'), (y_pl, 'lap / plinth')):
        line(pg, (x0, yy), (x0 + c.L * k, yy), 0.9, (1, 1, 1))
    magnets(pg, x0, y_lap + 1.2 * MM, c.L, k, c)
    dim_h(pg, x0, x0 + c.L * k, y_pl + c.plinth * k + 10 * MM, f'{c.L:g}')
    dim_v(pg, y1, y_lap, x0 + c.L * k + 8 * MM, f'{c.roll:g} roll', anchor='right')
    dim_v(pg, y_lap, y_pl, x0 + c.L * k + 8 * MM, f'{c.lap:g} lap', anchor='right')
    dim_v(pg, y_pl, y_pl + c.plinth * k, x0 + c.L * k + 8 * MM,
          f'{c.plinth:g} plinth', anchor='right')
    dim_v(pg, y1, y_pl + c.plinth * k, x0 - 12 * MM, f'{c.H:g}', anchor='left')

    # --- end elevation ----------------------------------------------------
    x2 = x0 + c.L * k + 46 * MM
    pg.insert_text(pymupdf.Point(x2, y1 - 4 * MM), 'end — skirt over plinth',
                   fontname='Helvetica', fontsize=7, color=GREY)
    pg.draw_rect(pymupdf.Rect(x2, y1, x2 + c.W * k, y1 + c.roll * k),
                 color=None, fill=LEATHER)
    face(pg, x2, y1 + c.roll * k, c.W, c.skirt, c, k, which=TOP2, border=True)
    face(pg, x2, y_pl, c.W, c.plinth, c, k, which=BOT2, border=False)
    line(pg, (x2, y_pl), (x2 + c.W * k, y_pl), 0.9, (1, 1, 1))
    dim_h(pg, x2, x2 + c.W * k, y_pl + c.plinth * k + 10 * MM, f'{c.W:g}')

    # --- plan: the lid top with the foil ----------------------------------
    y3 = y_pl + c.plinth * k + 26 * MM
    pg.insert_text(pymupdf.Point(x0, y3 - 4 * MM), 'lid top — foil and caps',
                   fontname='Helvetica', fontsize=7, color=GREY)
    face(pg, x0, y3, c.L, c.W, c, k, which=ALL4, border=True)
    mark(pg, x0 + c.L * k / 2, y3 + c.W * k / 2, c, k)
    dim_h(pg, x0, x0 + c.L * k, y3 + c.W * k + 10 * MM, f'{c.L:g}')
    dim_v(pg, y3, y3 + c.W * k, x0 - 12 * MM, f'{c.W:g}', anchor='left')

    note(pg, x2, y3 + 2 * MM, [
        'The lap carries no corner cap.',
        'The caps you see beside it when the box is',
        'shut belong to the lid above and the plinth',
        f'below. Cap reach {c.R:g}; the plinth is {c.plinth:g}, so a',
        'lower cap finishes exactly on the plinth line',
        'and nothing crosses the opening.',
        '',
        f'Magnetic catch: pair at {c.magnet:g} centres, set behind',
        "the lap's free edge, catching the lid.",
    ], bold_first=True)
    return pg


def sheet_parts(doc, c, s):
    """The three parts separated, so the split is unmistakable."""
    k = s * MM
    pg = _page(doc)
    title(pg, 24 * MM, 20 * MM, 'TRAXNYC trunk box — how it opens',
          'the three parts drawn apart · scale 1:%g' % (1 / s))

    x0, y0 = 32 * MM, 54 * MM
    gap = 16 * MM

    # lid
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM),
                   f'1 · LID — top {c.L:g} x {c.W:g} plus a {c.skirt:g} skirt on the back and '
                   'both ends. Hinged at the back. Four top caps, and the foil.',
                   fontname='Helvetica-Bold', fontsize=7.5, color=(0, 0, 0))
    face(pg, x0, y0, c.L, c.W, c, k, which=ALL4, border=True)
    mark(pg, x0 + c.L * k / 2, y0 + c.W * k / 2, c, k)
    face(pg, x0, y0 + c.W * k + 3 * MM, c.L, c.skirt, c, k, which=TOP2, border=True)
    pg.insert_text(pymupdf.Point(x0 + c.L * k + 5 * MM, y0 + c.W * k + 10 * MM),
                   'back skirt', fontname='Helvetica', fontsize=6.5, color=GREY)
    for i, sx in enumerate((0, 1)):
        ex = x0 + c.L * k + 14 * MM + i * (c.W * k + 8 * MM)
        face(pg, ex, y0, c.W, c.skirt, c, k, which=TOP2, border=True)
        pg.insert_text(pymupdf.Point(ex, y0 - 1.5 * MM),
                       'end skirt', fontname='Helvetica', fontsize=6.5, color=GREY)

    # lap
    y1 = y0 + c.W * k + c.skirt * k + gap + 8 * MM
    pg.insert_text(pymupdf.Point(x0, y1 - 4 * MM),
                   f'2 · LAP — {c.L:g} x {c.lap:g}. Hinged on the plinth line, drops forward. '
                   'Debossed line only: NO caps, NO studs.',
                   fontname='Helvetica-Bold', fontsize=7.5, color=(0, 0, 0))
    face(pg, x0, y1, c.L, c.lap, c, k, which=(), border=True)
    magnets(pg, x0, y1 - 1.2 * MM, c.L, k, c)
    dim_v(pg, y1, y1 + c.lap * k, x0 - 12 * MM, f'{c.lap:g}', anchor='left')
    dim_h(pg, x0 + (c.L / 2 - c.magnet / 2) * k, x0 + (c.L / 2 + c.magnet / 2) * k,
          y1 + 5.5 * MM, f'{c.magnet:g} catch centres', col=CUT)

    # plinth
    y2 = y1 + c.lap * k + gap
    pg.insert_text(pymupdf.Point(x0, y2 - 4 * MM),
                   f'3 · PLINTH — a {c.plinth:g} band all the way round, '
                   f'{c.L:g} + {c.W:g} + {c.L:g} + {c.W:g}. Fixed. '
                   'Four bottom caps, no debossed line (the band is too shallow).',
                   fontname='Helvetica-Bold', fontsize=7.5, color=(0, 0, 0))
    bx = x0
    for w, lab in ((c.L, 'front'), (c.W, 'end'), (c.L, 'back'), (c.W, 'end')):
        face(pg, bx, y2, w, c.plinth, c, k, which=BOT2, border=False)
        pg.insert_text(pymupdf.Point(bx + 1.5 * MM, y2 + c.plinth * k + 4 * MM),
                       lab, fontname='Helvetica', fontsize=6, color=GREY)
        bx += w * k
        line(pg, (bx, y2 - 2 * MM), (bx, y2 + c.plinth * k + 2 * MM), 0.6, FOLDC,
             '[2 1.6] 0')
    dim_v(pg, y2, y2 + c.plinth * k, x0 - 12 * MM, f'{c.plinth:g}', anchor='left')
    return pg


def sheet_detail(doc, c):
    """One corner at 2:1, with the geometry that fixes the cap and the line."""
    k = 2.0 * MM
    pg = _page(doc, land=False)
    title(pg, 24 * MM, 20 * MM, 'Corner detail',
          'scale 2:1 · the debossed line stops where the cap arc crosses it')

    fw, fh = 46.0, 40.0
    x0, y0 = 40 * MM, 56 * MM
    face(pg, x0, y0, fw, fh, c, k, which=(TL,), border=True, width=0.9)

    r = c.run
    witness(pg, (x0, y0 + c.b * k), (x0 - 10 * MM, y0 + c.b * k))
    dim_v(pg, y0, y0 + c.b * k, x0 - 8 * MM, f'{c.b:g}', anchor='left')
    witness(pg, (x0 + r * k, y0), (x0 + r * k, y0 - 10 * MM))
    dim_h(pg, x0, x0 + r * k, y0 - 8 * MM, f'{r:.1f}')
    witness(pg, (x0 + c.R * k, y0), (x0 + c.R * k, y0 - 18 * MM))
    dim_h(pg, x0, x0 + c.R * k, y0 - 16 * MM, f'R{c.R:g} cap reach')
    sx = x0 + c.stud_in * k
    sy = y0 + c.stud_in * k
    witness(pg, (sx, sy), (sx, y0 - 4 * MM))
    dim_h(pg, x0, sx, y0 + 15 * MM, f'{c.stud_in:g}')
    dim_v(pg, y0, sy, x0 + 17 * MM, f'{c.stud_in:g}', anchor='right')

    note(pg, 40 * MM, y0 + fh * k + 20 * MM, [
        'Cap: a quarter-round struck from the corner, worked in the wrap.',
        f'Radius {c.R:g}. Domed stud {c.stud:g} dia, centre {c.stud_in:g} in from both edges.',
        f'Debossed line {c.b:g} in from the edge, {0.7:g} wide, blind — no colour.',
        f'The straight run ends at sqrt({c.R:g}^2 - {c.b:g}^2) = {r:.1f} from the corner,',
        'where the arc crosses it. The two marks meet; neither crosses.',
        '',
        'The cap is NOT drawn round into the field, and it is NOT drawn on',
        'the lap. Faces that carry caps: lid top (4), lid back and both end',
        'skirts (top 2 each), plinth band (bottom 2 each run), bottom (4).',
    ], bold_first=True)
    return pg


def sheet_flat(doc, c, s):
    """The exterior opened out, cut at the two hinges.

    What a printer and a tooler need: every decorated panel in the place it
    occupies when the covering is laid flat. The box is two sub-assemblies,
    so this is two developments side by side, not one continuous net.

    In a development every cap sits against a FOLD, because a cap wraps a
    real edge of the finished box. So the keys below name the corners on
    the fold side of each panel, not the corners of the drawing.
    """
    k = s * MM
    pg = doc.new_page(width=1191, height=842)        # A3 landscape
    title(pg, 26 * MM, 22 * MM,
          'TRAXNYC trunk box — printing and tooling, laid flat',
          f'closed {c.L:g} x {c.W:g} x {c.H:g} · scale 1:{1 / s:.1f} · '
          'magenta = outer silhouette (cut) · blue dashed = fold · '
          'grey = blind deboss · gold = foil')

    # ---- A: the base, developed off the bottom --------------------------
    ax, ay = 40 * MM, 74 * MM
    pg.insert_text(pymupdf.Point(ax, ay - 16 * MM), 'A  ·  BASE — fixed',
                   fontname='Helvetica-Bold', fontsize=10)
    pg.insert_text(pymupdf.Point(ax, ay - 10.5 * MM),
                   f'bottom {c.L:g} x {c.W:g}, a {c.plinth:g} plinth band on all four sides, '
                   f'and the {c.lap:g} lap hinged off the front band',
                   fontname='Helvetica', fontsize=7, color=GREY)

    bw, bh = c.L, c.W
    ox = ax + c.plinth * k
    oy = ay + c.plinth * k

    def A(mx, my):
        return (ox + mx * k, oy + my * k)

    face(pg, *A(0, -c.plinth), bw, c.plinth, c, k, which=TOP2, border=False)
    face(pg, *A(0, bh), bw, c.plinth, c, k, which=BOT2, border=False)
    face(pg, *A(-c.plinth, 0), c.plinth, bh, c, k, which=(TL, BL), border=False)
    face(pg, *A(bw, 0), c.plinth, bh, c, k, which=(TR, BR), border=False)
    face(pg, *A(0, 0), bw, bh, c, k, which=ALL4, border=True)
    pg.insert_text(pymupdf.Point(*A(3, 8)), 'BOTTOM', fontname='Helvetica-Bold',
                   fontsize=8, color=(1, 1, 1))
    for lab, pt in (('back band', A(3, -c.plinth + 10)),
                    ('front band', A(3, bh + 10)),
                    ('end', A(-c.plinth + 3, bh - 3)),
                    ('end', A(bw + 3, bh - 3))):
        pg.insert_text(pymupdf.Point(*pt), lab, fontname='Helvetica',
                       fontsize=5.5, color=(1, 1, 1))

    lx, ly = A(0, bh + c.plinth)
    face(pg, lx, ly, c.L, c.lap, c, k, which=(), border=True)
    pg.insert_text(pymupdf.Point(lx + 3 * MM, ly + 7 * MM),
                   f'LAP  {c.L:g} x {c.lap:g}  —  no caps, no studs',
                   fontname='Helvetica-Bold', fontsize=8, color=(1, 1, 1))
    magnets(pg, lx, ly + c.lap * k - 2 * MM, c.L, k, c)
    pg.insert_text(pymupdf.Point(lx + 3 * MM, ly + c.lap * k - 6 * MM),
                   f'magnetic catch, pair at {c.magnet:g} centres',
                   fontname='Helvetica', fontsize=5.5, color=CUT)

    sil = [A(0, -c.plinth), A(bw, -c.plinth), A(bw, 0), A(bw + c.plinth, 0),
           A(bw + c.plinth, bh), A(bw, bh), A(bw, bh + c.plinth + c.lap),
           A(0, bh + c.plinth + c.lap), A(0, bh), A(-c.plinth, bh),
           A(-c.plinth, 0), A(0, 0)]
    pg.draw_polyline([pymupdf.Point(*q) for q in sil], color=CUT, width=1.3,
                     closePath=True)
    for p0, p1 in ((A(0, 0), A(bw, 0)), (A(0, bh), A(bw, bh)),
                   (A(0, 0), A(0, bh)), (A(bw, 0), A(bw, bh)),
                   (A(0, bh + c.plinth), A(bw, bh + c.plinth))):
        line(pg, p0, p1, 1.0, FOLDC, '[3 2] 0')

    dim_h(pg, A(0, 0)[0], A(bw, 0)[0], A(0, -c.plinth)[1] - 9 * MM, f'{c.L:g}')
    xd = A(-c.plinth, 0)[0] - 10 * MM
    dim_v(pg, A(0, -c.plinth)[1], A(0, 0)[1], xd, f'{c.plinth:g}', anchor='left')
    dim_v(pg, A(0, 0)[1], A(0, bh)[1], xd, f'{c.W:g}', anchor='left')
    dim_v(pg, A(0, bh)[1], A(0, bh + c.plinth)[1], xd, f'{c.plinth:g}', anchor='left')
    dim_v(pg, A(0, bh + c.plinth)[1], A(0, bh + c.plinth + c.lap)[1], xd,
          f'{c.lap:g}', anchor='left')
    dim_h(pg, A(-c.plinth, 0)[0], A(bw + c.plinth, 0)[0],
          A(0, bh + c.plinth + c.lap)[1] + 12 * MM,
          f'{c.plinth:g} + {c.L:g} + {c.plinth:g} = {c.L + 2 * c.plinth:g} over the bands')

    # ---- B: the lid, developed off the top ------------------------------
    bx = ax + (c.L + 2 * c.plinth) * k + 62 * MM
    by = ay + 6 * MM
    pg.insert_text(pymupdf.Point(bx, by - 22 * MM), 'B  ·  LID — hinged at the back',
                   fontname='Helvetica-Bold', fontsize=10)
    pg.insert_text(pymupdf.Point(bx, by - 16.5 * MM),
                   f'top {c.L:g} x {c.W:g} with a {c.skirt:g} skirt on the back and both ends; '
                   f'the front edge is the {c.roll:g} roll only, because the lap closes against it',
                   fontname='Helvetica', fontsize=7, color=GREY)

    tox = bx + c.skirt * k
    toy = by + c.skirt * k

    def B(mx, my):
        return (tox + mx * k, toy + my * k)

    face(pg, *B(0, -c.skirt), c.L, c.skirt, c, k, which=BOT2, border=True)
    face(pg, *B(-c.skirt, 0), c.skirt, c.W, c, k, which=(TR, BR), border=True)
    face(pg, *B(c.L, 0), c.skirt, c.W, c, k, which=(TL, BL), border=True)
    face(pg, *B(0, 0), c.L, c.W, c, k, which=ALL4, border=True)
    mark(pg, B(c.L / 2, c.W / 2)[0], B(c.L / 2, c.W / 2)[1], c, k)
    pg.insert_text(pymupdf.Point(*B(3, 8)), 'LID TOP — foil here',
                   fontname='Helvetica-Bold', fontsize=8, color=(1, 1, 1))
    for lab, pt in (('back skirt', B(3, -c.skirt + 8)),
                    ('end skirt', B(-c.skirt + 3, 8)),
                    ('end skirt', B(c.L + 3, 8))):
        pg.insert_text(pymupdf.Point(*pt), lab, fontname='Helvetica',
                       fontsize=5.5, color=(1, 1, 1))

    sil2 = [B(0, -c.skirt), B(c.L, -c.skirt), B(c.L, 0), B(c.L + c.skirt, 0),
            B(c.L + c.skirt, c.W), B(c.L, c.W), B(0, c.W), B(-c.skirt, c.W),
            B(-c.skirt, 0), B(0, 0)]
    pg.draw_polyline([pymupdf.Point(*q) for q in sil2], color=CUT, width=1.3,
                     closePath=True)
    for p0, p1 in ((B(0, 0), B(c.L, 0)), (B(0, 0), B(0, c.W)),
                   (B(c.L, 0), B(c.L, c.W))):
        line(pg, p0, p1, 1.0, FOLDC, '[3 2] 0')
    line(pg, B(0, c.W), B(c.L, c.W), 1.3, CUT)

    dim_h(pg, B(0, 0)[0], B(c.L, 0)[0], B(0, -c.skirt)[1] - 9 * MM, f'{c.L:g}')
    xe = B(-c.skirt, 0)[0] - 10 * MM
    dim_v(pg, B(0, -c.skirt)[1], B(0, 0)[1], xe, f'{c.skirt:g}', anchor='left')
    dim_v(pg, B(0, 0)[1], B(0, c.W)[1], xe, f'{c.W:g}', anchor='left')
    dim_h(pg, B(-c.skirt, 0)[0], B(c.L + c.skirt, 0)[0], B(0, c.W)[1] + 12 * MM,
          f'{c.skirt:g} + {c.L:g} + {c.skirt:g} = {c.L + 2 * c.skirt:g} over the skirts')

    # ---- what goes where -------------------------------------------------
    ny = max(A(0, bh + c.plinth + c.lap)[1], B(0, c.W)[1]) + 28 * MM
    note(pg, ax, ny, [
        'A and B are separate pieces. B hinges to A along the back of the '
        'plinth; the lap hinges to A along the front of the plinth.',
        'Every corner cap sits against a fold, because a cap wraps a real '
        'edge of the finished box — four on the bottom, four on the top.',
        'The lap is the only large panel with no cap and no stud. The caps '
        'a shut box shows beside it belong to the lid above and the plinth below.',
        f'Allow {c.wrap:g} turn-in on every raw edge, not drawn. Board {c.board:g}.',
        f'Blind deboss: {c.b:g} in from each panel edge, 0.7 wide, each run '
        f'stopping {c.run:.1f} from the corner where the cap arc meets it.',
    ], lead=4.4 * MM)
    return pg


def sheet_art(doc, c, fw, fh, label, which=ALL4, border=True, foil=False,
              catch=False):
    """One panel, 1:1, as the stamping file."""
    pg = doc.new_page(width=(fw + 40) * MM, height=(fh + 46) * MM)
    k = MM
    x0, y0 = 20 * MM, 30 * MM
    pg.insert_text(pymupdf.Point(x0, 14 * MM), f'TRAXNYC box — {label}',
                   fontname='Helvetica-Bold', fontsize=9)
    pg.insert_text(pymupdf.Point(x0, 19.5 * MM),
                   f'{fw:g} x {fh:g} mm · 1:1 · blind deboss in grey'
                   + (' · foil in gold' if foil else '')
                   + ('' if which else ' · NO corner caps on this panel'),
                   fontname='Helvetica', fontsize=6.8, color=GREY)
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + fw * k, y0 + fh * k),
                 color=CUT, fill=None, width=0.6, dashes='[3 2] 0')
    if border:
        deboss(pg, x0, y0, fw * k, fh * k, c.b * k, c.R * k, which, TOOL, 0.7)
    if which:
        caps(pg, x0, y0, fw * k, fh * k, c.R * k, which, TOOL, 0.7)
        studs(pg, x0, y0, fw * k, fh * k, c.stud_in * k, c.stud * k, which, TOOL)
    if foil:
        a, b = mark(pg, x0 + fw * k / 2, y0 + fh * k / 2, c, k, solid=False)
        pg.insert_text(pymupdf.Point(a.x0, a.y0 - 2 * MM),
                       f'medallion {c.medal:g} — client artwork',
                       fontname='Helvetica', fontsize=6, color=GOLD)
        pg.insert_text(pymupdf.Point(b.x0, b.y1 + 4 * MM),
                       f'wordmark {c.mark_w:g} x {c.mark_h:g} — client artwork',
                       fontname='Helvetica', fontsize=6, color=GOLD)
    if catch:
        magnets(pg, x0, y0 + 1.5 * MM, fw, k, c)
        pg.insert_text(pymupdf.Point(x0, y0 - 2.5 * MM),
                       f'magnetic catch, pair at {c.magnet:g} centres, behind this edge',
                       fontname='Helvetica', fontsize=6, color=CUT)
    return pg


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='assets/traxnyc-box')
    ap.add_argument('--L', type=float, default=170.0)
    ap.add_argument('--W', type=float, default=70.0)
    ap.add_argument('--H', type=float, default=60.0)
    ap.add_argument('--plinth', type=float, default=15.0)
    ap.add_argument('--lap', type=float, default=40.0)
    ap.add_argument('--board', type=float, default=2.0)
    ap.add_argument('--wrap', type=float, default=15.0)
    ap.add_argument('--border', type=float, default=7.0, help='deboss inset')
    ap.add_argument('--cap', type=float, default=20.0, help='cap reach')
    ap.add_argument('--stud', type=float, default=3.5)
    ap.add_argument('--stud-in', type=float, default=9.0)
    ap.add_argument('--magnet', type=float, default=40.0)
    ap.add_argument('--medal', type=float, default=26.0)
    ap.add_argument('--mark-w', type=float, default=52.0)
    ap.add_argument('--mark-h', type=float, default=8.0)
    ap.add_argument('--gap', type=float, default=4.0)
    a = ap.parse_args()

    c = Box(a.L, a.W, a.H, a.plinth, a.lap, a.board, a.wrap, a.border, a.cap,
            a.stud, a.stud_in, a.magnet, a.medal, a.mark_w, a.mark_h, a.gap)
    if c.roll < 0:
        sys.exit(f'plinth {c.plinth} + lap {c.lap} exceeds height {c.H}')

    os.makedirs(a.out, exist_ok=True)

    prod = pymupdf.open()
    sheet_ga(prod, c, 0.5)
    sheet_parts(prod, c, 0.5)
    sheet_detail(prod, c)
    sheet_flat(prod, c, 2.0 / 3.0)
    p1 = os.path.join(a.out, 'traxnyc-box-production.pdf')
    prod.save(p1)

    art = pymupdf.open()
    sheet_art(art, c, c.L, c.W, 'lid top', which=ALL4, border=True, foil=True)
    sheet_art(art, c, c.L, c.lap, 'lap (front)', which=(), border=True, catch=True)
    sheet_art(art, c, c.L, c.skirt, 'lid back skirt', which=TOP2, border=True)
    sheet_art(art, c, c.W, c.skirt, 'lid end skirt (x2)', which=TOP2, border=True)
    sheet_art(art, c, c.L, c.plinth, 'plinth band, front and back (x2)',
              which=BOT2, border=False)
    sheet_art(art, c, c.W, c.plinth, 'plinth band, ends (x2)', which=BOT2, border=False)
    sheet_art(art, c, c.L, c.W, 'bottom', which=ALL4, border=True)
    p2 = os.path.join(a.out, 'traxnyc-box-artwork.pdf')
    art.save(p2)

    print(f'{p1}  {prod.page_count} sheets')
    print(f'{p2}  {art.page_count} panels')
    print(f'plinth {c.plinth:g} + lap {c.lap:g} + roll {c.roll:g} = {c.H:g}; '
          f'cap run {c.run:.2f}')


if __name__ == '__main__':
    main()
