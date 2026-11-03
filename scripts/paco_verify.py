#!/usr/bin/env python3
"""Check a logo against a minimum feature size, in the ink and in the white.

Three attempts were needed to get the white right, so the reasoning is
worth recording.

The first version measured only enclosed counters. That missed the notch
beside the O's stem, which is open at one side, and which bolding had
closed to 0.14 mm.

Measuring the white by the minimum of its medial axis does not work: white
runs to nothing in the crook of every acute corner, so the minimum is
always about zero and says nothing about anything.

Closing the ink with a disc, which is what a die physically does, does not
work either: a disc cannot enter any corner sharper than itself, so every
serif bracket and every letter joint is reported as filled, 56 of them in
the untouched original.

What distinguishes a real defect is that a channel has white on a path
BETWEEN two edges, while a corner is a dead end. On the medial axis of the
white, a dead end is an endpoint. So the spine is measured with its
endpoint neighbourhoods removed, exactly as stroke width is measured with
the terminals removed, and what is left is the channels.
"""
import sys
import numpy as np, pymupdf
from PIL import Image
from scipy import ndimage
from skimage.morphology import medial_axis

PPMM = 70


def load(path, ppmm=PPMM):
    d = pymupdf.open(path); p = d[0]; k = ppmm * 25.4 / 72.0
    pm = p.get_pixmap(matrix=pymupdf.Matrix(k, k), colorspace=pymupdf.csGRAY)
    a = np.asarray(Image.frombytes('L', (pm.width, pm.height), pm.samples))
    return a < 128, p.rect.width / 72 * 25.4, p.rect.height / 72 * 25.4


def _ends(skel):
    nb = ndimage.convolve(skel.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - skel
    return skel & (nb <= 1)


def thinnest_ink(mask, ppmm=PPMM):
    lab, _ = ndimage.label(mask)
    sz = np.bincount(lab.ravel())[1:]
    out = []
    for k in np.nonzero(sz > 400)[0]:
        sk, dist = medial_axis(lab == k + 1, return_distance=True)
        w = 2.0 * dist[sk] / ppmm
        out.append(float(np.percentile(w[w > 0.05], 10)))
    return int((sz > 400).sum()), min(out)


def tightest_white(mask, ppmm=PPMM, pad_mm=2.0, cap_mm=4.0, n=6):
    """The narrowest channels in the white, ignoring corner dead ends."""
    p = int(pad_mm * ppmm)
    ys, xs = np.nonzero(mask)
    # pad explicitly: the artwork can sit flush against the page edge, and a
    # slice would then leave no white there and invent a zero-width channel
    sub = np.pad(mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1], p,
                 constant_values=False)
    y0, x0 = ys.min() - p, xs.min() - p
    sk, dist = medial_axis(~sub, return_distance=True)
    r = int(round(0.6 * ppmm))
    k = np.ones((2 * r + 1, 2 * r + 1), bool)
    keep = sk & ~ndimage.binary_dilation(_ends(sk), k) & (2 * dist / ppmm < cap_mm)
    if not keep.any():
        return 9.99, []
    w = 2 * dist / ppmm
    ys2, xs2 = np.nonzero(keep)
    order = np.argsort(w[ys2, xs2])
    spots, seen = [], []
    for i in order:
        x, y, ww = xs2[i] + x0, ys2[i] + y0, w[ys2[i], xs2[i]]
        if any(abs(x - sx) < 1.2 * ppmm and abs(y - sy) < 1.2 * ppmm
               for sx, sy, _ in seen):
            continue
        seen.append((x, y, ww)); spots.append((x / ppmm, y / ppmm, float(ww)))
        if len(spots) >= n:
            break
    return spots[0][2], spots


if __name__ == '__main__':
    target = float(sys.argv[1]) if sys.argv[1].replace('.', '').isdigit() else 1.0
    args = sys.argv[2:] if sys.argv[1].replace('.', '').isdigit() else sys.argv[1:]
    for arg in args:
        path, _, label = arg.partition('=')
        mask, W, H = load(path)
        n, hair = thinnest_ink(mask)
        wmin, spots = tightest_white(mask)
        ok = 'OK  ' if (hair >= target - 0.03 and wmin >= target - 0.03) else 'FAIL'
        print(f'{ok} {label or path:<24} {W:5.1f} x {H:4.1f} mm  shapes {n:>2}  '
              f'thinnest ink {hair:.2f} mm   tightest gap {wmin:.2f} mm')
        for x, y, w in spots[:3]:
            flag = '  <-- under target' if w < target - 0.03 else ''
            print(f'       gap {w:.2f} mm at x {x:5.1f}  y {y:5.1f}{flag}')
