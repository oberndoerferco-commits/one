"""How straight are the edges that are meant to be straight, and how smooth are
the curves? Splits each outline at its corners, then for every long run reports
the deviation from its own best-fit line (or circle, if it is clearly a curve)."""
import sys, numpy as np, math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
class P(BasePen):
    def __init__(s,gs): super().__init__(gs); s.c=[]
    def _moveTo(s,p): s.cur=[p]; s.c.append(s.cur)
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for i in range(1,33):
            t=i/32;u=1-t
            s.cur.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0],u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for i in range(1,33):
            t=i/32;u=1-t
            s.cur.append((u*u*p0[0]+2*u*t*a[0]+t*t*b[0],u*u*p0[1]+2*u*t*a[1]+t*t*b[1]))
    def _closePath(s): pass
    def _endPath(s): pass
def fit_line(q):
    c=q.mean(0); u,s,vt=np.linalg.svd(q-c,full_matrices=False); d=vt[0]
    return float(np.abs((q-c)@np.array([-d[1],d[0]])).max())
def fit_circle(q):
    x,y=q[:,0],q[:,1]; A=np.c_[x,y,np.ones(len(q))]; b=x*x+y*y
    try: sol,*_=np.linalg.lstsq(A,b,rcond=None)
    except Exception: return 1e9
    cx,cy=sol[0]/2,sol[1]/2; r2=sol[2]+cx*cx+cy*cy
    if r2<=1: return 1e9
    r=math.sqrt(r2); d=np.hypot(x-cx,y-cy)
    return float(np.abs(d-r).max())
def measure(ttf, R=7, corner_deg=122.0, min_len=90.0):
    f=TTFont(ttf); gs=f.getGlyphSet(); cm=f.getBestCmap()
    lines=[]; curves=[]
    for ch in 'OBERNDÖF':
        gn=cm.get(ord(ch)) or 'Odieresis'
        p=P(gs); gs[gn].draw(p)
        for q in p.c:
            q=np.array(q)
            d=np.r_[0,np.cumsum(np.hypot(*np.diff(np.vstack([q,q[:1]]),axis=0).T))]
            L=d[-1]
            if L<120: continue
            n=max(40,int(L/2)); t=np.linspace(0,L,n,endpoint=False)
            qq=np.c_[np.interp(t,d,np.r_[q[:,0],q[0,0]]), np.interp(t,d,np.r_[q[:,1],q[0,1]])]
            a=np.roll(qq,R,axis=0)-qq; b=np.roll(qq,-R,axis=0)-qq
            ca=(a*b).sum(1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)+1e-9)
            ang=np.degrees(np.arccos(np.clip(ca,-1,1)))
            sharp=ang<corner_deg
            idx=[i for i in range(len(qq)) if sharp[i]]
            brk=[]
            for i in idx:
                if not brk or (i-brk[-1])>R: brk.append(i)
            if not brk: brk=[0]
            for s0,s1 in zip(brk, brk[1:]+[brk[0]+len(qq)]):
                run=[m%len(qq) for m in range(s0,s1+1)]
                if len(run)<20: continue
                seg=qq[run]
                if np.hypot(*(seg[-1]-seg[0]))<min_len: continue
                le=fit_line(seg); ce=fit_circle(seg)
                # a run is "meant to be straight" if a line already nearly fits it,
                # "meant to be an arc" if a circle nearly fits but a line does not.
                if le<=12.0: lines.append(le)
                elif ce<=12.0: curves.append(ce)
    return lines, curves
if __name__=='__main__':
    for t in sys.argv[1:]:
        li,cu=measure(t)
        print('%-26s straight runs %2d  wobble mean %5.2f max %5.2f   |   curved runs %2d  ripple mean %5.2f max %5.2f'
              %(t.split('/')[-1], len(li), np.mean(li) if li else 0, max(li) if li else 0,
                len(cu), np.mean(cu) if cu else 0, max(cu) if cu else 0))
