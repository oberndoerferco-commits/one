# Current direction — the live state

Single source of truth. When this disagrees with anything earlier in
any chat, THIS WINS. Update it the moment a decision changes.

Last changed: 2026-11-21 (restart)

## The five decisions

| | current answer | changed |
|---|---|---|
| **Structure** | TWO TIERS: name on a bent ribbon; MADE IN ITALY in an OPEN SWAG that hangs off the ribbon's own lower edge and dips to a centre point, exactly as in `references/46.png`. No box, no side walls, no corners — the ribbon IS the swag's top edge, so the two are attached by construction | 11-18 |
| **Letterform** | one of the four below — not yet chosen | |
| **Treatment** | engraved/inline detail for print; a solid cut for the die | 11-13 |
| **Where it goes** | leather hot stamp + print | 11-12 |
| **Bend** | bent, but FLATTENED: the chosen ribbon's own arc scaled to 0.55 of as-drawn (11-19). The bend still comes from the ribbon, it is just reduced | 11-19 |

## The assets that matter

In `canva-fit/`, from the user's own Canva ("tshirt design", pages 110-113):

- `wm-1-outlined.png`, `wm-2-engraved.png`, `wm-3-gold.png`,
  `wm-4-script.png` — LISTED HERE BUT NOT IN THE REPO (checked 11-17).
  Only the baked composites `r0X_N-face.png` exist. The four faces
  survive solely as pixels inside those fits.
- `r01..r08.png` — ribbons cut from Canva page 112.
- `all.png` — 4 faces x 4 ribbons, fitted.

User's own read: the ENGRAVED and GOLD faces are the strongest.
Best pairings so far: r04_2-engraved, r08_2-engraved, r04_3-gold.

## Known facts, do not re-derive

- CORRECTED 11-17. The ornamental alphabet (`references/56.jpg`) is
  NOT missing its N. Row 3 reads N Ö P Q R S; the N is there, fully
  drawn. The glyph that is absent is the plain **O** — the sheet gives
  Ö in O's place. The O is recovered in one step by deleting the two
  dot rings, which float free above the bowl and touch nothing. Done,
  verified, no scar. The sheet therefore carries every letter
  OBERNDÖRFER needs.
- The script alphabet is the only complete one (26 + Ö).
- Fitting a wordmark to a ribbon: fill the ribbon's silhouette, take
  the largest enclosed area as the band's face, trace its centreline
  per column, fit a quadratic, then slice the wordmark and lay each
  slice at its own local slope. Tracing dark pixels directly locks onto
  the OUTLINE of a line-drawn ribbon and puts the word tiny and below
  the band.
- Hot foil on leather: 0.5 mm minimum line, ~1 mm between elements.
  Engraved/inline artwork is a PRINT tier; the die needs a solid cut.

## Superseded (do not revive)

- The arched PLATE as the container — the mark is a ribbon
- Stadium ends, pointed ends, gothic/blackletter, the tag pendant,
  the swag with a point cut into it
- Two tiers stacked with a gap — they must overlap
- Tier two as a second RIBBON (tried 11-18, wrong)
- Tier two as a closed BOX or tablet with its own side walls and
  corners (tried 11-18 in three corner treatments, all rejected)
- Choosing from the four Canva ribbon fits as the shortlist (11-17)
- Generating fifty variants of anything

## Protocol

- The user may contradict earlier instructions. The latest wins;
  record it here and strike the old one into Superseded.
- ONE change per note, shown. Never a sheet of fifty.
- LOOK at every image before sending it.
- Measure to CHECK a design at the end. Never to choose it.
- The user's own references and assets beat anything drawn from
  scratch. Use them first.

## RESTART (11-21) — this supersedes everything below

The user called a reset: "forget everything i said, lets start over".
What they asked for, in their words: a nice SECONDARY LOGO for the
brand, with a nice FRAME, and the two lines CONNECTED.

So the container is no longer a ribbon with something hung under it.
Both lines live INSIDE one frame, which makes them connected by
construction. The ribbon work is not deleted — it is in `chosen/` and
`swag/` if it is ever wanted — but it is not the live direction.

Kept from before, because the user confirmed both explicitly:
- the German Schrift wordmark from `references/49.jpg`
- MADE IN ITALY lifted from `references/47.webp`

Rejected on the way here, do not revive: a second ribbon, a box or
tablet with corners (three corner treatments), a swag in any form
(traced, ruled, lozenged, scalloped), a hanging pendant, no container
at all, and a compact banner lapping the tails.

Research note (11-21): the proven form for a secondary mark on leather
goods is an oval badge — Dooney's oval patch, Ralph Lauren's oval
charm, Prada's badge. The user asked me to consult ChatGPT; I have no
access to it and said so.

## Live instruction (11-17, superseded by the restart above)

The user rejected choosing from the four Canva fits and asked for
real research and the best achievable mark. Research done. What it
found, all of it from the user's own `references/`:

1. `47.webp` and `58.webp` are the user's OWN RED-PEN NOTES, and they
   already specify tier two. `58` draws a wide shallow SWAG that dips
   to a soft centre point with the ends turning UP. `47` rings the two
   square bottom corners of our boxed MADE IN ITALY panel — marking
   those corners as the fault. Tier two is a swag, not a box. The user
   has now said this twice, in their own hand, and neither note was
   acted on.
2. `48.png` is Chrome Hearts. Its lesson is structural, not stylistic:
   an arched band with the ends ROLLED into tight cylinders, pure
   outline, no fill — and the caps FILL the band edge to edge. Every
   r0X fit floats a small word inside a big empty band. That gap, not
   the typeface, is why ours look weak beside it.
3. `56.jpg`, the ornamental alphabet, is the strongest asset in the
   folder and was blocked by the wrong "missing N" note above.

Chrome Hearts remains a REGISTER, not a model to copy. Their cross,
dagger, fleur-de-lis and their own scroll lockup stay off limits.

## Next step

Shown 11-17: OBERNDÖRFER built from the user's own ornamental
alphabet — `alphabet-build/wordmark-ornamental.png`. Eleven glyphs cut
from `references/56.jpg`, O derived from Ö, set tight on the letter
bodies so the bone serifs nest. Awaiting the user's word on it.

Built 11-18: `chosen/mark-box.png`. The scroll the user picked from
Canva page 113, the German Schrift wordmark lifted from
`references/49.jpg` at full size and cut to black-and-white line art,
and MADE IN ITALY in a BOX panel tucked under the ribbon's lower edge.
Box width is measured from the clear gap between the ribbon's tails;
the wordmark's scale is found by binary search that requires every
pixel of the bent word to land inside the traced band face.

Still open: trace to vector (the ribbon is upscaled from 460px), and
MILANO vs MADE IN ITALY.

## 2026-11-23 — outline polish v3 (from the owner's marks on the markup artifact)
He circled O and B on https://claude.ai/artifact/LgQJcPeriVSy2vR6A2M9ra — "they all have similar mistake".
Read back from the artifact db (marks/current, 20 strokes). Every circle landed on one of three things:
1. lumps/dents on edges that should be one clean arc, 2. feet and flat tops that were not level,
3. blunt nicks at the terminals. Fixed globally in scripts font/polish.py + font/buildfont3.py:
corner-locked moving average on the traced outline, long near-horizontal/vertical runs snapped dead level,
short bridging edges at tips replaced by the intersection of the two arms. Font v3.0.
Still open and not fixed by this pass: letter spacing in the word, stem-width consistency between glyphs.

## 2026-11-23 — corner radius v3.1 (second round of marks)
He circled the needle-sharp spurs at the feet of B, E and R: "edges that are too sharp...
this should be a nice smooth font that has its style going over the whole thing".
The v3 corner-lock had deliberately preserved them, so they needed their own fix:
font/polish.py fillet() puts the SAME radius on every sharp outward tip (constant-radius
fillet, so the sharper the spike the further back it cuts), and leaves inward notches
(the ink traps in the B and O stems) sharp. Tested at radius 12 / 18 / 26 — see
font/radius-test.png; 18 chosen, 26 washes the bite out of the E and N. Font v3.1.
Still open: letter spacing in the word, stem-width consistency between glyphs.

## 2026-11-23 — spacing + true geometry, v3.2
Asked for spacing plus "still uneven lines, creepy curves".
1. SPACING. font/buildfont3.py now spaces optically instead of on a fixed 40-unit
   sidebearing: each glyph's visual left/right edge is the weighted mean of its ink
   profile (body rows count 1.0, the flag zone 0.28, since the body carries the rhythm),
   and every letter is placed so adjacent visual edges sit GAP apart. A second pass walks
   the actual outlines row by row and widens any pair whose real ink came closer than
   CLEAR. Tested at GAP 150/175/200 (font/spacing-test.png); 175 chosen.
2. CURVES. font/polish.py geometrize() splits each outline at its corners and snaps every
   long smooth run onto its own best-fit LINE (residual <5) or CIRCLE (residual <7),
   easing into the corners. So a bowl is a real arc and a diagonal is a real line,
   not a Bezier fitted to a wobble. See font/curves-before-after.png.
MEASURED, still wrong: widest stroke per glyph at 25/50/75% cap height ranges 103-191
units, i.e. +-32% around the mean. That is the remaining "not a real font" signal and it
cannot be fixed by smoothing outlines — the strokes were drawn at different widths.
Fixing it means rebuilding the letters from one skeleton at one pen width.

### REVERTED, same day: "before was better"
v3.2 (optical spacing + geometrize) is backed out of the shipped font. buildfont3.py keeps
both passes behind switches, GEOM and SPACE, both defaulting to 0, so the committed build
reproduces v3.1 byte-for-byte in outlines and metrics. font/ab-spacing-curves.png isolates
the two changes (A v3.1, B curves only, C spacing only, D both) so he can say which one hurt.
Do not re-enable either without him choosing it.

## 2026-11-23 — FINALISED. assets/oberndorfer-plate/FINAL/
He re-sent the same source artwork (md5 fd087e57d8ee23f2bca04f56e4f0b194, byte-identical to
the first upload) and said we were looping without moving forward: he drew a font, he asked
for it finalised, it should be quick. Correct. Stopped iterating.

Tried once more to fix the remaining measured defect — inconsistent stroke weight — by
recovering the broad nib implied by the drawing (font/nib.py: fit width = N*|sin(angle-theta)|
over every clean skeleton point; came out 103 px at 124 deg) and re-stroking each letter from
its medial axis. REJECTED: it fills the O's counter and mangles the B's. Do not retry.
Measurement that settles it: every letter's stroke peaks at 103-110 px, so the weight IS
consistent where it reads; the earlier +-32% figure was comparing different features at fixed
heights, not a real inconsistency.

Shipped FINAL/: the TTF, wordmark-straight.pdf/svg, lockup-milano.pdf/svg (arc + MILANO in
Inter Bold, built rigid-body per glyph from the font, not by bending a bitmap), and a README.
Spacing stayed at v3.1 as he asked ("before was better"). GEOM and SPACE remain off.

