"""Split motifs-reference.pdf (three motifs, grey/black vector art) into
motifs/roundel.svg, motifs/halo.svg and motifs/tile.svg.

    python3 -I design/monogram-canvas/extract_motifs.py

The PDF is a single page of plain fill operators (rg, m, l, c, h, f*), so it
is parsed directly. Colours become classes so each colourway can recolour:
  grey 0.549 -> .lt (light)   grey 0.078 -> .dk (dark fill)   black -> .ln (edge)
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'motifs-reference.pdf'), 'rb').read()
stream = re.search(rb'stream\r?\n(.*?)endstream', raw, re.S).group(1).decode('latin1')

H = 512.0  # page height (MediaBox 0 0 512 512); flip y for SVG
paths, st, d, col, pts = [], [], '', 'ln', []
for t in stream.split():
    if re.fullmatch(r'-?[\d.]+', t):
        st.append(float(t))
        continue
    if t == 'rg':
        grey = st[-1]  # the motifs are pure greys
        col = 'lt' if grey > 0.3 else ('dk' if grey > 0.02 else 'ln')
    elif t in ('m', 'l'):
        x, y = st[-2], H - st[-1]
        d += f'{t.upper()}{x:.2f} {y:.2f} '
        pts.append((x, y))
    elif t == 'c':
        a = st[-6:]
        d += 'C' + ' '.join(f'{a[i]:.2f} {H - a[i + 1]:.2f}' for i in (0, 2, 4)) + ' '
        pts.append((a[4], H - a[5]))
    elif t == 'h':
        d += 'Z '
    elif t in ('f', 'f*'):
        paths.append((col, d.strip(), pts))
        d, pts = '', []
    st = []

# group by position on the page: roundel (top-left), halo (top-right), tile (bottom-right)
groups = {'roundel': [], 'halo': [], 'tile': []}
for cls, d, pts in paths:
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    key = 'tile' if cy > 255 else ('roundel' if cx < 250 else 'halo')
    groups[key].append((cls, d, pts))

os.makedirs(os.path.join(HERE, 'motifs'), exist_ok=True)
for key, items in groups.items():
    xs = [p[0] for _, _, pts in items for p in pts]
    ys = [p[1] for _, _, pts in items for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    body = ''.join(f'<path class="{c}" fill-rule="evenodd" d="{d}"/>' for c, d, _ in items)
    with open(os.path.join(HERE, 'motifs', f'{key}.svg'), 'w') as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f}">'
                 f'<style>.lt{{fill:#8b8b8b}}.dk{{fill:#131313}}.ln{{fill:#000}}</style>{body}</svg>\n')
    print(key, len(items), 'paths', round(x1 - x0), 'x', round(y1 - y0))
