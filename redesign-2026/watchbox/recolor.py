# recolor.py BLACK_IMG TARGET_IMG OUT
# Rebuilds a colour variant of the Leather Watch Box from the black original photograph. Only the
# leather is recoloured, to the target's leather colour; the leather's grain and its shading are each
# scaled to match the target photograph. Hardware (with the dark reflections in the chrome), studs,
# the Alcantara lining and the background come straight from the black original.
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color

def labf(img): return color.rgb2lab(np.asarray(img).astype(np.float64)/255.0)

def iqr(x): return float(np.subtract(*np.percentile(x,[75,25])))

def split(L, sigma):
    low=ndi.gaussian_filter(L, sigma); return low, L-low

def target_stats(t):
    a=np.asarray(t).astype(np.float64)/255.0
    hsv=color.rgb2hsv(a); Lab=color.rgb2lab(a)
    m=(hsv[...,1]>0.18)&(hsv[...,2]<0.97)
    if m.sum()<1000: m=hsv[...,2]<0.5
    m=ndi.binary_erosion(m,iterations=3)
    sig=t.size[0]/250
    low,high=split(Lab[...,0],sig)
    return np.median(Lab[m],axis=0), iqr(low[m]), iqr(high[m])

def main(bp,tp,op):
    b=Image.open(bp).convert('RGB'); t=Image.open(tp).convert('RGB')
    B=labf(b); Lb=B[...,0]; Hh,Ww=Lb.shape
    # leather weight: dark pixels are leather; mid-tones (the leather's sheen) count as leather too
    # unless they sit right next to something bright (lining, hardware), where they are an edge
    rr=max(2,int(Ww/700))
    near=ndi.distance_transform_edt(~(Lb>52))<rr
    w=np.where(near, 1.0-np.clip((Lb-22.0)/12.0,0,1), 1.0-np.clip((Lb-40.0)/14.0,0,1))
    # hardware: bright pixels inside the object, closed and hole-filled (keeps chrome reflections)
    r=max(2,int(Ww/600))
    bright=Lb>45
    lab_,n=ndi.label(bright)
    border=set(np.unique(np.concatenate([lab_[0],lab_[-1],lab_[:,0],lab_[:,-1]])))-{0}
    metal=bright&~np.isin(lab_,list(border))
    closed=ndi.binary_closing(metal,structure=np.ones((2*r+1,2*r+1)),iterations=2)
    holes=ndi.binary_fill_holes(closed)&~closed
    hl,hn=ndi.label(holes)
    if hn:
        sizes=ndi.sum(holes,hl,range(1,hn+1))
        small=np.isin(hl,1+np.where(sizes<0.002*Ww*Hh)[0])   # chrome reflections, not the lid label
    else:
        small=np.zeros_like(holes)
    hw=closed|small
    w=w*(1-ndi.gaussian_filter(hw.astype(float),r/2))
    lm=w>0.95
    sig=Ww/250
    # shading from leather pixels only (normalised blur), so the bright lining and hardware do not
    # leak into the leather near their edges
    mk=(w>0.5).astype(float)
    num=ndi.gaussian_filter(Lb*mk,sig); den=ndi.gaussian_filter(mk,sig)
    lowb=np.where(den>1e-3,num/np.maximum(den,1e-3),Lb)
    highb=np.where(mk>0,Lb-lowb,0.0)
    tmed,tlow,thigh=target_stats(t)
    bmed=np.median(Lb[lm])
    g_t=float(np.clip(thigh/max(iqr(highb[lm]),1e-3),0.8,3.0))
    g_s=float(np.clip(tlow/max(iqr(lowb[lm]),1e-3),0.8,2.2))
    N=np.empty_like(B)
    N[...,0]=np.clip(tmed[0]+(lowb-bmed)*g_s+highb*g_t,0,100)
    rel=np.clip(N[...,0]/max(tmed[0],1e-3),0.45,1.2)
    N[...,1]=tmed[1]*rel; N[...,2]=tmed[2]*rel
    out=(np.asarray(b).astype(np.float64)/255.0)*(1-w[...,None])+color.lab2rgb(N)*w[...,None]
    Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8)).save(op,quality=95,subsampling=0)
    print(op,'target',np.round(tmed,1),'grain x',round(g_t,2),'shade x',round(g_s,2))

main(*sys.argv[1:4])
