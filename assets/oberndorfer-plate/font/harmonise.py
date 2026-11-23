"""Make the letters share their parts. One flag, one foot, grafted onto every
letter at its own attachment point, then everything re-traced as one system."""
import numpy as np, math, sys, os
sys.path.insert(0,'/home/user/one/scripts')
_oc=np.cross
def _cross(a,b,*r,**k):
    a=np.asarray(a); b=np.asarray(b)
    if a.shape[-1]==2 and b.shape[-1]==2: return a[...,0]*b[...,1]-a[...,1]*b[...,0]
    return _oc(a,b,*r,**k)
np.cross=_cross
from skimage import measure
from scipy import ndimage as ndi
import vectorize_lineart as vl
from regularise import regularise
from polish import smooth, flatten, sharpen, fillet
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.basePen import BasePen

UPM=1000; CAP=700; RES=2            # pixels per font unit
X0,X1=-60, 900; Y0,Y1=-120, 940     # raster window in font units
LET='OBERNDÖF'
FLAT='BERNDF'                       # letters whose flag springs off a straight stem
ROUNDG='OÖ'                         # letters whose flag springs off the bowl

class Flat(BasePen):
    def __init__(s,gs): super().__init__(gs); s.c=[]
    def _moveTo(s,p): s.cur=[p]; s.c.append(s.cur)
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for i in range(1,21):
            t=i/20; u=1-t
            s.cur.append((u**3*p0[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*c[0],
                          u**3*p0[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for i in range(1,21):
            t=i/20; u=1-t
            s.cur.append((u*u*p0[0]+2*u*t*a[0]+t*t*b[0], u*u*p0[1]+2*u*t*a[1]+t*t*b[1]))
    def _closePath(s): pass
    def _endPath(s): pass

src=TTFont('OberndorferDrawn-Regular.ttf'); gs=src.getGlyphSet(); cm=src.getBestCmap()
W=int((X1-X0)*RES); H=int((Y1-Y0)*RES)

def rasterise(ch):
    p=Flat(gs); gs[cm[ord(ch)]].draw(p)
    cs=[np.array(q) for q in p.c]
    m=np.zeros((H,W),bool)
    for j in range(H):
        y=Y0+(j+0.5)/RES; xs=[]
        for q in cs:
            for i in range(len(q)):
                a=q[i]; b=q[(i+1)%len(q)]
                if (a[1]>y)!=(b[1]>y): xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        xs.sort()
        for i in range(0,len(xs)-1,2):
            ia=int(max(0,(xs[i]-X0)*RES)); ib=int(min(W,(xs[i+1]-X0)*RES))
            if ib>ia: m[j,ia:ib]=True
    return m

def row(m, yunits):
    j=int((yunits-Y0)*RES)
    r=np.nonzero(m[j])[0]
    if not len(r): return None
    # leftmost run
    brk=np.nonzero(np.diff(r)>1)[0]
    end=r[brk[0]] if len(brk) else r[-1]
    return (r[0]/RES+X0, end/RES+X0)

masks={ch:rasterise(ch) for ch in LET}
anchor={}
for ch in LET:
    s=row(masks[ch], CAP-230)          # the neck: below the flag, in the stem
    b=row(masks[ch], 60)               # just above the baseline: the foot
    anchor[ch]=dict(stem=s, footrun=b)
    print('%s  neck stem x %7.1f..%-7.1f  foot run x %7.1f..%-7.1f'
          %(ch, s[0],s[1], b[0],b[1]))

# ---- the canonical parts, lifted from the letters that hold them best ----
FLAG_SRC='R'; FOOT_SRC='E'
FLAG_L, FLAG_R, FLAG_B = 320.0, 170.0, 210.0    # box left/right of the stem edge, height
FOOT_L, FOOT_R, FOOT_T = 175.0,  72.0, 140.0    # only the left spur, not the whole foot

def cut(ch, cx, x_l, x_r, y_lo, y_hi):
    m=masks[ch]
    i0=int(max(0,(cx-x_l-X0)*RES)); i1=int(min(W,(cx+x_r-X0)*RES))
    j0=int(max(0,(y_lo-Y0)*RES));   j1=int(min(H,(y_hi-Y0)*RES))
    return m[j0:j1, i0:i1].copy(), (i0,i1,j0,j1)

def graft(ch, part, cx, x_l, x_r, y_lo, y_hi, weld=0.0):
    """Replace the box with the canonical part. The bottom `weld` units of the
    box are unioned instead of replaced, so the part fuses onto whatever the
    letter already has there rather than cutting a notch into it."""
    m=masks[ch]
    i0=int(max(0,(cx-x_l-X0)*RES)); i1=i0+part.shape[1]
    j0=int(max(0,(y_lo-Y0)*RES));   j1=j0+part.shape[0]
    if i1>W or j1>H: return
    jw=j0+int(weld*RES)
    if jw>j0: m[j0:jw, i0:i1] |= part[:jw-j0]          # weld zone: union
    m[jw:j1, i0:i1] = part[jw-j0:]                     # above it: replace
    masks[ch]=m

flag_part,_=cut(FLAG_SRC, anchor[FLAG_SRC]['stem'][0], FLAG_L, FLAG_R, CAP-FLAG_B, CAP+30)
foot_part,_=cut(FOOT_SRC, anchor[FOOT_SRC]['footrun'][0], FOOT_L, FOOT_R, -30, FOOT_T)
print('\ncanonical flag from %s  (%d x %d px)   canonical foot from %s  (%d x %d px)'
      %(FLAG_SRC,*flag_part.shape[::-1],FOOT_SRC,*foot_part.shape[::-1]))

for ch in LET:                                # every letter gets the same flag
    weld = 95.0 if ch in ROUNDG else 45.0     # the bowl needs a longer weld than a stem
    graft(ch, flag_part, anchor[ch]['stem'][0], FLAG_L, FLAG_R, CAP-FLAG_B, CAP+30, weld)
for ch in 'BERNDF':                           # the round pair has no spur to share
    graft(ch, foot_part, anchor[ch]['footrun'][0], FOOT_L, FOOT_R, -30, FOOT_T)
print('grafted flag into %s, foot spur into %s'%(LET,'BERNDF'))

# heal the seam, then re-trace everything through the usual pipeline
for ch in LET:
    m=masks[ch]
    m=ndi.binary_closing(m, np.ones((5,5)))
    masks[ch]=ndi.binary_fill_holes(m) ^ (ndi.binary_fill_holes(m) & ~m) if False else m

np.save('/tmp/harm_masks.npy', np.array([masks[c] for c in LET]))
print('masks saved; window x %d..%d  y %d..%d at %d px/unit'%(X0,X1,Y0,Y1,RES))

# ---------------- re-trace the harmonised letters and build the font ----------
PAD=3
def contours_for(mask):
    mp=np.pad(mask,PAD,constant_values=False); out=[]
    for c in measure.find_contours(mp.astype(float),0.5):
        p=c[:, ::-1]-PAD                       # (x,y) in mask pixels
        if np.allclose(p[0],p[-1]): p=p[:-1]
        if len(p)<6: continue
        bb=max(np.ptp(p[:,0]), np.ptp(p[:,1]))
        if bb < 180*RES:
            fitted=vl.fit_contour(p, line_tol=1.6*RES, curve_tol=0.9*RES, smooth_deg=55.0)
        else:
            p=smooth(p, step=2.0*RES, win=11, passes=5)
            p=flatten(p, min_span=34.0*RES)
            fitted=vl.fit_contour(p, line_tol=0.9*RES, curve_tol=0.5*RES, smooth_deg=32.0)
            fitted=regularise(fitted, corner_deg=34.0, straight_tol=1.4*RES, fit_tol=1.8*RES)
        out.append(fitted)
    return out

def area_of(p):
    p=np.asarray(p); return 0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
def poly_of(start,segs,n=20):
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

T=lambda p:(X0+p[0]/RES, Y0+p[1]/RES)         # mask pixels -> font units
glyphs={}; widths={}
hmsrc=src['hmtx']
for ch in LET:
    tc=[]
    for start,segs in contours_for(masks[ch]):
        ns=[('L',T(s[1])) if s[0]=='L' else ('C',T(s[1]),T(s[2]),T(s[3])) for s in segs]
        st,ns=sharpen(T(start),ns)
        tc.append((st,ns))
    polys=[poly_of(st,sg) for st,sg in tc]
    ftc=[]
    for i,(st,sg) in enumerate(tc):
        depth=sum(1 for j,q in enumerate(polys)
                  if j!=i and abs(area_of(q))>abs(area_of(polys[i])) and inside(polys[i][0],q))
        poly=polys[i]; mat=(depth%2==0)
        ftc.append(fillet(st,sg, lambda pt,poly=poly,mat=mat: inside(tuple(pt),poly)==mat, radius=18.0))
    tc=ftc; polys=[poly_of(st,sg) for st,sg in tc]
    fixed=[]
    for i,(st,sg) in enumerate(tc):
        depth=sum(1 for j,q in enumerate(polys)
                  if j!=i and abs(area_of(q))>abs(area_of(polys[i])) and inside(polys[i][0],q))
        fixed.append((st,sg,(area_of(polys[i])>0)==(depth%2==1)))
    glyphs[ch]=fixed
    widths[ch]=hmsrc[cm[ord(ch)]][0]
    print('%s  contours %d  curves %3d  lines %3d'%(ch,len(fixed),
        sum(1 for _,sg,_ in fixed for x in sg if x[0]=='C'),
        sum(1 for _,sg,_ in fixed for x in sg if x[0]=='L')))

order=['.notdef']+list(LET)
fb=FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(order); fb.setupCharacterMap({ord(c):c for c in LET})
pens={'.notdef':TTGlyphPen(None).glyph()}
for ch,cs in glyphs.items():
    tt=TTGlyphPen(None); pen=Cu2QuPen(tt, max_err=1.0)
    for start,segs,ok in cs:
        if not ok:
            pts=poly_of(start,segs,n=20)[::-1]
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
fb.setupHorizontalHeader(ascent=900, descent=-200)
fb.setupNameTable(dict(familyName="Oberndorfer Drawn", styleName="Regular",
                       psName="OberndorferDrawn-Regular", version="5.0"))
fb.setupOS2(sTypoAscender=760, sTypoDescender=-240, usWinAscent=920, usWinDescent=220, sCapHeight=CAP)
fb.setupPost()
fb.save('_build.ttf')
print('\nwrote _build.ttf (harmonised) — run finalise.py next')
