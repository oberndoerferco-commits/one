import numpy as np, json
from PIL import Image
SRC="/home/user/one/assets/oberndorfer-plate/references/56.jpg"
OUT="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/work"
im=Image.open(SRC).convert("L"); A=np.asarray(im).astype(np.float32)
H,W=A.shape

# glyph = anything that is not flat paper (paper ~225..241)
mask = (A<208) | (A>244)

def cc_keep(m, drop_top_small=False):
    """label connected comps (4-conn) via BFS; return cleaned mask"""
    h,w=m.shape
    lab=np.zeros((h,w),np.int32); cur=0; comps=[]
    idx=np.argwhere(m)
    import collections
    for sy,sx in idx:
        if lab[sy,sx]: continue
        cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0; ys=[];xs=[]
        while q:
            y,x=q.popleft(); n+=1; ys.append(y); xs.append(x)
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<h and 0<=nx<w and m[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=cur; q.append((ny,nx))
        comps.append((cur,n,min(ys),max(ys),min(xs),max(xs)))
    return lab, comps

BANDS=[(3,180),(240,420),(445,690),(720,905)]
runs=json.load(open("runs.json"))

def box(band, i):
    y0,y1=BANDS[band]; x0,x1=runs[str(band)][i]; return x0,y0,x1,y1

def split_at_min(x0,x1,y0,y1,lo=0.33,hi=0.67):
    sub=mask[y0:y1, x0:x1]
    cp=sub.sum(axis=0).astype(float)
    a=int((x1-x0)*lo); b=int((x1-x0)*hi)
    k=a+int(np.argmin(cp[a:b]))
    return x0+k

# needed glyphs
spec={}
# band0: A | B C | D E | F G
x0,y0,x1,y1=box(0,1); s=split_at_min(x0,x1,y0,y1); spec['B']=(x0,y0,s,y1); spec['C']=(s,y0,x1,y1)
x0,y0,x1,y1=box(0,2); s=split_at_min(x0,x1,y0,y1); spec['D']=(x0,y0,s,y1); spec['E']=(s,y0,x1,y1)
x0,y0,x1,y1=box(0,3); s=split_at_min(x0,x1,y0,y1); spec['F']=(x0,y0,s,y1); spec['G']=(s,y0,x1,y1)
# band2: N O(umlaut) P Q R S
for i,ch in enumerate(['N','Odier','P','Q','R','S']):
    spec[ch]=box(2,i)
spec['Oum']=spec.pop('Odier')
print({k:v for k,v in spec.items()})

glyphs={}
for ch,(x0,y0,x1,y1) in spec.items():
    m=mask[y0:y1, x0:x1].copy()
    lab,comps=cc_keep(m)
    comps.sort(key=lambda c:-c[1])
    keep=np.zeros_like(m)
    # keep components >=1.5% of largest
    big=comps[0][1]
    kept=[]
    for (cid,n,ya,yb,xa,xb) in comps:
        if n >= max(40, big*0.004):
            keep |= (lab==cid); kept.append((cid,n,ya,yb,xa,xb))
    glyphs[ch]=dict(mask=keep, comps=kept, box=(x0,y0,x1,y1))
    print(ch, "comps kept", len(kept), "size", keep.shape)

np.save(OUT+"/masks.npy", np.array([1]))  # placeholder
import pickle
pickle.dump({k:(v['mask'],v['comps'],v['box']) for k,v in glyphs.items()}, open(OUT+"/glyphs.pkl","wb"))

# contact strip of extracted glyphs on cream
order=['B','C','D','E','F','G','N','Oum','P','Q','R','S']
hh=max(glyphs[c]['mask'].shape[0] for c in order)
ww=sum(glyphs[c]['mask'].shape[1] for c in order)+10*len(order)
strip=Image.new("RGB",(ww,hh+20),(238,236,230))
cx=5
for c in order:
    m=glyphs[c]['mask']; x0,y0,x1,y1=glyphs[c]['box']
    src=Image.open(SRC).convert("RGB").crop((x0,y0,x1,y1))
    al=Image.fromarray((m*255).astype(np.uint8))
    strip.paste(src,(cx,10),al); cx+=m.shape[1]+10
strip.save(OUT+"/extracted.png")
print("strip", strip.size)
