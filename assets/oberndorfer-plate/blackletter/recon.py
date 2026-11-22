import numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
im=Image.open('bl-crop.png').convert('L')
W=3200; im=im.resize((W,int(im.height*W/im.width)),Image.LANCZOS)
ink=np.asarray(im)<150
mask=Image.fromarray((ink*255).astype('uint8'))

def erode(img,k): return img.filter(ImageFilter.MinFilter(k))
def dil(img,k=3):  return img.filter(ImageFilter.MaxFilter(k))

for K in (9,13,17,21):
    seed=erode(mask,K)
    prev=-1
    a=np.asarray(seed)>127
    for i in range(400):
        g=np.asarray(dil(Image.fromarray((a*255).astype('uint8'))))>127
        a=g&ink
        s=a.sum()
        if s==prev: break
        prev=s
    print('K=%2d iters=%d kept %.3f of ink'%(K,i,a.sum()/ink.sum()))
    Image.fromarray((~a*255).astype('uint8')).save('rec-k%d.png'%K)
