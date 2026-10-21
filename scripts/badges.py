#!/usr/bin/env python3
"""Vectorize each badge of a PDF on its own, at a given printed width.

One badge at a time, at its raster's native resolution and against its own
colours only. On a sheet of many badges the blend along a hairline usually
matches some *other* badge's fill -- olive is black over yellow, brown is
black over tan -- and the hairline comes out doubled. Per badge there is
nothing to confuse it with.

The dark hairline is measured, dissolved into the fills it divides, and laid
back as a band of one width, so the outline is even all the way round.
"""
import argparse, os, re, sys, tempfile, time
import numpy as np, pymupdf, vtracer
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vectorize import _key, parse_svg, emit, _lut   # noqa: E402

MM = 72.0 / 25.4


def _top(rgb, m, k=3):
    """The k commonest colours inside a mask, with the share each covers."""
    v = rgb[m]
    q = (v // 8).astype(np.int64)
    ks, cnt = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    out = []
    for i in np.argsort(-cnt)[:k]:
        key = int(ks[i])
        out.append((np.array([(key >> 16) & 255, (key >> 8) & 255, key & 255]) * 8 + 4,
                    float(cnt[i]) / m.sum()))
    return out


def _dist(x, y):
    """How unlike two colourways are, by colour and by how much each covers.

    The share matters as much as the colour: two colourways of one badge are
    often the same two inks swapped over -- a tan ground with a blue cross
    and a blue ground with a tan cross -- and on colour alone they match
    each other exactly.
    """
    if not x or not y:
        return 1e9
    tot = 0.0
    for c, f in x:
        d, g = min(((np.linalg.norm(c - o), fo) for o, fo in y), key=lambda t: t[0])
        tot += d + 400.0 * abs(f - g)
    return tot / len(x)


def badges_of(src, dpi, min_mm, scale=2, pad=4, pageno=0):
    """Each badge the page shows, at its raster's own resolution.

    The page is only used to find out which artwork it shows. Reading the
    badges off the rendered page instead costs real detail: each raster
    carries three colourways at four or five hundred pixels each, the page
    clips it to one and scales that up past eight hundred, and the renderer
    doubles pixels rather than interpolating -- so a diagonal edge arrives
    as a staircase with two-pixel steps that no amount of smoothing
    afterwards can undo. The raster still has the artwork as drawn.
    """
    doc = pymupdf.open(src)
    page = doc[pageno]
    pm = page.get_pixmap(dpi=dpi, alpha=False)
    pimg = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    ink = pimg.min(-1) < 236
    L, n = ndi.label(ndi.binary_closing(ink, np.ones((5, 5))))
    floor = (min_mm / 25.4 * dpi) ** 2 * 0.1
    shown = []
    for i, sl in enumerate(ndi.find_objects(L), start=1):
        if sl is None:
            continue
        m = L[sl] == i
        if m.sum() >= floor:
            shown.append((sl[1].start, _top(pimg[sl], m)))
    shown.sort(key=lambda t: t[0])

    # every colourway in every raster, at native size
    cands = []
    for xr in dict.fromkeys(b['xref'] for b in page.get_image_info(xrefs=True)):
        pix = pymupdf.Pixmap(doc, xr)
        sm = doc.xref_get_key(xr, 'SMask')
        if sm[0] == 'xref':
            pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, int(sm[1].split()[0])))
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 3:
            a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
        al = a[..., 3] > 128
        Lr, nr = ndi.label(ndi.binary_closing(al, np.ones((5, 5))))
        for i, sl in enumerate(ndi.find_objects(Lr), start=1):
            if sl is None:
                continue
            m = ndi.binary_fill_holes(Lr[sl] == i)
            if m.sum() < 20000:
                continue
            c = a[sl][..., :3].copy()
            crop = np.dstack([c, np.where(m, 255, 0).astype(np.uint8)])
            crop = np.pad(crop, ((pad, pad), (pad, pad), (0, 0)))
            if scale > 1:
                # Cubic, not the pixel doubling the page renderer does. The
                # extra pixels carry no new detail, but a hairline two pixels
                # wide cannot be measured or redrawn to better than half a
                # pixel, and at this size half a pixel is a fifth of its
                # width -- which is what made the outline come out heavy.
                crop = np.dstack([
                    np.clip(ndi.zoom(crop[..., i].astype(np.float32), scale,
                                     order=3, mode='nearest'), 0, 255)
                    for i in range(4)]).astype(np.uint8)
            cands.append((_top(c, m), crop))

    out, used = [], set()
    for _, want in shown:
        best = min((j for j in range(len(cands)) if j not in used),
                   key=lambda j: _dist(want, cands[j][0]), default=None)
        if best is None:
            continue
        used.add(best)
        out.append(cands[best][1])
    return out


def flat_mask(img, need=5):
    """Pixels agreeing with at least `need` of their 8 neighbours.

    Demanding all eight means a hairline never qualifies: two pixels wide,
    every one of them has a neighbour of another colour. The outline then
    never reaches the palette and the badge is traced without it.
    """
    k = _key(img)
    n = np.zeros(k.shape, np.int8)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                n += k == np.roll(np.roll(k, dy, 0), dx, 1)
    out = n >= need
    out[0] = out[-1] = False
    out[:, 0] = out[:, -1] = False
    return out


def palette(img, fm, frac, merge, blend_tol, thick=2.0):
    """The badge's own fills: flat colours by area, blends discarded.

    Relaxing the flatness test enough to admit a two-pixel hairline also
    admits the blends along every edge, and no single area threshold
    separates the two -- the share of the page a hairline covers varies more
    between badges than a blend's does. What tells them apart is position in
    colour space: a blend sits on the line between the two fills it divides,
    and a real ink does not. Black is not tan mixed with blue.
    """
    flat = img[fm]
    q = (flat // 4).astype(np.int64)
    ks, cnt = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    keep, keep_n = [], []
    for i in np.argsort(-cnt):
        if cnt[i] < frac * len(flat):
            break
        k = int(ks[i])
        c = np.array([(k >> 16) & 255, (k >> 8) & 255, k & 255]) * 4 + 2
        if any(np.sqrt(((c - np.array(q2)) ** 2).sum()) < merge for q2 in keep):
            continue
        keep.append(tuple(int(v) for v in c))
        keep_n.append(int(cnt[i]))
    # Sitting on the line is necessary but not sufficient: a real ink can
    # land there by chance, as this artwork's mid green does between its
    # yellow and its dark green. What a blend cannot have is body. It exists
    # only as a film along the boundary it divides, so it is thin
    # everywhere, while an ink -- even a hairline -- has a core.
    lut = _lut(keep, list(range(len(keep))))
    qq = (img >> 2).astype(np.int32)
    hard = lut[(qq[..., 0] << 12) | (qq[..., 1] << 6) | qq[..., 2]]
    hard[~fm & ~ndi.binary_dilation(fm, np.ones((3, 3)))] = -1
    out = []
    for i, c in enumerate(keep):
        p0 = np.array(c, float)
        on_line = False
        for j in range(len(keep)):
            for l in range(j + 1, len(keep)):
                if i in (j, l) or keep_n[j] <= keep_n[i] or keep_n[l] <= keep_n[i]:
                    continue
                a, b = np.array(keep[j], float), np.array(keep[l], float)
                ab = b - a
                n = np.dot(ab, ab)
                if n < 1:
                    continue
                t = np.clip(np.dot(p0 - a, ab) / n, 0, 1)
                if 0.1 < t < 0.9 and np.linalg.norm(p0 - (a + t * ab)) < blend_tol * np.sqrt(n):
                    on_line = True
        if not on_line:
            out.append(c)
            continue
        d = ndi.distance_transform_edt(hard == i)
        if d.max() >= thick:
            out.append(c)
    return out


def label_badge(img, ink, cols, sigma):
    """Nearest fill, then a Gaussian vote so the edge is smooth.

    Voting only over the blurred band between fills, with every clean pixel
    pinned, makes the traced edge follow that band exactly -- and in JPEG
    artwork the band carries ringing, so the edge comes out bitten. The vote
    runs over every pixel instead; it cannot move an interior.
    """
    q = (img[..., :3] >> 2).astype(np.int32)
    cube = (q[..., 0] << 12) | (q[..., 1] << 6) | q[..., 2]
    lab = _lut(cols, list(range(len(cols))))[cube]
    lab[~ink] = -1
    best = np.zeros(lab.shape, np.float32)
    out = np.full(lab.shape, -1, np.int16)
    for i in range(len(cols)):
        v = ndi.gaussian_filter((lab == i).astype(np.float32), sigma,
                                truncate=2.0, mode='nearest')
        np.copyto(out, np.int16(i), where=(v > best) & ink)
        np.maximum(best, v, out=best)
    return out


def despeckle(lab, ink, floor, skip=()):
    """Drop each fill's small islands into whatever surrounds them.

    Two fills a few levels apart -- this artwork's two greens -- swap
    pixels wherever JPEG noise pushes one over the line, and the band comes
    out mottled with patches of the other. What separates a patch from the
    real thing is not colour but size: the centre dot is one solid region,
    the mottle is scattered crumbs.
    """
    out = lab.copy()
    drop = np.zeros(lab.shape, bool)
    for i in range(int(lab.max()) + 1):
        # the hairline is exempt: it is legitimately small and broken into
        # short runs, and sweeping it up takes the ring off every centre dot
        if i in skip:
            continue
        m = lab == i
        if not m.any():
            continue
        L, n = ndi.label(m)
        if n < 2:
            continue
        sz = np.bincount(L.ravel())
        small = np.flatnonzero(sz < floor)
        if small.size:
            drop |= np.isin(L, small[small > 0])
    if not drop.any():
        return out
    out[drop] = -1
    keep = (out >= 0)
    if not keep.any():
        return lab
    idx = ndi.distance_transform_edt(~keep, return_distances=False, return_indices=True)
    out = out[tuple(idx)]
    out[~ink] = -1
    return out


def even_outline(lab, cols, lum, min_frac):
    """(labels with the hairline dissolved, band mask, ink index) or None."""
    dark = [i for i, c in enumerate(cols) if max(c) < lum]
    if not dark:
        return None
    m = np.isin(lab, dark)
    if m.sum() < min_frac * (lab >= 0).sum():
        return None
    dist = ndi.distance_transform_edt(m)
    sk = skeletonize(m)
    if not sk.any():
        return None
    # area over length, not twice the median distance: on a line only a
    # few pixels wide the distance transform rounds up at every step and
    # the outline comes back a third too heavy
    w = float(m.sum()) / max(int(sk.sum()), 1)
    core = dist > w * 2.5
    fill = ndi.binary_propagation(core, mask=m)
    key = m & ~fill
    if not key.any():
        return None
    out = lab.copy()
    idx = ndi.distance_transform_edt(key, return_distances=False, return_indices=True)
    out[key] = lab[tuple(idx)][key]
    spine = skeletonize(key)
    # a threshold of w/2 round a one-pixel spine gives a band of w+1, and
    # the fills' dilation adds more on top, so the outline printed a
    # third heavier than the drawing's
    band = (ndi.distance_transform_edt(~spine) <= (w - 1.0) / 2.0) & (lab >= 0)
    kcol = min(dark, key=lambda i: sum(cols[i]))
    return out, band, w, kcol


def upsample(m, u, sigma):
    """A mask at u times the scale, with its edge placed between pixels.

    A binary mask only knows whole pixels, so a diagonal edge is a
    staircase, and the tracer reproduces the staircase faithfully --
    it has nothing else to go on, whatever the corner threshold. Scaling
    the mask up as a continuous field and cutting it at a half puts the
    edge where it actually falls, between pixels, and the steps shrink with
    u rather than surviving at full size.
    """
    if u <= 1:
        return m
    # Scale up the signed distance to the edge, not the mask itself. A mask
    # interpolates between 0 and 1 and can still only put the edge at a
    # pixel centre, so the staircase survives at a quarter the size; the
    # distance field is smooth and roughly linear across the edge, so
    # interpolating it puts the edge where it belongs and the steps go.
    d = (ndi.distance_transform_edt(m).astype(np.float32)
         - ndi.distance_transform_edt(~m).astype(np.float32))
    f = ndi.zoom(d, u, order=1, mode='nearest')
    if sigma:
        f = ndi.gaussian_filter(f, sigma, truncate=2.0, mode='nearest')
    return f >= 0


def trace(mask, work, opts):
    png, svg = os.path.join(work, 'm.png'), os.path.join(work, 'm.svg')
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(png)
    vtracer.convert_image_to_svg_py(
        png, svg, colormode='binary', hierarchical='stacked', mode='spline',
        filter_speckle=opts.speckle, corner_threshold=opts.corner,
        length_threshold=opts.length, max_iterations=10,
        splice_threshold=opts.splice, path_precision=4)
    return parse_svg(open(svg).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_dir')
    ap.add_argument('--width-mm', type=float, default=30.0)
    ap.add_argument('--dpi', type=int, default=600,
                    help='resolution the page is read at')
    ap.add_argument('--pre-scale', type=int, default=2,
                    help='scale the raster up by this before reading it')
    ap.add_argument('--sigma', type=float, default=1.1,
                    help='edge smoothing in source px; the hairline is only '
                         'two px wide, so this cannot go much higher')
    ap.add_argument('--min-area', type=float, default=0.0006)
    ap.add_argument('--merge', type=float, default=26.0)
    ap.add_argument('--blend-tol', type=float, default=0.18,
                    help='how near the line between two fills a colour '
                         'must sit to count as their blend')
    ap.add_argument('--min-blob', type=float, default=0.002,
                    help="smallest island of a fill to keep, as a "
                         "fraction of the badge's ink")
    ap.add_argument('--supersample', type=int, default=4,
                    help='scale the mask up by this before tracing, so the\n'
                         'edge can fall between pixels')
    ap.add_argument('--band-sigma', type=float, default=4.0,
                    help='smoothing on the outline band, in upscaled px')
    ap.add_argument('--up-sigma', type=float, default=2.0,
                    help='smoothing on the scaled-up mask, in its own px')
    ap.add_argument('--speckle', type=int, default=4)
    ap.add_argument('--corner', type=int, default=60)
    ap.add_argument('--splice', type=int, default=45)
    ap.add_argument('--length', type=float, default=4.0)
    ap.add_argument('--outline-lum', type=float, default=90.0)
    ap.add_argument('--even-outline', action='store_true',
                    help='rebuild the hairline at one width. Measured worse '
                         'than tracing it as drawn: 44% variation against 12%')
    ap.add_argument('--outline-trim', type=int, default=1,
                    help='shave this many upscaled px off the hairline')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    imgs = badges_of(a.src, a.dpi, a.width_mm, a.pre_scale)
    print(f'{len(imgs)} badges on the page', file=sys.stderr)
    work = tempfile.mkdtemp()
    W = a.width_mm * MM
    made = []

    for n, img in enumerate(imgs, start=1):
        t0 = time.time()
        ink = img[..., 3] > 128
        fm = flat_mask(img[..., :3].astype(np.int32)) & ink
        cols = palette(img[..., :3].astype(np.int32), fm, a.min_area,
                       a.merge, a.blend_tol)
        lab = label_badge(img[..., :3].astype(np.int32), ink, cols, a.sigma)

        dark = {i for i, c in enumerate(cols) if max(c) < a.outline_lum}
        lab = despeckle(lab, ink, a.min_blob * ink.sum(), dark)
        band = kcol = None
        res = even_outline(lab, cols, a.outline_lum, 0.002) if a.even_outline else None
        if res:
            lab, band, w, kcol = res

        # trim to the ink and scale so the badge prints W wide
        ys, xs = np.nonzero(lab >= 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        lab = lab[y0:y1, x0:x1]
        if band is not None:
            band = band[y0:y1, x0:x1]
        ph, pw = lab.shape
        s = W / pw
        out = pymupdf.open()
        page = out.new_page(width=pw * s, height=ph * s)

        order = sorted(range(len(cols)), key=lambda i: -(lab == i).sum())
        keep_u = upsample(lab >= 0, a.supersample, a.up_sigma)
        shapes = 0
        for i in order:
            m = lab == i
            if m.sum() < a.speckle:
                continue
            mu = upsample(m, a.supersample, a.up_sigma)
            if i in dark and a.outline_trim:
                # the hairline's soft flanks classify as hairline too, so it
                # traces a touch heavier than it is drawn
                # a cross, not a square: a square erodes diagonally too and
                # takes off about twice as much as intended
                mu = ndi.binary_erosion(
                    mu, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool),
                    iterations=a.outline_trim)
            else:
                mu = ndi.binary_dilation(mu, np.ones((3, 3), bool))
            mu &= keep_u
            for subs in trace(mu, work, a):
                sh = page.new_shape()
                emit(sh, subs, s / a.supersample, s / a.supersample)
                sh.finish(color=None, fill=[v / 255 for v in cols[i]],
                          even_odd=True, closePath=True, width=0)
                sh.commit()
                shapes += 1
        if band is not None and band.any():
            # the band gets the same dilation the fills got, or they eat into
            # it from both sides and the outline comes out uneven -- thick at
            # a spike's tip, thin along its flank
            # the band is grown off a skeleton, and a skeleton jitters by a
            # pixel wherever the shape it came from is a little fatter on one
            # side; dilated, that jitter becomes a visibly wavy outline, so
            # the band is smoothed harder than the fills are
            bu = upsample(band, a.supersample, a.band_sigma) & keep_u
            for subs in trace(bu, work, a):
                sh = page.new_shape()
                emit(sh, subs, s / a.supersample, s / a.supersample)
                sh.finish(color=None, fill=[v / 255 for v in cols[kcol]],
                          even_odd=True, closePath=True, width=0)
                sh.commit()
                shapes += 1

        f = os.path.join(a.out_dir, f'badge-{n}.pdf')
        out.save(f, garbage=4, deflate=True)
        made.append((f, pw * s, ph * s))
        note = f'outline {w*s:.2f} pt' if band is not None else 'no hairline found'
        print(f'badge {n}: {img.shape[1]}x{img.shape[0]} px, {len(cols)} fills, '
              f'{shapes} shapes, {pw*s:.1f} x {ph*s:.1f} pt, {note} '
              f'[{time.time()-t0:.1f}s]', file=sys.stderr)

    # one sheet with all three at the same printed width
    gap, pad = 6 * MM, 6 * MM
    tw = sum(w for _, w, _ in made) + gap * (len(made) - 1) + 2 * pad
    th = max(h for _, _, h in made) + 2 * pad
    sheet = pymupdf.open()
    pg = sheet.new_page(width=tw, height=th)
    x = pad
    for f, w, h in made:
        pg.show_pdf_page(pymupdf.Rect(x, pad + (th - 2 * pad - h) / 2,
                                      x + w, pad + (th - 2 * pad - h) / 2 + h),
                         pymupdf.open(f), 0)
        x += w + gap
    sf = os.path.join(a.out_dir, 'badges-30mm.pdf')
    sheet.save(sf, garbage=4, deflate=True)
    print(f'wrote {sf}: {tw:.1f} x {th:.1f} pt', file=sys.stderr)


if __name__ == '__main__':
    main()
