import json, cv2, numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
INK="#1C1714"
d=json.load(open('parts.json'))
G=sorted([r for r in d['res'] if r['tag']=='path' and r['y1']<90],key=lambda r:r['x0'])
assert len(G)==11
CAP=75.2-41.7; BASE=75.2; TOP=41.7; DOT=41.7-31.3
# ---- cross mark -> path (unit box 0..1)
im=cv2.imread('mark.png',cv2.IMREAD_UNCHANGED); a=im[:,:,3]
_,th=cv2.threshold(a,127,255,cv2.THRESH_BINARY)
cs,_=cv2.findContours(th,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea); c=cv2.approxPolyDP(c,2.0,True).reshape(-1,2)
MARK="M"+" L".join(f"{x/3000:.4f} {y/3000:.4f}" for x,y in c)+"Z"
print('mark points',len(c))
# ---- MILANO from EB Garamond
def text_paths(txt,font,cap_px,track_em,weight_file):
    f=TTFont(weight_file); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
    capH=f['OS/2'].sCapHeight or 0.65*upm; s=cap_px/capH; x=0; out=[]
    for ch in txt:
        g=cmap[ord(ch)]; pen=SVGPathPen(gs); tp=TransformPen(pen,(s,0,0,-s,x,0)); gs[g].draw(tp)
        out.append(pen.getCommands()); x+=gs[g].width*s + track_em*cap_px/0.65
    width=x - track_em*cap_px/0.65
    return "".join(f'<path d="{p}"/>' for p in out), width
def wordmark(extra):
    """glyphs re-spaced: original gaps + extra (fraction of cap height). returns svg group (origin: x=0 left, y=0 baseline) and width"""
    parts=[]; x=0; prev=None
    for g in G:
        if prev is None: shift=-g['x0']
        else: shift = (prev_x1_new + (g['x0']-prev['x1']) + extra*CAP) - g['x0']
        m=g['m']; parts.append(f'<path d="{g["d"]}" transform="matrix({m[0]},{m[1]},{m[2]},{m[3]},{m[4]+shift:.3f},{m[5]-BASE:.3f})"/>')
        prev_x1_new=g['x1']+shift; prev=g
    return "".join(parts), prev_x1_new
def svg(body,w,h,pad=0):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w+2*pad:.2f} {h+2*pad:.2f}" width="{w+2*pad:.0f}" height="{h+2*pad:.0f}"><g fill="{INK}">{body}</g></svg>'
out={}
# A: spaced wordmark + light MILANO centred below
wm,ww=wordmark(0.20); mc=CAP*0.34; mil,mw=text_paths("MILANO",None,mc,0.48,'ebg1.ttf')
gap=CAP*0.55; H=DOT+CAP+gap+mc
body=f'<g transform="translate(0,{DOT+CAP:.2f})">{wm}</g><g transform="translate({(ww-mw)/2:.2f},{DOT+CAP+gap+mc:.2f})">{mil}</g>'
out['A']=svg(body,ww,H+2,1)
# B: one line, MILANO smaller after a gap, baselines aligned
wm,ww=wordmark(0.16); mc=CAP*0.40; mil,mw=text_paths("MILANO",None,mc,0.42,'ebg1.ttf')
g2=CAP*0.95; body=f'<g transform="translate(0,{DOT+CAP:.2f})">{wm}</g><g transform="translate({ww+g2:.2f},{DOT+CAP:.2f})">{mil}</g>'
out['B']=svg(body,ww+g2+mw,DOT+CAP+1.5,1)
# C: mark above, A below (stacked)
wm,ww=wordmark(0.20); mc=CAP*0.32; mil,mw=text_paths("MILANO",None,mc,0.5,'ebg1.ttf')
ms=CAP*1.9; gapm=CAP*0.55; gap=CAP*0.62
body=(f'<path d="{MARK}" transform="translate({(ww-ms)/2:.2f},0) scale({ms:.2f})"/>'
      f'<g transform="translate(0,{ms+gapm+CAP:.2f})">{wm}</g>'
      f'<g transform="translate({(ww-mw)/2:.2f},{ms+gapm+CAP+gap+mc:.2f})">{mil}</g>')
out['C']=svg(body,ww,ms+gapm+CAP+gap+mc+2,1)
# D: wordmark alone
wm,ww=wordmark(0.20); out['D']=svg(f'<g transform="translate(0,{DOT+CAP:.2f})">{wm}</g>',ww,DOT+CAP+1.5,1)
# M: the mark alone (favicon / avatar)
out['M']=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" width="512" height="512"><path fill="{INK}" d="{MARK}"/></svg>'
for k,v in out.items(): open(f'opt-{k}.svg','w').write(v); print(k,len(v))
