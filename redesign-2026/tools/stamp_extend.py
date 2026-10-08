# stamp_extend.py SRC OUT : put the original brass-stamp photograph (with its own cast shadow and
# grey surface) into a 5:7 portrait frame by extending the backdrop above and the table below,
# instead of cutting the stamp out (owner, 8 October: the cut-out lost the shadow of the original).
import sys, numpy as np, cv2
src = cv2.cvtColor(cv2.imread(sys.argv[1]), cv2.COLOR_BGR2RGB).astype(np.float32)
W, H = 1500, 2100
s = W / src.shape[1]
img = cv2.resize(src, (W, int(src.shape[0] * s)), interpolation=cv2.INTER_LANCZOS4)
ih = img.shape[0]
oy = int(H * 0.56 - 0.50 * ih)             # stamp centre a little below the middle
canvas = np.zeros((H, W, 3), np.float32)
canvas[oy:oy + ih] = img
rng = np.random.default_rng(7)
# above: the smooth backdrop, continued from its top rows (blurred column colours plus the
# vertical trend of the first rows), with a little grain so it does not look painted
band = img[:60].mean(0)
band = cv2.GaussianBlur(band[None], (0, 0), 40)[0]
slope = (img[:30].mean((0, 1)) - img[90:120].mean((0, 1))) / 90.0
for y in range(oy):
    d = oy - y
    canvas[y] = band + slope * min(d, 260) * 0.6
canvas[:oy] += rng.normal(0, 1.1, (oy, W, 1))
# below: the table, mirrored and softened more the further it is from the photo (depth of field)
rest = H - (oy + ih)
if rest > 0:
    # only the bare table below the stamp's base (last ~160 rows), repeated as mirror, copy, mirror ...
    tile = img[ih - 160:]
    reps = []
    k = 0
    while sum(t.shape[0] for t in reps) < rest:
        reps.append(tile[::-1] if k % 2 == 0 else tile)
        k += 1
    mir = np.concatenate(reps)[:rest].copy()
    out = np.empty_like(mir)
    for i in range(0, rest, 8):
        sig = 0.6 + 6.0 * (i / rest)
        blk = cv2.GaussianBlur(mir, (0, 0), sig)
        out[i:i + 8] = blk[i:i + 8]
    canvas[oy + ih:] = out
# feather both seams
def feather(y, r=50):
    lo, hi = max(0, y - r), min(H, y + r)
    seg = canvas[lo:hi].copy()
    canvas[lo:hi] = cv2.GaussianBlur(seg, (0, 0), 0.1 + 0) * 0 + cv2.GaussianBlur(seg, (1, 41), 0)
feather(oy); feather(oy + ih, 24)
cv2.imwrite(sys.argv[2], cv2.cvtColor(np.clip(canvas, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
print('photo rows', oy, oy + ih)
