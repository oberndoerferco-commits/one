#!/usr/bin/env python3
"""Trace cast-metal capitals from a photograph into a font and vector artwork.

The source is a photograph of two gold letters on black velvet.  Separating
them does not need a luminance threshold - that would cut off the letters' own
dark sides, which are as dark as the cloth.  The velvet is neutral, so its
chroma (max minus min of RGB) is essentially zero, while cast gold holds 20-120
even in shadow.  Thresholding chroma gives exactly two components, stable
anywhere from 18 to 40, with no holes and no spill.

The outline then comes from the chroma image's own anti-aliased edge rather
than from the binary mask, so edge positions are sub-pixel; the interior and
exterior are forced solid a few pixels either side so the hammered texture
inside the metal cannot raise a contour of its own.

The O is symmetrised about both axes.  It is drawn with a vertical stress and
measures symmetric to within 1-2 px in the photograph, so the residual is
camera, not design.  The M is left alone: its V is deliberately thick on the
left stroke and thin on the right, and mirroring it would destroy that.
"""

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_lineart as vl

UPM = 1000
CAP = 700


# ------------------------------------------------------------------ the image


def letter_fields(path, chroma_t=25, open_iter=2, edge=3):
    """Return {name: (ink field, bbox)} for the two letters, ink dark."""
    rgb = np.asarray(Image.open(path).convert('RGB')).astype(np.float64)
    chroma = rgb.max(2) - rgb.min(2)
    mask = ndi.binary_opening(chroma > chroma_t, np.ones((3, 3)), iterations=open_iter)
    lbl, n = ndi.label(mask)
    sizes = ndi.sum(mask, lbl, range(1, n + 1))
    if n < 2:
        raise SystemExit('expected two letters, found %d components' % n)
    big = np.argsort(sizes)[::-1][:2]

    soft = np.clip((chroma - chroma_t * 0.45) / (chroma_t * 1.6), 0.0, 1.0)
    out = {}
    for i in big:
        comp = lbl == i + 1
        # The bevel's shadow dips in chroma in a few places and pits the mask.
        # Fill every hole but the ones big enough to be a real counter.
        filled = ndi.binary_fill_holes(comp)
        hl, hn = ndi.label(filled & ~comp)
        for k in range(1, hn + 1):
            h = hl == k
            if h.sum() < 0.02 * comp.sum():
                comp = comp | h
        ys, xs = np.nonzero(comp)
        name = 'O' if xs.mean() < rgb.shape[1] / 2 else 'M'
        inside = ndi.binary_erosion(comp, iterations=edge)
        outside = ~ndi.binary_dilation(comp, iterations=edge)
        f = np.where(inside, 1.0, np.where(outside, 0.0, soft))
        pad = 12
        y0, y1 = max(0, ys.min() - pad), min(f.shape[0], ys.max() + pad + 1)
        x0, x1 = max(0, xs.min() - pad), min(f.shape[1], xs.max() + pad + 1)
        out[name] = (1.0 - f[y0:y1, x0:x1], (x0, y0),
                     (xs.min() - x0, ys.min() - y0, xs.max() - x0, ys.max() - y0))
    return out


def symmetrise(ink, axis_x=None, axis_y=None):
    """Average the field with its mirror about a sub-pixel axis."""
    yy, xx = np.mgrid[0:ink.shape[0], 0:ink.shape[1]].astype(np.float64)
    out = ink
    for axis, coord in (('x', axis_x), ('y', axis_y)):
        if coord is None:
            continue
        sx = (2 * coord - xx) if axis == 'x' else xx
        sy = (2 * coord - yy) if axis == 'y' else yy
        mir = ndi.map_coordinates(out, [sy, sx], order=3, mode='nearest')
        print('      %s-mirror residual: mean %.3f px-equivalent, max %.3f'
              % (axis, float(np.abs(out - mir).mean()), float(np.abs(out - mir).max())))
        out = 0.5 * (out + mir)
    return out


def centroid(ink):
    w = 1.0 - ink
    tot = w.sum()
    yy, xx = np.mgrid[0:ink.shape[0], 0:ink.shape[1]]
    return float((w * xx).sum() / tot), float((w * yy).sum() / tot)


# ----------------------------------------------------------------- the outline


def contours_of(ink, sigma=1.8, **fit):
    """Trace one letter; returns contours in the crop's pixel coordinates.

    These letters are cast and hammered, so the silhouette carries about two
    pixels of physical irregularity at this scale.  A font wants deliberate
    curves, so the tolerances are set to absorb that wobble rather than trace
    it - while the corner-preserving fit keeps what is real, including the
    angular vertex on each of the O's flanks, which the casting genuinely has.
    """
    return vl.trace(ink, level=0.5, sigma=sigma, dot_area=0, min_area=40,
                    min_contour_area=30.0, **fit)


def _pts(contour):
    start, segs = contour
    return np.array([start] + [s[1] if s[0] == 'L' else s[3] for s in segs])


def signed_area(contour):
    p = _pts(contour)
    x, y = p[:, 0], p[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0


def reverse(contour):
    """Reverse a contour's direction, keeping it a closed path."""
    start, segs = contour
    anchors = [start] + [s[1] if s[0] == 'L' else s[3] for s in segs]
    out = []
    for k in range(len(segs) - 1, -1, -1):
        s = segs[k]
        out.append(('L', anchors[k]) if s[0] == 'L'
                   else ('C', s[2], s[1], anchors[k]))
    return anchors[-1], out


def transform(contour, fn):
    start, segs = contour
    return fn(start), [(s[0], fn(s[1])) if s[0] == 'L'
                       else ('C', fn(s[1]), fn(s[2]), fn(s[3])) for s in segs]


# -------------------------------------------------------------------- the font


def orient_for_cff(contours):
    """CFF fills non-zero with outer contours counter-clockwise."""
    ordered = sorted(contours, key=lambda c: -abs(signed_area(c)))
    out = []
    for i, c in enumerate(ordered):
        want_ccw = (i == 0)
        is_ccw = signed_area(c) > 0
        out.append(c if is_ccw == want_ccw else reverse(c))
    return out


def draw(pen, contours):
    for start, segs in contours:
        pen.moveTo(tuple(start))
        for s in segs:
            if s[0] == 'L':
                pen.lineTo(tuple(s[1]))
            else:
                pen.curveTo(tuple(s[1]), tuple(s[2]), tuple(s[3]))
        pen.closePath()


def build_otf(glyphs, widths, path, family, style='Regular', version='1.000'):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.t2CharStringPen import T2CharStringPen

    ps = family.replace(' ', '') + '-' + style
    order = ['.notdef', 'space', 'O', 'M']
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({0x20: 'space', 0x4F: 'O', 0x4D: 'M'})
    cs, metrics = {}, {}
    for name in order:
        adv = widths.get(name, 400)
        pen = T2CharStringPen(adv, None)
        if name in glyphs:
            draw(pen, glyphs[name])
        cs[name] = pen.getCharString()
        xs = [p[0] for c in glyphs.get(name, []) for p in _pts(c)]
        metrics[name] = (adv, int(round(min(xs))) if xs else 0)
    fb.setupCFF(ps, {'FullName': family + ' ' + style, 'FamilyName': family,
                     'Weight': style}, cs, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=int(CAP * 1.07), descent=-int(UPM * 0.25),
                             lineGap=0)
    fb.setupNameTable({
        'familyName': family, 'styleName': style,
        'uniqueFontIdentifier': '%s %s; %s' % (family, version, ps),
        'fullName': family + ' ' + style, 'psName': ps, 'version': 'Version ' + version,
        'description': 'Traced from a photograph of cast metal capitals.',
    })
    fb.setupOS2(sTypoAscender=int(CAP * 1.07), sTypoDescender=-int(UPM * 0.25),
                sTypoLineGap=0, usWinAscent=int(CAP * 1.12), usWinDescent=int(UPM * 0.25),
                sCapHeight=CAP, sxHeight=int(CAP * 0.72), fsType=0,
                panose=dict(bFamilyType=2, bSerifStyle=6, bWeight=9, bProportion=4,
                            bContrast=8, bStrokeVariation=0, bArmStyle=0,
                            bLetterForm=0, bMidline=0, bXHeight=0))
    fb.setupPost(isFixedPitch=0, underlinePosition=-int(UPM * 0.1),
                 underlineThickness=int(UPM * 0.07))
    fb.save(path)
    # web build: same outlines, compressed, for use in a theme's @font-face
    try:
        from fontTools.ttLib import TTFont
        web = TTFont(path)
        web.flavor = 'woff2'
        web.save(path[:-4] + '.woff2')
    except ImportError:
        print('   (woff2 skipped: brotli not installed)')
    return path


# -------------------------------------------------------------------- the main


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--family', default='Oberndorfer OM')
    ap.add_argument('--chroma', type=float, default=25.0)
    ap.add_argument('--size', type=float, default=480.0,
                    help='cap height in points for the artwork')
    ap.add_argument('--sigma', type=float, default=1.8)
    ap.add_argument('--line-tol', type=float, default=1.3)
    ap.add_argument('--curve-tol', type=float, default=0.85)
    ap.add_argument('--smooth-deg', type=float, default=34.0)
    ap.add_argument('--min-smooth-run', type=int, default=3)
    ap.add_argument('--no-symmetry', action='store_true')
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    fit = dict(sigma=a.sigma, line_tol=a.line_tol, curve_tol=a.curve_tol,
               smooth_deg=a.smooth_deg, min_smooth_run=a.min_smooth_run)

    fields = letter_fields(a.image, a.chroma)
    traced, boxes = {}, {}
    for name in ('M', 'O'):
        ink, origin, bbox = fields[name]
        if name == 'O' and not a.no_symmetry:
            cx, cy = centroid(ink)
            print('   O: symmetrising about (%.2f, %.2f)' % (cx, cy))
            ink = symmetrise(ink, cx, cy)
        cs = contours_of(ink, **fit)
        traced[name] = cs
        pts = np.vstack([_pts(c) for c in cs])
        boxes[name] = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
        print('   %s: %d contour(s), %d lines + %d curves, bbox %.1f x %.1f px'
              % (name, len(cs),
                 sum(1 for c in cs for q in c[1] if q[0] == 'L'),
                 sum(1 for c in cs for q in c[1] if q[0] == 'C'),
                 boxes[name][2] - boxes[name][0], boxes[name][3] - boxes[name][1]))

    # M's flat top and foot set the cap height and the baseline; the O keeps the
    # overshoot it was cast with, centred on the same band.
    cap_px = boxes['M'][3] - boxes['M'][1]
    scale = CAP / cap_px
    side = int(round(20.5 * scale))          # half the letter gap in the photo
    print('   cap %.1f px -> %d units (scale %.4f), sidebearing %d units'
          % (cap_px, CAP, scale, side))

    glyphs, widths = {}, {'.notdef': 400, 'space': int(round(UPM * 0.30))}
    for name in ('O', 'M'):
        x0, y0, x1, y1 = boxes[name]
        base = boxes['M'][3] if name == 'M' else (y0 + y1) / 2 + CAP / 2 / scale
        fn = (lambda b, xx0: (lambda p: ((p[0] - xx0) * scale + side,
                                         (b - p[1]) * scale)))(base, x0)
        glyphs[name] = orient_for_cff([transform(c, fn) for c in traced[name]])
        widths[name] = int(round((x1 - x0) * scale)) + 2 * side

    font = build_otf(glyphs, widths, os.path.join(
        a.outdir, a.family.replace(' ', '') + '-Regular.otf'), a.family)
    for f in (font, font[:-4] + '.woff2'):
        if os.path.exists(f):
            print('   %-32s %6d bytes' % (os.path.basename(f), os.path.getsize(f)))
    print('   advance widths: O %d, M %d, space %d (UPM %d, cap %d)'
          % (widths['O'], widths['M'], widths['space'], UPM, CAP))

    # ---- vector artwork, at the requested cap height
    k = a.size / CAP
    pad = 0.09 * a.size
    for nm, items in (('O', ['O']), ('M', ['M']), ('OM', ['O', 'M'])):
        placed, pen = [], 0.0
        for q in items:
            dx = pen - side
            placed += [transform(c, (lambda d: lambda p: ((p[0] + d) * k, p[1] * k))(dx))
                       for c in glyphs[q]]
            pen += widths[q]
        xs = [p[0] for c in placed for p in _pts(c)]
        ys = [p[1] for c in placed for p in _pts(c)]
        ox, oy = min(xs) - pad, min(ys) - pad
        w, h = (max(xs) - min(xs)) + 2 * pad, (max(ys) - min(ys)) + 2 * pad
        base = os.path.join(a.outdir, 'om-%s' % nm.lower())
        vl.write_pdf(base + '.pdf',
                     vl.emit(placed, lambda p: (p[0] - ox, p[1] - oy))[1], w, h)
        vl.write_svg(base + '.svg',
                     vl.emit(placed, lambda p: (p[0] - ox, h + oy - p[1]))[0], w, h)
        print('   om-%s.pdf / .svg  %.1f x %.1f pt' % (nm.lower(), w, h))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
