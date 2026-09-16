# Email marketing: what exists, what to fix (16 September 2026)

Read from the Shopify admin and the live theme ("NEW WEBSITE BUG fix 6"). Nothing was sent
and nothing was changed; this is the state before any email work starts.

## What exists today

| | |
|---|---|
| Customer records | 43 |
| Of those, subscribed to email marketing | 16 (single opt-in; the oldest from May 2023, most from Feb to Aug 2026) |
| Subscribers who have ever ordered | 1 |
| Campaigns or automations ever sent from Shopify | none recorded (Marketing activities is empty) |
| Email app installed | none found (no Klaviyo, Omnisend, Mailchimp, Privy script on the storefront; Windsor shows only GA4, Search Console, Merchant Center, Business Profile) |
| Sign-up form | one, in the footer: "Join our email list / Get exclusive deals and early access to new products." (Horizon's default copy) |
| Pop-up or exit form | none |
| Welcome offer | a discount code "Welcome" exists (5% off six collections, one use per customer) but nothing delivers it: no welcome email, no mention at the form |
| Abandoned checkouts since March | 2: a Table Trunk at EUR 34,250 (today, 16 Sept) and a BAG MODEL 017 at EUR 842 (15 Aug). Neither customer is subscribed. No recovery email is configured |
| Sender addresses | store email oberndoerfer.co@gmail.com, customer-facing info@oberndoerferco.com |
| Last 90 days on site | 3,621 sessions, 50 added to cart, 46 reached checkout, 1 order |
| Last 12 months | 1 order (EUR 10, August, likely a test) |

The picture: there is no email programme. Sixteen addresses, most of them collected by the
footer form with generic copy, nobody has been written to, and two people who got as far as
checkout with a EUR 34,000 trunk and an EUR 840 bag were never followed up.

## What has to improve, in order

1. **Follow up the checkouts that already happen.** 46 people reached checkout in 90 days and
   one bought. Shopify's abandoned-checkout automation (Marketing > Automations, free with
   Shopify Email) sends one email an hour or so after the checkout is left; for pieces at this
   price a second, personal one from the atelier two days later does more than a reminder.
   This is the single highest-value email on the store and it is off.
2. **Give the sign-up a reason.** "Exclusive deals and early access" is not what the house
   sells, and 5% is a small reason to hand over an address. Rewrite the footer block in the
   site's own voice (what the letter is: new pieces, the ateliers, pre-orders first) and make
   the "Welcome" code arrive by email, or replace it with something that fits the brand better
   (first access to pre-orders, complimentary monogramming, an invitation to see a piece at the
   Miramare).
3. **A welcome series, not one welcome email.** Three emails over ten days: who makes the
   pieces and where; one family of pieces explained (the trunks, the alligator SAC); the
   T-shirts and hoodies as the accessible entry, on pre-order. Written in the site's own prose,
   one photograph per email, no banners.
4. **Sender and deliverability.** Send from info@oberndoerferco.com, not the gmail address.
   Add the domain in Shopify (Settings > Notifications > Sender email) and set up the SPF and
   DKIM records it asks for, or the first campaign lands in spam. Check DMARC too.
5. **Collect consent at checkout.** Make sure the "Email me with news and offers" box is on in
   Settings > Checkout, and consider a small line on the pre-order confirmation asking to be
   kept informed about production.
6. **One monthly letter, no more.** For a house this size, a monthly note (a new piece, a
   commission, a photograph from the atelier, one product) is enough; more than that at this
   list size is noise. Segment only two ways at first: bought / not bought.
7. **Grow the list where the buyers are.** The traffic is there (3,600 sessions a quarter); the
   list is not. Options that fit the site: a quiet sign-up on the pre-order product pages
   ("be told when the next run opens"), on Materials & Craftsmanship, and on Where to Find
   Us; a sign-up on the Miramare hotel's page or card (the MIRAMARE10 code already exists).
   Avoid a pop-up on entry; a scroll-triggered one on collection pages is acceptable if it is
   one line and the house's own words.

## Tooling

Shopify Email is enough for all of the above (automations for abandoned checkout, welcome
and post-purchase; campaigns for the monthly letter; 10,000 free emails a month). Klaviyo is
not needed at 16 subscribers and would add cost and another design system to keep in the
site's style. Revisit at a few hundred subscribers.

## Next steps I can do on request (no emails sent without a go)

- Rewrite the footer sign-up block and add sign-up blocks to the pre-order product pages
  (theme copy, owner publishes).
- Draft the abandoned-checkout, welcome series and first monthly letter as text, in the
  site's voice, for review.
- Once approved, build them in Shopify Email as drafts and switch on the automations.
- Set the sender address and check the DNS records.
