"""Hoodies in navy (owner, 1 November: "replace the white hoodies with a navy blue hoodie").

Recolours the black hoodie photos (washed black, white prints) to the navy of the Wide-Leg Joggers
OM: Lab shift of the fabric only, the white prints, label and cord tips are left as they are.
usage: python3 -I hoodie-navy.py JOGGER_JPG OUT_DIR BLACK_JPG...
"""
import sys, os, cv2, numpy as np
jog_path, out = sys.argv[1], sys.argv[2]

def garment_mask(im):
    bg = np.median(im[20:120, 20:120].reshape(-1, 3), axis=0)
    d = np.abs(im.astype(int) - bg.astype(int)).sum(2)
    m = (d > 60).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    m = (lab_ == k).astype(np.uint8)
    ff = m.copy(); h, w = m.shape
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    return m | (1 - ff)

def fabric_lab(im):
    m = cv2.erode(garment_mask(im), np.ones((31, 31), np.uint8)) > 0
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
    m &= lab[..., 0] < 150
    return np.array([np.median(lab[..., i][m]) for i in range(3)])

dst = fabric_lab(cv2.imread(jog_path))
print("jogger fabric Lab", dst)
for p in sys.argv[3:]:
    im = cv2.imread(p)
    src = fabric_lab(im)
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(float)
    m = cv2.GaussianBlur(garment_mask(im).astype(np.float32), (0, 0), 2)
    # prints are much lighter than the fabric: fade the shift out above the fabric's light end
    lo = src[0] + 35
    w = m * np.clip((lo + 45 - lab[..., 0]) / 45.0, 0, 1)
    new = lab.copy()
    new[..., 0] = lab[..., 0] * (dst[0] / src[0])
    new[..., 1] = lab[..., 1] + (dst[1] - src[1])
    new[..., 2] = lab[..., 2] + (dst[2] - src[2])
    res = lab * (1 - w[..., None]) + new * w[..., None]
    o = cv2.cvtColor(np.clip(res, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    name = os.path.basename(p).replace("-black-", "-navy-").replace("-v2", "")
    cv2.imwrite(f"{out}/{name}", o, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(name, "src", src, "->", fabric_lab(o))
