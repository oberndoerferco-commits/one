import numpy as np, math, sys, importlib.util
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
spec=importlib.util.spec_from_file_location("lk",H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
t1,f1 = lk.t1, lk.f1
RW,RH=t1.size
MII=Image.open(H+"/mii.png").convert("RGBA")
STROKE=18

prof=np.load(H+"/swag-profile.npy")
pt,pd = prof[0], prof[1]
# symmetrise and smooth the traced profile
grid=np.linspace(-1,1,401)
d1=np.interp(grid,pt,pd); d2=np.interp(-grid,pt,pd)
d=(d1+d2)/2.0
k=15; ker=np.ones(k)/k
d=np.convolve(np.pad(d,(k,k),mode='edge'),ker,mode='same')[k:-k]
d=np.clip(d,0,None); d/=d.max()

ybf=np.full(RW,-1)
for x in range(RW):
    ys=np.where(f1[:,x])[0]
    if len(ys): ybf[x]=ys[-1]
valid=np.where(ybf>=0)[0]; cxm=(valid[0]+valid[-1])//2

SPAN=int(RW*0.42)
DEPTH=int(SPAN*0.21)
xa,xb=cxm-SPAN//2, cxm+SPAN//2
# where does the ribbon's OUTLINE actually end at the centre?
t1ink=(np.asarray(t1)[:,:,3]>40)&(np.asarray(t1)[:,:,:3].mean(axis=2)<140)
y=int(ybf[cxm])
while y+1<RH and t1ink[y+1,cxm]: y+=1
EDGE=y
FLAT=DEPTH*float(np.interp(0.5,grid,d))      # depth of the flat run
avail=(ybf[cxm]+FLAT)-EDGE-STROKE
print("edge",EDGE,"face bottom",ybf[cxm],"flat depth %.0f"%FLAT,"avail",avail)
sc=min((SPAN*0.78)/MII.width, (avail*0.76)/MII.height)
mii=MII.resize((max(1,int(MII.width*sc)),max(1,int(MII.height*sc))),Image.LANCZOS)

PAD=110
CW=RW+2*PAD; CH=RH+2*PAD+DEPTH+120
cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
top=[];bot=[]
for x in range(xa,xb+1):
    t=(x-cxm)/(SPAN/2.0)
    yt=ybf[x]
    yb=yt+DEPTH*float(np.interp(t,grid,d))
    top.append((PAD+x,PAD+yt)); bot.append((PAD+x,PAD+yb))
sw=Image.new("RGBA",(CW,CH),(0,0,0,0)); dr=ImageDraw.Draw(sw)
dr.polygon(top+bot[::-1], fill=(255,255,255,255))
dr.line(bot, fill=(0,0,0,255), width=STROKE, joint="curve")
cv.alpha_composite(sw,(0,0))
ytxt = PAD+EDGE + (avail - mii.height)/2
cv.alpha_composite(mii,((CW-mii.width)//2, int(ytxt)))
cv.alpha_composite(t1,(PAD,PAD))
a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
P=60
cv.convert("RGB").crop((max(0,xx[0]-P),max(0,yy[0]-P),min(CW,xx[-1]+P),min(CH,yy[-1]+P))).save(H+"/mark-swag2.png")
print("span",SPAN,"depth",DEPTH,"text",mii.size,"->",Image.open(H+"/mark-swag2.png").size)
