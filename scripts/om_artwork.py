#!/usr/bin/env python3
"""Vectorise the hand-drawn OM artwork - all three layers, exactly as drawn.

An earlier version of this rebuilt the cream keyline and the cyan hatch from
measurements instead of tracing them.  That was wrong twice over: it was not
asked for, and the hatch was modelled as a drop shadow - a translated copy of
the letters - when the drawing's hatch is a halo that follows the letter all the
way round.  A halo correlates well enough with a translated copy that the fitted
offset looked convincing while the shape was not.

So: every layer is traced.  The only thing changed is the one thing asked for,
which is that the M is made symmetrical, and that is applied to the black and
the cream together so the keyline keeps hugging the letter.  The cyan is left
alone, because mirroring a 45 degree hatch would fold it into a chevron.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_lineart as vl
import pathio
from om_hand import layers, write_pdf, write_svg, CYAN, CREAM, BLACK


def mirror_pair(masks, axis_from):
    """Mirror several layers about one axis, solved for on the first of them."""
    f0 = masks[axis_from].astype(np.float64)
    ys, xs = np.nonzero(masks[axis_from])
    yy, xx = np.mgrid[0:f0.shape[0], 0:f0.shape[1]].astype(np.float64)
    c0 = float(xs.mean())
    best, bc = None, c0
    for d in np.arange(-14.0, 14.001, 0.1):
        c = c0 + d
        mir = ndi.map_coordinates(f0, [yy, 2 * c - xx], order=1, mode='constant')
        e = float(np.abs(f0 - mir).sum())
        if best is None or e < best:
            best, bc = e, c
    print('      mirror axis %.2f px (centroid %.2f)' % (bc, c0))
    out = []
    for m in masks:
        f = m.astype(np.float64)
        mir = ndi.map_coordinates(f, [yy, 2 * bc - xx], order=3, mode='constant')
        out.append(0.5 * (f + mir))
    return out


def _disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def repair(mask, keyline, r):
    """Give back the bites the keyline took out of a layer.

    The three layers are separated by colour, so they are disjoint: wherever the
    cream keyline strayed over the edge of a letter or a hatch stroke, those
    pixels were classed cream and the layer underneath lost them.  In the colour
    artwork that is invisible, because the cream sits in the bite and fills it.
    In the one-colour version the cream is gone and every bite reads as a white
    nick chewed out of the letter.

    A bite is a concavity no deeper than the keyline is wide which is actually
    covered by keyline ink, so closing by that radius and intersecting with the
    cream finds them without inventing ink anywhere the drawing left white.
    """
    return mask | (ndi.binary_closing(mask, _disk(r)) & keyline)


def clear_of(mask, letters, g, keep=0.25):
    """Hold a layer a constant distance off the letters.

    Cutting a diagonal stroke against a curved boundary can leave a thin wedge
    behind - the far corner of the stroke, orphaned by the cut - which reads as
    a splinter rather than as part of the hatch.  Anything left smaller than
    `keep` of the median stroke goes with it.
    """
    out = mask & ~ndi.binary_dilation(letters, _disk(g))
    lab, n = ndi.label(out)
    if n:
        sz = ndi.sum(out, lab, range(1, n + 1))
        floor = keep * np.median(sz[sz > np.percentile(sz, 40)])
        drop = np.flatnonzero(sz < floor) + 1
        if len(drop):
            out = out & ~np.isin(lab, drop)
            print('      dropped %d splinter(s) left by the cut' % len(drop))
    return out


def trace_layer(field, sigma, **fit):
    return vl.trace(1.0 - field, level=0.5, sigma=sigma, dot_area=0,
                    min_area=60, min_contour_area=40.0, **fit)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--size', type=float, default=480.0)
    ap.add_argument('--sigma', type=float, default=1.2)
    ap.add_argument('--cyan-sigma', type=float, default=0.7,
                    help='the hatch is traced less smoothed than the letters: '
                         'at 1.2 the blur closes the narrow white gaps where two '
                         'strokes nearly touch and fuses them into one')
    ap.add_argument('--line-tol', type=float, default=1.1)
    ap.add_argument('--curve-tol', type=float, default=0.7)
    ap.add_argument('--repair', type=int, default=6,
                    help='radius in source px for giving back the bites the '
                         'cream keyline took out of the letters and the hatch')
    ap.add_argument('--gap', type=int, default=14,
                    help='in the one-colour version the keyline is gone, so the '
                         'hatch is held this far off the letters and that even '
                         'white channel does the keyline\'s job')
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    fit = dict(line_tol=a.line_tol, curve_tol=a.curve_tol,
               smooth_deg=34.0, min_smooth_run=3)

    black, cream, cyan = layers(a.image)
    b0, c0 = black.sum(), cyan.sum()
    black = repair(black, cream, a.repair)
    cyan = repair(cyan, cream, a.repair)
    print('   keyline bites given back: letters %d px, hatch %d px'
          % (black.sum() - b0, cyan.sum() - c0))

    # the M half of the drawing, so black and cream can be mirrored together
    lab, n = ndi.label(black)
    sizes = ndi.sum(black, lab, range(1, n + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s > 2000]
    cols = {i: np.nonzero((lab == i).any(0))[0] for i in big}
    m_id = max(big, key=lambda i: cols[i].mean())
    split_x = int((max(cols[i].min() for i in big if i == m_id)
                   + max(cols[i].max() for i in big if i != m_id)) / 2)
    print('   splitting O from M at x=%d' % split_x)
    right = np.zeros_like(black)
    right[:, split_x:] = True

    bl = black.astype(float)
    cr = cream.astype(float)
    print('   M: symmetrising black + cream together')
    mb, mc = mirror_pair([black & right, cream & right], 0)
    bl = np.where(right, mb, bl)
    cr = np.where(right, mc, cr)

    cap_px = float(np.ptp(np.nonzero(black & ~right)[0]))
    k = a.size / cap_px
    H = black.shape[0]
    out = {}
    # the hatch is traced twice: as drawn for the colour artwork, where the
    # cream keyline separates it from the letters, and held clear of the letters
    # for the one-colour version, where nothing else would
    cyan_clear = clear_of(cyan, bl > 0.5, a.gap)
    print('   one-colour hatch held %d px off the letters (%d px trimmed, %.1f%%)'
          % (a.gap, cyan.sum() - cyan_clear.sum(),
             100.0 * (cyan.sum() - cyan_clear.sum()) / cyan.sum()))
    for nm, f, sg in (('cyan', cyan.astype(float), a.cyan_sigma),
                      ('cyan_clear', cyan_clear.astype(float), a.cyan_sigma),
                      ('cream', cr, a.sigma),
                      ('black', bl, a.sigma)):
        cs = trace_layer(f, sg, **fit)
        out[nm] = [((c[0][0] * k, (H - c[0][1]) * k),
                    [(q[0],) + tuple((p[0] * k, (H - p[1]) * k) for p in q[1:])
                     for q in c[1]]) for c in cs]
        print('   %-6s %4d contours, %5d segments'
              % (nm, len(cs), sum(len(c[1]) for c in cs)))

    pts = [p for cs in out.values() for c in cs for q in [(('L',) + (c[0],))] + c[1]
           for p in q[1:]]
    x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
    x1 = max(p[0] for p in pts); y1 = max(p[1] for p in pts)
    pad = 0.05 * a.size
    mv = lambda cs: [((c[0][0] - x0 + pad, c[0][1] - y0 + pad),
                      [(q[0],) + tuple((p[0] - x0 + pad, p[1] - y0 + pad)
                                       for p in q[1:]) for q in c[1]])
                     for c in cs]
    W, Hh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    C, Cc = mv(out['cyan']), mv(out['cyan_clear'])
    K, B = mv(out['cream']), mv(out['black'])
    sets = {'om-colour': [(CYAN, C), (CREAM, K), (BLACK, B)],
            'om-black': [(BLACK, Cc), (BLACK, B)],
            'om-black-letters': [(BLACK, B)]}
    for nm, lay in sets.items():
        write_pdf(os.path.join(a.outdir, nm + '.pdf'), lay, W, Hh)
        write_svg(os.path.join(a.outdir, nm + '.svg'), lay, W, Hh)
        print('   %-20s %7.1f x %7.1f pt' % (nm + '.pdf/.svg', W, Hh))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
