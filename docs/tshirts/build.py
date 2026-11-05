import cv2,numpy as np,glob,os,sys
from compose import base, crop_up, put_label
from extract import shirt_geom
def own_design(path):
    im=cv2.imread(path); fill,(x,y,w,h)=shirt_geom(im)
    inner=cv2.erode(fill,np.ones((61,61),np.uint8))
    sc=np.median(im[inner>0].reshape(-1,3),0); dark=sc.mean()<128
    d=np.abs(im.astype(np.float32)-sc).sum(2)
    t0,t1=(150,330) if dark else (45,120)
    a=np.clip((d-t0)/(t1-t0),0,1)*inner
    comp=(a>0.3).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(comp)
    keep=np.zeros_like(comp)
    for i in range(1,n):
        cx,cy,cw,ch,area=st[i]
        if area<5: continue
        if cy < y+0.11*w and abs(cx+cw/2-(x+w/2))<0.15*w: continue
        if max(cw,ch)>150 and min(cw,ch)<22: continue
        if abs(cx+cw/2-(x+w/2))>0.31*w: continue
        keep[lab==i]=1
    keep=cv2.dilate(keep,np.ones((5,5),np.uint8))
    if dark:  # recover soft edges around kept strokes with lower threshold
        a=np.clip((d-60)/(330-60),0,1)*keep
    else: a=a*keep
    A=np.maximum(a,1e-3)[...,None]
    col=np.clip((im.astype(np.float32)-(1-a[...,None])*sc)/A,0,255)
    return a,col,(x,y,w,h),dark
def final_geom(a2):
    ys,xs=np.where(a2>0.5); return xs.min(),ys.min(),xs.max()-xs.min(),ys.max()-ys.min()
def render(path,color,side,out):
    img,a=base(color,side); img,a2,xf=crop_up(img,a)
    if side=='front': img=put_label(img,xf)
    da,dc,g,dark=own_design(path)
    if da.max()>0:
        G=final_geom(a2); x,y,w,h=g; X,Y,W,H=G; s=W/w
        M=np.float32([[s,0,X+W/2-(x+w/2)*s],[0,s,Y-y*s]])
        A=cv2.warpAffine(da,M,(img.shape[1],img.shape[0]),flags=cv2.INTER_LINEAR)
        C=cv2.warpAffine(dc,M,(img.shape[1],img.shape[0]),flags=cv2.INTER_LINEAR)
        A=cv2.GaussianBlur(A,(0,0),0.6)*a2
        # transfer folds / texture of the shirt onto the print
        med=np.median(img[a2>0.99].reshape(-1,3),0)
        tex=cv2.GaussianBlur(img,(0,0),1.0)-med
        ink=np.clip(C+0.8*tex,0,255)
        img=img*(1-A[...,None])+ink*A[...,None]
    # unify background: neutral light grey
    cv2.imwrite(out,np.clip(img,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,93])
if __name__=='__main__':
    for p in sys.argv[1:]:
        n=os.path.basename(p)
        color='black' if '-black' in n else 'white'
        side='back' if '-back' in n else 'front'
        render(p,color,side,'new/'+n); print('ok',n,color,side)
