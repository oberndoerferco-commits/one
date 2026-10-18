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

Layout (from `layout-sketch.png`): every OM is the centre of a rosette. Four
outline motifs sit close around it on the diagonals, square motifs above,
below and to either side, and disc motifs at the corners. Grid spacing 36 mm;
one repeat is 72 × 72 mm. OM 21 mm wide, disc and outline motifs 15 mm,
square 12.5 mm.

## Files

- `canvas-<colourway>-tile.svg`: one repeat at true size (mm), for print, jacquard or plate artwork.
- `canvas-colourways.jpg`: graphite (your PDF's greys), denim, cognac, ivory.
- `canvas-sketch-vs-pattern.jpg`: the sketch next to the generated pattern.

## Regenerate

```
pip install potracer opencv-python-headless numpy   # only for the OM trace
python3 -I design/monogram-canvas/trace_om.py
python3 -I design/monogram-canvas/extract_motifs.py
python3 -I design/monogram-canvas/generate.py
```

Spacing, sizes and colours are at the top of `generate.py`.
