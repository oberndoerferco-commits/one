"""Read the spacing straight off the original artwork instead of computing it.
His letters do not overlap, so each one's x position is exactly what he drew."""
import json, numpy as np
from PIL import Image
import pymupdf as fitz
from fontTools.ttLib import TTFont

PDF='/root/.claude/uploads/e41bc041-1735-5f25-b722-feca72576a19/8b158ad0-Untitled_Artwork_4.pdf'
NAME='OBERNDÖRFER'; CAP=700

pix=fitz.open(PDF)[0].get_pixmap(dpi=200)
a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,0]
ink=a<200
cols=ink.any(0); rows=ink.any(1)
base=np.nonzero(rows)[0][-1]
wrow=ink.sum(1); y0=np.nonzero(rows)[0][0]
cap=next(j for j in range(y0,base) if wrow[j]>0.35*wrow.max())
k=CAP/float(base-cap)                                   # px -> font units

import scipy.ndimage as ndi
lab,n=ndi.label(cols)
assert n==len(NAME), 'expected %d letters, found %d'%(len(NAME),n)
runs=[(np.nonzero(lab==i)[0][0], np.nonzero(lab==i)[0][-1]) for i in range(1,n+1)]
lefts=[r[0] for r in runs]; widths=[(r[1]-r[0])*k for r in runs]
his_adv=[(lefts[i+1]-lefts[i])*k for i in range(n-1)]

f=TTFont('_build.ttf'); g=f['glyf']; cm=f.getBestCmap()
mine={}
for ch in set(NAME):
    gl=g[cm[ord(ch)]]; gl.recalcBounds(g); mine[ch]=gl.xMax-gl.xMin

print('%-3s %10s %10s %8s'%('','his ink','my ink','diff'))
for i,ch in enumerate(NAME):
    print('%-3s %10.0f %10d %7.1f%%'%(ch,widths[i],mine[ch],100*(mine[ch]-widths[i])/widths[i]))

gaps=[his_adv[i]-widths[i] for i in range(n-1)]
GAP=float(np.mean(gaps))
print('\nhis gap between letters: %.0f .. %.0f units, mean %.0f'%(min(gaps),max(gaps),GAP))

adv={ch:int(round(mine[ch]+GAP)) for ch in mine}
kern={}
for i in range(n-1):
    a_,b_=NAME[i],NAME[i+1]
    v=his_adv[i]-adv[a_]
    kern.setdefault((a_,b_),[]).append(v)
kern={p:int(round(np.mean(v))) for p,v in kern.items() if abs(np.mean(v))>=3}
print('\nadvances:', {c:adv[c] for c in NAME if True})
print('kerns from his own spacing:', {a+b:v for (a,b),v in kern.items()})
json.dump({'advances':adv,'kerns':{a+'|'+b:v for (a,b),v in kern.items()},'gap':GAP},
          open('drawing_spacing.json','w'), ensure_ascii=False, indent=1)
print('\nwrote drawing_spacing.json')
