import cv2, numpy as np, sys, os
from base import shirt_alpha, lab, bgr
from extract import shirt_geom
from PIL import Image, ImageDraw, ImageFont
OUT=2400; CROP=1220
PINK={'front':'ref/u3870_8.jpg','back':'ref/u3870_9.jpg'}
GREY={'front':'ref/grey_front.jpg'}
def base(color, side):
    pink=cv2.imread(PINK[side]); a,fill=shirt_alpha(pink)
    src = cv2.imread(GREY[side]) if (color=='white' and side in GREY) else pink
    if src is not pink: a=cv2.erode(a,np.ones((3,3),np.uint8))
    Lab=lab(src); L=Lab[...,0]; Lm=np.median(L[a>0.99]); d=L-Lm
    if color=='black': Ln=np.clip(14+0.62*d,2,45); A,B=0.2,-0.5
    else:
        k=1.15 if side in GREY else 0.95
        Ln=np.clip(94.5+k*d,55,99.0); A,B=-0.2,0.8
        if side in GREY:  # lift the darker rim the grey photo has along the outline
            core=cv2.GaussianBlur(cv2.erode((a>0.5).astype(np.uint8),np.ones((15,15),np.uint8)).astype(np.float32),(0,0),4)
            band=np.clip((a>0.5)-core,0,1)
            Ln=Ln+band*np.maximum(0,93.0-Ln)*0.85
    shirt=bgr(np.dstack([Ln,np.full_like(Ln,A),np.full_like(Ln,B)]).astype(np.float32))
    g=lab(src); g[...,1]=0.3; g[...,2]=1.6
    gp=lab(pink); gp[...,1]=0.3; gp[...,2]=1.6
    bgest=bgr(gp)
    hole=cv2.dilate((a>0.02).astype(np.uint8),np.ones((9,9),np.uint8))
    bgest=cv2.inpaint(np.clip(bgest,0,255).astype(np.uint8),hole,7,cv2.INPAINT_TELEA).astype(np.float32)
    out=a[...,None]*shirt+(1-a[...,None])*bgest
    return out.astype(np.float32), a
def crop_up(img, a):
    ys,xs=np.where(a>0.5); cx=(xs.min()+xs.max())//2; cy=(ys.min()+ys.max())//2+10
    x0=cx-CROP//2; y0=cy-CROP//2
    img=img[y0:y0+CROP,x0:x0+CROP]; a=a[y0:y0+CROP,x0:x0+CROP]
    s=OUT/CROP
    return cv2.resize(img,(OUT,OUT),interpolation=cv2.INTER_LANCZOS4), cv2.resize(a,(OUT,OUT),interpolation=cv2.INTER_LINEAR), (x0,y0,s)
LABEL_RECT=(612,573,710,603)  # in ref coords: covers old label 620-701 x 576-594
def make_label(w,h):
    S=10; W,H=w*S,h*S
    im=Image.new('RGB',(W,H),(246,245,241)); d=ImageDraw.Draw(im)
    f1=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',int(H*0.36))
    f2=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',int(H*0.22))
    t1='OBERNDÖRFER'; t2='MILANO'
    b1=d.textbbox((0,0),t1,font=f1); b2=d.textbbox((0,0),t2,font=f2)
    d.text(((W-(b1[2]-b1[0]))/2-b1[0], H*0.16-b1[1]),t1,font=f1,fill=(28,28,28))
    d.text(((W-(b2[2]-b2[0]))/2-b2[0], H*0.62-b2[1]),t2,font=f2,fill=(60,60,60))
    return np.asarray(im)[...,::-1].astype(np.float32)
def put_label(img, xform):
    x0,y0,s=xform; X0,Y0,X1,Y1=LABEL_RECT
    fx0,fy0=int((X0-x0)*s),int((Y0-y0)*s); fx1,fy1=int((X1-x0)*s),int((Y1-y0)*s)
    w,h=fx1-fx0,fy1-fy0
    lb=make_label(w,h)
    lb=cv2.resize(cv2.resize(lb,(w*10,h*10)),(w,h),interpolation=cv2.INTER_AREA)
    # soft shading: slight gradient + soft edge shadow
    yy=np.linspace(0.96,1.0,h)[:,None,None]; lb=lb*yy
    sh=np.zeros(img.shape[:2],np.float32); sh[fy0+3:fy1+3,fx0+2:fx1+2]=1; sh=cv2.GaussianBlur(sh,(0,0),3)
    img=img*(1-0.25*sh[...,None])
    m=np.zeros(img.shape[:2],np.float32); m[fy0:fy1,fx0:fx1]=1; m=cv2.GaussianBlur(m,(0,0),0.8)[...,None]
    full=img.copy(); full[fy0:fy1,fx0:fx1]=lb
    return img*(1-m)+full*m
