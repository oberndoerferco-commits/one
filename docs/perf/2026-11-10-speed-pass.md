# Speed and search pass, 10 November 2026

Draft theme "REDESIGN 2026 - 1.2 icon + speed (draft)" (210626511173) = the live theme + favicon fix + the
changes below. Nothing was written to the live theme; the owner publishes.

## Baseline (live, Lighthouse 12.6.1 mobile)
SEO 100, accessibility 100, best practices 75, performance 49-52. LCP 5.8-7.3 s.
Product pages: the main photo had 3.6 s of load delay because it sits ~77% of the way down a 435 KB
document. Home: LCP is the hero text, held back by main-thread script (Google tags, Shopify, Klaviyo).

## Changed in the draft
1. layout/theme.liquid - product pages preload their main photo right after the viewport meta tag, with
   the same srcset/sizes as the gallery's first image (one download, reused; checked on phone and desktop).
2. snippets/product-media-gallery-content.liquid - only the first gallery photo loads eagerly; the rest
   are lazy (phones no longer download photos 2 and 3 before they are swiped to).
3. snippets/oberndoerfer-color-grouping.liquid - comments stripped from the inline swatch script
   (22.6 -> 17.5 KB, gzip 7.5 -> 5.2 KB on every page). Identical program: terser output of old and new
   is byte-identical. Commented original: docs/perf/oberndoerfer-color-grouping.commented.liquid.
4. snippets/oberndoerfer-organization-schema.liquid - hasMerchantReturnPolicy from the store's refund
   policy (14 days, by mail). Fees and refund type left out: the policy does not state them.
5. sections/obm-panels.liquid - a video hero gets its poster from the script for the right screen, so
   phones no longer download the desktop poster too (no effect today: the home hero is a photo).

## Measured (docs/perf/lcp-compare.js: Pixel 5, ~1.6 Mbps / 150 ms, 4x CPU, alternating runs)
- Wide-Leg Joggers OM: main photo shown at 2.44 s live vs 2.16 s draft (median of 5; draft faster in every pair).
- 3-Place Watch Box green: 2.30 s vs 2.10 s (median of 4; draft faster in every pair).
Lighthouse scores swing +-10 between runs because of third-party scripts, so they are not used to compare.

## For the owner (not code)
- The Google & YouTube app loads two Google tags (G-1ETY4BPEW7 and GT-K5Q7S5K) in one pixel; together the
  biggest script cost on every page (~0.5 s main thread on a phone). If GT-K5Q7S5K only duplicates the
  GA4 property, removing it in the app settings is the largest single speed gain left.
- Product reviews (Judge.me is installed but shows nothing) would add review stars in Google results.

## 11 November 2026: Horizon 4.5.0 update with customisations kept
The owner published the speed draft through Shopify's "Update theme", which produced "Updated copy of
REDESIGN 2026 - 1.2 ..." (Horizon 4.4.0 -> 4.5.0). The update replaced 117 files; 18 of them were customised.
Shopify merged 7 correctly and overwrote 12 with stock Horizon (meta-tags.liquid - all the extra schema;
main-collection - one card per model on Ready to Wear; price, card gallery/swatches, slideshow controls,
product title heading level, measure-header-heights, paginated-list.js, product recommendations/information).
Fix: duplicated the updated theme as "REDESIGN 2026 - 1.3 Horizon update + customs (draft)" (211074220357) and
ran a 3-way merge per file (ours = 1.2 draft, base = github.com/Shopify/horizon b2b74b0 "Horizon v4.4.0",
theirs = 51b31c9 "Horizon v4.5.0"): no conflicts; those 12 files did not change between 4.4.0 and 4.5.0, so
the merge is the customised version. Locales and the other 99 files were stock and take 4.5.0 as is.
Checked against the 1.2 draft: same structured data on 8 page types, pixel-identical screenshots, same 19
products on Ready to Wear, add to cart works on desktop and phone, no script errors.
Lesson: "Update theme" overwrites customised files. Update via a duplicate and re-merge instead.
