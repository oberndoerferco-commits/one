#!/usr/bin/env python3
"""Replace the patches on a garment mockup with vector ones, in place.

Each patch is measured where it sits on the mockup -- its colours, the
weight of its outline, the size of its dot -- and rebuilt from the logo's
own curve. Matching them against a library of finished badges instead is
unreliable at this size: a patch is a few hundred pixels across, sitting on
patterned cloth, and the nearest match by image is often simply the one
with the most neutral colours.
"""
import argparse, json, os, sys
import numpy as np, pymupdf
from scipy import ndimage as ndi
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from badges_vector import measure                    # noqa: E402
from badges_logo import flatten, draw                # noqa: E402

MM = 72.0 / 25.4


def colourways(doc, xref):
    """The separate colourways inside one raster, at native size."""
    pix = pymupdf.Pixmap(doc, xref)
    sm = doc.xref_get_key(xref, 'SMask')
    if sm[0] == 'xref':
        pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, int(sm[1].split()[0])))
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    al = a[..., 3] > 128
    L, n = ndi.label(ndi.binary_closing(al, np.ones((3, 3))))
    out = []
    for i, sl in enumerate(ndi.find_objects(L), 1):
        if sl is None:
            continue
        m = ndi.binary_fill_holes(L[sl] == i)
        if m.sum() < 300:
            continue
        c = a[sl].copy()
        c[..., 3] = np.where(m, 255, 0)
        out.append(np.pad(c, ((4, 4), (4, 4), (0, 0))))
    return out


def _inks(rgb, mask, k=2, bucket=16):
    v = rgb[mask]
    if len(v) < 20:
        return []
    q = (v // bucket).astype(np.int64)
    ks, c = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    return [np.array([(int(ks[i]) >> 16) & 255, (int(ks[i]) >> 8) & 255,
                      int(ks[i]) & 255]) * bucket + bucket // 2
            for i in np.argsort(-c)[:k]]


def patches_boxed(page, dpi=1600, min_pt=5.0):
    """One patch per placement, cut from a page holding only the patches.

    Segmenting the page alone merges any two patches that touch, and this
    artwork overlaps them deliberately. The file still lists a placement
    per patch, so each is cut at its own box and the piece nearest its
    centre is taken.
    """
    out = []
    for b in page.get_image_info(xrefs=True):
        if b['width'] >= 200:
            continue
        r = pymupdf.Rect(b['bbox'])
        pm = page.get_pixmap(dpi=dpi, clip=r, alpha=False)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
        s = r.width / pm.width
        L, n = ndi.label(ndi.binary_closing(a.min(-1) < 242, np.ones((3, 3))))
        if not n:
            continue
        cy, cx = a.shape[0] / 2, a.shape[1] / 2
        best, bd = None, 1e9
        for i, sl in enumerate(ndi.find_objects(L), 1):
            if sl is None:
                continue
            m = ndi.binary_fill_holes(L[sl] == i)
            if m.sum() < 1200:
                continue
            yy, xx = ndi.center_of_mass(m)
            d = np.hypot(yy + sl[0].start - cy, xx + sl[1].start - cx)
            if d < bd:
                bd, best = d, (sl, m)
        if best is None:
            continue
        sl, m = best
        if (sl[1].stop - sl[1].start) * s < min_pt:
            continue
        crop = np.dstack([a[sl], np.where(m, 255, 0).astype(np.uint8)])
        out.append((pymupdf.Rect(r.x0 + sl[1].start * s, r.y0 + sl[0].start * s,
                                 r.x0 + sl[1].stop * s, r.y0 + sl[0].stop * s),
                    np.pad(crop, ((6, 6), (6, 6), (0, 0)))))
    ded = []
    for r, c in out:
        if all(abs(r.x0 - e.x0) > 2 or abs(r.y0 - e.y0) > 2 for e, _ in ded):
            ded.append((r, c))
    return ded


def patches_on_white(page, dpi=1200, min_pt=5.0, close=5):
    """Each patch cut straight off a page that has nothing else on it.

    This is the way to do it. On a garment mockup a patch is a few
    millimetres across on patterned cloth and its colours read back as the
    cloth's; with the garment layer hidden they are simply the artwork's.
    """
    pm = page.get_pixmap(dpi=dpi, alpha=False)
    a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    s = 72.0 / dpi
    ink = a.min(-1) < 242
    L, n = ndi.label(ndi.binary_closing(ink, np.ones((close, close))))
    out = []
    for i, sl in enumerate(ndi.find_objects(L), 1):
        if sl is None:
            continue
        m = ndi.binary_fill_holes(L[sl] == i)
        w = (sl[1].stop - sl[1].start) * s
        if m.sum() < 1500 or w < min_pt or w > 60:
            continue
        crop = np.dstack([a[sl], np.where(m, 255, 0).astype(np.uint8)])
        out.append((pymupdf.Rect(sl[1].start * s, sl[0].start * s,
                                 sl[1].stop * s, sl[0].stop * s),
                    np.pad(crop, ((6, 6), (6, 6), (0, 0)))))
    return out


def patches(page, dpi=1600, min_pt=8.0, doc=None):
    """(rect on the page, RGBA crop) for each patch.

    The crop is taken from the raster, not from the mockup: a patch is only
    a few millimetres across there, sitting on patterned cloth, and its
    colours come back as the cloth's. The mockup is used only to see which
    of the raster's colourways is the one on show.
    """
    out = []
    for b in page.get_image_info(xrefs=True):
        if b['width'] >= 200:                 # the garment photo itself
            continue
        r = pymupdf.Rect(b['bbox'])
        pm = page.get_pixmap(dpi=dpi, clip=r, alpha=False)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
        v = a.astype(int)
        mx, mn = v.max(-1), v.min(-1)
        # the cloth is near-neutral; a patch is either saturated or very dark
        m = ndi.binary_closing(((mx - mn) > 75) | (mx < 55), np.ones((9, 9)))
        L, n = ndi.label(m)
        if not n:
            continue
        sz = ndi.sum(m, L, range(1, n + 1))
        i = 1 + int(np.argmax(sz))
        sl = ndi.find_objects(L)[i - 1]
        mask = ndi.binary_fill_holes(L[sl] == i)
        s = r.width / pm.width
        w = (sl[1].stop - sl[1].start) * s
        if w < min_pt or mask.sum() < 2000:
            continue
        seen = _inks(a[sl].astype(int), mask)
        ways = colourways(doc, b['xref'])
        best, bd = None, 1e9
        for cw in ways:
            cand = _inks(cw[..., :3].astype(int), cw[..., 3] > 128)
            if not cand or not seen:
                continue
            d = float(np.mean([min(np.linalg.norm(x - y) for y in cand) for x in seen]))
            if d < bd:
                bd, best = d, cw
        if best is None:
            continue
        out.append((pymupdf.Rect(r.x0 + sl[1].start * s, r.y0 + sl[0].start * s,
                                 r.x0 + sl[1].stop * s, r.y0 + sl[0].stop * s),
                    best))
    # two placements can resolve to the same patch
    ded = []
    for r, c in out:
        if all(abs(r.x0 - e.x0) > 3 or abs(r.y0 - e.y0) > 3 for e, _ in ded):
            ded.append((r, c))
    return ded


def build(page, rect, g, poly, cross_shape, a):
    """Draw one patch as vectors, filling the rect it occupied."""
    W = max(rect.width, rect.height)
    kd, bd = g['key_w'] * W, g['band_w'] * W
    dark = g['key'] is not None and kd >= bd
    key = g['key'] if dark else g['band']
    kw = kd if dark else 0.0
    band = 0.0 if dark else bd * a.band_scale
    ox, oy = rect.x0, rect.y0

    if g['ground'] is not None:
        sh = page.new_shape()
        r = pymupdf.Rect(ox + kw, oy + kw, ox + W - kw, oy + W - kw)
        sh.draw_rect(r) if g['shape'] == 'square' else sh.draw_oval(r)
        sh.finish(color=[v / 255 for v in key] if kw else None,
                  fill=[v / 255 for v in g['ground']], width=kw,
                  closePath=True, lineJoin=1)
        sh.commit()

    ch, cw = cross_shape
    side = g['cross_w'] * (W - 2 * (kw + band * a.band_out))
    P = poly * side + np.array([ox + (W - side) / 2, oy + (W - side) / 2])
    if band <= 0:
        draw(page, P, g['fill'], key, kw)
    else:
        sil = Polygon(P).buffer(0)
        o_g = sil.buffer(band * a.band_out, join_style=1, resolution=32)
        i_g = sil.buffer(-band * (1 - a.band_out), join_style=1, resolution=32)
        for geo, col in ((o_g, g['band']), (i_g, g['fill'])):
            if geo.is_empty:
                continue
            for gg in ([geo] if geo.geom_type == 'Polygon' else geo.geoms):
                draw(page, np.array(gg.exterior.coords), col,
                     key, kw if col is g['band'] else 0)

    if g['dot_r'] > 0:
        c = pymupdf.Point(ox + W / 2, oy + W / 2)
        ring = g.get('dot_ring', 0.0) * W
        edge = g.get('dot_edge') or key
        if ring > 0:
            sh = page.new_shape()
            sh.draw_circle(c, g['dot_r'] * W + ring)
            sh.finish(color=None, fill=[v / 255 for v in edge], width=0)
            sh.commit()
        sh = page.new_shape()
        sh.draw_circle(c, g['dot_r'] * W)
        sh.finish(color=[v / 255 for v in key] if (kw and not ring) else None,
                  fill=[v / 255 for v in g['dot']],
                  width=kw if (kw and not ring) else 0, closePath=True)
        sh.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('logo_json')
    ap.add_argument('out_dir')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--dpi', type=int, default=1600)
    ap.add_argument('--sigma', type=float, default=1.1)
    ap.add_argument('--min-area', type=float, default=0.0006)
    ap.add_argument('--merge', type=float, default=26.0)
    ap.add_argument('--blend-tol', type=float, default=0.18)
    ap.add_argument('--min-blob', type=float, default=0.002)
    ap.add_argument('--outline-lum', type=float, default=60.0)
    ap.add_argument('--band-out', type=float, default=0.7)
    ap.add_argument('--band-scale', type=float, default=0.88)
    ap.add_argument('--corner', type=int, default=60)
    ap.add_argument('--on-white', action='store_true',
                    help='the page holds only the patches')
    ap.add_argument('--min-pt', type=float, default=5.0)
    ap.add_argument('--close', type=int, default=5)
    ap.add_argument('--over', default=None,
                    help='a mockup to lay the vector patches onto')
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    L = json.load(open(a.logo_json))
    poly = flatten(L['chain'])
    bb = L['bbox']
    poly -= np.array([bb[0], bb[1]])
    poly /= max(bb[2] - bb[0], bb[3] - bb[1])
    from PIL import Image, ImageDraw
    R = 512
    im = Image.new('L', (R, R), 0)
    ImageDraw.Draw(im).polygon([tuple(v) for v in (poly * (R - 1))], fill=255)
    ref = np.asarray(im) > 127

    doc = pymupdf.open(a.src)
    found = (patches_boxed(doc[a.page], a.dpi, a.min_pt)
             if a.on_white else patches(doc[a.page], a.dpi, doc=doc))
    print(f'{len(found)} patches on the mockup', file=sys.stderr)

    # the mockup with its patch rasters taken out
    base = pymupdf.open(a.src)
    for b in base[a.page].get_image_info(xrefs=True):
        if b['width'] < 200:
            base[a.page].delete_image(b['xref'])

    out = pymupdf.open()
    W, H = doc[a.page].rect.width, doc[a.page].rect.height
    # page objects go stale when another page is added, so they are fetched
    # by index at the point of drawing
    idx = []
    if a.over:
        ob = pymupdf.open(a.over)
        for b in ob[0].get_image_info(xrefs=True):
            if b['width'] < 200:
                ob[0].delete_image(b['xref'])
        out.new_page(width=W, height=H).show_pdf_page(
            pymupdf.Rect(0, 0, W, H), ob, 0)
        idx.append(0)
    k = len(out)
    out.new_page(width=W, height=H)
    if not a.over:
        out[k].show_pdf_page(doc[a.page].rect, base, a.page)
    idx.append(k)

    for n, (rect, crop) in enumerate(found, 1):
        g = measure(crop, ref, a)
        for j in idx:
            build(out[j], rect, g, poly, ref.shape, a)
        one = pymupdf.open()
        q = one.new_page(width=max(rect.width, rect.height),
                         height=max(rect.width, rect.height))
        build(q, pymupdf.Rect(0, 0, q.rect.width, q.rect.height), g, poly, ref.shape, a)
        one.save(os.path.join(a.out_dir, f'patch-{n}.pdf'), garbage=4, deflate=True)
        print(f"  patch {n}: {rect.width:.1f} pt, {g['shape'] or 'no ground'}, "
              f"cross #{'%02x%02x%02x' % g['fill']}", file=sys.stderr)

    f = os.path.join(a.out_dir, 'jacket-vector.pdf')
    out.save(f, garbage=4, deflate=True)
    print(f'wrote {f}', file=sys.stderr)


if __name__ == '__main__':
    main()
