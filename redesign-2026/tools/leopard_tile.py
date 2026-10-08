# leopard_tile.py GREY_IN OUT [--soft] : (--soft keeps a fur texture: no re-cut into three tones)
# make the grey leopard (from leopard_grey.py) repeat downwards without a
# seam (the footer shows it at full width, so it only repeats vertically). Shift by half a tile vertically, cross-fade the seam band with the unshifted image, then re-cut the blended
# field into the print's own three tones (spot, shadow patch, ground) so blended spots merge into new
# organic shapes instead of showing as half-transparent ghosts.
import sys, numpy as np, cv2
g = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE).astype(np.float32)
g = cv2.GaussianBlur(g, (0, 0), 0.6 if '--soft' in sys.argv else 1.0)
h, w = g.shape
# the print's tones: three clusters
Z = g.reshape(-1, 1)
_, lab, cen = cv2.kmeans(Z, 3, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5), 3, cv2.KMEANS_PP_CENTERS)
c = np.sort(cen.ravel())
t1, t2 = (c[0] + c[1]) / 2, (c[1] + c[2]) / 2
r = np.roll(g, h // 2, 0)
yy, xx = np.mgrid[0:h, 0:w]
b = 110.0
m = (1 - np.abs(yy - h / 2) / b).clip(0, 1)
m = m * m * (3 - 2 * m)
f = r * (1 - m) + g * m
if '--soft' in sys.argv:
    q = f.copy()
else:
    q = np.where(f < t1, c[0], np.where(f < t2, c[1], c[2])).astype(np.float32)
    q = cv2.GaussianBlur(q, (0, 0), 0.9)
q += np.random.default_rng(4).normal(0, 0.6, q.shape)
cv2.imwrite(sys.argv[2], np.clip(q, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
print('tones', c.round(1))
