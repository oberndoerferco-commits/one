import numpy as np, collections
from PIL import Image
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
im=Image.open("/home/user/one/assets/oberndorfer-plate/references/47.webp").convert("RGB")
a=np.asarray(im).astype(int)
# red pen is coloured; letters are black
sat=a.max(axis=2)-a.min(axis=2)
ink=(a.mean(axis=2)<120)&(sat<60)
# work inside the panel only
sub=ink[360:450, 600:1360]
h,w=sub.shape
lab=np.zeros((h,w),np.int32); cur=0; keep=np.zeros_like(sub)
for sy,sx in np.argwhere(sub):
    if lab[sy,sx]: continue
    cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; pts=[]
    while q:
        y,x=q.popleft(); pts.append((y,x))
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and sub[ny,nx] and not lab[ny,nx]:
                lab[ny,nx]=cur; q.append((ny,nx))
    p=np.array(pts)
    touches = p[:,0].min()==0 or p[:,0].max()==h-1 or p[:,1].min()==0 or p[:,1].max()==w-1
    if len(p)>=40 and not touches:
        keep[lab==cur]=True
ys=np.where(keep.any(axis=1))[0]; xs=np.where(keep.any(axis=0))[0]
k=keep[ys[0]:ys[-1]+1, xs[0]:xs[-1]+1]
rgb=np.where(k[...,None],0,255).repeat(3,axis=2).astype(np.uint8)
al=np.where(k,255,0).astype(np.uint8)
out=Image.fromarray(np.dstack([rgb,al]),"RGBA")
out.save(H+"/mii.png")
bg=Image.new("RGB",out.size,(255,255,255)); bg.paste(out,(0,0),out); bg.save(H+"/mii-chk.png")
print("MADE IN ITALY lifted:",out.size)
