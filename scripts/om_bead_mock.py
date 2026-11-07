#!/usr/bin/env python3
"""Export the bead's marks for the browser mock-up.

The viewer has to place the same five marks the STL does, on the fly,
while someone drags them about. It cannot run the Python, so what it
needs is each mark reduced to the one thing the relief depends on:
distance, in millimetres, from the edge of the ink inwards. That field
is smooth, so it downsamples honestly and the viewer can read a lip of
any width off it - which is what makes the relief slider work in the
browser instead of only here.

Written as JSON next to the page, one byte per pixel, base64.
"""
import base64, json, math, os, sys
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from om_bead import PAGE, PATTERN, stamp_from_pdf, ringed, rings

OUT = 'assets/om-bead/mockup/stamps.json'
MAXDIM = 176          # px on the long side of a stamp
DRANGE = 0.40         # mm of distance the byte covers


def field(mask, long_mm):
    """Distance from the edge of the ink, in mm, downsampled."""
    if mask.shape[1] >= mask.shape[0]:
        w_mm = long_mm
    else:
        w_mm = long_mm * mask.shape[1] / mask.shape[0]
    mm_per_px = w_mm / mask.shape[1]
    d = ndimage.distance_transform_edt(mask) * mm_per_px
    k = max(1, int(round(max(mask.shape) / MAXDIM)))
    h = (mask.shape[0] // k) * k
    w = (mask.shape[1] // k) * k
    d = d[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))
    q = np.clip(d / DRANGE * 255.0, 0, 255).astype(np.uint8)
    return q


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    stamps = []
    for name, box, _, _, mm, share in PATTERN:
        # exactly what the STL uses, so the page shows the part
        m = stamp_from_pdf(PAGE, box=box, px=2200)
        if name == 'circ':
            m = ringed(m)
        q = field(m, mm)
        stamps.append({
            'name': name, 'w': int(q.shape[1]), 'h': int(q.shape[0]),
            'mm': mm, 'share': share,
            'data': base64.b64encode(q.tobytes()).decode('ascii'),
        })
        print(f'   {name:5s} {q.shape[1]:3d} x {q.shape[0]:3d} px   '
              f'{mm:.2f} mm   {len(stamps[-1]["data"])/1024:.1f} KB')
    doc = {
        'drange': DRANGE,
        'stamps': stamps,
        'rings': [{'lon': lo, 'lat': la, 'kind': k, 'mm': mm}
                  for lo, la, k, mm in rings(3.95)],
        'labels': {'om': 'OM monogram', 'sq': 'Cross in a square',
                   'n925': 'Cross and 925', 'circ': 'Cross in a circle',
                   'outl': 'Outlined cross'},
    }
    with open(OUT, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'))
    print(f'{OUT}: {os.path.getsize(OUT)/1024:.0f} KB, '
          f'{len(doc["rings"])} marks in the ring plan')


if __name__ == '__main__':
    main()
