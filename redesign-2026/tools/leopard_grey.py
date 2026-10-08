# leopard_grey.py SRC OUT [--mark] : the owner's leopard print (8 October) turned into dark grey shades for
# the footer: removes the small sparkle mark in the lower right corner, then maps the luminance onto a
# narrow dark-grey range so white writing stays readable on top.
import sys, numpy as np, cv2
im = cv2.imread(sys.argv[1], cv2.IMREAD_COLOR)
h, w = im.shape[:2]
if '--mark' in sys.argv:  # the first print carried a small sparkle mark near (0.875w, 0.885h)
    mask = np.zeros((h, w), np.uint8)
    cx, cy, r = int(w * 0.876), int(h * 0.885), int(w * 0.03)
    roi = cv2.cvtColor(im[cy - r:cy + r, cx - r:cx + r], cv2.COLOR_BGR2GRAY)
    mask[cy - r:cy + r, cx - r:cx + r] = (roi > np.percentile(roi, 80)).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    im = cv2.inpaint(im, mask, 7, cv2.INPAINT_TELEA)
L = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)[..., 0].astype(np.float32)
lo, hi = np.percentile(L, 2), np.percentile(L, 98)
t = np.clip((L - lo) / (hi - lo), 0, 1)
g = 0x1c + t * (0x3e - 0x1c)               # spots ~#1c1c1c, ground ~#3e3e3e
g += np.random.default_rng(2).normal(0, 0.6, g.shape)  # a little grain against banding
out = np.clip(g, 0, 255).astype(np.uint8)
cv2.imwrite(sys.argv[2], cv2.merge([out, out, out]), [cv2.IMWRITE_JPEG_QUALITY, 90])
print(w, h, 'range', lo, hi)
