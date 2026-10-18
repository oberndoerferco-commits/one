# Monogram canvas

An all-over repeat laid out like a classic monogram canvas (reference:
`canvas-reference.jpg`), built only from Oberndörfer marks:

| Motif | Source |
| --- | --- |
| OM blackletter monogram | `om-reference.png`, traced to `motifs/om.svg` |
| Star-cross in a disc | `motifs-reference.pdf` → `motifs/roundel.svg` |
| Star-cross with outline ring | `motifs-reference.pdf` → `motifs/halo.svg` |
| Star-cross on a square | `motifs-reference.pdf` → `motifs/tile.svg` |

The three star-cross motifs are your PDF's vector paths, unchanged; only their
colours are swapped per colourway.

Layout: motifs on a diagonal grid, 40 mm apart in a row. The OMs run in
diagonal lines alternating with the discs; the outline and square motifs sit
in the rows between. One repeat is 80 × 80 mm and holds two of each motif.
OM 22 mm wide, disc 15.5 mm, outline motif 16.5 mm, square 13 mm, which leaves
at least about 7 mm of clear ground between neighbouring motifs.

## Files

- `canvas-<colourway>-tile.svg`: one repeat at true size (mm), for print, jacquard or plate artwork.
- `canvas-colourways.jpg`: graphite (your PDF's greys), denim, cognac, ivory.

## Regenerate

```
pip install potracer opencv-python-headless numpy   # only for the OM trace
python3 -I design/monogram-canvas/trace_om.py
python3 -I design/monogram-canvas/extract_motifs.py
python3 -I design/monogram-canvas/generate.py
```

Spacing, sizes and colours are at the top of `generate.py`.
