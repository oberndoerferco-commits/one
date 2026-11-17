import numpy as np, pickle, collections, sys
from PIL import Image
OUT="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/work"
SRC="/home/user/one/assets/oberndorfer-plate/references/56.jpg"
G=pickle.load(open(OUT+"/glyphs.pkl","rb"))
full=Image.open(SRC).convert("RGB")
A=np.asarray(Image.open(SRC).convert("L")).astype(np.float32)
TARGET=float(sys.argv[1]); CREAM=(238,236,230)

def comps_of(m):
    h,w=m.shape; lab=np.zeros((h,w),np.int32); cur=0; out=[]
    for sy,sx in np.argwhere(m):
        if lab[sy,sx]: continue
        cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; ys=[]
        while q:
            y,x=q.popleft(); ys.append((y,x))
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<h and 0<=nx<w and m[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=cur; q.append((ny,nx))
        ys=np.array(ys); out.append((cur,len(ys),ys[:,0].min(),ys[:,0].max()))
    return lab,out

def glyph(ch):
    key='Oum' if ch in ('O','Ö') else ch
    m,comps,box=G[key]
    if ch=='O':
        lab,cs=comps_of(m); keep=np.zeros_like(m)
        for (cid,n,ya,yb) in cs:
            if yb<40: continue
            keep|=(lab==cid)
        m=keep
    x0,y0,x1,y1=box
    sub=A[y0:y1, x0:x1]
    body = m & (sub<115)          # dark letter + its dark outline, no light shading
    return full.crop((x0,y0,x1,y1)), m, body

WORD="OBERNDÖRFER"
raw=[glyph(c) for c in WORD]
tr=[]
for rgb,m,body in raw:
    ys=np.where(m.any(axis=1))[0]; xs=np.where(m.any(axis=0))[0]
    t,b,l,r=ys[0],ys[-1],xs[0],xs[-1]
    tr.append((rgb.crop((l,t,r+1,b+1)), m[t:b+1,l:r+1], body[t:b+1,l:r+1]))

Hm=max(m.shape[0] for _,m,_ in tr); canvasH=Hm+80
def extents(b):
    L=np.full(b.shape[0],10**9); R=np.full(b.shape[0],-10**9)
    for y in range(b.shape[0]):
        xs=np.where(b[y])[0]
        if len(xs): L[y]=xs[0]; R[y]=xs[-1]
    return L,R

placed=[]; prevx=None; prevL=prevR=None; prevTop=None
for rgb,m,body in tr:
    h,w=m.shape; ytop=canvasH-40-h
    L,R=extents(body)
    if prevx is None: px=40
    else:
        px=None
        for cand in range(prevx-10, prevx+prevR.shape[0]+400):
            mind=10**9
            for yy in range(canvasH):
                a=yy-prevTop; b2=yy-ytop
                if 0<=a<prevR.shape[0] and 0<=b2<h and prevR[a]>-10**8 and L[b2]<10**8:
                    mind=min(mind,(cand+L[b2])-(prevx+prevR[a]))
            if mind>=TARGET: px=cand; break
        if px is None: px=prevx+w
    placed.append((px,ytop,rgb,m)); prevx=px; prevL,prevR=L,R; prevTop=ytop

Wt=placed[-1][0]+placed[-1][3].shape[1]+40
cv=Image.new("RGB",(Wt,canvasH),CREAM)
for px,ytop,rgb,m in placed:
    cv.paste(rgb,(px,ytop),Image.fromarray((m*255).astype(np.uint8)))
cv.save(OUT+"/word-raw.png")
sc=1600/cv.width
cv.resize((1600,int(cv.height*sc)),Image.LANCZOS).save(OUT+"/word.png")
print("raw",cv.size,"target",TARGET)
