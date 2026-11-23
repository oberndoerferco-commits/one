"""Build a real TrueType font from the hand-drawn capitals.

Each letter becomes a glyph on a 1000-unit em: contours simplified, every
long run snapped to the drawing's own dominant stroke angles, corners taken
as the exact intersections of those lines, y-extremes snapped to the baseline
and cap line, and consistent sidebearings.  Repeated letters are one glyph.
"""
import numpy as np, math, sys
from skimage import measure
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM=1000; CAP=700          # cap height in font units
RDP_EPS=4.0; SNAP_DEG=11.0; MINLEN=45.0
SB=40                      # sidebearing in font units

sp=list(np.load('sprites.npy', allow_pickle=True))
NAME='OBERNDÖRFER'
for s in sp: s['baseoff']=s['base']-s['y0']
canon={}
for ch in set(NAME):
    inst=[s for s in sp if s['ch']==ch]
    canon[ch]=inst[int(np.argsort([i['w'] for i in inst])[len(inst)//2])]

def rdp(p,eps):
    if len(p)<3: return p
    d=p[-1]-p[0]; L=np.hypot(*d)
    q=p-p[0]
    dist=(np.abs(d[0]*q[:,1]-d[1]*q[:,0])/L) if L>1e-9 else np.hypot(*q.T)
    i=int(np.argmax(dist))
    if dist[i]>eps: return np.vstack([rdp(p[:i+1],eps)[:-1], rdp(p[i:],eps)])
    return np.vstack([p[0],p[-1]])

# dominant angles, measured across every letter
angs={}
raw={}
for ch,s in canon.items():
    PAD=3
    mp=np.pad(s['mask'], PAD, constant_values=False)
    cs=[]
    for c in measure.find_contours(mp.astype(float), 0.5):
        p=c[:, ::-1] - PAD                      # (row,col)->(x,y), undo the pad
        if not np.allclose(p[0], p[-1]): p=np.vstack([p, p[:1]])
        cs.append(rdp(p, RDP_EPS))
    raw[ch]=[c for c in cs if len(c)>=4]
hist=np.zeros(180)
for ch,cs in raw.items():
    for c in cs:
        for a,b in zip(c[:-1],c[1:]):
            v=b-a; L=np.hypot(*v)
            if L>=MINLEN: hist[int(round(math.degrees(math.atan2(v[1],v[0]))%180))%180]+=L
k=np.ones(7)/7
hs=np.convolve(np.r_[hist[-7:],hist,hist[:7]],k,mode='same')[7:-7]
peaks=[i for i in range(180) if hs[i]==max(hs[max(0,i-6):i+7]) and hs[i]>hs.mean()*1.3]
print('stroke angles:',peaks)

def snap(c):
    pts=c[:-1]; n=len(pts); lines=[]
    for i in range(n):
        a=pts[i]; b=pts[(i+1)%n]; v=b-a; L=np.hypot(*v)
        ang=math.degrees(math.atan2(v[1],v[0]))%180
        if L>=MINLEN and peaks:
            best=min(peaks,key=lambda p:min(abs(ang-p),180-abs(ang-p)))
            if min(abs(ang-best),180-abs(ang-best))<=SNAP_DEG: ang=float(best)
            lines.append(('L',a,b,ang))
        else: lines.append(('K',a,b,ang))
    res=[]
    for i,(kd,a,b,ang) in enumerate(lines):
        if kd!='L': res.append(b); continue
        th=math.radians(ang); d=np.array([math.cos(th),math.sin(th)]); mid=(a+b)/2
        kd2,a2,b2,ang2=lines[(i+1)%n]
        if kd2=='L':
            th2=math.radians(ang2); d2=np.array([math.cos(th2),math.sin(th2)])
            # only intersect when the two lines actually meet at a real angle
            dang=abs((ang-ang2+90)%180-90)
            M=np.array([[d[0],-d2[0]],[d[1],-d2[1]]])
            if dang>=18.0 and abs(np.linalg.det(M))>1e-6:
                t=np.linalg.solve(M,(a2+b2)/2-mid)
                P=mid+t[0]*d
                lim=0.45*min(np.hypot(*(b-a)), np.hypot(*(b2-a2)))
                if np.hypot(*(P-b))<=lim:          # corner must stay near where it was
                    res.append(P); continue
        res.append(b)
    return np.array(res)

glyphs={}; widths={}
for ch,s in canon.items():
    cappx=s['base']-s['top']
    k=CAP/float(cappx)
    base_in_sprite=s['baseoff']
    cs=[snap(c) for c in raw[ch]]
    # to font units: y up from baseline, x from left sidebearing
    out=[]
    for c in cs:
        p=np.empty_like(c)
        p[:,0]=c[:,0]*k+SB
        p[:,1]=(base_in_sprite-c[:,1])*k
        out.append(np.round(p).astype(int))
    # snap y extremes onto the baseline / cap line
    for p in out:
        p[np.abs(p[:,1])<=10,1]=0
        p[np.abs(p[:,1]-CAP)<=12,1]=CAP
    # TrueType winding: outer contours clockwise, counters counter-clockwise
    def area(p):
        return 0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
    def inside(pt, poly):
        x,y=pt; n=len(poly); c=False; j=n-1
        for i in range(n):
            xi,yi=poly[i]; xj,yj=poly[j]
            if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi): c=not c
            j=i
        return c
    fixed=[]
    for i,p in enumerate(out):
        depth=0
        for j,q in enumerate(out):
            if i==j: continue
            if abs(area(q))>abs(area(p)) and inside(p[0], q): depth+=1
        want_ccw = (depth%2==1)
        is_ccw = area(p)>0
        fixed.append(p if is_ccw==want_ccw else p[::-1])
    out=fixed
    glyphs[ch]=out
    widths[ch]=int(round(s['w']*k))+2*SB
    print('%s  cap %dpx -> %d units   contours %d   advance %d'%(ch,cappx,CAP,len(out),widths[ch]))

order=['.notdef']+[c for c in dict.fromkeys(NAME)]
fb=FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(order)
fb.setupCharacterMap({ord(c):c for c in dict.fromkeys(NAME)})
pens={}
pen=TTGlyphPen(None); pens['.notdef']=pen.glyph()
for ch,cs in glyphs.items():
    pen=TTGlyphPen(None)
    for p in cs:
        pen.moveTo(tuple(p[0]))
        for q in p[1:]: pen.lineTo(tuple(q))
        pen.closePath()
    pens[ch]=pen.glyph()
fb.setupGlyf(pens)
fb.setupHorizontalMetrics({g:(widths.get(g,600),0) for g in order})
fb.setupHorizontalHeader(ascent=820, descent=-180)
fb.setupNameTable(dict(familyName="Oberndorfer Drawn", styleName="Regular",
                       psName="OberndorferDrawn-Regular", version="1.0"))
fb.setupOS2(sTypoAscender=820, sTypoDescender=-180, usWinAscent=900, usWinDescent=220,
            sCapHeight=CAP)
fb.setupPost()
fb.save('OberndorferDrawn-Regular.ttf')
print('wrote OberndorferDrawn-Regular.ttf')
