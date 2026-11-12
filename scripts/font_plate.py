"""Build a plate.json from a typeface, so the viewer can set any face.

The frame, the pendant, the knockout, the rules, the optical spacing
and the measuring all live in the viewer already and all of it is
indifferent to where the letters came from. It reads a word as eleven
outlines with widths and an optical fit. Tracing the artwork produces
that; so can a font. This writes the second kind.

The optical fit is solved the same way as for the traced letters -
equal PAPER between neighbours rather than equal advances - because a
font's own sidebearings are fitted for text at reading size, not for
eleven capitals set on an arch at 10 mm.
"""
import argparse, json, math, os
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw, ImageFont

CAP = 1000.0          # working units per cap height
RBASE = 40000.0       # the nominal baseline radius these angles are about


def outlines(path, text):
    f = TTFont(path)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    # Measure the H rather than believe the font. OS/2's declared cap
    # height is advisory and display faces get it wrong: Cinzel says
    # 700 for an H that is really 1030, and a cap height 47% out scales
    # every advance by the same factor while the rendered profiles stay
    # right - which is how the first fit came out with one pair at the
    # bisection's ceiling.
    bp = BoundsPen(gs)
    gs[cmap[ord('H')]].draw(bp)
    cap = bp.bounds[3] - bp.bounds[1]
    s = CAP / cap
    out = []
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            raise SystemExit(f'{os.path.basename(path)}: no glyph for {ch!r}')
        gb = BoundsPen(gs)
        gs[gn].draw(gb)
        if gb.bounds is None:
            out.append(dict(ch=ch, adv=gs[gn].width * s, d='',
                            left=0.0, right=0.0))
            continue
        cxf = (gb.bounds[0] + gb.bounds[2]) / 2
        # Bake the placement into the coordinates. The viewer puts each
        # letter's own origin on the arc and sets `d` straight onto a
        # path, so there is nowhere for a transform to live: the glyph
        # has to arrive already centred on its ink and already y-down.
        pen = SVGPathPen(gs, ntos=lambda v: f'{v:.1f}')
        gs[gn].draw(TransformPen(pen, (s, 0, 0, -s, -cxf * s, 0)))
        out.append(dict(ch=ch, adv=gs[gn].width * s, d=pen.getCommands(),
                        left=(gb.bounds[0] - cxf) * s,
                        right=(gb.bounds[2] - cxf) * s))
    return out, s


def profiles(path, text, rows=200):
    """Left/right silhouette per row, in CAP units, for each letter."""
    px = 700
    fnt = ImageFont.truetype(path, px)
    a, b, c, e = fnt.getbbox('H')
    cap_px = e - b
    k = CAP / cap_px
    out = []
    for ch in text:
        im = Image.new('L', (px * 3, px * 3), 255)
        ImageDraw.Draw(im).text((px, px), ch, font=fnt, fill=0)
        arr = np.array(im) < 128
        ys, xs = np.nonzero(arr)
        if not len(ys):
            out.append((np.full(rows, np.nan), np.full(rows, np.nan), 0.0))
            continue
        # rows measured from the baseline up to the cap
        base = px + (fnt.getbbox('H')[3])
        top = base - cap_px
        left = np.full(rows, np.nan); right = np.full(rows, np.nan)
        for r in range(rows):
            y = int(round(top + (base - top) * r / (rows - 1)))
            if 0 <= y < arr.shape[0]:
                xr = np.nonzero(arr[y])[0]
                if len(xr):
                    left[r] = xr.min() * k
                    right[r] = xr.max() * k
        cx = (xs.min() + xs.max() + 1) / 2 * k
        out.append((left - cx, right - cx,
                    (xs.min() * k - cx, (xs.max() + 1) * k - cx)))
    return out


def optical(profs, advs, limit=0.5, rows=200):
    dy = CAP / (rows - 1)
    cl = limit * CAP

    def gap(i, s, shift):
        r = profs[i][1] - shift[i]
        l = profs[i + 1][0] - shift[i + 1]
        ok = ~np.isnan(r) & ~np.isnan(l)
        if not ok.any():
            return 0.0
        return float(np.clip((l[ok] + s) - r[ok], 0, cl).sum() * dy)

    shift = [0.0] * len(profs)      # profiles already sit on their centres

    def solve(i, target):
        lo, hi = 0.0, 8.0 * CAP
        for _ in range(60):
            m = (lo + hi) / 2
            if gap(i, m, shift) < target:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2

    want = sum(advs) - (advs[0] + advs[-1]) / 2
    lo, hi = 1e-6, cl * CAP * 4
    for _ in range(60):
        t = (lo + hi) / 2
        if sum(solve(i, t) for i in range(len(profs) - 1)) < want:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return [solve(i, t) for i in range(len(profs) - 1)], shift


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('font'); ap.add_argument('out')
    ap.add_argument('--word', default='OBERNDÖRFER')
    ap.add_argument('--banner', default='MADE IN ITALY')
    ap.add_argument('--bannerfont',
                    default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    ap.add_argument('--weight', type=float, default=0.0,
                    help='CAP units added to every stroke, for a die')
    o = ap.parse_args()

    glyphs, s = outlines(o.font, o.word)
    profs = profiles(o.font, o.word)
    fit, shift = optical(profs, [g['adv'] for g in glyphs])

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'ap_mod', os.path.join(os.path.dirname(__file__), 'arch_plate.py'))
    apm = importlib.util.module_from_spec(spec); spec.loader.exec_module(apm)

    letters, ang = [], 0.0
    for i, g in enumerate(glyphs):
        letters.append(dict(
            ch=g['ch'], angle=math.degrees(ang),
            left=g['left'], right=g['right'],
            paths=[g['d']] if g['d'] else [], inlay=[], detail=[]))
        if i < len(fit):
            ang += fit[i] / RBASE

    doc = dict(source=os.path.basename(o.font),
               px=dict(w=4000, h=1500), shadow=[0, 0],
               banner=apm.set_text(o.banner, o.bannerfont) if o.banner else None,
               fit=[float(v) for v in fit],
               arc=dict(cx=0.0, cy=0.0, r_top=RBASE + CAP, r_bot=RBASE - CAP,
                        r_bot_wander=0.0, r_base=RBASE, cap=CAP,
                        x0=0.0, x1=1.0, key_px=10.0),
               letters=letters)
    with open(o.out, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'))
    print(f'{os.path.basename(o.font)}: {len(letters)} letters, '
          f'fit {min(fit):.0f}..{max(fit):.0f} units, '
          f'{os.path.getsize(o.out)/1024:.0f} KB')


if __name__ == '__main__':
    main()
