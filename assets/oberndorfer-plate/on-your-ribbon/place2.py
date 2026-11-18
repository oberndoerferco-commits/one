import numpy as np, math, os, sys
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))

rib=Image.open(HERE+"/r04-trim.png").convert("RGBA")
face=np.asarray(Image.open(HERE+"/r04-face.png").convert("L"))>127
H,W=face.shape
WM=Image.open(HERE+"/wm.png"); SW,SH=WM.size

# measured centreline + half-thickness, per column
cx=[];cy=[];hh=[]
for x in range(W):
    ys=np.where(face[:,x])[0]
    if len(ys)>6: cx.append(x); cy.append((ys[0]+ys[-1])/2.0); hh.append((ys[-1]-ys[0])/2.0)
cx=np.array(cx,float); cy=np.array(cy,float); hh=np.array(hh,float)
lo,hi=np.percentile(cx,[3,97]); sel=(cx>=lo)&(cx<=hi)
CO=np.polyfit(cx[sel],cy[sel],4); DCO=np.polyder(CO)
print("centreline deg4 fitted over %d..%d"%(lo,hi))
pc=lambda x: np.polyval(CO,x); pd=lambda x: np.polyval(DCO,x)
# perpendicular half-thickness
perp=np.interp(np.arange(W),cx,hh)*np.cos(np.arctan(pd(np.arange(W))))

def bend_poly(img, p, dp, pad=30, iters=6):
    src=np.asarray(img.convert("RGBA")).astype(np.float32)/255.0
    h,w,_=src.shape
    P=np.concatenate([src[:,:,:3]*src[:,:,3:4], src[:,:,3:4]],axis=2)
    xs_=np.arange(-pad,w+pad,dtype=np.float32)
    yv=p(xs_); y0=float(yv.min()-h/2-pad); y1=float(yv.max()+h/2+pad)
    OW=len(xs_); OH=int(math.ceil(y1-y0))
    Xg,Yg=np.meshgrid(xs_, np.arange(OH,dtype=np.float32)+y0)
    x=Xg.copy()
    for _ in range(iters):
        th=np.arctan(dp(x)); c=np.cos(th); s=np.sin(th)
        v=(Yg-p(x))/np.maximum(c,1e-6)
        x=Xg+v*s
    th=np.arctan(dp(x)); v=(Yg-p(x))/np.maximum(np.cos(th),1e-6)
    ys=v+h/2.0
    x0i=np.floor(x).astype(np.int32); y0i=np.floor(ys).astype(np.int32)
    fx=(x-x0i)[...,None]; fy=(ys-y0i)[...,None]
    def at(ix,iy):
        ok=(ix>=0)&(ix<w)&(iy>=0)&(iy<h)
        return P[np.clip(iy,0,h-1),np.clip(ix,0,w-1)]*ok[...,None]
    o=(at(x0i,y0i)*(1-fx)+at(x0i+1,y0i)*fx)*(1-fy)+(at(x0i,y0i+1)*(1-fx)+at(x0i+1,y0i+1)*fx)*fy
    al=np.clip(o[:,:,3:4],0,1)
    col=np.where(al>1e-5,o[:,:,:3]/np.maximum(al,1e-5),0.0)
    im=Image.fromarray((np.concatenate([np.clip(col,0,1),al],axis=2)*255).astype(np.uint8),"RGBA")
    return im, -pad, y0

MARGIN=10.0
best=None
for L in range(600,1500,4):
    xa,xb=None,None
    # centre the span on the middle of the usable range
    mid=(lo+hi)/2.0; xa,xb=mid-L/2.0, mid+L/2.0
    if xa<lo+6 or xb>hi-6: continue
    av=perp[int(xa):int(xb)+1]
    s=L/SW
    if s*SH/2.0 <= av.min()-MARGIN: best=(L,s,av.min(),mid)
L,s,avmin,mid=best
print("span %.0f scale %.3f half-h %.1f band %.1f fill %.0f%%"%(L,s,s*SH/2,avmin,100*(s*SH/2)/avmin))

wm=WM.resize((int(SW*s),int(SH*s)),Image.LANCZOS)
xoff=mid-wm.width/2.0
p  = lambda xl: np.polyval(CO,  np.asarray(xl)+xoff)
dp = lambda xl: np.polyval(DCO, np.asarray(xl)+xoff)
bw,ox,oy=bend_poly(wm,p,dp)
out=rib.copy(); out.alpha_composite(bw,(int(round(xoff+ox)),int(round(oy))))
bg=Image.new("RGB",out.size,(255,255,255)); bg.paste(out,(0,0),out)
bg.save(HERE+"/r04-fitted.png"); print("saved",bg.size)
