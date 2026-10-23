#!/usr/bin/env python3
"""Redraw a Canva jacket layout with vector patches, positions untouched.

Canva writes each patch as a raster clipped to a frame, so the file says
exactly where every patch sits and how big it is -- the clip rectangle. The
placements overlap, but that never needed untangling: each one is a separate
draw, so the patch behind is simply drawn first and the one in front after,
which is what the page already does.

For each placement the clip is intersected with the raster, which gives a
clean picture of that one patch, free of its neighbours. That picture is
matched against the badges already vectorized, and the vector is laid into
the same rectangle. Photographs (the garment itself) are copied across
unchanged -- there is nothing in a photograph to vectorize.
"""
import argparse, glob, io, os, re, sys
import numpy as np, pymupdf
from PIL import Image

NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


# ---------------------------------------------------------------- content

def mul(a, b):
    return (a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3],
            a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3],
            a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5])


def ap(m, x, y):
    return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])


def through(m, r):
    p = [ap(m, r[0], r[1]), ap(m, r[2], r[1]), ap(m, r[2], r[3]), ap(m, r[0], r[3])]
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    return (min(xs), min(ys), max(xs), max(ys))


def isect(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def resources(doc, xref):
    out = {}
    ks = doc.xref_get_key(xref, 'Resources/XObject')
    if not ks or ks[0] == 'null':
        return out
    txt = ks[1]
    if ks[0] == 'xref':
        txt = doc.xref_object(int(txt.split()[0]))
    for name, ref in re.findall(r'/([A-Za-z0-9#_.\-]+)\s+(\d+)\s+0\s+R', txt):
        ref = int(ref)
        st = doc.xref_get_key(ref, 'Subtype')
        if st and st[1] == '/Form':
            m = doc.xref_get_key(ref, 'Matrix')
            mtx = tuple(float(v) for v in NUM.findall(m[1])) if m and m[0] != 'null' \
                else (1, 0, 0, 1, 0, 0)
            b = doc.xref_get_key(ref, 'BBox')
            bb = None
            if b and b[0] != 'null':
                v = [float(x) for x in NUM.findall(b[1])]
                bb = (min(v[0], v[2]), min(v[1], v[3]), max(v[0], v[2]), max(v[1], v[3]))
            out[name] = ('Form', ref, mtx, bb, resources(doc, ref))
        else:
            out[name] = ('Image', ref, None, None, None)
    return out


def walk(doc, stream, xo, ctm, clip, out):
    toks = stream.replace('\r', '\n').split()
    stack, pend = [], None
    for i, t in enumerate(toks):
        if t == 'q':
            stack.append((ctm, clip))
        elif t == 'Q':
            if stack:
                ctm, clip = stack.pop()
        elif t == 'cm':
            ctm = mul(tuple(float(x) for x in toks[i-6:i]), ctm)
        elif t == 're':
            v = [float(x) for x in toks[i-4:i]]
            pend = (v[0], v[1], v[0] + v[2], v[1] + v[3])
        elif t in ('W', 'W*'):
            if pend is not None:
                clip = isect(clip, through(ctm, pend))
        elif t == 'Do':
            e = xo.get(toks[i-1].lstrip('/'))
            if not e:
                continue
            if e[0] == 'Form':
                c2 = mul(e[2], ctm)
                c3 = isect(clip, through(c2, e[3])) if e[3] else clip
                walk(doc, doc.xref_stream(e[1]).decode('latin-1'), e[4], c2, c3, out)
            else:
                out.append((e[1], ctm, clip))


def placements(path):
    doc = pymupdf.open(path)
    page = doc[0]
    out = []
    walk(doc, page.read_contents().decode('latin-1'),
         resources(doc, page.xref), (1, 0, 0, -1, 0, page.rect.height), None, out)
    return doc, page, out


# ------------------------------------------------------------------ pixels

def raster(doc, xref, cache):
    """The image with its soft mask applied, as RGBA."""
    if xref in cache:
        return cache[xref]
    inf = doc.extract_image(xref)
    im = Image.open(io.BytesIO(inf['image'])).convert('RGB')
    sm = inf.get('smask', 0)
    a = Image.open(io.BytesIO(doc.extract_image(sm)['image'])).convert('L').resize(im.size) \
        if sm else Image.new('L', im.size, 255)
    im = im.convert('RGBA'); im.putalpha(a)
    cache[xref] = im
    return im


def cut(doc, xref, ctm, clip, cache):
    """The one patch a placement shows, and where its ink sits on the page."""
    im = raster(doc, xref, cache)
    W, H = im.size
    u0, v0 = (clip[0] - ctm[4]) / ctm[0], (clip[1] - ctm[5]) / ctm[3]
    u1, v1 = (clip[2] - ctm[4]) / ctm[0], (clip[3] - ctm[5]) / ctm[3]
    us, vs = sorted((u0, u1)), sorted((v0, v1))
    x0, x1 = int(round(us[0] * W)), int(round(us[1] * W))
    y0, y1 = int(round((1 - vs[1]) * H)), int(round((1 - vs[0]) * H))
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    crop = im.crop((x0, y0, x1, y1))
    ink = np.asarray(crop)[..., 3] > 128
    if not ink.any():
        return None, None
    ys, xs = np.nonzero(ink)
    # the ink's own box, back in page points
    def px(x, y):
        return ap(ctm, (x0 + x) / W, 1 - (y0 + y) / H)
    a = px(xs.min(), ys.min()); b = px(xs.max() + 1, ys.max() + 1)
    box = pymupdf.Rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
    return crop, box


def fit(im, S=56):
    a = np.asarray(im.convert('RGBA'))
    m = a[..., 3] > 128
    ys, xs = np.nonzero(m)
    a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    t = Image.fromarray(a)
    bg = Image.new('RGBA', t.size, (255, 255, 255, 255)); bg.alpha_composite(t)
    return np.asarray(bg.convert('RGB').resize((S, S), Image.BILINEAR), float)


def library(dirs):
    lib = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, 'badge-*.pdf'))):
            doc = pymupdf.open(f)
            pm = doc[0].get_pixmap(dpi=100, alpha=True)
            im = Image.open(io.BytesIO(pm.tobytes('png')))
            a = np.asarray(im.convert('RGBA'))
            ys, xs = np.nonzero(a[..., 3] > 16)
            ink = pymupdf.Rect(xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) \
                * (doc[0].rect.width / pm.width)
            lib.append((f, fit(im), doc, ink))
    return lib


def lay(page, doc, src, ink, box):
    """Put the badge down so its ink lands exactly on `box`."""
    r = src[0].rect
    sx, sy = box.width / ink.width, box.height / ink.height
    page.show_pdf_page(
        pymupdf.Rect(box.x0 - ink.x0 * sx, box.y0 - ink.y0 * sy,
                     box.x0 + (r.width - ink.x0) * sx,
                     box.y0 + (r.height - ink.y0) * sy), src, 0)


# -------------------------------------------------------------------- main

def build(path, out, lib, photo_pt, force, keep_photos=True):
    doc, page, pls = placements(path)
    cache = {}
    pg = out.new_page(width=page.rect.width, height=page.rect.height)
    n = 0
    for k, (xref, ctm, clip) in enumerate(pls):
        if clip is None:
            continue
        w = clip[2] - clip[0]
        if w > photo_pt:                       # the garment photograph
            if keep_photos:
                r = pymupdf.Rect(*clip)
                pg.insert_image(r, pixmap=pymupdf.Pixmap(doc, xref), keep_proportion=False)
            continue
        crop, box = cut(doc, xref, ctm, clip, cache)
        if crop is None:
            continue
        q = fit(crop)
        f = force.get(n)
        if f:
            hit = next(x for x in lib if x[0].endswith(f))
        else:
            hit = min(lib, key=lambda x: float(np.abs(q - x[1]).mean()))
        lay(pg, doc, hit[2], hit[3], box)
        print(f'  patch {n+1:2d}  {box.width:5.1f} x {box.height:5.1f} pt  '
              f'{os.sep.join(hit[0].split(os.sep)[-2:])}', file=sys.stderr)
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='+')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--lib', nargs='+', default=['assets/badges-17', 'assets/badges-17d',
                                                 'assets/badges-19'])
    ap.add_argument('--photo-pt', type=float, default=100.0,
                    help='a placement wider than this is a photograph, not a patch')
    ap.add_argument('--no-photos', action='store_true',
                    help='leave the garment out and keep only the patches')
    ap.add_argument('--force', default='',
                    help='n=file,... to override a match the pixels get wrong')
    a = ap.parse_args()

    force = {}
    for part in filter(None, a.force.split(',')):
        k, v = part.split('=')
        force[int(k)] = v

    lib = library(a.lib)
    print(f'{len(lib)} vectorized badges to choose from', file=sys.stderr)
    out = pymupdf.open()
    for s in a.src:
        print(os.path.basename(s), file=sys.stderr)
        n = build(s, out, lib, a.photo_pt, force, not a.no_photos)
        print(f'  {n} patches', file=sys.stderr)
    out.save(a.out, garbage=4, deflate=True)
    print('->', a.out, f'{len(out)} page(s)', file=sys.stderr)


if __name__ == '__main__':
    main()
