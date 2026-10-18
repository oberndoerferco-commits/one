"""Trace the OM monogram (om-reference.png) into a clean vector path.

    python3 design/monogram-canvas/trace_om.py

Writes motifs/om.svg (black fill, even-odd) using potrace (pip: potracer).
"""
import os
import cv2
import numpy as np
import potrace

HERE = os.path.dirname(os.path.abspath(__file__))
img = cv2.imread(os.path.join(HERE, 'om-reference.png'), cv2.IMREAD_GRAYSCALE)
# the letters are black with a thin grey rim; upsample for smoother curves
img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
img = cv2.GaussianBlur(img, (0, 0), 2)
mask = img < 160
ys, xs = np.nonzero(mask)
x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
mask = np.pad(mask[y0:y1 + 1, x0:x1 + 1], 8)  # clear margin so no edge contour

bmp = potrace.Bitmap(mask)
plist = bmp.trace(turdsize=40, alphamax=1.0, opticurve=True, opttolerance=0.2)
k = 0.25  # back to source pixels
parts = []
H, W = mask.shape
for curve in plist:
    # potracer also returns the bitmap's own border as a contour; skip it
    if abs(curve.start_point.x) < 1 or abs(curve.start_point.y) < 1:
        continue
    s = curve.start_point
    d = f'M{s.x * k:.2f} {s.y * k:.2f}'
    for seg in curve.segments:
        if seg.is_corner:
            d += f' L{seg.c.x * k:.2f} {seg.c.y * k:.2f} L{seg.end_point.x * k:.2f} {seg.end_point.y * k:.2f}'
        else:
            d += (f' C{seg.c1.x * k:.2f} {seg.c1.y * k:.2f} {seg.c2.x * k:.2f} {seg.c2.y * k:.2f}'
                  f' {seg.end_point.x * k:.2f} {seg.end_point.y * k:.2f}')
    parts.append(d + ' Z')
w, h = mask.shape[1] * k, mask.shape[0] * k  # includes the 2-px margin
os.makedirs(os.path.join(HERE, 'motifs'), exist_ok=True)
with open(os.path.join(HERE, 'motifs', 'om.svg'), 'w') as fh:
    fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}">'
             f'<path fill="#000" fill-rule="evenodd" d="{" ".join(parts)}"/></svg>\n')
print('om.svg', round(w), 'x', round(h), len(parts), 'contours')
