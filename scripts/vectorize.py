#!/usr/bin/env python3
"""Vectorize a PDF page or image to PDF, faithfully, with VTracer.

Shapes are traced as drawn — no smoothing, no node reduction, no
regularising. The one piece of preprocessing is a palette snap: the flat
fills are sampled from inside flat regions only, and every antialiased edge
pixel is handed to the fill it actually divides. Without that the edge ramps
trace as thousands of sliver contours of their own.
"""
import argparse, os, re, sys, tempfile, time
import numpy as np, pymupdf, vtracer
from scipy import ndimage as ndi
from PIL import Image


def render(src, dpi, pageno):
    """(HxWx3 int32, page width pt, page height pt)"""
    if src.lower().endswith('.pdf'):
        page = pymupdf.open(src)[pageno]
        pm = page.get_pixmap(dpi=dpi, alpha=False)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
        return a.astype(np.int32), page.rect.width, page.rect.height
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.int32)
    return a, a.shape[1] * 72 / dpi, a.shape[0] * 72 / dpi


def _key(img):
    """Pack RGB into one uint32 per pixel, so colours compare in one op."""
    return ((img[..., 0].astype(np.uint32) << 16)
            | (img[..., 1].astype(np.uint32) << 8)
            | img[..., 2].astype(np.uint32))


def flat_mask(img):
    """Pixels whose whole 3x3 neighbourhood is one constant colour.

    Eight shifted comparisons on the packed colour, rather than min/max
    filters per channel — same answer, a fraction of the time.
    """
    k = _key(img)
    out = np.ones(k.shape, bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                out &= k == np.roll(np.roll(k, dy, 0), dx, 1)
    out[0] = out[-1] = False
    out[:, 0] = out[:, -1] = False
    return out


def palette(img, fm, frac, merge):
    """The flat fills, largest area first, near-duplicates folded together.

    JPEG blocking splits one flat fill into several colours a few levels
    apart; folded together they stay one fill instead of becoming layers
    whose shared boundary is pure noise.
    """
    k = _key(img)[fm] >> 2 & 0x3F3F3F  # bucket to 6 bits per channel
    ks, cnt = np.unique(((k >> 16) << 12) | ((k >> 8 & 0x3F) << 6) | (k & 0x3F),
                        return_counts=True)
    keep = []
    for i in np.argsort(-cnt):
        if cnt[i] < frac * fm.sum():
            break
        v = int(ks[i])
        c = np.array([(v >> 12) & 63, (v >> 6) & 63, v & 63]) * 4 + 2
        if all(np.sqrt(((c - np.array(q)) ** 2).sum()) >= merge for q in keep):
            keep.append(tuple(int(x) for x in c))
    return keep


def quantize(img, cols, fm, win):
    """Label every pixel with its fill, settling edges by majority vote.

    Matching every pixel on colour alone speckles the layers: an antialiased
    pixel is a blend of the two fills it divides, so it lands on whatever
    third fill sits nearest it in RGB — a grey between black and white, and
    so on. A majority filter settles each edge pixel on one of the fills
    actually around it. Handing it instead to the nearest *flat* pixel also
    de-speckles, but erases any feature thinner than the flatness window; it
    ate the hairline ring around one of the badges.

    Nearest-colour goes through a 64^3 lookup table instead of a distance to
    every fill per pixel, and the vote is counted only on the edge pixels
    that need it, which is a few per cent of the page.
    """
    c = np.array(cols, np.int32)
    grid = np.indices((64, 64, 64), dtype=np.int32).reshape(3, -1).T * 4 + 2
    lut = ((grid[:, None, :] - c[None, :, :]) ** 2).sum(-1).argmin(-1).astype(np.int16)
    q = (img >> 2).astype(np.int32)
    lab = lut[(q[..., 0] << 12) | (q[..., 1] << 6) | q[..., 2]]
    if win >= 3:
        h, w = lab.shape
        ys, xs = np.nonzero(~fm)
        r = win // 2
        votes = np.zeros((len(ys), len(cols)), np.uint8)
        rows = np.arange(len(ys))
        for dy in range(-r, r + 1):
            yy = np.clip(ys + dy, 0, h - 1)
            for dx in range(-r, r + 1):
                votes[rows, lab[yy, np.clip(xs + dx, 0, w - 1)]] += 1
        lab[ys, xs] = votes.argmax(1)
    return lab


NUM = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
PATH = re.compile(r'<path\s+d="([^"]+)"(?:[^>]*?fill="#([0-9a-fA-F]{6})")?'
                  r'(?:[^>]*?transform="translate\(([^)]*)\)")?[^>]*>')


def parse_svg(svg):
    """[[(cmd, pts), ...] subpath, ...] from a VTracer SVG, translates applied."""
    subs = []
    for m in PATH.finditer(svg):
        tx = ty = 0.0
        if m.group(3):
            v = [float(x) for x in NUM.findall(m.group(3))]
            if len(v) >= 2:
                tx, ty = v[0], v[1]
        cur = None
        for tok in re.finditer(r'([MLCZmlcz])([^MLCZmlcz]*)', m.group(1)):
            op = tok.group(1)
            n = [float(v) for v in NUM.findall(tok.group(2))]
            pts = [(x + tx, y + ty) for x, y in zip(n[0::2], n[1::2])]
            if op in 'Mm':
                if not pts:
                    continue
                cur = [('M', pts[0])]
                subs.append(cur)
                cur += [('L', q) for q in pts[1:]]
            elif cur is None:
                continue
            elif op in 'Ll':
                cur += [('L', q) for q in pts]
            elif op in 'Cc':
                for i in range(0, len(pts) - 2, 3):
                    cur.append(('C', pts[i:i + 3]))
    return subs


def trace_mask(mask, work, opts):
    """Trace one binary layer with VTracer; returns its subpaths in pixels."""
    png = os.path.join(work, 'm.png')
    svg = os.path.join(work, 'm.svg')
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(png)
    vtracer.convert_image_to_svg_py(
        png, svg, colormode='binary', hierarchical='stacked', mode='spline',
        filter_speckle=opts.speckle, corner_threshold=opts.corner,
        length_threshold=opts.length, max_iterations=10,
        splice_threshold=opts.splice, path_precision=4)
    return parse_svg(open(svg).read())


def pts_of(subs):
    """Flat array of the on-curve points of every subpath, for sampling."""
    out = []
    for sp in subs:
        for op, p in sp:
            if op == 'M' or op == 'L':
                out.append(p)
            elif op == 'C':
                out.append(p[2])
    return np.array(out) if out else np.zeros((0, 2))


def emit(shape, subs, sx, sy):
    P = lambda p: pymupdf.Point(p[0] * sx, p[1] * sy)
    for sp in subs:
        start = cur = None
        for op, p in sp:
            if op == 'M':
                start = cur = P(p)
            elif op == 'L':
                q = P(p)
                if q != cur:
                    shape.draw_line(cur, q)
                cur = q
            elif op == 'C':
                e = P(p[2])
                shape.draw_bezier(cur, P(p[0]), P(p[1]), e)
                cur = e
        if start is not None and cur != start:
            shape.draw_line(cur, start)


def keyline_split(lab, cols, lum):
    """(keyline mask, width in px, labels with the keyline dissolved away).

    The dark ink is both a hairline around the fills and, in a few badges, a
    fill of its own. Thin and thick are told apart on the distance transform,
    and the hairline's width is read off the *skeleton*: most of the skeleton's
    length is hairline, so its median half-width is the hairline's, while a
    mean over all dark pixels is dragged up by the solid black crosses.

    Keyline pixels are then handed to the fill they border, so two fills meet
    along the hairline's own centre line and a stroke laid on that join lands
    exactly where the hairline was.
    """
    from skimage.morphology import skeletonize
    dark = [i for i, c in enumerate(cols) if max(c) < lum]
    m = np.isin(lab, dark)
    if not m.any():
        return m, 0.0, lab
    dist = ndi.distance_transform_edt(m)
    sk = skeletonize(m)
    w = 2 * float(np.median(dist[sk])) if sk.any() else 2 * float(dist[m].mean())
    core = dist > w * 0.9
    fill = ndi.binary_propagation(core, mask=m)
    key = m & ~fill
    print(f'  dark ink {m.sum()} px: hairline {key.sum()}, solid {fill.sum()}',
          file=sys.stderr)
    if not key.any():
        return key, w, lab
    idx = ndi.distance_transform_edt(key, return_distances=False, return_indices=True)
    return key, w, lab[tuple(idx)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_pdf')
    ap.add_argument('--dpi', type=int, default=400)
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--min-area', type=float, default=0.0004,
                    help='flat-area fraction for a colour to count as a fill')
    ap.add_argument('--merge', type=float, default=26.0,
                    help='fold fills closer than this in RGB')
    ap.add_argument('--clean', type=int, default=3,
                    help='majority-filter window for edge pixels; 0 = off')
    ap.add_argument('--speckle', type=int, default=16, help='drop blobs below N px')
    ap.add_argument('--corner', type=int, default=60, help='corner threshold, degrees')
    ap.add_argument('--splice', type=int, default=45)
    ap.add_argument('--length', type=float, default=4.0)
    ap.add_argument('--grow', type=int, default=1, help='px of overlap between fills')
    ap.add_argument('--even-keyline', action='store_true',
                    help='redraw the dark hairline as one constant-width stroke')
    ap.add_argument('--keyline-lum', type=float, default=60.0,
                    help='max RGB channel below which a fill is keyline ink')
    ap.add_argument('--keyline-width', type=float, default=0.0,
                    help='keyline width in pt; 0 = the measured median')
    a = ap.parse_args()

    t0 = time.time()
    img, w_pt, h_pt = render(a.src, a.dpi, a.page)
    ph, pw = img.shape[:2]
    sx, sy = w_pt / pw, h_pt / ph
    print(f'{pw} x {ph} px  ->  {w_pt:.1f} x {h_pt:.1f} pt  [{time.time()-t0:.1f}s]',
          file=sys.stderr)

    t = time.time()
    fm = flat_mask(img)
    cols = palette(img, fm, a.min_area, a.merge)
    lab = quantize(img, cols, fm, a.clean)
    print(f'{100*fm.mean():.1f}% flat, {len(cols)} fills  [{time.time()-t:.1f}s]',
          file=sys.stderr)

    key = None
    if a.even_keyline:
        key, kw, lab = keyline_split(lab, cols, a.keyline_lum)
        kw_pt = a.keyline_width or kw * sx
        print(f'keyline: {key.sum()} px, measured {kw:.2f} px = {kw*sx:.2f} pt'
              f' -> drawn at {kw_pt:.2f} pt', file=sys.stderr)
        kband = ndi.distance_transform_edt(~key) <= max(kw, 2.0)

    work = tempfile.mkdtemp()
    order = sorted(range(len(cols)), key=lambda i: -(lab == i).sum())
    grow = np.ones((2 * a.grow + 1,) * 2, bool)

    doc = pymupdf.open()
    page = doc.new_page(width=w_pt, height=h_pt)
    nfill = nstroke = 0
    strokes = []
    t = time.time()
    for i in order:
        m = lab == i
        n = int(m.sum())
        if n < a.speckle:
            continue
        if a.grow:
            # fills overlap by a pixel instead of abutting, so no hairline of
            # the layer beneath shows through at a shared edge
            m = ndi.binary_dilation(m, grow)
        subs = trace_mask(m, work, a)
        if not subs:
            continue
        sh = page.new_shape()
        emit(sh, subs, sx, sy)
        sh.finish(color=None, fill=[v / 255 for v in cols[i]], even_odd=True,
                  closePath=True, width=0)
        sh.commit()
        nfill += len(subs)
        if key is not None:
            # a contour that runs along the old hairline gets the even stroke
            for sp in subs:
                P = pts_of([sp])
                if len(P) < 4:
                    continue
                yy = np.clip(P[:, 1].astype(int), 0, ph - 1)
                xx = np.clip(P[:, 0].astype(int), 0, pw - 1)
                if kband[yy, xx].mean() > 0.5:
                    strokes.append(sp)

    if strokes:
        sh = page.new_shape()
        emit(sh, strokes, sx, sy)
        sh.finish(color=(0, 0, 0), fill=None, width=kw_pt, closePath=True,
                  lineJoin=1, lineCap=1)
        sh.commit()
        nstroke = len(strokes)

    doc.save(a.out_pdf, garbage=4, deflate=True)
    print(f'traced {len(order)} layers [{time.time()-t:.1f}s]', file=sys.stderr)
    print(f'wrote {a.out_pdf}: {nfill} filled contours, {nstroke} stroked, '
          f'{os.path.getsize(a.out_pdf)/1e6:.2f} MB  [total {time.time()-t0:.1f}s]',
          file=sys.stderr)


if __name__ == '__main__':
    main()
