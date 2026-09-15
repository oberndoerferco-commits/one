# German and Italian product titles

Rewritten 15 September 2026 for all 134 active products, in both published locales.
Written via `translationsRegister` against the `title` key; the English titles are the
source of truth and were not touched. Before/after for every product is in
`data/product-titles-de-it.json`, which is also the rollback source.

## Why

Three separate problems, all live on the storefront:

1. **Colour variants shared one title.** Nine `Leather Watch Box` colours were all
   `Uhrenbox` in German; nine leather trays were all `svuotatasche` in Italian; all
   ten SAC backpacks were `SACK` / `Marsupio SAC`. A German shopper saw nine identical
   products in a collection, and Google saw nine pages competing for one term.
2. **Mistranslations.** `Table Trunk` (a €34,250 piece of furniture) was `Tabellenstamm`
   in German — the spreadsheet sense of "table" plus the tree sense of "trunk" — and
   `Tronco del tavolo` in Italian. `Leather Watch Box` was `Scatola di guardia`, the
   watchman sense of "watch". `SAC`, a backpack, was `Marsupio` (bum bag).
3. **Material misstatement.** The four `Classic Leather Belt` products are full-grain
   calf per their own descriptions, but were titled `Krokodilgürtel` and
   `Cintura di coccodrillo` — crocodile — in both locales. Now corrected to
   `Ledergürtel aus Vollnarbenleder` / `Cintura in Pelle Pieno Fiore`. The crocodile
   and alligator terms are kept only on the wallets and SAC bags that genuinely are.

## Approach

Titles lead with the noun buyers actually search, then the distinguishing variant:
`Uhrenbox für 3 Uhren - Dunkelgrün`, `Portafoglio in Coccodrillo - Cognac`. The head
terms come from Search Console demand — `uhrenbox`, `häkelhandtasche`,
`krokodilleder geldbörse`, `portafogli coccodrillo`, `cintura coccodrillo` — and from
the Merchant Center free listings, where the German- and Italian-titled entries were
already the best click earners.

Italian colour adjectives agree with the head noun, so feminine nouns take feminine
forms: `Borsa Modello 017 - Nera`, `Ventiquattrore in Pelle - Nera`,
`Borsa Modello 017 - Azzurra`.

After the rewrite all 134 titles are distinct in each locale; before it, they were not.

## Not covered

- The 138 draft products, including the fine-jewellery line and the apparel still in
  draft. Their titles are untouched and several have no translation at all.
- `meta_title` and `meta_description` in German and Italian, which are what actually
  render in the search result. Many are still missing or still carry the old wording.
- Image alt text, still placeholder-grade (`Oberndorfer 3p green ivory`).

## Before and after

### Watchbox (37)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| 3-Place Watch Box - Dark Green | Uhrenbox → **Uhrenbox für 3 Uhren - Dunkelgrün** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Verde Scuro** |
| 3-Place Watch Box - Grey | Uhrenbox → **Uhrenbox für 3 Uhren - Grau** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Grigio** |
| 3-Place Watch Box - Yellow | Uhrenbox → **Uhrenbox für 3 Uhren - Gelb** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Giallo** |
| 3-Place Watch Box - Blue | Uhrenbox → **Uhrenbox für 3 Uhren - Blau** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Blu** |
| 3-Place Watch Box - Red | Uhrenbox → **Uhrenbox für 3 Uhren - Rot** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Rosso** |
| 3-Place Watch Box - Green | Uhrenbox → **Uhrenbox für 3 Uhren - Grün** | Porta Orologi 3 posti → **Porta Orologi 3 Posti - Verde** |
| 8-Place Watch Box - Black Stud | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Schwarz mit Nieten** | Porta Orologi 8 posti → **Porta Orologi 8 Posti - Nero Borchiato** |
| 8-Place Watch Box - Green | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Grün** | Porta Orologi 8 posti → **Porta Orologi 8 Posti - Verde** |
| 8-Place Watch Box - Turquoise & Black | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Türkis & Schwarz** | Porta Orologi 8 posti → **Porta Orologi 8 Posti - Turchese e Nero** |
| 8-Place Watch Box - Red | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Rot** | Porta Orologi 8 posti → **Porta Orologi 8 Posti - Rosso** |
| 8-Place Watch Box - Grey | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Grau** | Porta Orologi 8 posti → **Porta Orologi 8 Posti - Grigio** |
| 8-Place Watch Box - Turquoise | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Türkis** | porta orologi 8 posti → **Porta Orologi 8 Posti - Turchese** |
| 8-Place Watch Box - Orange | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Orange** | porta orologi 8 posti → **Porta Orologi 8 Posti - Arancione** |
| 8-Place Watch Box - Black Classic | Uhrenbox 8 Plätze Basic → **Uhrenbox für 8 Uhren - Schwarz Classic** | porta orologi 8 posti → **Porta Orologi 8 Posti - Nero Classic** |
| 8-Place Watch Box - Brown | Uhrenbox 8 Plätze → **Uhrenbox für 8 Uhren - Braun** | porta orologi 8 posti → **Porta Orologi 8 Posti - Marrone** |
| 8-Place XL Watch Box | 8-Fach XL Uhrenbox → **Uhrenbox XL für 8 Uhren** | XL porta orologi 8 posti → **Porta Orologi XL 8 Posti** |
| Watch & Jewelry Box - Turquoise | Schmuck- und Uhrenbox → **Uhren- und Schmuckbox aus Leder - Türkis** | Porta Gioielli → **Porta Orologi e Gioielli in Pelle - Turchese** |
| Watch & Jewelry Box - Brown | Schmuck- und Uhrenbox → **Uhren- und Schmuckbox aus Leder - Braun** | Porta Gioielli → **Porta Orologi e Gioielli in Pelle - Marrone** |
| Watch & Jewelry Box - Orange | Schmuck- und Uhrenbox → **Uhren- und Schmuckbox aus Leder - Orange** | Porta Gioielli → **Porta Orologi e Gioielli in Pelle - Arancione** |
| Nabuk Leather Jewelry Box - Grey | Schmuckkästchen aus Nubukleder → **Schmuckkästchen aus Nubukleder - Grau** | baule portagioielli e orologi → **Portagioie in Nabuk - Grigio** |
| Nabuk Leather Jewelry Box - Yellow | Schmuckkästchen aus Nubukleder → **Schmuckkästchen aus Nubukleder - Gelb** | baule portagioielli e orologi → **Portagioie in Nabuk - Giallo** |
| Nabuk Leather Jewelry Box - Blue | Schmuckkästchen aus Nubukleder → **Schmuckkästchen aus Nubukleder - Blau** | baule portagioielli e orologi → **Portagioie in Nabuk - Blu** |
| Nabuk Leather Jewelry Box - Red | Schmuckkästchen aus Nubukleder → **Schmuckkästchen aus Nubukleder - Rot** | baule portagioielli e orologi → **Portagioie in Nabuk - Rosso** |
| Leather Jewelry Box - Beige & Brown | Schmuckkästchen aus Nubukleder → **Schmuckkästchen aus Leder - Beige & Braun** | baule portagioielli e orologi → **Portagioie in Pelle - Beige e Marrone** |
| Leather Necklace Box | Leder-Halskettenbox → **Halskettenbox aus Leder** | Porta collana → **Porta Collane in Pelle** |
| Necklace Box x Trax NYC | Halsketten-Box x Trax NYC → **Halskettenbox aus Leder x Trax NYC** | Scatola per collana x Trax NYC → **Porta Collane in Pelle x Trax NYC** |
| Jewelry Box x Trax Nyc | Schmuckkästchen x Trax NYC → **Schmuckkästchen aus Leder x Trax NYC** | Portagioie x Trax Nyc → **Portagioie in Pelle x Trax NYC** |
| Gold Trunk mini x Trax Nyc | Schmuckkästchen x Trax NYC → **Schmuckkoffer Mini in Gold x Trax NYC** | Portagioie x Trax Nyc → **Baule Portagioie Mini Oro x Trax NYC** |
| Leather Watch Box - Black | Uhrenbox → **Uhrenbox aus Leder - Schwarz** | Scatola di guardia → **Porta Orologi in Pelle - Nero** |
| Leather Watch Box - Cognac | Uhrenbox → **Uhrenbox aus Leder - Cognac** | Scatola di guardia → **Porta Orologi in Pelle - Cognac** |
| Leather Watch Box - Jeans Blue | Uhrenbox → **Uhrenbox aus Leder - Jeansblau** | Scatola di guardia → **Porta Orologi in Pelle - Blu Jeans** |
| Leather Watch Box - Pastel Blue | Uhrenbox → **Uhrenbox aus Leder - Pastellblau** | Scatola di guardia → **Porta Orologi in Pelle - Blu Pastello** |
| Leather Watch Box - Pastel Pink | Uhrenbox → **Uhrenbox aus Leder - Pastellrosa** | Scatola di guardia → **Porta Orologi in Pelle - Rosa Pastello** |
| Leather Watch Box - Dark Green | Uhrenbox → **Uhrenbox aus Leder - Dunkelgrün** | Scatola di guardia → **Porta Orologi in Pelle - Verde Scuro** |
| Leather Watch Box - Yellow | Uhrenbox → **Uhrenbox aus Leder - Gelb** | Scatola di guardia → **Porta Orologi in Pelle - Giallo** |
| Leather Watch Box - Navy Blue | Uhrenbox → **Uhrenbox aus Leder - Marineblau** | Scatola di guardia → **Porta Orologi in Pelle - Blu Navy** |
| Leather Watch Box - Cognac Suede | Uhrenbox → **Uhrenbox aus Leder - Cognac Wildleder** | Scatola di guardia → **Porta Orologi in Pelle - Cognac Scamosciato** |

### Handbag (24)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| The Mirror Handbag - Nude | Die Spiegelhandtasche → **Handtasche Mirror - Nude** | The Mirror Handbag → **Borsa Mirror - Nude** |
| The Mirror Handbag - Lavender | Die Spiegelhandtasche → **Handtasche Mirror - Lavendel** | The Mirror Handbag → **Borsa Mirror - Lavanda** |
| The Mirror Handbag in Ostrich | Die Spiegelhandtasche aus Straußenleder → **Handtasche Mirror aus Straußenleder** | The Mirror Handbag in struzzo → **Borsa Mirror in Struzzo** |
| The Mirror Handbag - Pink | Die Spiegelhandtasche → **Handtasche Mirror - Rosa** | The Mirror Handbag → **Borsa Mirror - Rosa** |
| The Mirror Handbag - Blue | Die Spiegelhandtasche → **Handtasche Mirror - Blau** | The Mirror Handbag → **Borsa Mirror - Blu** |
| The Mirror Handbag - Black | Die Spiegelhandtasche → **Handtasche Mirror - Schwarz** | The Mirror Handbag → **Borsa Mirror - Nera** |
| Tote Leather Bag | Tote aus Leder → **Shopper aus Leder** | Borsa tote → **Borsa Tote in Pelle** |
| Crochet Handbag - Pink | Gehäkelte Handtasche → **Häkelhandtasche - Rosa** | Borsa all'uncinetto media → **Borsa all'Uncinetto - Rosa** |
| Crochet Handbag - Beige | Gehäkelte Handtasche → **Häkelhandtasche - Beige** | Borsa all'uncinetto media → **Borsa all'Uncinetto - Beige** |
| Crochet Handbag - Blue | Gehäkelte Handtasche → **Häkelhandtasche - Blau** | Borsa all'uncinetto media → **Borsa all'Uncinetto - Blu** |
| Crochet Handbag - Peach | Gehäkelte Handtasche → **Häkelhandtasche - Pfirsich** | Borsa all'uncinetto media → **Borsa all'Uncinetto - Pesca** |
| Crochet Handbag - Purple | Gehäkelte Handtasche → **Häkelhandtasche - Violett** | Borsa all'uncinetto media → **Borsa all'Uncinetto - Viola** |
| Mini Crochet Handbag - Purple | Mini Häkelhandtasche → **Mini Häkelhandtasche - Violett** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Viola** |
| Mini Crochet Handbag - Pink | Mini Häkelhandtasche → **Mini Häkelhandtasche - Rosa** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Rosa** |
| Mini Crochet Handbag - Multicolor Print | Mini Häkelhandtasche → **Mini Häkelhandtasche - Multicolor** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Multicolore** |
| Mini Crochet Handbag - Beige | Mini Häkelhandtasche → **Mini Häkelhandtasche - Beige** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Beige** |
| Mini Crochet Handbag - Peach | Mini Häkelhandtasche → **Mini Häkelhandtasche - Pfirsich** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Pesca** |
| Mini Crochet Handbag - Blue | Mini Häkelhandtasche → **Mini Häkelhandtasche - Blau** | Borsa all'uncinetto mini → **Mini Borsa all'Uncinetto - Blu** |
| Ostrich Mini Trunk Handbag | Milano Handtasche → **Mini Trunk Handtasche aus Straußenleder** | Mini Trunk Handbag → **Mini Borsa Trunk in Struzzo** |
| Vault Bag | Milano Handtasche → **Vault Handtasche aus Leder** | Vault Bag → **Borsa Vault in Pelle** |
| BAG MODEL 017 - Black | TASCHENMODELL 017 → **Handtasche Modell 017 - Schwarz** | BORSA MODELLO 017 → **Borsa Modello 017 - Nera** |
| BAG MODEL 017 - Brown | TASCHENMODELL 017 → **Handtasche Modell 017 - Braun** | BORSA MODELLO 017 → **Borsa Modello 017 - Marrone** |
| BAG MODEL 017 - Light Blue | TASCHENMODELL 017 → **Handtasche Modell 017 - Hellblau** | BORSA MODELLO 017 → **Borsa Modello 017 - Azzurra** |
| BAG MODEL 017 - Pink | TASCHENMODELL 017 → **Handtasche Modell 017 - Rosa** | BORSA MODELLO 017 → **Borsa Modello 017 - Rosa** |

### Sunglasses (11)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Narcos Glasses - Smoke Grey | Narcos-Brille → **Sonnenbrille Narcos - Rauchgrau** | Occhiali da narcos → **Occhiali da Sole Narcos - Grigio Fumo** |
| Narcos Glasses - Bottle Green | Narcos-Brille → **Sonnenbrille Narcos - Flaschengrün** | Occhiali da narcos → **Occhiali da Sole Narcos - Verde Bottiglia** |
| Tortoise Rectangle Sunglasses | Schildpatt-Rechtecksonnenbrille → **Sonnenbrille Rechteckig - Havanna** | Occhiali da sole rettangolari tartarugati → **Occhiali da Sole Rettangolari - Tartaruga** |
| Black Rectangle Sunglasses | Schwarze rechteckige Sonnenbrille → **Sonnenbrille Rechteckig - Schwarz** | Occhiali da Sole Neri Rettangolari → **Occhiali da Sole Rettangolari - Neri** |
| Green Rectangle Sunglasses | Grüne Rechteckige Sonnenbrille → **Sonnenbrille Rechteckig - Grün** | Occhiali da sole rettangolari verdi → **Occhiali da Sole Rettangolari - Verdi** |
| Tortoise Square Sunglasses | Schildpatt-Sonnenbrille mit eckigem Rahmen → **Sonnenbrille Eckig - Havanna** | Occhiali da sole quadrati tartarugati → **Occhiali da Sole Quadrati - Tartaruga** |
| Black Square Sunglasses | Schwarze quadratische Sonnenbrille → **Sonnenbrille Eckig - Schwarz** | Occhiali da sole quadrati neri → **Occhiali da Sole Quadrati - Neri** |
| Grey Square Sunglasses | Graue eckige Sonnenbrille → **Sonnenbrille Eckig - Grau** | Occhiali da sole quadrati grigi → **Occhiali da Sole Quadrati - Grigi** |
| Black Slim Rectangle Sunglasses | Schwarze schmale rechteckige Sonnenbrille → **Sonnenbrille Schmal Rechteckig - Schwarz** | Occhiali da sole neri sottili rettangolari → **Occhiali da Sole Rettangolari Slim - Neri** |
| Black Geometric Sunglasses | Schwarze geometrische Sonnenbrille → **Sonnenbrille Geometrisch - Schwarz** | Occhiali da sole neri geometrici → **Occhiali da Sole Geometrici - Neri** |
| Black Oversized Square Sunglasses | Schwarze Oversized-Sonnenbrille im Quadratform → **Sonnenbrille Oversized Eckig - Schwarz** | Occhiali da sole quadrati neri oversize → **Occhiali da Sole Quadrati Oversize - Neri** |

### Backpack (10)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| SAC - Brown | SACK → **SAC Rucksack aus Leder - Braun** | Marsupio SAC → **Zaino SAC in Pelle - Marrone** |
| SAC - Black | SACK → **SAC Rucksack aus Leder - Schwarz** | Marsupio SAC → **Zaino SAC in Pelle - Nero** |
| SAC - Blue | SACK → **SAC Rucksack aus Leder - Blau** | Marsupio SAC → **Zaino SAC in Pelle - Blu** |
| SAC - Grey | SACK → **SAC Rucksack aus Leder - Grau** | Marsupio SAC → **Zaino SAC in Pelle - Grigio** |
| SAC Alligator - Yellow | SACK → **SAC Rucksack aus Alligatorleder - Gelb** | Marsupio SAC → **Zaino SAC in Alligatore - Giallo** |
| SAC Alligator - Black | SACK → **SAC Rucksack aus Alligatorleder - Schwarz** | Marsupio SAC → **Zaino SAC in Alligatore - Nero** |
| SAC Alligator - Blue | SACK → **SAC Rucksack aus Alligatorleder - Blau** | Marsupio SAC → **Zaino SAC in Alligatore - Blu** |
| SAC Alligator - Green | SACK → **SAC Rucksack aus Alligatorleder - Grün** | Marsupio SAC → **Zaino SAC in Alligatore - Verde** |
| SAC Alligator - Brown | SACK → **SAC Rucksack aus Alligatorleder - Braun** | Marsupio SAC → **Zaino SAC in Alligatore - Marrone** |
| SAC Himalaya Alligator | SACK → **SAC Rucksack aus Alligatorleder - Himalaya** | Marsupio SAC → **Zaino SAC in Alligatore - Himalaya** |

### Leather Tray (9)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Brown Leather Tray | Brauner Taschenleerer aus Leder → **Taschenleerer aus Leder - Braun** | svuotatasche → **Svuotatasche in Pelle - Marrone** |
| Dark Blue Leather Tray | Dunkelblauer Taschenleerer aus Leder → **Taschenleerer aus Leder - Dunkelblau** | svuotatasche → **Svuotatasche in Pelle - Blu Scuro** |
| Yellow and Brown Leather Tray | Gelb/Brauner Taschenleerer aus Leder → **Taschenleerer aus Leder - Gelb & Braun** | svuotatasche → **Svuotatasche in Pelle - Giallo e Marrone** |
| Dark Green Leather Tray | Dunkelgrüner Taschenleerer aus Leder → **Taschenleerer aus Leder - Dunkelgrün** | svuotatasche → **Svuotatasche in Pelle - Verde Scuro** |
| Black and Yellow Leather Tray | Schwarz/Gelber Taschenleerer aus Leder → **Taschenleerer aus Leder - Schwarz & Gelb** | svuotatasche → **Svuotatasche in Pelle - Nero e Giallo** |
| Dark Green and Brown Leather Tray | Dunkelgrün/Brauner Taschenleerer aus Leder → **Taschenleerer aus Leder - Dunkelgrün & Braun** | svuotatasche → **Svuotatasche in Pelle - Verde Scuro e Marrone** |
| Red Leather Tray | Roter Taschenleerer aus Leder → **Taschenleerer aus Leder - Rot** | svuotatasche → **Svuotatasche in Pelle - Rosso** |
| White/Blue Leather Tray | Weiß/blauer Taschenleerer aus Leder → **Taschenleerer aus Leder - Weiß/Blau** | svuotatasche → **Svuotatasche in Pelle - Bianco e Blu** |
| Black Leather Tray | Schwarzer Taschenleerer aus Leder → **Taschenleerer aus Leder - Schwarz** | svuotatasche → **Svuotatasche in Pelle - Nero** |

### Wallet (9)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Blue Alligator Wallet | Blaue Alligator-Geldbörse → **Geldbörse aus Alligatorleder - Blau** | Portafoglio in alligatore blu → **Portafoglio in Alligatore - Blu** |
| Crocodile Wallet - Grey | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Grau** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Grigio** |
| Crocodile Passport Holder | Krokodil-Passhülle → **Passhülle aus Krokodilleder** | Portapassaporto coccodrillo → **Portapassaporto in Coccodrillo** |
| Crocodile Wallet - Cognac | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Cognac** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Cognac** |
| Crocodile Wallet - Light Brown | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Hellbraun** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Marrone Chiaro** |
| Crocodile Wallet - Dark Blue | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Dunkelblau** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Blu Scuro** |
| Crocodile Wallet - Turquoise | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Türkis** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Turchese** |
| Crocodile Wallet - Black/Khaki | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Schwarz/Khaki** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Nero/Kaki** |
| Crocodile Wallet - Chocolate | Krokodil Geldbörse → **Geldbörse aus Krokodilleder - Schokoladenbraun** | Portafoglio coccodrillo → **Portafoglio in Coccodrillo - Cioccolato** |

### Furniture (6)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Table Trunk | Tabellenstamm → **Truhentisch aus Leder** | Tronco del tavolo → **Baule Tavolo in Pelle** |
| Table Trunk - Black | Tabellenstamm → **Truhentisch aus Leder - Schwarz** | Tronco del tavolo → **Baule Tavolo in Pelle - Nero** |
| Blue Leather Pouf | — → **Lederpouf - Blau** | — → **Pouf in Pelle - Blu** |
| Black Leather Pouf | — → **Lederpouf - Schwarz** | — → **Pouf in Pelle - Nero** |
| Brown Leather Pouf | — → **Lederpouf - Braun** | — → **Pouf in Pelle - Marrone** |
| Orange Leather Pouf | — → **Lederpouf - Orange** | — → **Pouf in Pelle - Arancione** |

### Cap (5)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Cotton Cap - Blue | — → **Baseballcap aus Baumwolle - Blau** | — → **Cappellino in Cotone - Blu** |
| Cotton Cap - Black, Pink Logo | — → **Baseballcap aus Baumwolle - Schwarz mit rosa Logo** | — → **Cappellino in Cotone - Nero con Logo Rosa** |
| Cotton Cap - Black | — → **Baseballcap aus Baumwolle - Schwarz** | — → **Cappellino in Cotone - Nero** |
| Cotton Cap - Leopard, Pink Logo | — → **Baseballcap aus Baumwolle - Leopard mit rosa Logo** | — → **Cappellino in Cotone - Leopardo con Logo Rosa** |
| Cotton Cap - Leopard, Black Logo | — → **Baseballcap aus Baumwolle - Leopard mit schwarzem Logo** | — → **Cappellino in Cotone - Leopardo con Logo Nero** |

### T-Shirt (5)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Embroidered T-Shirt | — → **T-Shirt mit besticktem Logo** | — → **T-Shirt con Logo Ricamato** |
| T-Shirt OM | — → **T-Shirt mit OM Monogramm** | — → **T-Shirt con Monogramma OM** |
| T-Shirt OBERNDÖRFER MILANO | — → **T-Shirt OBERNDÖRFER MILANO** | — → **T-Shirt OBERNDÖRFER MILANO** |
| T-Shirt Star patch | — → **T-Shirt mit Sternen-Print** | — → **T-Shirt con Stampa a Stelle** |
| T-Shirt with Logo | — → **T-Shirt mit Logo-Muster** | — → **T-Shirt con Motivo Logo** |

### Belt (4)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Classic Leather Belt - Brown | Krokodilgürtel → **Ledergürtel aus Vollnarbenleder - Braun** | Cintura di coccodrillo → **Cintura in Pelle Pieno Fiore - Marrone** |
| Classic Leather Belt- Handpainted | Krokodilgürtel → **Ledergürtel aus Vollnarbenleder - handbemalt** | Cintura di coccodrillo → **Cintura in Pelle Pieno Fiore - Dipinta a Mano** |
| Classic Leather Belt - Black, Round Buckle | Krokodilgürtel → **Ledergürtel aus Vollnarbenleder - Schwarz, runde Schnalle** | Cintura di coccodrillo → **Cintura in Pelle Pieno Fiore - Nera, Fibbia Tonda** |
| Classic Leather Belt - Black, Squared Buckle | Krokodilgürtel → **Ledergürtel aus Vollnarbenleder - Schwarz, eckige Schnalle** | Cintura di coccodrillo → **Cintura in Pelle Pieno Fiore - Nera, Fibbia Quadrata** |

### Briefcase (4)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Briefcase x Trax NYC | — → **Aktenkoffer aus Leder x Trax NYC** | Valigetta x Trax NYC → **Ventiquattrore in Pelle x Trax NYC** |
| Briefcase - Black | Aktenkoffer → **Aktenkoffer aus Leder - Schwarz** | Ventiquattrore → **Ventiquattrore in Pelle - Nera** |
| Briefcase - Blue | Aktenkoffer → **Aktenkoffer aus Leder - Blau** | Ventiquattrore → **Ventiquattrore in Pelle - Blu** |
| Briefcase - Brown | Aktenkoffer → **Aktenkoffer aus Leder - Braun** | Ventiquattrore → **Ventiquattrore in Pelle - Marrone** |

### Home Accessories (4)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Brown Leather Coaster Set | — → **Untersetzer-Set aus Leder - Braun** | — → **Set di Sottobicchieri in Pelle - Marrone** |
| Black Leather Coaster Set | — → **Untersetzer-Set aus Leder - Schwarz** | — → **Set di Sottobicchieri in Pelle - Nero** |
| Blue Leather Coaster Set | — → **Untersetzer-Set aus Leder - Blau** | — → **Set di Sottobicchieri in Pelle - Blu** |
| Orange Leather Coaster Set | — → **Untersetzer-Set aus Leder - Orange** | — → **Set di Sottobicchieri in Pelle - Arancione** |

### Travel Bag (3)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Leather Belt Bag | Gürteltasche aus Leder → **Gürteltasche aus Leder** | Marsupio → **Marsupio in Pelle** |
| Weekend Bag | Wochenendtasche → **Weekender aus Leder** | Borsa da weekend → **Borsa da Weekend in Pelle** |
| Beauty Bag | Kosmetiktasche → **Beautycase aus Leder** | Borsa di bellezza → **Beauty Case in Pelle** |

### sofa (2)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Leather Sofa - Orange | — → **Ledersofa - Orange** | — → **Divano in Pelle - Arancione** |
| Leather Sofa - Black | — → **Ledersofa - Schwarz** | — → **Divano in Pelle - Nero** |

### Wine Case (1)

| English | German before → after | Italian before → after |
| --- | --- | --- |
| Wine Holder Leather Box | Weinhalter Lederbox → **Weinkiste aus Leder** | Porta vino → **Cassetta Portavino in Pelle** |
