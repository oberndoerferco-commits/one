"""Pants product photographs from the owner's Canva design (pages 14-18, one colour per page,
front tile left, back tile right). Each tile is keyed onto the same light ground as the T-shirt
and hoodie photographs, with a soft shadow, cropped square with air around it, 2400px."""
import numpy as np
from PIL import Image, ImageFilter
OUT, GROUND, MARGIN = 2400, (233, 232, 227), 0.12
PAGES = {14: "steel", 15: "navy", 16: "slate", 17: "taupe", 18: "sage"}   # provisional colour slugs

def tiles(page):
    im = Image.open(f"page{page}.png").convert("RGB"); a = np.array(im.convert("L"))
    cols = np.where((a < 250).any(axis=0))[0]; rows = np.where((a < 250).any(axis=1))[0]
    gaps = np.where(np.diff(cols) > 50)[0]; split = gaps[0]
    left = (cols[0], rows[0], cols[split], rows[-1]); right = (cols[split+1], rows[0], cols[-1], rows[-1])
    return im.crop(left), im.crop(right)

def square(im, box, margin=MARGIN):
    x0, y0, x1, y1 = box; side = int(max(x1 - x0, y1 - y0) * (1 + 2 * margin))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; L, T = cx - side // 2, cy - side // 2
    return im.crop((L, T, L + side, T + side)).resize((OUT, OUT), Image.LANCZOS)

def build(tile, name):
    W, H = tile.size
    a_hard = tile.convert("L").point(lambda v: 255 if v < 236 else 0)
    a = a_hard.filter(ImageFilter.MedianFilter(9)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.4))
    pad = 500
    canvas = Image.new("RGB", (W + 2*pad, H + 2*pad), GROUND)
    full_a = Image.new("L", canvas.size, 0); full_a.paste(a, (pad, pad))
    shadow = Image.new("L", canvas.size, 0); shadow.paste(a, (pad, pad + 26))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.22))
    canvas = Image.composite(Image.new("RGB", canvas.size, (150, 148, 142)), canvas, shadow)
    garment = Image.new("RGB", canvas.size, GROUND); garment.paste(tile, (pad, pad))
    comp = Image.composite(garment, canvas, full_a)
    bb = full_a.point(lambda v: 255 if v > 128 else 0).getbbox()
    out = square(comp, bb).filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
    out.save(f"out/{name}.jpg", quality=92, subsampling=0)

import os; os.makedirs("out", exist_ok=True)
for p, c in PAGES.items():
    f, b = tiles(p); build(f, f"{c}-front"); build(b, f"{c}-back"); print(c, f.size)
