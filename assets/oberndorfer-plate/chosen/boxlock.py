import numpy as np, sys, os
from PIL import Image, ImageDraw, ImageFont
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
sys.path.insert(0,H)
import importlib.util
spec=importlib.util.spec_from_file_location("lk", H+"/lockup.py")
lk=importlib.util.module_from_spec(spec); spec.loader.exec_module(lk)
T1,f1,t1 = lk.T1, lk.f1, lk.t1          # ribbon, band face, ribbon+word
FONT="/home/user/one/assets/oberndorfer-plate/faces/d_cinzel.ttf"

RW,RH=t1.size
# band face bottom edge at the centre column
cxm=RW//2
ys=np.where(f1[:,cxm])[0]
band_bottom=ys[-1]
print("ribbon",t1.size,"band bottom at centre",band_bottom)

# measure the ribbon's outline weight so the box matches
row=np.asarray(t1.convert("L"))[band_bottom+1:band_bottom+40, cxm]
stroke=int((row<128).sum()) or 10
print("outline stroke ~",stroke,"px")

def textimg(txt,px,track):
    f=ImageFont.truetype(FONT,px); adv=[(c,f.getlength(c)) for c in txt]
    tot=sum(w for _,w in adv)+track*(len(txt)-1); asc,desc=f.getmetrics()
    im=Image.new("RGBA",(int(tot)+40,asc+desc+40),(0,0,0,0)); d=ImageDraw.Draw(im); x=20
    for c,w in adv: d.text((x,20),c,font=f,fill=(0,0,0,255)); x+=w+track
    a=np.asarray(im)[:,:,3]; yy=np.where(a.any(axis=1))[0]; xx=np.where(a.any(axis=0))[0]
    return im.crop((xx[0],yy[0],xx[-1]+1,yy[-1]+1))

# how much clear width is there between the ribbon's tails, below the band?
alpha=np.asarray(t1)[:,:,3]
probe=min(RH-1, band_bottom+150)
row=alpha[probe]>40
cxm2=RW//2
l=cxm2
while l>0 and not row[l]: l-=1
r=cxm2
while r<RW-1 and not row[r]: r+=1
gap=r-l
print("clear gap between tails at y=%d: %d px (x %d..%d)"%(probe,gap,l,r))

BOX_W=int(gap*0.80)
PADX,PADY=70,54
# size the text to the box
size=130
while True:
    MI=textimg("MADE IN ITALY", size, int(size*0.30))
    if MI.width <= BOX_W-2*PADX or size<=40: break
    size-=4
print("MADE IN ITALY at %dpx -> %dx%d, box %d wide"%(size,MI.width,MI.height,BOX_W))

VIS_H=MI.height+2*PADY
TUCK=80
BOX_H=VIS_H+TUCK

PAD=90
CW=RW+2*PAD
CH=max(PAD+RH, PAD+band_bottom-TUCK+BOX_H)+PAD
cv=Image.new("RGBA",(CW,CH),(255,255,255,255))
bx0=(CW-BOX_W)//2; by0=PAD+band_bottom-TUCK
box=Image.new("RGBA",(BOX_W,BOX_H),(0,0,0,0))
d=ImageDraw.Draw(box)
d.rectangle([0,0,BOX_W-1,BOX_H-1], fill=(255,255,255,255), outline=(0,0,0,255), width=stroke)
cv.alpha_composite(box,(bx0,by0))
ty=by0+TUCK+(VIS_H-MI.height)//2
cv.alpha_composite(MI,((CW-MI.width)//2, ty))
cv.alpha_composite(t1,(PAD,PAD))

a=np.asarray(cv.convert("RGB")).mean(axis=2); m=a<200
yy=np.where(m.any(axis=1))[0]; xx=np.where(m.any(axis=0))[0]
P=70
cv.convert("RGB").crop((max(0,xx[0]-P),max(0,yy[0]-P),
                        min(CW,xx[-1]+P),min(CH,yy[-1]+P))).save(H+"/mark-box.png")
print("saved", Image.open(H+"/mark-box.png").size)
