#!/usr/bin/env python3
"""Construct the OM mark from geometry - no tracing, no fitting, no pixels.

Every previous attempt in this repo derived the letters from the photograph and
then tried to clean up what the scan put there.  That cannot work: a dent is
low-frequency, so smoothing follows it and fitting reproduces it.  Here nothing
is measured off an image.  Each outline is built from straight lines and
circular arcs joined at exact tangents, so the curves are smooth because of how
they are defined, not because of how hard they were filtered.

The brief is a mark for a ring: a few millimetres across, struck or engraved in
metal.  That argues for fewer and larger shapes, a bolder cut and *less* stroke
contrast than the gold reference has - thin strokes are the first thing to die
at 3 mm - and for a silhouette that reads before the letters do.
"""

import math

CAP = 1000.0


# ----------------------------------------------------------------- primitives


def arc(cx, cy, rx, ry, a0, a1):
    """Elliptical arc as cubic Beziers, at most 90 degrees each."""
    out, n = [], max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 2))))
    step = (a1 - a0) / n
    k = 4.0 / 3.0 * math.tan(step / 4.0)
    for i in range(n):
        t0 = a0 + i * step
        t1 = t0 + step
        p0 = (cx + rx * math.cos(t0), cy + ry * math.sin(t0))
        p1 = (cx + rx * math.cos(t1), cy + ry * math.sin(t1))
        d0 = (-rx * math.sin(t0), ry * math.cos(t0))
        d1 = (-rx * math.sin(t1), ry * math.cos(t1))
        out.append(('C', (p0[0] + k * d0[0], p0[1] + k * d0[1]),
                    (p1[0] - k * d1[0], p1[1] - k * d1[1]), p1))
    return out


def ellipse(cx, cy, rx, ry, ccw=True):
    segs = arc(cx, cy, rx, ry, 0.0, 2 * math.pi if ccw else -2 * math.pi)
    return ((cx + rx, cy), segs)


def poly(points):
    return (points[0], [('L', p) for p in points[1:]])


def round_rect_path(pts, radii):
    """Closed path through `pts`, each corner cut by a tangent arc of radii[i]."""
    n = len(pts)
    out, start = [], None
    for i in range(n):
        p = pts[i]
        a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        r = radii[i]
        va = (a[0] - p[0], a[1] - p[1])
        vb = (b[0] - p[0], b[1] - p[1])
        la = math.hypot(*va) or 1.0
        lb = math.hypot(*vb) or 1.0
        ua, ub = (va[0] / la, va[1] / la), (vb[0] / lb, vb[1] / lb)
        ang = math.acos(max(-1.0, min(1.0, ua[0] * ub[0] + ua[1] * ub[1])))
        if r <= 0 or ang < 1e-6 or abs(math.pi - ang) < 1e-6:
            if start is None:
                start = p
            else:
                out.append(('L', p))
            continue
        t = r / math.tan(ang / 2.0)
        t = min(t, la * 0.5, lb * 0.5)
        r_eff = t * math.tan(ang / 2.0)
        p1 = (p[0] + ua[0] * t, p[1] + ua[1] * t)
        p2 = (p[0] + ub[0] * t, p[1] + ub[1] * t)
        bis = (ua[0] + ub[0], ua[1] + ub[1])
        lb2 = math.hypot(*bis) or 1.0
        d = r_eff / math.sin(ang / 2.0)
        c = (p[0] + bis[0] / lb2 * d, p[1] + bis[1] / lb2 * d)
        a0 = math.atan2(p1[1] - c[1], p1[0] - c[0])
        a1 = math.atan2(p2[1] - c[1], p2[0] - c[0])
        while a1 - a0 > math.pi:
            a1 -= 2 * math.pi
        while a0 - a1 > math.pi:
            a1 += 2 * math.pi
        if start is None:
            start = p1
        else:
            out.append(('L', p1))
        out += arc(c[0], c[1], r_eff, r_eff, a0, a1)
    return (start, out)


def tr(contour, k=1.0, dx=0.0, dy=0.0, mx=1.0):
    f = lambda p: (p[0] * k * mx + dx, p[1] * k + dy)
    s, segs = contour
    return f(s), [(q[0],) + tuple(f(v) for v in q[1:]) for q in segs]


def bbox(contours):
    pts = [p for c in contours for q in [(('L',) + (c[0],))] + c[1] for p in q[1:]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- letterforms


def _ring(poly_):
    return list(poly_.exterior.coords)[:-1]


def fillet(ring, r_convex=0.0, r_concave=0.0):
    """Cut every corner of a polygon with a tangent arc, by corner type."""
    n = len(ring)
    area = sum(ring[i][0] * ring[(i + 1) % n][1] - ring[(i + 1) % n][0] * ring[i][1]
               for i in range(n))
    sgn = 1.0 if area > 0 else -1.0
    radii = []
    for i in range(n):
        a, p, b = ring[(i - 1) % n], ring[i], ring[(i + 1) % n]
        cross = ((p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])) * sgn
        radii.append(r_convex if cross > 0 else r_concave)
    return round_rect_path(ring, radii)


def glyph_O(cap=CAP, w=0.86, side=0.172, thin=0.118):
    """A ring: two ellipses, thick at the sides, lighter over the crown.

    Contrast is deliberately lower than the gold reference's.  At three
    millimetres the thin part of a high-contrast O is the first thing to vanish.
    """
    rx, ry = w * cap / 2, cap / 2
    cy = cap / 2
    return [ellipse(0, cy, rx, ry, True),
            ellipse(0, cy, rx - side * cap, ry - thin * cap, False)]


def glyph_M(cap=CAP, width=0.90, stem=0.166, over=0.065, slab=0.095,
            ya=0.54, yb=0.40, pix=0.038, piy=0.12, bracket=0.085, tip=0.022):
    """Slab-serif M, written out as an explicit vertex list.

    Two upright stems with square serifs, and a V between them whose outer edges
    meet in a point on the baseline and whose inner notch comes down to `piy`.
    Putting the inner apex right of centre (`pix`) makes the left stroke of the V
    heavier than the right, which is the contrast the gold reference is drawn
    with - kept, but moderated, because a very thin stroke will not survive
    being struck at three millimetres.
    """
    W, S, V, T = width * cap, stem * cap, over * cap, slab * cap
    xl, xr = V + S / 2, W - V - S / 2
    xlL, xlR = xl - S / 2 - V, xl + S / 2 + V
    xrL, xrR = xr - S / 2 - V, xr + S / 2 + V
    mid = W / 2
    pts = [(xlL, 0), (xlR, 0), (xlR, T), (xl + S / 2, T),
           (xl + S / 2, ya * cap), (mid, 0), (xr - S / 2, yb * cap),
           (xr - S / 2, T), (xrL, T), (xrL, 0), (xrR, 0), (xrR, T),
           (xr + S / 2, T), (xr + S / 2, cap - T), (xrR, cap - T), (xrR, cap),
           (xrL, cap), (mid + pix * cap, piy * cap), (xlR, cap), (xlL, cap),
           (xlL, cap - T), (xl - S / 2, cap - T), (xl - S / 2, T), (xlL, T)]
    return [fillet(pts, r_convex=tip * cap, r_concave=bracket * cap)]


def centred(contours, cap=CAP):
    x0, y0, x1, y1 = bbox(contours)
    return [tr(c, 1.0, -(x0 + x1) / 2, 0.0) for c in contours]


# ------------------------------------------------- node-and-tangent splines


def node(x, y, ang, lin=0.0, lout=None):
    """A point on an outline with a chosen tangent direction, in degrees."""
    a = math.radians(ang)
    return dict(p=(x, y), d=(math.cos(a), math.sin(a)),
                lin=lin, lout=lin if lout is None else lout)


def corner(x, y, ang_in, ang_out, lin=0.0, lout=0.0):
    ai, ao = math.radians(ang_in), math.radians(ang_out)
    return dict(p=(x, y), d=(math.cos(ao), math.sin(ao)),
                din=(math.cos(ai), math.sin(ai)), lin=lin, lout=lout)


def spline(nodes):
    """Closed outline through nodes, each span one cubic with chosen tangents.

    Nothing is fitted - the handles are set from the tangent directions and
    lengths given, so each span is smooth because of how it is specified.
    """
    segs = []
    n = len(nodes)
    for i in range(n):
        a, b = nodes[i], nodes[(i + 1) % n]
        p0, p3 = a['p'], b['p']
        da = a['d']
        db = b.get('din', b['d'])
        if a['lout'] == 0 and b['lin'] == 0:
            segs.append(('L', p3))
            continue
        p1 = (p0[0] + da[0] * a['lout'], p0[1] + da[1] * a['lout'])
        p2 = (p3[0] - db[0] * b['lin'], p3[1] - db[1] * b['lin'])
        segs.append(('C', p1, p2, p3))
    return (nodes[0]['p'], segs)


def glyph_O2(cap=CAP, rx=0.410, ry=0.500, facet=4.0, run=0.22,
             cx_i=0.101, cy_i=0.350, waist=0.081, lobe=0.145,
             h_top=0.55, h_flank=0.50):
    """The reference O, constructed: faceted flanks and a waisted counter.

    Two features carry this letter and a plain ellipse has neither.  Each flank
    runs dead straight for a stretch and meets its opposite number in a shallow
    vertex; the counter pinches at half height.  Both are drawn on purpose - the
    facet is a real straight line between two tangent points, and the waist is a
    pair of vertical-tangent nodes with the curve between them an S.
    """
    RX, RY, cy = rx * cap, ry * cap, cap / 2
    t = math.radians(facet)
    dx, dy = math.sin(t) * run * RY, math.cos(t) * run * RY
    ht, hf = RX * h_top, RY * h_flank
    outer = [node(0, cy + RY, 0, ht),
             node(RX - dx, cy + dy, facet - 90, hf, 0),
             node(RX, cy, facet - 90, 0, 0),
             node(RX - dx, cy - dy, -90 - facet, 0, hf),
             node(0, cy - RY, 180, ht),
             node(-RX + dx, cy - dy, 90 + facet, hf, 0),
             node(-RX, cy, 90 + facet, 0, 0),
             node(-RX + dx, cy + dy, 90 - facet, 0, hf)]
    rxi, ryi = cx_i * cap, cy_i * cap
    w, lo = waist * cap, lobe * cap
    ha, hb, hc = rxi * 0.58, (ryi - lo) * 0.55, lo * 0.62
    # wound the opposite way to the outer, so the fill knocks it out
    inner = [node(0, cy + ryi, 180, ha),
             node(-rxi, cy + lo, -90, hb, hc),
             node(-w, cy, -90, hc, hc),
             node(-rxi, cy - lo, -90, hc, hb),
             node(0, cy - ryi, 0, ha),
             node(rxi, cy - lo, 90, hb, hc),
             node(w, cy, 90, hc, hc),
             node(rxi, cy + lo, 90, hc, hb)]
    return [spline(outer), spline(inner)]


# -------------------------------------------------------------- western serifs


def serif_run(cx, H, T, at_top, cap, rtl=False, spur=0.26, dip=0.17,
              hump=0.76, soft=0.55, cove_h=0.70):
    """A western serif's outer edge, as a run of nodes in traversal order.

    Not a straight slab.  The tip turns up into a spur, and between the tips the
    edge rides over a hump, dips in the middle and rises again.  That wave, and
    the long cove into the stem that the caller joins on, are what make the face
    read as wood type rather than a modern slab.
    """
    sp, dp, hx = spur * T, dip * T, hump * H
    y = (lambda v: cap - v) if at_top else (lambda v: v)
    h1, h2 = (H - hx) * soft, hx * soft
    ch = T * cove_h
    sgn = -1 if at_top else 1
    a_mid = 180.0 if rtl else 0.0
    a_up, a_dn = (90.0, -90.0) if not at_top else (-90.0, 90.0)
    xs = [cx - H, cx - hx, cx, cx + hx, cx + H]
    ys = [y(sp), y(0), y(dp), y(0), y(sp)]
    ns = [corner(xs[0], ys[0], a_dn, 0.0, ch, h1),
          node(xs[1], ys[1], 0.0, h1, h2),
          node(xs[2], ys[2], 0.0, h2, h2),
          node(xs[3], ys[3], 0.0, h2, h1),
          corner(xs[4], ys[4], 0.0, a_up, h1, ch)]
    if not rtl:
        return ns
    out = []
    for n in reversed(ns):
        d = dict(n)
        ai = math.degrees(math.atan2(n['d'][1], n['d'][0])) + 180.0
        ao = math.degrees(math.atan2(*reversed(n.get('din', n['d'])))) + 180.0
        d['d'] = (math.cos(math.radians(ao)), math.sin(math.radians(ao)))
        d['din'] = (math.cos(math.radians(ai)), math.sin(math.radians(ai)))
        d['lin'], d['lout'] = n['lout'], n['lin']
        out.append(d)
    return out


def _cove_stem(x, y, up, lin):
    """The stem end of a cove: vertical tangent, handle pointing down the sweep."""
    a = 90.0 if up else -90.0
    return dict(p=(x, y), d=(math.cos(math.radians(a)), math.sin(math.radians(a))),
                lin=lin, lout=0.0)


def glyph_M_west(cap=CAP, width=0.947, stem=0.195, over=0.080, slab=0.112,
                 br=0.045, ya=0.48, yb=0.48, pix=0.010, piy=0.63,
                 apex=0.17, spur=0.10, dip=0.05, cove_x=0.30):
    """M in the western / French Clarendon manner of the reference: big spurred
    serifs with a waved edge, long concave coves into the stems, and a V heavy on
    the left stroke and light on the right."""
    W, S, V, T = width * cap, stem * cap, over * cap, slab * cap
    BR = br * cap
    xl, xr = V + S / 2, W - V - S / 2
    H, mid = S / 2 + V, W / 2
    kw = dict(spur=spur, dip=dip)
    cl = (H - S / 2) * cove_x
    ns = []
    ns += serif_run(xl, H, T, False, cap, **kw)
    ns.append(_cove_stem(xl + S / 2, T + BR, True, cl))
    ns.append(corner(xl + S / 2, ya * cap, 90.0,
                     math.degrees(math.atan2(apex * cap - ya * cap,
                                             mid - xl - S / 2)), 0, 0))
    ns.append(corner(mid, apex * cap, 0.0, 0.0, 0, 0))
    ns.append(corner(xr - S / 2, yb * cap, 0.0, -90.0, 0, 0))
    ns.append(_cove_stem(xr - S / 2, T + BR, False, 0.0))
    ns[-1]['lout'] = cl
    ns += serif_run(xr, H, T, False, cap, **kw)
    ns.append(_cove_stem(xr + S / 2, T + BR, True, cl))
    ns.append(_cove_stem(xr + S / 2, cap - T - BR, True, 0.0))
    ns[-1]['lout'] = cl
    ns += serif_run(xr, H, T, True, cap, rtl=True, **kw)
    ns.append(_cove_stem(xr - S / 2, cap - T - BR, False, cl))
    ns.append(dict(p=(mid + pix * cap, piy * cap),
                   d=(0.0, 1.0), din=(0.0, -1.0), lin=0.0, lout=0.0))
    ns.append(_cove_stem(xl + S / 2, cap - T - BR, True, 0.0))
    ns[-1]['lout'] = cl
    ns += serif_run(xl, H, T, True, cap, rtl=True, **kw)
    ns.append(_cove_stem(xl - S / 2, cap - T - BR, False, cl))
    ns.append(_cove_stem(xl - S / 2, T + BR, False, 0.0))
    ns[-1]['lout'] = cl
    return [spline(ns)]
