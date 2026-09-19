# Building the six emails in Shopify Email (19 September 2026)

Shopify Email has no API for creating campaigns or automations, so the emails cannot be
created from here. What exists instead: the six finished designs in `docs/emails/*.html`
(open any of them in a browser), built in the manner of the Canva reference the owner chose
("Cream and Brown Minimalist Fashion Email Newsletter"): brown bar, logo on cream, a
full-bleed photograph with one serif line in white, cream body text centred, a brown pill
button, two photograph tiles with serif labels, quiet footer. This sheet is the block-by-block
recipe for rebuilding each one in the Shopify Email editor in a few minutes.

## Once, before any email: Settings > Brand, and the sender

- Logo: MILANO_13_x_4_cm_-6.svg (already in Files). Square logo: 2.svg.
- Colours: primary #6B4B36 (buttons), secondary #EFEBE6 (backgrounds), text #2B2320.
- Fonts in Shopify Email: heading serif "Playfair Display" if offered, otherwise Georgia;
  body "Inter" if offered, otherwise Helvetica/Arial.
- Sender: Settings > Notifications > Sender email = info@oberndoerferco.com, then
  Authenticate domain and add the two CNAME records plus the SPF and DMARC records at
  GoDaddy (see the audit). Do this before the first send.

## The template, block by block (same for all six)

1. Section background: #EFEBE6. Top: a Spacer, 26px, background #5F4534 (the brown bar).
2. Logo block, centred, 40px high, 30px padding above and below.
3. Image block, full width, the hero photograph (list below), with an overlay/text: the
   headline in the serif heading font, white, centred, 40 to 44px. If the editor has no text
   overlay, use the "Image with text" or "Hero" section and set its overlay to 40% brown.
4. Text block, centred, 16px, 1.7 line height, the paragraphs below. Where an eyebrow is
   listed, a small uppercase Text block first (12px, letter-spaced, #7D7069).
5. For the abandoned-checkout emails: the Product block (Shopify fills the piece from the
   checkout) set to image left, title and one line, no price emphasis.
6. Button block, centred, label below, background #6B4B36, white text, fully rounded.
7. Two-column Image block with the two tile photographs, each with its label as caption
   (if captions cannot sit on the photograph, put the label under it in the serif font).
8. Footer: "Oberndörfer Milano · Milan, Italy · info@oberndoerferco.com", unsubscribe.

Photographs are all in Files already; use the names as given.

## 1a. Abandoned checkout, 1 hour (Marketing > Automations > Abandoned checkout, delay 1 h)
Subject: Your piece is still with us · Preview: Nothing has moved. It is held for you.
Hero: oberndoerfer-trunk-hardware-detail.jpg · Headline: Your piece is still with us.
Text: You left {product} in your cart. Nothing has moved: it is held for you, and the price
you saw is the price it stays. / Every piece is made by hand in our ateliers around Milan,
so there is no rush on our side and no reason to hurry on yours. If a question stopped you,
reply to this email and a person in the atelier will answer, usually within one working day.
Product block. Button: Return to your cart (checkout link).
Tiles: oberndoerfer-about-craft-detail.jpg "Materials" → /pages/materials-craftsmanship;
gift_boxes.heic "Delivery" → /pages/shipping-and-delivery.

## 1b. Abandoned checkout, 2 days (second step of the same automation, only if not recovered)
Subject: A note from the atelier · Preview: In case a question stopped you.
Hero: oberndoerfer-cle-atelier-bench.jpg · Headline: A note from the atelier.
Text (left-aligned): The piece you looked at is still in your cart. Three things people ask
us before they decide, in case one of them is yours. / **Where the leather comes from.**
Full-grain hides from tanneries in Italy, France and Germany. The hardware is solid brass,
finished in palladium or gold. / **How it travels.** Free with DHL Express, wherever you are,
in a box made by hand in Italy. Fourteen days from delivery to return it if it is not right.
/ **Whether it can be made yours.** Most pieces can be made in another hide or colour, or
marked with initials. Reply and tell us what you have in mind.
Button: Return to your cart. Tiles: obm-lane-sac-black.jpg "Bags" → /collections/bags;
oberndoerfer-trunk-hardware-detail.jpg "Trunks" → /collections/trunks.

## 2a. Welcome, on sign-up (Marketing > Automations > Welcome new subscribers, email 1)
Subject: You are on the list · Preview: What that means, and what it does not.
Hero: Artisan.jpg · Headline: You are on the list. · Eyebrow: Welcome
Text: When a new piece opens on pre-order, you will hear before it is shown on the site, and
you will be able to order first. Once a month, one letter from the atelier: a piece, a
commission, a photograph from the bench. That is all. / If you would like to know how the
pieces are made, the next two letters cover it. If you would rather just wait for the
pre-orders, that is fine too.
Button: See what is made now → /collections/new-in.
Tiles: obm-lane-sac-black.jpg "Bags"; obm-lane-ostrich-mini-trunk.jpg "Trunks".

## 2b. Welcome, 3 days later (email 2)
Subject: What it is made of, and who makes it · Preview: Two questions we ask of every piece.
Hero: oberndoerfer-about-craft-detail.jpg · Headline: What it is made of, and who makes it.
Eyebrow: Handmade in Milan
Text (left-aligned): Every piece starts from the same two questions: what is this material,
and who is making it by hand. / **The leather** is full-grain, from tanneries in Italy, France
and Germany: the outer layer of the hide, left uncorrected, so the grain you see is the grain
the animal had. It takes on a patina rather than wearing out. / **The hardware** is solid
brass, finished in palladium or gold, chosen because it can be repaired and re-plated in
twenty years rather than replaced. / **The making** happens in small ateliers around Milan,
to order, in small batches. There is no factory floor and no stock room.
Button: Materials & Craftsmanship → /pages/materials-craftsmanship.
Tiles: oberndoerfer-trunk-hardware-detail.jpg "Hardware"; oberndoerfer-cle-workshop-trunks.jpg
"The atelier".

## 2c. Welcome, 10 days later (email 3)
Subject: The trunk that became a table · Preview: Where the house began, and where the pieces are now.
Hero: oberndoerfer-aol-lobby.jpg · Headline: The trunk that became a table.
Eyebrow: Miramare The Palace, Sanremo
Text: The first piece we made for a room rather than a person was a trunk, built for
Miramare The Palace in Sanremo, on the Ligurian coast. It was meant to travel. It stayed,
and became a table, and the hotel's public rooms are furnished with what followed. / Our
pieces are on show there now, and for sale. If you are on the coast, it is the best way to
see the work before deciding on anything. Everything else is on the site, made to order and
sent free with DHL Express.
Button: Where to find us → /pages/where-to-find-us.
Tiles: oberndoerfer-aol-ensemble.jpg "Art of Living" → /pages/oberndorfer-x-miramare-sanremo;
obm-hoodie-om-grey-back-v2.jpg "Ready to Wear" → /collections/ready-to-wear.

## 3. October letter (Marketing > Campaigns, send to segment "Email subscribers")
Subject: From the atelier, October · Preview: Three hoodies, one trunk, and a box.
Hero: obm-hoodie-om-grey-back-v2.jpg · Headline: From the atelier, October. · Eyebrow: October 2026
Text (left-aligned): One letter a month, as promised. This is the first. / **Three hoodies,
on pre-order.** The wordmark at the chest, the interlocking O and M across the back, and the
star lattice, on a heavyweight cotton hoodie in grey, black or white. Made in Italy in a
small run; order today and it ships the moment the run arrives. You are reading this before
it is shown on the site. / **A trunk in progress.** [one paragraph and a photograph from the
bench, written by the house] / **The box.** A piece leaves Milan wrapped in something made
much the same way it was: boxes, labels and tags made by hand in Italy.
Button: The hoodies → /collections/ready-to-wear (the hoodies must be set Active first).
Tiles: obm-hoodie-lattice-black-back-v2.jpg "Hoodies"; gift_boxes.heic "The Art of Packaging"
→ /pages/the-art-of-packaging.

Nothing is sent until the owner presses send; the automations stay off until switched on.
