#!/usr/bin/env python3
"""Take the arched nameplate apart so the arch, the spacing and the frame
can be changed.

The artwork arrives as a flat picture: eleven letters already rotated onto
one particular arch, inside one particular frame. Nothing about it can be
adjusted, because the arch is baked into every letter. So this undoes it.

The plate's two keylines are circular to within a third of a pixel, which
is what makes the rest possible: fitting them gives the centre the whole
drawing was struck about, and every letter's rotation is then just its
own angle about that centre. Rotate each one back by its own angle and
the arch is gone, leaving upright letters, their widths, and the gaps
between them - which is a typesetting problem again, and can be re-struck
onto any arch at all.

Two things in the source are worth knowing about, and both are kept as
measured rather than quietly repaired:

  - The left dot of the umlaut touches the top keyline. It is not a
    separate shape in the picture at all; it hangs off the frame by a
    six pixel neck, which is why it has to be cut free here.
  - The band is not concentric. The top keyline's centre sits 71 px
    above the bottom one's, so the plate is 257 px deep at the middle
    and 263 at the ends. The viewer draws it concentric, which is a
    2 per cent change and the reason the ends sit a hair tighter.

Writes plate.json for the viewer and a proof SVG.

    python3 scripts/arch_plate.py <image> <outdir> [--text OBERNDORFER]
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import morphology

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vectorize_lineart import trace, emit            # noqa: E402

# Everything darker than this is ink. The plate itself sits at 230 and the
# letters run from 48 to 220, so the cut is well clear of both; between
# 185 and 215 the component count does not move.
INK = 210

# Inside a letter, anything brighter than this is the engraved highlight
# rather than the body of the stroke. 19 per cent of the letter area.
HILIGHT = 165


def fit_circle(x, y, iters=6):
    """Algebraic circle fit, outliers dropped as it goes.

    Needed because the top keyline carries the stray umlaut dot: with
    every column weighted the same, that one blob pulls the centre.
    """
    for _ in range(iters):
        a = np.column_stack([x, y, np.ones_like(x)])
        d, e, f = np.linalg.lstsq(a, -(x ** 2 + y ** 2), rcond=None)[0]
        cx, cy = -d / 2, -e / 2
        r = np.sqrt(cx * cx + cy * cy - f)
        res = np.hypot(x - cx, y - cy) - r
        keep = np.abs(res) < max(1.5, 3 * res.std())
        if keep.all():
            break
        x, y = x[keep], y[keep]
    return cx, cy, r, res


def keylines(mask, band):
    """The two arcs of the frame, from the top and bottom edge of its ink.

    Only the middle is used. The ends are rounded, so their topmost and
    bottommost pixels leave the arcs and would bend the fit.
    """
    h, w = mask.shape
    cols = np.arange(w)
    top = np.full(w, -1)
    bot = np.full(w, -1)
    for c in range(w):
        ys = np.where(band[:, c])[0]
        if len(ys):
            top[c], bot[c] = ys.min(), ys.max()
    x0, x1 = np.where(top >= 0)[0][[0, -1]]
    span = int(0.17 * (x1 - x0))
    mid = (top >= 0) & (cols > x0 + span) & (cols < x1 - span)
    ct = fit_circle(cols[mid].astype(float), top[mid].astype(float))
    cb = fit_circle(cols[mid].astype(float), bot[mid].astype(float))
    return (x0, x1), ct, cb


def free_the_dot(band, ct, cb, x0, x1, rad=5):
    """Cut the umlaut dot off the frame it is stuck to.

    The dot hangs below the top keyline on a neck six pixels wide, so it
    is not a shape of its own in the picture at all. An opening settles
    it: the keyline is eight pixels thick and does not survive a disc of
    radius five, while a dot thirty-eight across keeps a core of six
    hundred pixels. Dilating that core back and meeting the ink again
    returns the dot without the neck - two blobs left on the whole
    plate, and only one of them is round.
    """
    yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
    disc = (xx ** 2 + yy ** 2) <= rad * rad
    core = ndimage.binary_erosion(band, disc)
    lab, n = ndimage.label(core)
    out = np.zeros_like(band)
    for i in range(1, n + 1):
        blob = lab == i
        s = int(blob.sum())
        ys, xs = np.nonzero(blob)
        wd, ht = np.ptp(xs) + 1, np.ptp(ys) + 1
        if not (250 <= s <= 2000 and 0.55 < wd / ht < 1.8
                and s / (wd * ht) > 0.55):
            continue
        out |= ndimage.binary_dilation(blob, disc)
    return out & band


def split_at_neck(comp, lo, hi):
    """Cut a two-letter blob apart at its narrowest column."""
    cols = comp[:, lo:hi].sum(0)
    inner = cols[int(0.3 * len(cols)):int(0.7 * len(cols))]
    cut = lo + int(0.3 * len(cols)) + int(np.argmin(inner))
    left, right = comp.copy(), comp.copy()
    left[:, cut:] = False
    right[:, :cut] = False
    return left, right, cut, int(cols[cut - lo])


def components(mask, band, dots):
    """Every letter of the word, in reading order.

    The letters are what is left once the frame is taken away, plus the
    dot cut off it. Any blob that touches its neighbour is split at the
    narrowest column between them - in this drawing the D and the O
    overlap by three pixels.
    """
    letters = (mask & ~band) | dots
    letters = ndimage.binary_closing(letters, np.ones((3, 3)))
    lab, n = ndimage.label(letters)
    sz = np.bincount(lab.ravel())
    objs = ndimage.find_objects(lab)
    out = []
    for i in range(1, n + 1):
        if sz[i] < 150:
            continue
        ys, xs = objs[i - 1]
        out.append(dict(mask=(lab == i), x0=xs.start, x1=xs.stop,
                        y0=ys.start, y1=ys.stop, px=int(sz[i])))
    out.sort(key=lambda d: d['x0'])
    return out


def hatched(gray, body, thresh=9.0):
    """Which part of a letter the engraver ruled, and which he left blank.

    The one measurement in this picture that is not ambiguous. The
    hatching is a stripe pattern in y; removing the local mean over a
    five pixel column leaves the stripes and nothing else, and the energy
    in that residual reads 11.3 inside the letters against 0.3 on the
    plate. It says nothing about inside against outside - which is why it
    could not find the cast shadow - but it says exactly where the ruling
    is, and that is what the hatch has to be clipped to or the modelling
    is lost and every stroke reads flat.
    """
    hp = gray - ndimage.uniform_filter(gray, size=(5, 1))
    energy = ndimage.uniform_filter(np.abs(hp), size=(9, 9))
    m = body & (energy > thresh)
    m = ndimage.binary_closing(m, np.ones((5, 5)))
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    # The boundary between ruled and blank is soft in the picture, where
    # the hatching thins out rather than stopping, so the mask comes back
    # freckled with islands either way. Anything under a fiftieth of a
    # square millimetre is such a freckle and not a decision the engraver
    # made: it reads as dirt at any size.
    keep = max(60, int(0.05 / (10.74 / 154.9) ** 2))
    m = morphology.remove_small_objects(m, keep)
    m = morphology.remove_small_holes(m, keep)
    m = ndimage.binary_closing(m, np.ones((7, 7)))
    m = ndimage.binary_opening(m, np.ones((5, 5)))
    return m & body


def deshadow(mask, dx, dy):
    """The letter without the cast shadow fused to its lower right.

    The drawing shades every letter with a solid shadow pushed down and
    right, and at any ink cut that keeps the hatching the shadow comes
    with it - so the silhouette traced from this picture is the letter
    and its shadow welded into one blob, which is why it reads a size too
    heavy and cannot be given a shadow of its own.

    If the silhouette is the letter unioned with a copy of itself pushed
    by d, then intersecting it with itself pushed BACK by d leaves the
    letter: every point of the shadow that is not also letter loses its
    partner. It only works on the filled mask - the counters have to be
    closed first and punched back after, or the O's inside overlaps the
    shadow's and tears holes through the stroke, which is what four
    earlier attempts at this got wrong.

    Five other routes were tried and none held: local roughness (the
    shadow is smooth and so is the lit side), a tight ink cut and a fill
    (the shadow is inside the letter's own dark edge, so the fill takes
    it too), the stripe energy alone (it marks hatched against smooth,
    not inside against outside), the tone of the smooth regions (a flat
    continuum from 60 to 210 with no second mode), and estimating d by
    pushing the hatched region onto the smooth ink (it saturated at the
    edge of the search).
    """
    solid = ndimage.binary_fill_holes(mask)
    counters = solid & ~mask
    if not (dx or dy):
        return mask
    back = np.roll(np.roll(solid, -dy, 0), -dx, 1)
    body = ndimage.binary_opening(solid & back, np.ones((3, 3)))
    return body & ~np.roll(np.roll(counters, -dy, 0), -dx, 1)


def unroll(comp, centre, r_base):
    """Rotate one letter back off the arch.

    Its angle about the centre the plate was struck about is the angle it
    was turned by, so turning it back by the same amount stands it
    upright. The point on its own radius at the baseline radius becomes
    the origin, which is where a typesetter would put it.
    """
    cx, cy = centre
    ys, xs = np.nonzero(comp)
    vx, vy = xs.mean() + 0.5 - cx, -(ys.mean() + 0.5) - (-cy)
    th = np.arctan2(vx, vy)                      # from straight up, east +ve
    # The letter's radius has argument 90 - th, and wants to be 90, so the
    # turn is exp(i*th) and not its conjugate. Getting that backwards
    # turns each letter the wrong way and leaves it sitting at its own
    # arc distance from the middle instead of over the origin.
    rot = complex(np.cos(th), np.sin(th))        # y-up, anticlockwise

    def to_local(p):
        z = complex(p[0] - cx, -(p[1]) + cy) * rot
        return (z.real, -(z.imag - r_base))      # svg: y down, baseline at 0

    return th, to_local


def glyph(gray, comp, to_local, level, pad=4):
    """Trace one letter, already placed in its upright frame."""
    ys, xs = np.nonzero(comp)
    y0, y1 = max(0, ys.min() - pad), min(gray.shape[0], ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(gray.shape[1], xs.max() + 1 + pad)
    win = np.ones((y1 - y0, x1 - x0), np.float32)
    sub = comp[y0:y1, x0:x1]
    win[sub] = gray[y0:y1, x0:x1][sub] / 255.0
    cons = trace(np.minimum(win, 1.0), level=level, sigma=0.4,
                 line_tol=0.45, curve_tol=0.3)
    shift = lambda p: to_local((p[0] + x0, p[1] + y0))
    svg, _, _ = emit(cons, shift)
    return svg


def trace_mask(mask, to_local, pad=4, smooth=0.6):
    """Trace a mask that has no greyscale edge of its own to measure.

    `smooth` blurs the mask before the contour is taken, which rounds its
    boundary. For the ruled region that matters: the line where the
    hatching stops is drawn in the reference, and drawing a boundary
    measured off a soft edge makes every wobble in it louder rather than
    quieter. Two pixels of blur is about a seventh of a millimetre on the
    plate - enough to lose the wobble, not enough to lose a corner.
    """
    ys, xs = np.nonzero(mask)
    y0, y1 = max(0, ys.min() - pad), mask.shape[0]
    x0, x1 = max(0, xs.min() - pad), mask.shape[1]
    y1 = min(y1, ys.max() + 1 + pad)
    x1 = min(x1, xs.max() + 1 + pad)
    win = np.ones((y1 - y0, x1 - x0), np.float32)
    win[mask[y0:y1, x0:x1]] = 0.0
    cons = trace(ndimage.gaussian_filter(win, smooth), level=0.5, sigma=0.0,
                 line_tol=0.5, curve_tol=0.4)
    svg, _, _ = emit(cons, lambda p: to_local((p[0] + x0, p[1] + y0)))
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('outdir')
    ap.add_argument('--text', default='OBERNDORFER',
                    help='the letters, in order, one per shape found')
    ap.add_argument('--umlaut', type=int, default=6,
                    help='which letter carries the dots (0-based)')
    ap.add_argument('--ink', type=float, default=INK)
    ap.add_argument('--hilight', type=float, default=HILIGHT)
    ap.add_argument('--deshadow', default='11,18', metavar='DX,DY',
                    help='how far the cast shadow is pushed down and right '
                         'in source pixels, to be taken back off the '
                         'silhouette; 0,0 leaves it welded on')
    o = ap.parse_args()

    rgb = np.asarray(Image.open(o.image).convert('RGB')).astype(np.float32)
    gray = rgb.mean(2)
    mask = ndimage.binary_closing(gray < o.ink, np.ones((3, 3)))
    lab, _ = ndimage.label(mask)
    band = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)

    (x0, x1), ct, cb = keylines(mask, band)
    print(f'frame spans x {x0}..{x1} ({x1 - x0} px)')
    print(f'   top keyline    centre ({ct[0]:.1f}, {ct[1]:.1f})  radius '
          f'{ct[2]:.1f}  fit {np.abs(ct[3]).max():.2f} px worst')
    print(f'   bottom keyline centre ({cb[0]:.1f}, {cb[1]:.1f})  radius '
          f'{cb[2]:.1f}  fit {np.abs(cb[3]).max():.2f} px worst')

    dots = free_the_dot(band, ct, cb, x0, x1)
    print(f'   cut {int(dots.sum())} px of umlaut dot off the top keyline')

    comps = components(mask, band, dots)
    for c in comps:
        print(f'      blob x {c["x0"]:4d}-{c["x1"]:4d}  y {c["y0"]:4d}-'
              f'{c["y1"]:4d}  {c["px"]:6d} px')
    want = len(o.text) + 2                      # the two dots stand alone
    while len(comps) < want:
        big = max(comps, key=lambda d: d['x1'] - d['x0'])
        l, r, cut, ink = split_at_neck(big['mask'], big['x0'], big['x1'])
        print(f'   split a {big["x1"] - big["x0"]} px blob at x={cut}, '
              f'where only {ink} px of ink join the two')
        comps = [c for c in comps if c is not big]
        for part in (l, r):
            ys, xs = np.nonzero(part)
            comps.append(dict(mask=part, x0=xs.min(), x1=xs.max() + 1,
                              y0=ys.min(), y1=ys.max() + 1,
                              px=int(part.sum())))
        comps.sort(key=lambda d: d['x0'])

    # One centre for the whole drawing, and it has to be one: the two
    # keylines were struck about centres 71 px apart, so a radius quoted
    # about the average of them belongs to neither arc. The top keyline's
    # own centre is the choice - it is the best-conditioned of the fits,
    # a thousand columns of edge against eleven letter feet - and the
    # bottom keyline is then described as a radius about it, which varies
    # with angle by exactly as much as the drawing is out of true.
    centre = (ct[0], ct[1])
    cxx, cyy = centre
    bodies, marks = [], []
    for c in comps:
        ys, xs = np.nonzero(c['mask'])
        r = np.hypot(xs.mean() - cxx, ys.mean() - cyy)
        (marks if c['px'] < 4000 else bodies).append((r, c))
    bodies.sort(key=lambda t: t[1]['x0'])
    if len(bodies) != len(o.text):
        raise SystemExit(f'found {len(bodies)} letters for {len(o.text)} '
                         f'in {o.text!r}')
    for _, d in marks:
        host = bodies[o.umlaut][1]
        host['mask'] = host['mask'] | d['mask']
        host['x0'] = min(host['x0'], d['x0'])
        host['x1'] = max(host['x1'], d['x1'])
        host['y0'] = min(host['y0'], d['y0'])
    print(f'   {len(bodies)} letters, {len(marks)} loose marks joined to '
          f'{o.text[o.umlaut]}')

    # the baseline: the radius the flat-footed letters stand on. Round
    # letters dip below it, so the fit takes the letters that do not.
    yy, xx = np.mgrid[:gray.shape[0], :gray.shape[1]]
    rad = np.hypot(xx + 0.5 - cxx, yy + 0.5 - cyy)
    feet = np.array([rad[d['mask']].min() for _, d in bodies])
    head = np.array([rad[d['mask']].max() for _, d in bodies])
    flat = feet > np.median(feet) - 3
    r_base = float(feet[flat].mean())
    cap = float(np.median(head[flat]) - r_base)
    print(f'   baseline radius {r_base:.1f} px, cap height {cap:.1f} px '
          f'({(np.abs(feet - r_base).max()):.1f} px worst foot)')

    # the bottom keyline, as a radius about that one centre
    edge = np.zeros(gray.shape[1], float)
    for c in range(gray.shape[1]):
        ys = np.where(band[:, c])[0]
        edge[c] = rad[ys.max(), c] if len(ys) else np.nan
    span = int(0.17 * (x1 - x0))
    sel = slice(x0 + span, x1 - span)
    rb_mean = float(np.nanmean(edge[sel]))
    rb_dev = float(np.nanmax(edge[sel]) - np.nanmin(edge[sel]))
    print(f'   bottom keyline sits {rb_mean:.1f} px from that centre, '
          f'wandering {rb_dev:.1f} px - the plate is out of true by '
          f'{rb_dev / (ct[2] - rb_mean) * 100:.1f}%')

    # what the frame leaves round the letters, in the source
    tops = head.max()
    print(f'   frame: {ct[2] - (r_base + cap):.1f} px over the cap line, '
          f'{(r_base - feet.min()) + rb_mean - r_base:+.1f} px under the '
          f'feet; the umlaut overruns the top keyline by '
          f'{tops - ct[2]:.1f} px')

    sdx, sdy = (int(v) for v in o.deshadow.split(','))
    letters = []
    for ch, (_, d) in zip(o.text, bodies):
        th, to_local = unroll(d['mask'], centre, r_base)
        body = deshadow(d['mask'], sdx, sdy)
        if body.sum() < 0.3 * d['mask'].sum():
            raise SystemExit(f'de-shadowing {ch} left only '
                             f'{body.sum() / d["mask"].sum():.0%} of it')
        solid = glyph(gray, body, to_local, o.ink / 255.0)
        shade = hatched(gray, body)
        inlay = trace_mask(shade, to_local, smooth=2.0) \
            if shade.sum() > 200 else []
        ys, xs = np.nonzero(body)
        edge = [to_local((x, y)) for x, y in
                ((xs.min(), ys.mean()), (xs.max() + 1, ys.mean()))]
        letters.append(dict(ch=ch, angle=float(np.degrees(th)),
                            left=min(e[0] for e in edge),
                            right=max(e[0] for e in edge),
                            paths=solid, inlay=inlay))
        print(f'   {ch}  turned {np.degrees(th):+6.2f} deg   '
              f'{len(solid):2d} contours, {len(inlay):2d} ruled, '
              f'body {body.sum() / d["mask"].sum():.0%} of the silhouette, '
              f'{shade.sum() / max(body.sum(), 1):.0%} of it hatched')

    doc = dict(
        source=os.path.basename(o.image),
        px=dict(w=int(gray.shape[1]), h=int(gray.shape[0])),
        shadow=dict(dx=sdx, dy=sdy),
        arc=dict(cx=centre[0], cy=centre[1], r_top=ct[2], r_bot=rb_mean,
                 r_bot_wander=rb_dev, r_base=r_base, cap=cap,
                 x0=int(x0), x1=int(x1),
                 key_px=float((band & (np.abs(rad - ct[2]) < 9)).sum(0).max())),
        letters=letters,
    )
    os.makedirs(o.outdir, exist_ok=True)
    with open(os.path.join(o.outdir, 'plate.json'), 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'))
    print(f'{o.outdir}/plate.json: {len(letters)} letters, '
          f'{os.path.getsize(os.path.join(o.outdir, "plate.json")) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
