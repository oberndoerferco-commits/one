#!/usr/bin/env python3
"""Production drawing for the domed PA & CO logo, A3 landscape.

Drawn to the usual conventions: plan and elevations in third angle, a
hatched section on a cutting plane marked in the plan, an enlarged detail
of the profile, an isometric, and a title block.

The part is not a constant-height relief. The dome is struck from the edge
of every stroke and only reaches full height 1.25 mm in, so a stroke
narrower than 2.50 mm runs out of width first and crowns lower. One
thickness figure would be wrong, so the crown height is tabulated against
stroke width and the section says what happens at the centre line.
"""
import argparse, math, os, sys
import numpy as np, pymupdf
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_dome import artwork, rings

MM = 72.0 / 25.4
THIN, MED, THICK = 0.18, 0.3, 0.55
CHAIN = '[5 1.6 1 1.6] 0'          # centre lines
DASH = '[2.4 1.6] 0'


def elevation(levels, axis, lo, hi, n=440):
    pre = [(z, prep(g)) for z, g in levels]
    out = []
    xs = np.linspace(lo, hi, n)
    for x in xs:
        seg = (LineString([(x, -80), (x, 80)]) if axis == 'x'
               else LineString([(-80, x), (80, x)]))
        h = 0.0
        for z, p in pre:
            if p.intersects(seg):
                h = z
        out.append(h)
    return xs, np.array(out)


def section_profile(levels, y_cut, lo, hi, n=1100):
    """Material height along the cutting plane: what a section actually shows.

    elevation() projects the whole part onto an axis, which is a view, not a
    section. Here each station is tested against the plane itself, so the
    result is the strokes the plane passes through and nothing else.
    """
    pre = [(z, prep(g)) for z, g in levels]
    xs = np.linspace(lo, hi, n)
    hs, on = [], []
    for x in xs:
        pt = Point(x, y_cut)
        h, inside = 0.0, False
        for z, g in pre:
            if g.contains(pt):
                h, inside = z, True
        hs.append(h); on.append(inside)
    return xs, np.array(hs), np.array(on)


def runs(xs, on):
    out, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j + 1 < n and on[j+1]:
                j += 1
            if j > i:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def crown(width, inset, height):
    hw = width / 2.0
    if hw >= inset:
        return height
    return height * math.sqrt(max(0.0, 1 - (1 - hw / inset) ** 2))


class Sheet:
    def __init__(self, w=420, h=297):
        self.doc = pymupdf.open()
        self.pg = self.doc.new_page(width=w * MM, height=h * MM)
        self.W, self.H = w, h

    def P(self, x, y):
        return pymupdf.Point(x * MM, y * MM)

    def line(self, x0, y0, x1, y1, col=(0, 0, 0), w=MED, dash=None):
        self.pg.draw_line(self.P(x0, y0), self.P(x1, y1), color=col, width=w,
                          dashes=dash)

    def poly(self, pts, col=(0, 0, 0), w=MED, fill=None, close=False):
        p = [self.P(*q) for q in pts]
        if close:
            p.append(p[0])
        self.pg.draw_polyline(p, color=col, width=w, fill=fill)

    def rect(self, x0, y0, x1, y1, col=(0, 0, 0), w=MED, fill=None):
        self.pg.draw_rect(pymupdf.Rect(self.P(x0, y0), self.P(x1, y1)),
                          color=col, width=w, fill=fill)

    def circle(self, cx, cy, r, col=(0, 0, 0), w=MED, dash=None):
        self.pg.draw_circle(self.P(cx, cy), r * MM, color=col, width=w, dashes=dash)

    def text(self, x, y, s, size=2.5, col=(0, 0, 0), font='helv', align=0):
        fs = size * MM
        if align:
            tw = pymupdf.get_text_length(s, fontname=font, fontsize=fs)
            x -= (tw / MM) * (0.5 if align == 1 else 1.0)
        self.pg.insert_text(self.P(x, y), s, fontsize=fs, color=col, fontname=font)

    def arrow(self, x, y, dx, dy, L=1.7, col=(0, 0, 0)):
        n = math.hypot(dx, dy) or 1
        ux, uy = dx / n, dy / n
        px, py = -uy, ux
        self.pg.draw_polyline([self.P(x, y),
                               self.P(x - ux*L + px*L*0.28, y - uy*L + py*L*0.28),
                               self.P(x - ux*L - px*L*0.28, y - uy*L - py*L*0.28)],
                              color=col, fill=col, width=0.15)

    def dim_h(self, x0, x1, y, label, ext=None, size=2.4, below=False):
        if ext is not None:
            s = 1 if below else -1
            self.line(x0, ext, x0, y - s*1.4, w=THIN)
            self.line(x1, ext, x1, y - s*1.4, w=THIN)
        self.line(x0, y, x1, y, w=THIN)
        self.arrow(x0, y, -1, 0); self.arrow(x1, y, 1, 0)
        self.text((x0+x1)/2, y - 1.1, label, size, align=1)

    def dim_v(self, y0, y1, x, label, ext=None, size=2.4, left=True):
        if ext is not None:
            s = 1 if left else -1
            self.line(ext, y0, x + s*1.4, y0, w=THIN)
            self.line(ext, y1, x + s*1.4, y1, w=THIN)
        self.line(x, y0, x, y1, w=THIN)
        self.arrow(x, y0, 0, -1); self.arrow(x, y1, 0, 1)
        if left:
            self.text(x - 1.1, (y0+y1)/2 + 0.85, label, size, align=2)
        else:
            self.text(x + 1.4, (y0+y1)/2 + 0.85, label, size)

    def hatch(self, poly, step=1.3, ang=45, col=(0, 0, 0), w=THIN):
        x0, y0, x1, y1 = poly.bounds
        d = math.hypot(x1-x0, y1-y0)
        cx, cy = (x0+x1)/2, (y0+y1)/2
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        px, py = -uy, ux
        k = int(d / step) + 2
        for i in range(-k, k + 1):
            ox, oy = cx + px*i*step, cy + py*i*step
            seg = LineString([(ox - ux*d, oy - uy*d), (ox + ux*d, oy + uy*d)])
            inter = seg.intersection(poly)
            if inter.is_empty:
                continue
            parts = inter.geoms if hasattr(inter, 'geoms') else [inter]
            for s in parts:
                if s.geom_type == 'LineString' and s.length > 0.05:
                    a, b = list(s.coords)[0], list(s.coords)[-1]
                    self.line(a[0], a[1], b[0], b[1], col, w)


def build(src, inset, height, base, iso_png, out):
    g, W, H = artwork(src)
    rs = rings(g, inset, 30)
    k = height / inset
    levels = [(z*k, poly) for z, poly in rs]
    total = base + height

    s = Sheet()
    s.rect(10, 10, 410, 287, w=0.7)
    s.rect(14, 14, 406, 283, w=0.25)

    # ============ VIEW A : PLAN, 2:1
    SC, px, py = 2.0, 42, 32
    pw, ph = W*SC, H*SC
    s.text(px, py-5.5, 'VIEW A    PLAN', 3.1, font='hebo')
    s.text(px+34, py-5.5, 'SCALE 2:1', 2.3, (.35, .35, .35))
    doc = pymupdf.open(src)
    s.pg.show_pdf_page(pymupdf.Rect(s.P(px, py), s.P(px+pw, py+ph)), doc, 0)
    # centre lines
    s.line(px-5, py+ph/2, px+pw+5, py+ph/2, (0, 0, 0), THIN, CHAIN)
    s.line(px+pw/2, py-5, px+pw/2, py+ph+5, (0, 0, 0), THIN, CHAIN)
    s.dim_h(px, px+pw, py+ph+10, f'{W:.2f}', ext=py+ph, below=True)
    s.dim_v(py, py+ph, px-17, f'{H:.2f}', ext=px)
    # cutting plane A-A, through the letters
    Y_CUT = -9.5
    sy = py + (H/2 - Y_CUT)*SC
    s.line(px-9, sy, px+pw+9, sy, (0, 0, 0), THICK, CHAIN)
    s.arrow(px-9, sy+4.5, 0, -1, 2.2); s.line(px-9, sy, px-9, sy+4.5, w=THICK)
    s.arrow(px+pw+9, sy+4.5, 0, -1, 2.2); s.line(px+pw+9, sy, px+pw+9, sy+4.5, w=THICK)
    s.text(px-11.5, sy+8, 'A', 3.2, font='hebo')
    s.text(px+pw+7.5, sy+8, 'A', 3.2, font='hebo')

    # ============ SECTION A-A : the real thing, across the whole part
    ax0, ay0 = px, py + ph + 30
    s.text(ax0, ay0 - 6, 'SECTION A-A', 3.1, font='hebo')
    s.text(ax0 + 30, ay0 - 6, 'SCALE 2:1', 2.3, (.35, .35, .35))
    s.text(ax0 + 56, ay0 - 6,
           'the strokes the plane passes through, cut at y = -9.50',
           2.3, (.35, .35, .35))
    xs, hs, on = section_profile(levels, Y_CUT, -W/2, W/2)
    base_line = ay0 + 14
    for i, j in runs(xs, on):
        seg = [(ax0 + (xs[k] + W/2)*SC, base_line - (base + hs[k])*SC)
               for k in range(i, j + 1)]
        ring = ([(seg[0][0], base_line)] + seg + [(seg[-1][0], base_line)])
        s.hatch(Polygon(ring), step=0.9, ang=45)
        s.poly(ring, w=THICK, close=True)
    s.line(ax0, base_line, ax0 + pw, base_line, w=THIN, dash=DASH)
    s.dim_v(base_line - total*SC, base_line, ax0 + pw + 9, f'{total:.2f}',
            ext=ax0 + pw, left=False)
    s.text(ax0, base_line + 7,
           'Crown varies with the width of the stroke the plane meets. See DETAIL C.',
           2.3, (.3, .3, .3))

    # ============ BODY SCHEDULE
    bx, by = px, base_line + 22
    s.text(bx, by-4.5, 'BODY SCHEDULE', 3.1, font='hebo')
    s.text(bx+36, by-4.5, 'six separate solids, not joined', 2.3, (.35, .35, .35))
    cols = [(0, 'ITEM'), (13, 'BODY'), (44, 'WIDTH'), (66, 'HEIGHT'), (90, 'COUNTERS')]
    s.rect(bx, by, bx+114, by+5.8, w=MED, fill=(.9, .9, .9))
    for dx_, t in cols:
        s.text(bx+2.5+dx_, by+4, t, 2.3, font='hebo')
    names = ['P', 'A', 'DIAMOND', 'AMPERSAND', 'C', 'O WITH BAR']
    yy = by+5.8
    for i, q in enumerate(sorted(g.geoms, key=lambda r: r.bounds[0])):
        a, b, c, d = q.bounds
        s.rect(bx, yy, bx+114, yy+5.4, w=THIN)
        for dx_, t in zip([0, 13, 44, 66, 90],
                          [str(i+1), names[i], f'{c-a:.2f}', f'{d-b:.2f}',
                           str(len(q.interiors))]):
            s.text(bx+2.5+dx_, yy+3.8, t, 2.3)
        yy += 5.4

    # ============ ISOMETRIC
    ix, iy, iw = 158, 30, 118
    img = pymupdf.open(iso_png)
    r = img[0].rect
    ih = iw * r.height / r.width
    s.pg.insert_image(pymupdf.Rect(s.P(ix, iy), s.P(ix+iw, iy+ih)), filename=iso_png)
    s.text(ix+iw/2, iy+ih+6, 'ISOMETRIC VIEW', 3.1, font='hebo', align=1)

    # ============ DETAIL C : stroke profiles at the two extremes
    SS = 20.0
    cx, cy = 158, iy+ih+26
    s.text(cx, cy, 'DETAIL C', 3.1, font='hebo')
    s.text(cx+22, cy, 'STROKE PROFILES', 2.6, (.35, .35, .35))
    s.text(cx+56, cy, 'SCALE 20:1', 2.3, (.35, .35, .35))
    s.text(cx, cy+4.5, 'the thinnest and the thickest stroke in the artwork',
           2.3, (.35, .35, .35))
    base_y = cy + 66
    for n_, (wid, lab) in enumerate([(1.05, 'THINNEST  1.05'), (2.37, 'THICKEST  2.37')]):
        mid = cx + 20 + n_*62
        half = wid/2*SS
        bz = base*SS
        ch = crown(wid, inset, height)
        prof = []
        for i in range(61):
            d = (wid/2)*i/60
            z = height*math.sqrt(max(0.0, 1-(1-min(d, inset)/inset)**2))
            prof.append((d, z))
        ring = ([(mid-half, base_y), (mid-half, base_y-bz)]
                + [(mid-half+d*SS, base_y-bz-z*SS) for d, z in prof]
                + [(mid+half-d*SS, base_y-bz-z*SS) for d, z in reversed(prof)]
                + [(mid+half, base_y-bz), (mid+half, base_y)])
        s.hatch(Polygon(ring), step=1.4, ang=45)
        s.poly(ring, w=THICK, close=True)
        s.line(mid-half, base_y-bz, mid+half, base_y-bz, (0, 0, 0), THIN, DASH)
        s.line(mid, base_y+4, mid, base_y-bz-ch*SS-5, (0, 0, 0), THIN, CHAIN)
        s.dim_h(mid-half, mid+half, base_y+11, f'{wid:.2f}', ext=base_y, below=True)
        s.dim_v(base_y-bz-ch*SS, base_y, mid+half+9, f'{bz/SS+ch:.2f}',
                ext=mid+half, left=False)
        s.text(mid, base_y+17, lab, 2.4, font='hebo', align=1)
    s.dim_v(base_y-base*SS, base_y, cx+4, f'{base:.2f}', ext=cx+20-1.05/2*SS)
    s.text(cx, base_y+26,
           'The dome is struck from the edge of the stroke, so a narrow stroke', 2.3, (.3, .3, .3))
    s.text(cx, base_y+30,
           'runs out of width before full height and the two faces meet in a', 2.3, (.3, .3, .3))
    s.text(cx, base_y+34,
           'ridge. That ridge is correct and must not be flattened or blended.', 2.3, (.3, .3, .3))

    # ============ DETAIL B : the dome profile
    dx0, dy0 = 292, 30
    s.text(dx0, dy0, 'DETAIL B', 3.1, font='hebo')
    s.text(dx0+22, dy0, 'DOME PROFILE', 2.6, (.35, .35, .35))
    s.text(dx0, dy0+4.5, 'struck from the edge of every stroke', 2.3, (.35, .35, .35))
    PS = 26.0
    gx, gy = dx0+8, dy0+60
    s.line(gx-4, gy, gx+inset*PS+10, gy, (0, 0, 0), THIN, CHAIN)
    s.line(gx, gy+5, gx, gy-height*PS-6, (0, 0, 0), THIN, CHAIN)
    s.poly([(gx+(inset*i/80)*PS,
             gy-height*math.sqrt(max(0.0, 1-(1-(inset*i/80)/inset)**2))*PS)
            for i in range(81)], w=THICK)
    s.line(gx, gy, gx, gy-height*PS, (0, 0, 0), THIN, DASH)
    s.line(gx, gy-height*PS, gx+inset*PS, gy-height*PS, (0, 0, 0), THIN, DASH)
    s.dim_h(gx, gx+inset*PS, gy+11, f'{inset:.2f}', ext=gy, below=True)
    s.text(gx+inset*PS/2, gy+15, 'INSET TO FULL HEIGHT', 2.2, (.35, .35, .35), align=1)
    s.dim_v(gy-height*PS, gy, gx+inset*PS+11, f'{height:.2f}', ext=gx+inset*PS, left=False)
    s.text(gx-2, gy+4.5, 'EDGE OF STROKE', 2.2, (.35, .35, .35))
    s.text(dx0, gy+22,
           f'z = {height:.2f} x sqrt( 1 - (1 - d / {inset:.2f})^2 )', 2.6)
    s.text(dx0, gy+26.5,
           f'for d <= {inset:.2f} mm;  z = {height:.2f} beyond.  d is measured',
           2.3, (.3, .3, .3))
    s.text(dx0, gy+30.5, 'in plan from the edge of the stroke.', 2.3, (.3, .3, .3))

    # ============ CROWN TABLE
    tx, ty = 292, gy+44
    s.text(tx, ty-4.5, 'CROWN HEIGHT BY STROKE WIDTH', 3.1, font='hebo')
    s.rect(tx, ty, tx+114, ty+5.8, w=MED, fill=(.9, .9, .9))
    s.text(tx+2.5, ty+4, 'STROKE WIDTH', 2.3, font='hebo')
    s.text(tx+42, ty+4, 'CROWN', 2.3, font='hebo')
    s.text(tx+66, ty+4, 'NOTE', 2.3, font='hebo')
    yy = ty+5.8
    for w_, note in [(1.05, 'thinnest in artwork'), (1.50, ''), (2.00, ''),
                     (2.37, 'thickest in artwork'), (2.50, 'full height from here')]:
        s.rect(tx, yy, tx+114, yy+5.4, w=THIN)
        s.text(tx+2.5, yy+3.8, f'{w_:.2f}', 2.3)
        s.text(tx+42, yy+3.8, f'{crown(w_, inset, height):.2f}', 2.3)
        s.text(tx+66, yy+3.8, note, 2.2, (.35, .35, .35))
        yy += 5.4

    # ============ NOTES
    ny = yy+9
    s.text(tx, ny, 'NOTES', 3.1, font='hebo'); ny += 5.5
    for i, t in enumerate([
        'All dimensions in millimetres. Do not scale from this drawing.',
        'Six separate bodies. They do not touch and must not be joined.',
        'Outline is fixed. No stroke may be thinned; 1.05 mm is the '
        'minimum and is already at the limit.',
        'Top surface domed per DETAIL B. Underside flat, no draft.',
        'Finish satin silver, uniform. No polished or mirror areas.',
        'Geometry of record is the STL: paco-logo-dome1.50-base0.30.stl',
        'General tolerance +/-0.05. Crown height +/-0.10.',
    ]):
        s.text(tx, ny, str(i+1), 2.3, font='hebo')
        for j, ln in enumerate(wrap(t, 54)):
            s.text(tx+4.5, ny + j*3.8, ln, 2.3)
        ny += 3.8*len(wrap(t, 54)) + 1.4

    # ============ TITLE BLOCK
    TX0, TY0, TX1, TY1 = 256, 247, 406, 283
    s.rect(TX0, TY0, TX1, TY1, w=THICK)
    for yy_ in (TY0+12, TY0+19, TY0+26):
        s.line(TX0, yy_, TX1, yy_, w=MED)
    s.line(TX0+96, TY0, TX0+96, TY1, w=MED)
    s.line(TX0+96, TY0+6, TX1, TY0+6, w=MED)
    s.text(TX0+3, TY0+8.5, 'PA & CO   LOGO, DOMED', 4.4, font='hebo')
    def cell(x, y, k, v, kw=2.0, vw=2.5):
        s.text(x, y, k, kw, (.4, .4, .4))
        s.text(x+20, y, v, vw)
    cell(TX0+3, TY0+16.5, 'MATERIAL', 'per supplier')
    cell(TX0+3, TY0+23.5, 'FINISH', 'satin silver')
    cell(TX0+3, TY0+30.5, 'OVERALL', f'{W:.2f} x {H:.2f} x {total:.2f}')
    cell(TX0+56, TY0+16.5, 'UNITS', 'mm')
    cell(TX0+56, TY0+23.5, 'MIN STROKE', '1.05')
    cell(TX0+56, TY0+30.5, 'TOLERANCE', '+/-0.05')
    s.text(TX0+99, TY0+4.3, 'THIRD ANGLE', 2.0, (.4, .4, .4))
    cell(TX0+99, TY0+10.5, 'DWG NO.', 'PACO-3D-01', 2.0, 2.4)
    cell(TX0+99, TY0+16.5, 'SCALE', 'AS NOTED', 2.0, 2.4)
    cell(TX0+99, TY0+23.5, 'SHEET', '1 OF 1', 2.0, 2.4)
    cell(TX0+99, TY0+30.5, 'REV', 'A', 2.0, 2.4)

    s.doc.save(out)
    return s.doc, total


def wrap(t, n):
    words, lines, cur = t.split(), [], ''
    for w in words:
        if len(cur)+len(w)+1 > n:
            lines.append(cur); cur = w
        else:
            cur = (cur+' '+w).strip()
    if cur:
        lines.append(cur)
    return lines


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default='assets/paco/paco-50mm-min1mm-FINAL.pdf')
    a.add_argument('--iso', required=True)
    a.add_argument('--inset', type=float, default=1.25)
    a.add_argument('--height', type=float, default=1.80)
    a.add_argument('--base', type=float, default=0.30)
    a.add_argument('--out', default='assets/paco/paco-production-drawing.pdf')
    a.add_argument('--png')
    o = a.parse_args()
    doc, total = build(o.src, o.inset, o.height, o.base, o.iso, o.out)
    print(f'{o.out}: A3 landscape, part {total:.2f} mm thick')
    if o.png:
        doc[0].get_pixmap(matrix=pymupdf.Matrix(2.6, 2.6)).save(o.png)
        print('   preview', o.png)
