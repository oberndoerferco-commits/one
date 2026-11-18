import numpy as np, math, sys, importlib.util
from PIL import Image, ImageDraw
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
spec=importlib.util.spec_from_file_location("lk",H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
t1,f1 = lk.t1, lk.f1
RW,RH=t1.size
cxm=RW//2
band_bottom=np.where(f1[:,cxm])[0][-1]
alpha=np.asarray(t1)[:,:,3]
probe=min(RH-1,band_bottom+150); row=alpha[probe]>40
l=cxm
while l>0 and not row[l]: l-=1
r=cxm
while r<RW-1 and not row[r]: r+=1
GAP=r-l
STROKE=20
MII=Image.open(H+"/mii.png").convert("RGBA")

def panel(kind, PW, PH, dip, inset, stroke=STROKE):
    pad=stroke*3
    W=PW+2*pad; Hh=PH+dip+2*pad
    im=Image.new("RGBA",(W,Hh),(0,0,0,0)); d=ImageDraw.Draw(im)
    X=lambda v: v+pad
    Y=lambda v: v+pad
    pts=[(X(0),Y(0)),(X(PW),Y(0))]            # top edge
    # right side down to the bottom-right corner
    brx,bry = PW-inset, PH
    blx,bly = inset, PH
    if kind=="tips":
        pts += [(X(brx+26),Y(bry+34))]
        corner_r=[(X(brx+26),Y(bry+34))]
        corner_l=[(X(blx-26),Y(bly+34))]
    elif kind=="chamfer":
        ch=46
        pts += [(X(brx+ch),Y(bry-ch)),(X(brx),Y(bry))]
        corner_r=[(X(brx),Y(bry))]; corner_l=[(X(blx),Y(bly))]
    else:  # scroll
        pts += [(X(brx),Y(bry))]
        c=[]
        for k in range(13):
            th=math.radians(-80+k*22); rr=40-k*2.0
            c.append((X(brx-6+rr*math.cos(th)), Y(bry-10+rr*math.sin(th))))
        pts += c; corner_r=[c[-1]]; corner_l=None
    # swagged bottom, right -> left, dipping to a point at centre
    swag=[]
    for k in range(121):
        t=k/120.0
        x=brx+(blx-brx)*t
        y=PH+dip*(1-abs(2*t-1))**0.75
        swag.append((X(x),Y(y)))
    pts += swag
    if kind=="tips":
        pts += [(X(blx-26),Y(bly+34))]
    elif kind=="chamfer":
        ch=46
        pts += [(X(blx),Y(bly)),(X(blx-ch),Y(bly-ch))]
    else:
        c=[]
        for k in range(13):
            th=math.radians(260-k*22); rr=40-k*2.0
            c.append((X(blx+6+rr*math.cos(th)), Y(bly-10+rr*math.sin(th))))
        pts += c
    d.polygon(pts, fill=(255,255,255,255))
    d.line(pts+[pts[0]], fill=(0,0,0,255), width=stroke, joint="curve")
    return im

PW=int(GAP*0.74); INSET=int(PW*0.055); DIP=74
sc=(PW-2*int(PW*0.13))/MII.width
mii=MII.resize((int(MII.width*sc),int(MII.height*sc)),Image.LANCZOS)
PH=mii.height+120
TUCK=78
PAD=90
outs=[]
for kind,name in (("tips","A-tips"),("chamfer","B-chamfer"),("scroll","C-scroll")):
    pn=panel(kind,PW,PH,DIP,INSET)
    CW=RW+2*PAD; CH=max(PAD+RH, PAD+band_bottom-TUCK+pn.height)+PAD
    cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
    px=(CW-pn.width)//2; py=PAD+band_bottom-TUCK
    cv.alpha_composite(pn,(px,py))
    cv.alpha_composite(mii,((CW-mii.width)//2, py+STROKE*3+TUCK+(PH-TUCK-mii.height)//2))
    cv.alpha_composite(t1,(PAD,PAD))
    a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
    yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
    P=60
    c=cv.convert("RGB").crop((max(0,xx[0]-P),max(0,yy[0]-P),min(CW,xx[-1]+P),min(CH,yy[-1]+P)))
    c.save(H+"/panel-"+name+".png"); outs.append((name,c)); print(name, c.size)
