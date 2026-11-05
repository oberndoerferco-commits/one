#!/usr/bin/env python3
"""The TraxNYC crest split into the two things a struck button needs.

    silhouette   the quatrefoil outline, filled - the blank the button is
    relief       the band and the eagle head - what stands proud of it

In the drawing the head is an island floating inside the band, 1.01 mm
clear of it on a 138.6 mm crest. Carried on a button it does not have to
be joined to anything: the blank under it holds it, and the clearance is
a groove in a face rather than a gap between two parts. That is the whole
reason this is a button and not six pieces like the PA & CO lockup.

What the relief has to satisfy is the tooling. Measured on the solid
crest, as a fraction of its width:

    thinnest band             W / 39.1      1.28 mm at 50
    thinnest head stroke      W / 46.9      1.07 mm at 50
    pupil, as a recess        W / 57.3      0.87 mm at 50
    head to band clearance    W / 136.6     0.37 mm at 50

and one place where the drawing is simply not manufacturable at any
size: the iris meets the upper lid at a tangent, leaving 0.154 mm of
metal between the two halves of the eye white on a 138.6 mm crest and
0.06 mm at 50. A tangency is a knife edge whatever it is scaled to.

None of that is patched spot by spot. The relief is passed through what
a round-nosed cutter can actually leave behind - see tool() - which
closes the sub-size grooves, drops the recesses too small to enter, and
resolves the tangency by the same stroke. It costs a quarter of one
per cent of the drawn area at 50 mm, and what it visibly changes is the
eye: below about 57 mm the white above and below the iris is a tenth of
a millimetre, so what survives is the two corners of the almond and the
pupil. That is what the drawing means at this size.
"""
import argparse
import math
import os
import sys

import numpy as np
import pymupdf
from scipy import ndimage
from shapely import affinity
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union
from skimage.morphology import medial_axis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paco_bold import MM, assemble, subpaths                      # noqa: E402

SRC = 'assets/traxnyc-crest/traxnyc-crest-solid.pdf'


def artwork(src, width):
    """The crest at `width` mm across, centred on the origin, y up."""
    pg = pymupdf.open(src)[0]
    g = assemble([np.array(r) for r in subpaths(pg)])
    g = affinity.scale(g, 1, -1, origin=(0, 0))        # PDF y runs down
    # to the drawing's own extent, not the page's: the source carries a
    # 4.2 mm margin, and scaling by the page makes a 50 mm crest 47 across
    x0, y0, x1, y1 = g.bounds
    g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
    k = width / max(x1 - x0, y1 - y0)
    return affinity.scale(g, k, k, origin=(0, 0))


def pieces(g):
    return sorted((g.geoms if hasattr(g, 'geoms') else [g]), key=lambda s: -s.area)


def silhouette(g):
    """The blank: the outer ring's own outline, holes and island discarded."""
    return Polygon(pieces(g)[0].exterior)


def drop_small_holes(g, least):
    """Fill any recess too small for the cutter to reach the bottom of."""
    out, dropped = [], []
    for s in pieces(g):
        keep = []
        for h in s.interiors:
            d = 2 * math.sqrt(Polygon(h).area / math.pi)
            if d >= least:
                keep.append(h)
            else:
                dropped.append(d)
        out.append(Polygon(s.exterior, keep))
    return (MultiPolygon(out) if len(out) > 1 else out[0]), dropped


def _ends(sk):
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8),
                          mode='constant') - sk
    return sk & (nb <= 1)


def _raster(g, ppmm, pad=2.0):
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = g.bounds
    w = int((x1 - x0 + 2 * pad) * ppmm) + 1
    h = int((y1 - y0 + 2 * pad) * ppmm) + 1
    im = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(im)

    def xy(p):
        return ((p[0] - x0 + pad) * ppmm, (y1 - p[1] + pad) * ppmm)
    for s in pieces(g):
        dr.polygon([xy(p) for p in s.exterior.coords], fill=255)
        for r in s.interiors:
            dr.polygon([xy(p) for p in r.coords], fill=0)
    return np.asarray(im) > 127, (x0 - pad, y1 + pad)


def tool(blank, relief, cutter, fill, rounds=2):
    """Keep only what a cutter of radius `cutter` can leave behind.

    A pocket in the die is swept by a round-nosed cutter, so the die can
    only hold a recess where a disc of that radius fits. Opening the air
    with that disc - erode, then dilate - is not an approximation of the
    tooling, it IS the tooling: every groove narrower than the cutter
    closes, every pocket too small to enter disappears, and nothing else
    moves. The relief is then opened in turn with a smaller disc, because
    a ridge thinner than `fill` will not fill even where a cutter could
    cut around it.

    This replaces measuring the drawing for thin spots and patching them
    one at a time. That was tried first here and it does not work: the
    eye alone throws five near-tangencies within three millimetres, and
    a disc dropped on each leaves the eye looking shot through. It also
    repeats a mistake the PA & CO measurement already recorded, from the
    other direction - a disc cannot enter a corner sharper than itself,
    so corner after corner reads as a defect. Applying the disc instead
    of measuring with it gets the right answer from the same fact: the
    corners round because the tool rounds them.
    """
    def clean(g, least_area):
        # An opening on a polygon this size leaves slivers a few microns
        # wide where the two buffers do not land on the same arc. Left in,
        # they are counted as recesses and they measure as the narrowest
        # feature on the part, which is nonsense: they are not in the
        # drawing and the tool could not cut them.
        g = g.buffer(0).simplify(cutter / 60, preserve_topology=True).buffer(0)
        keep = [p for p in pieces(g) if p.area >= least_area]
        return unary_union(keep) if keep else g

    air = blank.difference(relief)
    for _ in range(rounds):
        air = clean(air.buffer(-cutter, quad_segs=16).buffer(cutter, quad_segs=16),
                    math.pi * cutter ** 2)
        relief = clean(blank.difference(air)
                       .buffer(-fill, quad_segs=16).buffer(fill, quad_segs=16),
                       math.pi * fill ** 2)
        air = blank.difference(relief)
    return relief.intersection(blank), clean(air, math.pi * cutter ** 2)


def measure(g, ppmm=40, skip_mm=0.8):
    """(thinnest metal, tightest channel in the air), terminals excluded."""
    m, _ = _raster(g, ppmm)
    out = []
    for mask in (m, ~m):
        sk, dist = medial_axis(mask, return_distance=True)
        r = max(1, int(round(skip_mm * ppmm)))
        keep = sk & ~ndimage.binary_dilation(_ends(sk),
                                             np.ones((2 * r + 1, 2 * r + 1), bool))
        out.append(float((2 * dist[keep] / ppmm).min()) if keep.any() else 99.0)
    return out[0], out[1]


def prepare(src, width, cutter, fill):
    """(blank, relief, report) for a button `width` mm across."""
    g = artwork(src, width)
    blank = silhouette(g)
    drawn = unary_union(list(pieces(g))).intersection(blank)
    relief, air = tool(blank, drawn, cutter / 2, fill / 2)
    lost = drawn.difference(relief).area + relief.difference(drawn).area
    return blank, relief, dict(moved=lost, drawn=drawn.area,
                               recesses=len(pieces(air)))


def write_pdf(geoms, path, pad=2.0):
    x0, y0, x1, y1 = unary_union([g for g, _ in geoms]).bounds
    doc = pymupdf.open()
    pg = doc.new_page(width=(x1 - x0 + 2 * pad) * MM, height=(y1 - y0 + 2 * pad) * MM)

    def xy(p):
        return pymupdf.Point((p[0] - x0 + pad) * MM, (y1 - p[1] + pad) * MM)
    sh = pg.new_shape()
    for g, col in geoms:
        for s in pieces(g):
            # one finish per polygon, after all of its rings: even-odd applies
            # to the path built since the last finish, so finishing ring by
            # ring fills every hole in as solid
            for ring in [s.exterior] + list(s.interiors):
                sh.draw_polyline([xy(p) for p in ring.coords])
            sh.finish(color=None, fill=col, even_odd=True, closePath=True, width=0)
    sh.commit()
    doc.save(path, deflate=True)
    return (x1 - x0 + 2 * pad), (y1 - y0 + 2 * pad)


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', default=SRC)
    a.add_argument('--width', type=float, default=50.0)
    a.add_argument('--cutter', type=float, default=0.70,
                   help='narrowest recess the die tooling can hold, mm')
    a.add_argument('--fill', type=float, default=0.50,
                   help='narrowest ridge of relief that will fill, mm')
    a.add_argument('--pdf')
    o = a.parse_args()

    blank, rel, rep = prepare(o.src, o.width, o.cutter, o.fill)
    ink, air = measure(rel)
    print(f'crest {o.width:.1f} mm across')
    print(f'  blank {blank.area:.1f} mm2   relief {rel.area:.1f} mm2 '
          f'({100 * rel.area / blank.area:.0f}% of the face), '
          f'{len(pieces(rel))} island(s), {rep["recesses"]} recess(es)')
    print(f'  tooling moved {rep["moved"]:.2f} mm2, '
          f'{100 * rep["moved"] / rep["drawn"]:.2f}% of the drawn relief')
    ok = 'OK  ' if min(ink, air) >= min(o.cutter, o.fill) - 0.05 else 'note'
    print(f'  {ok} relief: thinnest ridge {ink:.2f} mm, '
          f'narrowest recess {air:.2f} mm')
    if o.pdf:
        w, h = write_pdf([(blank, (0.82, 0.82, 0.84)), (rel, (0, 0, 0))], o.pdf)
        print(f'  {o.pdf}: {w:.2f} x {h:.2f} mm')
