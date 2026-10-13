#!/usr/bin/env python3
"""Shared helpers for the hand-drawn OM artwork: layer separation and writers.

The build itself lives in om_artwork.py.  An earlier version of this file also
*rebuilt* the keyline and the hatch from measurements; that was wrong and has
been removed, so it cannot be run by accident.
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


CYAN, CREAM, BLACK = (0x6c, 0xd7, 0xe1), (0xf4, 0xc8, 0x8b), (0, 0, 0)


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
