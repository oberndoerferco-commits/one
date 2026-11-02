#!/usr/bin/env python3
"""Twenty t-shirt designs built on the client's machete and the OM motif.

The blade and the handle are the client's reference machete, traced from it:
the silhouette was lifted, straightened on its principal axis, split at the
bolster and simplified, with the two long runs of the blade snapped dead
straight so the lines stay crisp at print size.

The pattern is the client's own: the OM cross from motif-grey-black.pdf and
the O/M monogram from om-colour.pdf, both off their Canva, laid on the
diagonal checkerboard of the reference.

Each design is 2400 x 3200 px = 8 x 10.67 in at 300 dpi, RGBA on a clear
ground so it drops onto any shirt colour.

    python3 scripts/machete_tees.py --out assets/machete-tees
"""
import argparse, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 2400, 3200
SS = 2
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'assets', 'machete-tees', 'art')

# ------------------------------------------------- the reference machete
# Blade-space: x 0 at the bolster, 1 at the tip; y up, same scale.
BLADE = [(0.0, 0.0649), (0.055, 0.0567), (0.78, 0.0968), (0.8101, 0.0889),
         (0.8353, 0.0781), (0.8714, 0.0769), (0.9099, 0.0577), (0.9363, 0.0385),
         (0.9471, 0.0361), (0.9712, 0.0024), (0.9808, -0.0192), (0.9964, -0.0589),
         (0.9988, -0.0865), (1.0, -0.0913), (0.8, -0.0861), (0.04, -0.0651),
         (0.0, -0.0841)]
HANDLE = [(-0.3738, 0.0288), (-0.3678, 0.0601), (-0.3498, 0.0709),
          (-0.3137, 0.0685), (-0.2885, 0.0565), (-0.2296, 0.0649),
          (-0.1695, 0.0649), (-0.0673, 0.0541), (-0.0409, 0.0733),
          (-0.0156, 0.0733), (0.0, 0.0649), (0.0, -0.0841), (-0.0325, -0.0925),
          (-0.0589, -0.0769), (-0.0721, -0.0757), (-0.3365, -0.0757),
          (-0.351, -0.0637), (-0.3618, -0.0433), (-0.3738, 0.0216)]
KEY = 0.0060                      # keyline width, as a fraction of blade length


def place(pts, cx, cy, length, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x * length) * ca - (-y * length) * sa,
             cy + (x * length) * sa + (-y * length) * ca) for x, y in pts]


def masks(scale=1, deg=-61.0, margin=0.07, crossed=False):
    """Blade and handle fills, the heavy keyline, and the outer silhouette."""
    w, h = W * scale, H * scale
    polys = {'blade': BLADE, 'handle': HANDLE}
    angles = [deg, 180 - deg] if crossed else [deg]
    probe = [p for g in angles for q in polys.values()
             for p in place(q, 0.0, 0.0, 1.0, g)]
    xs = [p[0] for p in probe]; ys = [p[1] for p in probe]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    pad = 1.0 + KEY * 2
    length = min(w * (1 - 2 * margin) / (bw * pad), h * (1 - 2 * margin) / (bh * pad))
    cx = w / 2 - (min(xs) + bw / 2) * length
    cy = h / 2 - (min(ys) + bh / 2) * length
    kw = max(3, int(round(KEY * length)))

    out = {k: Image.new('L', (w, h), 0) for k in polys}
    key = Image.new('L', (w, h), 0)
    dk = ImageDraw.Draw(key)
    for g in angles:
        for name, poly in polys.items():
            P = place(poly, cx, cy, length, g)
            im = Image.new('L', (w, h), 0)
            ImageDraw.Draw(im).polygon(P, fill=255)
            out[name] = ImageChops.lighter(out[name], im)
            dk.line(P + [P[0]], fill=255, width=kw, joint='curve')
    out['key'] = key
    out['all'] = ImageChops.lighter(ImageChops.lighter(out['blade'], out['handle']),
                                    key)
    return out


def down(im):
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


def arr(im):
    return np.asarray(im, dtype=np.float32) / 255.0


# ------------------------------------------------------- the OM pattern

_MOTIF = {}


def motif(name):
    if name not in _MOTIF:
        _MOTIF[name] = Image.open(os.path.join(ART, f'{name}_mask.png')).convert('L')
    return _MOTIF[name]


def paste_motif(tile, name, cx, cy, span, col):
    """Drop one brand mark, scaled to `span` across, centred on (cx, cy)."""
    m = motif(name)
    w0, h0 = m.size
    k = span / float(w0)
    nw, nh = max(1, int(w0 * k)), max(1, int(h0 * k))
    m = m.resize((nw, nh), Image.LANCZOS)
    tile.paste(Image.new('RGB', (nw, nh), col),
               (int(cx - nw / 2), int(cy - nh / 2)), m)


def pattern_tile(cell, light, dark, ink):
    """Two cells square: checker, with the cross and the OM on the pale cells."""
    t = Image.new('RGB', (cell * 2, cell * 2), dark)
    d = ImageDraw.Draw(t)
    d.rectangle([0, 0, cell - 1, cell - 1], fill=light)
    d.rectangle([cell, cell, cell * 2 - 1, cell * 2 - 1], fill=light)
    paste_motif(t, 'cross', cell * 0.5, cell * 0.5, cell * 0.54, ink)
    paste_motif(t, 'om', cell * 1.5, cell * 1.5, cell * 0.72, ink)
    return t


def tiled(tile, angle=45.0, size=(W, H)):
    big = int(math.hypot(*size) * 1.3)
    reps = big // tile.size[0] + 2
    sheet = Image.new('RGB', (tile.size[0] * reps, tile.size[1] * reps))
    for i in range(reps):
        for j in range(reps):
            sheet.paste(tile, (i * tile.size[0], j * tile.size[1]))
    sheet = sheet.rotate(angle, resample=Image.BICUBIC, expand=False)
    x = (sheet.size[0] - size[0]) // 2
    y = (sheet.size[1] - size[1]) // 2
    return sheet.crop((x, y, x + size[0], y + size[1]))


def pattern(cell=120, light=(236, 236, 232), dark=(118, 121, 126),
            ink=(38, 39, 43), angle=45.0):
    return arr(tiled(pattern_tile(cell, light, dark, ink), angle))


def pat_mono(cell=120, angle=45.0):
    """The pattern as one channel: 1 on the pale cells and off the marks."""
    return pattern(cell, (255, 255, 255), (0, 0, 0), (0, 0, 0), angle)[..., 0]


# ----------------------------------------------------------- helpers

def fbm(shape, octaves=6, seed=0, persistence=0.55):
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


def soft(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def flat(shape, colour):
    return np.dstack([np.full(shape, colour[i] / 255.0, np.float32) for i in range(3)])


def ink_key(body, M, col=(0.05, 0.05, 0.06)):
    k = arr(down(M['key']))[..., None]
    return body * (1 - k) + np.array(col, np.float32) * k


def compose(body, alpha):
    out = Image.fromarray((np.clip(body, 0, 1) * 255).astype(np.uint8), 'RGB')
    out.putalpha(Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8)))
    return out


def parts(M):
    return (arr(down(M['blade'])), arr(down(M['handle'])), arr(down(M['all'])))


# ------------------------------------------------------------ designs

def d01_checker(M):
    blade, handle, allm = parts(M)
    body = pattern() * blade[..., None]
    body += flat((H, W), (18, 18, 20)) * handle[..., None] * (1 - blade[..., None])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = xx * math.cos(a) + yy * math.sin(a)
    band = ((u % 560 < 86) | ((u + 270) % 560 < 40)).astype(np.float32) * blade
    body = np.clip(body + band[..., None] * 0.20, 0, 1)
    return compose(ink_key(body, M), allm)


def d02_painted(M):
    blade, handle, allm = parts(M)
    grain = fbm((H, W), 7, 11)
    streak = soft(fbm((H, W), 4, 12, 0.8), 1)
    ink = np.clip(0.42 + 1.25 * (grain * 0.40 + streak * 0.60) - 0.34, 0, 1)
    body = flat((H, W), (14, 13, 16)) * (0.35 + 0.65 * ink[..., None])
    pm = pat_mono()
    body = np.where((blade * pm > 0.5)[..., None],
                    flat((H, W), (176, 42, 38)) * 0.85 + body * 0.15, body)
    drips = Image.new('L', (W, H), 0)
    dd = ImageDraw.Draw(drips)
    rng = np.random.default_rng(3)
    ys, xs = np.nonzero(allm > 0.5)
    for _ in range(24):
        i = rng.integers(0, len(xs)); x, y = int(xs[i]), int(ys[i])
        if y < H * 0.45:
            continue
        ln = int(rng.integers(50, 340)); wd = int(rng.integers(5, 16))
        dd.rounded_rectangle([x - wd, y, x + wd, y + ln], radius=wd, fill=255)
    body = ink_key(body, M, (0.04, 0.04, 0.05))
    alpha = np.maximum(allm * (0.45 + 0.70 * ink), arr(drips) * 0.9)
    return compose(body, np.clip(np.maximum(alpha, arr(down(M['key']))), 0, 1))


def d03_nebula(M):
    blade, handle, allm = parts(M)
    cloud = np.clip(fbm((H, W), 7, 21) * 1.35 - 0.25, 0, 1) ** 1.5
    r = 0.10 + 1.25 * cloud * np.clip(fbm((H, W), 6, 22) * 1.3, 0, 1)
    g = 0.04 + 0.55 * cloud * fbm((H, W), 5, 23)
    b = 0.22 + 1.45 * cloud
    body = np.clip(np.dstack([r, g, b]), 0, 1)
    rng = np.random.default_rng(24)
    stars = np.zeros((H, W), np.float32)
    for n, s in ((2600, 1.0), (700, 2.0), (120, 3.4)):
        ys = rng.integers(0, H, n); xs = rng.integers(0, W, n)
        stars[ys, xs] = np.maximum(stars[ys, xs], rng.random(n) ** 0.4 * s)
    body = np.clip(body + (soft(np.clip(stars, 0, 1), 1.1) * 2.4)[..., None], 0, 1)
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], body * 0.28, body)
    body = np.where(handle[..., None] > 0.5, body * 0.12, body)
    body = ink_key(body, M, (0.86, 0.80, 1.0))
    halo = soft(allm, 42) * 0.55
    bg = compose(np.clip(halo[..., None] * np.array([0.35, 0.12, 0.85], np.float32), 0, 1),
                 np.clip(halo, 0, 1))
    bg.alpha_composite(compose(body, allm))
    return bg


def d04_riso(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    def screen(angle, pitch):
        a = math.radians(angle)
        u = xx * math.cos(a) + yy * math.sin(a)
        v = -xx * math.sin(a) + yy * math.cos(a)
        return (np.sin(u * 2 * math.pi / pitch) * np.sin(v * 2 * math.pi / pitch) + 1) / 2

    shade = np.clip(0.35 + 0.65 * fbm((H, W), 5, 31), 0, 1)
    pm = pat_mono()
    A = ((shade * (0.35 + 0.65 * pm)) > screen(15, 11)) & (allm > 0.5)
    B = ((shade * 0.75 * (1.1 - pm)) > screen(75, 13)) & (allm > 0.5)
    A = np.roll(np.roll(A, 7, 0), -9, 1); B = np.roll(np.roll(B, -6, 0), 8, 1)
    ia = np.array([232, 62, 54], np.float32) / 255
    ib = np.array([20, 42, 120], np.float32) / 255
    body = np.ones((H, W, 3), np.float32)
    body = np.where(A[..., None], body * ia, body)
    body = np.where(B[..., None], body * ib, body)
    body = np.clip(body * (0.90 + 0.14 * fbm((H, W), 8, 33)[..., None]), 0, 1)
    kk = arr(down(M['key']))
    body = body * (1 - kk[..., None]) + ib * kk[..., None]
    return compose(body, np.clip(A + B + kk, 0, 1))


def d05_chrome(M):
    blade, handle, allm = parts(M)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None].repeat(W, 1)
    t = np.clip(yy + fbm((H, W), 4, 41) * 0.10 - 0.05, 0, 1)
    sky = np.dstack([0.18 + 0.75 * (1 - t), 0.30 + 0.62 * (1 - t), 0.52 + 0.46 * (1 - t)])
    ground = np.dstack([0.92 - 0.55 * t, 0.74 - 0.60 * t, 0.42 - 0.34 * t])
    hz = (t > 0.52).astype(np.float32)
    body = sky * (1 - hz[..., None]) + ground * hz[..., None]
    body = np.clip(body + (np.exp(-((t - 0.52) ** 2) / (2 * 0.011 ** 2)))[..., None] * 0.95, 0, 1)
    body = np.clip(body + (np.exp(-((t - 0.20) ** 2) / (2 * 0.035 ** 2)) * 0.6)[..., None], 0, 1)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.14 + 0.03, 0, 1), body)
    return compose(ink_key(body, M), allm)


def d06_airbrush(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * 0.44, H * 0.52
    r = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.60)) ** 2)
    th = np.arctan2(yy - cy, xx - cx)
    lick = 0.30 + 0.24 * np.sin(th * 7 + fbm((H, W), 4, 51) * 7.0)
    f = soft(np.clip(1.0 - (r / np.clip(lick + 0.55, 0.1, 2)), 0, 1) ** 1.3, 9)
    body = np.zeros((H, W, 3), np.float32)
    stops = [(0.00, (18, 4, 40)), (0.30, (120, 10, 60)), (0.55, (228, 52, 24)),
             (0.78, (250, 160, 20)), (1.00, (255, 245, 190))]
    for i in range(len(stops) - 1):
        a0, c0 = stops[i]; a1, c1 = stops[i + 1]
        k = np.clip((f - a0) / (a1 - a0), 0, 1)[..., None]
        m = ((f >= a0) & (f <= a1))[..., None]
        body = np.where(m, (np.array(c0, np.float32) * (1 - k) +
                            np.array(c1, np.float32) * k) / 255.0, body)
    halo = soft(np.clip(f, 0, 1), 26)
    body = np.where(allm[..., None] > 0.5, np.clip(body * 0.10, 0, 1), body)
    body = ink_key(body, M, (1.0, 0.90, 0.58))
    return compose(body, np.clip(np.maximum(allm, halo * 1.25) ** 0.85, 0, 1))


def d07_engraved(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = np.clip(0.25 + 0.75 * fbm((H, W), 4, 61), 0, 1)
    a = math.radians(32)
    h1 = (np.sin((xx * math.cos(a) + yy * math.sin(a)) * 2 * math.pi / 15) + 1) / 2
    a2 = math.radians(92)
    h2 = (np.sin((xx * math.cos(a2) + yy * math.sin(a2)) * 2 * math.pi / 22) + 1) / 2
    ink = ((h1 < shade * 0.95) | (h2 < shade * 0.62)).astype(np.float32)
    pm = pat_mono()
    ink = np.where(pm > 0.5, 1.0 - ink * 0.25, ink)
    ink = np.where(handle > 0.5, 1.0, ink)
    orn = Image.new('L', (W, H), 0)
    do = ImageDraw.Draw(orn)
    ccx, ccy, rad = W * 0.52, H * 0.46, W * 0.36
    for k in range(3):
        rr = rad - k * 30
        do.ellipse([ccx - rr, ccy - rr * 1.22, ccx + rr, ccy + rr * 1.22],
                   outline=255, width=7 if k == 1 else 4)
    for k in range(64):
        t = k / 64 * 2 * math.pi
        px, py = ccx + math.cos(t) * rad * 1.06, ccy + math.sin(t) * rad * 1.30
        do.ellipse([px - 13, py - 13, px + 13, py + 13], outline=255, width=5)
    mark = np.clip(arr(orn) * 0.85 + ink * allm + arr(down(M['key'])), 0, 1)
    body = np.ones((H, W, 3), np.float32) * (np.array([238, 231, 212], np.float32) / 255)
    return compose(np.clip(body * (0.72 + 0.28 * mark[..., None]), 0, 1), mark)


def d08_glitch(M):
    a = np.asarray(d01_checker(M).convert('RGB'), np.float32) / 255
    al = arr(down(M['all']))
    rng = np.random.default_rng(81)
    out, alo = a.copy(), al.copy()
    for _ in range(16):
        y0 = int(rng.integers(0, H - 10)); hgt = int(rng.integers(6, 70))
        dx = int(rng.integers(-110, 110))
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], dx, axis=1)
        alo[y0:y0 + hgt] = np.roll(alo[y0:y0 + hgt], dx, axis=1)
    out = np.dstack([np.roll(out[..., 0], -16, 1), out[..., 1], np.roll(out[..., 2], 16, 1)])
    alo = np.clip(np.maximum(np.maximum(alo, np.roll(alo, -16, 1)), np.roll(alo, 16, 1)), 0, 1)
    scan = (np.mgrid[0:H, 0:W][0] % 6 < 2).astype(np.float32)
    out = np.clip(out * (1 - scan[..., None] * 0.45), 0, 1)
    flash = (np.mgrid[0:H, 0:W][0] % 160 < 5).astype(np.float32) * alo
    return compose(np.clip(out + flash[..., None] * np.array([1.0, .25, .55], np.float32), 0, 1), alo)


def d09_blueprint(M):
    blade, handle, allm = parts(M)
    edge = arr(down(M['key']))
    pm = pat_mono()
    pe = np.clip((np.abs(np.gradient(pm)[0]) + np.abs(np.gradient(pm)[1])) * 4, 0, 1) * allm
    grid = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    grid[(yy % 120 < 2) | (xx % 120 < 2)] = 0.22
    grid[(yy % 600 < 3) | (xx % 600 < 3)] = 0.40
    marks = np.clip(grid + edge + pe * 0.7, 0, 1)
    body = np.ones((H, W, 3), np.float32) * (np.array([12, 44, 96], np.float32) / 255)
    ln = np.array([208, 226, 255], np.float32) / 255
    body = body * (1 - marks[..., None]) + ln * marks[..., None]
    im = Image.fromarray((body * 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    d.line([150, 2980, 2250, 2980], fill=(208, 226, 255), width=4)
    for x in (150, 2250):
        d.line([x, 2954, x, 3006], fill=(208, 226, 255), width=4)
    im = im.convert('RGBA'); im.putalpha(255)
    return im


def d10_allover(M):
    allm = arr(down(M['all']))
    pat = pattern(128, (238, 238, 234), (46, 48, 54), (238, 238, 234))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sx = np.clip(xx + np.sin(yy / 260.0) * 46 + fbm((H, W), 4, 91) * 60 - 30, 0, W - 1).astype(np.int32)
    sy = np.clip(yy + np.cos(xx / 300.0) * 40 + fbm((H, W), 4, 92) * 60 - 30, 0, H - 1).astype(np.int32)
    body = pat[sy, sx]
    body = body * (1 - allm[..., None]) + np.array([.06, .06, .07], np.float32) * allm[..., None]
    body = ink_key(body, M, (0.97, 0.97, 0.96))
    halo = np.clip(soft(allm, 26) - allm, 0, 1)
    body = np.clip(body + halo[..., None] * 0.65, 0, 1)
    vig = np.clip(1.25 - np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .64)) ** 2), 0, 1)
    return compose(body, np.clip(vig ** 0.7, 0, 1))


def d11_sketch(M):
    """Ballpoint: looping hatch, a doubled-back outline, the pattern sketched in."""
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wob = fbm((H, W), 5, 111) * 26 - 13
    shade = np.clip(0.30 + 0.70 * fbm((H, W), 4, 112), 0, 1)
    pm = pat_mono()
    dens = np.where(pm > 0.5, 0.30, 0.78) * shade
    dens = np.where(handle > 0.5, 0.92, dens)
    lines = np.zeros((H, W), np.float32)
    for a_deg, pitch, w8 in ((34, 19, 1.0), (-52, 27, 0.75), (8, 41, 0.5)):
        a = math.radians(a_deg)
        u = (xx + wob) * math.cos(a) + (yy - wob) * math.sin(a)
        lines = np.maximum(lines, (((u % pitch) / pitch) < dens * 0.55).astype(np.float32) * w8)
    lines *= allm
    ks = arr(down(M['key']))
    ol = np.maximum(np.roll(np.roll(ks, 6, 0), 4, 1), np.roll(np.roll(ks, -5, 0), -7, 1))
    mark = np.clip(lines * 0.85 + np.maximum(ks, ol * 0.75), 0, 1)
    mark = mark * (0.55 + 0.45 * fbm((H, W), 8, 113))
    # pale ballpoint, so it reads as pencil on a dark shirt rather than
    # vanishing into it
    body = np.ones((H, W, 3), np.float32) * (np.array([206, 218, 242], np.float32) / 255)
    return compose(np.clip(body * (0.70 + 0.30 * mark[..., None]), 0, 1),
                   np.clip(mark * 2.1, 0, 1))


def d12_metal(M):
    """The patch read as metal: brushed steel with the motif struck into it."""
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = xx * math.cos(a) + yy * math.sin(a)
    brush = np.sin(u * 0.9 + fbm((H, W), 7, 121) * 26) * 0.5 + 0.5
    base = 0.46 + 0.30 * brush + 0.22 * np.clip(fbm((H, W), 3, 122), 0, 1)
    pm = pat_mono()
    gy, gx = np.gradient(soft(pm, 2.0))
    relief = np.clip((gx * -0.62 + gy * -0.78) * 46, -1, 1)
    steel = np.clip(base + relief * 0.55, 0, 1)
    steel = np.where(pm > 0.5, steel * 0.80, steel * 1.06)
    body = np.dstack([steel * 1.00, steel * 1.01, steel * 1.06])
    body = np.clip(body + (np.clip(relief, 0, 1) ** 2)[..., None] * 0.55, 0, 1)
    body = np.where(handle[..., None] > 0.5,
                    np.clip(np.dstack([steel, steel, steel]) * 0.22 + 0.04, 0, 1), body)
    return compose(ink_key(body, M, (0.08, 0.09, 0.11)), allm)


def d13_woodcut(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = np.clip(0.18 + 0.82 * fbm((H, W), 3, 131), 0, 1)
    pm = pat_mono()
    dens = np.where(pm > 0.5, 0.20, 0.80) * shade
    a = math.radians(29)
    u = xx * math.cos(a) + yy * math.sin(a)
    pitch = 26 + 16 * fbm((H, W), 3, 132)
    cut = (((u % pitch) / pitch) < dens).astype(np.float32) * allm
    mark = np.clip(cut + arr(down(M['key'])), 0, 1)
    body = np.ones((H, W, 3), np.float32) * (np.array([236, 228, 210], np.float32) / 255)
    return compose(body, mark)


def d14_neon(M):
    blade, handle, allm = parts(M)
    k = arr(down(M['key']))
    pm = pat_mono() * allm
    pe = np.clip((np.abs(np.gradient(pm)[0]) + np.abs(np.gradient(pm)[1])) * 5, 0, 1)
    tube = np.clip(k + pe * 0.75, 0, 1)
    glow = soft(tube, 10) * 1.5 + soft(tube, 34) * 0.9 + soft(tube, 70) * 0.5
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    col = np.array([1.00, 0.18, 0.62], np.float32) * (1 - t) + \
          np.array([0.20, 0.85, 1.00], np.float32) * t
    body = np.clip(glow[..., None] * col + tube[..., None] * 0.95, 0, 1)
    return compose(body, np.clip(np.maximum(tube, glow * 0.55), 0, 1))


def d15_camo(M):
    blade, handle, allm = parts(M)
    n = fbm((H, W), 5, 151)
    cols = [(36, 42, 30), (74, 83, 56), (120, 126, 92), (28, 30, 26)]
    edges = [0.0, 0.34, 0.56, 0.78, 1.01]
    body = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate(cols):
        m = ((n >= edges[i]) & (n < edges[i + 1]))[..., None]
        body = np.where(m, np.array(c, np.float32) / 255, body)
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.45 + 0.06, 0, 1), body)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.35, 0, 1), body)
    return compose(ink_key(body, M, (0.06, 0.07, 0.05)), allm)


def d16_damascus(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = xx * math.cos(a) + yy * math.sin(a) + fbm((H, W), 5, 161) * 150
    bands = (np.sin(u * 2 * math.pi / 46) * 0.5 + 0.5) ** 0.7
    steel = 0.22 + 0.62 * bands
    pm = pat_mono()
    steel = np.where(pm > 0.5, np.clip(steel * 1.5 + 0.12, 0, 1), steel * 0.78)
    body = np.dstack([steel * 1.02, steel * 1.0, steel * 0.96])
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.20, 0, 1), body)
    return compose(ink_key(body, M, (0.05, 0.05, 0.06)), allm)


def d17_glass(M):
    blade, handle, allm = parts(M)
    pm = pat_mono()
    n = fbm((H, W), 4, 171)
    pal = [(196, 42, 52), (232, 162, 32), (28, 86, 160), (26, 128, 96), (214, 214, 206)]
    body = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate(pal):
        m = ((n >= i / len(pal)) & (n < (i + 1) / len(pal)))[..., None]
        body = np.where(m, np.array(c, np.float32) / 255, body)
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.25, 0, 1), body * 0.72)
    lead = np.clip((np.abs(np.gradient(pm)[0]) + np.abs(np.gradient(pm)[1])) * 6, 0, 1)
    lead = np.clip(soft(lead, 1.6) * 2.2, 0, 1) * allm
    body = body * (1 - lead[..., None]) + np.array([.07, .07, .08], np.float32) * lead[..., None]
    body = np.where(handle[..., None] > 0.5, np.array([.08, .08, .09], np.float32), body)
    return compose(ink_key(body, M, (0.05, 0.05, 0.06)), allm)


def d18_holo(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = (xx * math.cos(a) + yy * math.sin(a)) / 1100.0 + fbm((H, W), 4, 181) * 0.6
    body = np.dstack([0.5 + 0.5 * np.sin(u * 6.283),
                      0.5 + 0.5 * np.sin(u * 6.283 + 2.09),
                      0.5 + 0.5 * np.sin(u * 6.283 + 4.19)])
    body = np.clip(body ** 0.75, 0, 1)
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.25 + 0.12, 0, 1), body * 0.55)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.18 + 0.03, 0, 1), body)
    return compose(ink_key(body, M, (0.05, 0.05, 0.07)), allm)


def d19_stencil(M):
    """Two tones only: the pattern knocked out of a solid blade."""
    blade, handle, allm = parts(M)
    pm = pat_mono()
    body = np.ones((H, W, 3), np.float32) * (np.array([244, 242, 236], np.float32) / 255)
    cut = np.where(blade > 0.5, pm, 0.0)
    alpha = np.clip(np.maximum(allm - cut * blade, arr(down(M['key']))), 0, 1)
    return compose(body, alpha)


def d20_tartan(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(45)
    u = xx * math.cos(a) + yy * math.sin(a)
    v = -xx * math.sin(a) + yy * math.cos(a)

    def stripe(t):
        s = t % 300
        out = np.where(s < 150, 0.35, 0.0)
        out = np.where((s >= 150) & (s < 210), 0.82, out)
        out = np.where((s >= 210) & (s < 232), 0.08, out)
        return np.where(s >= 232, 0.58, out)

    weave = (stripe(u) + stripe(v)) / 2
    base = np.array([112, 18, 24], np.float32) / 255
    body = np.clip(base[None, None, :] * (0.35 + 1.5 * weave[..., None]), 0, 1)
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.35 + 0.10, 0, 1), body)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.22, 0, 1), body)
    return compose(ink_key(body, M, (0.06, 0.05, 0.06)), allm)


# --------------------------------------------------- the second ten

def d21_duotone(M):
    """Two inks, straight gradient, the pattern holding the midtones."""
    blade, handle, allm = parts(M)
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    c1 = np.array([250, 86, 32], np.float32) / 255
    c2 = np.array([22, 24, 70], np.float32) / 255
    body = c1 * (1 - t) + c2 * t
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.6 + 0.10, 0, 1), body * 0.72)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.30, 0, 1), body)
    return compose(ink_key(body, M, (0.05, 0.05, 0.10)), allm)


def d22_leopard(M):
    blade, handle, allm = parts(M)
    n = fbm((H, W), 6, 221)
    rosette = ((n > 0.52) & (n < 0.66)).astype(np.float32)
    rosette = np.maximum(rosette, ((n > 0.74) & (n < 0.80)).astype(np.float32) * 0.8)
    tan = np.array([206, 150, 60], np.float32) / 255
    body = np.ones((H, W, 3), np.float32) * tan
    body = body * (1 - rosette[..., None]) + np.array([.12, .09, .06], np.float32) * rosette[..., None]
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.25 + 0.08, 0, 1), body * 0.80)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.22, 0, 1), body)
    return compose(ink_key(body, M, (0.06, 0.05, 0.04)), allm)


def d23_marble(M):
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    swirl = np.sin(xx / 150.0 + fbm((H, W), 5, 231) * 11) * 0.5 + 0.5
    vein = np.abs(swirl - 0.5)
    vein = np.clip(1 - vein * 7, 0, 1)
    body = np.ones((H, W, 3), np.float32) * (np.array([238, 236, 230], np.float32) / 255)
    body = body * (1 - vein[..., None]) + np.array([.12, .14, .22], np.float32) * vein[..., None]
    pm = pat_mono()
    body = np.where((pm > 0.5)[..., None], np.clip(body * 1.1, 0, 1), body * 0.68)
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.20, 0, 1), body)
    return compose(ink_key(body, M, (0.05, 0.06, 0.09)), allm)


def d24_jacquard(M):
    """Read as woven cloth: a warp and weft crossing under the motif."""
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(45)
    u = xx * math.cos(a) + yy * math.sin(a)
    v = -xx * math.sin(a) + yy * math.cos(a)
    warp = (np.sin(u * 2 * math.pi / 9) * 0.5 + 0.5)
    weft = (np.sin(v * 2 * math.pi / 9) * 0.5 + 0.5)
    over = (np.floor(u / 9) + np.floor(v / 9)) % 2
    weave = np.where(over > 0.5, warp, weft)
    pm = pat_mono()
    base = np.where(pm > 0.5, 0.82, 0.30)
    th = np.clip(base * (0.70 + 0.52 * weave), 0, 1)
    body = np.dstack([th * 1.00, th * 0.99, th * 0.95])
    body = np.where(handle[..., None] > 0.5, np.clip(body * 0.20, 0, 1), body)
    return compose(ink_key(body, M, (0.05, 0.05, 0.06)), allm)


def d25_gold(M):
    """Foil on black, the way the trunks are stamped."""
    blade, handle, allm = parts(M)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(29)
    u = (xx * math.cos(a) + yy * math.sin(a)) / 700.0
    sheen = 0.55 + 0.45 * np.sin(u * 6.283 + fbm((H, W), 4, 251) * 3.0)
    gold = np.dstack([0.52 + 0.46 * sheen, 0.36 + 0.42 * sheen, 0.10 + 0.22 * sheen])
    pm = pat_mono()
    mark = np.where(blade > 0.5, pm, 0.0)
    k = arr(down(M['key']))
    body = np.clip(gold, 0, 1)
    alpha = np.clip(np.maximum(mark * blade, k), 0, 1)
    return compose(body, alpha)


def d26_repeat(M):
    """The knife as a border print: a column of them, small and ranked."""
    blade, handle, allm = parts(M)
    tile = np.asarray(d01_checker(M).convert('RGBA'), np.float32) / 255
    out = np.zeros((H, W, 4), np.float32)
    small = Image.fromarray((tile * 255).astype(np.uint8), 'RGBA')
    sw, sh = int(W * 0.46), int(H * 0.46)
    small = small.resize((sw, sh), Image.LANCZOS)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for r in range(3):
        for c in range(3):
            x = int(c * (W - sw) / 2) + (40 if r % 2 else -40)
            y = int(r * (H - sh) / 2)
            canvas.alpha_composite(small, (max(0, min(W - sw, x)), y))
    return canvas


def d27_xray(M):
    blade, handle, allm = parts(M)
    pm = pat_mono()
    body = np.ones((H, W, 3), np.float32) * (np.array([150, 232, 214], np.float32) / 255)
    core = np.clip(soft(allm, 18) * 1.4, 0, 1)
    alpha = np.clip(core * 0.42 + np.where(blade > 0.5, 1 - pm, 0) * 0.55
                    + arr(down(M['key'])), 0, 1)
    return compose(body, alpha)


# ---- the three that need the client's Progetto Campione poem -----------
POEM = None          # set to the poem text to render designs 28-30


def _poem_lines():
    if not POEM:
        return None
    return [l.strip() for l in POEM.strip().splitlines() if l.strip()]


def d28_poem_column(M):
    raise NotImplementedError('needs POEM')


def d29_poem_blade(M):
    raise NotImplementedError('needs POEM')


def d30_poem_ring(M):
    raise NotImplementedError('needs POEM')


# name, label, renderer, (angle, crossed, margin)
DESIGNS = [
    ('01-checker', 'Checker', d01_checker, (-61, False, 0.07)),
    ('02-painted', 'Painted', d02_painted, (-80, False, 0.05)),
    ('03-spacey', 'Spacey', d03_nebula, (-61, False, 0.09)),
    ('04-riso', 'Risograph', d04_riso, (-58, True, 0.06)),
    ('05-chrome', 'Chrome', d05_chrome, (-90, False, 0.05)),
    ('06-airbrush', 'Airbrush', d06_airbrush, (-61, False, 0.12)),
    ('07-engraved', 'Engraved', d07_engraved, (-58, True, 0.10)),
    ('08-glitch', 'Glitch', d08_glitch, (-61, False, 0.08)),
    ('09-blueprint', 'Blueprint', d09_blueprint, (-90, False, 0.09)),
    ('10-allover', 'All-over', d10_allover, (-66, False, 0.10)),
    ('11-sketch', 'Sketch', d11_sketch, (-61, False, 0.07)),
    ('12-metal', 'Metal patch', d12_metal, (-61, False, 0.06)),
    ('13-woodcut', 'Woodcut', d13_woodcut, (-58, True, 0.08)),
    ('14-neon', 'Neon', d14_neon, (-61, False, 0.11)),
    ('15-camo', 'Camo', d15_camo, (-61, False, 0.07)),
    ('16-damascus', 'Damascus', d16_damascus, (-90, False, 0.05)),
    ('17-glass', 'Stained glass', d17_glass, (-58, True, 0.08)),
    ('18-holo', 'Holographic', d18_holo, (-61, False, 0.07)),
    ('19-stencil', 'Stencil', d19_stencil, (-61, False, 0.07)),
    ('20-tartan', 'Tartan', d20_tartan, (-61, False, 0.07)),
    ('21-duotone', 'Duotone', d21_duotone, (-61, False, 0.07)),
    ('22-leopard', 'Leopard', d22_leopard, (-61, False, 0.07)),
    ('23-marble', 'Marble', d23_marble, (-90, False, 0.05)),
    ('24-jacquard', 'Jacquard', d24_jacquard, (-61, False, 0.06)),
    ('25-gold', 'Gold foil', d25_gold, (-61, False, 0.07)),
    ('26-repeat', 'Repeat', d26_repeat, (-61, False, 0.07)),
    ('27-xray', 'X-ray', d27_xray, (-61, False, 0.08)),
]


def contact(images, path, shirt=(30, 30, 32)):
    cols = 5
    rows = (len(images) + cols - 1) // cols
    cw, ch, pad, lab = 460, 620, 22, 30
    sheet = Image.new('RGB', (cols * cw + pad * (cols + 1),
                              rows * (ch + lab) + pad * (rows + 1)), (18, 18, 20))
    d = ImageDraw.Draw(sheet)
    for i, (name, title, im) in enumerate(images):
        c, r = i % cols, i // cols
        x = pad + c * (cw + pad); y = pad + r * (ch + lab + pad)
        card = Image.new('RGB', (cw, ch), shirt)
        t = im.copy(); t.thumbnail((cw - 34, ch - 34), Image.LANCZOS)
        card.paste(t, ((cw - t.size[0]) // 2, (ch - t.size[1]) // 2), t)
        sheet.paste(card, (x, y))
        d.text((x + 2, y + ch + 8), f'{name}  ·  {title}', fill=(190, 190, 195))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='assets/machete-tees')
    ap.add_argument('--only', default=None)
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
        print(cp)


if __name__ == '__main__':
    main()
