"""The fourth mark: a gothic wordmark on an arched, folded banner.

Nothing here is traced from the nameplate - this is a different drawing
in a different voice, which is what was asked for. What it keeps is the
bend: the band and both lines of type are struck about one centre, the
same way the plate is, so the family still reads as one hand.

The face is Grenze Gotisch Bold, and it was chosen by measurement
rather than by eye. Hot foil on leather wants a 0.5 mm line and about
a millimetre between elements, and blackletter is the worst possible
starting point for that - it is a style built on the contrast between a
broad stem and a hairline join. Set at a 9 mm cap:

    UnifrakturCook        thinnest 0.055 mm    contrast 18.7 : 1
    UnifrakturMaguntia    thinnest 0.183 mm    contrast  4.0 : 1
    Grenze Gotisch Bold   thinnest 0.386 mm    contrast  3.1 : 1

Only the last is within reach of a die, and it is also the one furthest
from the reference, being a modern gothic rather than a textura. That
is a convenience, not a coincidence: what makes a blackletter look
antique is exactly the contrast that makes it unstampable.

Even so 0.386 is under 0.5, so `--weight` dilates the letterforms by
stroking them in their own colour. It is the honest lever - it changes
the face's colour slightly and buys the line width a die needs without
making the mark enormous.
"""
import argparse, math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen


def load(path, text):
    f = TTFont(path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upem = f['head'].unitsPerEm
    try:
        cap = f['OS/2'].sCapHeight
    except Exception:
        cap = None
    if not cap:
        cap = f['hhea'].ascent * 0.72
    out = []
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            raise SystemExit(f'{os.path.basename(path)} has no glyph for {ch!r}')
        pen = SVGPathPen(gs)
        gs[gn].draw(pen)
        out.append(dict(ch=ch, adv=gs[gn].width, d=pen.getCommands()))
    return dict(upem=upem, cap=cap, glyphs=out)


def setline(font, cap_mm, track_mm):
    """Advances in mm for one line of type at a given cap height."""
    s = cap_mm / font['cap']
    adv = [g['adv'] * s for g in font['glyphs']]
    total = sum(adv) + track_mm * (len(adv) - 1)
    return s, adv, total


def arcline(font, s, adv, track, r, R, cx_off=0.0):
    """Place each glyph on the arc of radius r, turned to its own angle."""
    out = []
    at = -(sum(adv) + track * (len(adv) - 1)) / 2 + cx_off
    for i, g in enumerate(font['glyphs']):
        mid = at + adv[i] / 2
        t = mid / r
        x, y = r * math.sin(t), R - r * math.cos(t)
        if g['d'].strip():
            out.append((
                f'translate({x:.4f} {y:.4f}) rotate({math.degrees(t):.4f}) '
                f'scale({s:.6f} {-s:.6f}) translate({-g["adv"]/2:.2f} 0)',
                g['d']))
        at += adv[i] + track
    return out


def band(R, rt, rb, half, step, deep, fork):
    """An arched band whose ends are folded back and forked.

    Not a scroll. A scroll's ends roll forward and that roll is the
    whole of the reference's character, so this does the other
    traditional thing instead: the band steps DEEPER at each end, as a
    ribbon does where it folds back on itself, and the end is cut with
    a fork. Same vocabulary, different word.
    """
    P = lambda r, t: (r * math.sin(t), R - r * math.cos(t))
    w1, w2 = half - step / ((rt + rb) / 2), half
    rt2, rb2 = rt + deep, rb - deep
    rm2 = (rt2 + rb2) / 2
    fk = fork / rm2
    f = lambda p: f'{p[0]:.4f} {p[1]:.4f}'
    A = lambda r, p: f'A{r:.4f} {r:.4f} 0 0 1 {f(p)}'
    B = lambda r, p: f'A{r:.4f} {r:.4f} 0 0 0 {f(p)}'
    return (
        f'M{f(P(rt, -w1))}' + A(rt, P(rt, w1)) +
        f'L{f(P(rt2, w1))}' + A(rt2, P(rt2, w2)) +
        f'L{f(P(rm2, w2 - fk))}' +
        f'L{f(P(rb2, w2))}' + B(rb2, P(rb2, w1)) +
        f'L{f(P(rb, w1))}' + B(rb, P(rb, -w1)) +
        f'L{f(P(rb2, -w1))}' + B(rb2, P(rb2, -w2)) +
        f'L{f(P(rm2, -w2 + fk))}' +
        f'L{f(P(rt2, -w2))}' + A(rt2, P(rt2, -w1)) +
        f'L{f(P(rt, -w1))} Z')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('outdir')
    ap.add_argument('--word', default='OBERNDÖRFER')
    ap.add_argument('--tag', default='MADE IN ITALY')
    ap.add_argument('--font', default='/tmp/claude-0/-home-user-one/'
                    '9a731093-06fb-50bc-9d28-75940e80fb3f/scratchpad/fonts/gotisch.ttf')
    ap.add_argument('--tagfont',
                    default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    ap.add_argument('--cap', type=float, default=10.4, help='mm')
    ap.add_argument('--track', type=float, default=0.55, help='mm')
    ap.add_argument('--weight', type=float, default=0.22,
                    help='mm added to every stroke, for the die')
    ap.add_argument('--rise', type=float, default=7.0, help='mm over the word')
    ap.add_argument('--mtop', type=float, default=2.6, help='mm')
    ap.add_argument('--mbot', type=float, default=2.6, help='mm')
    ap.add_argument('--ends', type=float, default=6.0, help='mm past the word')
    ap.add_argument('--step', type=float, default=5.0, help='mm, the fold')
    ap.add_argument('--deep', type=float, default=1.9, help='mm, how much deeper')
    ap.add_argument('--fork', type=float, default=2.8, help='mm, the fork')
    ap.add_argument('--key', type=float, default=0.75, help='mm, band keyline')
    ap.add_argument('--tagcap', type=float, default=2.9, help='mm')
    ap.add_argument('--tagtrack', type=float, default=0.80, help='mm')
    ap.add_argument('--taggap', type=float, default=3.2, help='mm below the band')
    o = ap.parse_args()

    word = load(o.font, o.word)
    tag = load(o.tagfont, o.tag)
    s, adv, span = setline(word, o.cap, o.track)

    # the radius that bows the word by `rise` over its own length
    if o.rise <= 0.001:
        raise SystemExit('this mark is built on the bend; rise must be > 0')
    lo, hi = span / 8, span * 400
    for _ in range(200):
        R = (lo + hi) / 2
        th = span / (2 * R)
        if R * (1 - math.cos(th)) > o.rise:
            lo = R
        else:
            hi = R
    R = (lo + hi) / 2

    r_base = R
    rt = R + o.cap + o.mtop          # band outer
    rb = R - o.mbot                  # band inner
    half = (span / 2 + o.ends) / ((rt + rb) / 2)

    d = band(R, rt, rb, half, o.step, o.deep, o.fork)
    glyphs = arcline(word, s, adv, o.track, r_base, R)

    ts, tadv, tspan = setline(tag, o.tagcap, o.tagtrack)
    r_tag = rb - o.deep - o.taggap - o.tagcap
    tagged = arcline(tag, ts, tadv, o.tagtrack, r_tag, R)

    parts = [f'<path d="{d}" fill="#fff" stroke="#000" '
             f'stroke-width="{o.key}" stroke-linejoin="round"/>']
    body = ''.join(f'<path d="{g}" transform="{t}"/>' for t, g in glyphs)
    parts.append(f'<g fill="#000" stroke="#000" stroke-width="{o.weight/s:.2f}" '
                 f'stroke-linejoin="round">{body}</g>')
    tbody = ''.join(f'<path d="{g}" transform="{t}"/>' for t, g in tagged)
    parts.append(f'<g fill="#000" stroke="#000" '
                 f'stroke-width="{o.weight/ts:.2f}" stroke-linejoin="round">'
                 f'{tbody}</g>')

    inner = '\n'.join(parts)
    os.makedirs(o.outdir, exist_ok=True)
    tmp = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400mm" '
           f'height="400mm" viewBox="-200 -200 400 400">{inner}</svg>')
    open(os.path.join(o.outdir, '_m.svg'), 'w').write(tmp)
    print(f'R {R:.1f} mm   word {span:.1f} mm   cap {o.cap} mm')
    print(f'wrote {o.outdir}/_m.svg (unfitted; the exporter sets the box)')


if __name__ == '__main__':
    main()
