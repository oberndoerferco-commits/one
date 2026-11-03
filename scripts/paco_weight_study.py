#!/usr/bin/env python3
"""Why bolding will not fix the PA & CO hairlines, and what does.

The logo is set in Bodoni Moda (the ampersand settles it: Playfair and
Prata both draw a curly one, Bodoni's is the open slanted form with the
straight leg). Bodoni Moda is a variable font with two axes, Weight and
Optical size, and they do very different things here.

Measured at the logo's own cap height of 12 mm:

    wght 400 -> 900 at opsz 6 : hairline 0.50 -> 0.52, stem 1.76 -> 3.60
    opsz 72 -> 6 at wght 400  : hairline 0.04 -> 0.50, stem unchanged

Bolding a Didone thickens the stems and leaves the hairlines alone - that
is the defining property of the style, so contrast gets worse with weight,
not better. The optical size axis is the one that matters: a cut drawn for
6 pt carries sturdy hairlines by design, and at the logo's cap height it
doubles them over the original without moving the stems.

Needs the font: curl -sSL -o BodoniModa.ttf \\
  https://raw.githubusercontent.com/google/fonts/main/ofl/bodonimoda/BodoniModa%5Bopsz,wght%5D.ttf
"""
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import medial_axis

CAP_MM, PPMM = 12.0, 45


def stats(font, wght, opsz, txt='PA & CO'):
    f = ImageFont.truetype(font, 900)
    f.set_variation_by_axes([wght, opsz])
    t = Image.new('L', (11000, 2600), 255)
    ImageDraw.Draw(t).text((80, 200), txt, font=f, fill=0)
    a = np.asarray(t) < 128
    ys, xs = np.nonzero(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = (CAP_MM * PPMM) / a.shape[0]
    b = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize(
        (max(1, int(a.shape[1] * k)), int(a.shape[0] * k)), Image.LANCZOS)) > 128
    lab, _ = ndimage.label(b)
    hair, stem = [], []
    for i, s in enumerate(ndimage.find_objects(lab)):
        comp = lab[s] == i + 1
        if comp.sum() < 150:
            continue
        skel, dist = medial_axis(comp, return_distance=True)
        w = 2.0 * dist[skel] / PPMM
        w = w[w > 0.04]
        if len(w):
            hair.append(np.percentile(w, 10))
            stem.append(np.percentile(w, 90))
    return min(hair), max(stem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', required=True)
    a = ap.parse_args()
    print(f'cap height {CAP_MM:g} mm   (original: hairline 0.25, stem 1.70)')
    print(f'{"wght":>5} {"opsz":>5} {"hairline":>9} {"stem":>7} {"contrast":>9}')
    for opsz in (6, 8, 11, 16, 72):
        for wght in (400, 600, 900):
            h, s = stats(a.font, wght, opsz)
            print(f'{wght:>5} {opsz:>5} {h:9.2f} {s:7.2f} {s/h:8.1f}:1')


if __name__ == '__main__':
    main()
