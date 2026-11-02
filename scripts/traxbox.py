#!/usr/bin/env python3
"""Exterior drawings and stamping artwork for the TRAXNYC trunk box.

A rigid board carcass wrapped in black leatherette, tooled in the trunk
manner: a quarter-round cap worked into each corner of each face with a
domed stud in it, and a blind-debossed line inside the caps. Gold foil on
the lid top. Exterior only -- nothing here about fittings or lining.

The debossed line stops at the cap and does not go round it. An arc of
radius R struck from the corner crosses a line inset b from the edge at
sqrt(R^2 - b^2) along that edge, so the straight run ends there and the two
marks meet without one crossing the other. With R 22 and b 7 that is 20.9
from each corner, which is what fixes the length of every run.

The box opens on a flap. The bottom band stays put and the shell above it
lifts, its front face dropping forward, held shut by a magnetic catch. So
the only line on the outside is where the band ends -- it runs across the
front and returns along both ends, and the back has none because that is
the hinge.

The cap radius is tied to that band. At R20 a cap reaches exactly 20 along
each edge, so on the front and the ends the lower caps finish on the band
line instead of straddling it, and nothing on the outside crosses the
opening. The cap radius is therefore not free: it is the band height.
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

# face corners as (at the far x?, at the far y?, x sign, y sign)
CORNERS = [(0, 0, 1, 1), (1, 0, -1, 1), (1, 1, -1, -1), (0, 1, 1, -1)]


class Box:
    def __init__(self, L, W, H, band, board, wrap, b, R, stud, stud_in,
                 magnet, medal, mark_w, mark_h, gap):
        self.L, self.W, self.H, self.band = L, W, H, band
        self.board, self.wrap = board, wrap
        self.b, self.R, self.stud, self.stud_in = b, R, stud, stud_in
        self.magnet = magnet
        self.medal, self.mark_w, self.mark_h, self.gap = medal, mark_w, mark_h, gap
        self.flap = H - band

    @property
    def run(self):
        """Where the debossed line meets the cap, measured along the edge."""
        return math.sqrt(self.R ** 2 - self.b ** 2)


def _arc(cx, cy, sx, sy, R, a0, a1, n=28):
    return [(cx + sx * R * math.cos(a0 + (a1 - a0) * i / n),
             cy + sy * R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def deboss(pg, x, y, w, h, b, R, col=TOOL, width=0.7):
    """Four straight runs, each stopping where the cap arc crosses it."""
    if R <= b:
        return
    r = math.sqrt(R * R - b * b)
    for p0, p1 in (((r, b), (w - r, b)), ((w - b, r), (w - b, h - r)),
                   ((r, h - b), (w - r, h - b)), ((b, r), (b, h - r))):
        if (p1[0] - p0[0]) + (p1[1] - p0[1]) <= 0:
            continue                       # the face is too small for a run
        line(pg, (x + p0[0], y + p0[1]), (x + p1[0], y + p1[1]), width, col)


def caps(pg, x, y, w, h, R, col=TOOL, width=0.7):
    for fx, fy, sx, sy in CORNERS:
        cx, cy = (w if fx else 0), (h if fy else 0)
        pg.draw_polyline([pymupdf.Point(x + px, y + py) for px, py in
                          _arc(cx, cy, sx, sy, R, 0.0, math.pi / 2)],
                         color=col, width=width)


def studs(pg, x, y, w, h, inset, dia, col=TOOL, width=0.6):
    for fx, fy, sx, sy in CORNERS:
        cx, cy = (w if fx else 0), (h if fy else 0)
        pg.draw_circle(pymupdf.Point(x + cx + sx * inset, y + cy + sy * inset),
                       dia / 2, color=col, fill=None, width=width)


def face(pg, x, y, fw, fh, c, k, fill=LEATHER, tool=TOOL, width=0.7):
    if fill:
        pg.draw_rect(pymupdf.Rect(x, y, x + fw * k, y + fh * k), color=None, fill=fill)
    deboss(pg, x, y, fw * k, fh * k, c.b * k, c.R * k, tool, width)
    caps(pg, x, y, fw * k, fh * k, c.R * k, tool, width)
    studs(pg, x, y, fw * k, fh * k, c.stud_in * k, c.stud * k, tool)


def mark(pg, cx, cy, c, k, col=GOLD, solid=True):
    mh, mw = c.medal * k, c.mark_w * k
    tot = mh + c.gap * k + c.mark_h * k
    top = cy - tot / 2
    a = pymupdf.Rect(cx - mh / 2, top, cx + mh / 2, top + mh)
    b = pymupdf.Rect(cx - mw / 2, top + mh + c.gap * k, cx + mw / 2, top + tot)
    for r in (a, b):
        pg.draw_rect(r, color=col, fill=col if solid else None, width=0.7,
                     dashes=None if solid else '[2.5 2] 0')
    return a, b


def band_line(pg, x, y, fw, fh, c, k, col=(1, 1, 1), w=0.9):
    """Where the bottom band ends and the opening shell begins."""
    yy = y + (fh - c.band) * k
    line(pg, (x, yy), (x + fw * k, yy), w, col)


# ---------------------------------------------------------------- sheets

def sheet_ga(doc, c, s):
    k = s * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box · exterior',
          f'{c.L:g} x {c.W:g} x {c.H:g} mm closed.  drawing at 1:{1/s:g}')
    x0, y0 = 24 * MM, 46 * MM

    face(pg, x0, y0, c.L, c.W, c, k)
    mark(pg, x0 + c.L * k / 2, y0 + c.W * k / 2, c, k)
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM), 'top · gold foil',
                   fontname='Helvetica', fontsize=7)
    for xv in (0, c.L):
        witness(pg, (x0 + xv * k, y0 + c.W * k), (x0 + xv * k, y0 + c.W * k + 13 * MM))
    dim_h(pg, x0, x0 + c.L * k, y0 + c.W * k + 8 * MM, f'{c.L:g}')
    for yv in (0, c.W):
        witness(pg, (x0, y0 + yv * k), (x0 - 13 * MM, y0 + yv * k))
    dim_v(pg, y0, y0 + c.W * k, x0 - 8 * MM, f'{c.W:g}')

    y1 = y0 + c.W * k + 28 * MM
    face(pg, x0, y1, c.L, c.H, c, k)
    band_line(pg, x0, y1, c.L, c.H, c, k)
    mx = x0 + c.L * k / 2
    pg.draw_rect(pymupdf.Rect(mx - c.magnet * k / 2, y1 + 10 * k,
                              mx + c.magnet * k / 2, y1 + 13 * k),
                 color=HID, fill=None, width=0.5, dashes='[2 1.6] 0')
    pg.insert_text(pymupdf.Point(mx + c.magnet * k / 2 + 2 * MM, y1 + 12.5 * k),
                   f'magnetic catch {c.magnet:g}, behind the flap edge',
                   fontname='Helvetica', fontsize=6.5, color=HID)
    pg.insert_text(pymupdf.Point(x0, y1 - 4 * MM),
                   'front · the flap drops forward from the band line',
                   fontname='Helvetica', fontsize=7)
    for yv in (0, c.flap, c.H):
        witness(pg, (x0 + c.L * k, y1 + yv * k), (x0 + c.L * k + 22 * MM, y1 + yv * k))
    dim_v(pg, y1, y1 + c.flap * k, x0 + c.L * k + 7 * MM, f'{c.flap:g} flap', anchor='right')
    dim_v(pg, y1 + c.flap * k, y1 + c.H * k, x0 + c.L * k + 7 * MM, f'{c.band:g} band',
          anchor='right')
    for yv in (0, c.H):
        witness(pg, (x0, y1 + yv * k), (x0 - 13 * MM, y1 + yv * k))
    dim_v(pg, y1, y1 + c.H * k, x0 - 8 * MM, f'{c.H:g}')

    x2 = x0 + c.L * k + 50 * MM
    face(pg, x2, y1, c.W, c.H, c, k)
    band_line(pg, x2, y1, c.W, c.H, c, k)
    pg.insert_text(pymupdf.Point(x2, y1 - 4 * MM), 'end · band line returns',
                   fontname='Helvetica', fontsize=7)
    for xv in (0, c.W):
        witness(pg, (x2 + xv * k, y1 + c.H * k), (x2 + xv * k, y1 + c.H * k + 13 * MM))
    dim_h(pg, x2, x2 + c.W * k, y1 + c.H * k + 8 * MM, f'{c.W:g}')

    nx = x0 + c.L * k + 16 * MM
    y = note(pg, nx, y0 + 2 * MM, [
        'tooling, every face',
        f'debossed line {c.b:g} in from the edge',
        f'corner cap R{c.R:g} from the corner',
        f'each run stops {c.run:.1f} from the corner,',
        'where the cap crosses it -- the two',
        'marks meet and neither runs over',
        f'stud ø{c.stud:g}, {c.stud_in:g} in from both edges',
    ], bold_first=True)
    note(pg, nx, y + 3 * MM, [
        'gold foil, top only',
        f'medallion {c.medal:g} x {c.medal:g}',
        f'wordmark {c.mark_w:g} x {c.mark_h:g}',
        f'{c.gap:g} between, block centred',
    ], bold_first=True)
    return pg


def sheet_detail(doc, c):
    k = 2.0 * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box · corner detail',
          'at 2:1.  every dimension is taken from the corner of the face')
    vw, vh = 42.0, 34.0
    x0, y0 = 56 * MM, 70 * MM
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + vw * k, y0 + vh * k), color=None, fill=LEATHER)
    pale = (0.60, 0.58, 0.57)
    pg.draw_polyline([pymupdf.Point(x0 + px * k, y0 + py * k)
                      for px, py in _arc(0, 0, 1, 1, c.R, 0.0, math.pi / 2)],
                     color=pale, width=1.2)
    line(pg, (x0 + c.run * k, y0 + c.b * k), (x0 + vw * k, y0 + c.b * k), 1.2, pale)
    line(pg, (x0 + c.b * k, y0 + c.run * k), (x0 + c.b * k, y0 + vh * k), 1.2, pale)
    pg.draw_circle(pymupdf.Point(x0 + c.stud_in * k, y0 + c.stud_in * k),
                   c.stud * k / 2, color=pale, fill=None, width=1.0)

    for xv in (0, c.run, c.R):
        witness(pg, (x0 + xv * k, y0), (x0 + xv * k, y0 - 24 * MM))
    dim_h(pg, x0, x0 + c.R * k, y0 - 19 * MM, f'R{c.R:g}  cap')
    dim_h(pg, x0, x0 + c.run * k, y0 - 10 * MM, f'{c.run:.1f}  run ends here')
    for yv in (0, c.b, c.R):
        witness(pg, (x0, y0 + yv * k), (x0 - 34 * MM, y0 + yv * k))
    dim_v(pg, y0, y0 + c.b * k, x0 - 11 * MM, f'{c.b:g}  line inset', anchor='left')
    dim_v(pg, y0, y0 + c.R * k, x0 - 30 * MM, f'R{c.R:g}', anchor='left')
    witness(pg, (x0 + c.stud_in * k, y0), (x0 + c.stud_in * k, y0 + c.stud_in * k))
    witness(pg, (x0, y0 + c.stud_in * k), (x0 + c.stud_in * k, y0 + c.stud_in * k))
    dim_h(pg, x0, x0 + c.stud_in * k, y0 + (c.stud_in + 10) * k, f'{c.stud_in:g}')
    dim_v(pg, y0, y0 + c.stud_in * k, x0 + (c.stud_in + 10) * k, f'{c.stud_in:g}')
    pg.insert_text(pymupdf.Point(x0 + (c.stud_in + 13) * k, y0 + (c.stud_in + 11) * k),
                   f'stud ø{c.stud:g}, domed', fontname='Helvetica', fontsize=7)

    note(pg, x0 - 36 * MM, y0 + vh * k + 20 * MM, [
        f'the line stops at the cap. it does not curve round it and the cap does not '
        f'cross it:',
        f'an arc of R{c.R:g} from the corner meets a line {c.b:g} in from the edge at '
        f'sqrt({c.R:g}² - {c.b:g}²) = {c.run:.1f} along that edge.',
        '',
        'blind deboss: no ink, no foil, a tooled groove in the leatherette,',
        'about 0.35 deep and 0.8 wide, radiused, not a sharp vee.',
        f'the cap is a quarter round of R{c.R:g} struck from the corner, left slightly '
        'proud of the face.',
        f'the stud is a dome ø{c.stud:g}, about 0.8 proud, on the 45° bisector '
        f'{c.stud_in*math.sqrt(2):.1f} from the corner.',
        'the same tooling runs on all six faces.',
    ])
    return pg


def sheet_spec(doc, c, s):
    k = s * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box · how it opens',
          f'section on the length.  drawing at 1:{1/s:g}.  exterior only')
    x0, y0 = 34 * MM, 56 * MM
    t = (c.board + c.wrap) * k
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + c.L * k, y0 + c.H * k),
                 color=LEATHER, fill=(1, 1, 1), width=0.5)
    for r in (pymupdf.Rect(x0, y0, x0 + c.L * k, y0 + t),
              pymupdf.Rect(x0, y0 + c.H * k - t, x0 + c.L * k, y0 + c.H * k),
              pymupdf.Rect(x0, y0, x0 + t, y0 + c.H * k),
              pymupdf.Rect(x0 + c.L * k - t, y0, x0 + c.L * k, y0 + c.H * k)):
        pg.draw_rect(r, color=None, fill=LEATHER)
    yb = y0 + c.flap * k
    line(pg, (x0, yb), (x0 + c.L * k, yb), 0.6, CUT)
    pg.insert_text(pymupdf.Point(x0 + c.L * k + 3 * MM, yb + 1.5),
                   'band line', fontname='Helvetica', fontsize=6.5, color=CUT)
    mx = x0 + c.L * k / 2
    pg.draw_rect(pymupdf.Rect(mx - c.magnet * k / 2, y0 + t, mx + c.magnet * k / 2,
                              y0 + t + 2.5 * k), color=HID, fill=None, width=0.5,
                 dashes='[2 1.6] 0')
    pg.insert_text(pymupdf.Point(x0, y0 - 4 * MM), 'section on the length',
                   fontname='Helvetica', fontsize=7)
    for yv in (0, c.flap, c.H):
        witness(pg, (x0, y0 + yv * k), (x0 - 18 * MM, y0 + yv * k))
    dim_v(pg, y0, y0 + c.flap * k, x0 - 11 * MM, f'{c.flap:g}', anchor='left')
    dim_v(pg, y0 + c.flap * k, y0 + c.H * k, x0 - 11 * MM, f'{c.band:g}', anchor='left')

    rows = [
        ('overall', f'{c.L:g} x {c.W:g} x {c.H:g} mm closed'),
        ('split', f'{c.band:g} mm band at the bottom, {c.flap:g} mm shell above it'),
        ('opening', 'the shell lifts and its front drops forward as a flap'),
        ('band line', 'across the front and returning along both ends; '
                      'none on the back, which is the hinge'),
        ('closure', f'magnetic catch, {c.magnet:g} mm long, centred on the front'),
        ('carcass', f'{c.board:g} mm greyboard'),
        ('wrap', f'{c.wrap:g} mm black leatherette, tooled flat, then wrapped'),
        ('tooling', f'cap R{c.R:g}, line {c.b:g} in stopping {c.run:.1f} from each corner, '
                    f'stud ø{c.stud:g}'),
        ('foil', 'gold, hot stamped on the top only'),
    ]
    tx, ty = 34 * MM, y0 + c.H * k + 24 * MM
    for name, v in rows:
        pg.insert_text(pymupdf.Point(tx, ty), name, fontname='Helvetica-Bold', fontsize=7.5)
        pg.insert_text(pymupdf.Point(tx + 30 * MM, ty), v, fontname='Helvetica', fontsize=7.5)
        ty += 5.4 * MM
    note(pg, tx, ty + 4 * MM, [
        'nothing here covers the inside: no lining, no compartments, no fittings.',
    ])
    return pg


def sheet_art(doc, c, fw, fh, label, foil=False, band=False):
    k = MM
    pg = doc.new_page(width=(fw + 96) * MM, height=(fh + 86) * MM)
    title(pg, 20 * MM, 18 * MM, f'TRAXNYC box · artwork · {label}',
          'full size.  magenta cuts, grey is tooling, gold is foil')
    x0, y0 = 32 * MM, 42 * MM
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + fw * k, y0 + fh * k), color=CUT,
                 fill=None, width=0.6)
    pg.draw_rect(pymupdf.Rect(x0 - 3 * k, y0 - 3 * k, x0 + (fw + 3) * k,
                              y0 + (fh + 3) * k), color=CUT, fill=None,
                 width=0.4, dashes='[3 2] 0')
    face(pg, x0, y0, fw, fh, c, k, fill=None, tool=(0.45, 0.45, 0.45), width=0.8)
    if band:
        yy = y0 + (fh - c.band) * k
        line(pg, (x0, yy), (x0 + fw * k, yy), 0.5, HID, '[4 2] 0')
        pg.insert_text(pymupdf.Point(x0 + 2 * MM, yy - 2 * MM),
                       f'band line, {c.band:g} up — not printed',
                       fontname='Helvetica', fontsize=6.5, color=HID)
    if foil:
        a, b = mark(pg, x0 + fw * k / 2, y0 + fh * k / 2, c, k, solid=False)
        pg.insert_text(pymupdf.Point(a.x1 + 3 * MM, a.y0 + 4 * MM),
                       'medallion — your file, centred here',
                       fontname='Helvetica', fontsize=6.5, color=GOLD)
        pg.insert_text(pymupdf.Point(b.x1 + 3 * MM, b.y1 - 1 * MM),
                       'TRAXNYC — your file, centred here',
                       fontname='Helvetica', fontsize=6.5, color=GOLD)
        witness(pg, (x0 + fw * k / 2, y0), (x0 + fw * k / 2, y0 - 12 * MM))
        dim_h(pg, x0, x0 + fw * k / 2, y0 - 8 * MM, f'{fw/2:g} to centre')
        for r, t in ((a, f'{c.medal:g}'), (b, f'{c.mark_h:g}')):
            dim_v(pg, r.y0, r.y1, x0 - 9 * MM, t, anchor='left')
            witness(pg, (x0, r.y0), (x0 - 11 * MM, r.y0))
            witness(pg, (x0, r.y1), (x0 - 11 * MM, r.y1))
    witness(pg, (x0, y0 + fh * k), (x0, y0 + fh * k + 16 * MM))
    witness(pg, (x0 + fw * k, y0 + fh * k), (x0 + fw * k, y0 + fh * k + 16 * MM))
    dim_h(pg, x0, x0 + fw * k, y0 + fh * k + 11 * MM, f'{fw:g}')
    dim_v(pg, y0, y0 + fh * k, x0 + fw * k + 11 * MM, f'{fh:g}', anchor='right')
    witness(pg, (x0 + fw * k, y0), (x0 + fw * k + 13 * MM, y0))
    witness(pg, (x0 + fw * k, y0 + fh * k), (x0 + fw * k + 13 * MM, y0 + fh * k))
    note(pg, x0, y0 + fh * k + 26 * MM, [
        'magenta solid = trim.  magenta dashed = 3 mm bleed on the wrap.',
        f'grey = blind deboss and cap: line {c.b:g} in, stopping {c.run:.1f} from each '
        f'corner where the R{c.R:g} cap meets it; stud ø{c.stud:g} at '
        f'{c.stud_in:g}, {c.stud_in:g}.',
        'the line never crosses the cap and the cap never crosses the line.',
        'nothing grey is printed or foiled; it is tooling only.',
    ])
    return pg


def sheet_flat(doc, c):
    """Every face at 1:1, laid out as the box unwraps, so nothing is guessed."""
    k = MM
    L, W, H = c.L, c.W, c.H
    dev_w, dev_h = H + L + H, H + W + H + W
    pg = doc.new_page(width=(dev_w + 86) * MM, height=(dev_h + 76) * MM)
    title(pg, 20 * MM, 18 * MM, 'TRAXNYC box \u00b7 artwork \u00b7 flat',
          'every face at full size, laid out as the box unwraps.  '
          'magenta cuts, blue folds, grey is tooling, gold is foil')
    ox, oy = 40 * MM, 46 * MM

    def P(mx, my):
        return ox + mx * k, oy + my * k

    panels = [
        ('back',   H,     0,     L, H, False, None),
        ('end',    0,     H,     H, W, False, 'x'),
        ('top',    H,     H,     L, W, True,  None),
        ('end',    H + L, H,     H, W, False, 'X'),
        ('front',  H,     H + W, L, H, False, 'y'),
        ('bottom', H,     H + W + H, L, W, False, None),
    ]
    for name, mx, my, fw, fh, foil, bandside in panels:
        x, y = P(mx, my)
        face(pg, x, y, fw, fh, c, k, fill=None, tool=(0.45, 0.45, 0.45), width=0.7)
        if bandside == 'x':                       # left end: band at the outer edge
            bx = x + c.band * k
            line(pg, (bx, y), (bx, y + fh * k), 0.5, HID, '[4 2] 0')
        elif bandside == 'X':                     # right end
            bx = x + (fw - c.band) * k
            line(pg, (bx, y), (bx, y + fh * k), 0.5, HID, '[4 2] 0')
        elif bandside == 'y':                     # front: band at the bottom
            by = y + (fh - c.band) * k
            line(pg, (x, by), (x + fw * k, by), 0.5, HID, '[4 2] 0')
            mxc = x + fw * k / 2
            pg.draw_rect(pymupdf.Rect(mxc - c.magnet * k / 2, y + 10 * k,
                                      mxc + c.magnet * k / 2, y + 13 * k),
                         color=HID, fill=None, width=0.5, dashes='[2 1.6] 0')
        if foil:
            a, b = mark(pg, x + fw * k / 2, y + fh * k / 2, c, k, solid=False)
        pg.insert_text(pymupdf.Point(x + 2.5 * MM, y + 5 * MM), name,
                       fontname='Helvetica-Bold', fontsize=7, color=(0.45, 0.45, 0.45))

    # the trim is the outside of the development only; everything inside folds
    sil = [(H, 0), (H + L, 0), (H + L, H), (H + L + H, H), (H + L + H, H + W),
           (H + L, H + W), (H + L, H + W + H + W), (H, H + W + H + W),
           (H, H + W), (0, H + W), (0, H), (H, H), (H, 0)]
    pg.draw_polyline([pymupdf.Point(*P(mx, my)) for mx, my in sil],
                     color=CUT, width=0.8)

    # fold lines where panels meet
    for p0, p1 in ((P(H, H), P(H + L, H)), (P(H, H + W), P(H + L, H + W)),
                   (P(H, H), P(H, H + W)), (P(H + L, H), P(H + L, H + W)),
                   (P(H, H + W + H), P(H + L, H + W + H))):
        line(pg, p0, p1, 0.8, FOLDC, '[5 2.5] 0')

    # overall development
    x0, y0 = P(0, 0)
    xe, ye = P(dev_w, dev_h)
    witness(pg, (x0, ye), (x0, ye + 15 * MM))
    witness(pg, (xe, ye), (xe, ye + 15 * MM))
    dim_h(pg, x0, xe, ye + 10 * MM, f'{dev_w:g} across the development')
    witness(pg, (x0, y0), (x0 - 15 * MM, y0))
    witness(pg, (x0, ye), (x0 - 15 * MM, ye))
    dim_v(pg, y0, ye, x0 - 10 * MM, f'{dev_h:g} down')

    note(pg, x0, ye + 22 * MM, [
        'magenta = trim.  blue dashed heavy = fold.  blue dashed fine = the band line and '
        'the magnet, neither of them printed.',
        f'grey = blind deboss and cap, the same on every face: line {c.b:g} in from the '
        f'edge, each run stopping {c.run:.1f} from the corner',
        f'where the R{c.R:g} cap meets it, stud \u00f8{c.stud:g} at {c.stud_in:g}, '
        f'{c.stud_in:g}.  nothing grey is printed or foiled.',
        f'gold = foil, top panel only.  the medallion and the wordmark are your files; '
        'the dashed boxes are where they sit.',
        f'the caps are R{c.R:g} so that on the front and the ends they finish exactly on '
        f'the band line {c.band:g} up, and nothing crosses the opening.',
        'the ends are drawn lying on their sides, as they fall when the box is unwrapped; '
        'their band line runs vertically, at the outer edge.',
        'add bleed to the outside of the development to suit the wrapping method.',
    ])
    return pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--L', type=float, default=170.0)
    ap.add_argument('--W', type=float, default=70.0)
    ap.add_argument('--H', type=float, default=60.0)
    ap.add_argument('--band', type=float, default=20.0,
                    help='the fixed bottom band; the shell above it is H - band')
    ap.add_argument('--board', type=float, default=2.0)
    ap.add_argument('--wrap', type=float, default=0.8)
    ap.add_argument('--border', type=float, default=7.0)
    ap.add_argument('--cap', type=float, default=20.0)
    ap.add_argument('--stud', type=float, default=3.5)
    ap.add_argument('--stud-in', type=float, default=9.0)
    ap.add_argument('--magnet', type=float, default=40.0)
    ap.add_argument('--medal', type=float, default=26.0)
    ap.add_argument('--mark-w', type=float, default=52.0)
    ap.add_argument('--mark-h', type=float, default=8.0)
    ap.add_argument('--gap', type=float, default=4.0)
    ap.add_argument('--scale', type=float, default=0.5)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    c = Box(a.L, a.W, a.H, a.band, a.board, a.wrap, a.border, a.cap, a.stud,
            a.stud_in, a.magnet, a.medal, a.mark_w, a.mark_h, a.gap)

    spec = pymupdf.open()
    sheet_ga(spec, c, a.scale)
    sheet_spec(spec, c, a.scale)
    sheet_detail(spec, c)
    f1 = os.path.join(a.out_dir, 'traxnyc-box-production.pdf')
    spec.save(f1, garbage=4, deflate=True)

    art = pymupdf.open()
    sheet_flat(art, c)
    sheet_art(art, c, c.L, c.W, 'top · tooling + gold foil', foil=True)
    sheet_art(art, c, c.L, c.H, 'front · tooling', band=True)
    sheet_art(art, c, c.W, c.H, 'end · tooling', band=True)
    f2 = os.path.join(a.out_dir, 'traxnyc-box-artwork.pdf')
    art.save(f2, garbage=4, deflate=True)

    print(f'{f1}  3 sheets\n{f2}  flat development + 3 faces, all 1:1\n'
          f'  {c.L:g} x {c.W:g} x {c.H:g}, band {c.band:g} + shell {c.flap:g}\n'
          f'  cap R{c.R:g}, line {c.b:g} in, runs stop {c.run:.1f} from each corner\n'
          f'  magnetic catch {c.magnet:g} long, centred on the front', file=sys.stderr)


if __name__ == '__main__':
    main()
