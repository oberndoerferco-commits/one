"""Repaint a photo's white studio background in the site's ivory (238, 237, 232), so a product shot on
white no longer shows as a white rectangle on the ivory product-page panel (owner, 7 October: "the
watchboxes have a creepy white cutout, fix!!!"). Only the background is touched: the near-white region
connected to the image border (plus its soft shadow) is multiplied by ivory/white through a feathered
mask, so shadows keep their shading and the piece itself is unchanged.
usage: ivory_ground.py IN OUT"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage

IVORY = np.array([238, 237, 232], float)

def ground(path_in, path_out):
    im = Image.open(path_in).convert('RGB'); a = np.asarray(im).astype(float)
    mn, mx = a.min(2), a.max(2)
    light = (mn >= 200) & ((mx - mn) <= 14)                       # white and light neutral shadow
    lab, n = ndimage.label(light)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border > 0]
    bg = np.isin(lab, border)
    bg = ndimage.binary_opening(bg, iterations=2)
    # enclosed pure-white gaps (the loop of a clasp, between handles): flat, large, not chrome glints
    pure = (mn >= 249) & ((mx - mn) <= 5)
    plab, pn = ndimage.label(pure & ~bg)
    if pn:
        sizes = ndimage.sum(pure, plab, range(1, pn + 1))
        keep = np.where(sizes >= a.shape[0] * a.shape[1] * 0.00012)[0] + 1
        hole = np.isin(plab, keep)
        hole = ndimage.binary_dilation(hole, iterations=2) & (mn >= 236)
        bg |= hole
    w = ndimage.gaussian_filter(bg.astype(float), sigma=max(1.5, a.shape[1] / 1400))
    w = np.clip(w, 0, 1)[..., None]
    out = a * (1 - w) + (a * IVORY / 255.0) * w
    Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(path_out, quality=93, subsampling=0)

if __name__ == '__main__':
    ground(sys.argv[1], sys.argv[2])
