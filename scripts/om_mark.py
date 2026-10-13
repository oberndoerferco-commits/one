#!/usr/bin/env python3
"""Build the OM mark: a font, vector artwork, and the ring lockup.

The letterforms come from scripts/monogram.py, which constructs them from
straight lines, circular arcs and splines with chosen tangents.  Nothing is
traced or fitted, so the outlines cannot carry a dent.
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monogram as mg
import metal_letters_font as mf
import outline_to_fill as of
from pathio import ops_of, svg_of

UPM, CAP = 1000, 700


def letters(cap_units=CAP):
    """O and M in font units: baseline y=0, cap height cap_units."""
    k = cap_units / mg.CAP
    out = {}
    for name, cs in (('O', mg.glyph_O2()), ('M', mg.glyph_M_west())):
        x0, y0, x1, y1 = mg.bbox(cs)
        out[name] = [mg.tr(c, k, -x0 * k, -y0 * k) for c in cs]
    return out


def lockup(cross_pdf, cap=mg.CAP, ratio=0.58, gap=0.30):
    """Cross, O, M, cross - all on one baseline band."""
    segs, _ = of.read_subpaths(cross_pdf)
    run, _, _ = of.chain(of.dedupe(segs))
    run, _ = of.snap(run)
    path = of.as_path(run)
    pts = [p for s in path for p in s[1:]]
    x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
    h = max(p[1] for p in pts) - y0
    w = max(p[0] for p in pts) - x0
    xp = (((path[0][1][0] - x0) / h, (path[0][1][1] - y0) / h),
          [(q[0].upper(),) + tuple(((v[0] - x0) / h, (v[1] - y0) / h) for v in q[1:])
           for q in path[1:]])
    gl = letters(cap)
    ch, cw = ratio * cap, ratio * cap * (w / h)
    G = gap * cap
    items, x = [], 0.0
    items.append(('x', x)); x += cw + G
    for q in ('O', 'M'):
        items.append((q, x))
        x += mg.bbox(gl[q])[2] - mg.bbox(gl[q])[0] + G
    items.append(('x', x - G + G * 0.0)); total = items[-1][1] + cw
    shapes = []
    for kind, dx in items:
        if kind == 'x':
            shapes.append(mg.tr(xp, ch, dx, (cap - ch) / 2))
        else:
            shapes += [mg.tr(c, 1.0, dx, 0.0) for c in gl[kind]]
    return shapes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('outdir')
    ap.add_argument('--cross', default='assets/cross-cliche/source-Cliche_15cm.pdf')
    ap.add_argument('--family', default='Oberndorfer OM')
    ap.add_argument('--size', type=float, default=480.0)
    ap.add_argument('--cap-mm', type=float, action='append', default=None)
    ap.add_argument('--lsb-o', type=float, default=0.055)
    ap.add_argument('--lsb-m', type=float, default=0.075)
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)

    gl = letters(CAP)
    glyphs, widths = {}, {'.notdef': 400, 'space': int(UPM * 0.30)}
    for name, side in (('O', a.lsb_o), ('M', a.lsb_m)):
        sb = int(round(side * CAP))
        cs = [mg.tr(c, 1.0, sb, 0.0) for c in gl[name]]
        glyphs[name] = mf.orient_for_cff(cs)
        x0, _, x1, _ = mg.bbox(cs)
        widths[name] = int(round(x1 - x0)) + 2 * sb
    font = mf.build_otf(glyphs, widths,
                        os.path.join(a.outdir, a.family.replace(' ', '') + '-Regular.otf'),
                        a.family)
    for f in (font, font[:-4] + '.woff2'):
        if os.path.exists(f):
            print('   %-34s %6d bytes' % (os.path.basename(f), os.path.getsize(f)))
    print('   advance widths: O %d, M %d (UPM %d, cap %d)'
          % (widths['O'], widths['M'], UPM, CAP))

    k = a.size / CAP
    for nm, items in (('o', ['O']), ('m', ['M']), ('om', ['O', 'M'])):
        placed, pen = [], 0.0
        for q in items:
            sb = int(round((a.lsb_o if q == 'O' else a.lsb_m) * CAP))
            placed += [mg.tr(c, k, (pen + sb) * k, 0.0) for c in gl[q]]
            pen += widths[q]
        x0, y0, x1, y1 = mg.bbox(placed)
        pad = 0.08 * a.size
        w, h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
        base = os.path.join(a.outdir, 'om-%s' % nm)
        to = lambda p: (p[0] - x0 + pad, p[1] - y0 + pad)
        of.write_pdf(base + '.pdf', [o for c in placed for o in ops_of(c, to)], w, h)
        of.write_svg(base + '.svg',
                     ' '.join(svg_of(c, lambda p: (to(p)[0], h - to(p)[1])) for c in placed),
                     w, h, (w / 72 * 25.4, h / 72 * 25.4))
        print('   %-14s %7.1f x %7.1f pt' % (os.path.basename(base) + '.pdf/.svg', w, h))

    shapes = lockup(a.cross)
    x0, y0, x1, y1 = mg.bbox(shapes)
    for cap_mm in (a.cap_mm or [4.0]):
        kk = cap_mm / mg.CAP * 72 / 25.4
        w, h = (x1 - x0) * kk, (y1 - y0) * kk
        to = lambda p: ((p[0] - x0) * kk, (p[1] - y0) * kk)
        base = os.path.join(a.outdir, 'om-lockup-%gmm' % cap_mm)
        of.write_pdf(base + '.pdf', [o for c in shapes for o in ops_of(c, to)], w, h)
        of.write_svg(base + '.svg',
                     ' '.join(svg_of(c, lambda p: (to(p)[0], h - to(p)[1])) for c in shapes),
                     w, h, (w / 72 * 25.4, h / 72 * 25.4))
        print('   %-22s %7.3f x %7.3f mm' % (os.path.basename(base) + '.pdf/.svg',
                                             w / 72 * 25.4, h / 72 * 25.4))


if __name__ == '__main__':
    main()
