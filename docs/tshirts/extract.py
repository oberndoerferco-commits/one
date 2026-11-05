import cv2,numpy as np,glob,json,sys
def shirt_geom(im):
    bg=im[20,20].astype(int); d=np.abs(im.astype(int)-bg).sum(2)
    m=(cv2.GaussianBlur((d>18).astype(np.uint8)*255,(0,0),2)>128).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cnts,key=cv2.contourArea)
    fill=np.zeros(m.shape,np.uint8); cv2.drawContours(fill,[c],-1,1,-1)
    x,y,w,h=cv2.boundingRect(c); return fill,(x,y,w,h)
def extract(f):
    im=cv2.imread(f); fill,(x,y,w,h)=shirt_geom(im)
    inner=cv2.erode(fill,np.ones((41,41),np.uint8))
    sc=np.median(im[inner>0].reshape(-1,3),0)
    dark=sc.mean()<128
    d=np.abs(im.astype(np.float32)-sc).sum(2)
    t0,t1=(40,110) if dark else (45,120)
    a=np.clip((d-t0)/(t1-t0),0,1)*inner
    # drop label area: components in top 14% of shirt height near center-top
    comp=(a>0.3).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(comp)
    keep=np.zeros_like(comp)
    for i in range(1,n):
        cx,cy,cw,ch,area=st[i]
        if area<6: continue
        if cy < y+0.11*w and abs(cx+cw/2-(x+w/2))<0.15*w: continue  # neck label
        keep[lab==i]=1
    keep=cv2.dilate(keep,np.ones((7,7),np.uint8))
    a=a*keep
    # unpremultiply colour
    A=np.maximum(a,1e-3)[...,None]
    col=np.clip((im.astype(np.float32)-(1-a[...,None])*sc)/A,0,255)
    ys,xs=np.where(a>0.05)
    return dict(a=a,col=col,geom=(x,y,w,h),sc=sc,dark=dark,bbox=(xs.min(),ys.min(),xs.max(),ys.max()) if len(xs) else None)
if __name__=='__main__':
    for f in sorted(glob.glob('orig/*.jpg')):
        r=extract(f); print(f[9:50].ljust(42),r['geom'],r['bbox'])
