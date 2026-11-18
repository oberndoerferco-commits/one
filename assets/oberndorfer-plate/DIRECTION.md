# Current direction — the live state

Single source of truth. When this disagrees with anything earlier in
any chat, THIS WINS. Update it the moment a decision changes.

Last changed: 2026-11-18 (swag)

## The five decisions

| | current answer | changed |
|---|---|---|
| **Structure** | TWO TIERS: name on a bent ribbon; MADE IN ITALY in an OPEN SWAG that hangs off the ribbon's own lower edge and dips to a centre point, exactly as in `references/46.png`. No box, no side walls, no corners — the ribbon IS the swag's top edge, so the two are attached by construction | 11-18 |
| **Letterform** | one of the four below — not yet chosen | |
| **Treatment** | engraved/inline detail for print; a solid cut for the die | 11-13 |
| **Where it goes** | leather hot stamp + print | 11-12 |
| **Bend** | bent, and the bend comes FROM the ribbon, not chosen | 11-15 |

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

## Live instruction (11-17, supersedes "pick one of the four")

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
