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


def _lut(cols, keep):
    """64^3 nearest-colour table restricted to the fills in `keep`."""
    c = np.array([cols[i] for i in keep], np.int32)
    grid = np.indices((64, 64, 64), dtype=np.int32).reshape(3, -1).T * 4 + 2
    near = ((grid[:, None, :] - c[None, :, :]) ** 2).sum(-1).argmin(-1)
    return np.array(keep, np.int16)[near]


def quantize(img, cols, fm, win, paper, blobs=None):
    """Label every pixel with its fill, settling edges by majority vote.

    Matching every pixel on colour alone speckles the layers: an antialiased
    pixel is a blend of the two fills it divides, so it lands on whatever
    third fill sits nearest it in RGB. A majority filter settles each edge
    pixel on one of the fills actually around it.

    The vote cannot help where the blend band is several pixels wide, and on
    a page of many colours some fill usually *is* the blend of two others —
    olive is black over yellow, brown is black over tan — so the soft edge of
    a keyline came out as a foreign badge's colour, doubling the line. Each
    blob of artwork is therefore matched only against the fills that have
    flat pixels of their own inside it, which no blend of its neighbours can
    satisfy.
    """
    q = (img >> 2).astype(np.int32)
    cube = (q[..., 0] << 12) | (q[..., 1] << 6) | q[..., 2]
    if blobs is None:
        lab = _lut(cols, list(range(len(cols))))[cube]
    else:
        lab = np.full(img.shape[:2], paper, np.int16)
        full = _lut(cols, list(range(len(cols))))
        for sl, m in blobs:
            inside = full[cube[sl]][m]
            seen, cnt = np.unique(inside[fm[sl][m]], return_counts=True)
            keep = sorted({paper} | {int(k) for k, n in zip(seen, cnt)
                                     if n >= 0.002 * m.sum()})
            lab[sl][m] = _lut(cols, keep)[cube[sl]][m]
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


def blobs_of(img, cols, paper, pad=3):
    """(slice, mask) per connected piece of artwork, with its soft edge."""
    pc = np.array(cols[paper], np.int32)
    ink = (np.abs(img - pc).max(-1) > 16)
    ink = ndi.binary_dilation(ink, np.ones((2 * pad + 1,) * 2))
    L, n = ndi.label(ink)
    out = []
    for i, sl in enumerate(ndi.find_objects(L), start=1):
        if sl is None:
            continue
        m = L[sl] == i
        if m.sum() >= 64:
            out.append((sl, m))
    return out


NUM = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
PATH = re.compile(r'<path\s+d="([^"]+)"(?:[^>]*?fill="#([0-9a-fA-F]{6})")?'
                  r'(?:[^>]*?transform="translate\(([^)]*)\)")?[^>]*>')


def parse_svg(svg):
    """[[subpath, ...] shape, ...] from a VTracer SVG, translates applied.

    Each <path> element is kept as its own shape. Pouring every subpath of a
    layer into one even-odd fill instead lets contours from unrelated blobs
    cancel one another, which punched the keyline into a dashed line.
    """
    shapes = []
    for m in PATH.finditer(svg):
        subs = []
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
        if subs:
            shapes.append(subs)
    return shapes


def trace_mask(mask, work, opts):
    """Trace one binary layer with VTracer; returns its shapes in pixels."""
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


def keyline_split(lab, cols, lum, lum_soft):
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
    # the badges are separate rasters at different scales, so their
    # hairlines differ in width; one global median under-reads the wider
    # ones and half the keyline was being kept as solid fill
    core = dist > w * 2.5
    fill = ndi.binary_propagation(core, mask=m)
    key = m & ~fill
    print(f'  dark ink {m.sum()} px: hairline {key.sum()}, solid {fill.sum()}',
          file=sys.stderr)
    if not key.any():
        return key, w, lab, key
    # A hairline this thin only reaches pure black at its core; its flanks
    # are a blend with whatever it divides, and on a page of many colours
    # that blend is usually some other badge's fill — olive for black over
    # yellow, brown for black over tan. Left as fills they flank the band
    # that replaces the core, and the keyline reads brown with a black
    # middle. They belong to the hairline, so take them into it.
    lum = np.array([sum(c) / 3 for c in cols])
    soft = lum[lab] < lum_soft
    for _ in range(max(int(round(w / 2)), 1)):
        nb = ndi.binary_dilation(key, np.ones((3, 3), bool)) & ~key & soft & ~fill
        if not nb.any():
            break
        key |= nb
    sk = skeletonize(key)
    print(f'  hairline with its blend flanks: {key.sum()} px', file=sys.stderr)
    idx = ndi.distance_transform_edt(key, return_distances=False, return_indices=True)
    return key, w, lab[tuple(idx)], sk & key


def keyline_band(spine, w):
    """A constant-width band on the hairline's own centre line.

    Taking the band from where the fills now meet gives a line one pixel wide
    and broken at the diagonals, which renders as a dashed keyline. The
    hairline's skeleton is already a connected centre line in the right
    place, so the even band is just that line grown to half the width on
    either side.
    """
    if not spine.any():
        return spine
    return ndi.distance_transform_edt(~spine) <= w / 2.0


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
    ap.add_argument('--blob-palette', action='store_true',
                    help='match each blob only against fills with flat pixels '
                         'inside it; starves blobs whose fills are faint')
    ap.add_argument('--clean', type=int, default=3,
                    help='majority-filter window for edge pixels; 0 = off')
    ap.add_argument('--speckle', type=int, default=4,
                    help="VTracer's speckle threshold; not a plain pixel area — "
                         "at 16 it dropped the 120 px dots of the umlaut")
    ap.add_argument('--corner', type=int, default=60, help='corner threshold, degrees')
    ap.add_argument('--splice', type=int, default=45)
    ap.add_argument('--length', type=float, default=4.0)
    ap.add_argument('--even-keyline', action='store_true',
                    help='redraw the dark hairline as one constant-width stroke')
    ap.add_argument('--keyline-lum', type=float, default=60.0,
                    help='max RGB channel below which a fill is keyline ink')
    ap.add_argument('--soft-lum', type=float, default=140.0,
                    help='mean RGB below which a fill flanking the hairline is '
                         'taken to be its blended edge')
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
    paper = max(range(len(cols)), key=lambda i: int(sum(cols[i])))
    blobs = blobs_of(img, cols, paper) if a.blob_palette else None
    lab = quantize(img, cols, fm, a.clean, paper, blobs)
    print(f'{100*fm.mean():.1f}% flat, {len(cols)} fills, '
          f'{0 if blobs is None else len(blobs)} blobs  [{time.time()-t:.1f}s]',
          file=sys.stderr)

    band = kcol = None
    if a.even_keyline:
        key, kw, lab, spine = keyline_split(lab, cols, a.keyline_lum, a.soft_lum)
        if key.any():
            kcol = min((c for c in cols if max(c) < a.keyline_lum),
                       key=lambda c: sum(c))
            kpx = (a.keyline_width / sx) if a.keyline_width else kw
            band = keyline_band(spine, kpx)
            print(f'keyline: {key.sum()} px, measured {kw:.2f} px = {kw*sx:.2f} pt'
                  f' -> drawn at {kpx*sx:.2f} pt, {band.sum()} px',
                  file=sys.stderr)

    work = tempfile.mkdtemp()
    order = sorted(range(len(cols)), key=lambda i: -(lab == i).sum())
    # Overlap each fill into its neighbours by a pixel, but never into the
    # paper. Spline fitting pulls every contour in by a fraction of a pixel,
    # so two fills traced as exact tiles stop meeting and the bare page shows
    # between them; overlapping closes that. Growing into the paper as well
    # is what welded the two dots of the umlaut together and onto the O, and
    # against the paper there is nothing to hide anyway.
    ink = lab != order[0]
    grow = np.ones((3, 3), bool)

    doc = pymupdf.open()
    page = doc.new_page(width=w_pt, height=h_pt)
    nfill = nband = 0
    t = time.time()
    for i in order:
        m = lab == i
        n = int(m.sum())
        if n < a.speckle:
            continue
        if i != order[0]:
            m = ndi.binary_dilation(m, grow) & (m | ink)
        shapes = trace_mask(m, work, a)
        if not shapes:
            continue
        for subs in shapes:
            sh = page.new_shape()
            emit(sh, subs, sx, sy)
            sh.finish(color=None, fill=[v / 255 for v in cols[i]], even_odd=True,
                      closePath=True, width=0)
            sh.commit()
        nfill += len(shapes)

    if band is not None and band.any():
        shapes = trace_mask(band, work, a)
        for subs in shapes:
            sh = page.new_shape()
            emit(sh, subs, sx, sy)
            sh.finish(color=None, fill=[v / 255 for v in kcol], even_odd=True,
                      closePath=True, width=0)
            sh.commit()
        nband = len(shapes)

    doc.save(a.out_pdf, garbage=4, deflate=True)
    print(f'traced {len(order)} layers [{time.time()-t:.1f}s]', file=sys.stderr)
    print(f'wrote {a.out_pdf}: {nfill} filled contours, {nband} keyline, '
          f'{os.path.getsize(a.out_pdf)/1e6:.2f} MB  [total {time.time()-t0:.1f}s]',
          file=sys.stderr)


if __name__ == '__main__':
    main()
