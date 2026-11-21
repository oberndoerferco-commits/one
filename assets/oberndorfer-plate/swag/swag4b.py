import numpy as np, math, sys, importlib.util
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
spec=importlib.util.spec_from_file_location("lk",H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
t1,f1=lk.t1,lk.f1
RW,RH=t1.size
MII=Image.open(H+"/mii.png").convert("RGBA")
STROKE=18

ybf=np.full(RW,-1.0)
for x in range(RW):
    ys=np.where(f1[:,x])[0]
    if len(ys): ybf[x]=ys[-1]
valid=np.where(ybf>=0)[0]; cxm=(valid[0]+valid[-1])//2
ink=(np.asarray(t1)[:,:,3]>40)&(np.asarray(t1)[:,:,:3].mean(axis=2)<140)
y=int(ybf[cxm])
while y+1<RH and ink[y+1,cxm]: y+=1
EDGE=y
PAD=120

def canvas(extra=320):
    CW=RW+2*PAD; CH=RH+2*PAD+extra
    return Image.new("RGBA",(CW,CH),(255,255,255,255)),CW,CH

def finish(cv,CW,CH,name):
    cv.alpha_composite(t1,(PAD,PAD))
    a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
    yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
    Q=60
    out=cv.convert("RGB").crop((max(0,xx[0]-Q),max(0,yy[0]-Q),min(CW,xx[-1]+Q),min(CH,yy[-1]+Q)))
    out.save(H+"/v-"+name+".png"); print(name,out.size)

# ---------- 1. scalloped festoon ----------
def festoon():
    cv,CW,CH=canvas()
    SPAN=int(RW*0.46); xa,xb=cxm-SPAN//2,cxm+SPAN//2
    DMIN=110; DAMP=86; LOBES=3
    top=[];bot=[]
    for x in range(xa,xb+1):
        t=(x-cxm)/(SPAN/2.0); u=(t+1)/2.0
        env=1-abs(t)**7
        fr=(u*LOBES)%1.0
        dep=env*(DMIN+DAMP*math.sin(math.pi*fr)**0.7)
        top.append((PAD+x,PAD+ybf[x])); bot.append((PAD+x,PAD+ybf[x]+dep))
    d=ImageDraw.Draw(cv)
    d.polygon(top+bot[::-1], fill=(255,255,255,255))
    d.line(bot, fill=(0,0,0,255), width=STROKE, joint="curve")
    avail=DMIN-STROKE-10
    sc=min((SPAN*0.70)/MII.width,(avail*0.80)/MII.height)
    mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
    cv.alpha_composite(mii,((CW-mii.width)//2,int(PAD+EDGE+(avail-mii.height)/2)))
    finish(cv,CW,CH,"festoon")

# ---------- 2. hanging pendant ----------
def pendant():
    cv,CW,CH=canvas(420)
    PW=int(RW*0.30); PH=int(PW*0.52)
    x0=cxm-PW//2
    ytop=int(ybf[cxm])-26
    pts=[]
    for i in range(61):                     # left side down
        u=i/60.0; pts.append((PAD+x0, PAD+ytop+u*PH*0.52))
    for i in range(121):                    # bottom curve to a point
        u=i/120.0
        xx=x0+u*PW
        yy=ytop+PH*0.52+ (PH*0.48)*math.sin(math.pi*u)**0.85
        pts.append((PAD+xx,PAD+yy))
    for i in range(61):
        u=i/60.0; pts.append((PAD+x0+PW, PAD+ytop+PH*0.52-u*PH*0.52))
    d=ImageDraw.Draw(cv)
    d.polygon(pts, fill=(255,255,255,255))
    d.line(pts+[pts[0]], fill=(0,0,0,255), width=STROKE, joint="curve")
    sc=(PW*0.74)/MII.width
    mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
    cv.alpha_composite(mii,((CW-mii.width)//2, int(PAD+max(EDGE+22, ytop+PH*0.40-mii.height/2))))
    finish(cv,CW,CH,"pendant")

# ---------- 3. no container ----------
def bare():
    cv,CW,CH=canvas(300)
    sc=(RW*0.34)/MII.width
    mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
    ty=PAD+EDGE+86
    cv.alpha_composite(mii,((CW-mii.width)//2,ty))
    d=ImageDraw.Draw(cv)
    cy=ty+mii.height//2
    for sgn in (-1,1):
        ox=CW//2+sgn*(mii.width//2+46); r=12
        d.polygon([(ox,cy-r),(ox+r,cy),(ox,cy+r),(ox-r,cy)], fill=(0,0,0,255))
    finish(cv,CW,CH,"bare")

pendant()
