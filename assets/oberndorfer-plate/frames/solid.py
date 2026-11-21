import numpy as np
from PIL import Image, ImageFilter
H="/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/w2"
im=Image.open(H+"/schrift-bw.png").convert("RGBA")
a=np.asarray(im)
ink=(a[:,:,3]>120)&(a[:,:,:3].mean(axis=2)<128)   # the drawn strokes + stripes
print("wordmark",im.size,"ink frac %.3f"%ink.mean())
# measure vertical gap runs inside the ink region
col=ink[:, ink.any(axis=0)]
gaps=[]
for x in range(0,col.shape[1],7):
    c=col[:,x]; run=0
    on=np.where(c)[0]
    if len(on)<2: continue
    for y in range(on[0],on[-1]):
        if not c[y]: run+=1
        elif run: gaps.append(run); run=0
g=np.array(gaps)
print("gap runs: median %d  p75 %d  p90 %d  p97 %d"%(np.median(g),np.percentile(g,75),np.percentile(g,90),np.percentile(g,97)))
base=Image.fromarray((ink*255).astype(np.uint8))
for k in (7,9,11,13,15):
    closed=base.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    m=np.asarray(closed)>127
    print("k=%2d  fill frac %.3f"%(k,m.mean()))
    out=np.dstack([np.zeros(m.shape+(3,),np.uint8), (m*255).astype(np.uint8)])
    Image.fromarray(out,"RGBA").save(H+"/solid-k%d.png"%k)
    bg=Image.new("RGB",m.shape[::-1],(255,255,255))
    bg.paste(Image.fromarray(out,"RGBA"),(0,0),Image.fromarray(out,"RGBA"))
    bg.save(H+"/solid-k%d-chk.png"%k)
