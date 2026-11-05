#!/usr/bin/env python3
"""Build one supplier pack from the brief, with the TRAXNYC marks taken out.

The brief arrived as three A4 pages - the piece photographed, the brand
marks, the storefront that lines the lid - and the artwork arrived
separately as the opened-out net. This puts what survives into a single
PDF and removes the marks wherever they appear:

  * the foil crest and wordmark on the lid of the closed box
  * the foil lockup inside the open lid, and the shop sign on the
    storefront card behind it
  * the wordmark over the drawer, and the 'x' that joined it to
    OBERNDOERFER MILANO, which stays
  * the sign on the storefront artwork itself

The brand-marks page goes entirely: with the marks gone there is nothing
left on it to print.

Needs opencv-python-headless. --src is the brief as it was sent; the
default points at where it landed in this session, so pass the path if
you have it somewhere else. The cleaned plates are written out beside
the pack, which is what lets it be rebuilt without the branded original.

Photographs are repaired in retouch.py; see there for why the grain is
rebuilt rather than copied. The vector overlays are a different problem
and are handled here: the wordmark over the drawer is its own image, so
it is deleted outright, and the 'x' is live text, so a redaction removes
it without disturbing the photograph underneath.
"""
import argparse
import os
import sys

import cv2
import numpy as np
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retouch import face_band, grain_of, patch_over, regrain, strip, strip_dark

HERE = os.path.dirname(os.path.abspath(__file__))
UPLOAD = ('/root/.claude/uploads/9a731093-06fb-50bc-9d28-75940e80fb3f/'
          '3bde4325-box_design_2.pdf')

# Each plate is keyed by the pixel size of the image it replaces, which is
# how it is found again once the page has been copied into the new file
# and every xref has changed.
SHUT = (829, 639)          # the closed box, foil crest and wordmark on the lid
OPEN = (1099, 778)         # the open box, foil lockup inside the lid
WORD = (216, 34)           # the wordmark laid over the drawer
SHOP = (1365, 491)         # the storefront that lines the lid


def plate_shut(im):
    """Lid of the closed box: crest and wordmark, gold on black leather.

    The mask is held inside the lid's top face so that dilating it cannot
    reach the piping along the front edge, which runs within 30 px of the
    wordmark and smears the moment it is included.
    """
    face = face_band(im.shape, [(250, 195), (660, 70), (660, 235), (250, 380)])
    out, _ = strip(im, face, clean=(160, 250, 300, 340))
    return out


def plate_open(im):
    """Open box: the lockup on the suede, and the sign on the shop card.

    Two passes, because the two marks are opposite in tone - the lockup is
    gold on grey suede, the shop sign is dark grey on a lit fascia - and a
    single detector would have to be loose enough to catch both, which on
    this image means catching the window frames as well.
    """
    lid = face_band(im.shape, [(398, 52), (795, 110), (795, 208), (398, 155)])
    out, _ = strip(im, lid, clean=(745, 120, 790, 195), reach=31)
    sign = face_band(im.shape, [(548, 165), (628, 177), (628, 197), (548, 185)])
    out, _ = strip_dark(out, sign)
    return out


def plate_shop(im):
    """The shop sign on the storefront artwork.

    Not inpainted. The letters are tall, lit and close above a gilt
    frame, and inpainting pulls that gold up into the stone. The facade
    is an even band the full width of the image, so a clean stretch of it
    is moved across instead and relit to match.
    """
    return patch_over(im, (512, 0, 838, 92), dx=332)


def build(src_path, art_path, out_path, plate_dir):
    src = pymupdf.open(src_path)
    art = pymupdf.open(art_path)
    doc = pymupdf.open()
    doc.insert_pdf(src, from_page=0, to_page=0)      # the piece, photographed
    doc.insert_pdf(art, from_page=0, to_page=0)      # artwork and finish, 1:1
    doc.insert_pdf(src, from_page=2, to_page=2)      # the storefront, lid lining
    # page 1 of the brief, the brand marks, is left out on purpose

    os.makedirs(plate_dir, exist_ok=True)
    work = {SHUT: plate_shut, OPEN: plate_open, SHOP: plate_shop}
    done = []
    for pno in (0, 2):
        pg = doc[pno]
        for xref, smask, *_ in pg.get_images(full=True):
            info = doc.extract_image(xref)
            key = (info['width'], info['height'])
            if key == WORD:
                pg.delete_image(xref)
                done.append('wordmark over the drawer: deleted')
                continue
            if key not in work:
                continue
            raw = os.path.join(plate_dir, 'src-%dx%d.png' % key)
            open(raw, 'wb').write(info['image'])
            out = work[key](cv2.imread(raw))
            # PNG only where there is a soft mask to carry; everything
            # else goes back as JPEG, as it arrived. Writing all four
            # plates lossless triples the size of the pack for nothing.
            if smask:
                # The cut-out shot carries its background in a soft mask.
                # Replacing the image alone drops it and the shot comes
                # back on solid black, so the mask is carried over as an
                # alpha channel and written back with the plate.
                open(raw, 'wb').write(doc.extract_image(smask)['image'])
                out = np.dstack([out, cv2.imread(raw, cv2.IMREAD_GRAYSCALE)])
                new = os.path.join(plate_dir, 'clean-%dx%d.png' % key)
                cv2.imwrite(new, out)
            else:
                new = os.path.join(plate_dir, 'clean-%dx%d.jpg' % key)
                cv2.imwrite(new, out, [cv2.IMWRITE_JPEG_QUALITY, 94])
            os.remove(raw)
            pg.replace_image(xref, filename=new)
            done.append('%dx%d: mark removed%s' % (key[0], key[1],
                        ', soft mask kept' if smask else ''))

    # The 'x' of 'TRAXNYC x OBERNDOERFER MILANO' is live text, not image.
    # fill=False leaves the photograph under it alone; images=NONE keeps
    # the redaction from touching the photograph at all.
    pg = doc[0]
    for b in pg.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for sp in line['spans']:
                if sp['text'].strip().lower() == 'x':
                    pg.add_redact_annot(pymupdf.Rect(sp['bbox']) + (-1, -1, 1, 1),
                                        fill=False)
                    done.append("the 'x' before OBERNDOERFER: redacted")
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)

    doc.save(out_path, garbage=4, deflate=True)
    return doc, done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=UPLOAD,
                    help='the three-page brief, as sent')
    ap.add_argument('--art', default='assets/traxnyc-box/box-artwork.pdf')
    ap.add_argument('--out', default='assets/traxnyc-box/box-pack.pdf')
    ap.add_argument('--plates', default='assets/traxnyc-box/plates')
    a = ap.parse_args()
    doc, done = build(a.src, a.art, a.out, a.plates)
    for d in done:
        print(' ', d)
    print('%s  %d pages' % (a.out, doc.page_count))
    for i, p in enumerate(doc):
        print('  %d  %.0f x %.0f mm' % (i + 1, p.rect.width / 72 * 25.4,
                                        p.rect.height / 72 * 25.4))


if __name__ == '__main__':
    main()
