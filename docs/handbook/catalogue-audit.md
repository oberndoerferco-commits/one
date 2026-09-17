# Catalogue audit — product data completeness

Run 17 September 2026 against `5fae2a.myshopify.com`, all 269 products, by
`merchandising-manager`. Read-only: nothing was written to Shopify.

Method: `products(first: 250, after: $cursor)` paginated to exhaustion —
six pages, 269 unique product IDs, verified unique. Per-product row data is in
`docs/handbook/catalogue-audit.csv`.

---

## 1. The headline

**Not one product a first-time buyer could realistically risk money on has its
dimensions filled in.**

| ACTIVE price band | Products | With `custom.dimensions` |
| --- | --- | --- |
| €110–400 (entry) | 54 | **0 (0%)** |
| €400–2,500 (core) | 65 | 26 (40%) |
| €2,500+ (commission) | 15 | 5 (33%) |

The 31 ACTIVE products that do carry dimensions start at €825 and run to
€34,250. Every tray, every coaster set, every belt, every 3-place watch box,
every cap, every pair of sunglasses — the whole self-serve band — is blank.

That is exactly backwards. The commission tier has a person attached to it and
can answer a measurement question by email. The entry tier cannot; it has only
the page.

## 2. What the theme is actually doing about it

The brief assumed a blank metafield renders nothing. It does not. Reading
`theme/templates/product.json` (block `liquid_specs`, line 326), the
fallback branch is:

```liquid
{%- if dim == blank -%}<p>Interior and exterior measurements on request.</p>{%- endif -%}
```

So 103 of 134 ACTIVE product pages (77%) do not merely omit the measurements —
they print a sentence telling the buyer to write in and ask. On a €395 watch
box bought by a stranger, that is a request for correspondence placed exactly
where the buyer was about to decide. It is worse than silence.

Three fallbacks are firing across the live catalogue:

| Block | Fallback text fires when | ACTIVE pages affected |
| --- | --- | --- |
| `liquid_specs` — dimensions | `custom.dimensions` blank | 103 / 134 (77%) |
| `liquid_specs` — materials | `custom.materials_craft` blank | 80 / 134 (60%) |
| `liquid_specs` — what fits | `custom.what_fits` blank | 134 / 134 (100%) — renders nothing at all |
| `liquid_leadtime` | `custom.lead_time` blank | 134 / 134 (100%) |

The materials fallback is the same paragraph — "Cut, stitched and finished by
hand in ateliers around Milan…" — on 80 pages. The lead-time fallback is the
same paragraph on all 134. A buyer comparing two colourways sees identical
boilerplate and correctly concludes nobody has looked at either piece.

## 3. Metafield definitions in the `custom` namespace

`metafieldDefinitions(ownerType: PRODUCT, first: 100)` returns 50 definitions.
Forty-six are Shopify's own taxonomy (`shopify.*`) and one is
`mm-google-shopping.custom_product`. Only **four** are house-defined:

| Namespace | Key | Type | Pinned | Products populated | % of 269 |
| --- | --- | --- | --- | --- | --- |
| `custom` | `dimensions` | single_line_text_field | 1 | 33 | 12% |
| `custom` | `what_fits` | single_line_text_field | 2 | **0** | 0% |
| `custom` | `lead_time` | single_line_text_field | — | **0** | 0% |
| `custom` | `materials_craft` | multi_line_text_field | — | 68 | 25% |

Two notes the brief did not have:

- **`custom.materials_craft` exists and is 25% populated.** It is the richest
  house field on the store and it was not in the brief. It is also the one the
  theme leans on hardest — it carries the material paragraph on every product
  page. Filling it is worth more per page than `what_fits`.
- **`custom.siblings` is in use on 101 products but has no definition.** It is
  an undefined JSON metafield carrying colourway swatch data
  (`[{handle, colour, hex}, …]`). It works, but it is unmanaged: it will not
  appear in the admin metafield UI, cannot be validated, and nothing stops a
  handle in it going stale when a product is drafted. Worth defining properly.

There is **no** definition for weight, care, provenance or tannery. Points 1, 3
and 6 of the house's page standard have nowhere to live yet.

## 4. Completeness by product type

### ACTIVE products (134)

| Type | n | dimensions | what_fits | lead_time | materials_craft | SEO title | SEO desc | body copy | image | copy <200 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Watch boxes | 26 | 9 (35%) | 0 (0%) | 0 (0%) | 3 (12%) | 26 (100%) | 26 (100%) | 26 (100%) | 26 (100%) | 0 (0%) |
| Jewellery boxes | 11 | 4 (36%) | 0 (0%) | 0 (0%) | 8 (73%) | 11 (100%) | 11 (100%) | 11 (100%) | 11 (100%) | 0 (0%) |
| Trays | 9 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 7 (78%) | 9 (100%) | 9 (100%) | 9 (100%) | 8 (89%) |
| Wallets | 9 | 0 (0%) | 0 (0%) | 0 (0%) | 9 (100%) | 8 (89%) | 8 (89%) | 9 (100%) | 9 (100%) | 0 (0%) |
| Handbags | 24 | 10 (42%) | 0 (0%) | 0 (0%) | 4 (17%) | 24 (100%) | 24 (100%) | 24 (100%) | 24 (100%) | 0 (0%) |
| Bags & travel | 17 | 4 (24%) | 0 (0%) | 0 (0%) | 15 (88%) | 17 (100%) | 17 (100%) | 17 (100%) | 17 (100%) | 0 (0%) |
| Sunglasses | 11 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 11 (100%) | 11 (100%) | 11 (100%) | 11 (100%) | 0 (0%) |
| Apparel | 10 | 0 (0%) | 0 (0%) | 0 (0%) | 10 (100%) | 10 (100%) | 9 (90%) | 10 (100%) | 10 (100%) | 0 (0%) |
| Furniture | 8 | 4 (50%) | 0 (0%) | 0 (0%) | 4 (50%) | 8 (100%) | 8 (100%) | 8 (100%) | 8 (100%) | 0 (0%) |
| Other | 9 | 0 (0%) | 0 (0%) | 0 (0%) | 1 (11%) | 8 (89%) | 8 (89%) | 9 (100%) | 9 (100%) | 0 (0%) |
| **All** | **134** | **31 (23%)** | **0 (0%)** | **0 (0%)** | **54 (40%)** | **130 (97%)** | **131 (98%)** | **134 (100%)** | **134 (100%)** | **8 (6%)** |

### All products, ACTIVE + DRAFT (269)

| Type | n | dimensions | what_fits | lead_time | materials_craft | SEO title | SEO desc | body copy | image | copy <200 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Watch boxes | 28 | 9 (32%) | 0 (0%) | 0 (0%) | 3 (11%) | 28 (100%) | 28 (100%) | 28 (100%) | 28 (100%) | 0 (0%) |
| Jewellery boxes | 12 | 4 (33%) | 0 (0%) | 0 (0%) | 8 (67%) | 11 (92%) | 11 (92%) | 12 (100%) | 12 (100%) | 0 (0%) |
| Trays | 9 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 7 (78%) | 9 (100%) | 9 (100%) | 9 (100%) | 8 (89%) |
| Wallets | 14 | 0 (0%) | 0 (0%) | 0 (0%) | 9 (64%) | 8 (57%) | 8 (57%) | 14 (100%) | 14 (100%) | 0 (0%) |
| Handbags | 37 | 11 (30%) | 0 (0%) | 0 (0%) | 4 (11%) | 24 (65%) | 24 (65%) | 37 (100%) | 37 (100%) | 0 (0%) |
| Bags & travel | 33 | 5 (15%) | 0 (0%) | 0 (0%) | 15 (45%) | 18 (55%) | 18 (55%) | 33 (100%) | 33 (100%) | 0 (0%) |
| Jewellery | 80 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 33 (41%) | 33 (41%) | 80 (100%) | 80 (100%) | 31 (39%) |
| Sunglasses | 11 | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 11 (100%) | 11 (100%) | 11 (100%) | 11 (100%) | 0 (0%) |
| Apparel | 23 | 0 (0%) | 0 (0%) | 0 (0%) | 23 (100%) | 13 (57%) | 22 (96%) | 23 (100%) | 23 (100%) | 0 (0%) |
| Furniture | 8 | 4 (50%) | 0 (0%) | 0 (0%) | 4 (50%) | 8 (100%) | 8 (100%) | 8 (100%) | 8 (100%) | 0 (0%) |
| Other | 14 | 0 (0%) | 0 (0%) | 0 (0%) | 2 (14%) | 9 (64%) | 9 (64%) | 14 (100%) | 14 (100%) | 2 (14%) |
| **All** | **269** | **33 (12%)** | **0 (0%)** | **0 (0%)** | **68 (25%)** | **170 (63%)** | **181 (67%)** | **269 (100%)** | **269 (100%)** | **41 (15%)** |

Status split: **134 ACTIVE, 135 DRAFT, 0 archived.** Half the catalogue is
already invisible — which materially softens the "269 products is too many"
framing. The live storefront is 134 products, not 269.

## 5. Faults, named

### 5.1 Silent dead ends — ACTIVE, inventory 0, policy DENY

**Zero.** No ACTIVE product is unbuyable. This fault does not exist on the live
store and can be struck off the standing worry list.

Six products match the pattern, and all six are already DRAFT, so no client can
reach them:

| Product | Handle | Price |
| --- | --- | --- |
| Travel Watchbox | `leather-watchbox` | €189 |
| Leather Watch Roll | `red-leather-watch-roll` | €199 |
| The Mirror Handbag | `milano-handbag-blue` | €1,675 |
| 18k White Gold Diamond Bracelet | `18k-white-gold-diamond-bracelet` | €90,000 |
| Rubin Flower Necklace | `rubin-flower-necklace` | €0 |
| Chesterfield Sofa | `italian-leather-chesterfield-sofa-turquoise` | €0 |

If any of these are revived, the inventory policy must be changed at the same
time or they will publish as dead ends.

### 5.2 Inventory 0 but sellable — the page implies stock it does not have

17 ACTIVE products. These will take an order, but no page says *made to order*
or *pre-order*, and the generic lead-time paragraph does not say it either.

| Product | Price | Policy | Tracked |
| --- | --- | --- | --- |
| 8-Place XL Watch Box | €3,389 | CONTINUE | yes |
| Nabuk Leather Jewelry Box - Red | €1,930 | CONTINUE | yes |
| Weekend Bag | €1,950 | CONTINUE | yes |
| The Mirror Handbag - Nude | €1,675 | CONTINUE | yes |
| The Mirror Handbag - Lavender | €1,675 | CONTINUE | yes |
| Leather Belt Bag | €890 | CONTINUE | yes |
| BAG MODEL 017 - Pink | €825 | CONTINUE | yes |
| Blue Alligator Wallet | €765 | CONTINUE | yes |
| Crocodile Wallet - Cognac | €720 | CONTINUE | yes |
| T-Shirt OM / OBERNDÖRFER MILANO / Star patch / with Logo | €130 | CONTINUE | yes |
| Embroidered T-Shirt | €110 | CONTINUE | yes |
| Cotton Cap - Black / Black, Pink Logo / Leopard, Pink Logo | €125 | DENY | **no** |

The three caps are the sharper risk. Inventory is **untracked**, so the DENY
policy is inert and the store will sell them without limit against a recorded
stock of zero. That is an oversell waiting to happen on a piece with two
colourways that do hold stock — it looks like a settings slip, not a decision.

The five apparel lines are genuinely pre-order, and the ready-to-wear template
does handle it — but only for products tagged `preorder`. All five carry the
tag, so they are covered. The nine non-apparel items are not.

### 5.3 ACTIVE with no image

**Zero.** Every live product has at least one image; the ACTIVE median is 5.

### 5.4 ACTIVE with no SEO title (4)

- Yellow and Brown Leather Tray — `yellow-and-brown-leather-tray`
- White/Blue Leather Tray — `white-blue-leather-tray`
- Crocodile Passport Holder — `crocodile-passport-holder`
- Wine Holder Leather Box — `wine-holder-leather-box`

### 5.5 ACTIVE with no SEO description (3)

- Crocodile Passport Holder — `crocodile-passport-holder`
- Wine Holder Leather Box — `wine-holder-leather-box`
- T-Shirt OBERNDÖRFER MILANO — `chrome-t-shirt`

Crocodile Passport Holder and Wine Holder Leather Box are missing **both**. A
€720 crocodile passport holder is a specific, low-competition search term and
the page is not competing for it.

### 5.6 ACTIVE with body copy under 200 characters (8)

All eight are the leather trays, and they are the cheapest way into the house.

| Chars | Price | Product |
| --- | --- | --- |
| 181 | €129 | Red Leather Tray |
| 183 | €129 | Brown Leather Tray |
| 183 | €129 | Black Leather Tray |
| 184 | €129 | White/Blue Leather Tray |
| 187 | €129 | Dark Blue Leather Tray |
| 188 | €129 | Dark Green Leather Tray |
| 198 | €129 | Yellow and Brown Leather Tray |
| 198 | €129 | Dark Green and Brown Leather Tray |

The trays are also 0% on dimensions and 0% on `materials_craft`. They are the
thinnest pages in the catalogue attached to the most accessible price.

### 5.7 Retire-list words

**Zero in ACTIVE copy.** The live store is clean.

**40 DRAFT products** carry at least one, concentrated in the jewellery lines:
`exquisite` (22), `masterpiece` (20), `timeless elegance` (10),
`attention to detail` (7), `unparalleled` (4), `the perfect blend of` (3),
`a true celebration of` (3), `impeccable` (2),
`the finer things in life` (1). None must go live as written.

## 6. The twenty to fill first

Chosen on four tests: a price a stranger will risk on an unknown house
(€110–€800), photography that already exists, inventory that can actually be
sold today, and a search term a real person types.

Every one of these is ACTIVE, has stock, has at least three images, and has
zero of the three spec metafields filled.

| # | Product | Price | Stock | Imgs | Missing | Why this one |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Crocodile Wallet - Black/Khaki | €720 | 2 | 10 | dim, fits, lead | The €720 wallet the plan is arguing about. Deepest photography on the store; `materials_craft` already written; CITES story is real. |
| 2 | 3-Place Watch Box - Grey | €395 | 2 | 9 | dim, fits, lead, mat | "leather watch box" is the house's strongest search term and 39 SKUs sit behind it. Cheapest honest entry to the category. |
| 3 | 3-Place Watch Box - Dark Green | €395 | 2 | 8 | dim, fits, lead, mat | Same family, stock in hand, second-best imagery. |
| 4 | Classic Leather Belt - Black, Round Buckle | €190 | 1 | 9 | dim, fits, lead, mat | Nine images at €190. "Italian leather belt" is high-intent and the price clears the risk bar outright. |
| 5 | Crocodile Wallet - Chocolate | €720 | 1 | 7 | dim, fits, lead | Best-selling colour in the category generally; copy already 653 chars. |
| 6 | Watch & Jewelry Box - Brown | €619 | 1 | 8 | dim, fits, lead, mat | The combined box answers a question buyers actually ask — watches *and* jewellery. `what_fits` matters more here than anywhere. |
| 7 | Beauty Bag | €320 | 2 | 7 | dim, fits, lead, mat | In stock ×2, seven images, and the shortest real copy in the band (288 chars) — largest gain per hour. |
| 8 | Brown Leather Tray | €129 | 3 | 3 | dim, fits, lead, mat | Most stock of any piece on the store (3). Lowest price. Copy is 183 chars. "Leather valet tray" is a genuine gift search. |
| 9 | Dark Blue Leather Tray | €129 | 3 | 3 | dim, fits, lead, mat | Same, 3 in stock, 187 chars. |
| 10 | 3-Place Watch Box - Blue | €395 | 2 | 7 | dim, fits, lead, mat | Third colourway; the family carries 12 units of stock between six SKUs. |
| 11 | Crocodile Passport Holder | €720 | 1 | 6 | dim, fits, lead, **SEO title + desc** | The only piece on this list missing both SEO fields. Specific, low-competition term. Fixing it is cheap. |
| 12 | Classic Leather Belt - Black, Squared Buckle | €190 | 1 | 9 | dim, fits, lead, mat | Nine images; buckle choice is the whole decision, so dimensions and width are the deciding fact. |
| 13 | Watch & Jewelry Box - Orange | €619 | 1 | 8 | dim, fits, lead, mat | Second colourway of a strong model, eight images. |
| 14 | Brown Leather Coaster Set | €145 | 1 | 4 | dim, fits, lead, mat | Gifting at €145. "Leather coasters" converts on specification — diameter is the entire question. |
| 15 | Black and Yellow Leather Tray | €129 | 2 | 3 | dim, fits, lead, mat | Only tray with copy over 200 chars (213); use it as the pattern for the other eight. |
| 16 | Cotton Cap - Leopard, Black Logo | €125 | 2 | 3 | dim/fit, lead | In stock, `materials_craft` written, 557 chars of copy. Needs a fit note, not a rewrite. |
| 17 | Black Leather Coaster Set | €145 | 1 | 4 | dim, fits, lead, mat | Sibling of #14; one write serves four SKUs. |
| 18 | Black Leather Pouf | €595 | 1 | 3 | dim, fits, lead, mat | The only furniture a stranger can buy without a conversation. Dimensions are non-negotiable for furniture. |
| 19 | Mini Crochet Handbag - Multicolor Print | €279 | 1 | 5 | dim, fits, lead, mat | Distinctive, photographs well, and the craft story is different from the leather lines. |
| 20 | Crocodile Wallet - Dark Blue | €720 | 1 | 8 | dim, fits, lead | Completes the wallet set that carries the house's most defensible material claim. |

### Why this list is cheaper than it looks

Seventeen of the twenty belong to sibling families linked by
`custom.siblings`. Writing the spec once and replicating across the family
reaches far more of the store than twenty pages:

| Family | ACTIVE SKUs | Units in stock |
| --- | --- | --- |
| Leather Tray | 9 | 19 |
| Crocodile Wallet | 7 | 7 |
| 3-Place Watch Box | 6 | 12 |
| Mini Crochet Handbag | 6 | 6 |
| Cotton Cap | 5 | 4 |
| Classic Leather Belt | 4 | 4 |
| Leather Coaster Set | 4 | 4 |
| Leather Pouf | 4 | 4 |
| Watch & Jewelry Box | 3 | 3 |

**48 ACTIVE SKUs, 63 sellable units** — 36% of the live catalogue — reachable
from twenty pieces of writing.

### Deliberately excluded

- **Sunglasses (11, €325–425).** Price is right, but only two images each. The
  photography test fails. Worth a reshoot brief to `art-director` before copy.
- **Crochet Handbag, full size (5 ACTIVE, €329).** "Crochet handbag" is a
  crowded low-price search where an unknown house at €329 is hard to justify.
  The €279 Mini is on the list as the one test of the line.
- **8-Place and Leather Watch Boxes (18 ACTIVE, €1,110–1,490).** Above the risk
  band for a first order. They are the right *second* wave, once the 3-place
  box has proved the category.
- **All 135 DRAFT products.** No client can see them; they cost nothing to
  leave alone, and 40 of them need retire-list words removed before they could
  publish anyway.

## 7. What to do about it, in order

1. **Fill `custom.dimensions` on the twenty above.** It removes "measurements
   on request" from the pages most likely to make the first sale. The atelier
   must supply the measurements; `atelier-director` verifies.
2. **Fill `custom.lead_time` on the nine non-apparel zero-stock items in
   §5.2** so the page stops implying stock it has not got.
3. **Fix the three caps' inventory tracking.** Untracked with zero recorded
   stock is an oversell risk, not a merchandising choice. → `ecommerce-manager`
4. **Rewrite the nine tray descriptions.** Cheapest piece, thinnest page,
   19 units in stock. → `editorial-director`, then `creative-director`
5. **Add the four missing SEO titles and three missing descriptions.** Seven
   fields, an hour's work.
6. **Define `custom.siblings` properly, and add definitions for weight and
   care.** Points 3 and 6 of the page standard have nowhere to live.

Nothing in this audit changes a price, and nothing was written to Shopify.
Any copy produced from it passes `creative-director` before it ships, and any
material claim passes `atelier-director`.
