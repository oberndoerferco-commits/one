# Oberndörfer Milano

Working repository for the store `oberndoerferco.com` — the house, its rules,
and the theme working copy.

## Start here

| | |
| --- | --- |
| **Dashboard** | https://claude.ai/artifact/CP9kz8iV7ESgJehs5bLwbZ |
| **The house** | [`docs/handbook/README.md`](docs/handbook/README.md) |
| **The standing plan** | [`docs/handbook/plan.md`](docs/handbook/plan.md) |
| **House rules — everyone inherits these** | [`CLAUDE.md`](CLAUDE.md) |

## The house

Eleven roles in four divisions, staffed the way a maison is staffed. You speak
to your co-founder; the co-founder runs the house.

```
  FOUNDER'S OFFICE      STUDIO              COMMERCIAL             MAISON
  co-founder            creative-director   merchandising-manager  atelier-director
  performance-analyst   art-director        ecommerce-manager      communications
                        editorial-director  client-advisor
                                            client-relations
```

Briefs in `.claude/agents/`. Commands in `.claude/commands/`:
`/brief`, `/monday`, `/funnel`, `/journal`, `/product`, `/enquiry`, `/campaign`.

## Where the business stands

Twelve months to 15 Sep 2026: 8,601 sessions → 158 cart additions →
139 reached checkout → **1 order, €10** (a test). The store works; the demand
does not exist yet. Full diagnosis in the plan.

## Art of Living page

- Page: `/pages/oberndorfer-x-miramare-sanremo` (titled "Art of Living")
- Template: `templates/page.art-of-living.json`
- Theme: **Claude** (unpublished, id `204228231493`)

| File | What it is |
| --- | --- |
| `theme/templates/page.art-of-living.BEFORE.json` | The template before the copy rewrite |
| `theme/templates/page.art-of-living.json` | The template as written to the Claude theme |
| `docs/art-of-living-copy-review.html` | The copy review: diagnosis, rewrite, voice rules |

Diff the two JSON files to see exactly which strings changed.

### Not applied

- Captions for the four full-bleed images in `section_aol_pieces` — drafted in
  the review, but they need checking against the actual photographs first.
- Optional hero line over `hero_eAhQMJ`.
- Moving "a byproduct of the meat industry" onto the Materials & Craftsmanship page.
- Changing the page handle to `art-of-living` with a redirect from the old one.

## Other files

- `docs/dashboard.html` — source for the published dashboard above.
- `scripts/README-theme-writes.md` — how to write large theme files correctly.
