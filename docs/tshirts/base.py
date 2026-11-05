import cv2, numpy as np, sys
def lab(img): return cv2.cvtColor(img.astype(np.float32)/255., cv2.COLOR_BGR2Lab)
def bgr(L): return np.clip(cv2.cvtColor(L, cv2.COLOR_Lab2BGR)*255,0,255)
def shirt_alpha(im):
    b,g,r=[im[...,i].astype(np.float32) for i in range(3)]
    rg=cv2.GaussianBlur(r-g,(0,0),1.0)
    a=np.clip((rg-4)/(22-4),0,1)
    # fill holes (label, stitching) : close
    m=(a>0.5).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    fill=np.zeros_like(m); cv2.drawContours(fill,[max(cnts,key=cv2.contourArea)],-1,1,-1)
    inner=cv2.erode(fill,np.ones((5,5),np.uint8))
    a=np.where(inner>0,1.0,a*fill.astype(np.float32)+a*(1-fill)*0)  # inside => 1, outside keep ramp only near edge
    a=np.where(fill>0,np.maximum(a,inner.astype(np.float32)),a)
    # smooth contour-based alpha (removes JPEG jaggies along the outline)
    f=cv2.GaussianBlur(fill.astype(np.float32),(0,0),2.2)
    f=np.clip((f-0.5)*2.2+0.5,0,1)
    return f, fill
def recolor(im, a, target):
    Lab=lab(im); L=Lab[...,0]
    inside=a>0.99
    Lm=np.median(L[inside])
    d=L-Lm
    if target=='black': Ln=np.clip(13+0.50*d,2,40); A=0.3; B=-0.6
    else:                Ln=np.clip(95.5+0.85*d,60,99.2); A=0.2; B=1.2
    new=np.dstack([Ln,np.full_like(Ln,A),np.full_like(Ln,B)]).astype(np.float32)
    shirt=bgr(new)
    # background estimate: desaturate original pixel
    grey=Lab.copy(); grey[...,1]=0.4; grey[...,2]=2.0
    bgest=bgr(grey)
    out=a[...,None]*shirt+(1-a[...,None])*bgest
    return out.astype(np.uint8)
if __name__=='__main__':
    for side,f in [('front','ref/u3870_8.jpg'),('back','ref/u3870_9.jpg')]:
        im=cv2.imread(f); a,fill=shirt_alpha(im)
        for t in ['black','white']:
            cv2.imwrite(f'base_{t}_{side}.png',recolor(im,a,t))
