# leopard.py OUT.svg : a seamless leopard-print tile in grey shades for the footer (owner, 8 October:
# "dark grey with white writing ... maybe even a leopard pattern in grey shades"). Rosettes are broken
# rings of soft blobs around a slightly lighter centre, plus small loose spots; everything near an edge is
# drawn again on the opposite side so the tile repeats without seams.
import sys, math, random
T = 640
BASE, CENTRE, SPOT = '#2b2b2b', '#333333', '#1f1f1f'
rnd = random.Random(11)

def blob(cx, cy, r, n=7, jitter=0.35):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rnd.uniform(-jitter, jitter))
        pts.append((cx + rr * math.cos(a), cy + rr * 0.8 * math.sin(a)))
    # Catmull-Rom to cubic Bezier, closed
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + 'Z'

shapes = []  # (fill, path builder args) placed at centre (x, y)
# rosettes on a jittered grid
cells = 6
for gy in range(cells):
    for gx in range(cells):
        x = (gx + 0.5 + rnd.uniform(-0.38, 0.38)) * T / cells + (gy % 2) * T / cells / 2
        y = (gy + 0.5 + rnd.uniform(-0.38, 0.38)) * T / cells
        R = rnd.uniform(30, 40)
        rot = rnd.uniform(0, 2 * math.pi)
        shapes.append((CENTRE, x % T, y % T, R * 0.82, 9, 0.18))
        k = rnd.choice([4, 5, 5, 6])
        gaps = sorted(rnd.uniform(0, 2 * math.pi) for _ in range(k))
        for j in range(k):
            a = rot + 2 * math.pi * j / k + rnd.uniform(-0.2, 0.2)
            bx, by = x + R * math.cos(a), y + R * 0.85 * math.sin(a)
            shapes.append((SPOT, bx % T, by % T, rnd.uniform(8, 12.5), 6, 0.5))
# loose small spots between rosettes
for _ in range(30):
    shapes.append((SPOT, rnd.uniform(0, T), rnd.uniform(0, T), rnd.uniform(4, 8), 6, 0.4))

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">',
       f'<rect width="{T}" height="{T}" fill="{BASE}"/>']
for fill, x, y, r, n, j in shapes:
    state = rnd.getstate()
    for dx in (-T, 0, T):
        for dy in (-T, 0, T):
            if -90 < x + dx < T + 90 and -90 < y + dy < T + 90:
                rnd.setstate(state)  # same shape on every copy, so the tile wraps cleanly
                out.append(f'<path fill="{fill}" d="{blob(x + dx, y + dy, r, n, j)}"/>')
out.append('</svg>')
open(sys.argv[1], 'w').write(''.join(out))
print(len(''.join(out)), 'bytes')
