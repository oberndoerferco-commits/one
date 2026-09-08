"""Rebuild the T-shirt product photographs from the Canva layers, in each photograph's own space.
Base photographs (EDSR x3) + print layers exported at 4x page scale (4492x3176). Each shirt is cropped to a
square with air around it, on the photograph's own ground; the white shirts are keyed off their black ground
and set on the same light ground as the black photographs."""
import json, os, sys
from PIL import Image, ImageFilter, ImageChops
S = 4.0
OUT = 2400
GROUND = (233, 232, 227)
MARGIN = 0.16
plan = json.load(open("copy-plan.json")); pages = {int(k): v for k, v in plan.items()}

def load_base(name):
    f = name + "-x3.png"
    if os.path.exists(f): im = Image.open(f).convert("RGB")
    else:
        im = Image.open(name + ".png").convert("RGB"); im = im.resize((im.width*3, im.height*3), Image.LANCZOS)
    return im

def overlay_for(page, geo, target_size):
    """the print layer, cut to the photograph's footprint on the page and scaled to the photograph's pixels"""
    ov = Image.open(f"ov{page:02d}.png").convert("RGBA")
    b = geo["box"]; x = (geo["left"] + b["left"]) * S; y = (geo["top"] + b["top"]) * S
    w = b["width"] * S; h = b["height"] * S
    cut = ov.crop((round(x), round(y), round(x + w), round(y + h)))   # out-of-page areas come back transparent
    return cut.resize(target_size, Image.LANCZOS)

def modulate(overlay, base_rgb):
    """the print follows the folds: its colour scaled by the cloth's local brightness under it"""
    a = overlay.split()[3]; bbox = a.getbbox()
    if not bbox: return overlay
    L = base_rgb.convert("L")
    reg = L.crop(bbox); m = a.crop(bbox).point(lambda v: 255 if v > 128 else 0)
    hist = Image.composite(reg, Image.new("L", reg.size, 0), m).histogram()
    n = sum(hist[1:]); ref = max(1.0, sum(i * c for i, c in enumerate(hist[1:], 1)) / max(1, n))
    k = L.point(lambda v: int(255 * (0.6 + 0.4 * min(1.0, v / ref))))
    rgb = Image.merge("RGB", overlay.split()[:3])
    rgb = ImageChops.multiply(rgb, Image.merge("RGB", (k, k, k)))
    return Image.merge("RGBA", rgb.split() + (a,))

from PIL import ImageDraw, ImageFont
FONT = "Marcellus-Regular.ttf"
# the mockups carry other houses' labels inside the collar; ours goes in the same place, at the same size.
# rects in base-photograph pixels (x0, y0, x1, y1), colours sampled from the originals.
BLACK_LABEL = dict(rect=(402, 353, 451, 366), fill=(214, 216, 218), ink=(58, 56, 54), lines=("OBERNDÖRFER", "MILANO"))
WHITE_LABEL = dict(rect=(308, 185, 352, 205), fill=(228, 224, 223), ink=(52, 50, 48), lines=("OBERNDÖRFER", "MILANO", "MADE IN ITALY"))
def paint_label(base, spec, k=3):
    x0, y0, x1, y1 = [v * k for v in spec["rect"]]; w, h = x1 - x0, y1 - y0
    lab = Image.new("RGB", (w, h), spec["fill"])
    d = ImageDraw.Draw(lab)
    # a faint woven border
    d.rectangle((1, 1, w - 2, h - 2), outline=tuple(c - 18 for c in spec["fill"]), width=1)
    lines = spec["lines"]; n = len(lines)
    # sizes: the name takes ~70% of the width, the rest proportionally smaller
    def fit(text, target_w, max_h):
        size = 6
        while True:
            f = ImageFont.truetype(FONT, size + 1); bb = d.textbbox((0, 0), text, font=f)
            if bb[2] - bb[0] > target_w or bb[3] - bb[1] > max_h: break
            size += 1
        return ImageFont.truetype(FONT, size)
    if n == 2:
        f1 = fit(lines[0], w * 0.72, h * 0.46); f2 = fit(lines[1], w * 0.32, h * 0.26)
        fonts = [f1, f2]
    else:
        f1 = fit(lines[0], w * 0.72, h * 0.34); f2 = fit(lines[1], w * 0.30, h * 0.20); f3 = fit(lines[2], w * 0.44, h * 0.16)
        fonts = [f1, f2, f3]
    heights = [d.textbbox((0, 0), t, font=f)[3] - d.textbbox((0, 0), t, font=f)[1] for t, f in zip(lines, fonts)]
    gap = max(1, int(h * 0.06)); total = sum(heights) + gap * (n - 1); y = (h - total) // 2
    for t, f, hh in zip(lines, fonts, heights):
        bb = d.textbbox((0, 0), t, font=f); tw = bb[2] - bb[0]
        d.text(((w - tw) // 2 - bb[0], y - bb[1]), t, font=f, fill=spec["ink"])
        y += hh + gap
    # soften to the photograph's own sharpness and let the cloth's shading through a little
    lab = lab.filter(ImageFilter.GaussianBlur(0.7))
    under = base.crop((x0, y0, x1, y1)).convert("L").filter(ImageFilter.GaussianBlur(4))
    mean = sum(i * c for i, c in enumerate(under.histogram())) / (w * h)
    kimg = under.point(lambda v: int(255 * min(1.0, 0.85 + 0.15 * v / max(1, mean))))
    lab = ImageChops.multiply(lab, Image.merge("RGB", (kimg, kimg, kimg)))
    out = base.copy(); out.paste(lab, (x0, y0)); return out

def square(im, box, margin=MARGIN):
    x0, y0, x1, y1 = box; side = int(max(x1 - x0, y1 - y0) * (1 + 2 * margin))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; L, T = cx - side // 2, cy - side // 2
    return im.crop((L, T, L + side, T + side)).resize((OUT, OUT), Image.LANCZOS)

def dark_bbox(rgb):
    g = rgb.convert("L").resize((rgb.width // 6, rgb.height // 6)); bb = g.point(lambda v: 255 if v < 120 else 0).getbbox()
    return tuple(v * 6 for v in bb)

def build_black(page, name):
    geo = pages[page]["geo"]
    for side, key in (("front", "MAHTZv1m2vI"), ("back", "MAHTZqRCJ4w")):
        base = load_base("base-black-" + side)
        if side == "front": base = paint_label(base, BLACK_LABEL)
        ov = modulate(overlay_for(page, geo[key], base.size), base)
        comp = base.copy(); comp.paste(ov, (0, 0), ov)
        square(comp, dark_bbox(base)).save(f"out/{name}-black-{side}.jpg", quality=92, subsampling=0)

def build_white(page, name):
    geo = pages[page]["geo"]["MAHUWArrQKo"]
    base = load_base("base-white"); base = base.crop((0, 0, base.width, 864 * 3 - 8))   # the export padded a white row; keep clear of it
    base = paint_label(base, WHITE_LABEL)
    W, H = base.size
    a_all = base.convert("L").point(lambda v: 255 if v > 150 else int(255 * v / 150))
    ov_all = overlay_for(page, geo, (W, 864 * 3 + 3)).crop((0, 0, W, H))   # the page footprint covers the padded row too
    split = 616 * 3   # the gap between the two shirts in the photograph
    pad_x, pad_y = 500, 800
    for side, (x0, x1) in (("front", (0, split)), ("back", (split, W))):
        # one shirt at a time: the other is masked out so the crop never reaches it
        keep = Image.new("L", (W, H), 0); keep.paste(255, (x0, 0, x1, H))
        a = ImageChops.multiply(a_all, keep)
        canvas = Image.new("RGB", (W + 2 * pad_x, H + 2 * pad_y), GROUND)
        full_a = Image.new("L", canvas.size, 0); full_a.paste(a, (pad_x, pad_y))
        shadow = Image.new("L", canvas.size, 0); shadow.paste(a, (pad_x, pad_y + 24))
        shadow = shadow.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.20))
        canvas = Image.composite(Image.new("RGB", canvas.size, (152, 150, 144)), canvas, shadow)
        inv = ImageChops.invert(full_a)
        ground_part = ImageChops.multiply(canvas, Image.merge("RGB", (inv, inv, inv)))
        # a white object on black: pixel = colour x alpha, so ground x (1 - alpha) + pixel is the exact composite
        masked = ImageChops.multiply(base, Image.merge("RGB", (keep, keep, keep)))
        pixel_part = Image.new("RGB", canvas.size, (0, 0, 0)); pixel_part.paste(masked, (pad_x, pad_y))
        comp = ImageChops.add(ground_part, pixel_part)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ov.paste(ov_all.crop((x0, 0, x1, H)), (x0, 0))
        full_ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); full_ov.paste(ov, (pad_x, pad_y))
        full_ov = modulate(full_ov, comp)
        comp.paste(full_ov, (0, 0), full_ov)
        bb = full_a.point(lambda v: 255 if v > 128 else 0).getbbox()
        square(comp, bb).save(f"out/{name}-white-{side}.jpg", quality=92, subsampling=0)

os.makedirs("out", exist_ok=True)
NAMES = {1: "embroidered", 3: "om", 5: "chrome", 7: "star", 9: "lattice"}
only = sys.argv[1:]
for p, n in NAMES.items():
    if not only or str(p) in only: build_black(p, n); print("black", n, flush=True)
    if not only or str(p + 1) in only: build_white(p + 1, n); print("white", n, flush=True)
print("done")
