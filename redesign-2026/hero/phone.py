# Builds obm-2026-mirror-sun-phone.jpg (in Shopify Files), the phone version of the home hero.
# The camera original IMG_3258_2.jpg is 6000x4000 landscape; a full-height phone panel is about 1:2, so a
# plain crop cuts the bag at the sides. This keeps a 3300px-wide slice around the bag, extends the dark
# wall upward (its own colour and grain) and stretches the sunlit floor downward, to 3300x6900, then
# saves at 2400px wide.  Usage: python3 phone.py IMG_3258_2.jpg out.jpg
import sys
import numpy as np
from PIL import Image, ImageFilter

im = Image.open(sys.argv[1]).convert('RGB')
x0, W, TOP, BOT, FL = 1220, 3300, 1700, 1200, 700
crop = im.crop((x0, 0, x0 + W, 4000))
a = np.asarray(crop).astype(np.float32)
# The wall above: a smooth gradient continuing the photo's top rows, with fine random grain. (The first
# version repeated the top rows' grain, which drew vertical streaks and blocks that read as pixelation on
# phones, owner 8 October.)
band = a[:300].mean(0)
k = np.exp(-0.5 * (np.arange(-660, 661) / 220.0) ** 2); k /= k.sum()
band = np.stack([np.convolve(np.pad(band[:, ch], 660, mode='edge'), k, mode='valid') for ch in range(3)], 1).astype(np.float32)
top = band[None] * np.linspace(0.84, 1.0, TOP)[:, None, None]
sd = float((a[:300] - np.asarray(Image.fromarray(a[:300].clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)))).std())
g = np.random.default_rng(1).normal(0, 1, (TOP, W, 1)).astype(np.float32)
g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype(np.uint8)[..., 0]).filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32)[..., None]
sd = max(sd, 2.4)  # at least enough grain to dither away 8-bit banding on the dark wall
g = (g - g.mean()) / (g.std() + 1e-6) * sd
top = (top + g).clip(0, 255)
floor = crop.crop((0, 4000 - FL, W, 4000)).resize((W, FL + BOT), Image.LANCZOS)
canvas = Image.new('RGB', (W, TOP + 4000 + BOT))
canvas.paste(Image.fromarray(top.astype(np.uint8)), (0, 0))
canvas.paste(crop.crop((0, 0, W, 4000 - FL)), (0, TOP))
canvas.paste(floor, (0, TOP + 4000 - FL))
c = np.asarray(canvas).astype(np.float32)
for y, h in ((TOP, 260), (TOP + 4000 - FL, 60)):  # soften both seams; long blend into the wall
    s = c[y - h:y + h].copy()
    if h > 100:  # wall seam: cross-fade the gradient into the photo's own wall
        t = np.linspace(0, 1, 2 * h)[:, None, None]
        grad = np.concatenate([top[TOP - h:TOP], (band[None] + g[:h]).clip(0, 255)])  # gradient carried on under the photo
        c[y - h:y + h] = grad * (1 - t) + s * t
    else:
        b = np.asarray(Image.fromarray(s.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
        w = 1 - np.abs(np.linspace(-1, 1, 2 * h))[:, None, None]
        c[y - h:y + h] = s * (1 - w) + b * w
out = Image.fromarray(c.clip(0, 255).astype(np.uint8))
out = out.resize((2400, round(2400 * out.height / out.width)), Image.LANCZOS)
out.save(sys.argv[2], quality=93, optimize=True, progressive=True, subsampling=0)
