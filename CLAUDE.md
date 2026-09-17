# Oberndörfer Milano — house rules

Everyone in this house inherits this file. Read it before you write a word of
client-facing copy or touch the store.

The house is eleven roles in four divisions — Founder's Office, Studio,
Commercial, Maison. The chart and the briefs are in `docs/handbook/README.md`.
You speak to `co-founder`; it runs the house.

## The business

Luxury leather goods, jewellery, eyewear and furniture. Handmade in Italy.
Shopify store `www.oberndoerferco.com` (`5fae2a.myshopify.com`), Basic plan,
EUR, 269 products across 21 collections. Price band €110 → €34,250.

Three tiers, and they do not sell the same way:

| Tier | Range | Examples | How it sells |
| --- | --- | --- | --- |
| Entry | €110–€400 | trays, coasters, caps, t-shirts, watch boxes (3-place) | self-serve checkout |
| Core | €400–€2,500 | wallets, handbags, watch boxes (8-place), jewellery boxes, poufs | self-serve, but needs proof |
| Commission | €2,500+ | Mirror Handbag Ostrich, SAC Alligator, sofas, table trunks | conversation, never add-to-cart |

Most pieces are inventory 1. This is a one-of-a-kind house, not a warehouse.

## Voice

Established in `docs/art-of-living-copy-review.html` against fifteen houses in
the sector. The register is Italian–French maison: **full, slow, material-first,
subordinate clauses allowed.** Not Nordic minimalism. Not short lines.

What earns the register:

- **Institutions, dates and numbers do the boasting. Adjectives cannot.**
  Frette says "Official Purveyor to the Italian Royal Family, 1881", never
  "prestigious clients". Name the tannery, the year, the commission.
- **Name the hand.** Hermès frames handmade irregularity as the point. A piece
  is the work of a hand, not a machine — say so.
- **Specific and modest beats grand and vague.** Promemoria's founders repaired
  aristocratic carriages. That is why it lands.
- **Scarcity as preference, not tactic.** "We would rather make them slowly."

### Retire list — never use these words

Confirmed against every house in the sector. None of them use these. They are
the phrases that make expensive things read cheaply.

```
exquisite            timeless elegance      masterpiece
attention to detail  the perfect blend of   the finer things in life
impeccable           unparalleled           nestled
a true celebration of
```

If you catch one in existing copy, flag it. Do not quietly leave it.

## Facts — do not invent, do not drift

- The Hotel Miramare founding year appears as both 1870 and 1875 across
  sources. Write "the 1870s" until the hotel confirms.
- Leather is a byproduct of the meat industry — a real and creditable claim.
  It belongs on Materials & Craftsmanship.
- CITES certification applies to the alligator pieces. Never soften or omit it.
- The leather is not yet named. Poltrona Frau has Pelle Frau®, Serapian has
  Mosaico. Naming it is the highest-leverage change available to the catalogue.

Never invent a client, a stockist, a press mention, an award or a year. If a
claim cannot be sourced, it does not ship.

## Guardrails — everyone, no exceptions

1. **The house never writes to the theme at all.** The owner makes theme
   changes himself, in a separate "website theme" chat. The "Claude" theme this
   file used to name (id `204228231493`) no longer exists.

   The live theme is **"NEW WEBSITE BUG fix 7"**, id `206519796037`, Horizon-
   based. Read it freely — the working copy is in `theme/`, with the full
   inventory in `theme/MANIFEST.txt`. **Never write, never publish.**

   When theme work is needed, `ecommerce-manager` writes a brief to
   `docs/handbook/theme-briefs/` that the owner can paste straight into the
   website theme chat: what to change, where, the exact copy or Liquid, and how
   to check it worked. A brief that assumes our context is a brief that fails.
2. **Never change a price** without the owner saying so in writing.
3. **Never delete a product, collection, page or article.** Set to draft.
4. **Never post to a social account or send an email campaign** without the
   owner approving the exact copy first.
5. **Never spend money.** No ad campaigns, no app installs, no plan upgrades.
6. Anything irreversible or outward-facing gets confirmed first.
7. **Anything the public will see passes `creative-director` before it ships** —
   copy, imagery, a campaign, a page. No exceptions, including `co-founder`.
8. **Anything asserted about a material passes `atelier-director`.** If a claim
   cannot be substantiated, it does not publish.

## How the numbers are read

Shopify analytics on this store are **heavily bot-contaminated**. Before any
agent reports a traffic number, it must be filtered:

- Signups from `storebotmail.joonix.net` are Google Shopping crawlers.
- The large "direct / United States" block is largely non-human.
- `/password` landings are not shoppers.

Report human sessions, and say what you excluded. A number nobody trusts is
worse than no number. `performance-analyst` is the only role permitted to state
a figure as fact.

## Where the work is written down

- `docs/handbook/` — the house: who does what, and the standing plan.
- `docs/art-of-living-copy-review.html` — the voice, in full.
- `scripts/README-theme-writes.md` — how to write large theme files correctly.
- `theme/` — working copy of the Claude theme.
