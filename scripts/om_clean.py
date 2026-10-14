#!/usr/bin/env python3
"""Draw the hand-drawn OM properly, instead of photocopying the sketch.

The iPad drawing is the design, not the master.  Tracing it faithfully is what
guarantees the faults: a pen edge wobbles, a hatch stroke stops wherever the
hand lifted, and the keyline strays over an outline and takes a bite out of it.
Reproducing all of that accurately still produces a rough sketch.

So nothing here is traced for its own sake.  The drawing is measured, and the
measurements are drawn clean:

letters  the outline is rebuilt on structural nodes only - corners and the
         extremes in x and y - with one cubic per span, so a span cannot dent in
         the middle because it has no interior control of its own.  The M is
         mirrored about its own axis.

halo     the drawing's 136 hatch strokes sit at a median 135.0 deg (sd 2.6) and
         are 17.2 px wide (varying only 1.1x), so the angle and the width are
         plainly meant to be constant and are made constant.  Length is NOT:
         it varies 1.4x across the deciles because the halo is wider in some
         places than others, so each stroke keeps its own, smoothed along the
         run.  Every stroke is redrawn as a true stadium - a rectangle with
         semicircular ends - evenly spaced along the letter it follows.
"""

import argparse
import math
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_lineart as vl
from regularise import regularise
from om_artwork import mirror_pair, repair, _disk, trace_layer
from om_hand import layers, write_pdf, write_svg, CYAN, CREAM, BLACK


# ---------------------------------------------------------------- the letters

def clean_letters(mask, sigma, fit, **reg):
    """Trace, then rebuild each outline on corner and extreme nodes."""
    out = []
    for c in trace_layer(mask.astype(float), sigma, **fit):
        out.append(regularise(c, **reg))
    return out


def _axis_of(mask, right):
    """The M's own mirror axis, as the centroid of the symmetrised half."""
    xs = np.nonzero(mask & right)[1]
    return float(xs.mean())


def symmetrise_contour(contour, axis, tol=None):
    """Replace a contour's right half with a mirror of its left.

    Rebuilding an outline on structural nodes does not place those nodes
    symmetrically even when the shape is, so an M that is symmetrical as a mask
    stops being symmetrical as curves.  The cure is to draw one half and reflect
    it, which is how the letter would be drawn by hand anyway.

    The two nodes nearest the axis are the M's top notch and its centre vertex.
    Both belong on the axis, so they are snapped to it and used as the seam.
    """
    start, segs = contour
    N = len(segs)
    node = [np.asarray(start, float)]
    for i in range(N - 1):
        node.append(np.asarray(segs[i][-1], float))
    if len(node) != N:
        return contour
    dx = np.array([abs(p[0] - axis) for p in node])
    order = np.argsort(dx)
    a = int(order[0])
    b = next((int(i) for i in order[1:]
              if min((i - a) % N, (a - i) % N) > N // 5), None)
    if b is None:
        return contour
    if tol is not None and max(dx[a], dx[b]) > tol:
        return contour
    a, b = min(a, b), max(a, b)
    runs = {'ab': list(range(a, b)), 'ba': list(range(b, N)) + list(range(0, a))}
    mean = {k: np.mean([node[i][0] for i in v]) for k, v in runs.items()}
    keep = runs['ab'] if mean['ab'] < mean['ba'] else runs['ba']
    first = a if keep is runs['ab'] else b
    last = b if keep is runs['ab'] else a
    mir = lambda p: (2 * axis - p[0], p[1])
    on = lambda p: (axis, p[1])

    out, cur = [], on(node[first])
    seam = cur
    for k, i in enumerate(keep):
        q = segs[i]
        end = on(node[last]) if k == len(keep) - 1 else tuple(node[(i + 1) % N])
        out.append((q[0],) + tuple(q[1:-1]) + (end,))
    far = out[-1][-1]
    back = []
    for q in reversed(out):
        if q[0] == 'C':
            back.append(('C', mir(q[2]), mir(q[1]), None))
        else:
            back.append(('L', None))
    ends = [mir(out[i - 1][-1]) if i else seam for i in range(len(out))][::-1]
    back = [(q[0],) + tuple(q[1:-1]) + (ends[i],) for i, q in enumerate(back)]
    return seam, out + back


# ------------------------------------------------------------------- the halo

def measure_strokes(cyan, min_area=150):
    """Centre, angle, length and width of every hatch stroke."""
    lab, n = ndi.label(cyan)
    rows = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < min_area:
            continue
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean(), ys.mean()
        cov = np.cov(np.vstack([xs - cx, ys - cy]))
        w, v = np.linalg.eigh(cov)
        ax = v[:, -1]
        # true extent along each axis, rather than the Gaussian equivalent
        t = (xs - cx) * ax[0] + (ys - cy) * ax[1]
        s = -(xs - cx) * ax[1] + (ys - cy) * ax[0]
        rows.append((cx, cy, math.atan2(ax[1], ax[0]),
                     t.max() - t.min(), s.max() - s.min()))
    return np.array(rows)


def _order_along(cs, pts):
    """For each point, the nearest letter outline, and where along it it falls."""
    best = np.full(len(pts), -1), np.zeros(len(pts)), np.full(len(pts), 1e18)
    which, where, dist = best[0].copy(), best[1].copy(), best[2].copy()
    for ci, poly in enumerate(cs):
        seg = np.linalg.norm(np.diff(np.vstack([poly, poly[:1]]), axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])[:-1]
        d = np.linalg.norm(pts[:, None, :] - poly[None, :, :], axis=2)
        j = d.argmin(1)
        dm = d[np.arange(len(pts)), j]
        hit = dm < dist
        which[hit], where[hit], dist[hit] = ci, s[j][hit], dm[hit]
    return which, where, dist


def _smooth_runs(order, value, gap_idx, win):
    """Median-smooth a quantity along each uninterrupted run of strokes."""
    out = value.copy()
    start = 0
    for end in list(gap_idx) + [len(order)]:
        run = order[start:end]
        if len(run) >= 3:
            v = value[run]
            k = min(win, len(v) if len(v) % 2 else len(v) - 1)
            if k >= 3:
                out[run] = ndi.median_filter(v, size=k, mode='nearest')
        start = end
    return out


K_ARC = 4.0 / 3.0 * math.tan(math.pi / 8)     # quarter circle as one cubic


def stadium(cx, cy, ang, length, width):
    """A rectangle with semicircular ends, as one closed path of cubics."""
    r = width / 2.0
    h = max(length / 2.0 - r, 0.0)
    ca, sa = math.cos(ang), math.sin(ang)
    loc = lambda p: (cx + p[0] * ca - p[1] * sa, cy + p[0] * sa + p[1] * ca)

    def arc(u, a0, a1):
        """Quarter arc of radius r about (u, 0), from a0 to a1."""
        p0 = (u + r * math.cos(a0), r * math.sin(a0))
        p3 = (u + r * math.cos(a1), r * math.sin(a1))
        t0 = (-r * math.sin(a0) * K_ARC, r * math.cos(a0) * K_ARC)
        t1 = (-r * math.sin(a1) * K_ARC, r * math.cos(a1) * K_ARC)
        return (p0, (p0[0] + t0[0], p0[1] + t0[1]),
                (p3[0] - t1[0], p3[1] - t1[1]), p3)

    H = math.pi / 2
    quarters = [arc(h, -H, 0.0), arc(h, 0.0, H),          # the leading cap
                None,                                      # the long side back
                arc(-h, H, math.pi), arc(-h, math.pi, 3 * H),
                None]                                      # the long side out
    start = loc((h, -r))
    segs = []
    for q in quarters:
        if q is None:
            continue
        segs.append(('C', loc(q[1]), loc(q[2]), loc(q[3])))
        if q is quarters[1]:
            segs.append(('L', loc((-h, r))))
        elif q is quarters[4]:
            segs.append(('L', loc((h, -r))))
    return start, segs


def clip_clear(cx, cy, ang, length, width, dl, gap, min_len):
    """Shorten a stroke to the longest stretch that keeps clear of the letters.

    Measuring the centreline against a distance transform of the letters is
    enough: if every point of the centreline is at least gap + half the stroke
    width away, then so is every point of the stroke, caps included.
    """
    need = gap + width / 2.0
    ca, sa = math.cos(ang), math.sin(ang)
    t = np.arange(-length / 2.0, length / 2.0 + 1e-9, 1.0)
    xs = np.clip((cx + t * ca).round().astype(int), 0, dl.shape[1] - 1)
    ys = np.clip((cy + t * sa).round().astype(int), 0, dl.shape[0] - 1)
    ok = dl[ys, xs] >= need
    if not ok.any():
        return None
    best = (0, 0, 0)
    i = 0
    while i < len(ok):
        if ok[i]:
            j = i
            while j + 1 < len(ok) and ok[j + 1]:
                j += 1
            if j - i > best[0] - 1:
                best = (j - i + 1, i, j)
            i = j + 1
        else:
            i += 1
    n, i, j = best
    if n < 2:
        return None
    t0, t1 = t[i], t[j]
    if t1 - t0 < min_len:
        return None
    return cx + (t0 + t1) / 2 * ca, cy + (t0 + t1) / 2 * sa, t1 - t0


def halo_band(cyan, pitch, smooth, level=0.5):
    """The area the halo covers, as one solid shape with a smooth edge.

    Closing by the pitch merges the separate strokes into the band they imply;
    opening and a blurred re-threshold take the pen's ragged ends off its edge,
    so the rebuilt strokes end on a clean envelope instead of where the hand
    happened to stop.
    """
    b = ndi.binary_closing(cyan, _disk(int(round(pitch))), border_value=0)
    b = ndi.binary_fill_holes(b)
    # a light opening takes the pen's stray ends off the envelope; a heavy one
    # eats the band itself, which is only one or two strokes deep in places
    if smooth > 0:
        b = ndi.binary_opening(b, _disk(max(2, int(round(pitch * 0.18)))))
        # thresholding below the midpoint smooths the edge without pulling it
        # in: at 0.5 the envelope settles on the mean of the drawing's stroke
        # tips and every stroke that reached past it loses that reach
        b = ndi.gaussian_filter(b.astype(float), smooth) > level
    return b


def hatch(region, pitch, width, min_len, dl=None, phase=None, cyan=None,
          trim=0.5, lone=2.2):
    """A true parallel hatch across a region: one family, one pitch, one angle.

    At 135 degrees the lines are the anti-diagonals x + y = c, so stepping c by
    pitch * sqrt(2) walks the family exactly, with no resampling anywhere.
    """
    H, W = region.shape
    step = pitch * math.sqrt(2.0)
    ys, xs = np.nonzero(region)
    if not len(xs):
        return []
    s0, s1 = (xs + ys).min(), (xs + ys).max()
    if phase is None and cyan is not None:
        best = None
        for ph in np.arange(0.0, step, 1.0):
            hit = 0
            for s in np.arange(s0 + ph, s1, step):
                si = int(round(s))
                x = np.arange(max(0, si - H + 1), min(W, si + 1))
                y = si - x
                hit += int(cyan[y, x].sum())
            if best is None or hit > best[0]:
                best = (hit, ph)
        phase = best[1]
    out = []
    for s in np.arange(s0 + (phase or 0.0), s1 + 1, step):
        si = int(round(s))
        x = np.arange(max(0, si - H + 1), min(W, si + 1))
        y = si - x
        keep = (y >= 0) & (y < H)
        x, y = x[keep], y[keep]
        if len(x) < 2:
            continue
        v = region[y, x]
        d = np.diff(v.astype(np.int8))
        starts = list(np.flatnonzero(d == 1) + 1)
        ends = list(np.flatnonzero(d == -1))
        if v[0]:
            starts.insert(0, 0)
        if v[-1]:
            ends.append(len(v) - 1)
        for i, j in zip(starts, ends):
            xi, yi, xj, yj = float(x[i]), float(y[i]), float(x[j]), float(y[j])
            L = math.hypot(xj - xi, yj - yi)
            if L < 1e-6:
                continue
            if dl is not None:
                # the run already clears the letters along its whole length, so
                # the cap on that end may sit where the run ends.  The other end
                # is the halo's outer edge, where the cap belongs just inside it.
                ux, uy = (xj - xi) / L, (yj - yi) / L
                r = width / 2.0 * trim
                if dl[int(yi), int(xi)] > dl[int(yj), int(xj)]:
                    xi, yi = xi + ux * r, yi + uy * r
                else:
                    xj, yj = xj - ux * r, yj - uy * r
                L = math.hypot(xj - xi, yj - yi)
            if L < min_len:
                continue
            out.append(((xi + xj) / 2.0, (yi + yj) / 2.0,
                        math.atan2(yj - yi, xj - xi), L))
    # a stroke with no neighbour at all is a speck the band tapered down to, not
    # part of the hatch; the hatch reads as a run of strokes
    if out:
        P = np.array([(o[0], o[1]) for o in out])
        d = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
        np.fill_diagonal(d, 1e18)
        alone = d.min(1) > lone * pitch
        if alone.any():
            print('      dropped %d isolated speck(s)' % int(alone.sum()))
        out = [o for o, bad in zip(out, alone) if not bad]
    return [stadium(cx, cy, an, L, width) for cx, cy, an, L in out]


def clean_halo(cyan, letter_polys, letter_mask, angle_deg, gap, even,
               smooth_win, verbose=True):
    r = measure_strokes(cyan)
    if not len(r):
        return []
    ang = math.radians(angle_deg if angle_deg is not None
                       else np.degrees(np.median(r[:, 2])) % 180)
    width = float(np.median(r[:, 4]))
    which, where, dist = _order_along(letter_polys, r[:, :2])

    order = np.lexsort((where, which))
    ws, cs_ = where[order], which[order]
    step = np.diff(ws, prepend=ws[0])
    gaps = np.flatnonzero((np.diff(cs_, prepend=cs_[0]) != 0) |
                          (step > 3.0 * np.median(step[step > 0])))
    gaps = [g for g in gaps if g > 0]

    length = _smooth_runs(order, r[:, 3], gaps, smooth_win)
    off = _smooth_runs(order, dist, gaps, smooth_win)

    cx, cy = r[:, 0].copy(), r[:, 1].copy()
    if even:
        start = 0
        for end in list(gaps) + [len(order)]:
            run = order[start:end]
            if len(run) >= 4:
                w0, w1 = where[run[0]], where[run[-1]]
                tgt = np.linspace(w0, w1, len(run))
                for q, i in enumerate(run):
                    ci = int(which[i])
                    poly = letter_polys[ci]
                    seg = np.linalg.norm(np.diff(np.vstack([poly, poly[:1]]),
                                                 axis=0), axis=1)
                    s = np.concatenate([[0.0], np.cumsum(seg)])[:-1]
                    j = int(np.argmin(np.abs(s - tgt[q])))
                    base = poly[j]
                    out = r[i, :2] - base
                    nrm = np.linalg.norm(out)
                    if nrm > 1e-6:
                        cx[i], cy[i] = base + out / nrm * max(off[i], gap + width / 2)
            start = end
    dl = ndi.distance_transform_edt(~letter_mask)
    out, dropped, trimmed = [], 0, 0
    for i in range(len(r)):
        c = clip_clear(cx[i], cy[i], ang, length[i], width, dl, gap,
                       min_len=1.2 * width)
        if c is None:
            dropped += 1
            continue
        if length[i] - c[2] > 1.0:
            trimmed += 1
        out.append(stadium(c[0], c[1], ang, c[2], width))
    if verbose:
        print('   halo: %d strokes at %.1f deg, width %.1f px; %d held off the '
              'letters, %d too short to keep'
              % (len(out), math.degrees(ang) % 180, width, trimmed, dropped))
    return out


# -------------------------------------------------------------------- the job

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--size', type=float, default=480.0)
    ap.add_argument('--sigma', type=float, default=1.6)
    ap.add_argument('--line-tol', type=float, default=1.1)
    ap.add_argument('--curve-tol', type=float, default=0.7)
    ap.add_argument('--repair', type=int, default=6)
    ap.add_argument('--angle', type=float, default=135.0,
                    help='the hatch angle, in degrees; the drawing measures '
                         '135.0 with a 2.6 deg spread, so it is held exactly')
    ap.add_argument('--gap', type=float, default=8.0)
    ap.add_argument('--pitch', type=float, default=21.0,
                    help='perpendicular spacing of the hatch; the drawing '
                         'measures 21.4 px between neighbours, and scanning '
                         'across it gives 22.6')
    ap.add_argument('--width', type=float, default=15.0,
                    help='hatch stroke width; the drawing measures 14.3 px by '
                         'area over length and 15.6 px by scan run-length')
    ap.add_argument('--band-smooth', type=float, default=6.0)
    ap.add_argument('--band-level', type=float, default=0.30)
    ap.add_argument('--keyline', type=float, default=10.0,
                    help='how far the keyline ring is grown off the letters. '
                         'The drawing\'s cream measures 6.0 px, but rebuilding '
                         'the grown outline on structural nodes rounds it back '
                         'in, so 10 px of growth is what lands a ring of the '
                         'right weight: 0.345%% of the letters box against the '
                         'drawing\'s 0.360%%')
    ap.add_argument('--lone', type=float, default=999.0,
                    help="a stroke with no neighbour within this many pitches "
                         "is dropped as a speck. Effectively off: at 2.2 it ate "
                         "the halo wherever the band is only one stroke deep, "
                         "which emptied the O's upper left entirely. The minimum "
                         "stroke length already removes real specks.")
    ap.add_argument('--trim', type=float, default=0.0,
                    help='how far inside the halo edge a stroke ends, in cap '
                         'radii; 1.0 puts the cap exactly on the smoothed edge, '
                         'which sits at the mean of the drawing\'s stroke tips '
                         'and so loses the reach of every stroke that went past it')
    ap.add_argument('--min-len', type=float, default=0.4,
                    help='shortest stroke to keep, in stroke widths')
    ap.add_argument('--smooth-win', type=int, default=5)
    ap.add_argument('--corner-deg', type=float, default=38.0)
    ap.add_argument('--fit-tol', type=float, default=8.0,
                    help='how far a span\'s single cubic may stray from the '
                         'traced run before the span is split and refitted. '
                         'Too large and a long span bows - it cannot follow a '
                         'double bend; too small and the splits chase the pen '
                         'wobble the rebuild exists to remove')
    ap.add_argument('--no-even', action='store_true')
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    fit = dict(line_tol=a.line_tol, curve_tol=a.curve_tol,
               smooth_deg=34.0, min_smooth_run=3)

    black, cream, cyan = layers(a.image)
    black = repair(black, cream, a.repair)
    cyan = repair(cyan, cream, a.repair)

    lab, n = ndi.label(black)
    sizes = ndi.sum(black, lab, range(1, n + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s > 2000]
    cols = {i: np.nonzero((lab == i).any(0))[0] for i in big}
    m_id = max(big, key=lambda i: cols[i].mean())
    split_x = int((cols[m_id].min() + max(cols[i].max()
                                          for i in big if i != m_id)) / 2)
    right = np.zeros_like(black)
    right[:, split_x:] = True
    print('   splitting O from M at x=%d; symmetrising the M' % split_x)
    bl = np.where(right, mirror_pair([black & right], 0)[0], black.astype(float))

    reg = dict(corner_deg=a.corner_deg, corner_span=11, extreme_span=9,
               min_run=9, straight_tol=1.1, merge=9.0, fit_tol=a.fit_tol)
    B = clean_letters(bl > 0.5, a.sigma, fit, **reg)
    axis = _axis_of(bl > 0.5, right)
    on_m = lambda c: np.mean([p[0] for q in [('L', c[0])] + c[1]
                              for p in q[1:]]) >= split_x
    B = [symmetrise_contour(c, axis) if on_m(c) else c for c in B]
    print('   letters %d contours, %d nodes (was %d before rebuilding)'
          % (len(B), sum(len(c[1]) for c in B),
             sum(len(c[1]) for c in trace_layer(bl, a.sigma, **fit))))

    polys = [np.asarray(vl._flatten(c, step=2.0) if hasattr(vl, '_flatten')
                        else _flat(c), float) for c in B]
    r = measure_strokes(cyan)
    width = float(np.median(r[:, 4])) if a.width is None else a.width
    pitch = a.pitch
    band = halo_band(cyan, pitch, a.band_smooth, a.band_level)
    rad = int(round(width / 2.0))
    # no all-direction erosion of the band: that eats the places where the halo
    # is only one stroke deep, and shortens every stroke besides.  A stroke only
    # has to clear the letters, which the dilation below guarantees along its
    # whole length, and end inside the halo's outer edge, which is a trim of one
    # radius at that end alone.
    region = band & ~ndi.binary_dilation(bl > 0.5, _disk(int(round(a.gap)) + rad))
    dl = ndi.distance_transform_edt(~(bl > 0.5))
    C = hatch(region, pitch, width, a.min_len * width, dl=dl, cyan=cyan,
              trim=a.trim, lone=a.lone)

    # the keyline, as an even ring rather than the hand's varying band: the
    # letters grown by the width the drawing's cream measures, traced and
    # rebuilt the same way, and painted under the letters so only the ring shows
    key = ndi.binary_dilation(bl > 0.5, _disk(int(round(a.keyline))))
    K = clean_letters(key, a.sigma, fit, **reg)
    K = [symmetrise_contour(c, axis) if on_m(c) else c for c in K]
    print('   keyline: even ring %.0f px wide, %d contours'
          % (a.keyline, len(K)))
    print('   halo: %d strokes, one family at %.1f deg, pitch %.1f px, '
          'width %.1f px (white gap %.1f px)'
          % (len(C), a.angle, pitch, width, pitch - width))

    cap = float(np.ptp(np.nonzero((bl > 0.5) & ~right)[0]))
    k = a.size / cap
    H = black.shape[0]
    up = lambda cs: [((c[0][0] * k, (H - c[0][1]) * k),
                      [(q[0],) + tuple((p[0] * k, (H - p[1]) * k) for p in q[1:])
                       for q in c[1]]) for c in cs]
    B, C, K = up(B), up(C), up(K)
    pts = [p for cs in (B, C, K) for c in cs
           for q in [('L', c[0])] + c[1] for p in q[1:]]
    x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
    x1 = max(p[0] for p in pts); y1 = max(p[1] for p in pts)
    pad = 0.05 * a.size
    mv = lambda cs: [((c[0][0] - x0 + pad, c[0][1] - y0 + pad),
                      [(q[0],) + tuple((p[0] - x0 + pad, p[1] - y0 + pad)
                                       for p in q[1:]) for q in c[1]])
                     for c in cs]
    B, C, K = mv(B), mv(C), mv(K)
    W, Hh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    sets = {'om-colour': [(CYAN, C), (CREAM, K), (BLACK, B)],
            'om-black': [(BLACK, C), (BLACK, B)],
            'om-black-letters': [(BLACK, B)]}
    for nm, lay in sets.items():
        write_pdf(os.path.join(a.outdir, nm + '.pdf'), lay, W, Hh)
        write_svg(os.path.join(a.outdir, nm + '.svg'), lay, W, Hh)
        print('   %-26s %7.1f x %7.1f pt' % (nm + '.pdf/.svg', W, Hh))
    return 0


def _flat(contour, step=2.0):
    start, segs = contour
    cur = np.asarray(start, float)
    out = [cur]
    for s in segs:
        if s[0] == 'L':
            cur = np.asarray(s[1], float)
            out.append(cur)
        else:
            b = [cur] + [np.asarray(q, float) for q in s[1:]]
            t = np.linspace(0, 1, 20)[1:, None]
            out += list((1 - t) ** 3 * b[0] + 3 * (1 - t) ** 2 * t * b[1]
                        + 3 * (1 - t) * t ** 2 * b[2] + t ** 3 * b[3])
            cur = b[3]
    return np.asarray(out)


if __name__ == '__main__':
    raise SystemExit(main())
