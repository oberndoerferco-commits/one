#!/usr/bin/env python3
"""Ten t-shirt designs built around a machete with a checkerboard blade.

The client's reference was a watermarked stock illustration, so nothing here
is traced from it: the blade, the handle and the checker motif are all drawn
from scratch, which also means the artwork is theirs to print.

Every design is 2400 x 3200 px = 8 x 10.67 in at 300 dpi, RGBA with a clear
ground so it drops onto any shirt colour. A contact sheet shows all ten on a
garment-coloured field.

    python3 scripts/machete_tees.py --out assets/machete-tees
"""
import argparse, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 2400, 3200
SS = 2                      # supersample factor for the silhouette masks

# ---------------------------------------------------------------- geometry

# Straight-edged, like the reference: the spine is one straight run, the edge
# another that diverges from it, and the nose is a single swept arc joining
# the two. Nothing is smoothed, so every line stays dead straight.
SPINE_Y = 0.045          # half-width at the spine, constant
EDGE_0 = 0.042           # half-width at the bolster, on the edge side
EDGE_1 = 0.117           # ...and at the tip: the blade widens as it runs out
NOSE_X = 0.855           # where the spine stops and the nose arc begins
KEY = 0.0062             # keyline width, as a fraction of blade length


def blade_poly(n=26):
    """Spine, nose arc, edge. Three runs, two of them perfectly straight."""
    pts = [(0.0, SPINE_Y), (NOSE_X, SPINE_Y)]
    dx, dy = 1.0 - NOSE_X, SPINE_Y + EDGE_1
    for i in range(1, n + 1):
        t = i / n * math.pi / 2
        pts.append((NOSE_X + dx * math.sin(t), SPINE_Y - dy * (1 - math.cos(t))))
    pts.append((0.0, -EDGE_0))
    return pts


def handle_poly():
    """A chunky straight-sided grip, square finger swells, rounded butt."""
    return [
        (0.004, 0.056), (-0.030, 0.086), (-0.360, 0.086),
        (-0.402, 0.072), (-0.424, 0.038),
        (-0.424, -0.030), (-0.400, -0.064), (-0.356, -0.080),
        (-0.300, -0.086), (-0.236, -0.080), (-0.198, -0.066),
        (-0.160, -0.074), (-0.120, -0.086), (-0.074, -0.082),
        (-0.030, -0.088), (0.004, -0.058),
    ]


def bolster_poly():
    return [(0.030, 0.052), (0.030, -0.050), (-0.030, -0.088), (-0.030, 0.086)]


def place(pts, cx, cy, length, deg):
    """Blade-space -> canvas, rotated deg clockwise from pointing right."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        X, Y = x * length, -y * length          # y up in blade space
        out.append((cx + X * ca - Y * sa, cy + X * sa + Y * ca))
    return out


HOLE = (-0.340, 0.004, 0.024)          # lanyard hole: x, y, radius


def masks(scale=1, deg=-61.0, margin=0.07, crossed=False):
    """Fill masks, the heavy keyline, and the outer silhouette.

    `crossed` lays a mirrored second knife over the first.
    """
    w, h = W * scale, H * scale
    polys = {'blade': blade_poly(), 'handle': handle_poly(),
             'bolster': bolster_poly()}
    angles = [deg, 180 - deg] if crossed else [deg]
    probe = []
    for g in angles:
        for q in polys.values():
            probe += place(q, 0.0, 0.0, 1.0, g)
    xs = [p[0] for p in probe]; ys = [p[1] for p in probe]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    pad = 1.0 + KEY * 2
    length = min(w * (1 - 2 * margin) / (bw * pad), h * (1 - 2 * margin) / (bh * pad))
    cx = w / 2 - (min(xs) + bw / 2) * length
    cy = h / 2 - (min(ys) + bh / 2) * length
    kw = max(3, int(round(KEY * length)))

    out = {k: Image.new('L', (w, h), 0) for k in polys}
    key = Image.new('L', (w, h), 0)
    holes = Image.new('L', (w, h), 0)
    dk = ImageDraw.Draw(key)
    for g in angles:
        for name, poly in polys.items():
            P = place(poly, cx, cy, length, g)
            im = Image.new('L', (w, h), 0)
            ImageDraw.Draw(im).polygon(P, fill=255)
            out[name] = ImageChops.lighter(out[name], im)
            if name != 'bolster':
                dk.line(P + [P[0]], fill=255, width=kw, joint='curve')
        P = place(bolster_poly()[:2], cx, cy, length, g)
        dk.line(P, fill=255, width=kw, joint='curve')
        hx, hy = place([(HOLE[0], HOLE[1])], cx, cy, length, g)[0]
        r = HOLE[2] * length
        ImageDraw.Draw(holes).ellipse([hx - r, hy - r, hx + r, hy + r], fill=255)
        dk.ellipse([hx - r, hy - r, hx + r, hy + r], outline=255, width=kw)
    inv = ImageChops.invert(holes)
    fill = ImageChops.lighter(ImageChops.lighter(out['blade'], out['handle']),
                              out['bolster'])
    for k in list(out):
        out[k] = ImageChops.darker(out[k], inv)
    out['key'] = ImageChops.darker(key, ImageChops.invert(
        ImageChops.darker(holes, ImageChops.invert(key))))
    out['key'] = ImageChops.darker(key, inv) if False else key
    out['key'] = ImageChops.subtract(key, holes)
    out['all'] = ImageChops.darker(ImageChops.lighter(fill, key), inv)
    return out


def down(im):
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


def arr(im):
    return np.asarray(im, dtype=np.float32) / 255.0


# ---------------------------------------------------------------- textures

def fbm(shape, octaves=6, seed=0, persistence=0.55):
    """Fractal value noise in [0, 1]."""
    rng = np.random.default_rng(seed)
    h, w = shape
    total = np.zeros(shape, np.float32)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        n = 2 ** (o + 2)
        g = rng.random((n, n)).astype(np.float32)
        layer = np.asarray(Image.fromarray((g * 255).astype(np.uint8))
                           .resize((w, h), Image.BICUBIC), np.float32) / 255.0
        total += layer * amp
        norm += amp
        amp *= persistence
    total /= norm
    total -= total.min()
    return total / max(total.max(), 1e-6)


def cross_pattee(d, cx, cy, r, col):
    """Four arms flaring outward from a narrow waist: a cross pattee."""
    a, b, L = 0.21, 0.54, 1.0
    u = [(-a, -a), (-b, -L), (b, -L), (a, -a),
         (L, -b), (L, b), (a, a),
         (b, L), (-b, L), (-a, a),
         (-L, b), (-L, -b)]
    d.polygon([(cx + px * r, cy + py * r) for px, py in u], fill=col)


def checker_tile(cell, light, dark, motif, seed=0):
    """One diagonal checker repeat with a cross in the dark squares."""
    t = Image.new('RGB', (cell * 2, cell * 2), light)
    d = ImageDraw.Draw(t)
    d.rectangle([0, 0, cell - 1, cell - 1], fill=dark)
    d.rectangle([cell, cell, cell * 2 - 1, cell * 2 - 1], fill=dark)
    cross_pattee(d, cell * 0.5, cell * 0.5, cell * 0.30, motif)
    cross_pattee(d, cell * 1.5, cell * 1.5, cell * 0.30, motif)
    for ox, oy in ((cell * 1.5, cell * 0.5), (cell * 0.5, cell * 1.5)):
        r = cell * 0.17
        d.ellipse([ox - r, oy - r, ox + r, oy + r], outline=motif,
                  width=max(2, cell // 22))
        d.ellipse([ox - r * .45, oy - r * .45, ox + r * .45, oy + r * .45],
                  fill=motif)
    return t


def tiled(tile, angle=45.0, size=(W, H)):
    """Tile an image over the canvas at an angle."""
    big = int(math.hypot(*size) * 1.25)
    reps = big // tile.size[0] + 2
    sheet = Image.new('RGB', (tile.size[0] * reps, tile.size[1] * reps))
    for i in range(reps):
        for j in range(reps):
            sheet.paste(tile, (i * tile.size[0], j * tile.size[1]))
    sheet = sheet.rotate(angle, resample=Image.BICUBIC, expand=False)
    x = (sheet.size[0] - size[0]) // 2
    y = (sheet.size[1] - size[1]) // 2
    return sheet.crop((x, y, x + size[0], y + size[1]))


def ink_key(body, M, col=(0.05, 0.05, 0.06)):
    """Lay the heavy outline over a finished body."""
    k = arr(down(M['key']))[..., None]
    return body * (1 - k) + np.array(col, np.float32) * k


def compose(layers, m_all):
    """Stack RGB layers, then cut to the knife silhouette."""
    base = layers
    a = (np.clip(m_all, 0, 1) * 255).astype(np.uint8)
    out = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8), 'RGB')
    out.putalpha(Image.fromarray(a))
    return out


def rough_edge(mask, amount=0.012, seed=1, scale=7):
    """Chew the silhouette with noise, for hand-made looks."""
    n = fbm(mask.shape, octaves=scale, seed=seed)
    return np.clip((mask - 0.5) + (n - 0.5) * amount * 40, 0, 1)


def soft(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def rgb(*c):
    return np.dstack(c).astype(np.float32)


def flat(mask, colour):
    return np.dstack([np.full(mask.shape, colour[i] / 255.0, np.float32)
                      for i in range(3)])


# ---------------------------------------------------------------- designs

def d01_checker(M):
    """Straight translation: the checker blade, crisp, one colour."""
    blade, handle, bolster, allm = (arr(down(M[k])) for k in
                                    ('blade', 'handle', 'bolster', 'all'))
    tile = checker_tile(104, (236, 236, 232), (92, 95, 100), (26, 27, 30))
    pat = arr(tiled(tile, 45))
    body = pat * blade[..., None]
    body += flat(blade, (16, 16, 18)) * handle[..., None] * (1 - blade[..., None])
    body += flat(blade, (58, 60, 64)) * bolster[..., None] * (1 - blade[..., None]) * (1 - handle[..., None])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = xx * math.cos(a) + yy * math.sin(a)
    band = ((u % 520 < 90) | ((u + 250) % 520 < 46)).astype(np.float32) * blade
    body = np.clip(body + band[..., None] * 0.22, 0, 1)
    return compose(ink_key(body, M), allm)


def d02_painted(M):
    """Dry brush and ink wash, torn edge, drips off the tip."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    chewed = allm.copy()
    grain = fbm((H, W), octaves=7, seed=11)
    streak = fbm((H, W), octaves=4, seed=12, persistence=0.8)
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(1))
                        .resize((W, H)), np.float32) / 255.0
    ink = np.clip(0.42 + 1.25 * (grain * 0.40 + streak * 0.60) - 0.34, 0, 1)
    body = flat(blade, (14, 13, 16)) * (0.35 + 0.65 * ink[..., None])
    wash = flat(blade, (176, 42, 38))
    pat = arr(tiled(checker_tile(118, (255, 255, 255), (0, 0, 0), (255, 255, 255)), 45))
    pat = pat[..., 0]
    body = np.where((blade * pat > 0.5)[..., None], wash * 0.85 + body * 0.15, body)
    drip = np.zeros((H, W), np.float32)
    rng = np.random.default_rng(3)
    d = ImageDraw.Draw(Image.fromarray((drip * 255).astype(np.uint8)))
    dim = Image.new('L', (W, H), 0)
    dd = ImageDraw.Draw(dim)
    ys, xs = np.nonzero(chewed > 0.5)
    for _ in range(26):
        i = rng.integers(0, len(xs))
        x, y = int(xs[i]), int(ys[i])
        if y < H * 0.45:
            continue
        ln = int(rng.integers(40, 330))
        wdt = int(rng.integers(5, 17))
        dd.rounded_rectangle([x - wdt, y, x + wdt, y + ln], radius=wdt, fill=255)
        dd.ellipse([x - wdt * 1.5, y + ln - wdt, x + wdt * 1.5, y + ln + wdt * 2], fill=255)
    chewed = np.clip(chewed + arr(dim), 0, 1)
    body = ink_key(body, M, (0.04, 0.04, 0.05))
    kk = arr(down(M['key']))
    alpha = np.clip(np.maximum(chewed * (0.45 + 0.70 * ink), kk), 0, 1)
    return compose(body, alpha)


def d03_nebula(M):
    """Deep space inside the blade: stars, nebula, a glowing rim."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    n1 = fbm((H, W), octaves=7, seed=21)
    n2 = fbm((H, W), octaves=6, seed=22)
    n3 = fbm((H, W), octaves=5, seed=23)
    cloud = np.clip(n1 * 1.35 - 0.25, 0, 1) ** 1.5
    r = 0.10 + 1.25 * cloud * np.clip(n2 * 1.3, 0, 1)
    g = 0.04 + 0.55 * cloud * np.clip(n3, 0, 1)
    b = 0.22 + 1.45 * cloud
    body = np.clip(np.dstack([r, g, b]), 0, 1)
    body = body * 0.55 + np.dstack([b * 0.5, g * 0.35, r * 0.9]) * 0.45
    rng = np.random.default_rng(24)
    stars = np.zeros((H, W), np.float32)
    for n, s in ((2600, 1.0), (700, 2.0), (120, 3.4)):
        ys = rng.integers(0, H, n); xs = rng.integers(0, W, n)
        stars[ys, xs] = np.maximum(stars[ys, xs], rng.random(n) ** 0.4 * s)
    stars = soft(np.clip(stars, 0, 1), 1.1) * 2.4
    body = np.clip(body + stars[..., None], 0, 1)
    pat = arr(tiled(checker_tile(110, (255, 255, 255), (0, 0, 0), (255, 255, 255)), 45))[..., 0]
    body = np.where((pat > 0.5)[..., None], body * 0.30, body)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.12, 0, 1), body)
    body = ink_key(body, M, (0.86, 0.80, 1.0))
    halo = soft(allm, 42) * 0.55
    glow = np.clip(halo[..., None] * np.array([0.35, 0.12, 0.85], np.float32), 0, 1)
    out = Image.fromarray((np.clip(body, 0, 1) * 255).astype(np.uint8), 'RGB')
    out.putalpha(Image.fromarray((np.clip(allm + halo * 0.55, 0, 1) * 255).astype(np.uint8)))
    bg = Image.fromarray((glow * 255).astype(np.uint8), 'RGB')
    bg.putalpha(Image.fromarray((np.clip(halo, 0, 1) * 255).astype(np.uint8)))
    bg.alpha_composite(out)
    return bg


def d04_riso(M):
    """Two-colour risograph: halftone, misregistration, paper tooth."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    def screen(angle, pitch):
        a = math.radians(angle)
        u = xx * math.cos(a) + yy * math.sin(a)
        v = -xx * math.sin(a) + yy * math.cos(a)
        return (np.sin(u * 2 * math.pi / pitch) * np.sin(v * 2 * math.pi / pitch) + 1) / 2

    shade = np.clip(0.35 + 0.65 * fbm((H, W), octaves=5, seed=31), 0, 1)
    pat = arr(tiled(checker_tile(108, (255, 255, 255), (0, 0, 0), (255, 255, 255)), 45))[..., 0]
    plate_a = ((shade * (0.35 + 0.65 * pat)) > screen(15, 11)) & (allm > 0.5)
    plate_b = ((shade * 0.75 * (1.1 - pat)) > screen(75, 13)) & (allm > 0.5)
    ink_a = np.array([232, 62, 54], np.float32) / 255
    ink_b = np.array([20, 42, 120], np.float32) / 255
    body = np.ones((H, W, 3), np.float32)
    A = np.roll(np.roll(plate_a, 7, 0), -9, 1)
    B = np.roll(np.roll(plate_b, -6, 0), 8, 1)
    body = np.where(A[..., None], body * ink_a, body)
    body = np.where(B[..., None], body * ink_b, body)
    tooth = fbm((H, W), octaves=8, seed=33)
    body = np.clip(body * (0.90 + 0.14 * tooth[..., None]), 0, 1)
    kk = arr(down(M['key']))
    body = body * (1 - kk[..., None]) + ink_b * kk[..., None]
    alpha = np.clip(A.astype(np.float32) + B.astype(np.float32) + kk, 0, 1)
    return compose(body, alpha)


def d05_chrome(M):
    """Liquid chrome: a hard horizon, warm sky, cold ground."""
    blade, handle, bolster, allm = (arr(down(M[k])) for k in
                                    ('blade', 'handle', 'bolster', 'all'))
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None].repeat(W, 1)
    wob = fbm((H, W), octaves=4, seed=41) * 0.10
    t = np.clip(yy + wob - 0.05, 0, 1)
    sky = np.dstack([0.18 + 0.75 * (1 - t), 0.30 + 0.62 * (1 - t), 0.52 + 0.46 * (1 - t)])
    ground = np.dstack([0.92 - 0.55 * t, 0.74 - 0.60 * t, 0.42 - 0.34 * t])
    horizon = (t > 0.52).astype(np.float32)
    body = sky * (1 - horizon[..., None]) + ground * horizon[..., None]
    band = np.exp(-((t - 0.52) ** 2) / (2 * 0.011 ** 2))
    body = np.clip(body + band[..., None] * 0.95, 0, 1)
    spec = np.exp(-((t - 0.20) ** 2) / (2 * 0.035 ** 2)) * 0.6
    body = np.clip(body + spec[..., None], 0, 1)
    body = np.where(handle[..., None] > 0.5,
                    np.clip(body * 0.14 + 0.03, 0, 1), body)
    body = np.where(bolster[..., None] > 0.5, np.clip(body * 1.1, 0, 1), body)
    return compose(ink_key(body, M), allm)


def d06_airbrush(M):
    """Eighties airbrush: flames behind, the blade dark against them."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * 0.44, H * 0.52
    r = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.60)) ** 2)
    th = np.arctan2(yy - cy, xx - cx)
    lick = 0.30 + 0.24 * np.sin(th * 7 + fbm((H, W), 4, 51) * 7.0)
    f = np.clip(1.0 - (r / np.clip(lick + 0.55, 0.1, 2)), 0, 1) ** 1.3
    f = soft(f, 9)
    body = np.zeros((H, W, 3), np.float32)
    stops = [(0.00, (18, 4, 40)), (0.30, (120, 10, 60)), (0.55, (228, 52, 24)),
             (0.78, (250, 160, 20)), (1.00, (255, 245, 190))]
    for i in range(len(stops) - 1):
        a0, c0 = stops[i]; a1, c1 = stops[i + 1]
        k = np.clip((f - a0) / (a1 - a0), 0, 1)
        m = ((f >= a0) & (f <= a1))[..., None]
        col = (np.array(c0, np.float32) * (1 - k[..., None]) +
               np.array(c1, np.float32) * k[..., None]) / 255.0
        body = np.where(m, col, body)
    halo = soft(np.clip(f, 0, 1), 26)
    body = np.where(allm[..., None] > 0.5, np.clip(body * 0.10, 0, 1), body)
    body = ink_key(body, M, (1.0, 0.90, 0.58))
    alpha = np.clip(np.maximum(allm, halo * 1.25) ** 0.85, 0, 1)
    return compose(body, alpha)


def d07_engraved(M):
    """Banknote engraving: hatching across the blade, ornament behind."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = np.clip(0.25 + 0.75 * fbm((H, W), 4, 61), 0, 1)
    a = math.radians(-58 + 90)
    u = xx * math.cos(a) + yy * math.sin(a)
    h1 = (np.sin(u * 2 * math.pi / 15) + 1) / 2
    a2 = math.radians(-58 + 150)
    u2 = xx * math.cos(a2) + yy * math.sin(a2)
    h2 = (np.sin(u2 * 2 * math.pi / 22) + 1) / 2
    ink = ((h1 < shade * 0.95) | (h2 < shade * 0.62)).astype(np.float32)
    pat = arr(tiled(checker_tile(112, (255, 255, 255), (0, 0, 0), (255, 255, 255)), 45))[..., 0]
    ink = np.where(pat > 0.5, 1.0 - ink * 0.25, ink)
    ink = np.where(handle > 0.5, 1.0, ink)
    orn = Image.new('L', (W, H), 0)
    do = ImageDraw.Draw(orn)
    ccx, ccy, rad = W * 0.52, H * 0.46, W * 0.36
    for k in range(3):
        rr = rad - k * 30
        do.ellipse([ccx - rr, ccy - rr * 1.22, ccx + rr, ccy + rr * 1.22],
                   outline=255, width=6 if k == 1 else 3)
    for k in range(64):
        t = k / 64 * 2 * math.pi
        px = ccx + math.cos(t) * rad * 1.06
        py = ccy + math.sin(t) * rad * 1.30
        do.ellipse([px - 13, py - 13, px + 13, py + 13], outline=255, width=4)
    ornf = arr(orn)
    # light ink on a clear ground: on a dark shirt an engraving has to be
    # the light, not the paper
    line = np.array([238, 231, 212], np.float32) / 255
    mark = np.clip(ornf * 0.85 + ink * allm + arr(down(M['key'])), 0, 1)
    body = np.ones((H, W, 3), np.float32) * line
    body = np.clip(body * (0.72 + 0.28 * mark[..., None]), 0, 1)
    return compose(body, mark)


def d08_glitch(M):
    """Channel split, scanlines and block displacement."""
    base = d01_checker(M).convert('RGB')
    a = np.asarray(base, np.float32) / 255
    al = arr(down(M['all']))
    rng = np.random.default_rng(81)
    out = a.copy()
    alo = al.copy()
    for _ in range(16):
        y0 = int(rng.integers(0, H - 10))
        hgt = int(rng.integers(6, 70))
        dx = int(rng.integers(-110, 110))
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], dx, axis=1)
        alo[y0:y0 + hgt] = np.roll(alo[y0:y0 + hgt], dx, axis=1)
    r = np.roll(out[..., 0], -16, 1)
    b = np.roll(out[..., 2], 16, 1)
    out = np.dstack([r, out[..., 1], b])
    ar = np.roll(alo, -16, 1); ab = np.roll(alo, 16, 1)
    alo = np.clip(np.maximum(np.maximum(alo, ar), ab), 0, 1)
    scan = (np.mgrid[0:H, 0:W][0] % 6 < 2).astype(np.float32)
    out = np.clip(out * (1 - scan[..., None] * 0.45), 0, 1)
    tint = np.array([1.0, 0.25, 0.55], np.float32)
    flash = (np.mgrid[0:H, 0:W][0] % 160 < 5).astype(np.float32) * alo
    out = np.clip(out + flash[..., None] * tint, 0, 1)
    return compose(out, alo)


def d09_blueprint(M):
    """Shop drawing: the machete dimensioned on blueprint ground."""
    blade, handle, allm = (arr(down(M[k])) for k in ('blade', 'handle', 'all'))
    edge = arr(down(M['key']))
    pat = arr(tiled(checker_tile(108, (255, 255, 255), (0, 0, 0), (255, 255, 255)), 45))[..., 0]
    pe = np.abs(np.gradient(pat)[0]) + np.abs(np.gradient(pat)[1])
    pe = np.clip(pe * 4, 0, 1) * allm
    grid = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    grid[(yy % 120 < 2) | (xx % 120 < 2)] = 0.22
    grid[(yy % 600 < 3) | (xx % 600 < 3)] = 0.40
    paper = np.array([12, 44, 96], np.float32) / 255
    ln = np.array([208, 226, 255], np.float32) / 255
    body = np.ones((H, W, 3), np.float32) * paper
    marks = np.clip(grid + edge + pe * 0.7, 0, 1)
    body = body * (1 - marks[..., None]) + ln * marks[..., None]
    im = Image.fromarray((body * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    col = (208, 226, 255)
    for (x0, y0, x1, y1) in ((150, 2960, 2250, 2960),):
        d.line([x0, y0, x1, y1], fill=col, width=4)
        for x in (x0, x1):
            d.line([x, y0 - 26, x, y0 + 26], fill=col, width=4)
    im2 = Image.new('RGBA', (W, H))
    im2.paste(im, (0, 0))
    im2.putalpha(255)
    return im2


def d10_allover(M):
    """The checker field warped across the whole print, knife knocked out."""
    allm = arr(down(M['all']))
    pat = arr(tiled(checker_tile(128, (238, 238, 234), (46, 48, 54), (238, 238, 234)), 45))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wobx = (np.sin(yy / 260.0) * 46 + fbm((H, W), 4, 91) * 60 - 30)
    woby = (np.cos(xx / 300.0) * 40 + fbm((H, W), 4, 92) * 60 - 30)
    sx = np.clip(xx + wobx, 0, W - 1).astype(np.int32)
    sy = np.clip(yy + woby, 0, H - 1).astype(np.int32)
    body = pat[sy, sx]
    knock = allm
    body = body * (1 - knock[..., None]) + np.array([0.06, 0.06, 0.07], np.float32) * knock[..., None]
    body = ink_key(body, M, (0.97, 0.97, 0.96))
    halo = np.clip(soft(allm, 26) - allm, 0, 1)
    body = np.clip(body + halo[..., None] * 0.65, 0, 1)
    vig = np.clip(1.25 - np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 +
                                 ((yy - H / 2) / (H * 0.64)) ** 2), 0, 1)
    alpha = np.clip(vig ** 0.7, 0, 1)
    return compose(body, alpha)


# name, label, renderer, (angle, crossed, margin)
DESIGNS = [
    ('01-checker', 'Checker', d01_checker, (-61, False, 0.07)),
    ('02-painted', 'Painted', d02_painted, (-80, False, 0.05)),
    ('03-nebula', 'Spacey', d03_nebula, (-61, False, 0.09)),
    ('04-riso', 'Risograph', d04_riso, (-58, True, 0.06)),
    ('05-chrome', 'Chrome', d05_chrome, (-90, False, 0.05)),
    ('06-airbrush', 'Airbrush', d06_airbrush, (-61, False, 0.12)),
    ('07-engraved', 'Engraved', d07_engraved, (-58, True, 0.10)),
    ('08-glitch', 'Glitch', d08_glitch, (-61, False, 0.08)),
    ('09-blueprint', 'Blueprint', d09_blueprint, (-90, False, 0.09)),
    ('10-allover', 'All-over', d10_allover, (-66, False, 0.10)),
]


def contact(images, path, shirt=(30, 30, 32)):
    cols, rows = 5, 2
    cw, ch = 520, 700
    pad, lab = 26, 34
    sheet = Image.new('RGB', (cols * cw + pad * (cols + 1),
                              rows * (ch + lab) + pad * (rows + 1)), (18, 18, 20))
    d = ImageDraw.Draw(sheet)
    for i, (name, title, im) in enumerate(images):
        c, r = i % cols, i // cols
        x = pad + c * (cw + pad)
        y = pad + r * (ch + lab + pad)
        card = Image.new('RGB', (cw, ch), shirt)
        t = im.copy()
        t.thumbnail((cw - 40, ch - 40), Image.LANCZOS)
        card.paste(t, ((cw - t.size[0]) // 2, (ch - t.size[1]) // 2), t)
        sheet.paste(card, (x, y))
        d.text((x + 2, y + ch + 9), f'{name}  ·  {title}', fill=(190, 190, 195))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='assets/machete-tees')
    ap.add_argument('--only', default=None, help='comma-separated design keys')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    keep = set(a.only.split(',')) if a.only else None
    made = []
    for name, title, fn, (deg, crossed, margin) in DESIGNS:
        if keep and name.split('-')[0] not in keep and name not in keep:
            continue
        M = {k: down(v) for k, v in
             masks(SS, deg=deg, crossed=crossed, margin=margin).items()}
        im = fn(M)
        p = os.path.join(a.out, f'machete-{name}.png')
        im.save(p)
        made.append((name, title, im))
        print(f'{p}  {im.size[0]}x{im.size[1]}')
    if len(made) == len(DESIGNS):
        cp = os.path.join(a.out, 'machete-contact-sheet.png')
        contact(made, cp)
        print(f'{cp}')


if __name__ == '__main__':
    main()
