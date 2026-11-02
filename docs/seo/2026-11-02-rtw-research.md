# Ready to wear: what people search for (2 November 2026)

Source: Google autocomplete (US, UK, Germany, Italy), raw data in 2026-11-02-rtw-autocomplete.json, script
scripts/seo/autocomplete-rtw.py. Google Trends blocks automated access and Keyword Planner is not connected, so these
are relative signals: "letters typed" = how few letters before Google suggests the phrase (fewer = more searched).

## Findings
- "italian streetwear" is a small, research-type search: it needs 12 letters (US) / 12 (IT) before it is suggested,
  and the follow-ups are lists ("italian streetwear brands", "brand streetwear italiani emergenti"). People look for
  brand lists, not products: it belongs on the collection page and in list articles, not in product titles.
- Product words carry the demand:
  - US/UK: "quarter zip" 3 letters, "wide leg sweatpants" 4, "heavyweight hoodie" 6, "heavyweight t shirt" 6,
    "half zip" 6, "luxury streetwear" 9, "made in italy clothing" 9, "wide leg joggers" 10, "matching sweatsuit" 11.
    "luxury hoodie" and "luxury t shirt" are never suggested on their own; "embroidered beanie" needs 14.
  - Germany: "jogginganzug herren" 3, "half zip pullover" 4, "troyer herren" 4, "beanie mütze" 4, "luxus hoodie" 9,
    "oversized t shirt" 9, "schweres t shirt" 10, "jogginghose weites bein" 13.
  - Italy: "tuta uomo" 4, "felpa con cappuccio" 7, "felpa mezza zip" 8, "brand streetwear italiani" 8, "cuffia uomo" 8,
    "t shirt oversize" 9, "streetwear italiano" 12. Italians add the fabric: "felpa cotone made in italy",
    "felpa 100 cotone made in italy".
- People add the wearer ("men", "herren", "uomo") to nearly every clothing search.
- "made in italy hoodie" is searched with big brand names in front (Gucci, Nike, Aries, Amiri): the phrase works as a
  quality signal next to a product word, not as a search on its own.
- Sets are searched: "matching sweatsuit", "jogginganzug herren", "tuta uomo completa".

## Applied (English SEO titles; rollback in 2026-11-02-rtw-seo-before.json)
- Ready to Wear collection: "Italian Streetwear, Made in Italy | Oberndörfer Milano"; description names hoodies,
  half-zip sweatshirts, wide-leg sweatpants, T-shirts, beanies and caps.
- Products lead with the searched product word: Half-Zip Sweatshirt, Quarter-Zip; Wide-Leg Sweatpants; Blackletter
  Hoodie OM; Hoodie with Star Print; Grey Sweatpants with Logo; Blackletter T-Shirt OM; Embroidered Beanie OM;
  Check Jacket with Emblems, Padded; Hooded Canvas Work Jacket. "Made in Italy" only where the product page says so.

## Next (needs the owner)
- Fabric weight: if the hoodies, half-zip and T-shirts are heavy cotton (about 400 g/m² hoodies, 220+ g/m² tees),
  "heavyweight" / "schwer" is one of the strongest words to add.
- Men / unisex: say who the pieces are for; the word appears in most searches.
- German and Italian SEO titles (Half-Zip Pullover Herren, Jogginghose weites Bein, Felpa mezza zip uomo, Pantaloni
  tuta larghi, Felpa con cappuccio, Cuffia ricamata).
- A "Tracksuit / Sets" collection (Hoodie OM + Wide-Leg Joggers OM in navy, Hoodie with Logo + Joggers with Logo).
- "Italian streetwear brands" list articles and marketplaces (e.g. Edropit) for the brand-list searches.

## Fix
- Titles ending "| Oberndörfer" got the theme's " – Oberndörfer Milano" added (brand twice in Google). Now ending
  "| Oberndörfer Milano": Wide-Leg Sweatpants, and the caps Leopard/Black logo, Leopard/Pink logo, Black/Pink logo
  (were "Leopard Cotton Cap, Black Leather Patch | Oberndörfer", "Leopard Washed Cotton Cap, Leather Patch | Oberndörfer",
  "Black Washed Cotton Cap, Pink Leather Patch | Oberndörfer").
