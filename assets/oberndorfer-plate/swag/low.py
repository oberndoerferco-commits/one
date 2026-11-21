import numpy as np, math, sys, importlib.util
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
spec=importlib.util.spec_from_file_location("lk",H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
t1=lk.t1
RW,RH=t1.size
MII=Image.open(H+"/mii.png").convert("RGBA")
STROKE=18
PAD=120
ink=(np.asarray(t1)[:,:,3]>40)&(np.asarray(t1)[:,:,:3].mean(axis=2)<140)
# bottom of the whole ribbon (the tails)
rows=np.where(ink.any(axis=1))[0]; BOT=rows[-1]
print("ribbon",RW,RH,"tails bottom",BOT)

SPAN=int(RW*0.40); xa,xb=RW//2-SPAN//2, RW//2+SPAN//2
sc=(SPAN*0.86)/MII.width
mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
BH=int(mii.height*2.05)                 # band depth, tight to the text
YC=int(BOT-RH*0.20)                     # sit low, lapping the tails
ARC=26

CW=RW+2*PAD; CH=RH+2*PAD+160
cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
cv.alpha_composite(t1,(PAD,PAD))

def edge(off):
    pts=[]
    for x in range(xa,xb+1):
        t=(x-RW/2)/(SPAN/2.0)
        pts.append((PAD+x, PAD+YC+off+ARC*(t*t)))
    return pts
top=edge(-BH//2); bot=edge(BH//2)
ban=Image.new("RGBA",(CW,CH),(0,0,0,0)); d=ImageDraw.Draw(ban)
# forked ends
ltx,lty=top[0]; lbx,lby=bot[0]
rtx,rty=top[-1]; rbx,rby=bot[-1]
TL=84; NOTCH=40
left=[(ltx,lty),(ltx-TL,lty-14),(ltx-TL+NOTCH,(lty+lby)/2),(ltx-TL,lby+14),(lbx,lby)]
right=[(rtx,rty),(rtx+TL,rty-14),(rtx+TL-NOTCH,(rty+rby)/2),(rtx+TL,rby+14),(rbx,rby)]
poly=left[::-1]+top+right+bot[::-1]
d.polygon(poly, fill=(255,255,255,255))
d.line(poly+[poly[0]], fill=(0,0,0,255), width=STROKE, joint="curve")
cv.alpha_composite(ban,(0,0))
cv.alpha_composite(mii,((CW-mii.width)//2, int(PAD+YC-mii.height/2+ARC*0.30)))

a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
Q=60
cv.convert("RGB").crop((max(0,xx[0]-Q),max(0,yy[0]-Q),min(CW,xx[-1]+Q),min(CH,yy[-1]+Q))).save(H+"/v-low.png")
print("saved", Image.open(H+"/v-low.png").size)
