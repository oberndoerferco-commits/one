#!/usr/bin/env python3
"""Vectorise the hand-drawn OM artwork and regularise it.

Three layers come out of the drawing: the black letterforms, a cream keyline
hugging them, and a cyan diagonal hatch standing off as a block shadow.  The
letterforms are traced from the drawing; the keyline and the hatch are rebuilt
from them geometrically, so they sit at a constant distance and a constant pitch
instead of following the wobble of a finger on glass.

The M is mirrored about its own axis before tracing, which is what makes it
symmetrical without redrawing it.
"""

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_lineart as vl
from regularise import regularise
import pathio


def layers(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    black = ndi.binary_closing(a.mean(2) < 100, np.ones((3, 3)))
    cyan = ndi.binary_opening((B > 140) & (G > 140) & (R < 190) & (G - R > 30),
                              np.ones((3, 3)))
    cream = ndi.binary_opening((R > 200) & (G > 150) & (G < 235) & (B < 190)
                               & (R - B > 45), np.ones((3, 3)))
    return black, cream, cyan


def split(mask, min_px=2000):
    lab, n = ndi.label(mask)
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    comps = []
    for i, s in enumerate(sizes):
        if s < min_px:
            continue
        m = lab == i + 1
        xs = np.nonzero(m.any(0))[0]
        comps.append((xs.min(), m))
    comps.sort(key=lambda t: t[0])
    return [m for _, m in comps]


def mirror_x(mask, span=14.0, step=0.1):
    """Make a component mirror-symmetric about its own best axis.

    The centroid is not the axis: using it leaves the halves a few pixels out of
    register, and averaging then ghosts every edge.  The axis is solved for
    first, by sliding it until the mismatch between the mask and its reflection
    is least, and only then are the two averaged.
    """
    ys, xs = np.nonzero(mask)
    f = mask.astype(np.float64)
    yy, xx = np.mgrid[0:mask.shape[0], 0:mask.shape[1]].astype(np.float64)
    c0 = float(xs.mean())
    best, bc = None, c0
    for d in np.arange(-span, span + 1e-9, step):
        c = c0 + d
        mir = ndi.map_coordinates(f, [yy, 2 * c - xx], order=1, mode='constant')
        err = float(np.abs(f - mir).sum())
        if best is None or err < best:
            best, bc = err, c
    mir = ndi.map_coordinates(f, [yy, 2 * bc - xx], order=3, mode='constant')
    print('      axis %.2f px (centroid %.2f, moved %.2f); residual %.4f mean'
          % (bc, c0, bc - c0, float(np.abs(f - mir).mean())))
    return 0.5 * (f + mir)


def trace(field, sigma=1.4, **fit):
    """Trace a 0..1 ink field (1 = ink) and rebuild it on structural nodes."""
    cs = vl.trace(1.0 - field, level=0.5, sigma=sigma, dot_area=0, min_area=200,
                  min_contour_area=120.0, **fit)
    return [regularise(c, corner_deg=30.0, corner_span=11, straight_tol=1.1,
                       merge=7.0) for c in cs]


# ------------------------------------------------------------ rebuilt layers


def flat(contour, n=28):
    """Dense polyline for one (start, segs) contour."""
    st, segs = contour
    cur = np.asarray(st, float)
    out = [tuple(cur)]
    for q in segs:
        if q[0] == 'L':
            cur = np.asarray(q[1], float)
            out.append(tuple(cur))
        else:
            b = [cur] + [np.asarray(v, float) for v in q[1:]]
            t = np.linspace(0, 1, n)[1:, None]
            pts = ((1 - t) ** 3 * b[0] + 3 * (1 - t) ** 2 * t * b[1]
                   + 3 * (1 - t) * t ** 2 * b[2] + t ** 3 * b[3])
            out += [tuple(p) for p in pts]
            cur = b[3]
    return out


def as_poly(contours):
    """Shapely geometry for a set of contours, largest first as outers."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    rings = sorted((Polygon(flat(c)).buffer(0) for c in contours),
                   key=lambda p: -p.area)
    g = rings[0]
    for r in rings[1:]:
        g = g.symmetric_difference(r) if g.contains(r) else g.union(r)
    return g.buffer(0)


def keyline_of(letters, width):
    """The cream line, as a band of constant width just outside the letters."""
    return letters.buffer(width, join_style=1, quad_segs=48).difference(letters)


def shadow_of(letters, dx, dy, keyline=None):
    """The block the hatch lives in: the letters pushed off, minus the letters."""
    from shapely import affinity
    s = affinity.translate(letters, dx, dy).difference(letters)
    return s.difference(keyline) if keyline is not None else s


def hatch(region, angle, pitch, width):
    """Parallel strokes of constant pitch, clipped to a region."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    x0, y0, x1, y1 = region.bounds
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    span = math.hypot(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    k = -span
    while k <= span:
        px, py = cx + nx * k, cy + ny * k
        seg = LineString([(px - ux * span, py - uy * span),
                          (px + ux * span, py + uy * span)])
        bar = seg.buffer(width / 2, cap_style=2, join_style=2)
        piece = bar.intersection(region)
        if not piece.is_empty:
            out.append(piece)
        k += pitch
    return unary_union(out).buffer(0)


def rings_of(geom):
    """Shapely geometry -> (start, segs) contours of straight segments."""
    out = []
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if g.is_empty or g.geom_type != 'Polygon':
            continue
        for ring in [g.exterior] + list(g.interiors):
            c = list(ring.coords)[:-1]
            if len(c) > 2:
                out.append((c[0], [('L', p) for p in c[1:]]))
    return out


# ------------------------------------------------------------------- output


def write_pdf(path, layers_, w, h):
    body = []
    for rgb, contours in layers_:
        if not contours:
            continue
        r, g, b = [v / 255.0 for v in rgb]
        body.append('%.4f %.4f %.4f rg' % (r, g, b))
        for c in contours:
            body += pathio.ops_of(c, lambda p: p)
        body.append('f*')
    content = ('\n'.join(body) + '\n').encode('latin-1')
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.3f %.3f] '
             '/Contents 4 0 R /Resources << >> >>' % (w, h)).encode(),
            b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n'
            + content + b'endstream']
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offs = []
    for i, bb in enumerate(objs, 1):
        offs.append(len(out))
        out += ('%d 0 obj\n' % i).encode() + bb + b'\nendobj\n'
    x = len(out)
    out += ('xref\n0 %d\n' % (len(objs) + 1)).encode() + b'0000000000 65535 f \n'
    for o in offs:
        out += ('%010d 00000 n \n' % o).encode()
    out += ('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'
            % (len(objs) + 1, x)).encode()
    open(path, 'wb').write(bytes(out))


def write_svg(path, layers_, w, h):
    parts = []
    for rgb, contours in layers_:
        if not contours:
            continue
        d = ' '.join(pathio.svg_of(c, lambda p: (p[0], h - p[1])) for c in contours)
        parts.append('<path fill="#%02x%02x%02x" fill-rule="evenodd" stroke="none"'
                     ' d="%s"/>' % (rgb[0], rgb[1], rgb[2], d))
    open(path, 'w').write(
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        'width="%.3fpt" height="%.3fpt" viewBox="0 0 %.3f %.3f">\n%s\n</svg>\n'
        % (w, h, w, h, '\n'.join(parts)))


CYAN, CREAM, BLACK = (0x6c, 0xd7, 0xe1), (0xf4, 0xc8, 0x8b), (0, 0, 0)


def main(argv=None):
    from shapely.ops import unary_union
    from shapely import affinity
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--size', type=float, default=480.0, help='cap height, pt')
    ap.add_argument('--keyline', type=float, default=0.0115)
    ap.add_argument('--shadow-x', type=float, default=-0.1148)
    ap.add_argument('--shadow-y', type=float, default=-0.0961)
    ap.add_argument('--pitch', type=float, default=0.0301)
    ap.add_argument('--stroke', type=float, default=0.0215)
    ap.add_argument('--angle', type=float, default=45.0)
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)

    black, cream, cyan = layers(a.image)
    parts = split(black)
    assert len(parts) == 2, 'expected two letters, found %d' % len(parts)
    cap_px = float(np.ptp(np.nonzero(parts[0])[0]))
    k = a.size / cap_px
    glyphs = []
    for nm, m in (('O', parts[0]), ('M', parts[1])):
        f = m.astype(float)
        if nm == 'M':
            print('   M: symmetrising')
            f = mirror_x(m)
        cs = trace(f, line_tol=0.9, curve_tol=0.55, smooth_deg=34.0,
                   min_smooth_run=3)
        print('   %s: %d contour(s), %d lines + %d curves'
              % (nm, len(cs), sum(1 for c in cs for q in c[1] if q[0] == 'L'),
                 sum(1 for c in cs for q in c[1] if q[0] == 'C')))
        glyphs += cs
    H = black.shape[0]
    flip = [((c[0][0] * k, (H - c[0][1]) * k),
             [(q[0],) + tuple((p[0] * k, (H - p[1]) * k) for p in q[1:])
              for q in c[1]]) for c in glyphs]
    letters = as_poly(flip)
    x0, y0, x1, y1 = letters.bounds
    letters = affinity.translate(letters, -x0, -y0)
    flip = [((c[0][0] - x0, c[0][1] - y0),
             [(q[0],) + tuple((p[0] - x0, p[1] - y0) for p in q[1:])
              for q in c[1]]) for c in flip]
    S = a.size
    key = keyline_of(letters, a.keyline * S)
    shade = shadow_of(letters, a.shadow_x * S, a.shadow_y * S, key)
    hat = hatch(shade, a.angle, a.pitch * S, a.stroke * S)
    print('   keyline %.2f pt, shadow (%.1f, %.1f) pt, hatch %.2f pt at %.0f pt pitch'
          % (a.keyline * S, a.shadow_x * S, a.shadow_y * S,
             a.stroke * S, a.pitch * S))

    allg = unary_union([letters, key, hat])
    bx0, by0, bx1, by1 = allg.bounds
    pad = 0.05 * S
    sh = lambda g: affinity.translate(g, pad - bx0, pad - by0)
    W, Hh = (bx1 - bx0) + 2 * pad, (by1 - by0) + 2 * pad
    L = [((c[0][0] + pad - bx0, c[0][1] + pad - by0),
          [(q[0],) + tuple((p[0] + pad - bx0, p[1] + pad - by0) for p in q[1:])
           for q in c[1]]) for c in flip]
    Kr, Hr = rings_of(sh(key)), rings_of(sh(hat))
    sets = {
        'om-colour': [(CYAN, Hr), (CREAM, Kr), (BLACK, L)],
        'om-black': [(BLACK, L)],
        'om-black-shadow': [(BLACK, Hr), (BLACK, L)],
    }
    for nm, lay in sets.items():
        write_pdf(os.path.join(a.outdir, nm + '.pdf'), lay, W, Hh)
        write_svg(os.path.join(a.outdir, nm + '.svg'), lay, W, Hh)
        print('   %-20s %7.1f x %7.1f pt' % (nm + '.pdf/.svg', W, Hh))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
