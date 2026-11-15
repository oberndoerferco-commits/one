# OBERNDÖRFER logo — handover brief

Paste this into a fresh session. Everything below is already built and
pushed to `claude/vectorize-file-1uk2vw`.

## What exists

| file | what it does |
|---|---|
| `assets/oberndorfer-plate/index.html` | live editor: arched plate, banner, knockout, rules, optical spacing, measuring |
| `assets/oberndorfer-plate/plate.json` | the house letters, traced from the original artwork |
| `scripts/arch_plate.py` | re-traces the artwork; optical spacing, chip/nick repair |
| `scripts/font_plate.py` | turns ANY font into a plate.json, so the editor can set it |
| `scripts/marks.py` | shape library: circle, ellipse, shield, lozenge, hexagon, keystone, barrel, ribbon, arch band + type set straight, on an arc, or round a seal |
| `scripts/marks_render.js` | fits and renders any generated SVG to SVG + PDF |
| `scripts/arch_plate_batch.js` | renders many settings files in one browser |
| `assets/oberndorfer-plate/faces/` | 48 OFL display faces, all carrying the umlaut |

## Decisions already made (do not re-litigate)

- The house letters are a Victorian slab with bone terminals, traced
  from the artwork. They measured better than all 48 free faces.
- The cast shadow is welded into the silhouette. Seven attempts to
  lift it failed. It stays.
- The N has no counters in the source at any threshold. Solid, it is a
  blob; outlined or engraved, the line work carries it.
- Optical spacing is solved and on a toggle: equal PAPER between
  letters, not equal advances. The artwork's own was 50% uneven.

## Manufacturing floors (measured, not assumed)

| process | min line | what the mark needs |
|---|---|---|
| hot foil on leather | 0.50 mm | solid cuts only; engraved needs 285 mm+ |
| laser engraving | 0.15 mm | solid lockup ~60 mm |
| casting + polishing | 0.30 mm | ~95 mm |

Engraved/inline artwork is a PRINT tier. The die needs a solid cut.
This is the one conclusion every round of measuring has repeated.

## State this up front in the new session

1. **Structure** — ribbon only / plate only / plate + ribbon / seal / none
2. **Letterform** — the house letters, or a named face
3. **Treatment** — solid, outlined, engraved, knockout
4. **Where it goes** — leather stamp, print, both
5. **Bend** — arched, or straight

## What was never tried

The ribbon as the WHOLE logo, with no plate behind it. Every version
so far hung the ribbon under the plate. `marks.py` already has the
ribbon with folded, forked tails; nothing has set the name ON it.
