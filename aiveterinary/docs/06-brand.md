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

## Visual direction (original note, superseded above where they differ)

- Calm neutrals, one deep teal or ink-blue accent. Avoid the purple-gradient
  "AI" look and the cartoon-paw pet-shop look.
- Photography: real clinical moments with hands on animals, not screens.
- Logomark: simple, geometric, works at 16 px and in monochrome (letterheads,
  fax-quality printouts still exist in clinics).
- Typography: a humanist sans (Inter / Source Sans 3 / IBM Plex Sans) for product;
  same family for marketing.
