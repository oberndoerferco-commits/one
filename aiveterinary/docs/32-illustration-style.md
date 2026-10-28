# 32 · Illustration style: warm ink sketch

Every drawing on the site (animal icons, the hero, the booklet, travel and loading scenes) is one family: an ink line over a flat, slightly misregistered coat wash, like a pen sketch coloured with watercolour. Source of truth: `site/src/components/animal-art.ts` (drawings), `site/src/components/art.css` (tokens). Logo files (`Logo.astro`, `public/logo-*.svg`, favicon) are separate and final.

## Palette

| Role | Token | Light | Dark |
|---|---|---|---|
| Ink line | `--sk-line` | `--art-ink` #12304a | warm chalk #eadfd0 |
| Eyes, nostrils | `--sk-eye` | #12304a | #12304a (always sits on a coat fill) |
| Eye highlight | `--sk-hi` | #fff7ec | #fff7ec |
| Accent (collar, comb, heart, suitcase, nose) | `--sk-accent` | #d86c50 (logo terracotta) | #f28a70 |
| Paper blob behind scenes | `--sk-paper` | `--hs-blob` | `--hs-blob` |
| Ground shadow | `--sk-shadow` | navy 10 % | black 28 % |
| Coats | existing `--hs-dog`, `--hs-dog-2`, `--hs-cat`, `--hs-cream`, `--ic-rabbit`, `--ic-horse(-2)`, `--ic-ferret(-2)`, `--ic-shell(-2)`, `--ic-bird(-2)`, `--ic-ear` | from styles.css | from styles.css |

- Never hard-code a fill that only works on one background. Dark values come from the tokens; the line flips to a light chalk in dark mode so silhouettes never dissolve into the page.
- Per animal: one coat colour, at most one markings colour, plus the accent used once (a collar, a comb, a nose). The booklet cover uses `--accent` (teal), its paw and label `--surface`.

## Line

- One pen: round caps and joins, `stroke="var(--sk-line)"` on the `<svg>`, everything inherits.
- The weight follows the rendered size so ink looks the same on screen: `strokeFor(px)` gives about 1.2px at 20px, 1.6px at 34px, 2px at 64px, 3px at 150px, 4–5px at hero size (capped at 2.8 grid units).
- Detail strokes (fur ticks, haunch and leg lines, scute seams, feather scallops, whiskers) carry `class="d"` and are drawn at 0.62× the contour.
- Hand-drawn feel comes from the path shapes, not filters: slightly uneven curves, and the coat fill is the same path nudged 0.6/0.8 units down-right (`class="w"`), so colour peeks out on one side and paper shows on the other. No SVG filters, no blur, no rough-edge effects.

## Detail by size

| Size | Shows |
|---|---|
| ≤ 30px (chips, list bullets) | silhouette, coat, markings, eye; `.d` details hidden via `sk-xs` |
| 34–64px (lists, cards, footer) | plus detail strokes |
| 88–150px (page headers) | same drawing; thinner relative line |
| scenes (220–540px) | animals placed with `place()` at scene scale with one scene stroke; the scene draws a single shared ground line |

## Drawing the animals

All animals stand in profile facing right on the ground line y ≈ 44.6 of a 48×48 grid, so they read the same in a row. Study the silhouette first, then simplify:

- **Dog:** sitting lab type. Stop between skull and muzzle, drop ear, deep chest, straight foreleg, round haunch, tail up, terracotta collar.
- **Cat:** sitting. Two upright ear triangles (near and far), short muzzle with whisker pad, sloping back, tail wrapped round the front paws.
- **Rabbit:** crouched. Long ears laid back, high round haunch, cotton tail, blunt muzzle.
- **Guinea pig:** loaf body, big blunt head, petal ear, no tail, tiny pink feet, bicolour patches.
- **Ferret:** bounding arch. Long body, short dark legs, small round ear, dark mask over the eye, pale muzzle, long tail.
- **Horse:** walking. Long head angled down, arched neck with mane, level back, rounded croup, tail, four legs, the hind cannon below a backward-pointing hock.
- **Bird (budgie, also used for parrots and canaries):** perched. Short hooked beak with cere, yellow face, green body, scalloped folded wing, long tail behind the perch.
- **Reptile (tortoise):** high dome with vertebral and costal scutes, marginal rim, column legs, head on a short neck.
- **Fish (goldfish):** deep oval body, forked tail, dorsal and anal fins, gill arc, big eye.
- **Hen:** plump breast, upright tail, single comb and wattle in terracotta, short beak, yellow legs.
- **Paw:** four toe pads and the main pad (the `general` icon).

## Composition (scenes)

- An irregular paper blob behind, one ground line, the animals from the icon set (never a second drawing of the same animal), and one or two warm accents (a heart, two dots).
- Animals face each other or face the content. Keep the edges open: nothing touches the viewBox border.

## Hard rules

- No crosses or plus signs anywhere: no medical cross, no "+", no four-point sparkles, no crossing hatch. Junctions are T-shaped, and yarn and fur strokes run parallel.
- No text inside drawings. Decorative SVGs are `aria-hidden="true"`; the hero keeps `role="img"` and its label.
- Inline SVG only: no rasters, fonts, libraries or filters. Prefer no motion; the loading cat's yarn ball is the only animation, and it stops under `prefers-reduced-motion`.
