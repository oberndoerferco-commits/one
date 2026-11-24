"""Rebuild an outline out of true primitives.
import sys as _sys; _sys.setrecursionlimit(20000)

Not smoothing. Each piece of the outline becomes either an exact straight
segment or an exact circular arc, fitted to his own points; neighbouring
pieces are then re-intersected so the corner is a mathematical point rather
than a blend. A straight edge is then straight to the last decimal, an arc is
a real circle, and there is nothing in between for wobble to live in.
"""
import numpy as np, math

# ---------- fitting ----------
def _stats(err):
    return float(np.sqrt((err**2).mean())), float(err.max())

def fit_line(q):
    c=q.mean(0); u,s,vt=np.linalg.svd(q-c, full_matrices=False); d=vt[0]
    nrm=np.array([-d[1],d[0]])
    return dict(kind='L', p=c, d=d, n=nrm), _stats(np.abs((q-c)@nrm))

def fit_circle(q):
    x,y=q[:,0],q[:,1]
    A=np.c_[x,y,np.ones(len(q))]; b=x*x+y*y
    try: sol,*_=np.linalg.lstsq(A,b,rcond=None)
    except np.linalg.LinAlgError: return None,(1e9,1e9)
    cx,cy=sol[0]/2.0, sol[1]/2.0
    r2=sol[2]+cx*cx+cy*cy
    if r2<=1.0: return None,(1e9,1e9)
    r=math.sqrt(r2); ctr=np.array([cx,cy])
    if r>6000: return None,(1e9,1e9)               # a circle that big is a line
    d=np.hypot(x-cx,y-cy)
    return dict(kind='A', c=ctr, r=r), _stats(np.abs(d-r))

MAXK=3.0        # a piece may not stray further than MAXK x tol anywhere

def ok(e, tol): return e[0]<=tol and e[1]<=MAXK*tol

def classify(q, tol, line_bias=1.25):
    """Prefer a straight line unless a circle fits clearly better.
    Judged on RMS, with a cap on the worst point so a piece cannot bow away."""
    L,le=fit_line(q)
    C,ce=fit_circle(q)
    lok=ok(le,tol); cok=(C is not None and ok(ce,tol))
    if lok and (not cok or le[0]<=ce[0]*line_bias): return L,le
    if cok: return C,ce
    if C is None: return L,le
    return (L,le) if le[0]<=ce[0]*line_bias else (C,ce)

# ---------- recursive decomposition ----------
def decompose(q, tol=1.6, min_pts=7, depth=0, max_depth=48):
    """Split until every piece is a line or an arc within `tol`.

    Splitting at the worst-fitting point is right, but if that point sits near
    an end the split peels off a handful of points and the recursion walks the
    outline one bite at a time until it runs out of depth and accepts whatever
    is left. So a lopsided split falls back to the midpoint."""
    if len(q)<min_pts*2 or depth>max_depth:
        P,e=classify(q,tol); return [(P,q)]
    P,e=classify(q,tol)
    if ok(e,tol): return [(P,q)]
    if P['kind']=='L': err=np.abs((q-P['p'])@P['n'])
    else: err=np.abs(np.hypot(*(q-P['c']).T)-P['r'])
    i=int(np.argmax(err))
    if i<min_pts or i>len(q)-min_pts:
        i=len(q)//2
    return (decompose(q[:i+1],tol,min_pts,depth+1,max_depth)
            +decompose(q[i:],tol,min_pts,depth+1,max_depth))

def tangent_at(P, pt, forward=True):
    if P['kind']=='L':
        return P['d']
    v=pt-P['c']; t=np.array([-v[1],v[0]])/ (np.hypot(*v)+1e-9)
    return t

def merge(prims, tol=1.6):
    """Join neighbours that are really one primitive. Walks forward, then tries
    the wrap-around pair once, and repeats until nothing more joins."""
    out=list(prims)
    changed=True
    while changed and len(out)>2:
        changed=False
        i=0
        while i < len(out)-1:
            q=np.vstack([out[i][1], out[i+1][1][1:]])
            P,e=classify(q,tol)
            if ok(e,tol):
                out[i]=(P,q); out.pop(i+1); changed=True
            else:
                i+=1
        if len(out)>2:                       # the seam between last and first
            q=np.vstack([out[-1][1], out[0][1][1:]])
            P,e=classify(q,tol)
            if ok(e,tol):
                out[0]=(P,q); out.pop(-1); changed=True
    return out

# ---------- re-intersection ----------
def _line_line(A,B):
    d1,d2=A['d'],B['d']
    den=d1[0]*d2[1]-d1[1]*d2[0]
    if abs(den)<1e-9: return None
    p1,p2=A['p'],B['p']; w=p2-p1
    t=(w[0]*d2[1]-w[1]*d2[0])/den
    return p1+d1*t

def _line_circle(L,C,near):
    f=L['p']-C['c']; d=L['d']
    b=2*f@d; c=f@f-C['r']**2
    disc=b*b-4*c
    if disc<0: return None
    s=math.sqrt(disc)
    cands=[L['p']+d*((-b+s)/2), L['p']+d*((-b-s)/2)]
    return min(cands, key=lambda p: np.hypot(*(p-near)))

def _circle_circle(A,B,near):
    d=np.hypot(*(B['c']-A['c']))
    if d<1e-9 or d>A['r']+B['r'] or d<abs(A['r']-B['r']): return None
    a=(A['r']**2-B['r']**2+d*d)/(2*d)
    h2=A['r']**2-a*a
    if h2<0: return None
    h=math.sqrt(h2)
    m=A['c']+a*(B['c']-A['c'])/d
    perp=np.array([-(B['c']-A['c'])[1],(B['c']-A['c'])[0]])/d
    return min([m+perp*h, m-perp*h], key=lambda p: np.hypot(*(p-near)))

def intersect(A,B,near,max_move=12.0):
    p=None
    if A['kind']=='L' and B['kind']=='L': p=_line_line(A,B)
    elif A['kind']=='L' and B['kind']=='A': p=_line_circle(A,B,near)
    elif A['kind']=='A' and B['kind']=='L': p=_line_circle(B,A,near)
    else: p=_circle_circle(A,B,near)
    if p is None or np.hypot(*(p-near))>max_move: return near
    return p

# ---------- emit ----------
def arc_to_beziers(C, p0, p1, ccw, max_sweep=None):
    ctr,r=C['c'],C['r']
    a0=math.atan2(*(p0-ctr)[::-1]); a1=math.atan2(*(p1-ctr)[::-1])
    sweep=a1-a0
    if ccw:
        while sweep<=0: sweep+=2*math.pi
    else:
        while sweep>=0: sweep-=2*math.pi
    # an endpoint nudged past the arc's own midpoint by the re-intersection must
    # not send the sweep the long way round the circle
    if max_sweep is not None and abs(sweep) > abs(max_sweep)+math.pi/2:
        sweep = sweep - math.copysign(2*math.pi, sweep)
    n=max(1,int(math.ceil(abs(sweep)/(math.pi/2))))
    segs=[]; step=sweep/n
    for i in range(n):
        s=a0+step*i; e=s+step
        ps=ctr+r*np.array([math.cos(s),math.sin(s)])
        pe=ctr+r*np.array([math.cos(e),math.sin(e)])
        k=4.0/3.0*math.tan(step/4.0)
        c1=ps+k*r*np.array([-math.sin(s),math.cos(s)])
        c2=pe-k*r*np.array([-math.sin(e),math.cos(e)])
        segs.append(('C',tuple(c1),tuple(c2),tuple(pe)))
    return segs

def rebuild(points, tol=1.6, merge_tol=1.6):
    """points: closed polyline (N,2). Returns (start, segs) in the repo's format."""
    q=np.asarray(points,float)
    if len(q)<12: return None
    # resample to a uniform ~1.2 px step so fits are not biased by point density
    cl=np.vstack([q,q[:1]])
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(cl,axis=0).T))]
    L=d[-1]
    if L<24: return None
    n=max(24,int(L/1.2))
    t=np.linspace(0,L,n,endpoint=False)
    qq=np.c_[np.interp(t,d,cl[:,0]), np.interp(t,d,cl[:,1])]
    prims=decompose(np.vstack([qq,qq[:1]]), tol=tol)
    prims=merge(prims, tol=merge_tol)
    if len(prims)==1:
        P,src=prims[0]
        if P['kind']!='A': return None            # one straight line is not a shape
        ctr,r=P['c'],P['r']                        # a closed circle: four quarters
        area=0.5*np.sum(qq[:,0]*np.roll(qq[:,1],-1)-np.roll(qq[:,0],-1)*qq[:,1])
        ccw=area>0
        pts=[ctr+r*np.array([math.cos(a),math.sin(a)])
             for a in ([0,math.pi/2,math.pi,3*math.pi/2] if ccw else
                       [0,-math.pi/2,-math.pi,-3*math.pi/2])]
        segs=[]
        for i in range(4):
            segs.extend(arc_to_beziers(P, pts[i], pts[(i+1)%4], ccw))
        return tuple(pts[0]), segs
    if len(prims)<2: return None
    # corner points: intersect each neighbouring pair
    corners=[]
    for i in range(len(prims)):
        A=prims[i][0]; B=prims[(i+1)%len(prims)][0]
        near=prims[i][1][-1]
        corners.append(intersect(A,B,near))
    # winding of the source, for arc direction
    area=0.5*np.sum(qq[:,0]*np.roll(qq[:,1],-1)-np.roll(qq[:,0],-1)*qq[:,1])
    segs=[]; start=tuple(corners[-1])
    for i in range(len(prims)):
        P,src=prims[i]
        p0=np.array(corners[i-1]); p1=np.array(corners[i])
        if P['kind']=='L':
            segs.append(('L',tuple(p1)))
        else:
            mid=src[len(src)//2]
            v0=src[0]-P['c']; vm=mid-P['c']; v1=src[-1]-P['c']
            cross=v0[0]*vm[1]-v0[1]*vm[0]
            a0=math.atan2(v0[1],v0[0]); a1=math.atan2(v1[1],v1[0])
            orig=a1-a0
            if cross>0:
                while orig<=0: orig+=2*math.pi
            else:
                while orig>=0: orig-=2*math.pi
            segs.extend(arc_to_beziers(P,p0,p1, ccw=(cross>0), max_sweep=orig))
    return start, segs
