"""Round only the corners he circled.

Works on the finished font, so his marks land exactly where he drew them, and
touches nothing he did not mark. A corner is rounded by cutting back along both
of its arms and bridging with a quadratic — the native curve of a TrueType
outline — so no other point in the glyph moves.
"""
import json, os, re, math, sys
import numpy as np
from fontTools.ttLib import TTFont

SRC=DST='OberndorferDrawn-Regular.ttf'
MARKS='/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/art/marks2/marks'
LIVE='/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/art/live/index.html'
RAD=float(os.environ.get('MRAD','26'))     # the radius asked of a marked corner
ANG=float(os.environ.get('MANG','118'))    # only corners sharper than this
PAD=float(os.environ.get('MPAD','30'))     # how far outside a circle still counts
REACH=50.0                                  # span used to judge a corner

NAME={'Odieresis':'Ö'}
live=open(LIVE).read()
boxes={}
for m in re.finditer(r'<div class="stage" data-panel="([^"]+)">\s*<svg class="art" viewBox="([^"]+)"', live):
    boxes[m.group(1)]=[float(v) for v in m.group(2).split()]

def marked_regions():
    out={}
    for fn in sorted(os.listdir(MARKS)):
        key=fn[:-5]; ch=NAME.get(key,key)
        if ch not in boxes: continue
        x0,y0,W,H=boxes[ch]
        regions=[]
        for st in json.loads(json.load(open(os.path.join(MARKS,fn)))['strokes']):
            pts=np.array([[x0+p[0]*W, 780.0-(y0+p[1]*H)] for p in st])   # -> glyph units
            c=pts.mean(0)
            r=float(np.hypot(*(pts-c).T).max())+PAD
            regions.append((c,r))
        out[key]=regions
    return out

def walk(pts, start, n, i, step, reach):
    """Point about `reach` units away along the contour, in direction `step`."""
    j=i; d=0.0
    for _ in range(n):
        k=(j+step)%n
        d+=math.hypot(pts[start+k][0]-pts[start+j][0], pts[start+k][1]-pts[start+j][1])
        j=k
        if d>=reach: break
    return j, d

def corners(pts, flags, start, end, ang_deg, reach=50.0):
    """On-curve points whose turn, measured over a span rather than against the
    neighbouring control point, is sharper than ang_deg. Measuring against the
    immediate neighbour misses every real tip, because that neighbour is a
    control point a few units away and the angle there reads as straight."""
    n=end-start+1
    res=[]
    for i in range(n):
        gi=start+i
        if not (flags[gi]&1): continue
        p=np.array(pts[gi],float)
        ja,da=walk(pts,start,n,i,-1,reach)
        jb,db=walk(pts,start,n,i,+1,reach)
        if da<4 or db<4: continue
        va=np.array(pts[start+ja],float)-p
        vb=np.array(pts[start+jb],float)-p
        la=np.hypot(*va); lb=np.hypot(*vb)
        if la<1e-6 or lb<1e-6: continue
        cosv=float(np.clip((va/la)@(vb/lb),-1,1))
        th=math.degrees(math.acos(cosv))
        if th<ang_deg: res.append((gi,i,p,va/la,vb/lb,la,lb,th,ja,jb))
    return res

def point_in(pt, poly):
    x,y=pt; n=len(poly); c=False; j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi): c=not c
        j=i
    return c

f=TTFont(SRC); g=f['glyf']; cm=f.getBestCmap()
regions=marked_regions()
total=0
for key,regs in regions.items():
    gn=key if key in g.glyphs else cm.get(ord(NAME.get(key,key)))
    if gn is None or gn not in g.glyphs: continue
    gl=g[gn]
    co=gl.getCoordinates(g); pts=[tuple(p) for p in co[0]]; ends=list(co[1]); flags=list(co[2])
    newpts=[]; newflags=[]; newends=[]; s=0; hits=0
    for e in ends:
        n=e-s+1
        poly=[pts[k] for k in range(s,e+1)]
        cs=corners(pts,flags,s,e,ANG)
        # One corner per circle: the sharpest. Several corners inside one mark,
        # each cut back, overlap and cross into spikes — which is what the first
        # attempt produced. And no two accepted cuts may reach each other.
        best={}
        for c in cs:
            gi,i,p,ua,ub,la,lb,th,ja,jb = c
            for ri,(rc,rr) in enumerate(regs):
                if np.hypot(*(p-rc))<=rr:
                    if ri not in best or th<best[ri][7]: best[ri]=c
                    break
        cut={}; absorb=set(); taken=[]
        for c in sorted(best.values(), key=lambda z:z[7]):
            gi,i,p,ua,ub,la,lb,th,ja,jb = c
            d=RAD/max(math.tan(math.radians(th/2)),1e-3)
            d=min(d, 0.45*la, 0.45*lb, 70.0)
            # never let a cut reach across a thin feature to the far side of the
            # stroke: that is what left a tooth at the hairline ends and in the N
            far=1e9
            for j in range(n):
                dj=min(abs(j-i), n-abs(j-i))
                if dj<=max(3,int(n*0.06)): continue
                far=min(far, float(np.hypot(*(np.array(pts[s+j],float)-p))))
            # Distinguish a real tip from a tiny curled blob (a hairline
            # terminal): walking `reach` units of outline from a true tip lands
            # `reach` units away in a straight line, but curls back on a blob.
            # Cutting a blob leaves a visible step instead of a round.
            if la < 0.60*REACH or lb < 0.60*REACH: continue
            # Only outward corners — the tips he marked. Cutting an inward notch
            # opens a crack: that is where the 6 degree slivers in the F and E
            # came from. Probe along the bisector; inside the ink means outward.
            w=ua+ub; nw=np.hypot(*w)
            if nw<1e-9: continue
            probe=p + w/nw*min(12.0, 0.5*d)
            if not point_in(probe, poly): continue
            d=min(d, 0.45*far)
            for q,dq in taken:
                gap=np.hypot(*(p-q))
                if gap < d+dq+6: d=max(0.0, gap-dq-6)
            if d<4: continue
            take=set()
            for step,stop in ((-1,ja),(+1,jb)):
                j=i
                while True:
                    j=(j+step)%n
                    if j in cut: break
                    q=np.array(pts[s+j],float)
                    if np.hypot(*(q-p))>=d or j==stop: break
                    take.add(j)
            if take & set(cut): continue
            cut[i]=(p+ua*d, p+ub*d); absorb |= take; taken.append((p,d))
        def build(cutset, absorbset):
            op=[]; of=[]
            for i2 in range(n):
                gi2=s+i2
                if i2 in cutset:
                    p1,p2=cutset[i2]
                    op.append((int(round(p1[0])),int(round(p1[1])))); of.append(1)
                    op.append(pts[gi2]);                              of.append(0)
                    op.append((int(round(p2[0])),int(round(p2[1])))); of.append(1)
                elif i2 in absorbset: continue
                else: op.append(pts[gi2]); of.append(flags[gi2])
            return op, of

        def sharpest(op):
            m=180.0; where=None
            L=len(op)
            if L<8: return m, where
            for i2 in range(L):
                p0=np.array(op[i2],float)
                ja,_=walk(op,0,L,i2,-1,26.0); jb,_=walk(op,0,L,i2,+1,26.0)
                va=np.array(op[ja],float)-p0; vb=np.array(op[jb],float)-p0
                la2=np.hypot(*va); lb2=np.hypot(*vb)
                if la2<4 or lb2<4: continue
                th2=math.degrees(math.acos(float(np.clip((va/la2)@(vb/lb2),-1,1))))
                if th2<m: m, where = th2, p0
            return m, where

        base,_=sharpest([pts[k] for k in range(s,e+1)])
        while cut:
            op,of=build(cut,absorb)
            m,where=sharpest(op)
            if m >= min(base, 62.0) - 1.0: break
            # drop the cut nearest the corner that got worse, then try again
            k=min(cut, key=lambda i2: np.hypot(*(np.array(pts[s+i2],float)-where)))
            del cut[k]
            absorb=set()
            for i2,(q1,q2) in cut.items():
                pp=np.array(pts[s+i2],float); dd=np.hypot(*(np.array(q1)-pp))
                for step in (-1,+1):
                    j=i2
                    while True:
                        j=(j+step)%n
                        if j in cut: break
                        if np.hypot(*(np.array(pts[s+j],float)-pp))>=dd: break
                        absorb.add(j)
        op,of=build(cut,absorb)
        hits+=len(cut)
        newpts.extend(op); newflags.extend(of)
        newends.append(len(newpts)-1)
        s=e+1
    if hits:
        gl.coordinates=type(co[0])(newpts); gl.endPtsOfContours=newends
        gl.flags=type(co[2])(newflags); gl.numberOfContours=len(newends)
        gl.recalcBounds(g)
    total+=hits
    print('  %-10s %2d marked regions -> %2d corners rounded'%(key,len(regs),hits))
print('rounded %d corners, radius %g, only where he marked'%(total,RAD))
f.save(DST)
