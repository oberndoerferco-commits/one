#!/usr/bin/env python3
"""Compose a lockup: vector badges with the curved wordmark around them.

The wordmark is live text in the page, so it is taken as real glyph
outlines rather than traced. Clipping the page behind the badges instead
leaves the original raster showing round the edges of the vector ones.
"""
import argparse, os, re, sys
import numpy as np, pymupdf
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vectorize import parse_svg, emit, NUM                      # noqa: E402

MM = 72.0 / 25.4


def glyphs(page, fill):
    """Every glyph of one colour, as page-space outlines."""
    svg = page.get_svg_image(text_as_path=True)
    defs = dict(re.findall(r'<path id="(font_[0-9_]+)" d="([^"]+)"', svg))
    out = []
    for m in re.finditer(r'<use[^>]*xlink:href="#(font_[0-9_]+)"[^>]*'
                         r'transform="matrix\(([^)]*)\)"[^>]*fill="([^"]+)"', svg):
        gid, mat, col = m.group(1), m.group(2), m.group(3)
        if col.lower() != fill.lower() or gid not in defs:
            continue
        a, b, c, d, e, f = [float(v) for v in NUM.findall(mat)][:6]
        T = lambda p: (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)
        for sub in parse_svg(f'<path d="{defs[gid]}" fill="{col}"/>'):
            out.append([[(op, T(p) if op != 'C' else [T(q) for q in p])
                         for op, p in sp] for sp in sub])
    return out


def ink_boxes(page, dpi=300, floor=8000):
    pm = page.get_pixmap(dpi=dpi, alpha=False)
    a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    L, n = ndi.label(ndi.binary_closing(a.min(-1) < 236, np.ones((7, 7))))
    out = []
    for i, sl in enumerate(ndi.find_objects(L), 1):
        if sl and (L[sl] == i).sum() > floor:
            out.append((sl[1].start * 72 / dpi, sl[0].start * 72 / dpi,
                        sl[1].stop * 72 / dpi, sl[0].stop * 72 / dpi))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_pdf')
    ap.add_argument('badges', nargs='+', help='vector badge PDFs, left to right')
    ap.add_argument('--page', type=int, default=1)
    ap.add_argument('--text-fill', default='#25754a')
    ap.add_argument('--min-x', type=float, default=0.0,
                    help='ignore ink left of this; 0 keeps the whole row')
    ap.add_argument('--pad', type=float, default=4.0)
    a = ap.parse_args()

    doc = pymupdf.open(a.src)
    page = doc[a.page]
    boxes = [b for b in ink_boxes(page) if b[0] >= a.min_x]
    gl = glyphs(page, a.text_fill)
    pts = [p for sh in gl for sp in sh for op, p in sp
           for p in ([p] if op != 'C' else p)]
    gx0 = min(q[0] for q in pts); gx1 = max(q[0] for q in pts)
    gy0 = min(q[1] for q in pts); gy1 = max(q[1] for q in pts)
    print(f'{len(boxes)} badges, {len(gl)} glyphs', file=sys.stderr)

    x0 = min([b[0] for b in boxes] + [gx0]) - a.pad
    y0 = min([b[1] for b in boxes] + [gy0]) - a.pad
    x1 = max([b[2] for b in boxes] + [gx1]) + a.pad
    y1 = max([b[3] for b in boxes] + [gy1]) + a.pad

    out = pymupdf.open()
    pg = out.new_page(width=x1 - x0, height=y1 - y0)
    for f, b in zip(a.badges, boxes):
        d = pymupdf.open(f)
        pg.show_pdf_page(pymupdf.Rect(b[0] - x0, b[1] - y0,
                                      b[0] - x0 + d[0].rect.width,
                                      b[1] - y0 + d[0].rect.height), d, 0)
    col = [int(a.text_fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    for sh in gl:
        s = pg.new_shape()
        emit(s, [[(op, (p[0] - x0, p[1] - y0)) if op != 'C'
                  else (op, [(q[0] - x0, q[1] - y0) for q in p])
                  for op, p in sp] for sp in sh], 1.0, 1.0)
        s.finish(color=None, fill=col, even_odd=True, closePath=True, width=0)
        s.commit()
    out.save(a.out_pdf, garbage=4, deflate=True)
    print(f'{a.out_pdf}: {x1-x0:.1f} x {y1-y0:.1f} pt '
          f'({(x1-x0)/MM:.1f} x {(y1-y0)/MM:.1f} mm)', file=sys.stderr)


if __name__ == '__main__':
    main()
