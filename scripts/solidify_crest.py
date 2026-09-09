#!/usr/bin/env python3
"""Turn the outlined TraxNYC crest into the solid, symmetric form.

The source is Illustrator line art: an 8pt outer rim, then an inner "lane" made
of four separate arcs that run ~4pt wide and thicken to ~8pt at their ends.
Read as a solid shape those hairlines disappear, which is not what the piece
should look like - the reference is a solid emblem with one wide continuous
band around the outside.

This rebuilds the frame from primitives rather than editing the traced outline:

  * The silhouette has exact 4-fold ROTATIONAL symmetry (C4) and is NOT mirror
    symmetric - it is a pinwheel, the lobe centres sitting ~0.63 degrees off the
    cardinal axes. Mirroring it would corrupt the design, so only C4 is enforced,
    by averaging the three structurally identical quadrants and replicating one
    90-degree sector.
  * The four lobes are true circles (r = 97.52pt, centres 86.92pt out, the four
    fits agreeing to 0.001pt), so the inner edge is emitted as exact circular
    arcs rather than a traced approximation.

The band is then the silhouette with a quatrefoil hole, giving one continuous
band of uniform width all the way round, star points included.
"""

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity

def fit_circle(pts):
    x,y=pts[:,0],pts[:,1]
    A=np.column_stack([2*x,2*y,np.ones(len(x))]); b=x**2+y**2
    a,bb,c=np.linalg.lstsq(A,b,rcond=None)[0]
    return a,bb,float(np.sqrt(c+a*a+bb*bb))

def frame_params(OUTER):
    mnx,mny,mxx,mxy=OUTER.bounds
    cx,cy=(mnx+mxx)/2,(mny+mxy)/2
    C=np.array(OUTER.exterior.coords)
    ang=np.degrees(np.arctan2(C[:,1]-cy,C[:,0]-cx))%360
    Rs,offs,ths=[],[],[]
    for a0 in (0,90,180,270):
        d=(ang-a0+180)%360-180
        xc,yc,r=fit_circle(C[np.abs(d)<20])
        Rs.append(r); offs.append(np.hypot(xc-cx,yc-cy))
        ths.append((np.degrees(np.arctan2(yc-cy,xc-cx))-a0+180)%360-180)
    return dict(cx=cx,cy=cy,R=float(np.mean(Rs)),d=float(np.mean(offs)),
                twist=float(np.mean(ths)),
                spread=dict(R=float(np.ptp(Rs)),d=float(np.ptp(offs)),twist=float(np.ptp(ths))))

def lobe_centres(p, offset=None):
    d = p['d'] if offset is None else offset
    return [(p['cx']+d*np.cos(np.radians(p['twist']+k*90)),
             p['cy']+d*np.sin(np.radians(p['twist']+k*90))) for k in range(4)]

def inner_circles(p, lane, notch):
    """Inner lobe circles: cardinal band fixed at `lane`, notch depth `notch`.

    The source ring's lobes are circles, but at the diagonals the ring leaves
    them to weave into the star points, so completing them as a plain union
    cuts the notch far deeper (r~106) than the artwork ever goes (r~137).
    Depth is therefore a free parameter: solve for the circle pair that keeps
    the cardinal band exactly `lane` wide while placing the notch at `notch`.
    """
    card = p['d'] + p['R'] - lane          # inner radius at the lobe centres
    def notch_radius(D):
        Rc = card - D
        return D/np.sqrt(2) + np.sqrt(max(Rc*Rc - D*D/2.0, 0.0))
    lo, hi = 1.0, card - 1.0               # notch_radius decreases as D grows
    for _ in range(200):
        mid = (lo + hi)/2
        if notch_radius(mid) > notch: lo = mid
        else: hi = mid
    D = (lo + hi)/2
    return D, card - D


def lobes(p, radius=None, quad_segs=256):
    r=p['R'] if radius is None else radius
    return unary_union([Point(*c).buffer(r,quad_segs=quad_segs) for c in lobe_centres(p)])

def symmetrise(poly, p):
    """Enforce exact C4 symmetry by replicating one 90-degree sector."""
    cx,cy=p['cx'],p['cy']
    C=np.array(poly.exterior.coords)[:-1]
    ang=(np.degrees(np.arctan2(C[:,1]-cy,C[:,0]-cx))-p['twist'])%360
    order=np.argsort(ang); C=C[order]; ang=ang[order]
    sector=C[(ang>=0)&(ang<90)]
    pts=[]
    for k in range(4):
        t=np.radians(90*k); ct,st=np.cos(t),np.sin(t)
        v=sector-[cx,cy]
        pts.append(np.column_stack([cx+v[:,0]*ct-v[:,1]*st, cy+v[:,0]*st+v[:,1]*ct]))
    return Polygon(np.vstack(pts)).buffer(0)
K = 4.0/3.0*(np.sqrt(2)-1)      # circular-arc Bezier constant for 90 degrees

def rot_pt(pt, deg, cx, cy):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    x, y = pt[0]-cx, pt[1]-cy
    return (cx + x*c - y*s, cy + x*s + y*c)

def average_quadrants(canons, use=(0,1,2)):
    """Average matching quadrant curves to cancel residual asymmetry."""
    ref = canons[use[0]]
    start = np.mean([[canons[k][0][0], canons[k][0][1]] for k in use], axis=0)
    segs = []
    for i in range(1, len(ref)):
        kind = ref[i][0]
        pts = []
        for j in range(1, len(ref[i])):
            pts.append(tuple(np.mean([canons[k][i][j] for k in use], axis=0)))
        segs.append((kind,)+tuple(pts))
    return (tuple(start), segs)

def replicate(quad, cx, cy):
    """One 90-degree sector -> full closed path with exact C4 symmetry."""
    start, segs = quad
    out = []
    for k in range(4):
        for s in segs:
            out.append((s[0],)+tuple(rot_pt(p, 90*k, cx, cy) for p in s[1:]))
    return (start, out)

def arc_to_beziers(cx, cy, r, a0, a1):
    """Circular arc a0->a1 (degrees, CCW) as cubic Bezier segments."""
    a0r, a1r = np.radians(a0), np.radians(a1)
    sweep = a1r - a0r
    while sweep <= 0: sweep += 2*np.pi
    n = max(1, int(np.ceil(sweep/(np.pi/2) - 1e-9)))
    step = sweep/n
    k = 4.0/3.0*np.tan(step/4.0)
    segs = []
    a = a0r
    for _ in range(n):
        b = a + step
        p0 = np.array([cx+r*np.cos(a), cy+r*np.sin(a)])
        p3 = np.array([cx+r*np.cos(b), cy+r*np.sin(b)])
        t0 = np.array([-np.sin(a), np.cos(a)])*r*k
        t1 = np.array([-np.sin(b), np.cos(b)])*r*k
        segs.append(('C', tuple(p0+t0), tuple(p3-t1), tuple(p3)))
        a = b
    return segs

def circle_intersections(c0, r0, c1, r1):
    d = np.hypot(c1[0]-c0[0], c1[1]-c0[1])
    a = (r0*r0 - r1*r1 + d*d)/(2*d)
    h2 = r0*r0 - a*a
    if h2 < 0: return []
    h = np.sqrt(h2)
    xm = c0[0] + a*(c1[0]-c0[0])/d
    ym = c0[1] + a*(c1[1]-c0[1])/d
    rx = -(c1[1]-c0[1])*(h/d); ry = (c1[0]-c0[0])*(h/d)
    return [(xm+rx, ym+ry), (xm-rx, ym-ry)]

def rounded_cross(cx, cy, a, rtip, twist=0.0):
    """Two crossing capsules as one exact path: 8 lines + 4 semicircular caps.

    `a` is the arm half-width, `rtip` the distance from centre to the outer
    face of each rounded end. This is the shape the emblem actually uses - the
    arms have straight parallel sides meeting at sharp concave corners on the
    diagonals, which a union of circles cannot produce.
    """
    L = rtip - a
    def rot(x, y):
        t = np.radians(twist); c, sn = np.cos(t), np.sin(t)
        return (cx + x*c - y*sn, cy + x*sn + y*c)

    segs = []
    start = rot(a, a)
    # right side of the top arm, over the top cap, down the left side
    segs.append(('L', rot(a, L)))
    segs += [(k[0],)+tuple(rot(*q) for q in k[1:])
             for k in _arc_local(0.0, L, a, 0.0, 180.0)]
    segs.append(('L', rot(-a, a)))
    segs.append(('L', rot(-L, a)))
    segs += [(k[0],)+tuple(rot(*q) for q in k[1:])
             for k in _arc_local(-L, 0.0, a, 90.0, 270.0)]
    segs.append(('L', rot(-a, -a)))
    segs.append(('L', rot(-a, -L)))
    segs += [(k[0],)+tuple(rot(*q) for q in k[1:])
             for k in _arc_local(0.0, -L, a, 180.0, 360.0)]
    segs.append(('L', rot(a, -a)))
    segs.append(('L', rot(L, -a)))
    segs += [(k[0],)+tuple(rot(*q) for q in k[1:])
             for k in _arc_local(L, 0.0, a, 270.0, 450.0)]
    segs.append(('L', rot(a, a)))
    return (start, segs)


def _arc_local(cx, cy, r, a0, a1):
    """arc_to_beziers in local (untwisted) coordinates."""
    return arc_to_beziers(cx, cy, r, a0, a1)


def quatrefoil(centres, r, cx, cy):
    """Boundary of the union of 4 equal circles, as exact arcs."""
    n = len(centres)
    start = None; segs = []
    for i in range(n):
        c = centres[i]
        prev = centres[(i-1) % n]; nxt = centres[(i+1) % n]
        def outer(pts):
            return max(pts, key=lambda q: np.hypot(q[0]-cx, q[1]-cy))
        p_in  = outer(circle_intersections(c, r, prev, r))
        p_out = outer(circle_intersections(c, r, nxt, r))
        a0 = np.degrees(np.arctan2(p_in[1]-c[1],  p_in[0]-c[0]))
        a1 = np.degrees(np.arctan2(p_out[1]-c[1], p_out[0]-c[0]))
        if start is None: start = p_in
        segs.extend(arc_to_beziers(c[0], c[1], r, a0, a1))
    return (start, segs)

def path_ops(path, prec=5):
    f = lambda v: (f"{v:.{prec}f}".rstrip('0').rstrip('.')) or '0'
    start, segs = path
    o = [f"{f(start[0])} {f(start[1])} m"]
    for s in segs:
        if s[0] == 'L': o.append(f"{f(s[1][0])} {f(s[1][1])} l")
        else: o.append(" ".join(f(v) for p in s[1:] for v in p)+" c")
    return " ".join(o)+" h"

def write_pdf(path, groups, W, H):
    """groups: list of (list_of_paths, 'black'|'white')."""
    body = []
    for paths, colour in groups:
        body.append("0 g" if colour == 'black' else "1 g")
        body.append("\n".join(path_ops(p) for p in paths))
        body.append("f*")
    content = ("\n".join(body)+"\n").encode('latin-1')
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W:.4f} {H:.4f}] "
             f"/Contents 4 0 R /Resources << >> >>").encode(),
            b"<< /Length "+str(len(content)).encode()+b" >>\nstream\n"+content+b"endstream"]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offs=[]
    for i,b in enumerate(objs,1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode()+b+b"\nendobj\n"
    x=len(out); out += f"xref\n0 {len(objs)+1}\n".encode()+b"0000000000 65535 f \n"
    for o in offs: out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    open(path,'wb').write(bytes(out))


# --------------------------------------------------------------------- main

def solidify(src_pdf, out_pdf, lane=22.0, arm=60.0, margin=12.0):
    """Read the outlined crest, write the solid version."""
    import pymupdf
    from shapely.geometry import Polygon

    doc = pymupdf.open(src_pdf)
    page = doc[0]
    H = page.rect.height
    draw = page.get_drawings()

    def conv(sp):
        return ((sp[0][0], H - sp[0][1]),
                [(s[0],) + tuple((x, H - y) for x, y in s[1:]) for s in sp[1]])

    def subpaths(path):
        out, cur, last = [], None, None
        for it in path['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if cur is None or last is None or abs(a.x-last.x) > 1e-6 or abs(a.y-last.y) > 1e-6:
                    cur = [(a.x, a.y), []]; out.append(cur)
                cur[1].append(('L', (b.x, b.y))); last = b
            elif it[0] == 'c':
                a, c1, c2, b = it[1], it[2], it[3], it[4]
                if cur is None or last is None or abs(a.x-last.x) > 1e-6 or abs(a.y-last.y) > 1e-6:
                    cur = [(a.x, a.y), []]; out.append(cur)
                cur[1].append(('C', (c1.x, c1.y), (c2.x, c2.y), (b.x, b.y))); last = b
        return out

    def flatten(path, n=80):
        pts = [path[0]]
        for s in path[1]:
            if s[0] == 'L':
                pts.append(s[1])
            else:
                p0 = np.array(pts[-1]); p1 = np.array(s[1])
                p2 = np.array(s[2]); p3 = np.array(s[3])
                t = np.linspace(0, 1, n)[1:]; mt = 1 - t
                pts.extend(map(tuple, (np.outer(mt**3, p0) + np.outer(3*t*mt**2, p1)
                                       + np.outer(3*t**2*mt, p2) + np.outer(t**3, p3))))
        return np.array(pts)

    # path 3 = the crest band; its second subpath is the outer silhouette
    crest = [conv(s) for s in subpaths(draw[3])]
    outer_path = crest[1]
    OUTER = Polygon(flatten(outer_path)).buffer(0)
    p = frame_params(OUTER)

    # split the silhouette into quadrants at the four repeating anchors
    segs = outer_path[1]
    anchors = [outer_path[0]] + [s[-1] for s in segs]
    ang = [(np.degrees(np.arctan2(y - p['cy'], x - p['cx'])) - p['twist']) % 360
           for x, y in anchors]
    marks = [i for i, a in enumerate(ang[:-1])
             if min(abs(a - t) for t in (0, 90, 180, 270)) < 1.0]
    canons = []
    for k, (a, b) in enumerate(zip(marks, marks[1:] + [marks[0] + len(segs)])):
        q = [anchors[a % len(anchors)]]
        for i in range(a, b):
            q.append(segs[i % len(segs)])
        canons.append([rot_pt(q[0], -90*k, p['cx'], p['cy'])]
                      + [(s[0],) + tuple(rot_pt(v, -90*k, p['cx'], p['cy']) for v in s[1:])
                         for s in q[1:]])
    usable = [k for k, c in enumerate(canons) if len(c) == min(len(x) for x in canons)]
    sym = replicate(average_quadrants(canons, tuple(usable)), p['cx'], p['cy'])

    rtip = p['d'] + p['R'] - lane          # 22pt band at the arm tips
    quat = rounded_cross(p['cx'], p['cy'], arm, rtip, p['twist'])
    eagle = [conv(s) for s in subpaths(draw[5])][1]
    eye = [conv(s) for s in subpaths(draw[7])][0]
    pupil = [conv(s) for s in subpaths(draw[6])][0]

    pts = np.vstack([flatten(sym), flatten(eagle)])
    x0, y0 = pts.min(0); x1, y1 = pts.max(0)
    W = (x1 - x0) + 2*margin; Hp = (y1 - y0) + 2*margin

    def shift(path):
        f = lambda q: (q[0] - x0 + margin, q[1] - y0 + margin)
        return (f(path[0]), [(s[0],) + tuple(f(v) for v in s[1:]) for s in path[1]])

    write_pdf(out_pdf, [([shift(sym), shift(quat)], 'black'),
                        ([shift(eagle)], 'black'),
                        ([shift(eye)], 'white'),
                        ([shift(pupil)], 'black')], W, Hp)
    return dict(params=p, page=(W, Hp), lane=lane, arm=arm, rtip=rtip,
                segments=len(sym[1]) + len(quat[1]) + len(eagle[1]) + len(eye[1]) + len(pupil[1]))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split(chr(10))[0])
    ap.add_argument('input'); ap.add_argument('output')
    ap.add_argument('--lane', type=float, default=22.0,
                    help='width of the outer band in points (default 22, the '
                         'width implied by the original artwork)')
    ap.add_argument('--arm', type=float, default=60.0,
                    help='half-width of the inner cross arms in points '
                         '(default 60, i.e. 120pt wide arms)')
    a = ap.parse_args()
    info = solidify(a.input, a.output, a.lane, a.arm)
    p = info['params']
    print('lobe circles r=%.4f pt, centres %.4f pt out, pinwheel twist %.4f deg'
          % (p['R'], p['d'], p['twist']))
    print('agreement across the four lobes: r %.5f, offset %.5f, twist %.5f'
          % (p['spread']['R'], p['spread']['d'], p['spread']['twist']))
    print('inner cross: arms %.1f pt wide, tips at r=%.3f, corners at r=%.2f'
          % (2*info['arm'], info['rtip'], info['arm']*np.sqrt(2)))
    print('page %.3f x %.3f pt, %d segments, lane %.1f pt'
          % (info['page'][0], info['page'][1], info['segments'], info['lane']))
