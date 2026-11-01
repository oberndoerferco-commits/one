"""Half-Zip OM, new colours (owner, 1 November): charcoal and navy.

- Squares the owner's 1280x1920 photos onto the 2400px site ground, framed like the black half-zip.
- Navy: shifted in Lab so the fabric matches the Wide-Leg Joggers OM (median of the jogger fabric).
- Backs: the white OM and OBERNDÖRFER MILANO artwork lifted from the black back photo and printed
  at the same place.
usage: python3 -I halfzip-new-colours.py REF_DIR OUT_DIR
REF_DIR holds black-front.jpg, black-back.jpg, jog-front.jpg, 26.jpg (charcoal front),
27.jpg (charcoal back), 28.jpg (navy back), 29.jpg (navy front).
"""
import sys, cv2, numpy as np
ref, out = sys.argv[1], sys.argv[2]
GROUND = np.array([227, 232, 233], float)  # BGR of (233,232,227)
S = 2400

def garment_mask(im, thr):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    m = (lab[..., 0] < thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    m = (lab_ == k).astype(np.uint8)
    # fill holes (zip, logo)
    ff = m.copy(); h, w = m.shape
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    return m | (1 - ff)

def bbox(m):
    ys, xs = np.where(m > 0); return xs.min(), xs.max(), ys.min(), ys.max()

def to_square(im, thr, target):
    """Scale/translate so the garment bbox height and centre match target (x0,x1,y0,y1)."""
    x0, x1, y0, y1 = bbox(garment_mask(im, thr))
    tx0, tx1, ty0, ty1 = target
    s = (ty1 - ty0) / (y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    tcx, tcy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
    M = np.float32([[s, 0, tcx - s * cx], [0, s, tcy - s * cy]])
    big = cv2.warpAffine(im, M, (S, S), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    cover = cv2.warpAffine(np.ones(im.shape[:2], np.float32), M, (S, S), flags=cv2.INTER_LINEAR)
    # feather the photo's own edges into flat ground
    cover = cv2.erode(cover, np.ones((3, 3), np.uint8))
    d = cv2.distanceTransform((cover > 0.99).astype(np.uint8), cv2.DIST_L2, 5)
    a = np.clip(d / 120.0, 0, 1)[..., None]
    # bring the photo's background to the site ground
    corner = np.median(im[20:120, 20:120].reshape(-1, 3), axis=0)
    big = big.astype(float) * (GROUND / corner)
    res = big * a + GROUND * (1 - a)
    return np.clip(res, 0, 255).astype(np.uint8), s

def fabric_lab(im, thr):
    m = garment_mask(im, thr) > 0
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
    dark = cv2.erode(m.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool) & (lab[..., 0] < 150)
    return np.array([np.median(lab[..., i][dark]) for i in range(3)])

def recolour(im, thr, src, dst):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
    m = cv2.GaussianBlur(garment_mask(im, thr).astype(np.float32), (0, 0), 2)
    w = m * np.clip((150 - lab[..., 0]) / 50.0, 0, 1)   # leave the silver zip alone
    new = lab.copy()
    new[..., 0] = lab[..., 0] * (dst[0] / src[0])
    new[..., 1] = lab[..., 1] + (dst[1] - src[1])
    new[..., 2] = lab[..., 2] + (dst[2] - src[2])
    res = lab * (1 - w[..., None]) + new * w[..., None]
    return cv2.cvtColor(np.clip(res, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

bf = cv2.imread(f"{ref}/black-front.jpg"); bb = cv2.imread(f"{ref}/black-back.jpg")
tf = bbox(garment_mask(bf, 70)); tb = bbox(garment_mask(bb, 70))
print("black front bbox", tf, "black back bbox", tb)

# logo artwork from the black back: bright pixels inside the garment
g = cv2.cvtColor(bb, cv2.COLOR_BGR2GRAY).astype(float)
inside = cv2.erode(garment_mask(bb, 70), np.ones((25, 25), np.uint8)) > 0
alpha = np.clip((g - 30) / (235 - 30), 0, 1) * inside
logo_col = np.median(bb[alpha > 0.95], axis=0)
print("logo colour", logo_col[::-1], "pixels", int((alpha > 0.5).sum()))

def print_logo(im):
    a = alpha[..., None]
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
    shade = cv2.GaussianBlur(lab[..., 0], (0, 0), 25)
    ref_l = np.median(shade[alpha > 0.5])
    k = np.clip(1 + 0.25 * (shade - ref_l) / 255.0 * 4, 0.92, 1.03)[..., None]
    return np.clip(im * (1 - a) + logo_col * k * a, 0, 255).astype(np.uint8)

jog = fabric_lab(cv2.imread(f"{ref}/jog-front.jpg"), 90)
print("jogger fabric Lab", jog)

jobs = [("charcoal", "front", "26.jpg", 110, tf, False),
        ("charcoal", "back", "27.jpg", 110, tb, True),
        ("navy", "front", "29.jpg", 80, tf, False),
        ("navy", "back", "28.jpg", 80, tb, True)]
for colour, side, f, thr, target, logo in jobs:
    im = cv2.imread(f"{ref}/{f}")
    if colour == "navy":
        src = fabric_lab(im, thr)
        im = recolour(im, thr, src, jog)
        print(f, "navy", src, "->", fabric_lab(im, 90))
    sq, s = to_square(im, thr if colour == "charcoal" else 90, target)
    if logo:
        sq = print_logo(sq)
    sq = cv2.filter2D(sq, -1, np.array([[0, -0.15, 0], [-0.15, 1.6, -0.15], [0, -0.15, 0]]))  # mild sharpen after ~1.7x upscale
    p = f"{out}/obm-halfzip-{colour}-{side}.jpg"
    cv2.imwrite(p, sq, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(p, "scale", round(s, 2), "fabric Lab", fabric_lab(sq, thr if colour == "charcoal" else 90))
