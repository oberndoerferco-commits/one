import numpy as np, math, os, sys
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from allrib import bend_poly
rib=Image.open(HERE+"/chosen-big.png").convert("RGBA")
face=np.asarray(Image.open(HERE+"/chosen-face.png").convert("L"))>127
H,W=face.shape
WM=Image.open(HERE+"/"+sys.argv[1]); SW,SH=WM.size
cx=[];cy=[];hh=[]
for x in range(W):
    ys=np.where(face[:,x])[0]
    if len(ys)>8: cx.append(x); cy.append((ys[0]+ys[-1])/2.); hh.append((ys[-1]-ys[0])/2.)
cx=np.array(cx,float);cy=np.array(cy,float);hh=np.array(hh,float)
lo,hi=np.percentile(cx,[4,96]); sel=(cx>=lo)&(cx<=hi)
CO=np.polyfit(cx[sel],cy[sel],4); DCO=np.polyder(CO)
perp=np.interp(np.arange(W),cx,hh)*np.cos(np.arctan(np.polyval(DCO,np.arange(W))))
mid=(lo+hi)/2.; best=None
for L in range(500,2200,4):
    xa,xb=mid-L/2.,mid+L/2.
    if xa<lo+10 or xb>hi-10: continue
    s=L/SW
    if s*SH/2. <= np.percentile(perp[int(xa):int(xb)+1],3)-14: best=(L,s)
L,s=best
wm=WM.resize((int(SW*s),int(SH*s)),Image.LANCZOS); xoff=mid-wm.width/2.
bw,ox,oy=bend_poly(wm, lambda t: np.polyval(CO,np.asarray(t)+xoff),
                       lambda t: np.polyval(DCO,np.asarray(t)+xoff))
out=rib.copy(); out.alpha_composite(bw,(int(round(xoff+ox)),int(round(oy))))
bg=Image.new("RGB",out.size,(255,255,255)); bg.paste(out,(0,0),out)
bg.save(HERE+"/"+sys.argv[2])
print("span %d scale %.3f fill %.0f%%"%(L,s,100*(s*SH/2)/np.percentile(perp[int(mid-L/2):int(mid+L/2)],3)))
