# Current direction — the live state

Single source of truth. When this disagrees with anything earlier in
any chat, THIS WINS. Update it the moment a decision changes.

Last changed: 2026-11-16

## The five decisions

| | current answer | changed |
|---|---|---|
| **Structure** | TWO TIERS: name on a bent ribbon, MADE IN ITALY on its own panel below, the two OVERLAPPING so they read as one object | 11-15 |
| **Letterform** | one of the four below — not yet chosen | |
| **Treatment** | engraved/inline detail for print; a solid cut for the die | 11-13 |
| **Where it goes** | leather hot stamp + print | 11-12 |
| **Bend** | bent, and the bend comes FROM the ribbon, not chosen | 11-15 |

## The assets that matter

In `canva-fit/`, from the user's own Canva ("tshirt design", pages 110-113):

- `wm-1-outlined.png`, `wm-2-engraved.png`, `wm-3-gold.png` — three
  FINISHED wordmarks, already rendered. No font needed.
- `wm-4-script.png` — assembled letter by letter from the user's
  ornamental-script alphabet sheet.
- `r01..r08.png` — ribbons cut from Canva page 112.
- `all.png` — 4 faces x 4 ribbons, fitted.

User's own read: the ENGRAVED and GOLD faces are the strongest.
Best pairings so far: r04_2-engraved, r08_2-engraved, r04_3-gold.

## Known facts, do not re-derive

- The ornamental serif and outline serif alphabets are MISSING N.
  Re-cut carefully, both are 26 glyphs running ...L M Ö O... The name
  cannot be built from them until the user adds an N.
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
- Generating fifty variants of anything

## Protocol

- The user may contradict earlier instructions. The latest wins;
  record it here and strike the old one into Superseded.
- ONE change per note, shown. Never a sheet of fifty.
- LOOK at every image before sending it.
- Measure to CHECK a design at the end. Never to choose it.
- The user's own references and assets beat anything drawn from
  scratch. Use them first.

## Next step

Pick one ribbon + one face, then put MADE IN ITALY on its panel
beneath it and clean the whole thing up. The ribbons are stock
mock-ups; the chosen shape gets redrawn as vector.
