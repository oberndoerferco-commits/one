# AI Veterinary — aiveterinary.org

> Less paperwork. More animal care.

Planning workspace for AI Veterinary, a documentation assistant for veterinary
teams. The vet types rough notes, the AI structures them into a report, the vet
reviews and approves it, and from that approved record the product generates
owner instructions, referral letters and translations. The vet stays in charge.

This folder is independent of the Shopify theme content in the rest of this
repository.

**Status:** research and design. No application code yet, and deliberately so
(see the brief, §21–22).

## Documents

| | Document | What it answers |
|---|---|---|
| A | [Competitive analysis](docs/01-competitive-analysis.md) | What vets use today, what AI scribes exist, which systems have APIs, where the gap is |
| B | [Product architecture](docs/02-architecture.md) | Stack, data model, AI pipeline, permissions, audit, API, deployment |
| C | [MVP specification](docs/03-mvp-spec.md) | Exactly what we build first, acceptance criteria, metrics, build plan |
| D | [UX](docs/04-ux.md) | Desktop, keyboard-first workspace; states; interactions; accessibility |
| E | [Security & privacy model](docs/05-security-model.md) | Threat model, controls, dev-data rule, gate before real data |
| — | [Brand](docs/06-brand.md) | Positioning lines to test, tone, visual direction |
| — | [Costs](docs/07-costs.md) | Competitor prices, our AI cost per consultation, running and build costs |

## Product principles (from the brief)

1. **Less computer, more animal care.** The success metric is the time from
   finishing a consultation to having accurate, approved documentation.
2. **Text-first.** Bullets, abbreviations and typos are the input. Voice may come
   later and is never required.
3. **Enter once, reuse everywhere.** An approved structured record is the single
   source for every document.
4. **The AI assists and the vet decides.** Everything the AI writes is a draft
   until a vet approves it. Missing information is flagged and never invented.
   Medication details are never changed.
5. **Work alongside existing software.** Standalone browser app first. Later,
   integrations only through official APIs and partnerships. No scraping and no
   fake integrations.
6. **Workflow over features.** If it doesn't make the vet's day faster, it waits.

## Next steps

1. Discovery: 12–15 vet, nurse and reception interviews (DE, IT, UK) plus
   shadowing sessions (MVP spec §9, §10).
2. Build the synthetic eval set and the extraction schema before any UI.
3. A clickable prototype on synthetic patients, timed with 5 vets.
4. Contact PIMS vendors' partner programmes early. Integration agreements take
   months (see competitive analysis).
