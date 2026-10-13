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


def trace_layer(field, sigma, **fit):
    return vl.trace(1.0 - field, level=0.5, sigma=sigma, dot_area=0,
                    min_area=60, min_contour_area=40.0, **fit)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--size', type=float, default=480.0)
    ap.add_argument('--sigma', type=float, default=1.2)
    ap.add_argument('--line-tol', type=float, default=1.1)
    ap.add_argument('--curve-tol', type=float, default=0.7)
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    fit = dict(line_tol=a.line_tol, curve_tol=a.curve_tol,
               smooth_deg=34.0, min_smooth_run=3)

    black, cream, cyan = layers(a.image)

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
    for nm, f, sg in (('cyan', cyan.astype(float), a.sigma),
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
    C, K, B = mv(out['cyan']), mv(out['cream']), mv(out['black'])
    # the one-colour version keeps the halo; the keyline's area simply stays
    # white, which works because no hatch stroke touches a letter in the drawing
    sets = {'om-colour': [(CYAN, C), (CREAM, K), (BLACK, B)],
            'om-black': [(BLACK, C), (BLACK, B)],
            'om-black-letters': [(BLACK, B)]}
    for nm, lay in sets.items():
        write_pdf(os.path.join(a.outdir, nm + '.pdf'), lay, W, Hh)
        write_svg(os.path.join(a.outdir, nm + '.svg'), lay, W, Hh)
        print('   %-20s %7.1f x %7.1f pt' % (nm + '.pdf/.svg', W, Hh))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
