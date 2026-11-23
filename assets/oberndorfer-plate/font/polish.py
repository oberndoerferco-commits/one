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
