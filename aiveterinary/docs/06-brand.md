# Brand — AI Veterinary · aiveterinary.org

## Tension to manage

"AI" in the name gets attention and makes the category clear. It also makes the
product sound like a chatbot that replaces the vet, which is exactly what we
aren't. So the name carries "AI" and everything else (tagline, visuals, tone)
says *professional tool, vet in charge*.

The `.org` domain reads as institutional/non-profit to many people. That helps
trust, but the product will be commercial. Recommend also securing
`aiveterinary.com` / relevant ccTLDs (`.de`, `.it`, `.co.uk`) if available, and
being clear on the site that this is a company.

## Positioning lines (to test with vets, not decide internally)

| Line | Angle | Risk |
|---|---|---|
| **Less paperwork. More animal care.** | outcome, emotional | generic-ish; many vendors say "less admin" |
| **Your notes. Finished.** | speed, ownership (vet's words) | plain; may undersell owner-facing docs |
| **From bullet points to approved records.** | exactly what it does | functional, less memorable |
| **Documentation at the speed of a consult.** | time | slightly long |
| **You examine. We write it up. You approve.** | the workflow + control | three beats; strong on trust |
| **The quiet assistant for veterinary teams.** | calm, not flashy | vague on value |

Recommendation for the landing page: headline **"Less paperwork. More animal
care."** with the sub-line **"You examine. We write it up. You approve."** One
states the outcome, the other states the control model.

## Tone

Plain, precise, clinical-grade. Short sentences. No hype words ("revolutionary",
"magic", "superpowers"), no human-like AI persona, no claims of accuracy
percentages we haven't measured. Say what it doesn't do.

## Visual system (decided 14 Oct 2026, from a benchmark of 22 sites)

Research: `docs/13-design-research.md`. The patterns below are the ones the
best-designed owner and vet sites share and that a zero-budget static site can
reproduce. Everything is implemented in `site/src/styles.css`.

| Token | Value | Role |
|---|---|---|
| `--bg` | `#fbf7f2` | warm cream page (Figo, Small Door, FirstVet, VetRec, Curala all use off-white, never pure white) |
| `--surface` | `#ffffff` | cards, so they lift off the page |
| `--ink` | `#12304a` | text, headings, illustration outlines; never `#000` |
| `--accent` | `#14655e` | primary buttons, links, nav CTA |
| `--accent-soft` | `#e6f1ef` | tints, chips |
| `--coral` / `--warm` | `#e8735a` / `#ffb400` | step numbers, blush, sparkles; decoration only |

- **Type**: Fraunces (display, `opsz` 72, `SOFT` 50, 600) for h1/h2 and card
  titles; Plus Jakarta Sans for body (17 px / 1.55) and UI. Same pairing as
  HappyDoc; Petleo uses Fraunces + Karla. Loaded from Google Fonts, three
  weights.
- **Buttons**: pill (`999px`), 44–48 px tall, 600 weight; primary filled
  accent, secondary accent outline; hover lifts 1 px.
- **Cards**: 16–20 px radius, 1 px tinted border `#e6e0d8`, no resting shadow.
- **Nav**: sticky, 4 items + one filled CTA (Health booklet) + language switch.
- **Hero**: kicker, display headline (max 12 words), one-sentence sub, primary
  pill + secondary, illustration right. Vet pages add trust chips under the
  CTAs (GDPR · EU hosting · no training · nothing recorded), the pattern
  Curala and VetRec use.
- **Section rhythm**: hero → proof strip (only claims we can defend) → species
  buttons → latest → three steps → vet band → FAQ → newsletter.
- **Illustration**: own SVG faces built from circles and ellipses on a 48-unit
  grid, 2.2 stroke in ink, soft fills, eyes ≈ 20 % of head width placed below
  the centre line, small nose and mouth, one blush per cheek. Shapes live in
  `site/src/lib/animal-icons.ts`; the hero scene reuses them. Owner side only;
  the vet workspace stays calm.
- **Tone**: owner pages informal where the language allows (IT "tu"); vet
  pages formal (DE "Sie"), proof over adjectives.

## Logo (final, 25 Oct 2026)

Chosen from the logo canvas (concept D2, "Coral app tile"): **two white paw
prints walking up and to the right on a coral rounded square**, with the
wordmark "AI Veterinary" and the locked tagline "Know what to do for your
animal". The brand sheet is the "Final logo: walking paws" artboard on the
design canvas. What this means for registration: `docs/26-logo-research.md`,
Part 4.

### The mark

Units: the tile is 100 × 100.

| Element | Specification |
|---|---|
| Tile | Square, corner radius 22 (22 % of the side), coral `#d86c50` |
| Prints | Two identical white paws, both turned 22° clockwise; pad centres at (30.7, 72.9) and (63.1, 37.5), so the trail rises at about 48° |
| Paw | Main pad: one large circle and two smaller lobes joined by tangent lines, with a shallow notch arc between the lobes. Toes: four equal beans (ellipses, 7.4 × 10) on one circle around the pad centre, at ±18° and ±54°, leaning outward 9° and 26°. The pad is 24 wide |
| Spacing | 15–17 between the prints and every edge; the gap between the two prints (about 15) matches the margins. The prints sit 1 unit towards the light toes, so the heavier pads do not crowd their corner |
| Colour | The concept coral `#e07a5f` gives white only **2.95:1** (WCAG relative luminance), not the 3.4:1 assumed. Deepened to `#d86c50` (same hue, lightness 62.5 % → 58 %) it gives **3.40:1**, above the 3:1 guideline for graphics, and the paws read better at 24–32 px. Logos are exempt from WCAG contrast; the deeper tile is simply the better icon and still looks like the concept |

Nothing else goes on the tile: no crosses, plus signs, hearts, sparkles or
letters.

**Small sizes.** Two prints blur below about 24 px: at 16 px each toe would be
narrower than 1.5 px. From 16 to 23 px use the **favicon**: one upright paw,
drawn larger (the pad is 44 % of the tile), with rounder toes so every gap stays
at least 1 px wide at 16 px. Same tile, same coral.

### Lockups

- **Horizontal** (`logo-horizontal.svg`): mark, a gap of 0.24 × the mark
  height, then the name over the tagline. The name's cap height sits on the
  tile's top edge and the tagline's baseline on its bottom edge; the tagline
  spans the name.
- **Stacked** (on the brand sheet; no file yet): mark centred above the name
  (name size 0.4 × the mark height), tagline under it, spanning the name.
- **Type**: Fraunces 700, opsz 72, SOFT 100, WONK 0, tracking −1 % (the
  site's heading face, softened). Tagline in Plus Jakarta Sans 800, capitals,
  tracking +12 %. Both are outlined in the SVG files, so they render without
  the fonts.
- **Colours**: name ink `#12304a`; tagline teal `#14655e` with "ANIMAL" in deep
  coral `#b8502f`. On dark grounds: name cream `#fbf7f2`, tagline `#6cc3b7`,
  "ANIMAL" `#f28a70`; the tile stays coral. One colour: everything ink
  `#12304a`, paws cut out of the tile.

### Clear space and minimum sizes

Clear space on every side: **one toe-bean height**, which is 10 % of the mark
height. The same rule applies to the mark and both lockups.

| Use | Minimum |
|---|---|
| Two-paw mark | 24 px on screen (32 px preferred), 8 mm in print |
| One-paw favicon | 16–23 px only |
| Horizontal lockup with tagline | 48 px tall (about 300 px wide), 12 mm tall in print |
| Stacked lockup | mark 96 px |

Below the lockup minimum, use the mark and the name without the tagline, as in
the site header.

### Usage rules

- Use the files below as they are. The tile stays coral with white paws on
  light and dark grounds.
- In navigation the mark always sits next to the name in live text (the
  header uses `Logo.astro` beside "AI Veterinary").
- Never recolour the tile or the paws, and never mirror, rotate or re-space
  the prints: they always walk up and to the right.
- Never add anything to the tile. Crosses and plus signs are excluded for legal
  reasons (`docs/26-logo-research.md` §2.2), and hearts, sparkles and letters
  for clarity.
- Don't use the two-paw mark under 24 px. Don't stretch it, outline it, or add
  shadows or gradients.
- Red stays reserved for the emergency button. The coral tile is never used as
  a warning or a button.

### Files

In `site/public/` unless noted.

| File | What |
|---|---|
| `favicon.svg` | One-paw favicon, vector; what browsers show in the tab |
| `favicon.ico` | 16 and 32 px with one paw, 48 px with both paws (PNG-compressed entries) |
| `apple-touch-icon.png` | 180 × 180, opaque, full-bleed coral; iOS rounds the corners |
| `icon-192.png`, `icon-512.png` | The rounded tile with transparent corners (manifest, purpose "any") |
| `icon-maskable-512.png` | Full-bleed coral, prints scaled to 90 % so every point sits inside the 80 % safe zone (manifest, purpose "maskable") |
| `logo-mark.svg` | The mark |
| `logo-horizontal.svg` | Mark, name and tagline, outlined, for light grounds |
| `logo-horizontal-dark.svg` | The same for dark grounds |
| `logo-mono.svg` | One colour (ink), paws cut out of the tile |
| `manifest.webmanifest` | Name "AI Veterinary", short name "AI Vet", the three icons, theme and background `#fbf7f2`, standalone, start URL `/`. No service worker yet |
| `og.png`, `og-it.png`, `og-de.png` | Share images with the new mark, made by `site/scripts/og.mjs` |
| `site/src/components/Logo.astro` | The mark as inline SVG; props `size`, `class` and `title`; aria-hidden unless it has a title |

The PNGs and the ICO are rendered from the same geometry with sharp. The
paths in the SVG files are flat (no transforms), so they can be edited
directly.

## Visual direction (original note, superseded above where they differ)

- Calm neutrals, one deep teal or ink-blue accent. Avoid the purple-gradient
  "AI" look and the cartoon-paw pet-shop look. (The final logo is a paw mark,
  chosen by the owner; see "Logo" above and the trade-mark note in
  `docs/26-logo-research.md`.)
- Photography: real clinical moments with hands on animals, not screens.
- Logomark: simple, geometric, works at 16 px and in monochrome (letterheads,
  fax-quality printouts still exist in clinics).
- Typography: a humanist sans (Inter / Source Sans 3 / IBM Plex Sans) for product;
  same family for marketing.
