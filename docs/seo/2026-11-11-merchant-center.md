# Google Merchant Center check, 11 November 2026 (via Windsor, read-only)

Account 5295958284, still named "Oberndörfer & CO".

## Free listings status
| Country | Active | Disapproved | Pending |
|---|---|---|---|
| DE | 196 | 36 | 0 |
| IT | 96 | 85 | 0 |
| JP | 47 | 22 | 4 |
| US | 0 | 136 | 0 |
| GB | 0 | 4 | 0 |

Performance, last 90 days: about 20-60 impressions a day and roughly 1 click every 1-2 days. No conversions.

## Where the products come from
- "Content API": Shopify's Google & YouTube app. Feed label DE, English, Germany only.
- "oberndoerferco.com" AUTOFEED: Google crawling the website. This produces the IT, JP, US and GB items.
  Many of them carry USD prices: IT 83 items, DE 30, JP all, US all. Google's crawler is likely seen as a US
  visitor, so Shopify Markets shows it dollar prices, while Italian and German shoppers see euros.
  That price/currency mismatch fits the IT and DE disapproval counts. The US cause is not visible
  through the API; it shows in Merchant Center > Products > Needs attention.

## Owner actions
1. Shopify admin > Google & YouTube > Settings: add the other markets (Italy, US, UK, Japan) so Shopify sends
   correct per-country prices itself.
2. Merchant Center > Settings > Data sources: once Shopify covers those countries, switch off the website
   crawl (Autofeed), which creates the dollar-priced duplicates.
3. Merchant Center > Products > Needs attention: read the US reason (e.g. shipping or policy).
4. Rename the account to "Oberndörfer Milano" (Settings > Business info).
