#!/usr/bin/env python3
"""Production drawing for the domed PA & CO logo, A3 landscape.

The part is not a constant-height relief: the top is an elliptical dome
that runs out of width on a narrow stroke, so a 1.05 mm stroke crowns
lower than a 2.37 mm one. A supplier cannot read that off a single
thickness figure, so the sheet carries the profile as a dimensioned
section and the crown height as a table against stroke width.
"""
import argparse, math, os, sys
import numpy as np, pymupdf
from shapely.geometry import LineString
from shapely.prepared import prep

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_dome import artwork, rings

MM = 72.0 / 25.4


# ---------------------------------------------------------------- geometry
def elevation(levels, axis, lo, hi, n=420):
    """Silhouette height along an axis: the tallest level covering each station."""
    pre = [(z, prep(g)) for z, g in levels]
    xs = np.linspace(lo, hi, n)
    out = []
    for x in xs:
        seg = (LineString([(x, -60), (x, 60)]) if axis == 'x'
               else LineString([(-60, x), (60, x)]))
        h = 0.0
        for z, p in pre:
            if p.intersects(seg):
                h = z
        out.append(h)
    return xs, np.array(out)


def crown(width, inset, height):
    """How high the dome gets on a stroke of this width."""
    hw = width / 2.0
    if hw >= inset:
        return height
    return height * math.sqrt(max(0.0, 1 - (1 - hw / inset) ** 2))


# ------------------------------------------------------------------ drawing
class Sheet:
    def __init__(self, w=420, h=297):
        self.doc = pymupdf.open()
        self.pg = self.doc.new_page(width=w * MM, height=h * MM)
        self.W, self.H = w, h

    def P(self, x, y):
        return pymupdf.Point(x * MM, y * MM)

    def line(self, x0, y0, x1, y1, col=(0, 0, 0), w=0.25, dash=None):
        self.pg.draw_line(self.P(x0, y0), self.P(x1, y1), color=col,
                          width=w, dashes=dash)

    def rect(self, x0, y0, x1, y1, col=(0, 0, 0), w=0.25, fill=None):
        self.pg.draw_rect(pymupdf.Rect(self.P(x0, y0), self.P(x1, y1)),
                          color=col, width=w, fill=fill)

    def text(self, x, y, s, size=2.6, col=(0, 0, 0), font='helv', align=0):
        fs = size * MM
        if align:
            tw = pymupdf.get_text_length(s, fontname=font, fontsize=fs)
            x -= (tw / MM) * (0.5 if align == 1 else 1.0)
        self.pg.insert_text(self.P(x, y), s, fontsize=fs, color=col, fontname=font)

    def arrow(self, x, y, dx, dy, L=1.8, col=(0, 0, 0)):
        n = math.hypot(dx, dy) or 1
        ux, uy = dx / n, dy / n
        px, py = -uy, ux
        self.pg.draw_polyline([self.P(x, y),
                               self.P(x - ux * L + px * L * 0.3, y - uy * L + py * L * 0.3),
                               self.P(x - ux * L - px * L * 0.3, y - uy * L - py * L * 0.3)],
                              color=col, fill=col, width=0.2)

    def dim_h(self, x0, x1, y, label, ext_from=None, size=2.4, flip=False):
        c = (0, 0, 0)
        if ext_from is not None:
            self.line(x0, ext_from, x0, y + (1.2 if flip else -1.2), c, 0.15)
            self.line(x1, ext_from, x1, y + (1.2 if flip else -1.2), c, 0.15)
        self.line(x0, y, x1, y, c, 0.2)
        self.arrow(x0, y, -1, 0); self.arrow(x1, y, 1, 0)
        self.text((x0 + x1) / 2, y - 1.1, label, size, align=1)

    def dim_v(self, y0, y1, x, label, ext_from=None, size=2.4):
        c = (0, 0, 0)
        if ext_from is not None:
            self.line(ext_from, y0, x + 1.2, y0, c, 0.15)
            self.line(ext_from, y1, x + 1.2, y1, c, 0.15)
        self.line(x, y0, x, y1, c, 0.2)
        self.arrow(x, y0, 0, -1); self.arrow(x, y1, 0, 1)
        self.text(x - 1.0, (y0 + y1) / 2 + 0.8, label, size, align=2)


def build(src, inset, height, base, out, steps=28):
    g, W, H = artwork(src)
    rs = rings(g, inset, steps)
    k = height / inset
    levels = [(z * k, poly) for z, poly in rs]
    total = base + height

    s = Sheet()
    BX0, BY0, BX1, BY1 = 10, 10, 410, 287
    s.rect(BX0, BY0, BX1, BY1, w=0.6)
    s.rect(BX0 + 3, BY0 + 3, BX1 - 3, BY1 - 3, w=0.25)

    # ---- plan, 2:1
    SC = 2.0
    px, py = 34, 34
    pw, ph = W * SC, H * SC
    s.text(px, py - 5, 'VIEW A   PLAN', 3.2, font='hebo')
    s.text(px + 36, py - 5, 'scale 2:1', 2.4, (.35, .35, .35))
    doc = pymupdf.open(src)
    s.pg.show_pdf_page(pymupdf.Rect(s.P(px, py), s.P(px + pw, py + ph)), doc, 0)
    s.dim_h(px, px + pw, py + ph + 9, f'{W:.2f}', ext_from=py + ph)
    s.dim_v(py, py + ph, px - 9, f'{H:.2f}', ext_from=px)
    # section line A-A through the O
    sy = py + ph * 0.74
    s.line(px - 6, sy, px + pw + 6, sy, (0, 0, 0), 0.4, dash='[3 2] 0')
    s.text(px - 9, sy + 1, 'A', 3.0, font='hebo')
    s.text(px + pw + 7, sy + 1, 'A', 3.0, font='hebo')

    # ---- front elevation, 2:1
    ex, ey = px, py + ph + 26
    s.text(ex, ey - 5, 'VIEW B   FRONT ELEVATION', 3.2, font='hebo')
    s.text(ex + 56, ey - 5, 'scale 2:1', 2.4, (.35, .35, .35))
    xs, hs = elevation(levels, 'x', -W / 2, W / 2)
    ZS = 10.0                                   # the part is 2 mm thick: exaggerate z
    s.text(ex + 86, ey - 5, f'z x{ZS:g}', 2.4, (.55, .55, .55))
    y0 = ey + total * ZS
    pts = [s.P(ex + (x + W / 2) * SC, y0 - (base + h) * ZS) for x, h in zip(xs, hs)]
    s.pg.draw_polyline(pts, color=(0, 0, 0), width=0.35)
    s.line(ex, y0, ex + pw, y0, (0, 0, 0), 0.35)
    s.line(ex, y0 - base * ZS, ex + pw, y0 - base * ZS, (0, 0, 0), 0.2, dash='[2 2] 0')
    s.dim_v(y0 - total * ZS, y0, ex + pw + 10, f'{total:.2f}', ext_from=ex + pw)
    s.dim_v(y0 - base * ZS, y0, ex + pw + 24, f'{base:.2f}', ext_from=ex + pw)
    s.text(ex + pw + 26, y0 - base * ZS - 2.5, 'base', 2.2, (.35, .35, .35))

    # ---- side elevation, 2:1
    vx, vy = px, ey + 44
    s.text(vx, vy - 5, 'VIEW C   SIDE ELEVATION', 3.2, font='hebo')
    s.text(vx + 54, vy - 5, 'scale 2:1', 2.4, (.35, .35, .35))
    s.text(vx + 80, vy - 5, f'z x{ZS:g}', 2.4, (.55, .55, .55))
    ys, hs2 = elevation(levels, 'y', -H / 2, H / 2)
    y2 = vy + total * ZS
    pts = [s.P(vx + (y + H / 2) * SC, y2 - (base + h) * ZS) for y, h in zip(ys, hs2)]
    s.pg.draw_polyline(pts, color=(0, 0, 0), width=0.35)
    s.line(vx, y2, vx + H * SC, y2, (0, 0, 0), 0.35)
    s.dim_h(vx, vx + H * SC, y2 + 9, f'{H:.2f}', ext_from=y2)

    # ---- body schedule
    bx, by = px, vy + 44
    s.text(bx, by - 5, 'BODIES', 3.2, font='hebo')
    s.text(bx + 20, by - 5, 'six separate solids, not joined', 2.4, (.35, .35, .35))
    s.rect(bx, by, bx + 118, by + 6, w=0.25, fill=(.93, .93, .93))
    for t, dx_ in [('item', 3), ('body', 16), ('width', 48), ('height', 72), ('counters', 96)]:
        s.text(bx + dx_, by + 4.2, t, 2.4, font='hebo')
    names = ['P', 'A', 'diamond', 'ampersand', 'C', 'O with bar']
    geoms = sorted(g.geoms, key=lambda q: q.bounds[0])
    yy = by + 6
    for i, q in enumerate(geoms):
        x0, y0b, x1, y1b = q.bounds
        s.rect(bx, yy, bx + 118, yy + 5.6, w=0.15)
        s.text(bx + 3, yy + 3.9, str(i + 1), 2.4)
        s.text(bx + 16, yy + 3.9, names[i] if i < len(names) else '-', 2.4)
        s.text(bx + 48, yy + 3.9, f'{x1 - x0:.2f}', 2.4)
        s.text(bx + 72, yy + 3.9, f'{y1b - y0b:.2f}', 2.4)
        s.text(bx + 96, yy + 3.9, str(len(q.interiors)), 2.4)
        yy += 5.6

    # ---- section A-A, 20:1
    SS = 20.0
    cx, cy = 186, 54
    s.text(cx, cy - 10, 'SECTION A-A', 3.2, font='hebo')
    s.text(cx + 30, cy - 10, 'scale 20:1', 2.4, (.35, .35, .35))
    s.text(cx, cy - 5.5, 'through the thinnest stroke, 1.05 mm', 2.4, (.35, .35, .35))
    wmin = 1.05
    half = wmin / 2 * SS
    bz = base * SS
    ch = crown(wmin, inset, height)
    base_y = cy + 40
    # the dome: z = height * sqrt(1-(1-d/inset)^2) at distance d from the edge
    prof = []
    N = 60
    for i in range(N + 1):
        d = (wmin / 2) * i / N
        z = height * math.sqrt(max(0.0, 1 - (1 - d / inset) ** 2))
        prof.append((d, z))
    pts = [s.P(cx - half + d * SS, base_y - bz - z * SS) for d, z in prof]
    pts += [s.P(cx + half - d * SS, base_y - bz - z * SS) for d, z in reversed(prof)]
    s.pg.draw_polyline(pts, color=(0, 0, 0), width=0.4)
    s.line(cx - half, base_y, cx + half, base_y, (0, 0, 0), 0.4)
    s.line(cx - half, base_y, cx - half, base_y - bz, (0, 0, 0), 0.4)
    s.line(cx + half, base_y, cx + half, base_y - bz, (0, 0, 0), 0.4)
    s.line(cx - half, base_y - bz, cx + half, base_y - bz, (0, 0, 0), 0.2, dash='[2 2] 0')
    s.dim_h(cx - half, cx + half, base_y + 10, f'{wmin:.2f}', ext_from=base_y)
    s.dim_v(base_y - bz, base_y, cx + half + 12, f'{base:.2f}', ext_from=cx + half)
    s.dim_v(base_y - bz - ch * SS, base_y - bz, cx + half + 26, f'{ch:.2f}', ext_from=cx + half)
    s.text(cx + half + 28, base_y - bz - ch * SS - 3, 'crown on this stroke', 2.2, (.35, .35, .35))
    s.text(cx - 26, base_y + 20,
           'A stroke narrower than 2.50 mm runs out of width before the dome', 2.3, (.3, .3, .3))
    s.text(cx - 26, base_y + 24,
           'reaches full height, so the two faces meet in a ridge along the', 2.3, (.3, .3, .3))
    s.text(cx - 26, base_y + 28,
           'centre of the stroke. This is correct and must not be flattened.', 2.3, (.3, .3, .3))

    # ---- dome profile definition
    dx, dy = 186, 142
    s.text(dx, dy - 6, 'DOME PROFILE', 3.2, font='hebo')
    s.text(dx, dy - 1.5, 'elliptical, struck from the edge of every stroke', 2.4, (.35, .35, .35))
    gx, gy = dx + 4, dy + 44
    PS = 20.0
    s.line(gx, gy, gx + inset * PS, gy, (.6, .6, .6), 0.2)
    s.line(gx, gy, gx, gy - height * PS, (.6, .6, .6), 0.2)
    pts = []
    for i in range(81):
        d = inset * i / 80
        z = height * math.sqrt(max(0.0, 1 - (1 - d / inset) ** 2))
        pts.append(s.P(gx + d * PS, gy - z * PS))
    s.pg.draw_polyline(pts, color=(0, 0, 0), width=0.45)
    s.dim_h(gx, gx + inset * PS, gy + 9, f'{inset:.2f}', ext_from=gy)
    s.text(gx + inset * PS / 2, gy + 13.5, 'inset to full height', 2.2, (.35, .35, .35), align=1)
    s.dim_v(gy - height * PS, gy, gx + inset * PS + 12, f'{height:.2f}', ext_from=gx + inset * PS)
    s.text(gx - 1, gy + 4, 'edge of stroke', 2.2, (.35, .35, .35))
    s.text(dx, gy + 20,
           'z = 1.80 x sqrt( 1 - (1 - d / 1.25)^2 )   for d <= 1.25 mm,'
           '   z = 1.80 beyond', 2.4)
    s.text(dx, gy + 24.5, 'd = distance from the edge of the stroke, in plan', 2.3, (.35, .35, .35))

    # ---- table: crown height against stroke width
    tx, ty = 288, 34
    s.text(tx, ty - 5, 'CROWN HEIGHT BY STROKE WIDTH', 3.2, font='hebo')
    s.rect(tx, ty, tx + 108, ty + 6, w=0.25, fill=(.93, .93, .93))
    s.text(tx + 3, ty + 4.2, 'stroke width', 2.4, font='hebo')
    s.text(tx + 42, ty + 4.2, 'crown height', 2.4, font='hebo')
    s.text(tx + 82, ty + 4.2, 'note', 2.4, font='hebo')
    rows = [(1.05, 'thinnest in the artwork'), (1.25, ''), (1.50, ''), (1.75, ''),
            (2.00, ''), (2.37, 'thickest in the artwork'), (2.50, 'full height from here')]
    yy = ty + 6
    for w, note in rows:
        s.rect(tx, yy, tx + 108, yy + 5.6, w=0.15)
        s.text(tx + 3, yy + 3.9, f'{w:.2f} mm', 2.4)
        s.text(tx + 42, yy + 3.9, f'{crown(w, inset, height):.2f} mm', 2.4)
        s.text(tx + 82, yy + 3.9, note, 2.2, (.35, .35, .35))
        yy += 5.6

    # ---- notes
    ny = yy + 10
    s.text(tx, ny, 'NOTES', 3.2, font='hebo'); ny += 6
    for i, t in enumerate([
        'All dimensions in millimetres. Do not scale from this drawing.',
        'Part is six separate bodies: P, A, ampersand, C, O with bar, diamond.',
        'Outline is fixed. No stroke may be thinned; 1.05 mm is the minimum '
        'and is already at the limit.',
        'Top surface domed per SECTION A-A. Flat underside.',
        'Finish: satin silver, uniform. No polished or mirror areas.',
        'Supplied as a closed STL in millimetres: '
        'paco-logo-dome1.80-base0.30.stl',
        'General tolerance +/-0.05 mm. Dome height +/-0.10 mm.',
    ]):
        s.text(tx, ny, f'{i+1}', 2.4, font='hebo')
        for j, line in enumerate(wrap(t, 56)):
            s.text(tx + 5, ny + j * 4.0, line, 2.4)
        ny += 4.0 * len(wrap(t, 56)) + 1.6

    # ---- title block
    tbx, tby = BX1 - 3 - 150, BY1 - 3 - 32
    s.rect(tbx, tby, BX1 - 3, BY1 - 3, w=0.5)
    s.line(tbx, tby + 11, BX1 - 3, tby + 11, (0, 0, 0), 0.25)
    s.line(tbx, tby + 21, BX1 - 3, tby + 21, (0, 0, 0), 0.25)
    s.line(tbx + 95, tby, tbx + 95, tby + 21, (0, 0, 0), 0.25)
    s.text(tbx + 3, tby + 7.5, 'PA & CO   -   LOGO, DOMED', 4.2, font='hebo')
    for i, (k, v) in enumerate([('MATERIAL', 'per supplier'),
                                ('FINISH', 'satin silver'),
                                ('UNITS', 'millimetres')]):
        s.text(tbx + 3, tby + 15 + i * 0, '', 2.2)
    s.text(tbx + 3, tby + 16, 'FINISH', 2.2, (.35, .35, .35))
    s.text(tbx + 20, tby + 16, 'satin silver', 2.6)
    s.text(tbx + 50, tby + 16, 'UNITS', 2.2, (.35, .35, .35))
    s.text(tbx + 62, tby + 16, 'mm', 2.6)
    s.text(tbx + 98, tby + 16, 'SCALE', 2.2, (.35, .35, .35))
    s.text(tbx + 112, tby + 16, 'as noted', 2.6)
    s.text(tbx + 3, tby + 26.5, 'OVERALL', 2.2, (.35, .35, .35))
    s.text(tbx + 20, tby + 26.5, f'{W:.2f} x {H:.2f} x {total:.2f}', 2.6)
    s.text(tbx + 98, tby + 7.5, 'SHEET', 2.2, (.35, .35, .35))
    s.text(tbx + 112, tby + 7.5, '1 of 1', 2.6)
    s.text(tbx + 98, tby + 26.5, 'MIN. STROKE', 2.2, (.35, .35, .35))
    s.text(tbx + 125, tby + 26.5, '1.05', 2.6)

    s.doc.save(out)
    return s.doc, total


def wrap(t, n):
    words, lines, cur = t.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-min1mm-FINAL.pdf')
    a.add_argument('--inset', type=float, default=1.25)
    a.add_argument('--height', type=float, default=1.80)
    a.add_argument('--base', type=float, default=0.30)
    a.add_argument('--out', default='assets/paco/paco-production-drawing.pdf')
    a.add_argument('--png')
    o = a.parse_args()
    doc, total = build(o.src, o.inset, o.height, o.base, o.out)
    print(f'{o.out}: A3 landscape, overall {total:.2f} mm thick')
    if o.png:
        doc[0].get_pixmap(matrix=pymupdf.Matrix(2.6, 2.6)).save(o.png)
        print('   preview', o.png)
