"""Smooth the outline inside each circle he drew. Nothing else.

Corner-cutting was the wrong operation: it needs to know what a feature IS
(tip? pen terminal? counter?) and it works in the wrong direction on an inner
contour, which is how it put cracks in the F and the E and turned a round
terminal on the N into a point.

This does the thing he actually asked for instead — take the wobble out of
this patch of outline — by replacing the points inside a circle with a
smoothed version of themselves, weighted to zero at the circle's edge so the
join is seamless. It cannot sharpen anything, cannot cross into a counter and
cannot change the topology, because every point stays on its own outline and
no point is added or removed.
"""
import json, os, re, math
import numpy as np
from fontTools.ttLib import TTFont

SRC=DST='OberndorferDrawn-Regular.ttf'
MARKS='/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/art/marks2/marks'
LIVE='/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/art/live/index.html'
PASSES=int(os.environ.get('SPASS','6'))      # how hard to smooth inside a circle
WIN=int(os.environ.get('SWIN','2'))          # half-width of the averaging window
GROW=float(os.environ.get('SGROW','18'))     # how far past the circle the taper runs

NM={'Odieresis':'Ö'}
live=open(LIVE).read()
boxes={m.group(1):[float(v) for v in m.group(2).split()] for m in
  re.finditer(r'<div class="stage" data-panel="([^"]+)">\s*<svg class="art" viewBox="([^"]+)"', live)}

def regions():
    out={}
    for fn in sorted(os.listdir(MARKS)):
        key=fn[:-5]; ch=NM.get(key,key)
        if ch not in boxes: continue
        x0,y0,W,H=boxes[ch]; rs=[]
        for st in json.loads(json.load(open(os.path.join(MARKS,fn)))['strokes']):
            p=np.array([[x0+q[0]*W, 780.0-(y0+q[1]*H)] for q in st])
            c=p.mean(0); r=float(np.hypot(*(p-c).T).max())
            rs.append((c,r))
        out[key]=rs
    return out

f=TTFont(SRC); g=f['glyf']; cm=f.getBestCmap()
regs=regions(); moved_total=0
for key,rs in regs.items():
    gn=key if key in g.glyphs else cm.get(ord(NM.get(key,key)))
    if gn is None: continue
    gl=g[gn]; co=gl.getCoordinates(g)
    pts=np.array([list(p) for p in co[0]],float); ends=list(co[1]); flags=list(co[2])
    s=0; moved=0
    for e in ends:
        n=e-s+1
        if n<8: s=e+1; continue
        seg=pts[s:e+1].copy()
        # weight: 1 well inside a circle, falling to 0 GROW units outside it
        w=np.zeros(n)
        for c,r in rs:
            d=np.hypot(*(seg-c).T)
            wi=np.clip((r+GROW-d)/max(GROW,1e-6), 0.0, 1.0)
            w=np.maximum(w,wi)
        if w.max()<=0: s=e+1; continue
        out=seg.copy()
        for _ in range(PASSES):
            acc=np.zeros_like(out)
            for k in range(-WIN,WIN+1):
                acc+=np.roll(out,k,axis=0)
            avg=acc/(2*WIN+1)
            out=out*(1-w[:,None])+avg*w[:,None]
        d=np.hypot(*(out-seg).T)
        moved+=int((d>0.5).sum())
        pts[s:e+1]=out
        s=e+1
    if moved:
        gl.coordinates=type(co[0])([(int(round(a)),int(round(b))) for a,b in pts])
        gl.recalcBounds(g)
    moved_total+=moved
    print('  %-10s %2d circles -> %3d outline points smoothed'%(key,len(rs),moved))
print('smoothed %d points, passes %d, window %d; no point added, removed or crossed'
      %(moved_total,PASSES,WIN))
f.save(DST)
