"""Monogram canvas: an all-over repeat in the manner of a classic monogram
canvas, built only from Oberndörfer marks:

  OM       the blackletter monogram          (motifs/om.svg, traced)
  roundel  star-cross in a disc              (motifs/roundel.svg, from the PDF)
  halo     star-cross with an outline ring   (motifs/halo.svg, from the PDF)
  tile     star-cross on a square            (motifs/tile.svg, from the PDF)

    python3 -I design/monogram-canvas/trace_om.py        # once, needs potracer
    python3 -I design/monogram-canvas/extract_motifs.py  # once
    python3 -I design/monogram-canvas/generate.py

Layout (from the owner's sketch): every OM is the centre of a rosette.
Motifs sit on a square grid of spacing A; one repeat is 2A x 2A:

    OM       at (0, 0)            the centre of each rosette
    square   at (A, 0), (0, A)    above, below and either side of the OM
    disc     at (A, A)            the corners of the rosette
    outline  at (A/2, A/2) etc.   four close around every OM (and every disc)

Writes canvas-<colourway>-tile.svg (one repeat, true size in mm).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
A = 36.0            # mm grid spacing
T = 2 * A           # repeat
SIZE = {            # motif width in mm
    'om': 21.0,
    'roundel': 15.0,
    'halo': 15.0,
    'tile': 12.5,
}
LAYOUT = [
    ('om', 0, 0),
    ('tile', A, 0), ('tile', 0, A),
    ('roundel', A, A),
    ('halo', A / 2, A / 2), ('halo', 3 * A / 2, A / 2),
    ('halo', A / 2, 3 * A / 2), ('halo', 3 * A / 2, 3 * A / 2),
]
# ground, light (main motif colour), dark (fills inside motifs), edge
COLOURWAYS = {
    'graphite': ('#101010', '#8b8b8b', '#1e1e1e', '#000000'),
    'denim': ('#232b39', '#a9b2bf', '#2d3647', '#1a2029'),
    'cognac': ('#5a3a25', '#c9a46b', '#6b4630', '#3e2717'),
    'ivory': ('#f1ece3', '#1b1b1b', '#e1d9cb', '#1b1b1b'),
}


def load(name):
    s = open(os.path.join(HERE, 'motifs', f'{name}.svg')).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    body = re.sub(r'<style>.*?</style>', '', s[s.index('>') + 1:s.rindex('</svg>')], flags=re.S)
    if name == 'om':
        body = body.replace('fill="#000"', 'class="lt"')
    return vb, body


MOTIFS = {k: load(k) for k in SIZE}


def symbols():
    out = []
    for k, (vb, body) in MOTIFS.items():
        out.append(f'<symbol id="{k}" viewBox="{" ".join(f"{v:.2f}" for v in vb)}">{body}</symbol>')
    return ''.join(out)


def uses():
    out = []
    for k, x, y in LAYOUT:
        vb = MOTIFS[k][0]
        w = SIZE[k]
        h = w * vb[3] / vb[2]
        for dx in (-T, 0, T):
            for dy in (-T, 0, T):
                X, Y = x + dx, y + dy
                if -T / 2 <= X <= 1.5 * T and -T / 2 <= Y <= 1.5 * T:
                    out.append(f'<use href="#{k}" x="{X - w / 2:.3f}" y="{Y - h / 2:.3f}" width="{w:.3f}" height="{h:.3f}"/>')
    return ''.join(out)


def tile_svg(cw):
    g, lt, dk, ln = COLOURWAYS[cw]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{T:g}mm" height="{T:g}mm" viewBox="0 0 {T:g} {T:g}">'
            f'<style>.lt{{fill:{lt}}}.dk{{fill:{dk}}}.ln{{fill:{ln}}}</style>'
            f'<defs>{symbols()}<clipPath id="c"><rect width="{T:g}" height="{T:g}"/></clipPath></defs>'
            f'<rect width="{T:g}" height="{T:g}" fill="{g}"/>'
            f'<g clip-path="url(#c)">{uses()}</g></svg>\n')


if __name__ == '__main__':
    for cw in COLOURWAYS:
        with open(os.path.join(HERE, f'canvas-{cw}-tile.svg'), 'w') as fh:
            fh.write(tile_svg(cw))
    print('wrote', ', '.join(f'canvas-{c}-tile.svg' for c in COLOURWAYS), f'(repeat {T:g} mm)')
