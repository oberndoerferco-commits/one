#!/usr/bin/env python3
"""An 8 mm bead carrying the marks as a monogram pattern.

The bead is drilled from one side only. It sits on a post, so a tunnel
through it would be a hole too many: the far pole is solid and carries
pattern like the rest of the ball.

The motifs are not drawn onto the sphere one by one. They are painted
into an equirectangular map, the map is turned into a relief by the same
rule the PA & CO part uses - height from distance to the edge of the
mark - and an icosphere is displaced radially through it. Two details
matter and both are about the map being a map:

A stamp near the equator and the same stamp near the pole cover very
different spans of longitude for the same width on the ball, so each one
is stretched by 1 / cos(latitude) as it is painted. Without that the
marks come out pinched at the top and bottom.

The map wraps, so a mark crossing the date line has to be painted on
both sides of it. Painting is done with modular indexing, which costs
nothing and removes the seam.
"""
import argparse, math, os, sys
import numpy as np, pymupdf, trimesh
from scipy import ndimage

MM = 72.0 / 25.4


PAGE = 'assets/om-monogram/om-pattern-page.pdf'

# The five marks, cropped off the page they come from, each with the size
# it should be ON THE BALL. These are not the page's relative sizes: there
# the little crosses are a third of the OM, which on an 8 mm ball puts
# them under a millimetre and leaves gaps that read as bald. Sized to
# look equal instead, so the space between any two marks is the same
# wherever you look.
PATTERN = [
    # name  crop box on the page               _  _   mm on ball  share
    ('om',   (0.1038, 0.0940, 0.2140, 0.2420), 0, 0, 2.70, 2.0),
    ('sq',   (0.2858, 0.1030, 0.3432, 0.1825), 0, 0, 2.10, 1.0),
    ('n925', (0.2532, 0.2667, 0.3432, 0.3379), 0, 0, 2.50, 1.1),
    ('circ', (0.1197, 0.3129, 0.1830, 0.4050), 0, 0, 2.60, 1.0),
    ('outl', (0.2443, 0.3910, 0.3106, 0.4806), 0, 0, 2.25, 1.0),
    ('cross', (0.1197, 0.3129, 0.1830, 0.4050), 0, 0, 1.60, 1.0),
    # The monogram a second time, at a size that fits between the big
    # ones. Same artwork, its own entry, because a kind carries one size
    # across the whole ball and the four on the equator are 3.07 mm.
    ('om2',  (0.1038, 0.0940, 0.2140, 0.2420), 0, 0, 1.65, 1.0),
]

BYNAME = {q[0]: i for i, q in enumerate(PATTERN)}


def stamp_from_pdf(path, box=None, px=900, pad=6):
    """A mark as a binary stamp, trimmed to its own ink."""
    d = pymupdf.open(path)
    p = d[0]
    zoom = px / max(p.rect.width, p.rect.height)
    pm = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    m = a.mean(2) < 128
    if box:
        x0, y0, x1, y1 = box
        m = m[int(y0 * m.shape[0]):int(y1 * m.shape[0]),
              int(x0 * m.shape[1]):int(x1 * m.shape[1])]
    ys, xs = np.nonzero(m)
    if not len(ys):
        raise SystemExit(f'no ink in {path} {box}')
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.pad(m, pad)


def edge_distance(mask, long_mm):
    """Distance from the edge of the ink, inwards, in millimetres.

    Measured once per stamp, in the stamp's own square pixels, where it
    is isotropic and means what it says. The old code measured it on the
    equirectangular map instead and converted pixels to millimetres with
    the north-south pixel size alone - but an east-west pixel shrinks
    with the cosine of the latitude, so a lip asked to be 0.05 mm came
    out 0.035 mm east-west at 45 degrees and 0.029 at 54, while staying
    0.05 north-south. Every mark off the equator was cut with a sharper
    edge on its sides than on its top, and the further out the worse.
    """
    h, w = mask.shape
    if w >= h:
        wmm = long_mm
    else:
        wmm = long_mm * w / h
    return ndimage.distance_transform_edt(mask) * (wmm / w)


def ink_radius(mask, long_mm):
    """How far the ink reaches from the middle of a mark, in mm.

    Two marks clash when this distance, added across the pair, is more
    than the arc between their centres. The bounding box would answer
    the same question far more pessimistically: a cross fills a square
    with empty corners, so its box half-diagonal is 1.59 mm where its
    ink only reaches 1.00. On a ball 24.5 mm round, that difference is
    the difference between a pattern that fits and one that does not.
    """
    h, w = mask.shape
    if w >= h:
        wmm, hmm = long_mm, long_mm * h / w
    else:
        hmm, wmm = long_mm, long_mm * w / h
    ys, xs = np.nonzero(mask)
    dx = (xs - (w - 1) / 2.0) * (wmm / w)
    dy = (ys - (h - 1) / 2.0) * (hmm / h)
    return float(np.hypot(dx, dy).max())


def gaps(places, radius, radii):
    """Edge-to-edge clearance of every pair, closest first.

    Negative means the two marks run into each other. This is the check
    the pattern has to pass: "the logos can't overlap" is not a matter of
    taste, it is one number per pair and the smallest of them decides.
    """
    out = []
    v = [_unit(lo, la) for lo, la, _, _ in places]
    for i in range(len(places)):
        for j in range(i + 1, len(places)):
            d = math.acos(max(-1.0, min(1.0, _dot(v[i], v[j])))) * radius
            ri = radii[places[i][2]] * places[i][3] / PATTERN[places[i][2]][4]
            rj = radii[places[j][2]] * places[j][3] / PATTERN[places[j][2]][4]
            out.append((d - ri - rj, i, j, d))
    out.sort(key=lambda t: t[0])
    return out


def despeckle(mask, long_mm, floor=0.004, pad=6):
    """Drop parts of a mark too small to be anything but trace noise.

    The circled cross is cropped from a page that draws its ring as a
    light grey hairline. At 2200 px the 128 threshold took the whole
    ring off, which is why the circle had to be redrawn. At 8800 px it
    takes about a third of it: 139 separate crumbs, four to seventy-five
    pixels each, strung round the crop like a dotted line. Inverted they
    punch that dotted line into the floor of the engraving as pimples a
    few hundredths of a millimetre across - visible at ten times life
    size, and nothing a caster could reproduce.

    `floor` is in square millimetres, so the rule is about the part and
    not about the resolution it happened to be traced at. 0.004 mm2 is
    a speck 0.06 mm across. It clears every crumb by a factor of four
    and leaves the smallest real piece - the dot at the centre of the
    squared cross, 0.0066 mm2 - by about the same.
    """
    lab, n = ndimage.label(mask)
    if n < 2:
        return mask
    h, w = mask.shape
    per_px = (long_mm / max(h, w)) ** 2
    keep = np.bincount(lab.ravel())[1:] * per_px >= floor
    m = keep[lab - 1] & mask
    # trim again: the crumbs sat round the outside, so while they were
    # there the stamp's box was the hairline's and not the mark's, and
    # every size quoted for the mark was the box's size instead.
    ys, xs = np.nonzero(m)
    if not len(ys):
        return mask
    return np.pad(m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], pad)


def fatten(mask, each_side, long_mm):
    """Grow a mark's stroke by a fixed width on every side.

    The outlined cross is a drawn outline, and at 1.89 mm on an 8 mm
    ball that outline is 28 microns wide: a scratch, not an engraving.
    Scale does not fix it - the mark would have to be 10 mm across to
    carry a 0.15 mm line - so the line itself has to grow. A distance
    transform does it evenly, inside corners and out, which a pen would
    not: every point within `each_side` of the ink becomes ink.

    The footprint barely moves, because an outline grown outwards is
    still inside its own bounding box except at the extremes: 0.03 mm
    takes the mark's reach from 0.934 to 0.943 mm, so the lattice does
    not have to be solved again.
    """
    if each_side <= 0:
        return mask
    r = each_side / (long_mm / max(mask.shape))
    return ndimage.distance_transform_edt(~mask) <= r


def rotate(mask, deg):
    return ndimage.rotate(mask.astype(float), deg, order=1,
                          reshape=True, mode='constant', cval=0.0) > 0.5


def blind_bore(r, bore, depth, sections=96):
    """The cutter for a hole drilled from one side and stopping inside.

    The bead sits on a post, so it needs one hole, not a tunnel: the far
    pole stays closed and carries pattern like any other part of the
    ball. Under the wall is a 118-degree point, the angle a twist drill
    leaves, so the shape is one a workshop can produce rather than a
    flat-bottomed slot only a mill could cut.

    It is one revolved profile, not a cylinder unioned with a cone.
    Those two meet on a shared plane, and the union leaves a sliver of
    that plane behind - a forty-seven face disc of zero thickness, which
    is enough to cost the finished bead its watertightness.
    """
    b = bore / 2.0
    zb = r - depth
    tip = b / math.tan(math.radians(59.0))
    prof = np.array([[0.0, zb - tip], [b, zb], [b, r * 1.6], [0.0, r * 1.6]])
    return trimesh.creation.revolve(prof, sections=sections)


def spread(radius, n, cap_deg):
    """Marks at one spacing everywhere on the ball, poles included.

    A ball cannot be tiled by a grid of rows. Rows a fixed arc apart hold
    a whole number of marks, so every row's spacing is rounded to a
    different value, and above the last row there is nothing at all - the
    bald cap around the bore. Neither fault is fixable by choosing better
    numbers; a sphere simply has no regular tiling of that kind.

    A Fibonacci spiral does have the one property that matters: every
    point is the same distance from its neighbours, at the poles as much
    as the equator. Points are generated over the whole sphere and the
    caps dropped afterwards, so the spacing of what remains is the
    spacing of the whole.

    Only the drilled pole is kept clear. The other one is solid metal
    now and takes a mark like anywhere else, so clearing it too would
    put back the bald patch the spiral was chosen to avoid.
    """
    ga = math.pi * (3 - math.sqrt(5))
    lim = math.sin(math.radians(cap_deg))
    out = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        if z > lim:
            continue
        out.append((math.degrees((i * ga) % (2 * math.pi)) - 180,
                    math.degrees(math.asin(z))))
    return out


# The cube and its 26 directions, written as rings. That is all the
# reference is: a mark at the middle of a face, four more on the
# cardinals around it, four on the diagonals. On a sphere those are the
# cube's face centres, its edge midpoints at 45 degrees, and its corners
# at 35.26 - which is why the pattern closes up on itself with nothing
# left over and nothing touching. The hole takes the top face.
FACE, EDGE_EQ, EDGE_MID, CORNER = 0.0, 0.0, 45.0, 35.26439
GRID = dict(
    om=lambda sc: dict(lat=FACE, n=4, kinds=['om'], scale=sc, turn=0),
    card_eq=lambda k, sc: dict(lat=EDGE_EQ, n=4, kinds=[k], scale=sc, turn=45),
    card_up=lambda k, sc: dict(lat=EDGE_MID, n=4, kinds=[k], scale=sc, turn=0,
                               nest=False),
    diag=lambda k, sc: dict(lat=CORNER, n=4,
                            kinds=(k if isinstance(k, list) else [k]),
                            scale=sc, turn=45, nest=False,
                            kindflip=isinstance(k, list)),
    foot=lambda k, sc: dict(lat=-90, n=1, kinds=[k], scale=sc, mirror=False),
)


def _grid(cardinal='outl', diagonal='sq', om=1.20, cross=0.90, foot='n925',
          foot_scale=0.85, extra=None):
    r = [GRID['om'](om),
         GRID['card_eq'](cardinal, cross),
         GRID['card_up'](cardinal, cross),
         GRID['diag'](diagonal, cross)]
    if foot:
        r.append(GRID['foot'](foot, foot_scale))
    if extra:
        r.extend(extra)
    return r


# Three rings of eight, in columns, after the hand-edited placement. The
# equator alternates OM and the outlined cross; each ring carries the
# circled cross on the meridians of the OM, the outlined cross on the
# meridians between the OMs, and the squared cross on the four diagonals;
# 925 sits at the foot.
#
# EIGHTS_LAT is not a choice of taste. With eight to a ring the step
# along a ring and the step from the equator up to it are equal at one
# latitude only, 36.05 degrees, and that is the whole of "the same
# distance to each other" for this arrangement. Pushing the rings out
# towards 45 makes room for a larger OM and takes the ring step down
# with it: at 44.5 the steps run 1.93 / 2.72 / 2.75 mm instead of one
# figure.
EIGHTS_LAT = 36.05
EIGHTS_WIDE = 44.50


def _eights(lat, om, outl=0.840, sq=0.738, circ=0.635, n925=1.003,
            crosses=1.0):
    """`crosses` scales everything but the OM.

    These were sized against a 2200 px trace, which rounds the tips off
    the crosses and so under-reports how far their ink reaches. At 8800
    the four designs below all ran into themselves, by 0.011 to 0.045
    mm. The OM is the headline of each, so the crosses give way.
    """
    outl *= crosses; sq *= crosses; circ *= crosses; n925 *= crosses
    return [
        dict(lat=0, n=4, kinds=['om'], scale=om, turn=0),
        dict(lat=0, n=4, kinds=['outl'], scale=outl, turn=45),
        dict(lat=lat, n=2, kinds=['circ'], scale=circ, turn=0, nest=False),
        dict(lat=lat, n=2, kinds=['outl'], scale=outl, turn=90, nest=False),
        dict(lat=lat, n=4, kinds=['sq'], scale=sq, turn=45, nest=False),
        dict(lat=-90, n=1, kinds=['n925'], scale=n925, mirror=False),
    ]


# Offsetting the rings by half a step is what the Louis Vuitton ball
# does, and it is not only a matter of looks: with the rings turned 22.5
# degrees nothing sits directly under anything, the equal-step latitude
# moves from 36.05 to 31.55, and every step grows from 2.20 to 2.33 mm on
# a 7 mm ball. Staggering buys room.
EIGHTS_OFFSET_LAT = 31.55


def _eights_offset(lat, om, outl=0.840, sq=0.738, circ=0.635, n925=1.003,
                   crosses=1.0):
    outl *= crosses; sq *= crosses; circ *= crosses; n925 *= crosses
    return [
        dict(lat=0, n=4, kinds=['om'], scale=om, turn=0),
        dict(lat=0, n=4, kinds=['outl'], scale=outl, turn=45),
        dict(lat=lat, n=4, kinds=['circ'], scale=circ, turn=22.5, nest=False),
        dict(lat=lat, n=4, kinds=['sq'], scale=sq, turn=67.5, nest=False),
        dict(lat=-90, n=1, kinds=['n925'], scale=n925, mirror=False),
    ]


# The second hand edit: the same three bands, but with the OM taken up to
# 3.65 mm and the crosses cut back to make room. At that size it does not
# fit - seventeen pairs ran into each other, the worst by 0.45 mm -
# because an OM of 3.65 mm reaches 2.08 mm from its own centre and the
# equator only gives it 2.75 mm to the next mark. 3.32 mm is the largest
# that clears, and the rings then want splitting: whatever stands over an
# OM has to be pushed out, while the squared cross over the small
# equatorial cross can come in.
BIG = dict(om=3.07/2.70, outl=1.65/2.25, sq=1.40/2.10,
           circ=1.65/2.60, n925=2.65/2.50, om2=1.65/1.65,
           cross=1.80/1.60)
BIG_OM = dict(BIG, om=3.32/2.70, outl=1.35/2.25, circ=1.40/2.60)


def on_ball(z, dia, was=7.0):
    """The same design on a bigger ball.

    Every size in BIG was solved against a 7 mm ball. Arc distances and
    mark sizes both scale with the diameter, so scaling the marks by
    dia/7 keeps the drawing identical and multiplies every clearance by
    the same factor: the tightest pair goes from +0.12 mm to +0.14 on
    an 8 mm ball rather than needing to be solved again.
    """
    return {k: v * dia / was for k, v in z.items()}


def _eights_split(p_axis, p_diag, z=BIG, diag='cross', line='outl'):
    """Columns as drawn, but the two rings at their own latitudes.

    `diag` is what the eight marks on the 45 degree diagonals carry.
    The squared cross was there first - a square of cut ground with the
    cross standing in it. The bare cross is what sits there now, cut
    into the ball with no square round it, at 1.80 mm: bigger than the
    1.40 mm plate it replaces, because without the square to fill the
    position the mark has to carry it alone, and sized to read at the
    same weight as the outlined cross beside it (0.87 mm of reach
    against 0.80). Those positions would hold 2.06 mm before anything
    on the ball got tighter than it already is.
    """
    return [
        dict(lat=0, n=4, kinds=['om'], scale=z['om'], turn=0),
        dict(lat=0, n=4, kinds=[line], scale=z[line], turn=45),
        dict(lat=p_axis, n=2, kinds=['circ'], scale=z['circ'], turn=0, nest=False),
        dict(lat=p_axis, n=2, kinds=[line], scale=z[line], turn=90, nest=False),
        dict(lat=p_diag, n=4, kinds=[diag], scale=z[diag], turn=45,
             nest=False),
        dict(lat=-90, n=1, kinds=['n925'], scale=z['n925'], mirror=False),
    ]


LAYOUTS = [
    dict(name='Monogram Eights, OM 3.51', note='four big OM round the middle, '
         'bare crosses on the diagonals, outlined crosses between them, the '
         'circled cross raised out of its field; an 8 mm ball',
         ball=dict(dia=8.0, cut=True),
         rings=_eights_split(45.0, 45.0, z=on_ball(BIG, 8.0))),

    dict(name='Monogram Eights, OM 3.51, No Outline', note='the outlined '
         'cross replaced by the bare one, smaller; its line is 28 microns '
         'wide and will not survive a casting',
         ball=dict(dia=8.0, cut=True),
         rings=_eights_split(45.0, 45.0, z=dict(on_ball(BIG, 8.0),
                                                outl=1.55/1.60), line='cross')),

    dict(name='Monogram Eights, OM 3.51, Squared', note='the same with the '
         'squared cross back on the diagonals',
         ball=dict(dia=8.0, cut=True),
         rings=_eights_split(45.0, 45.0, z=on_ball(BIG, 8.0), diag='sq')),

    dict(name='Monogram Eights, OM 3.07', note='the same drawing on a 7 mm '
         'ball, where it was first solved',
         ball=dict(dia=7.0, cut=True),
         rings=_eights_split(45.0, 45.0)),

    dict(name='Monogram Eights, OM 3.32', note='the OM kept at 3.32 mm by '
         'taking the four equatorial crosses down to 1.35 mm instead',
         ball=dict(dia=7.0, cut=True),
         rings=_eights_split(45.0, 45.0, z=BIG_OM)),

    dict(name='Monogram Eights, OM 3.32 Split', note='the same OM with the two '
         'rings at their own latitudes, 54 over the OM and 36 over the small '
         'cross, which evens the steps',
         ball=dict(dia=7.0, cut=True),
         rings=_eights_split(54.0, 36.0, z=dict(BIG, n925=2.40/2.50))),

    dict(name='Monogram Eights, Offset', note='the rings turned half a step, '
         'the way the LV ball staggers its rows: nothing sits directly under '
         'anything, and every step is 2.33 mm',
         ball=dict(dia=7.0, cut=True),
         rings=_eights_offset(EIGHTS_OFFSET_LAT, om=0.803, crosses=0.860)),

    dict(name='Monogram Eights', note='three rings of eight in columns, every '
         'step the same: 2.20 mm on a 7 mm ball, nothing touching',
         ball=dict(dia=7.0, cut=True),
         rings=_eights(EIGHTS_LAT, om=0.807, crosses=0.857)),

    dict(name='Monogram Eights, Big OM', note='the rings pushed out to make '
         'room for a 3.10 mm OM; the steps are no longer equal',
         ball=dict(dia=7.0, cut=True),
         rings=_eights(EIGHTS_WIDE, om=1.148, crosses=0.823)),

    dict(name='Monogram Eights, Full Size', note='the OM at 3.54 mm with every '
         'step equal, which a 7 mm ball cannot hold - this one wants 9.5 mm',
         ball=dict(dia=9.5, cut=True),
         rings=_eights(EIGHTS_LAT, om=1.311, crosses=0.832)),


    dict(name='Monogram Grid', note='the reference: four OM round the middle, '
         'outlined crosses on the cardinals, squared and circled crosses '
         'alternating on the diagonals, 925 at the foot',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(diagonal=['sq', 'circ'])),

    dict(name='Monogram Grid, Four Motifs', note='the same without the circled '
         'cross: squared on every diagonal',
         ball=dict(dia=8.0, cut=False),
         rings=_grid()),

    dict(name='Monogram Grid, Swapped', note='the same lattice with the two '
         'crosses the other way round',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(cardinal='sq', diagonal='outl', cross=0.84)),

    dict(name='Monogram Grid, Circled', note='circled crosses on the diagonals',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(diagonal='circ', cross=0.86)),

    dict(name='Monogram Grid, Three Crosses', note='outlined on the cardinals, '
         'squared above and below, circled round the middle',
         ball=dict(dia=8.0, cut=False),
         rings=[GRID['om'](1.20),
                GRID['card_eq']('circ', 0.86),
                GRID['card_up']('outl', 0.90),
                GRID['diag']('sq', 0.90),
                GRID['foot']('n925', 0.85)]),

    dict(name='Monogram Grid, Plain', note='every cross the small solid one, '
         'so the OM carries the whole pattern',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(cardinal='cross', diagonal='cross', cross=1.05)),

    dict(name='Monogram Grid, Big OM', note='the OM as large as the lattice '
         'will take, crosses eased back',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(om=1.32, cross=0.84)),

    dict(name='Monogram Grid, Quiet OM', note='a smaller OM, the crosses '
         'given their full drawn size',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(om=0.96, cross=0.96)),

    dict(name='Monogram Grid, Crowned', note='a ring of small crosses between '
         'the pattern and the hole, top and bottom',
         ball=dict(dia=8.0, cut=False),
         rings=_grid(extra=[dict(lat=70, n=4, kinds=['cross'], scale=0.90,
                                 turn=45, mirror=False)])),

    dict(name='Monogram Grid, Two OM', note='OM on two opposite faces only, '
         'circled crosses on the other two',
         ball=dict(dia=8.0, cut=False),
         rings=[dict(lat=0, n=2, kinds=['om'], scale=1.30, turn=0),
                dict(lat=0, n=2, kinds=['circ'], scale=0.90, turn=90),
                GRID['card_eq']('outl', 0.90),
                GRID['card_up']('outl', 0.90),
                GRID['diag']('sq', 0.90),
                GRID['foot']('n925', 0.85)]),

    dict(name='Monogram Grid, 925 Band', note='925 four times round the '
         'middle instead of once at the foot',
         ball=dict(dia=8.0, cut=False),
         rings=[GRID['om'](1.20),
                GRID['card_eq']('n925', 0.80),
                GRID['card_up']('outl', 0.90),
                GRID['diag']('sq', 0.90),
                GRID['foot']('cross', 1.00)]),

    dict(name='Monogram Grid, Bare', note='four OM and 925, polished ball '
         'between them',
         ball=dict(dia=8.0, cut=False),
         rings=[GRID['om'](1.32), GRID['foot']('n925', 0.90)]),

    dict(name='Monogram Grid, Six OM', note='OM on every face the hole leaves '
         'free, 925 moved into the pattern',
         ball=dict(dia=8.0, cut=False),
         rings=[GRID['om'](1.16),
                GRID['foot']('om', 1.16),
                GRID['card_eq']('n925', 0.78),
                GRID['card_up']('outl', 0.88),
                GRID['diag']('sq', 0.88)]),
]

LAYOUT_BY_NAME = {d['name']: d for d in LAYOUTS}


def ring_places(ring):
    """One ring of marks: latitude, count, motifs, size, turn, mirror, nest.

    `nest` offsets the southern copy by half a step so the marks sit
    between their northern counterparts rather than below them. That is
    right for a medallion and wrong for a lattice: the cube's corners
    share a longitude north and south, and nesting them moved each
    southern corner directly under an OM, 2.40 mm away instead of 3.73,
    which put every design in the library through the middle of its own
    monogram.
    """
    lat = float(ring.get('lat', 0.0))
    n = int(ring.get('n', 0))
    if not n or not ring.get('kinds'):
        return []
    sc = float(ring.get('scale', 1.0))
    turn = float(ring.get('turn', 0.0))
    mirror = ring.get('mirror', True) and abs(lat) > 1e-6
    nest = ring.get('nest', True)
    # `kindflip` starts the southern copy on the next motif. On the cube's
    # eight corners that splits them into the two tetrahedra - alternating
    # round the northern four and alternating the other way round the
    # southern four is exactly the even and odd sign products - so each
    # face looks out on two of one motif and two of the other, diagonally
    # opposite. It is the only way to get a fifth motif onto this lattice:
    # the four cardinals and the four marks on the silhouette are the same
    # orbit of edge midpoints, so they cannot differ from one another.
    flip = 1 if ring.get('kindflip') else 0
    out = []
    for sign in ((1, -1) if mirror else (1,)):
        off = 180.0 / n if (sign < 0 and nest) else 0.0
        base = flip if sign < 0 else 0
        for c in range(n):
            k = BYNAME[ring['kinds'][(c + base) % len(ring['kinds'])]]
            out.append(((-180.0 + 360.0 * c / n + off + turn + 180) % 360 - 180,
                        sign * lat, k, PATTERN[k][4] * sc))
    return out


def fill_places(spec, placed, radius, cap_deg=76.0, clearance=0.60):
    """Drop a Fibonacci set over what is left and keep what fits.

    "The rest filled with crosses" has no grid to fall back on: a sphere
    admits no tiling of rows that keeps one spacing. So the filler is the
    spiral again - every point the same distance from its neighbours -
    generated over the whole ball and then thinned against what the rings
    have already taken. A point survives if the gap between its edge and
    the edge of every mark already placed is positive; `clearance` says
    how much of each mark's half-width counts as its edge.
    """
    n = int(spec.get('n', 0))
    if not n or not spec.get('kinds'):
        return []
    sc = float(spec.get('scale', 1.0))
    kinds = [BYNAME[k] for k in spec['kinds']]
    pts = spread(radius, n, cap_deg)
    if not pts:
        return []
    weights = spec.get('weights') or [PATTERN[k][5] for k in kinds]
    order = deal(pts, weights)
    out = []
    kept = list(placed)
    for (lo, la), oi in zip(pts, order):
        k = kinds[oi % len(kinds)]
        mm = PATTERN[k][4] * sc
        c = _unit(lo, la)
        ok = True
        for plo, pla, pk, pmm in kept:
            d = math.acos(max(-1.0, min(1.0, _dot(c, _unit(plo, pla))))) * radius
            if d < clearance * (mm + pmm) / 2.0 + 0.10:
                ok = False
                break
        if ok:
            out.append((lo, la, k, mm))
            kept.append(out[-1])
    return out


def _unit(lon, lat):
    la, lo = math.radians(lat), math.radians(lon)
    c = math.cos(la)
    return (c * math.cos(lo), c * math.sin(lo), math.sin(la))


def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def layout(name, radius, cap_deg=76.0):
    """Every mark a named design puts on the ball."""
    d = LAYOUT_BY_NAME.get(name)
    if d is None:
        raise SystemExit(f'no design called {name!r}; '
                         f'try one of: {", ".join(x["name"] for x in LAYOUTS)}')
    places = []
    for ring in d.get('rings') or []:
        places.extend(ring_places(ring))
    if d.get('fill'):
        places.extend(fill_places(d['fill'], places, radius, cap_deg))
    return places


def deal(places, weights, near=6):
    """Give each mark a kind, so that no two touching marks share one.

    Dealing them out in a fixed cycle does not work, and the reason is
    worth keeping. On a Fibonacci spiral the points next to each other in
    SPACE are a Fibonacci number apart in INDEX - 5, 8 or 13 at this
    count - so a cycle of any of those lengths hands every neighbour the
    same kind, and one eight long put the OMs in bands. Nine broke the
    bands but not the clumps, because a cycle knows nothing about where
    its marks land.

    So the neighbours are found and then coloured. Each mark takes the
    kind that none of its neighbours has and that is furthest behind its
    share, which spaces the OMs out by construction rather than by luck.
    The weights set how often each kind wants to appear.
    """
    from scipy.spatial import cKDTree
    pts = np.array([[math.cos(math.radians(la)) * math.cos(math.radians(lo)),
                     math.cos(math.radians(la)) * math.sin(math.radians(lo)),
                     math.sin(math.radians(la))] for lo, la in places])
    k = min(near + 1, len(pts))
    nb = cKDTree(pts).query(pts, k=k)[1]
    w = np.asarray(weights, float)
    w /= w.sum()
    kind = [-1] * len(pts)
    count = np.zeros(len(w))
    for i in range(len(pts)):
        taken = {kind[j] for j in nb[i][1:] if kind[j] >= 0}
        free = [t for t in range(len(w)) if t not in taken] or list(range(len(w)))
        pick = min(free, key=lambda t: count[t] / w[t])
        kind[i] = pick
        count[pick] += 1
    return kind


def spacing(radius, n):
    """Centre-to-centre distance a Fibonacci set of n points gives."""
    return math.sqrt(4 * math.pi * radius ** 2 / (n * math.sqrt(3) / 2))


def paint(fields, places, radius, W, Hh, bases):
    """Depth map in millimetres, each mark laid flat on the ball.

    What is carried is not whether a pixel is inked but how far inside
    the ink it lies, read from the stamp's own distance field and
    scaled by the size the mark is drawn at. The projection below is
    distance-preserving, so that figure is in true millimetres of arc
    wherever the mark sits, which is what the old equirectangular
    distance transform could not say.

    The obvious way is to stamp into the equirectangular map and stretch
    by 1 / cos(latitude) to pay for the squeeze. That works for a mark so
    small it sits at one latitude. These do not: a 2.4 mm mark on a 4 mm
    ball spans about thirty-five degrees, and cos(latitude) changes a
    long way across the mark itself. One factor taken at the centre
    cannot straighten that, so the square frame round the cross came out
    as a curved trapezoid - wider along its lower edge than its upper,
    and bowed.

    So the marks are not stamped into the map at all. Each one gets a
    frame on the sphere - east and north at its own centre - and every
    map pixel near it is carried into that frame by an azimuthal
    equidistant projection, which is the one that keeps distance from the
    centre. A square stays square because its sides stay the same length
    in millimetres of arc, which is what a square means on a ball.
    """
    depth = np.zeros((Hh, W), np.float32)
    for lon, lat, which, long_mm in places:
        s = fields[which]
        grow = long_mm / bases[which]      # the field was measured at base size
        if s.shape[1] >= s.shape[0]:
            w_mm, h_mm = long_mm, long_mm * s.shape[0] / s.shape[1]
        else:
            h_mm, w_mm = long_mm, long_mm * s.shape[1] / s.shape[0]
        la, lo = math.radians(lat), math.radians(lon)
        c = np.array([math.cos(la) * math.cos(lo),
                      math.cos(la) * math.sin(lo), math.sin(la)])
        e = np.array([-math.sin(lo), math.cos(lo), 0.0])
        nth = np.cross(c, e)

        # only the map rows and columns the mark can reach
        rad = math.hypot(w_mm, h_mm) / 2.0 / radius            # radians of arc
        dlat = math.degrees(rad) * 1.15
        dlon = dlat / max(math.cos(la), 1e-3)
        r0 = int((90 - lat - dlat) / 180.0 * Hh)
        r1 = int((90 - lat + dlat) / 180.0 * Hh) + 2
        c0 = int((lon + 180 - dlon) / 360.0 * W)
        c1 = int((lon + 180 + dlon) / 360.0 * W) + 2
        # A mark at a pole spans every longitude there is, and dividing by
        # cos(latitude) says so: at lat -90 the clamp of 1e-3 turns a 35
        # degree box into 35,000, and the column array it asks for runs the
        # machine out of memory before anything is painted. One map width
        # is the most any mark can need.
        if c1 - c0 > W:
            c0, c1 = 0, W
        rr = np.clip(np.arange(r0, r1), 0, Hh - 1)
        cc = np.arange(c0, c1)
        if not len(rr) or not len(cc):
            continue
        LA = np.radians(90 - (rr + 0.5) / Hh * 180.0)[:, None]
        LO = np.radians((cc + 0.5) / W * 360.0 - 180.0)[None, :]
        px = np.cos(LA) * np.cos(LO)
        py = np.cos(LA) * np.sin(LO)
        pz = np.broadcast_to(np.sin(LA), px.shape)
        dot = np.clip(px * c[0] + py * c[1] + pz * c[2], -1.0, 1.0)
        # azimuthal equidistant: keep the arc distance from the centre
        ang = np.arccos(dot)
        ue = px * e[0] + py * e[1] + pz * e[2]
        un = px * nth[0] + py * nth[1] + pz * nth[2]
        norm = np.hypot(ue, un)
        norm[norm < 1e-12] = 1e-12
        u = radius * ang * ue / norm                       # mm, east
        v = radius * ang * un / norm                       # mm, north
        col = (u / w_mm + 0.5) * s.shape[1]
        row = (0.5 - v / h_mm) * s.shape[0]
        ok = (dot > 0) & (col >= 0) & (col < s.shape[1]) \
            & (row >= 0) & (row < s.shape[0])
        if not ok.any():
            continue
        # bilinear, so the profile does not inherit the stamp's pixel grid
        val = np.zeros(col.shape, np.float32)
        if ok.any():
            cf = col[ok]; rf = row[ok]
            c0 = np.floor(cf).astype(int); r0 = np.floor(rf).astype(int)
            c1 = np.minimum(c0 + 1, s.shape[1] - 1)
            r1 = np.minimum(r0 + 1, s.shape[0] - 1)
            fx = (cf - c0).astype(np.float32); fy = (rf - r0).astype(np.float32)
            v = ((s[r0, c0] * (1 - fx) + s[r0, c1] * fx) * (1 - fy)
                 + (s[r1, c0] * (1 - fx) + s[r1, c1] * fx) * fy)
            val[ok] = v * grow
        block = depth[np.ix_(rr, cc % W)]
        depth[np.ix_(rr, cc % W)] = np.maximum(block, val)
    return depth


def relief(depth, radius, W, Hh, height, inset):
    """Depth or height from distance to the edge of the mark.

    A laser mark is not a dome. It goes to its full depth within a few
    hundredths of a millimetre of the edge and stays flat across the
    middle, so the profile here is a smoothstep over `inset` rather than
    an arc over half the stroke - flat floor, crisp wall, a slightly
    eased lip so it does not read as a stamped-out hole.
    """
    t = np.clip(depth / max(inset, 1e-9), 0.0, 1.0)
    return height * (t * t * (3.0 - 2.0 * t))


# The circle round the cross, drawn two ways. As a LINE the ring is the
# mark, and 1.25 times the cross is right: the cross fills its circle
# the way it does on the page. INVERTED the field is the mark - the
# ground inside the circle is what the cutter takes out - and 1.25
# pinches that field to 0.13 mm where the cross's four tips reach for
# the rim. The lip eases over 0.05 mm on each side, so a 0.16 mm
# channel is very nearly a V-groove; magnified, it read as crumpled
# wire. The squared cross is the same inversion and looks right because
# its corners leave real pockets of ground.
#
# 1.28, with the mark at 1.89 mm on an 8 mm ball, stands the cross
# 1.38 mm across in a field 0.23 mm wide - 68 per cent of the cut at
# full depth against the squared cross's 63, so the ground still reads
# as ground. The mark itself is capped by the OM at the equator, which
# gives it 1.89 mm whatever the ratio; past that only the ratio moves,
# and it trades straight across: 1.20 would stand the cross 1.47 mm but
# puts the field back to 0.18, which is where it was when it looked
# like crumpled wire.
RING_RATIO = 1.25
FIELD_RATIO = 1.28

# How much heavier the outlined cross's line is drawn, in mm of the stamp
# at its nominal 2.25. At 1.89 mm on the ball that is 0.030 mm a side and
# takes the line from 28 microns to 63 - the most the drawing takes. Past
# about 0.04 the notches between the arms fill in and it stops being the
# mark: see fatten().
OUTLINE_WEIGHT = 0.036


def ringed(mask, ratio=RING_RATIO, weight=0.075, pad=8, invert=False):
    """The cross inside its ring, with the ring drawn rather than traced.

    On the page that ring is a hairline in light grey. The 128 threshold
    drops it, which is why the bead has been going out carrying the bare
    cross twice over and no circled one at all - the crop was right, the
    threshold took the circle off it. Raising the threshold gets it back
    at 116 px instead of 93, so the radius is measurable: 1.25 times the
    cross.

    Capturing it would not help though. Scaled to a 2.25 mm mark on an
    8 mm ball that hairline comes to about three hundredths of a
    millimetre, far under anything that can be cut or cast. So the
    radius is kept and the weight is redrawn at something that reads.
    """
    h, w = mask.shape
    R = int(round(max(h, w) / 2.0 * ratio))
    n = 2 * (R + pad) + 1
    out = np.zeros((n, n), bool)
    cy = cx = n // 2
    y0, x0 = cy - h // 2, cx - w // 2
    out[y0:y0 + h, x0:x0 + w] |= mask
    yy, xx = np.mgrid[:n, :n]
    d = np.hypot(yy - cy, xx - cx)
    if invert:
        # the ground inside the circle is what gets cut, and the cross is
        # left standing at the surface of the ball
        return (d <= R) & ~out
    t = max(2.0, weight * 2 * R)
    out |= (d <= R) & (d >= R - t)
    return out


def framed(mask, border=0.055):
    """A mark the right way round, inside its own square.

    The tile carries this element in reverse - a filled square with the
    cross knocked out of it - so used as it comes the square is the mark
    and the cross is the gap. Inverted, the cross is the mark; the square
    is then drawn back round it as a rule, which is what it is on the
    tile.
    """
    m = ~mask
    b = max(2, int(round(border * min(m.shape))))
    m[:b, :] = m[-b:, :] = True
    m[:, :b] = m[:, -b:] = True
    return m


def build(stamps, out, dia=8.0, bore=1.2, depth=4.0, n=30, mark=1.0,
          design=None, height=0.10, radii=None,
          inset=0.025, cap=76.0, sub=7, W=7200, Hh=3600, cut=False):
    # embossed, the marks stand proud and the ball under them is
    # smaller by that much; engraved, the ball is the full size and the
    # marks go into it. Either way the bead measures the 8 mm it is
    # called.
    r = dia / 2.0 if cut else (dia - 2 * height) / 2.0
    places = [(lo, la, k, mm * mark)
              for lo, la, k, mm in layout(design, r, cap)]

    # nothing may run into anything else. One number per pair, and the
    # smallest decides; it is printed either way so the figure is on the
    # record rather than taken on trust.
    if radii:
        g = gaps(places, r, radii)
        if g:
            worst, i, j, d = g[0]
            a, b = PATTERN[places[i][2]][0], PATTERN[places[j][2]][0]
            print(f'   tightest pair {a} to {b}: centres {d:.2f} mm apart, '
                  f'edge to edge {worst:+.2f} mm'
                  + ('   OVERLAP' if worst < 0 else '   clear'))
            if worst < 0:
                bad = sum(1 for t in g if t[0] < 0)
                raise SystemExit(f'{bad} pair(s) overlap; this is not the '
                                 'pattern that was asked for')
    bases = [q[4] for q in PATTERN]
    ink = paint(stamps, places, r, W, Hh, bases)
    rel = relief(ink, r, W, Hh, height, inset)
    if cut:
        rel = -rel
    # Only enough to take the staircase off the map's own pixels. The map
    # is 7200 wide now, so a pixel is 3.5 microns at the equator and half
    # a pixel of blur is under 2 - well inside the mesh's own 19 micron
    # triangle, which is what actually limits the edge. The old 1.2 at
    # 3600 was blurring 8 microns of a 50 micron wall.
    rel = ndimage.gaussian_filter(rel, 0.6, mode='wrap')
    ball = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    v = ball.vertices.view(np.ndarray).copy()
    n_ = np.linalg.norm(v, axis=1)
    lat = np.degrees(np.arcsin(np.clip(v[:, 2] / n_, -1, 1)))
    lon = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
    rr = (90 - lat) / 180.0 * Hh
    cc = (lon + 180) / 360.0 * W
    dr = ndimage.map_coordinates(rel, [rr, cc], order=1, mode='wrap')
    v *= ((r + dr) / n_)[:, None]
    m = trimesh.Trimesh(vertices=v, faces=ball.faces.view(np.ndarray).copy(),
                        process=False)
    m.process(validate=True)
    if bore and depth > 0:
        m = trimesh.boolean.difference([m, blind_bore(r, bore, depth)],
                                       engine='manifold')
    m.merge_vertices()
    m.process(validate=True)
    m.fix_normals()
    m.export(out)
    back = trimesh.load(out)
    b = back.split(only_watertight=False)
    print(f'{out}: {len(back.faces)} triangles, '
          f'{back.extents[0]:.2f} x {back.extents[1]:.2f} x {back.extents[2]:.2f} mm, '
          f'{len(b)} bodies, closed: {all(x.is_watertight for x in b)}, '
          f'{os.path.getsize(out)/1e6:.1f} MB')
    used = sorted({PATTERN[k][0] for _, _, k, _ in places})
    print(f'   {design}: {len(places)} marks, {len(used)} motifs ({", ".join(used)}), '
          f'{spacing(r, len(places)):.2f} mm apart on average, '
          f'{min(q[3] for q in places):.2f} to {max(q[3] for q in places):.2f} mm across, '
          f'relief {height:.2f} mm, hole {bore:.2f} mm x {depth:.2f} mm deep')
    return m, ink, rel


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--dia', type=float, default=None,
                   help='ball diameter; defaults to the one the chosen '
                        'design was worked out for')
    a.add_argument('--bore', type=float, default=1.2,
                   help='diameter of the hole the post sits in')
    a.add_argument('--bore-depth', type=float, default=4.0,
                   help='how far the hole goes in; it is blind, so the '
                        'far side of the bead stays closed')
    a.add_argument('--marks', type=int, default=30,
                   help='marks over the whole sphere before the caps are '
                        'dropped; fewer means bigger and further apart')
    a.add_argument('--layout', default='Four Crowns',
                   help='which design to build; --list names them all')
    a.add_argument('--list', action='store_true',
                   help='print the designs and stop')
    a.add_argument('--simple', action='store_true',
                   help='OM and the framed cross only - the page pattern '
                        'thinned for a ball this small')

    a.add_argument('--mark', type=float, default=1.0,
                   help='scale every mark by this')
    a.add_argument('--relief', type=float, default=0.10)
    a.add_argument('--inset', type=float, default=0.025,
                   help='how far in from the edge the cut reaches full '
                        'depth; smaller is a steeper wall')
    a.add_argument('--cut', action='store_true',
                   help='engrave the marks into the ball instead of '
                        'raising them off it')
    a.add_argument('--stamp-px', type=int, default=8800,
                   help='resolution the motif page is rendered at. The '
                        'outlines are traced from this, so it sets how fine '
                        'the engraved wall can be: at the old 2200 the '
                        'outlined cross was 117 px across, a step of 14 '
                        'microns against a 50 micron lip, and the steps '
                        'showed on the wall. It also sets how much ink the '
                        'clearance check can see: a coarse trace drops the '
                        'sharp tips of the crosses and reports the marks '
                        'smaller than they are, so the gaps read better than '
                        'they were. The figure settles by about 8800.')
    a.add_argument('--open-circle', dest='solid_circle', action='store_false',
                   help='cut the circled cross itself, the old way round. By '
                        'default the ground inside its circle is cut instead '
                        'and the cross is left standing at the surface')
    a.set_defaults(solid_circle=True)
    a.add_argument('--fatten-outline', type=float, default=OUTLINE_WEIGHT,
                   metavar='MM',
                   help="grow the outlined cross's line by this much on "
                        "every side, in mm of the mark at its nominal size")
    a.add_argument('--sub', type=int, default=7)
    a.add_argument('--out', default='assets/om-bead/om-bead-8mm.stl')
    o = a.parse_args()
    if o.list:
        for d in LAYOUTS:
            print(f'{d["name"]:22s} {d["note"]}')
        raise SystemExit(0)
    os.makedirs(os.path.dirname(o.out), exist_ok=True)
    _ball = (LAYOUT_BY_NAME.get(o.layout) or {}).get('ball') or {}
    if o.dia is None:
        o.dia = _ball.get('dia', 8.0)
    if not o.cut and _ball.get('cut'):
        o.cut = True
    print(f'{o.layout}: {o.dia:.2f} mm ball, '
          + ('engraved' if o.cut else 'embossed'))
    if o.simple:
        PATTERN[:] = [q for q in PATTERN if q[0] in ('om', 'sq')]
    stamps = []
    for nm, b, _, _, mm, _ in PATTERN:
        m = despeckle(stamp_from_pdf(PAGE, box=b, px=o.stamp_px), mm)
        if nm == 'outl':
            m = fatten(m, o.fatten_outline, mm)
        if nm == 'circ':
            m = ringed(m, ratio=FIELD_RATIO if o.solid_circle else RING_RATIO,
                       invert=o.solid_circle)
        stamps.append(m)
    radii = [ink_radius(st, q[4]) for st, q in zip(stamps, PATTERN)]
    fields = [edge_distance(st, q[4]) for st, q in zip(stamps, PATTERN)]
    for (nm, _, _, _, mm, _), st, fd in zip(PATTERN, stamps, fields):
        print(f'   {nm:5s} {st.shape[1]:5d} x {st.shape[0]:5d} px   '
              f'{mm:.2f} mm, {mm/st.shape[1]*1000:5.1f} um a pixel   '
              f'deepest {fd.max():.3f} mm in')
    build(fields, o.out, dia=o.dia, bore=o.bore, depth=o.bore_depth,
          n=o.marks, mark=o.mark, radii=radii, inset=o.inset,
          design=o.layout, height=o.relief, sub=o.sub, cut=o.cut)
