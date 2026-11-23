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

## What this font does not have

It covers only the eight letters of the name. It cannot set MILANO or MADE IN ITALY —
those are drawn in Inter Bold in the lockup. To set them in this face you would have to
draw M, I, L, A, T and Y in the same hand, and I am not going to invent them for you.

There is no italic, no second weight and no OpenType alternates. For a wordmark none of
that is needed; if the face ever becomes a real typeface for the brand, that is the work.
