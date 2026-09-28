# B. Product architecture

Status: proposal, pre-prototype. Nothing here is built yet.
Scope: what we need for the MVP (see `03-mvp-spec.md`) plus the seams that let us
grow into integrations, the owner app and the animal-health network *without*
building them now.

---

## 1. Shape of the system

```
                ┌──────────────────────────────────────────────┐
 Browser (vet)  │  Web app (Next.js, React, TypeScript)        │
 keyboard-first │  - consultation workspace                    │
                │  - review / approve / export                 │
                └───────────────┬──────────────────────────────┘
                                │ HTTPS, session cookie (httpOnly)
                ┌───────────────▼──────────────────────────────┐
                │  API (TypeScript modular monolith)           │
                │  modules: identity · tenancy · patients ·    │
                │  consultations · documents · ai · audit ·    │
                │  export                                      │
                │  - REST + OpenAPI (also our future public API)│
                │  - every write → audit_event                 │
                └───┬───────────────┬───────────────┬──────────┘
                    │               │               │
          ┌─────────▼──────┐ ┌──────▼───────┐ ┌─────▼──────────────┐
          │ PostgreSQL     │ │ Job queue    │ │ AI gateway          │
          │ (EU region)    │ │ (pg-boss, in │ │ - prompt registry   │
          │ RLS per tenant │ │  Postgres)   │ │ - schema validation │
          │ audit, versions│ │ PDF, exports │ │ - grounding checks  │
          └────────────────┘ └──────────────┘ │ - PII minimisation  │
                                              │ - provider adapter  │
                                              └─────┬───────────────┘
                                                    │
                                          LLM provider (EU-processing
                                          option, no training on data,
                                          DPA in place)
```

**Why a modular monolith, not microservices.** One team, one product, one
database. Microservices would add deployment, tracing and consistency cost with
no benefit at MVP scale. Module boundaries are enforced in code (each module owns
its tables and exposes a service interface) so the AI gateway or an integrations
module can be split out later if load or compliance requires it.

---

## 2. Technology choices

| Layer | Choice | Why | Alternatives considered |
|---|---|---|---|
| Frontend | **Next.js + React + TypeScript**, rendered mostly client-side for the workspace | Large hiring pool, mature a11y ecosystem, same language as backend | SvelteKit (smaller ecosystem), plain SPA (fine too) |
| UI primitives | **Radix UI / React Aria** + own design tokens, no heavy component kit | Accessible keyboard behaviour for free; calm custom look | MUI (looks generic, heavier) |
| i18n | **ICU MessageFormat** (`next-intl` or `FormatJS`) from day one; all UI strings externalised | Multilingual-ready is a requirement; retrofitting is expensive | — |
| Backend | **Node.js (TypeScript), Fastify**, REST with **OpenAPI** spec generated from schemas (Zod) | Shared types with frontend; OpenAPI becomes the integration/public API contract | tRPC (fast but not a public API), Python/FastAPI (good for ML, but split-language cost) |
| Database | **PostgreSQL 16+** (managed, EU region) with **row-level security** | Relational integrity for clinical records, JSONB for structured AI output, FTS built in, pgvector later | MongoDB (weaker integrity/audit story) |
| ORM / migrations | **Drizzle** or **Prisma** + SQL migrations in repo | Typed queries, reviewable migrations | — |
| Jobs | **pg-boss** (queue in Postgres) | No extra infra for MVP; transactional enqueue | Redis/BullMQ later if needed |
| Auth | Managed **OIDC** provider with an EU data region (evaluate: Auth0 EU, Zitadel, Keycloak self-hosted, WorkOS) · **MFA mandatory** for clinical roles · SSO/SAML later for groups | Don't hand-roll auth; clinics need MFA and later SSO | Roll-own (no) |
| File storage | **S3-compatible object storage**, EU region, SSE-KMS encryption, private buckets, short-lived signed URLs | Standard, cheap, encrypted | — |
| PDF | Server-side HTML → PDF (headless Chromium / Playwright) from the same templates used on screen | One template = identical screen and print | — |
| Search | **Postgres full-text search** (per-language configs: `german`, `italian`, `english`, …) | Enough for "find patient / find consultation" in MVP | OpenSearch later; pgvector for semantic history search in Phase 2 |
| Hosting | One cloud, **EU region** (e.g. AWS eu-central-1 / Frankfurt or GCP europe-west), containers (ECS/Fargate or Cloud Run), IaC (Terraform) | Data residency, GDPR, simple ops | Multi-region later |
| Observability | OpenTelemetry traces + structured logs **with PHI/PII redaction**; error tracking (Sentry EU or self-hosted) | Debuggability without leaking clinical text into logs | — |

All choices are reversible except PostgreSQL and the "structured record is the
source of truth" data model — those are the two load-bearing decisions.

---

## 3. Data model

### 3.1 MVP entities (build now)

```
organization (clinic)            ── tenant boundary; settings: locale, units, templates, SOAP on/off
 ├─ membership (user ↔ org, role)
 ├─ client (owner)                ── minimal: display name, preferred language, contact (optional in MVP)
 ├─ patient (animal)              ── name, species, breed, sex/neuter, DOB or age, weight, microchip (optional, string)
 │   └─ consultation              ── date, clinician, reason, status: draft → in_review → approved → amended
 │       ├─ note_input            ── raw text the vet typed (immutable once submitted; new rows for edits)
 │       ├─ clinical_record       ── STRUCTURED JSON (schema-versioned), versioned; one row approved
 │       │                           (the single source of truth for all generated documents)
 │       └─ document              ── type (consult_report, soap, discharge, owner_summary, referral, email…),
 │           │                       language, status (draft/approved/superseded)
 │           └─ document_version  ── immutable content + author (human|ai) + parent version
 ├─ template                      ── clinic-customisable section layout / letterhead per document type
 └─ audit_event                   ── append-only; who, what, when, before/after hashes
user
ai_generation                     ── model id, prompt id+version, input hash, output, validator results,
                                     latency, tokens; linked to the record/doc version it produced
approval                          ── who approved which version, when, role, attestation text
```

### 3.2 The key design decision: record first, documents second

```
note_input (raw bullets)
   │  AI extraction (structured, schema-validated, grounded)
   ▼
clinical_record  ── vet reviews / edits / approves  ──►  APPROVED record (versioned)
   │
   ├─► consultation report   (render)
   ├─► SOAP note             (render)
   ├─► discharge summary     (render + AI prose)
   ├─► owner explanation     (AI prose, plain language, from approved record only)
   ├─► referral letter       (render + AI prose)
   └─► translation           (AI, from approved document; medication table re-rendered, not translated freely)
```

Documents are **views of an approved record**, not independent AI essays. This
gives us:

- one approval that all downstream documents inherit facts from;
- no re-entry of information;
- medication and vitals rendered **deterministically by code** from structured
  fields, so a model can't silently change a dose while "rewording";
- a diff-able, auditable history.

Documents still need their own review/approval (a vet should read the owner text
before it goes out), but they can only contain facts present in the approved
record — enforced by validators (§4.4).

### 3.3 Later entities (design the seams, don't build)

appointment · diagnosis (coded) · treatment · medication (catalogue-backed) ·
lab_result · attachment (imaging, PDFs) · vaccination · access_grant (owner →
clinic/vet, scoped, time-limited) · owner account · animal_identity (microchip ↔
registry, kept **separate** from medical access) · integration_connection
(per-PIMS credentials, scopes) · external_reference (our id ↔ PIMS id).

Identity, ownership and medical-record access are three different tables and
three different permission checks. A microchip number resolves at most to
"a profile exists"; it never grants read access to medical data.

---

## 4. AI architecture

### 4.1 Principles turned into mechanisms

| Principle | Mechanism |
|---|---|
| Don't invent facts | Extraction into a strict JSON schema; every clinical field carries `source_span` (offsets into the vet's text). Unsupported → `null` + `missing` flag. Post-validators reject values not found in the input. |
| Never alter medication | Medication = structured object `{drug, strength, dose, dose_unit, route, frequency, duration, instructions, source_span}`. Rendered by code in every document. Validators check every drug name and every number against the source text. LLM prose may *refer* to medication but the table is canonical. |
| Human approval | Status machine enforced in the API: nothing leaves `draft` without an `approval` row from a user with an approving role. Exports/PDF of unapproved content are watermarked **DRAFT**. |
| Traceability | `ai_generation` row per call: model, prompt version, input hash, raw output, validator results. Every `document_version` points to its generation or its human author. |
| Minimise data sent | Owner contact data is never sent to the model. Patient identity reduced to what the document needs (name, species, breed, sex, age, weight). |
| Deterministic where possible | Headings, patient header, vitals, medication tables, dates, clinic letterhead: templates. AI only for (a) parsing messy input, (b) prose sections, (c) plain-language and translation. |

### 4.2 Pipeline for one consultation

1. **Normalise input** (code): trim, detect language, expand the clinic's own
   abbreviation dictionary (e.g. `bid` → twice daily, `SC`, `IV`, `q12h`,
   German/Italian clinic shorthand). Unknown abbreviations are left as-is and
   flagged, never guessed.
2. **Extract** (LLM, structured output): notes + patient header → `ClinicalRecord`
   JSON (schema in `03-mvp-spec.md` §6). Structured outputs / strict tool schemas
   guarantee shape; content is checked next.
3. **Validate** (code):
   - every numeric value (temp, weight, HR, RR, doses, durations) appears in the
     input text (unit-aware: `39.1`, `39,1`);
   - every drug name appears in the input (fuzzy match for typos → flag, not fix);
   - no section filled that has no `source_span`;
   - required-for-document fields present, else listed as **missing**;
   - species-plausibility warnings (e.g. temperature outside a species range) shown
     as *warnings for the vet*, never auto-corrected.
4. **Render draft report** (template + short AI prose for narrative sections,
   generated *from the structured record only*, not from the raw notes).
5. **Vet review**: side-by-side notes ↔ report, missing/uncertain items
   highlighted, inline edit, `Ctrl+Enter` approve.
6. **Derived documents** on demand from the approved record: same validators run
   on every output (a drug or number appearing in an owner letter that isn't in
   the approved record = block + highlight).

### 4.3 Model and provider

- Provider-agnostic **AI gateway** module: one interface (`extractRecord`,
  `writeSection`, `plainLanguage`, `translate`), adapters per provider, prompts
  versioned in the repo, **evals in CI** (see §4.5).
- Initial candidate: Anthropic Claude via API — strong at structured extraction,
  instruction following and EU languages. Start with the most capable current
  model for extraction (e.g. `claude-opus-5`) and only move routine steps
  (translation, plain-language rewrite) to a cheaper model (e.g.
  `claude-sonnet-5` / `claude-haiku-4-5`) when the eval suite shows no quality
  loss. Use structured outputs / strict tool schemas for extraction, prompt
  caching for the long stable system prompt + schema + clinic templates.
- **Data residency must be verified, not assumed.** As of this writing the
  first-party Claude API's `inference_geo` control offers `us` / `global`; EU
  in-region processing is available through cloud platforms (Google Vertex AI
  EU regions, Amazon Bedrock EU regions), but *which models are served in which
  EU region* changes and must be confirmed before contracting. Whatever route is
  chosen: a DPA, no training on customer data, the shortest available
  retention (zero-data-retention where the provider offers it for the chosen
  model), and a documented transfer mechanism if any processing leaves the EEA.
- Keep a second provider adapter tested (even if unused) so a pricing, outage or
  residency change doesn't block the product.

### 4.4 Output validators (shared library, used on every AI output)

`grounding` (facts ⊆ source) · `medication_integrity` (drug/dose/route/frequency/
duration identical to approved record) · `numbers_integrity` · `no_new_diagnosis`
(owner texts may not introduce diagnoses not in the record) · `language` (output
is in the requested language) · `length/format`. Failures never silently
"auto-fix": they block approval and show the vet what failed.

### 4.5 Evaluation from day one

A synthetic, vet-reviewed test set (start ~150 cases: species × presenting
problem × note style × language, including abbreviations, typos, contradictory
notes, missing temperature, multiple drugs). Metrics, tracked per prompt/model
version in CI:

- field-level extraction precision/recall;
- **hallucination rate** (any value not in source) — target 0 on medication/
  numbers; any non-zero blocks release;
- missing-information detection recall;
- vet edit distance on review (from pilot telemetry, see MVP metrics).

---

## 5. Permissions (RBAC now, ABAC-ready)

| Action | Vet | Nurse / assistant | Reception | Clinic admin | Clinic owner |
|---|---|---|---|---|---|
| Create patient | ✓ | ✓ | ✓ | ✓ | ✓ |
| Enter clinical notes / draft | ✓ | ✓ (drafts) | ✗ | ✗ | ✓ if vet |
| **Approve clinical record** | ✓ | ✗ | ✗ | ✗ | ✓ only if also a vet |
| Generate owner/discharge docs | ✓ | ✓ (drafts) | ✗ | ✗ | — |
| Approve owner-facing docs | ✓ | configurable per clinic | ✗ | ✗ | — |
| Send / export approved docs | ✓ | ✓ | ✓ | ✓ | ✓ |
| Manage users, templates, settings | ✗ | ✗ | ✗ | ✓ | ✓ |
| Read audit log | own actions | own | own | ✓ | ✓ |

- "Clinical approver" is a capability attached to a verified veterinarian
  membership, not to a job title string.
- Enforced twice: in the API service layer **and** by Postgres RLS on
  `organization_id` (defence in depth against a missing `WHERE`).
- Owner/pet-parent role arrives with the owner app and will be driven by
  `access_grant`, not by clinic membership.

---

## 6. Audit logging

- `audit_event(id, org_id, actor_user_id, actor_type[user|system|ai], action,
  entity_type, entity_id, entity_version, at, ip_hash, user_agent_hash,
  before_hash, after_hash, prev_event_hash)`.
- Append-only: DB role used by the app has `INSERT` only on this table; hash chain
  (`prev_event_hash`) makes tampering detectable; nightly anchor of the chain head
  to write-once storage (S3 Object Lock).
- Logged: login/MFA, patient create/update, note submit, every AI generation,
  every edit, approval, export/print/copy-to-clipboard, document sent, settings
  and role changes, data export/deletion requests.
- Clinical text is **not** duplicated in the audit log — it references immutable
  versions by id + hash.

---

## 7. API architecture

- `/api/v1/...` REST, JSON, OpenAPI 3.1 published internally from day one.
  Resource-oriented: `/patients`, `/consultations/{id}/notes`,
  `/consultations/{id}/record:extract`, `/records/{id}/versions`,
  `/records/{id}:approve`, `/documents`, `/documents/{id}:render?format=pdf`.
- Idempotency keys on generation and approval endpoints (double-click safety).
- Long AI calls: server streams progress to the browser (SSE) so the section
  headings appear immediately and the vet can start reading.
- **Integration layer (Phase 2) is a separate module** with one adapter per PIMS,
  built *only* on each vendor's documented API under a partner agreement. Each
  adapter implements the same small port:
  `listTodayAppointments`, `getPatientSummary`, `writeBackNote(approvedDocument)`.
  No screen scraping, no stored clinic PIMS passwords, no RPA against UIs we
  aren't licensed to automate. Where no API exists, the fallback is
  copy/paste, PDF, and structured export — honestly labelled.
- Interop standards to watch for the network phase: HL7 FHIR (there is no
  widely adopted veterinary FHIR profile we can rely on — treat as research, not
  assumption), VeNom / SNOMED CT veterinary extension for coded diagnoses,
  ISO 11784/11785 for microchip numbers.

---

## 8. Security (summary — full model in `05-security-model.md`)

TLS 1.2+ everywhere, HSTS · encryption at rest (managed KMS) · per-tenant RLS ·
MFA for clinical roles · short sessions with re-auth for approval · secrets only
in a secret manager (never in the repo; pre-commit secret scanning) · least-
privilege IAM · redacted logs · dependency and container scanning in CI ·
**synthetic data only in dev and staging** · backups encrypted, restore tested.

---

## 9. Deployment

- Environments: `dev` (synthetic data), `staging` (synthetic data, prod-like),
  `pilot/prod` (real data only after the security gate in `05-security-model.md`
  §9 is passed).
- CI: typecheck, lint, unit tests, AI eval suite (on prompt/model changes),
  migrations dry-run, SAST, dependency audit, container scan, secret scan.
- CD: IaC (Terraform); blue/green for API; DB migrations backward-compatible
  (expand → migrate → contract).
- Region: single EU region with cross-AZ Postgres; point-in-time recovery;
  documented RPO ≤ 15 min, RTO ≤ 4 h for pilot.

---

## 10. What we are deliberately *not* building yet

Voice capture · owner app · PIMS integrations · microchip lookup · attachments/
imaging · lab parsing · desktop app / side panel · semantic history search ·
billing. Each has a seam above; none has code.
