# stamp.py SRC REF OUT : cut the brass stamp out of SRC and place it, small and centred, on a soft light
# grey seamless ground in a 5:7 portrait frame, with a soft contact shadow (style of REF, Bottega's still life)
import sys, numpy as np, cv2
from PIL import Image, ImageFilter
src=cv2.imread(sys.argv[1]); ref=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float)
h,w=src.shape[:2]
mask=np.zeros((h,w),np.uint8); bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
rect=(int(w*0.24),int(h*0.20),int(w*0.46),int(h*0.62))
cv2.grabCut(src,mask,rect,bgd,fgd,8,cv2.GC_INIT_WITH_RECT)
m=np.where((mask==1)|(mask==3),1,0).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(lab==k).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((15,15),np.uint8))
m=cv2.erode(m,np.ones((3,3),np.uint8))
cv2.imwrite('mask.png',m*255)
x,y,bw,bh=cv2.boundingRect(m)
alpha=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)
rgb=cv2.cvtColor(src,cv2.COLOR_BGR2RGB).astype(float)
# lift the brass towards the brighter, airier light of the reference (gamma and a little exposure)
rgb=255*np.clip((rgb/255)**0.82*1.06,0,1)
# reference ground: take its top and bottom tones
top=ref[:int(ref.shape[0]*0.1)].reshape(-1,3).mean(0); bot=ref[-int(ref.shape[0]*0.1):].reshape(-1,3).mean(0)
W,H=1500,2100
yy=np.linspace(0,1,H)[:,None,None]
ground=top*(1-yy)+bot*yy; ground=np.repeat(ground,W,axis=1)
noise=np.random.default_rng(3).normal(0,1.2,(H,W,1)); ground=np.clip(ground+noise,0,255)
# scale stamp to ~44% of frame width, centred a little below the middle (as Bottega)
s=W*0.40/bw
sw,sh=int(w*s),int(h*s)
rgb_s=cv2.resize(rgb,(sw,sh),interpolation=cv2.INTER_LANCZOS4); a_s=cv2.resize(alpha,(sw,sh),interpolation=cv2.INTER_LINEAR)
cx=W//2; cy=int(H*0.56)
ox=int(cx-(x+bw/2)*s); oy=int(cy-(y+bh/2)*s)
canvas=ground.copy()
# soft contact shadow: the stamp's footprint squashed and blurred, under its base
sh_m=np.zeros((H,W),np.float32)
base_y=oy+int((y+bh)*s)
fw=int(bw*s*1.02); fh=int(bw*s*0.10)
cv2.ellipse(sh_m,(cx-int(bw*s*0.04),base_y-int(fh*0.25)),(fw//2,fh//2),0,0,360,1.0,-1)
sh_m=cv2.GaussianBlur(sh_m,(0,0),W*0.018)
canvas=canvas*(1-0.32*sh_m[...,None])
y0,x0=max(0,oy),max(0,ox); y1,x1=min(H,oy+sh),min(W,ox+sw)
sub=rgb_s[y0-oy:y1-oy,x0-ox:x1-ox]; al=a_s[y0-oy:y1-oy,x0-ox:x1-ox][...,None]
canvas[y0:y1,x0:x1]=canvas[y0:y1,x0:x1]*(1-al)+sub*al
out=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8))
out.save(sys.argv[3],quality=92)
print('ground top',top.round(),'bottom',bot.round(),'stamp box',(x,y,bw,bh),'scale',round(s,2))
