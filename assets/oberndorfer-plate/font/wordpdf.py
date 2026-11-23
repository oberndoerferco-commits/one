import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen

TTF='OberndorferDrawn-Regular.ttf'; TXT='OBERNDÖRFER'; SIZE=200.0   # points
f=TTFont(TTF); upm=f['head'].unitsPerEm; cmap=f.getBestCmap(); gs=f.getGlyphSet(); hmtx=f['hmtx']
sc=SIZE/upm
adv=[hmtx[cmap[ord(c)]][0]*sc for c in TXT]

class Box(BasePen):
    def __init__(self,gs): super().__init__(gs); self.xs=[]; self.ys=[]
    def _moveTo(self,p): self.xs.append(p[0]); self.ys.append(p[1])
    def _lineTo(self,p): self.xs.append(p[0]); self.ys.append(p[1])
    def _curveToOne(self,a,b,c):
        for q in (a,b,c): self.xs.append(q[0]); self.ys.append(q[1])
    def _closePath(self): pass
ys=[]
for c in TXT:
    b=Box(gs); gs[cmap[ord(c)]].draw(b); ys+=[min(b.ys)*sc,max(b.ys)*sc]
YMIN,YMAX=min(ys),max(ys)
M=SIZE*0.12
PW=sum(adv)+2*M; PH=(YMAX-YMIN)+2*M

class PDFPen(BasePen):
    def __init__(self,gs,ops,dx,dy): super().__init__(gs); self.o=ops; self.dx=dx; self.dy=dy
    def _t(self,p): return (p[0]*sc+self.dx, p[1]*sc+self.dy)
    def _moveTo(self,p): self.o.append('%.3f %.3f m'%self._t(p))
    def _lineTo(self,p): self.o.append('%.3f %.3f l'%self._t(p))
    def _curveToOne(self,a,b,c):
        self.o.append('%.3f %.3f %.3f %.3f %.3f %.3f c'%(self._t(a)+self._t(b)+self._t(c)))
    def _closePath(self): self.o.append('h')

ops=[]; x=M
for c,a in zip(TXT,adv):
    pen=PDFPen(gs,ops,x,M-YMIN); gs[cmap[ord(c)]].draw(pen); x+=a
ops.append('f')
stream=' '.join(ops).encode()
objs=[b'<< /Type /Catalog /Pages 2 0 R >>',
      b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents 4 0 R /Resources << >> >>'%(PW,PH)).encode(),
      ('<< /Length %d >>\nstream\n'%len(stream)).encode()+stream+b'\nendstream']
pdf=b'%PDF-1.4\n'; offs=[]
for i,o in enumerate(objs,1):
    offs.append(len(pdf)); pdf+=('%d 0 obj\n'%i).encode()+o+b'\nendobj\n'
xref=len(pdf)
pdf+=('xref\n0 %d\n'%(len(objs)+1)).encode()+b'0000000000 65535 f \n'
for o in offs: pdf+=('%010d 00000 n \n'%o).encode()
pdf+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF'%(len(objs)+1,xref)).encode()
open('wordmark.pdf','wb').write(pdf)

# SVG too
parts=[]; x=M
for c,a in zip(TXT,adv):
    p=SVGPathPen(gs); gs[cmap[ord(c)]].draw(p); d=p.getCommands()
    if d: parts.append('<g transform="translate(%.3f,%.3f) scale(%.5f,%.5f)"><path d="%s"/></g>'%(x, PH-(M-YMIN), sc, -sc, d))
    x+=a
open('wordmark.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="%.2f" height="%.2f" viewBox="0 0 %.2f %.2f"><g fill="#000">%s</g></svg>'%(PW,PH,PW,PH,''.join(parts)))
print('wrote wordmark.pdf and wordmark.svg  page %.1f x %.1f pt'%(PW,PH))
