import re, sys
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

ARC=sys.argv[1]; OUT=sys.argv[2]
FONT='/tmp/claude-0/-home-user-one/e41bc041-1735-5f25-b722-feca72576a19/scratchpad/fonts/inter700.ttf'
svg=open(ARC).read()
m=re.search(r'width="([\d.]+)" height="([\d.]+)"', svg); W,H=float(m.group(1)),float(m.group(2))
d=re.search(r'd="(.*?)"', svg, re.S).group(1)

# arc polygons: parse the M/L/Z path back out
polys=[]; cur=[]
for tok in re.findall(r'[MLZ][^MLZ]*', d):
    c=tok[0]; rest=tok[1:].strip()
    if c=='Z':
        if cur: polys.append(cur); cur=[]
    else:
        x,y=rest.split(','); cur.append((float(x),float(y)))
if cur: polys.append(cur)
xs=[p[0] for q in polys for p in q]; ys=[p[1] for q in polys for p in q]
AX0,AX1,AY0,AY1=min(xs),max(xs),min(ys),max(ys)
print('arc bbox %.1f..%.1f x %.1f..%.1f pt'%(AX0,AX1,AY0,AY1))

class PDFPen(BasePen):
    def __init__(self, glyphSet, ops, sx, sy, dx, dy, pageh):
        super().__init__(glyphSet); self.o=ops; self.sx=sx; self.sy=sy; self.dx=dx; self.dy=dy; self.ph=pageh
    def _t(self,p): return (p[0]*self.sx+self.dx, self.ph-(p[1]*self.sy+self.dy))
    def _moveTo(self,p): x,y=self._t(p); self.o.append('%.3f %.3f m'%(x,y))
    def _lineTo(self,p): x,y=self._t(p); self.o.append('%.3f %.3f l'%(x,y))
    def _curveToOne(self,a,b,c):
        ax,ay=self._t(a); bx,by=self._t(b); cx,cy=self._t(c)
        self.o.append('%.3f %.3f %.3f %.3f %.3f %.3f c'%(ax,ay,bx,by,cx,cy))
    def _closePath(self): self.o.append('h')

f=TTFont(FONT); upm=f['head'].unitsPerEm; cmap=f.getBestCmap(); gs=f.getGlyphSet(); hmtx=f['hmtx']
TXT='MILANO'
CAP=AY1-AY0
SIZE=CAP*0.215; TRACK=SIZE*0.26
sc=SIZE/upm
adv=[hmtx[cmap[ord(c)]][0]*sc for c in TXT]
total=sum(adv)+TRACK*(len(TXT)-1)
GAP=CAP*0.26
PAGEH=AY1+GAP+SIZE*0.78+ (AY0)
PAGEW=W
x=(AX0+AX1)/2.0-total/2.0
ybase=AY1+GAP+SIZE*0.74

ops=[]
for q in polys:
    for i,(px,py) in enumerate(q):
        ops.append('%.3f %.3f %s'%(px, PAGEH-py, 'm' if i==0 else 'l'))
    ops.append('h')
ops.append('f*')
for c,a in zip(TXT,adv):
    pen=PDFPen(gs, ops, sc, -sc, x, ybase, PAGEH)
    gs[cmap[ord(c)]].draw(pen)
    ops.append('f*')
    x+=a+TRACK

stream=' '.join(ops).encode()
objs=[b'<< /Type /Catalog /Pages 2 0 R >>',
      b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents 4 0 R /Resources << >> >>'%(PAGEW,PAGEH)).encode(),
      ('<< /Length %d >>\nstream\n'%len(stream)).encode()+stream+b'\nendstream']
pdf=b'%PDF-1.4\n'; offs=[]
for i,o in enumerate(objs,1):
    offs.append(len(pdf)); pdf+=('%d 0 obj\n'%i).encode()+o+b'\nendobj\n'
xref=len(pdf)
pdf+=('xref\n0 %d\n'%(len(objs)+1)).encode()+b'0000000000 65535 f \n'
for o in offs: pdf+=('%010d 00000 n \n'%o).encode()
pdf+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF'%(len(objs)+1,xref)).encode()
open(OUT,'wb').write(pdf)
print('wrote',OUT,'page %.1f x %.1f pt  MILANO %.1fpt'%(PAGEW,PAGEH,SIZE))
