# Oberndörfer Milano — the identity, in one page

Read this before touching the Claude theme (id 204228231493). It is the result of the
4 September 2026 comparison against Goyard, Moynat, Valextra, Serapian, Métier, Bennett
Winch, Globe-Trotter, Au Départ, Connolly, Ettinger and Brunello Cucinelli at desktop width,
and it is what every page of the theme now follows. Scripts: `scripts/house-style-pass*.py`
(story pages) and `scripts/identity-pass.py` (site-wide); both are re-runnable.

## What the house is

An independent house making trunks, bags, small leather goods and furniture by hand in
ateliers around Milan, to order, in small numbers, with one public interior (Miramare The
Palace, Sanremo) and one place in New York (Trax NYC). The one-line version, used in the
home hero: **Trunks, bags and objects for the home. Made by hand, around Milan.**

## What the field taught us

- Trunk houses (Goyard, Moynat, Globe-Trotter, Au Départ) open on one full-bleed photograph
  with a tracked eyebrow, a serif line and an underlined link, bottom left, in white.
- The best sites use one photographic mood (Valextra: amber interiors; Au Départ: sunlit
  Paris; Métier: a yellow set) and never a low-resolution file.
- Navigation is small tracked capitals; actions are underlined text, not boxes; a filled
  button appears only where money changes hands.
- Nobody explains themselves in adjectives. Métier: "Our Story" and three plain paragraphs.
  Globe-Trotter: eyebrow, serif head, one paragraph of fact.

## Visual rules

| Element | Rule |
| --- | --- |
| Ground | `#eeede8` page, `#e5e0d7` band, `#1c1714` ink, `#4a3f35` saddle (filled buttons), `#d3cabc` lines, `#7a2e2b` accent (sale badge). Riviera blue `#cfdbe3` on Art of Living only. |
| Type | Marcellus for every heading; Inter for body, eyebrows, navigation. |
| Hero (every page) | Full-bleed photograph ≥1800px, ink gradient from the bottom (`#1c171499`), bottom-left: eyebrow in `#e5e0d7`, Marcellus 40px title in `#fbf9f6`, optional one-line dek, optional underlined link in white. The title is the page's h1. |
| Eyebrow | Inter 12px, capitals, loose tracking. Names the page, a place, a material or a chapter. |
| Statement | Marcellus 32px, centred, one or two lines, once per section. |
| Chapter head | Marcellus 32px (h3 preset), sentence case, a sentence with a claim in it. |
| Body | Inter 16px, left beside a photograph, centred only under a statement. |
| Actions | One filled saddle button per page (Add to cart, Send, Begin a commission). Everything else is an underlined text link. |
| Cards | Eyebrow shows the family (Trunks, Bags…) in mixed grids; on a collection page only the exceptions: Made to order, Limited edition, Exotic leather. |
| Photographs | Product on the sand ground; places and hands in daylight. No file narrower than 1800px in a hero or a full-width row. Low-res files still in use are listed at the end. |
| Navigation | 12px tracked capitals; logo centred. |

## Writing rules

1. A heading is a sentence with a claim, in sentence case. Labels live in the eyebrow.
2. Second person where the reader acts (Bespoke, Care); "we" for what the house does; never the brand in the third person.
3. Concrete nouns and numbers instead of adjectives: "4–6 weeks", "solid brass galvanised in gold", "nothing is cut until you have approved it".
4. Say what happens next and what it costs. Process, lead time, returns, repairs.
5. Heads of seven words or fewer; paragraphs of fifty words or fewer; one idea each. No semicolons, no dash-lists inside sentences.
6. Captions say what is in the photograph and nothing more.

## Page by page (all in the Claude theme)

- Home: eyebrow / "Made by hand, around Milan." / Discover the collections. "Collections" (was SHOP BY CATEGORY). One filled button: Begin a commission.
- About: hero on the stacked cases (was a 780px model shot). "Leather, learned at the source." Captions under the three photographs.
- Bespoke: "Made to your measure." with a line and "How a commission works". Four-step process. One filled button: Send.
- Art of Living: "Furniture, made the way we make a trunk." / The Miramare commission.
- Materials, Packaging, Custom, Contact, Leather Care: same hero grammar; Contact hero on the atelier bench (was a 1232px file).

## Collection and product pages (commerce pass, 5 September)

- Collection hero: the same section as the home hero, with a photograph of the family
  (Bags: ostrich case detail; Trunks: black case with gold hardware; Travel: the Miramare
  terrace; Home accessories: the lobby ensemble; Small leather goods: brass fittings;
  Sunglasses: the polishing bench). Eyebrow "Collection", the collection title as h1, then
  the collection's `custom.editorial_line` metafield or its description as one line.
  A text block's dynamic source may carry only one Liquid filter, so the line is a
  custom-liquid block.
- Grid: four across on desktop, three between 750 and 989px, two on the phone. Horizon has
  no four-column option, so a `<style>` block in the hero pins `--product-grid-columns-desktop`.
  Cards sit straight on the page ground: no card background, no border, no quick-add icon,
  square images, Marcellus 18px title, Inter 14px price, the exception eyebrow above the image.
- Collection close: a band with "Looking for a leather, a colour or a size you don't see?
  Most of what we make is made to order." and the link "Write to the atelier".
- Product page: eyebrow (family and leather, or "Limited edition"), Marcellus title, price
  in body type, variant picker, quantity and one filled "Add to cart", an atelier line, the
  description, then six accordions from existing data only: Details, Delivery, Made to order,
  Repairs, Care, Packaging. A "Made by hand" chapter follows the product; "You may also like"
  shows four pieces in the same card style.

## Files that are still too small (replace when new photographs exist)

`17.jpg` (780px, the model in the garden — a good picture, needs the original), `bag.jpg`
(772px), `IMG_0815.jpg` (1170px), `IMG_3640.jpg` (1232px), `oberndoerfer-hero-trunk-bag-amalfi.jpg`
(900px), `oberndoerfer-miramare-arch-terrace.jpg` (1001px), the three `oberndoerfer-ig-*` files.

## Do not

Change the home hero photograph; apply the proposed menu; merge colour families; touch the
journal drafts. The owner publishes the theme.
