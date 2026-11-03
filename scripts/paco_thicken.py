#!/usr/bin/env python3
"""Raise every stroke of the PA & CO logo to a minimum width, in place.

The logo is a Didone, so its thick-to-thin contrast is around 5:1: stems of
1.1-1.7 mm against hairlines of 0.25-0.33 mm at 50 mm wide. Scaling the
whole logo up to clear a 1 mm minimum would need it at 200 mm, and simply
outsetting every edge would fatten the stems just as much and close the
counters. Neither keeps the drawing.

So this thickens only what is too thin. Along the medial axis, every point
carries the radius of the largest disc that fits there, which is half the
local stroke width. Clamp that radius to the minimum and take the union of
those discs with the original: a point already thicker than the minimum
contributes a disc that was inside the shape anyway, so the stems are
untouched to the pixel, while the hairlines grow to exactly the minimum.

Proportions are kept: nothing moves, nothing scales, the outer silhouette
only ever grows outward, and the letter positions, heights and stems are
the artwork's own.

    python3 scripts/paco_thicken.py --min-mm 1.0
"""
import argparse, os
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from skimage.morphology import medial_axis

PPMM = 60                     # raster resolution, px per mm (0.017 mm)


def render(path, ppmm=PPMM):
    d = pymupdf.open(path)
    p = d[0]
    k = ppmm * 25.4 / 72.0
    pm = p.get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    a = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples))
    return a < 128, p.rect.width / 72 * 25.4, p.rect.height / 72 * 25.4


def disc(r_px):
    n = int(np.ceil(r_px))
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return (x * x + y * y) <= r_px * r_px


def widths(mask, ppmm=PPMM):
    """Stroke width in mm at every point of the medial axis."""
    skel, dist = medial_axis(mask, return_distance=True)
    return skel, dist, 2.0 * dist[skel] / ppmm


def endpoints(skel):
    """Spine pixels with at most one neighbour: serif tips, the diamond point."""
    k = np.ones((3, 3), int)
    nb = ndimage.convolve(skel.astype(int), k, mode='constant') - skel
    return skel & (nb <= 1)


def thicken(mask, min_mm, ppmm=PPMM, cache={}):
    """Grow only what is thinner than min_mm, and leave the terminals alone.

    A disc centred on a spine endpoint would stick out past the tip by its
    whole radius, capping every serif and the diamond's point with a little
    dome. So the spine within one radius of an endpoint is held back: the
    stroke behind the terminal thickens, the terminal keeps the taper it
    was drawn with.
    """
    key = id(mask)
    if key not in cache:
        cache[key] = medial_axis(mask, return_distance=True)
    skel, dist = cache[key]
    r0 = (min_mm / 2.0) * ppmm
    tips = ndimage.binary_dilation(endpoints(skel), disc(r0 * 1.15))
    thin = skel & (dist < r0) & ~tips
    if not thin.any():
        return mask.copy(), 0
    return mask | ndimage.binary_dilation(thin, disc(r0)), int(thin.sum())


def report(mask, label, ppmm=PPMM, target=None):
    lab, n = ndimage.label(mask)
    sl = ndimage.find_objects(lab)
    keep = [(k, s) for k, s in enumerate(sl)
            if (lab[s] == k + 1).sum() > 200]
    keep.sort(key=lambda t: t[1][1].start)
    thinnest = 9e9
    allw = []
    for k, s in keep:
        comp = lab[s] == k + 1
        _, _, w = widths(comp, ppmm)
        w = w[w > 0.04]
        allw.append(w)
        thinnest = min(thinnest, float(np.percentile(w, 10)))
    allw = np.concatenate(allw)
    # counters: holes inside the ink
    holes = ndimage.binary_fill_holes(mask) & ~mask
    hl, hn = ndimage.label(holes)
    hsz = np.bincount(hl.ravel())[1:]
    big = hsz[hsz > 40]
    t = target if target else 1.0
    print(f'  {label:<18} shapes {len(keep):>2}  p10 {thinnest:.2f} mm  '
          f'median {np.median(allw):.2f}  '
          f'spine under {t:g} mm: {100*(allw < t).mean():.0f}%  '
          f'counters {len(big)}')
    return len(keep), thinnest, len(big)


def to_pdf(mask, w_mm, h_mm, path, ppmm=PPMM, tol_mm=0.012):
    """Trace the raster back to filled vector paths, even-odd for counters."""
    pad = np.pad(mask, 2, constant_values=False)
    doc = pymupdf.open()
    MM = 72.0 / 25.4
    page = doc.new_page(width=w_mm * MM, height=h_mm * MM)
    shape = page.new_shape()
    tol_px = max(0.4, tol_mm * ppmm)
    n = 0
    for c in find_contours(pad.astype(float), 0.5):
        c = approximate_polygon(c, tolerance=tol_px)
        if len(c) < 3:
            continue
        pts = [pymupdf.Point((x - 2) / ppmm * MM, (y - 2) / ppmm * MM)
               for y, x in c]
        shape.draw_polyline(pts + [pts[0]])
        n += 1
    shape.finish(color=None, fill=(0, 0, 0), even_odd=True, closePath=True)
    shape.commit()
    doc.save(path)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='assets/paco/paco-50mm.pdf')
    ap.add_argument('--out', default='assets/paco')
    ap.add_argument('--min-mm', type=float, nargs='+', default=[1.0, 1.5])
    a = ap.parse_args()

    mask, w_mm, h_mm = render(a.src)
    print(f'{a.src}  {w_mm:.2f} x {h_mm:.2f} mm  at {PPMM} px/mm')
    print('\nbefore:')
    report(mask, 'original', target=1.0)

    for mn in a.min_mm:
        thick, npts = thicken(mask, mn)
        tag = f'{mn:g}'.replace('.', 'p')
        out = os.path.join(a.out, f'paco-50mm-min{tag}mm.pdf')
        print(f'\nminimum {mn:g} mm  (thickened {npts} spine points):')
        report(thick, f'min {mn:g} mm', target=mn)
        paths = to_pdf(thick, w_mm, h_mm, out)
        gain = 100.0 * (thick.sum() - mask.sum()) / mask.sum()
        print(f'  ink area +{gain:.1f}%   {paths} contours   -> {out}')


if __name__ == '__main__':
    main()
