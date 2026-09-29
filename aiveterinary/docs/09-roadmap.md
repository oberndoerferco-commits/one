# Step-by-step plan — aiveterinary.org

Context: a side project next to Oberndörfer Milano, driven by love of animals
and by watching vets struggle at the computer. Budget and time are limited, so
the plan is ordered by **cheapest, lowest-risk, most-learning first**. Each
phase has a clear stop/go decision so the project never silently grows into a
second full-time business.

---

## The three parts, in the order to build them

| Part | For | Why this order |
|---|---|---|
| **1. Website + animal information** | owners, vets, search engines | Cheap, no clinical or legal risk, builds audience and mailing list, gives the vet tool a place to launch from |
| **2. Vet documentation tool (MVP)** | vets | The real product. Needs vet interviews, an eval set, security work and money. Start only after phase 1 proves interest |
| **3. Owner tools, animal profile, network** | owners, vets, clinics | Long-term vision. Only after the vet tool has paying users |

---

## Phase 0 — Foundations (weeks 1–2, mostly admin)

- [ ] Secure related domains if available: `aiveterinary.com`, `.de`, `.it`, `.eu`; check the trademark "AI Veterinary" in the EU.
- [ ] Decide the legal owner (a new company, or a division of the existing one). Clinical data later needs a clear controller/processor structure, so decide now.
- [ ] Set up the basics: GitHub repo for the site (separate from the Shopify theme), email (`hello@aiveterinary.org`), analytics that don't need cookies (Plausible or similar), a mailing-list tool.
- [ ] Recruit 5–10 vets you already know (your own vets first) as an informal advisory group. Offer them early access, not money.

**Stop/go:** none, this is groundwork.

## Phase 1 — Website and animal information (months 1–3)

**Goal:** a calm, trustworthy site that people find useful before any product exists, with two audiences on one domain.

### 1a. Site structure

```
aiveterinary.org
├── /                    Home: what this is, the two audiences, newsletter
├── /animals             Animal information (the content engine)
│   ├── /dogs, /cats, /rabbits, /horses, …   species guides
│   ├── /symptoms        "my dog is vomiting" style guides: what to watch, when to call a vet
│   ├── /conditions      plain-language explanations of common diagnoses
│   ├── /medications     what a vet-prescribed drug is for, how to give it (never dosing advice)
│   ├── /travel          taking animals between countries: pet passports, microchips, rabies rules
│   └── /first-aid       emergency basics + "go to a vet now" signals
├── /vets                For veterinary teams
│   ├── /documentation   the product page: the problem, the 12 commitments, waiting list
│   ├── /research        our published comparisons and findings (from the docs in this repo)
│   └── /quality         the future public quality page
├── /about               why this exists, who is behind it, the vet advisory group
└── /newsletter          one list, two segments: owners / vets
```

### 1b. Content rules (these are what make it trustworthy)

- Every animal-health article is **reviewed and signed by a named veterinarian** from the advisory group. Show the reviewer and the review date. Sites without this are ignored by vets and increasingly by search engines.
- Plain language, short, honest about uncertainty. Every symptom page ends with clear "see a vet today / this week / emergency now" guidance.
- **No diagnoses, no doses, no "instead of a vet".** The site prepares people for the vet; it does not replace one.
- German, Italian and English from the start, but launch with **one language done well** (Italian or German, whichever your first vets speak) and translate proven pages later.
- AI can draft, humans decide. Use AI to produce first drafts from a fixed outline, then the vet reviewer edits and signs. This is the same "AI drafts, professional approves" principle as the product, and you can say so.

### 1c. Build

- **Stack:** a static site generator (Astro or Next.js) with content in Markdown, hosted on Vercel/Netlify/Cloudflare Pages. Fast, cheap (€0–20/month), no database, no login, so no security risk yet.
- **Design:** follow `06-brand.md`: calm neutrals, one accent, real photographs of animals with people, no chatbot look. Mobile-first for owners (they search on phones), desktop-first later for the vet tool.
- **Launch content:** 20–30 articles, not 200. Pick the questions your own vets hear most.

**Cost:** hosting ≈ €0–20/month; vet reviewers paid per article (≈ €50–100 each) or in early access; design either DIY from the brand doc or a freelancer (≈ €2–5k).

**Stop/go at month 3:**
- ≥ 200 newsletter sign-ups, of which ≥ 30 vets → proceed to phase 2.
- Fewer → keep publishing, delay the product, no money lost.

## Phase 2 — Vet documentation tool, validated before built (months 3–9)

Follow `03-mvp-spec.md` §9. The order matters: **validate → measure → prototype → security → pilot**.

| Step | What | Exit criterion | Cost |
|---|---|---|---|
| 2.1 Interviews (month 3–4) | 12–15 vets, nurses, receptionists in DE/IT (MVP spec §10 has the questions); 3 half-days shadowing in clinics | Top 5 workflows written down; vets confirm they would type shorthand into a tool | your time + travel |
| 2.2 The typing test (month 4) | Time 5 vets writing a routine note in their current software vs. typing bullets + reviewing an AI draft (paper mock-up or throwaway prototype is fine) | Bullets + review is clearly faster (≥ 30 %). **If not, the text-first idea fails and you stop here having spent almost nothing.** | ≈ €0 |
| 2.3 Eval set + extraction (month 5–6) | 150–300 synthetic cases written with vets; the extraction schema; validators; CI that reports unsourced sentences and medication mismatches | 0 medication/number mismatches on the set | 1 engineer, ≈ €15–30k |
| 2.4 Clickable prototype (month 6–7) | The one-screen workspace from `04-ux.md` on synthetic patients | 5 vets complete notes → approved report → owner instructions unaided | same engineer |
| 2.5 Security gate (month 7–8) | `05-security-model.md` §9: DPA, DPIA, pen test, EU hosting, no real data before this | Checklist complete | ≈ €10–35k one-off |
| 2.6 Pilot (month 8–9) | 3–5 clinics, 15–25 vets, 6 weeks; measure time-to-approved, edit ratio, hallucination rate | ≥ 50 % less time than baseline; 0 medication errors; vets would pay | AI cost ≈ €25–30/vet/month |

**Cost of phase 2 overall:** €70–150k with one senior engineer (see `07-costs.md`). If that is more than the side project should carry, the alternatives are: a technical co-founder who takes equity, or a grant/accelerator (several EU and Italian programmes fund animal-health and AI start-ups), or stopping after 2.2 with the website as the outcome.

**Stop/go after the pilot:** paying pilot clinics → phase 3 and integrations. Otherwise the website and research remain a valuable, low-cost asset.

## Phase 3 — Owners, animal profile, network (year 2+)

Only after paying vets exist. In this order, because each step reuses the last:

1. **Owner pre-visit brief** (`brief` §12–13): the owner answers structured questions on the website, gets a printable/sendable summary. No AI diagnosis. This reuses the animal-information content and the same structured record format the vet tool uses.
2. **After-visit page**: the vet's approved owner instructions delivered as a clean page/PDF with medication schedule and "when to call" rules. This is just another document from the approved record.
3. **Animal profile**: vaccinations, medications, documents, timeline, owner-controlled sharing. Start as a simple owner account; legal design first (the security model §2 says the controller/processor roles change here).
4. **PIMS integrations**: Provet and ezyVet partner programmes first (`01-competitive-analysis.md` §5).
5. **Microchip and cross-border records**: country by country, official registries stay authoritative, identity ≠ ownership ≠ medical access.

## What to do this week

1. Register the extra domains and check the trademark.
2. Ask your own vets: "If I built a tool where you type five bullet points and get the finished report to approve, would you use it? What would stop you?" Write down the exact answers.
3. Pick the first language and the first 10 article topics from what those vets say owners ask most.
4. Choose the site stack and put up a one-page site with the newsletter signup, so the domain starts working now.
