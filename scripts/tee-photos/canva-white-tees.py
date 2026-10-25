# White T-shirt photos rebuilt from the owner's Canva "tshirt design" (25 October): the old white
# tee base photo was small and upscaled (soft prints, unreadable neck label). Each Canva page holds
# front (left) and back (right) on white; the tee is keyed off the white, scaled to the site's
# framing (1696px wide on a 2400px square), toned to the same white as the hoodies and set on the
# site's warm grey ground with a soft shadow.
# Usage: python3 canva-white-tees.py PAGE_DIR REFERENCE_WHITE_JPG OUT_DIR
import sys, os
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

PAGES = {  # page export -> (front name, back name)
    'p1': ('obm-tee-emblem-magenta-front', 'obm-tee-emblem-magenta-back'),
    'p2': ('obm-tee-emblem-ochre-front', 'obm-tee-emblem-ochre-back'),
    'p5': ('obm-tee-om-white-front-v4', 'obm-tee-om-white-back-v4'),
    'p7': ('obm-tee-star-white-front-v4', 'obm-tee-star-white-back-v4'),
    'p9': ('obm-tee-lattice-white-front-v4', 'obm-tee-lattice-white-back-v4'),
}
SIZE, WIDTH, TOP = 2400, 1696, 288
GROUND = np.array([233, 232, 227], np.float32)

def key(half):
    L = half.mean(2)
    bg = (L >= 253.5).astype(np.uint8)
    mask = np.zeros((bg.shape[0] + 2, bg.shape[1] + 2), np.uint8)
    cv2.floodFill(bg, mask, (0, 0), 2)
    g = (bg != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(g)
    g = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    cs, _ = cv2.findContours(g, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(g); cv2.drawContours(full, cs, -1, 1, -1)
    # the blown-out highlights touch the white page in places (collar, shoulders): smooth the
    # outline so it does not follow single pixels there
    full = cv2.morphologyEx(full, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    full = (cv2.GaussianBlur(full.astype(np.float32), (0, 0), 4) > 0.5).astype(np.uint8)
    return full

def fabric_lf(img, m):
    L = img.mean(2)
    fab = np.clip((L - 226) / 10, 0, 1) * m
    lf = cv2.GaussianBlur(img * fab[..., None], (0, 0), 30) / np.maximum(cv2.GaussianBlur(fab, (0, 0), 30), 1e-3)[..., None]
    return fab, lf

def reference_points(path):
    img = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    L = img.mean(2); m = (L > 234).astype(np.float32)
    fab, lf = fabric_lf(img, m)
    v = lf.mean(2)[fab > 0.9]
    return np.percentile(v, [1, 5, 25, 50, 75, 95, 99.5])

def build(rgb, m, ref):
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgb, m = rgb[y0:y1, x0:x1], m[y0:y1, x0:x1].astype(np.float32)
    s = WIDTH / rgb.shape[1]
    w, h = WIDTH, int(round(rgb.shape[0] * s))
    img = cv2.resize(rgb.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    # the Canva cut-out has a bright, beaded rim a few pixels wide: trim it off
    m = cv2.erode((m > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)
    # tone: map the local light of the fabric onto the hoodie white, keep fold detail, prints shift only
    fab, lf = fabric_lf(img, (m > 0.5).astype(np.float32))
    v = lf.mean(2)[fab > 0.9]
    src = np.percentile(v, [1, 5, 25, 50, 75, 95, 99.5])
    src = np.maximum.accumulate(src + np.arange(7) * 1e-3)
    lf2 = np.interp(lf, src, ref)
    on_fabric = lf2 + (img - lf) * 1.4
    on_ink = img + (lf2 - lf)
    wf = fab[..., None]
    img = np.clip(wf * on_fabric + (1 - wf) * on_ink, 0, 255)
    # compose on the ground
    out = np.tile(GROUND, (SIZE, SIZE, 1))
    X, Y = (SIZE - w) // 2, TOP
    canvas_m = np.zeros((SIZE, SIZE), np.float32); canvas_m[Y:Y + h, X:X + w] = m
    canvas_i = out.copy(); canvas_i[Y:Y + h, X:X + w] = img
    sh = cv2.GaussianBlur(np.roll(canvas_m, 18, axis=0), (0, 0), 24)
    out = out * (1 - 0.13 * sh)[..., None]
    a = cv2.GaussianBlur(canvas_m, (0, 0), 0.7)[..., None]
    return out * (1 - a) + canvas_i * a

page_dir, ref_path, out_dir = sys.argv[1:4]
ref = reference_points(ref_path)
print('reference white', ref.round(1))
for p, names in PAGES.items():
    page = np.asarray(Image.open(os.path.join(page_dir, p + '.png')).convert('RGB'))
    mid = page.shape[1] // 2
    for half, name in ((page[:, :mid], names[0]), (page[:, mid:], names[1])):
        m = key(half)
        res = build(half, m, ref)
        Image.fromarray(res.astype(np.uint8)).save(os.path.join(out_dir, name + '.jpg'), quality=93, optimize=True)
        L = res.mean(2)[TOP:2150, 400:2000]
        print(name, 'fabric p50', np.percentile(L[L > 234], 50).round(1))
