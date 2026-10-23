#!/usr/bin/env python3
"""Build the badges from the vector cross plus exact geometry.

Nothing here is traced from the badge artwork. The cross comes from the
logo's own vector; the square, the circle, the centre dot and the keyline
are drawn from measurements taken off the artwork. So the only thing read
from a raster is a handful of numbers -- sizes, colours, a stroke weight --
and every edge in the output is either the real curve or a true circle.
"""
import argparse, os, sys, tempfile
import numpy as np, pymupdf, vtracer
from scipy import ndimage as ndi
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vectorize import parse_svg, emit                      # noqa: E402
from badges import badges_of, flat_mask, palette, label_badge, despeckle, upsample  # noqa: E402

MM = 72.0 / 25.4


def cross_path(mask, work, opts):
    """Trace the vector cross once, at the resolution it was rendered."""
    return _trace(mask, work, opts), mask.shape


def _trace(mask, work, opts):
    png, svg = os.path.join(work, 'c.png'), os.path.join(work, 'c.svg')
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(png)
    vtracer.convert_image_to_svg_py(
        png, svg, colormode='binary', hierarchical='stacked', mode='spline',
        filter_speckle=4, corner_threshold=opts.corner, length_threshold=4.0,
        max_iterations=10, splice_threshold=45, path_precision=5)
    return parse_svg(open(svg).read())


def inset(mask, px):
    """The cross shrunk inward by px, as a real offset of its own outline.

    The band round the cross lies inside its silhouette. Stroking the
    silhouette instead centres the line on it, so half the band falls
    outside -- which both halves its apparent weight and pushes the arm tips
    off the page.
    """
    if px <= 0:
        return mask
    return ndi.distance_transform_edt(mask) > px


def _modal(rgb, m):
    v = rgb[m]
    if not len(v):
        return (0, 0, 0)
    q = (v // 6).astype(np.int64)
    ks, cnt = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    k = int(ks[cnt.argmax()])
    sel = ((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2]) == k
    return tuple(int(round(x)) for x in v[sel].mean(0))


def measure(img, cross, a):
    """Every badge is the same four parts, so only numbers need reading.

    A ground (a square, a circle, or nothing), the cross, a band round the
    cross, and a dot at the centre. Registering the logo's own cross against
    the artwork gives all of it: the band is what lies between the cross's
    true edge and the fill inside, and its width is simply where the colour
    stops changing.
    """
    ink = img[..., 3] > 128
    rgb = img[..., :3].astype(np.int32)
    H, W = ink.shape

    # ground: the colour of the badge's outer shell. Sampling the corners
    # instead misses a round badge, whose corners are not badge at all.
    ys0, xs0 = np.nonzero(ink)
    bw, bh = xs0.max() - xs0.min() + 1, ys0.max() - ys0.min() + 1
    fillfrac = ink.sum() / (bw * bh)
    shell = ink & (ndi.distance_transform_edt(ink) <= max(bw // 40, 2))
    ground = _modal(rgb, shell)
    # a cross standing on its own has arms, not a solid outline: its shell is
    # the band round the cross and its bounding box is mostly empty
    if fillfrac < 0.62:
        ground = None

    # the cross silhouette: ink that is not ground
    if ground is None:
        sil = ink
    else:
        sil = ink & (np.abs(rgb - np.array(ground)).max(-1) > 40)
    L, n = ndi.label(sil)
    if n:
        sz = ndi.sum(sil, L, range(1, n + 1))
        sil = (L == 1 + int(np.argmax(sz)))
    ys, xs = np.nonzero(sil)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

    # scale the logo's cross onto that box
    ch, cw = cross.shape
    zy, zx = (box[3] - box[1]) / ch, (box[2] - box[0]) / cw
    V = ndi.zoom(cross.astype(np.float32), (zy, zx), order=1) >= 0.5
    pad = np.zeros_like(ink)
    pad[box[1]:box[1] + V.shape[0], box[0]:box[0] + V.shape[1]] = V[
        :H - box[1], :W - box[0]]
    V = pad

    # walk inwards from the cross's true edge and read the colours off in
    # order. The first is the band, the next is the fill; if the first is
    # simply the ground showing through, the cross sits a little inside the
    # registered outline, so step past it.
    side = max(box[2] - box[0], box[3] - box[1])
    dist = ndi.distance_transform_edt(V)
    prof = []
    for d in range(1, max(int(side * 0.25), 6)):
        m = V & (dist > d) & (dist <= d + 1.5)
        if m.sum() < 40:
            break
        prof.append((d, _modal(rgb, m)))
    def same(x, y):
        return np.abs(np.array(x) - np.array(y)).max() <= 40
    i = 0
    while i < len(prof) - 1 and ground is not None and same(prof[i][1], ground):
        i += 1
    outer = prof[i][1] if prof else (0, 0, 0)
    band_w = 0
    fill = outer
    for d, c in prof[i:]:
        if not same(c, outer):
            fill = c
            break
    if not same(fill, outer):
        # width as area over length, the same way the keyline is measured.
        # Walking inwards in steps only says which ring the colour changes
        # in, which rounds the band down by a third.
        from skimage.morphology import skeletonize as _sk
        # over the whole badge, not inside the registered outline: that
        # outline sits a shade inside the band's true edge, which clipped
        # the band by about a quarter
        bm = ink & (np.abs(rgb - np.array(outer)).max(-1) <= 40)
        if bm.any():
            band_w = bm.sum() / max(int(_sk(bm).sum()), 1)

    # the dot at the centre
    cy, cx = (box[1] + box[3]) / 2, (box[0] + box[2]) / 2
    yy, xx = np.ogrid[:H, :W]
    rr = np.hypot(yy - cy, xx - cx)
    dot_col = _modal(rgb, rr <= side * 0.012)
    dot_r = dot_ring = 0.0
    dot_edge = None
    for r in np.arange(side * 0.012, side * 0.10, 0.5):
        ring = (rr > r) & (rr <= r + 2)
        c = _modal(rgb, ring)
        # tighter than elsewhere: this badge's two greens differ by 38, so a
        # threshold of 40 reads the dot and its ring as one colour
        if np.abs(np.array(c) - np.array(dot_col)).max() > 22:
            dot_r, dot_edge = r / side, c
            break
    if dot_edge is not None:
        # the dot has its own outline, a ring of its own colour round it,
        # and drawing it as one flat disc loses that
        # start past the boundary itself, or the core colour still in the
        # first ring ends the walk before it begins
        for r in np.arange(dot_r * side + 2.5, side * 0.16, 0.5):
            ring = (rr > r) & (rr <= r + 2)
            if np.abs(np.array(_modal(rgb, ring)) - np.array(dot_edge)).max() > 22:
                dot_ring = r / side - dot_r
                break

    # the keyline round the ground, same ink as the band when it is dark
    gw, gh = box[2] - box[0], box[3] - box[1]
    shape = None
    if ground is not None:
        shape = 'square' if fillfrac > 0.88 else 'circle'
    # the dark keyline measured on its own: a hairline this thin slips
    # between the steps of the walk above
    from skimage.morphology import skeletonize
    dk = ink & (rgb.max(-1) < a.outline_lum)
    key, key_w = None, 0.0
    if dk.sum() > 0.0005 * ink.sum():
        # only the thin dark ink counts. On a badge whose cross is itself
        # dark, area over length measures the cross, not the keyline, and
        # came back at sixteen points -- wide enough to swallow the badge.
        dd = ndi.distance_transform_edt(dk)
        sk = skeletonize(dk)
        w = 2 * dd[sk]
        w = w[w <= 0.03 * bw]
        if w.size:
            key = _modal(rgb, dk & (dd <= 0.015 * bw))
            key_w = float(np.median(w)) / bw
    return dict(ground=ground, shape=shape, band=outer, band_w=band_w / side,
                key=key, key_w=key_w, bw=bw,
                fill=fill, dot=dot_col, dot_r=dot_r,
                dot_ring=dot_ring, dot_edge=dot_edge,
                cross_w=gw / bw, cross_h=gh / bh, side=side,
                box=box, H=H, W=W)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('cross_npy')
    ap.add_argument('out_dir')
    ap.add_argument('--width-mm', type=float, default=30.0)
    ap.add_argument('--dpi', type=int, default=600)
    ap.add_argument('--pre-scale', type=int, default=2)
    ap.add_argument('--sigma', type=float, default=1.1)
    ap.add_argument('--min-area', type=float, default=0.0006)
    ap.add_argument('--merge', type=float, default=26.0)
    ap.add_argument('--blend-tol', type=float, default=0.18)
    ap.add_argument('--min-blob', type=float, default=0.002)
    ap.add_argument('--outline-lum', type=float, default=90.0)
    ap.add_argument('--corner', type=int, default=60)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    work = tempfile.mkdtemp()
    shapes, (ch, cw) = cross_path(np.load(a.cross_npy), work, a)
    print(f'cross from the logo vector: {cw}x{ch} px, {len(shapes)} shapes',
          file=sys.stderr)

    W = a.width_mm * MM
    cross = np.load(a.cross_npy)
    made = []
    for n, img in enumerate(badges_of(a.src, a.dpi, a.width_mm, a.pre_scale), start=1):
        g = measure(img, cross, a)
        out = pymupdf.open()
        page = out.new_page(width=W, height=W)
        # whichever outline is actually the wider one is the real outline:
        # the green badge carries a thick coloured band and only a sliver of
        # dark pixels, which otherwise wins on being dark alone
        kd, bd = g['key_w'] * W, g['band_w'] * W
        dark = g['key'] is not None and kd >= bd
        key = g['key'] if dark else g['band']
        kw = band_w = kd if dark else bd

        if g['ground'] is not None:
            # a true square or a true circle, not a traced one
            sh = page.new_shape()
            r = pymupdf.Rect(kw, kw, W - kw, W - kw)
            sh.draw_rect(r) if g['shape'] == 'square' else sh.draw_oval(r)
            sh.finish(color=[v / 255 for v in key] if dark else None,
                      fill=[v / 255 for v in g['ground']],
                      width=kw if dark else 0, closePath=True, lineJoin=1)
            sh.commit()

        # the logo's own cross. The band is a second, smaller copy of the
        # same curve rather than a stroke, so it sits wholly inside the
        # silhouette at its full weight and nothing overhangs the page.
        ch, cw = cross.shape
        s_ = g['cross_w'] * (W - 2 * kw) / cw
        ox, oy = (W - cw * s_) / 2, (W - ch * s_) / 2
        shift = lambda subs: [[(op, (q[0] + ox / s_, q[1] + oy / s_)) if op != 'C'
                               else (op, [(r[0] + ox / s_, r[1] + oy / s_) for r in q])
                               for op, q in sp] for sp in subs]
        layers = [(shapes, g['band'] if band_w > 0 else g['fill'])]
        if band_w > 0:
            inner = _trace(inset(cross, band_w / s_), work, a)
            if inner:
                layers.append((inner, g['fill']))
        for i, (shps, col) in enumerate(layers):
            for subs in shps:
                sh = page.new_shape()
                emit(sh, shift(subs), s_, s_)
                sh.finish(color=[v / 255 for v in key] if (dark and i == 0) else None,
                          fill=[v / 255 for v in col],
                          width=kw if (dark and i == 0) else 0,
                          even_odd=True, closePath=True, lineJoin=1)
                sh.commit()

        if g['dot_r'] > 0:
            sh = page.new_shape()
            r = g['dot_r'] * W
            sh.draw_circle(pymupdf.Point(W / 2, W / 2), r)
            sh.finish(color=[v / 255 for v in key] if dark else None,
                      fill=[v / 255 for v in g['dot']],
                      width=kw if dark else 0, closePath=True)
            sh.commit()

        f = os.path.join(a.out_dir, f'badge-{n}.pdf')
        out.save(f, garbage=4, deflate=True)
        made.append(f)
        print(f"badge {n}: ground {g['shape']} #{'%02x%02x%02x' % g['ground'] if g['ground'] else '--'}, "
              f"cross #{'%02x%02x%02x' % g['fill']}, "
              f"{'keyline' if dark else 'band'} #{'%02x%02x%02x' % key} "
              f"{band_w:.2f} pt, dot r {g['dot_r']*W:.2f} pt", file=sys.stderr)


if __name__ == '__main__':
    main()
