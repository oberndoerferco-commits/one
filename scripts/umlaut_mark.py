"""The Ö as the mark.

The name is German, the goods are Italian, and the only letter that
says so is the O-umlaut. Three rounds of this project treated it as a
clearance problem - something to get out from under the keyline. It is
the most distinctive thing in the word.

So the device is the umlaut, drawn at the letter's own proportions
rather than invented beside it. Measured off Sancreek's Ö: the bowl's
stroke is 30 per cent of its width, each dot is 21 per cent, their
centres sit 34 per cent apart and 20 per cent above the bowl. The ring
below keeps those ratios, so the mark is the letter restated, not a
circle with two spots over it.

It is one idea at both ends of the range. At 8 mm it is a ring and two
dots, which a die can hold and the bead can carry. At full size the
same ring sits over the plate, and the plate's crown repeats the two
dots, so the lockup signs itself with the letter the name turns on.
"""
import argparse, math, os

F = lambda v: f'{v:.4f}'

# measured off the letter, as fractions of the bowl's width
STROKE, DOT, SPREAD, ABOVE = 0.295, 0.210, 0.340, 0.200


def ring(D, stroke=STROKE):
    """An annulus as two circles, even-odd filled."""
    ro, ri = D / 2, D / 2 - stroke * D
    return (f'M{F(-ro)} 0A{F(ro)} {F(ro)} 0 1 0 {F(ro)} 0'
            f'A{F(ro)} {F(ro)} 0 1 0 {F(-ro)} 0Z'
            f'M{F(-ri)} 0A{F(ri)} {F(ri)} 0 1 1 {F(ri)} 0'
            f'A{F(ri)} {F(ri)} 0 1 1 {F(-ri)} 0Z')


def oval(D, ratio, stroke=STROKE):
    """The same, on the letter's own width-to-height ratio."""
    ro, rih = D / 2, D / 2 * ratio
    ri, rii = D / 2 - stroke * D, D / 2 * ratio - stroke * D
    return (f'M{F(-ro)} 0A{F(ro)} {F(rih)} 0 1 0 {F(ro)} 0'
            f'A{F(ro)} {F(rih)} 0 1 0 {F(-ro)} 0Z'
            f'M{F(-ri)} 0A{F(ri)} {F(rii)} 0 1 1 {F(ri)} 0'
            f'A{F(ri)} {F(rii)} 0 1 1 {F(-ri)} 0Z')


def dots(D, cy, dot=DOT, spread=SPREAD):
    r = dot * D / 2
    x = spread * D / 2
    return (f'<circle cx="{F(-x)}" cy="{F(cy)}" r="{F(r)}"/>'
            f'<circle cx="{F(x)}" cy="{F(cy)}" r="{F(r)}"/>')


def monogram(D, kind='ring', ratio=1.0):
    top = -D / 2 * (ratio if kind == 'oval' else 1.0)
    cy = top - ABOVE * D
    body = oval(D, ratio) if kind == 'oval' else ring(D)
    return [f'<path d="{body}" fill="#000" fill-rule="evenodd"/>',
            f'<g fill="#000">{dots(D, cy)}</g>']


def disc(D, kind='ring', ratio=1.0, pad=0.26):
    """The device cut out of a solid disc.

    Inverting the first version drew a white ring on black and left the
    ring's own counter black in the middle of it - a dot inside a ring
    under two more dots, which reads as a face and not as a letter.
    Cutting the WHOLE device out in one even-odd path keeps the counter
    black because it is part of the disc, which is what it should be.
    """
    top = -D / 2 * (ratio if kind == 'oval' else 1.0)
    cy = top - ABOVE * D
    r = DOT * D / 2
    x = SPREAD * D / 2
    hi = cy - r
    lo = D / 2 * (ratio if kind == 'oval' else 1.0)
    rr = (lo - hi) / 2 + pad * D
    cc = (lo + hi) / 2
    body = oval(D, ratio) if kind == 'oval' else ring(D)
    hole = lambda cx, cyy, rad: (
        f'M{F(cx-rad)} {F(cyy)}A{F(rad)} {F(rad)} 0 1 0 {F(cx+rad)} {F(cyy)}'
        f'A{F(rad)} {F(rad)} 0 1 0 {F(cx-rad)} {F(cyy)}Z')
    d = (hole(0, cc, rr) + body + hole(-x, cy, r) + hole(x, cy, r))
    return [f'<path d="{d}" fill="#000" fill-rule="evenodd"/>']


def main():
    import importlib.util, json
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location('mk', os.path.join(here, 'marks.py'))
    mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)

    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('--face', required=True)
    ap.add_argument('--tagface',
                    default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    o = ap.parse_args()
    os.makedirs(o.outdir, exist_ok=True)
    face, tagface = mk.Face(o.face), mk.Face(o.tagface)

    def write(name, parts, pad=4.0):
        open(os.path.join(o.outdir, name + '.svg'), 'w').write(mk.svg(parts, pad))

    D = 22.0
    write('1-mark-ring', monogram(D, 'ring'))
    write('2-mark-oval', monogram(D, 'oval', ratio=984 / 682))
    write('3-mark-disc', disc(D, 'ring'), pad=1.0)
    write('3b-mark-disc-oval', disc(D, 'oval', ratio=984 / 682), pad=1.0)

    # the plate, with the crown carrying the same two dots
    base = dict(mk.DEF, endgap=1.5, pdepth=7.2, taggap=1.5, cap=10.4,
                mtop=3.0, mbot=3.4)
    for nm, extra in (('4-plate-crowned', {}),
                      ('5-plate-crowned-knock', {'invert': True}),
                      ('6-plate-crowned-rule', {'rules': [(1.5, 0.38)]})):
        cfg = dict(base); cfg.update(extra)
        parts = mk.compose(face, tagface, cfg)
        # the crown dots, at the word's own umlaut size, over the plate
        adv = face.widths(cfg['word'], cfg['cap'])
        span = sum(adv) + cfg['track'] * (len(cfg['word']) - 1)
        lo, hi = span / 8, span * 400
        for _ in range(160):
            R = (lo + hi) / 2
            if R * (1 - math.cos(span / (2 * R))) > cfg['rise']: lo = R
            else: hi = R
        R = (lo + hi) / 2
        rt = R + cfg['cap'] + cfg['mtop']
        cy = R - rt - cfg['cap'] * ABOVE * 1.15
        # Always ink: the crown dots stand on paper above the plate,
        # not on it, so inverting the plate must not invert them. Drawn
        # white they simply vanished.
        parts.append(f'<g fill="#000">{dots(cfg["cap"] * 1.55, cy)}</g>')
        write(nm, parts)

    # the monogram over the plate: the full lockup
    cfg = dict(base)
    parts = mk.compose(face, tagface, cfg)
    adv = face.widths(cfg['word'], cfg['cap'])
    span = sum(adv) + cfg['track'] * (len(cfg['word']) - 1)
    lo, hi = span / 8, span * 400
    for _ in range(160):
        R = (lo + hi) / 2
        if R * (1 - math.cos(span / (2 * R))) > cfg['rise']: lo = R
        else: hi = R
    R = (lo + hi) / 2
    rt = R + cfg['cap'] + cfg['mtop']
    Dm = cfg['cap'] * 2.9
    off = R - rt - Dm * (0.5 + ABOVE + DOT / 2) - 2.2
    stack = [f'<g transform="translate(0 {F(off)})">' + p + '</g>'
             for p in monogram(Dm, 'ring')]
    write('7-lockup', stack + parts)
    print('7 drawings ->', o.outdir)


if __name__ == '__main__':
    main()
