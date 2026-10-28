# REV draft payload (Italy, Ricetta Veterinaria Elettronica)

As of 23 October 2026, every Italian veterinary prescription is issued in the Ministry of Health's information system. Paper is kept only for narcotic and psychotropic products under DPR 309/1990. For a companion animal, the system's own technical spec and the D.M. 8 febbraio 2019 list what one prescription needs:

- the prescribing vet;
- the owner's or keeper's codice fiscale, plus first and last name;
- the species and, where an animal registry requires it, the animal's identifier;
- per medicine: the product (AIC code), the number of packs, the dosage, the duration, the deroga code and, for an antimicrobial, prophylaxis/metaphylaxis and a justification;
- optionally a diagnosis code.

When the vet confirms, the system generates a **prescription number and a PIN**. The owner gives both to the pharmacy.

`buildRevDraft(record, header, ctx, issued?)` in `app/src/rev.ts` returns these fields for each prescribed medicine, filled only from the approved record, the patient header and the vet's `VisitContext`. Every other field is `null` and listed in `missing`, with the source that requires it. `renderRevDraftText(draft, 'it')` prints an Italian checklist headed "BOZZA DA TRASCRIVERE — NON È UNA RICETTA" for the vet to copy into the official system. We submit nothing, store neither the number nor the PIN, and do no AIC lookup. The prescription type, repeatability, deroga and diagnosis code are left for the vet to choose in the system.

## Sources (all opened 2026-10-23)

| Key | Document | URL |
|---|---|---|
| DM | D.M. 8 febbraio 2019, "Modalità applicative delle disposizioni in materia di tracciabilità dei medicinali veterinari e dei mangimi medicati", GU SG n. 89 del 15-4-2019, art. 1–5 and Disciplinare tecnico §4.4.1–4.4.2 | https://www.gazzettaufficiale.it/eli/id/2019/04/15/19A02527/sg |
| WS | IZS Teramo / CSN, "Specifiche tecniche dei Web Services … Prescrizione Veterinaria per animali PET ed equidi NDPA", Release 1.1.1, doc. v1.7 (28/08/2025), and the earlier v1.1 doc r1.6, which holds the full request table (v1.7 documents only what changed). Both are linked from the official Software House page, in the "Medici Veterinari, studi e ambulatori" Drive folder | https://www.ricettaveterinariaelettronica.it/softwarehouse.html → https://drive.google.com/drive/folders/1JbQk20REON2d4BRBu5ID9WH0FtL1Yxzm |
| MO | Ministero della Salute, "Manuale operativo … La prescrizione medico-veterinaria elettronica", v2.0 (April 2019), §6.2–6.3 and §6.7 | https://www.ricettaveterinariaelettronica.it/documenti/manuale%20operativo/Manuale%20Operativo.pdf |
| HELP | vetinfo.it Help wiki, "emissionericetta" (PET ed equidi NDPA section, last edited 2018-09-10) | https://www.vetinfo.it/help/farmaco/help/emissionericetta |
| HOME | ricettaveterinariaelettronica.it, home page "Inizia da qui" | https://www.ricettaveterinariaelettronica.it/ |
| L28 / L37 | D.Lgs. 7 dicembre 2023, n. 218 (GU SG n. 2 del 3-1-2024), art. 28 "Prescrizione veterinaria" and art. 37 "Cessione dei medicinali veterinari" | https://www.gazzettaufficiale.it/eli/id/2024/01/03/23G00225/sg |
| NDPA | "Guida allo scarico dalle giacenze per animali NDPA" (official REV manual set) | https://www.ricettaveterinariaelettronica.it/documenti/manuale%20operativo/guida_scarico_giacenze_ndpa.pdf |

**Could not open:**

- **Ministero della Salute portal.** The REV/traceability pages on salute.gov.it are JS-walled: the old `p2_6.jsp` URLs return a JavaScript redirect to `/new/`, and `?id=3737` returned 502.
- **REV FAQ and "Normativa di riferimento".** On ricettaveterinariaelettronica.it both pages load their content by script, so curl received empty shells.
- **Reg. (EU) 2019/6 on EUR-Lex.** The page returned HTTP 202 with an empty body (a bot challenge), both with curl and WebFetch. D.Lgs. 218/2023 art. 28 says the prescription "reca gli elementi di cui all'articolo 105, paragrafo 5, del regolamento", but that list was not opened, so it is not used here.
- **FNOVI.** No REV field list was found. The only FNOVI-hosted document opened was the Ministry's note correcting the "vendita diretta" point of its D.Lgs. 218/2023 operating guidance (https://www.fnovi.it/sites/default/files/Trasm%20indicazioni%20operative_29%20marzo.pdf). It does not cover prescription contents.

## Fields for a companion-animal REV, and where each value comes from

The WS names are the request fields of `POST /ws/1.1.1/emissione/ricetta/pet/emetti`. "Req." is what WS v1.1 says about the field. **Draft source** is what `buildRevDraft` fills it from. "missing" means the field is always `null` and listed in `missing`, so the vet chooses it in the system.

| Field | WS name | Req. (WS) | Sources | Draft source |
|---|---|---|---|---|
| Prescription type (PET ed equidi NDPA / scorta propria / scorta impianto non zootecnico / DPA …) | endpoint, `ricTipoCodice` | chosen by endpoint | HELP, HOME, MO §6.3 | missing (never inferred) |
| Vet's codice fiscale | `vetIdFiscale` | yes (= the logged-in user) | WS, DM §4 ("identificati con il codice fiscale e il numero di iscrizione") | missing (the system fills it from the login) |
| Vet's albo registration number | – (registered with the account) | – | DM art. 3 c.4, DM §4 | `ctx.author.registration` |
| Vet's name | `vetDenominazione` (output) | – | WS | `ctx.author.name` |
| Veterinary practice | `strCodice` | no | WS, HELP ("non è un dato obbligatorio") | missing, optional |
| Owner/keeper's tax ID (CF, 16 chars, or P.IVA, 11) | `propIdFiscale` | yes | DM §4.4.1 ("identificativo fiscale, nome e cognome del proprietario o detentore"), WS, MO §6.3 d | `ctx.owner.tax_id` |
| Owner's first / last name (or company name) | `propNome`, `propCognome` / `propRagioneSociale` | yes for a natural person | DM §4.4.1, WS; HELP: needed if the person is not yet registered, and must match the CF | `ctx.owner.name` (one string; the split is left to the vet) |
| Owner has no Italian CF (e.g. tourist) | `propFlStraniero` | no | WS, MO §6.3 d (the prescription is printed, or the vet hands over a reminder with number and PIN) | not filled |
| Species | `prescapoSpecieCodice` | yes | DM §4.4.1 ("specie e numero di capi"), WS | `header.species` (the system's species code is chosen there) |
| Animal identifier (microchip) | `prescapoIdentificativo` | yes for equid species codes; warning when missing for species code "C" | DM §4.4.1 (identifier where a national registry provides for one), MO §6.3 d (dogs: microchip from the pet registry; otherwise species only) | `ctx.microchip` |
| Farm code where kept | `aziCodice` | yes for equids; must stay empty for other pets | HELP, MO §6.3 d | missing, flagged for horses only |
| Diagnosis | `prescapoDiagnosiCodice` | no (code from `/codifica/diagnosi`) | DM §4.4.1 ("relativa diagnosi") | `record.assessment.text` as the vet wrote it; the code is chosen in the system |
| Product type (N with AIC, S galenic, O homeopathic, E foreign, SMP medicated pet food …) | `presrigaFlTipoMedicinale` | yes | WS | missing |
| Product / AIC | `presrigaProdAic` (9 digits), `presrigaDescrizione` for non-AIC | AIC yes if type N | WS, HELP ("Medicinale identificato da AIC"), DM §4.4.1 | `ctx.dispensings[i].authorisation_number` and `.product`. A non-9-digit AIC raises a warning; there is no lookup |
| Pack | `presrigaProdConfezione` | – | WS | `ctx.dispensings[i].pack` |
| Quantity = **number of packs** | `presrigaQuantitativo` | yes; must be 1 for galenic preparations and for repeatable lines | WS, DM §4.4.1 ("relativo quantitativo"), MO §6.2 b (stabulogeni: packs = doses) | `ctx.dispensings[i].quantity.value`, **only** when its unit is a pack word (confezione, pack, Packung …). Any other unit is shown as written and the field stays missing |
| Dosage | `presrigaPosologia` (free text) | yes | DM §4.4.1, WS | `record.medications[i]` dose + dose_unit, route, frequency joined, with each part's path in `provenance` |
| Duration | `presrigaDurataTrattamento` (number) | yes unless `presrigaFlMalattiaCronica` | DM §4.4.1, WS | `record.medications[i].duration` as written; the unit of the WS number is not stated, so nothing is converted |
| Chronic disease | `presrigaFlMalattiaCronica` | no | WS | not filled |
| Repeatable / non-repeatable | `presrigaFlRipetibile` (S/N, default N) | no; S only if the product is repeatable; forced to N for antimicrobials; not allowed with a deroga | WS, MO §6.3 a (one REV can mix repeatable and non-repeatable lines; the system applies the rules per line), HOME | missing, never inferred |
| Validity | (set by the system) | – | L28: repeatable 6 months / max 10 uses; non-repeatable, stock and off-label 30 days; antimicrobials 5 days | not filled (the system sets it) |
| Deroga (off-label / cascade use) | `prescapoDerogaCodice` (per medicine-animal link; N = none, A = other reason) | yes (N applies if no links are sent); note required if A | WS, HELP (the system warns when the species is not authorised), MO §6.3 l | missing, never inferred |
| Antimicrobial: therapy / prophylaxis / metaphylaxis | `presrigaProfilassiMetafilassiCodice` | yes if the AIC is antimicrobial | WS v1.7 | missing; listed when the vet ticked `is_antibiotic` |
| Antimicrobial justification | `presrigaGiustificazioneCodice` + `presrigaGiustificazioneNote` (≤2000 chars) | yes if antimicrobial and not therapy; note required if ALTRO (the only one allowed for PET prophylaxis) | WS v1.5–1.7 | `ctx.dispensings[i].antibiotic_justification` → note; the code stays missing |
| Line / prescription notes | `presrigaNote`, `ricNote` | no | WS; MO §6.3 l (deroga info, antimicrobial prophylaxis, non-substitutability, warnings) | not filled |
| Continuation of an earlier prescription | `ricFlProsieguo` | no | WS | not filled |
| **REV number and PIN** | `ricNumero`, `ricPin` (String(4)) – output | generated at issue | DM §4.4.1 ("genera un numero di ricetta e il corrispondente PIN. Il medico veterinario fornisce all'utilizzatore il numero della ricetta e il relativo PIN"), HELP (popup with the PIN after "Conferma"), HOME (PIN changes per prescription; the pharmacy retrieves by number + PIN or by CF + PIN), MO §6.7 | the optional `issued: { numero, pin }` argument the vet types after issuing; `ctx.prescription_number` is the fallback for the number. Stored nowhere by this module |

### Which medicines go on the draft

- **prescribed** → a REV line.
- **dispensed** (handed over from the vet's own stock) → not a REV line but `cessioni_da_scorta`. L37: the vet may hand over medicines from their stock "allo scopo di avviare la terapia prescritta" and registers the **discharge within seven days** in the traceability system. NDPA: the discharge records quantity, a discharge reason chosen from a list (e.g. "Cessione per confezione integra") and notes. The reason is left `null`.
- **performed**, including **vaccines given in the clinic** → excluded with a note. No source makes an in-clinic administration a prescription to the owner. NDPA names "Scarico Massivo per trattamento animali NDPA" for stock used on animals, so the note points the vet to the stock register. No source says how a vaccine given in clinic is recorded in the REV system specifically. WS has a vaccine flag (`presrigaFlOrmonaleVaccino`) only for prescribed lines.
- **declined, planned, recommended** → excluded.
- **narcotics** (`is_controlled`) → a warning. HOME says the REV does not apply to AIC medicines containing narcotics (paper is kept). WS v1.3 added narcotic codes only for galenic and foreign products.

## Not done, on purpose

- **No submission.** WS access requires the Software House accreditation form and OAuth/SPID. The site's terms forbid using the system through means not intentionally provided. The draft is only a transcription aid.
- **No AIC lookups.** WS says "la REV non gestisce la banca dati dei Farmaci". The AIC comes from the pack, typed by the vet.
- **No species-code mapping.** The species list is served by `/codifica/specie` behind authentication; the fixtures seen in WS use "C" and "G", but the list itself was not opened.
- **No diagnosis-code or deroga-code mapping**, for the same reason.

## Gaps in our schema

- `VisitContext.owner.name` is one string. The REV asks for first and last name separately, so the draft says to split them.
- There is no field for the vet's codice fiscale. The system takes it from the login, so this is not needed.
- There is no field for the farm code of a non-DPA horse.
- `Dispensing.is_antibiotic` defaults to `false`, so "not antimicrobial" and "not entered" look the same. The draft therefore fills `antimicrobico` only when it is `true`.
