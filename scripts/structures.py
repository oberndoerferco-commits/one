"""Eight structures for the same name, so the shape can be chosen by eye.

One letterform throughout on purpose. Everything that has been shown so
far was one structure dressed fifty ways; this is the opposite - eight
different things the mark could BE, with the typeface held constant so
it cannot confuse the choice.
"""
import math, os, importlib.util, argparse
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mk', os.path.join(here, 'marks.py'))
mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)
F = mk.F


def radius(span, rise):
    lo, hi = span / 8, span * 400
    for _ in range(160):
        R = (lo + hi) / 2
        if R * (1 - math.cos(span / (2 * R))) > rise: lo = R
        else: hi = R
    return (lo + hi) / 2


def ribbon_band(R, rt, rb, half, tail, drop, fork):
    P = lambda r, t: mk.P(R, r, t)
    f = lambda q: f'{F(q[0])} {F(q[1])}'
    rm = (rt + rb) / 2
    tw = tail / rm
    rtT, rbT = rt - drop, rb - drop
    rmT = (rtT + rbT) / 2
    fq = fork / rmT
    A = lambda r, q: f'A{F(r)} {F(r)} 0 0 1 {f(q)}'
    B = lambda r, q: f'A{F(r)} {F(r)} 0 0 0 {f(q)}'
    return ('M' + f(P(rt, -half)) + A(rt, P(rt, half)) +
            'L' + f(P(rtT, half)) + A(rtT, P(rtT, half + tw)) +
            'L' + f(P(rmT, half + tw - fq)) +
            'L' + f(P(rbT, half + tw)) + B(rbT, P(rbT, half)) +
            'L' + f(P(rb, half)) + B(rb, P(rb, -half)) +
            'L' + f(P(rbT, -half)) + B(rbT, P(rbT, -half - tw)) +
            'L' + f(P(rmT, -half - tw + fq)) +
            'L' + f(P(rtT, -half - tw)) + A(rtT, P(rtT, -half)) + 'Z')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir'); ap.add_argument('--face', required=True)
    ap.add_argument('--tagface',
                    default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    o = ap.parse_args()
    os.makedirs(o.outdir, exist_ok=True)
    face, tag = mk.Face(o.face), mk.Face(o.tagface)
    W, T = 'OBERNDÖRFER', 'MADE IN ITALY'
    CAP, TC = 11.0, 3.2
    K = 'fill="none" stroke="#000" stroke-linejoin="round"'
    out = lambda n, p: open(os.path.join(o.outdir, n + '.svg'), 'w').write(mk.svg(p, 5))

    def arcset(f_, txt, cap, tr, r, R, cy=None):
        return mk.arc(f_, txt, cap, tr, r, 0.0, cx=0, cy=R if cy is None else cy)[0]

    adv = face.widths(W, CAP); span = sum(adv)
    # ---- 1  ribbon only ------------------------------------------
    R = radius(span, 5.0)
    rt, rb = R + CAP + 3.4, R - 3.4
    half = (span / 2 + 3.0) / ((rt + rb) / 2)
    d = ribbon_band(R, rt, rb, half, 15.0, 5.2, 3.6)
    t2 = mk.arc(tag, T, TC, 1.3, rb - 4.0 - TC, 0.0, cx=0, cy=R)[0]
    out('1-ribbon-only',
        [f'<path d="{d}" fill="#fff" {K} stroke-width="1.2"/>',
         f'<g fill="#000">{arcset(face, W, CAP, 0, R, R)}</g>',
         f'<g fill="#000">{t2}</g>'])

    # ---- 2  plate only -------------------------------------------
    cfg = dict(mk.DEF, word=W, tag=T, cap=CAP, endgap=4.6, mtop=3.6, mbot=3.2,
               key=1.25, rules=[(1.5, 0.34)], pend=None, tagplace='inside',
               tagcap=TC, tagtrack=1.1, taggap=1.6, rise=5.0)
    out('2-plate-only', mk.compose(face, tag, cfg))

    # ---- 3  plate + ribbon ---------------------------------------
    cfg3 = dict(cfg, pend='ribbon', pdepth=7.0, pwidth=62.0, tagplace='pendant')
    out('3-plate-ribbon', mk.compose(face, tag, cfg3))

    # ---- 4  seal -------------------------------------------------
    Rs = 34.0
    out('4-seal', mk.seal(face, T, W, Rs, 7.2, 0.4, 3.0, 1.2,
                          [1.3, (Rs - 3.0, 0.45)]))

    # ---- 5  shield -----------------------------------------------
    w5, h5 = 62.0, 72.0
    l1, _ = mk.line(face, 'OBERN', 9.0, 0.4, 0, -6.0)
    l2, _ = mk.line(face, 'DÖRFER', 9.0, 0.4, 0, 6.5)
    l3, _ = mk.line(tag, T, 2.8, 1.1, 0, 22.0)
    out('5-shield',
        [f'<path d="{mk.shield(w5, h5)}" fill="#fff" {K} stroke-width="1.3"/>',
         f'<path d="{mk.shield(w5-5.2, h5-5.4)}" {K} stroke-width="0.34"/>',
         f'<g fill="#000">{l1}{l2}{l3}</g>'])

    # ---- 6  wordmark and rules ------------------------------------
    lw, tw_ = mk.line(face, W, CAP, 0.6, 0, 0)
    lt, _ = mk.line(tag, T, 3.0, 2.6, 0, 11.0)
    out('6-rules',
        [f'<g fill="#000">{lw}{lt}</g>',
         f'<path d="M{F(-tw_/2)} -16.5H{F(tw_/2)}" {K} stroke-width="1.1"/>',
         f'<path d="M{F(-tw_/2)} 4.6H{F(tw_/2)}" {K} stroke-width="1.1"/>',
         f'<path d="M{F(-tw_/2)} 6.6H{F(tw_/2)}" {K} stroke-width="0.4"/>'])

    # ---- 7  monogram over the name --------------------------------
    D = 26.0; ro, ri = D/2, D/2 - 0.295*D; rr = 0.21*D/2; xx = 0.34*D/2
    cyd = -ro - 0.20*D
    lw2, _ = mk.line(face, W, 8.4, 0.5, 0, 30.0)
    lt2, _ = mk.line(tag, T, 2.7, 2.2, 0, 39.5)
    out('7-monogram',
        [f'<path fill-rule="evenodd" fill="#000" d="M{F(-ro)} 0'
         f'A{F(ro)} {F(ro)} 0 1 0 {F(ro)} 0A{F(ro)} {F(ro)} 0 1 0 {F(-ro)} 0Z'
         f'M{F(-ri)} 0A{F(ri)} {F(ri)} 0 1 1 {F(ri)} 0'
         f'A{F(ri)} {F(ri)} 0 1 1 {F(-ri)} 0Z"/>',
         f'<g fill="#000"><circle cx="{F(-xx)}" cy="{F(cyd)}" r="{F(rr)}"/>'
         f'<circle cx="{F(xx)}" cy="{F(cyd)}" r="{F(rr)}"/></g>',
         f'<g fill="#000">{lw2}{lt2}</g>'])

    # ---- 8  ribbon across a roundel --------------------------------
    Rc = 33.0
    Rb = radius(span * 0.92, 3.2)
    rt8, rb8 = Rb + 8.6 + 2.6, Rb - 2.6
    half8 = (span * 0.92 / 2 + 2.4) / ((rt8 + rb8) / 2)
    d8 = ribbon_band(Rb, rt8, rb8, half8, 13.0, 4.6, 3.2)
    lt8, _ = mk.line(tag, T, 2.8, 1.6, 0, 22.0)
    out('8-ribbon-roundel',
        [f'<path d="{mk.circle(Rc)}" fill="#fff" {K} stroke-width="1.3"/>',
         f'<path d="{mk.circle(Rc-3.2)}" {K} stroke-width="0.4"/>',
         f'<g fill="#000">{lt8}</g>',
         f'<g transform="translate(0 {F(-Rb+2.0)})">'
         f'<path d="{d8}" fill="#fff" {K} stroke-width="1.2"/>'
         f'<g fill="#000">{arcset(face, W, 8.6, 0, Rb, Rb)}</g></g>'])
    print('8 structures ->', o.outdir)


if __name__ == '__main__':
    main()
