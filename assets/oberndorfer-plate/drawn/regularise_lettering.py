import sys, os, argparse
import numpy as np
# numpy 2 dropped 2-D np.cross; the repo's tracer still uses it
_oc = np.cross
def _cross(a, b, *rest, **kw):
    a = np.asarray(a); b = np.asarray(b)
    if a.shape[-1] == 2 and b.shape[-1] == 2:
        return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]
    return _oc(a, b, *rest, **kw)
np.cross = _cross
sys.path.insert(0, '/home/user/one/scripts')
import vectorize_lineart as vl
from regularise import regularise

ap=argparse.ArgumentParser()
ap.add_argument('image'); ap.add_argument('outdir'); ap.add_argument('--name',default='reg')
ap.add_argument('--dpi',type=float,default=132.0)
ap.add_argument('--sigma',type=float,default=0.6)
ap.add_argument('--corner-deg',type=float,default=36.0)
ap.add_argument('--corner-span',type=int,default=9)
ap.add_argument('--straight-tol',type=float,default=0.9)
ap.add_argument('--fit-tol',type=float,default=1.6)
ap.add_argument('--merge',type=float,default=6.0)
a=ap.parse_args()

gray,(w,h)=vl.load_gray(a.image)
cons=vl.trace(gray, sigma=a.sigma)
reg=[regularise(c, corner_deg=a.corner_deg, corner_span=a.corner_span,
                straight_tol=a.straight_tol, fit_tol=a.fit_tol, merge=a.merge)
     for c in cons]
nodes=lambda fs: sum(len(s[1]) for s in fs)
print('contours %d | nodes before %d  after %d'%(len(cons),nodes(cons),nodes(reg)))
k=72.0/a.dpi; wpt,hpt=w*k,h*k
to_svg=lambda p:(p[0]*k,p[1]*k)
to_pdf=lambda p:(p[0]*k,hpt-p[1]*k)
svg,_,_=vl.emit(reg,to_svg)
_,pdf,ps=vl.emit(reg,to_pdf)
os.makedirs(a.outdir,exist_ok=True)
b=os.path.join(a.outdir,a.name)
vl.write_svg(b+'.svg',svg,wpt,hpt); vl.write_pdf(b+'.pdf',pdf,wpt,hpt); vl.write_eps(b+'.eps',ps,wpt,hpt)
print('wrote',a.name)
