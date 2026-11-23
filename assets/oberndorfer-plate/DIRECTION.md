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

## 2026-11-23 — v4.0. Audited as a FONT, not as artwork. font/finalise.py
"are you even checking what you are doing? study what makes a font, whats important".
Fair. I had been polishing curves and never audited the font's own machinery. The audit
found real defects, all now fixed in font/finalise.py (runs on the build output):
 - baselines ranged -1..+4 and caps 699..701: now exactly 0 and 700 for flat-footed
   letters, with 8 units of overshoot top and bottom on the round O and Ö.
 - NO KERNING AT ALL. This, not the sidebearings, was the spacing problem — it is
   pair-specific. Measured the real white area between outlines row by row for all 64
   pairs and solved each kern to a constant 266 units of visual white, floored at 112
   units of ink clearance. 57 pairs carry a value, FF -128 to DÖ +39. Written as both a
   GPOS kern feature and a legacy kern table.
 - no space glyph at all: added at 280 units, U+00A0 mapped.
 - .notdef was empty: now a visible box.
 - hhea ascender 820 clipped the Ö at 886: now 900, typo metrics set, USE_TYPO_METRICS on.
 - OS/2 was v3 with weight class 400 on a heavy face, no style bit, fsType 4, empty
   PANOSE, no vendor ID: all corrected, OS/2 v4.
 - name table had 4 records: now copyright, unique ID, full name, trademark, designer,
   licence, typographic family.
 - glyph was literally named "Ö", illegal as a PostScript name: now Odieresis.
Verified: 0 missing extrema across all 8 glyphs, winding correct, clean save/load
round-trip. Proof sheet at font/kerning-proof.png. FINAL/ regenerated, and final.py now
applies the font's own kerning so the PDF and the installed font set the word identically.

## 2026-11-23 — v5.0 PARTS KIT. font/harmonise.py
"a font has to be symmetrical, have a style that reflects in all of the letters, be
precise". He is right and this was the real defect. Measured it: the top-left flag was
EIGHT DIFFERENT SHAPES — worst pair disagreed on 42.5% of its area, all eight agreed on
only 20.8% (font/flags-before.png shows them side by side and overlaid).
harmonise.py now builds the letters from shared parts: it rasterises each glyph at 2 px
per unit, finds each letter's own attachment point (left edge of the first stem at the
neck row, CAP-230), lifts the canonical flag from R (the medoid of the disagreement
matrix) and the canonical foot spur from E, and grafts them into every letter. The bottom
of the graft box is UNIONED not replaced (45 units on stems, 95 on the round O and Ö whose
flag springs off a curve) so the part welds on instead of notching the bowl — that weld
is what fixed the floating contours in the first attempt. Everything re-traced through the
full pipeline afterwards so no seam survives. Then finalise.py as usual.
Result: all eight share one flag outline; kern range collapsed from -128..+39 to -41..+43,
which is the proof that consistent parts space themselves.
DO NOT go back to treating the glyphs as eight independent outlines.

## 2026-11-23 — v5 HARMONISATION REVERTED. Spacing now read off the artwork.
He showed the original PDF open in Preview: "before This, and it got even worse. Look at my
drawing. From far, it looks perfect. Just do it like that." Rendered his PDF and put it
next to my v5 at the same cap height (font/harmonised-was-worse.png). He is right and the
cause is plain: HIS FLAGS ARE SHORT AND TUCKED, the R's flag I grafted into all eight is
LONG, so every letter swept into the one before it and the word smeared. My v5 was also 11%
narrower than his drawing — crowded where his breathes. Harmonisation reverted; glyph
shapes are the faithful v3.1 trace again.
Then the thing I should have done first: font/spacing_from_drawing.py reads his PDF at
200 dpi, finds cap height 303 px, splits the word into its 11 non-touching letter blocks
and converts his letter positions to font units. THOSE are the metrics now.
It also settles the shape question: my traced widths match his to within 2% (O +0.5, E 0.0,
R +0.6, N -0.2, F +0.4, B -1.1, D -1.3, Ö -2.1). The trace was always faithful. The spacing
was the defect, and I had been computing it instead of reading it off his page.
His mean gap is 151 units -> advance = ink width + 151; his deviations from his own average
become the kerns (RN +44, RF -60, BE/ER/ÖR +12, OB +5, FE -5, DÖ -10). finalise.py now
prefers drawing_spacing.json over its own optical solve.
Result: the font sets the word 1.1% wider than his drawing with every letter in the same
place (font/matches-your-drawing.png).
RULE LEARNED: measure his artwork before inventing anything. Restyling his letterforms has
failed every single time; reproducing them has worked every time.

## 2026-11-23 — the E. "just the E needs fixing"
Cropped both of his drawn E's from the artwork, rendered the font's E, scaled both to the
same cap height and overlaid them: 3.28% disagreement, the worst of the eight letters.
Two causes, both mine: flatten() was snapping a level line across the junction where the
top arm meets the body and taking a notch out of it, and 5 smoothing passes over an 11-wide
window were pushing the bottom-left corner out into a bulge.
Fix in font/buildfont3.py: GENTLE={'E'} — that glyph skips flatten entirely, smooths with
3 passes over a 9-wide window, and takes a 7-unit corner radius instead of 18.
Swept six settings and measured each against his artwork before choosing
(rad/pass/win: 7/5/11 2.45%, 0/5/11 2.47%, 7/3/9 1.65%, 0/3/9 1.66%, 0/2/7 2.24%,
4/4/9 1.83%). Chose 7/3/9. Deviation 3.28% -> 1.65%. Proof at font/e-fix.png.
Verified the built glyphs are byte-identical to the tested build, and the word still sets
1.1% wider than his drawing. No other glyph changed.

