import numpy as np, collections
from PIL import Image
HERE="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
im=Image.open("/home/user/one/assets/oberndorfer-plate/references/49.jpg").convert("RGB")
a=np.asarray(im).astype(np.float32); H,W,_=a.shape
lum=a.mean(axis=2)
print("lum percentiles",[int(np.percentile(lum,p)) for p in (5,40,70,85,95)])
gold=lum>95
# drop the caption band at the bottom
rows=gold.sum(axis=1)
# find the big wordmark block
on=rows> W*0.015
runs=[];s0=None
for y in range(H):
    if on[y] and s0 is None: s0=y
    elif not on[y] and s0 is not None: runs.append((s0,y-1)); s0=None
if s0 is not None: runs.append((s0,H-1))
runs.sort(key=lambda r: r[1]-r[0])
y0,y1=runs[-1]
# pull in nearby bands above (the umlaut dots sit in their own run)
for (a0,a1) in runs:
    if a1 < y0 and (y0-a1) < 70: y0=min(y0,a0)
print("row runs",runs,"-> using",y0,y1)
xs=np.where(gold[y0:y1+1].any(axis=0))[0]; x0,x1=xs[0],xs[-1]
g=gold[y0:y1+1, x0:x1+1]; h,w=g.shape
print("wordmark block",w,"x",h)
# fill holes: flood non-gold from the border
free=~g; seen=np.zeros_like(free); q=collections.deque()
for x in range(w):
    for y in (0,h-1):
        if free[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
for y in range(h):
    for x in (0,w-1):
        if free[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
while q:
    y,x=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny,nx=y+dy,x+dx
        if 0<=ny<h and 0<=nx<w and free[ny,nx] and not seen[ny,nx]:
            seen[ny,nx]=True; q.append((ny,nx))
sil=g|(free&~seen)
rgb=np.where(g[...,None],0.0,255.0).repeat(3,axis=2)
out=Image.fromarray(np.dstack([rgb.astype(np.uint8), np.where(sil,255,0).astype(np.uint8)]),"RGBA")
out.save(HERE+"/schrift-bw.png")
bg=Image.new("RGB",out.size,(255,255,255)); bg.paste(out,(0,0),out); bg.save(HERE+"/schrift-chk.png")
print("saved",out.size)
