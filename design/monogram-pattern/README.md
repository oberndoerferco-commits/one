# Monogram pattern

A seamless repeat in the spirit of an embossed damask, with the Oberndörfer
star-cross in the place a classic monogram canvas puts its four-petal flower.

Run `node design/monogram-pattern/generate.js` to regenerate every SVG.

| File | What it is |
| --- | --- |
| `generate.js` | The geometry: logo trace, lattice, scrolls, colourways |
| `tile-*.svg` | One 400×400 seamless tile per colourway — repeat it edge to edge |
| `logo.svg` | The logo as a clean vector, traced from `logo-reference.png` |
| `previews/preview-*.png` | 2×2 tiles of each colourway |

Colourways: `line` (black on white, for production artwork), `embossed-ivory`
(like blind-embossed card), `embossed-cognac` (like blind-embossed leather),
`navy-gold` (foil / print).

## Layout of one tile

- **Logo** at the corners and centre, raised, with a sunk inner outline so it
  still reads as the outline mark when blind-embossed.
- **Concave star** around each logo; its tips meet the stars around the small
  flowers, so the frames form one continuous lattice.
- **Oval medallions** between the logos, each holding four mirrored C-scrolls.
- **Small quatrefoil flower** with leaves and tiny scrolls at the edge midpoints.

To change a colourway, edit `variants` at the bottom of `generate.js`.
