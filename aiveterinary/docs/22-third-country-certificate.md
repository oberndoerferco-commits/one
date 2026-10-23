# Third-country certificate: pre-fill for the EU animal health certificate for pet dogs, cats and ferrets

As of 23 October 2026. This note covers the certificate a pet dog, cat or ferret needs to enter the EU from a third country or territory for a non-commercial movement. It sets out the fields on the model, the legal basis, who may sign, and what our pre-fill does and does not fill in.

**The instrument in force on 2026-10-23** is the model in **Annex III, Part 1 to Commission Implementing Regulation (EU) 2026/705**. That regulation was adopted on 20 March 2026, published in OJ L on 27 March 2026, and applies from 22 April 2026 (Art. 8). It is the model required by **Art. 18(1) of Commission Delegated Regulation (EU) 2026/131**, which also applies from 22 April 2026 (Art. 33). The two other numbers in the brief are not the certificate. **(EU) 2026/132** is a Delegated Regulation amending 2019/2035 on the traceability of kept dogs, cats and ferrets. **(EU) 2026/133** is a Delegated Regulation amending 2020/688 on movements of dogs, cats and ferrets within the Union. Both are delegated acts, not implementing acts. **(EU) No 577/2013 Annex IV** was repealed from 22 April 2026 (Art. 7 IR 2026/705). Under a transition rule, an Annex IV certificate on the old model that was **issued before 1 October 2026** is still accepted **until 31 March 2027** (Art. 6(3) IR 2026/705). Any certificate issued today has to follow the 2026/705 model.

We never issue, sign or send anything. `buildTravelCertificate` builds a checklist and `renderTravelCertificate` prints it in EN, DE or IT. The heading reads "Pre-fill for the official certificate — not a certificate; must be completed and signed by an official/authorised veterinarian". `pack.signed` and `pack.sent` are always `false`.

Implementation: `app/src/travel-certificate.ts`. Tests: `app/test/travel-certificate.test.ts`.

## Sources (all opened 2026-10-23)

| Key | Source | URL |
|---|---|---|
| DR | Commission Delegated Regulation (EU) 2026/131 of 20 January 2026, animal health requirements for non-commercial movement of pet animals (OJ L, 2026/131, 27.3.2026), EN text read in full (Arts. 1–33) | https://publications.europa.eu/resource/celex/32026R0131 · ELI http://data.europa.eu/eli/reg_del/2026/131/oj |
| IR | Commission Implementing Regulation (EU) 2026/705 of 20 March 2026, model identification documents and model declarations for non-commercial movements of pet animals (OJ L, 2026/705, 27.3.2026). EN Arts. 1–8, Annex III Parts 1–2 and Annex V read. DE and IT language versions opened for the official field labels used in the renderer | https://publications.europa.eu/resource/celex/32026R0705 · ELI http://data.europa.eu/eli/reg_impl/2026/705/oj |
| L636 | Commission Implementing Regulation (EU) 2026/636 of 20 March 2026, lists of third countries or territories (Annex I: equivalent rules, so a passport is possible; Annex II: no titration test; Annex III: birds) | https://publications.europa.eu/resource/celex/32026R0636 · ELI http://data.europa.eu/eli/reg_impl/2026/636/oj |
| 132 / 133 | Delegated Regulations (EU) 2026/132 (traceability, amending 2019/2035) and 2026/133 (intra-Union movement, amending 2020/688). Opened only to identify them | https://publications.europa.eu/resource/celex/32026R0132 · https://publications.europa.eu/resource/celex/32026R0133 |
| 620 | Implementing Regulation (EU) 2021/620, consolidated version 02021R0620-20260810, Annex XIX (Member States free from *Echinococcus multilocularis*): Malta (Part I); Finland, Ireland, United Kingdom (Northern Ireland) (Part II) | https://publications.europa.eu/resource/celex/02021R0620-20260810 |
| Cellar | Cellar SPARQL query for acts amending, correcting or consolidating 32026R0705 / 32026R0131. Result: no amendment to 2026/705. 2026/131 has corrigenda R(01)–R(04) (BG 22.6., ES 27.7., LV 11.9., DA 22.10.2026) and none in EN | https://publications.europa.eu/webapi/rdf/sparql |

## Who may issue and sign (DR Art. 19, IR Annex III Part 2 point 6)

- An **official veterinarian of the third country or territory of dispatch**, on the basis of supporting documentation, **or**
- an **authorised veterinarian** (DR Art. 2(1): authorised by the competent authority under Art. 31(2) Reg. (EU) 2017/625), whose certificate is **then endorsed by the competent authority** of the country of dispatch. The "Endorsement by the competent authority" block is "not necessary when the animal health certificate is signed by an official veterinarian".
- The certificate must be issued or endorsed **no more than 10 days before entry** into the Union. For sea transport this is extended by the length of the voyage (DR Art. 19(b)).
- Before signing, the issuing vet verifies the identification (Art. 13), completes the entries listed in Art. 18(2)(a)–(j), and checks that the certified copies of the vaccination details, the titration lab report (where relevant) and the non-commercial declaration are attached (Art. 19(a)(i)–(iv)).

**Consequence for our users (DE, IT, AT, CH clinics):** a vet practising in an EU Member State cannot issue this certificate. Only the third country of dispatch can. An EU-resident animal that goes to a third country and comes back uses its **EU pet passport** (DR Art. 20(b)). The passport has to show a valid rabies vaccination and, unless the country is on the 2026/636 lists, a favourable titration test done before leaving. Animals from Annex I countries of 2026/636 can travel on the Annex II passport model (Art. 20(a)). So for an EU clinic the pre-fill is a **data sheet handed to the issuing vet abroad**, for example for a patient that lives part of the year in a third country. It is never a document an EU clinic signs. Switzerland is a third country but appears on the 2026/636 lists, and the site's travel page says the Swiss passport is used. The pack carries notes `issuer_third_country` and `passport_alternative` that say this.

## The model (IR Annex III Part 1) and what we fill

Labels are given as they appear in the EN model. The DE and IT labels in the renderer follow the DE and IT language versions of IR 2026/705 ("Veterinärbescheinigung für den Eingang in die EU", "Certificato sanitario per l'UE").

### Part I: Details of dispatched consignment

| Box | Model label | Pre-fill | Source |
|---|---|---|---|
| I.1 | Consignor: Name, Address, Tel. | owner name, address, phone | `ctx.owner.name` (fallback `opts.owner.name`), `opts.owner.address`, `opts.owner.phone`. DR Art. 18(2)(d): "name and contact information of the pet owner" |
| I.2 / II.a | Certificate reference No | **not filled**: issued by the competent authority of dispatch (Part 2 point 8) | — |
| I.3, I.4 | Central / local competent authority | not filled | — |
| I.5 | Consignee. Note: "Indicate Member State of first destination" | `opts.destination_member_state` | typed |
| I.6 | Person responsible for the consignment in the EU | not filled | — |
| I.7 | Country of origin (ISO code) | `opts.dispatch_country` (also used in II.b "of … insert name of territory or third country") | typed |
| I.9 | Country of destination | `opts.destination_member_state` | typed |
| I.8, I.10–I.27 | Region, places, date of departure, transport, BCP, CITES, commodity (HS 010619), quantity, packages, "Pets ☐", transit / import | not filled | — |
| I.28 | Identification of the commodities: **Species (scientific name), Sex, Colour, Breed, Identification number, Identification system and location, Date of birth [dd/mm/yyyy]**. Notes: system = transponder or tattoo; number = the alphanumeric code; date of birth "As stated by the owner" | species, sex, breed from `header` (fallback `record.patient`); colour `opts.animal.colour`; id number `ctx.microchip` (fallback `opts.animal.id_code` for a pre-2011 tattoo); system `opts.animal.id_system`; location `opts.animal.id_location`; date of birth `opts.animal.date_of_birth` | DR Art. 18(2)(a)–(b) |

The renderer prints the scientific names given in note (a): *Canis lupus familiaris*, *Felis silvestris catus*, *Mustela putorius furo*. This is a translation of the species value, not an inference.

### Part II: Certification

| Point | Content | Pre-fill |
|---|---|---|
| II.b | "I, the undersigned official veterinarian / veterinarian authorised by the competent authority of … certify that:" | `opts.vet_role` (official / authorised) and `opts.dispatch_country`. Never chosen for the vet |
| II.1 | Five animals or fewer. Or more than five, older than six months, for competitions etc., with evidence | **not filled** |
| II.2 | "show no disease symptoms and are fit for the non-commercial movement on … (date)" | **not filled**: a clinical certification statement |
| II.3 | At least 12 weeks old at rabies vaccination, ≥ 21 days since the primary vaccination completed (DR 2020/688 Annex VII Part 1), revaccinations within validity | — (statement) |
| II.3.1, option 1 | From a country in **Annex II to 2026/636**, directly, via a listed country, or via another country under DR Art. 17(2) (with the transit declaration, Annex V Part 5) | `opts.rabies_option = 'listed_country'` |
| II.3.1, option 2 | From, or transiting, a country **not in Annex I or II to 2026/636**: titration test on a blood sample taken by the authorised vet ≥ 30 days after primary vaccination (or within a valid series) and **not less than 90 days before the date of issue**, ≥ 0.5 IU/ml | `opts.rabies_option = 'titration'` |
| II.3 table | **Transponder or tattoo: alphanumeric code; date of implantation and/or reading** · **Date of vaccination** · **Name and manufacturer of vaccine** · **Batch number** · **Validity of vaccination: from / to** · **Date of the blood sampling** | code `ctx.microchip`; id date `opts.animal.id_date`; vaccination date `opts.rabies.vaccination_date`; vaccine name `opts.rabies.vaccine`, or `ctx.dispensings[i].product` when the vet points at dispensing line `i` (`opts.rabies.dispensing_index`); manufacturer `opts.rabies.manufacturer`; batch `opts.rabies.batch` or `ctx.dispensings[i].batch`; validity from `opts.rabies.valid_from`; validity to `opts.rabies.valid_to` or `ctx.dispensings[i].valid_until`; blood sampling `opts.titration.sample_date` |
| II.4, option 1 | Dogs destined for an *E. multilocularis*-free Member State or zone (Annex XIX to 2021/620), treated under DR 2020/692 Annex XXI | `opts.echinococcus_option = 'treated'` |
| II.4, option 2 | Dogs not treated | `opts.echinococcus_option = 'not_treated'` |
| II.4 table | **Transponder or tattoo number of the dog** · **Name and manufacturer of the product** · **Date [dd/mm/yyyy] and time [00:00] of treatment** · **Administering veterinarian: name in capitals, stamp and signature** | product, manufacturer, date, time, administering vet from `opts.echinococcus.*`. Signature and stamp are never filled |
| II.5 | Owner declared non-commercial movement, **or** owner authorised the movement (signed declaration plus evidence of the owner's own movement) and the owner or authorised person declared non-commercial movement | `opts.declaration_by` (owner / authorised_person); `opts.authorised_person.*` |
| Signature block | Official / authorised veterinarian: Name (capitals), Qualification and title, Address, Telephone, Date, Signature, Stamp | name `ctx.author.name`. Everything else is **not filled** |
| Endorsement | Competent authority: name, qualification, address, phone, date, signature, stamp | not filled |
| Point of entry | Official at the travellers' point of entry: name, address, phone, e-mail, date of checks, signature, stamp | not filled |

Note (12) on the treatment: the product must be given by a veterinarian between 24 and 120 hours before the scheduled entry, and must be an approved medicinal product with praziquantel or an equivalent proven active substance. We print the rule nowhere as a computed time window.

The **titration laboratory and result** are not boxes on the model. The certified copy of the designated laboratory's report is attached (note (6)). `opts.titration.laboratory` and `.result` are optional so the vet can tick off the attachment. They are never `missing`.

### Attachments (rendered as a checklist)

- Certified copy of the identification and vaccination details: note (4). Always.
- Non-commercial declaration, signed by the owner or the authorised person: DR Art. 18(3), IR Annex V Part 2. Always.
- Certified copy of the official lab report on the titration test: note (6). Only when `rabies_option = 'titration'`.
- The owner's signed authorisation of the person carrying out the movement: DR Art. 4, IR Annex V Part 1. Only when `declaration_by = 'authorised_person'`.

### Validity (note (b)), printed as rule text only

The certificate is valid for 10 days from issue (or endorsement) until the documentary and identity checks at the travellers' point of entry. For sea transport this is extended by the length of the voyage. For onward movement it is then valid for six months from those checks, or until the rabies vaccination expires, whichever is earlier (also DR Art. 18(1) second subparagraph). **No date is computed.**

## Required / missing logic

- Always required: owner name, address, phone; dispatch country; Member State of first destination; species, sex, colour, breed, identification number, system, location, date of implantation/reading, date of birth; II.3.1 option; vaccination date, vaccine name, manufacturer, batch, validity from and to; II.5 declarant; vet name and capacity.
- Required only when the vet's own choice makes it required: the blood sampling date (when the titration option is chosen); the II.4 option (dogs only, judged from the species in the header or record); the treatment details (when "treated" is chosen); the authorised person's name (when the authorised person signs the declaration).
- Not boxes, never missing: the animal's name, the titration lab and the result.

## Nothing inferred

- No date of birth from `header.age`. No colour. No identification system assumed from a chip number.
- No rabies vaccine searched for in `record.medications`. The 010 fixture has a DHPPi + Lepto vaccine, and it stays out. Dispensing data is used only from the line the vet points at.
- No validity start (vaccination + 21 days) and no validity end (vaccination + 1 or 3 years) computed. No titration timing check (30 / 90 days), no Echinococcus window (24–120 h), no 10-day or 6-month dates.
- No choice between II.3.1 options, which would need a judgement on the 2026/636 lists and the route. No choice of II.4 option, which would need a judgement that the destination is listed in 2021/620 Annex XIX. No "eligible to travel" judgement.
- Test `no inference` checks that every date in the EN/DE/IT output is a date the vet typed.

## Could not open, or not checked

- **EUR-Lex HTML pages** (`eur-lex.europa.eu/legal-content/...`) were not used. All texts came from the Publications Office cellar (`publications.europa.eu/resource/celex/…`), which returned the OJ XHTML.
- **The 2026/131 corrigenda R(01)–R(04)**: these exist only in BG, ES, LV and DA (per Cellar metadata), so no EN text applies. Their content was not read.
- **Annex V Parts 4–6 of IR 2026/705** (young-animal declaration, transit declaration, language rules): only skimmed. Part 6 language requirements were not checked in detail.
- **DR 2020/692 Annex XXI** (titration test and Echinococcus treatment rules referred to by the model) and **DR 2020/688 Annex VII** (rabies vaccination validity) were not opened. We quote only the certificate's own notes.
- **2026/636 Annexes I and II** (country lists) were opened but are not encoded. The module makes no country judgement, so they are not used.
- **Consolidated 02021R0620-20261101** exists with a future date. The version in force on 2026-10-23 (20260810) was read.
- The **Commission pet-travel web pages** (food.ec.europa.eu) were not opened for this note. Only primary legal texts were used.

## Where the site's text differs from these sources (not edited)

- `site/src/content/animals/travelling-eu-pets.md` says "passports issued under the old model before 22 April 2026 remain valid". That matches DR Art. 31(b)(ii). But IR 2026/705 Art. 6(1)–(2) goes further: old-model passports **issued before 1 January 2028** are deemed compliant. The site's `/travel` page says this correctly ("from 1 January 2028 new passports must follow the new model"), so the article is narrower than the law and than the travel page.
- The article and the `/travel` page list **Norway** among the countries requiring Echinococcus treatment. Annex XIX to 2021/620 (consolidated 2026-08-10) lists only Malta, Finland, Ireland and Northern Ireland. Norway's requirement comes through the EEA or national rules, which this note does not cover. The statement isn't wrong, but its source is not the EU annex the certificate cites.
- `/travel` "Into the EU from a non-EU country" says entry must be "through a travellers' point of entry". DR Art. 15(a) exempts animals coming from Annex I countries of 2026/636, and Art. 20 allows a passport instead of the certificate in two cases. The page states neither exception.
- No page mentions the **transitional acceptance of old-model (577/2013 Annex IV) certificates** issued before 1 October 2026, which are valid until 31 March 2027 (IR Art. 6(3)).
