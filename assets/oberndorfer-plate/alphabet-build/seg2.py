import numpy as np, json
from PIL import Image, ImageDraw
SRC="/home/user/one/assets/oberndorfer-plate/references/56.jpg"
im=Image.open(SRC).convert("L"); a=np.asarray(im).astype(np.float32)
ink = a < 100
H,W = ink.shape
BANDS=[(3,180),(240,420),(445,690),(720,905)]
out={}
vis=Image.open(SRC).convert("RGB"); d=ImageDraw.Draw(vis)
for bi,(y0,y1) in enumerate(BANDS):
    band=ink[y0:y1]; cp=band.sum(axis=0)
    runs=[];inrun=False;gap=0;s=0
    for x in range(W):
        if cp[x]>0:
            if not inrun: inrun=True;s=x
            gap=0
        else:
            if inrun:
                gap+=1
                if gap>=4:
                    e=x-gap+1
                    if e-s>12: runs.append((s,e))
                    inrun=False;gap=0
    if inrun and W-s>12: runs.append((s,W))
    out[bi]=runs
    for i,(x0,x1) in enumerate(runs):
        d.rectangle([x0,y0,x1,y1], outline=(255,0,0), width=3)
        d.text((x0+4,y0+4), str(i), fill=(255,0,0))
    print("band",bi,len(runs),runs)
vis.save("/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/work/seg-vis.png")
json.dump({str(k):v for k,v in out.items()}, open("runs.json","w"))
