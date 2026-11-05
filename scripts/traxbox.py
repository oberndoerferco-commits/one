#!/usr/bin/env python3
"""Exterior drawings and stamping artwork for the trunk box.

Built from the client's own paper net, not inferred from photographs.

ONE PIECE, one column 170 wide, five rows, top to bottom:

    row 1   lap       40      folds down over the front
    row 2   top       70      the lid
    row 3   back      55
    row 4   bottom    65      the two end walls hang off this row
    row 5   front     55

285 over the five rows. The top is 70 and the bottom 65 because the lid
overhangs the front by the thickness of the front wall and the lap. Each
end wall is 65 (matching row 4) by 55 (the wall height). No glue tab.

HOW IT OPENS

    lap     hinged on the top's front edge. Lift it first; the magnetic
            catch is in its free edge. Shut, it covers 40 of the front's
            55 and leaves 15 of the front wall showing below -- which is
            the 4 cm and 1,5 cm measured on the sample.
    lid     the top panel, hinged on the top/back fold. Swings back, and
            the lap folds back with it.
    front   hinged on the bottom's front edge. Drops forward.
    base    bottom, back and both ends. Fixed.

There is no separate bottom band. The 15 reveal is simply the part of the
front wall the lap does not reach.

CORNER CAPS sit at both ends of all four long folds -- eight corners, as
the net draws them. The two front-bottom caps are the ones hidden under
the lap: only their lowest 15 shows on a shut box. The lap's own free
edge carries no cap, and nor does the top edge of the front wall.

The debossed line stops at the cap and does not go round it. An arc of
radius R struck from the corner crosses a line inset b from the edge at
sqrt(R^2 - b^2) along that edge, so the straight run ends there and the
two marks meet without one crossing the other.
"""
import argparse, math, os, sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft import MM, GREY, line, dim_h, dim_v, witness, note, title  # noqa: E402

# The client's own lockup, exported from Canva. Both marks are vector; the
# ink bands were measured off the page at 300 dpi.
LOGO_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'assets', 'traxnyc-box', 'traxnyc-lockup.pdf')
# The foil mark is off. Its geometry stays here because it was measured off
# the sample and is the only record of where it sat, but nothing draws it.
SHOW_LOGO = False

# Where each net sits on its own sheet, in mm. Named because the fused
# sheet has to line the two nets up and must not guess at these.
ART_MX, ART_TOP = 20.0, 36.0       # artwork sheet: margin, top margin
NET_OX, NET_OY = 62.0, 56.0        # A3 net sheet: origin of the net column
MEDAL_CLIP = (113.3, 56.6, 482.2, 425.5)     # the quatrefoil, square
WORD_CLIP = (112.1, 454.8, 482.9, 509.3)     # TRAXNYC
# "MADE IN ITALY" sits below both and is deliberately not used.

LEATHER = (0.13, 0.12, 0.12)
TOOL = (0.42, 0.40, 0.39)
GOLD = (0.76, 0.60, 0.29)
CUT = (0.90, 0.10, 0.45)
FOLDC = (0.10, 0.35, 0.80)
LAPL = (0.35, 0.78, 0.45)

TL, TR, BR, BL = 'tl', 'tr', 'br', 'bl'
ALL4 = (TL, TR, BR, BL)
TOP2 = (TL, TR)
BOT2 = (BL, BR)
LEFT2 = (TL, BL)
RIGHT2 = (TR, BR)


class Box:
    def __init__(self, L, Wt, Wb, H, lap, end_tab, board, wrap, b, R, stud,
                 stud_in, magnet, medal, mark_w, mark_h, gap, line=1.2):
        self.L, self.Wt, self.Wb, self.H = L, Wt, Wb, H
        self.lap, self.end_tab = lap, end_tab
        self.board, self.wrap = board, wrap
        self.b, self.R, self.stud, self.stud_in = b, R, stud, stud_in
        self.magnet = magnet
        self.medal, self.mark_w, self.mark_h, self.gap = medal, mark_w, mark_h, gap
        self.line = line                     # debossed line width, mm

    @property
    def reveal(self):
        """What the lap leaves showing of the front wall."""
        return self.H - self.lap

    @property
    def rows(self):
        """The net, top to bottom: (height, name)."""
        return [(self.lap, 'lap'), (self.Wt, 'top'), (self.H, 'back'),
                (self.Wb, 'bottom'), (self.H, 'front')]

    @property
    def net_h(self):
        return sum(h for h, _ in self.rows)

    @property
    def run(self):
        """Where a debossed line meets a cap, measured along the edge."""
        return math.sqrt(max(0.0, self.R ** 2 - self.b ** 2))


# A cap always sits on a fold, because it wraps a real edge of the finished
# box. These are the corners each panel of the net carries one at.
CAPS_OF = {
    'lap': BOT2,        # the fold it shares with the top; free edge is clear
    'top': ALL4,
    'back': ALL4,
    'bottom': ALL4,
    'front': TOP2,      # the fold it shares with the bottom; top edge is clear
}

# The lap and the front wall meet each other, not a board edge, so neither
# frame closes on that side: the side lines run straight out to the free edge
# and together they read as one frame round the whole front of the shut box.
# Keys are net orientation -- in the net the lap's free edge is its top and
# the front wall's is its bottom.
OPEN_OF = {'lap': ('t',), 'front': ('b',)}


# ------------------------------------------------------------- primitives

def _arc(cx, cy, sx, sy, R, a0, a1, n=28):
    return [(cx + sx * R * math.cos(a0 + (a1 - a0) * i / n),
             cy + sy * R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _corner(w, h, key):
    cx = 0.0 if key[1] == 'l' else w
    cy = 0.0 if key[0] == 't' else h
    return cx, cy, (1 if key[1] == 'l' else -1), (1 if key[0] == 't' else -1)


def deboss(pg, x, y, w, h, b, R, which=ALL4, col=TOOL, width=None, open_edges=()):
    """The debossed frame.

    A run stops short only at a corner that has a cap. An edge named in
    `open_edges` carries no run at all, and the two runs meeting it carry
    straight on to the panel edge instead of turning -- which is how the lap
    and the front wall are marked up: their frames do not close against each
    other, the side lines simply run down the front of the shut box.
    """
    r = math.sqrt(max(0.0, R * R - b * b)) if R > b else 0.0

    def inx(key):
        return r if key in which else b

    t0 = 0.0 if 't' in open_edges else inx(TL)
    t1 = 0.0 if 't' in open_edges else inx(TR)
    b0 = 0.0 if 'b' in open_edges else inx(BL)
    b1 = 0.0 if 'b' in open_edges else inx(BR)
    l0 = 0.0 if 'l' in open_edges else inx(TL)
    l1 = 0.0 if 'l' in open_edges else inx(BL)
    r0 = 0.0 if 'r' in open_edges else inx(TR)
    r1 = 0.0 if 'r' in open_edges else inx(BR)

    segs = []
    if 't' not in open_edges:
        segs.append(((l0, b), (w - r0, b)))
    if 'r' not in open_edges:
        segs.append(((w - b, t1), (w - b, h - b1)))
    if 'b' not in open_edges:
        segs.append(((l1, h - b), (w - r1, h - b)))
    if 'l' not in open_edges:
        segs.append(((b, t0), (b, h - b0)))
    for p0, p1 in segs:
        if (p1[0] - p0[0]) + (p1[1] - p0[1]) <= 0.2:
            continue
        line(pg, (x + p0[0], y + p0[1]), (x + p1[0], y + p1[1]), width, col)


def caps(pg, x, y, w, h, R, which=ALL4, col=TOOL, width=None):
    """Quarter-round cap arcs, clipped to a face shallower than R."""
    for key in which:
        cx, cy, sx, sy = _corner(w, h, key)
        pts = [(px, py) for px, py in _arc(cx, cy, sx, sy, R, 0.0, math.pi / 2)
               if -0.01 <= px <= w + 0.01 and -0.01 <= py <= h + 0.01]
        if len(pts) > 1:
            pg.draw_polyline([pymupdf.Point(x + px, y + py) for px, py in pts],
                             color=col, width=width)


def studs(pg, x, y, w, h, inset, dia, which=ALL4, col=TOOL, width=None):
    for key in which:
        cx, cy, sx, sy = _corner(w, h, key)
        pg.draw_circle(pymupdf.Point(x + cx + sx * inset, y + cy + sy * inset),
                       dia / 2, color=col, fill=None, width=width)


def face(pg, x, y, fw, fh, c, k, which=ALL4, border=True, fill=LEATHER,
         tool=TOOL, width=None, open_edges=()):
    """One decorated exterior panel, fw x fh mm, top-left at (x, y).

    `width` is in POINTS. Left unset it becomes the box's real debossed line
    width at this drawing's scale, so a 1:1 sheet carries the true weight and
    a reduced sheet thins in proportion.
    """
    if width is None:
        width = c.line * k
    if fill:
        pg.draw_rect(pymupdf.Rect(x, y, x + fw * k, y + fh * k), color=None, fill=fill)
    if border:
        deboss(pg, x, y, fw * k, fh * k, c.b * k, c.R * k, which, tool, width,
               open_edges)
    if which:
        caps(pg, x, y, fw * k, fh * k, c.R * k, which, tool, width)
        studs(pg, x, y, fw * k, fh * k, c.stud_in * k, c.stud * k, which, tool,
              max(0.4, width * 0.8))


_LOGO_DOC = None


def _logo():
    """The client's lockup, opened once. None if the file is missing."""
    global _LOGO_DOC
    if _LOGO_DOC is None:
        try:
            _LOGO_DOC = pymupdf.open(LOGO_PDF)
        except Exception:
            _LOGO_DOC = False
    return _LOGO_DOC or None


_GOLD_CACHE = {}


def _gold_png(clip, rotate, col=GOLD, dpi=600):
    """The lockup's ink as a gold RGBA image, its paper transparent.

    The client's file is black on white. Placed straight onto a drawing of
    black leatherette the white page would show as a box, so for those sheets
    the ink is turned into an alpha channel and tinted foil gold.
    """
    key = (clip, rotate, col, dpi)
    if key in _GOLD_CACHE:
        return _GOLD_CACHE[key]
    src = _logo()
    if src is None:
        return None
    m = pymupdf.Matrix(dpi / 72.0, dpi / 72.0)
    if rotate % 360:
        m = m * pymupdf.Matrix(rotate % 360)
    pm = src[0].get_pixmap(matrix=m, clip=pymupdf.Rect(*clip), colorspace=pymupdf.csGRAY)
    g = bytearray(pm.samples)
    w, h = pm.width, pm.height
    out = bytearray(w * h * 4)
    r8, g8, b8 = (int(round(v * 255)) for v in col)
    for i in range(w * h):
        a = 255 - g[i]                       # ink opaque, paper clear
        j = i * 4
        out[j] = r8; out[j + 1] = g8; out[j + 2] = b8; out[j + 3] = a
    png = pymupdf.Pixmap(pymupdf.csRGB, w, h, bytes(out), True).tobytes('png')
    _GOLD_CACHE[key] = png
    return png


def _place(pg, rect, clip, rotate, gold=False):
    src = _logo()
    if src is None:
        pg.draw_rect(rect, color=GOLD, fill=None, width=0.7, dashes='[2.5 2] 0')
        return False
    if gold:
        png = _gold_png(clip, rotate)
        if png:
            pg.insert_image(rect, stream=png, keep_proportion=True)
            return True
    pg.show_pdf_page(rect, src, 0, clip=pymupdf.Rect(*clip), rotate=rotate)
    return True


def mark(pg, cx, cy, c, k, rotate=0, gold=False):
    """Place the client's foil lockup centred on (cx, cy).

    Measured off the sample: the medallion sits toward the BACK of the lid
    and the wordmark toward the FRONT, so in a view whose front edge is at
    the bottom the medallion is uppermost. Pass rotate=180 for a drawing
    whose front edge is at the top -- the net -- where the whole lockup
    turns with it and the wordmark lands uppermost on the page.

    Returns (medallion rect, wordmark rect) in page points.
    """
    mw = c.medal * k
    ww = c.mark_w * k
    wh = ww * (WORD_CLIP[3] - WORD_CLIP[1]) / (WORD_CLIP[2] - WORD_CLIP[0])
    tot = mw + c.gap * k + wh
    top = cy - tot / 2
    if rotate % 360 == 180:
        word = pymupdf.Rect(cx - ww / 2, top, cx + ww / 2, top + wh)
        medal = pymupdf.Rect(cx - mw / 2, top + wh + c.gap * k, cx + mw / 2, top + tot)
    else:
        medal = pymupdf.Rect(cx - mw / 2, top, cx + mw / 2, top + mw)
        word = pymupdf.Rect(cx - ww / 2, top + mw + c.gap * k, cx + ww / 2, top + tot)
    _place(pg, medal, MEDAL_CLIP, rotate, gold)
    _place(pg, word, WORD_CLIP, rotate, gold)
    return medal, word


def _front_edge(pg, x, y, w, col=LAPL, side='right'):
    """Mark which edge of a plan view faces the front of the box."""
    line(pg, (x, y - 1.4 * MM), (x + w, y - 1.4 * MM), 1.4, col)
    tx = x + w - 18 * MM if side == 'right' else x + 2 * MM
    pg.insert_text(pymupdf.Point(tx, y + 1.4 * MM), 'FRONT EDGE',
                   fontname='Helvetica-Bold', fontsize=6, color=col)


def magnets(pg, x, y, w, k, c, col=CUT):
    """The catch pair, centred on the lap's free edge."""
    for sx in (-1, 1):
        pg.draw_circle(pymupdf.Point(x + w * k / 2 + sx * c.magnet / 2 * k, y),
                       2.0 * MM, color=col, fill=None, width=0.6)


def legend(pg, x, y, size=6.6):
    """The colour key. Gold only appears while there is a foil mark."""
    items = ([('cut', CUT), ('fold', FOLDC), ('blind deboss, cap, stud', TOOL)]
             + ([('hot foil', GOLD)] if SHOW_LOGO else [])
             + [('where the lap closes', LAPL)])
    for lab, col in items:
        pg.draw_line(pymupdf.Point(x, y), pymupdf.Point(x + 7 * MM, y),
                     color=col, width=1.4)
        pg.insert_text(pymupdf.Point(x + 8.5 * MM, y + 0.8 * MM), lab,
                       fontname='Helvetica', fontsize=size, color=(0.2, 0.2, 0.2))
        x += 8.5 * MM + pymupdf.get_text_length(lab, 'Helvetica', size) + 11 * MM


# ------------------------------------------------------------------ sheets

def _page(doc, land=True):
    return doc.new_page(width=842 if land else 595, height=595 if land else 842)


def sheet_ga(doc, c, s):
    """General arrangement: the three faces a buyer sees, shut."""
    k = s * MM
    pg = _page(doc)
    title(pg, 24 * MM, 20 * MM, 'Trunk box — general arrangement',
          f'shut {c.L:g} x {c.Wt:g} x {c.H:g} mm · scale 1:{1 / s:g} · '
          'exterior only · all dimensions mm')

    x0, y0 = 30 * MM, 56 * MM

    # --- front elevation: the lap hanging over the front wall -------------
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM),
                   'front — the lap hangs over the front wall',
                   fontname='Helvetica', fontsize=7, color=GREY)
    face(pg, x0, y0, c.L, c.H, c, k, which=BOT2, border=True,
         open_edges=('t',))                                         # front wall
    yl = y0 + c.lap * k
    face(pg, x0, y0, c.L, c.lap, c, k, which=TOP2, border=True,
         open_edges=('b',))                                         # lap over it
    line(pg, (x0, yl), (x0 + c.L * k, yl), 1.1, LAPL)
    magnets(pg, x0, yl - 1.6 * MM, c.L, k, c)
    dim_h(pg, x0, x0 + c.L * k, y0 + c.H * k + 11 * MM, f'{c.L:g}')
    dim_v(pg, y0, yl, x0 + c.L * k + 8 * MM, f'{c.lap:g} lap', anchor='right')
    dim_v(pg, yl, y0 + c.H * k, x0 + c.L * k + 8 * MM,
          f'{c.reveal:g} showing', anchor='right')
    dim_v(pg, y0, y0 + c.H * k, x0 - 12 * MM, f'{c.H:g}', anchor='left')

    # --- end elevation ----------------------------------------------------
    x2 = x0 + c.L * k + 48 * MM
    pg.insert_text(pymupdf.Point(x2, y0 - 4 * MM), 'end — one panel, unbroken',
                   fontname='Helvetica', fontsize=7, color=GREY)
    face(pg, x2, y0, c.Wb, c.H, c, k, which=ALL4, border=True)
    dim_h(pg, x2, x2 + c.Wb * k, y0 + c.H * k + 11 * MM, f'{c.Wb:g}')

    # --- plan: the lid top with the foil ----------------------------------
    y3 = y0 + c.H * k + 30 * MM
    pg.insert_text(pymupdf.Point(x0, y3 - 4 * MM),
                   f'lid top {c.L:g} x {c.Wt:g} — four caps, '
                   'front edge at the bottom',
                   fontname='Helvetica', fontsize=7, color=GREY)
    face(pg, x0, y3, c.L, c.Wt, c, k, which=ALL4, border=True)
    if SHOW_LOGO:
        mark(pg, x0 + c.L * k / 2, y3 + c.Wt * k / 2, c, k, gold=True)
    _front_edge(pg, x0, y3 + c.Wt * k + 3.2 * MM, c.L * k)
    dim_h(pg, x0, x0 + c.L * k, y3 + c.Wt * k + 11 * MM, f'{c.L:g}')
    dim_v(pg, y3, y3 + c.Wt * k, x0 - 12 * MM, f'{c.Wt:g}', anchor='left')

    note(pg, x2, y3 + 2 * MM, [
        'Eight corner caps, one at each end of all four long folds.',
        'The two front-bottom caps are mostly hidden: only the lowest',
        f'{c.reveal:g} of each shows below the lap on a shut box. The lap\'s own',
        'free edge carries no cap.',
        '',
        f'Magnetic catch: pair at {c.magnet:g} centres, behind the lap\'s free',
        'edge, catching the front wall.',
        '',
        f'The lid overhangs the front by {c.Wt - c.Wb:g} — a {c.Wt:g} top over a {c.Wb:g}',
        'bottom — which is the front wall plus the lap.',
    ], bold_first=True)
    return pg


def sheet_parts(doc, c, s):
    """The parts drawn apart, so the split is unmistakable."""
    k = s * MM
    pg = _page(doc)
    title(pg, 24 * MM, 20 * MM, 'Trunk box — how it opens',
          f'the parts drawn apart · scale 1:{1 / s:g}')

    x0, y = 34 * MM, 54 * MM
    steps = [
        ('1 · LAP', c.L, c.lap, TOP2, ('b',),
         f'{c.L:g} x {c.lap:g}, hinged on the top\'s front edge. Lift it first — the '
         f'catch is in its free edge. Shut, it leaves {c.reveal:g} of the front showing. '
         'The frame does not close at the bottom: the side lines run straight out.'),
        ('2 · LID TOP', c.L, c.Wt, ALL4, (),
         f'{c.L:g} x {c.Wt:g}, hinged on the top/back fold. Swings back, and the lap '
         'folds back with it.' + (' Carries the foil.' if SHOW_LOGO else '')),
        ('3 · FRONT WALL', c.L, c.H, BOT2, ('t',),
         f'{c.L:g} x {c.H:g}, hinged on the bottom\'s front edge. Drops forward once '
         'the lap is clear. Open at the top, so its side lines carry on from the lap\'s.'),
    ]
    for lab, fw, fh, which, opens, text in steps:
        pg.insert_text(pymupdf.Point(x0, y - 4 * MM), f'{lab} — {text}',
                       fontname='Helvetica-Bold', fontsize=7.2, color=(0, 0, 0))
        face(pg, x0, y, fw, fh, c, k, which=which, border=True, open_edges=opens)
        if lab.endswith('LID TOP'):
            if SHOW_LOGO:
                mark(pg, x0 + fw * k / 2, y + fh * k / 2, c, k, gold=True)
            _front_edge(pg, x0, y + fh * k + 3.2 * MM, fw * k)
        if lab.endswith('LAP'):
            magnets(pg, x0, y + fh * k + 1.6 * MM, fw, k, c)
            pg.insert_text(pymupdf.Point(x0 + fw * k + 4 * MM, y + fh * k + 2.5 * MM),
                           f'catch, {c.magnet:g} centres', fontname='Helvetica',
                           fontsize=6, color=CUT)
        dim_v(pg, y, y + fh * k, x0 - 11 * MM, f'{fh:g}', anchor='left')
        y += fh * k + 18 * MM

    pg.insert_text(pymupdf.Point(x0, y - 4 * MM),
                   f'4 · BASE — bottom {c.L:g} x {c.Wb:g}, back {c.L:g} x {c.H:g}, '
                   f'two ends {c.Wb:g} x {c.H:g}. Fixed.',
                   fontname='Helvetica-Bold', fontsize=7.2, color=(0, 0, 0))
    bx = x0
    for fw, fh, lab in ((c.Wb, c.H, 'end'), (c.L, c.H, 'back'), (c.Wb, c.H, 'end')):
        face(pg, bx, y, fw, fh, c, k, which=ALL4, border=True)
        pg.insert_text(pymupdf.Point(bx + 2 * MM, y + fh * k + 4 * MM), lab,
                       fontname='Helvetica', fontsize=6, color=GREY)
        bx += fw * k + 5 * MM
    face(pg, bx, y, c.L, c.Wb, c, k, which=ALL4, border=True)
    pg.insert_text(pymupdf.Point(bx + 2 * MM, y + c.Wb * k + 4 * MM), 'bottom',
                   fontname='Helvetica', fontsize=6, color=GREY)
    return pg


def sheet_detail(doc, c):
    """One corner at 2:1, with the geometry that fixes the cap and the line."""
    k = 2.0 * MM
    pg = _page(doc, land=False)
    title(pg, 24 * MM, 20 * MM, 'Corner detail',
          'scale 2:1 · the debossed line stops where the cap arc crosses it')

    fw, fh = 46.0, 40.0
    x0, y0 = 40 * MM, 58 * MM
    face(pg, x0, y0, fw, fh, c, k, which=(TL,), border=True, width=0.9)

    r = c.run
    witness(pg, (x0, y0 + c.b * k), (x0 - 10 * MM, y0 + c.b * k))
    dim_v(pg, y0, y0 + c.b * k, x0 - 8 * MM, f'{c.b:g}', anchor='left')
    witness(pg, (x0 + r * k, y0), (x0 + r * k, y0 - 10 * MM))
    dim_h(pg, x0, x0 + r * k, y0 - 8 * MM, f'{r:.1f}')
    witness(pg, (x0 + c.R * k, y0), (x0 + c.R * k, y0 - 18 * MM))
    dim_h(pg, x0, x0 + c.R * k, y0 - 16 * MM, f'R{c.R:g} cap reach')
    sx, sy = x0 + c.stud_in * k, y0 + c.stud_in * k
    witness(pg, (sx, sy), (sx, y0 - 4 * MM))
    dim_h(pg, x0, sx, y0 + 15 * MM, f'{c.stud_in:g}')
    dim_v(pg, y0, sy, x0 + 17 * MM, f'{c.stud_in:g}', anchor='right')

    note(pg, 40 * MM, y0 + fh * k + 22 * MM, [
        'Cap: a quarter-round struck from the corner, worked in the wrap.',
        f'Radius {c.R:g}. Domed stud {c.stud:g} dia, centre {c.stud_in:g} in from both edges.',
        f'Debossed line {c.b:g} in from the edge, {c.line:g} wide, blind — no colour.',
        f'The straight run ends at sqrt({c.R:g}^2 - {c.b:g}^2) = {r:.1f} from the corner,',
        'where the arc crosses it. The two marks meet; neither crosses.',
        '',
        'A cap always sits on a fold, because it wraps a real edge of the',
        'finished box: eight corners, both ends of each of the four long',
        'folds. So the lap carries caps on the fold it shares with the top',
        'and none on its free edge, and the front wall carries caps on the',
        'fold it shares with the bottom and none on its top edge.',
        '',
        'Nor does either frame close on that side. The two side runs carry',
        'straight out to the free edge, so a shut box shows one frame down',
        'the whole front instead of two frames meeting.',
    ], bold_first=True)
    return pg


def sheet_net(doc, c, s, preview=False):
    """The client's net, dimensioned and decorated. One piece."""
    k = s * MM
    pg = doc.new_page(width=1191, height=842)        # A3 landscape
    if preview:
        title(pg, 30 * MM, 24 * MM,
              'Trunk box — how the finished piece reads',
              'the same artwork on black leatherette, blind deboss · '
              'visual reference, not the production file')
    else:
        title(pg, 30 * MM, 24 * MM,
              'Trunk box — the net, printing and tooling',
              f'{c.L:g} wide x {c.net_h:g} over five rows · scale 1:{1 / s:.1f} · '
              'magenta = cut · blue dashed = fold · grey = blind deboss'
              + (' · gold = foil' if SHOW_LOGO else ''))

    ox = NET_OX * MM + (c.H + c.end_tab) * k
    oy = NET_OY * MM

    def P(mx, my):
        return (ox + mx * k, oy + my * k)

    ys, acc = {}, 0.0
    for h, n in c.rows:
        ys[n] = acc
        acc += h
    yb = ys['bottom']

    # --- the two end walls, hung off the bottom row -----------------------
    for ex, which, tx in ((-c.H, RIGHT2, -c.H - c.end_tab), (c.L, LEFT2, c.L + c.H)):
        if c.end_tab > 0:
            pg.draw_rect(pymupdf.Rect(*P(tx, yb), *P(tx + c.end_tab, yb + c.Wb)),
                         color=CUT, fill=(0.92, 0.92, 0.94), width=0.6,
                         dashes='[2 2] 0')
            pg.insert_text(pymupdf.Point(*P(tx + 2, yb + c.Wb / 2)), 'tab',
                           fontname='Helvetica', fontsize=5.5, color=GREY)
        face(pg, *P(ex, yb), c.H, c.Wb, c, k, which=ALL4, border=True)
        pg.insert_text(pymupdf.Point(*P(ex + 3, yb + 9)), 'END WALL',
                       fontname='Helvetica-Bold', fontsize=6.5, color=(1, 1, 1))
        if not preview:
            pg.insert_text(pymupdf.Point(*P(ex + 3, yb + 15)), f'{c.H:g} x {c.Wb:g}',
                           fontname='Helvetica', fontsize=5.5, color=(1, 1, 1))

    # --- the five rows ----------------------------------------------------
    for h, n in c.rows:
        face(pg, *P(0, ys[n]), c.L, h, c, k, which=CAPS_OF[n], border=True,
             open_edges=OPEN_OF.get(n, ()))
    if SHOW_LOGO:
        mc = P(c.L / 2, ys['top'] + c.Wt / 2)
        mark(pg, mc[0], mc[1], c, k, rotate=180, gold=True)
    magnets(pg, P(0, 1.6)[0], P(0, 1.6)[1], c.L, k, c)

    if preview:
        labels = {'lap': 'LAP', 'top': 'LID TOP', 'back': 'BACK',
                  'bottom': 'BOTTOM', 'front': 'FRONT WALL'}
    else:
        labels = {
            'lap': f'LAP  {c.L:g} x {c.lap:g}  —  catch in the free edge, no cap there',
            'top': f'LID TOP  {c.L:g} x {c.Wt:g}  —  '
                   'the fold to the lap is the FRONT edge',
            'back': f'BACK  {c.L:g} x {c.H:g}',
            'bottom': f'BOTTOM  {c.L:g} x {c.Wb:g}',
            'front': f'FRONT  {c.L:g} x {c.H:g}  —  drops forward',
        }
    for h, n in c.rows:
        pg.insert_text(pymupdf.Point(*P(4, ys[n] + 9)), labels[n],
                       fontname='Helvetica-Bold', fontsize=7, color=(1, 1, 1))

    # where the lap closes to on the front wall
    yr = ys['front'] + c.lap
    line(pg, P(0, yr), P(c.L, yr), 0.9, LAPL, '[4 2.5] 0')
    pg.insert_text(pymupdf.Point(*P(c.L - 76, yr - 2.5)),
                   'the lap closes to here'
                   + ('' if preview else f' — {c.reveal:g} of the front shows below it'),
                   fontname='Helvetica', fontsize=5.8, color=LAPL)

    # --- silhouette, folds, dimensions ------------------------------------
    sil = [P(0, 0), P(c.L, 0), P(c.L, yb), P(c.L + c.H + c.end_tab, yb),
           P(c.L + c.H + c.end_tab, yb + c.Wb), P(c.L, yb + c.Wb),
           P(c.L, c.net_h), P(0, c.net_h), P(0, yb + c.Wb),
           P(-c.H - c.end_tab, yb + c.Wb), P(-c.H - c.end_tab, yb), P(0, yb)]
    pg.draw_polyline([pymupdf.Point(*q) for q in sil], color=CUT, width=1.4,
                     closePath=True)
    acc = 0.0
    for h, _ in c.rows[:-1]:
        acc += h
        line(pg, P(0, acc), P(c.L, acc), 1.1, FOLDC, '[3 2] 0')
    for xx in (0.0, c.L):
        line(pg, P(xx, yb), P(xx, yb + c.Wb), 1.1, FOLDC, '[3 2] 0')
    if c.end_tab > 0:
        for xx in (-c.H, c.L + c.H):
            line(pg, P(xx, yb), P(xx, yb + c.Wb), 0.8, FOLDC, '[2 2] 0')

    if not preview:
        dim_h(pg, P(0, 0)[0], P(c.L, 0)[0], P(0, 0)[1] - 11 * MM, f'{c.L:g}')
        xd = P(-c.H - c.end_tab, 0)[0] - 12 * MM
        for h, n in c.rows:
            dim_v(pg, P(0, ys[n])[1], P(0, ys[n] + h)[1], xd, f'{h:g}  {n}',
                  anchor='left')
        dim_v(pg, P(0, 0)[1], P(0, c.net_h)[1], xd - 30 * MM, f'{c.net_h:g}',
              anchor='left')
        ye = P(0, yb + c.Wb)[1] + 10 * MM
        dim_h(pg, P(-c.H, yb)[0], P(0, yb)[0], ye, f'{c.H:g}')
        dim_h(pg, P(c.L, yb)[0], P(c.L + c.H, yb)[0], ye, f'{c.H:g}')

    if preview:
        return pg
    note(pg, 30 * MM, P(0, c.net_h)[1] + 32 * MM, [
        'One piece. Lap down over the front, top over from the back, back '
        'and front up off the bottom, end walls up off the bottom row. '
        'The end walls butt the back and the front; no glue tab.',
        'Every corner cap sits on a fold, because it wraps a real edge — '
        'eight corners, both ends of each of the four long folds.',
        'The lap has no cap on its free edge and the front wall none on its '
        'top edge; those two meet each other, not a board edge. Neither frame '
        'closes there either: the side lines run straight out to the free edge, '
        'so the shut box shows one frame down the whole front.',
        f'Allow {c.wrap:g} turn-in on every raw edge, not drawn. Board {c.board:g}.',
        f'Blind deboss {c.b:g} in from each panel edge, {c.line:g} wide, each run '
        f'stopping {c.run:.1f} from the corner where the cap arc meets it.',
    ], lead=4.6 * MM)
    return pg


def sheet_art_net(doc, c):
    """THE artwork file: the whole model opened out, 1:1, as line work.

    One page, no panel-by-panel sheets. White ground, because this is what
    the tooler and the foil shop work from: cut, fold, deboss, cap, stud and
    foil, each on its own colour, every one of them at full size.
    """
    k = MM
    mx, top = ART_MX, ART_TOP                 # margins, mm
    span_x = c.L + 2 * (c.H + c.end_tab)
    pw = (span_x + 2 * mx) * MM
    ph = (c.net_h + top + mx) * MM
    pg = doc.new_page(width=pw, height=ph)

    title(pg, mx * MM, 15 * MM, 'Trunk box — artwork, opened out',
          'one piece · sizes and tolerances on the production sheets')
    # Nothing on this sheet is dimensioned, not even the scale. It is a
    # print and tooling file drawn at full size: the geometry IS the
    # specification. Sizes, the catch and the tolerances live on the
    # production sheets.
    legend(pg, mx * MM, 25 * MM)

    ox = (mx + c.H + c.end_tab) * MM
    oy = top * MM

    def P(fx, fy):
        return (ox + fx * k, oy + fy * k)

    ys, acc = {}, 0.0
    for h, n in c.rows:
        ys[n] = acc
        acc += h
    yb = ys['bottom']

    # --- end walls and their glue tabs ------------------------------------
    for ex, tx in ((-c.H, -c.H - c.end_tab), (c.L, c.L + c.H)):
        if c.end_tab > 0:
            pg.insert_text(pymupdf.Point(*P(tx + 2.5, yb + c.Wb / 2)), 'glue tab',
                           fontname='Helvetica', fontsize=5.5, color=GREY)
        face(pg, *P(ex, yb), c.H, c.Wb, c, k, which=ALL4, border=True, fill=None)
        pg.insert_text(pymupdf.Point(*P(ex + 11, yb + c.Wb / 2 + 2)), 'END WALL',
                       fontname='Helvetica-Bold', fontsize=6.5, color=(0.25, 0.25, 0.25))

    # --- the five rows ----------------------------------------------------
    for h, n in c.rows:
        face(pg, *P(0, ys[n]), c.L, h, c, k, which=CAPS_OF[n], border=True,
             fill=None, open_edges=OPEN_OF.get(n, ()))

    # --- foil, on the lid top, wordmark toward the lap --------------------
    if SHOW_LOGO:
        mcx, mcy = P(c.L / 2, ys['top'] + c.Wt / 2)
        medal, word = mark(pg, mcx, mcy, c, k, rotate=180)
        pg.insert_text(pymupdf.Point(word.x1 + 4 * MM, word.y1 - 1 * MM),
                       '1  wordmark - logo', fontname='Helvetica',
                       fontsize=6.2, color=GOLD)
        pg.insert_text(pymupdf.Point(medal.x1 + 4 * MM, medal.y1 - 1 * MM),
                       '2  medallion - logo', fontname='Helvetica',
                       fontsize=6.2, color=GOLD)
        for r in (word, medal):
            pg.draw_rect(r, color=GOLD, fill=None, width=0.5, dashes='[2 2] 0')

    # --- panel names ------------------------------------------------------
    labels = {
        'lap': 'LAP   free edge above — no cap, no frame there',
        'top': 'LID TOP',
        'back': 'BACK',
        'bottom': 'BOTTOM',
        'front': 'FRONT WALL   free edge below — frame open there',
    }
    for h, n in c.rows:
        pg.insert_text(pymupdf.Point(*P(c.R + 5, ys[n] + 11)), labels[n],
                       fontname='Helvetica-Bold', fontsize=6.8,
                       color=(0.25, 0.25, 0.25))

    _front_edge(pg, *P(0, ys['top'] + 3.0), c.L * k, side='left')

    # The catch, on the lap's free edge. Here too, not only on the finish
    # reference beside it, so the two halves of the sheet agree; the
    # production sheet is where it is dimensioned.
    magnets(pg, *P(0, 1.6), c.L, k, c)

    # --- where the lap closes on the front wall ---------------------------
    yr = ys['front'] + c.lap
    line(pg, P(0, yr), P(c.L, yr), 0.9, LAPL, '[4 2.5] 0')
    pg.insert_text(pymupdf.Point(*P(c.L - 76, yr - 3)),
                   'the lap closes to here — the front wall shows below it',
                   fontname='Helvetica', fontsize=6.2, color=LAPL)

    # --- cut silhouette and folds -----------------------------------------
    sil = [P(0, 0), P(c.L, 0), P(c.L, yb), P(c.L + c.H + c.end_tab, yb),
           P(c.L + c.H + c.end_tab, yb + c.Wb), P(c.L, yb + c.Wb),
           P(c.L, c.net_h), P(0, c.net_h), P(0, yb + c.Wb),
           P(-c.H - c.end_tab, yb + c.Wb), P(-c.H - c.end_tab, yb), P(0, yb)]
    pg.draw_polyline([pymupdf.Point(*q) for q in sil], color=CUT, width=1.4,
                     closePath=True)
    acc = 0.0
    for h, _ in c.rows[:-1]:
        acc += h
        line(pg, P(0, acc), P(c.L, acc), 1.0, FOLDC, '[3 2] 0')
    for xx in (0.0, c.L):
        line(pg, P(xx, yb), P(xx, yb + c.Wb), 1.0, FOLDC, '[3 2] 0')
    if c.end_tab > 0:
        for xx in (-c.H, c.L + c.H):
            line(pg, P(xx, yb), P(xx, yb + c.Wb), 0.7, FOLDC, '[2 2] 0')

    # No dimensions here by design — see the production sheets.


    return pg


# -------------------------------------------------------------------- main

def _net_clip(ox, oy, k, c, pad=(4.0, 5.0, 4.0, 4.0)):
    """The net's own bounding box on a sheet, with a margin in net mm.

    Anchored to the net rather than to whatever happens to be drawn. That
    is what lets the fused sheet line the two halves up: a content box
    would follow the magnet circles on one sheet and the frame on the
    other, and the rows would sit at two different heights.
    pad is left, top, right, bottom.
    """
    l, t, r, b = pad
    return pymupdf.Rect(ox - (c.H + c.end_tab + l) * k, oy - t * k,
                        ox + (c.L + c.H + c.end_tab + r) * k,
                        oy + (c.net_h + b) * k)


def sheet_fused(doc, c):
    """Line work and the leatherette reading, side by side at full size.

    They were two sheets at two scales, which made them awkward to
    compare. Both go down here at 1:1 — the preview is laid out at 2:3,
    so it is placed at 1.5x — which puts the same panel at the same
    height in both halves, to the millimetre.
    """
    tmp = pymupdf.open()
    sheet_art_net(tmp, c)
    s = 2.0 / 3.0
    sheet_net(tmp, c, s, preview=True)
    r1 = _net_clip((ART_MX + c.H + c.end_tab) * MM, ART_TOP * MM, MM, c)
    r2 = _net_clip(NET_OX * MM + (c.H + c.end_tab) * s * MM, NET_OY * MM,
                   s * MM, c)

    mx, top, gap, bot = 20 * MM, 44 * MM, 26 * MM, 20 * MM
    w, h = r1.width, r1.height                 # r2 scales to the same size
    pw = mx * 2 + w * 2 + gap
    ph = top + h + bot

    pg = doc.new_page(width=pw, height=ph)
    title(pg, mx, 16 * MM, 'Trunk box · artwork and finish, opened out',
          'one piece, drawn at full size · left: cut, fold and tooling · '
          'right: how it reads on black leatherette')
    legend(pg, mx, 28 * MM)

    x2 = mx + w + gap
    pg.show_pdf_page(pymupdf.Rect(mx, top, mx + w, top + h), tmp, 0, clip=r1)
    pg.show_pdf_page(pymupdf.Rect(x2, top, x2 + w, top + h), tmp, 1, clip=r2)

    for x, lab in ((mx, 'CUT, FOLD AND TOOLING'),
                   (x2, 'FINISH REFERENCE')):
        pg.insert_text(pymupdf.Point(x, top - 6 * MM), lab,
                       fontname='Helvetica-Bold', fontsize=8,
                       color=(0.25, 0.25, 0.25))
    tmp.close()
    return pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='assets/traxnyc-box')
    ap.add_argument('--L', type=float, default=170.0, help='net column width')
    ap.add_argument('--Wt', type=float, default=70.0, help='net row 2, the top')
    ap.add_argument('--Wb', type=float, default=65.0, help='net row 4, the bottom')
    ap.add_argument('--H', type=float, default=55.0, help='net rows 3 and 5')
    ap.add_argument('--lap', type=float, default=40.0, help='net row 1')
    ap.add_argument('--end-tab', type=float, default=0.0,
                help='glue tab beyond each end wall; 0 for none')
    ap.add_argument('--board', type=float, default=2.0)
    ap.add_argument('--wrap', type=float, default=15.0)
    ap.add_argument('--border', type=float, default=6.0, help='deboss inset')
    ap.add_argument('--line', type=float, default=1.2,
                    help='debossed line width, mm')
    ap.add_argument('--cap', type=float, default=20.0, help='cap reach')
    ap.add_argument('--stud', type=float, default=3.5)
    ap.add_argument('--stud-in', type=float, default=9.0)
    ap.add_argument('--magnet', type=float, default=40.0)
    ap.add_argument('--medal', type=float, default=36.0)
    ap.add_argument('--mark-w', type=float, default=53.0)
    ap.add_argument('--mark-h', type=float, default=7.8)
    ap.add_argument('--gap', type=float, default=3.0)
    a = ap.parse_args()

    c = Box(a.L, a.Wt, a.Wb, a.H, a.lap, a.end_tab, a.board, a.wrap, a.border,
            a.cap, a.stud, a.stud_in, a.magnet, a.medal, a.mark_w, a.mark_h,
            a.gap, a.line)
    if c.reveal <= 0:
        sys.exit(f'lap {c.lap} is not shorter than the front wall {c.H}')

    os.makedirs(a.out, exist_ok=True)

    prod = pymupdf.open()
    sheet_ga(prod, c, 0.5)
    sheet_parts(prod, c, 0.5)
    sheet_detail(prod, c)
    sheet_net(prod, c, 2.0 / 3.0)
    p1 = os.path.join(a.out, 'box-production.pdf')
    prod.save(p1)

    art = pymupdf.open()
    sheet_fused(art, c)
    p2 = os.path.join(a.out, 'box-artwork.pdf')
    art.save(p2)

    print(f'{p1}  {prod.page_count} sheets')
    print(f'{p2}  {art.page_count} sheet, {(c.L + 2 * (c.H + c.end_tab)):g} x {c.net_h:g} at 1:1')
    print(f'net {c.L:g} x {c.net_h:g}  rows ' +
          ' / '.join(f'{h:g} {n}' for h, n in c.rows))
    print(f'lap {c.lap:g} over a {c.H:g} front leaves {c.reveal:g} showing; '
          f'cap run {c.run:.2f}')


if __name__ == '__main__':
    main()
