"""Two tiers: the name on a bent ribbon, MADE IN ITALY on its own panel.

The structure is fixed now; what varies here is only how the ribbon's
ends are treated. Eight ways, all on the same bend, with the same
typeface and the same lower panel, so the ends are the only thing
being judged.
"""
import math, os, importlib.util, argparse
here = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('mk', os.path.join(here, 'marks.py'))
mk = importlib.util.module_from_spec(sp); sp.loader.exec_module(mk)
F = mk.F


def radius(span, rise):
    lo, hi = span / 8, span * 400
    for _ in range(160):
        R = (lo + hi) / 2
        if R * (1 - math.cos(span / (2 * R))) > rise: lo = R
        else: hi = R
    return (lo + hi) / 2


def band(R, rt, rb, half, style, tail=14.0, drop=5.0, fork=3.6):
    """One bent band, with its ends done eight different ways."""
    P = lambda r, t: mk.P(R, r, t)
    f = lambda q: f'{F(q[0])} {F(q[1])}'
    A = lambda r, q: f'A{F(r)} {F(r)} 0 0 1 {f(q)}'
    B = lambda r, q: f'A{F(r)} {F(r)} 0 0 0 {f(q)}'
    rm = (rt + rb) / 2
    tw = tail / rm

    if style == 'plain':
        return ('M' + f(P(rt, -half)) + A(rt, P(rt, half)) +
                'L' + f(P(rb, half)) + B(rb, P(rb, -half)) + 'Z')

    if style == 'swallow':
        fq = fork / rm
        return ('M' + f(P(rt, -half)) + A(rt, P(rt, half)) +
                'L' + f(P(rm, half - fq)) + 'L' + f(P(rb, half)) +
                B(rb, P(rb, -half)) + 'L' + f(P(rm, -half + fq)) + 'Z')

    if style == 'pennant':
        pq = fork * 2.0 / rm
        return ('M' + f(P(rt, -half)) + A(rt, P(rt, half)) +
                'L' + f(P(rm, half + pq)) + 'L' + f(P(rb, half)) +
                B(rb, P(rb, -half)) + 'L' + f(P(rm, -half - pq)) + 'Z')

    # the folded family: the tail steps DOWN and OUT from the band
    rtT, rbT = rt - drop, rb - drop
    if style == 'flare':
        rtT, rbT = rt - drop * 0.6, rb - drop * 1.5
    rmT = (rtT + rbT) / 2
    fq = fork / rmT

    if style == 'fold-fork':
        endr = 'L' + f(P(rmT, half + tw - fq)) + 'L' + f(P(rbT, half + tw))
        endl = 'L' + f(P(rmT, -half - tw + fq)) + 'L' + f(P(rtT, -half - tw))
    elif style in ('fold-straight', 'flare'):
        endr = 'L' + f(P(rbT, half + tw))
        endl = 'L' + f(P(rtT, -half - tw))
    elif style == 'step':
        endr = 'L' + f(P(rbT, half + tw))
        endl = 'L' + f(P(rtT, -half - tw))
        tw = tw * 0.55
        endr = 'L' + f(P(rbT, half + tw))
        endl = 'L' + f(P(rtT, -half - tw))
    elif style == 'roll':
        rq = fork * 1.3 / rmT
        endr = ('L' + f(P(rbT, half + tw)) + B(rbT, P(rbT, half + tw - rq)) +
                'L' + f(P(rtT, half + tw - rq)) + A(rtT, P(rtT, half + tw)) +
                'L' + f(P(rbT, half + tw)))
        endl = ('L' + f(P(rtT, -half - tw)) + B(rtT, P(rtT, -half - tw + rq)) +
                'L' + f(P(rbT, -half - tw + rq)) + A(rbT, P(rbT, -half - tw)) +
                'L' + f(P(rtT, -half - tw)))
    else:
        endr = 'L' + f(P(rbT, half + tw)); endl = 'L' + f(P(rtT, -half - tw))

    return ('M' + f(P(rt, -half)) + A(rt, P(rt, half)) +
            'L' + f(P(rtT, half)) + A(rtT, P(rtT, half + tw)) + endr +
            B(rbT, P(rbT, half)) + 'L' + f(P(rb, half)) +
            B(rb, P(rb, -half)) + 'L' + f(P(rbT, -half)) +
            B(rbT, P(rbT, -half - tw)) + endl +
            A(rtT, P(rtT, -half)) + 'Z')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir'); ap.add_argument('--face', required=True)
    ap.add_argument('--tagface', required=True)
    o = ap.parse_args()
    os.makedirs(o.outdir, exist_ok=True)
    face, tf = mk.Face(o.face), mk.Face(o.tagface)
    W, T = 'OBERNDÖRFER', 'MADE IN ITALY'
    CAP, TC = 10.6, 4.0
    K = 'stroke="#000" stroke-linejoin="round"'
    adv = face.widths(W, CAP); span = sum(adv)
    R = radius(span, 4.6)
    rt, rb = R + CAP + 3.0, R - 3.0
    half = (span / 2 + 2.6) / ((rt + rb) / 2)

    tadv = tf.widths(T, TC); tspan = sum(tadv) + 1.1 * (len(T) - 1)
    GAP = 3.0
    for style in ('fold-fork', 'fold-straight', 'swallow', 'pennant',
                  'step', 'roll', 'flare', 'plain'):
        top = band(R, rt, rb, half, style)
        # the lower panel: the same bend, narrower, simple ends
        Rp = R
        prt = rb - GAP
        prb = prt - (TC + 4.2)
        phalf = (tspan / 2 + 4.0) / ((prt + prb) / 2)
        low = band(Rp, prt, prb, phalf,
                   'swallow' if style in ('swallow', 'pennant') else 'plain',
                   fork=2.4)
        parts = [f'<path d="{top}" fill="#fff" {K} stroke-width="1.35"/>',
                 f'<g fill="#000">'
                 f'{mk.arc(face, W, CAP, 0.0, R, 0.0, cx=0, cy=R)[0]}</g>',
                 f'<path d="{low}" fill="#fff" {K} stroke-width="1.15"/>',
                 f'<g fill="#000">'
                 f'{mk.arc(tf, T, TC, 1.1, prb + 2.1, 0.0, cx=0, cy=Rp)[0]}</g>']
        open(os.path.join(o.outdir, style + '.svg'), 'w').write(mk.svg(parts, 5))
    print('8 ribbons ->', o.outdir)


if __name__ == '__main__':
    main()
