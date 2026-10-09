# leopard_ref.py SRC OUT : the owner's pink "pop" leopard reference (8 October) turned into grey shades for the
# footer, keeping its exact spots. Pixels are sorted into black spots, light centres (lighter or bluer than the
# local ground, or small islands enclosed by a ring) and ground; the masks are doubled in size and re-cut so the
# edges stay crisp, made to repeat seamlessly (each spot lifted out and put back on a wrapping canvas), and
# painted: ground #3b3b3b, spots #121212, centres in greys from the original lightness of each centre.
import sys, numpy as np, cv2
im = cv2.imread(sys.argv[1])
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
L, Bc = lab[..., 0], lab[..., 2]
black = L < 70
def localmed(ch):
    c = ch.copy(); c[black] = np.nan
    return cv2.medianBlur(np.nan_to_num(c, nan=float(np.nanmedian(c))).clip(0, 255).astype(np.uint8), 61).astype(np.float32)
centre = (~black) & ((L > localmed(L) + 10) | (Bc < localmed(Bc) - 10))
n, lab_, st, _ = cv2.connectedComponentsWithStats((~black).astype(np.uint8), 8)
centre |= np.isin(lab_, np.where(st[:, cv2.CC_STAT_AREA] < 700)[0]) & (~black)
centre = cv2.morphologyEx(centre.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool) & (~black)
# drop specks: centre pieces that are tiny or not touching a black ring
near_black = cv2.dilate(black.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
n, cl, st, _ = cv2.connectedComponentsWithStats(centre.astype(np.uint8), 8)
keep = np.zeros(n, bool)
for i in range(1, n):
    if 40 <= st[i, cv2.CC_STAT_AREA] <= 1400 and near_black[cl == i].any():   # bigger pieces are ground, not a centre
        keep[i] = True
centre = keep[cl]
# shade of each centre from its original lightness
shade = np.zeros(L.shape, np.float32)
for i in range(1, n):
    if keep[i]:
        m = cl == i
        shade[m] = float(L[m].mean())
lo, hi = np.percentile(shade[centre], 5), np.percentile(shade[centre], 95)
shade = np.where(centre, 0x66 + np.clip((shade - lo) / (hi - lo + 1e-6), 0, 1) * (0x84 - 0x66), 0)
shade = cv2.dilate(shade, np.ones((5, 5), np.uint8))   # carry the shade a little past the edges for resampling
# double the size with soft masks
S = 2
h, w = L.shape
big = lambda a, interp=cv2.INTER_CUBIC: cv2.resize(a.astype(np.float32), (w * S, h * S), interpolation=interp)
mb = big(cv2.GaussianBlur(black.astype(np.float32), (0, 0), 0.8))
mc = big(cv2.GaussianBlur(centre.astype(np.float32), (0, 0), 0.8))
sh = big(shade, cv2.INTER_NEAREST)
H, W = mb.shape
# crisp masks and the painted image (not yet seamless)
cut = lambda m: np.clip((m - 0.5) * 2.2 + 0.5, 0, 1)
ab, ac = cut(cv2.GaussianBlur(mb, (0, 0), 1.0)), cut(cv2.GaussianBlur(mc, (0, 0), 1.0))
ac = ac * (1 - ab)
shf = np.where(sh > 0, sh, 0x66)
paint = 0x12 * ab + shf * ac                      # premultiplied: spot colour times its coverage
alpha = np.clip(ab + ac, 0, 1)
# seamless: the spots are separate shapes on a plain ground. Touching spots are split apart (watershed from
# eroded cores); the tile is a window inside the picture with a margin all round, so every spot that reaches over
# a tile edge is available whole. Spots whose centre lies in the window are put on a wrapping canvas; where a
# spot reaching over one edge would land on a spot near the opposite edge, the smaller one is left out.
M = 200                                           # stay clear of the picture's own edges
Wt, Ht = W - 2 * M, H - 2 * M
fg = (alpha > 0.05).astype(np.uint8)
core = cv2.erode((ab > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))   # cores from the black only, so a centre floods from its own ring
nm, markers = cv2.connectedComponents(core)
markers = markers.astype(np.int32); markers[fg == 0] = nm + 1   # ground as its own basin
vis = cv2.merge([(255 * (1 - alpha)).astype(np.uint8)] * 3)
markers = cv2.watershed(vis, markers)
labels = np.where((markers > 0) & (markers <= nm), markers, 0)
out_p = np.zeros((Ht, Wt), np.float32); out_a = np.zeros((Ht, Wt), np.float32)
occ = np.zeros((Ht, Wt), np.int32)
placed = {}
items = []
for k in range(1, nm + 1):
    ys, xs = np.nonzero(labels == k)
    if len(ys) < 12:
        continue
    cy, cx = ys.mean(), xs.mean()
    if not (M <= cx < M + Wt and M <= cy < M + Ht):
        continue
    d = min(cx - M, M + Wt - cx, cy - M, M + Ht - cy)
    items.append((d, len(ys), k, ys, xs))
items.sort(key=lambda t: (-t[0], -t[1]))          # interior first; near edges, larger first
dropped = 0
for d, size, k, ys, xs in items:
    gy, gx = (ys - M) % Ht, (xs - M) % Wt
    if d < 60 and occ[gy, gx].any():
        dropped += 1
        continue
    occ[gy, gx] = k
    out_a[gy, gx] = alpha[ys, xs]; out_p[gy, gx] = paint[ys, xs]
H, W = Ht, Wt
# shapes that cross the tile edge in the source were also cut there: they now wrap, so nothing is cut
img = 0x3b * (1 - out_a) + out_p
img += np.random.default_rng(5).normal(0, 0.5, img.shape)
print('dropped at the seams:', dropped)
cv2.imwrite(sys.argv[2], np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
print(W, H)
