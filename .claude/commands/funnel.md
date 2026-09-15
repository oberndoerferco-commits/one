---
description: Diagnose exactly where visitors are being lost, and what to fix first
---

Diagnose the conversion funnel.

Use the `analyst` agent to establish, over the last 90 days:

1. Filtered human sessions, by source and landing page.
2. How many reached a product page, and which products.
3. How many added to cart, and on which products.
4. How many reached checkout, and how many completed.

Then have `merchandiser` inspect the specific product pages where people are
dropping, checking for:

- Products with inventory 0 and `DENY` policy — silently unbuyable.
- Missing dimensions, weight, or material detail.
- Retire-list words (`exquisite`, `timeless elegance`, `impeccable`, `nestled`).
- Missing or weak meta title and description.
- No mention of free worldwide DHL shipping on the page itself.

Report back the single biggest leak with evidence, and what fixing it involves.
Do not give me five problems ranked by severity — give me the one that is
costing the most, and say why you are confident it is that one.
