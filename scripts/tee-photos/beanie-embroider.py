"""Make the printed OM on the beanie cuff look embroidered (owner, 2 November; v2, more realistic).

The flat OM is lifted from the photo as a mask, the knit under it is filled in, and the letters are
redrawn as raised satin stitch:
- stitches run across each stroke and turn with it (orientation from the structure tensor of the mask),
- the threads are drawn as streaks of fibre along that direction (line integral convolution of noise),
  so there is no repeating pattern to beat against the turning direction,
- the letters are domed and lit from the top left, with a darker thread edge and a slightly uneven outline,
- the knit dips into a thin dark seam around the letters and takes a soft shadow,
- the thread is softened and given grain to match the photo.
usage: python3 beanie-embroider.py IN.jpg OUT.jpg {light|dark}   (light = white OM on dark knit)
"""
import sys, cv2, numpy as np
src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
im = cv2.imread(src).astype(np.float32)
H, W = im.shape[:2]
gray = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
rng = np.random.default_rng(7)

# 1. the OM in the cuff band
band = np.zeros((H, W), bool); band[int(H * .5):int(H * .82), int(W * .2):int(W * .8)] = True
if mode == "light":
    a = np.clip((gray - 60) / (200 - 60), 0, 1)
else:
    knit = np.median(gray[band])
    a = np.clip((knit - 25 - gray) / (knit - 25 - 30), 0, 1)
a = a * band
core = (a > 0.5).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(core)
keep = np.zeros_like(core)
for k in range(1, n):
    if st[k, cv2.CC_STAT_AREA] > 400: keep[lab == k] = 1
ys, xs = np.where(keep); x0, x1, y0, y1 = xs.min() - 40, xs.max() + 40, ys.min() - 40, ys.max() + 40
a = a * cv2.dilate(keep, np.ones((7, 7), np.uint8))

sl = (slice(y0, y1), slice(x0, x1))
A = a[sl]; I = im[sl].copy(); h, w = A.shape
wob = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.4)
mask = cv2.GaussianBlur(((cv2.GaussianBlur(A, (0, 0), 1.2) + 0.2 * wob) > 0.45).astype(np.float32), (0, 0), 0.7)
binm = (mask > 0.5).astype(np.uint8)

# 2. clean knit under the old print
hole = cv2.dilate((A > 0.08).astype(np.uint8), np.ones((11, 11), np.uint8))
base = cv2.inpaint(I.astype(np.uint8), hole, 11, cv2.INPAINT_TELEA).astype(np.float32)

# 3. stitch direction: across the stroke, smoothed as a doubled angle; a 130-degree fill where weak
ms = cv2.GaussianBlur(binm.astype(np.float32), (0, 0), 3)
gx = cv2.Sobel(ms, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(ms, cv2.CV_32F, 0, 1, ksize=5)
jxx = cv2.GaussianBlur(gx * gx, (0, 0), 7); jyy = cv2.GaussianBlur(gy * gy, (0, 0), 7); jxy = cv2.GaussianBlur(gx * gy, (0, 0), 7)
phi = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-6)
fill = np.radians(130)
c2 = coh * np.cos(2 * phi) + (1 - coh) * np.cos(2 * fill)
s2 = coh * np.sin(2 * phi) + (1 - coh) * np.sin(2 * fill)
phi = 0.5 * np.arctan2(s2, c2)

# threads: noise smeared along the thread direction (line integral convolution)
cx, cy = np.cos(phi).astype(np.float32), np.sin(phi).astype(np.float32)
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
noise = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.3)
acc = noise.copy(); L = 9
for sgn in (1, -1):
    px, py = xx.copy(), yy.copy()
    for k in range(L):
        dx = cv2.remap(cx, px, py, cv2.INTER_LINEAR); dy = cv2.remap(cy, px, py, cv2.INTER_LINEAR)
        px += sgn * 1.5 * dx; py += sgn * 1.5 * dy
        acc += cv2.remap(noise, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
lic = acc / (2 * L + 1)
lic = (lic - lic[binm > 0].mean()) / (lic[binm > 0].std() + 1e-6)
thread = np.clip(0.5 + 0.28 * lic, 0, 1)
fine = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.5)
per = 1.0 + 0.03 * fine
twist = 0.5 + 0.5 * np.tanh(lic)

# 4. dome relief and light
d = cv2.distanceTransform(binm, cv2.DIST_L2, 5)
r = 10.0
hgt = cv2.GaussianBlur(np.sqrt(np.clip(d / r, 0, 1)), (0, 0), 1.5)
hy, hx = np.gradient(hgt)
light = np.clip(1.0 + 3.0 * (-hx - hy), 0.55, 1.4)
edge = np.clip(1 - d / 2.5, 0, 1) * binm
fibre = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.6) * 0.06

if mode == "light":
    col = np.array([232, 236, 239], np.float32)   # BGR warm white
    tone = (0.58 + 0.42 * thread) * per * (0.94 + 0.06 * twist) * light * (1 - 0.2 * edge) + fibre
    sheen = np.clip(thread * light - 1.0, 0, 1) * 0.5
    thr = col * tone[..., None] + 255 * sheen[..., None] * 0.3
else:
    col = np.array([40, 38, 36], np.float32)
    tone = (0.6 + 0.4 * thread) * per * (0.9 + 0.1 * twist) * light * (1 - 0.15 * edge) + fibre
    sheen = np.clip(thread * light - 0.95, 0, 1) * 0.6
    thr = col * tone[..., None] + 255 * sheen[..., None] * 0.22

# 5. knit around the letters: thin dark seam and a soft shadow
ring = cv2.GaussianBlur(cv2.dilate(binm, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2) * (1 - mask)
sh = cv2.GaussianBlur(np.roll(np.roll(mask, 5, 0), 4, 1), (0, 0), 5) * (1 - mask)
base = base * (1 - 0.35 * ring - 0.3 * sh)[..., None]

# 6. match the photo: soften the thread slightly and add grain
thr = cv2.GaussianBlur(thr, (0, 0), 0.6) + rng.normal(0, 2.0, thr.shape).astype(np.float32)
out = base * (1 - mask[..., None]) + thr * mask[..., None]
res = im.copy(); res[sl] = out
cv2.imwrite(dst, np.clip(res, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
print(dst, "logo box", x0, y0, x1, y1)
