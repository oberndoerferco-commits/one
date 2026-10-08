# leopard_pop.py OUT.svg : seamless leopard tile in grey shades after the owner's reference (8 October): thick,
# open black rings (C and U shapes with round ends) around lighter centres, tightly packed, plus a few small
# black commas. Vector, so it is crisp at any size; shapes near an edge are drawn again on the opposite side.
import sys, math, random
T = 600
BG, BLACK = '#363636', '#121212'
CENTRES = ['#646464', '#6e6e6e', '#5e5e5e', '#787878', '#696969']
rnd = random.Random(7)

def tdist(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return math.hypot(min(dx, T - dx), min(dy, T - dy))

def smooth(pts, closed):
    n = len(pts)
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[i - 1] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + ('Z' if closed else '')

def rosette(x, y):
    r = rnd.uniform(14, 19)
    sx, sy, rot = rnd.uniform(0.9, 1.15), rnd.uniform(0.75, 0.95), rnd.uniform(0, math.pi)
    def at(a, rr):
        px, py = rr * math.cos(a) * sx, rr * math.sin(a) * sy
        return (x + px * math.cos(rot) - py * math.sin(rot), y + px * math.sin(rot) + py * math.cos(rot))
    out = []
    # lighter centre, slightly irregular, filling the ring
    n = 8; cen = [at(2 * math.pi * i / n, r * rnd.uniform(0.82, 1.02)) for i in range(n)]
    out.append(('fill', rnd.choice(CENTRES), smooth(cen, True), 0))
    # the ring: one open arc (C/U), sometimes split in two
    w = r * rnd.uniform(0.58, 0.68)
    start = rnd.uniform(0, 2 * math.pi)
    sweep = rnd.uniform(3.9, 5.2)                      # 225..300 degrees
    arcs = [(start, sweep)]
    if rnd.random() < 0.35:                            # split into two pieces
        cut = rnd.uniform(0.35, 0.6) * sweep
        arcs = [(start, cut - 0.45), (start + cut + 0.15, sweep - cut - 0.15)]
    for a0, sw in arcs:
        k = max(4, int(sw / 0.45))
        pts = [at(a0 + sw * i / k, r * rnd.uniform(0.95, 1.08)) for i in range(k + 1)]
        ww = w * rnd.uniform(0.9, 1.1)
        out.append(('stroke', BLACK, smooth(pts, False), ww))
        # fatter in the middle of the arc, like a brush mark
        m0, m1 = int(len(pts) * 0.25), int(len(pts) * 0.75) + 1
        if m1 - m0 >= 2:
            out.append(('stroke', BLACK, smooth(pts[m0:m1], False), ww * 1.22))
    return out

def comma(x, y):
    a = rnd.uniform(0, 2 * math.pi); L = rnd.uniform(5, 11)
    if rnd.random() < 0.5:
        return [('stroke', BLACK, f'M{x:.1f},{y:.1f}L{x + L * math.cos(a):.1f},{y + L * math.sin(a):.1f}', rnd.uniform(10, 13))]
    pts = [(x + rnd.uniform(-5, 5), y + rnd.uniform(-5, 5)) for _ in range(3)]
    return [('stroke', BLACK, smooth(pts, False), rnd.uniform(10, 13))]

pts = []
for _ in range(30000):
    p = (rnd.uniform(0, T), rnd.uniform(0, T))
    if all(tdist(p, q) > 54 for q in pts):
        pts.append(p)
small = []
for _ in range(30000):
    p = (rnd.uniform(0, T), rnd.uniform(0, T))
    if all(tdist(p, q) > 36 for q in pts) and all(tdist(p, q) > 48 for q in small):
        small.append(p)

items = [(p, rosette(*p)) for p in pts] + [(p, comma(*p)) for p in small]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{T}" height="{T}" viewBox="0 0 {T} {T}">',
       f'<rect width="{T}" height="{T}" fill="{BG}"/>']
for (cx, cy), shapes in items:
    for dx in (-T, 0, T):
        for dy in (-T, 0, T):
            if -60 < cx + dx < T + 60 and -60 < cy + dy < T + 60:
                svg.append(f'<g transform="translate({dx} {dy})">')
                for kind, col, d, w in shapes:
                    if kind == 'fill':
                        svg.append(f'<path fill="{col}" d="{d}"/>')
                    else:
                        svg.append(f'<path fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round" d="{d}"/>')
                svg.append('</g>')
svg.append('</svg>')
s = ''.join(svg)
open(sys.argv[1], 'w').write(s)
print(len(pts), 'rosettes', len(small), 'commas', len(s), 'bytes')
