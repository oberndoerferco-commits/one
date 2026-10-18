"""Fifty monogram pattern variations for Oberndörfer, built only from the
brand's marks:

  om       OM blackletter monogram            ../monogram-canvas/motifs/om.svg
  roundel  star-cross in a disc  (PDF)        ../monogram-canvas/motifs/roundel.svg
  halo     star-cross, outline ring (PDF)     ../monogram-canvas/motifs/halo.svg
  tile     star-cross on a square (PDF)       ../monogram-canvas/motifs/tile.svg
  logo     the star-cross, solid              (drawn here from the traced outline)
  logoline the star-cross as an outline
  spark    small concave four-point star derived from the logo's notches
  dot, ring, diamond                          simple supporting shapes

    python3 -I design/monogram-variations/generate.py

Writes tiles/NN-<name>.svg (one repeat each, true size in mm) and
sheet-NN.html pages for rendering. See render.js for the preview images.
"""
import math
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MOTIF_DIR = os.path.join(HERE, '..', 'monogram-canvas', 'motifs')

# ---------------------------------------------------------------- symbols


def logo_path(R=1.0):
    """Star-cross, D4-symmetric, traced from the logo reference (tip radius R)."""
    k = R / 745.0
    P = lambda x, y: (x * k, y * k)
    refl = lambda p: (-p[1], -p[0])
    tip, a, b, c, n = P(0, -745), P(143, -528), P(345, -419), P(199, -273), P(148, -146)

    def rot(p, q):
        x, y = p
        for _ in range(q):
            x, y = -y, x
        return x, y

    s = lambda p, q: '%.4f %.4f' % rot(p, q)
    d = ''
    for q in range(4):
        d += ('L' if q else 'M') + f'{s(tip, q)} L{s(a, q)} L{s(b, q)} Q{s(c, q)} {s(n, q)} '
        d += f'Q{s(refl(c), q)} {s(refl(b), q)} L{s(refl(a), q)} '
    return d + 'Z'


def spark_path(r=1.0, pull=0.2):
    p = r * pull
    return (f'M0 {-r} Q{p} {-p} {r} 0 Q{p} {p} 0 {r} Q{-p} {p} {-r} 0 Q{-p} {-p} 0 {-r} Z')


def load_motif(name):
    s = open(os.path.join(MOTIF_DIR, f'{name}.svg')).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = re.sub(r'<style>.*?</style>', '', s[s.index('>') + 1:s.rindex('</svg>')], flags=re.S)
    if name == 'om':
        body = body.replace('fill="#000"', 'fill="currentColor"')
    return vb, body


SYMBOLS = {}
for name in ('om', 'roundel', 'halo', 'tile'):
    SYMBOLS[name] = load_motif(name)
SYMBOLS['logo'] = ('-1 -1 2 2', f'<path fill="currentColor" d="{logo_path(0.98)}"/>')
SYMBOLS['logoline'] = ('-1 -1 2 2', f'<path fill="none" stroke="currentColor" stroke-width="0.09" '
                       f'stroke-linejoin="miter" stroke-miterlimit="3" d="{logo_path(0.93)}"/>')
SYMBOLS['spark'] = ('-1 -1 2 2', f'<path fill="currentColor" d="{spark_path(0.98)}"/>')
SYMBOLS['dot'] = ('-1 -1 2 2', '<circle r="1" fill="currentColor"/>')
SYMBOLS['ring'] = ('-1 -1 2 2', '<circle r="0.9" fill="none" stroke="currentColor" stroke-width="0.14"/>')
SYMBOLS['diamond'] = ('-1 -1 2 2', '<path fill="currentColor" d="M0 -1 L1 0 L0 1 L-1 0 Z"/>')
# OM inside a thin ring (medallion)
om_vb = [float(v) for v in SYMBOLS['om'][0].split()]
SYMBOLS['ommedal'] = ('-1 -1 2 2',
                      '<circle r="0.94" fill="none" stroke="currentColor" stroke-width="0.06"/>'
                      '<circle r="0.84" fill="none" stroke="currentColor" stroke-width="0.025"/>'
                      f'<svg x="-0.62" y="-0.51" width="1.24" height="1.02" viewBox="{SYMBOLS["om"][0]}">{SYMBOLS["om"][1]}</svg>')
OM_ASPECT = om_vb[3] / om_vb[2]


def aspect(name):
    vb = [float(v) for v in SYMBOLS[name][0].split()]
    return vb[3] / vb[2]


# ---------------------------------------------------------------- palettes
# ground, primary (main motif), secondary (support motifs), dark (fills inside PDF motifs)
PAL = {
    'graphite': ('#101010', '#8b8b8b', '#5c5c5c', '#1e1e1e'),
    'denim': ('#232b39', '#a9b2bf', '#6f7b8c', '#2d3647'),
    'cognac': ('#5a3a25', '#c9a46b', '#a07c4c', '#6b4630'),
    'ivory': ('#f1ece3', '#1b1b1b', '#8a8278', '#e1d9cb'),
    'navygold': ('#16213a', '#c8a95e', '#8a7543', '#1f2c4a'),
    'blackgold': ('#0c0c0c', '#c3a35d', '#6e5d36', '#1a1a1a'),
    'olive': ('#3c3f2b', '#c9c2a3', '#8d8a6d', '#474a33'),
    'burgundy': ('#4a1620', '#d8b9a6', '#9d6d6a', '#5a1d28'),
    'sand': ('#d9c8ad', '#5a3a25', '#9b7e5a', '#cbb895'),
    'white': ('#ffffff', '#111111', '#9a9a9a', '#e9e9e9'),
    'tonalblack': ('#121212', '#262626', '#1c1c1c', '#171717'),
    'tonalbrown': ('#5a3a25', '#684530', '#613f2a', '#553622'),
    'stone': ('#bdb6aa', '#efebe4', '#d6d0c5', '#b0a99c'),
    'forest': ('#1e3226', '#c8b98a', '#7f8a6a', '#26402f'),
}


# ---------------------------------------------------------------- pattern builder

class Pattern:
    def __init__(self, W, H, pal):
        self.W, self.H = W, H
        self.pal = PAL[pal]
        self.items = []   # svg snippets in tile coordinates (may overflow; copies added on output)
        self.under = []   # drawn first (lines, bands)

    def put(self, sym, x, y, w, rot=0, col='p', wrap=True):
        c = {'p': self.pal[1], 's': self.pal[2], 'g': self.pal[0], 'd': self.pal[3]}.get(col, col)
        h = w * aspect(sym)
        snip = (f'<use href="#{sym}" x="{-w / 2:.3f}" y="{-h / 2:.3f}" width="{w:.3f}" height="{h:.3f}" '
                f'color="{c}" transform="translate(XX YY) rotate({rot})"/>')
        self.items.append((snip, x, y, wrap))

    def raw(self, svg, under=True):
        (self.under if under else self.items).append((svg, 0, 0, False))

    def svg(self):
        W, H = self.W, self.H
        g, p, s, d = self.pal
        out = []
        for lst in (self.under, self.items):
            for snip, x, y, wrap in lst:
                offs = [(dx, dy) for dx in (-W, 0, W) for dy in (-H, 0, H)] if wrap else [(0, 0)]
                for dx, dy in offs:
                    X, Y = x + dx, y + dy
                    if wrap and not (-W * 0.5 <= X <= W * 1.5 and -H * 0.5 <= Y <= H * 1.5):
                        continue
                    out.append(snip.replace('XX', f'{X:.3f}').replace('YY', f'{Y:.3f}'))
        defs = ''.join(f'<symbol id="{k}" viewBox="{vb}" overflow="visible">{body}</symbol>' for k, (vb, body) in SYMBOLS.items())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}">'
                f'<style>.lt{{fill:{p}}}.dk{{fill:{d}}}.ln{{fill:{g}}}</style>'
                f'<defs>{defs}<clipPath id="c"><rect width="{W:g}" height="{H:g}"/></clipPath></defs>'
                f'<rect width="{W:g}" height="{H:g}" fill="{g}"/><g clip-path="url(#c)">{"".join(out)}</g></svg>\n')


def lines(P, segs, col='s', w=0.6, dash=None, cap='butt'):
    c = {'p': P.pal[1], 's': P.pal[2], 'd': P.pal[3]}.get(col, col)
    d = ' '.join(f'M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}' for x1, y1, x2, y2 in segs)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    P.raw(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="{cap}"{da}/>')


def rect(P, x, y, w, h, col='d', rx=0):
    c = {'p': P.pal[1], 's': P.pal[2], 'd': P.pal[3]}.get(col, col)
    for dx in (-P.W, 0, P.W):
        for dy in (-P.H, 0, P.H):
            P.raw(f'<rect x="{x + dx:.2f}" y="{y + dy:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{c}"/>')


def diag_lattice(P, step, col='s', w=0.6, dash=None):
    W, H = P.W, P.H
    segs = []
    for k in range(-6, 7):
        c = k * step
        segs.append((c - H, -H, c + 2 * H, 2 * H))
        segs.append((c + 2 * H, -H, c - H, 2 * H))
    lines(P, segs, col, w, dash)


# ---------------------------------------------------------------- the fifty

V = []


def variant(name, title):
    def deco(fn):
        V.append((name, title, fn))
        return fn
    return deco


# 1-5 rosette family (the owner's sketch)
def rosette(pal, A=36, om=21, small=15, tile=12.5, stagger=False, swap=False):
    P = Pattern(2 * A, 2 * A if not stagger else 4 * A, pal)
    rows = 2 if stagger else 1
    for r in range(rows):
        ox = A if (stagger and r) else 0
        oy = r * 2 * A
        P.put('om', ox, oy, om)
        P.put('roundel' if swap else 'tile', ox + A, oy, tile if not swap else small)
        P.put('roundel' if swap else 'tile', ox, oy + A, tile if not swap else small)
        P.put('tile' if swap else 'roundel', ox + A, oy + A, small if not swap else tile)
        for x, y in ((A / 2, A / 2), (3 * A / 2, A / 2), (A / 2, 3 * A / 2), (3 * A / 2, 3 * A / 2)):
            P.put('halo', ox + x, oy + y, small)
    return P


variant('rosette-graphite', 'Rosette · graphite')(lambda: rosette('graphite'))
variant('rosette-denim', 'Rosette · denim')(lambda: rosette('denim'))
variant('rosette-swapped', 'Rosette, discs and squares swapped')(lambda: rosette('cognac', swap=True))
variant('rosette-compact', 'Rosette, compact')(lambda: rosette('navygold', A=28, om=17, small=12, tile=10))
variant('rosette-airy', 'Rosette, airy')(lambda: rosette('ivory', A=44, om=22, small=13, tile=11))


# 6-10 diagonal canvas family
def canvas(pal, D=40, om=22, order=('om', 'halo', 'roundel', 'tile'), sizes=(15.5, 16.5, 13)):
    P = Pattern(2 * D, 2 * D, pal)
    a, b, c, d = order
    sz = {'om': om, 'roundel': sizes[0], 'halo': sizes[1], 'tile': sizes[2], 'logo': sizes[1],
          'spark': sizes[2] * 0.7, 'logoline': sizes[1], 'ommedal': om}
    for m, x, y in ((a, 0, 0), (b, D, 0), (c, D / 2, D / 2), (d, 3 * D / 2, D / 2),
                    (b, 0, D), (a, D, D), (d, D / 2, 3 * D / 2), (c, 3 * D / 2, 3 * D / 2)):
        P.put(m, x, y, sz[m])
    return P


variant('canvas-classic', 'Diagonal canvas · cognac')(lambda: canvas('cognac'))
variant('canvas-graphite', 'Diagonal canvas · graphite')(lambda: canvas('graphite'))
variant('canvas-logo-spark', 'Canvas with solid logo and spark')(lambda: canvas('denim', order=('om', 'logo', 'roundel', 'spark')))
variant('canvas-outline', 'Canvas, outline logos only')(lambda: canvas('ivory', order=('om', 'logoline', 'halo', 'spark')))
variant('canvas-medal', 'Canvas with OM medallions')(lambda: canvas('blackgold', om=24, order=('ommedal', 'logo', 'roundel', 'spark')))


# 11-14 logo-only / OM-only half-drops
@variant('logo-halfdrop', 'Star-cross half-drop')
def _():
    P = Pattern(30, 30, 'graphite')
    P.put('logo', 0, 0, 13); P.put('logo', 15, 15, 13)
    return P


@variant('logo-spark', 'Star-cross with sparks')
def _():
    P = Pattern(32, 32, 'navygold')
    P.put('logo', 0, 0, 13); P.put('logo', 16, 16, 13)
    P.put('spark', 16, 0, 5); P.put('spark', 0, 16, 5)
    return P


@variant('om-halfdrop', 'OM half-drop')
def _():
    P = Pattern(44, 36, 'cognac')
    P.put('om', 0, 0, 20); P.put('om', 22, 18, 20)
    return P


@variant('om-dots', 'OM with dot grid')
def _():
    P = Pattern(40, 40, 'burgundy')
    P.put('om', 0, 0, 19); P.put('om', 20, 20, 19)
    for x, y in ((20, 0), (0, 20)):
        P.put('dot', x, y, 2.2)
    for x, y in ((10, 10), (30, 10), (10, 30), (30, 30)):
        P.put('dot', x, y, 1.2, col='s')
    return P


# 15-18 checkers
@variant('checker-om-logo', 'Checker: OM and star-cross')
def _():
    P = Pattern(48, 48, 'denim')
    rect(P, 24, 0, 24, 24); rect(P, 0, 24, 24, 24)
    P.put('om', 12, 12, 17); P.put('om', 36, 36, 17)
    P.put('logo', 36, 12, 12); P.put('logo', 12, 36, 12)
    return P


@variant('checker-tonal', 'Tonal checker with logo')
def _():
    P = Pattern(40, 40, 'tonalbrown')
    rect(P, 20, 0, 20, 20, col='s'); rect(P, 0, 20, 20, 20, col='s')
    P.put('logo', 30, 10, 11, col='#c9a46b'); P.put('logo', 10, 30, 11, col='#c9a46b')
    return P


@variant('checker-motifs', 'Checker of disc and outline motifs')
def _():
    P = Pattern(40, 40, 'graphite')
    rect(P, 20, 0, 20, 20); rect(P, 0, 20, 20, 20)
    P.put('roundel', 10, 10, 13); P.put('roundel', 30, 30, 13)
    P.put('halo', 30, 10, 14); P.put('halo', 10, 30, 14)
    return P


@variant('checker-diagonal', 'Diagonal checker')
def _():
    P = Pattern(40, 40, 'olive')
    P.raw('<path d="M20 0 L40 20 L20 40 L0 20 Z" fill="%s"/>' % PAL['olive'][3])
    P.put('om', 20, 20, 16); P.put('logo', 0, 0, 11); P.put('spark', 20, 0, 4); P.put('spark', 0, 20, 4)
    return P


# 19-22 trellis / grids
@variant('trellis-logo', 'Diamond trellis with star-cross')
def _():
    P = Pattern(36, 36, 'cognac')
    diag_lattice(P, 36, w=0.7)
    P.put('logo', 0, 18, 13); P.put('logo', 18, 0, 13)
    P.put('dot', 0, 0, 2.4); P.put('dot', 18, 18, 2.4)
    return P


@variant('trellis-om', 'Diamond trellis with OM')
def _():
    P = Pattern(44, 44, 'ivory')
    diag_lattice(P, 44, w=0.5)
    P.put('om', 0, 22, 18); P.put('om', 22, 0, 18)
    P.put('spark', 0, 0, 4); P.put('spark', 22, 22, 4)
    return P


@variant('grid-om', 'Square grid with OM')
def _():
    P = Pattern(36, 36, 'navygold')
    lines(P, [(0, -1, 0, 37), (-1, 0, 37, 0)], w=0.5)
    P.put('om', 18, 18, 17); P.put('spark', 0, 0, 5)
    return P


@variant('trellis-dotted', 'Dotted trellis with discs')
def _():
    P = Pattern(36, 36, 'denim')
    diag_lattice(P, 36, w=1.0, dash='0.01 2.2')
    P.raw('', under=True)
    P.put('roundel', 0, 18, 13); P.put('roundel', 18, 0, 13)
    return P


# 23-27 stripes
@variant('stripe-om-columns', 'Columns: OM and star-cross')
def _():
    P = Pattern(40, 52, 'cognac')
    lines(P, [(10, -1, 10, 53), (30, -1, 30, 53)], w=0.4)
    P.put('om', 0, 13, 15); P.put('om', 0, 39, 15)
    P.put('logo', 20, 0, 10); P.put('logo', 20, 26, 10)
    return P


@variant('stripe-bands', 'Horizontal bands')
def _():
    P = Pattern(30, 44, 'graphite')
    rect(P, -1, 15, 32, 14)
    P.put('om', 15, 0, 17)
    P.put('spark', 0, 22, 4, col='p'); P.put('spark', 15, 22, 4, col='p')
    return P


@variant('stripe-diagonal', 'Diagonal stripes')
def _():
    P = Pattern(40, 40, 'navygold')
    for k in range(-3, 4):
        P.raw(f'<path d="M{k * 40 - 2} -2 L{k * 40 + 18} -2 L{k * 40 + 58} 42 L{k * 40 + 38} 42 Z" fill="{PAL["navygold"][3]}" transform="skewX(0)"/>')
    P.put('logo', 10, 30, 10); P.put('om', 30, 10, 14)
    return P


@variant('pinstripe', 'Pinstripe with tiny logos')
def _():
    P = Pattern(14, 28, 'ivory')
    lines(P, [(0, -1, 0, 29)], col='s', w=0.25)
    P.put('logo', 7, 7, 5); P.put('spark', 7, 21, 2.4, col='s')
    return P


@variant('band-big-om', 'Rows of large OM and small logos')
def _():
    P = Pattern(60, 50, 'burgundy')
    P.put('om', 15, 14, 24); P.put('om', 45, 14, 24)
    for x in (0, 10, 20, 30, 40, 50):
        P.put('logo', x + 5, 38, 6, col='s')
    return P


# 28-31 tonal / jacquard
@variant('tonal-black', 'Tonal black jacquard')
def _():
    return canvas('tonalblack', order=('om', 'logo', 'roundel', 'spark'))


@variant('tonal-brown', 'Tonal brown, micro logo')
def _():
    P = Pattern(12, 12, 'tonalbrown')
    P.put('logo', 0, 0, 6); P.put('logo', 6, 6, 6)
    return P


@variant('tonal-big-om', 'Big OM over micro logos')
def _():
    P = Pattern(60, 60, 'denim')
    for i in range(10):
        for j in range(10):
            if (i + j) % 2 == 0:
                P.put('logo', i * 6, j * 6, 2.6, col='d', wrap=False)
    P.put('om', 30, 30, 30)
    return P


@variant('stone-relief', 'Stone, light on light')
def _():
    return rosette('stone')


# 32-35 rotation / geometry
@variant('pinwheel', 'Pinwheel of turned logos')
def _():
    P = Pattern(30, 30, 'forest')
    P.put('logo', 0, 0, 12); P.put('logo', 15, 15, 12, rot=45)
    P.put('spark', 15, 0, 4); P.put('spark', 0, 15, 4, rot=45)
    return P


@variant('herringbone-om', 'Herringbone OM')
def _():
    P = Pattern(36, 40, 'cognac')
    P.put('om', 9, 10, 15, rot=-30); P.put('om', 27, 10, 15, rot=30)
    P.put('om', 9, 30, 15, rot=-30); P.put('om', 27, 30, 15, rot=30)
    return P


@variant('alternating-rows', 'Alternating rows: OM and star-cross')
def _():
    P = Pattern(52, 44, 'graphite')
    P.put('om', 0, 0, 15); P.put('om', 26, 0, 15)
    P.put('logo', 13, 22, 9); P.put('logo', 39, 22, 9)
    P.put('spark', 13, 0, 3, col='s'); P.put('spark', 39, 0, 3, col='s')
    return P


@variant('logo-diamonds', 'Logos in diamonds')
def _():
    P = Pattern(30, 30, 'blackgold')
    P.put('diamond', 0, 0, 20, col='d'); P.put('diamond', 15, 15, 20, col='d')
    P.put('logo', 0, 0, 11); P.put('logo', 15, 15, 11)
    return P


# 36-39 medallions
@variant('medallion-om', 'OM medallions')
def _():
    P = Pattern(40, 40, 'navygold')
    P.put('ommedal', 0, 0, 26); P.put('ommedal', 20, 20, 26)
    P.put('spark', 20, 0, 5); P.put('spark', 0, 20, 5)
    return P


@variant('medallion-mixed', 'OM medallions with discs')
def _():
    P = Pattern(44, 44, 'cognac')
    P.put('ommedal', 0, 0, 26); P.put('ommedal', 22, 22, 26)
    P.put('roundel', 22, 0, 12); P.put('roundel', 0, 22, 12)
    return P


@variant('ring-chain', 'Ring chain with logos')
def _():
    P = Pattern(24, 24, 'ivory')
    P.put('ring', 0, 0, 24, col='s'); P.put('logo', 0, 0, 10); P.put('dot', 12, 12, 2)
    return P


@variant('ring-om', 'Rings with OM')
def _():
    P = Pattern(40, 40, 'olive')
    P.put('ring', 0, 0, 34, col='s'); P.put('ring', 20, 20, 34, col='s')
    P.put('om', 0, 0, 17); P.put('logo', 20, 20, 11)
    return P


# 40-42 scattered (repeatable)
def scatter(pal, n, seed, syms, W=80, rot=False):
    P = Pattern(W, W, pal)
    rng = random.Random(seed)
    # best-candidate sampling: always terminates, keeps marks evenly apart
    dist = lambda x, y, a, b: min(abs(x - a), W - abs(x - a)) ** 2 + min(abs(y - b), W - abs(y - b)) ** 2
    pts = [(rng.uniform(0, W), rng.uniform(0, W))]
    while len(pts) < n:
        cands = [(rng.uniform(0, W), rng.uniform(0, W)) for _ in range(60)]
        pts.append(max(cands, key=lambda c: min(dist(c[0], c[1], a, b) for a, b in pts)))
    for i, (x, y) in enumerate(pts):
        m, w = syms[i % len(syms)]
        P.put(m, x, y, w, rot=rng.uniform(-35, 35) if rot else 0)
    return P


variant('scatter-logos', 'Scattered marks')(lambda: scatter('denim', 14, 3, [('om', 16), ('logo', 10), ('roundel', 11), ('spark', 4)]))
variant('scatter-tossed', 'Tossed, turned marks')(lambda: scatter('cognac', 14, 7, [('om', 16), ('logo', 10), ('halo', 12), ('spark', 4)], rot=True))
variant('scatter-stars', 'Star field')(lambda: scatter('navygold', 22, 11, [('logo', 7), ('spark', 3), ('spark', 2), ('logo', 4)]))


# 43-45 linked
@variant('constellation', 'Constellation: logos linked by lines')
def _():
    P = Pattern(40, 40, 'graphite')
    lines(P, [(0, 0, 20, 20), (20, 20, 40, 0), (20, 20, 0, 40), (20, 20, 40, 40)], w=0.3)
    P.put('logo', 0, 0, 10); P.put('roundel', 20, 20, 11)
    return P


@variant('chain-om', 'OM chain')
def _():
    P = Pattern(40, 24, 'burgundy')
    lines(P, [(-1, 12, 41, 12)], w=0.4, dash='1 1.4')
    P.put('om', 10, 12, 15); P.put('logo', 30, 12, 8); P.put('dot', 10, 0, 1.4, col='s'); P.put('dot', 30, 0, 1.4, col='s')
    return P


@variant('net', 'Net of sparks')
def _():
    P = Pattern(20, 20, 'forest')
    diag_lattice(P, 20, w=0.3)
    P.put('spark', 0, 0, 5); P.put('logo', 10, 10, 8)
    return P


# 46-50 minimal
@variant('minimal-om', 'Minimal OM')
def _():
    P = Pattern(60, 60, 'white')
    P.put('om', 0, 0, 16); P.put('om', 30, 30, 16)
    return P


@variant('minimal-logo', 'Minimal star-cross')
def _():
    P = Pattern(40, 40, 'sand')
    P.put('logo', 0, 0, 9); P.put('logo', 20, 20, 9)
    return P


@variant('minimal-spark', 'Micro sparks with one OM')
def _():
    P = Pattern(48, 48, 'blackgold')
    for i in range(4):
        for j in range(4):
            if (i, j) != (0, 0):
                P.put('spark', i * 12, j * 12, 2.6, col='s')
    P.put('om', 0, 0, 16)
    return P


@variant('signature-row', 'Signature rows')
def _():
    P = Pattern(48, 30, 'ivory')
    P.put('om', 12, 15, 14); P.put('logo', 30, 15, 8); P.put('spark', 42, 15, 3, col='s')
    return P


@variant('grand-om', 'Grand OM')
def _():
    P = Pattern(90, 90, 'graphite')
    P.put('om', 0, 0, 42); P.put('om', 45, 45, 42)
    P.put('logo', 45, 0, 10, col='s'); P.put('logo', 0, 45, 10, col='s')
    return P


# ---------------------------------------------------------------- output

if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'tiles'), exist_ok=True)
    meta = []
    for i, (name, title, fn) in enumerate(V, 1):
        P = fn()
        fname = f'{i:02d}-{name}.svg'
        with open(os.path.join(HERE, 'tiles', fname), 'w') as fh:
            fh.write(P.svg())
        meta.append((i, title, fname, P.W, P.H))
    with open(os.path.join(HERE, 'tiles', 'index.tsv'), 'w') as fh:
        for row in meta:
            fh.write('\t'.join(map(str, row)) + '\n')
    print(len(meta), 'variations written to tiles/')
