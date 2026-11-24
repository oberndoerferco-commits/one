"""Remove the floral decoration from Logo_2026-2 and write a clean vector logo.

Reads the artwork at 600 dpi, splits letters from vines (separate.split),
redraws the thin inner stems as solid bars (separate.thicken_stems), and
traces the result to a one-colour PDF and SVG at the original 1500 pt page.

If a reference file is given with --reference, the letters already cleaned by
hand in it are spliced in untouched (here: O, B and E), and the run reports how
closely the automatic result reproduces them.

  python3 clean_logo.py SOURCE.pdf --reference HAND_CLEANED.pdf --out DIR
"""
import argparse, sys
import numpy as np
from scipy import ndimage as ndi
import pymupdf as fitz
import separate as S

# numpy 2 dropped 2-D np.cross, which the repo's tracer uses
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

DPI = 600.0
PAD = 40                      # render px kept around the ink

def render(path, dpi=DPI):
    page = fitz.open(path)[0]
    pm = page.get_pixmap(dpi=int(dpi), colorspace=fitz.csGRAY)
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    return a < 128, page.rect.width, page.rect.height

def contours(mask, tol=1.1):
    out = []
    mp = np.pad(mask, 3, constant_values=False)
    for c in measure.find_contours(mp.astype(float), 0.5):
        p = c[:, ::-1] - 3
        if np.allclose(p[0], p[-1]): p = p[:-1]
        if len(p) < 10: continue
        if max(np.ptp(p[:, 0]), np.ptp(p[:, 1])) < 4: continue
        out.append(vl.fit_contour(p, line_tol=tol, curve_tol=tol*0.6, smooth_deg=32.0))
    return out

def emit(cs, x0, y0, w_pt, h_pt, out):
    s = 72.0/DPI
    def pt(p): return ((p[0]+x0)*s, h_pt-(p[1]+y0)*s)
    ops, d = [], []
    for start, segs in cs:
        x, y = pt(start); ops.append('%.3f %.3f m' % (x, y)); d.append('M%.3f %.3f' % (x, h_pt-y))
        for g in segs:
            if g[0] == 'L':
                x, y = pt(g[1]); ops.append('%.3f %.3f l' % (x, y)); d.append('L%.3f %.3f' % (x, h_pt-y))
            else:
                a, b, c = pt(g[1]), pt(g[2]), pt(g[3])
                ops.append('%.3f %.3f %.3f %.3f %.3f %.3f c' % (a[0], a[1], b[0], b[1], c[0], c[1]))
                d.append('C%.3f %.3f %.3f %.3f %.3f %.3f' % (a[0], h_pt-a[1], b[0], h_pt-b[1], c[0], h_pt-c[1]))
        ops.append('h'); d.append('Z')
    cs_b = ('0 g\n' + '\n'.join(ops) + '\nf*\n').encode()
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.0f %.0f] /Contents 4 0 R /Resources << >> >>' % (w_pt, h_pt)).encode(),
            ('<< /Length %d >>\nstream\n' % len(cs_b)).encode() + cs_b + b'endstream']
    buf = bytearray(b'%PDF-1.4\n'); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(buf)); buf += ('%d 0 obj\n' % i).encode() + o + b'\nendobj\n'
    x = len(buf)
    buf += ('xref\n0 %d\n' % (len(objs)+1)).encode() + b'0000000000 65535 f \n'
    for o in offs: buf += ('%010d 00000 n \n' % o).encode()
    buf += ('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs)+1, x)).encode()
    open(out+'.pdf', 'wb').write(bytes(buf))
    open(out+'.svg', 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
        '<path fill="#000000" fill-rule="evenodd" d="%s"/></svg>' % (w_pt, h_pt, w_pt, h_pt, ' '.join(d)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source'); ap.add_argument('--reference'); ap.add_argument('--out', default='logo-clean')
    ap.add_argument('--reference-box', nargs=4, type=int, default=[5300, 6500, 2000, 4300],
                    help='y0 y1 x0 x1 in 600 dpi page pixels, taken from the reference as-is')
    a = ap.parse_args()

    ink, w_pt, h_pt = render(a.source)
    ys, xs = np.where(ink)
    y0, y1 = ys.min()-PAD, ys.max()+PAD
    x0, x1 = xs.min()-PAD, xs.max()+PAD
    sub = ink[y0:y1, x0:x1]

    out, found = S.clean(sub, verbose=True)
    print('letters separated, %d inner stems thickened' % len(found))

    if a.reference:
        ref, _, _ = render(a.reference)
        by0, by1, bx0, bx1 = a.reference_box
        box = (slice(by0-y0, by1-y0), slice(bx0-x0, bx1-x0))
        hb = ref[by0:by1, bx0:bx1]
        lb, n = ndi.label(hb, structure=np.ones((3, 3)))
        sz = ndi.sum(hb, lb, range(1, n+1))
        hb = np.isin(lb, [i+1 for i, s in enumerate(sz) if s >= 2000])   # drop eraser specks
        mine = out[box]
        print('match with the hand-cleaned letters: %.1f%% of their union'
              % (100*(mine & hb).sum()/(mine | hb).sum()))
        out[box] = hb

    cs = contours(out)
    print('traced %d contours' % len(cs))
    emit(cs, x0, y0, w_pt, h_pt, a.out)
    print('wrote %s.pdf and %s.svg (%.0f x %.0f pt)' % (a.out, a.out, w_pt, h_pt))
    return out

if __name__ == '__main__':
    main()
