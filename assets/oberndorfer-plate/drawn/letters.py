import numpy as np, collections, json
from PIL import Image
g=np.asarray(Image.open('clean.png').convert('L'))
ink=g<128; H,W=ink.shape
lab=np.zeros((H,W),np.int32); cur=0; comps=[]
for sy,sx in np.argwhere(ink):
    if lab[sy,sx]: continue
    cur+=1; q=collections.deque([(sy,sx)]); lab[sy,sx]=cur; pts=[]
    while q:
        y,x=q.popleft(); pts.append((y,x))
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<H and 0<=nx<W and ink[ny,nx] and not lab[ny,nx]:
                lab[ny,nx]=cur; q.append((ny,nx))
    p=np.array(pts)
    if len(p)<300: continue
    comps.append(dict(id=cur,x0=int(p[:,1].min()),x1=int(p[:,1].max()),
                      y0=int(p[:,0].min()),y1=int(p[:,0].max()),n=len(p)))
bodies=[c for c in comps if (c['y1']-c['y0'])>400]
bodies.sort(key=lambda c:c['x0'])
small=[c for c in comps if (c['y1']-c['y0'])<=400]
NAME=list('OBERNDÖRFER')
assert len(bodies)==len(NAME), (len(bodies),len(NAME))
for b,ch in zip(bodies,NAME): b['ch']=ch
# attach each small piece to the body it overlaps most in x
for s in small:
    best=None;bv=-1
    for b in bodies:
        ov=min(s['x1'],b['x1'])-max(s['x0'],b['x0'])
        if ov>bv: bv=ov; best=b
    best.setdefault('extra',[]).append(s)
sprites=[]
for b in bodies:
    ids=[b['id']]+[s['id'] for s in b.get('extra',[])]
    m=np.isin(lab,ids)
    ys=np.where(m.any(axis=1))[0]; xs=np.where(m.any(axis=0))[0]
    sub=m[ys[0]:ys[-1]+1, xs[0]:xs[-1]+1]
    sprites.append(dict(ch=b['ch'], mask=sub, base=b['y1'], top=b['y0'],
                        x0=int(xs[0]), y0=int(ys[0]), w=sub.shape[1], h=sub.shape[0]))
    print('%s  w=%4d h=%4d  body top=%d base=%d  pieces=%d'%(b['ch'],sub.shape[1],sub.shape[0],b['y0'],b['y1'],len(ids)))
np.save('sprites.npy', np.array(sprites, dtype=object), allow_pickle=True)
