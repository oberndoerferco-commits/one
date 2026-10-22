#!/usr/bin/env python3
"""Lay badges out on one sheet: same printed size, grouped by colour.

Each badge is scaled by its own artwork rather than its page, since one
with a ground fills its page and a bare cross does not, and they would
otherwise print at different sizes. The order runs round the colour wheel
with the near-neutrals kept together at the end.
"""
import argparse, colorsys, os, re, sys
import numpy as np, pymupdf

MM = 72.0 / 25.4


def profile(path, dpi=300, n=3):
    """(doc, ink box in pt, the few colours it is mostly made of)"""
    d = pymupdf.open(path)
    pm = d[0].get_pixmap(dpi=dpi, alpha=False)
    a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    ink = a.min(-1) < 238
    v = a[ink]
    q = (v // 8).astype(np.int64)
    ks, cnt = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    cols = []
    for i in np.argsort(-cnt)[:n]:
        k = int(ks[i])
        c = np.array([(k >> 16) & 255, (k >> 8) & 255, k & 255]) * 8 + 4
        cols.append((tuple(int(x) for x in c), cnt[i] / ink.sum()))
    ys, xs = np.nonzero(ink)
    box = (xs.min() * 72 / dpi, ys.min() * 72 / dpi,
           (xs.max() + 1) * 72 / dpi, (ys.max() + 1) * 72 / dpi)
    return d, box, cols


def order_key(cols, bins=24):
    """The badge's own colour: the most of it that is not a near-neutral.

    Sorting on the commonest colour alone puts a white cross on black beside
    a white cross on pink. What the eye groups by is the colour the badge
    actually is, so a near-neutral only counts when the whole badge is one.
    """
    for c, _ in cols:
        h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in c])
        if s > 0.25 and v > 0.12:
            return (0, round(h * bins) / bins, -v, -s)
    return (1, 0, -max(cols[0][0]) / 255, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('out_pdf')
    ap.add_argument('--size-mm', type=float, default=30.0)
    ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--gap-mm', type=float, default=5.0)
    ap.add_argument('--no-sort', action='store_true')
    a = ap.parse_args()

    fs = sorted([f for f in os.listdir(a.dir) if re.match(r'badge-\d+\.pdf$', f)],
                key=lambda f: int(re.findall(r'\d+', f)[0]))
    items = []
    for f in fs:
        d, box, cols = profile(os.path.join(a.dir, f))
        items.append((order_key(cols), f, d, box))
    if not a.no_sort:
        items.sort(key=lambda t: t[0])

    W = a.size_mm * MM
    gap = pad = a.gap_mm * MM
    rows = (len(items) + a.cols - 1) // a.cols
    out = pymupdf.open()
    pg = out.new_page(width=pad * 2 + a.cols * W + (a.cols - 1) * gap,
                      height=pad * 2 + rows * W + (rows - 1) * gap)
    for i, (_, f, d, b) in enumerate(items):
        s = W / max(b[2] - b[0], b[3] - b[1])
        cx = pad + W / 2 + (i % a.cols) * (W + gap)
        cy = pad + W / 2 + (i // a.cols) * (W + gap)
        w, h = d[0].rect.width * s, d[0].rect.height * s
        pg.show_pdf_page(pymupdf.Rect(cx - (b[0] + b[2]) / 2 * s,
                                      cy - (b[1] + b[3]) / 2 * s,
                                      cx - (b[0] + b[2]) / 2 * s + w,
                                      cy - (b[1] + b[3]) / 2 * s + h), d, 0)
    out.save(a.out_pdf, garbage=4, deflate=True)
    print(f'{len(items)} badges at {a.size_mm:g} mm, sheet '
          f'{pg.rect.width:.0f} x {pg.rect.height:.0f} pt -> {a.out_pdf}',
          file=sys.stderr)


if __name__ == '__main__':
    main()
