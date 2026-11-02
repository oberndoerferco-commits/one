#!/usr/bin/env python3
"""Set the PA & CO logo to a given width, close the O's bar, and dimension it.

Three things, from the artwork's own geometry rather than from a ruler held
up to a screenshot: the mark scaled so its overall width is what was asked
for, a stem added to join the bar under the O to the O itself, and a sheet
that measures every piece.

The bar hangs free in the original, a little under a millimetre below the
O. The stem that closes that gap is set at the O's horizontal centre, which
on a round letter is also where its lowest point falls, so the two meet
without a notch; it runs a hair into both so no hairline can open between
them at any resolution.

Every number on the sheet is read off the paths. The cap height is taken
from the P, whose top and bottom are flat: the round letters overshoot it
at both ends, as drawn type always does, and quoting one of those as the
cap height would have everything else set a sixth of a millimetre low.
"""
import argparse, os, sys
import pymupdf

MM = 72.0 / 25.4
NAMES = ['diamond', 'P', 'A', '&', 'C', 'O', 'bar under O']


def geometry(src):
    doc = pymupdf.open(src)
    page = doc[0]
    rects = [d['rect'] for d in page.get_drawings()]
    whole = rects[0]
    for r in rects[1:]:
        whole = whole | r
    return doc, page, rects, whole


def line(page, p0, p1, w=0.35, col=(0, 0, 0)):
    page.draw_line(pymupdf.Point(*p0), pymupdf.Point(*p1), color=col, width=w)


def arrow(page, tip, d, size=1.6 * MM, col=(0, 0, 0)):
    """A small solid arrowhead at `tip`, pointing along d = (+1|-1, 0) or (0, ±1)."""
    dx, dy = d
    bx, by = tip[0] - dx * size, tip[1] - dy * size
    px, py = -dy * size * 0.30, dx * size * 0.30
    page.draw_polyline([pymupdf.Point(*tip), pymupdf.Point(bx + px, by + py),
                        pymupdf.Point(bx - px, by - py)],
                       color=None, fill=col, closePath=True)


def dim_h(page, x0, x1, y, text, tick=2.2 * MM, size=7, col=(0, 0, 0)):
    line(page, (x0, y - tick), (x0, y + tick), 0.3, col)
    line(page, (x1, y - tick), (x1, y + tick), 0.3, col)
    line(page, (x0, y), (x1, y), 0.35, col)
    arrow(page, (x0, y), (-1, 0), col=col)
    arrow(page, (x1, y), (1, 0), col=col)
    w = pymupdf.get_text_length(text, 'Helvetica', size)
    cx = (x0 + x1) / 2
    page.draw_rect(pymupdf.Rect(cx - w / 2 - 1.2, y - size * 0.46 - 1.0,
                                cx + w / 2 + 1.2, y + size * 0.46 + 1.0),
                   color=None, fill=(1, 1, 1))
    page.insert_text(pymupdf.Point(cx - w / 2, y + size * 0.36), text,
                     fontname='Helvetica', fontsize=size, color=col)


def dim_v(page, y0, y1, x, text, tick=2.2 * MM, size=7, col=(0, 0, 0), align='center'):
    line(page, (x - tick, y0), (x + tick, y0), 0.3, col)
    line(page, (x - tick, y1), (x + tick, y1), 0.3, col)
    line(page, (x, y0), (x, y1), 0.35, col)
    arrow(page, (x, y0), (0, -1), col=col)
    arrow(page, (x, y1), (0, 1), col=col)
    w = pymupdf.get_text_length(text, 'Helvetica', size)
    cy = (y0 + y1) / 2
    # a long label hung off the line rather than centred on it, so it cannot
    # reach back over the drawing
    tx = x - w / 2 if align == 'center' else x + 1.6 * MM
    page.draw_rect(pymupdf.Rect(tx - 1.2, cy - size * 0.46 - 1.0,
                                tx + w + 1.2, cy + size * 0.46 + 1.0),
                   color=None, fill=(1, 1, 1))
    page.insert_text(pymupdf.Point(tx, cy + size * 0.36), text,
                     fontname='Helvetica', fontsize=size, color=col)


def place(page, src_doc, whole, rects, at, scale, stem_mm, gap_units, unit):
    """Draw the mark at `at` (top-left, points), `scale` points per source unit."""
    page.show_pdf_page(pymupdf.Rect(at[0], at[1],
                                    at[0] + whole.width * scale,
                                    at[1] + whole.height * scale),
                       src_doc, 0, clip=whole)
    if stem_mm <= 0:
        return None
    O, bar = rects[5], rects[6]
    cx = (O.x0 + O.x1) / 2
    half = stem_mm * MM / scale / 2
    bleed = gap_units * 0.08
    r = pymupdf.Rect(cx - half, O.y1 - bleed, cx + half, bar.y0 + bleed)
    out = pymupdf.Rect(at[0] + (r.x0 - whole.x0) * scale, at[1] + (r.y0 - whole.y0) * scale,
                       at[0] + (r.x1 - whole.x0) * scale, at[1] + (r.y1 - whole.y0) * scale)
    page.draw_rect(out, color=None, fill=(0, 0, 0))
    return out


def sheet(doc, rects, whole, unit, stem_mm, gap_u, width_mm, rows, path):
    """A dimensioned sheet: the mark at full size, a detail of the join, a table."""
    out = pymupdf.open()
    pg = out.new_page(width=297 * MM, height=210 * MM)
    sc = unit * MM                                   # points per source unit
    W, H = whole.width * sc, whole.height * sc
    ox, oy = 26 * MM, 52 * MM
    place(pg, doc, whole, rects, (ox, oy), sc, stem_mm, gap_u, unit)

    def X(u):
        return ox + (u - whole.x0) * sc

    def Y(u):
        return oy + (u - whole.y0) * sc

    grey = (0.55, 0.55, 0.55)
    # witness lines
    for xv in (whole.x0, whole.x1):
        line(pg, (X(xv), oy + H + 2 * MM), (X(xv), oy + H + 13 * MM), 0.25, grey)
    for yv in (whole.y0, whole.y1):
        line(pg, (ox - 2 * MM, Y(yv)), (ox - 15 * MM, Y(yv)), 0.25, grey)
    dim_h(pg, X(whole.x0), X(whole.x1), oy + H + 10 * MM, f'{width_mm:.2f} mm')
    dim_v(pg, Y(whole.y0), Y(whole.y1), ox - 12 * MM, f'{whole.height*unit:.2f} mm')

    dia, P, O, bar = rects[0], rects[1], rects[5], rects[6]
    for xv in (dia.x0, dia.x1):
        line(pg, (X(xv), oy - 2 * MM), (X(xv), oy - 10 * MM), 0.25, grey)
    dim_h(pg, X(dia.x0), X(dia.x1), oy - 7 * MM, f'{dia.width*unit:.2f} mm')
    dim_v(pg, Y(dia.y0), Y(dia.y1), X(dia.x1) + 7 * MM, f'{dia.height*unit:.2f} mm')
    line(pg, (X(dia.x1), Y(dia.y0)), (X(dia.x1) + 9 * MM, Y(dia.y0)), 0.25, grey)
    line(pg, (X(dia.x1), Y(dia.y1)), (X(dia.x1) + 9 * MM, Y(dia.y1)), 0.25, grey)

    wl = rects[1] | rects[2] | rects[3] | rects[4] | rects[5]
    dim_v(pg, Y(P.y0), Y(P.y1), ox + W + 10 * MM,
          f'{P.height*unit:.2f} mm  cap height, from the P', align='right')
    line(pg, (ox + W + 2 * MM, Y(P.y0)), (ox + W + 12 * MM, Y(P.y0)), 0.25, grey)
    line(pg, (ox + W + 2 * MM, Y(P.y1)), (ox + W + 12 * MM, Y(P.y1)), 0.25, grey)
    dim_v(pg, Y(dia.y1), Y(wl.y0), ox + W + 10 * MM,
          f'{(wl.y0-dia.y1)*unit:.2f} mm  clearance', align='right')
    line(pg, (X(dia.x1), Y(dia.y1)), (ox + W + 12 * MM, Y(dia.y1)), 0.25, grey)
    line(pg, (ox + W + 2 * MM, Y(wl.y0)), (ox + W + 12 * MM, Y(wl.y0)), 0.25, grey)

    # ---- detail of the join, 4:1
    dsc = sc * 4
    box = pymupdf.Rect(O.x0 - 10, O.y0 - 10, O.x1 + 10, bar.y1 + 14)
    dx, dy = 30 * MM, 118 * MM
    pg.show_pdf_page(pymupdf.Rect(dx, dy, dx + box.width * dsc, dy + box.height * dsc),
                     doc, 0, clip=box)
    cx = (O.x0 + O.x1) / 2
    half = stem_mm * MM / sc / 2
    bl = gap_u * 0.08
    pg.draw_rect(pymupdf.Rect(dx + (cx - half - box.x0) * dsc, dy + (O.y1 - bl - box.y0) * dsc,
                              dx + (cx + half - box.x0) * dsc, dy + (bar.y0 + bl - box.y0) * dsc),
                 color=None, fill=(0, 0, 0))
    sy0, sy1 = dy + (O.y1 - box.y0) * dsc, dy + (bar.y0 - box.y0) * dsc
    sx0, sx1 = dx + (cx - half - box.x0) * dsc, dx + (cx + half - box.x0) * dsc
    dim_h(pg, sx0, sx1, sy1 + 13 * MM, f'{stem_mm:.2f} mm wide', tick=1.6 * MM, size=6.5)
    line(pg, (sx0, sy1), (sx0, sy1 + 14 * MM), 0.25, grey)
    line(pg, (sx1, sy1), (sx1, sy1 + 14 * MM), 0.25, grey)
    dim_v(pg, sy0, sy1, sx1 + 16 * MM, f'{gap_u*unit:.2f} mm gap, now bridged',
          tick=1.6 * MM, size=6.5, align='right')
    line(pg, (sx1, sy0), (sx1 + 18 * MM, sy0), 0.25, grey)
    line(pg, (sx1, sy1), (sx1 + 18 * MM, sy1), 0.25, grey)
    pg.insert_text(pymupdf.Point(dx, dy - 5 * MM), 'the stem joining the bar to the O, at 4:1',
                   fontname='Helvetica-Bold', fontsize=8)

    # ---- table
    tx, ty = 150 * MM, 26 * MM
    pg.insert_text(pymupdf.Point(tx, ty - 5 * MM), 'every piece, in millimetres',
                   fontname='Helvetica-Bold', fontsize=8)
    cols = [0, 34 * MM, 54 * MM, 76 * MM, 98 * MM]
    head = ['', 'width', 'height', 'from left', 'from top']
    for c, h in zip(cols, head):
        pg.insert_text(pymupdf.Point(tx + c, ty), h, fontname='Helvetica-Bold',
                       fontsize=7, color=grey)
    line(pg, (tx, ty + 1.6 * MM), (tx + 118 * MM, ty + 1.6 * MM), 0.4)
    y = ty + 6.5 * MM
    for n, w, h, x0, y0 in rows:
        pg.insert_text(pymupdf.Point(tx, y), n, fontname='Helvetica', fontsize=7.5)
        for c, v in zip(cols[1:], (w, h, x0, y0)):
            t = f'{v:.2f}'
            pg.insert_text(pymupdf.Point(tx + c + 14 * MM -
                                         pymupdf.get_text_length(t, 'Helvetica', 7.5), y),
                           t, fontname='Helvetica', fontsize=7.5)
        y += 5.0 * MM
    line(pg, (tx, y - 3.4 * MM), (tx + 118 * MM, y - 3.4 * MM), 0.4)
    y += 2 * MM
    for note in (f'cap height is taken from the P, whose top and bottom are flat.',
                 f'C and O overshoot it by {(rects[4].height-rects[1].height)*unit/2:.2f} mm '
                 f'top and bottom, as drawn type does.',
                 f'the A overshoots by {(rects[2].height-rects[1].height)*unit/2:.2f} mm.',
                 f'from left and from top are to each piece\'s own top-left corner.'):
        pg.insert_text(pymupdf.Point(tx, y), note, fontname='Helvetica-Oblique',
                       fontsize=6.5, color=grey)
        y += 3.6 * MM

    pg.insert_text(pymupdf.Point(26 * MM, 20 * MM), 'PA & CO', fontname='Helvetica-Bold',
                   fontsize=15)
    pg.insert_text(pymupdf.Point(26 * MM, 27 * MM),
                   f'set to {width_mm:g} mm overall width; drawing at 1:1, measure it',
                   fontname='Helvetica', fontsize=8, color=grey)
    out.save(path, garbage=4, deflate=True)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_dir')
    ap.add_argument('--width-mm', type=float, default=50.0)
    ap.add_argument('--stem-mm', type=float, default=1.0,
                    help='thickness of the line joining the bar to the O')
    ap.add_argument('--name', default='paco')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    doc, page, rects, whole = geometry(a.src)
    unit = a.width_mm / whole.width            # mm per source unit
    scale = unit * MM                          # points per source unit
    W, H = whole.width * scale, whole.height * scale
    gap_u = rects[6].y0 - rects[5].y1

    # ---- the artwork itself, trimmed to the ink
    art = pymupdf.open()
    pg = art.new_page(width=W, height=H)
    place(pg, doc, whole, rects, (0, 0), scale, a.stem_mm, gap_u, unit)
    f = os.path.join(a.out_dir, f'{a.name}-{a.width_mm:g}mm.pdf')
    art.save(f, garbage=4, deflate=True)
    with open(f[:-4] + '.svg', 'w', encoding='utf-8') as fh:
        fh.write(art[0].get_svg_image())
    print(f'{f}  {a.width_mm:g} x {whole.height*unit:.2f} mm', file=sys.stderr)

    rows = [(n, r.width * unit, r.height * unit,
             (r.x0 - whole.x0) * unit, (r.y0 - whole.y0) * unit)
            for n, r in zip(NAMES, rects)]
    rows.append(('stem (added)', a.stem_mm, gap_u * unit,
                 ((rects[5].x0 + rects[5].x1) / 2 - whole.x0) * unit - a.stem_mm / 2,
                 (rects[5].y1 - whole.y0) * unit))

    g = os.path.join(a.out_dir, f'{a.name}-measurements.pdf')
    sheet(doc, rects, whole, unit, a.stem_mm, gap_u, a.width_mm, rows, g)
    print(f'{g}  A4 landscape, drawing at 1:1', file=sys.stderr)
    for n, w, h, x0, y0 in rows:
        print(f'  {n:14s} {w:7.2f} x {h:7.2f} mm   at ({x0:6.2f}, {y0:6.2f})',
              file=sys.stderr)


if __name__ == '__main__':
    main()
