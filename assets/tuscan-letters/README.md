# Tuscan display capitals — O and M

Two capitals drawn to match the "PREMIUM" lettering on the 1936 label: a
French Clarendon / Tuscan circus wood type.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `tuscan-O.pdf`, `tuscan-M.pdf` | The letters, ink + inline |
| `tuscan-O-shadow.pdf`, `tuscan-M-shadow.pdf` | The same with the reference's drop shadow |
| `tuscan-OM.pdf`, `tuscan-OM-shadow.pdf` | Both letters on one sheet |
| `reference-premium.png` | The source lettering, enlarged |

Cap height is 480 pt; the geometry is built on a 1000-unit cap height, so it
scales to anything. Ink `#2b2218`, inline `#f2ece0`.

Reproduce with:

```sh
python3 scripts/tuscan_letters.py . --size 480
```

## Drawn, not traced — and why

M *is* in "PREMIUM", so extracting it looked like the obvious route. It is not
viable: the source is 689 × 313 px, which puts about 90 px across each letter
and leaves the bifurcated serifs — the feature that defines the style — as a
handful of blurred pixels. Tracing that reproduces the blur, not the letter. O
does not appear in the word at all and had to be drawn regardless.

So both are constructed from the style's rules instead. That has a second
benefit: O and M come out of the same parameters, so they are consistent with
each other rather than one being a trace and one an invention.

## What was matched

Read off the reference and rebuilt:

- **Heavy slab stems**, tapering very slightly towards the foot.
- **Wide flat top slabs** with a short spur turning down at the outer corners.
- **Clawed baseline serifs** — the serif splits and hooks below the baseline,
  finishing in a ball. This is the signature of the genre and carries most of
  the character.
- **An inline** following the stroke, inset from the outline.
- **A drop shadow** down and to the right.

Deliberately simplified: the reference's claws carry several nested curls, and
its letters are filled with fine horizontal engraving lines. Both are artefacts
of wood type printed at size; reproduced literally at vector scale they read as
noise. The inline stands in for the engraving.

## Shape notes

The **O** is a heavy ring, thicker at the sides (215 units) than over the crown
(150), with a short forked barb at the crown and the same clawed foot as the
other letters, so it sits in a word with them.

The **M** has upright outer stems rather than splayed ones, matching the
reference, with the V landing just above the baseline and its own small foot.
