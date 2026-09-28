# Costs — market prices and our own cost to build and run

All figures are estimates for planning. Competitor prices come from
`01-competitive-analysis.md` (check live vendor pages before quoting them).
Our costs are rough ranges: verify them with real quotes and a measured pilot.

---

## 1. What the market charges (per vet, per month)

| Segment | Products | Public price |
|---|---|---|
| Free tiers | Scribenote, CoVet, PawfectNotes (50/mo), Curala (10/mo) | €0 |
| Entry | PawfectNotes $29, ScribbleVet Essential $40 (150 notes), CoVet $46, ScribVet $49, VetGeni $50, Squako €57 | €30–60 |
| Standard | Petleo.ai from €79, Scribenote Pro $79–99, VetRec $99–150, CoVet Unlimited $99, Curala €85 | €80–150 |
| Practice-wide | HappyDoc from $119 (unlimited users), Otto $169 (unlimited users) | per clinic |
| Top tier | ScribbleVet Unleashed $150–200/DVM | €150–200 |
| Bundled | Covetrus AI free in Pulse; ezyVet, Provet, Digitail, Shepherd, Vetspire include AI in the PIMS subscription | €0 extra |

**Takeaway:** the going rate is **€40–100 per vet per month**, with free tiers
setting the floor. A price above ~€100 needs proof of time saved.

**Working hypothesis for AI Veterinary** (to test in discovery, not decided):

| Plan | Price | Includes |
|---|---|---|
| Trial | 30 days free | full product |
| Vet | €59–79 / vet / month | unlimited consultations, all document types, 3 languages |
| Nurse / reception seats | free | draft + export, no approval |
| Clinic group | custom | SSO, central templates, later integrations |

---

## 2. AI cost per consultation (our biggest variable cost)

Assumed tokens for one routine consultation:

| Step | Input tokens | Output tokens |
|---|---|---|
| Extract notes → structured record | ~4,000 (instructions + schema, cacheable) + ~300 notes | ~1,500 |
| Draft report prose | ~2,000 | ~800 |
| 2 derived documents (e.g. owner + discharge) | ~2 × 2,000 | ~2 × 700 |
| **Total** | **~10,000** (most cacheable) | **~3,700** |

Anthropic first-party list prices (per million tokens, input / output):
Claude Opus 5 $5 / $25 · Claude Sonnet 5 $2 / $10 · Claude Haiku 4.5 $1 / $5.
Cached input reads cost much less than normal input.

| Model mix | ≈ cost per consultation | ≈ per vet per month (400 consults) |
|---|---|---|
| All Opus 5 | $0.10–0.14 | $40–56 |
| Opus 5 for extraction, Sonnet 5 for prose/translation | $0.06–0.08 | $24–32 |
| All Sonnet 5 (only if evals show no quality loss) | $0.04–0.05 | $16–20 |

These assume 20 consults a day for 20 days. Most GP vets do fewer, but emergency vets can do more.

**Conclusions:**
- **At €59–79 per vet, running everything on the top model would take half the revenue.**
  - Use the strongest model where accuracy matters most (extraction).
  - Use cheaper models for rewriting and translation once the eval suite shows no quality loss.
  - Cache the long, stable instructions.
  - Add a fair-use limit.
- EU-region processing through Google Vertex AI or Amazon Bedrock is **priced separately**. Get quotes before committing.
- Measure the real token counts in the prototype. Don't budget from this table.

---

## 3. Running costs (infrastructure, pilot scale: under 50 vets)

| Item | ≈ €/month |
|---|---|
| Hosting: containers, managed Postgres (EU, high availability), object storage, backups | 300–700 |
| Login provider with MFA (depends on vendor and user count) | 0–250 |
| Monitoring, error tracking, logs | 50–200 |
| Email, domain, CDN/WAF | 30–100 |
| **Total excluding AI** | **≈ 400–1,250** |

## 4. One-off costs before real clinical data

| Item | ≈ € |
|---|---|
| Legal: data processing agreement, privacy policy, terms, DPIA support (GDPR) | 5,000–20,000 |
| External penetration test | 5,000–15,000 |
| Trademark "AI Veterinary" (EU + key markets) | 1,000–3,000 |
| Vet advisors for the test cases and review (paid hours) | 3,000–10,000 |
| Later: ISO 27001 or SOC 2 | 20,000–60,000 + yearly audit |

## 5. Building the MVP (people are the main cost)

| Option | Team | Time | ≈ Cost |
|---|---|---|---|
| Lean | 1 senior full-stack engineer + part-time designer + vet advisor | 5–7 months | €70k–150k |
| Standard | 2 engineers + designer + part-time vet/product lead | 4–5 months | €150k–300k |
| Agency | outsourced build | 4–6 months | €120k–350k, with less control over quality and AI safety |

Ranges depend heavily on country and seniority. Founder time is not included.

## 6. Unit economics sketch (to verify in the pilot)

At €69 per vet per month:
- AI cost: €20–30
- Hosting and support share: ~€5–10
- **Gross margin: ~55–70%**

The margin improves with caching, cheaper models on eval-approved steps, and scale.
Break-even on €1,000 a month of fixed costs needs about 25–30 paying vets, before salaries.
