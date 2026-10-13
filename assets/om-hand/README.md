# OM — the hand-drawn mark, vectorised

Your iPad drawing, traced and tidied. The letterforms are yours; what changed is
that everything is now regular.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `om-colour.pdf` / `.svg` | Full artwork — cyan hatch, cream keyline, black letters |
| `om-black.pdf` / `.svg` | One-colour: the letterforms, solid black |
| `om-black-shadow.pdf` / `.svg` | One-colour with the hatch shadow, also black |
| `source-drawing.jpg` | The drawing as supplied |

```sh
python3 scripts/om_hand.py assets/om-hand/source-drawing.jpg assets/om-hand --size 480
```

## What was done

**The letterforms are traced from your drawing** and rebuilt on structural nodes
— one curve per span between corners and extremes — so the finger-wobble comes
out while the shapes stay yours. O is 17 straight segments and 22 curves; M is
29 and 44.

**The M is symmetrical.** It is mirrored about its own axis, and the axis is
solved for rather than assumed: the centroid was 0.2 px off, which is enough to
ghost every edge if you average without checking. Residual between the halves
after alignment is 0.003.

**The keyline and the hatch are rebuilt, not traced.** Both were measured off the
drawing and then regenerated geometrically, so they are even:

| | measured in the drawing | rebuilt as |
| --- | --- | --- |
| Keyline | 1–8 px outside the black, median 5 | a constant band, 0.0115 cap |
| Shadow offset | dx −80, dy +67 px (down-left) | −0.115, −0.096 cap |
| Hatch angle | 135° in image space | 45°, exactly |
| Hatch pitch | 21 px | 0.0301 cap, constant |
| Hatch stroke | 16 px, duty 0.79 | 0.0215 cap |

## One thing I changed on purpose

In the drawing the hatch is made of **short separate dashes**; here it is
**continuous strokes**, because that is what "make everything fit together"
asks for and it holds up when the mark is scaled down. If you want the dashed
texture kept, that is a change to `hatch()` and I can put it back.

## The O's open tail is deliberate

The O has no enclosed counter — the ring's upper right splits into a pointed
wedge and the counter escapes through the gap. The trace keeps it as the single
open contour it is, since the cream keyline in your drawing runs round both
prongs, which is how you can tell it was meant.
