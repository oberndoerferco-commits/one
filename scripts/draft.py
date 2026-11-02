"""Dimension lines, arrowheads and labels for a drawing laid out in millimetres."""
import pymupdf

MM = 72.0 / 25.4
GREY = (0.55, 0.55, 0.55)


def line(page, p0, p1, w=0.35, col=(0, 0, 0), dash=None):
    page.draw_line(pymupdf.Point(*p0), pymupdf.Point(*p1), color=col, width=w, dashes=dash)


def arrow(page, tip, d, size=1.5 * MM, col=(0, 0, 0)):
    dx, dy = d
    bx, by = tip[0] - dx * size, tip[1] - dy * size
    px, py = -dy * size * 0.30, dx * size * 0.30
    page.draw_polyline([pymupdf.Point(*tip), pymupdf.Point(bx + px, by + py),
                        pymupdf.Point(bx - px, by - py)], color=None, fill=col,
                       closePath=True)


def _label(page, x, y, text, size, col, anchor='center'):
    w = pymupdf.get_text_length(text, 'Helvetica', size)
    tx = {'center': x - w / 2, 'right': x + 1.4 * MM, 'left': x - w - 1.4 * MM}[anchor]
    page.draw_rect(pymupdf.Rect(tx - 1.1, y - size * 0.46 - 0.9,
                                tx + w + 1.1, y + size * 0.46 + 0.9),
                   color=None, fill=(1, 1, 1))
    page.insert_text(pymupdf.Point(tx, y + size * 0.35), text,
                     fontname='Helvetica', fontsize=size, color=col)


def dim_h(page, x0, x1, y, text, size=6.5, col=(0, 0, 0), anchor='center', tick=1.8 * MM):
    line(page, (x0, y - tick), (x0, y + tick), 0.3, col)
    line(page, (x1, y - tick), (x1, y + tick), 0.3, col)
    line(page, (x0, y), (x1, y), 0.35, col)
    if x1 - x0 > 7 * MM:
        arrow(page, (x0, y), (-1, 0), col=col)
        arrow(page, (x1, y), (1, 0), col=col)
    _label(page, (x0 + x1) / 2, y, text, size, col, anchor)


def dim_v(page, y0, y1, x, text, size=6.5, col=(0, 0, 0), anchor='center', tick=1.8 * MM):
    line(page, (x - tick, y0), (x + tick, y0), 0.3, col)
    line(page, (x - tick, y1), (x + tick, y1), 0.3, col)
    line(page, (x, y0), (x, y1), 0.35, col)
    if y1 - y0 > 7 * MM:
        arrow(page, (x, y0), (0, -1), col=col)
        arrow(page, (x, y1), (0, 1), col=col)
    _label(page, x, (y0 + y1) / 2, text, size, col, anchor)


def witness(page, p0, p1):
    line(page, p0, p1, 0.22, GREY)


def note(page, x, y, lines, size=6.5, lead=3.5 * MM, col=GREY, bold_first=False):
    for i, t in enumerate(lines):
        f = 'Helvetica-Bold' if (bold_first and i == 0) else 'Helvetica-Oblique'
        page.insert_text(pymupdf.Point(x, y), t, fontname=f, fontsize=size,
                         color=(0, 0, 0) if (bold_first and i == 0) else col)
        y += lead
    return y


def title(page, x, y, main, sub=None):
    page.insert_text(pymupdf.Point(x, y), main, fontname='Helvetica-Bold', fontsize=13)
    if sub:
        page.insert_text(pymupdf.Point(x, y + 6.5 * MM), sub, fontname='Helvetica',
                         fontsize=8, color=GREY)
