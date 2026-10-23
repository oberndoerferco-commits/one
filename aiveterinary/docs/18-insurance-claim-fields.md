# Pet-insurance claim fields: what the forms and invoice rules ask the practice for

As of 23 October 2026. I opened the public claim forms, claim pages and policy-condition clauses of 15 insurers active in Germany, Austria and Italy, plus § 7 GOT. They agree on a small core. **Diagnosis, treatment date(s), the animal's identity and an itemised invoice** are wanted almost everywhere. The **microchip number** is the identity field that German and Italian insurers name explicitly. Italian forms also want the **onset date** and a **dated, stamped vet statement**. Breed and date of birth are asked by **no claim form** I could open: they sit on the policy (application form), not on the claim. "Pre-existing?" is never a box for the vet on any form I opened. It is the insurer's decision, made from the history it requests. No source asks for a diagnosis code.

German insurers do **not** list the GOT **factor** as a required invoice field in any source opened. § 7(4) GOT requires the "laufende Nummer" of each service and the invoice amount, not the multiplier. Insurers still reimburse "bis zum 2-/4-fachen Satz" (Allianz, BarmeniaGothaer, AGILA), so they need the factor to apply their cap. `buildClaimPack` therefore flags a missing factor per line in DE, alongside a missing GOT number, and this document records that the flag goes beyond the opened rules.

Implementation: `app/src/claim.ts` (`buildClaimPack`, `renderClaimSummary`), tests in `app/test/claim.test.ts`.

## Sources (all opened 2026-10-23)

| Key | Insurer / law | Document | URL |
|---|---|---|---|
| GOT | Gebührenordnung für Tierärztinnen und Tierärzte (GOT 2022) | § 7 Abs. 4 (Rechnung) | https://www.gesetze-im-internet.de/got_2022/__7.html |
| FIG | Figo (petplan.de now redirects to figopet.de, "FIGO Tierversicherung, by AGILA") | Schadenmeldung: Rechnung erstatten lassen; Online-Schadenmeldung (checklist) | https://figopet.de/kundenservice/schadenmeldung-bestehendes-produkt/ · https://figopet.de/kundenservice/online-schadenmeldung/ |
| AG-K | AGILA Haustierversicherung | Rechnung einreichen & Schaden melden (customer page) | https://www.agila.de/service/rechnungen-schaeden |
| AG-V | AGILA | Tierarztportal: Rechnung per Online-Formular (direct billing by the practice) | https://www.agila.de/kontakt/tierarztportal/online-formular |
| AG-B | AGILA | Vertragswerk DE (AHKV/BB 11/2025, 2026-07-15) and AT (AHKV/BB 09/2026): invoice clause | https://www.agila.de/images/pdf/Vertragswerke/2026-07-15_de_agila_vertragswerk_barrierefrei.pdf · https://www.agila.de/images/pdf/Vertragswerke/agila-vertragswerk-at-2026-09.pdf |
| BG | BarmeniaGothaer (barmenia.de redirects to barmeniagothaer.de) | AVB Tier-KV A3688-03 § 4.2.1; AVB Hunde-OP/Unfall A3685-03 § 7.2.1 "Vorlage der Rechnung" | https://cdn.barmeniagothaer.de/barmeniagothaer/media/tiere_freizeit/tiere/tierkranken/barmeniagothaer-avb-tier-kv-a3688-03.pdf · https://cdn.barmeniagothaer.de/barmeniagothaer/media/tiere_freizeit/tiere/tierkranken/barmeniagothaer-avb-hunde-op-unfall-a3685-03.pdf |
| HM | HanseMerkur | FAQ Tier-Krankenversicherung ("Welche Daten müssen auf der Tierarzt-Rechnung immer stehen?") | https://www.hansemerkur.de/faq/tier-krankenversicherung |
| UE | Uelzener | OP-/KV-Schaden melden (online form fields and FAQ) | https://cx.uelzener.de/public/e/l//service-op-kv-schaden-melden |
| AZ-DE | Allianz Deutschland | Leistung beantragen (page); product sheet Tierkrankenversicherung Hunde MMS--2338Z0 (03-02-2026) | https://www.allianz.de/service/schaden-melden/tierkranken/ · https://goa-cdeportale.allianz.de/MMS/--2/MMS--2338Z0.pdf.open.pdf |
| HE-AT | Helvetia Österreich | PetCare Unfall-/Kranken-/Vorsorgebericht (fillable PDF, UHs 12 07.15) | https://www.helvetia.com/content/dam/os/at/web/dokumente/schadenformulare/PetCare.pdf |
| AZ-AT | Allianz Österreich (Petplan) | Antrag Petplan Tierversicherung (application, not a claim form); IPID 2025 Petplan | https://www.allianz.at/content/dam/onemarketing/cee/azat/makler-pdf/petplan/Antrag-Petplan-Tierversicherung.pdf · https://www.allianz.at/content/dam/onemarketing/cee/azat/privat_pdf/wohnen---recht/IPID-2025-Petplan.pdf |
| CT | ConTe.it (cane e gatto) | Questionario medico veterinario (PDF, 12/2025) | https://canegatto.conte.it/hubfs/Questionario%20Veterinario%20ConTe%20Cane%20e%20Gatto%20(1).pdf |
| PO | Poste Assicura | Linea Protezione Animali Domestici, Rimborso spese veterinarie (Mod. 63.5, ed. febbraio 2026) | https://www.media.poste.it/3fdd4126-39eb-4e81-b8b6-c59dc4a6be58/file/rimborso-spese-veterinarie |
| UN | UnipolSai (claims by UniSalute) | C@NE & G@TTO ISFAST, Art. 5.10–5.11.2 (Mod. 7300, **ed. 30/09/2018**, old) | https://www.unipol.it/api/pub/ueba/download/doc/v1/fascicoli/c6ff30bb-b8ea-4987-8f4d-4cea70d0294c |
| NI | Net Insurance | MyPet, Condizioni Art. 31 "Obblighi dell'Assicurato in caso di Sinistro" | https://www.netinsurance.it/wp-content/uploads/2024/02/Set-Informativo_MyPet-062023.pdf |
| GE | Generali Italia | Immagina Adesso – Modulo CUCCIOLO (ed. 28.06.2025, agg. 01.10.2026), In agilità: spese veterinarie, norme in caso di sinistro | https://www.generali.it/cmsassets/site/bcb9ce24-2d3a-4b6d-a456-943527379964/ORI_Immagina_Adesso_CUCCIOLO_ed._28.06.2025_agg._01.10.2026.pdf |
| QX | Quixa (AXA Italia) | Modulo di denuncia Quixa Smart (pet) | https://www.quixa.it/wp-content/documents/modulo_di_denuncia_quixa_smart.pdf |

Helvetia AT and ConTe returned "access denied" / 403 to curl. I read both through the WebFetch download and extracted the text with pypdf. gesetze-im-internet.de reset curl connections, and § 7 was read through WebFetch.

### Could not open (not used)

- **DA Direkt**: `dadirekt.de` reset every connection (curl), and WebFetch got 503.
- **Prima** (`prima.it/assicurazione-cane-gatto`): 403 to both curl and WebFetch.
- **Petplan Deutschland**: there is no Petplan DE site any more. `petplan.de` redirects to Figo (FIG).
- **Pet Insurance Italia / Animalia** (`petinsuranceitalia.it`): the proxy tunnel failed (502).
- **Helvetia Italia** (pet page): 504. **Allianz Italia**: the guessed pet-insurance URL returned 404, and I found no other link.
- **Allianz DE online claim form** (`/service/formular/?form=tkv_einreichen`) and **HanseMerkur upload form** are JavaScript apps, so their field lists were not readable. Only the pages around them were used (AZ-DE, HM FAQ).
- **Santévet Italia FAQ** renders by JavaScript, so there was no content.
- **GOT § 2** (fee range and factor) and the GOT full text returned 503. The factor range "1- bis 3-fach (§ 2 GOT)" already cited in `render.ts` was **not** re-verified today.
- **Deutsche Familienversicherung AVB**: 403 (not in the target list).
- **Barmenia old URL** (`barmenia.de/.../leistungsfall/tierversicherung.xhtml`): 404, replaced by BG.

## Fields asked, and what the claim pack does with them

**✓** = asked/required by the source. **(✓)** = implied (eligibility, or "documents that support the diagnosis"). Ours: **R** = filled from the approved record, **H** = from the patient header (record signalment as fallback), **C** = from `VisitContext`, **V** = typed by the vet at the claim step (`ClaimOpts`), never derived, **O** = owner's part of the form, not in the pack, **–** = not adopted. Everything R/H/C/V that is absent is `null` and listed in `pack.missing`.

| Field | GOT | FIG | AG-K/V | AG-B | BG | HM | UE | HE-AT | CT | PO | UN | NI | GE | QX | Ours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Owner name (address) | | ✓ (address) | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | | | C (`owner.name`); address O |
| Policy / customer number | | ✓ | ✓ | | | | ✓ | ✓ | ✓ | | ✓ | ✓ | | | V (`policy_number`, usually O) |
| Animal name | | | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | | | | | | H |
| Species | ✓ | | | | | | | | | | | | | | H |
| Breed | | | | | | | | | | | | | | | H (asked only on the application, AZ-AT) |
| Date of birth | | | | | | | | | | | | | | | V (application only, AZ-AT; the header has age, not DOB) |
| Microchip / tattoo on the invoice or claim | | ✓ | | | ✓ | ✓ | | ✓ | ✓ | (✓) | ✓ | ✓ | ✓ (identity) | | C (`microchip`) |
| Diagnosis / reason for consultation | ✓ | ✓ | ✓ (optional field) | ✓ | ✓ | ✓ | | | ✓ (patologia / sospetta) | (✓) certificato | (✓) | ✓ | ✓ | ✓ | R (`assessment.text`) or V (`diagnosis`); differentials never promoted |
| Accident or illness | | | | | | | | ✓ | ✓ | | | | | | V (`condition_type`) |
| Onset / first-symptom date | | | | | | | | ✓ | ✓ | | | | | ✓ | V (`first_symptom_date`) |
| First visit for this problem | | | | | | | | | ✓ | | | | | | – (covered by treatment dates when typed) |
| Short history / course | | | | | | | | ✓ | ✓ | | | ✓ | ✓ | ✓ | R (presenting complaint, performed treatments and diagnostics) |
| Date(s) of service | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ (first) | | ✓ | | | | | | V (`visit_date`, line dates) |
| Outpatient / day hospital / inpatient | | | | | | | | | ✓ | | | | | | V (`setting`) |
| Surgery marked "OP" | | | ✓ | | | | | | | | | | | | V (`surgery`) |
| Itemised services | ✓ | ✓ (spezifiziert) | | ✓ | ✓ | ✓ | | | ✓ | | (✓) distinte | | ✓ | | V (`invoice.lines`) |
| GOT number per service (DE) | ✓ | | | (✓) "beruht auf GOT" | ✓ | ✓ | | | | | | | | | V; flagged per line in DE |
| GOT factor per service (DE) | | | | | | | | | | | | | | | V; flagged per line in DE (no opened source requires it; caps at 2-/4-fold need it) |
| Medicines and consumables shown separately | ✓ | | | ✓ | | ✓ | | | | | | | | | R (medication table, reused from `renderMedicationTable`); prices V |
| Invoice amount | ✓ | | ✓ | ✓ | | ✓ | | | | ✓ | ✓ | ✓ (quietanzate) | ✓ | ✓ | V (`invoice.total`, string as typed, never summed) |
| VAT | ✓ | | | | | ✓ | | | | | | | | | V (`invoice.vat`, as typed) |
| Invoice number and date | | | ✓ | | | | | | | | | | | | V |
| Pre-existing conditions | | | | | | | ✓ (owner's Krankmeldung) | | | (exclusion) | | | | | V (`pre_existing`), never derived; application AZ-AT asks the owner |
| Vet name / letterhead / stamp | | | ✓ (practice e-mail, partner no.) | | | | | ✓ (name, address) | ✓ (nominativo e timbro) | ✓ (timbrare) | | ✓ (carta intestata) | ✓ (formulario or letterhead) | ✓ (relazione) | C (`author`); practice name and address V; stamp and signature line printed blank |
| Copies of lab / imaging reports | | | | | ✓ (on request) | | ✓ (on request) | | ✓ | | ✓ | ✓ | ✓ | ✓ | – (attachments; not in the pack) |
| Health booklet / registry certificate (IT) | | | | | | | | | | (✓) | | ✓ | (✓) ENCI on death | | – |
| Other insurance for the same event | | | | | ✓ | | | ✓ | | | ✓ | | | | O |
| Payee / assignment to the practice | | | ✓ | | ✓ (Direktabrechnung) | ✓ | ✓ | | | | | | | | – |
| One invoice per animal, no handwritten notes | | ✓ | ✓ | | | | | | | | | | | | – (the summary is printed, not annotated) |

### What the sources say in their own words (short)

- **§ 7(4) GOT**: the invoice must state at least "das Datum der Erbringung der Leistung", "die Tierart", "die Diagnose oder den Grund der Konsultation", "die berechnete Leistung mit Angabe der laufenden Nummer", "den Rechnungsbetrag" and "die Umsatzsteuer". Outlays under paragraph 2 not covered by the fees are shown separately, and the invoice is itemised on request. The factor is not in this list.
- **BG** (both AVBs): "Aus der Rechnung muss ersichtlich sein – der Name des Halters …; – der Name und Beschreibung des Tieres (Chip/Tätowierungsnummer) …; – die Diagnose; – die berechnete Leistungsposition gemäß der geltenden GOT; – das Datum der erbrachten Leistungen." Lab and imaging documents are submitted on request.
- **AG-B** (DE and AT): the invoice "muss den Namen des versicherten Hundes [der Katze], das Datum der erbrachten Leistung, die Diagnose, die berechneten Leistungen unter Angabe der Einzelpositionen mit entsprechenden Preisen, die Kosten für Verbrauchsmaterial und Arzneimittel sowie den Rechnungsbetrag enthalten und auf der … GOT beruhen". The Austrian contract also refers to the German GOT.
- **HM**: "Versicherungsnehmer Daten, Tierdaten (Name, Chip-Nummer), Behandlungsdatum, Diagnose/Befund, berechnete Leistung mit Angabe GOT-Ziffer, Kosten für Verbrauchsmaterial und Medikamente, Rechnungsbetrag und Mehrwertsteuer."
- **FIG**: the chip number must be on the original invoice, together with the owner's address and "Diagnose/Behandlungsgrund". Handwritten notes on the invoice are not accepted.
- **AG-K**: the word "Operation" or "OP" must be on surgery invoices. Each invoice covers one animal, with no handwritten notes. **AG-V** (practice direct billing) asks for: contract no., practice partner no. (optional), owner's first and last name, an assignment confirmation, practice e-mail, animal name, invoice no., invoice date, treatment date, "Diagnose / Befund (optional)", gross amount, payee, and the invoice file.
- **UE**: partner/contract no., first name, surname, e-mail, animal name, "Das erste Behandlungsdatum der eingereichten Rechnung", then the upload. A "Krankheitsbericht" for the vet is sent only on request.
- **HE-AT**: polizza and claim no., owner, chip number, date and time of the accident or illness, description of the course, injured body parts, the treating vet's name and address, and the owner's signature with release of the vet from confidentiality.
- **CT**: policy, animal name, microchip, claim date, "INFORTUNIO occorso il / MALATTIA insorta il", "DATA PRIMA VISITA", description of lesions or symptoms and "patologia / sospetta patologia", services and treatment, "AMBULATORIALE il / DAY HOSPITAL il / RICOVERO dal … al", and "NOMINATIVO E TIMBRO DEL VETERINARIO". Attachments: invoices, the clinical record with the diagnosis and the onset date, and the exams.
- **QX**: the vet's prescription "contenente la diagnosi, la data di insorgenza e una breve anamnesi", a detailed vet report for surgery, clinical documentation, and invoices.
- **NI**: "rapporto circostanziato a cura del veterinario, su carta intestata", the clinical record "riportante n. microchip", fiscal receipts, the libretto sanitario and the registry document.
- **GE**: the vet writes "un rapporto circostanziato sulle cause e le modalità del Sinistro" on Generali's form or on letterhead. The documentation must show "l'identità dell'animale" and "l'indicazione precisa delle singole voci di spesa e il relativo importo".
- **PO**: for out-of-network claims, the "Certificato del medico veterinario" and copies of the invoices. Microchip and registry entry are eligibility conditions for dogs.
- **UN** (2018 edition): a signed claim form, veterinary documentation, prescription certificates, and expense documents "da cui risulti il relativo pagamento e i dati identificativi dell'Animale". Microchip or tattoo to identify the animal.

## Rules the code follows

1. **Only from approved or typed sources.** Every value in the pack is `{ value, source }`. The source is `header.*`, `record.*`, `ctx.*` or `opts.*`. A test resolves every source path back to the object it names.
2. **No fee arithmetic.** Amounts, factors, quantities and totals are strings exactly as typed. Nothing is parsed, summed, multiplied or rounded, and no total is printed unless the practice typed one. The tests check the types and the rendered output, and scan the module for number parsing and arithmetic on amounts.
3. **No inferred diagnosis, code or onset.** The diagnosis is `opts.diagnosis` or `record.assessment.text`, and differentials are never promoted. There is no diagnosis-code field, because no form asks for one. "seit 5 Tagen" in the record does not produce a first-symptom date.
4. **No answer to "pre-existing?".** `pre_existing` is the vet's typed yes/no or `null`, which is flagged. It is printed as "the veterinarian's statement".
5. **Missing is explicit.** Every null field is listed in `pack.missing`, plus each invoice line's date and amount. In DE, the GOT number and factor of each line are listed as well. The summary prints them under "▲ Missing / Fehlt / Mancante".
6. **The vet confirms.** The summary says the vet checks and confirms the details with stamp and signature, and prints blank lines for place/date and stamp/signature. It is not an invoice. Until approved, it carries the DRAFT line.
7. **Medication table reused.** The table is `renderMedicationTable` from `render.ts`, called with the medicines given that day (dispensed, prescribed, performed). It is byte-identical to the report's table.

## Open points

- **Per-insurer claim packs.** CT, GE and Poste want their own form or letterhead. Filling an insurer's own PDF would need per-form field maps, and only HE-AT is a fillable AcroForm among the forms opened.
- **Attachments** (lab and imaging reports) are asked by most Italian insurers. A link from `diagnostics[i]` to stored files would let the pack list them.
- **Austria.** No Austrian statutory fee schedule appears in the sources. AGILA AT's contract refers to the German GOT. The pack does not flag GOT numbers for AT.
- **Not verified today:** § 2 GOT (factor range), DA Direkt, Prima, Allianz Italia, Helvetia Italia, Pet Insurance Italia, Santévet IT.
