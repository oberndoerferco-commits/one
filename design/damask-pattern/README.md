# Damask monogram

The first reference (embossed damask with oval scroll medallions) redrawn as
clean, stamp-ready vector art. The star-cross stands on its own where the
reference had its large flower: no star frame, no lattice around it.

- **Logo** at the corners and centre of each repeat.
- **Four oval medallions** point at each logo like petals. Each holds four mirrored C-scrolls.
- **Small four-petal flower** with a pair of scrolls above and below, between the logos.

Regenerate with `node design/damask-pattern/generate.js`.

## Files

- `damask-tile.svg`: one 80 × 80 mm repeat, black artwork at true size. For the plate / roller maker.
- `damask-sheet-240x160mm.svg`: 3 × 2 repeats as one seamless vector.
- `damask-preview.png`: the 240 × 160 mm sheet as line art.

## Stamping specs (at the 80 mm repeat)

- Logo 26.4 mm tip to tip.
- Thinnest line 1 mm (oval rims, scroll tails). Smallest dot 2 mm. Gaps ≥ 1.2 mm.
- Solid black, no gradients or hairlines.
- Flower centre hole is 1.4 mm; it may fill in on soft leathers, which is fine.
- `TILE_MM` in `generate.js` scales everything. Don't go below about 70 mm,
  or the 1 mm lines drop under the stamping minimum.
