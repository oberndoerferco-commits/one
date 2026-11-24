"""Edge polish: kill the lumps, flatten what should be flat, keep real corners."""
import numpy as np, math

def resample(p, step=2.0):
    q=np.vstack([p,p[:1]])
    d=np.r_[0.0,np.cumsum(np.hypot(*np.diff(q,axis=0).T))]
    L=d[-1]
    if L<8: return p
    n=max(24,int(round(L/step)))
    t=np.linspace(0,L,n,endpoint=False)
    return np.c_[np.interp(t,d,q[:,0]), np.interp(t,d,q[:,1])]

def _span_angle(p,R):
    a=np.roll(p,R,axis=0)-p; b=np.roll(p,-R,axis=0)-p
    ca=(a*b).sum(1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)+1e-9)
    return np.degrees(np.arccos(np.clip(ca,-1,1)))      # 180 = dead straight

def _blur(v,k):
    n=len(v); w=np.ones(k)/k
    return np.convolve(np.r_[v,v,v],w,'same')[n:2*n]

def smooth(p, step=2.0, win=11, passes=5, corner_deg=122.0, R=7):
    """Moving-average the outline, but lock the genuine corners in place."""
    p=resample(p,step)
    if len(p)<30: return p
    lock=_span_angle(p,R) < corner_deg
    lock=np.convolve(np.r_[lock,lock,lock].astype(float),np.ones(5),'same')[len(p):2*len(p)]>0
    q=p.copy()
    for _ in range(passes):
        s=np.c_[_blur(q[:,0],win), _blur(q[:,1],win)]
        q=np.where(lock[:,None], q, s)
    return q

def flatten(p, ang_tol=7.0, min_span=34.0, R=4):
    """Any long run that is nearly horizontal/vertical becomes exactly flat."""
    n=len(p)
    if n<30: return p
    d=np.roll(p,-R,axis=0)-np.roll(p,R,axis=0)
    th=np.degrees(np.arctan2(d[:,1],d[:,0]))%180.0
    q=p.copy()
    for axis,target in ((1,0.0),(0,90.0)):          # horizontal runs -> level y; vertical -> level x
        near=np.minimum(np.abs(th-target),180-np.abs(th-target))<ang_tol
        i=0
        while i<n:
            if not near[i]: i+=1; continue
            j=i
            while j<2*n and near[j%n]: j+=1
            idx=[m%n for m in range(i,j)]
            seg=p[idx]
            span=seg[:,1-axis].max()-seg[:,1-axis].min()
            if span>=min_span:
                lvl=np.median(seg[:,axis])
                w=np.ones(len(idx)); e=max(2,len(idx)//6)
                w[:e]=np.linspace(0,1,e); w[-e:]=np.linspace(1,0,e)   # ease at the ends
                q[idx,axis]=seg[:,axis]*(1-w)+lvl*w
            if j>=2*n: break
            i=j
    return q

# ---- terminals: a blunt nick at a tip becomes a true point --------------
def _ends(start, segs):
    pts=[start]; 
    for s in segs: pts.append(s[-1])
    return pts

def sharpen(start, segs, max_nick=30.0, min_arm=55.0, max_reach=130.0, min_ang=12.0):
    """Short edge bridging two converging long edges -> one sharp corner."""
    import numpy as np
    n=len(segs)
    pts=_ends(start,segs)[:-1]                       # node i starts segs[i]
    def seg_len(i): 
        a=np.array(pts[i]); b=np.array(pts[(i+1)%n]); return float(np.hypot(*(b-a)))
    def tang_out(i):      # direction leaving node i along segs[i]
        s=segs[i]; a=np.array(pts[i])
        b=np.array(s[1] if s[0]=='C' else s[1])
        v=b-a; 
        if np.hypot(*v)<1e-6: v=np.array(s[-1])-a
        return v/ (np.hypot(*v)+1e-9)
    def tang_in(i):       # direction arriving at node i+1 along segs[i]
        s=segs[i]; e=np.array(s[-1])
        b=np.array(s[2] if s[0]=='C' else pts[i])
        v=e-b
        if np.hypot(*v)<1e-6: v=e-np.array(pts[i])
        return v/(np.hypot(*v)+1e-9)
    kill={}
    for i in range(n):
        if segs[i][0]!='L' or seg_len(i)>max_nick: continue
        p=(i-1)%n; q=(i+1)%n
        if seg_len(p)<min_arm or seg_len(q)<min_arm: continue
        A=np.array(pts[i]); dA=tang_in(p)            # arriving edge direction
        B=np.array(pts[q]); dB=tang_out(q)           # leaving edge direction
        cr=dA[0]*dB[1]-dA[1]*dB[0]
        ang=abs(math.degrees(math.asin(max(-1,min(1,cr)))))
        if abs(cr)<1e-6 or ang<min_ang: continue
        t=((B-A)[0]*dB[1]-(B-A)[1]*dB[0])/cr
        X=A+dA*t
        if np.hypot(*(X-A))>max_reach or np.hypot(*(X-B))>max_reach: continue
        kill[i]=tuple(X)
    if not kill: return start,segs
    newpts=list(pts); drop=set()
    for i,X in kill.items():
        newpts[i]=X; drop.add((i+1)%n)
    out=[]; st=None
    for i in range(n):
        if i in drop: continue
        a=newpts[i]; j=(i+1)%n
        while j in drop: j=(j+1)%n
        b=newpts[j]
        s=segs[i]
        if st is None: st=a
        if s[0]=='L' or (i+1)%n in drop: out.append(('L',b))
        else:
            # shift the控 control points with the endpoints
            d0=np.array(a)-np.array(pts[i]); d1=np.array(b)-np.array(pts[(i+1)%n])
            c1=tuple(np.array(s[1])+d0*0.5); c2=tuple(np.array(s[2])+d1*0.5)
            out.append(('C',c1,c2,b))
    return st,out

# ---- fillet: every sharp OUTWARD tip gets the same corner radius --------
def fillet(start, segs, inside_fn, radius=18.0, radius_in=None, max_cut=62.0,
           max_frac=0.40, max_wedge=108.0, k=0.56):
    """Round sharp corners. Outward spikes get `radius`; inward notches get
    `radius_in` (default 55% of it) so an ink trap stays tighter than a tip but
    does not read as a crack. The convexity probe walks a quarter of the shorter
    arm along the bisector — a fixed 6-unit probe lands outside a needle and the
    corner was then skipped, which is how the D's 2.9 degree spike survived."""
    if radius_in is None: radius_in=radius*0.55
    n=len(segs)
    nodes=[start]+[segs[i][-1] for i in range(n-1)]
    P=lambda i: np.array(nodes[i],float)
    def armA(i):
        s=segs[(i-1)%n]
        q=np.array(s[2] if s[0]=='C' else nodes[(i-1)%n],float); v=q-P(i)
        return (np.array(nodes[(i-1)%n],float)-P(i)) if np.hypot(*v)<1e-6 else v
    def armB(i):
        s=segs[i]; q=np.array(s[1],float); v=q-P(i)
        return (np.array(s[-1],float)-P(i)) if np.hypot(*v)<1e-6 else v
    def slen(i): return float(np.hypot(*(np.array(segs[i][-1],float)-P(i))))
    cuts={}
    for i in range(n):
        A=armA(i); B=armB(i); la=np.hypot(*A); lb=np.hypot(*B)
        if la<1e-6 or lb<1e-6: continue
        Ah=A/la; Bh=B/lb
        th=math.degrees(math.acos(float(np.clip(Ah@Bh,-1,1))))
        if th>max_wedge: continue
        w=Ah+Bh; nw=np.hypot(*w)
        if nw<1e-9: continue
        probe=min(60.0, max(2.0, 0.25*min(la,lb)))
        outward = inside_fn(P(i)+w/nw*probe)
        r = radius if outward else radius_in
        if r<=0: continue
        d=min(r/max(math.tan(math.radians(th/2)),1e-3), max_cut,
              max_frac*min(slen((i-1)%n), slen(i)))
        if d<2.0: continue
        cuts[i]=(tuple(P(i)+Ah*d), tuple(P(i)+Bh*d))
    if not cuts: return start,segs
    out=[]; first=None
    for i in range(n):
        j=(i+1)%n
        if i in cuts:
            p1,p2=cuts[i]; V=P(i)
            c1=tuple(np.array(p1)+(V-np.array(p1))*k); c2=tuple(np.array(p2)+(V-np.array(p2))*k)
            if first is None: first=p1
            else: out.append(('L',p1))
            out.append(('C',c1,c2,p2))
            a=p2
        else:
            a=nodes[i]
            if first is None: first=a
        b=cuts[j][0] if j in cuts else nodes[j]
        s=segs[i]
        if s[0]=='L': out.append(('L',b))
        else:
            d0=np.array(a,float)-P(i); d1=np.array(b,float)-np.array(segs[i][-1],float)
            out.append(('C',tuple(np.array(s[1],float)+d0*0.6),
                            tuple(np.array(s[2],float)+d1*0.6), b))
    return first,out

# ---- geometrize: long edges become a TRUE line or a TRUE circular arc ----
def _runs(p, corner_deg, R):
    n=len(p); sharp=_span_angle(p,R)<corner_deg
    idx=[i for i in range(n) if sharp[i]]
    if not idx: return [list(range(n))+[0]]
    # collapse neighbouring corner samples to one break each
    brk=[]; 
    for i in idx:
        if not brk or (i-brk[-1])>R: brk.append(i)
    out=[]
    for a,b in zip(brk, brk[1:]+[brk[0]+n]):
        out.append([m%n for m in range(a,b+1)])
    return out

def _fit_line(q):
    c=q.mean(0); u,s,vt=np.linalg.svd(q-c, full_matrices=False)
    d=vt[0]; t=(q-c)@d
    proj=c+np.outer(t,d)
    return proj, float(np.abs((q-c)@np.array([-d[1],d[0]])).max())

def _fit_circle(q):
    x,y=q[:,0],q[:,1]
    A=np.c_[x,y,np.ones(len(q))]
    b=x*x+y*y
    try: sol,*_=np.linalg.lstsq(A,b,rcond=None)
    except np.linalg.LinAlgError: return None,1e9
    cx,cy=sol[0]/2,sol[1]/2
    r2=sol[2]+cx*cx+cy*cy
    if r2<=1.0: return None,1e9
    r=math.sqrt(r2)
    v=q-np.array([cx,cy]); d=np.hypot(v[:,0],v[:,1])
    proj=np.array([cx,cy])+v/ d[:,None]*r
    return proj, float(np.abs(d-r).max())

def geometrize(p, corner_deg=122.0, R=7, min_pts=22, tol_line=5.0, tol_circle=7.0,
               max_r=5000.0, ease=0.06):
    """Snap each smooth run between corners onto its best-fit line or circle."""
    if len(p)<40: return p
    q=p.copy()
    for run in _runs(p, corner_deg, R):
        if len(run)<min_pts: continue
        seg=p[run]
        lp,le=_fit_line(seg)
        cp,ce=_fit_circle(seg)
        if le<=tol_line: tgt=lp
        elif cp is not None and ce<=tol_circle and np.hypot(*(cp[0]-cp[-1]))<max_r*2: tgt=cp
        else: continue
        m=len(run); w=np.ones(m); e=max(2,int(m*ease))
        w[:e]=np.linspace(0,1,e); w[-e:]=np.linspace(1,0,e)   # ease into the corners
        q[run]=seg*(1-w[:,None])+tgt*w[:,None]
    return q
