# Registry export: what the Austrian Heimtierdatenbank and the Italian SINAC ask for

As of 23 October 2026. This note covers what the vet has to give the registry when a dog (or cat) is chipped and registered, when it changes owner, dies or is lost. For **Austria**, the field list is in the law itself: TSchG § 24a(2) lists the data, and § 24a(4) says which of them are mandatory for dogs. Since 1 January 2025, the vet who chips the animal for the first time **must** enter it in the database, for a fee, with the keeper's name, photo-ID data and the chipping date (§ 24a(4c)). For **Italy**, the national decree (DM 2 November 2023) sets the **deadlines** and who registers, but it contains **no field list**. It hands the details to ministerial "istruzioni", which I could not find or open. The Italian field set below therefore comes from the regional forms and pages I could open: Friuli Venezia Giulia (FVG) Modello 1 and 2, the FVG SINAC operating manual, and the Veneto anagrafe page.

We never submit anything to a registry. `buildRegistryEntry` builds a checklist and `renderRegistryEntry` prints it. The first lines say the data is to be entered in the registry and that nothing was sent (`entry.submitted` is always `false`).

Implementation: `app/src/registry-export.ts` (`buildRegistryEntry`, `renderRegistryEntry`). Tests are in `app/test/registry-export.test.ts`.

## Sources (all opened 2026-10-23)

| Key | Source | URL |
|---|---|---|
| TSchG § 24a | Tierschutzgesetz § 24a, consolidated version in force since 01.01.2025 (BGBl. I Nr. 124/2024), RIS | https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20003541&Paragraf=24a |
| TSchG § 13 | § 13(4) Sachkundenachweis from 1 July 2026 | https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20003541&Paragraf=13 |
| TSchG § 44 | Commencement: §§ 13(4)–(5) from 1 July 2026, the rest of BGBl. I 124/2024 from 1 Jan 2025 | https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20003541&Paragraf=44 |
| HDB | Heimtierdatenbank start page and downloads (ID Austria login, chip search) | https://heimtierdatenbank.ehealth.gv.at/ · https://heimtierdatenbank.ehealth.gv.at/Download.aspx |
| HDB-HB | Heimtierdatenbank für Onlinemelder, Benutzerhandbuch v1.7 (last revised 26.06.2023), PDF, 29 pp. | https://heimtierdatenbank.ehealth.gv.at/Downloads/Benutzerhandbuch/Benutzerhandbuch.pdf |
| VG-FAQ | Ministry FAQ "Chippflicht beim Hund" (linked from the HDB start page as "Informationen zur Chip-Pflicht") | https://www.verbrauchergesundheit.gv.at/tiere/faqs/faqhundchip.html |
| OEGV | oesterreich.gv.at, Registrierung von Hunden (last updated 19.02.2026; "Rechtsgrundlagen: § 24a Tierschutzgesetz") | https://www.oesterreich.gv.at/de/themen/reisen_und_freizeit/haustiere/1/Seite.741000 |
| EPN-AT | Europetnet member page for code BMG | https://europetnet.org/europetnet-member/?membercode=BMG |
| KDG § 24 | Kontroll- und Digitalisierungs-Durchführungsgesetz § 24 (names the "Heimtierdatenbank für Hunde und Katzen gemäß § 24a Abs. 6 TSchG") | https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20012480&Paragraf=24 |
| DM | DM Salute 2 novembre 2023, "Modalità tecniche e operative per l'implementazione del SINAC" (GU SG n. 294 of 18-12-2023, 23A06843), arts. 1–13 read one by one on gazzettaufficiale.it | https://www.gazzettaufficiale.it/eli/id/2023/12/18/23A06843/sg |
| D.Lgs 134 | D.Lgs. 5 agosto 2022 n. 134, art. 16 (read via WebFetch, summary only) | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2022-08-05;134~art16 |
| FVG | Regione FVG, Cani: registrazione al SINAC (last updated 13.11.2025) | https://www.regione.fvg.it/rafvg/cms/RAFVG/salute-sociale/igiene-urbana-veterinaria/FOGLIA1/ |
| FVG-MAN | FVG zip "Approvazione manuale SINAC FVG": decreto of approval, *Manuale operativo SINAC FVG rev. 1.3*, Modello 1 (identification and registration), Modello 2 (changes) | https://www.regione.fvg.it/rafvg/export/sites/default/RAFVG/salute-sociale/igiene-urbana-veterinaria/FOGLIA1/allegati/20251113_APPROVAZIONE_MANUALE_SINAC_FVG_SINAC_FVG.zip |
| VEN | Regione Veneto, Anagrafe canina (last updated 24.07.2026) | https://www.regione.veneto.it/web/rete-degli-urp-del-veneto/anagrafe-canina |

Modello 1 and 2 are Word 97 files. LibreOffice would not load them, so I pulled the text out directly. Some short fill-in labels between apostrophes were lost (for example the owner's first-name and date-of-birth blanks), and all the headings and boxes were readable.

### Could not open, or not found

- **A "Heimtierdatenbank-Verordnung"**: RIS (Bundesrecht konsolidiert) has none. Title and full-text searches for "Heimtierdatenbank", "Heimtier", "Hundekennzeichnung" and "Microchipnummer" return only TSchG §§ 24a, 31, 31b and KDG § 24. oesterreich.gv.at gives § 24a TSchG as the only legal basis, and the HDB download page links only the TSchG. As far as I could find, no separate ordinance is in force, and the field list is § 24a(2) itself.
- **gesundheit.gv.at**: the guessed search URL returned 404, and I found no HDB page there. The ministry FAQ (VG-FAQ) and oesterreich.gv.at were used instead.
- **The HDB data-entry screens**: these sit behind an ID Austria login. The handbook shows them only as screenshots, so the exact on-screen field labels and asterisks were not readable. The handbook text names chip type (ISO/Andere), chip code, registration number, and name, breed and sex in the search result.
- **The SINAC national "istruzioni"** (decreto of the Director-General for animal health, DM art. 1 c. 3, due by 31 March 2024 under art. 12 c. 1): not found on salute.gov.it or vetinfo.it by search. The DM applies 120 days after they are published (art. 12 c. 4), and I could not verify that publication date.
- **sinac.vetinfo.it / anagrafecanina.vetinfo.it**: these are JavaScript-only apps, so curl got no content. The guessed vetinfo.it info pages (normativa, FAQ) returned 404.
- **GU full PDF** (`/eli/gu/2023/12/18/294/sg/pdf`) and the print view: the connection was reset on every try. The articles were read one at a time instead.
- **Regione Piemonte SINAC page**: the connection was reset (curl) and WebFetch got 503. **Regione Lombardia** page: the content is rendered by JavaScript, so there was no text.
- **Reg. delegati (UE) 2026/131–133** (2026/132 = traceability of dogs, cats and ferrets kept), cited on the Veneto page: not opened. If 2026/132 sets an EU-wide data set, it may change both field lists. **Open item.**

## Austria: Heimtierdatenbank (TSchG § 24a)

**Scope.** All dogs (§ 24a(3)), and cats used or meant for breeding (§ 24a(3a), (4a)). A registration in a Land or municipal dog register does not replace the HDB entry (VG-FAQ).

**Who may register** (§ 24a(4) Z 1–3, the same for breeding cats in (4a)):
1. the keeper, online (ID Austria / Handy-Signatur, free of charge per VG-FAQ);
2. the authority (Bezirksverwaltungsbehörde), after the keeper reports the data to it (VG-FAQ: fees may apply; many municipalities also have access);
3. **on the keeper's behalf, the private-practice vet who chips or vaccinates the animal**, or another "Meldestelle". VG-FAQ names the private databases with an interface to the HDB (Animaldata, Petcard, PawID, IFTA) and shelters. A private-database entry reaches the HDB only once the extra HDB data are complete, which can take up to a week.

**Vet duty at first chipping** (§ 24a(4c), in force 1 Jan 2025): the vet must enter the dog or breeding cat, for a fee, with the keeper's **name** and **type and number of an official photo ID** (§ 24a(2) Z 1 lit a, b) and the **date of first marking**. The entry can go straight into the HDB or through an existing register. The keeper must show a photo ID. Whoever makes the entry on someone's behalf passes the **registration number** to the keeper (§ 24a(5)).

**Fields** (§ 24a(2); M = mandatory for dogs under § 24a(4); opt = may be reported):

| Field | § 24a(2) | Dogs | In `buildRegistryEntry` |
|---|---|---|---|
| Keeper name (and owner/breeder if different) | Z 1 lit a | M | `ctx.owner.name` |
| Type and number of official photo ID | Z 1 lit b | M | `opts.owner.id_document_type/number` |
| Delivery address | Z 1 lit c | M | `opts.owner.address` |
| Contact data | Z 1 lit d | M | `opts.owner.contact` |
| Keeper's date of birth | Z 1 lit e | M | `opts.owner.date_of_birth` |
| Date keeping began | Z 1 lit f | M | `opts.owner.keeping_since` |
| Date of handover + new keeper (name, photo-ID number), or date of death | Z 1 lit g | M | `opts.event_date`, `opts.new_owner.*` |
| Breeder status (§ 31b) | Z 1 lit h | opt | not modelled |
| Sachkundenachweis (§ 13(4), from 1 July 2026) | Z 1 lit i | M | `opts.owner.competence_certificate` (as typed, e.g. "not required: keeping since 2024") |
| Breed | Z 2 lit a | M | header (record fallback) |
| Sex | Z 2 lit b | M | header (record fallback) |
| Date of birth (at least the year) | Z 2 lit c | M | `opts.animal.date_of_birth`, **never derived from age** |
| Chip number, and the parents' chips if known | Z 2 lit d | M | `ctx.microchip`; parents optional |
| Interventions on body parts for veterinary reasons: exact reason + vet (or other reasons, e.g. seizure) | Z 2 lit e | M (if any) | `opts.animal.interventions`, optional, **never from record.treatments** |
| Country of birth | Z 2 lit f | M | `opts.animal.country_of_birth` |
| Pet passport number | Z 2 lit g | opt | `opts.animal.pet_passport` |
| Date of last rabies vaccination + vaccine | Z 2 lit h | opt | `opts.animal.rabies_*`, **never from record.medications** |
| Qualzucht commission opinion (breeding animals) | Z 2 lit i | M (if breeding) | not modelled |
| Orders under § 35(6a) + date of any procedure to prevent reproduction | Z 2 lit j | M (if any) | `opts.animal.neutering_date`, optional, **never from neuter_status** |

HDB-HB adds the **chip type** (ISO / Andere; ISO = 15 digits), the **animal's name** (shown in every search result together with breed and sex) and the **registration number**. The registration number confirms a registration. A change of keeper creates a new one (§ 24a(5), (6)), and the new keeper can take the animal over only with the current number (HDB-HB pp. 24–28).

**Deadlines.** Puppies must be chipped by 3 months of age and in any case before the first handover (§ 24a(3)). Registration is due **within one month** of chipping, entry into Austria or taking over an already chipped dog, and in any case before passing it on (§ 24a(4)). Every change must be reported (§ 24a(6)), and the law gives no day count. A death reported to the authority with a death certificate leads to deletion of the animal data after 2 years. If a death is never reported, the record is deleted automatically 20 years after the dog's birth year (§ 24a(6)). **Loss:** § 24a defines no loss field, and the HDB handbook describes no loss entry. Fines for non-registration are up to €3,750, or €7,500 for a repeat offence (§ 38 per VG-FAQ; § 38 itself was not opened).

## Italy: SINAC (D.Lgs. 134/2022 art. 16, DM 2 novembre 2023)

**Legal frame.** D.Lgs. 134/2022 art. 16 requires owners and operators to identify companion animals, register them in the SINAC section of the BDN and report changes. The timing and methods are left to a decree. That decree is the **DM 2.11.2023**, which in turn hands the detailed instructions, including number series and data, to a Director-General decree (art. 1 c. 3; art. 4 c. 1).

**Who registers** (DM art. 3):
- Identification and registration are done **by the veterinarian** (art. 3 c. 2), except in cases set out in the instructions.
- Animals in Annex I Part A of Reg. (EU) 2016/429 (**dogs, cats, ferrets**) are identified by ISO transponder and registered in SINAC by the **official vet or an authorised private vet** (art. 8 D.Lgs. 136/2022) **within 60 days of birth and in any case before any transfer** (art. 3 c. 4).
- The **owner or keeper may enter changes personally** (transfer, movement, death, loss, finding) in SINAC through SPID/CIE, unless the region provides otherwise (art. 3 c. 3).
- Companion animals brought in from abroad and staying more than 30 days are registered in SINAC (art. 3 c. 8).

**Deadlines** (DM art. 3 c. 3): transfer of ownership, movement and death within **7 days** of the event; loss and finding "as soon as possible and in any case within **48 hours**". Regions add their own rules. FVG (FVG page): register by day 60 of life, or within 10 days of acquisition, always before handover. Loss and theft go to the municipality within 5 days, with the police report for a theft. A handover goes within 10 days, with the new owner's details. A death goes within 30 days with the vet's certificate, unless an accredited private vet has already recorded it online. A change of residence goes within 30 days. Veneto (VEN): the vet registers at chipping or within 48 hours, every change goes to the ULSS within 15 days, and arrival from another region or abroad within 10 days.

**Fields** (no national list was opened; F1 = FVG Modello 1, F2 = FVG Modello 2, V = Veneto page):

| Event | Field | Source | In `buildRegistryEntry` |
|---|---|---|---|
| Registration | Microchip code ("codice anagrafico") applied / already present | F1; DM art. 3 c. 4 (ISO) | `ctx.microchip` |
| Registration | Species | V | header |
| Registration | Breed, sex, size (taglia), date **or year** of birth | F1, V | header (breed, sex); `opts.animal.size`, `opts.animal.date_of_birth` |
| Registration | Coat (mantello), notes / distinguishing marks | F1 | `opts.animal.coat`, `opts.animal.marks` (marks optional) |
| Registration | Owner surname and name, codice fiscale, residence | F1, V ("dati anagrafici") | `ctx.owner.name`, `ctx.owner.tax_id`, `opts.owner.address` |
| Registration | Event: acquisition / birth from own breeding animal | F1 | `opts.origin` |
| Registration | Place and date; certifying vet (signature, stamp with codice fiscale) | F1 | `opts.event_date`, `ctx.author.name` (Ordine registration printed if present, not required) |
| Change of owner | Date; chip; outgoing owner (name, CF); new owner surname/name, CF, comune of residence, e-mail | F2 1.1 + "parte riservata" | `opts.event_date`, `opts.new_owner.*` (e-mail optional) |
| Death | Date; chip; owner; vet's or collection service's certificate | F2 1.3 | `opts.death_certificate` |
| Loss | Date; chip; owner; place lost | F2 1.4 | `opts.loss.place` |
| Theft | as for loss + copy of the police report | F2 1.5; FVG page | `opts.loss.theft`, `opts.loss.police_report` (required only if theft) |

The FVG manual (rev. 1.3) lists the SINAC events: registration (ISC in-region / ACQ from outside), change of location, chip application, custody transfer, change of ownership, loss/theft, finding, death, bite, and administrative exit. It also shows that an authorised private vet in FVG can enter registrations, deaths, chip applications and health events, but not changes of ownership or losses, which go to the municipality (FVG page). So the IT checklist is something the vet hands to whoever enters it, and the rendered note says regional routes differ.

## What `buildRegistryEntry` does

- `registry`: `'AT-HDB' | 'IT-SINAC'`. `opts.event`: `'first_registration' | 'change_of_owner' | 'death' | 'loss'`, chosen by the vet and never derived.
- Each field is `{ key, value: { value, source } | null, required, basis }`. `source` is a path into `header`, `record` (signalment fallback only), `ctx` or `opts`. `basis` cites the paragraph or form above.
- `missing` lists the required fields that are null. For a theft (`opts.loss.theft === true`), the police report becomes required.
- `notes` holds scope and procedure notes: vet duty at first chipping (AT), cats only if used for breeding (AT), a new registration number on a handover (AT), deletion after death (AT), no loss field (AT), regional rules and the unopened national list (IT), species scope (IT), and a country mismatch between the visit context and the registry.
- Deadlines are printed **as published rules**. No due date is computed from the event date.
- Not inferred: date of birth from age, breed from notes, neutering date from neuter status, rabies date from a vaccine in the record, interventions from procedures in the record, the event type itself.
- `renderRegistryEntry(entry, lang)` prints a tick-box checklist in `de` (default for AT), `it` (default for IT) or `en`. Its first lines are "Data to enter in…" and a bold "Nothing was sent to any registry". Missing values are flagged inline (▲) and listed at the end.

## Cross-check with `site/src/pages/registry.astro` (and `de/`, `it/`)

Not edited. Each discrepancy is listed for whoever owns the site pages:

1. **Europetnet and Austria (EN/DE/IT pages)**: the pages say the Italian and Austrian federal registries are not Europetnet members. Europetnet's member page lists "Bundesministerium für Gesundheit (BMG)" as a **verified (associate) member** with the HDB search URL, and the HDB start page links to it (EPN-AT, HDB). The Italian half of the claim was not checked.
2. **"Immediately" (EN) / „unverzüglich" (DE) for AT changes**: § 24a(6) says only "Jede Änderung ist … zu melden". The words "unverzüglich" and "immediately" do not appear in § 24a. "No day count" is correct, but the quoted word has no source.
3. **AT Sachkundenachweis "if the Land requires one"**: under § 13(4) TSchG (in force 1 July 2026, § 44) the requirement is **federal**. Anyone who wants to keep a dog must complete a course of at least 4 × 60 min before keeping begins, plus a 2-hour practical unit within one year for dogs aged 6 months or older. The Land only determines where the course is taken. § 24a(4) makes the certificate mandatory HDB data for dogs.
4. **AT "who registers" omits Meldestellen**: § 24a(4) Z 3 and VG-FAQ also allow "sonstige Meldestellen". These are private databases with an HDB interface (Animaldata, Petcard, PawID, IFTA) and shelters. The page's line "Entries in a private database … do not count" is only half right: an entry counts once the database has forwarded the complete HDB data set.
5. **AT loss ("enter the loss in the Heimtierdatenbank")**: neither § 24a nor the HDB user handbook v1.7 describes a loss entry. This may exist behind the login, but it is unverified.
6. **IT deadlines "vary by region"**: the DM 2.11.2023 sets a **national baseline** the page does not mention. Vet registration is due within 60 days of birth and before any transfer, transfers, movements and deaths within 7 days, and loss and finding within 48 hours (art. 3 c. 3–4). Regional limits are on top of that.
7. **IT cats "depend on the region"**: DM art. 3 c. 4 applies to all Annex I Part A species (dogs, cats, ferrets). Read literally, cats and ferrets are to be identified and registered nationally. Veneto's page (updated July 2026) still describes cats as only for animals from outside the region or needing a passport, and the DM's applicability depends on the istruzioni (art. 12 c. 4). **Flag for verification, not a confirmed error.**
8. **IT owner self-service**: the page lists loss, found and death reports through the SINAC citizen portal. DM art. 3 c. 3 also covers **transfer of ownership and movement**, unless the region says otherwise. In FVG, losses, handovers and moves go to the **municipality** (FVG page).
9. **Minor**: FVG public-vet fee is "€5 + ENPAV" (the page says €5). Veneto: changes within 15 days and registration by the vet within 48 hours of chipping (the page only gives the 10-day arrival rule). The oesterreich.gv.at link now redirects to `/de/themen/...` and still works.

Confirmed as on the page: the AT 1-month registration window, 3-month chipping and "before passing on" (§ 24a(3), (4)); the vet's registration duty since 2025, for a fee (§ 24a(4c)); cats only if used for breeding; fines up to €3,750 (VG-FAQ); the FVG figures (60 days / 10 days / before handover; owner change 10, address 30, loss 5, death 30 days).
