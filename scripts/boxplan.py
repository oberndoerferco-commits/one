#!/usr/bin/env python3
"""A working drawing for a two-door presentation case that opens out flat.

The reference is a necklace case: a deep tray with a lined, hooked field,
and a lined, hooked door to either side, so that opening it lays three
hanging faces side by side.

Everything follows from the closed size, and one consequence is worth
stating before it surprises anyone on the bench. The two doors have to meet
on the centre line when shut, so each is half the closed width -- they come
out narrower than the tray, where the photograph's wings look nearly as
wide as its centre. A wing as wide as the tray cannot shut in the same
plane as its partner; it has to fold over it, which spends the depth three
times instead of twice. Both are drawn, one in full and one as a note.

The depth is the other thing the closed size decides: 60 mm has to hold the
tray and one door thickness, since the doors shut side by side rather than
stacked. 42 and 18 here, which leaves 36 mm of clear hanging depth inside.
"""
import argparse, os, sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft import MM, GREY, line, dim_h, dim_v, witness, note, title, arrow  # noqa: E402

VELVET = (0.52, 0.07, 0.09)
VELVET_HI = (0.60, 0.10, 0.12)
CARCASS = (0.14, 0.13, 0.13)
STEEL = (0.75, 0.75, 0.78)


class Case:
    def __init__(self, w, h, d, wall, base, door_t, rim, recess, pitch, drop):
        self.W, self.H, self.D = w, h, d          # closed, overall
        self.wall, self.base = wall, base
        self.door_t, self.rim, self.recess = door_t, rim, recess
        self.pitch, self.drop = pitch, drop
        self.tray_d = d - door_t                  # the doors shut side by side
        self.cav_w = w - 2 * wall
        self.cav_h = h - 2 * wall
        self.cav_d = self.tray_d - base
        self.door_w = w / 2
        self.field_w = self.door_w - 2 * rim
        self.field_h = h - 2 * rim
        self.open_w = w + 2 * self.door_w

    def hooks(self, field_w):
        """How many hooks fit the field, and the span they cover.

        Kept to a whole number of pitches with a margin of at least a pitch
        at each end, then centred -- so the row reads as set out from the
        middle of the panel rather than from one end of it.
        """
        n = int((field_w - 2 * self.pitch) // self.pitch) + 1
        return max(n, 2), (max(n, 2) - 1) * self.pitch


def panel(pg, x, y, w, h, inset, fill_in, c=None):
    """A lined panel: dark frame, lined field inside it."""
    pg.draw_rect(pymupdf.Rect(x, y, x + w, y + h), color=None, fill=c or CARCASS)
    pg.draw_rect(pymupdf.Rect(x + inset, y + inset, x + w - inset, y + h - inset),
                 color=None, fill=fill_in)


def hook_row(pg, x0, y, n, pitch, s):
    """The row of hooks, drawn as little posts."""
    span = (n - 1) * pitch * s
    for i in range(n):
        hx = x0 + i * pitch * s - span / 2
        pg.draw_rect(pymupdf.Rect(hx - 0.42 * MM, y - 1.0 * MM,
                                  hx + 0.42 * MM, y + 1.0 * MM),
                     color=None, fill=STEEL)
        pg.draw_rect(pymupdf.Rect(hx - 0.95 * MM, y + 0.6 * MM,
                                  hx + 0.95 * MM, y + 1.3 * MM),
                     color=None, fill=STEEL)


def page_open(doc, c, s):
    k = s * MM                      # points on the page per millimetre of case
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'Presentation case — open',
          f'two doors out flat; {c.W:g} x {c.H:g} x {c.D:g} mm closed.  drawing at 1:{1/s:g}')
    ow, oh = c.open_w * k, c.H * k
    x0 = 24 * MM
    y0 = 52 * MM

    panel(pg, x0, y0, c.door_w * k, oh, c.rim * k, VELVET)
    tx = x0 + c.door_w * k
    panel(pg, tx, y0, c.W * k, oh, c.wall * k, VELVET_HI)
    rx = tx + c.W * k
    panel(pg, rx, y0, c.door_w * k, oh, c.rim * k, VELVET)

    nd, _ = c.hooks(c.field_w)
    nt, _ = c.hooks(c.cav_w)
    hook_row(pg, x0 + c.door_w * k / 2, y0 + (c.rim + c.drop) * k, nd, c.pitch, s)
    hook_row(pg, tx + c.W * k / 2, y0 + (c.wall + c.drop) * k, nt, c.pitch, s)
    hook_row(pg, rx + c.door_w * k / 2, y0 + (c.rim + c.drop) * k, nd, c.pitch, s)

    for x in (x0, tx, rx, rx + c.door_w * k):
        witness(pg, (x, y0 + oh), (x, y0 + oh + 16 * MM))
    dim_h(pg, x0, tx, y0 + oh + 7 * MM, f'{c.door_w:g}')
    dim_h(pg, tx, rx, y0 + oh + 7 * MM, f'{c.W:g}')
    dim_h(pg, rx, rx + c.door_w * k, y0 + oh + 7 * MM, f'{c.door_w:g}')
    dim_h(pg, x0, rx + c.door_w * k, y0 + oh + 14 * MM, f'{c.open_w:g} open')
    witness(pg, (x0, y0), (x0 - 16 * MM, y0))
    witness(pg, (x0, y0 + oh), (x0 - 16 * MM, y0 + oh))
    dim_v(pg, y0, y0 + oh, x0 - 10 * MM, f'{c.H:g}')

    # the hinges sit on the outer long edges
    for hx in (x0, rx + c.door_w * k):
        for f in (0.18, 0.82):
            pg.draw_rect(pymupdf.Rect(hx - 1.1 * MM, y0 + oh * f - 7 * MM,
                                      hx + 1.1 * MM, y0 + oh * f + 7 * MM),
                         color=(0, 0, 0), fill=(1, 1, 1), width=0.4)
    pg.insert_text(pymupdf.Point(x0 - 2 * MM, y0 - 4 * MM), 'hinge', fontname='Helvetica',
                   fontsize=6.5, color=GREY)
    pg.insert_text(pymupdf.Point(rx + c.door_w * k - 8 * MM, y0 - 4 * MM), 'hinge',
                   fontname='Helvetica', fontsize=6.5, color=GREY)

    nx = x0 + ow + 16 * MM
    y = note(pg, nx, y0 + 4 * MM, [
        'lined fields',
        f'doors  {c.field_w:g} x {c.field_h:g}',
        f'tray floor  {c.cav_w:g} x {c.cav_h:g}',
    ], bold_first=True)
    y = note(pg, nx, y + 4 * MM, [
        'hooks',
        f'{c.pitch:g} centres, {c.drop:g} below the',
        'top of each field',
        f'{nd} per door, {nt} in the tray',
        f'{2*nd+nt} in all',
    ], bold_first=True)
    note(pg, nx, y + 4 * MM, [
        'why the doors are narrow',
        'they have to meet on the centre',
        'line when shut, so each is half',
        'the closed width.  a wing as wide',
        'as the tray, which is how the',
        'photograph reads, cannot shut',
        'beside its partner at all -- it has',
        'to fold over it, and the depth is',
        f'then spent three times, not twice:',
        f'{c.D - 2*c.door_t:g} + {c.door_t:g} + {c.door_t:g} '
        f'instead of {c.tray_d:g} + {c.door_t:g}.',
    ], bold_first=True)
    return pg


def page_closed(doc, c, s):
    k = s * MM
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'Presentation case — closed',
          f'front, side and a section through the middle.  drawing at 1:{1/s:g}')
    y0 = 56 * MM
    fx = 22 * MM
    fw, fh = c.W * k, c.H * k
    pg.draw_rect(pymupdf.Rect(fx, y0, fx + fw, y0 + fh), color=CARCASS,
                 fill=CARCASS, width=0.4)
    line(pg, (fx + fw / 2, y0), (fx + fw / 2, y0 + fh), 0.5, (1, 1, 1))
    pg.insert_text(pymupdf.Point(fx, y0 - 4 * MM), 'front — the doors meet here',
                   fontname='Helvetica', fontsize=7)
    witness(pg, (fx, y0 + fh), (fx, y0 + fh + 12 * MM))
    witness(pg, (fx + fw, y0 + fh), (fx + fw, y0 + fh + 12 * MM))
    dim_h(pg, fx, fx + fw, y0 + fh + 8 * MM, f'{c.W:g}')
    witness(pg, (fx, y0), (fx - 12 * MM, y0))
    witness(pg, (fx, y0 + fh), (fx - 12 * MM, y0 + fh))
    dim_v(pg, y0, y0 + fh, fx - 8 * MM, f'{c.H:g}')

    sx = fx + fw + 26 * MM
    sw = c.D * k
    pg.draw_rect(pymupdf.Rect(sx, y0, sx + sw, y0 + fh), color=CARCASS,
                 fill=(0.93, 0.93, 0.93), width=0.4)
    pg.draw_rect(pymupdf.Rect(sx, y0, sx + c.door_t * k, y0 + fh), color=CARCASS,
                 fill=CARCASS, width=0.4)
    pg.insert_text(pymupdf.Point(sx, y0 - 4 * MM), 'side', fontname='Helvetica', fontsize=7)
    witness(pg, (sx, y0 + fh), (sx, y0 + fh + 12 * MM))
    witness(pg, (sx + c.door_t * k, y0 + fh), (sx + c.door_t * k, y0 + fh + 12 * MM))
    witness(pg, (sx + sw, y0 + fh), (sx + sw, y0 + fh + 12 * MM))
    dim_h(pg, sx, sx + c.door_t * k, y0 + fh + 4 * MM, f'{c.door_t:g}', anchor='left')
    dim_h(pg, sx, sx + sw, y0 + fh + 8 * MM, f'{c.D:g}')

    # section on the flat: the tray behind, the two doors shut in front of it
    px = sx + sw + 30 * MM
    pw, pd = c.W * k, c.D * k
    py = y0
    pg.draw_rect(pymupdf.Rect(px, py, px + pw, py + pd), color=CARCASS,
                 fill=(1, 1, 1), width=0.4)
    # tray walls and base
    pg.draw_rect(pymupdf.Rect(px, py + c.door_t * k, px + c.wall * k, py + pd),
                 color=None, fill=CARCASS)
    pg.draw_rect(pymupdf.Rect(px + pw - c.wall * k, py + c.door_t * k, px + pw, py + pd),
                 color=None, fill=CARCASS)
    pg.draw_rect(pymupdf.Rect(px, py + pd - c.base * k, px + pw, py + pd),
                 color=None, fill=CARCASS)
    pg.draw_rect(pymupdf.Rect(px + c.wall * k, py + c.door_t * k,
                              px + pw - c.wall * k, py + pd - c.base * k),
                 color=None, fill=VELVET_HI)
    # the doors
    for i in (0, 1):
        dx = px + i * c.door_w * k
        pg.draw_rect(pymupdf.Rect(dx, py, dx + c.door_w * k, py + c.door_t * k),
                     color=(1, 1, 1), fill=CARCASS, width=0.4)
        pg.draw_rect(pymupdf.Rect(dx + c.rim * k, py + (c.door_t - c.recess) * k,
                                  dx + (c.door_w - c.rim) * k, py + c.door_t * k),
                     color=None, fill=VELVET)
    pg.insert_text(pymupdf.Point(px, py - 4 * MM), 'section, looking down',
                   fontname='Helvetica', fontsize=7)
    witness(pg, (px + pw, py), (px + pw + 14 * MM, py))
    witness(pg, (px + pw, py + c.door_t * k), (px + pw + 14 * MM, py + c.door_t * k))
    witness(pg, (px + pw, py + pd), (px + pw + 14 * MM, py + pd))
    dim_v(pg, py, py + c.door_t * k, px + pw + 5 * MM, f'{c.door_t:g} door', anchor='right')
    dim_v(pg, py + c.door_t * k, py + pd, px + pw + 5 * MM, f'{c.tray_d:g} tray',
          anchor='right')
    witness(pg, (px, py + c.door_t * k), (px - 10 * MM, py + c.door_t * k))
    witness(pg, (px, py + pd - c.base * k), (px - 10 * MM, py + pd - c.base * k))
    dim_v(pg, py + c.door_t * k, py + pd - c.base * k, px - 7 * MM,
          f'{c.cav_d:g} clear', anchor='left')

    note(pg, fx, y0 + fh + 24 * MM, [
        f'the doors shut side by side, not stacked, so the {c.D:g} depth carries '
        f'one door thickness and the tray: {c.door_t:g} + {c.tray_d:g}.',
        f'walls {c.wall:g}, base {c.base:g}; cavity {c.cav_w:g} x {c.cav_h:g} x '
        f'{c.cav_d:g} clear for the chains to hang in.',
        f'door recess {c.recess:g} deep inside a {c.rim:g} rim, so a hook and its chain '
        f'clear the tray rim when it shuts.',
    ])
    return pg


def page_parts(doc, c):
    pg = doc.new_page(width=297 * MM, height=210 * MM)
    title(pg, 20 * MM, 18 * MM, 'Presentation case — cutting list',
          'sizes over the carcass, before lining')
    nd, dspan = c.hooks(c.field_w)
    nt, tspan = c.hooks(c.cav_w)
    rows = [
        ('tray, back', 1, c.W - 2 * c.wall, c.H - 2 * c.wall, c.base, 'let into the walls'),
        ('tray, long wall', 2, c.H, c.tray_d - 0, c.wall, 'full height of the case'),
        ('tray, short wall', 2, c.W - 2 * c.wall, c.tray_d, c.wall, 'between the long walls'),
        ('door panel', 2, c.door_w, c.H, c.door_t, f'{c.recess:g} recess, {c.rim:g} rim'),
        ('lining, tray floor', 1, c.cav_w, c.cav_h, None, 'velvet over 1 mm card'),
        ('lining, tray wall', 4, None, c.cav_d, None, 'cut to suit on fitting'),
        ('lining, door field', 2, c.field_w, c.field_h, None, 'velvet over 1 mm card'),
        ('hinge, 40 mm butt', 4, None, None, None, 'two per door, inset in the outer edge'),
        ('hook', 2 * nd + nt, None, None, None,
         f'{nd} per door, {nt} in the tray, {c.pitch:g} centres'),
        ('catch, magnetic', 2, None, None, None, 'on the meeting edges'),
    ]
    tx, ty = 20 * MM, 40 * MM
    cols = [0, 52 * MM, 66 * MM, 84 * MM, 102 * MM, 120 * MM]
    for cx, h in zip(cols, ['part', 'no.', 'length', 'width', 'thick', 'note']):
        pg.insert_text(pymupdf.Point(tx + cx, ty), h, fontname='Helvetica-Bold',
                       fontsize=7, color=GREY)
    line(pg, (tx, ty + 1.6 * MM), (tx + 250 * MM, ty + 1.6 * MM), 0.4)
    y = ty + 6.5 * MM
    for name, n, L, W, T, nt_ in rows:
        pg.insert_text(pymupdf.Point(tx, y), name, fontname='Helvetica', fontsize=7.5)
        for cx, v in zip(cols[1:5], (n, L, W, T)):
            t = '' if v is None else (f'{v:g}' if not isinstance(v, int) or cx != cols[1]
                                     else f'{v:g}')
            if t:
                w = pymupdf.get_text_length(t, 'Helvetica', 7.5)
                pg.insert_text(pymupdf.Point(tx + cx + 12 * MM - w, y), t,
                               fontname='Helvetica', fontsize=7.5)
        pg.insert_text(pymupdf.Point(tx + cols[5], y), nt_, fontname='Helvetica',
                       fontsize=7, color=GREY)
        y += 5.2 * MM
    line(pg, (tx, y - 3.6 * MM), (tx + 250 * MM, y - 3.6 * MM), 0.4)

    # hook spacing, full size
    hy = y + 26 * MM
    pg.insert_text(pymupdf.Point(tx, hy - 8 * MM), 'hook spacing in the tray, full size',
                   fontname='Helvetica-Bold', fontsize=8)
    s = 1.0
    cx = tx + c.cav_w * MM / 2
    hook_row(pg, cx, hy, nt, c.pitch, MM)
    witness(pg, (cx - tspan * MM / 2, hy), (cx - tspan * MM / 2, hy + 12 * MM))
    witness(pg, (cx + tspan * MM / 2, hy), (cx + tspan * MM / 2, hy + 12 * MM))
    dim_h(pg, cx - tspan * MM / 2, cx + tspan * MM / 2, hy + 9 * MM,
          f'{tspan:g} over {nt} hooks')
    dim_h(pg, cx - tspan * MM / 2, cx - tspan * MM / 2 + c.pitch * MM, hy + 4 * MM,
          f'{c.pitch:g}', anchor='left')
    note(pg, tx, hy + 22 * MM, [
        f'hooks sit {c.drop:g} below the top of the lined field on every face.',
        'set them out from the centre line so the row stays centred whatever the count.',
    ])
    return pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--w', type=float, default=200.0, help='closed width, mm')
    ap.add_argument('--h', type=float, default=270.0, help='closed height, mm')
    ap.add_argument('--d', type=float, default=60.0, help='closed depth, mm')
    ap.add_argument('--wall', type=float, default=10.0)
    ap.add_argument('--base', type=float, default=6.0)
    ap.add_argument('--door', type=float, default=18.0)
    ap.add_argument('--rim', type=float, default=10.0)
    ap.add_argument('--recess', type=float, default=8.0)
    ap.add_argument('--pitch', type=float, default=15.0)
    ap.add_argument('--drop', type=float, default=25.0)
    ap.add_argument('--scale', type=float, default=0.5)
    a = ap.parse_args()

    c = Case(a.w, a.h, a.d, a.wall, a.base, a.door, a.rim, a.recess, a.pitch, a.drop)
    doc = pymupdf.open()
    page_open(doc, c, a.scale)
    page_closed(doc, c, a.scale)
    page_parts(doc, c)
    doc.save(a.out, garbage=4, deflate=True)
    nd, _ = c.hooks(c.field_w)
    nt, _ = c.hooks(c.cav_w)
    print(f'{a.out}: closed {c.W:g} x {c.H:g} x {c.D:g}, open {c.open_w:g} x {c.H:g}\n'
          f'  tray {c.tray_d:g} deep, cavity {c.cav_w:g} x {c.cav_h:g} x {c.cav_d:g}\n'
          f'  doors {c.door_w:g} x {c.H:g} x {c.door_t:g}, field {c.field_w:g} x {c.field_h:g}\n'
          f'  hooks {nd} + {nt} + {nd} = {2*nd+nt}', file=sys.stderr)


if __name__ == '__main__':
    main()
