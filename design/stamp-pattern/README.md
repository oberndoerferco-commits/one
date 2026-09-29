# Stamp-ready monogram patterns

Three repeat patterns built for stamping into leather (heat or roller
embossing). No star frame behind the logo, no fine swirls: just the star-cross
and one or two simple companions, spaced out in the sparse, tonal
"quiet luxury" style.

Regenerate with `node design/stamp-pattern/generate.js`.

| Pattern | Look | Stamping |
| --- | --- | --- |
| **Signature** | Logo + small spark on a diagonal grid | Easiest. Solid shapes only |
| **Tonal** | Solid and outlined logos alternate | 1 mm outline, needs a sharp plate |
| **Trellis** | 1 mm diamond trellis, logo in every cell, stud at crossings | Classic canvas look. Longest press time |

## Files

- `<pattern>-tile.svg`: one 36 × 36 mm repeat, black artwork at true size (mm). Give this to the plate / roller maker.
- `<pattern>-sheet-216x144mm.svg`: 6 × 4 repeats as one seamless vector, for proofs and larger plates.
- `logo.svg`: the logo on its own at 14 mm.
- `preview.html` / `preview.png`: simulated stamping on cognac, black and taupe leather. For review only; not artwork.

## Specs

- Repeat 36 × 36 mm. Logo 14 mm tip to tip; spark 5.2 mm (4.4 mm in Tonal); stud 3 mm.
- Lines 1 mm; gaps between separate shapes ≥ 5 mm.
- Artwork is solid black, no gradients or hairlines.
- The logo's four diagonal notches narrow to a point. At 14 mm the last ~1 mm
  of each notch will fill in on most leathers, and the logo still reads. Don't
  go below about 12 mm.
- To scale, change `T` (repeat) and `LOGO_R` (half the logo width) together.
