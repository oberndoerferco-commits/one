"""Rebuild named letters of the logo out of true primitives, leave the rest alone.

The reference artwork (Canva "Logo 2026" page 18, exported as PNG because the
PDF export does not match the screen) is a raster. Most of its letters are
already right. The ones named with --fix are hand-edited and carry the wobble
of a hand-drawn edge: the outline weaves by a few px, and what should be one
curve is a chain of small arcs pulling in different directions.

For those letters each outline is taken apart into pieces that are each either
an exact straight segment or an exact circular arc (font/reconstruct.py), and
the neighbouring pieces are re-intersected, so a straight edge is straight to
the last decimal and a curve is a real circle. There is nothing left in between
for wobble to live in. Every other letter is traced as it stands.

Two details that cost a pass each:

  - the letters are refitted at a 700 px cap height, the size reconstruct.py's
    tolerances were tuned at, and mapped back afterwards. The output is vector,
    so nothing is lost by fitting small;
  - parts under 18% of the cap height -- the umlaut dots -- are traced, not
    refitted. At that size the fitter has too few points per piece and turns a
    diamond into a heart.

  python3 fix_letters.py page18.png --fix O B D Oe M Om --out logo-final
"""
import argparse, os, sys
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

# numpy 2 dropped 2-D np.cross, which the repo's tracer uses
_oc = np.cross
def _cross(a, b, *r, **k):
    a = np.asarray(a); b = np.asarray(b)
    if a.shape[-1] == 2 and b.shape[-1] == 2:
        return a[..., 0]*b[..., 1] - a[..., 1]*b[..., 0]
    return _oc(a, b, *r, **k)
np.cross = _cross

os.environ.setdefault('MAXR', '1400')        # above this radius, call it a line
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'font'))
sys.path.insert(0, '/home/user/one/scripts')
from skimage import measure
import reconstruct as RC
import vectorize_lineart as vl

Image.MAX_IMAGE_PIXELS = None
FIT_CAP = 700.0        # refit every letter at this cap height
SMALL_PART = 0.18      # below this share of the cap, trace instead of refit
SPECK = 1000           # components this small are export noise

# the artwork's letter boxes, in source pixels
TOPY, MILY = (4700, 6100), (6450, 7300)
LETTERS = [('O',  TOPY, (120, 1290)),  ('B',  TOPY, (1300, 2320)),
           ('E',  TOPY, (2330, 3290)), ('R1', TOPY, (3300, 4400)),
           ('N',  TOPY, (4460, 5600)), ('D',  TOPY, (5660, 6650)),
           ('Oe', TOPY, (6700, 7920)), ('R2', TOPY, (7930, 8950)),
           ('F',  TOPY, (8990, 10010)),('E2', TOPY, (10060, 10980)),
           ('R3', TOPY, (11000, 11999)),
           ('M',  MILY, (3500, 4560)), ('I',  MILY, (4570, 5150)),
           ('L',  MILY, (5200, 5950)), ('A',  MILY, (5990, 6780)),
           ('N2', MILY, (6800, 7680)), ('Om', MILY, (7700, 8640))]

def contours_of(mask, min_len=40):
    out = []
    mp = np.pad(mask, 3, constant_values=False)
    for c in measure.find_contours(mp.astype(float), 0.5):
        p = c[:, ::-1] - 3
        if np.allclose(p[0], p[-1]): p = p[:-1]
        if len(p) >= min_len: out.append(p)
    return out

def trace(p):
    return vl.fit_contour(p, line_tol=1.6, curve_tol=1.0, smooth_deg=32.0)

def despeck(mask, area):
    lab, n = ndi.label(mask, np.ones((3, 3)))
    sz = ndi.sum(mask, lab, range(1, n+1))
    return np.isin(lab, [i+1 for i, s in enumerate(sz) if s >= area]), int((sz < area).sum())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', help='PNG export of the reference artwork')
    ap.add_argument('--fix', nargs='*', default=[], help='letter keys to rebuild')
    ap.add_argument('--out', default='logo-final')
    ap.add_argument('--tol', type=float, default=2.0)
    ap.add_argument('--scale', type=float, default=6.0, help='source px per output point')
    ap.add_argument('--page', type=float, default=2000.0)
    a = ap.parse_args()

    ink = np.array(Image.open(a.source).convert('L')) < 128
    ink, dropped = despeck(ink, SPECK)
    print('specks dropped: %d' % dropped)

    out = []
    for nm, (y0, y1), (x0, x1) in LETTERS:
        box = ink[y0:y1, x0:x1]
        if not box.any():
            print('%-3s EMPTY box' % nm); continue
        ys, xs = np.where(box)
        oy, ox = ys.min(), xs.min()
        sub = box[ys.min():ys.max()+1, xs.min():xs.max()+1]
        if nm in a.fix:
            k = FIT_CAP/sub.shape[0]
            small = np.array(Image.fromarray(sub.astype(np.uint8)*255).resize(
                (max(1, int(round(sub.shape[1]*k))), int(FIT_CAP)), Image.LANCZOS)) > 127
            small, _ = despeck(small, 60)
            got = []
            for p in contours_of(small):
                if max(np.ptp(p[:, 0]), np.ptp(p[:, 1])) < SMALL_PART*small.shape[0]:
                    got.append(trace(p)); continue
                r = RC.rebuild(p, tol=a.tol, merge_tol=a.tol)
                got.append(r if r else (tuple(p[0]), [('L', tuple(q)) for q in p[1:]]))
            put = lambda q: (q[0]/k + ox + x0, q[1]/k + oy + y0)
        else:
            got = [trace(p) for p in contours_of(sub)]
            put = lambda q: (q[0] + ox + x0, q[1] + oy + y0)
        for start, segs in got:
            out.append((put(start), [(s[0],) + tuple(put(q) for q in s[1:]) for s in segs]))
        print('%-3s %-5s %d contours' % (nm, 'REBUILT' if nm in a.fix else 'kept', len(got)))

    S, P = a.scale, a.page
    pt = lambda q: (q[0]/S, P - q[1]/S)
    ops, d = [], []
    for start, segs in out:
        x, y = pt(start); ops.append('%.4f %.4f m' % (x, y)); d.append('M%.4f %.4f' % (x, P-y))
        for s in segs:
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
    print('wrote %s.pdf and %s.svg (%d contours, %.0f x %.0f pt)' % (a.out, a.out, len(out), P, P))

if __name__ == '__main__':
    main()
