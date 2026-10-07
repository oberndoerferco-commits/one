# cleanup.py BLACK_IMG COLOUR_IMG OUT
# Tidies a colour photograph of the Leather Watch Box without replacing anything in it:
# 1) framing: scales and moves the box so its outline matches the black photograph of the same view;
# 2) a gentle unsharp mask for the grain and studs;
# 3) a little more contrast in the neutral, bright hardware (the silver lock, hinges and studs).
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

def bbox(img):
    a=np.asarray(img.convert('RGB')).astype(float)
    bg=np.median(np.concatenate([a[:20,:20].reshape(-1,3),a[:20,-20:].reshape(-1,3),a[-20:,:20].reshape(-1,3),a[-20:,-20:].reshape(-1,3)]),axis=0)
    d=np.abs(a-bg).sum(axis=2)>30
    d=ndi.binary_opening(d,iterations=3)
    lab,n=ndi.label(d)
    if n==0: return None,bg
    sizes=ndi.sum(d,lab,range(1,n+1)); keep=np.isin(lab,1+np.where(sizes>0.02*sizes.max())[0])
    ys,xs=np.where(keep)
    return (xs.min(),ys.min(),xs.max(),ys.max()),bg

def main(bp,cp,op,amount=0.9,radius=2.5,metal_gain=1.22):
    b=Image.open(bp).convert('RGB'); c=Image.open(cp).convert('RGB')
    if c.size!=b.size: c=c.resize(b.size,Image.LANCZOS)
    bb,_=bbox(b); cb,bg=bbox(c)
    W,H=b.size
    # scale by the outline's width and height average, place at the black's centre
    s=((bb[2]-bb[0])/(cb[2]-cb[0])+(bb[3]-bb[1])/(cb[3]-cb[1]))/2
    nc=c.resize((round(W*s),round(H*s)),Image.LANCZOS)
    ccx=(cb[0]+cb[2])/2*s; ccy=(cb[1]+cb[3])/2*s
    bcx=(bb[0]+bb[2])/2; bcy=(bb[1]+bb[3])/2
    canvas=Image.new('RGB',(W,H),tuple(int(v) for v in bg))
    canvas.paste(nc,(round(bcx-ccx),round(bcy-ccy)))
    # gentle sharpening
    sharp=canvas.filter(ImageFilter.UnsharpMask(radius=radius*W/3464,percent=int(amount*100),threshold=2))
    a=np.asarray(sharp).astype(float)/255
    # hardware: neutral and bright pixels inside the box
    mx=a.max(2); mn=a.min(2); sat=(mx-mn)/np.maximum(mx,1e-3)
    obj=np.zeros(a.shape[:2],bool); x0=max(0,round(bcx-(bb[2]-bb[0])/2)); x1=min(W,round(bcx+(bb[2]-bb[0])/2)); y0=max(0,round(bcy-(bb[3]-bb[1])/2)); y1=min(H,round(bcy+(bb[3]-bb[1])/2)); obj[y0:y1,x0:x1]=True
    metal=(sat<0.12)&(mx>0.45)&obj
    metal=ndi.binary_opening(metal,iterations=1)
    m=ndi.gaussian_filter(metal.astype(float),1.5)[...,None]
    lum=a.mean(2,keepdims=True)
    con=np.clip(0.55+(a-0.55)*metal_gain,0,1)
    out=a*(1-m)+con*m
    Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8)).save(op,quality=94,subsampling=0)
    print(op,'scale',round(s,3),'black box',bb,'colour box',cb)

main(*sys.argv[1:4])
