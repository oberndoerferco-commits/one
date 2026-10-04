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
band = a[:250].mean(0)
band = np.asarray(Image.fromarray(band[None].clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))).astype(np.float32)[0]
top = band[None] * np.linspace(0.8, 1.0, TOP)[:, None, None]
grain = a[:250] - a[:250].mean(0)
top = (top + grain[np.random.default_rng(1).integers(0, 250, TOP)]).clip(0, 255)
floor = crop.crop((0, 4000 - FL, W, 4000)).resize((W, FL + BOT), Image.LANCZOS)
canvas = Image.new('RGB', (W, TOP + 4000 + BOT))
canvas.paste(Image.fromarray(top.astype(np.uint8)), (0, 0))
canvas.paste(crop.crop((0, 0, W, 4000 - FL)), (0, TOP))
canvas.paste(floor, (0, TOP + 4000 - FL))
c = np.asarray(canvas).astype(np.float32)
for y in (TOP, TOP + 4000 - FL):  # soften both seams
    h = 60
    s = c[y - h:y + h].copy()
    b = np.asarray(Image.fromarray(s.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    w = 1 - np.abs(np.linspace(-1, 1, 2 * h))[:, None, None]
    c[y - h:y + h] = s * (1 - w) + b * w
out = Image.fromarray(c.clip(0, 255).astype(np.uint8))
out = out.resize((2400, round(2400 * out.height / out.width)), Image.LANCZOS)
out.save(sys.argv[2], quality=88, optimize=True, progressive=True)
