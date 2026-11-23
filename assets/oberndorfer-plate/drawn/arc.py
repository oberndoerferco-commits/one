import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont
sp=list(np.load('sprites.npy', allow_pickle=True))
NAME=list('OBERNDÖRFER')
GAP=float(sys.argv[1]) if len(sys.argv)>1 else 150.0
RISEF=float(sys.argv[2]) if len(sys.argv)>2 else 0.055
for s in sp: s['baseoff']=s['base']-s['y0']
canon={}
for ch in set(NAME):
    inst=[s for s in sp if s['ch']==ch]
    canon[ch]=inst[int(np.argsort([i['w'] for i in inst])[len(inst)//2])]
rows=[canon[c] for c in NAME]
adv=[r['w']+GAP for r in rows[:-1]]+[rows[-1]['w']]
L=sum(adv)                                   # arc length of the baseline
rise=RISEF*L
R=(rise/2.0)+(L*L)/(8.0*rise)                # circle through chord L with sagitta rise
theta=L/R
print('arc length %.0f  rise %.0f  radius %.0f  sweep %.1f deg'%(L,rise,R,math.degrees(theta)))

PAD=160
cx,cy = 0.0, R                               # centre of the circle, arc apex at origin
pos=[]; run=0.0
for r,a in zip(rows,adv):
    centre_s = run + r['w']/2.0              # arc-length to this letter's baseline centre
    run += a
    t = (centre_s - L/2.0)/R                 # angle from apex
    px = R*math.sin(t); py = R - R*math.cos(t)
    pos.append((px,py,math.degrees(t)))

canvW = int(L+2*PAD); canvH = int(rise + max(r['h'] for r in rows) + 2*PAD)
cv = Image.new('RGBA',(canvW,canvH),(0,0,0,0))
for r,(px,py,deg) in zip(rows,pos):
    m=r['mask']; h,w=m.shape
    sprite=Image.fromarray(np.dstack([np.zeros((h,w,3),np.uint8),(m*255).astype(np.uint8)]),'RGBA')
    # put the baseline-centre anchor at the middle of a square canvas, then rotate rigidly
    S=int(math.hypot(w,h))+8
    box=Image.new('RGBA',(S*2,S*2),(0,0,0,0))
    box.alpha_composite(sprite,(S-int(w/2), S-int(r['baseoff'])))
    rot=box.rotate(-deg, resample=Image.BICUBIC, center=(S,S))
    X=int(PAD+L/2.0+px-S); Y=int(PAD+py-S+ (max(rr['h'] for rr in rows)-0))
    cv.alpha_composite(rot,(X,Y))
a=np.asarray(cv)[:,:,3]
ys=np.where(a.any(axis=1))[0]; xs=np.where(a.any(axis=0))[0]
cv=cv.crop((xs[0]-20,ys[0]-20,xs[-1]+21,ys[-1]+21))
bg=Image.new('RGB',cv.size,(255,255,255)); bg.paste(cv,(0,0),cv)
bg.save('arc-word.png'); print('arc word',cv.size)
