import numpy as np, math, os, sys, collections
from PIL import Image, ImageFont, ImageDraw, ImageFilter
HERE="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,HERE)
from allrib import bend_poly
FONT="/home/user/one/assets/oberndorfer-plate/faces/d_cinzel.ttf"

def ribbon_bw(scale):
    src=Image.open(HERE+"/chosen.png").convert("RGBA")
    w,h=src.size
    big=src.resize((int(w*scale),int(h*scale)),Image.LANCZOS)
    a=np.asarray(big).astype(np.float32)
    lum=a[:,:,:3].mean(axis=2)
    # the source has no real alpha: flood the white page in from the border
    light=lum>=172
    hh,ww=light.shape
    seen=np.zeros_like(light); q=collections.deque()
    for x in range(ww):
        for y in (0,hh-1):
            if light[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    for y in range(hh):
        for x in (0,ww-1):
            if light[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<hh and 0<=nx<ww and light[ny,nx] and not seen[ny,nx]:
                seen[ny,nx]=True; q.append((ny,nx))
    inside=~seen
    outline=inside&(lum<172)
    rgb=np.where(outline[...,None],0.0,255.0).repeat(3,axis=2)
    al=np.where(inside,255,0).astype(np.uint8)
    im=Image.fromarray(np.dstack([rgb.astype(np.uint8),al]),"RGBA")
    return im

def face_of(im):
    a=np.asarray(im.convert("RGBA"))
    lum=a[:,:,:3].mean(axis=2); alpha=a[:,:,3]
    ink=(alpha>110)&(lum<128)
    H,W=ink.shape
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
    lab=np.zeros((H,W),np.int32); cur=0; sz={}
    for sy,sx in np.argwhere(enc):
        if lab[sy,sx]: continue
        cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0
        while q:
            y,x=q.popleft(); n+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<H and 0<=nx<W and enc[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=cur; q.append((ny,nx))
        sz[cur]=n
    best=max(sz.items(),key=lambda kv:kv[1])[0]
    return lab==best

def fit_word(ribimg, face, wm, margin=10, clearance_iters=5):
    """Largest scale whose BENT wordmark lies wholly inside the band face."""
    H,W=face.shape; SW,SH=wm.size
    cx=[];cy=[];hh=[]
    for x in range(W):
        ys=np.where(face[:,x])[0]
        if len(ys)>8: cx.append(x); cy.append((ys[0]+ys[-1])/2.); hh.append((ys[-1]-ys[0])/2.)
    cx=np.array(cx,float);cy=np.array(cy,float);hh=np.array(hh,float)
    lo,hi=np.percentile(cx,[4,96]); sel=(cx>=lo)&(cx<=hi)
    CO=np.polyfit(cx[sel],cy[sel],4); DCO=np.polyder(CO)
    mid=(lo+hi)/2.
    faceimg=Image.fromarray((face*255).astype(np.uint8))

    def attempt(s):
        w2=wm.resize((max(8,int(SW*s)),max(2,int(SH*s))),Image.LANCZOS)
        xoff=mid-w2.width/2.
        bw,ox,oy=bend_poly(w2, lambda t: np.polyval(CO,np.asarray(t)+xoff),
                               lambda t: np.polyval(DCO,np.asarray(t)+xoff))
        px=int(round(xoff+ox)); py=int(round(oy))
        canvas=Image.new("L",(W,H),0)
        a=Image.fromarray((np.asarray(bw)[:,:,3]>40).astype(np.uint8)*255)
        canvas.paste(a,(px,py))
        grown=canvas
        for _ in range(clearance_iters):
            grown=grown.filter(ImageFilter.MaxFilter(margin//clearance_iters*2+1))
        g=np.asarray(grown)>0
        ok = not (g & ~face).any()
        return ok,bw,px,py

    glo,ghi=0.05,1.6
    best=None
    for _ in range(16):
        s=(glo+ghi)/2.
        ok,bw,px,py=attempt(s)
        if ok: best=(s,bw,px,py); glo=s
        else:  ghi=s
    if best is None: raise SystemExit("no containable scale")
    s,bw,px,py=best
    s*=0.93
    ok,bw,px,py=attempt(s)
    out=ribimg.copy(); out.alpha_composite(bw,(px,py))
    return out, s

def textimg(txt,px,track):
    f=ImageFont.truetype(FONT,px); adv=[(c,f.getlength(c)) for c in txt]
    tot=sum(w for _,w in adv)+track*(len(txt)-1); asc,desc=f.getmetrics()
    im=Image.new("RGBA",(int(tot)+40,asc+desc+40),(0,0,0,0)); d=ImageDraw.Draw(im); x=20
    for c,w in adv: d.text((x,20),c,font=f,fill=(0,0,0,255)); x+=w+track
    a=np.asarray(im)[:,:,3]; yy=np.where(a.any(axis=1))[0]; xx=np.where(a.any(axis=0))[0]
    return im.crop((xx[0],yy[0],xx[-1]+1,yy[-1]+1))

T1=ribbon_bw(6.0); f1=face_of(T1)
WM=Image.open(HERE+"/schrift-bw.png").convert("RGBA")
t1,fill1=fit_word(T1,f1,WM,margin=14)
print("tier1",T1.size,"scale %.3f"%fill1)

T2=ribbon_bw(2.55); f2=face_of(T2)
MI=textimg("MADE IN ITALY", 150, 40)
t2,fill2=fit_word(T2,f2,MI,margin=10)
print("tier2",T2.size,"scale %.3f"%fill2)

# lowest ink of the WORD inside tier one, per column
d=(np.asarray(t1).astype(int)-np.asarray(T1).astype(int))
wordmask=np.abs(d).sum(axis=2)>30
wb=np.full(t1.width,-1)
for x in range(t1.width):
    ys=np.where(wordmask[:,x])[0]
    if len(ys): wb[x]=ys[-1]
# topmost ink of tier two, per column
t2a=np.asarray(t2); t2ink=(t2a[:,:,3]>110)&(t2a[:,:,:3].mean(axis=2)<128)
tt=np.full(t2.width,10**9)
for x in range(t2.width):
    ys=np.where(t2ink[:,x])[0]
    if len(ys): tt[x]=ys[0]
PAD=90
CW=max(t1.width,t2.width)+2*PAD
x1=(CW-t1.width)//2; x2=(CW-t2.width)//2
CLEAR=16
need=0
for x in range(t2.width):
    if tt[x]>10**8: continue
    gx=x+x2-x1
    if 0<=gx<t1.width and wb[gx]>=0:
        need=max(need, wb[gx]+CLEAR-tt[x])
TOP2=int(need)
CH=max(t1.height, TOP2+t2.height)+2*PAD
cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
cv.alpha_composite(t1,(x1, PAD))
cv.alpha_composite(t2,(x2, PAD+TOP2))
print("tier2 top offset",TOP2,"of tier1 height",t1.height)
cv.convert("RGB").save(HERE+"/lockup.png")
print("lockup",cv.size)
