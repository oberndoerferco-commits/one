import numpy as np, math, os, sys, collections
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)

SC=5
src=Image.open(HERE+"/chosen.png").convert("RGBA")
bgw=Image.new("RGBA",src.size,(255,255,255,255)); bgw.alpha_composite(src)
rib=bgw.convert("RGB").resize((src.width*SC,src.height*SC),Image.LANCZOS)
a=np.asarray(rib.convert("L")); H,W=a.shape
print("ribbon",rib.size,"lum percentiles",[int(np.percentile(a,p)) for p in (1,5,30,60,95)])
ink=a<170
free=~ink; seen=np.zeros_like(free); q=collections.deque()
for x in range(W):
    for y in (0,H-1):
        if free[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
for y in range(H):
    for x in (0,W-1):
        if free[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
while q:
    y,x=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny,nx=y+dy,x+dx
        if 0<=ny<H and 0<=nx<W and free[ny,nx] and not seen[ny,nx]:
            seen[ny,nx]=True; q.append((ny,nx))
enc=free&~seen
lab=np.zeros((H,W),np.int32); cur=0; sizes={}
for sy,sx in np.argwhere(enc):
    if lab[sy,sx]: continue
    cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0
    while q:
        y,x=q.popleft(); n+=1
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and enc[ny,nx] and not lab[ny,nx]:
                lab[ny,nx]=cur; q.append((ny,nx))
    sizes[cur]=n
top=sorted(sizes.items(),key=lambda kv:-kv[1])[:4]
print("enclosed regions",top)
face=lab==top[0][0]
Image.fromarray((face*255).astype(np.uint8)).save(HERE+"/chosen-face.png")
v=np.asarray(rib).copy(); v[face]=(v[face]*0.45+np.array([255,0,0])*0.55).astype('uint8')
Image.fromarray(v).save(HERE+"/chosen-facevis.png")
rib.save(HERE+"/chosen-big.png")
