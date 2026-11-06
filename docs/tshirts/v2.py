import os
import cv2,numpy as np,os,sys
from extract import shirt_geom
from compose import make_label
REF={'front':'ref/u3870_8.jpg','back':'ref/u3870_9.jpg'}
def tolab(i): return cv2.cvtColor(i.astype(np.float32)/255.,cv2.COLOR_BGR2Lab)
def tobgr(L): return np.clip(cv2.cvtColor(L.astype(np.float32),cv2.COLOR_Lab2BGR)*255,0,255)
def _nconv(img,wgt,sig):
    if img.ndim==3:
        num=cv2.GaussianBlur(img*wgt[...,None],(0,0),sig); den=cv2.GaussianBlur(wgt,(0,0),sig)[...,None]
    else:
        num=cv2.GaussianBlur(img*wgt,(0,0),sig); den=cv2.GaussianBlur(wgt,(0,0),sig)
    return num/np.maximum(den,1e-4)
def recolor(side,color):
    im=cv2.imread(REF[side])
    if side=='front':   # remove the old woven label completely (it is replaced by ours later)
        m=np.zeros(im.shape[:2],np.uint8); m[576:600,617:707]=1
        im=cv2.inpaint(im,m,6,cv2.INPAINT_TELEA)
        strip=im[577:584,593:617].copy()                      # the back-neck stitching right next to the old label
        for x in range(617,707,24):
            wdt=min(24,707-x); im[577:584,x:x+wdt]=strip[:,:wdt]   # continue it behind our label
    f=im.astype(np.float32)
    Lab=tolab(im); L,A,B=Lab[...,0],Lab[...,1],Lab[...,2]
    C=np.sqrt(A**2+B**2)
    here=os.path.dirname(os.path.abspath(__file__))
    soft=np.load(os.path.join(here,f'soft2_{side}.npy'))      # precise GrabCut outline, smoothed along its length, anti-aliased
    fill=(soft>0.5).astype(np.uint8)
    inner=cv2.erode(fill,np.ones((7,7),np.uint8)).astype(np.float32)
    outer=(1-cv2.dilate(fill,np.ones((5,5),np.uint8))).astype(np.float32)
    band=(inner==0)&(outer==0)
    # local shirt colour and local wall colour, estimated right next to every edge pixel
    S=_nconv(f,inner,3); Bg=_nconv(f,outer,3)
    d=S-Bg; den=(d**2).sum(2)
    cov=np.clip(((f-Bg)*d).sum(2)/np.maximum(den,1.0),0,1)
    Cs=_nconv(C,inner,5)                               # how pink the shirt is right here (lit areas are paler)
    wc=cv2.GaussianBlur(np.clip((C-2.8)/np.maximum(Cs-2.8,1.0),0,1),(0,0),1.6)   # colour is half-resolution in JPEG: smooth its steps
    t=np.clip((den-40)/80,0,1)
    cov=t*cov+(1-t)*wc                      # very low contrast (lit shoulder): fall back to colour
    cov=np.clip((cov-0.04)/0.62,0,1)                 # edge pixels are mostly shirt: no light seam between shirt and shadow
    if color=='black': cov=np.clip(cov/0.45,0,1)       # lit edge fabric is still fabric: no light band on black
    fsoft=cv2.GaussianBlur(cv2.dilate(fill,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),1.0)
    cov=cov*fsoft                                      # never colour wall/shadow pixels outside the smooth outline
    geo=soft
    w=np.where(inner>0,1.0,np.where(band,geo,0.0)).astype(np.float32)
    # target shirt colour
    Lm=np.median(L[inner>0]); dL=L-Lm
    Ld=cv2.bilateralFilter(L.astype(np.float32),7,2.0,5)          # remove JPEG grain, keep fabric structure
    dLs=cv2.GaussianBlur(Ld,(0,0),6)-Lm                            # folds
    if color=='white':
        dL=0.55*dLs+0.45*(Ld-Lm-dLs)                                # gentler folds + fine weave, no blotches
        deep=cv2.erode(fill,np.ones((19,19),np.uint8)).astype(np.float32)
        dLi=_nconv(dL,deep,4)                                       # fabric tone a little further inside
        dist=cv2.distanceTransform(fill,cv2.DIST_L2,3)
        zone=np.clip((10-dist)/10,0,1)                              # last ~10px before the edge
        dL=np.where(zone>0,np.maximum(dL,dLi-2.0*(1-zone)-0.5),dL)
    if color=='white': T=np.clip(96.0+1.0*dL,60,99.5); ta,tb=-0.1,0.9
    else:              T=np.clip(14.0+0.85*dL,2,48);   ta,tb=0.2,-0.4
    shirt=tobgr(np.dstack([T,np.full_like(T,ta),np.full_like(T,tb)]))
    # at the edge the pixel is part wall: rebuild it as cov*new_shirt + (1-cov)*wall
    Tedge=_nconv(T,inner,1.5)                        # edge pixels take the tone of the fabric right next to them
    shirt_edge=tobgr(np.dstack([Tedge,np.full_like(Tedge,ta),np.full_like(Tedge,tb)]))
    out=np.where(inner[...,None]>0, shirt, f)
    eb=band[...,None]
    if color=='white':
        mix=w[...,None]*shirt_edge+(1-w[...,None])*f
    else:
        mix=f+w[...,None]*(shirt_edge-S)           # swap only the shirt share of the pixel; wall/shadow share stays original
    # edge colour: white/black shirt on a neutral wall is neutral too -> no pink or cyan fringe
    ml=tolab(np.clip(mix,0,255).astype(np.uint8)); bl=tolab(np.clip(Bg,0,255).astype(np.uint8))
    ml[...,1]=(1-w)*bl[...,1]+w*ta; ml[...,2]=(1-w)*bl[...,2]+w*tb
    mix=tobgr(ml)
    out=np.where(eb, mix, out)
    # final pass: no pink may survive in a ring just outside the shirt (soft/lit edges spill a few pixels)
    ring=(cv2.dilate(fill,np.ones((31,31),np.uint8))>0)&(w<0.98)
    far=(1-cv2.dilate(fill,np.ones((35,35),np.uint8))).astype(np.float32)
    wab=_nconv(tolab(im)[...,1:],far,6)                       # the wall's own (neutral) tint nearby
    ol=tolab(np.clip(out,0,255).astype(np.uint8))
    Co=np.sqrt(ol[...,1]**2+ol[...,2]**2)
    k=np.clip((Co-2.6)/1.5,0,1)*ring
    ol[...,1]=ol[...,1]*(1-k)+wab[...,0]*k; ol[...,2]=ol[...,2]*(1-k)+wab[...,1]*k
    out=np.where(ring[...,None],tobgr(ol),out)
    return out.astype(np.float32), w
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
def torso_geom(fill_or_w, top=None, width=None):
    m=(fill_or_w>0.5).astype(np.uint8); ys,xs=np.where(m>0); y=ys.min(); W=xs.max()-xs.min()
    yy=int(y+0.62*W*1.08); xx=np.where(m[yy]>0)[0]; return (xx.min()+xx.max())/2, xx.max()-xx.min(), y
def orig_torso(path):
    im=cv2.imread(path); fill,_=shirt_geom(im); return torso_geom(fill)
def to_ref_t(b,src,dst):
    (tc,tw,ty),(TC,TW,TY)=src,dst; s=TW/tw
    return tuple(int(v) for v in ((b[0]-tc)*s+TC,(b[1]-ty)*s+TY,(b[2]-tc)*s+TC,(b[3]-ty)*s+TY))
def to_ref(b,g,G):
    x,y,w,h=g; X,Y,W,H=G; s=W/w
    return tuple(int(v) for v in ((b[0]-x)*s+X+0*(W/2-w*s/2),(b[1]-y)*s+Y,(b[2]-x)*s+X,(b[3]-y)*s+Y))
def build(white_path, black_path, side, outdir):
    res={}
    aw,cw_,gw=extract(white_path); clw=clusters(aw,gw)
    tw_white=orig_torso(white_path); tw_black=orig_torso(black_path)
    for color in ['white','black']:
        img,w=recolor(side,color); G=shirt_bbox(w); TR=torso_geom(w)
        if color=='white': a,col,g,cl=aw,cw_,gw,clw
        else: a,col,g=extract(black_path); cl=clusters(a,g)
        if color=='black' and 'hem' in clw:
            cl=dict(cl); cl.pop('hem',None)
            b=clw['hem']; dst=to_ref_t(b,tw_white,TR)
            m=np.zeros(aw.shape,np.float32); m[b[1]-3:b[3]+4,b[0]-3:b[2]+4]=1
            A,_=place(aw*m,cw_,b,dst,img.shape); A=cv2.GaussianBlur(A,(0,0),0.4)*w
            med=np.median(img[w>0.98].reshape(-1,3),0)
            ink=np.clip(np.array([238,238,236],np.float32)+0.8*(img-med),0,255)
            img=img*(1-A[...,None])+ink*A[...,None]
        for name,b in cl.items():
            # destination = where this element sits on the WHITE shirt (mapped to the reference)
            # black and white use the SAME position and size: the one the design has on the white shirt
            dst=to_ref_t(clw[name] if name in clw else b, tw_white if name in clw else tw_black, TR)
            m=np.zeros(a.shape,np.float32); m[b[1]-3:b[3]+4,b[0]-3:b[2]+4]=1
            A,Cc=place(a*m,col,b,dst,img.shape); res.setdefault('boxes_'+color,[]).append(dst)
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
