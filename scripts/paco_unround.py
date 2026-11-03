"""Replace sub-visible corner fillets with true corners before offsetting.

Offsetting adds the offset to every existing radius: a 0.055 mm fillet,
invisible at 50 mm, comes back as 0.455 mm after a 0.40 mm outset. So any
fillet too small to see is squared off first, by intersecting the two
straight edges that bound it. Real curves are left alone: a fillet only
counts when both neighbouring segments are long and straight.
"""
import numpy as np

def _inter(p0, p1, q0, q1):
    d1, d2 = p1 - p0, q1 - q0
    den = d1[0]*d2[1] - d1[1]*d2[0]
    if abs(den) < 1e-12:
        return None
    t = ((q0[0]-p0[0])*d2[1] - (q0[1]-p0[1])*d2[0]) / den
    return p0 + t*d1


def unround(ring, max_fillet=0.14, min_edge=0.35, max_shift=0.30):
    """ring: Nx2 array (closed or not). Returns a new ring."""
    p = np.asarray(ring, float)
    if len(p) > 2 and np.allclose(p[0], p[-1]):
        p = p[:-1]
    n = len(p)
    if n < 5:
        return ring
    seg = np.roll(p, -1, 0) - p
    ln = np.hypot(seg[:, 0], seg[:, 1])
    long_ = ln > min_edge
    if not long_.any():
        return ring
    keep = np.ones(n, bool)
    new = {}
    idx = np.nonzero(long_)[0]
    for a, b in zip(idx, np.roll(idx, -1)):
        # vertices strictly between the end of edge a and the start of edge b
        run = []
        i = (a + 1) % n
        while i != (b + 1) % n and len(run) < 12:
            run.append(i); i = (i + 1) % n
        run = run[:-1] if run and run[-1] == b else run
        if not run or len(run) > 10:
            continue
        span = sum(ln[j] for j in [a_ for a_ in run])
        if span > max_fillet:
            continue
        x = _inter(p[a], p[(a+1) % n], p[b], p[(b+1) % n])
        if x is None:
            continue
        if np.hypot(*(x - p[run[0]])) > max_shift:
            continue
        for j in run:
            keep[j] = False
        new[run[0]] = x
    out = []
    for i in range(n):
        if i in new:
            out.append(new[i])
        elif keep[i]:
            out.append(p[i])
    out = np.array(out)
    return out if len(out) >= 3 else ring
