#!/usr/bin/env python3
"""Turn a stroked outline drawing in a PDF into one filled shape, exactly.

The source cross is already vector: 28 stroked subpaths, no fill, drawn with a
2.04 pt pen.  Nothing here is re-traced or re-fitted - the lines and cubics are
read straight out of the content stream, de-duplicated, and chained into a
single closed contour, so the geometry that comes out is the geometry that went
in.  The only change is the paint: stroke becomes fill.

Two things in the source need handling and neither moves the drawing:

  * Four of the 28 subpaths are exact duplicates of others.
  * Consecutive subpaths do not quite share endpoints - they are out by up to
    0.11 pt (0.039 mm), invisible under a 2.04 pt pen but enough to stop the
    contour closing.  Each join is snapped to the midpoint of its two
    endpoints, so no point moves by more than half the gap.

The filled shape takes the pen's centreline as its boundary, which is where the
drawing says the edge of the cross is.
"""

import argparse
import math
import os
import re

import numpy as np
import pymupdf


# --------------------------------------------------------------- the content


def read_subpaths(path, page=0):
    """Every stroked subpath, in page coordinates, with the CTM applied."""
    cs = pymupdf.open(path)[page].read_contents().decode('latin-1')
    toks = re.findall(r'[-+]?\d*\.?\d+|[A-Za-z\'"*]+', cs)
    ctm = np.eye(3)
    stack, cur, out, args, width = [], [], [], [], None
    xf = lambda m, p: tuple((np.array([p[0], p[1], 1.0]) @ m)[:2])
    for t in toks:
        try:
            args.append(float(t))
            continue
        except ValueError:
            pass
        if t == 'cm':
            a, b, c, d, e, f = args[-6:]
            ctm = np.array([[a, b, 0], [c, d, 0], [e, f, 1]]) @ ctm
        elif t == 'q':
            stack.append(ctm.copy())
        elif t == 'Q':
            ctm = stack.pop()
        elif t == 'w':
            width = args[-1]
        elif t == 'm':
            cur = [('m', xf(ctm, args[-2:]))]
        elif t == 'l':
            cur.append(('l', xf(ctm, args[-2:])))
        elif t == 'c':
            p = args[-6:]
            cur.append(('c', xf(ctm, p[0:2]), xf(ctm, p[2:4]), xf(ctm, p[4:6])))
        elif t in ('S', 's', 'f', 'F', 'f*', 'B', 'b', 'n'):
            if len(cur) > 1 and t in ('S', 's'):
                out.append(cur)
            cur = []
        args = []
    return out, (width * abs(ctm[0, 0]) if width is not None else None)


def dedupe(segs, prec=4):
    seen, out = set(), []
    for sg in segs:
        k = tuple(round(v, prec) for s in sg for pt in s[1:] for v in pt)
        if k not in seen:
            seen.add(k)
            out.append(sg)
    return out


# ------------------------------------------------------------------ chaining


def _start(sg):
    return np.array(sg[0][1], float)


def _end(sg):
    return np.array(sg[-1][-1], float)


def _reverse(sg):
    s, e = _start(sg), _end(sg)
    if sg[-1][0] == 'l':
        return [('m', tuple(e)), ('l', tuple(s))]
    return [('m', tuple(e)), ('c', sg[-1][2], sg[-1][1], tuple(s))]


def chain(segs):
    """Order the subpaths into one closed run, nearest endpoint first."""
    rest = segs[:]
    run = [rest.pop(0)]
    gaps = []
    while rest:
        tail = _end(run[-1])
        best = min(((float(np.linalg.norm((_end(s) if r else _start(s)) - tail)), i, r)
                    for i, s in enumerate(rest) for r in (False, True)))
        d, i, rev = best
        sg = rest.pop(i)
        gaps.append(d)
        run.append(_reverse(sg) if rev else sg)
    return run, gaps, float(np.linalg.norm(_end(run[-1]) - _start(run[0])))


def snap(run):
    """Move each join to the midpoint of the two endpoints that meet there."""
    moved = 0.0
    for i in range(len(run)):
        a, b = run[i], run[(i + 1) % len(run)]
        mid = (_end(a) + _start(b)) / 2.0
        moved = max(moved, float(np.linalg.norm(_end(a) - mid)))
        a[-1] = a[-1][:-1] + (tuple(mid),)
        b[0] = ('m', tuple(mid))
    return run, moved


def as_path(run):
    """One closed path: a single moveto then the chained lines and curves."""
    out = [('m', tuple(_start(run[0])))]
    for sg in run:
        out += sg[1:]
    return out


# ------------------------------------------------------------------- writers


def _f(v, prec=4):
    s = f'{v:.{prec}f}'.rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def ops_of(path, to_xy):
    out = []
    for s in path:
        if s[0] == 'm':
            x, y = to_xy(s[1]); out.append(f'{_f(x)} {_f(y)} m')
        elif s[0] == 'l':
            x, y = to_xy(s[1]); out.append(f'{_f(x)} {_f(y)} l')
        else:
            a, b, c = to_xy(s[1]), to_xy(s[2]), to_xy(s[3])
            out.append(f'{_f(a[0])} {_f(a[1])} {_f(b[0])} {_f(b[1])} '
                       f'{_f(c[0])} {_f(c[1])} c')
    return out


def svg_of(path, to_xy):
    out = []
    for s in path:
        if s[0] == 'm':
            x, y = to_xy(s[1]); out.append(f'M{_f(x)} {_f(y)}')
        elif s[0] == 'l':
            x, y = to_xy(s[1]); out.append(f'L{_f(x)} {_f(y)}')
        else:
            a, b, c = to_xy(s[1]), to_xy(s[2]), to_xy(s[3])
            out.append(f'C{_f(a[0])} {_f(a[1])} {_f(b[0])} {_f(b[1])} '
                       f'{_f(c[0])} {_f(c[1])}')
    return ' '.join(out) + ' Z'


def write_pdf(dest, ops, w, h, paint='f'):
    content = ('0 g\n' + '\n'.join(ops) + f'\nh\n{paint}\n').encode('latin-1')
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.4f} {h:.4f}] '
             f'/Contents 4 0 R /Resources << >> >>').encode(),
            b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n'
            + content + b'endstream']
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offs = []
    for i, body in enumerate(objs, 1):
        offs.append(len(out))
        out += f'{i} 0 obj\n'.encode() + body + b'\nendobj\n'
    x = len(out)
    out += f'xref\n0 {len(objs)+1}\n'.encode() + b'0000000000 65535 f \n'
    for o in offs:
        out += f'{o:010d} 00000 n \n'.encode()
    out += (f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\n'
            f'startxref\n{x}\n%%EOF\n').encode()
    open(dest, 'wb').write(bytes(out))


def write_svg(dest, d, w, h, mm):
    open(dest, 'w').write(
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
        f' width="{mm[0]:.4f}mm" height="{mm[1]:.4f}mm"\n'
        f' viewBox="0 0 {w:.4f} {h:.4f}">\n'
        f'<path fill="#000000" fill-rule="nonzero" stroke="none"\n d="{d}"/>\n</svg>\n')


# ---------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('src')
    ap.add_argument('outdir')
    ap.add_argument('--name', default='cross')
    ap.add_argument('--margin', type=float, default=0.0, help='pt around the art')
    ap.add_argument('--size-mm', type=float, action='append', default=None,
                    help='also write a copy scaled to this width in mm')
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)

    segs, pen = read_subpaths(a.src)
    uniq = dedupe(segs)
    run, gaps, close = chain(uniq)
    run, moved = snap(run)
    path = as_path(run)
    print('   %d stroked subpaths, %d unique, pen %.4f pt' % (len(segs), len(uniq), pen))
    print('   chained into 1 closed contour; largest join gap %.4f pt (%.4f mm),'
          ' closing gap %.4f pt' % (max(gaps), max(gaps) / 72 * 25.4, close))
    print('   snapped to midpoints: no point moved more than %.4f pt (%.4f mm)'
          % (moved, moved / 72 * 25.4))

    pts = np.array([p for s in path for p in s[1:]])
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    x1, y1 = pts[:, 0].max(), pts[:, 1].max()
    w, h = (x1 - x0) + 2 * a.margin, (y1 - y0) + 2 * a.margin
    print('   artwork %.4f x %.4f pt  =  %.3f x %.3f mm'
          % (w, h, w / 72 * 25.4, h / 72 * 25.4))

    made = []
    targets = [(a.name, 1.0)] + [('%s-%gmm' % (a.name, s), s / (w / 72 * 25.4))
                                 for s in (a.size_mm or [])]
    for nm, k in targets:
        to = lambda p: ((p[0] - x0) * k + a.margin, (p[1] - y0) * k + a.margin)
        W, H = w * k, h * k
        write_pdf(os.path.join(a.outdir, nm + '.pdf'), ops_of(path, to), W, H)
        write_svg(os.path.join(a.outdir, nm + '.svg'),
                  svg_of(path, lambda p: (to(p)[0], H - to(p)[1])), W, H,
                  (W / 72 * 25.4, H / 72 * 25.4))
        made.append((nm, W, H))
    for nm, W, H in made:
        print('   %-18s %8.3f x %8.3f pt   %7.3f x %7.3f mm'
              % (nm + '.pdf/.svg', W, H, W / 72 * 25.4, H / 72 * 25.4))
    return path, pen, (x0, y0, x1, y1)


if __name__ == '__main__':
    main()
