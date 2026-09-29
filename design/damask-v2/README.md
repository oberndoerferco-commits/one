# Damask v2

A close vector redraw of the embossed reference (`reference.jpg`), with the
star-cross in place of the large flower and nothing behind it.

- **Logo**: stands alone where the flower was.
- **Frame**: four sweeping curves around each logo, tall and pointed, as in the photo.
- **Oval medallions**: four paisleys each (heads outward, tails curling in), with a bead stem between them.
- **Centre clusters**: a cross of beads, two small four-petal flowers, ram's-horn scrolls and leaves.

Regenerate with `node design/damask-v2/generate.js`, then `node design/damask-v2/preview.js`.

## Files

- `damask-v2-tile.svg`: one 150 × 150 mm repeat, black artwork at true size. For the plate / roller maker.
- `damask-v2-sheet-300x300mm.svg`: 2 × 2 repeats as one seamless vector.
- `damask-v2-preview.png`: embossed white-on-white (like the photo) and black line art. Review only.

## Stamping specs (at the 150 mm repeat)

- Logo 51 mm tip to tip.
- Lines 1.35 mm; scroll tails taper to about 1 mm; smallest bead 1.6 mm.
- Solid black, no gradients or hairlines.
- `TILE_MM=120 node generate.js` scales the whole pattern. Below about 110 mm
  the finest curls drop under 1 mm and may blur when stamped.
