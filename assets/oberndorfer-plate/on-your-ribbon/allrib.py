import numpy as np, math, os, sys, collections
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
CF="/home/user/one/assets/oberndorfer-plate/canva-fit"
WM=Image.open(HERE+"/wm-gold.png"); SW,SH=WM.size

def clean_plate(pre):
    fs=[f"{CF}/{pre}_{i}-{n}.png" for i,n in ((1,"outlined"),(2,"engraved"),(3,"gold"),(4,"script"))]
    st=np.stack([np.asarray(Image.open(f).convert("RGB")).astype(np.int16) for f in fs])
    return Image.fromarray(st.max(axis=0).astype("uint8"))

def trim(rib):
    a=np.asarray(rib.convert("L")); cols=(a<90).mean(axis=0); right=rib.width
    for x in range(rib.width-1, rib.width-90, -1):
        if cols[x]>0.75: right=x
    return rib.crop((0,0,right,rib.height))

def band_face(rib):
    a=np.asarray(rib.convert("L")); H,W=a.shape; ink=a<150
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
    lab=np.zeros((H,W),np.int32); cur=0; best=(0,None)
    for sy,sx in np.argwhere(enc):
        if lab[sy,sx]: continue
        cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0
        while q:
            y,x=q.popleft(); n+=1
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<H and 0<=nx<W and enc[ny,nx] and not lab[ny,nx]:
                    lab[ny,nx]=cur; q.append((ny,nx))
        if n>best[0]: best=(n,cur)
    return lab==best[1], best[0]

def bend_poly(img,p,dp,pad=30,iters=6):
    src=np.asarray(img.convert("RGBA")).astype(np.float32)/255.0
    h,w,_=src.shape
    P=np.concatenate([src[:,:,:3]*src[:,:,3:4],src[:,:,3:4]],axis=2)
    xs_=np.arange(-pad,w+pad,dtype=np.float32); yv=p(xs_)
    y0=float(yv.min()-h/2-pad); y1=float(yv.max()+h/2+pad)
    Xg,Yg=np.meshgrid(xs_,np.arange(int(math.ceil(y1-y0)),dtype=np.float32)+y0)
    x=Xg.copy()
    for _ in range(iters):
        th=np.arctan(dp(x)); v=(Yg-p(x))/np.maximum(np.cos(th),1e-6); x=Xg+v*np.sin(th)
    th=np.arctan(dp(x)); v=(Yg-p(x))/np.maximum(np.cos(th),1e-6); ys=v+h/2.0
    xi=np.floor(x).astype(np.int32); yi=np.floor(ys).astype(np.int32)
    fx=(x-xi)[...,None]; fy=(ys-yi)[...,None]
    def at(ix,iy):
        ok=(ix>=0)&(ix<w)&(iy>=0)&(iy<h)
        return P[np.clip(iy,0,h-1),np.clip(ix,0,w-1)]*ok[...,None]
    o=(at(xi,yi)*(1-fx)+at(xi+1,yi)*fx)*(1-fy)+(at(xi,yi+1)*(1-fx)+at(xi+1,yi+1)*fx)*fy
    al=np.clip(o[:,:,3:4],0,1)
    col=np.where(al>1e-5,o[:,:,:3]/np.maximum(al,1e-5),0.0)
    return Image.fromarray((np.concatenate([np.clip(col,0,1),al],axis=2)*255).astype(np.uint8),"RGBA"), -pad, y0

for pre in ("r04","r06","r08"):
    rib=trim(clean_plate(pre)).convert("RGBA")
    face,npx=band_face(rib); H,W=face.shape
    cx=[];cy=[];hh=[]
    for x in range(W):
        ys=np.where(face[:,x])[0]
        if len(ys)>6: cx.append(x); cy.append((ys[0]+ys[-1])/2.); hh.append((ys[-1]-ys[0])/2.)
    cx=np.array(cx,float);cy=np.array(cy,float);hh=np.array(hh,float)
    lo,hi=np.percentile(cx,[3,97]); sel=(cx>=lo)&(cx<=hi)
    CO=np.polyfit(cx[sel],cy[sel],4); DCO=np.polyder(CO)
    perp=np.interp(np.arange(W),cx,hh)*np.cos(np.arctan(np.polyval(DCO,np.arange(W))))
    mid=(lo+hi)/2.; best=None
    for L in range(500,1600,4):
        xa,xb=mid-L/2.,mid+L/2.
        if xa<lo+6 or xb>hi-6: continue
        s=L/SW
        if s*SH/2. <= perp[int(xa):int(xb)+1].min()-10: best=(L,s)
    if not best: print(pre,"no fit"); continue
    L,s=best
    wm=WM.resize((int(SW*s),int(SH*s)),Image.LANCZOS); xoff=mid-wm.width/2.
    bw,ox,oy=bend_poly(wm, lambda t: np.polyval(CO,np.asarray(t)+xoff),
                           lambda t: np.polyval(DCO,np.asarray(t)+xoff))
    out=rib.copy(); out.alpha_composite(bw,(int(round(xoff+ox)),int(round(oy))))
    bg=Image.new("RGB",out.size,(255,255,255)); bg.paste(out,(0,0),out)
    bg.save(f"{HERE}/fit-{pre}.png")
    print(pre,"face",npx,"span",L,"fill %.0f%%"%(100*(s*SH/2)/perp[int(mid-L/2):int(mid+L/2)].min()))
