# AI Veterinary — documentation core

The part of the vet tool that must be right before any screen exists:
the clinical record, the checks that enforce "nothing on the page you didn't
write", the deterministic report rendering, and the evaluation harness.

```
notes (text) ─► normalize ─► extract (model or fixture) ─► ClinicalRecord
                                                             │
                              validators (block / warn) ◄────┤
                              requiredMissing (flags)   ◄────┤
                              render (report, med table) ◄───┘
```

## Run

```bash
cd aiveterinary/app
npm install
npm test          # unit tests, offline
npm run eval      # evaluation on eval/cases with fixture records, offline
npm run demo      # Luna example: notes → report → checks, offline

# with a model (needs ANTHROPIC_API_KEY; costs cents per case):
AIVET_EXTRACTOR=claude npm run eval -- --verbose
npm run demo -- --claude "vomiting 3x since yesterday, T 39.1, abdomen soft, recheck 48h"
```

## Files

| Path | What |
|---|---|
| `src/schema.ts` | `ClinicalRecord` v0.2 (zod). Every fact carries `source_spans`, `source_role` (owner/vet) and `status` (planned/performed/declined…). `PatientHeader` is the locked patient identity. |
| `src/normalize.ts` | Whitespace normalisation (offsets refer to this text), abbreviation hints (EN/DE/IT), rough language detection. Never rewrites the notes. |
| `src/validators.ts` | `validateGrounding` (spans valid, numbers in notes), `validateMedications` (drug/dose/unit/frequency/duration in notes), `validatePatient` (header wins; pregnancy on a male → block), `validatePlausibility` (species temperature ranges → warn), `validateDerivedText` (owner texts add nothing), `requiredMissing` (what a document still needs). Findings are reported, never auto-fixed. |
| `src/render.ts` | Report in EN/DE/IT. Medication table rendered by code from structured fields. Draft watermark until approved. |
| `src/extract.ts` | `Extractor` interface, the prompt (`extract-v1`), `FixtureExtractor` (tests) and `ClaudeExtractor` (structured output via `messages.parse` + zod). |
| `src/cli/eval.ts` | Harness: runs every case, applies validators and expectations, prints a summary; exit 1 on failure. |
| `eval/cases/*.json` | Synthetic cases: notes, patient header, expectations, and a hand-written fixture record. Case 005 is a deliberately wrong fixture that must be blocked. |

## Adding a case

Copy a case file. Notes must be realistic shorthand. `expect` lists the drugs
allowed to appear, the missing flags that must be raised, the assessment text
(or `null`), and anything that must not appear. If you add a `fixture_record`,
compute spans with:

```bash
node -e 'const n=process.argv[1];let p=0;for(const l of n.split("\n")){console.log(p,p+l.length,JSON.stringify(l));p+=l.length+1}' "$(jq -r .notes eval/cases/NEW.json)"
```

Target before any pilot: ≥ 300 cases across EN/DE/IT written with vets,
0 blocking findings on the model's output, missing-recall ≥ 95 %.

## Country field packs (`src/country.ts`)

Facts the vet enters at sign-off, never extracted from prose: microchip, owner name and tax id, author and registration, consent (obtained, scope, method), Italian REV number, and one dispensing record per medication (product, authorisation number, batch, pack, quantity, antibiotic flag and justification). `countryMissing(record, header, ctx)` returns flags for DE (TÄHAV dispensing record, antibiotic justification, prescription names the keeper), IT (microchip, codice fiscale, REV number, consent modi e tempi), CH (TAMV product and quantity, IS ABV pack and indication for antibiotics) and AT (TAMG product, batch, quantity). Common to all: responsible vet named, vaccine batch, consent for performed procedures, declined care documented. Flags are printed in the report's missing section; nothing is filled in.

`provenance(record)` gives the counts printed under every document: facts from the notes, not recorded, added by AI (always 0, every fact carries a span).

## Documents from the approved record (`src/render.ts`)

All documents are rendered by code from the record's own sentences; headings, tables and flags are code, nothing else is added.

- `renderConsultReport` — the clinical report with the medication table, declined-care section and provenance line.
- `renderOwnerSummary` — the same facts grouped for the person acting at home: why you came, what we found, what we did, medication to give (identical table), a dose checklist when frequency and duration parse unambiguously (`parseDosesPerDay`, `parseDurationDays`), at home, next appointment, discussed and declined.
- `renderReferralLetter` — clinical letter to a colleague; the referral reason is the vet's own words passed in, flagged when absent.
- `renderVaccinationEntry` — booklet line per vaccine given, with batch, site and validity from the dispensing record, flags when absent.
- `renderConsentForm` — planned procedures with the FNOVI/chamber consent elements as headings; risks, alternatives and costs are left for the vet to write.
- `renderCostEstimate` — planned diagnostics, procedures and medicines as rows with empty price cells (GOT number and factor columns for DE, the written-estimate note for IT).
- `renderAnaesthesiaRecord` — the team's anaesthesia and surgery entries (`AnaesthesiaRecord`) as a record with ASA, protocol, monitoring, implants, recovery and team flagged when absent.
- `renderControlledDrugsEntry` — one register line per dispensing marked controlled; quantity and responsible vet flagged when absent.
- `renderLabExplanation` — owner-facing explanation of each result using only the vet's own interpretation from `VisitContext.interpretations`; results without one are flagged, never explained by code.
- `renderPrescription` — one section per dispensed or prescribed medicine with the Art. 105(5) Reg. (EU) 2019/6 content, taking product, quantity, authorisation number and batch from the `VisitContext` dispensing record; keeper, microchip and prescribing vet flagged when absent.

The workspace preview on the site exposes all of them through its document selector.

## Approved versions (`src/versions.ts`)

`approve` freezes a copy of the record with a fingerprint; it cannot be edited afterwards. `amend` requires a reason and a real change and returns the next version pointing back to the one it supersedes. `documentFrom` stamps each generated document with the version it came from, and `propagationMap` lists the documents that are stale after an amendment. The fingerprint is for change detection; tamper evidence comes from append-only storage on the server.

## Snippets and the identity check

`expandSnippets(notes, snippets)` expands clinic-written dot-phrases (`.ou` → "otherwise unremarkable") only where the vet typed the trigger, before structuring, so every fact taken from the expanded text still has a source span. `crossDocumentMedicationCheck(record, documents)` verifies that each medication's drug, dose, route, frequency and duration appear unchanged in every generated document; where a document has a medication table, the drug's own row must carry them.
