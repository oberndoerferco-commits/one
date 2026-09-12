#!/usr/bin/env python3
"""Vectorise flat-colour raster art (logos, tiles, badges) into stacked fills.

The input is assumed to be flat colour regions with anti-aliased edges, which
is what an exported logo or pattern tile looks like. Rather than tracing each
colour separately and hoping the seams line up, regions are painted as nested
filled shapes:

  * quantise to the image's own palette (entries within a small RGB distance
    are merged, so 254-white and 255-white do not become separate layers);
  * take connected regions per colour and fill their holes, so each region is
    simply connected and has exactly one outline;
  * paint them largest first. A hole in a region is, by construction, covered
    by regions nested inside it, which are smaller and so painted later.

That ordering means adjacent regions never leave a hairline gap: whatever sits
on top is drawn over a parent that already extends underneath it. A thin drawn
outline works out too - its filled extent is the whole enclosed shape, painted
first, with the fill painted over the middle and leaving the outline showing.

Outlines are fitted with the same corner-preserving line/curve fitter used for
line art, so straight edges stay straight and curves stay smooth.
"""

import argparse
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_lineart as VL


def palette_of(rgb, min_fraction=0.001, merge_dist=6):
    """The image's flat colours, most common first, near-duplicates merged."""
    flat = rgb.reshape(-1, 3).astype(np.uint8)
    cols, counts = np.unique(flat, axis=0, return_counts=True)
    order = np.argsort(counts)[::-1]
    out = []
    for k in order:
        if counts[k] / len(flat) < min_fraction:
            break
        c = cols[k].astype(np.float32)
        if not any(np.abs(c - m).max() <= merge_dist for m in out):
            out.append(c)
    return np.array(out, dtype=np.float32)


def quantise(rgb, pal, chunk=256):
    """Nearest-palette label per pixel, in row chunks to bound memory."""
    h, w, _ = rgb.shape
    lab = np.empty((h, w), np.uint8)
    for y in range(0, h, chunk):
        a = rgb[y:y + chunk].astype(np.float32)
        d = ((a[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(3)
        lab[y:y + chunk] = d.argmin(2).astype(np.uint8)
    return lab


def regions(lab, n_colours, min_area=64):
    """Connected regions as (filled_mask, colour_index, filled_area)."""
    out = []
    for c in range(n_colours):
        m = lab == c
        if not m.any():
            continue
        lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
        for k in range(1, n + 1):
            comp = lbl == k
            if comp.sum() < min_area:
                continue
            filled = ndimage.binary_fill_holes(comp)
            out.append((filled, c, int(filled.sum())))
    out.sort(key=lambda r: -r[2])
    return out


def outline(mask, sigma=0.8, **fit):
    """Sub-pixel outline of a filled mask, fitted to lines and curves."""
    from skimage import measure
    f = ndimage.gaussian_filter(mask.astype(np.float32), sigma)
    paths = []
    for con in measure.find_contours(f, 0.5):
        pts = con[:, ::-1].astype(np.float64) + 0.5
        if len(pts) > 1 and np.allclose(pts[0], pts[-1]):
            pts = pts[:-1]
        if len(pts) < 8:
            continue
        paths.append(VL.fit_contour(pts, **fit))
    return paths


def _fmt(v, prec=2):
    s = f"{v:.{prec}f}".rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def svg_path_data(paths, to_xy, prec=2):
    out = []
    f = lambda v: _fmt(v, prec)
    for start, segs in paths:
        sx, sy = to_xy(start)
        d = [f"M{f(sx)} {f(sy)}"]
        for s in segs:
            if s[0] == 'L':
                x, y = to_xy(s[1])
                d.append(f"L{f(x)} {f(y)}")
            else:
                a, b, c = to_xy(s[1]), to_xy(s[2]), to_xy(s[3])
                d.append(f"C{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])}")
        out.append(" ".join(d) + " Z")
    return " ".join(out)


def pdf_ops(paths, to_xy, prec=2):
    out = []
    f = lambda v: _fmt(v, prec)
    for start, segs in paths:
        sx, sy = to_xy(start)
        o = [f"{f(sx)} {f(sy)} m"]
        for s in segs:
            if s[0] == 'L':
                x, y = to_xy(s[1])
                o.append(f"{f(x)} {f(y)} l")
            else:
                o.append(" ".join(f(v) for p in (to_xy(s[1]), to_xy(s[2]), to_xy(s[3]))
                                   for v in p) + " c")
        out.append(" ".join(o) + " h")
    return out


def write_svg(path, layers, w, h):
    body = []
    for colour, paths in layers:
        d = svg_path_data(paths, lambda p: (p[0], p[1]))
        if d:
            body.append(f'<path fill="{colour}" fill-rule="evenodd" d="{d}"/>')
    with open(path, 'w') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                 f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
                 f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
                 + "\n".join(body) + "\n</svg>\n")


def write_pdf(path, layers, w, h, scale):
    body = []
    for rgb, paths in layers:
        r, g, b = [v / 255.0 for v in rgb]
        body.append(f"{_fmt(r,4)} {_fmt(g,4)} {_fmt(b,4)} rg")
        body.append("\n".join(pdf_ops(paths, lambda p: (p[0] * scale, (h / scale - p[1]) * scale))))
        body.append("f*")
    content = ("\n".join(body) + "\n").encode('latin-1')
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.4f} {h:.4f}] "
             f"/Contents 4 0 R /Resources << >> >>").encode(),
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"endstream"]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offs = []
    for i, b in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + b + b"\nendobj\n"
    x = len(out)
    out += f"xref\n0 {len(objs)+1}\n".encode() + b"0000000000 65535 f \n"
    for o in offs:
        out += f"{o:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\n"
            f"startxref\n{x}\n%%EOF\n").encode()
    open(path, 'wb').write(bytes(out))


def vectorise(src, out_svg=None, out_pdf=None, pdf_size=512.0, drop_background=True,
              min_area=64, **fit):
    from PIL import Image
    rgb = np.asarray(Image.open(src).convert('RGB'))
    h, w, _ = rgb.shape
    pal = palette_of(rgb)
    lab = quantise(rgb, pal)
    regs = regions(lab, len(pal), min_area)

    if drop_background:
        # the region that reaches the image border is the paper; leave it clear
        regs = [r for r in regs
                if not (r[0][0].any() or r[0][-1].any() or r[0][:, 0].any() or r[0][:, -1].any())]

    layers_svg, layers_pdf = [], []
    for mask, ci, _ in regs:
        paths = outline(mask, **fit)
        if not paths:
            continue
        c = pal[ci].astype(int)
        layers_svg.append(('#%02x%02x%02x' % tuple(c), paths))
        layers_pdf.append((tuple(c), paths))

    if out_svg:
        write_svg(out_svg, layers_svg, w, h)
    if out_pdf:
        write_pdf(out_pdf, layers_pdf, pdf_size, pdf_size, pdf_size / w)
    return dict(palette=[tuple(int(v) for v in c) for c in pal],
                regions=len(regs), layers=len(layers_svg),
                segments=sum(len(s) for _, ps in layers_svg for _, s in ps))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument('input')
    ap.add_argument('outdir')
    ap.add_argument('--name', default=None)
    ap.add_argument('--pdf-size', type=float, default=512.0,
                    help='PDF page size in points (default 512)')
    ap.add_argument('--line-tol', type=float, default=0.6)
    ap.add_argument('--curve-tol', type=float, default=0.4)
    a = ap.parse_args(argv)
    name = a.name or os.path.splitext(os.path.basename(a.input))[0]
    os.makedirs(a.outdir, exist_ok=True)
    info = vectorise(a.input,
                     os.path.join(a.outdir, name + '.svg'),
                     os.path.join(a.outdir, name + '.pdf'),
                     pdf_size=a.pdf_size,
                     line_tol=a.line_tol, curve_tol=a.curve_tol)
    print(f"{name}: palette {info['palette']}")
    print(f"   {info['layers']} filled regions, {info['segments']} segments")
    return info


if __name__ == '__main__':
    main()
