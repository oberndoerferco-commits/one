# 50 monogram variations

Built only from Oberndörfer marks: the OM monogram, the star-cross (solid and
outline), the three star-cross motifs from the PDF, plus a small spark derived
from the logo's notches. Families: rosettes (1–5), diagonal canvas (6–10),
half-drops (11–14), checkers (15–18), trellis and grids (19–22), stripes
(23–27), tonal jacquards (28–31), rotation and geometry (32–35), medallions
(36–39), scattered (40–42), linked (43–45), minimal (46–50).

- `overview-all-50.jpg`: all fifty, numbered.
- `sheet-1.jpg` … `sheet-5.jpg`: ten per sheet, larger.
- `tiles/NN-<name>.svg`: one repeat each at true size (mm).

Regenerate: `python3 -I design/monogram-variations/generate.py`, then
`node design/monogram-variations/render.js` (needs Playwright).
Motif sources live in `../monogram-canvas/motifs/`.

## Shortlist

`shortlist.pdf`: 3, 15, 33 and 41, one A4 page each at true size. Rebuild with
`node design/monogram-variations/shortlist.js 3 15 33 41`.
