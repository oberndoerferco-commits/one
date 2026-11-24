"""Split the ornamental logo into letter and decoration by stroke thickness.

The PDF's text is live in an embedded font, so each glyph's outline holds the
letter AND its vine as one shape. They are told apart by how thick the stroke
is: measured on this artwork at 600 dpi the vines run 10-22 px and the letter
strokes 50-130, so a morphological opening with an 18 px disk keeps the letters
and drops the vines. Two corrections follow:

  - a piece of "vine" whose skeleton is shorter than `min_vine_len` is a
    letter's own tip that the opening rounded off, not a trailing vine, so it
    goes back to the letter;
  - a surviving piece is kept only if it also survives a much coarser opening
    (`support_r`). The fat leaves and buds clear the 18 px disk but not the
    30 px one, while every real letter part -- down to the umlaut dots and the
    smaller MILANO line -- clears both. Measured on this artwork the supported
    parts run 74-133 px at their widest and the unsupported leaves 36-58.

`thicken_stems` then handles the hairlines the opening is right to drop: the
thin vertical inner stem of O, B, E, R, N, D, F keeps the letter readable, and
the reference cleaning thickens it from 17 px to 45 (27 on the MILANO line).
They are found as the only long dead-vertical runs outside the letter mask, and
redrawn as a bar of that width with a round foot.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

def disk(r):
    y,x=np.mgrid[-r:r+1,-r:r+1]; return (x*x+y*y)<=r*r+0.5

def split(ink, open_r=18, min_vine_len=110, support_r=30):
    letter=ndi.binary_opening(ink, structure=disk(open_r))
    # drop whole pieces that clear the fine disk but not the coarse one: the
    # fat leaves and buds.  Done BEFORE the tips are put back, or a leaf that
    # hangs off a stem by a short neck rides back in with the neck.
    support=ndi.binary_opening(ink, structure=disk(support_r))
    lab,n=ndi.label(letter, structure=np.ones((3,3)))
    keep=[i for i in range(1,n+1) if (support & (lab==i)).any()]
    dropped=letter & ~np.isin(lab,keep)
    letter=np.isin(lab,keep)
    # put back the letters' own tips, which the opening rounds off
    gone=ink & ~(letter | dropped)
    lab,n=ndi.label(gone, structure=np.ones((3,3)))
    lens=np.bincount((lab*skeletonize(gone)).ravel(), minlength=n+1)
    nb=np.ones((3,3))
    touch=set(np.unique(lab[ndi.binary_dilation(letter, structure=nb) & gone]))
    bad=set(np.unique(lab[ndi.binary_dilation(dropped, structure=nb) & gone]))
    short=[i for i in range(1,n+1)
           if lens[i]<min_vine_len and i in touch and i not in bad]
    letter=letter | (np.isin(lab,short) & gone)
    return letter, (ink & ~letter)

def thicken_stems(ink, letter, run=260, min_h=250, max_w=25, big_h=400,
                  width_big=45.0, width_small=27.0, trim=45, up=30):
    """Redraw the thin vertical inner stems as solid bars, as the reference
    cleaning does: same left edge, widened to the right, square at the top
    where it meets the letter and a semicircular foot `trim` px above where the
    hairline's own tail ended.  Returns the bar mask and what it found."""
    seed=ndi.binary_opening(ink, np.ones((run,1),bool)) & ~letter
    lab,n=ndi.label(seed, structure=np.ones((3,3)))
    bars=np.zeros_like(ink); found=[]
    for i,sl in enumerate(ndi.find_objects(lab), 1):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        if h<min_h or w>max_w: continue
        big=h>big_h
        tw=int(width_big if big else width_small)
        tr=int(trim if big else round(trim*width_small/width_big))
        xa=sl[1].start; xb=min(ink.shape[1], xa+tw)
        ya=max(0, sl[0].start-up); yb=max(ya+1, sl[0].stop-tr)
        bars[ya:yb, xa:xb]=True
        r=tw/2.0; R=int(np.ceil(r))
        y0=max(0,yb-R); y1=min(ink.shape[0], yb+R+1)
        gy,gx=np.mgrid[y0:y1, xa:xb]
        bars[y0:y1, xa:xb] |= ((gy-yb)**2+(gx-(xa+r-0.5))**2) <= r*r
        found.append((xa, sl[0].start, h, w, tw))
    return bars, found

def bands(ink, gap=120):
    """Horizontal bands of ink, one per line of type."""
    rows=np.where(ink.any(axis=1))[0]
    if not len(rows): return []
    out=[]; s=rows[0]; p=rows[0]
    for y in rows[1:]:
        if y-p>gap: out.append((s,p+1)); s=y
        p=y
    out.append((s,p+1)); return out

def clean(ink, base_open=18, base_support=30, base_vine=110, base_run=260,
          base_width=45.0, base_trim=45, verbose=False):
    """Split and rebuild every line of type, each at its own scale.

    A smaller line has proportionally thinner strokes, so every threshold is
    scaled by that line's stroke weight relative to the heaviest line.  Without
    that, a short vine on the small line reads as a letter's own tip and stays.
    """
    out=np.zeros_like(ink); found=[]
    bs=bands(ink)
    wt=[np.percentile(2*ndi.distance_transform_edt(ink[a:b]), 99.9) for a,b in bs]
    ref=max(wt) if wt else 1.0
    for (a,b),w in zip(bs,wt):
        k=w/ref
        sub=ink[a:b]
        letter,_=split(sub, open_r=max(3,int(round(base_open*k))),
                       min_vine_len=base_vine*k,
                       support_r=max(4,int(round(base_support*k))))
        bars,f=thicken_stems(sub, letter, run=int(round(base_run*k)),
                             min_h=int(round(250*k)), max_w=int(round(25*k)),
                             big_h=0, width_big=base_width*k,
                             trim=int(round(base_trim*k)), up=int(round(30*k)))
        out[a:b]=letter|bars
        found += [(x,y+a,h,ww,tw) for x,y,h,ww,tw in f]
        if verbose: print('  line y%d-%d  weight %.0f px (x%.2f)  %d stems' % (a,b,w,k,len(f)))
    return out, found
