"""Hoodie product photographs from the owner's Canva PDF (three designs on one grey hoodie).
The PDF holds one 615x922 grey photograph per side and the prints as vectors; the photographs are
upscaled 4x (EDSR), recoloured to black and white on the garment only, keyed onto the same light
ground as the T-shirt photographs, and the prints re-laid from an 8x render of the page."""
import sys, os
import pypdfium2 as pdfium
from PIL import Image, ImageFilter, ImageChops
OUT = 2400; GROUND = (233, 232, 227); MARGIN = 0.14
SC = 8                                   # page render scale
# hoodie photo footprints at 8x. The PDF's object bounds are in a content space 3511 units wide on an
# 842.25pt page (scale 0.23989 to points, then x8), not in 4x page pixels as first assumed: the wrong
# footprint put every print high and to the left (owner, 16 Sept: "the hoodie logo positioning is wrong").
BOX = {"front": (906, 677, 3180, 4085), "back": (3677, 677, 5951, 4085)}
LABEL = (1993, 1623, 2136, 1686)         # the woven hood label, at 8x, front page only
DESIGNS = {1: "wordmark", 2: "om", 3: "lattice"}

def render(page_i, keep_images, drop_bg):
    pdf = pdfium.PdfDocument("designs.pdf"); page = pdf[page_i]
    imgs = [o for o in page.get_objects(max_depth=4) if o.type == pdfium.raw.FPDF_PAGEOBJ_IMAGE]
    for k, o in enumerate(imgs):
        if k not in keep_images: page.remove_obj(o)
    if drop_bg:   # the page-filling white rectangles, one at page level and one inside a form
        for o in list(page.get_objects(max_depth=4)):
            if o.type == pdfium.raw.FPDF_PAGEOBJ_PATH and o.get_bounds()[2] - o.get_bounds()[0] > 800:
                if o.container is None: page.remove_obj(o)
                else: pdfium.raw.FPDFFormObj_RemoveObject(o.container.raw, o.raw)
    page.gen_content()
    return page.render(scale=SC, fill_color=(0, 0, 0, 0)).to_pil().convert("RGBA")

def ink_overlay(page_i):
    f = f"ink{page_i+1}.png"
    if not os.path.exists(f):
        im = render(page_i, keep_images={3}, drop_bg=True)     # vectors + the lattice image, no photos, no label
        im.save(f)
    return Image.open(f).convert("RGBA")

def label_patch():
    f = "label.png"
    if not os.path.exists(f):
        im = render(0, keep_images={2}, drop_bg=False).convert("RGB").crop(LABEL); im.save(f)
    return Image.open(f).convert("RGB")

def clear_neck_label(base):
    """the mockup carries another house's label at the back neck, inside the hood: painted out with the cloth around it"""
    import cv2, numpy as np
    im = cv2.cvtColor(np.array(base), cv2.COLOR_RGB2BGR)
    mask = np.zeros(im.shape[:2], np.uint8); mask[1005:1100, 1175:1375] = 255
    out = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

def recolour(base, colour):
    """the garment only: the grey cloth is remapped in luminance, the ground is left for the key"""
    if colour == "grey": return base
    L = base.convert("L")
    if colour == "black": m = L.point(lambda v: max(4, min(255, int(0.77 * v - 33))))
    else:                 m = L.point(lambda v: max(0, min(255, int(0.85 * v + 135))))
    tinted = Image.merge("RGB", (m, m, m))
    garment = L.point(lambda v: 255 if v < 232 else 0).filter(ImageFilter.GaussianBlur(1.0))
    return Image.composite(tinted, base, garment)

def modulate(overlay, base_rgb):
    a = overlay.split()[3]; bbox = a.getbbox()
    if not bbox: return overlay
    L = base_rgb.convert("L")
    reg = L.crop(bbox); m = a.crop(bbox).point(lambda v: 255 if v > 128 else 0)
    hist = Image.composite(reg, Image.new("L", reg.size, 0), m).histogram()
    n = sum(hist[1:]); ref = max(1.0, sum(i * c for i, c in enumerate(hist[1:], 1)) / max(1, n))
    k = L.point(lambda v: int(255 * (0.6 + 0.4 * min(1.0, v / ref))))
    rgb = ImageChops.multiply(Image.merge("RGB", overlay.split()[:3]), Image.merge("RGB", (k, k, k)))
    return Image.merge("RGBA", rgb.split() + (a,))

def square(im, box, margin=MARGIN):
    x0, y0, x1, y1 = box; side = int(max(x1 - x0, y1 - y0) * (1 + 2 * margin))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; Lx, T = cx - side // 2, cy - side // 2
    return im.crop((Lx, T, Lx + side, T + side)).resize((OUT, OUT), Image.LANCZOS)

def build(design, colour, side):
    base = Image.open(f"base-grey-{side}-x4.png").convert("RGB"); W, H = base.size
    if side == "front": base = clear_neck_label(base)
    a_hard = base.convert("L").point(lambda v: 255 if v < 236 else 0)
    a = a_hard.filter(ImageFilter.MedianFilter(9)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.4))
    body = recolour(base, colour)
    pad_x, pad_y = 500, 700
    canvas = Image.new("RGB", (W + 2 * pad_x, H + 2 * pad_y), GROUND)
    full_a = Image.new("L", canvas.size, 0); full_a.paste(a, (pad_x, pad_y))
    shadow = Image.new("L", canvas.size, 0); shadow.paste(a, (pad_x, pad_y + 26))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.22))
    canvas = Image.composite(Image.new("RGB", canvas.size, (150, 148, 142)), canvas, shadow)
    garment = Image.new("RGB", canvas.size, GROUND); garment.paste(body, (pad_x, pad_y))
    comp = Image.composite(garment, canvas, full_a)
    # the print, from the page render, in the photograph's pixels
    ov = ink_overlay(design - 1).crop(BOX[side]).resize((W, H), Image.LANCZOS)
    if colour == "black":                                   # black ink becomes white, the grey keyline dark
        r, g, b, al = ov.split(); ov = Image.merge("RGBA", (ImageChops.invert(r), ImageChops.invert(g), ImageChops.invert(b), al))
    full_ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); full_ov.paste(ov, (pad_x, pad_y))
    full_ov = modulate(full_ov, comp); comp.paste(full_ov, (0, 0), full_ov)
    if side == "front":                                     # the woven label inside the hood, same on every colour
        lab = label_patch(); k = W / (BOX["front"][2] - BOX["front"][0])
        lab = lab.resize((round(lab.width * k), round(lab.height * k)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
        comp.paste(lab, (pad_x + round((LABEL[0] - BOX["front"][0]) * k), pad_y + round((LABEL[1] - BOX["front"][1]) * k)))
    bb = full_a.point(lambda v: 255 if v > 128 else 0).getbbox()
    out = square(comp, bb).filter(ImageFilter.UnsharpMask(radius=1.2, percent=50, threshold=2))
    os.makedirs("out", exist_ok=True)
    out.save(f"out/{DESIGNS[design]}-{colour}-{side}.jpg", quality=92, subsampling=0)

only = sys.argv[1:]
for d, name in DESIGNS.items():
    for colour in ("grey", "black", "white"):
        for side in ("front", "back"):
            if only and name not in only and colour not in only: continue
            build(d, colour, side); print(name, colour, side, flush=True)
