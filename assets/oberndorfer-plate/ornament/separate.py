"""Split the ornamental logo into letter and decoration by stroke thickness.

The PDF's text is live in an embedded font, so each glyph's outline holds the
letter AND its vine as one shape. They are told apart by how thick the stroke
is: measured on this artwork the vines run 10-22 px at 600 dpi and the letter
strokes 50-130, so a morphological opening with an 18 px disk keeps the letters
and drops the vines. Two corrections follow:
  - a piece of "vine" whose skeleton is shorter than 110 px is a letter's own
    tip, not a trailing vine, so it goes back to the letter;
  - a surviving piece whose widest point is under 60 px is an ornament bud that
    happened to be fat enough to survive, so it goes to the decoration. The gap
    is clean: letter components measure 122-133 px at their widest, buds 13-40.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

def disk(r):
    y,x=np.mgrid[-r:r+1,-r:r+1]; return (x*x+y*y)<=r*r+0.5

def split(ink, open_r=18, min_vine_len=110, min_letter_width=60):
    letter=ndi.binary_opening(ink, structure=disk(open_r))
    vine=ink & ~letter
    lab,n=ndi.label(vine, structure=np.ones((3,3)))
    lens=np.bincount((lab*skeletonize(vine)).ravel(), minlength=n+1)
    short=[i for i in range(1,n+1) if lens[i]<min_vine_len]
    letter=letter | (np.isin(lab,short) & vine)
    edt=ndi.distance_transform_edt(ink)
    lab,n=ndi.label(letter, structure=np.ones((3,3)))
    keep=[i+1 for i in range(n) if 2*edt[lab==i+1].max() >= min_letter_width]
    letter=np.isin(lab,keep) & letter
    return letter, (ink & ~letter)
