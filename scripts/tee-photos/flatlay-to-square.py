# Owner's flat-lay photos (light or white background) to the shop format: the garment is keyed off
# the background, scaled to the usual framing (about 80% of a 2400px square, by height for trousers)
# and set on the warm grey ground with the same soft shadow as the other ready-to-wear photos.
# Usage: python3 flatlay-to-square.py IN.jpg OUT.jpg THRESHOLD   (garment pixels have lightness below THRESHOLD)
import sys
import numpy as np, cv2
from PIL import Image
SIZE, FILL_H, MAX_W, TOP = 2400, 1960, 1980, 220
GROUND = np.array([233, 232, 227], np.float32)

src, out, thr = sys.argv[1], sys.argv[2], float(sys.argv[3])
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
m = (img.mean(2) < thr).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
filled = np.zeros_like(m); cv2.drawContours(filled, cs, -1, 1, -1)
# fill only small holes (white embroidery, prints); large light areas inside the outline are background
holes = (filled > 0) & (m == 0)
n, lab, st, _ = cv2.connectedComponentsWithStats(holes.astype(np.uint8))
big = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 1500])
m = (filled > 0) & ~big
m = m.astype(np.uint8)
ys, xs = np.where(m)
x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
crop, mc = img[y0:y1, x0:x1], m[y0:y1, x0:x1].astype(np.float32)
s = min(FILL_H / crop.shape[0], MAX_W / crop.shape[1])
w, h = int(round(crop.shape[1] * s)), int(round(crop.shape[0] * s))
big = cv2.resize(crop, (w, h), interpolation=cv2.INTER_LANCZOS4)
# gentle sharpening after the upscale
blur = cv2.GaussianBlur(big, (0, 0), 1.6)
big = np.clip(big + 0.45 * (big - blur), 0, 255)
mb = cv2.resize(mc, (w, h), interpolation=cv2.INTER_LINEAR)
mb = cv2.erode((mb > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)  # trims the light blended edge of the original
out_img = np.tile(GROUND, (SIZE, SIZE, 1))
X, Y = (SIZE - w) // 2, TOP
cm = np.zeros((SIZE, SIZE), np.float32); cm[Y:Y + h, X:X + w] = mb
ci = out_img.copy(); ci[Y:Y + h, X:X + w] = big
sh = cv2.GaussianBlur(np.roll(cm, 16, axis=0), (0, 0), 22)
out_img = out_img * (1 - 0.13 * sh)[..., None]
a = cv2.GaussianBlur(cm, (0, 0), 0.9)[..., None]
res = out_img * (1 - a) + ci * a
Image.fromarray(res.astype(np.uint8)).save(out, quality=93, optimize=True)
print(out, 'scale', round(s, 2))
