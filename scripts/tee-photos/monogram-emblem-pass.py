import numpy as np, cv2
from PIL import Image
import os
os.chdir('/tmp/claude-0/-home-user-one/80d22099-9194-5203-ae1e-233f8c53bd87/scratchpad/tees')

def load(f): return np.asarray(Image.open('base/'+f).convert('RGB')).astype(np.float32)

# monogram mask from the vector render (black on white)
m = 255 - np.asarray(Image.open('mono_t6.png').convert('L')).astype(np.float32)
ys, xs = np.where(m > 30); m = m[ys.min():ys.max()+1, xs.min():xs.max()+1] / 255.0
# drop the faint grey outline so the letter edge is clean
m = np.clip((m - 0.25) / 0.6, 0, 1)

def shade(img, x0, y0, w, h):
    L = img[..., :3].mean(2)
    b = cv2.GaussianBlur(L, (0, 0), 20)
    s = np.clip(L / np.maximum(b, 1), 0.8, 1.2)
    return s[y0:y0+h, x0:x0+w]

def place(img, mask, cx, cy, width, ink):
    h = int(round(mask.shape[0] * width / mask.shape[1]))
    a = cv2.resize(mask, (width, h), interpolation=cv2.INTER_AREA)
    a = cv2.GaussianBlur(a, (0, 0), 0.6)
    x0, y0 = int(cx - width / 2), int(cy - h / 2)
    s = shade(img, x0, y0, width, h)[..., None]
    reg = img[y0:y0+h, x0:x0+width]
    col = np.array(ink, np.float32)[None, None, :] * (s ** (0.35 if ink[0] > 128 else 1.0))
    a3 = (a * 0.97)[..., None]
    img[y0:y0+h, x0:x0+width] = reg * (1 - a3) + col * a3
    return img

def place_rgba(img, rgba, cx, cy, width, k=1.0):
    h = int(round(rgba.shape[0] * width / rgba.shape[1]))
    r = cv2.resize(rgba, (width, h), interpolation=cv2.INTER_CUBIC)
    a = np.clip(r[..., 3:] / 255.0, 0, 1)
    x0, y0 = int(cx - width / 2), int(cy - h / 2)
    s = shade(img, x0, y0, width, h)[..., None]
    reg = img[y0:y0+h, x0:x0+width]
    # printed look: ink picks up the fabric's light and shadow
    s = 1 + k * (s - 1)
    col = np.clip(r[..., :3] * (0.92 + 0.08 * s) * s ** 0.6, 0, 255)
    img[y0:y0+h, x0:x0+width] = reg * (1 - a) + col * a
    return img

def remove_wordmark(img):
    # Fill the wordmark box with the fabric just below it, corrected to the local light
    # (normalised blur that ignores the box), with a soft edge.
    H, W_ = img.shape[:2]
    M = np.zeros((H, W_), np.float32)
    M[903:989, 1372:1630] = 1
    dy = 100
    src = np.roll(img, -dy, axis=0)
    keep = 1 - M
    sig = 22
    lf_o = cv2.GaussianBlur(img * keep[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(keep, (0, 0), sig), 1e-3)[..., None]
    ks = np.roll(keep, -dy, axis=0)
    lf_s = cv2.GaussianBlur(src * ks[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(ks, (0, 0), sig), 1e-3)[..., None]
    fill = src - lf_s + lf_o
    Mf = cv2.GaussianBlur(M, (0, 0), 3)[..., None]
    Mf = np.clip(Mf * 1.6, 0, 1)
    return img * (1 - Mf) + fill * Mf

def save(img, name):
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save('out/' + name, quality=92, optimize=True)

W = 190
save(place(load('obm-tee-om-black-front.jpg'), m, 1456, 907, W, (236, 235, 231)), 'obm-tee-monogram-black-front.jpg')
save(place(load('obm-tee-om-white-front-v4.jpg'), m, 1478, 913, W, (24, 24, 24)), 'obm-tee-monogram-white-front.jpg')

HW, HC = 172, (1548, 930)
for colour, f, ink in (('grey', 'obm-hoodie-om-grey-front-v2.jpg', (22, 22, 22)),
                       ('black', 'obm-hoodie-om-black-front-v2.jpg', (236, 235, 231)),
                       ('white', 'obm-hoodie-om-white-front-v3.jpg', (22, 22, 22))):
    img = remove_wordmark(load(f))
    save(img.copy(), f'clean-hoodie-{colour}.jpg')
    save(place(img, m, HC[0], HC[1], HW, ink), f'obm-hoodie-monogram-{colour}-front.jpg')

# emblems: key the white off the 1200dpi render
for n in (1, 2):
    e = np.asarray(Image.open(f'canva/emb{n}_v9.png').convert('RGB')).astype(np.float32)
    mn = e.min(2)
    a = np.clip((236 - mn) / 40, 0, 1)
    ys, xs = np.where(a > 0.05)
    e, a = e[ys.min():ys.max()+1, xs.min():xs.max()+1], a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    # un-mix the white the edges were blended with
    col = np.clip((e - 245 * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0, 255)
    rgba = np.dstack([col, a * 255])
    np.save(f'emb{n}_rgba.npy', rgba)
    print(n, rgba.shape, xs.min(), ys.min())

for n, w, top, cx, name in ((1, 234, 851, 1507, 'obm-tee-emblem-violet-front.jpg'),
                            (2, 255, 862, 1494, 'obm-tee-emblem-colour-front.jpg')):
    rgba = np.load(f'emb{n}_rgba.npy')
    h = rgba.shape[0] * w / rgba.shape[1]
    save(place_rgba(load('obm-tee-om-white-front-v4.jpg'), rgba, cx, top + h / 2, w), name)

# black versions (owner, 18 October): same emblems, placed by the black shirt's proportions
for n, w, top, cx, name in ((1, 241, 844, 1484, 'obm-tee-emblem-magenta-black-front.jpg'),
                            (2, 263, 855, 1471, 'obm-tee-emblem-ochre-black-front.jpg')):
    rgba = np.load(f'emb{n}_rgba.npy').copy()
    # tighter edge on black: the cut-out's soft rim was blended with white in the artwork
    a = rgba[..., 3] / 255.0
    a = cv2.erode(np.clip((a - 0.45) / 0.55, 0, 1).astype(np.float32), np.ones((3, 3), np.uint8))
    rgba[..., 3] = a * 255
    h = rgba.shape[0] * w / rgba.shape[1]
    save(place_rgba(load('obm-tee-om-black-front.jpg'), rgba, cx, top + h / 2, w, k=0.2), name)
