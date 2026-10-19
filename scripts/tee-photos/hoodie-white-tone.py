import numpy as np, cv2
from PIL import Image
img = np.asarray(Image.open('out/clean-hoodie-white.jpg').convert('RGB')).astype(np.float32)
L = img.mean(2)
# garment mask: brighter than the 232 ground, cleaned up
m = (L > 236).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m = (lab == big).astype(np.float32)
m = cv2.GaussianBlur(m, (0, 0), 4)[..., None]
lf = cv2.GaussianBlur(img, (0, 0), 30)
detail = img - lf
# pull the highlights down a little and bring the folds back
lf2 = 255 - (255 - lf) * 1.55
out = lf2 + detail * 1.9
out = img * (1 - m) + out * m
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save('out/clean-hoodie-white-toned.jpg', quality=92, optimize=True)
a = out.mean(2)[700:1900, 900:1700]; print('mean', a.mean().round(1), 'p5', np.percentile(a, 5).round())
