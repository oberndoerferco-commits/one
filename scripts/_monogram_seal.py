import sys, math
sys.path.insert(0, '/home/user/one/scripts')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
from monogram import glyph_M, ellipse, tr, bbox, CAP
from shapely.geometry import Polygon
from shapely.ops import unary_union

M_KW = dict(piy=0.12, ya=0.54, yb=0.40, pix=0.038)

def centre(cs):
    x0, y0, x1, y1 = bbox(cs)
    return [tr(c, 1.0, -(x0+x1)/2, -(y0+y1)/2) for c in cs]

def flat(c, n=36):
    s, segs = c; cur = list(s); out = [tuple(cur)]
    for q in segs:
        if q[0] == 'L': cur = list(q[1]); out.append(tuple(cur))
        else:
            b = [cur, q[1], q[2], q[3]]
            for i in range(1, n+1):
                t = i/n; mt = 1-t
                out.append((mt**3*b[0][0]+3*mt*mt*t*b[1][0]+3*mt*t*t*b[2][0]+t**3*b[3][0],
                            mt**3*b[0][1]+3*mt*mt*t*b[1][1]+3*mt*t*t*b[2][1]+t**3*b[3][1]))
            cur = list(q[3])
    return out

def seal(R=520.0, t=112.0, fill=0.92, clear=None):
    r = R - t
    m = centre(glyph_M(**M_KW))
    k = (2*r*fill) / math.hypot(0.90, 1.0) / CAP
    m = [tr(c, k, 0, 0) for c in m]
    ring = [ellipse(0, 0, R, R, True), ellipse(0, 0, r, r, False)]
    if clear is None:
        return ring + m
    # the M breaks the ring: knock a clearance out of the ring where they meet
    mp = unary_union([Polygon(flat(c)) for c in m]).buffer(0)
    rp = Polygon(flat(ring[0])).difference(Polygon(flat(ring[1])))
    cut = rp.difference(mp.buffer(clear))
    out = []
    for g in (cut.geoms if hasattr(cut, 'geoms') else [cut]):
        ext = list(g.exterior.coords)[:-1]
        out.append((ext[0], [('L', p) for p in ext[1:]]))
        for i in g.interiors:
            c2 = list(i.coords)[:-1]
            out.append((c2[0], [('L', p) for p in c2[1:]]))
    return out + m

def patch(cs, color='#111'):
    v, c = [], []
    for s, segs in cs:
        v.append(s); c.append(MP.MOVETO)
        for q in segs:
            if q[0] == 'L': v.append(q[1]); c.append(MP.LINETO)
            else: v += [q[1], q[2], q[3]]; c += [MP.CURVE4]*3
        v.append(s); c.append(MP.CLOSEPOLY)
    return PathPatch(MP(v, c), facecolor=color, edgecolor='none')

variants = [('A1  M inside', dict(R=520, t=112, fill=0.88)),
            ('A2  M filling the ring', dict(R=520, t=118, fill=1.00)),
            ('A3  heavier ring', dict(R=520, t=150, fill=0.94)),
            ('A4  M breaking the ring', dict(R=520, t=130, fill=1.16, clear=26))]
fig, axes = plt.subplots(2, len(variants), figsize=(4.4*len(variants), 9.6),
                         gridspec_kw=dict(height_ratios=[4, 1]))
for col, (nm, kw) in enumerate(variants):
    cs = seal(**kw); b = bbox(cs)
    for row in (0, 1):
        ax = axes[row, col]; ax.add_patch(patch(cs))
        pad = (b[2]-b[0])*0.07
        ax.set_xlim(b[0]-pad, b[2]+pad); ax.set_ylim(b[1]-pad, b[3]+pad)
        ax.set_aspect('equal'); ax.set_axis_off()
        if row == 0: ax.set_title(nm, fontsize=12)
fig.tight_layout()
fig.savefig('/tmp/claude-0/-home-user-one/9a731093-06fb-50bc-9d28-75940e80fb3f/scratchpad/seal.png', dpi=78)
print('ok')
