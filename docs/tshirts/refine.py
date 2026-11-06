import cv2,numpy as np,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from v2 import REF,_nconv
from mask import smooth_soft
for side in ['front','back']:
    im=cv2.imread(REF[side]).astype(np.float32)
    soft=np.load(f'soft_{side}.npy'); fill=(soft>0.5).astype(np.uint8)
    inner=cv2.erode(fill,np.ones((7,7),np.uint8)).astype(np.float32)
    outer=(1-cv2.dilate(fill,np.ones((5,5),np.uint8))).astype(np.float32)
    S=_nconv(im,inner,2); B=_nconv(im,outer,2); d=S-B; den=(d**2).sum(2)
    cov=np.clip(((im-B)*d).sum(2)/np.maximum(den,1.0),0,1)
    t=np.clip((den-40)/120,0,1); cov=t*cov+(1-t)*soft
    band=(inner==0)&(outer==0)
    newfill=((inner>0)|(band&(cov>0.5))).astype(np.uint8)
    newfill=cv2.morphologyEx(newfill,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    s2=smooth_soft(newfill,sigma_pts=4)
    np.save(f'soft2_{side}.npy',s2.astype(np.float32))
    print(side,'mean |shift| px', np.abs(s2-soft).sum()/ (cv2.Canny((soft>0.5).astype(np.uint8)*255,1,1)>0).sum())
