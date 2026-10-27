"""Vectorize a subject against its ground as one solid black shape.

For artwork that is one thing on one background -- an ornament, a motif, a
stamp -- where what is wanted back is the shape, not the shading.

The cut is made along the line between the two colours the picture is
actually made of, found by a two-means pass in RGB, rather than on
brightness. A gold relief on grey paper separates on hue far better than on
tone: the paper here runs from 192 to 245 across its own gradient while the
ornament's lit faces run to 190, so no brightness threshold divides them,
and on the colour axis they are never in doubt.

What is left after that is a cleaning job, because a relief is lit: every
raised face carries a highlight that falls on the paper's side of the cut
and arrives as a speck inside the shape. Specks are filled and notches
closed; the real openings -- the scroll curls, the gaps between stem and
leaf -- are orders of magnitude larger and are kept.

The modelling can be kept two ways, and a plain threshold is neither of
them -- the beading on the leaves is at the resolution limit and a
threshold returns it as mottle. What works is to ask what kind of thing
each mark is:

  line    the shape's own contour, plus the dark grooves inside it found
          as ridges rather than as dark pixels, so that a groove running
          between two leaves is kept and a dark speck is not. Reads as an
          engraving; print it, do not emboss it, since the lines go finer
          than a die will hold.

  relief  solid, with the lit faces knocked out and each knockout pulled
          back from its edge so a black web is left between them. Keeps
          the masses an emboss needs and still says where one leaf ends
          and the next begins.
"""
import argparse, os, sys
import numpy as np, pymupdf, vtracer
from PIL import Image
from scipy import ndimage as ndi
from skimage.filters import sato


def disc(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def two_means(a):
    """The two colours the picture is made of: ground first, subject second."""
    X = a.reshape(-1, 3)
    c0 = X[X.mean(1).argmax()].copy()                  # lightest: the paper
    c1 = X[(X[:, 0] - X[:, 2]).argmax()].copy()        # warmest: the ink
    for _ in range(80):
        near1 = ((X - c1) ** 2).sum(1) < ((X - c0) ** 2).sum(1)
        if not near1.any() or near1.all():
            break
        n0, n1 = X[~near1].mean(0), X[near1].mean(0)
        done = np.abs(n0 - c0).max() < 1e-3 and np.abs(n1 - c1).max() < 1e-3
        c0, c1 = n0, n1
        if done:
            break
    return c0, c1


def silhouette(a, zoom, bias, close_r, min_hole, min_blob):
    c0, c1 = two_means(a)
    axis = c1 - c0
    length = float(np.linalg.norm(axis))
    p = ((a - c0) @ (axis / length)) / length
    f = ndi.gaussian_filter(ndi.zoom(p, zoom, order=3), 1.2)
    m = f > bias
    if close_r:
        m = ndi.binary_closing(m, disc(close_r))
    hole = ndi.binary_fill_holes(m) & ~m
    L, n = ndi.label(hole)
    if n:
        sz = ndi.sum(hole, L, range(1, n + 1))
        m = m | np.isin(L, [i + 1 for i in range(n) if sz[i] < min_hole])
    L, n = ndi.label(m)
    if n:
        sz = ndi.sum(m, L, range(1, n + 1))
        m = np.isin(L, [i + 1 for i in range(n) if sz[i] >= min_blob])
    return m, c0, c1


def lines(lum, sil, zoom, keep, open_r, edge_r, min_run):
    """Contour plus the grooves inside, taken as ridges, not as dark pixels."""
    big = ndi.gaussian_filter(ndi.zoom(lum, zoom, order=3), 1.5)
    r = sato(255 - big, sigmas=range(2, 9, 2), black_ridges=False)
    g = sil & (r > np.percentile(r[sil], keep))
    g = ndi.binary_opening(ndi.binary_closing(g, disc(2)), disc(open_r))
    art = (sil & ~ndi.binary_erosion(sil, disc(edge_r))) | g
    L, n = ndi.label(art)
    if n:
        sz = ndi.sum(art, L, range(1, n + 1))
        art = np.isin(L, [i + 1 for i in range(n) if sz[i] >= min_run])
    return art


def relief(lum, sil, zoom, keep, back_r, min_face):
    """Solid, with the lit faces knocked out and held back from the edges."""
    big = ndi.gaussian_filter(ndi.zoom(lum, zoom, order=3), 1.5)
    lit = sil & (big > np.percentile(big[sil], keep))
    lit = ndi.binary_erosion(ndi.binary_opening(lit, disc(2)), disc(back_r))
    L, n = ndi.label(lit)
    if n:
        sz = ndi.sum(lit, L, range(1, n + 1))
        lit = np.isin(L, [i + 1 for i in range(n) if sz[i] >= min_face])
    return sil & ~lit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_dir')
    ap.add_argument('--name', default=None)
    ap.add_argument('--width-mm', type=float, default=None,
                    help='printed width; without it the page keeps the source size')
    ap.add_argument('--zoom', type=int, default=8)
    ap.add_argument('--bias', type=float, default=0.45,
                    help='0 is the ground, 1 the subject; where to put the edge')
    ap.add_argument('--close', type=int, default=4, help='closes notches, in zoomed px')
    ap.add_argument('--min-hole', type=float, default=1600,
                    help='openings smaller than this are lighting, and get filled')
    ap.add_argument('--min-blob', type=float, default=400)
    ap.add_argument('--invert', action='store_true', help='also write white on black')
    ap.add_argument('--detail', choices=('none', 'line', 'relief'), default='none',
                    help="none: the solid shape. line: contour plus interior "
                         "grooves, for print. relief: solid with the lit faces "
                         "knocked out, for an emboss that still shows its leaves")
    ap.add_argument('--keep', type=float, default=None,
                    help='percentile kept as groove (line) or as lit face (relief); '
                         'defaults to 70 and 60')
    ap.add_argument('--edge', type=int, default=3, help='contour weight, zoomed px')
    ap.add_argument('--open', dest='open_r', type=int, default=3)
    ap.add_argument('--back', type=int, default=5, help='how far a knockout is held '
                                                        'back from its edge')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    stem = a.name or os.path.splitext(os.path.basename(a.src))[0]
    im = Image.open(a.src).convert('RGB')
    arr = np.asarray(im, float)
    m, c0, c1 = silhouette(arr, a.zoom, a.bias, a.close, a.min_hole, a.min_blob)
    if not m.any():
        sys.exit('nothing separated from the ground')
    lum = arr.mean(-1)
    if a.detail == 'line':
        m = lines(lum, m, a.zoom, 70 if a.keep is None else a.keep,
                  a.open_r, a.edge, a.min_blob)
    elif a.detail == 'relief':
        m = relief(lum, m, a.zoom, 60 if a.keep is None else a.keep,
                   a.back, max(a.min_blob * 3, 1200))

    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    png = os.path.join(a.out_dir, f'.{stem}-mask.png')
    Image.fromarray(np.where(m, 0, 255).astype(np.uint8)).save(png)
    svg = os.path.join(a.out_dir, f'{stem}.svg')
    vtracer.convert_image_to_svg_py(png, svg, colormode='binary', mode='spline',
                                    filter_speckle=8, corner_threshold=70,
                                    length_threshold=4.0, splice_threshold=45)
    os.remove(png)

    doc = pymupdf.open(svg)
    r = doc[0].rect
    w = a.width_mm * 72 / 25.4 if a.width_mm else m.shape[1] / a.zoom
    h = w * r.height / r.width
    made = []
    for tag, rgb in ([('', (0, 0, 0))] + ([('-reversed', (255, 255, 255))] if a.invert else [])):
        txt = open(svg, encoding='utf-8').read().replace(
            'fill="#000000"', 'fill="#%02x%02x%02x"' % rgb)
        tmp = svg + '.tmp'
        open(tmp, 'w', encoding='utf-8').write(txt)
        art = pymupdf.open('pdf', pymupdf.open(tmp).convert_to_pdf())
        os.remove(tmp)
        out = pymupdf.open()
        page = out.new_page(width=w, height=h)
        if rgb != (0, 0, 0):
            page.draw_rect(page.rect, color=None, fill=(0, 0, 0))
        page.show_pdf_page(pymupdf.Rect(0, 0, w, h), art, 0)
        f = os.path.join(a.out_dir, f'{stem}{tag}.pdf')
        out.save(f, garbage=4, deflate=True)
        made.append(f)
    open(svg, encoding='utf-8')          # the plain black svg stays as traced

    print(f'{stem}: source {im.width}x{im.height}, ink {100*m.mean():.1f}% of its box\n'
          f'  ground #{"%02x%02x%02x" % tuple(int(v) for v in c0)}  '
          f'subject #{"%02x%02x%02x" % tuple(int(v) for v in c1)}\n'
          f'  {open(svg, encoding="utf-8").read().count("<path")} paths, '
          f'page {w:.1f} x {h:.1f} pt', file=sys.stderr)
    for f in made + [svg]:
        print(f'  {f}', file=sys.stderr)


if __name__ == '__main__':
    main()
