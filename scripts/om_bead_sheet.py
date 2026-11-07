#!/usr/bin/env python3
"""Compose the twenty rendered designs into one contact sheet."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

SC = '/tmp/claude-0/-home-user-one/9a731093-06fb-50bc-9d28-75940e80fb3f/scratchpad'
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{SC}/om-bead-designs.png'
VIEW = sys.argv[2] if len(sys.argv) > 2 else 'a'

# the viewer's own dark ground, so the sheet reads as one picture
BG = (17, 20, 20)
INK = (231, 233, 230)
MUTE = (140, 150, 147)
ACCENT = (92, 178, 165)

rows = json.load(open(f'{SC}/designs.json'))
COLS, CELL, GAP, CAP = 4, 330, 16, 62
PAD = 26
HEAD = 92
n = len(rows)
R = (n + COLS - 1) // COLS
W = PAD * 2 + COLS * CELL + (COLS - 1) * GAP
H = HEAD + PAD + R * (CELL + CAP) + (R - 1) * GAP


def font(sz, bold=False):
    for p in (('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
               else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def wrap(dr, text, f, width):
    out, line = [], ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if dr.textlength(t, font=f) <= width:
            line = t
        else:
            if line:
                out.append(line)
            line = w
    if line:
        out.append(line)
    return out


TITLE = ('OM Monogram Bead \u2014 twenty designs' if VIEW == 'a'
         else 'OM Monogram Bead \u2014 the same twenty, looking down the hole')
SUB = ('8 mm, sterling silver 925. Each one turns in the viewer; the first is '
       'the brief: four OM round the middle, 925 at the foot, crosses filling '
       'the rest.' if VIEW == 'a' else
       'The polished middle throws a highlight that hides whatever sits there, '
       'so this angle is the one to judge the pattern by.')

sheet = Image.new('RGB', (W, H), BG)
dr = ImageDraw.Draw(sheet)
f_title = font(30, True)
f_name = font(17, True)
f_note = font(13)
f_num = font(13, True)

dr.text((PAD, PAD), TITLE, font=f_title, fill=INK)
dr.text((PAD, PAD + 40), SUB, font=f_note, fill=MUTE)

for i, row in enumerate(rows):
    r, c = divmod(i, COLS)
    x = PAD + c * (CELL + GAP)
    y = HEAD + PAD + r * (CELL + CAP + GAP)
    a = f'{SC}/dz-{i:02d}' + VIEW + '.png'
    if not os.path.exists(a):
        continue
    im = Image.open(a).convert('RGB')
    # crop the toolbar off the top and the hint off the bottom
    im = im.crop((0, 72, im.width, im.height - 46))
    im = im.resize((CELL, int(CELL * im.height / im.width)), Image.LANCZOS)
    box = Image.new('RGB', (CELL, CELL), BG)
    box.paste(im, (0, (CELL - im.height) // 2))
    sheet.paste(box, (x, y))
    dr.text((x, y + CELL + 6), f'{i + 1:02d}', font=f_num, fill=ACCENT)
    dr.text((x + 24, y + CELL + 5), row['name'], font=f_name, fill=INK)
    for j, ln in enumerate(wrap(dr, row['note'], f_note, CELL - 24)[:2]):
        dr.text((x + 24, y + CELL + 25 + j * 15), ln, font=f_note, fill=MUTE)

sheet.save(OUT)
print(OUT, sheet.size)
