"""Trace the letter mask and the vine mask separately and write a two-colour
PDF and SVG at the original page size. Letters black, decoration red."""
import numpy as np, sys
sys.path.insert(0,'/home/user/one/scripts')
_oc=np.cross
def _c(a,b,*r,**k):
    a=np.asarray(a); b=np.asarray(b)
    if a.shape[-1]==2 and b.shape[-1]==2: return a[...,0]*b[...,1]-a[...,1]*b[...,0]
    return _oc(a,b,*r,**k)
np.cross=_c
from skimage import measure
import vectorize_lineart as vl

DPI=600.0; PAGE=1500.0
X0,Y0 = 2034-40, 5332-40          # where the crop sits in the 600dpi render
S = 72.0/DPI                      # render px -> PDF points

def contours(mask, tol=1.1):
    out=[]
    mp=np.pad(mask,3,constant_values=False)
    for c in measure.find_contours(mp.astype(float),0.5):
        p=c[:, ::-1]-3
        if np.allclose(p[0],p[-1]): p=p[:-1]
        if len(p)<10: continue
        if max(np.ptp(p[:,0]),np.ptp(p[:,1]))<4: continue
        out.append(vl.fit_contour(p, line_tol=tol, curve_tol=tol*0.6, smooth_deg=32.0))
    return out

def to_pt(p):                      # mask px -> PDF points, y up
    return ((p[0]+X0)*S, PAGE-(p[1]+Y0)*S)

def pdf_ops(cs):
    o=[]
    for start,segs in cs:
        x,y=to_pt(start); o.append('%.3f %.3f m'%(x,y))
        for s in segs:
            if s[0]=='L':
                x,y=to_pt(s[1]); o.append('%.3f %.3f l'%(x,y))
            else:
                a=to_pt(s[1]); b=to_pt(s[2]); c=to_pt(s[3])
                o.append('%.3f %.3f %.3f %.3f %.3f %.3f c'%(a[0],a[1],b[0],b[1],c[0],c[1]))
        o.append('h')
    return o

def svg_d(cs):
    d=[]
    for start,segs in cs:
        x,y=to_pt(start); d.append('M%.3f %.3f'%(x,PAGE-y))
        for s in segs:
            if s[0]=='L':
                x,y=to_pt(s[1]); d.append('L%.3f %.3f'%(x,PAGE-y))
            else:
                a=to_pt(s[1]); b=to_pt(s[2]); c=to_pt(s[3])
                d.append('C%.3f %.3f %.3f %.3f %.3f %.3f'%(a[0],PAGE-a[1],b[0],PAGE-b[1],c[0],PAGE-c[1]))
        d.append('Z')
    return ' '.join(d)

letter=np.load('letter.npy'); vine=np.load('vine.npy')
cl=contours(letter); cv=contours(vine)
print('traced: letter %d contours, decoration %d contours'%(len(cl),len(cv)))

body=['0 g']+pdf_ops(cl)+['f*','0.839 0.110 0.149 rg']+pdf_ops(cv)+['f*']
cs=('\n'.join(body)+'\n').encode()
objs=[b'<< /Type /Catalog /Pages 2 0 R >>',
      b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.0f %.0f] /Contents 4 0 R /Resources << >> >>'%(PAGE,PAGE)).encode(),
      ('<< /Length %d >>\nstream\n'%len(cs)).encode()+cs+b'endstream']
out=bytearray(b'%PDF-1.4\n'); offs=[]
for i,o in enumerate(objs,1):
    offs.append(len(out)); out+=('%d 0 obj\n'%i).encode()+o+b'\nendobj\n'
x=len(out)
out+=('xref\n0 %d\n'%(len(objs)+1)).encode()+b'0000000000 65535 f \n'
for o in offs: out+=('%010d 00000 n \n'%o).encode()
out+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'%(len(objs)+1,x)).encode()
open('logo-red-ornament.pdf','wb').write(bytes(out))

svg=('<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
     '<path fill="#111111" fill-rule="evenodd" d="%s"/>'
     '<path fill="#D61C26" fill-rule="evenodd" d="%s"/></svg>')%(PAGE,PAGE,PAGE,PAGE,svg_d(cl),svg_d(cv))
open('logo-red-ornament.svg','w').write(svg)
print('wrote logo-red-ornament.pdf and .svg  (%.0f x %.0f pt)'%(PAGE,PAGE))
