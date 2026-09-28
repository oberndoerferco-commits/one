# C. MVP specification — the documentation assistant

**One job:** turn a vet's rough notes into an accurate, approved consultation
report, and from that same approved record produce owner-facing instructions,
with the vet in control of every word.

If a feature doesn't shorten *end of consultation → approved documentation*, it
is not in the MVP.

---

## 0. Why this MVP, given the market

The competitive analysis (`01-competitive-analysis.md`) shows that "AI writes the
SOAP note" is already crowded, and that PIMS vendors are bundling it. The MVP's
edge therefore isn't generation. It's **governance and speed of checking**:

- keyboard-optimised input
- one approved structured record
- missing-info flags
- medication integrity
- sentence-to-source traceability
- owner documents in the owner's language

The first target is clinics on PIMS without bundled AI, in DE/IT. The riskiest
assumption is that text-first is fast enough without voice. Step 0 of the build
plan (§9) measures that before anything else.

## 1. Users and setting

- **Primary user:** small-animal veterinarian in a 1–10 vet clinic (dogs, cats;
  rabbits and other small mammals supported by species field only).
- **Secondary:** veterinary nurse drafting notes for a vet to approve.
- **Languages at launch:** English, German, Italian for both UI and output. The
  vet can write notes in one language and generate owner documents in another.
- **Setting:** desktop browser next to the clinic's existing PIMS. No integration;
  output leaves via copy, PDF or print.

## 2. In scope

| # | Capability | Acceptance criteria |
|---|---|---|
| 1 | Sign-in with MFA, one clinic per account (multi-clinic later) | Vet can't reach any page without MFA; session idles out after a configurable 30 min default |
| 2 | Clinic setup | Name, address, logo, default language, units (°C/°F, kg/lb), SOAP vs narrative report, abbreviation dictionary (pre-filled per language, editable) |
| 3 | Patient quick-create / quick-find | Create in one line (`Luna, dog, Labrador, F, 6y, 28kg`); find by name/owner/chip with `/` or `Ctrl+K`; < 150 ms search on 10k patients |
| 4 | Consultation note entry | Plain textarea, bullets/abbreviations/typos accepted; autosaves every 2 s; works without the mouse |
| 5 | Structure → draft report | `Ctrl+Enter` produces a sectioned report; first section visible < 3 s, full draft p95 < 15 s |
| 6 | Missing / uncertain flags | Required fields not in the notes are shown as **Missing**, never filled; uncertain parses (unknown abbreviation, possible typo in a drug) are highlighted with the original text |
| 7 | Side-by-side review | Notes left, report right; clicking a report sentence highlights its source text; inline editing; per-section "regenerate" that keeps the vet's manual edits elsewhere |
| 8 | Approve & save | `Ctrl+Shift+Enter` or button "Approve & save"; requires vet role; creates immutable approved version; re-auth if last auth > 12 h |
| 9 | Amend after approval | Creates a new version with reason; previous stays viewable; diff visible |
| 10 | Export | Copy as plain text (formatted for pasting into PIMS free-text fields), copy as rich text, PDF on clinic letterhead, print. Drafts are watermarked DRAFT |
| 11 | Derived documents from the approved record | Owner summary, home-care & medication instructions, discharge summary, referral letter, client email. Each: generate → review → approve → export |
| 12 | Translation | Any approved document → EN/DE/IT; medication table re-rendered from structured data; translated doc needs its own approval |
| 13 | Consultation list / history | Per patient, reverse-chronological; open any approved version |
| 14 | Audit trail view | Per consultation: who created, what the AI generated, who edited, who approved, when, exports |
| 15 | Feedback | One-key "this was wrong" on any section → captured with the version for the eval set (no clinical text leaves the tenant without consent) |

## 3. Explicitly out of scope for MVP

Voice/dictation · PIMS integrations · owner accounts/app · appointments ·
billing/invoicing · lab/imaging uploads · coded diagnoses (free text only) ·
drug catalogue/dose calculators · reminders · microchip registry lookup ·
multi-clinic groups · mobile layout beyond "readable" · offline mode.

## 4. The core flow (keyboard only)

```
Ctrl+K  "luna"  ↵                       → patient opened, new consultation today
type notes                               → autosave
Ctrl+Enter                               → draft report streams in
Tab / Shift+Tab                          → jump between flagged items
type to fix, Esc to leave edit           
Ctrl+Shift+Enter                         → Approve & save
D                                        → generate discharge/owner instructions (menu)
Ctrl+Shift+C                             → copy approved report for PIMS
```

Target: **≤ 90 seconds and ≤ 3 mouse clicks** from finishing the notes to an
approved report, for a routine consultation.

## 5. Document types (MVP)

| Type | Built from | Audience | Style |
|---|---|---|---|
| Consultation report (narrative) | approved record | clinical file | concise, sectioned, third person, clinic's section order |
| SOAP note | approved record | clinical file | S / O / A / P; if the clinic enabled SOAP |
| Discharge summary | approved record | owner + file | what was done, what to do at home, when to come back |
| Owner explanation | approved record | owner | plain language (target reading age ~12), no jargon, no new diagnoses |
| Home-care & medication instructions | approved record (meds table deterministic) | owner | checklist-style; "contact us if…" only from vet-entered instructions plus the clinic's fixed emergency line |
| Referral letter | approved record + recipient field | colleague | formal, history + reason for referral + questions |
| Client email | chosen approved document | owner | short cover text + document |

## 6. Structured clinical record (schema v0, abridged)

For the Luna notes from the brief (`source_spans` offsets are illustrative).

```jsonc
{
  "schema_version": "0.1",
  "patient": { "name": "Luna", "species": "dog", "breed": "Labrador Retriever",
               "sex": "female", "neuter_status": null, "age": {"value": 6, "unit": "year"},
               "weight": null },
  "presenting_complaint": { "text": "Vomiting since yesterday, approx. 3 episodes", "source_spans": [[22, 55]] },
  "history": [
    { "finding": "appetite", "value": "reduced", "source_spans": [[70, 86]] },
    { "finding": "drinking", "value": "normal",  "source_spans": [[89, 105]] },
    { "finding": "diarrhoea", "value": "absent", "source_spans": [[58, 69]] }
  ],
  "examination": {
    "vitals": { "temperature": {"value": 39.1, "unit": "C", "source_spans": [[108, 117]]},
                "heart_rate": null, "respiratory_rate": null, "weight": null },
    "findings": [ { "system": "abdomen", "text": "soft, mild pain on palpation", "source_spans": [[120, 147]] } ]
  },
  "diagnostics": [ { "test": "bloodwork", "status": "performed", "result": null, "source_spans": [[150, 159]] },
                   { "test": "abdominal ultrasound", "status": "performed", "result": null, "source_spans": [[162, 172]] } ],
  "assessment": { "text": null, "differentials": [] },
  "treatment": [ { "type": "procedure", "text": "fluid therapy", "source_spans": [[175, 181]] } ],
  "medications": [
    { "drug": null, "class_as_written": "antiemetic", "dose": null, "dose_unit": null,
      "route": null, "frequency": null, "duration": null, "dispensed": null,
      "source_spans": [[184, 194]] }
  ],
  "plan": { "follow_up": { "text": "Recheck in 48 hours", "interval": {"value": 48, "unit": "hour"}, "source_spans": [[197, 208]] } },
  "missing": [
    { "field": "medications[0].drug",  "reason": "Antiemetic given but drug not named" },
    { "field": "medications[0].dose",  "reason": "No dose recorded" },
    { "field": "diagnostics[*].result", "reason": "No results recorded" },
    { "field": "assessment", "reason": "No assessment / working diagnosis recorded" }
  ],
  "uncertain": []
}
```

Note what the Luna example in the brief looks like after extraction: the draft
report reads well, **and** the vet is shown four gaps (which antiemetic, what
dose, results of the tests, assessment). This is intended behaviour — the product
makes gaps visible instead of hiding them behind fluent prose.

## 7. Safety rules (non-negotiable acceptance criteria)

1. No value (number, drug, dose, route, frequency, duration, diagnosis, test
   result) appears in any output unless it is present in the vet's input /
   approved record. Violations block approval.
2. Medication tables are rendered from structured fields, identically in every
   document and every language.
3. Owner-facing texts never contain a diagnosis, prognosis or instruction that
   isn't in the approved record.
4. Every draft carries "Draft — AI-assisted, not yet reviewed" until approved.
5. Approved content is immutable; amendments create versions.
6. The AI never gives advice to the vet in the MVP (no "consider also…"). It
   structures, rewrites and translates. Decision support is a later, separately
   validated feature.

## 8. Metrics (instrumented in the pilot)

| Metric | Definition | MVP target (to validate, not promise) |
|---|---|---|
| **Time-to-approved** | first keystroke of structuring (`Ctrl+Enter`) → approval | median < 90 s routine consults |
| Baseline comparison | same vets' current time per report (time-motion study before pilot) | ≥ 50 % reduction |
| Edit ratio | characters changed by vet / characters generated | < 15 % after week 2 |
| Section acceptance | % sections approved without edit | > 80 % |
| Hallucination rate | outputs containing any value not in source (from validators + vet flags) | **0 in medication/numbers**; < 1 % any |
| Missing-info recall | flagged missing / actually missing (eval set) | > 95 % |
| Keystrokes / clicks | per consultation | tracked, trend down |
| Weekly active vets / consults per vet | adoption | tracked |
| Qualitative | 5-point "would be upset if taken away" | > 40 % "very" at week 6 |

Telemetry records timings and counts, **not** clinical text.

## 9. Build plan

| Step | Output | Exit criterion |
|---|---|---|
| 0. Discovery (parallel with 1) | 12–15 interviews (vets, nurses, reception) across DE/IT/UK; 3 half-day shadowing sessions; 50 anonymised or synthetic real-style note samples written by vets | Top 5 workflows + note styles documented; schema v0 validated |
| 1. Eval harness + schema | Synthetic case set (~150), extraction prompt, validators, CI eval | Zero medication/number hallucinations on the set |
| 2. Clickable prototype | Workspace with real AI on synthetic patients | 5 vets complete the flow unaided; time measured |
| 3. MVP (private beta) | Items 1–15 above; security gate passed (`05-security-model.md` §9) | DPA, DPIA, pen test done |
| 4. Pilot | 3–5 clinics, 15–25 vets, 6 weeks | Metrics in §8; go/no-go for integrations |

## 10. Open questions for veterinarians (discovery script seeds)

- Show me your last three consultation notes. What did you write in the PIMS and
  what did you write later?
- When do you finish documentation — between consults, end of day, at home?
- What do you retype most often? (discharge text, medication instructions,
  referral letters, insurance forms?)
- How do you currently write owner instructions? Templates? Handwritten?
- What must a report contain for your clinic / country / insurer?
- Which abbreviations do you use? Which languages do your owners need?
- What would make you *not trust* an AI-written note?
- Who is allowed to approve records in your clinic?
- What would you pay, and who decides?
