import cv2,numpy as np,sys
from v2 import tolab, REF
def precise_fill(side):
    im=cv2.imread(REF[side]); Lab=tolab(im); C=np.sqrt(Lab[...,1]**2+Lab[...,2]**2)
    Cb=cv2.GaussianBlur(C,(0,0),2.5)
    strong=(Cb>6).astype(np.uint8)
    cnts,_=cv2.findContours(strong,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    core=np.zeros_like(strong); cv2.drawContours(core,[max(cnts,key=cv2.contourArea)],-1,1,-1)
    gc=np.full(core.shape,cv2.GC_PR_BGD,np.uint8)
    gc[cv2.dilate(core,np.ones((5,5),np.uint8))>0]=cv2.GC_PR_FGD
    gc[(Cb>3.8)&(cv2.dilate(core,np.ones((25,25),np.uint8))>0)]=cv2.GC_PR_FGD
    gc[cv2.erode(core,np.ones((21,21),np.uint8))>0]=cv2.GC_FGD
    gc[cv2.dilate(core,np.ones((61,61),np.uint8))==0]=cv2.GC_BGD
    bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
    cv2.grabCut(im,gc,None,bgd,fgd,6,cv2.GC_INIT_WITH_MASK)
    m=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    m=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    fill=np.zeros_like(m); cv2.drawContours(fill,[max(cnts,key=cv2.contourArea)],-1,1,-1)
    fill=(cv2.GaussianBlur(fill.astype(np.float32),(0,0),1.5)>0.5).astype(np.uint8)
    return fill
if __name__=='__main__':
    for side in ['front','back']:
        f=precise_fill(side); np.save(f'fill_{side}.npy',f)
        im=cv2.imread(REF[side]); cnts,_=cv2.findContours(f,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        o=im.copy(); cv2.drawContours(o,cnts,-1,(0,0,255),1)
        cv2.imwrite(f'fillchk_{side}.png',np.vstack([np.hstack([cv2.resize(o[650:1100,800:1150],None,fx=1.2,fy=1.2),cv2.resize(o[1050:1500,180:530],None,fx=1.2,fy=1.2)]),np.hstack([cv2.resize(o[480:780,180:530],None,fx=1.2,fy=1.2),cv2.resize(o[480:780,800:1150],None,fx=1.2,fy=1.2)])]))
