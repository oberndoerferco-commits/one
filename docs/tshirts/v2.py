import cv2,numpy as np,os,sys
from extract import shirt_geom
from compose import make_label
REF={'front':'ref/u3870_8.jpg','back':'ref/u3870_9.jpg'}
def tolab(i): return cv2.cvtColor(i.astype(np.float32)/255.,cv2.COLOR_BGR2Lab)
def tobgr(L): return np.clip(cv2.cvtColor(L.astype(np.float32),cv2.COLOR_Lab2BGR)*255,0,255)
def recolor(side,color):
    im=cv2.imread(REF[side]); Lab=tolab(im); L,A,B=Lab[...,0],Lab[...,1],Lab[...,2]
    C=np.sqrt(A**2+B**2)
    w=np.clip((C-4.5)/(10.3-4.5),0,1)                    # per-pixel pink coverage at the outline (wall chroma ~2.6)
    w=cv2.GaussianBlur(w,(0,0),0.6)
    m=(cv2.GaussianBlur(C,(0,0),2)>6).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    fill=np.zeros_like(m); cv2.drawContours(fill,[max(cnts,key=cv2.contourArea)],-1,1,-1)
    interior=cv2.GaussianBlur(cv2.erode(fill,np.ones((9,9),np.uint8)).astype(np.float32),(0,0),2)
    w=np.maximum(w,interior)                               # inside the shirt: always full recolour (highlights too)
    wc=np.maximum(np.clip((C-3.2)/2.5,0,1),w)              # remove pink tint even on faint edge pixels
    Lm=np.median(L[w>0.95]); d=L-Lm
    if color=='white': T=np.clip(96.0+1.0*d,60,99.5); ta,tb=-0.1,0.9
    else:              T=np.clip(14.0+0.62*d,2,45);   ta,tb=0.2,-0.4
    out=Lab.copy()
    out[...,0]=L+w*(T-L); out[...,1]=A*(1-wc)+wc*ta; out[...,2]=B*(1-wc)+wc*tb
    return tobgr(out), w
def shirt_bbox(w):
    m=(w>0.5).astype(np.uint8); cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    return cv2.boundingRect(max(cnts,key=cv2.contourArea))
def extract(path):
    im=cv2.imread(path); fill,(x,y,w,h)=shirt_geom(im)
    inner=cv2.erode(fill,np.ones((61,61),np.uint8))
    sc=np.median(im[inner>0].reshape(-1,3),0); dark=sc.mean()<128
    d=np.abs(im.astype(np.float32)-sc).sum(2)
    t0,t1=(150,330) if dark else (45,120)
    a=np.clip((d-t0)/(t1-t0),0,1)*inner
    n,lab,st,_=cv2.connectedComponentsWithStats((a>0.3).astype(np.uint8))
    keep=np.zeros(a.shape,np.uint8)
    for i in range(1,n):
        cx,cy,cw,ch,area=st[i]
        if area<60: continue
        if abs(cx+cw/2-(x+w/2))>0.27*w: continue
        if cy<y+0.11*w and abs(cx+cw/2-(x+w/2))<0.15*w: continue
        if max(cw,ch)>150 and min(cw,ch)<22: continue
        if abs(cx+cw/2-(x+w/2))>0.31*w: continue
        keep[lab==i]=1
    keep=cv2.dilate(keep,np.ones((5,5),np.uint8))
    a=(np.clip((d-60)/(330-60),0,1) if dark else a)*keep
    col=np.clip((im.astype(np.float32)-(1-a[...,None])*sc)/np.maximum(a,1e-3)[...,None],0,255)
    return a,col,(x,y,w,h)
def clusters(a,geom):
    """split design alpha into main design and hem lockup; return list of (mask,bbox)"""
    x,y,w,h=geom; ys,xs=np.where(a>0.2)
    if len(xs)==0: return {}
    cut=y+0.80*h
    out={}
    for name,sel in [('main',ys<cut),('hem',ys>=cut)]:
        if sel.sum()<20: continue
        out[name]=(xs[sel].min(),ys[sel].min(),xs[sel].max(),ys[sel].max())
    return out
def place(a,col,src_bbox,dst_bbox,shape):
    sx0,sy0,sx1,sy1=src_bbox; dx0,dy0,dx1,dy1=dst_bbox
    s=(dx1-dx0)/max(1,(sx1-sx0))
    M=np.float32([[s,0,(dx0+dx1)/2-(sx0+sx1)/2*s],[0,s,(dy0+dy1)/2-(sy0+sy1)/2*s]])
    A=cv2.warpAffine(a,M,(shape[1],shape[0]),flags=cv2.INTER_AREA if s<1 else cv2.INTER_LINEAR)
    Cc=cv2.warpAffine(col,M,(shape[1],shape[0]),flags=cv2.INTER_AREA if s<1 else cv2.INTER_LINEAR)
    return A,Cc
def to_ref(b,g,G):
    x,y,w,h=g; X,Y,W,H=G; s=W/w
    return tuple(int(v) for v in ((b[0]-x)*s+X+0*(W/2-w*s/2),(b[1]-y)*s+Y,(b[2]-x)*s+X,(b[3]-y)*s+Y))
def build(white_path, black_path, side, outdir):
    res={}
    aw,cw_,gw=extract(white_path); clw=clusters(aw,gw)
    for color in ['white','black']:
        img,w=recolor(side,color); G=shirt_bbox(w)
        if color=='white': a,col,g,cl=aw,cw_,gw,clw
        else: a,col,g=extract(black_path); cl=clusters(a,g)
        if color=='black' and 'hem' in clw:
            cl=dict(cl); cl.pop('hem',None)
            b=clw['hem']; dst=to_ref(b,gw,G)
            m=np.zeros(aw.shape,np.float32); m[b[1]-3:b[3]+4,b[0]-3:b[2]+4]=1
            A,_=place(aw*m,cw_,b,dst,img.shape); A=cv2.GaussianBlur(A,(0,0),0.4)*w
            med=np.median(img[w>0.98].reshape(-1,3),0)
            ink=np.clip(np.array([238,238,236],np.float32)+0.8*(img-med),0,255)
            img=img*(1-A[...,None])+ink*A[...,None]
        for name,b in cl.items():
            # destination = where this element sits on the WHITE shirt (mapped to the reference)
            ref_b=clw.get(name,b); gg=gw if name in clw else g
            dst=to_ref(ref_b,gg,G)
            m=np.zeros(a.shape,np.float32); m[b[1]-3:b[3]+4,b[0]-3:b[2]+4]=1
            A,Cc=place(a*m,col,b,dst,img.shape)
            A=cv2.GaussianBlur(A,(0,0),0.4)*w
            med=np.median(img[w>0.98].reshape(-1,3),0)
            ink=np.clip(Cc+0.8*(img-med),0,255)
            img=img*(1-A[...,None])+ink*A[...,None]
        if side=='front':
            X0,Y0,X1,Y1=612,573,710,603
            lb=make_label(X1-X0,Y1-Y0)
            lb=cv2.resize(cv2.resize(lb,((X1-X0)*10,(Y1-Y0)*10)),(X1-X0,Y1-Y0),interpolation=cv2.INTER_AREA)
            sh=np.zeros(img.shape[:2],np.float32); sh[Y0+2:Y1+2,X0+1:X1+1]=1; sh=cv2.GaussianBlur(sh,(0,0),1.5)
            img=img*(1-0.25*sh[...,None]); img[Y0:Y1,X0:X1]=lb*np.linspace(0.96,1,Y1-Y0)[:,None,None]
        res[color]=img
    return res
