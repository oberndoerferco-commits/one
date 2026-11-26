"""Take the wobble out of a traced outline without redrawing it.

His artwork is hand-made, so an edge that should be one curve weaves by a
pixel or two along the way -- the lumps he keeps pointing at on the O's bowl.
Refitting the outline into straight lines and circular arcs removes them, but
it also decides what the letter ought to be: measured against his drawing that
moved the O by 4.6% of its area, and he could see it immediately.

This does the opposite. The outline stays his, point for point; only the
high-frequency part of it is filtered out. The path is walked by arc length,
the places where it genuinely turns a corner are found and pinned, and between
them the coordinates are low-passed with a Gaussian. A corner stays a corner,
a curve stays the curve he drew, and the weave in the middle goes. At sigma 26
on a 1030 px cap the letter keeps 99.9% of its area and matches his outline at
IoU 0.987 -- a thirtieth of what the refit moved.

The correction is ramped to zero over `taper` sigmas on each side of a pinned
corner, or the filter rounds the very corners it was told to keep.
"""
import numpy as np

def resample(p, step):
    cl=np.vstack([p,p[:1]])
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(cl,axis=0).T))]
    L=d[-1]
    if L<4*step: return p
    n=max(8,int(round(L/step)))
    t=np.linspace(0,L,n,endpoint=False)
    return np.c_[np.interp(t,d,cl[:,0]), np.interp(t,d,cl[:,1])]

def corners(p, k, deg):
    """vertices where the path turns more than `deg` across +-k steps"""
    n=len(p)
    a=p[np.arange(n)-k]; b=p[(np.arange(n)+k)%n]
    v1=p-a; v2=b-p
    c=(v1[:,0]*v2[:,0]+v1[:,1]*v2[:,1])
    s=(v1[:,0]*v2[:,1]-v1[:,1]*v2[:,0])
    ang=np.abs(np.degrees(np.arctan2(s,c)))
    hit=ang>deg
    # keep only the local maximum of each run of flagged vertices
    out=np.zeros(n,bool); i=0
    idx=np.where(hit)[0]
    if not len(idx): return out
    runs=[]; s0=idx[0]; prev=idx[0]
    for j in idx[1:]:
        if j!=prev+1: runs.append((s0,prev)); s0=j
        prev=j
    runs.append((s0,prev))
    if len(runs)>1 and runs[0][0]==0 and runs[-1][1]==n-1:
        a0,b0=runs[-1]; runs=runs[1:-1]+[(a0,runs[0][1]+n if runs else b0)]
    for a0,b0 in runs:
        seg=[(i%n) for i in range(a0,b0+1)]
        out[seg[int(np.argmax(ang[seg]))]]=True
    return out

def gauss(sig, step):
    r=max(1,int(round(3*sig/step)))
    x=np.arange(-r,r+1)*step
    g=np.exp(-0.5*(x/sig)**2); return g/g.sum()

def smooth_closed(p, sigma=26.0, step=2.0, corner_k=4, corner_deg=38.0, taper=1.5,
                  freeze=26.0):
    """Low-pass the outline along arc length, holding detected corners fixed."""
    q=resample(p, step)
    n=len(q)
    if n<16: return p
    # two scales. The wide window alone misses the ends of a narrow slit:
    # its cap is two ~90 deg corners some 30 px apart, so a +-20 px window
    # spans both and their turns cancel to nothing. A short window with a high
    # threshold catches each one, and wobble never turns 70 deg over 12 px.
    cs=corners(q, corner_k, corner_deg) | corners(q, 3, 70.0)
    g=gauss(sigma, step); r=(len(g)-1)//2
    idx=np.where(cs)[0]
    out=q.copy()
    if len(idx)==0:
        pad=np.vstack([q[-r:],q,q[:r]])
        out=np.c_[np.convolve(pad[:,0],g,'valid'), np.convolve(pad[:,1],g,'valid')]
        return out
    # smooth each span between consecutive corners
    for a0,b0 in zip(idx, np.r_[idx[1:], idx[0]+n]):
        m=b0-a0+1
        if m<6: continue
        seg=q[np.arange(a0,b0+1)%n]
        pad=np.vstack([np.repeat(seg[:1],r,0), seg, np.repeat(seg[-1:],r,0)])
        sm=np.c_[np.convolve(pad[:,0],g,'valid'), np.convolve(pad[:,1],g,'valid')]
        # hold the corner itself, then ramp the correction in. Pinning the
        # single apex is not enough on a needle: the two sides of a wedge sit
        # far apart along the path but close together in space, so the filter
        # still pulls each toward its own neighbourhood and blunts the point.
        # `freeze` px either side stay exactly as traced.
        d=np.minimum(np.arange(m), np.arange(m)[::-1])*step
        w=np.clip((d-freeze)/(taper*sigma),0,1)[:,None]
        out[np.arange(a0,b0+1)%n]=seg+(sm-seg)*w
    return out

def taubin_closed(p, iters=120, lam=0.5, mu=-0.53, step=2.0,
                  corner_k=10, corner_deg=52.0, wide=True, fine=True, d=1,
                  drop_nicks=False, unpin=None):
    """Taubin's lambda/mu filter: a low-pass that does not shrink.

    lam/mu set a fixed cutoff - waves longer than about 2*pi*d/0.3376
    vertices pass through untouched however many times it runs, which is
    exactly why it keeps the letter's size. With the neighbours one step
    away (d=1, step=2px) that cutoff sits at ~37px, so a 100px lump in an
    edge is 'shape' to the filter and survives any number of passes.
    Taking the Laplacian over neighbours d apart scales the cutoff by d
    without thinning the vertices, so corners stay where they are.
    """
    """Low-pass an outline without shrinking it.

    A Gaussian moves every point toward the local average, which on a convex
    curve pulls the whole outline inward by about sigma^2/2R -- at sigma 140 on
    a bowl of radius 500 that is 20 px off every edge, and it ate the O.
    Taubin's pair of passes, one positive and one negative, cancels that drift:
    the same high frequencies go, the shape stays where he drew it.

    Corner vertices are reset to their original position after every pass, so a
    corner stays put and its neighbours relax smoothly up to it instead of
    needing a hand-tuned freeze.
    """
    q=resample(p, step)
    n=len(q)
    if n<16: return p
    # Two detectors, and they disagree on purpose. The wide window (+-20px)
    # reads a wobble bump as a corner and anchors it, so nothing smooths; the
    # narrow one (+-6px) ignores a bump that wide but still fires on a real
    # corner. The wide window exists only because two corners 30px apart - the
    # two sides of a slit tip - cancel inside it. So the pass that has to kill
    # wobble asks for the narrow detector alone.
    anchor=np.zeros(n, bool)
    if wide: anchor = anchor | corners(q, corner_k, corner_deg)
    if fine: anchor = anchor | corners(q, 3, 70.0)
    if drop_nicks:
        anchor &= ~nicks(q, step)
    # Where one of his drawn arcs joins a bowl the seam is a single convex
    # corner with no cancelling partner, so nicks() cannot see it, and every
    # curvature measure scores it ABOVE the corners he wants kept - there is
    # no geometric test that separates the two. Named points it is.
    for ux, uy, ur in (unpin or ()):
        anchor &= np.hypot(q[:, 0]-ux, q[:, 1]-uy) > ur
    d=max(1,int(d))
    if d>1:
        # a wide stencil reaches across a corner, so hold the d vertices
        # either side of one too: that keeps the wedge itself rigid.
        a=anchor.copy()
        for s_ in range(1,d+1): a |= np.roll(anchor,s_) | np.roll(anchor,-s_)
        anchor=a
    orig=q.copy()
    for _ in range(int(iters)):
        for f in (lam, mu):
            lap=0.5*(np.roll(q,d,axis=0)+np.roll(q,-d,axis=0))-q
            q=q+f*lap
            q[anchor]=orig[anchor]
    return q


def nicks(q, step=2.0, gap=90.0, deg=45.0, net=55.0):
    """Mask the corners that are the pen's nicks rather than drawn corners.

    Both kinds are sharp, so no angle threshold tells them apart. The
    pairing does: a nick is a jog - the edge turns one way and straight
    back the other within a few tens of pixels, two corners whose turns
    CANCEL. A terminal or a slit tip is two corners of the same sign that
    add up to the turn round the end. So the cancelling pairs are the
    nicks. They are only unpinned here, never cut: the chord across a jog
    is the jog, and it is the low-pass that has to flatten it.
    """
    n=len(q)
    if n<32: return np.zeros(n, bool)
    k=max(2, int(round(6.0/step)))
    i=np.arange(n)
    a=q[np.roll(i,-k)]-q
    b=q-q[np.roll(i,k)]
    turn=np.degrees(np.arctan2(_cross(b,a), (a*b).sum(1)))
    t=np.abs(turn)
    peak=[j for j in range(n) if t[j]>deg and t[j]>=t[j-1] and t[j]>t[(j+1)%n]]
    span=int(round(gap/step))
    out=np.zeros(n, bool)
    for u in range(len(peak)):
        for v in range(u+1, len(peak)):
            x, y = peak[u], peak[v]
            if y-x > span: break
            if np.sign(turn[x]) == np.sign(turn[y]): continue
            if abs(turn[x]+turn[y]) > net: continue
            out[max(0, x-k):y+k+1]=True
    return out


def _cross(a, b):
    return a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]
