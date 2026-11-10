# Oberndörfer nameplate

The arched plate, taken apart so the arch, the letter spacing and the
frame can be changed.

## What was done

The artwork arrived as one flat picture: eleven letters already turned
onto one arch, inside one frame. Nothing about it could be adjusted,
because the arch was baked into every letter.

`scripts/arch_plate.py` undoes that. The plate's two keylines are
circular to within 0.9 px, which is what makes the rest possible: fitting
them gives the centre the whole drawing was struck about, and each
letter's rotation is then just its own angle about that centre. Turn
every letter back by its own angle and the arch is gone, leaving upright
outlines, their widths, and the arc distance from each letter to the
next — a typesetting problem again, and one that can be re-struck onto
any arch at all.

The outlines come from `scripts/vectorize_lineart.py`: sub-pixel
iso-contours, corners kept, straight edges emitted as straight lines.
The engraved highlights inside each letter are traced as a second layer,
so the preview carries the drawn look rather than a silhouette.

    python3 scripts/arch_plate.py <image> assets/oberndorfer-plate

## What it measured

| | |
|---|---|
| top keyline | centre (798.9, 2239.4) px, radius 2073.4, worst fit 0.89 px |
| bottom keyline | 1817.0 px about that same centre, wandering 3.6 px |
| baseline | 1860.2 px, worst letter foot 2.4 px off |
| cap height | 154.9 px |
| letters | turned −18.8° to +18.2°, eleven of them |
| spacing | 109 to 131 px centre to centre — uneven by 20% |

At a cap height of 10.74 mm the plate comes out 97.9 × 24.2 mm, with a
baseline radius of 129 mm and a 6.67 mm rise over the word.

## Two things in the source

**The left dot of the umlaut is joined to the frame.** Not near it —
joined, by a neck six pixels wide, which is why it is not a shape of its
own in the picture at all. An opening with a disc of radius 5 cuts it
free: the keyline is 10 px thick and does not survive, while a dot 38 px
across keeps a core of 600 px, and only one of the two blobs left on the
whole plate is round. The viewer opens the gap above it to 0.80 mm and
the slider winds back to the original 0.04 mm.

**The frame is not concentric.** The two keylines were struck about
centres 71 px apart, so the plate is 1.4 per cent out of true — deeper at
the ends than in the middle. The viewer draws it concentric, which makes
it describable in one radius and one depth.

Neither is repaired silently: both are printed by the script and stated
in the viewer.

## The viewer

`index.html` reads `plate.json`. Arch rise is how far the baseline bows
over the word, so 0 is a straight line. Letter spacing adds to the gaps
the artwork already has. Margins are the clear gap from the ink to the
inside of the keyline, measured separately above and below because the
source's are 0.04 and 2.47 mm. Downloads SVG in millimetres.

`source.jpg` is the artwork, carried along so the viewer can lay it
underneath for comparison.
