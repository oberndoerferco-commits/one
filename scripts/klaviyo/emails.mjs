import { layout, eyebrow, head, sub, p, small, link, caption, button, photo, rule, band, grid, SITE, C } from './layout.mjs';
import { readFileSync } from 'node:fs';
const P = JSON.parse(readFileSync(new URL('./products.json', import.meta.url), 'utf8'));

// The person who signs. Change here and every email follows.
const SIGNER = 'Celina';

const IMG = {
  brazing: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/Custom.jpg?v=1771176609',
  workshopTrunks: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/oberndoerfer-cle-workshop-trunks.jpg?v=1787035628',
  hardware: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/oberndoerfer-trunk-hardware-detail.jpg?v=1786626828',
  bench: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/oberndoerfer-cle-atelier-bench.jpg?v=1787035629',
  teeWhite: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/obm-tee-embroidered-white-front-v4.jpg?v=1789930159',
  hoodieWhite: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/obm-hoodie-wordmark-white-front-v3.jpg?v=1790010435',
  ensemble: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/oberndoerfer-aol-ensemble.jpg?v=1787011723',
  daybed: 'https://cdn.shopify.com/s/files/1/0758/8387/2581/files/oberndoerfer-aol-daybed-arch.jpg?v=1787011722',
};
const w = (u, px = 1200) => u.includes('?v=') ? u.replace('?v=', `?width=${px}&v=`) : `${u}?width=${px}`;
const piece = (key, note, cta) => ({ src: w(P[key].src, 600), title: P[key].title.replace(/ - .*$/, ''), href: `${SITE}/products/${P[key].handle}`, note, cta });

const greet = `{% if first_name %}{{ first_name }},{% else %}Good day,{% endif %}`;
const signed = p(`${SIGNER}<br /><span style="color:${C.muted};">Oberndörfer Milano</span>`);
const houseSigned = p(`Oberndörfer Milano`);

export const emails = [
  {
    key: 'welcome-1',
    name: 'OM · Welcome 1 · From the ateliers',
    subject: 'From the ateliers around Milan',
    preheader: 'Who makes the pieces, and what this letter is.',
    html: layout({
      title: 'From the ateliers around Milan',
      preheader: 'Who makes the pieces, and what this letter is.',
      body: `
${eyebrow('From the ateliers')}
${head('Thank you for joining us.')}
${p(greet)}
${p('We make trunks, bags and objects for the home by hand, in small ateliers around Milan, to order and in small numbers. Nothing is cut until it is yours.')}
${photo(w(IMG.brazing), 'The brass emblem being brazed by hand', SITE + '/about-us', 'The emblem, cut in solid brass and brazed by hand.')}
${p('The people who make the pieces learned from their parents and grandparents. The workshops are fewer every year. We stand behind them, stud by stud, so that what lies behind the words Made in Italy does not disappear.')}
${p('This letter arrives once a month, no more: a new piece, a commission in progress, a photograph from the bench. You hear of new pieces and pre-orders here first, before the site. Over the next ten days, two short notes follow: one on the trunks, one on the pieces you can order today.')}
${eyebrow('Three of the pieces')}
${grid([piece('ostrich', 'Trunk bag, ostrich'), piece('himalaya', 'Backpack, Himalaya alligator'), piece('watch8Green', 'Eight places, green calf')])}
${p(link('Discover the collections', SITE + '/collections'))}
${houseSigned}`,
    }),
  },
  {
    key: 'welcome-2',
    name: 'OM · Welcome 2 · A trunk begins with a drawing',
    subject: 'A trunk begins with a drawing',
    preheader: 'How a trunk is made, and how a commission works.',
    html: layout({
      title: 'A trunk begins with a drawing',
      preheader: 'How a trunk is made, and how a commission works.',
      body: `
${eyebrow('The trunks')}
${head('A trunk begins with a drawing.')}
${p(greet)}
${p('Then a wooden frame. The leather is cut by hand and stretched over it, the corners and locks are solid brass, galvanised in gold or palladium, and every stud is set one at a time.')}
${photo(w(IMG.workshopTrunks), 'Three black leather trunks with gold hardware on the workbench', SITE + '/collections/trunks', 'Three trunks on the bench, waiting for their hardware.')}
${p('Choose a piece from the collection, or begin a commission: your measurements, your leather, your colour, your initials. We tell you the lead time and the price before anything is cut, and nothing is cut until you have approved the drawing.')}
${eyebrow('Three trunks')}
${grid([piece('tableTrunk', 'A trunk that is a table'), piece('goldTrunk', 'With Trax NYC'), piece('wine', 'For six bottles')])}
${photo(w(IMG.hardware), 'Stitched corner, brass hardware and handle of an olive-green trunk', SITE + '/pages/bespoke', 'A corner, a handle, a lock: each set by hand.')}
${p(`${link('See the trunks', SITE + '/collections/trunks')} &nbsp;&nbsp;·&nbsp;&nbsp; ${link('Begin a commission', SITE + '/pages/bespoke')}`)}
${signed}`,
    }),
  },
  {
    key: 'welcome-3',
    name: 'OM · Welcome 3 · The pieces you can order today',
    subject: 'The T-shirts and hoodies, on pre-order',
    preheader: 'The pieces you can order today, and an invitation.',
    html: layout({
      title: 'The T-shirts and hoodies, on pre-order',
      preheader: 'The pieces you can order today, and an invitation.',
      body: `
${eyebrow('Ready to wear')}
${head('The pieces you can order today.')}
${p(greet)}
${p('T-shirts and hoodies in heavy cotton, embroidered or printed, in black and in white. Each run is small.')}
${photo(w(IMG.teeWhite), 'White embroidered T-shirt, front', SITE + '/collections/ready-to-wear', 'The Embroidered T-Shirt in white.')}
${p('They are on pre-order: you pay today, we dispatch when the run arrives, and you can cancel at any time before dispatch. We email you the shipping date.')}
${eyebrow('Also in the run')}
${grid([{ ...piece('cap', 'Cotton, tonal logo'), src: w(P.cap.src, 600) }, { src: w(IMG.hoodieWhite, 600), title: 'The Wordmark Hoodie', note: 'Heavy cotton, white or black', href: SITE + '/collections/ready-to-wear' }, piece('pants', 'Navy, slate, taupe or sage')])}
${p('If you would rather talk than read, reply to this email. It reaches me, not a mailbox. I am happy to help with a size, a leather or a piece for someone else.')}
${p(link('See Ready to Wear', SITE + '/collections/ready-to-wear'))}
${signed}`,
    }),
  },
  {
    key: 'checkout-1',
    name: 'OM · Checkout 1 · Your pieces are kept',
    subject: 'Your pieces are kept',
    preheader: 'Nothing has been charged. They are held for you.',
    html: layout({
      title: 'Your pieces are kept',
      preheader: 'Nothing has been charged. They are held for you.',
      body: `
${eyebrow('Your selection')}
${head('We have kept your pieces.')}
${p(greet)}
${p('You left these at checkout. They are held for you, and nothing has been charged.')}
{% for item in event.extra.line_items %}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 14px;border-top:1px solid ${C.line};">
<tr>
  <td width="120" valign="top" style="padding:14px 16px 14px 0;">{% if item.product.images.0.src %}<img src="{{ item.product.images.0.src }}" alt="" width="120" style="display:block;width:120px;height:auto;border:0;background:#f5f2ed;" />{% endif %}</td>
  <td valign="top" style="padding:14px 0;">
    <p style="margin:0 0 4px;font:400 17px/1.3 'Marcellus', Georgia, serif;color:${C.ink};">{{ item.product.title }}</p>
    {% if item.variant_title and item.variant_title != 'Default Title' %}<p style="margin:0 0 4px;font:400 13px/1.5 'Inter', Helvetica, Arial, sans-serif;color:${C.muted};">{{ item.variant_title }}</p>{% endif %}
    <p style="margin:0;font:400 13px/1.5 'Inter', Helvetica, Arial, sans-serif;color:${C.muted};">Quantity {{ item.quantity }}</p>
  </td>
</tr></table>
{% endfor %}
${rule()}
<div style="height:18px;"></div>
${button('Return to checkout', '{{ event.extra.checkout_url }}')}
${p('If a question stopped you, on a size, a lead time, duties or a colour, reply to this email and a person answers. Every parcel travels insured and tracked.')}
${houseSigned}`,
    }),
  },
  {
    key: 'checkout-2',
    name: 'OM · Checkout 2 · A note from the atelier',
    subject: 'A note from the atelier',
    preheader: 'In case a question stopped you.',
    html: layout({
      title: 'A note from the atelier',
      preheader: 'In case a question stopped you.',
      plain: true,
      body: `
${head('A note from the atelier.', 26)}
${p(greet)}
${p('Yesterday you set aside {{ event.extra.line_items.0.product.title }}{% if event.extra.line_items|length > 1 %} and {{ event.extra.line_items|length|add:"-1" }} other piece{% if event.extra.line_items|length > 2 %}s{% endif %}{% endif %}. It is still held for you.')}
${p('If it was a question of size, lead time, duties or colour, write back and I will answer it myself. Most pieces are made to order, so a colour or a detail can still be changed before anything is cut.')}
${p(link('Return to your selection', '{{ event.extra.checkout_url }}'))}
${signed}`,
    }),
  },
  {
    key: 'checkout-3',
    name: 'OM · Checkout 3 · Would you like to see it',
    subject: 'Would you like to see it?',
    preheader: 'An invitation, and then nothing more from us.',
    html: layout({
      title: 'Would you like to see it?',
      preheader: 'An invitation, and then nothing more from us.',
      plain: true,
      body: `
${head('Would you like to see it?', 26)}
${p(greet)}
${p('A piece like this deserves to be seen before it is decided. Our interior at Miramare The Palace in Sanremo and our partner Trax NYC in New York both have pieces to hand, and in Milan we receive by appointment. Reply with a day that suits you, or a telephone number, and I will call.')}
${p('If you have simply changed your mind, nothing more will follow from us.')}
${p(link('Return to your selection', '{{ event.extra.checkout_url }}'))}
${signed}`,
    }),
  },
  {
    key: 'letter',
    name: 'OM · Monthly letter · template',
    subject: 'Introducing: [the piece]',
    preheader: '[One line on what is in this letter.]',
    html: layout({
      title: 'The letter',
      preheader: '[One line on what is in this letter.]',
      body: `
${eyebrow('[Month year]')}
${head('[A heading that is a sentence with a claim in it.]')}
${p(greet)}
${p('[Fifty words at most. One idea. What happened in the ateliers this month, in plain words.]')}
${photo(w(IMG.ensemble), '[What is in the photograph]', SITE, '[Caption: what is in the photograph, and nothing more.]')}
${eyebrow('The piece')}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 22px;"><tr>
  <td width="250" valign="top" style="padding:0 20px 0 0;"><a href="${SITE}/products/${P.mirrorOstrich.handle}"><img src="${w(P.mirrorOstrich.src, 600)}" alt="[Product]" width="250" style="display:block;width:250px;height:auto;border:0;" /></a></td>
  <td valign="top">
    ${sub('[Product name]')}
    ${p('[Two sentences: the material, the hardware, the number made.]')}
    ${small('[Made to order, lead time / In stock, one]')}
    ${link('See the piece', SITE + '/products/[handle]')}
  </td>
</tr></table>
${eyebrow('Also in the ateliers')}
${grid([piece('briefcase', '[one line]'), piece('weekend', '[one line]'), piece('necklaceTrax', '[one line]')])}
${rule()}
<div style="height:22px;"></div>
${eyebrow('From the bench')}
${photo(w(IMG.bench), '[What is in the photograph]', SITE + '/about-us', '[Caption.]')}
${p('[Forty words on a commission in progress or a technique, without adjectives.]')}
${p('Reply to this letter for an appointment in Milan, or to ask about a piece.')}
${signed}`,
    }),
  },
];
