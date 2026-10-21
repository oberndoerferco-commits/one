"""Place each badge of a page at a fixed printed size. No tracing."""
import sys, os, numpy as np, pymupdf, importlib.util
from PIL import Image
spec = importlib.util.spec_from_file_location('b', '/home/user/one/scripts/badges.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

src, out_dir, mm = sys.argv[1], sys.argv[2], float(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
MM = 72 / 25.4
W = mm * MM
os.makedirs(out_dir, exist_ok=True)

imgs = b.badges_of(src, 600, mm, 1)          # native pixels, no upscaling
print(f'{len(imgs)} badges', file=sys.stderr)
gap = pad = 5 * MM
rows = (len(imgs) + cols - 1) // cols
doc = pymupdf.open()
page = doc.new_page(width=pad * 2 + cols * W + (cols - 1) * gap,
                    height=pad * 2 + rows * W + (rows - 1) * gap)
for i, a in enumerate(imgs):
    rgba = Image.fromarray(a, 'RGBA')
    p = os.path.join(out_dir, f'badge-{i+1}.png')
    rgba.save(p)
    s = W / max(rgba.width, rgba.height)
    w, h = rgba.width * s, rgba.height * s
    x = pad + (i % cols) * (W + gap) + (W - w) / 2
    y = pad + (i // cols) * (W + gap) + (W - h) / 2
    page.insert_image(pymupdf.Rect(x, y, x + w, y + h), filename=p, keep_proportion=True)
    # each badge on its own page too
    d2 = pymupdf.open(); pg = d2.new_page(width=w, height=h)
    pg.insert_image(pymupdf.Rect(0, 0, w, h), filename=p, keep_proportion=True)
    d2.save(os.path.join(out_dir, f'badge-{i+1}.pdf'), garbage=4, deflate=True)
    print(f'  badge {i+1}: {rgba.width}x{rgba.height} px -> {w:.1f} x {h:.1f} pt '
          f'({w/MM:.1f} x {h/MM:.1f} mm), {rgba.width/(w/72):.0f} dpi', file=sys.stderr)
f = os.path.join(out_dir, f'badges-{int(mm)}mm.pdf')
doc.save(f, garbage=4, deflate=True)
print(f'sheet {page.rect.width:.0f} x {page.rect.height:.0f} pt -> {f}', file=sys.stderr)
