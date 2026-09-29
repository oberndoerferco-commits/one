"""Swap the large four-petal flowers in the embossed photo for the star-cross logo.

    python3 design/monogram-photo/build.py

Reads original.jpg, writes logo-pattern.jpg (and debug overlays with --debug).
Steps: erase each flower (mask from a traced template), refill with paper
(local tone + grain borrowed from plain areas), then emboss the logo with the
same top-left lighting as the photo.
"""
import sys
import cv2
import numpy as np

HERE = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
DEBUG = '--debug' in sys.argv

# flower centres (the small circle in the middle) and circle radius, from HoughCircles
FLOWERS = [(961, 496, 50), (170, 1292, 50), (1735, 1301, 48), (949, 2099, 51)]
REF_R = 50

# flower outline, top tip → cusp → left tip, relative to centre at REF_R
QUARTER = [(0, -324), (-20, -290), (-45, -250), (-64, -220), (-75, -180), (-78, -150),
           (-76, -120), (-72, -95), (-64, -66)]


def flower_poly():
    half = QUARTER + [(y, x) for x, y in reversed(QUARTER[:-1])]  # mirror across the diagonal
    pts = []
    for q in range(4):  # rotate by 90° four times, top → left → bottom → right
        for x, y in half[:-1]:
            for _ in range(q):
                x, y = y, -x
            pts.append((x, y))
    return np.array(pts, float)


def logo_poly(R, steps=24):
    """The star-cross, traced from logo-reference.png (centre 999,900; tip radius 745)."""
    k = R / 745.0
    def quad(p0, c, p1):
        t = np.linspace(0, 1, steps)[1:, None]
        return list((1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p1)
    P = lambda *v: np.array(v, float)
    refl = lambda p: P(-p[1], -p[0])
    tip, a, b, c, notch = P(0, -745), P(143, -528), P(345, -419), P(199, -273), P(148, -146)
    octant = [tip, a, b] + quad(b, c, notch) + quad(notch, refl(c), refl(b))[:-1] + [refl(b), refl(a)]
    pts = []
    for q in range(4):
        for p in octant:
            x, y = p
            for _ in range(q):
                x, y = -y, x
            pts.append((x * k, y * k))
    return np.array(pts, float)


def main():
    img = cv2.imread(f'{HERE}/original.jpg').astype(np.float32)
    H, W = img.shape[:2]
    S = 4  # supersample masks for smooth edges

    def raster(polys, dilate=0):
        m = np.zeros((H * S, W * S), np.uint8)
        for p in polys:
            cv2.fillPoly(m, [np.round(p * S).astype(np.int32)], 255, lineType=cv2.LINE_AA)
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        if dilate:
            m = cv2.dilate((m > 0.02).astype(np.uint8), cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (2 * dilate + 1, 2 * dilate + 1))).astype(np.float32)
        return m

    fp = flower_poly()
    flowers = [fp * (r / REF_R) + (x, y) for x, y, r in FLOWERS]
    erase = raster(flowers, dilate=9)
    if DEBUG:
        dbg = img.copy().astype(np.uint8)
        for p in flowers:
            cv2.polylines(dbg, [np.round(p).astype(np.int32)], True, (0, 0, 255), 2)
        cv2.imwrite(f'{HERE}/debug-outline.jpg', dbg)

    # --- refill: low-frequency tone from the surroundings + borrowed paper grain
    keep = 1 - erase
    sig = 45
    tone = cv2.GaussianBlur(img * keep[..., None], (0, 0), sig) / \
        np.maximum(cv2.GaussianBlur(keep, (0, 0), sig), 1e-4)[..., None]
    # iterate so the tone reaches the middle of large holes
    for _ in range(3):
        filled = img * keep[..., None] + tone * erase[..., None]
        tone = cv2.GaussianBlur(filled, (0, 0), sig)
        tone = img * keep[..., None] * 0 + tone
    grain_src = img - cv2.GaussianBlur(img, (0, 0), 6)
    # plain paper: petal interiors of the first flower (before they are erased)
    x0, y0, _ = FLOWERS[0]
    boxes = [(x0 - 40, y0 - 250, 80, 110), (x0 - 250, y0 - 40, 110, 80),
             (x0 + 140, y0 - 40, 110, 80), (x0 - 40, y0 + 140, 80, 110)]
    rng = np.random.default_rng(7)
    grain = np.zeros_like(img)
    ph, pw = 64, 64
    for yy in range(0, H, ph):
        for xx in range(0, W, pw):
            bx, by, bw, bh = boxes[rng.integers(len(boxes))]
            sx = bx + rng.integers(0, bw - pw + 1) if bw > pw else bx
            sy = by + rng.integers(0, bh - ph + 1) if bh > ph else by
            patch = grain_src[sy:sy + ph, sx:sx + pw]
            if rng.integers(2): patch = patch[:, ::-1]
            if rng.integers(2): patch = patch[::-1]
            grain[yy:yy + ph, xx:xx + pw] = patch[:H - yy, :W - xx]
    soft = cv2.GaussianBlur(erase, (0, 0), 2.5)
    base = img * (1 - soft[..., None]) + (tone + grain) * soft[..., None]

    # --- emboss the logo: raised plateau lit from the top-left, like the circles
    logos = [logo_poly(305 * r / REF_R) + (x, y) for x, y, r in FLOWERS]
    m = raster(logos)
    h = cv2.GaussianBlur(m, (0, 0), 2.6)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    shade = (gx + gy) / np.sqrt(2)  # > 0 on edges facing the light
    light = np.clip(shade, 0, None) * 3.0
    dark = np.clip(-shade, 0, None) * 2.6
    out = base * (1 + light - dark)[..., None]
    # a faint cast shadow just outside the lower-right edges
    cast = cv2.GaussianBlur(m, (0, 0), 2.2)
    cast = np.roll(np.roll(cast, 2, 0), 2, 1) * (1 - m)
    out *= (1 - 0.08 * cast)[..., None]

    cv2.imwrite(f'{HERE}/logo-pattern.jpg', np.clip(out, 0, 255).astype(np.uint8),
                [cv2.IMWRITE_JPEG_QUALITY, 94])


if __name__ == '__main__':
    main()
