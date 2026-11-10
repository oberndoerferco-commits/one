import cv2,numpy as np,sys
sys.path.insert(0,'/tmp/claude-0/-home-user-one/80d22099-9194-5203-ae1e-233f8c53bd87/scratchpad/jogs')
from edges import gmask,runs
src,dst,y0,y1=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
im=cv2.imread(src); f=im.astype(np.float32); g,L=gmask(im)
ys=[];e1=[];e2=[]
for y in range(y0,y1):
    r=runs(g[y])
    if len(r)==2: ys.append(y); e1.append(r[0][1]); e2.append(r[1][0])
ys=np.array(ys); e1=np.array(e1,float); e2=np.array(e2,float)
# robust fit, biased to outer envelope of fabric (jaggies are notches): fit then use upper quantile
p=np.polyfit(ys,e1,3)
for it in range(6):
    r=e1-np.polyval(p,ys); s=np.std(r); keep=r>-1.5*s-0.5   # drop inward notches
    keep&=r<2.5*s+1
    p=np.polyfit(ys[keep],e1[keep],3)
r=e1-np.polyval(p,ys); off=np.percentile(r[keep],60); xe_all=np.polyval(p,np.arange(im.shape[0]))+off
print('fit resid std',np.std(r[keep]),'off',off)
out=f.copy(); rng=np.random.default_rng(3)
tex=f-cv2.GaussianBlur(f,(0,0),2.5)
BW=40
bgrow=np.zeros((im.shape[0],3),np.float32); fabrow=np.zeros((im.shape[0],3),np.float32)
for y in range(y0,y1):
    xe=xe_all[y]; gap=e2[ys==y][0]-xe if (ys==y).any() else 80
    xb=int(min(xe+BW+2, xe+gap*0.6)); bgrow[y]=np.median(f[y,xb:xb+8],0)
    xf=int(xe-18); fabrow[y]=np.median(f[y,xf-10:xf],0)
mir=np.zeros((im.shape[0],BW,3),np.float32)
for y in range(y0,y1):
    if (ys==y).any():
        e2y=int(e2[ys==y][0])
        for dd in range(BW): mir[y,dd]=f[y,e2y-1-dd]
mir[y0:y1]=cv2.GaussianBlur(mir[y0:y1],(0,0),sigmaX=0.6,sigmaY=6)
bgrow[y0:y1]=cv2.GaussianBlur(bgrow[y0:y1][:,None,:],(1,0),sigmaX=0.1,sigmaY=5)[:,0,:]
fabrow[y0:y1]=cv2.GaussianBlur(fabrow[y0:y1][:,None,:],(1,0),sigmaX=0.1,sigmaY=8)[:,0,:]
for y in range(y0,y1):
    xe=xe_all[y]; gap=(e2[ys==y][0]-xe) if (ys==y).any() else 80
    bw=int(min(BW,gap*0.6))
    xa=int(np.floor(xe-14)); xb=int(np.ceil(xe+bw))
    for x in range(xa,xb+1):
        a=np.clip(xe-x+0.5,0,1)   # fabric coverage
        if x<xe-1.5:
            if L[y,x]>75: out[y,x]=fabrow[y]+tex[y,x-25]
            continue
        d=x-xe; e2y=e2[ys==y][0] if (ys==y).any() else xe+gap
        bgv=mir[y,int(np.clip(round(d),0,BW-1))]+rng.normal(0,0.8,3)
        # blend toward bg near the far end to avoid seam
        fabv=f[y,int(xe-3)] if L[y,int(xe-3)]<75 else fabrow[y]+tex[y,x-25]
        val=a*fabv+(1-a)*bgv
        if x>xe+bw-12:
            t=(x-(xe+bw-12))/12.0; val=(1-t)*val+t*f[y,x]
        out[y,x]=val
# vertical feather at range ends
for yy,w,n in [(y0,1,45),(y1-1,-1,8)]:
    for k in range(n):
        y=yy+w*k; t=(k/n)**1.5; out[y]=t*out[y]+(1-t)*f[y]
cv2.imwrite(dst,np.clip(out,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
