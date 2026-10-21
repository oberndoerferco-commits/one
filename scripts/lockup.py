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
    ap.add_argument('--size-mm', type=float, default=30.0)
    ap.add_argument('--gap-mm', type=float, default=5.0)
    ap.add_argument('--text-under', type=float, default=380.0,
                    help='the wordmark belongs to badges right of this')
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

    # Each badge fills its 30 mm page differently -- one with a square
    # ground, one with a circle, one a bare cross -- so laying them out at
    # their page size leaves the artwork itself unequal. Scale each by its
    # own ink instead, sit them on one centre line, and space them evenly.
    ink = []
    for f in a.badges:
        d = pymupdf.open(f)
        pm = d[0].get_pixmap(dpi=600, alpha=False)
        arr = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
        ys, xs = np.nonzero(arr.min(-1) < 238)
        ink.append((xs.min() * 72 / 600, ys.min() * 72 / 600,
                    (xs.max() + 1) * 72 / 600, (ys.max() + 1) * 72 / 600,
                    d[0].rect.width, d[0].rect.height))

    W = a.size_mm * MM
    gap = a.gap_mm * MM
    pitch = W + gap
    n = len(a.badges)
    cy = W / 2 + a.pad
    placed = []
    for i, (bx0, by0, bx1, by1, pw, ph) in enumerate(ink):
        s_ = W / max(bx1 - bx0, by1 - by0)          # its own artwork to size
        cx = a.pad + W / 2 + i * pitch
        w, h = pw * s_, ph * s_
        x = cx - (bx0 + bx1) / 2 * s_
        y = cy - (by0 + by1) / 2 * s_
        placed.append((x, y, w, h))

    # keep the wordmark where it sits under the badges it belongs to
    keep = [i for i, b in enumerate(boxes) if b[0] >= a.text_under]
    if keep:
        dx = np.mean([placed[i][0] + (ink[i][0] * (W / max(ink[i][2] - ink[i][0],
                      ink[i][3] - ink[i][1]))) - boxes[i][0] for i in keep])
        dy = np.mean([placed[i][1] + (ink[i][1] * (W / max(ink[i][2] - ink[i][0],
                      ink[i][3] - ink[i][1]))) - boxes[i][1] for i in keep])
        sc = np.mean([W / (boxes[i][2] - boxes[i][0]) for i in keep])
    else:
        dx = dy = 0.0; sc = 1.0
    ax = np.mean([(boxes[i][0] + boxes[i][2]) / 2 for i in keep]) if keep else 0
    ay = np.mean([(boxes[i][1] + boxes[i][3]) / 2 for i in keep]) if keep else 0
    bx = np.mean([placed[i][0] + placed[i][2] / 2 for i in keep]) if keep else 0
    by = cy
    TX = lambda q: ((q[0] - ax) * sc + bx, (q[1] - ay) * sc + by)

    pw_total = a.pad * 2 + n * W + (n - 1) * gap
    tp = [TX(q) for sh in gl for sp in sh for op, p in sp
          for q in ([p] if op != 'C' else p)]
    ph_total = max([p[1] + p[3] for p in placed] + [max(q[1] for q in tp)]) + a.pad

    out = pymupdf.open()
    pg = out.new_page(width=pw_total, height=ph_total)
    for f, (x, y, w, h) in zip(a.badges, placed):
        d = pymupdf.open(f)
        pg.show_pdf_page(pymupdf.Rect(x, y, x + w, y + h), d, 0)
    col = [int(a.text_fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    for sh in gl:
        s = pg.new_shape()
        emit(s, [[(op, TX(p)) if op != 'C' else (op, [TX(q) for q in p])
                  for op, p in sp] for sp in sh], 1.0, 1.0)
        s.finish(color=None, fill=col, even_odd=True, closePath=True, width=0)
        s.commit()
    x1 = pw_total; x0 = 0; y1 = ph_total; y0 = 0
    out.save(a.out_pdf, garbage=4, deflate=True)
    print(f'{a.out_pdf}: {x1-x0:.1f} x {y1-y0:.1f} pt '
          f'({(x1-x0)/MM:.1f} x {(y1-y0)/MM:.1f} mm)', file=sys.stderr)


if __name__ == '__main__':
    main()
