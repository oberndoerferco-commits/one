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
