#!/usr/bin/env python3
"""Rebuild a traced contour the way a letter is drawn, not the way it scanned.

A trace follows whatever the source did, so a casting's small dents and a
scanner's wobble end up as real curvature in the outline.  Smoothing does not
fix that: a dent is a low-frequency deviation, so a tolerant curve fit simply
follows it more gently.

This rebuilds the contour instead.  Nodes go only where a letterform actually
has them - at corners, and at the extremes in x and y - and each span between
two nodes becomes a *single* cubic, which cannot dent in the middle because it
has no interior control of its own.  Tangents are constrained upright at the
extremes, which is both the type-design convention and what keeps stems looking
straight.  Spans that are nearly straight are emitted as straight lines.
"""

import math

import numpy as np

import vectorize_lineart as vl

EPS = 1e-12


def _resample(pts, step=0.5):
    closed = np.vstack([pts, pts[:1]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    d = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(16, int(round(d[-1] / step)))
    want = np.linspace(0.0, d[-1], n, endpoint=False)
    return np.column_stack([np.interp(want, d, closed[:, 0]),
                            np.interp(want, d, closed[:, 1])])


def _dirs(pts, span):
    """Unit direction at each sample, measured over +/-span samples."""
    n = len(pts)
    fwd = np.roll(pts, -span, axis=0) - pts
    bwd = pts - np.roll(pts, span, axis=0)
    unit = lambda v: v / (np.linalg.norm(v, axis=1, keepdims=True) + EPS)
    return unit(fwd), unit(bwd)


def _corners(pts, span, deg):
    fwd, bwd = _dirs(pts, span)
    cosang = np.clip((fwd * bwd).sum(1), -1.0, 1.0)
    turn = np.degrees(np.arccos(cosang))
    n = len(pts)
    out = []
    for i in range(n):
        if turn[i] < deg:
            continue
        lo = [turn[(i + k) % n] for k in range(-span, span + 1)]
        if turn[i] >= max(lo) - 1e-9:
            out.append(i)
    # collapse runs
    keep = []
    for i in out:
        if not keep or min((i - keep[-1]) % n, (keep[-1] - i) % n) > span:
            keep.append(i)
    return keep


def _extrema(pts, span, min_run):
    """Samples where the contour turns around in x or in y."""
    fwd, _ = _dirs(pts, max(2, span // 2))
    n = len(pts)
    out = []
    for axis in (0, 1):
        s = np.sign(fwd[:, axis])
        s[s == 0] = 1
        for i in range(n):
            j = (i + 1) % n
            if s[i] == s[j]:
                continue
            # only a real turnaround if the sign holds either side for a while
            a = all(s[(i - k) % n] == s[i] for k in range(1, min_run))
            b = all(s[(j + k) % n] == s[j] for k in range(1, min_run))
            if not (a and b):
                continue
            # snap to the true extreme nearby
            w = [(i + k) % n for k in range(-span, span + 1)]
            vals = pts[w, axis]
            k = int(np.argmax(vals) if s[i] > 0 else np.argmin(vals))
            out.append((w[k], axis))
    return out


def _tangent_at(pts, i, axis, outgoing, span):
    """Upright tangent at an extreme: vertical at an x-extreme, horizontal at a y-extreme."""
    fwd, bwd = _dirs(pts, span)
    d = fwd[i] if outgoing else bwd[i]
    t = np.array([0.0, 1.0]) if axis == 0 else np.array([1.0, 0.0])
    return t if float(d @ t) >= 0 else -t


def _fit_one(d, t1, t2, iters=4):
    """One cubic through a span, with both end tangents fixed."""
    if len(d) < 4:
        return None
    u = vl._chord_param(d)
    bez = vl._generate_bezier(d, u, t1, t2)
    for _ in range(iters):
        u = vl._reparameterize(d, bez, u)
        bez = vl._generate_bezier(d, u, t1, t2)
    return bez


def regularise(contour, step=0.5, corner_deg=36.0, corner_span=9,
               extreme_span=7, min_run=7, straight_tol=0.9, merge=6.0):
    """(start, segs) -> (start, segs), rebuilt on corner and extreme nodes."""
    pts = _resample(np.asarray(_poly(contour), float), step)
    n = len(pts)
    nodes = {}
    for i in _corners(pts, corner_span, corner_deg):
        nodes[i] = ('corner', None)
    for i, axis in _extrema(pts, extreme_span, min_run):
        if all(min((i - j) % n, (j - i) % n) > corner_span for j in nodes):
            nodes[i] = ('extreme', axis)
    if len(nodes) < 2:
        return contour
    idx = sorted(nodes)
    # drop nodes that sit on top of each other
    keep = [idx[0]]
    for i in idx[1:]:
        if (i - keep[-1]) * step >= merge:
            keep.append(i)
    if (keep[0] + n - keep[-1]) * step < merge and len(keep) > 2:
        keep.pop()
    idx = keep

    fwd, bwd = _dirs(pts, corner_span)
    segs = []
    for k, i in enumerate(idx):
        j = idx[(k + 1) % len(idx)]
        run = pts[i:j + 1] if j > i else np.vstack([pts[i:], pts[:j + 1]])
        if len(run) < 3:
            segs.append(('L', tuple(pts[j])))
            continue
        kind_i, ax_i = nodes[i]
        kind_j, ax_j = nodes[j]
        t1 = (_tangent_at(pts, i, ax_i, True, extreme_span) if kind_i == 'extreme'
              else vl._unit(fwd[i]))
        t2 = (_tangent_at(pts, j, ax_j, False, extreme_span) if kind_j == 'extreme'
              else vl._unit(bwd[j]))
        t2 = -t2
        chord = run[-1] - run[0]
        L = np.linalg.norm(chord)
        if L > EPS:
            u = chord / L
            dev = np.abs(np.cross(np.broadcast_to(u, run.shape), run - run[0])).max()
            if dev <= straight_tol:
                segs.append(('L', tuple(run[-1])))
                continue
        bez = _fit_one(run, t1, t2)
        if bez is None:
            segs.append(('L', tuple(run[-1])))
        else:
            segs.append(('C', tuple(bez[1]), tuple(bez[2]), tuple(run[-1])))
    return tuple(pts[idx[0]]), segs


def _poly(contour, n=26):
    start, segs = contour
    cur = np.asarray(start, float)
    out = [cur]
    for s in segs:
        if s[0] == 'L':
            cur = np.asarray(s[1], float)
            out.append(cur)
        else:
            b = [cur] + [np.asarray(q, float) for q in s[1:]]
            t = np.linspace(0, 1, n)[1:, None]
            out += list((1 - t) ** 3 * b[0] + 3 * (1 - t) ** 2 * t * b[1]
                        + 3 * (1 - t) * t ** 2 * b[2] + t ** 3 * b[3])
            cur = b[3]
    return np.array(out)
