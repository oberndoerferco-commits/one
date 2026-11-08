#!/usr/bin/env python3
"""A flat plan of one face of the bead, drawn the way the reference was.

The reference arrived as a circle with the pattern laid out inside it,
which is the right way to argue about a pattern: a render shows you a
lit sphere, and the highlight eats whatever sits in the middle of it.
This draws the same view from the actual placement data, so the
drawing and the bead can be held side by side.

Orthographic, looking straight at whichever mark faces you. Marks on
the far side are dropped; the rest are foreshortened by the cosine of
their angle off-axis, which is what the eye does.
"""
import argparse, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from om_bead import (PAGE, PATTERN, LAYOUTS, stamp_from_pdf, ringed,
                     ink_radius, layout, gaps)


def font(sz, bold=False):
    for p in (('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
               else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def face(places, stamps, radius, size=900, pad=46, lon0=0.0, lat0=0.0):
    img = Image.new('RGB', (size, size), 'white')
    dr = ImageDraw.Draw(img)
    cx = cy = size / 2.0
    rr = size / 2.0 - pad
    dr.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=(0, 0, 0), width=3)

    la0, lo0 = math.radians(lat0), math.radians(lon0)
    # the frame of the face we are looking at: out of the screen, right, up
    out = (math.cos(la0)*math.cos(lo0), math.cos(la0)*math.sin(lo0), math.sin(la0))
    rgt = (-math.sin(lo0), math.cos(lo0), 0.0)
    up = (out[1]*rgt[2]-out[2]*rgt[1], out[2]*rgt[0]-out[0]*rgt[2],
          out[0]*rgt[1]-out[1]*rgt[0])

    # far side first, so the near marks sit on top
    order = []
    for lon, lat, k, mm in places:
        la, lo = math.radians(lat), math.radians(lon)
        v = (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))
        z = sum(a*b for a, b in zip(v, out))
        order.append((z, lon, lat, k, mm, v))
    order.sort(key=lambda t: t[0])

    for z, lon, lat, k, mm, v in order:
        if z < -0.001:           # the far side
            continue
        x = sum(a*b for a, b in zip(v, rgt))
        y = sum(a*b for a, b in zip(v, up))
        st = stamps[k]
        h, w = st.shape
        if w >= h:
            wmm, hmm = mm, mm*h/w
        else:
            hmm, wmm = mm, mm*w/h
        # foreshortened, but floored so a mark right on the silhouette -
        # the 925 at the foot, for one - still shows rather than
        # vanishing to a line
        f_ = max(z, 0.11)**0.45
        pw = max(4, int(round(wmm/radius*rr*f_)))
        ph = max(4, int(round(hmm/radius*rr*f_)))
        tile = Image.fromarray((~st*255).astype(np.uint8)).convert('L')
        tile = tile.resize((pw, ph), Image.LANCZOS)
        px = int(round(cx + x*rr))
        py = int(round(cy - y*rr))
        img.paste(Image.new('RGB', (pw, ph), (0, 0, 0)),
                  (px-pw//2, py-ph//2), Image.eval(tile, lambda v: 255-v))
    return img


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--layout', default='Monogram Grid')
    a.add_argument('--dia', type=float, default=8.0)
    a.add_argument('--relief', type=float, default=0.10)
    a.add_argument('--cut', action='store_true',
                   help='engraved: the ball is the full diameter')
    a.add_argument('--out', default='assets/om-bead/renders/om-bead-plan.png')
    a.add_argument('--all', action='store_true',
                   help='one plan per design, as a sheet')
    o = a.parse_args()

    stamps = [ringed(stamp_from_pdf(PAGE, box=b, px=2200)) if nm == 'circ'
              else stamp_from_pdf(PAGE, box=b, px=2200) for nm, b, *_ in PATTERN]
    radii = [ink_radius(st, q[4]) for st, q in zip(stamps, PATTERN)]
    r = o.dia/2.0 if o.cut else (o.dia - 2*o.relief) / 2.0
    os.makedirs(os.path.dirname(o.out), exist_ok=True)

    names = [d['name'] for d in LAYOUTS] if o.all else [o.layout]
    tiles = []
    for nm in names:
        pl = layout(nm, r)
        g = gaps(pl, r, radii)
        worst = g[0][0] if g else 0.0
        tiles.append((nm, face(pl, stamps, r, size=820), len(pl), worst))
        print(f'{nm:32s} {len(pl):3d} marks, tightest pair {worst:+.2f} mm')

    if not o.all:
        tiles[0][1].save(o.out)
        print(o.out)
        return

    COLS, CELL, GAP, CAP, PAD, HEAD = 4, 330, 18, 56, 26, 92
    rows = (len(tiles)+COLS-1)//COLS
    W = PAD*2 + COLS*CELL + (COLS-1)*GAP
    H = HEAD + PAD + rows*(CELL+CAP) + (rows-1)*GAP
    sheet = Image.new('RGB', (W, H), 'white')
    dr = ImageDraw.Draw(sheet)
    dr.text((PAD, PAD), 'OM Monogram Bead — the lattice, drawn flat',
            font=font(30, True), fill=(20, 20, 20))
    dr.text((PAD, PAD+40), 'One face of each design, laid out the way the '
            'reference was. Every pair of marks is clear of every other; the '
            'figure under each is the tightest gap on the ball.',
            font=font(13), fill=(120, 120, 120))
    for i, (nm, im, cnt, worst) in enumerate(tiles):
        rw, cl = divmod(i, COLS)
        x = PAD + cl*(CELL+GAP)
        y = HEAD + PAD + rw*(CELL+CAP+GAP)
        sheet.paste(im.resize((CELL, CELL), Image.LANCZOS), (x, y))
        dr.text((x, y+CELL+6), f'{i+1:02d}', font=font(13, True), fill=(0, 140, 125))
        dr.text((x+24, y+CELL+5), nm, font=font(16, True), fill=(20, 20, 20))
        dr.text((x+24, y+CELL+26), f'{cnt} marks, {worst:+.2f} mm clear',
                font=font(13), fill=(120, 120, 120))
    sheet.save(o.out)
    print(o.out, sheet.size)


if __name__ == '__main__':
    main()
