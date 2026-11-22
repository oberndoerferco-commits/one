import numpy as np, collections, sys
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
im=Image.open('bl-crop.png').convert('L')
W=6400; im=im.resize((W,int(im.height*W/im.width)),Image.LANCZOS)
ink=np.asarray(im)<150
K=int(sys.argv[1]); SM=int(sys.argv[2])
m=Image.fromarray((ink*255).astype('uint8'))
op=m.filter(ImageFilter.MinFilter(K)).filter(ImageFilter.MaxFilter(K))
a=np.asarray(op)>127
# drop speckles
lab=np.zeros(a.shape,np.int32); cur=0; keep=np.zeros_like(a)
H,Wd=a.shape
for sy,sx in np.argwhere(a):
    if lab[sy,sx]: continue
    cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; n=0
    while q:
        y,x=q.popleft(); n+=1
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<Wd and a[ny,nx] and not lab[ny,nx]:
                lab[ny,nx]=cur; q.append((ny,nx))
    if n>4000: keep |= (lab==cur)
# smooth
s=Image.fromarray((keep*255).astype('uint8'))
s=s.filter(ImageFilter.MaxFilter(SM)).filter(ImageFilter.MinFilter(SM))
f=np.asarray(s)>127
print('K=%d SM=%d  kept %.3f of ink'%(K,SM,f.sum()/ink.sum()))
out=np.dstack([np.zeros(f.shape+(3,),np.uint8),(f*255).astype(np.uint8)])
Image.fromarray(out,'RGBA').save('clean-k%d.png'%K)
bg=Image.new('RGB',f.shape[::-1],(255,255,255)); o=Image.fromarray(out,'RGBA'); bg.paste(o,(0,0),o)
bg.save('clean-k%d-chk.png'%K)
