"""Build the font with real curves: straight runs stay straight, round runs
are true beziers (converted to TrueType quadratics)."""
import numpy as np, math, sys, os
sys.path.insert(0,'/home/user/one/scripts')
# numpy 2 dropped 2-D cross; the repo's tracer still calls it
_oc=np.cross
def _cross(a,b,*r,**k):
    a=np.asarray(a); b=np.asarray(b)
    if a.shape[-1]==2 and b.shape[-1]==2: return a[...,0]*b[...,1]-a[...,1]*b[...,0]
    return _oc(a,b,*r,**k)
np.cross=_cross
from skimage import measure
import vectorize_lineart as vl
from polish import smooth, flatten, sharpen, fillet
from regularise import regularise
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

UPM=1000; CAP=700; SB=40; PAD=3
RAD=float(__import__('os').environ.get('RAD','18'))
sp=list(np.load('sprites.npy', allow_pickle=True))
NAME='OBERNDÖRFER'
for s in sp: s['baseoff']=s['base']-s['y0']
canon={}
for ch in set(NAME):
    inst=[s for s in sp if s['ch']==ch]
    canon[ch]=inst[int(np.argsort([i['w'] for i in inst])[len(inst)//2])]

def contours_for(mask):
    mp=np.pad(mask,PAD,constant_values=False)
    out=[]
    for c in measure.find_contours(mp.astype(float),0.5):
        p=c[:, ::-1]-PAD
        if np.allclose(p[0],p[-1]): p=p[:-1]
        if len(p)<6: continue
        # small shapes (the umlaut dots) keep every corner: no node merging
        bb=max(p[:,0].max()-p[:,0].min(), p[:,1].max()-p[:,1].min())
        if bb < 180:
            fitted=vl.fit_contour(p, line_tol=1.6, curve_tol=0.9, smooth_deg=55.0)
        else:
            p=smooth(p)                       # lumps off the edges, corners locked
            p=flatten(p)                      # feet / flat tops become dead level
            fitted=vl.fit_contour(p, line_tol=2.6, curve_tol=2.0, smooth_deg=26.0)
            fitted=regularise(fitted, corner_deg=30.0, straight_tol=3.0, fit_tol=3.0)
        out.append(fitted)
    return out

def area_of(pts):
    p=np.asarray(pts)
    return 0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
def poly_of(start,segs,n=24):
    pts=[start]
    for s in segs:
        if s[0]=='L': pts.append(s[1])
        else:
            a,b,c=s[1],s[2],s[3]; p0=pts[-1]
            for i in range(1,n+1):
                t=i/n; u=1-t
                pts.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0],
                            u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    return np.array(pts)
def inside(pt,poly):
    x,y=pt; n=len(poly); c=False; j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi): c=not c
        j=i
    return c

glyphs={}; widths={}
for ch,s in canon.items():
    cs=contours_for(s['mask'])
    cappx=s['base']-s['top']; k=CAP/float(cappx); base=s['baseoff']
    T=lambda p:(p[0]*k+SB, (base-p[1])*k)
    tc=[]
    for start,segs in cs:
        ns=[]
        for sg in segs:
            ns.append(('L',T(sg[1])) if sg[0]=='L' else ('C',T(sg[1]),T(sg[2]),T(sg[3])))
        st,ns=sharpen(T(start),ns)
        tc.append((st,ns))
    polys=[poly_of(st,sg) for st,sg in tc]
    # round every sharp outward tip by the same radius; ink traps stay sharp
    ftc=[]
    for i,(st,sg) in enumerate(tc):
        depth=sum(1 for j,q in enumerate(polys)
                  if j!=i and abs(area_of(q))>abs(area_of(polys[i])) and inside(polys[i][0],q))
        mat = (depth%2==0)
        poly=polys[i]
        ftc.append(fillet(st,sg, lambda pt,poly=poly,mat=mat: inside(tuple(pt),poly)==mat,
                          radius=RAD))
    tc=ftc
    polys=[poly_of(st,sg) for st,sg in tc]
    fixed=[]
    for i,(st,sg) in enumerate(tc):
        depth=sum(1 for j,q in enumerate(polys)
                  if j!=i and abs(area_of(q))>abs(area_of(polys[i])) and inside(polys[i][0],q))
        ccw = area_of(polys[i])>0
        fixed.append((st,sg, ccw==(depth%2==1)))
    glyphs[ch]=fixed
    widths[ch]=int(round(s['w']*k))+2*SB
    ncur=sum(1 for st,sg,_ in fixed for x in sg if x[0]=='C')
    nlin=sum(1 for st,sg,_ in fixed for x in sg if x[0]=='L')
    print('%s contours %d  curves %3d  lines %3d  advance %d'%(ch,len(fixed),ncur,nlin,widths[ch]))

order=['.notdef']+list(dict.fromkeys(NAME))
fb=FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(order)
fb.setupCharacterMap({ord(c):c for c in dict.fromkeys(NAME)})
pens={'.notdef':TTGlyphPen(None).glyph()}
for ch,cs in glyphs.items():
    tt=TTGlyphPen(None); pen=Cu2QuPen(tt, max_err=1.0)
    for start,segs,ok in cs:
        seq=[('M',start)]+segs
        if not ok:   # reverse to get the right winding
            pts=poly_of(start,segs,n=24)[::-1]
            pen.moveTo(tuple(pts[0]))
            for q in pts[1:]: pen.lineTo(tuple(q))
            pen.closePath(); continue
        pen.moveTo(tuple(start))
        for sg in segs:
            if sg[0]=='L': pen.lineTo(tuple(sg[1]))
            else: pen.curveTo(tuple(sg[1]),tuple(sg[2]),tuple(sg[3]))
        pen.closePath()
    pens[ch]=tt.glyph()
fb.setupGlyf(pens)
fb.setupHorizontalMetrics({g:(widths.get(g,600),0) for g in order})
fb.setupHorizontalHeader(ascent=820, descent=-180)
fb.setupNameTable(dict(familyName="Oberndorfer Drawn", styleName="Regular",
                       psName="OberndorferDrawn-Regular", version="3.0"))
fb.setupOS2(sTypoAscender=820, sTypoDescender=-180, usWinAscent=900, usWinDescent=220, sCapHeight=CAP)
fb.setupPost()
fb.save('OberndorferDrawn-Regular.ttf')
print('wrote font v3')
