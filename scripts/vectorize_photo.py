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


def crisp(im, box, zoom, bias):
    """That box as two flat colours: the lighter subject over what is behind.

    The split is made along the line between the two colours the box is
    actually made of, found by a two-means pass in RGB, rather than on
    brightness alone -- gold lettering against grey separates on hue as much
    as on tone, and a brightness cut either keeps the cast shadow or eats
    the serifs. The cut is taken on the upscaled picture, which is what lets
    an edge fall between two pixels instead of on one: at this size a
    letter's stem is four pixels across.
    """
    a = np.asarray(im.crop(box), float)
    X = a.reshape(-1, 3)
    c0 = X[X.mean(1).argmin()].copy()
    c1 = X[X.mean(1).argmax()].copy()
    for _ in range(60):
        near1 = ((X - c1) ** 2).sum(1) < ((X - c0) ** 2).sum(1)
        if not near1.any() or near1.all():
            break
        n0, n1 = X[~near1].mean(0), X[near1].mean(0)
        done = np.abs(n0 - c0).max() < 1e-3 and np.abs(n1 - c1).max() < 1e-3
        c0, c1 = n0, n1
        if done:
            break
    axis = c1 - c0
    length = float(np.linalg.norm(axis))
    if length < 1e-6:
        return None, None
    p = ((a - c0) @ (axis / length)) / length      # 0 at the ground, 1 at the subject
    m = ndi.gaussian_filter(ndi.zoom(p, zoom, order=3), 1.0) > bias
    if not m.any():
        return None, None
    return m, tuple(int(v) for v in np.round(c1))


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
    ap.add_argument('--crisp-zoom', type=int, default=8)
    ap.add_argument('--crisp-bias', type=float, default=0.5,
                    help='0 keeps everything, 1 keeps only the subject core')
    ap.add_argument('--crisp-out', action='store_true',
                    help='also write the crisp region on its own, trimmed to its '
                         'ink, in its own colour and in black')
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
        m, fill = crisp(im, box, a.crisp_zoom, a.crisp_bias)
        if m is None:
            print('crisp: nothing to separate in that box', file=sys.stderr)
        else:
            mp = os.path.join(a.out_dir, f'.{stem}-crisp.png')
            lp = os.path.join(a.out_dir, f'.{stem}-crisp.svg')
            Image.fromarray(np.where(m, 0, 255).astype(np.uint8)).save(mp)
            vtracer.convert_image_to_svg_py(
                mp, lp, colormode='binary', mode='spline', filter_speckle=8,
                corner_threshold=70, length_threshold=4.0, splice_threshold=45)
            raw = open(lp, encoding='utf-8').read()
            def coloured(rgb):
                t = raw.replace('fill="#000000"', 'fill="#%02x%02x%02x"' % rgb)
                open(lp, 'w', encoding='utf-8').write(t)
                return pymupdf.open('pdf', pymupdf.open(lp).convert_to_pdf())
            one = coloured(fill)
            out[0].show_pdf_page(pymupdf.Rect(*box), one, 0)
            print(f'crisp: {raw.count(chr(60) + "path")} shapes in '
                  '#%02x%02x%02x' % fill, file=sys.stderr)
            if a.crisp_out:
                ys, xs = np.nonzero(m)
                h, w = m.shape
                px = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
                r = one[0].rect                      # the traced page, in its own units
                clip = pymupdf.Rect(px[0] * r.width / w, px[1] * r.height / h,
                                    px[2] * r.width / w, px[3] * r.height / h)
                pw = (px[2] - px[0]) * (box[2] - box[0]) / w
                ph = (px[3] - px[1]) * (box[3] - box[1]) / h
                for tag, rgb in (('', fill), ('-black', (0, 0, 0))):
                    piece = pymupdf.open()
                    pg = piece.new_page(width=pw, height=ph)
                    pg.show_pdf_page(pymupdf.Rect(0, 0, pw, ph),
                                     one if rgb == fill else coloured(rgb), 0, clip=clip)
                    f = os.path.join(a.out_dir, f'{stem}-crisp{tag}.pdf')
                    piece.save(f, garbage=4, deflate=True)
                    with open(f[:-4] + '.svg', 'w', encoding='utf-8') as fh:
                        fh.write(piece[0].get_svg_image())
                    print(f'  {f}  {pw:.1f} x {ph:.1f} pt', file=sys.stderr)
            os.remove(mp); os.remove(lp)

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
