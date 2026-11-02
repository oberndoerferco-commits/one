"""Beanie OM photos from the Canva "tshirt design" page 19 (owner, 2 November).

The page holds three tall light-grey panels, one per colour (black, light blue, grey); each has the
front (OM) above and the plain back below. Each beanie is cut from its panel, scaled to the framing of
the caps (about 71% of a 2400px square), and set on the site ground (233,232,227), the panel's own
grey shifted onto it with feathered edges.
usage: python3 -I canva-beanies.py PAGE.png OUT_DIR
"""
import sys, numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
page = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)[..., ::-1]  # BGR
out = sys.argv[2]
S, FIT = 2400, 1700
G = np.array([227, 232, 233], np.float32)
colours = ["black", "light-blue", "grey"]

def runs(idx, gap):
    r, s = [], idx[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a > gap: r.append((s, a)); s = b
    r.append((s, idx[-1])); return r

nonwhite = page.mean(2) < 252
for colour, (x0, x1) in zip(colours, runs(np.where(nonwhite.any(0))[0], 30)):
    rows = np.where(nonwhite[:, x0:x1].any(1))[0]
    panel = page[rows.min() + 6:rows.max() - 6, x0 + 6:x1 - 6]
    ground = np.median(np.concatenate([panel[:30].reshape(-1, 3), panel[:, :30].reshape(-1, 3)]), 0)
    obj = (np.abs(panel - ground).sum(2) > 24).astype(np.uint8)
    obj = cv2.morphologyEx(obj, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    blobs = runs(np.where(obj.any(1))[0], 60)
    blobs = sorted(blobs, key=lambda r: r[1] - r[0], reverse=True)[:2]
    blobs.sort()
    for side, (y0, y1) in zip(["front", "back"], blobs):
        xs = np.where(obj[y0:y1].any(0))[0]
        bx0, bx1 = xs.min(), xs.max()
        s = min(FIT / (bx1 - bx0), FIT / (y1 - y0))
        # crop with a generous margin of panel ground around the beanie
        m = 120
        cy0, cy1 = max(0, y0 - m), min(panel.shape[0], y1 + m)
        cx0, cx1 = max(0, bx0 - m), min(panel.shape[1], bx1 + m)
        crop = panel[cy0:cy1, cx0:cx1] - ground + G
        small = cv2.resize(crop, (int(crop.shape[1] * s), int(crop.shape[0] * s)), interpolation=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA)
        canvas = np.tile(G, (S, S, 1)).astype(np.float32)
        h, w = small.shape[:2]
        ox, oy = (S - w) // 2, (S - h) // 2
        a = np.ones((h, w), np.float32)
        f = int(m * s * 0.8)
        ramp = np.clip(np.minimum.reduce([np.arange(w)[None, :].repeat(h, 0), np.arange(w)[::-1][None, :].repeat(h, 0),
                                          np.arange(h)[:, None].repeat(w, 1), np.arange(h)[::-1][:, None].repeat(w, 1)]) / f, 0, 1)
        a = ramp[..., None]
        canvas[oy:oy + h, ox:ox + w] = small * a + canvas[oy:oy + h, ox:ox + w] * (1 - a)
        p = f"{out}/obm-beanie-om-{colour}-{side}.jpg"
        cv2.imwrite(p, np.clip(canvas, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(p, "scale", round(s, 2), "beanie px", bx1 - bx0, y1 - y0, "panel ground", ground[::-1])
