#!/usr/bin/env python3
"""Trace a photograph or a photoreal render to vector.

This is a different job from vectorizing flat artwork, and worth being
honest about: a render made of gradients, soft shadows and texture has no
flat shapes in it to find. A tracer can only quantize it into bands of one
colour, so what comes back is a posterized illustration of the picture, not
the picture. The architecture survives it well -- straight edges, keylines,
lettering -- and the modelling does not.

Two things were measured rather than assumed:

  Colour precision carries the result. At 6 bits the spotlights collapse
  into hard-edged blobs; at 8 they still read as light. Mean error per
  channel falls 16.9 -> 12.3 -> 8.3 across 6, 7, 8 bits.

  Resolution carries none of it. Tracing the same picture upscaled 2x costs
  three to four times the file for no gain at all (44.2 MB at error 8.04
  against 9.8 MB at 8.31). The bands are set by the colour quantizing, not
  by the pixel grid, so the extra pixels only buy more points along the
  same edges. Flat artwork is the opposite case, where upscaling is what
  stops a hairline landing on a half pixel.

A slight blur first keeps JPEG grain from being traced as its own speckle.

One part of a shopfront is not like the rest: the lettering. It is flat
colour on flat colour, which is the case a tracer is good at, and it is the
part a reader actually looks at -- so --crisp re-traces a named box on its
own terms. Split in two by brightness, upscaled first so an edge can land
between pixels, it comes back with its serifs intact instead of chewed, and
is laid over the trace, which keeps the cast shadow underneath it.
"""
import argparse, os, sys, time
import numpy as np, pymupdf, vtracer
from PIL import Image
from scipy import ndimage as ndi


def crisp(im, box, zoom, speckle, corner):
    """That box as two flat colours: the lighter subject over what is behind.

    Split by brightness rather than by any named colour, so it holds for
    gold on grey or anything else set against its ground. The split is made
    on the upscaled picture, which is what lets an edge fall between two
    pixels instead of on one -- at this size a letter's stem is four pixels
    across and half a pixel of it is visible.
    """
    a = np.asarray(im.crop(box), float)
    lum = a.mean(-1)
    lo, hi = lum.min(), lum.max()
    t = (lo + hi) / 2                      # two means, run to convergence
    for _ in range(40):
        d = lum <= t
        if not d.any() or d.all():
            break
        nt = (lum[d].mean() + lum[~d].mean()) / 2
        if abs(nt - t) < 1e-3:
            break
        t = nt
    m = ndi.zoom(lum, zoom, order=3) > t
    m = ndi.binary_opening(ndi.binary_closing(m, np.ones((3, 3))), np.ones((3, 3)))
    if not m.any():
        return None, None
    fill = tuple(int(v) for v in np.median(a[lum > t], 0))
    return m, fill


def render(svg, w, h):
    doc = pymupdf.open(svg)
    page = doc[0]
    pm = page.get_pixmap(matrix=pymupdf.Matrix(w / page.rect.width,
                                               h / page.rect.height), alpha=False)
    return np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)[:h, :w]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_dir')
    ap.add_argument('--name', default=None)
    ap.add_argument('--colors', type=int, default=8, help='bits of colour precision')
    ap.add_argument('--layer-difference', type=int, default=8)
    ap.add_argument('--filter-speckle', type=int, default=3)
    ap.add_argument('--corner', type=int, default=60)
    ap.add_argument('--blur', type=float, default=0.7,
                    help='softens JPEG grain so it is not traced as speckle')
    ap.add_argument('--crisp', default='',
                    help='x0,y0,x1,y1 -- re-trace this box as flat two-tone art '
                         'and lay it over the trace; for lettering and signage')
    ap.add_argument('--crisp-zoom', type=int, default=6)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    stem = a.name or os.path.splitext(os.path.basename(a.src))[0]
    im = Image.open(a.src).convert('RGB')
    W, H = im.size
    ref = np.asarray(im, float)

    src = np.asarray(im, float)
    if a.blur > 0:
        src = np.dstack([ndi.gaussian_filter(src[..., i], a.blur) for i in range(3)])
    tmp = os.path.join(a.out_dir, f'.{stem}-input.png')
    Image.fromarray(src.astype(np.uint8)).save(tmp)

    svg = os.path.join(a.out_dir, f'{stem}.svg')
    t = time.time()
    vtracer.convert_image_to_svg_py(
        tmp, svg, colormode='color', hierarchical='stacked', mode='spline',
        color_precision=a.colors, layer_difference=a.layer_difference,
        filter_speckle=a.filter_speckle, corner_threshold=a.corner,
        length_threshold=4.0, splice_threshold=45)
    os.remove(tmp)

    out = pymupdf.open('pdf', pymupdf.open(svg).convert_to_pdf())

    if a.crisp:
        box = tuple(float(v) for v in a.crisp.split(','))
        m, fill = crisp(im, box, a.crisp_zoom, a.filter_speckle, a.corner)
        if m is None:
            print('crisp: nothing to separate in that box', file=sys.stderr)
        else:
            mp = os.path.join(a.out_dir, f'.{stem}-crisp.png')
            lp = os.path.join(a.out_dir, f'.{stem}-crisp.svg')
            Image.fromarray(np.where(m, 0, 255).astype(np.uint8)).save(mp)
            vtracer.convert_image_to_svg_py(
                mp, lp, colormode='binary', mode='spline', filter_speckle=8,
                corner_threshold=70, length_threshold=4.0, splice_threshold=45)
            txt = open(lp, encoding='utf-8').read().replace(
                'fill="#000000"', 'fill="#%02x%02x%02x"' % fill)
            open(lp, 'w', encoding='utf-8').write(txt)
            out[0].show_pdf_page(pymupdf.Rect(*box),
                                 pymupdf.open('pdf', pymupdf.open(lp).convert_to_pdf()), 0)
            os.remove(mp); os.remove(lp)
            print(f'crisp: {txt.count(chr(60) + "path")} shapes in '
                  f'#%02x%02x%02x' % fill, file=sys.stderr)

    pdf = os.path.join(a.out_dir, f'{stem}.pdf')
    out.save(pdf, garbage=4, deflate=True)

    err = float(np.abs(render(pdf, W, H).astype(float) - ref).mean())
    paths = open(svg, encoding='utf-8', errors='replace').read().count('<path')
    print(f'{stem}: {W}x{H}, {paths} paths, {time.time()-t:.1f}s\n'
          f'  {svg}  {os.path.getsize(svg)/1e6:.2f} MB  (trace only)\n'
          f'  {pdf}  {os.path.getsize(pdf)/1e6:.2f} MB\n'
          f'  mean error {err:.2f} of 255 per channel', file=sys.stderr)


if __name__ == '__main__':
    main()
