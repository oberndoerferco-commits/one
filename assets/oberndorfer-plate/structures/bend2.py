import numpy as np, math
from PIL import Image

def bend(img, rise, pad=30, iters=6):
    """Bend RGBA along parabola y_c(x)=rise*t^2 (t=(x-cx)/hw). Inverse-mapped, bilinear."""
    src=np.asarray(img.convert("RGBA")).astype(np.float32)/255.0
    H,W,_=src.shape; cx=W/2.0; hw=W/2.0
    # premultiply alpha so edges don't fringe
    rgb=src[:,:,:3]*src[:,:,3:4]; a=src[:,:,3:4]
    P=np.concatenate([rgb,a],axis=2)

    yc   = lambda x: rise*(((x-cx)/hw)**2)
    dyc  = lambda x: 2.0*rise*(x-cx)/(hw*hw)

    y0=min(0.0, rise)-H/2.0-pad; y1=max(0.0,rise)+H/2.0+pad
    OW=W+2*pad; OH=int(math.ceil(y1-y0))
    Xg,Yg=np.meshgrid(np.arange(OW,dtype=np.float32)-pad,
                      np.arange(OH,dtype=np.float32)+y0)
    x=Xg.copy(); v=np.zeros_like(Xg)
    for _ in range(iters):
        th=np.arctan(dyc(x)); c=np.cos(th); s=np.sin(th)
        v=(Yg-yc(x))/np.maximum(c,1e-6)
        x=Xg+v*s
    ys=v+H/2.0; xs=x

    # bilinear sample
    x0i=np.floor(xs).astype(np.int32); y0i=np.floor(ys).astype(np.int32)
    fx=(xs-x0i)[...,None]; fy=(ys-y0i)[...,None]
    def at(ix,iy):
        ok=(ix>=0)&(ix<W)&(iy>=0)&(iy<H)
        ii=np.clip(ix,0,W-1); jj=np.clip(iy,0,H-1)
        out=P[jj,ii]; return out*ok[...,None]
    top=at(x0i,y0i)*(1-fx)+at(x0i+1,y0i)*fx
    bot=at(x0i,y0i+1)*(1-fx)+at(x0i+1,y0i+1)*fx
    o=top*(1-fy)+bot*fy
    al=np.clip(o[:,:,3:4],0,1)
    col=np.where(al>1e-5, o[:,:,:3]/np.maximum(al,1e-5), 0.0)
    out=np.concatenate([np.clip(col,0,1),al],axis=2)
    im=Image.fromarray((out*255).astype(np.uint8),"RGBA")
    arr=np.asarray(im)[:,:,3]
    yy=np.where(arr.any(axis=1))[0]; xx=np.where(arr.any(axis=0))[0]
    cropped=im.crop((xx[0],yy[0],xx[-1]+1,yy[-1]+1))
    # origin of cropped image expressed in the parabola frame
    return cropped, float(xx[0]-pad), float(yy[0]+y0)

if __name__=="__main__":
    HERE="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
    wm=Image.open(HERE+"/wm.png")
    b,ox,oy=bend(wm,110); print("origin",ox,oy); b.save(HERE+"/wm-bent.png")
    bg=Image.new("RGB",b.size,(255,255,255)); bg.paste(b,(0,0),b); bg.save(HERE+"/chk.png")
    print("bent",b.size)
