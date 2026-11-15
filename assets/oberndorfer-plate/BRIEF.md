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

---

# References and work so far

Nothing here needs re-uploading. Everything the user sent is in the
repo, and so is everything that was made from it.

## The user's references

All 24 images are in `assets/oberndorfer-plate/references/`, with
`all-references.png` as a contact sheet of the lot. They fall into
four groups.

**The source artwork.** `source.jpg` in the parent folder. An arched
nameplate, eleven letters on one arch inside one frame: Victorian slab
with bone terminals, ruled line-fill inside each stroke, a cast shadow
pushed down and right. Everything in `plate.json` was traced from it.

**Ornate inline Romans** — the "GERMAN SCHRIFT" gold specimen, the
engraved Victorian alphabet on cream, the decorated-initial sheets.
This is the register the user keeps returning to: Roman caps, fine
inline striping inside the letter, delicate floreted serifs, often a
drop shadow. Nearest free faces: Cinzel Decorative, Asset, Diplomata
SC, Elsie Swash Caps, Almendra Display, Gilda Display. None is an
exact match; the exact ones are commercial.

**Banners and ribbons** — several screenshots of ribbon sheets. Scroll
banners with rolled or folded ends, forked tails, swags, hand-drawn
ribbons. The user sent these repeatedly and they were only ever used
as a part hanging UNDER the plate. See "What was never tried".

**Red-pen annotations on our own renders.** Two matter: one marks
where the frame's ends should stop (right after the O and the R), one
draws the banner as a wide shallow swag dipping to a centre point.

**Chrome Hearts.** Sent as a liked style, explicitly NOT to copy. The
gothic/engraved-silver register is fair ground; their wordmark, cross,
dagger, fleur-de-lis and scroll lockup are not.

## What was made

| folder | what it holds |
|---|---|
| `final/` | the current mark, 4 cuts: engraved, engraved+shadow, ornament-cut, solid |
| `fifty2/` | 50 structural variations on the plate: rules, beading, flanking devices, finials, pendants, knockout, shadow |
| `fifty3/` | 50 as 10 faces x 5 banners, including the folded-tail ribbon |
| `faces48/` | all 48 free faces set in the plate |
| `faceframe/` | 9 faces compared like-for-like, with leather minimums |
| `umlaut/` | the O-umlaut as a device: ring + dots at the letter's own proportions, and the plate crowned with the same two dots |
| `brand/`, `system/`, `bolder/`, `sharper/`, `engraved/`, `ideas/` | earlier rounds, each with settings, SVG and PDF |

Each folder carries the settings JSON beside every drawing, so any of
them can be reopened in the editor and changed.

## Honest state

The user does not like any of it yet, and the reason is not the
drawing - it is that fifty variants of one template is not a design.
Every round answered a local note (rounder, shorter, different font)
and none answered what the mark should BE.

Two specific misses worth not repeating:

1. The ribbon references were never taken as a whole-logo idea, only
   as a sub-part under the plate.
2. Manufacturing measurement drove the aesthetics instead of checking
   them at the end. Design first, measure second.
