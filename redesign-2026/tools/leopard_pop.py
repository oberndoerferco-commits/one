# leopard_pop.py OUT.svg : a seamless leopard tile in grey shades after the owner's reference (8 October): the
# "pop" style, thick black C-shaped rings hugging a lighter centre, small black dots between, flat colours.
# Drawn as vector so it is crisp at any size; every shape near an edge is drawn again on the opposite side.
import sys, math, random
T = 560
BG, BLACK = '#2f2f2f', '#141414'
CENTRES = ['#4b4b4b', '#565656', '#434343', '#5e5e5e']
rnd = random.Random(23)

def blob(cx, cy, r, n=8, jit=0.22, sx=1.0, sy=0.85, rot=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rnd.uniform(-jit, jit))
        x, y = rr * math.cos(a) * sx, rr * math.sin(a) * sy
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + 'Z'

def tdist(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return math.hypot(min(dx, T - dx), min(dy, T - dy))

# rosette centres: dart throwing on the torus
pts = []
for _ in range(20000):
    p = (rnd.uniform(0, T), rnd.uniform(0, T))
    if all(tdist(p, q) > 64 for q in pts):
        pts.append(p)
dots = []
for _ in range(20000):
    p = (rnd.uniform(0, T), rnd.uniform(0, T))
    if all(tdist(p, q) > 40 for q in pts) and all(tdist(p, q) > 34 for q in dots):
        dots.append(p)

shapes = []  # each: list of (fill, path) built once, drawn at 9 offsets
for (x, y) in pts:
    r = rnd.uniform(15, 20)
    rot = rnd.uniform(0, math.pi)
    sx, sy = rnd.uniform(0.95, 1.15), rnd.uniform(0.75, 0.95)
    parts = []
    parts.append((BLACK, lambda dx, dy, s=rnd.getstate(), x=x, y=y, r=r, rot=rot, sx=sx, sy=sy: (rnd.setstate(s), blob(x + dx, y + dy, r * 1.72, 9, 0.16, sx, sy, rot))[1]))
    ox, oy = rnd.uniform(-2.5, 2.5), rnd.uniform(-2.5, 2.5)
    col = rnd.choice(CENTRES)
    parts.append((col, lambda dx, dy, s=rnd.getstate(), x=x + ox, y=y + oy, r=r, rot=rot, sx=sx, sy=sy: (rnd.setstate(s), blob(x + dx, y + dy, r * 0.95, 8, 0.25, sx, sy, rot))[1]))
    # one or two gaps in the ring make the C shapes
    for _ in range(rnd.choice([1, 1, 2])):
        a = rnd.uniform(0, 2 * math.pi)
        gx, gy = x + r * 1.62 * math.cos(a) * sx, y + r * 1.62 * math.sin(a) * sy
        parts.append((BG, lambda dx, dy, s=rnd.getstate(), gx=gx, gy=gy, r=r: (rnd.setstate(s), blob(gx + dx, gy + dy, r * 0.58, 6, 0.25))[1]))
        rnd.random()
    shapes.append(parts)
for (x, y) in dots:
    r = rnd.uniform(3.5, 6.5)
    shapes.append([(BLACK, lambda dx, dy, s=rnd.getstate(), x=x, y=y, r=r: (rnd.setstate(s), blob(x + dx, y + dy, r, 6, 0.35, 1.0, 0.8, rnd.uniform(0, 3)))[1])])
    rnd.random()

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">', f'<rect width="{T}" height="{T}" fill="{BG}"/>']
centres = [(x, y) for x, y in pts] + [(x, y) for x, y in dots]
for (cx, cy), parts in zip(centres, shapes):
    for dx in (-T, 0, T):
        for dy in (-T, 0, T):
            if -50 < cx + dx < T + 50 and -50 < cy + dy < T + 50:  # only copies that reach into the tile
                out.extend(f'<path fill="{f}" d="{mk(dx, dy)}"/>' for f, mk in parts)
out.append('</svg>')
svg = ''.join(out)
open(sys.argv[1], 'w').write(svg)
print(len(pts), 'rosettes', len(dots), 'dots', len(svg), 'bytes')
