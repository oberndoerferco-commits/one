"""List the sharpest corners in a font: angle over a +-9 unit span, 180 = flat."""
import sys, numpy as np, math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
class P(BasePen):
    def __init__(s,gs): super().__init__(gs); s.c=[]
    def _moveTo(s,p): s.cur=[p]; s.c.append(s.cur)
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for i in range(1,25):
            t=i/24;u=1-t
            s.cur.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0],u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for i in range(1,25):
            t=i/24;u=1-t
            s.cur.append((u*u*p0[0]+2*u*t*a[0]+t*t*b[0],u*u*p0[1]+2*u*t*a[1]+t*t*b[1]))
    def _closePath(s): pass
    def _endPath(s): pass
def inside(pt,poly):
    x,y=pt; n=len(poly); c=False; j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi): c=not c
        j=i
    return c
def area(p):
    p=np.asarray(p); return 0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
def corners(ttf, R=9.0):
    f=TTFont(ttf); gs=f.getGlyphSet(); cm=f.getBestCmap(); out=[]
    for ch in 'OBERNDÖF':
        gn=cm.get(ord(ch)) or 'Odieresis'
        p=P(gs); gs[gn].draw(p); cs=[np.array(q) for q in p.c]
        for k,q in enumerate(cs):
            d=np.r_[0,np.cumsum(np.hypot(*np.diff(np.vstack([q,q[:1]]),axis=0).T))]
            L=d[-1]
            if L<40: continue
            n=max(24,int(L/2)); t=np.linspace(0,L,n,endpoint=False)
            qq=np.c_[np.interp(t,d,np.r_[q[:,0],q[0,0]]), np.interp(t,d,np.r_[q[:,1],q[0,1]])]
            st=max(1,int(round(R/2)))
            a=np.roll(qq,st,axis=0)-qq; b=np.roll(qq,-st,axis=0)-qq
            ca=(a*b).sum(1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)+1e-9)
            ang=np.degrees(np.arccos(np.clip(ca,-1,1)))
            depth=sum(1 for j,o in enumerate(cs) if j!=k and abs(area(o))>abs(area(q)) and inside(tuple(q[0]),o))
            mat=(depth%2==0)
            for i in np.argsort(ang)[:40]:
                if ang[i]>95: continue
                w=(a[i]/np.linalg.norm(a[i]))+(b[i]/np.linalg.norm(b[i])); nw=np.linalg.norm(w)
                if nw<1e-6: continue
                o=inside(tuple(qq[i]+w/nw*5.0), q)==mat
                out.append((float(ang[i]),ch,float(qq[i][0]),float(qq[i][1]),o))
    out.sort(); keep=[]
    for c in out:
        if all(c[1]!=k[1] or math.hypot(c[2]-k[2],c[3]-k[3])>40 for k in keep): keep.append(c)
    return keep
if __name__=='__main__':
    for ttf in sys.argv[1:]:
        k=corners(ttf)
        sharp=[c for c in k if c[0]<60]
        print('%-18s sharpest %.1f deg   corners under 60 deg: %2d   under 30: %2d   under 15: %d'
              %(ttf.split('/')[-1], k[0][0], len(sharp), len([c for c in k if c[0]<30]), len([c for c in k if c[0]<15])))
