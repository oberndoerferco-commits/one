# E. Security & privacy model

Written **before** any code that touches sensitive data. This is a design, not a
compliance claim: no certification, GDPR-compliance statement or regulatory
position may be published until the assessments in §9 are done by qualified
people.

---

## 1. What we protect

| Asset | Examples | Sensitivity |
|---|---|---|
| Owner personal data | name, address, phone, email, payment later | **Personal data under GDPR** (the owner is the data subject) |
| Clinical records | notes, reports, diagnoses, medications | Confidential professional records; often linked to an identifiable owner → personal data in practice. Veterinary professional-secrecy rules vary by country (to verify per market). |
| Staff data | vet names, logins, activity logs | Personal data |
| Microchip numbers | ISO 11784 IDs | Identifier; linkable to owner via registries → treat as personal data |
| AI artefacts | prompts, outputs, eval sets | Contain clinical text → same class as records |
| Secrets | API keys, DB credentials, signing keys | Critical |

Animal health data is not a GDPR "special category" (that is human health), but
it is linked to identifiable people and is professionally confidential. We treat
it at a level comparable to human health data where practical — it costs little
extra and it's what clinics will expect.

## 2. Roles under GDPR (expected, to confirm with counsel)

- **Clinic = controller** of its client and patient records.
- **AI Veterinary = processor** for the clinic, acting only on documented
  instructions (DPA with every clinic).
- **Sub-processors:** cloud host, LLM provider, auth provider, email/PDF
  services, error tracking. Listed publicly, each under a DPA, EU-located or
  covered by an adequate transfer mechanism (adequacy decision / SCCs + transfer
  impact assessment).
- The future **owner app / animal-health network** changes this: AI Veterinary
  may become a controller for owner accounts. That needs its own legal design
  before it's built.

## 3. Threat model (STRIDE, MVP scope)

| Threat | Example | Controls |
|---|---|---|
| Spoofing | stolen vet password, phishing | MFA mandatory (TOTP/WebAuthn, passkeys preferred); breached-password check; login anomaly alerts |
| Tampering | editing an approved record, rewriting audit log | immutable versions; append-only, hash-chained audit; DB role without UPDATE/DELETE on audit |
| Repudiation | "I never approved that" | approval tied to authenticated user + recent auth + attestation; audit event with hashes |
| Information disclosure | cross-tenant leak; logs containing notes; LLM provider retention | Postgres RLS on `organization_id` + service-layer checks + automated cross-tenant tests; log redaction; provider DPA, no training, minimal retention; data minimisation before prompts |
| Denial of service | abuse of AI endpoint, cost blow-up | per-user/per-org rate limits and spend caps; WAF; queueing |
| Elevation of privilege | receptionist approving records; IDOR on `/documents/{id}` | RBAC capability checks per endpoint; ids are UUIDv7 *and* authorised per request; tests for every endpoint's authz |
| **Prompt injection** | owner-supplied text (later: pre-visit brief, emails) containing "ignore instructions…" | AI has no tools/actions in MVP (text in, text out); outputs validated against source; untrusted content delimited and labelled; no AI output is ever executed or auto-sent |
| **AI error as a safety threat** | invented dose, dropped allergy | validators (grounding, medication integrity), human approval gate, DRAFT watermark, eval CI gate (see architecture §4) |

## 4. Controls

**Identity & access**
- OIDC provider, MFA enforced for all clinic roles; SSO (SAML/OIDC) for groups later.
- Sessions: httpOnly, Secure, SameSite=Lax cookies; idle timeout (default 30 min,
  clinic-configurable within limits); absolute timeout 12 h; re-auth to approve if
  auth age > 12 h.
- Least privilege RBAC (architecture §5). Staff offboarding revokes sessions immediately.
- Internal (our staff) access to customer data: **none by default**; break-glass
  access requires the clinic's ticketed consent, is time-boxed and logged in the
  clinic's own audit trail.

**Data protection**
- TLS 1.2+ (prefer 1.3), HSTS; encryption at rest via managed KMS; separate keys
  per environment; key rotation.
- Field-level encryption for owner contact data (application-level, so DB dumps
  alone don't expose it).
- Backups encrypted, in-region, retention 35 days, quarterly restore test.
- No clinical data in: logs, analytics, error trackers, URLs, email subjects,
  browser localStorage (drafts autosave to server; browser cache is cleared on
  logout).

**AI-specific**
- Only the fields a task needs are sent (owner contact data never).
- Provider contract: no training on our data, DPA, EU processing or documented
  transfer mechanism, the shortest retention the provider offers for the chosen
  model — verified in writing, not assumed from marketing pages.
- Prompts/outputs stored in our DB (not the provider's) for traceability, under
  the same retention as the record they belong to.
- Clinic-level switch to exclude its data from any product-improvement use; the
  default is **excluded**. Improvement uses synthetic data and explicit, opt-in,
  de-identified samples only.

**Application security**
- Secrets only in a cloud secret manager; never in repo, images or client bundles;
  pre-commit + CI secret scanning; rotation runbook.
- Dependency audit, SAST, container scanning in CI; signed builds; pinned base images.
- Security headers: strict CSP (no inline scripts), frame-ancestors none,
  Referrer-Policy strict-origin, Permissions-Policy minimal.
- Input validation at every API boundary (Zod schemas); output encoding in UI.
- PDF rendering in a sandboxed worker without network access.

**Operations**
- Separate cloud accounts/projects for dev, staging, prod.
- Prod access via SSO + MFA + just-in-time elevation; all admin actions logged.
- Alerting on auth anomalies, authz failures spikes, cross-tenant query attempts,
  unusual export volume.

## 5. Development data rule

- **Only synthetic data** in dev, staging, CI, demos, screenshots and eval sets.
- Synthetic cases are written with vets (realistic style, fictitious animals and
  owners). Realistic ≠ real: no copying of real records "with names changed".
- Real data enters only the production pilot, after §9 gate, under DPA with the
  clinic.
- Any real-world sample used to improve the product requires: clinic consent,
  de-identification review, separate storage, time-limited retention.

## 6. Data lifecycle

| Data | Default retention | Notes |
|---|---|---|
| Clinical records & versions | Clinic-controlled; default = as long as the clinic account exists | Many countries mandate multi-year retention for veterinary records — clinic decides per its law; we provide export |
| Raw notes | same as record | they are part of the record's provenance |
| AI generations (prompt/output) | same as the record they produced | needed for traceability |
| Audit events | ≥ record retention | append-only |
| App logs (redacted) | 30 days | no clinical content |
| Account deletion | clinic export offered → deletion within 30 days → backups age out ≤ 35 days | documented, confirmed in writing |

Data-subject requests (owner access/erasure) are routed to the clinic
(controller); we provide tools to fulfil them.

## 7. Integrations (future) — security rules now

- Only official, documented APIs under a written agreement with the vendor.
- OAuth / vendor-issued tokens scoped to the minimum; stored encrypted; revocable
  by the clinic.
- **Never**: storing clinic users' PIMS passwords, screen scraping, UI automation
  against systems we're not licensed to automate, reverse-engineered APIs.
- Write-back only of approved documents, only to fields the vendor designates.

## 8. Animal-health network (future) — principles to keep

- Identity (chip → "profile exists"), ownership, and medical access are separate
  permissions.
- Medical access only via explicit, scoped, time-limited, revocable owner grants,
  with an access log the owner can see.
- Lost-animal flow: finder/vet can trigger contact *through* us without seeing
  owner details; official national registries stay authoritative.
- Country-by-country legal review before connecting any registry.

## 9. Gate before any real clinical data (pilot)

- [ ] DPA template reviewed by counsel; sub-processor list published
- [ ] Data Protection Impact Assessment (DPIA) completed
- [ ] Records of processing (Art. 30) prepared
- [ ] LLM provider terms verified in writing: no training, retention, region
- [ ] External penetration test; criticals/highs fixed
- [ ] Cross-tenant isolation test suite green
- [ ] Backup restore test passed
- [ ] Incident response runbook incl. 72 h breach-notification path (to clinic as controller)
- [ ] Eval suite: zero medication/number hallucinations on current release
- [ ] Clinic-facing documentation: what the AI does/doesn't do, their responsibility to review
- [ ] Check country-specific rules for each pilot market (professional secrecy,
      record-keeping duties, any rules on AI in veterinary practice, EU AI Act
      classification assessment)

Longer term, depending on customers: ISO/IEC 27001 and/or SOC 2 Type II;
country-specific certifications if clinics or groups require them.
