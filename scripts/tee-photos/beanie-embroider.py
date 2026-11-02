"""Make the printed OM on the beanie cuff look embroidered (owner, 2 November).

The flat OM is lifted from the photo as a mask, then redrawn as raised satin stitch: diagonal thread
lines, a rounded relief lit from the top left, thread sheen, a darker thread edge and a soft shadow
on the knit around it.
usage: python3 -I beanie-embroider.py IN.jpg OUT.jpg {light|dark}   (light = white OM on dark knit)
"""
import sys, cv2, numpy as np
src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
im = cv2.imread(src).astype(np.float32)
H, W = im.shape[:2]
gray = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)

# 1. the OM: search the cuff band (lower half, middle) for the logo pixels
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
ys, xs = np.where(keep); x0, x1, y0, y1 = xs.min() - 30, xs.max() + 30, ys.min() - 30, ys.max() + 30
a = a * cv2.dilate(keep, np.ones((7, 7), np.uint8))
rng0 = np.random.default_rng(3)
wob = cv2.GaussianBlur(rng0.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.5) * 0.9
soft = cv2.GaussianBlur(a, (0, 0), 1.2)
mask = cv2.GaussianBlur(((soft + 0.18 * wob) > 0.45).astype(np.float32), (0, 0), 0.8)  # slightly uneven stitched edge

# 2. fill the knit under the old print (inpaint) so the thread sits on clean knit
hole = cv2.dilate((a > 0.1).astype(np.uint8), np.ones((9, 9), np.uint8))
base = cv2.inpaint(im.astype(np.uint8), hole, 9, cv2.INPAINT_TELEA).astype(np.float32)

# 3. relief from the distance to the edge of the letters
binm = (mask > 0.5).astype(np.uint8)
d = cv2.distanceTransform(binm, cv2.DIST_L2, 5)
r = 11.0
h = np.sqrt(np.clip(d / r, 0, 1))                     # rounded profile, flat on top
h = cv2.GaussianBlur(h, (0, 0), 1.6)
gy, gx = np.gradient(h)
light = 1.0 + 3.2 * (-gx - gy)                        # lit from the top left
light = np.clip(light, 0.55, 1.45)

# 4. satin stitch: thread lines at 40 degrees, about 7.5 px apart, with a little jitter
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
jit = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 6) * 6
phase = (xx * np.cos(np.radians(40)) + yy * np.sin(np.radians(40)) + jit) / 7.5
thread = 0.5 + 0.5 * np.cos(2 * np.pi * phase)        # 1 on a thread, 0 in the groove
thread = thread ** 0.45
idx = np.floor(phase + 0.5).astype(np.int64)
per = rng.uniform(0.9, 1.06, 4096).astype(np.float32)[idx % 4096]   # each thread a little different
thread = thread * per
sheen = np.clip(thread * light - 0.9, 0, 1) * 0.6     # glossy highlight on the lit side of each thread
fibre = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7) * 0.05
edge = np.clip(1 - d / 2.5, 0, 1) * binm             # thread edge a touch darker

if mode == "light":
    col = np.array([236, 238, 240], np.float32)        # BGR, warm white thread
    shade = (0.62 + 0.38 * thread) * light * (1 - 0.18 * edge) + fibre
    thr = col * shade[..., None] + 255 * sheen[..., None] * 0.35
else:
    col = np.array([38, 36, 34], np.float32)           # near-black thread
    shade = (0.65 + 0.35 * thread) * light * (1 - 0.15 * edge) + fibre
    thr = col * shade[..., None] + 255 * sheen[..., None] * 0.22

# 5. soft shadow of the raised thread on the knit
sh = cv2.GaussianBlur(np.roll(np.roll(mask, 4, 0), 3, 1), (0, 0), 4)
base = base * (1 - 0.35 * sh * (1 - mask))[..., None]

out = base * (1 - mask[..., None]) + thr * mask[..., None]
res = im.copy(); res[y0:y1, x0:x1] = out[y0:y1, x0:x1]
cv2.imwrite(dst, np.clip(res, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
print(dst, "logo box", x0, y0, x1, y1)
