# Referral letter fields against published referral forms

As of 19 October 2026, ten publicly available referral forms from referral centres in Germany, Switzerland, Austria and Italy agree on a core. Every form asks for the referring practice, the owner and the **reason for referral**. Nine of ten ask for breed, sex, history and the results of tests already done, eight for age and seven for the patient's name, species and contact details. Our referral letter (`renderReferralLetter` in `app/src/render.ts`) already renders the clinical core from the approved record. It now also takes breed, sex and age from the record when the patient header lacks them, and it renders the vet's differential diagnoses. `requiredMissing(record, 'referral', header)` now also flags missing signalment, an empty history and a record with no examination at all. The biggest gaps were not clinical. The referring practice, the owner's contact details, urgency and the service requested are now typed by the vet at the referral step and rendered only when typed (see "Schema gaps" below). The microchip, the date of the last dose and long-term medication are still open. Nothing is filled or defaulted.

## Sources (all opened 2026-10-19)

| Key | Centre | Document | URL |
|---|---|---|---|
| TiHo | Tierärztliche Hochschule Hannover, Klinik für Kleintiere | Überweisungsformular (PDF form, 02/2022) | https://www.tiho-hannover.de/fileadmin/13_Kleintiere/Down/Ueberweisungsform0222.pdf |
| AC-RE | AniCura Recklinghausen (DE) | Überweisung (PDF, 2022) | https://www.anicura.de/globalassets/de-DE/pdfs/recklinghausen/anicura_recklinghausen_ueberweisungsformular_2022.pdf |
| AC-WA | AniCura Kleintierzentrum Walluf (DE) | Überweisungsformular (PDF) | https://anicura.de/globalassets/de-DE/pdfs/walluf/ac-walluf-uberweisung.pdf |
| AC-RV | AniCura Kleintierspezialisten Ravensburg (DE) | Überweisungsformular (PDF form) | https://anicura.de/globalassets/de-DE/pdfs/ravensburg/uberweiserformular.pdf |
| AC-EG | AniCura Tierklinik Egelsbach (DE) | Überweisung (PDF, 2023) | https://www.anicura.de/globalassets/de-DE/pdfs/egelsbach/uberweisung_egelsbach_2023_.pdf |
| AC-SU | AniCura Kleintierpraxis Sursee (CH) | Überweisungsformular Chirurgie (PDF) | https://www.anicura.ch/globalassets/switzerland/sursee/sursee_uberweisungsformular.pdf |
| VMU | Vetmeduni Wien, Interne Medizin Kleintiere | Überweisung (PDF, 2022-11-07) | https://www.vetmeduni.ac.at/fileadmin/v/kleintierklinik/20221107_Ueberweisungen_TA_Interne_KTK.pdf |
| UZH | Tierspital Zürich (Vetsuisse) | Web form "Überweisung von Kleintieren" (modified 2026-10-01) | https://www.tierspital.uzh.ch/fuer-tieraerztinnen/ueberweisungen-kleintiere/ |
| OCA | Ospedale Veterinario Croce Azzurra, Roma | Web form "Riferisci un caso" | https://www.ospedalecroceazzurra.it/centro-referenza |
| FV | Futuravet, Tolentino (MC) | Modulo richiesta appuntamento (PDF form) | https://www.futuravet.it/wp-content/uploads/2014/04/Futuravet_Modulo_Appuntamento_COMPILABILE.pdf |

The LMU Medizinische Kleintierklinik has no form, only an information page. It asks referring vets to phone first about the requested tests or the problem, and to email the referral documents to kleintier@lmu.de at least 24 hours before the appointment ([LMU, für Tierärzt:innen](https://www.vetmed.lmu.de/kleintierklinik/de/fuer-tieraerztinnen-und-tieraerzte/), opened 2026-10-19). That page is not counted below.

Four sources could not be opened and are not used. The LMU Chirurgische Kleintierklinik PDFs (`chir.vetmed.uni-muenchen.de/dokument/ueberweisung_ta.pdf`, `ueberw-ml.pdf`) and `med.vetmed.uni-muenchen.de/downloads/formular.pdf` now redirect to the LMU home page. The AniCura Italia "Modulo per la referenza" (`anicura.it/veterinari/referral-form/`) requires a Microsoft sign-in. The Leipzig form failed TLS verification, and the Vetmeduni Wien surgery form failed to download. No form was found for Bologna, Milano, Torino, Pisa, I-Vet or Ca' Zampa.

## Fields asked, and what we do with them

Ours: **R** = rendered in the referral letter, **F** = flagged by `requiredMissing('referral')` or by the renderer when absent, **V** = typed by the vet at the referral step, outside the record (`opts.referral` of `renderReferralLetter`), rendered only when typed and never flagged, **G** = no place in the record schema (schema suggestion), **–** = not adopted (asked by few forms). The rows follow the order most forms use.

| Field | TiHo | AC-RE | AC-WA | AC-RV | AC-EG | AC-SU | VMU | UZH | OCA | FV | n/10 | Ours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Urgency (emergency / routine / by date) | ✓ | ✓ | | | | | ✓ | ✓ | ✓ | | 5 | V |
| Department or service requested | | ✓ | | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | 7 | V |
| Referring practice / vet | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 10 | V (from the letterhead) |
| Referring vet phone / email | ✓ | | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | 7 | V (address and phone as one letterhead line; email) |
| Owner name | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 10 | V |
| Owner phone / address / email | ✓ | | ✓ | | | ✓ | ✓ | ✓ | ✓ | ✓ | 7 | V (phone, email; no owner address) |
| Patient name | ✓ | ✓ | | ✓ | | | ✓ | ✓ | ✓ | ✓ | 7 | R, F |
| Species | | ✓ | ✓ | ✓ | | ✓ | | ✓ | ✓ | ✓ | 7 | R, F |
| Breed | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | 9 | R, F |
| Age or date of birth | ✓ | ✓ | ✓ | | | ✓ | ✓ | ✓ | ✓ | ✓ | 8 | R (age), F |
| Sex | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | 9 | R, F |
| Neuter status | | ✓ | | ✓ | | | | ✓ | | ✓ | 4 | – (in schema, not rendered) |
| Weight | ✓ | | | | | | | | | | 1 | R (header, vitals) |
| Microchip | | | | | | | | ✓ | ✓ | | 2 | G |
| Reason for referral / question | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 10 | R, F (`referral.reason`; typed as the clinical question, `opts.reason` still accepted) |
| History (Anamnese / anamnesi) | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | 9 | R, F (`history`, `presenting_complaint`) |
| Clinical findings | ✓ | ✓ | | ✓ | | | | ✓ | ✓ | ✓ | 6 | R, F (`examination`) |
| Suspected diagnosis / differentials | | ✓ | | | | | ✓ | ✓ | ✓ | ✓ | 5 | R (assessment and differentials), F (`assessment`) |
| Tests done and results / reports enclosed | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | 9 | R, F (`diagnostics[i].result`) |
| Images enclosed (X-ray, CT, MRI) | ✓ | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | 7 | G (attachments) |
| Previous treatment / therapy | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ | 8 | R (treatments, medication table) |
| Medication with dose | ✓ | ✓ | | | | | | | | | 2 | R, F (dose, route, frequency) |
| Date or duration of each dose ("last given") | ✓ | ✓ | | | | | | | | ✓ | 3 | duration R; date G |
| Long-term medication (Dauermedikation) | | ✓ | | | | | ✓ | | ✓ | | 3 | G |
| Response to treatment | | | | | | | | | ✓ | | 1 | – |
| Known intolerances / allergies | | | | | | | ✓ | | | | 1 | – |
| Previous diseases | ✓ | | | | | | | | | ✓ | 2 | – (history items) |
| Vaccination status | | | | | | | | | ✓ | | 1 | – |
| Insurance | | | | | | | | | ✓ | | 1 | – |
| Owner consent to share data | | | | | | | | | ✓ | | 1 | – |
| Cost / deposit note to owner | | | | | (✓) | | (✓) | | | | 0 (text only) | – |
| Return report / update channel | | | | | ✓ | | | | ✓ | | 2 | – (closing sentence asks for findings) |
| Who books the appointment | | | | | | | | | ✓ | | 1 | – |
| Date and signature | | ✓ | ✓ | ✓ | | | ✓ | | | ✓ | 5 | R (approval disclosure; signature block is the PIMS's) |

## What changed in the code

- **Rendered:** the intro line now takes breed, sex and age from `record.patient` when the patient header lacks them (header values win). The history section now lists `assessment.differentials` after the assessment ("Differential diagnoses" / "Differenzialdiagnosen" / "Diagnosi differenziali").
- **Flagged** (`requiredMissing(record, 'referral', header)` only): `patient.name`, `patient.species`, `patient.breed`, `patient.sex` and `patient.age` when neither the header nor the record has them, `history` when the record has no history item, and `examination` when there is no finding and no vital. The referral reason was already flagged by the renderer as `referral.reason`. Presenting complaint, assessment, medication fields, weight for dosed drugs and performed-test results were already flagged.
- **Not flagged on purpose:** treatments and diagnostics may legitimately be empty, and flagging them would push the vet to write something. Neuter status (4 of 10) and weight (1 of 10) are below the majority line.

## Schema gaps

### Covered (19 October 2026)

`renderReferralLetter(record, header, lang, { referral })` takes an optional `ReferralInput` (`app/src/render.ts`). Every field is typed by the vet. A blank field is left out, and a block with no typed field is left out entirely. None of these fields is in the record, so none is added to `requiredMissing`.

1. **Referring vet and practice with contact details** (10 and 7 of 10). `referral.referrer` = `{ practice, address, email, vet, registration }` renders as a "Referring practice" block ("Überweisende Praxis" / "Struttura inviante"). In the workspace it comes from the "Your letterhead" fields stored on the device, which now include an optional email. The workspace's "Dr. Demo" placeholder for other documents is not used here.
2. **Owner name and contact** (10 and 7 of 10). `referral.owner` = `{ name, phone, email }` renders as an "Owner" block ("Tierhalter/in" / "Proprietario"). It is structurally compatible with `VisitContext.owner`, and the tax id is never printed. In the workspace these fields belong to the synthetic case: they are held only in the inputs, are never written to localStorage, and are cleared when the case changes. The owner's postal address is still not taken.
3. **Urgency, service requested and the clinical question** (5, 7 and 10 of 10). `referral.request` = `{ urgency: 'emergency' | 'urgent' | 'routine', service, question }`. When an urgency or a service is typed, a "Referral request" block ("Überweisungsauftrag" / "Richiesta di riferimento") lists them and then the question. Otherwise the letter keeps the earlier "Reason for referral" section. `opts.reason` still works and is used as the question when `request.question` is absent. The workspace urgency select starts on an empty "—" option. While the referral letter is on screen and the question is empty, the flag list shows a `referral.reason` missing hint with a button that focuses the question field. The hint does not block approval.

`VisitContext` was not extended. A referral needs no country pack, and `VisitContext.author` would have needed practice, address and email fields that no country check uses.

### Still open (schema suggestions, not implemented)

4. **Microchip** (2 of 10, but required on IT records). `VisitContext.microchip` exists but is not in the record.
5. **Date of the last dose and long-term medication** (3 and 3 of 10). `Medication` has a duration but no `last_given` date and no long-term flag.
6. **Attachments**: a list of enclosed reports and images (7 of 10 ask for images), so the letter can say what travels with it.
7. **Owner postal address** (part of the 7 of 10 owner-contact row). It is not taken.
