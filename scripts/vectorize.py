#!/usr/bin/env python3
"""Vectorize a PDF page or image to PDF, faithfully, with VTracer.

Shapes are traced as drawn — no smoothing, no node reduction, no
regularising. The one piece of preprocessing is a palette snap: the flat
fills are sampled from inside flat regions only, and every antialiased edge
pixel is handed to the fill it actually divides. Without that the edge ramps
trace as thousands of sliver contours of their own.
"""
import argparse, os, re, sys, tempfile, time
import numpy as np, pymupdf, vtracer
from scipy import ndimage as ndi
from PIL import Image


def render(src, dpi, pageno):
    """(HxWx3 int32, page width pt, page height pt)"""
    if src.lower().endswith('.pdf'):
        page = pymupdf.open(src)[pageno]
        pm = page.get_pixmap(dpi=dpi, alpha=False)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
        return a.astype(np.int32), page.rect.width, page.rect.height
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.int32)
    return a, a.shape[1] * 72 / dpi, a.shape[0] * 72 / dpi


def flat_mask(img, r=1):
    """Pixels whose whole neighbourhood is one constant colour."""
    k = 2 * r + 1
    lo = ndi.minimum_filter(img, size=(k, k, 1))
    hi = ndi.maximum_filter(img, size=(k, k, 1))
    return (hi - lo).max(-1) == 0


def palette(img, fm, frac, merge):
    """The flat fills, largest area first, near-duplicates folded together.

    JPEG blocking splits one flat fill into several colours a few levels
    apart; folded together they stay one fill instead of becoming layers
    whose shared boundary is pure noise.
    """
    flat = img[fm]
    q = (flat // 4).astype(np.int64)
    ks, cnt = np.unique((q[:, 0] << 16) | (q[:, 1] << 8) | q[:, 2], return_counts=True)
    keep = []
    for i in np.argsort(-cnt):
        if cnt[i] < frac * len(flat):
            break
        k = ks[i]
        c = np.array([(k >> 16) & 255, (k >> 8) & 255, k & 255]) * 4 + 2
        if all(np.sqrt(((c - np.array(p)) ** 2).sum()) >= merge for p in keep):
            keep.append(tuple(int(v) for v in c))
    return keep


def snap(img, cols, fm, win):
    """Quantize to the flat palette, then clean the edges by majority vote.

    Matching every pixel on colour alone speckles the layers: an antialiased
    pixel is a blend of the two fills it divides, so it lands on whatever
    third fill happens to sit nearest in RGB — a grey between black and white,
    and so on. A majority filter settles each edge pixel on one of the fills
    actually around it. Handing it instead to the nearest *flat* pixel also
    works, but erases any feature thinner than the flatness window — it ate
    the hairline ring around one of the badges.
    """
    c = np.array(cols, np.int32)
    lab = ((img[:, :, None, :] - c[None, None, :, :]) ** 2).sum(-1).argmin(-1).astype(np.int16)
    if win >= 3:
        best = np.zeros(img.shape[:2], np.float32)
        out = np.zeros(img.shape[:2], np.int16)
        for i in range(len(cols)):
            v = ndi.uniform_filter((lab == i).astype(np.float32), size=win)
            np.copyto(out, np.int16(i), where=v > best)
            np.maximum(best, v, out=best)
        lab = out
    px = c[lab].astype(np.uint8)
    # each fill keeps the artwork's own colour, not a quantizer's midpoint
    for i in range(len(cols)):
        m = lab == i
        if (m & fm).any():
            px[m] = np.round(img[m & fm].mean(0)).astype(np.uint8)
    return px


NUM = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')


def paths_of(svg):
    """[(rgb, [[(cmd, pts), ...] subpath, ...]), ...] from a VTracer SVG.

    VTracer writes d before fill and gives each path its own
    transform="translate(x,y)", which the points are relative to.
    """
    pat = re.compile(r'<path\s+d="([^"]+)"\s+fill="#([0-9a-fA-F]{6})"'
                     r'(?:\s+transform="translate\(([^)]*)\)")?')
    out = []
    for m in pat.finditer(svg):
        rgb = tuple(int(m.group(2)[i:i+2], 16) for i in (0, 2, 4))
        tx, ty = 0.0, 0.0
        if m.group(3):
            v = [float(x) for x in NUM.findall(m.group(3))]
            if len(v) >= 2:
                tx, ty = v[0], v[1]
        subs, cur = [], None
        for tok in re.finditer(r'([MLCZmlcz])([^MLCZmlcz]*)', m.group(1)):
            op = tok.group(1)
            nums = [float(v) for v in NUM.findall(tok.group(2))]
            pts = [(x + tx, y + ty) for x, y in zip(nums[0::2], nums[1::2])]
            if op in 'Mm':
                if not pts:
                    continue
                cur = [('M', pts[0])]
                subs.append(cur)
                cur += [('L', q) for q in pts[1:]]
            elif cur is None:
                continue
            elif op in 'Ll':
                cur += [('L', q) for q in pts]
            elif op in 'Cc':
                for i in range(0, len(pts) - 2, 3):
                    cur.append(('C', pts[i:i+3]))
            else:
                cur.append(('Z', None))
        if subs:
            out.append((rgb, subs))
    return out


def write_pdf(paths, px_w, px_h, w_pt, h_pt, out):
    doc = pymupdf.open()
    page = doc.new_page(width=w_pt, height=h_pt)
    sx, sy = w_pt / px_w, h_pt / px_h
    P = lambda p: pymupdf.Point(p[0] * sx, p[1] * sy)
    n = 0
    for rgb, subs in paths:
        sh = page.new_shape()
        for sp in subs:
            start = cur = None
            for op, p in sp:
                if op == 'M':
                    start = cur = P(p)
                elif op == 'L':
                    sh.draw_line(cur, P(p)); cur = P(p); n += 1
                elif op == 'C':
                    e = P(p[2]); sh.draw_bezier(cur, P(p[0]), P(p[1]), e); cur = e; n += 1
                elif start is not None and cur != start:
                    sh.draw_line(cur, start); cur = start
        sh.finish(color=None, fill=[v / 255 for v in rgb], even_odd=True,
                  closePath=True, width=0)
        sh.commit()
    doc.save(out, garbage=4, deflate=True)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_pdf')
    ap.add_argument('--dpi', type=int, default=400)
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--min-area', type=float, default=0.0004,
                    help='flat-area fraction for a colour to count as a fill')
    ap.add_argument('--merge', type=float, default=26.0, help='fold fills closer than this in RGB')
    ap.add_argument('--clean', type=int, default=3,
                    help='majority-filter window for edge pixels; 0 = off')
    ap.add_argument('--speckle', type=int, default=16, help='drop blobs below N px')
    ap.add_argument('--corner', type=int, default=60, help='corner threshold, degrees')
    ap.add_argument('--splice', type=int, default=45)
    ap.add_argument('--length', type=float, default=4.0)
    ap.add_argument('--no-snap', action='store_true', help='trace the raw render')
    a = ap.parse_args()

    t0 = time.time()
    img, w_pt, h_pt = render(a.src, a.dpi, a.page)
    ph, pw = img.shape[:2]
    print(f'{pw} x {ph} px  ->  {w_pt:.1f} x {h_pt:.1f} pt  [{time.time()-t0:.1f}s]',
          file=sys.stderr)

    if a.no_snap:
        flat = img.astype(np.uint8)
    else:
        t = time.time()
        fm = flat_mask(img)
        cols = palette(img, fm, a.min_area, a.merge)
        flat = snap(img, cols, fm, a.clean)
        print(f'{100*fm.mean():.1f}% flat, {len(cols)} fills  [{time.time()-t:.1f}s]',
              file=sys.stderr)

    d = tempfile.mkdtemp()
    png, svg = os.path.join(d, 'in.png'), os.path.join(d, 'out.svg')
    Image.fromarray(flat).save(png)
    t = time.time()
    vtracer.convert_image_to_svg_py(
        png, svg, colormode='color', hierarchical='stacked', mode='spline',
        filter_speckle=a.speckle, color_precision=8, layer_difference=0,
        corner_threshold=a.corner, length_threshold=a.length,
        max_iterations=10, splice_threshold=a.splice, path_precision=4)
    print(f'vtracer  [{time.time()-t:.1f}s]', file=sys.stderr)

    paths = paths_of(open(svg).read())
    n = write_pdf(paths, pw, ph, w_pt, h_pt, a.out_pdf)
    print(f'wrote {a.out_pdf}: {len(paths)} paths, {n} segments, '
          f'{os.path.getsize(a.out_pdf)/1e6:.2f} MB  [total {time.time()-t0:.1f}s]',
          file=sys.stderr)


if __name__ == '__main__':
    main()
