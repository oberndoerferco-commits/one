"""Bracelet photos: white background to the site ground (233,232,227) (owner, 1 November).

Curve per channel: out = v * (1 - (v/255)^2 * (1 - g/255)), so pure white lands exactly on the ground,
soft shadows follow, mid-tones (the silver) barely move. Applied evenly to the whole frame, the white onyx
included: protecting the bead centres left white patches, so the beads are toned like the rest.
usage: python3 -I bracelet-ground.py OUT_DIR IMG...
"""
import sys, os, cv2, numpy as np
out = sys.argv[1]
G = np.array([227, 232, 233], float)  # BGR
for p in sys.argv[2:]:
    im = cv2.imread(p).astype(float)
    t = (im / 255.0) ** 2
    toned = im * (1 - t * (1 - G / 255.0))
    keep = np.zeros(im.shape[:2], np.float32)
    if False:  # bead protection, tried and dropped (patchy)
        white = (im.min(2) >= 236).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
        h, w = white.shape
        for k in range(1, n):
            x, y, bw, bh, a = st[k]
            touches = x == 0 or y == 0 or x + bw >= w or y + bh >= h
            if not touches and 1500 < a < 0.05 * h * w:
                keep[lab == k] = 1
        # bead faces include their light shading just outside the near-white core
        keep = cv2.dilate(keep, np.ones((9, 9), np.uint8))
        keep = cv2.GaussianBlur(keep, (0, 0), 3)
    res = toned * (1 - keep[..., None]) + im * keep[..., None]
    name = os.path.basename(p)
    cv2.imwrite(f"{out}/{name}", np.clip(res + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    r = cv2.imread(f"{out}/{name}")
    print(name, "corner", r[5, 5][::-1], "protected px", int((keep > 0.5).sum()))
