import numpy as np, math, os, sys, collections
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from bend2 import bend

rib=Image.open(HERE+"/r04-clean.png").convert("RGB")
a=np.asarray(rib.convert("L"))
# trim the black crop bar on the right
cols=(a<90).mean(axis=0)
right=rib.width
for x in range(rib.width-1,rib.width-80,-1):
    if cols[x]>0.75: right=x
rib=rib.crop((0,0,right,rib.height)); a=np.asarray(rib.convert("L"))
H,W=a.shape
ink=a<150

# flood fill background from border
free=~ink; seen=np.zeros_like(free)
q=collections.deque()
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
enclosed=free&~seen

# largest enclosed region = band face
lab=np.zeros((H,W),np.int32); cur=0; best=(0,None)
for sy,sx in np.argwhere(enclosed):
    if lab[sy,sx]: continue
    cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0
    while q:
        y,x=q.popleft(); n+=1
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and enclosed[ny,nx] and not lab[ny,nx]:
                lab[ny,nx]=cur; q.append((ny,nx))
    if n>best[0]: best=(n,cur)
face=(lab==best[1])
print("band face px",best[0])

xs=np.where(face.any(axis=0))[0]
x0,x1=xs[0],xs[-1]
cxs=[];cys=[];hts=[]
for x in range(x0,x1+1):
    ys=np.where(face[:,x])[0]
    if len(ys)<6: continue
    cxs.append(x); cys.append((ys[0]+ys[-1])/2.0); hts.append(ys[-1]-ys[0])
cxs=np.array(cxs,float); cys=np.array(cys,float); hts=np.array(hts,float)
# use the central 86% where the face is a clean band
lo,hi=np.percentile(cxs,[7,93]); sel=(cxs>=lo)&(cxs<=hi)
A,B,C=np.polyfit(cxs[sel],cys[sel],2)
h=-B/(2*A); k=A*h*h+B*h+C
print("quadratic a=%.6g vertex=(%.1f,%.1f)"%(A,h,k))
print("face x %d..%d  usable %d..%d  height min/med %d/%d"%(x0,x1,int(lo),int(hi),hts[sel].min(),np.median(hts[sel])))
np.save(HERE+"/fit.npy", np.array([A,h,k,lo,hi,hts[sel].min(),np.median(hts[sel])]))
rib.save(HERE+"/r04-trim.png")
Image.fromarray((face*255).astype(np.uint8)).save(HERE+"/r04-face.png")
