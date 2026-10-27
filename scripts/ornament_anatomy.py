#!/usr/bin/env python3
"""Take a repeating ornament apart: what it is made of, and where each piece sits.

Understanding before drawing. A border like this is a stem with things
hung on it, so the first question is which pixels are stem and which are
leaf, and the answer is in the local width: a stem stays about four source
pixels across wherever it runs, a leaf swells to twenty.

So the distance transform supplies the markers -- everything above a width
is the core of a leaf, the thin skeleton is stem -- and a watershed over
the same distance hands every pixel to one of them. Pieces that come back
long and narrow are stem after all, however fat, and are given back to it;
what is left is the foliage, one region each.

Each region is then measured against the point where it meets the stem,
not against its own centre, because that joint is what fixes which way a
leaf points. Its axis is the line from the joint to the centroid, its
reach is how far it runs along that line, its span how wide it is across
it. Rotated upright by that axis, a leaf can be compared with the others,
lifted out on its own, or put back somewhere else.

What it says about this ornament is in the numbers it prints: a repeat of
137.56 px carrying four large leaves, seven smaller leaves and buds, a
stem that forks twice, and two volutes -- and leaves that measure twenty
to thirty pixels across, which is why they come out of the file as rounded
masses with a scalloped edge and not as anything with lobes.
"""
import argparse, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vectorize_silhouette as V


def flow(m, r, it=2):
    f = m.astype(float)
    for _ in range(it):
        f = (ndi.gaussian_filter(f, r) > 0.5).astype(float)
    return f > 0.5


def anatomy(arr, zoom, fat, thin, elongated=2.5):
    sil, _, _ = V.silhouette(arr, zoom, 0.45, 4, 1600, 400)
    dist = ndi.distance_transform_edt(sil)
    from skimage.morphology import medial_axis
    sk, _ = medial_axis(sil, return_distance=True)
    w = dist * 2 / zoom

    cores = sil & (w > fat)
    L, n = ndi.label(cores)
    sz = ndi.sum(cores, L, range(1, n + 1)) if n else []
    markers = np.zeros(sil.shape, np.int32)
    for k, i in enumerate([i + 1 for i in range(n) if sz[i] >= (1.1 * zoom) ** 2], start=2):
        markers[L == i] = k
    markers[(sk & (w <= thin)) & (markers == 0)] = 1
    lab = watershed(-dist, markers, mask=sil)

    stem = lab == 1
    parts = []
    for k in [v for v in np.unique(lab) if v > 1]:
        m = lab == k
        if m.sum() < (1.5 * zoom) ** 2:
            continue
        ys, xs = np.nonzero(m)
        cov = np.cov(np.vstack([xs - xs.mean(), ys - ys.mean()]))
        ev, _ = np.linalg.eigh(cov)
        long_, short = 2 * np.sqrt(ev[-1]) / zoom, 2 * np.sqrt(ev[0]) / zoom
        if long_ / max(short, 1e-6) > elongated:
            stem |= m                       # a long thin piece is stem, not leaf
        else:
            parts.append((k, m))
    return sil, stem, lab, parts


def describe(parts, stem, zoom):
    sd = ndi.distance_transform_edt(~stem)
    rows = []
    for k, m in parts:
        ys, xs = np.nonzero(m)
        j = int(np.argmin(sd[ys, xs]))          # where it joins the stem
        ay, ax = ys[j], xs[j]
        ang = np.degrees(np.arctan2(xs.mean() - ax, ys.mean() - ay))
        up = ndi.rotate(m.astype(float), -ang, reshape=True, order=1) > 0.5
        ry, rx = np.nonzero(up)
        rows.append(dict(id=int(k), area=m.sum() / zoom ** 2,
                         cx=xs.mean() / zoom, cy=ys.mean() / zoom, axis=ang,
                         reach=(ry.max() - ry.min() + 1) / zoom,
                         span=(rx.max() - rx.min() + 1) / zoom,
                         crop=up[ry.min():ry.max() + 1, rx.min():rx.max() + 1]))
    rows.sort(key=lambda r: -r['area'])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out_dir')
    ap.add_argument('--zoom', type=int, default=8)
    ap.add_argument('--fat', type=float, default=7.5, help='width above which it is foliage')
    ap.add_argument('--thin', type=float, default=6.0, help='width below which it is stem')
    ap.add_argument('--repeat', action='store_true', help='work on one repeat, not the whole')
    ap.add_argument('--smooth', type=float, default=0.30)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    arr = np.asarray(Image.open(a.src).convert('RGB'), float)
    if a.repeat:
        arr, info = V.tile(arr, 1)
        print(f'repeat {info[0]:.2f} px, cut at row {info[1]}', file=sys.stderr)

    sil, stem, lab, parts = anatomy(arr, a.zoom, a.fat, a.thin)
    rows = describe(parts, stem, a.zoom)
    print(f'stem {100*stem.sum()/sil.sum():.0f}% of the ink, {len(rows)} pieces of foliage',
          file=sys.stderr)
    print(f"{'id':>3} {'area':>7} {'cx':>6} {'cy':>7} {'axis':>7} {'reach':>6} {'span':>6}",
          file=sys.stderr)
    for r in rows:
        print(f"{r['id']:3d} {r['area']:7.0f} {r['cx']:6.1f} {r['cy']:7.1f} "
              f"{r['axis']:7.1f} {r['reach']:6.1f} {r['span']:6.1f}", file=sys.stderr)
        g = flow(r['crop'], a.smooth * a.zoom, 2)
        Image.fromarray(np.where(g, 0, 255).astype(np.uint8)).save(
            os.path.join(a.out_dir, f"piece-{r['id']:02d}.png"))
    Image.fromarray(np.where(stem, 0, 255).astype(np.uint8)).save(
        os.path.join(a.out_dir, 'stem.png'))
    print(f'  pieces and stem written to {a.out_dir}', file=sys.stderr)


if __name__ == '__main__':
    main()
