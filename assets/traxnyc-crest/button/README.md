# TraxNYC crest — domed button, riveted

The crest as a metal part: a quatrefoil blank with a shallow domed face,
the band and the eagle head struck proud of it, and two rivet posts on the
flat back.

![face](preview-face.png)

| File | What it is |
| --- | --- |
| `trax-crest-button.stl` | The part, in millimetres. One closed body |
| `trax-crest-button.pdf` | A3 production sheet: face, back, section A-A |
| `trax-crest-face.pdf` | The face artwork at 1:1, relief solid, blank grey |

Rebuild with:

```sh
python3 scripts/trax_button.py  --stl assets/traxnyc-crest/button/trax-crest-button.stl
python3 scripts/trax_drawing.py --out assets/traxnyc-crest/button/trax-crest-button.pdf
python3 scripts/trax_crest.py   --pdf assets/traxnyc-crest/button/trax-crest-face.pdf
```

## The part

| | |
| --- | --- |
| Across | **50.00 mm**, 7.75 overall with the posts |
| Face | spherical cap, R 214.2, rising **2.00** at the centre |
| Edge | **0.90** at the star tips, 1.44 at the cardinals |
| Relief | **0.85** above the face, top edge rolled R 0.25 |
| Posts | **2 × ⌀2.5 × 4.0**, 0.4 break, on the diagonal at r 14 |
| Volume | 5107 mm³ — 43 g in brass, 34 g in zinc alloy |

The blank is not round, so the edge is not one thickness: the star points
are the furthest from the centre and therefore the thinnest. The relief
follows the cap rather than a plane through it, so the band stands the
same 0.85 above the face at the rim as at the middle.

## Why it is a button and not six pieces

The PA & CO lockup was six separate pieces, each domed into a rounded rib
and each fixed on its own. The crest cannot be built that way. The eagle
head is an island floating inside the band — 1.01 mm clear of it on the
138.6 mm master, 0.37 mm at 50 — and holding two separately riveted parts
to a third of a millimetre by hand is not a thing to ask of anyone.

On a button it does not arise. The blank carries the head, and the
clearance is a groove in a face instead of a gap between two parts.

## What the tooling changed, and why

The relief is not the drawing. It is the drawing passed through what a
round-nosed cutter can leave behind: the air is opened with a disc of the
cutter radius, then the metal with a smaller one. That is not an
approximation of the tooling — a die pocket *is* swept by a round cutter,
so it can only hold a recess where that disc fits.

It costs **2.75 mm², 0.24%** of the drawn relief. What it does visibly:

- The three places the head comes within a millimetre of the band close
  up. They were 0.37, 0.65 and 0.70 mm at 50 and would have shut anyway
  the moment both sides carried a rolled edge.
- The star points take a small fillet. A tool cannot cut a corner sharper
  than itself, so a drawing that shows one is describing something that
  will not be made.
- **The eye changes.** Below about 57 mm the white above and below the
  iris is a tenth of a millimetre, so the iris merges into the lids and
  what is left is the two corners of the almond and the pupil. It still
  reads as an eye; it is no longer an iris in a ring of white.

The eye also carried a defect that no size would fix: the iris met the
upper lid at a tangent, which leaves 0.154 mm of metal on the master and
0.06 mm at 50. A tangency is a knife edge whatever it is scaled to, and
the same cutter pass resolves it.

Measured on the result: no ridge thinner than 1.15 mm, and the smallest
recess is the pupil at 0.87.

## Open

- **Size.** 50 mm matches the PA & CO piece and is the smallest that
  keeps every stroke over a millimetre. The lid's reserved square is
  currently 46 — it would have to go to about 52 for this to sit on the
  box with clearance, and the clear field inside the debossed frame is
  56.8, so it fits.
- **Fixing.** Posts are drawn plain for riveting over: drill ⌀2.7 and
  peen, or spin. Say if they should instead be threaded, knurled for a
  press fit, or dropped for adhesive.
- **Material and finish** are not specified here. Brass struck and
  polished, or zinc alloy cast and plated, both suit the geometry.
