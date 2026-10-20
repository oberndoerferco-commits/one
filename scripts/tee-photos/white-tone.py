# One white for every white garment photo (owner, 19 October): pull the blown-out highlights down
# and bring the folds back, the same curve on tees and hoodies. Prints, labels and emblems keep
# their own colour and only take the overall shift, so they do not get a halo.
# Usage: python3 white-tone.py SRC_DIR OUT_DIR
import sys, glob, os
import numpy as np, cv2
from PIL import Image

def tone(img):
    L = img.mean(2)
    m = (L > 236).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    # fill the holes the prints leave, so the whole garment is one region
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = np.zeros_like(m); cv2.drawContours(hull, cs, -1, 1, -1)
    fabric = np.clip((L - 226) / 10, 0, 1) * hull           # 1 on white fabric, 0 on ink
    sig = 30
    lf = cv2.GaussianBlur(img * fabric[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(fabric, (0, 0), sig), 1e-3)[..., None]
    lf2 = 255 - (255 - lf) * 1.55
    on_fabric = lf2 + (img - lf) * 1.9
    on_ink = img + (lf2 - lf)
    w = fabric[..., None]
    out = w * on_fabric + (1 - w) * on_ink
    h = cv2.GaussianBlur(hull.astype(np.float32), (0, 0), 4)[..., None]
    return img * (1 - h) + out * h

src, dst = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(src, '*.jpg'))):
    img = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    out = np.clip(tone(img), 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(dst, os.path.basename(f)), quality=92, optimize=True)
    a = out.mean(2); print(os.path.basename(f), 'garment p50', np.percentile(a[a > 234], 50).round(1))
