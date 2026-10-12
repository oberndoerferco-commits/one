#!/usr/bin/env python3
"""Compose the ring mark: a cross, O, M, a cross, as one flat vector.

Everything is flat black and a single filled path set - no strokes, no
gradients, nothing that a laser or a stamp cannot reproduce.  Sizes are given as
the cap height of the letters in millimetres, because that is the dimension that
has to fit the band of the ring.
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metal_letters_font as mf
import outline_to_fill as of
import vectorize_lineart as vl


def cross_contour(pdf):
    """The cross as one closed contour, normalised to a unit box at the origin."""
    segs, _ = of.read_subpaths(pdf)
    run, _, _ = of.chain(of.dedupe(segs))
    run, _ = of.snap(run)
    path = of.as_path(run)
    pts = np.array([p for s in path for p in s[1:]])
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    h = pts[:, 1].max() - y0
    w = pts[:, 0].max() - x0
    norm = lambda p: ((p[0] - x0) / h, (p[1] - y0) / h)
    out = [(s[0],) + tuple(norm(q) for q in s[1:]) for s in path]
    return out, w / h


def place(contour, k, dx, dy):
    fn = lambda p: (p[0] * k + dx, p[1] * k + dy)
    if isinstance(contour, tuple):
        start, segs = contour
        return fn(start), [(s[0], fn(s[1])) if s[0] == 'L'
                           else ('C', fn(s[1]), fn(s[2]), fn(s[3])) for s in segs]
    return [(s[0],) + tuple(fn(q) for q in s[1:]) for s in contour]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('cross')
    ap.add_argument('outdir')
    ap.add_argument('--cap-mm', type=float, action='append', default=None,
                    help='cap height of the letters, in mm (repeatable)')
    ap.add_argument('--cross-ratio', type=float, default=0.62,
                    help='cross height as a fraction of the cap height')
    ap.add_argument('--gap', type=float, default=0.34,
                    help='space between cross and letter, as a fraction of cap')
    ap.add_argument('--trim', type=float, default=9.0)
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)

    b = mf.build(a.image, trim=a.trim, sigma=0.8, line_tol=0.6, curve_tol=0.40,
                 smooth_deg=34.0, min_smooth_run=3)
    CAP = mf.CAP
    xpath, aspect = cross_contour(a.cross)
    ch = a.cross_ratio * CAP
    cw = ch * aspect
    gap = a.gap * CAP

    # lay out: cross, gap, O, M (on their own sidebearings), gap, cross
    items, x = [], 0.0
    items.append(('cross', x))
    x += cw + gap - b['side']
    for q in ('O', 'M'):
        items.append((q, x))
        x += b['widths'][q]
    x += gap - b['side']
    items.append(('cross', x))
    total = x + cw

    shapes = []
    cy = (CAP - ch) / 2.0
    for kind, dx in items:
        if kind == 'cross':
            shapes.append(('path', place(xpath, ch, dx, cy)))
        else:
            for c in b['glyphs'][kind]:
                shapes.append(('bez', place(c, 1.0, dx, 0.0)))

    pts = []
    for kind, g in shapes:
        pts += [p for s in g for p in s[1:]] if kind == 'path' else \
               [g[0]] + [s[1] if s[0] == 'L' else s[3] for s in g[1]]
    pts = np.array(pts)
    x0, y0, x1, y1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
    print('   lockup %.1f x %.1f units  (cap %d)' % (x1 - x0, y1 - y0, CAP))

    for cap_mm in (a.cap_mm or [4.0]):
        k = cap_mm / CAP * 72 / 25.4            # units -> pt
        W, H = (x1 - x0) * k, (y1 - y0) * k
        ops, svg = [], []
        for kind, g in shapes:
            to = lambda p: ((p[0] - x0) * k, (p[1] - y0) * k)
            if kind == 'path':
                ops += of.ops_of(g, to) + ['h']
                svg.append(of.svg_of(g, lambda p: (to(p)[0], H - to(p)[1])))
            else:
                o, _, _ = vl.emit([g], to)
                ops.append(o[0].replace('M', '', 1))
                p = vl.emit([g], lambda q: (to(q)[0], H - to(q)[1]))[1][0]
                ops[-1] = p
                svg.append(vl.emit([g], lambda q: (to(q)[0], H - to(q)[1]))[0][0])
        name = 'om-lockup-%gmm' % cap_mm
        of.write_pdf(os.path.join(a.outdir, name + '.pdf'),
                     [o for kind, g in shapes for o in
                      (of.ops_of(g, lambda p: ((p[0]-x0)*k, (p[1]-y0)*k)) + ['h'] if kind == 'path'
                       else vl.emit([g], lambda p: ((p[0]-x0)*k, (p[1]-y0)*k))[1])],
                     W, H, paint='f')
        of.write_svg(os.path.join(a.outdir, name + '.svg'), ' '.join(svg), W, H,
                     (W / 72 * 25.4, H / 72 * 25.4))
        print('   %-22s %7.3f x %7.3f mm   (cap %.1f mm)'
              % (name + '.pdf/.svg', W / 72 * 25.4, H / 72 * 25.4, cap_mm))


if __name__ == '__main__':
    main()
