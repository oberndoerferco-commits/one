#!/usr/bin/env python3
"""Lay one vector tile end to end into a border of any length.

The tile is a page holding exactly one period of the pattern, so the page
box -- not the ink box -- is what has to repeat: trimming to the ink first
would shorten the step by however much white the ends happen to carry, and
the border would creep. So the step comes from the page and the trim is
applied sideways only, where there is no repetition to break.

Anything the pattern crosses at the top of the tile it crosses identically
at the bottom, so the two edges abut exactly. Abutting exactly is not quite
enough: two coincident edges leave a hairline that a renderer shows and a
die would cut, so each tile is drawn a whisker taller than its step and
overlaps the next. The step itself stays exact, so nothing accumulates --
only the last fraction of a percent of each tile is doubled.
"""
import argparse, os, sys
import pymupdf

MM = 72.0 / 25.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tile', help='PDF holding one period, page = the period')
    ap.add_argument('out')
    ap.add_argument('-n', '--periods', type=int, default=8)
    ap.add_argument('--width-mm', type=float, default=None,
                    help='printed width of the inked part; default keeps the tile size')
    ap.add_argument('--margin', type=float, default=0.0,
                    help='white kept either side of the ink, in mm')
    ap.add_argument('--overlap', type=float, default=0.05,
                    help='how far each tile runs past its step, in points, so the '
                         'join closes instead of leaving a hairline')
    a = ap.parse_args()

    src = pymupdf.open(a.tile)
    page = src[0]
    step = page.rect.height                      # the period, from the page box
    ink = page.get_bboxlog()
    xs = [b[1][0] for b in ink] + [b[1][2] for b in ink]
    x0, x1 = (min(xs), max(xs)) if xs else (page.rect.x0, page.rect.x1)
    pad = a.margin * MM
    x0, x1 = max(page.rect.x0, x0 - pad), min(page.rect.x1, x1 + pad)
    clip = pymupdf.Rect(x0, 0, x1, step)

    scale = (a.width_mm * MM / clip.width) if a.width_mm else 1.0
    w, h = clip.width * scale, step * scale
    out = pymupdf.open()
    dst = out.new_page(width=w, height=h * a.periods)
    for k in range(a.periods):
        over = a.overlap if k < a.periods - 1 else 0.0
        dst.show_pdf_page(pymupdf.Rect(0, k * h, w, (k + 1) * h + over), src, 0, clip=clip)
    out.save(a.out, garbage=4, deflate=True)
    with open(os.path.splitext(a.out)[0] + '.svg', 'w', encoding='utf-8') as fh:
        fh.write(out[0].get_svg_image())
    print(f'{a.periods} x {h*25.4/72:.1f} mm = {h*a.periods*25.4/72:.1f} mm tall, '
          f'{w*25.4/72:.1f} mm wide -> {a.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
