"""Fifty marks that differ in STRUCTURE, not in typeface.

Swapping the face inside one frame is one idea shown fifty times. This
is a small library of frames and of ways to set type in them, and the
fifty are combinations of those: a seal with the name curved round it,
a shield, a lozenge, a keystone, a barrel, a ribbon, a monogram with
the name under it, two lines stacked with a rule between, and so on.

One face throughout on purpose - the variable here is the shape. Any
of these can be rebuilt in the house letters once one is chosen.
"""
import argparse, json, math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

F = lambda v: f'{v:.3f}'


class Face:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        bp = BoundsPen(self.gs)
        self.gs[self.cmap[ord('H')]].draw(bp)
        self.cap = bp.bounds[3] - bp.bounds[1]      # measured, not declared

    def glyph(self, ch, cap_mm):
        gn = self.cmap.get(ord(ch))
        if gn is None:
            raise SystemExit(f'no glyph for {ch!r}')
        s = cap_mm / self.cap
        pen = SVGPathPen(self.gs, ntos=lambda v: f'{v:.2f}')
        self.gs[gn].draw(TransformPen(pen, (s, 0, 0, -s, 0, 0)))
        return pen.getCommands(), self.gs[gn].width * s

    def widths(self, text, cap_mm):
        s = cap_mm / self.cap
        return [self.gs[self.cmap[ord(c)]].width * s for c in text]


def line(face, text, cap, track, cx=0.0, cy=0.0):
    """One straight line of type, centred on (cx, cy), baseline at cy."""
    adv = face.widths(text, cap)
    total = sum(adv) + track * (len(text) - 1)
    x = cx - total / 2
    out = []
    for ch, a in zip(text, adv):
        d, _ = face.glyph(ch, cap)
        if d.strip():
            out.append(f'<path d="{d}" transform="translate({F(x)} {F(cy)})"/>')
        x += a + track
    return ''.join(out), total


def arc(face, text, cap, track, r, phi0, flip=False, cx=0.0, cy=0.0):
    """Type round a circle. phi is clockwise from twelve o'clock.

    `flip` sets it along the bottom the right way up, which means the
    baseline sits OUTSIDE the letters and each one is turned a further
    half turn - not the same as running the top arc backwards.
    """
    adv = face.widths(text, cap)
    total = sum(adv) + track * (len(text) - 1)
    span = total / r
    d0 = -1 if flip else 1
    at = -span / 2
    out = []
    for ch, a in zip(text, adv):
        aw = (a + track) / r
        phi = phi0 + d0 * (at + aw / 2 - track / (2 * r))
        px = cx + r * math.sin(phi)
        py = cy - r * math.cos(phi)
        rot = math.degrees(phi) + (180 if flip else 0)
        g, _ = face.glyph(ch, cap)
        if g.strip():
            out.append(f'<path d="{g}" transform="translate({F(px)} {F(py)}) '
                       f'rotate({F(rot)}) translate({F(-a/2)} 0)"/>')
        at += aw
    return ''.join(out), span


# ---- frames -------------------------------------------------------
def circle(r):
    return (f'M{F(-r)} 0A{F(r)} {F(r)} 0 1 0 {F(r)} 0'
            f'A{F(r)} {F(r)} 0 1 0 {F(-r)} 0Z')


def ellipse(rx, ry):
    return (f'M{F(-rx)} 0A{F(rx)} {F(ry)} 0 1 0 {F(rx)} 0'
            f'A{F(rx)} {F(ry)} 0 1 0 {F(-rx)} 0Z')


def rrect(w, h, r):
    x, y = w / 2, h / 2
    return (f'M{F(-x+r)} {F(-y)}L{F(x-r)} {F(-y)}A{F(r)} {F(r)} 0 0 1 {F(x)} {F(-y+r)}'
            f'L{F(x)} {F(y-r)}A{F(r)} {F(r)} 0 0 1 {F(x-r)} {F(y)}'
            f'L{F(-x+r)} {F(y)}A{F(r)} {F(r)} 0 0 1 {F(-x)} {F(y-r)}'
            f'L{F(-x)} {F(-y+r)}A{F(r)} {F(r)} 0 0 1 {F(-x+r)} {F(-y)}Z')


def cutrect(w, h, c):
    x, y = w / 2, h / 2
    return ('M' + ' L'.join(f'{F(a)} {F(b)}' for a, b in
            [(-x+c,-y),(x-c,-y),(x,-y+c),(x,y-c),(x-c,y),(-x+c,y),(-x,y-c),(-x,-y+c)]) + 'Z')


def lozenge(w, h):
    x, y = w / 2, h / 2
    return f'M0 {F(-y)}L{F(x)} 0L0 {F(y)}L{F(-x)} 0Z'


def hexagon(w, h, c):
    x, y = w / 2, h / 2
    return ('M' + ' L'.join(f'{F(a)} {F(b)}' for a, b in
            [(-x+c,-y),(x-c,-y),(x,0),(x-c,y),(-x+c,y),(-x,0)]) + 'Z')


def shield(w, h, r=0.30):
    """Rounded shoulders, straight flanks, a point at the foot."""
    x, y = w / 2, h / 2
    rr = x * r
    return (f'M{F(-x)} {F(-y+rr)}A{F(rr)} {F(rr)} 0 0 1 {F(-x+rr)} {F(-y)}'
            f'L{F(x-rr)} {F(-y)}A{F(rr)} {F(rr)} 0 0 1 {F(x)} {F(-y+rr)}'
            f'L{F(x)} {F(y-h*0.42)}Q{F(x)} {F(y)} 0 {F(y)}'
            f'Q{F(-x)} {F(y)} {F(-x)} {F(y-h*0.42)}Z')


def keystone(w, h, taper):
    x, y = w / 2, h / 2
    return f'M{F(-x)} {F(-y)}L{F(x)} {F(-y)}L{F(x-taper)} {F(y)}L{F(-x+taper)} {F(y)}Z'


def barrel(w, h, bulge):
    x, y = w / 2, h / 2
    return (f'M{F(-x)} {F(-y)}Q0 {F(-y-bulge)} {F(x)} {F(-y)}'
            f'L{F(x)} {F(y)}Q0 {F(y+bulge)} {F(-x)} {F(y)}Z')


def ribbon(w, h, fork, drop):
    """A straight ribbon with forked ends and the ends dropped."""
    x, y = w / 2, h / 2
    return ('M' + ' L'.join(f'{F(a)} {F(b)}' for a, b in
            [(-x,-y-drop),(x,-y-drop),(x,-y),(x+0,-y),(x,y),(x,y+drop),
             (x-fork,y+drop-h/2),(x,y+drop)][:0] or
            [(-x,-y),(x,-y),(x-fork,0),(x,y),(-x,y),(-x+fork,0)]) + 'Z')


def endclear(R, rt, rb, half, cap, span, q):
    """How close the end letter comes to the inside of the rounded end.

    Pushing the end gap out is only one way to buy that clearance, and
    the expensive one - it lengthens the whole plate. The other is the
    roundness: a full semicircle curves back in over the letter's top
    corner, which is exactly where the O and the R were being crowded,
    while a flatter end leaves a straight run for them to sit against.
    Measuring both lets the cheaper one do the work.
    """
    f = q * (rt - rb) / 2
    te = half
    rT = rt - f
    dT = math.asin(min(1.0, f / rT)) if f > 0 else 0.0
    tc = te - dT                      # the fillet centre's own angle
    cx, cy = P(R, rT, tc)
    worst = 1e9
    ts = span / 2 / R                 # the end letter's own angle
    for i in range(41):               # up the letter's outer edge
        r = R + cap * i / 40
        x, y = P(R, r, ts)
        worst = min(worst, math.hypot(x - cx, y - cy) - f)
        worst = min(worst, rt - r, r - rb)
    return worst


def archband(R, rt, rb, half, tip=0.0, q=1.0):
    P = lambda r, t: (r * math.sin(t), R - r * math.cos(t))
    f = lambda p: f'{F(p[0])} {F(p[1])}'
    rm = (rt + rb) / 2
    if tip > 0:
        dt = tip / rm
        return (f'M{f(P(rt,-half))}A{F(rt)} {F(rt)} 0 0 1 {f(P(rt,half))}'
                f'L{f(P(rm,half+dt))}L{f(P(rb,half))}'
                f'A{F(rb)} {F(rb)} 0 0 0 {f(P(rb,-half))}'
                f'L{f(P(rm,-half-dt))}Z')
    fr = q * (rt - rb) / 2
    return (f'M{f(P(rt,-half))}A{F(rt)} {F(rt)} 0 0 1 {f(P(rt,half))}'
            f'A{F(fr)} {F(fr)} 0 0 1 {f(P(rb,half))}'
            f'A{F(rb)} {F(rb)} 0 0 0 {f(P(rb,-half))}'
            f'A{F(fr)} {F(fr)} 0 0 1 {f(P(rt,-half))}Z')


# ---- composition ---------------------------------------------------
STROKE = 'fill="none" stroke="#000" stroke-linejoin="round"'


def svg(parts, pad=4.0):
    body = '\n'.join(parts)
    return ('<svg xmlns="http://www.w3.org/2000/svg" data-pad="%g">%s</svg>'
            % (pad, body))


def seal(face, tag, word, R, cap, track, tagcap, tagtrack, rings, star=True):
    """Name round the top, MADE IN ITALY round the foot the right way up."""
    p = [f'<path d="{circle(R)}" {STROKE} stroke-width="{F(rings[0])}"/>']
    for r, w in rings[1:]:
        p.append(f'<path d="{circle(r)}" {STROKE} stroke-width="{F(w)}"/>')
    t, _ = arc(face, word, cap, track, R - rings[0] / 2 - cap * 0.55, 0.0)
    p.append(f'<g fill="#000">{t}</g>')
    t2, _ = arc(face, tag, tagcap, tagtrack,
                R - rings[0] / 2 - tagcap * 0.55, math.pi, flip=True)
    p.append(f'<g fill="#000">{t2}</g>')
    if star:
        s = cap * 0.42
        for side in (-1, 1):
            a = math.radians(side * 86)
            x, y = R * 0.74 * math.sin(a), -R * 0.74 * math.cos(a)
            p.append(f'<path d="{lozenge(s, s*1.9)}" fill="#000" '
                     f'transform="translate({F(x)} {F(y)})"/>')
    return p


# ---- the house mark: an arched, round-ended plate -------------------
# Everything below keeps that plate. What varies is what is built on
# it: inner rules, beading, flanking devices, what hangs under it,
# what sits over it, and whether the whole thing is solid, knocked out
# or drawn in line. Fifty marks, one frame.

def P(R, r, t):
    return (r * math.sin(t), R - r * math.cos(t))


def bead(R, r, half, n, d):
    """A row of dots along an arc - a beaded border."""
    out = []
    for i in range(n):
        t = -half + 2 * half * i / (n - 1)
        x, y = P(R, r, t)
        out.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(d/2)}"/>')
    return '<g fill="#000">' + ''.join(out) + '</g>'


def flank(R, r, t, size, kind='diamond'):
    x, y = P(R, r, t)
    rot = math.degrees(t)
    if kind == 'diamond':
        d = lozenge(size, size * 1.8)
    elif kind == 'dot':
        d = circle(size / 2)
    else:                                  # a small upright bar
        d = rrect(size * 0.45, size * 1.7, size * 0.2)
    return (f'<path d="{d}" fill="#000" transform="translate({F(x)} {F(y)}) '
            f'rotate({F(rot)})"/>')


def pendant(R, rb, half, kind, depth, width, point, fork, round_):
    """What hangs under the plate. Several, all sharing its centre."""
    rm = rb
    w = (width / 2) / rm
    rS, rA = rb - depth, rb - depth - point
    f = lambda p: f'{F(p[0])} {F(p[1])}'
    top = rb + 1.4                        # tuck up behind the plate
    if kind == 'point':
        c1 = P(R, rS, w * 0.45); c2 = P(R, rA + (rS - rA) * 0.45, w * 0.1)
        c3 = P(R, rA + (rS - rA) * 0.45, -w * 0.1); c4 = P(R, rS, -w * 0.45)
        return (f'M{f(P(R,top,-w))}A{F(top)} {F(top)} 0 0 1 {f(P(R,top,w))}'
                f'L{f(P(R,rS,w))}C{f(c1)} {f(c2)} {f(P(R,rA,0))}'
                f'C{f(c3)} {f(c4)} {f(P(R,rS,-w))}Z')
    if kind == 'fork':
        return (f'M{f(P(R,top,-w))}A{F(top)} {F(top)} 0 0 1 {f(P(R,top,w))}'
                f'L{f(P(R,rS,w))}L{f(P(R,(top+rS)/2,w-fork/rm))}'
                f'L{f(P(R,rS,w))}'[:0] or
                f'M{f(P(R,top,-w))}A{F(top)} {F(top)} 0 0 1 {f(P(R,top,w))}'
                f'L{f(P(R,rS,w))}A{F(rS)} {F(rS)} 0 0 0 {f(P(R,rS,-w))}Z')
    if kind == 'tag':                     # a rounded tab
        rr = min(round_, depth / 2)
        return (f'M{f(P(R,top,-w))}A{F(top)} {F(top)} 0 0 1 {f(P(R,top,w))}'
                f'L{f(P(R,rS+rr,w))}A{F(rr)} {F(rr)} 0 0 1 {f(P(R,rS,w-rr/rm))}'
                f'A{F(rS)} {F(rS)} 0 0 0 {f(P(R,rS,-w+rr/rm))}'
                f'A{F(rr)} {F(rr)} 0 0 1 {f(P(R,rS+rr,-w))}Z')
    return ''


def finial(R, rt, size, kind='diamond'):
    x, y = P(R, rt + size * 0.95, 0.0)
    d = lozenge(size, size * 1.9) if kind == 'diamond' else circle(size / 2)
    return f'<path d="{d}" fill="#000" transform="translate({F(x)} {F(y)})"/>'


def compose(face, tagface, o):
    """One mark: the house plate, plus whatever `o` asks to be built on it."""
    word, tag = o['word'], o['tag']
    cap, track = o['cap'], o['track']
    adv = face.widths(word, cap)
    span = sum(adv) + track * (len(word) - 1)

    lo, hi = span / 8, span * 400          # radius giving the asked-for rise
    for _ in range(160):
        R = (lo + hi) / 2
        if R * (1 - math.cos(span / (2 * R))) > o['rise']:
            lo = R
        else:
            hi = R
    R = (lo + hi) / 2

    rt = R + cap + o['mtop']
    rb = R - o['mbot']
    inset_tag = o['tagplace'] == 'inside'
    if inset_tag:
        rb -= o['tagcap'] + o['taggap']
    half = (span / 2 + o['endgap']) / ((rt + rb) / 2)

    ink, paper = ('#fff', '#000') if o['invert'] else ('#000', '#fff')
    parts = []

    if o.get('shadow'):
        sb = archband(R, rt, rb, half, o['tip'], o.get('q', 1.0))
        dx, dy = o['shadow'], o['shadow'] * 1.6
        parts.append(f'<path d="{sb}" fill="#000" '
                     f'transform="translate({F(dx)} {F(dy)})"/>')

    if o.get('pend'):
        pd = pendant(R, rb, half, o['pend'], o['pdepth'], o['pwidth'],
                     o['ppoint'], o['pfork'], o['pround'])
        parts.append(f'<path d="{pd}" fill="{paper}" stroke="{ink}" '
                     f'stroke-width="{F(o["key"])}" stroke-linejoin="round"/>')

    band = archband(R, rt, rb, half, o['tip'], o.get('q', 1.0))
    parts.append(f'<path d="{band}" fill="{paper}" stroke="{ink}" '
                 f'stroke-width="{F(o["key"])}" stroke-linejoin="round"/>')

    for d, w in o.get('rules', []):
        inner = archband(R, rt - d, rb + d, half - d / ((rt + rb) / 2),
                         o['tip'] * 0.5, o.get('q', 1.0))
        parts.append(f'<path d="{inner}" fill="none" stroke="{ink}" '
                     f'stroke-width="{F(w)}" stroke-linejoin="round"/>')

    if o.get('beads'):
        n, dd, inset = o['beads']
        parts.append(bead(R, rt - inset, half * 0.985, n, dd)
                     .replace('fill="#000"', f'fill="{ink}"'))

    t, _ = arc(face, word, cap, track, R, 0.0, cx=0.0, cy=R)
    parts.append(f'<g fill="{ink}">{t}</g>')

    for side in o.get('flanks', []):
        a = (span / 2 + o['endgap'] * 0.52) / R * side
        parts.append(flank(R, R + cap * 0.42, a, cap * o['flanksize'],
                           o['flankkind']).replace('fill="#000"', f'fill="{ink}"'))

    if o.get('finial'):
        parts.append(finial(R, rt, cap * o['finial'], o['finialkind'])
                     .replace('fill="#000"', 'fill="#000"'))

    tc, tt = o['tagcap'], o['tagtrack']
    if o['tagplace'] == 'inside':
        t2, _ = arc(tagface, tag, tc, tt, rb + o['taggap'] + tc, 0.0, cx=0, cy=R)
        parts.append(f'<g fill="{ink}">{t2}</g>')
    elif o['tagplace'] == 'pendant' and o.get('pend'):
        # Hang it clear of the plate's own keyline rather than off the
        # middle of the pendant: the pendant tucks up BEHIND the plate,
        # so half its depth is hidden and a tag centred on it rides
        # into the keyline. Measured, that left 0.34 mm.
        r_t = rb - o['key'] / 2 - o['taggap'] - tc
        t2, _ = arc(tagface, tag, tc, tt, r_t, 0.0, cx=0, cy=R)
        parts.append(f'<g fill="{ink}">{t2}</g>')
    elif o['tagplace'] == 'below':
        t2, _ = arc(tagface, tag, tc, tt, rb - o['taggap'] - tc, 0.0, cx=0, cy=R)
        parts.append(f'<g fill="#000">{t2}</g>')
    return parts


DEF = dict(word='OBERNDÖRFER', tag='MADE IN ITALY', cap=10.4, track=0.0,
           rise=5.6, mtop=2.6, mbot=3.4, endgap=11.0, key=1.05, tip=0.0,
           invert=False, shadow=0.0, rules=(), beads=None, flanks=(),
           flanksize=0.5, flankkind='diamond', finial=0.0, finialkind='diamond',
           pend='point', pdepth=6.4, pwidth=45.0, ppoint=4.2, pfork=2.6,
           pround=2.0, tagplace='pendant', tagcap=2.9, tagtrack=0.80,
           taggap=1.6, q=1.0)


def box(parts, pad=5.0):
    """Fit the view to what was drawn, by rendering once and measuring."""
    return svg(parts, pad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('--face', required=True)
    ap.add_argument('--tagface',
                    default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    ap.add_argument('--specs', required=True, help='json list of overrides')
    o = ap.parse_args()
    face, tagface = Face(o.face), Face(o.tagface)
    specs = json.load(open(o.specs))
    os.makedirs(o.outdir, exist_ok=True)
    for i, sp in enumerate(specs, start=1):
        name = sp.pop('name')
        cfg = dict(DEF); cfg.update(sp)
        parts = compose(face, tagface, cfg)
        open(os.path.join(o.outdir, '%02d-%s.svg' % (i, name)), 'w').write(
            box(parts))
    print('%d marks -> %s' % (len(specs), o.outdir))


if __name__ == '__main__':
    main()
