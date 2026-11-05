"""Take a mark out of a photograph and leave the surface behind.

Three things each had to be learned the hard way here, and each is the
reason a step looks more elaborate than it needs to.

A mark is found twice over: by colour, and by standing clear of a local
median. Colour alone keeps the core and leaves the anti-aliased halo,
and a halo is exactly the shape of the thing removed - it reads as a
removal where the mark itself would merely have read as a mark.

The mask is then confined twice: to the face the mark sits on, and to a
blob hugging the mark. Without the first, dilating the mask eats the
piping or the frame running past a few pixels away. Without the second,
the lift-above-median test catches the face's own highlights.

Grain goes back as matched noise, not as copied texture. cv2.inpaint
returns the right tone and no texture, which on leather or suede reads
as a smudge. A copied patch carries whatever structure it contained, and
growing it to size - tiled or reflected - prints that structure across
the repair as seams and crosses. Noise shaped to the surface's own
high-frequency amplitude carries nothing.

patch_over is the exception, for a mark that inpainting cannot be talked
out of smearing: it moves a clean stretch of the same surface across and
relights it column by column.
"""
import cv2
import numpy as np


def face_band(shape, pts):
    """A polygon mask for the one face a mark sits on."""
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m


def find_mark(im, face, lo_r=58, dr=15, lift=6, reach=25, med=61):
    """Mark pixels: gold, plus whatever stands above the local ground."""
    b, g, r = [im[:, :, i].astype(int) for i in range(3)]
    gold = (r > lo_r) & (r - b > dr) & (g >= b)
    near = cv2.dilate((gold & (face > 0)).astype(np.uint8) * 255,
                      np.ones((reach, reach), np.uint8))
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    lifted = gray.astype(int) - cv2.medianBlur(gray, med).astype(int) > lift
    return ((gold | lifted) & (face > 0) & (near > 0)).astype(np.uint8) * 255


def grain_of(im, clean, sigma=0.9):
    """How strong the surface's own fine texture is, per channel."""
    x0, y0, x1, y1 = clean
    p = im[y0:y1, x0:x1].astype(np.float32)
    return (p - cv2.GaussianBlur(p, (0, 0), sigma)).std(axis=(0, 1))


def regrain(bgr, mask, amp, sigma=0.9, seed=0):
    """Put texture of the right strength back over an inpainted patch."""
    h, w = bgr.shape[:2]
    n = np.random.default_rng(seed).standard_normal((h, w, 3)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigma)
    n *= amp / (n.std(axis=(0, 1)) + 1e-6)
    m = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), 2)[:, :, None]
    return np.clip(bgr.astype(np.float32) + n * m, 0, 255).astype(np.uint8)


def strip(im, face, clean, dil=3, rad=8, **kw):
    """Remove a mark that is lighter than its ground."""
    m = find_mark(im, face, **kw)
    m = cv2.bitwise_and(cv2.dilate(m, np.ones((dil, dil), np.uint8)), face)
    out = cv2.inpaint(im, m, rad, cv2.INPAINT_TELEA)
    return regrain(out, m, grain_of(im, clean)), m


def strip_dark(im, quad, drop=5, med=21, dil=3, rad=4):
    """Remove a mark that is darker than its ground.

    No regrain: the marks this handles are a few pixels tall, and noise
    added at that size is more visible than the smoothing it hides.
    """
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    dark = (gray.astype(int) - cv2.medianBlur(gray, med).astype(int)) < -drop
    m = (dark & (quad > 0)).astype(np.uint8) * 255
    m = cv2.bitwise_and(cv2.dilate(m, np.ones((dil, dil), np.uint8)), quad)
    return cv2.inpaint(im, m, rad, cv2.INPAINT_TELEA), m


def patch_over(im, rect, dx=0, dy=0, feather=4, edge=7, smooth=25):
    """Move a clean stretch of the same surface over the mark, and relight it.

    The lighting is read off the rows just above and below the rect, per
    column, so a gradient across the band is carried over too. A single
    offset for the whole patch leaves it readable as a rectangle.
    """
    x0, y0, x1, y1 = rect
    src = im[y0 - dy:y1 - dy, x0 - dx:x1 - dx].astype(np.float32)
    dst = im[y0:y1, x0:x1].astype(np.float32)
    rows = np.r_[0:edge, (y1 - y0 - edge):(y1 - y0)]
    off = np.median(dst[rows], axis=0) - np.median(src[rows], axis=0)
    off = cv2.GaussianBlur(off[None, :, :], (0, 0), smooth)[0]
    m = np.zeros(dst.shape[:2], np.float32)
    m[feather - 1:1 - feather, 2 * feather:-2 * feather] = 1
    m = cv2.GaussianBlur(m, (0, 0), feather)[:, :, None]
    out = im.copy()
    out[y0:y1, x0:x1] = np.clip(dst * (1 - m) + (src + off) * m,
                                0, 255).astype(np.uint8)
    return out
