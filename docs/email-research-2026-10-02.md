# Email marketing: how it is done properly now (2 October 2026)

Research for the owner's question "how it's done properly and what is the best workaround
right now", before building the Klaviyo flows. Part 1 is current practice with sources; part
2 is what the competitor houses do. Figures are from the sources named; anything the research
could not confirm is marked.

## Part 1: current practice, ranked by what matters for this house

1. **The abandoned-checkout flow first.** It is the only flow with real volume here (about
   46 started checkouts a quarter, 1 to 2 orders). Klaviyo's 2025 benchmark: abandoned-cart
   flows average 47% open, 5.2% click, 2.7% placed order, $3.07 revenue per recipient; campaign
   emails average 0.08% placed order, so flows are about 30 times more productive
   (klaviyo.com 2025 Benchmark Report PDF). Applied to 46 checkouts, even the average rate is
   about one extra order a quarter. Klaviyo's own guidance: two or three messages, the first
   2 to 4 hours after the checkout, the second 20 to 48 hours later
   (help.klaviyo.com/hc/en-us/articles/115002779411). Agencies push 30 to 60 minutes for the
   first; no controlled test found. For a €30,000 trunk the third message is an offer to
   talk, not a coupon.
2. **No discounts.** Klaviyo's advice, not only luxury taste: a coupon in the first cart
   email "can train customers to abandon carts in order to get the discount"; if ever, the
   last email and first-time buyers only. Luxury substitutes: early access to new pieces,
   a consultation, the atelier, complimentary services. The often-quoted "discounted first
   buyers repeat less" figure has no primary source; not relied on.
3. **Welcome series: three emails over about ten days.** Klaviyo 2025: welcome flows 51%
   open, 4.9% click, 2.0% placed order. Send the first immediately, the others at least a
   day apart, cover the ten-day window in which most subscribers who buy do so, and keep new
   subscribers out of campaigns until the series ends (klaviyo.com/blog/welcome-email-examples).
   Structure: welcome and what makes the pieces; the making; the collection plus a personal
   invitation to talk. Browse abandonment later (0.8% placed order). Post-purchase exists
   for a second commission and referrals, not for revenue.
4. **Italian consent rules, now.** Garante, 4 June 2025 (Noi Compriamo Auto, €45k fine):
   logs alone do not prove consent; double opt-in "constitutes, to date, a minimum standard".
   Turn on Klaviyo double opt-in; keep the checkout marketing box unticked for EU regions.
   Garante Provision 284 (17 April 2026): open-tracking pixels used for profiling need
   explicit consent, deadline 28 October 2026. Add a consent line to the forms; confirm with
   Klaviyo how open tracking is suppressed for profiles without consent (unverified).
5. **Deliverability basics.** The Gmail/Yahoo/Microsoft bulk-sender rules bind senders above
   5,000 a day, but Gmail requires SPF or DKIM from everyone and a spam rate under 0.3%. Do it
   anyway: Klaviyo branded sending subdomain, DMARC published (done, p=none). Warming is moot
   at 20 contacts. Sunset: suppress 180-day inactives.
6. **Measure clicks and orders, not opens.** Litmus July 2026: Apple is 62% of opens and
   Mail Privacy Protection inflates them; dark mode above 25%. Judge flows by click, placed
   order and revenue per recipient.
7. **Design.** 600px, one column, text-led with one or two real photographs; a letter-style
   email with real text survives dark mode and spam filters better than an image-only one
   (weakly sourced but directionally sound). Test the wordmark on dark backgrounds.
8. **Frequency.** Klaviyo suggests one campaign a week for lists under 20k; at 20 subscribers
   that is over-sending (0.27% unsubscribe per campaign send on average). One or two letters a
   month, only when there is news; let the flows do the rest.
9. **List growth.** Klaviyo: median pop-up submit rate 2.3%, target 3%; exit-intent 10 to
   13%; show after 5 seconds and 20% scroll with a teaser tab. At 3% of 3,600 sessions that is
   about 100 subscribers a quarter, five times today's list. Offer early access or a lookbook,
   not a code. WhatsApp is in Klaviyo since 24 September 2025 and Italy is "very
   WhatsApp-native"; defer until the list passes 200.
10. **Tools.** Klaviyo free to 250 profiles and 500 sends a month; Shopify Email 10,000 free
    sends a month. Both free at this size; Klaviyo for browse abandonment, flow branching and
    the branded domain. AI-written copy: readers and filters recognise its cadence; Klaviyo's
    tests favour about seven-word, curiosity-led subject lines. Write in the house's own voice.
    Personalisation at this size: a reply-able From address and a personal follow-up to every
    started checkout above about €1,000.

Order of work: double opt-in and the unticked checkout box; branded sending subdomain;
abandoned-checkout flow, three emails, no discount; three-email welcome; exit-intent form;
tracking-consent wording before 28 October 2026.

Not found: luxury-specific benchmarks; per-industry flow revenue (Klaviyo 2026 gives apparel
flows 34% open, 5.5% click, 2.2% placed order).

## Part 2: what the comparable houses do (sign-up copy and indexed subject lines, 2 Oct 2026)

Limits: milled.com and the other email archives block automated reading, so no email body
could be opened. The evidence is each house's own sign-up copy plus subject lines and dates
that search engines have indexed. Nothing below on welcome-email content or layout is claimed.

| House | Sign-up incentive | What the emails are |
| --- | --- | --- |
| Hermès | none ("stories, collections, and surprises") | short playful editorial subjects, never a price: "Objects for Interior life", "Faubourg Express" |
| Brunello Cucinelli | none | essays and dated letters from Solomeo: "Harmony and Hope" |
| Connolly | none | a recurring signed series, "Letter from Isabel: Driving Loafers"; one product, story first |
| Métier London | none | single-product explainers, "Introducing The Vagabond Messenger", "Which Perriand Is Right For You?"; signed "With Love, Melissa Morris" |
| Bennett Winch | 10% off first order | "Introducing:" launches, restocks, customer reviews |
| Carl Friedrik | none at sign-up, but sales often | "Summer Sale ends midnight", refurbished sales, fortnightly |
| Smythson | none | witty subjects, frequent outlet and sale mailings |
| Globe-Trotter | a service: complimentary initialling (earlier: a luggage tag) | first access to limited releases |
| Ettinger | a £70 gift | not found |
| Goyard, Berluti, Loro Piana, Valextra, Moynat, Serapian, Au Départ | none | "be the first to receive news"; no archived emails found |

What the best programmes share: no sign-up discount (12 of 16; where there is an incentive
it is a service or an object); one subject and one piece per email; short specific subjects
with no emoji and no price; a named human voice (Isabel at Connolly, Melissa at Métier,
Brunello Cucinelli's letters); launches, back-in-atelier notes and "introducing" do the
selling. Sales language only at the two volume businesses (Smythson, Carl Friedrik).

For Oberndörfer Milano: the Connolly and Métier model. A signed letter from the owner,
monthly, one piece per send, "Introducing:" and "Back in the atelier:" subjects, pre-orders
announced as letters, sign-up copy promising stories and first access, not offers. If any
incentive, a service such as complimentary initials. A reply-able From address. Avoid
percentage discounts, "ends midnight", outlet language, emoji, more than one call to action.

## Decisions taken in the emails (2 October)

- No discount codes anywhere (the owner's instinct; both parts of the research agree). The
  Welcome code stays in Shopify unused; the sign-up promise is first access and the letter.
- Header is the wordmark alone; cities removed from header and footer.
- Signed by a person, not the house. Welcome 2 and 3 and the checkout notes carry the owner's
  first name; the owner can change the signature in `scripts/klaviyo/emails.mjs`.
- Product photographs: the house's own studio shots on the ivory ground, in rows of three,
  each a link; one filled button only in the first checkout email.
- Checkout flow is three emails: 2 hours (your pieces are kept), 24 hours (a note from the
  atelier, personal), day 4 (an invitation to see the piece or to talk; "nothing more will
  follow"). Welcome flow stays three over ten days.
- Klaviyo settings to set with the owner: double opt-in on (Garante, June 2025), checkout
  marketing box unticked, open tracking treated as consent-based before 28 October 2026.
