# The house

Oberndörfer Milano is staffed the way a maison is staffed: twelve roles in four
divisions. You speak to your co-founder; the co-founder runs the house.

```
                              YOU
                               │
                          co-founder
              your partner — the only one you must remember
                               │
        ┌──────────────┬───────┴───────┬──────────────┐
        │              │               │              │
  FOUNDER'S OFFICE   STUDIO       COMMERCIAL       MAISON
        │              │               │              │
  performance-      creative-     merchandising-  atelier-
    analyst          director        manager       director
                        │               │              │
                    art-director   ecommerce-    communications
                        │            manager
                   editorial-          │
                    director      client-advisor
                                       │
                                 client-relations
```

## The roles

### Founder's Office

| | |
| --- | --- |
| **co-founder** | Your partner. Strategy, priorities, and putting the right person on the right thing. Disagrees when the plan is wrong. |
| **performance-analyst** | The only one permitted to state a number as fact. Trading figures, the funnel, and filtering the bots out of them. |

### Studio — how the house looks and sounds

| | |
| --- | --- |
| **creative-director** | Guardian of the identity. Everything public passes through this role before it ships — including the co-founder's work. |
| **art-director** | Imagery, film, campaign, lookbook. Never generates a product that does not exist. |
| **social-media-manager** | Instagram and TikTok end to end — trends, calendar, and the generation prompts that produce the content. |
| **editorial-director** | Every word the house publishes — the journal, product copy, search. Runs the only channel that has ever worked here. |

### Commercial — how the house sells

| | |
| --- | --- |
| **merchandising-manager** | The assortment. Which of the 269 pieces are shown, how they are grouped, and whether each page earns its price. |
| **ecommerce-manager** | The store as a machine. The funnel, the checkout, speed, navigation. Reads the theme, never writes to it — it writes briefs you paste into the website theme chat. |
| **client-advisor** | Private clients. Everything over €2,500, commissions, exotic skins. The pieces that will never move through a cart. |
| **client-relations** | The client register. Correspondence, welcome, abandoned checkout, after-sale, repeat purchase. |

### Maison — what the house is

| | |
| --- | --- |
| **atelier-director** | Materials, tanneries, provenance, CITES, construction, care. The source of every material fact the copy stands on. |
| **communications** | The house's voice outward. Press, partnerships, stockists, social. |

## What you type

| Command | What happens |
| --- | --- |
| `/brief` | The morning brief. One thing to do today, under 150 words. |
| `/monday` | The Monday review — filtered figures, what changed, one move for the week. |
| `/funnel` | Where clients are being lost, and the single biggest leak with evidence. |
| `/journal` | Publishes the next piece from the backlog of ten, on your go-ahead. |
| `/product <name>` | Brings one piece's page up to standard. Before and after, first. |
| `/enquiry <message>` | Drafts a reply to a private client. You send it. |
| `/campaign <occasion>` | Briefs the whole studio on a campaign as one piece of work. |

Or simply describe what you want. The co-founder routes it.

## Theme work

The house does not touch the theme. The owner makes theme changes himself, in a
separate **website theme** chat.

So when a theme change is needed, `ecommerce-manager` writes a self-contained
brief to `docs/handbook/theme-briefs/` — the exact block, the exact Liquid, the
reasoning, and how to check it worked — and you paste the whole file into that
chat. A brief that assumes our context is a brief that fails there.

## How work moves through the house

1. You bring a goal to **co-founder**.
2. It checks the figures with **performance-analyst** before deciding anything.
3. It briefs the specialist. **creative-director** sets direction on anything
   the public will see.
4. **atelier-director** supplies the material facts. Nothing unverifiable ships.
5. **creative-director** approves.
6. You approve. Then it publishes.

Steps 5 and 6 are never skipped, by anyone.

## The rules everyone inherits

In `CLAUDE.md` at the repository root — the register, the retire list, the facts
that must not drift, and six guardrails. The ones that bite:

- Nothing touches the live theme. Work lands on the unpublished "Claude" theme.
- No price changes, no deletions, no posting, no sending, no spending, without
  you saying so.
- Every traffic figure arrives with what was filtered out of it.

## Where things are written down

```
docs/handbook/plan.md          the standing plan and the order of work
docs/handbook/reviews/         Monday reviews, dated
docs/handbook/content-log.md   what the journal published, and what it earned
docs/handbook/enquiries.md     every private-client enquiry and its outcome
docs/handbook/crm-log.md       correspondence flows and their performance
docs/handbook/social-log.md    what was posted, and what it did
docs/handbook/prompt-library.md  generation prompts that worked, ready to run
docs/handbook/theme-briefs/    briefs to paste into the website theme chat
docs/handbook/catalogue-audit.md  product data completeness, all 269
docs/handbook/theme-baseline.md   the live theme, and what is in it
```
