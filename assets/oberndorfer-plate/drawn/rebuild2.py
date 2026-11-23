import numpy as np, sys
from PIL import Image
sp=list(np.load('sprites.npy', allow_pickle=True))
NAME=list('OBERNDÖRFER')
GAP=float(sys.argv[1]) if len(sys.argv)>1 else 150.0
for s in sp: s['baseoff']=s['base']-s['y0']
canon={}
for ch in set(NAME):
    inst=[s for s in sp if s['ch']==ch]
    w=[i['w'] for i in inst]
    canon[ch]=inst[int(np.argsort(w)[len(w)//2])]
rows=[canon[c] for c in NAME]
BASE=max(r['baseoff'] for r in rows); TOP=max(r['h']-r['baseoff'] for r in rows)
Hc=BASE+TOP+80
x=60; placed=[]
for s in rows:
    m=s['mask']; h,w=m.shape
    ytop=40+TOP-(h-s['baseoff'])
    placed.append((int(x),ytop,m)); x+=w+GAP
Wc=int(x)+60
out=np.zeros((Hc,Wc),bool)
for px,ytop,m in placed:
    h,w=m.shape; out[ytop:ytop+h, px:px+w] |= m
ys=np.where(out.any(axis=1))[0]; xs=np.where(out.any(axis=0))[0]
out=out[max(0,ys[0]-20):ys[-1]+21, max(0,xs[0]-20):xs[-1]+21]
Image.fromarray(np.where(out,0,255).astype(np.uint8)).save('rebuilt2.png')
print('gap %.0f -> %dx%d (as drawn was 7041x825)'%(GAP,out.shape[1],out.shape[0]))
