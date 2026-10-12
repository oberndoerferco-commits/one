import sys, math
sys.path.insert(0, '/home/user/one/scripts')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
from monogram import glyph_O, glyph_M, ellipse, tr, bbox, CAP
import outline_to_fill as of

M_KW = dict(piy=0.12, ya=0.54, yb=0.40, pix=0.038)

def cross():
    segs, _ = of.read_subpaths('/home/user/one/assets/cross-cliche/source-Cliche_15cm.pdf')
    run, _, _ = of.chain(of.dedupe(segs)); run, _ = of.snap(run)
    path = of.as_path(run)
    pts = [p for s in path for p in s[1:]]
    x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
    h = max(p[1] for p in pts) - y0; w = max(p[0] for p in pts) - x0
    start = ((path[0][1][0]-x0)/h, (path[0][1][1]-y0)/h)
    segs2 = [(s[0].upper(),) + tuple(((q[0]-x0)/h, (q[1]-y0)/h) for q in s[1:])
             for s in path[1:]]
    return (start, segs2), w/h

XP, XA = cross()

def place(cs, k, dx, dy):
    return [tr(c, k, dx, dy) for c in cs]

def centre(cs):
    x0, y0, x1, y1 = bbox(cs)
    return [tr(c, 1.0, -(x0+x1)/2, -(y0+y1)/2) for c in cs]

def direction(name):
    if name == 'A  seal':
        R, t = 520.0, 112.0
        r = R - t
        out = [ellipse(0, 0, R, R, True), ellipse(0, 0, r, r, False)]
        m = centre(glyph_M(**M_KW))
        k = (2*r*0.92) / math.hypot(0.90, 1.0) / CAP
        return out + place(m, k, 0, 0)
    if name == 'B  interlock':
        o = centre(glyph_O()); m = centre(glyph_M(**M_KW))
        ow = bbox(o)[2] - bbox(o)[0]; mw = bbox(m)[2] - bbox(m)[0]
        return place(o, 1.0, -(ow+mw)/2*0.40, 0) + place(m, 1.0, (ow+mw)/2*0.40, 0)
    if name == 'C  pair':
        o = centre(glyph_O()); m = centre(glyph_M(**M_KW))
        ow = bbox(o)[2] - bbox(o)[0]; mw = bbox(m)[2] - bbox(m)[0]
        gap = 0.10 * CAP
        return place(o, 1.0, -(mw+gap)/2 - ow/2 + ow/2, 0) + \
               place(m, 1.0, (ow+gap)/2 + mw/2 - mw/2, 0) if False else \
               place(o, 1.0, -(ow+gap)/2, 0) + place(m, 1.0, (mw+gap)/2, 0)
    if name == 'D  cross seal':
        R, t = 520.0, 112.0
        r = R - t
        out = [ellipse(0, 0, R, R, True), ellipse(0, 0, r, r, False)]
        m = centre(glyph_M(**M_KW))
        k = (2*r*0.86) / math.hypot(0.90, 1.0) / CAP
        res = out + place(m, k, 0, 0)
        ch = 0.46 * R
        for ang in (90, 270):
            a = math.radians(ang)
            res.append(tr(XP, ch, R*math.cos(a) - ch*XA/2, R*math.sin(a) - ch/2))
        return res
    raise ValueError(name)

def patch(cs, color='#111'):
    v, c = [], []
    for s, segs in cs:
        v.append(s); c.append(MP.MOVETO)
        for q in segs:
            if q[0] == 'L': v.append(q[1]); c.append(MP.LINETO)
            else: v += [q[1], q[2], q[3]]; c += [MP.CURVE4]*3
        v.append(s); c.append(MP.CLOSEPOLY)
    return PathPatch(MP(v, c), facecolor=color, edgecolor='none')

names = ['A  seal', 'B  interlock', 'C  pair', 'D  cross seal']
fig, axes = plt.subplots(2, len(names), figsize=(4.6*len(names), 10),
                         gridspec_kw=dict(height_ratios=[4, 1]))
for col, nm in enumerate(names):
    cs = direction(nm)
    b = bbox(cs); w = b[2]-b[0]; h = b[3]-b[1]
    for row, size in enumerate((1.0, 0.10)):
        ax = axes[row, col]
        ax.add_patch(patch(cs))
        pad = max(w, h) * 0.08
        ax.set_xlim(b[0]-pad, b[2]+pad); ax.set_ylim(b[1]-pad, b[3]+pad)
        ax.set_aspect('equal'); ax.set_axis_off()
        if row == 0: ax.set_title(nm, fontsize=13)
fig.tight_layout()
fig.savefig('/tmp/claude-0/-home-user-one/9a731093-06fb-50bc-9d28-75940e80fb3f/scratchpad/directions.png', dpi=78)
print('ok')
