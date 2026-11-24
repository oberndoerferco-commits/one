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

## Built from true lines and true arcs

You asked for straight lines where there are straight lines, curves where there are
curves, corners where there are corners, and nothing wobbling in between. That is a
different job from smoothing, and `reconstruct.py` does it:

1. Every outline is **decomposed** into pieces, splitting recursively at the worst-fitting
   point until each piece is either a straight line or a circular arc to within 0.8 px.
2. Neighbouring pieces that are really one primitive are **merged** back together, so a
   long stem is one line and a bowl is one arc rather than a chain of fragments.
3. Each piece is replaced by its **exact** primitive, and neighbours are **re-intersected**
   — line against line, line against circle, circle against circle — so every corner is a
   mathematical point rather than a blend.

Nothing is averaged or eased. A stem is straight to the last decimal because it *is* a
straight segment; a bowl is a real circle. There is no longer anything between the
primitives for wobble to live in.

**It is also closer to your drawing than the traced version was: 2.59% against 2.67%**,
and it does it with **947 points instead of 6,706**. The sharpest corner in the font went
from 14.9 degrees to 52.2, and there is now exactly one corner under 60 degrees in the
whole font.

`true-lines-and-arcs.png` is the proof at high zoom — the N stem, the B stem, the E stem
and arms, the O and D bowls, before and after. `letters-reconstructed.png` is all eight.

The method was verified on shapes with a known answer before it went near your letters: a
noisy circle comes back as one exact circle, a noisy square as exactly four lines with
corners landing within 0.2 px of the true corners, and a rounded rectangle as four lines
plus four arcs.

## What this font does not have

It covers only the eight letters of the name. It cannot set MILANO or MADE IN ITALY —
those are drawn in Inter Bold in the lockup. To set them in this face you would have to
draw M, I, L, A, T and Y in the same hand, and I am not going to invent them for you.

There is no italic, no second weight and no OpenType alternates. For a wordmark none of
that is needed; if the face ever becomes a real typeface for the brand, that is the work.
