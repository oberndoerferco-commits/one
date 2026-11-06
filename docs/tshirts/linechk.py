import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import cv2,numpy as np
def profile_dev(g,fill,c,i):
    n=len(c); p=c[i]; t=c[(i+4)%n]-c[(i-4)%n]; nrm=np.array([t[1],-t[0]]); nrm/=np.linalg.norm(nrm)+1e-9
    prof=[]
    for d in range(-6,7):
        x,y=p+nrm*d; xi,yi=int(round(x)),int(round(y))
        if 0<=yi<g.shape[0] and 0<=xi<g.shape[1]: prof.append((d,g[yi,xi],fill[yi,xi]))
    if len(prof)<13: return None
    out=[v for d,v,f in prof if f==0 and abs(d)>=4]; ins=[v for d,v,f in prof if f==1 and abs(d)>=4]; mid=[v for d,v,f in prof if abs(d)<=2]
    if not out or not ins: return None
    lo,hi=min(np.mean(out),np.mean(ins)),max(np.mean(out),np.mean(ins))
    return max(lo-min(mid),max(mid)-hi, 0)
def check(img,side,ref,label,show=0):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float); gr=cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY).astype(float)
    s=np.load(f'soft3_{side}.npy'); fill=(s>0.5).astype(np.uint8)
    cnts,_=cv2.findContours(fill,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cnts,key=cv2.contourArea)[:,0,:].astype(float)
    bad=[]
    for i in range(0,len(c),3):
        d=profile_dev(g,fill,c,i); dr=profile_dev(gr,fill,c,i)
        if d is None or dr is None: continue
        if d>6 and d>dr+4: bad.append((d,dr,tuple(c[i].astype(int))))
    bad.sort(reverse=True)
    print(label,'artefact lines (worse than original by >4):',len(bad),'worst',[ (round(a,1),round(b,1),p) for a,b,p in bad[:6]])
    if show and bad:
        t=[]
        for a,b,(x,y) in bad[:8]:
            x0,y0=max(0,x-25),max(0,y-25); t.append(np.hstack([cv2.resize(ref[y0:y0+50,x0:x0+50],(150,150),interpolation=cv2.INTER_NEAREST),cv2.resize(img[y0:y0+50,x0:x0+50],(150,150),interpolation=cv2.INTER_NEAREST),np.full((150,6,3),255,np.uint8)]))
        cv2.imwrite(f'bad_{label}.png',np.vstack([np.hstack(t[i:i+4]) for i in range(0,len(t)-len(t)%4 or 4,4)]) if len(t)>=4 else np.hstack(t))
    return bad
if __name__=='__main__':
    from v2 import recolor,REF
    for side in ['front','back']:
        ref=cv2.imread(REF[side])
        for col in ['white','black']:
            o,_=recolor(side,col); check(o.clip(0,255).astype(np.uint8),side,ref,f'{side}_{col}',show=1)
