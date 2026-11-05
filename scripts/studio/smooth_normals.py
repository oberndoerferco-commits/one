"""Shade a stacked STL like the polished part, not like a contour map.

    python3 scripts/studio/smooth_normals.py part.stl part.bin

paco-logo.stl is a stack: 38 z levels, 42,617 horizontal faces, 44,747
vertical ones, and not one sloped triangle. Its dome was built by
unioning level sets, so off its own face normals it shades as a
staircase - every 0.08 mm tread catching the light flat.

The geometry is not touched. Only the normals change, and only above the
base, so the part stays sharp where it is sharp and the dome reads as
the surface it stands for. The output is one blob - positions float32,
normals int16, indices uint32 - for the studio page to load.
"""
import os
import sys

import numpy as np
import trimesh

BASE = 0.30          # the flat plinth under the dome, mm


def smooth_normals(m, base=BASE, pitch=0.12, sigma=2.6):
    """Normals from the dome read as a height field, not from its facets.

    The first version fitted a plane to every vertex's neighbours inside a
    0.35 mm ball. On treads 0.08 mm wide that is several hundred points
    per vertex and twenty million pairs for the part; it was still running
    after four minutes. The dome is a height field, so the cheap way is to
    rasterise it once, smooth it, and read the gradient back: the same
    answer in a second.

    The blur is normalised by its own mask, so the six bodies do not bleed
    height into the gaps between them.
    """
    from scipy.ndimage import gaussian_filter
    v = np.asarray(m.vertices)
    # np.asarray, not m.vertex_normals used element by element: trimesh
    # hands back tracked arrays that re-hash themselves on access, and a
    # loop over 88,096 faces touching one spent four minutes hashing
    n = np.asarray(m.vertex_normals, dtype=float).copy()

    x0, y0 = v[:, 0].min() - 1, v[:, 1].min() - 1
    nx = int((v[:, 0].max() - x0 + 1) / pitch) + 2
    ny = int((v[:, 1].max() - y0 + 1) / pitch) + 2
    hi = np.full((ny, nx), -1e9)
    gx = np.clip(((v[:, 0] - x0) / pitch).astype(int), 0, nx - 1)
    gy = np.clip(((v[:, 1] - y0) / pitch).astype(int), 0, ny - 1)
    np.maximum.at(hi, (gy, gx), v[:, 2])
    mask = (hi > -1e8).astype(float)
    hi = np.where(mask > 0, hi, 0.0)

    num = gaussian_filter(hi * mask, sigma)
    den = gaussian_filter(mask, sigma)
    hs = np.where(den > 1e-6, num / np.maximum(den, 1e-9), 0.0)
    dy, dx = np.gradient(hs, pitch)

    def sample(g, px, py):
        fx = np.clip((px - x0) / pitch, 0, nx - 1.001)
        fy = np.clip((py - y0) / pitch, 0, ny - 1.001)
        ix, iy = fx.astype(int), fy.astype(int)
        tx, ty = fx - ix, fy - iy
        return ((g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx) * (1 - ty)
                + (g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx) * ty)

    dome = v[:, 2] > base + 1e-6
    sx = sample(dx, v[dome, 0], v[dome, 1])
    sy = sample(dy, v[dome, 0], v[dome, 1])
    nn = np.stack([-sx, -sy, np.ones_like(sx)], axis=1)
    nn /= np.linalg.norm(nn, axis=1, keepdims=True)
    out = n.copy()
    out[dome] = nn
    return out, int(dome.sum()), (ny, nx)


def pack(m, normals, path):
    """positions float32, normals int16, indices uint32 - one blob."""
    v = np.asarray(m.vertices, dtype=np.float32)
    nn = np.clip(np.rint(normals * 32767), -32767, 32767).astype('<i2')
    f = np.asarray(m.faces, dtype='<u4')
    with open(path, 'wb') as fh:
        fh.write(np.array([len(v), len(f)], dtype='<u4').tobytes())
        fh.write(v.astype('<f4').tobytes())
        fh.write(nn.tobytes())
        fh.write(f.tobytes())
    return len(v), len(f)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[2].strip())
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'logo.bin'
    m = trimesh.load(src)
    m.merge_vertices()
    print(f'{len(m.faces)} faces, {len(m.vertices)} vertices, '
          f'{m.extents[0]:.2f} x {m.extents[1]:.2f} x {m.extents[2]:.2f} mm')
    n, ndome, grid = smooth_normals(m)
    print(f'  height field {grid[1]} x {grid[0]} at {0.12} mm; '
          f'{ndome} dome vertices re-normalled')
    nv, nf = pack(m, n, out)
    print(f'{out}: {nv} verts, {nf} faces, {os.path.getsize(out)/1e6:.2f} MB')
    up = (np.asarray(m.face_normals)[:, 2] > 0.999).sum()
    print(f'  faces that were flat-up before smoothing: {up}')
