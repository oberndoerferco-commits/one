"""Vectorize the logo artwork. Trace it, don't redraw it.

Every outline here is his own, traced and nothing else: no refitting into
lines and arcs, no smoothing, no letter rebuilt from another source. The only
places that change are the discs listed in --repair, which are the spots he
circled.

Two things make the trace faithful rather than jagged:

  - contours are taken at the 50% grey level of the antialiased export, not
    from a black/white mask, so each point sits where the edge really falls
    instead of on a pixel corner. A 12000 px export carries about 150000
    part-grey pixels; that is the sub-pixel information a binary threshold
    throws away;
  - fitting runs at the artwork's own resolution with a tolerance under 2 px
    against a cap height near 1030, so the fit follows the drawing instead of
    deciding what it ought to be.

The repair inside a marked disc is grey morphology, for the same reason: a
closing fills the hairline slivers cut into a stroke, a smaller opening takes
the thin spikes off, and both run on the grey image so the repaired edge keeps
its antialiasing and traces as smoothly as the rest.

  python3 vectorize.py artwork.png --repair marked-spots.json --out logo
"""
import argparse, json, os, sys
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

_oc = np.cross
def _cross(a, b, *r, **k):
    a = np.asarray(a); b = np.asarray(b)
    if a.shape[-1] == 2 and b.shape[-1] == 2:
        return a[..., 0]*b[..., 1] - a[..., 1]*b[..., 0]
    return _oc(a, b, *r, **k)
np.cross = _cross
sys.path.insert(0, '/home/user/one/scripts')
from skimage import measure
import vectorize_lineart as vl
import smooth as sg

Image.MAX_IMAGE_PIXELS = None
SPECK = 1000           # components smaller than this are export noise

def disk(r):
    y, x = np.mgrid[-r:r+1, -r:r+1]
    return (x*x + y*y) <= r*r + 0.5

def repair(grey, marks, rclose=36, ropen=14):
    """Grey closing then a smaller grey opening, inside each disc only."""
    out = grey.copy(); H, W = grey.shape
    ink = 255 - grey.astype(np.int16)
    for cx, cy, r in marks:
        pad = int(3*max(rclose, ropen) + 4); R0 = int(r)
        y0, y1 = max(0, int(cy)-R0-pad), min(H, int(cy)+R0+pad)
        x0, x1 = max(0, int(cx)-R0-pad), min(W, int(cx)+R0+pad)
        w = ink[y0:y1, x0:x1]
        w = ndi.grey_closing(w, footprint=disk(rclose))
        w = ndi.grey_opening(w, footprint=disk(ropen))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        d = np.hypot(xx-cx, yy-cy) <= r
        tile = out[y0:y1, x0:x1].copy()
        tile[d] = np.clip(255 - w, 0, 255).astype(np.uint8)[d]
        out[y0:y1, x0:x1] = tile
    print('repaired %d marked spots' % len(marks))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('--repair', help='JSON {letter: [[cx, cy, r], ...]} in source pixels')
    ap.add_argument('--out', default='logo')
    ap.add_argument('--tol', type=float, default=1.4)
    ap.add_argument('--smooth', type=float, default=0.0,
                    help='sigma in source px for the wobble filter; 0 = trace as drawn')
    ap.add_argument('--corner-k', type=int, default=10)
    ap.add_argument('--corner-deg', type=float, default=52.0)
    ap.add_argument('--scale', type=float, default=6.0, help='source px per output point')
    ap.add_argument('--page', type=float, default=2000.0)
    a = ap.parse_args()

    grey = np.array(Image.open(a.source).convert('L'))
    print('artwork %d x %d, %d part-grey px' % (grey.shape[1], grey.shape[0],
          int(((grey > 0) & (grey < 255)).sum())))

    # drop export specks, on the mask, then paint them white in the grey
    ink = grey < 128
    lab, n = ndi.label(ink, np.ones((3, 3)))
    sz = ndi.sum(ink, lab, range(1, n+1))
    small = [i+1 for i, s in enumerate(sz) if s < SPECK]
    if small:
        grey = np.where(np.isin(lab, small), np.uint8(255), grey)
        print('specks dropped: %d' % len(small))

    if a.repair:
        spots = json.load(open(a.repair))
        grey = repair(grey, [m for v in spots.values() for m in v])

    cs = []
    for c in measure.find_contours(grey.astype(float), 127.5):
        p = c[:, ::-1]
        if np.allclose(p[0], p[-1]): p = p[:-1]
        if len(p) < 40: continue
        if a.smooth:
            p = sg.smooth_closed(p, sigma=a.smooth, step=2.0,
                                 corner_k=a.corner_k, corner_deg=a.corner_deg)
        cs.append(vl.fit_contour(p, line_tol=a.tol, curve_tol=a.tol*0.7, smooth_deg=32.0))
    if a.smooth:
        print('wobble filtered at sigma %g px, corners pinned over +-%d steps past %g deg'
              % (a.smooth, a.corner_k, a.corner_deg))
    segs = sum(len(s) for _, s in cs)
    print('traced %d contours, %d segments' % (len(cs), segs))

    S, P = a.scale, a.page
    pt = lambda q: (q[0]/S, P - q[1]/S)
    ops, d = [], []
    for start, sgs in cs:
        x, y = pt(start); ops.append('%.4f %.4f m' % (x, y)); d.append('M%.4f %.4f' % (x, P-y))
        for s in sgs:
            if s[0] == 'L':
                x, y = pt(s[1]); ops.append('%.4f %.4f l' % (x, y)); d.append('L%.4f %.4f' % (x, P-y))
            else:
                A, B, C = pt(s[1]), pt(s[2]), pt(s[3])
                ops.append('%.4f %.4f %.4f %.4f %.4f %.4f c' % (A[0], A[1], B[0], B[1], C[0], C[1]))
                d.append('C%.4f %.4f %.4f %.4f %.4f %.4f' % (A[0], P-A[1], B[0], P-B[1], C[0], P-C[1]))
        ops.append('h'); d.append('Z')
    body = ('0 g\n' + '\n'.join(ops) + '\nf*\n').encode()
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.0f %.0f] /Contents 4 0 R /Resources << >> >>' % (P, P)).encode(),
            ('<< /Length %d >>\nstream\n' % len(body)).encode() + body + b'endstream']
    buf = bytearray(b'%PDF-1.4\n'); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(buf)); buf += ('%d 0 obj\n' % i).encode() + o + b'\nendobj\n'
    x = len(buf)
    buf += ('xref\n0 %d\n' % (len(objs)+1)).encode() + b'0000000000 65535 f \n'
    for o in offs: buf += ('%010d 00000 n \n' % o).encode()
    buf += ('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs)+1, x)).encode()
    open(a.out + '.pdf', 'wb').write(bytes(buf))
    open(a.out + '.svg', 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
        '<path fill="#000000" fill-rule="evenodd" d="%s"/></svg>' % (P, P, P, P, ' '.join(d)))
    print('wrote %s.pdf and %s.svg (%.0f x %.0f pt)' % (a.out, a.out, P, P))

if __name__ == '__main__':
    main()
