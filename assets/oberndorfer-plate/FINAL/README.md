# OBERNDÖRFER — final files

Everything here comes from the letterforms you drew (Untitled_Artwork_4.pdf),
traced and finished. All vector, no raster.

| file | what it is |
|---|---|
| `OberndorferDrawn-Regular.ttf` | the installable font, version 4.0. Double-click to install, then type OBERNDÖRFER. Contains the 8 letters of the name (O B E R N D Ö F), a space, and a .notdef box. |
| `wordmark-straight.pdf` / `.svg` | the wordmark on a straight baseline, 1565 × 255 pt |
| `lockup-milano.pdf` / `.svg` | OBERNDÖRFER bent on an arch with MILANO under it in Inter Bold, 1518 × 431 pt |
| `kerning-proof.png` | the same word with kerning off and on, plus the baseline and space checks |

## What was done to the drawing

1. Traced at sub-pixel accuracy from the original artwork.
2. Outline smoothing with the real corners locked, so the pencil ripple
   came off the edges without rounding the corners you drew.
3. Feet and flat tops snapped dead level.
4. One corner radius (18/1000 em) on every sharp outward tip, so no needles;
   inward notches left sharp so the ink traps survive.
5. Built as a TrueType font, then finished as a font rather than as artwork:

   - **One baseline, one cap height.** Every flat-footed letter now sits at exactly 0
     and reaches exactly 700. Before this they ranged from −1 to +4 at the foot and
     699 to 701 at the cap, so the word sat on a slightly wavy line.
   - **Overshoot.** The O and Ö are round, so they are drawn 8 units below the baseline
     and 8 above the cap. A circle that stops exactly on the line looks short next to a
     flat foot; this is the correction every real typeface makes.
   - **Kerning, 57 pairs.** The spacing problem was never the sidebearings — it was
     pair-specific. For all 64 pairs of these letters I measured the real white area
     between the two outlines row by row, then solved each pair's kern so every pair
     carries the same visual white (266 units), with a hard floor of 112 units of ink
     clearance so the flags can never collide. FF needed −128, DÖ needed +39. Shipped
     as both a GPOS `kern` feature (modern apps, browsers, InDesign) and a legacy
     `kern` table (older desktop apps).
   - **A space glyph** at 280 units, and U+00A0 mapped to it. The font had no space at
     all before, so typing one produced nothing.
   - **A visible `.notdef`** box, so a missing character shows as a box instead of
     silently vanishing.
   - **Vertical metrics that clear the umlaut.** The Ö reaches 886 units; the ascender
     was 820, which clipped it in some renderers. Now 900, with typo metrics set and
     the USE_TYPO_METRICS flag on so line spacing is consistent across apps.
   - **Correct flags and identity.** OS/2 upgraded to version 4, weight class 700 (it is
     a heavy face, it was declaring 400), the REGULAR style bit set, embedding
     permission opened, PANOSE filled in as a decorative face, vendor ID, and a full
     name table: copyright, unique ID, full name, trademark, designer and licence.
   - **Legal glyph names.** `Ö` was literally named "Ö", which is not a valid
     PostScript glyph name; it is now `Odieresis`.
   - **Checked:** every curve has on-curve points at its extremes (0 missing across all
     8 glyphs), contour winding is correct by nesting depth, and the font round-trips
     through a save/load cycle with no warnings.

## Scaling

The font is scale-free. For manufacturing, the thinnest part of the
letterform is the hairline inside the O, B, R and D stems. At the floors in
BRIEF.md (hot foil 0.50 mm, laser 0.15 mm, casting 0.30 mm) check that
hairline before committing to a size.

## Spacing comes from your drawing, not from an algorithm

Your eleven letters do not touch, so your artwork records exactly where you put each one.
`spacing_from_drawing.py` reads the PDF at 200 dpi, measures the cap height (303 px),
splits the word into its eleven letter blocks and converts every letter position to font
units. Those positions are the font's metrics.

That measurement also settled an argument: **my traced letter widths match yours to within
2%** — O 0.5%, E 0.0%, R 0.6%, N −0.2%, F 0.4%, B −1.1%, D −1.3%, Ö −2.1%. The shapes were
faithful the whole time. What was wrong was the spacing, which I had been computing instead
of reading off your page.

Your average gap between letters is 151 units, so each letter's advance is its own ink
width plus 151. The places where you deviated from your own average become kerning:
RN +44, RF −60, BE/ER/ÖR +12, OB +5, FE −5, DÖ −10. Nothing invented.

Result: at the same cap height the font sets the word 1.1% wider than your drawing, with
every letter in the same place. `matches-your-drawing.png` is the two stacked.

## Corners

Rounded back to the level you approved: 38/22 over-softened it and lost the bite, so the
outward radius is 18 again and inward notches are left as drawn. Two things from that
round were kept, because they are corrections rather than restyling:

- **A bug fix.** The test that decides whether a corner is an outward tip or an inward
  notch probed a fixed 6 units along the bisector. On a needle that probe lands outside
  the ink, so the corner was classified wrongly and skipped. The probe now walks a
  quarter of the shorter arm.
- **Whisker removal.** A small opening on the mask before tracing deletes features two
  pixels wide. The D carried a 2.9 degree needle on its bowl that was a trace artefact,
  not something you drew, and it was shorter than any corner rounding could reach.

## Straightening and smoothing

`geometrize()` splits every outline at its corners, then takes each long run and asks
whether a straight line or a true circle already nearly fits it. If one does, the run is
projected onto that exact geometry, eased at both ends so the joins stay clean. A run that
fits neither is left alone, so nothing with real character gets flattened.

Tolerances were swept — 8/10, 12/14, 16/16, 20/18, 26/22 and 34/26 — and **12/14 measured
best**. Higher tolerances are worse, not better: they force gently curved runs onto
straight lines and the result bows somewhere else.

| | before | after |
|---|---|---|
| worst bow on a long straight edge | 15.6 units | **9.7** |
| ripple on runs that should be true arcs | 8.5 units mean | **6.4** |

`stems-before-after.png` shows the B stem, the N diagonal, the D hairline, the E stem and
the O and R bowls side by side.

## Repeated letters

Already identical, by construction. OBERNDÖRFER is eleven letters set from eight glyphs —
the three R and the two E are literally the same outline, so they cannot drift apart the
way they do in a drawing.

## The E

Measured against the artwork, the E was 3.28% off — the worst of the eight. Two causes,
both mine: the level-snapping pass was cutting across the junction where the top arm meets
the body, taking a notch out of it, and over-smoothing was pushing the bottom-left corner
outwards into a bulge. The E is now traced with that levelling pass off, three smoothing
passes instead of five over a narrower window, and a 7-unit corner radius instead of 18.
Deviation from your drawing: **3.28% to 1.65%**. `e-fix.png` is your E, the overlay before,
the overlay after, and the result.

## A thing I tried and reverted

I harmonised the letters by grafting one canonical flag into all eight, on the theory that
a typeface should share its parts. The flag I chose was the R's, which is long; yours are
short and tucked. The result swept into the letter before it and the whole word smeared
together — `harmonised-was-worse.png` in the font folder shows it against your drawing.
Reverted. Your flags vary, and at reading distance that variation is invisible while the
long grafted flag was not.

## What this font does not have

It covers only the eight letters of the name. It cannot set MILANO or MADE IN ITALY —
those are drawn in Inter Bold in the lockup. To set them in this face you would have to
draw M, I, L, A, T and Y in the same hand, and I am not going to invent them for you.

There is no italic, no second weight and no OpenType alternates. For a wordmark none of
that is needed; if the face ever becomes a real typeface for the brand, that is the work.
