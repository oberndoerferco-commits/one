#!/usr/bin/env python3
"""Lay one vector tile end to end into a border of any length.

The tile is a page holding exactly one period of the pattern, so the page
box -- not the ink box -- is what has to repeat: trimming to the ink first
would shorten the step by however much white the ends happen to carry, and
the border would creep. So the step comes from the page and the trim is
applied sideways only, where there is no repetition to break.

Anything the pattern crosses at the top of the tile it crosses identically
at the bottom, so the two edges meet. Meeting is not quite enough. A tracer
puts its contour on the iso-line, which at the edge of the raster sits a
fraction of a pixel inside it, so the ink stops just short of the page and
tile against tile leaves a hairline -- measured here at two rows, about a
tenth of a millimetre, which a renderer shows and a die would cut.

Closing it by drawing each tile a whisker taller does not work: that scales
the tile, and the shortfall scales with it. The step has to shorten instead.
Each tile is drawn at its own size and set down a hair less than a page
apart, so the ink of one laps over the ink of the next.
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
    ap.add_argument('--overlap', type=float, default=0.6,
                    help='how much the step is shortened, in points, so the ink of '
                         'one tile laps over the next instead of leaving a hairline')
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
    step0 = h - (a.overlap * scale if a.periods > 1 else 0.0)
    dst = out.new_page(width=w, height=step0 * (a.periods - 1) + h)
    step = h - (a.overlap * scale if a.periods > 1 else 0.0)
    for k in range(a.periods):
        dst.show_pdf_page(pymupdf.Rect(0, k * step, w, k * step + h), src, 0, clip=clip)
    out.save(a.out, garbage=4, deflate=True)
    with open(os.path.splitext(a.out)[0] + '.svg', 'w', encoding='utf-8') as fh:
        fh.write(out[0].get_svg_image())
    print(f'{a.periods} x {step*25.4/72:.2f} mm = {dst.rect.height*25.4/72:.1f} mm tall, '
          f'{w*25.4/72:.1f} mm wide -> {a.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
