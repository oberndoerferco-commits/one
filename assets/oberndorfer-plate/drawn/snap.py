"""Rebuild letter outlines as exact geometry: long runs become true straight
lines snapped to the drawing's own dominant angles, corners are the real
intersections of those lines, and genuinely round runs stay curved."""
import numpy as np, math, sys, collections
from PIL import Image

SRC=sys.argv[1]; OUT=sys.argv[2]
RDP=float(sys.argv[3]) if len(sys.argv)>3 else 5.0
SNAP=float(sys.argv[4]) if len(sys.argv)>4 else 10.0   # deg
MINLEN=float(sys.argv[5]) if len(sys.argv)>5 else 55.0 # px: a 'long run'

g=np.asarray(Image.open(SRC).convert('L')); ink=g<128
H,W=ink.shape

def contours(mask):
    from skimage import measure
    return [c[:, ::-1] for c in measure.find_contours(mask.astype(float), 0.5)]

def rdp(p, eps):
    if len(p)<3: return p
    d=p[-1]-p[0]; L=np.hypot(*d)
    if L<1e-9:
        dist=np.hypot(*(p-p[0]).T)
    else:
        q=p-p[0]
        dist=np.abs(d[0]*q[:,1]-d[1]*q[:,0])/L
    i=int(np.argmax(dist))
    if dist[i]>eps:
        return np.vstack([rdp(p[:i+1],eps)[:-1], rdp(p[i:],eps)])
    return np.vstack([p[0],p[-1]])

cs=[rdp(np.vstack([c,c[:1]]), RDP) for c in contours(ink)]
cs=[c for c in cs if len(c)>=4]

# dominant edge angles across the whole word, weighted by length
angs=[]; lens=[]
for c in cs:
    for a,b in zip(c[:-1],c[1:]):
        v=b-a; L=np.hypot(*v)
        if L>=MINLEN:
            angs.append(math.degrees(math.atan2(v[1],v[0]))%180.0); lens.append(L)
angs=np.array(angs); lens=np.array(lens)
hist=np.zeros(180)
for a,L in zip(angs,lens): hist[int(round(a))%180]+=L
k=np.ones(7)/7.0
hs=np.convolve(np.r_[hist[-7:],hist,hist[:7]],k,mode='same')[7:-7]
peaks=[i for i in range(180) if hs[i]==max(hs[max(0,i-6):i+7]) and hs[i]>hs.mean()*1.3]
print('dominant stroke angles (deg):', peaks)

def snap_ang(a):
    best=None;bd=1e9
    for p in peaks:
        d=min(abs(a-p),180-abs(a-p))
        if d<bd: bd=d; best=p
    return (best,bd)

out=[]
for c in cs:
    pts=c[:-1]; n=len(pts)
    lines=[]
    for i in range(n):
        a=pts[i]; b=pts[(i+1)%n]
        v=b-a; L=np.hypot(*v)
        ang=math.degrees(math.atan2(v[1],v[0]))%180.0
        if L>=MINLEN:
            s,d=snap_ang(ang)
            if d<=SNAP: ang=float(s)
            lines.append(('line',a,b,ang,L))
        else:
            lines.append(('keep',a,b,ang,L))
    # re-intersect consecutive snapped lines so corners are exact
    res=[]
    for i,(kind,a,b,ang,L) in enumerate(lines):
        if kind!='line': res.append(b); continue
        th=math.radians(ang); d=np.array([math.cos(th),math.sin(th)])
        mid=(a+b)/2.0
        j=(i+1)%n
        kind2,a2,b2,ang2,L2=lines[j]
        if kind2=='line':
            th2=math.radians(ang2); d2=np.array([math.cos(th2),math.sin(th2)])
            M=np.array([[d[0],-d2[0]],[d[1],-d2[1]]])
            if abs(np.linalg.det(M))>1e-6:
                mid2=(a2+b2)/2.0
                t=np.linalg.solve(M, mid2-mid)
                res.append(mid+t[0]*d); continue
        res.append(b)
    out.append(np.array(res))

# rasterise the result so it can be checked and re-traced
from PIL import ImageDraw
im=Image.new('L',(W,H),255); d=ImageDraw.Draw(im)
areas=[(abs(0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])),p) for p in out]
areas.sort(key=lambda t:-t[0])
for a,p in areas:
    d.polygon([tuple(q) for q in p], fill=0)
# holes: redraw smaller contours in white if they sit inside a bigger one
for a,p in areas[1:]:
    cx,cy=p[:,0].mean(),p[:,1].mean()
    for a2,p2 in areas:
        if a2<=a: continue
        if p2[:,0].min()<cx<p2[:,0].max() and p2[:,1].min()<cy<p2[:,1].max():
            d.polygon([tuple(q) for q in p], fill=255); break
im.save(OUT)

# --- emit the polygons straight to vector (no re-tracing) ---
import os
base=os.path.splitext(OUT)[0]
k=72.0/300.0                      # 300 dpi source -> points
wpt,hpt=W*k,H*k
def dpath(p, flipy):
    q=[]
    for i,(x,y) in enumerate(p):
        X=x*k; Y=(hpt-y*k) if flipy else y*k
        q.append(('M' if i==0 else 'L')+'%.3f,%.3f'%(X,Y))
    return ' '.join(q)+' Z'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="%.2f" height="%.2f" viewBox="0 0 %.2f %.2f">'%(wpt,hpt,wpt,hpt)]
svg.append('<path fill-rule="evenodd" fill="#000" d="%s"/>'%(' '.join(dpath(p,False) for p in out)))
svg.append('</svg>')
open(base+'.svg','w').write('\n'.join(svg))
ops=[]
for p in out:
    for i,(x,y) in enumerate(p):
        ops.append('%.3f %.3f %s'%(x*k, hpt-y*k, 'm' if i==0 else 'l'))
    ops.append('h')
ops.append('f*')
stream=' '.join(ops).encode()
objs=[]
objs.append(b'<< /Type /Catalog /Pages 2 0 R >>')
objs.append(('<< /Type /Pages /Kids [3 0 R] /Count 1 >>').encode())
objs.append(('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents 4 0 R /Resources << >> >>'%(wpt,hpt)).encode())
objs.append(('<< /Length %d >>\nstream\n'%len(stream)).encode()+stream+b'\nendstream')
pdf=b'%PDF-1.4\n'; offs=[]
for i,o in enumerate(objs,1):
    offs.append(len(pdf)); pdf+=('%d 0 obj\n'%i).encode()+o+b'\nendobj\n'
xref=len(pdf)
pdf+=('xref\n0 %d\n'%(len(objs)+1)).encode()+b'0000000000 65535 f \n'
for o in offs: pdf+=('%010d 00000 n \n'%o).encode()
pdf+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF'%(len(objs)+1,xref)).encode()
open(base+'.pdf','wb').write(pdf)
print('wrote',OUT,base+'.svg',base+'.pdf','| contours',len(out))
