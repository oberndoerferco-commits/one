"""Fill the white corners left where a product shot was pasted onto the ivory ground as a rectangle
(owner, 7 October, the pink watch box: "creepy white cutout"). Within the background (light neutral
pixels connected to the image border) every pixel lighter than the ivory is brought down to the ivory,
channel by channel, through a feathered mask; the ivory itself, the soft shadow and the piece are left
as they are. usage: ivory_corners.py IN OUT"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage

IVORY = np.array([238, 237, 232], float)

def fix(path_in, path_out):
    a = np.asarray(Image.open(path_in).convert('RGB')).astype(float)
    mn, mx = a.min(2), a.max(2)
    light = (mn >= 200) & ((mx - mn) <= 16)
    lab, n = ndimage.label(light)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])); border = border[border > 0]
    bg = ndimage.binary_dilation(np.isin(lab, border), iterations=2)
    w = np.clip(ndimage.gaussian_filter(bg.astype(float), 1.5), 0, 1)[..., None]
    out = a * (1 - w) + np.minimum(a, IVORY) * w
    Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(path_out, quality=93, subsampling=0)

if __name__ == '__main__':
    fix(sys.argv[1], sys.argv[2])
