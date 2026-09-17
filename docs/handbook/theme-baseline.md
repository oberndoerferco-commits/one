# Theme baseline

Pulled 2026-09-17. Read-only sync: nothing was written to Shopify.

## The live theme

| Field | Value |
| --- | --- |
| Name | NEW WEBSITE BUG fix 7 |
| ID | `gid://shopify/OnlineStoreTheme/206519796037` |
| Role | MAIN (published, live on the storefront) |
| Theme store ID | 2481 (Horizon) |
| Preview prefix | `/t/36` |
| Created | 2026-09-16T17:09:07Z |
| Last updated | 2026-09-16T17:55:54Z |
| Files | 519 |

The theme our working copy was taken from — "Claude", id `204228231493` — no longer exists. `theme(id:)` returns "Theme does not exist". There is no unpublished Claude theme to write to at present.

### All themes in the store (17)

| Name | ID | Role | Base | Updated |
| --- | --- | --- | --- | --- |
| Dawn | 149715059013 | UNPUBLISHED | Dawn (887) | 2026-03-03 |
| Current Dawn | 171188977989 | UNPUBLISHED | Dawn (887) | 2026-09-14 |
| Dawn new | 174055031109 | UNPUBLISHED | Dawn (887) | 2026-09-14 |
| AVADA Assets - DO NOT REMOVE | 175090172229 | UNPUBLISHED | none | 2025-12-30 |
| New | 181305573701 | UNPUBLISHED | Dawn (887) | 2026-09-14 |
| Update Miramare | 188915286341 | UNPUBLISHED | Dawn (887) | 2026-09-14 |
| Atelier | 192212861253 | UNPUBLISHED | Atelier (3621) | 2026-02-20 |
| Horizon | 192221872453 | UNPUBLISHED | Horizon (2481) | 2026-03-03 |
| NEW WEBSITE 1 | 194535817541 | UNPUBLISHED | Horizon (2481) | 2026-03-03 |
| Updated copy of NEW WEBSITE 1 | 195770745157 | UNPUBLISHED | Horizon (2481) | 2026-03-03 |
| NEW WEBSITE BUG FIX | 195782443333 | UNPUBLISHED | Horizon (2481) | 2026-04-04 |
| NEW WEBSITE BUG FIX 1.1 | 197755699525 | UNPUBLISHED | Horizon (2481) | 2026-07-18 |
| NEW WEBSITE BUG FIX 1.2 | 202859512133 | UNPUBLISHED | Horizon (2481) | 2026-09-08 |
| OBERNDÖRFER MILANO 4 | 205995508037 | UNPUBLISHED | Horizon (2481) | 2026-09-14 |
| OBERNDÖRFER MILANO 5 | 205996556613 | UNPUBLISHED | Horizon (2481) | 2026-09-14 |
| NEW WEBSITE BUG fix 3 | 206153285957 | UNPUBLISHED | Horizon (2481) | 2026-09-11 |
| NEW WEBSITE BUG fix 7 | 206519796037 | **MAIN** | Horizon (2481) | 2026-09-16 |

## What was pulled

`theme/MANIFEST.txt` holds the full 519-file inventory (`filename<TAB>size`, sorted).

Downloaded to `theme/`: all 34 JSON templates plus `config/settings_data.json` and `config/settings_schema.json`.

### Byte-count verification

The Admin API returns JSON template bodies **pretty-printed with two-space indent**. The `size` and `checksumMd5` it reports describe the *stored* bytes. Where the theme editor last saved a file it is stored minified, so the returned body is larger than the reported size and the MD5 does not match. Where a file was last written pretty-printed the body round-trips exactly.

Files whose bytes matched `size` and `checksumMd5` exactly:

- `config/settings_schema.json` (49893 bytes)
- `templates/page.materials-craftsmanship.json` (50221 bytes)
- `templates/page.json` (1713 bytes)
- `templates/page.the-art-of-packaging.json` (29810 bytes)
- `templates/product.json` (38851 bytes)
- `templates/product.ready-to-wear.json` (39947 bytes)
- `templates/product.sunglasses.json` (28159 bytes)

The remaining 29 files came back pretty-printed and are therefore larger on disk than the reported `size`. Each was parsed after comment-stripping and is structurally valid; no file was truncated. This is a serialisation difference, not data loss.

`templates/product.json` — the file this sync was chasing — matched byte for byte at 38,851 bytes, MD5 `6f571c2b87faa4177f84e1b7744658b1` verified against the API checksum.

## Product template — `templates/product.json`

### Section and block structure (live)

- **`main`** — section type `product-information`
  - `media-gallery` — `_product-media-gallery`
  - `product-details` — `_product-details`
    - `breadcrumbs_pdp` — `_breadcrumbs`
    - `eyebrow_pdp` — `custom-liquid`
    - `group_icgrde` — `group`
      - `text_xrnftG` — `text`
      - `price_tVjtKg` — `price`
    - `divider_VJhene` — `_divider`
    - `variant_picker_R3rGDr` — `variant-picker`
    - `buy_buttons_eYQEYi` — `buy-buttons`
      - `quantity` — `quantity`
      - `add-to-cart` — `add-to-cart`
      - `accelerated-checkout` — `accelerated-checkout`
    - `custom_liquid_atelier` — `custom-liquid`
    - `text_aEtTtq` — `text`
    - `accordion_info` — `accordion`
      - `row_details` — `_accordion-row`
        - `liquid` — `custom-liquid`
      - `row_delivery` — `_accordion-row`
        - `text_care` — `text`
      - `row_made` — `_accordion-row`
        - `liquid` — `custom-liquid`
      - `row_repairs` — `_accordion-row`
        - `text_care` — `text`
      - `row_care` — `_accordion-row`
        - `text_care` — `text`
      - `row_packaging` — `_accordion-row`
        - `text_gifting` — `text`
        - `liquid_packaging` — `custom-liquid`
- **`section_pdp_chapter`** — section type `media-with-content`
  - `media` — `_media-without-appearance`
  - `content` — `_content-without-appearance`
    - `group_craftGrp` — `group`
      - `eyebrow` — `text`
      - `text_craftHead` — `text`
      - `text_craftBody` — `text`
      - `link` — `button`
- **`product_recommendations_qggXJq`** — section type `oberndoerfer-recommendations`
  - `text_cbcgyb` — `text`

## Index template — `templates/index.json`

- **`hero_jVaWmY`** — section type `hero`
- **`collection_list_4pRwyd`** — section type `collection-list`
  - `group_AMj3LX` — `group`
    - `text_qfy38i` — `text`
- **`section_NCF7ci`** — section type `section`
  - `text_CGJkVK` — `text`
  - `text_UTmWem` — `text`
- **`hero_7cpgjh`** — section type `hero`
- **`product_list_NGhceV`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_button_U8EFmC` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_eR7d3x` — `_product-card-gallery`
    - `product_title_cexACD` — `product-title`
    - `price_p9h93w` — `price`
- **`product_list_kLLn8d`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_button_J4f7tL` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_q63Brm` — `_product-card-gallery`
    - `product_title_RQAJtB` — `product-title`
    - `price_DiaDML` — `price`
- **`blocks_UCnUHd`** — section type `_blocks`
  - `ai_gen_block_56185bb_dmyx4y` — `ai_gen_block_56185bb`
- **`section_PaekVn`** — section type `section`
  - `group_ee6M9F` — `group`
    - `group_kmUNxK` — `group`
      - `text_hYWtWG` — `text`
      - `text_AbYYDL` — `text`
    - `group_aKUPfn` — `group`
      - `button_pMdzD9` — `button`
  - `comparison_slider_AhJtCm` — `comparison-slider`
- **`product_list_mXdThg`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_text_LCLm7y` — `_product-list-text`
    - `product_list_button_z4yY49` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_q99QHM` — `_product-card-gallery`
    - `product_title_86hHGr` — `product-title`
    - `price_6nPQrh` — `price`
- **`divider_pUrTm9`** — section type `divider`
- **`media_with_content_REm8Na`** — section type `media-with-content`
  - `media` — `_media-without-appearance`
  - `content` — `_content-without-appearance`
    - `text_RpcapG` — `text`
    - `group_iafeWn` — `group`
      - `text_xedkEp` — `text`
      - `text_VFtHNK` — `text`
- **`media_with_content_te4pnz`** — section type `media-with-content`
  - `media` — `_media-without-appearance`
  - `content` — `_content-without-appearance`
    - `text_fWbJyR` — `text`
    - `group_q6Jtcr` — `group`
      - `text_haMmzt` — `text`
      - `text_R9PGRG` — `text`
    - `button_NYt8Pp` — `button`
- **`product_list_yVwMwY`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_button_7Xpwhg` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_BEAce3` — `_product-card-gallery`
    - `product_title_xr4pk8` — `product-title`
    - `price_naTf4Y` — `price`
- **`divider_EH7QRt`** — section type `divider`
- **`section_GK4wDR`** — section type `section`
  - `text_fyqreA` — `text`
  - `text_BihccN` — `text`
  - `button_RfBTpT` — `button`
- **`hero_f7abBH`** — section type `hero`
  - `text_bfxnEm` — `text`
  - `text_kjQrdn` — `text`
- **`product_list_aYnwwq`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_text_UrjjwL` — `_product-list-text`
    - `product_list_button_yG8drm` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_nmc3ip` — `_product-card-gallery`
    - `product_title_RgmLVg` — `product-title`
    - `price_Rbp8Xt` — `price`
- **`section_tr9CJe`** — section type `section`
  - `text_PPTP9J` — `text`
  - `text_fRcfLU` — `text`
- **`hero_nYfTwM`** — section type `hero`
- **`product_list_7DKRaN`** — section type `product-list`
  - `static-header` — `_product-list-content`
    - `product_list_text_xcUK7z` — `_product-list-text`
    - `product_list_button_kVp9Py` — `_product-list-button`
  - `static-product-card` — `_product-card`
    - `product_card_gallery_afpLWz` — `_product-card-gallery`
    - `product_title_EC6B7a` — `product-title`
    - `price_mPVMGB` — `price`
- **`section_M8B9qT`** — section type `section`
  - `group_gx6VCY` — `group`
    - `icon_K6V37H` — `icon`
    - `group_g43HyG` — `group`
      - `text_6pYzpC` — `text`
      - `text_AFybWJ` — `text`
  - `group_h4WHUt` — `group`
    - `icon_4Aq4Ct` — `icon`
    - `group_B3hJCW` — `group`
      - `text_8JNP4n` — `text`
      - `text_LWwGLH` — `text`
  - `group_JM6c4a` — `group`
    - `icon_7QPVBM` — `icon`
    - `group_AydCLT` — `group`
      - `text_y3qQXc` — `text`
      - `text_rbMHBf` — `text`

## Collection template — `templates/collection.json`

- **`section`** — section type `section`
  - `eyebrow` — `text`
  - `title` — `text`
  - `line` — `custom-liquid`
  - `css` — `custom-liquid`
- **`section_editorial`** — section type `section`
  - `liquid_editorial` — `custom-liquid`
- **`main`** — section type `main-collection`
  - `filters` — `filters`
  - `product-card` — `_product-card`
    - `card_eyebrow` — `custom-liquid`
    - `card-gallery` — `_product-card-gallery`
    - `product_title_4nY4eT` — `product-title`
    - `price_EzJzMm` — `price`
    - `swatches_card` — `swatches`

## Diff against the stale working copy

The old copy is commit `3c9a2ca` (`HEAD`). It held 14 files; the live theme has 519, of which 36 were pulled here. `theme/templates/page.art-of-living.BEFORE.json` is ours alone — a local snapshot, not a live theme file — and was left untouched.

### Files that existed locally and changed

| File | Old bytes | New bytes (as returned) | Live stored size |
| --- | --- | --- | --- |
| `config/settings_data.json` | 9993 | 9764 | 7919 |
| `templates/collection.json` | 9641 | 11430 | 7283 |
| `templates/index.json` | 75584 | 108331 | 64051 |
| `templates/list-collections.json` | 11802 | 11804 | 6703 |
| `templates/page.about-us.json` | 62306 | 40335 | 24877 |
| `templates/page.art-of-living.json` | 40026 | 30740 | 20565 |
| `templates/page.bespoke.json` | 85624 | 68036 | 41509 |
| `templates/page.contact.json` | 5749 | 5748 | 3488 |
| `templates/page.custom-limited-editions.json` | 46870 | 24987 | 16331 |
| `templates/page.faq.json` | 21060 | 20470 | 11648 |
| `templates/page.leather-care.json` | 32472 | 32483 | 19281 |
| `templates/page.materials-craftsmanship.json` | 24560 | 50221 | 50221 |
| `templates/product.json` | 32812 | 38851 | 38851 |

### Files pulled that we never had

- `config/settings_schema.json` (49893 bytes stored)
- `templates/404.json` (5104 bytes stored)
- `templates/article.json` (1494 bytes stored)
- `templates/blog.json` (1652 bytes stored)
- `templates/cart.json` (4710 bytes stored)
- `templates/collection.bags.json` (5399 bytes stored)
- `templates/collection.collections-2.json` (5433 bytes stored)
- `templates/collection.featured-products.json` (5415 bytes stored)
- `templates/collection.home-accessories.json` (5415 bytes stored)
- `templates/collection.new-in.json` (5425 bytes stored)
- `templates/collection.oberndoerfer-traxnyc.json` (5436 bytes stored)
- `templates/collection.oberndorfer-x-trax-nyc.json` (5436 bytes stored)
- `templates/collection.ready-to-wear.json` (5011 bytes stored)
- `templates/collection.small-leather-goods.json` (5427 bytes stored)
- `templates/collection.sunglasses.json` (3122 bytes stored)
- `templates/collection.travel.json` (5459 bytes stored)
- `templates/collection.trunks.json` (5425 bytes stored)
- `templates/page.json` (1713 bytes stored)
- `templates/page.the-art-of-packaging.json` (29810 bytes stored)
- `templates/password.json` (2420 bytes stored)
- `templates/product.ready-to-wear.json` (39947 bytes stored)
- `templates/product.sunglasses.json` (28159 bytes stored)
- `templates/search.json` (3121 bytes stored)

## `templates/product.json` — block-level diff of the `main` section

Section type is unchanged: `product-information`. Top-level block order is unchanged: `media-gallery`, then `product-details`. All movement is inside `product-details`.

### `product-details` child order

Was:

```
breadcrumbs_pdp
group_icgrde
divider_VJhene
variant_picker_R3rGDr
buy_buttons_eYQEYi
group_trust_signals
text_aEtTtq
liquid_specs
accordion_info
liquid_packaging
```

Now:

```
breadcrumbs_pdp
eyebrow_pdp
group_icgrde
divider_VJhene
variant_picker_R3rGDr
buy_buttons_eYQEYi
custom_liquid_atelier
text_aEtTtq
accordion_info
```

### Removed (12)

- `/product-details/accordion_info/row_delivery/text_delivery` — `text`
- `/product-details/accordion_info/row_gifting` — `_accordion-row`
- `/product-details/accordion_info/row_gifting/text_gifting` — `text`
- `/product-details/accordion_info/row_materials` — `_accordion-row`
- `/product-details/accordion_info/row_materials/text_materials` — `text`
- `/product-details/group_trust_signals` — `group`
- `/product-details/group_trust_signals/divider_trust_bottom` — `_divider`
- `/product-details/group_trust_signals/divider_trust_top` — `_divider`
- `/product-details/group_trust_signals/liquid_leadtime` — `custom-liquid`
- `/product-details/group_trust_signals/text_trust_badges` — `text`
- `/product-details/liquid_packaging` — `custom-liquid`
- `/product-details/liquid_specs` — `custom-liquid`

### Added (12)

- `/product-details/accordion_info/row_delivery/text_care` — `text`
- `/product-details/accordion_info/row_details` — `_accordion-row`
- `/product-details/accordion_info/row_details/liquid` — `custom-liquid`
- `/product-details/accordion_info/row_made` — `_accordion-row`
- `/product-details/accordion_info/row_made/liquid` — `custom-liquid`
- `/product-details/accordion_info/row_packaging` — `_accordion-row`
- `/product-details/accordion_info/row_packaging/liquid_packaging` — `custom-liquid`
- `/product-details/accordion_info/row_packaging/text_gifting` — `text`
- `/product-details/accordion_info/row_repairs` — `_accordion-row`
- `/product-details/accordion_info/row_repairs/text_care` — `text`
- `/product-details/custom_liquid_atelier` — `custom-liquid`
- `/product-details/eyebrow_pdp` — `custom-liquid`

No block kept its id and changed type. Nothing was reordered in place; the accordion was rebuilt from four rows to six.

### Accordion rows, old and new

| | Rows, in order |
| --- | --- |
| Was | Materials & Craft (`row_materials`), Care (`row_care`), Delivery (`row_delivery`), Gifting (`row_gifting`) |
| Now | Details (`row_details`), Delivery and returns (`row_delivery`), Made to order and personalisation (`row_made`), Repairs (`row_repairs`), Care (`row_care`), Packaging and gifts (`row_packaging`) |

### Sections added to the product template

| Section | Was | Now |
| --- | --- | --- |
| `main` | `product-information` | `product-information` |
| `section_pdp_chapter` | absent | `media-with-content` |
| `product_recommendations_qggXJq` | `product-recommendations` | `oberndoerfer-recommendations` |

Template order was `main, product_recommendations_qggXJq`; it is now `main, section_pdp_chapter, product_recommendations_qggXJq`.

## App residue in the theme

Files in the manifest that were put there by an app, not by the theme:

| File | Size | Source |
| --- | --- | --- |
| `snippets/avada-seo.liquid` | 296 | AVADA SEO Suite |
| `snippets/avada-seo-status.liquid` | 36 | AVADA SEO Suite |
| `snippets/avada-seo-other.liquid` | 0 | AVADA SEO Suite — empty file |
| `snippets/pagefly-main-js.liquid` | 4,328 | PageFly page builder |
| `blocks/ai_gen_block_56185bb.liquid` | 12,972 | Shopify AI-generated block |
| `blocks/ai_gen_block_70f4dac.liquid` | 10,784 | Shopify AI-generated block |

There is also a whole theme called **AVADA Assets - DO NOT REMOVE** (id `175090172229`,
unpublished, last touched 2025-12-30) which exists only to hold that app's files.

No review, loyalty, chat or upsell app has written into this theme.

## Themes

Seventeen themes exist. Sixteen are unpublished; the live one is
**NEW WEBSITE BUG fix 7**. Eleven of the seventeen are Horizon-based iterations of the same
site, named in a sequence (`NEW WEBSITE 1`, `... BUG FIX`, `1.1`, `1.2`, `BUG fix 3`,
`BUG fix 7`, plus two `OBERNDÖRFER MILANO` copies). Six are older Dawn or Atelier themes.

`themeDuplicate` is present in this store's Admin API version. It was not called.
