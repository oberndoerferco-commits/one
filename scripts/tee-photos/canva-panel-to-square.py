# Product photos from a Canva page that holds two photo panels (front left, back right) on a white
# page: each panel already has the site's warm grey ground, so the garment is cropped out of it,
# scaled to the framing of the other jackets (about 80% of a 2400px square) and pasted, feathered,
# onto the ground colour. Usage: python3 canva-panel-to-square.py PAGE.png OUT_FRONT.jpg OUT_BACK.jpg
import sys
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
SIZE, FILL_H, MAX_W = 2400, 1925, 1980
GROUND = np.array([233, 232, 227], np.float32)

page = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
nonwhite = page.mean(2) < 252
cols = np.where(nonwhite.any(0))[0]
runs, start = [], cols[0]
for a, b in zip(cols[:-1], cols[1:]):
    if b - a > 50: runs.append((start, a)); start = b
runs.append((start, cols[-1]))
for (x0, x1), out in zip(runs, sys.argv[2:4]):
    ys = np.where(nonwhite[:, x0:x1].any(1))[0]
    panel = page[ys.min() + 8:ys.max() - 8, x0 + 8:x1 - 8]
    ground = np.median(np.concatenate([panel[:40].reshape(-1, 3), panel[-40:].reshape(-1, 3)]), 0)
    diff = np.abs(panel - ground).sum(2) > 30
    diff = cv2.morphologyEx(diff.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    gy, gx = np.where(diff)
    gx0, gx1, gy0, gy1 = gx.min(), gx.max(), gy.min(), gy.max()
    s = min(FILL_H / (gy1 - gy0), MAX_W / (gx1 - gx0))
    small = cv2.resize(panel, (int(panel.shape[1] * s), int(panel.shape[0] * s)), interpolation=cv2.INTER_AREA)
    small = small - ground + GROUND          # match the panel's ground to the site's exactly
    cx, cy = (gx0 + gx1) / 2 * s, (gy0 + gy1) / 2 * s
    out_img = np.tile(GROUND, (SIZE, SIZE, 1))
    ox, oy = int(SIZE / 2 - cx), int(SIZE / 2 - cy + 40)
    h, w = small.shape[:2]
    # feathered paste: the panel's own edges fade into the ground
    a = np.zeros((h, w), np.float32); a[30:-30, 30:-30] = 1; a = cv2.GaussianBlur(a, (0, 0), 12)[..., None]
    X0, Y0, X1, Y1 = max(ox, 0), max(oy, 0), min(ox + w, SIZE), min(oy + h, SIZE)
    sub = small[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]; aa = a[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]
    out_img[Y0:Y1, X0:X1] = out_img[Y0:Y1, X0:X1] * (1 - aa) + sub * aa
    Image.fromarray(np.clip(out_img, 0, 255).astype(np.uint8)).save(out, quality=93, optimize=True)
    print(out, 'scale', round(s, 3))
