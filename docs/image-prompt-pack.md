# Image prompt pack — Oberndörfer Milano

Briefs written for the live catalogue: 3-place and 8-place watch boxes, and the
calf leather trays. Run them with `scripts/genimage.py`; see
`scripts/README-image-generation.md` for setup.

Every product brief below assumes `--ref` with the real Shopify photograph. The
model re-lights and re-stages a piece that exists. It does not invent one.

## House look

Carry this into any brief you write yourself. It is the Art of Living register
the site copy already uses: quiet, material, unhurried.

> Editorial still life, natural window light from the left, soft falloff, no
> hard specular hits on the leather. Muted warm-neutral palette, deep green and
> stone. Shallow depth of field, 85mm equivalent, shot slightly above eye level.
> Generous negative space. No text, no logos, no props that upstage the piece.

Avoid: ring flash, glossy reflections, gradient backdrops, floating objects,
confetti, anything that reads as a stock advertisement.

## Product, re-staged

**Valet tray, on a dresser.** For any of the trays at €129.

```bash
scripts/genimage.py \
  --ref <shopify url for the tray> \
  --size 1536x1024 --quality high --out tray-dresser.png \
  --prompt "Keep the tray exactly as photographed: same leather colour, same
  stitching, same proportions, same interior. Place it on a walnut dresser
  beside a folded linen pocket square. Morning window light from the left, soft
  shadow to the right. Muted warm-neutral palette. Shallow depth of field, 85mm.
  Editorial still life, generous negative space, no text or logos."
```

**Tray in use.** Shows the thing it solves, which is the pitch in the product copy.

```bash
--prompt "Keep the tray exactly as photographed. Overhead three-quarter view on
a stone surface. Inside it: a set of brass keys and a folded pair of reading
glasses, arranged loosely, not styled into a grid. Late afternoon light, long
soft shadows. No watch, no phone, no text."
```

**3-place watch box, open.** €395 pieces, where the velvet interior is the story.

```bash
--prompt "Keep the box exactly as photographed: same leather colour and grain,
same hardware, same velvet interior, same number of compartments. Open, on a
dark oak desk, angled so the interior lining catches the light. Empty
compartments. Window light from the left, soft shadow. 85mm, shallow depth of
field. Quiet editorial still life, no text or logos."
```

**8-place watch box, closed.** The €1,490 to €1,682 tier. Restraint sells it.

```bash
--prompt "Keep the box exactly as photographed, including the Saffiano
cross-hatch texture and every hardware detail. Closed, three-quarter view, on a
polished stone surface against a soft stone-grey background. Single window light
from the upper left, gentle falloff, no hard highlights. Generous negative
space above. 85mm, shallow depth of field. No text, no logos, no props."
```

## Model and lifestyle

No reference photograph exists here, so these are text-to-image. Keep the
product out of frame or far out of focus. A generated bag is a fabrication; a
generated hand near a real product is a compositing job, not a prompt.

**Hands, detail.** The safest lifestyle shot, and usually the best one.

```bash
scripts/genimage.py --size 1024x1536 --quality high --out hands-detail.png \
  --prompt "Close crop on an adult's hands resting on a walnut desk beside a
  folded newspaper, shirt cuff visible, no watch, no jewellery. Warm window
  light from the left. Muted palette, film grain, editorial photography. Hands
  in sharp focus, background falling away. No product, no text, no face."
```

**Interior, no people.** For page headers and the Art of Living template.

```bash
scripts/genimage.py --size 1792x1024 --quality high --out interior.png \
  --prompt "A quiet Milanese apartment interior in late morning. Tall window,
  sheer curtain, parquet floor, a low walnut console against a stone-white
  wall. Empty surfaces. Muted green and stone palette. Natural light only,
  soft shadows. Architectural editorial photography, wide, unpeopled, no text."
```

**Portrait.** Only if you genuinely need a person. Describe light and mood, not
ethnicity or a real person, and never a named individual.

```bash
scripts/genimage.py --size 1024x1536 --quality high --out portrait.png \
  --prompt "Editorial portrait of an adult seated at a desk in a quiet study,
  turned three-quarters away from camera, face not fully visible. Tailored dark
  wool. Window light from the left, deep soft shadows. Muted stone and green
  palette. 85mm, shallow depth of field, film grain. No product, no text."
```

## Before publishing

- **Check it against the real piece.** Hinges, stitch lines, compartment counts
  and lining colour are what these models quietly get wrong.
- **Disclose AI imagery in advertising.** EU transparency rules apply to
  synthetic media, and showing a product that differs from what ships is a
  separate advertising-law risk regardless of disclosure.
- **Never use a generated image as the main product photo.** Use it for mood,
  headers and lifestyle context. The buyer at €1,682 is paying for the specific
  object in the photograph.
