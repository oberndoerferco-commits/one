#!/usr/bin/env python3
"""Compose the shot bead into one sheet.

The frames come from bead_shoot.js, which renders the STL itself rather
than the placement, so this sheet is a photograph of the file a caster
would receive. Nothing here retouches them: it crops, scales and labels.

  python3 scripts/studio/bead_silver_sheet.py <frame-dir> <tag> <out.png>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BG = (10, 10, 12)
INK = (238, 238, 240)
DIM = (150, 152, 158)

TILES = [
    ('front', 'Straight on'),
    ('top', 'Down the hole'),
    ('under', 'From beneath'),
    ('macro', 'Ten times life size'),
    ('circle', 'The circled cross, standing in its field'),
    ('smallom', 'A cross on a diagonal'),
]

TITLE = 'OM Monogram Bead — {dia} mm, sterling silver 925, engraved'
SUB = ('Rendered from the STL itself, not from the layout. Four big OM at '
       '{om} mm round the middle, bare crosses on the diagonals, the '
       'circled cross left standing while the ground round it is cut away.')


def font(sz, bold=False):
    base = '/usr/share/fonts/truetype/dejavu/'
    for p in (base + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
              base + 'DejaVuSans.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def fit(path, w, h):
    """Centre-crop to the box, then scale. The renders are square."""
    im = Image.open(path).convert('RGB')
    want = w / h
    have = im.width / im.height
    if have > want:                      # too wide: trim the sides
        nw = int(round(im.height * want))
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:                                # too tall: trim top and bottom
        nh = int(round(im.width / want))
        y = (im.height - nh) // 2
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((w, h), Image.LANCZOS)


def main():
    src, tag, out = sys.argv[1], sys.argv[2], sys.argv[3]
    dia = sys.argv[4] if len(sys.argv) > 4 else '8'
    om = sys.argv[5] if len(sys.argv) > 5 else '3.51'
    pad, gap, cap = 18, 14, 24
    col = 240                                   # a small tile
    right = 2 * col + gap
    rows = (len(TILES) + 1) // 2
    body = rows * col + (rows - 1) * (cap + gap) + cap
    hero = body
    W = pad + hero + gap + right + pad
    head = 86
    H = head + body + cap + pad

    sheet = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), TITLE.format(dia=dia), INK, font=font(23, True))
    d.text((pad, 50), SUB.format(om=om), DIM, font=font(12))

    sheet.paste(fit(f'{src}/{tag}-hero.png', hero, body), (pad, head))
    d.text((pad, head + body + 6), 'The piece', INK, font=font(13, True))

    x0 = pad + hero + gap
    for i, (name, label) in enumerate(TILES):
        x = x0 + (i % 2) * (col + gap)
        y = head + (i // 2) * (col + cap + gap)
        sheet.paste(fit(f'{src}/{tag}-{name}.png', col, col), (x, y))
        d.text((x, y + col + 5), label, DIM, font=font(11))

    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    sheet.save(out)
    print(f'{out}: {W} x {H}')


if __name__ == '__main__':
    main()
