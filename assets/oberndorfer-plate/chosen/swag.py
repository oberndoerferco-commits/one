import numpy as np, math, sys, importlib.util
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
spec=importlib.util.spec_from_file_location("lk",H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
t1,f1 = lk.t1, lk.f1
RW,RH=t1.size
MII=Image.open(H+"/mii.png").convert("RGBA")
STROKE=20

# the ribbon's band-face bottom edge, per column
ybot_face=np.full(RW,-1)
for x in range(RW):
    ys=np.where(f1[:,x])[0]
    if len(ys): ybot_face[x]=ys[-1]
valid=np.where(ybot_face>=0)[0]
cxm=(valid[0]+valid[-1])//2

SPAN=int(RW*0.50)
xa,xb=cxm-SPAN//2, cxm+SPAN//2
sc=(SPAN*0.66)/MII.width
mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
DEPTH=mii.height+150

PAD=110
CW=RW+2*PAD; CH=RH+PAD*2+260
cv=Image.new("RGBA",(CW,CH),(255,255,255,255))

top=[]; bot=[]
for x in range(xa,xb+1):
    t=(x-cxm)/(SPAN/2.0)
    yt=ybot_face[x]
    yb=yt+DEPTH*max(0.0,(1-abs(t)))**0.72
    top.append((PAD+x, PAD+yt)); bot.append((PAD+x, PAD+yb))

sw=Image.new("RGBA",(CW,CH),(0,0,0,0)); d=ImageDraw.Draw(sw)
d.polygon(top+bot[::-1], fill=(255,255,255,255))
d.line(bot, fill=(0,0,0,255), width=STROKE, joint="curve")
cv.alpha_composite(sw,(0,0))

# text sits in the swag, centred between the ribbon edge and the dip
ymid=PAD+ybot_face[cxm]+ (DEPTH-mii.height)*0.40
cv.alpha_composite(mii,((CW-mii.width)//2, int(ymid)))
cv.alpha_composite(t1,(PAD,PAD))

a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
P=60
cv.convert("RGB").crop((max(0,xx[0]-P),max(0,yy[0]-P),
                        min(CW,xx[-1]+P),min(CH,yy[-1]+P))).save(H+"/mark-swag.png")
print("saved", Image.open(H+"/mark-swag.png").size)
