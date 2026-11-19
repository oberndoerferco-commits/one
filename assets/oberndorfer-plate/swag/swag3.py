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

prof=np.load(H+"/swag-profile.npy"); pt,pd=prof[0],prof[1]
grid=np.linspace(-1,1,401)
d=(np.interp(grid,pt,pd)+np.interp(-grid,pt,pd))/2.0
k=15; d=np.convolve(np.pad(d,(k,k),mode='edge'),np.ones(k)/k,mode='same')[k:-k]
d=np.clip(d,0,None); d/=d.max()

ybf=np.full(RW,-1.0)
for x in range(RW):
    ys=np.where(f1[:,x])[0]
    if len(ys): ybf[x]=ys[-1]
valid=np.where(ybf>=0)[0]; cxm=(valid[0]+valid[-1])//2
SPAN=int(RW*0.42); DEPTH=int(SPAN*0.21)
xa,xb=cxm-SPAN//2, cxm+SPAN//2
ink=(np.asarray(t1)[:,:,3]>40)&(np.asarray(t1)[:,:,:3].mean(axis=2)<140)
y=int(ybf[cxm])
while y+1<RH and ink[y+1,cxm]: y+=1
EDGE=y
FLAT=DEPTH*float(np.interp(0.5,grid,d))
avail=(ybf[cxm]+FLAT)-EDGE-STROKE

def curve(scale=1.0, lift=0.0):
    top=[];bot=[]
    for x in range(xa,xb+1):
        t=(x-cxm)/(SPAN/2.0)
        yt=ybf[x]
        yb=yt+ (DEPTH*float(np.interp(t,grid,d)))*scale - lift
        top.append((x,yt)); bot.append((x,yb))
    return top,bot

def normal_offset(bot, off):
    out=[]
    n=len(bot)
    for i,(x,yv) in enumerate(bot):
        i0=max(0,i-4); i1=min(n-1,i+4)
        dx=bot[i1][0]-bot[i0][0]; dy=bot[i1][1]-bot[i0][1]
        L=math.hypot(dx,dy) or 1.0
        nx,ny=-dy/L, dx/L          # upward normal
        out.append((x+nx*off, yv+ny*off))
    return out

def build(style):
    PAD=110
    CW=RW+2*PAD; CH=RH+2*PAD+DEPTH+140
    cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
    top,bot=curve()
    P=lambda pts:[(PAD+a,PAD+b) for a,b in pts]
    sw=Image.new("RGBA",(CW,CH),(0,0,0,0)); dr=ImageDraw.Draw(sw)
    dr.polygon(P(top)+P(bot)[::-1], fill=(255,255,255,255))
    dr.line(P(bot), fill=(0,0,0,255), width=STROKE, joint="curve")
    if style in ("rule","both"):
        inner=normal_offset(bot, 34)
        inner=[p for p in inner if xa+26 <= p[0] <= xb-26]
        dr.line(P(inner), fill=(0,0,0,255), width=max(5,STROKE//3), joint="curve")
    if style=="folds":
        for sgn,xe in ((-1,xa),(1,xb)):
            yt=ybf[xe]; yb=yt+DEPTH*float(np.interp(sgn*1.0,grid,d))
            w=86; h=70
            pts=[(xe,yt-4),(xe+sgn*w,yt-4),(xe+sgn*(w*0.45),yt+h),(xe,yt+h*0.75)]
            dr.polygon(P(pts), fill=(255,255,255,255))
            dr.line(P(pts+[pts[0]]), fill=(0,0,0,255), width=STROKE, joint="curve")
    sc=min((SPAN*0.72)/MII.width, (avail*0.74)/MII.height)
    mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
    cv.alpha_composite(sw,(0,0))
    tx=(CW-mii.width)//2; ty=int(PAD+EDGE+(avail-mii.height)/2)
    cv.alpha_composite(mii,(tx,ty))
    if style in ("fleuron","both"):
        cy=ty+mii.height//2
        for sgn in (-1,1):
            ox=CW//2+sgn*(mii.width//2+52)
            r=13
            dr2=ImageDraw.Draw(cv)
            dr2.polygon([(ox,cy-r),(ox+r,cy),(ox,cy+r),(ox-r,cy)], fill=(0,0,0,255))
    cv.alpha_composite(t1,(PAD,PAD))
    a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
    yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
    Q=60
    out=cv.convert("RGB").crop((max(0,xx[0]-Q),max(0,yy[0]-Q),min(CW,xx[-1]+Q),min(CH,yy[-1]+Q)))
    out.save(H+"/swag-"+style+".png"); print(style, out.size)

for st in ("rule","fleuron","both"): build(st)
