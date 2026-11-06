import cv2,numpy as np,os
from extract import shirt_geom
from compose import make_label
import v2h as v2
from v2h import recolor, torso_geom, orig_torso, to_ref_t, clusters
def layer(path):
    """clean design layer from an original 2400px photo: alpha + decontaminated colour (no halos)"""
    im=cv2.imread(path); fill,(x,y,w,h)=shirt_geom(im)
    inner=cv2.erode(fill,np.ones((61,61),np.uint8))
    sc=np.median(im[inner>0].reshape(-1,3),0); dark=sc.mean()<128
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2Lab).astype(np.float32); slab=cv2.cvtColor(np.uint8([[sc]]),cv2.COLOR_BGR2Lab)[0,0].astype(np.float32)
    d=np.sqrt(((lab-slab)**2).sum(2))          # perceptual distance: only used to find the artwork
    t0,t1=(22,60) if dark else (14,45)
    mask=np.clip((d-t0)/(t1-t0),0,1)*inner
    n,labs,st,_=cv2.connectedComponentsWithStats((mask>0.5).astype(np.uint8))
    keep=np.zeros(mask.shape,np.uint8)
    for i in range(1,n):
        cx,cy,cw,ch,area=st[i]
        if area<25: continue
        if abs(cx+cw/2-(x+w/2))>0.27*w: continue
        if cy<y+0.11*w and abs(cx+cw/2-(x+w/2))<0.15*w: continue
        if max(cw,ch)>150 and min(cw,ch)<22: continue
        keep[labs==i]=1
    keep=cv2.dilate(keep,np.ones((7,7),np.uint8))
    # inside the artwork: keep every pixel exactly as it is (multicolour boundaries untouched)
    m=(mask>0.5)&(keep>0)
    core=cv2.erode(m.astype(np.uint8),np.ones((3,3),np.uint8))>0
    # outer edge only: pixel = a*ink + (1-a)*shirt, ink = colour of the nearest solid artwork pixel
    f=im.astype(np.float32); diff=f-sc; dist=np.sqrt((diff**2).sum(2))
    ink=f.copy(); found=core.copy(); bestd=np.where(core,0,1e9).astype(np.float32)
    anyink=f.copy(); anybest=dist.copy()
    r=3
    for dy in range(-r,r+1):
        for dx in range(-r,r+1):
            if dx==0 and dy==0: continue
            sh=lambda z: np.roll(np.roll(z,dy,0),dx,1)
            cs=sh(core); fs=sh(f); dd=dx*dx+dy*dy
            sel=cs&(dd<bestd)&(~core)
            ink[sel]=fs[sel]; bestd[sel]=dd; found|=sel
            ds=sh(dist); s2=(ds>anybest)&(sh(keep)>0)
            anybest[s2]=ds[s2]; anyink[s2]=fs[s2]
    ink=np.where(found[...,None],ink,anyink)      # thin strokes with no solid core: use their darkest/strongest pixel
    idiff=ink-sc; den=np.maximum((idiff**2).sum(2),1.0)
    a=np.clip((diff*idiff).sum(2)/den,0,1)
    a=np.where(core,1.0,a)*keep
    a[a<0.06]=0
    col=np.where(core[...,None],f,ink)
    return a,col,(x,y,w,h),dark
def is_coloured(col,a):
    m=a>0.9
    if m.sum()==0: return False
    hsv=cv2.cvtColor(col.clip(0,255).astype(np.uint8),cv2.COLOR_BGR2HSV)
    return np.median(hsv[...,1][m])>60
def place_pm(a,col,src_b,dst_b,shape,box):
    sx0,sy0,sx1,sy1=src_b; dx0,dy0,dx1,dy1=dst_b; s=(dx1-dx0)/max(1,(sx1-sx0))
    M=np.float32([[s,0,(dx0+dx1)/2-(sx0+sx1)/2*s],[0,s,(dy0+dy1)/2-(sy0+sy1)/2*s]])
    m=np.zeros(a.shape,np.float32); m[box[1]:box[3],box[0]:box[2]]=1; a=a*m
    P=col*a[...,None]
    fl=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC
    A=cv2.warpAffine(a,M,(shape[1],shape[0]),flags=fl); PP=cv2.warpAffine(P,M,(shape[1],shape[0]),flags=fl)
    A=np.clip(A,0,1); C=PP/np.maximum(A,1e-4)[...,None]
    return A,C
def neutral_ink(C,target):
    g=cv2.cvtColor(np.clip(C,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
    if target=='light':  # white ink on black
        v=np.full_like(g,236.)
        return np.dstack([v,v,v*0.985])
    if target=='dark':   # black ink on white
        v=np.full_like(g,18.); return np.dstack([v,v,v])
    return np.dstack([g,g,g])  # keep tone (e.g. grey outline)
_TAG=None
def place_tag(img):
    """the brand's woven neck label, sewn into the back neck, lower edge tucked behind the front collar"""
    global _TAG
    if _TAG is None:
        tg=cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ref','tag.png'),cv2.IMREAD_UNCHANGED)
        if tg.shape[2]==4: tg=tg[...,:3]
        _TAG=tg[2:-2,2:-4].astype(np.float32)
    W=84; H=int(round(W*_TAG.shape[0]/_TAG.shape[1])); cx=1320; top=1148
    x0=cx-W//2; y0=top
    lab=cv2.resize(_TAG,(W,H),interpolation=cv2.INTER_AREA)
    lab=lab*np.linspace(1.0,0.93,H)[:,None,None]*0.985          # soft light fall-off down the label
    yy,xx=np.mgrid[0:img.shape[0],0:img.shape[1]].astype(np.float32)
    yedge=1150+90*np.sqrt(np.clip(1-((xx-1320)/300)**2,0,1))      # inner edge of the front collar rib
    vis=np.clip((yedge-yy)/3.0,0,1)                              # front collar covers what is below its edge
    # contact shadow of the label on the fabric
    sh=np.zeros(img.shape[:2],np.float32); sh[y0+4:y0+H+4,x0+2:x0+W+2]=1; sh=cv2.GaussianBlur(sh,(0,0),3.2)*vis
    img=img*(1-0.22*sh[...,None])
    a=np.zeros(img.shape[:2],np.float32); a[y0:y0+H,x0:x0+W]=1; a=cv2.GaussianBlur(a,(0,0),1.0)*vis
    full=img.copy(); full[y0:y0+H,x0:x0+W]=lab
    # the collar rib casts a little shade onto the label right above its edge
    rim=np.clip(1-(yedge-yy)/12,0,1)*a
    full=full*(1-0.18*rim[...,None])
    return img*(1-a[...,None])+full*a[...,None]
def build(white_path,black_path,side,own_black=None):
    # only these black designs differ in style from the white ones (outline OM, filled stars)
    if own_black is None: own_black=any(k in black_path for k in ['om-black-back','star-black-back'])
    aw,cw,gw,_=layer(white_path); clw=clusters(aw,gw); tww=orig_torso(white_path)
    ab,cb,gb,_=layer(black_path); clb=clusters(ab,gb); twb=orig_torso(black_path)
    coloured=is_coloured(cw,aw)
    res={}
    for color in ['white','black']:
        img,w=recolor(side,color); TR=torso_geom(w)
        med=np.median(img[w>0.98].reshape(-1,3),0)
        texL=cv2.cvtColor(np.clip(img,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)-cv2.cvtColor(np.uint8([[med]]),cv2.COLOR_BGR2GRAY)[0,0]
        for name,bw in clw.items():
            dst=to_ref_t(bw,tww,TR)
            if side=='back' and name=='main':   # back prints sit centred on the back
                cxm=(dst[0]+dst[2])/2; sh=int(round(TR[0]-cxm)); dst=(dst[0]+sh,dst[1],dst[2]+sh,dst[3])
            if color=='white' or coloured or name=='hem' or name not in clb or not own_black:
                a,c,b,box=aw,cw,bw,bw
                A,C=place_pm(a,c,b,dst,img.shape,(b[0]-4,b[1]-4,b[2]+5,b[3]+5))
                if color=='black':   # artwork lifted from a light shirt: tighten its soft edge so it can't glow on black
                    A=np.clip((A-0.12)/0.76,0,1)
                if color=='black' and not coloured: C=neutral_ink(C,'light')
                elif not coloured: C=neutral_ink(C,'dark')
            else:  # black has its own artwork style (outline OM, filled stars): own shape, white-shirt position
                b=clb[name]
                A,C=place_pm(ab,cb,b,dst,img.shape,(b[0]-4,b[1]-4,b[2]+5,b[3]+5))
                g=cv2.cvtColor(np.clip(C,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
                C=np.dstack([g,g,g*0.985])
                A=np.clip((A-0.22)/0.56,0,1); A=A*A*(3-2*A)
            res.setdefault('boxes_'+color,[]).append(dst)
            if color=='black' and 'om-black-back' in black_path and name=='main':
                # original: letters filled deep black (darker than the shirt) with a thin light-grey outline
                As,_=place_pm(aw,cw,bw,dst,img.shape,(bw[0]-4,bw[1]-4,bw[2]+5,bw[3]+5))
                As=As*w
                img=img*(1-As[...,None])+np.array([5,5,5],np.float32)*As[...,None]
                # thin hairline just outside the letter edge, like the original
                up=cv2.resize(As,None,fx=4,fy=4,interpolation=cv2.INTER_LINEAR)
                ring=np.clip(cv2.dilate(up,np.ones((13,13),np.uint8))-up,0,1)
                edge=np.clip(cv2.resize(ring,(As.shape[1],As.shape[0]),interpolation=cv2.INTER_AREA)*1.3,0,1)*w
                img=img*(1-edge[...,None])+np.array([205,205,203],np.float32)*edge[...,None]
                continue
            A=A*w
            ink=np.clip(C+0.35*texL[...,None],0,255)       # fabric texture through the print, luminance only
            img=img*(1-A[...,None])+ink*A[...,None]
        if side=='front':
            img=place_tag(img)
        res[color]=np.clip(img,0,255).astype(np.uint8)
    return res
