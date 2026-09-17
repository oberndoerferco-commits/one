# Theme brief — product page Details row

**Paste this whole file into the website theme chat.** It is written to stand on
its own; it assumes no knowledge of any other conversation.

Written 17 September 2026 by `ecommerce-manager`, from a read-only audit of all
269 products and the live theme. Every figure below was measured, not estimated.

---

## The theme

Live theme: **"NEW WEBSITE BUG fix 7"**, id `206519796037`, Horizon-based.
Template: `templates/product.json`.

## The block to change

Path inside the template:

```
sections
└ main
  └ blocks / product-details
    └ blocks / accordion_info
      └ blocks / row_details
        └ blocks / liquid        ← this one, type: custom-liquid
```

It is the custom-Liquid block inside the **Details** row of the product
accordion. Its current content, verbatim:

```liquid
{%- assign mat = product.metafields.custom.materials_craft.value -%}
{%- assign dim = product.metafields.custom.dimensions.value -%}
{%- assign fits = product.metafields.custom.what_fits.value -%}
<div style="font-size:0.9375rem;line-height:1.6">
{%- if mat != blank -%}<p>{{ mat }}</p>
{%- else -%}<p>Cut, stitched and finished by hand in ateliers around Milan. Full-grain hides from family tanneries in Italy, France and Germany; solid brass hardware.</p>{%- endif -%}
{%- if dim != blank -%}<p><strong>Dimensions</strong><br>{{ dim }}</p>{%- endif -%}
{%- if fits != blank -%}<p><strong>What fits inside</strong><br>{{ fits }}</p>{%- endif -%}
{%- if dim == blank -%}<p>Interior and exterior measurements on request.</p>{%- endif -%}
</div>
```

## What is wrong with it

**One line, the last one.** When `custom.dimensions` is empty, the page prints:

> Interior and exterior measurements on request.

That fires on **103 of the 134 active products — 77%**. And it fires hardest at
the cheap end, where it does the most damage:

| Price band | Active products | Dimensions filled |
| --- | --- | --- |
| €110–400 | 54 | **0** |
| €400–2,500 | 65 | 26 |
| €2,500+ | 15 | 5 |

Not one product under €400 has dimensions. So every tray, every 3-place watch
box, every cap and every pair of sunglasses asks the buyer to start a
correspondence — at exactly the moment they opened *Details* to find out
whether the thing fits.

The €2,500+ pieces have a person attached and can answer by email. The €129
tray has only the page.

Secondary, same block: when `custom.materials_craft` is empty the fallback
paragraph prints on **80 of 134 pages**. Someone comparing two colourways of
the same box reads identical boilerplate twice and reasonably concludes nobody
has looked at either piece.

## The change

Replace the block's content with this. The only difference is that the last
conditional is gone, and the materials fallback is narrowed so it stops
claiming tanneries for pieces it knows nothing about.

```liquid
{%- assign mat = product.metafields.custom.materials_craft.value -%}
{%- assign dim = product.metafields.custom.dimensions.value -%}
{%- assign fits = product.metafields.custom.what_fits.value -%}
<div style="font-size:0.9375rem;line-height:1.6">
{%- if mat != blank -%}<p>{{ mat }}</p>
{%- else -%}<p>Cut, stitched and finished by hand in ateliers around Milan.</p>{%- endif -%}
{%- if dim != blank -%}<p><strong>Dimensions</strong><br>{{ dim }}</p>{%- endif -%}
{%- if fits != blank -%}<p><strong>What fits inside</strong><br>{{ fits }}</p>{%- endif -%}
</div>
```

Silence is better than an instruction to go away. A page that simply does not
mention measurements reads as incomplete; a page that says *measurements on
request* reads as unwilling.

## Two notes on the shortened fallback

The line being cut — *Full-grain hides from family tanneries in Italy, France
and Germany; solid brass hardware* — is a material claim, and it currently
prints on 80 pages regardless of what the piece is actually made of. Some of
those are Nabuk, some sheep leather, some Alcantara-lined, some acetate
sunglasses with no hide in them at all. It should be earned per product in
`custom.materials_craft`, not asserted by default.

## How to check it worked

1. Open any **leather tray** product page (e.g. `/products/brown-leather-tray`)
   and expand **Details**. The line *Interior and exterior measurements on
   request* should be gone, and the paragraph should end at "ateliers around
   Milan."
2. Open **The Mirror Handbag - Black** (`/products/black-mirror-handbag-italian-leather`),
   which does have dimensions filled. The **Dimensions** line should still show
   `L 18.5 cm × W 7 cm × H 11 cm (7.3 × 2.8 × 4.3 in)`.
3. Check one sunglasses page to confirm the tannery sentence no longer appears.

## The real fix is not a theme change

Removing the line stops the page repelling people. It does not put the
measurements there.

**103 active products need their `custom.dimensions` filled**, and no agent can
supply those — someone has to measure the pieces. The twenty worth doing first
are ranked in `docs/handbook/catalogue-audit.md`, chosen on price a stranger
will risk, photography that already exists, and stock that can actually ship:

1. Crocodile Wallet - Black/Khaki — €720
2. 3-Place Watch Box - Grey — €395
3. 3-Place Watch Box - Dark Green — €395
4. Classic Leather Belt - Black, Round Buckle — €190
5. Crocodile Wallet - Chocolate — €720
6. Watch & Jewelry Box - Brown — €619
7. Beauty Bag — €320
8. Brown Leather Tray — €129
9. Dark Blue Leather Tray — €129

Fill `custom.dimensions` and `custom.materials_craft` on those nine and the
block starts earning its place on the pages most likely to make the first sale.

## Not in this brief

Two faults were found that are **not** theme problems and should not be fixed
here:

- **Three caps will oversell.** Cotton Cap in Black, Black/Pink Logo and
  Leopard/Pink Logo have inventory policy DENY but inventory **untracked**, so
  the limit is inert and the store will accept unlimited orders against a
  recorded stock of zero. That is a product settings fix, not a theme fix.
- **Missing SEO fields.** Crocodile Passport Holder and Wine Holder Leather Box
  have neither SEO title nor description; Yellow and Brown Leather Tray,
  White/Blue Leather Tray and the chrome T-Shirt are missing one or the other.
  Also product settings.
