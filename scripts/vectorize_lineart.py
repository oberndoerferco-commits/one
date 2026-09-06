#!/usr/bin/env python3
"""Vectorise raster line art into clean outlines: straight edges stay straight.

A general-purpose tracer fits curves to whatever the bitmap contains, so on a
low-resolution JPEG the pixel staircase and compression ringing along a 3px
stroke come out as visible ripple on edges that are meant to be dead straight.

This tracer separates signal from digitisation noise:

  1. Sub-pixel iso-contours from the greyscale (anti-aliasing aware), so the
     starting point is not the pixel grid.
  2. Corner detection over an arc-length window, so genuine corners survive
     while noise does not create new ones.
  3. Between corners, fit the simplest primitive that holds within tolerance:
     a straight line if one fits, otherwise smooth cubic Beziers (Schneider
     least-squares fitting with recursive subdivision).

Straight edges therefore come out as single straight segments, genuine curves
stay smooth, and ripple below the tolerance is absorbed rather than traced.
"""

import argparse
import math

import numpy as np
from scipy import ndimage
from skimage import measure

EPS = 1e-12


# ------------------------------------------------------------------ helpers


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > EPS else np.array([0.0, 0.0])


def _resample_closed(pts, step=0.5):
    """Uniform arc-length resampling of a closed contour."""
    closed = np.vstack([pts, pts[:1]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    d = np.concatenate([[0.0], np.cumsum(seg)])
    total = d[-1]
    if total < EPS:
        return pts
    m = max(8, int(round(total / step)))
    want = np.linspace(0.0, total, m, endpoint=False)
    return np.column_stack([np.interp(want, d, closed[:, 0]),
                            np.interp(want, d, closed[:, 1])])


def _tls_line(pts):
    c = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    return c, _unit(vt[0])


def _line_residual(pts, c, d):
    v = pts - c
    return float(np.abs(v[:, 0] * d[1] - v[:, 1] * d[0]).max()) if len(pts) else 0.0


def _intersect(c1, d1, c2, d2):
    """Intersection of two lines given as (point, direction)."""
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) < 1e-9:
        return None
    dc = c2 - c1
    return c1 + ((dc[0] * d2[1] - dc[1] * d2[0]) / denom) * d1


def _detect_corners(pts, window, angle_deg):
    """Indices of genuine corners, by turning angle over an arc-length window."""
    n = len(pts)
    if n < 3 * window:
        return []
    i = np.arange(n)
    back = pts[i] - pts[(i - window) % n]
    fwd = pts[(i + window) % n] - pts[i]
    nb = np.linalg.norm(back, axis=1)
    nf = np.linalg.norm(fwd, axis=1)
    ok = (nb > EPS) & (nf > EPS)
    cos = np.ones(n)
    cos[ok] = np.clip((back[ok] * fwd[ok]).sum(1) / (nb[ok] * nf[ok]), -1.0, 1.0)
    ang = np.degrees(np.arccos(cos))
    cand = np.flatnonzero(ang > angle_deg)
    if len(cand) == 0:
        return []
    # Non-maximum suppression: keep the sharpest point in each run of candidates.
    corners = []
    for idx in sorted(cand, key=lambda j: -ang[j]):
        if all(min(abs(idx - c), n - abs(idx - c)) >= window for c in corners):
            corners.append(int(idx))
    return sorted(corners)


# ------------------------------------------------- cubic Bezier curve fitting


def _bezier_point(b, t):
    mt = 1.0 - t
    return (b[0] * mt ** 3 + b[1] * 3 * t * mt ** 2
            + b[2] * 3 * t ** 2 * mt + b[3] * t ** 3)


def _bezier_points(b, t):
    """Evaluate a cubic Bezier at many parameters at once."""
    mt = 1.0 - t
    return (np.outer(mt ** 3, b[0]) + np.outer(3 * t * mt ** 2, b[1])
            + np.outer(3 * t ** 2 * mt, b[2]) + np.outer(t ** 3, b[3]))


def _chord_param(d):
    seg = np.linalg.norm(np.diff(d, axis=0), axis=1)
    u = np.concatenate([[0.0], np.cumsum(seg)])
    return u / u[-1] if u[-1] > EPS else np.linspace(0, 1, len(d))


def _generate_bezier(d, u, t1, t2):
    """Least-squares cubic Bezier through d with fixed end tangents."""
    n = len(d)
    a0 = np.outer(3 * u * (1 - u) ** 2, t1)
    a1 = np.outer(3 * u ** 2 * (1 - u), t2)
    c00 = float((a0 * a0).sum())
    c01 = float((a0 * a1).sum())
    c11 = float((a1 * a1).sum())
    base = (np.outer((1 - u) ** 3 + 3 * u * (1 - u) ** 2, d[0])
            + np.outer(3 * u ** 2 * (1 - u) + u ** 3, d[-1]))
    tmp = d - base
    x0 = float((a0 * tmp).sum())
    x1 = float((a1 * tmp).sum())
    det = c00 * c11 - c01 * c01
    dist = np.linalg.norm(d[-1] - d[0])
    if abs(det) > EPS:
        alpha1 = (x0 * c11 - x1 * c01) / det
        alpha2 = (c00 * x1 - c01 * x0) / det
    else:
        alpha1 = alpha2 = dist / 3.0
    if alpha1 < EPS or alpha2 < EPS or alpha1 > 3 * dist or alpha2 > 3 * dist:
        alpha1 = alpha2 = dist / 3.0
    return np.array([d[0], d[0] + t1 * alpha1, d[-1] + t2 * alpha2, d[-1]])


def _max_error(d, bez, u):
    err = np.linalg.norm(_bezier_points(bez, u) - d, axis=1)
    k = int(err.argmax())
    return float(err[k]), k


def _reparameterize(d, bez, u):
    mt = 1.0 - u
    p = _bezier_points(bez, u)
    d1 = (np.outer(3 * mt ** 2, bez[1] - bez[0])
          + np.outer(6 * mt * u, bez[2] - bez[1])
          + np.outer(3 * u ** 2, bez[3] - bez[2]))
    d2 = (np.outer(6 * mt, bez[2] - 2 * bez[1] + bez[0])
          + np.outer(6 * u, bez[3] - 2 * bez[2] + bez[1]))
    diff = p - d
    num = (diff * d1).sum(1)
    den = (d1 * d1).sum(1) + (diff * d2).sum(1)
    out = np.where(np.abs(den) > EPS, u - num / np.where(np.abs(den) > EPS, den, 1.0), u)
    return np.clip(out, 0.0, 1.0)


def _fit_cubic(d, t1, t2, tol, depth=0):
    """Schneider fit: cubic Beziers approximating d within tol."""
    if len(d) < 3:
        dist = np.linalg.norm(d[-1] - d[0]) / 3.0
        return [np.array([d[0], d[0] + t1 * dist, d[-1] + t2 * dist, d[-1]])]
    u = _chord_param(d)
    bez = _generate_bezier(d, u, t1, t2)
    err, split = _max_error(d, bez, u)
    if err < tol:
        return [bez]
    if err < tol * 4 and depth < 12:
        for _ in range(4):
            u = _reparameterize(d, bez, u)
            bez = _generate_bezier(d, u, t1, t2)
            err, split = _max_error(d, bez, u)
            if err < tol:
                return [bez]
    if depth >= 12 or split <= 0 or split >= len(d) - 1:
        return [bez]
    centre = _unit(d[split + 1] - d[split - 1])
    return (_fit_cubic(d[:split + 1], t1, -centre, tol, depth + 1)
            + _fit_cubic(d[split:], centre, t2, tol, depth + 1))


# ------------------------------------------------------------ contour fitting


def _rdp(pts, tol):
    """Douglas-Peucker on an open chain. Returns indices into pts."""
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, ab = pts[i], pts[j] - pts[i]
        n = np.linalg.norm(ab)
        seg = pts[i + 1:j]
        if n < EPS:
            dist = np.linalg.norm(seg - a, axis=1)
        else:
            u = ab / n
            v = seg - a
            dist = np.abs(v[:, 0] * u[1] - v[:, 1] * u[0])
        k = int(dist.argmax())
        if dist[k] > tol:
            k += i + 1
            keep[k] = True
            stack += [(i, k), (k, j)]
    return np.flatnonzero(keep)


def _polygon_indices(rs, tol):
    """Break a closed contour into straight runs. Returns vertex indices."""
    n = len(rs)
    c = rs.mean(axis=0)
    a = int(np.linalg.norm(rs - c, axis=1).argmax())
    b = int(np.linalg.norm(rs - rs[a], axis=1).argmax())
    lo, hi = min(a, b), max(a, b)
    first = _rdp(rs[lo:hi + 1], tol) + lo
    second = (_rdp(np.vstack([rs[hi:], rs[:lo + 1]]), tol) + hi) % n
    return list(np.unique(np.concatenate([first, second])))


def _run_points(rs, i0, i1):
    return rs[i0:i1 + 1] if i0 < i1 else np.vstack([rs[i0:], rs[:i1 + 1]])


def _end_tangent(run, forward, span=8):
    """Local direction at a run end, from a short least-squares fit."""
    k = min(len(run), max(3, span))
    seg = run[:k] if forward else run[-k:]
    _, d = _tls_line(seg)
    ref = (seg[-1] - seg[0]) if forward else (seg[0] - seg[-1])
    if float(d @ ref) < 0:
        d = -d
    return d


def _signed_turn(d0, d1):
    """Signed turn angle in degrees from direction d0 to d1."""
    cross = float(d0[0] * d1[1] - d0[1] * d1[0])
    dot = float(d0 @ d1)
    return math.degrees(math.atan2(cross, dot))


def fit_contour(pts, line_tol=0.5, curve_tol=0.35, smooth_deg=45.0,
                min_smooth_run=2, step=0.4, allow_corners=True,
                merge_deg=4.0, merge_slack=1.6):
    """Fit a closed contour as straight lines plus smooth curves where curved.

    Straight runs are fitted as single line segments with their vertices placed
    at the intersection of adjacent least-squares lines, so long edges come out
    straight and corners stay sharp. Runs whose polygonal approximation turns
    gently and consistently in one direction are genuine curves, and get
    refitted as smooth Beziers so they are not left faceted.

    Returns (start_point, [('L', p) | ('C', c1, c2, p), ...]).
    """
    rs = _resample_closed(pts, step)
    n = len(rs)
    if n < 8:
        return rs[0], [('L', p) for p in rs[1:]]

    if not allow_corners:
        # Small blobs (dots): one smooth closed loop, no corner hunting.
        anchors = [0, n // 2]
        segs = []
        for k in range(2):
            run = _run_points(rs, anchors[k], anchors[(k + 1) % 2])
            t1 = _end_tangent(run, True)
            t2 = -_end_tangent(run, False)
            for bez in _fit_cubic(run, t1, t2, curve_tol):
                segs.append(('C', bez[1], bez[2], bez[3]))
        return rs[anchors[0]], segs

    idx = _polygon_indices(rs, line_tol)
    if len(idx) < 3:
        return rs[0], [('L', p) for p in rs[1:]]

    def fit_lines(ix):
        out = []
        for k in range(len(ix)):
            run = _run_points(rs, ix[k], ix[(k + 1) % len(ix)])
            if len(run) < 2:
                run = np.vstack([rs[ix[k]], rs[ix[(k + 1) % len(ix)]]])
            out.append(_tls_line(run))
        return out

    lines = fit_lines(idx)

    # Merge neighbouring runs that are really one straight edge.
    cos_thresh = math.cos(math.radians(merge_deg))
    merged = True
    while merged and len(idx) > 3:
        merged = False
        for k in range(len(idx)):
            k2 = (k + 1) % len(idx)
            if abs(float(lines[k][1] @ lines[k2][1])) < cos_thresh:
                continue
            run = _run_points(rs, idx[k], idx[(k2 + 1) % len(idx)])
            c, d = _tls_line(run)
            if _line_residual(run, c, d) <= line_tol * merge_slack:
                del idx[k2]
                lines = fit_lines(idx)
                merged = True
                break

    m = len(idx)
    # Orient each fitted line along the direction of travel.
    dirs = []
    for k in range(m):
        d = lines[k][1]
        ref = rs[idx[(k + 1) % m]] - rs[idx[k]]
        dirs.append(-d if float(d @ ref) < 0 else d)

    turns = [_signed_turn(dirs[k - 1], dirs[k]) for k in range(m)]

    # A vertex is "smooth" when the polygon barely turns there; a maximal run of
    # smooth vertices all turning the same way is a curve, not a set of corners.
    smooth = [abs(t) <= smooth_deg for t in turns]
    curve_vertex = [False] * m
    k = 0
    while k < m:
        if not smooth[k]:
            k += 1
            continue
        run = [k]
        j = (k + 1) % m
        while len(run) < m and smooth[j] and (turns[j] > 0) == (turns[run[-1]] > 0):
            run.append(j)
            j = (j + 1) % m
        if len(run) >= min_smooth_run:
            for v in run:
                curve_vertex[v] = True
        k += len(run)

    # Vertices are intersections of adjacent lines, which restores sharp corners.
    verts = []
    for k in range(m):
        p = _intersect(lines[k - 1][0], lines[k - 1][1], lines[k][0], lines[k][1])
        orig = rs[idx[k]]
        if p is None or np.linalg.norm(p - orig) > 6.0 * line_tol + 2.0:
            p = orig
        verts.append(p)

    # Rotate so we start on a corner, so curve runs never straddle the seam.
    start_k = next((k for k in range(m) if not curve_vertex[k]), 0)
    order = [(start_k + i) % m for i in range(m)] + [start_k]

    segs = []
    i = 0
    while i < m:
        k = order[i]
        nxt = order[i + 1]
        if curve_vertex[nxt]:
            # Extend the curve across every consecutive smooth vertex.
            j = i + 1
            while j < m and curve_vertex[order[j]]:
                j += 1
            a, b = order[i], order[j]
            run = _run_points(rs, idx[a], idx[b]).copy()
            t1 = _end_tangent(run, True)
            t2 = -_end_tangent(run, False)
            # Pin the curve to the vertices already placed for its neighbours,
            # so lines and curves meet exactly with no seam.
            run[0] = verts[a]
            run[-1] = verts[b]
            for bez in _fit_cubic(run, t1, t2, curve_tol):
                segs.append(('C', bez[1], bez[2], bez[3]))
            i = j
        else:
            segs.append(('L', verts[nxt]))
            i += 1
    return verts[order[0]], segs


# ------------------------------------------------------------------- tracing


def _contour_area(contour):
    """Absolute enclosed area from a fitted contour's anchor points."""
    start, segs = contour
    pts = [start] + [s[1] if s[0] == 'L' else s[3] for s in segs]
    p = np.array(pts)
    x, y = p[:, 0], p[:, 1]
    return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def trace(gray, level=0.5, sigma=0.5, dot_area=500, min_area=12,
          min_contour_area=1.0, **fit):
    """Trace a greyscale image. Returns a list of (start, segments) contours."""
    g = ndimage.gaussian_filter(gray.astype(np.float32), sigma) if sigma > 0 else gray
    mask = g < level
    lbl, n = ndimage.label(mask, structure=np.ones((3, 3)))
    out = []
    for k in range(1, n + 1):
        comp = lbl == k
        if int(comp.sum()) < min_area:
            continue
        small = int(comp.sum()) <= dot_area
        region = ndimage.binary_dilation(comp, iterations=3)
        gk = np.where(region, g, 1.0)
        for con in measure.find_contours(gk, level):
            # (row,col) -> (x,y); find_contours indexes pixel centres, so +0.5
            # puts us in continuous image space where pixel k spans [k, k+1].
            pts = con[:, ::-1].astype(np.float64) + 0.5
            if len(pts) > 1 and np.allclose(pts[0], pts[-1]):
                pts = pts[:-1]
            if len(pts) < 4:
                continue
            fitted = fit_contour(pts, allow_corners=not small, **fit)
            # Drop sub-pixel specks and slivers: invisible at any print size,
            # and they only add clutter to the path data.
            if _contour_area(fitted) < min_contour_area:
                continue
            out.append(fitted)
    return out


# ------------------------------------------------------------------- writers


def _fmt(v, prec=3):
    s = f"{v:.{prec}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def emit(contours, to_xy, prec=3):
    """Render contours as (svg path data, pdf ops, postscript ops)."""
    svg, pdf, ps = [], [], []
    f = lambda v: _fmt(v, prec)
    for start, segs in contours:
        sx, sy = to_xy(start)
        s = [f"M{f(sx)} {f(sy)}"]
        p = [f"{f(sx)} {f(sy)} m"]
        q = [f"{f(sx)} {f(sy)} moveto"]
        for seg in segs:
            if seg[0] == 'L':
                x, y = to_xy(seg[1])
                s.append(f"L{f(x)} {f(y)}")
                p.append(f"{f(x)} {f(y)} l")
                q.append(f"{f(x)} {f(y)} lineto")
            else:
                a, b, c = to_xy(seg[1]), to_xy(seg[2]), to_xy(seg[3])
                s.append(f"C{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])}")
                p.append(f"{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])} c")
                q.append(f"{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} "
                         f"{f(c[0])} {f(c[1])} curveto")
        svg.append(" ".join(s) + " Z")
        pdf.append(" ".join(p) + " h")
        ps.append(" ".join(q) + " closepath")
    return svg, pdf, ps


def write_svg(path, subpaths, w, h, ox=0.0, oy=0.0):
    d = " ".join(subpaths)
    with open(path, "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                 '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
                 f' width="{w:.4f}pt" height="{h:.4f}pt"\n'
                 f' viewBox="{ox:.4f} {oy:.4f} {w:.4f} {h:.4f}">\n'
                 f'<path fill="#000000" fill-rule="evenodd" stroke="none"\n'
                 f' d="{d}"/>\n</svg>\n')


def write_pdf(path, ops, w, h, ox=0.0, oy=0.0):
    content = ("0 g\n" + "\n".join(ops) + "\nf*\n").encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [{ox:.4f} {oy:.4f} "
         f"{ox + w:.4f} {oy + h:.4f}] /Contents 4 0 R /Resources << >> >>").encode(),
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
        + content + b"endstream",
    ]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offs = []
    for i, body in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode() + b"0000000000 65535 f \n"
    for o in offs:
        out += f"{o:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    open(path, "wb").write(bytes(out))


def write_eps(path, ops, w, h, ox=0.0, oy=0.0):
    with open(path, "w") as fh:
        fh.write("%!PS-Adobe-3.0 EPSF-3.0\n"
                 f"%%BoundingBox: {math.floor(ox)} {math.floor(oy)} "
                 f"{math.ceil(ox + w)} {math.ceil(oy + h)}\n"
                 f"%%HiResBoundingBox: {ox:.4f} {oy:.4f} "
                 f"{ox + w:.4f} {oy + h:.4f}\n%%EndComments\n"
                 "0 setgray\nnewpath\n" + "\n".join(ops)
                 + "\neofill\nshowpage\n%%EOF\n")


def stats(contours):
    lines = sum(1 for _, segs in contours for s in segs if s[0] == 'L')
    curves = sum(1 for _, segs in contours for s in segs if s[0] == 'C')
    return len(contours), lines, curves


# ---------------------------------------------------------------------- main


def load_gray(path):
    """Load a greyscale array from an image, or from a PDF wrapping one image."""
    from PIL import Image
    if path.lower().endswith(".pdf"):
        import pymupdf
        doc = pymupdf.open(path)
        imgs = doc[0].get_images(full=True)
        if not imgs:
            raise SystemExit(f"{path}: no embedded image to trace")
        raw = doc.extract_image(imgs[0][0])
        import io
        im = Image.open(io.BytesIO(raw["image"]))
    else:
        im = Image.open(path)
    return np.asarray(im.convert("L")).astype(np.float32) / 255.0, im.size


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", help="source image, or PDF wrapping a single image")
    ap.add_argument("outdir", help="directory to write the vector files into")
    ap.add_argument("--name", default="traced", help="basename for the outputs")
    ap.add_argument("--dpi", type=float, default=132.0,
                    help="source resolution, sets the output's physical size")
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--line-tol", type=float, default=0.5,
                    help="straightness tolerance in source pixels")
    ap.add_argument("--curve-tol", type=float, default=0.35)
    ap.add_argument("--smooth-deg", type=float, default=40.0)
    ap.add_argument("--min-smooth-run", type=int, default=3)
    args = ap.parse_args(argv)

    import os
    gray, (w, h) = load_gray(args.input)
    k = 72.0 / args.dpi
    wpt, hpt = w * k, h * k
    contours = trace(gray, sigma=args.sigma, line_tol=args.line_tol,
                     curve_tol=args.curve_tol, smooth_deg=args.smooth_deg,
                     min_smooth_run=args.min_smooth_run)

    to_svg = lambda p: (p[0] * k, p[1] * k)
    to_pdf = lambda p: (p[0] * k, hpt - p[1] * k)
    svg_full, _, _ = emit(contours, to_svg)
    _, pdf_full, ps_full = emit(contours, to_pdf)

    os.makedirs(args.outdir, exist_ok=True)
    base = os.path.join(args.outdir, args.name)
    write_svg(base + ".svg", svg_full, wpt, hpt)
    write_pdf(base + ".pdf", pdf_full, wpt, hpt)
    write_eps(base + ".eps", ps_full, wpt, hpt)

    # Trimmed variants: same geometry, box tightened to the artwork.
    import pymupdf
    page = pymupdf.open(base + ".pdf")[0]
    r = None
    for d in page.get_drawings():
        r = d["rect"] if r is None else (r | d["rect"])
    write_svg(f"{base}-trimmed.svg", svg_full, r.width, r.height, r.x0, r.y0)
    write_pdf(f"{base}-trimmed.pdf", pdf_full, r.width, r.height, r.x0, hpt - r.y1)
    write_eps(f"{base}-trimmed.eps", ps_full, r.width, r.height, r.x0, hpt - r.y1)

    nc, nl, ncv = stats(contours)
    print(f"{nc} contours, {nl} straight segments, {ncv} curve segments")
    print(f"page {wpt:.2f} x {hpt:.2f} pt; artwork {r.width:.2f} x {r.height:.2f} pt "
          f"({r.width / 72 * 25.4:.1f} x {r.height / 72 * 25.4:.1f} mm)")
    return base, r


if __name__ == "__main__":
    main()
