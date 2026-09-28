# A. Competitive analysis

Research date: 2026-09-28. Method: public web sources only (vendor sites,
developer portals, press releases, Capterra/G2, trade press). Every claim links a
source. Anything marked *unverified* came from a third-party, competitor or SEO
source, or couldn't be confirmed. Many "comparison" articles in this market are
written by competing vendors, so they count as weak evidence. **Re-check all
prices and feature claims on the live vendor page before quoting them
externally.** No veterinarians have been interviewed yet, so "what vets hate"
below comes from public reviews, not from our own research.

---

## 1. Executive summary

1. **AI documentation is already a crowded, fast-moving category.** There are
   more than 20 standalone scribes (US, Canada, and a growing EU group) plus
   AI built into every modern practice-management system (PIMS). "AI writes the
   SOAP note" is no longer a differentiator on its own.
2. **The big PIMS vendors are bundling AI scribes, often at no extra cost.** Covetrus AI
   is "at no additional cost in Covetrus Pulse" ([Covetrus](https://covetrus.com/newsroom/covetrus-announces-ai-powered-workflow-automation-and-treatment-board-capabilities-enhancing-the-covetrus-platform/)).
   ezyVet's AI-Assisted Notes is rolling out to US customers ([ezyVet](https://www.ezyvet.com/blog/2025-checkup)).
   Provet launched a Clinical AI Agent and announced an MCP server for external AI in July 2026 ([Cision](https://news.cision.com/nordhealth-oy/r/provet-launches-the-first-all-in-one-veterinary-pims-built-for-ai-agents,c4366240)).
   Digitail, Shepherd, Vetspire and Instinct (which bought ScribbleVet in Jan 2026) also have it built in.
3. **Nearly every competitor is voice-first.** Ambient recording is the category's
   core promise. Typed input exists (CoVet, VetGeni, VET7.AI structured input), but
   it's a secondary text box, not the design centre.
4. **Europe has local standalone scribes with EU hosting.** Examples:
   Vetnio (Stockholm, YC, IVC Evidensia partnership), Petleo.ai (Munich,
   integrated with Vetera/Provet), Curala (Innsbruck), Squako (Liège), and Vetomatic
   and ReqVet (France). EU hosting and GDPR are table stakes, not a differentiator.
5. **Gaps we could not find anyone publicly claiming:**
   - An **approved, versioned structured record** as the single source for all documents
   - **Missing-information flagging** before approval
   - **Medication integrity checks** against the vet's own input
   - **Sentence-to-source traceability**
   - A product **designed around keyboard shorthand**
   - A dedicated **Italian-language** vet documentation assistant (weak evidence: nothing turned up in search)
6. **Integration reality:** documented APIs exist for Provet Cloud, ezyVet,
   Vetspire, Digitail and Shepherd, and all of them require partner approval.
   Covetrus, IDEXX Cornerstone/Neo and Instinct are partner-only with no public docs.
   Most EU local systems have no public API information at all.

**Implication for AI Veterinary:** a basic scribe won't win. A plausible wedge is
the **governance model** (text-first input → one approved structured record →
every document derived from it with traceability, missing-info prompts and
medication checks), aimed first at **clinics on legacy or non-AI PIMS** in
**DE/IT markets**, where bundled AI hasn't arrived. This must be validated
with vets (§8).

---

## 2. Practice-management systems (what vets already have)

| PIMS | Owner | Main market | Native AI scribe | Public pricing | API |
|---|---|---|---|---|---|
| **ezyVet** | IDEXX | Global (US, AU/NZ, UK); groups, specialty | Yes, AI-Assisted Notes (US rollout) | "from $260.50/month" ([ezyVet](https://www.ezyvet.com/pricing/us)) | Documented REST, 216 endpoints, OAuth2; partner application + certification ([developers.ezyvet.com](https://developers.ezyvet.com/)) |
| **Provet Cloud** | Nordhealth | Nordics, UK, EU, US pilot; 3,000+ clinics, 45 countries | Yes, AI Scribe, Clinical AI Agent; MCP "coming soon" | Quote-based ([Provet](https://www.provet.cloud/pricing)) | Documented REST, OAuth2; partner onboarding ([developers.provetcloud.com](https://developers.provetcloud.com/restapi/)) |
| **Covetrus Pulse** | Covetrus | US GP | Yes, free in Pulse | Not public | Covetrus Connect, partner-only ([Covetrus](https://covetrus.com/covetrus-platform/workflow-and-productivity-tools/technology-integration-hub/)) |
| **AVImark / ImproMed** | Covetrus | US legacy | None found | Not public | Covetrus Connect (partner) |
| **RoboVet / RxWorks** | Covetrus | UK-IE / AU-NZ | None found | Not public | Unclear / Connect APAC |
| **Cornerstone** | IDEXX | US, on-prem SQL Server | None, per third party ([Vet Clinic Tech](https://vetclinictech.com/idexx-neo-vs-cornerstone/)) | Not public | No public API; approved partners only ([IDEXX](https://software.idexx.com/cornerstone-integrations)) |
| **Neo** | IDEXX | US small practice, cloud | None, per third party | Not public | Partner-gated, limited |
| **Animana** | IDEXX | UK/EU cloud | None found | Not public | API docs page exists, access-restricted (*unverified*) |
| **Digitail** | Independent | US/EU, "AI-native" | Yes, Tails AI, plus the standalone **Tails VIP** app for other PIMS | No figures published | Documented REST, OAuth2+PKCE; reviewed access + DPA ([docs](https://documentation.digitail.io/)) |
| **Shepherd** | Independent | US GP | Yes, TranscribeAI | ~$299/mo + $99/DVM (*unverified*) | Public OpenAPI portal ([developer.shepherd.vet](https://developer.shepherd.vet/)) |
| **Vetspire** | Thrive Pet Healthcare | US | Yes, AI Scribe | Not public | GraphQL, token via support ([developer.vetspire.com](https://developer.vetspire.com/)) |
| **Instinct EMR** | Instinct Science | US ER/specialty | Yes, owns ScribbleVet | Not public | "Partner API", no public docs |
| **Vetera** | Nordhealth | DACH, ~18,000 users | Via Petleo.ai (Nordhealth holds 19.26%) ([Vetera](https://www.vetera.net/ki-dokumentation/)) | Not public | Unclear |
| **easyVET** | VetZ GmbH (not IDEXX) | DACH | Via ReportAssistant ([VetZ](https://www.vetz.de/ki-dokumentation-herausforderungen-vor-dem-einsatz-im-praxisalltag/)) | Not public | Unclear |
| **VET7.well** | VET7 | DE | Yes, VET7.AI (voice + structured input, approval, audit) ([vet7.net](https://www.vet7.net/ki-dokumentation-mit-vet7-well-vet7-ai-die-zukunft-der-tiermedizin/)) | Not public | Unclear |
| **Vetocom / Vetup** | FR vendors | France | Vetup integrates Vetomatic | Vetup ~€29 + €19 hosting (*unverified*) | Unclear |
| **Italian systems** (dr.veto, VetsGo, VetinCloud, Vets On Line, GVET, …) | various | Italy, fragmented | Some AI chat/templates (VetinCloud, Laika) | Mostly not public | Unclear |

**What users report** (Capterra, where available):
- **ezyVet:** strong integrations; "too many steps", steep learning curve, slowness ([Capterra](https://capterra.com/p/99977/ezyVet-Cloud-Vet-Software/reviews/)).
- **Covetrus Pulse:** glitches, outages, confusing record flow; support praised ([Capterra](https://capterra.com/p/130107/Covetrus-Pulse/reviews/)).
- **Cornerstone:** outdated, crashes and freezes, poor navigation ([Capterra](https://www.capterra.com/p/99976/Cornerstone-Practice-Management/reviews)).
- **Provet Cloud:** customisation praised; support and migration complaints ([Capterra](https://www.capterra.com/p/137569/Provet-Cloud/reviews)).
- **Digitail:** ease of use ([Capterra](https://www.capterra.com/p/167764/Digitail/reviews/)).

**The pattern:** documentation takes many clicks in a slow, form-heavy PIMS.
Nobody praises their PIMS's writing experience.

---

## 3. AI documentation products

### 3.1 Standalone scribes (North America)

| Product | Input | Typed source notes? | Outputs | PIMS route | Public price | Claims |
|---|---|---|---|---|---|---|
| **ScribbleVet** (Instinct) | Ambient voice | *unverified* | SOAP, dental charts, Care Cards, client emails, record summaries, Plumb's | 1-click ezyVet/Pulse/Vetspire; Chrome companion; copy | $40/mo for 150 notes; $150–200/DVM ([site](https://www.scribblevet.com/)) | SOC 2 T2 |
| **VetRec** (YC S23) | Ambient, phone, watch | *unverified* | SOAP, 30+ templates, records recap, discharge in client language | "12+ PIMS" one-click, structured copy | $99–150/vet, unlimited ([pricing](https://vetrec.io/pricing)) | SOC 2 II, "GDPR" |
| **CoVet** | Voice + typed | Claimed | SOAP, referral, discharge, 85+ templates | Cornerstone, AVImark, Provet, Merlin… | Free / $45.83 / $99 ([pricing](https://co.vet/pricing/)) | ISO 27001, SOC 2; 11 languages incl. DE/IT/FR |
| **Scribenote** (a16z seed) | Voice (+typed listed) | *unverified* quality | SOAP, client summaries | Included on all tiers | Free / $79–99 ([pricing](https://www.scribenote.com/pricing)) | Free-tier data may be used for improvement |
| **HappyDoc** | Phone recording, calls | Edits only | SOAP, dental charts | Native AVImark/Cornerstone; extension | From $119/mo unlimited users ([site](https://happydoc.ai/)) | "99.8% accuracy" (vendor claim) |
| **Talkatoo** | Dictation + ambient | *unverified* | Records, follow-ups, call summaries | Copy/paste only | ~$40–126 (*unverified*) | Reviews: weak on drug names ([Capterra](https://www.capterra.com/p/198507/Talkatoo/)) |
| **VetGeni** | Voice + text | Yes | SOAP, discharge, translated discharge | Cornerstone, ezyVet, Pulse… | $50/doctor ([site](https://www.vetgeni.com/)) | Wiley-referenced drug DB; published validation page |
| **PawfectNotes** | Voice | *unverified* | SOAP, discharge, referral, specialty reports | 19 PIMS, extension | Free 50/mo; from $29 ([site](https://pawfectnotes.com/)) | 41 languages; "GDPR" |

### 3.2 European scribes (our most direct competitors in DE/IT/FR)

| Product | HQ | Input | PIMS route | Price | Hosting / claims |
|---|---|---|---|---|---|
| **Vetnio** | Stockholm (YC W25) | Voice, calls | *unverified* | Not public | "All data remains in the EU"; IVC Evidensia partnership in SE/ES/PT ([vetnio](https://vetnio.com/news/building-vetnio-with-evidensia)) |
| **Petleo.ai** | Munich | Recording, dictation, retroactive | Vetera, Vet7well, TPV, Provet, VetStar + overlay | From €79/mo ([petleo](https://vet.petleo.net/petleo-ai)) | DE/FR hosting; vet releases each note |
| **ReportAssistant** | DE | *unverified* | easyVET | *unverified* | — |
| **Curala** | Innsbruck | Voice, dictation | Copy/export | €0–85/mo ([curala](https://www.curala.at/ki-dokumentation-tierarztpraxis)) | EU (AT) servers, no audio kept; 60+ languages → German |
| **Squako** | Liège | Voice | Copy-paste | €57/mo ([squako](https://squako.com/)) | EU, audio deleted; FR/EN/NL |
| **Vetomatic** | France | Audio | VetUp | Not public | HDS-certified EU servers ([vetomatic](https://vetomatic.com/)) |
| **ReqVet** | France | Dictation | *unverified* | Trial | Audio 24 h, reports 30 days ([reqvet](https://www.reqvet.com/)) |

### 3.3 Owner-facing / pre-visit (relevant for later phases)

- **Petriage:** vet-validated 4-level urgency checker. Free for owners; clinics pay $49.99–199.99/mo; the top tier includes PIMS integration ([pricing](https://petriage.com/pricing/)). This is the closest analogue to our "pre-visit brief sent to the clinic".
- **Joii** (UK): free symptom checker plus £28 video consults ([joii](https://www.joiipetcare.com/)).
- **FirstVet:** video vet in 7 countries, distributed via insurers ([firstvet](https://firstvet.com/)).
- **Dogtor** (Canada): "vet-ready" pre-visit summaries ([hellodogtor](https://hellodogtor.com/)).
- **PETSVETCHECK** (DE): symptom checker ([petsvetcheck](https://petsvetcheck.de/en/symptoms/about-the-symptom-checker/)).
- **Pawp and Vetster:** human telehealth, not AI-first.

---

## 4. Time and burnout evidence (sourced only)

- **Veterinary residents (NC State, peer-reviewed, 2026):** median after-hours EMR use was
  13.6 h/month on weekdays and 23.4 h/month on weekends. First-year residents were 4.6× more likely
  than third-years to chart after hours ([Frontiers in Vet Sci](https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2026.1951548/full)).
- **EU (FVE admin-burden survey, n=75, 2024–25):** 64% said admin workload had
  doubled; prescribing/dispensing documentation was the most time-consuming;
  most admin is unpaid ([FVE](https://fve.org/understanding-the-growing-administrative-burden-in-veterinary-practice/),
  via search summary because the page was unavailable at fetch time).
- **UK (RCVS/IES, 2022):** 53% of vets working overtime were not paid for it ([Vet Times](https://www.vettimes.com/news/business/human-resources/more-than-half-of-all-vets-working-overtime-not-being-paid-for-extra-hours-new-report)).
- **US (Merck/AVMA Wellbeing Study IV, 2024):** serious psychological distress remains
  a concern ([AVMA](https://www.avma.org/news/veterinary-profession-heading-right-direction-mental-health)).
  Exact percentages still need extracting from the JAVMA primary text.
- **Do not use in pitch material** (no primary source found): "30–40% of hours
  on documentation", "6.2 h/week after-hours (VIN 2024)", "28% of workday admin
  (AVMA 2023)".
- **Vendor time-savings claims** (unverified marketing): Covetrus says up to 5 min per
  appointment; Vetspire says up to 90 min/day.

---

## 5. Integration feasibility

| Tier | Systems | Route | Notes |
|---|---|---|---|
| **A: documented API, partner approval** | Provet Cloud, ezyVet, Vetspire, Digitail, Shepherd | Apply to partner programme; sandbox; certification | Provet is the best EU fit and has an MCP direction. ezyVet's process includes a 6-month dev window, a certification demo, and a 5-site pilot ([ezyVet](https://developers.ezyvet.com/apply/commercial.html)). All five ship competing native AI. |
| **B: partner-only, no public docs** | Covetrus Connect (Pulse, AVImark, ImproMed), IDEXX Cornerstone/Neo/Animana, Instinct | Commercial agreement | Largest legacy installed base **without** native AI. Long lead times. Cornerstone is on-prem. |
| **C: no public API info** | easyVET, Vetocom, Vetup, RoboVet, Merlin, Teleos, VetNet, Italian systems | Direct outreach | Local AI partnerships already exist (easyVET–ReportAssistant, Vetup–Vetomatic, Vetera–Petleo), so vendors accept partners but may prefer exclusive ones. |

**Open questions to verify with vendors:** can third parties write free-text
clinical notes via the ezyVet, Provet or Digitail APIs? What does Covetrus Connect
cost and which data does it cover?

**Browser extensions:** ScribbleVet's Chrome companion writes into several PIMS
([Chrome Web Store](https://chromewebstore.google.com/detail/ScribbleVet%20Browser%20Companion/gbcmfinnjfigkegmhplcpfflfkkjpgbm)).
This works commercially, but where the PIMS vendor hasn't sanctioned it, it carries
support and terms-of-service risk. **Our policy:** only official APIs, or
clipboard/PDF export, until an agreement exists.

---

## 6. What existing products don't do well (opportunities)

**What competitors already do.** Do not claim these as unique:
- Multilingual output (CoVet, PawfectNotes, Curala, VetRec discharge)
- EU hosting and GDPR (all EU scribes)
- Discharge, referral and client-email generation (most)
- "Human review before transfer" messaging (all)
- Drug references (VetGeni, ScribbleVet with Plumb's)
- Free tiers and entry prices of $29–57

**Where we could plausibly differ.** Each point needs to be validated with vets:

1. **Text-first by design.** Keyboard shorthand, clinic abbreviation
   dictionaries, bullet expansion. It suits:
   - vets who type fast
   - shared or quiet rooms
   - owners who object to recording
   - languages where speech recognition is weaker
   - specialists who write structured findings

   Having no audio also removes consent and audio-retention questions. Digitail's
   own help centre notes all-party consent laws in several US states ([Digitail](https://help.digitail.io/en/articles/8684084-tails-ai-dictation)).
   **Risk:** ambient capture saves typing, which is the category's main value.
   Text-first must prove it beats typing straight into the PIMS. This is the #1
   assumption to test.
2. **One approved, versioned record feeds every document.** Competitors generate
   documents from a transcript. Nobody publicly describes these together:
   - locking an approved structured record
   - deriving owner, referral and translated documents only from it
   - sentence-to-source highlighting
   - re-flagging downstream documents on amendment
3. **Missing-information prompts before approval.** Examples: dose without
   weight, drug without route or duration, referral without the question for the
   specialist. No public claim found. Enterprise tools might do this privately.
4. **Medication integrity.** No drug or number can appear unless the vet typed
   it, and medication tables are rendered by code in every language. This is a
   direct response to the documented hallucination failures, such as a male dog
   recorded as pregnant because the owner was, and invented drug names or doses
   ([vetsoftwarehub](https://www.vetsoftwarehub.com/article/veterinary-ai-scribe-buyers-guide)).
5. **Owner documents in the owner's language with verbatim medication.** The vet
   gets a side-by-side check, even for a language they don't speak.
6. **Italy.** Fragmented PIMS market and no dedicated Italian scribe found.
   German-speaking markets are more contested (Petleo, Curala, VET7.AI,
   ReportAssistant, Vetnio).
7. **PIMS-agnostic.** For clinics on Cornerstone, AVImark, RoboVet and EU local
   systems, no bundled AI is coming soon.

---

## 7. Strategic risks

- **Bundling:** PIMS vendors give AI away for free (Covetrus) or build it in (Provet,
  ezyVet, Digitail). Clinics on those systems may never need us.
- **Distribution:** Vetnio + IVC Evidensia, and Petleo + Nordhealth, show that EU
  distribution comes through groups and PIMS owners, not app stores.
- **Price floor:** free tiers exist. Our pricing must follow measured time saved.
- **Integration gatekeepers:** partner programmes take 6–12 months and can refuse
  a competitor.
- **Text-first adoption risk** (§6.1).

---

## 8. What to validate next (feeds MVP discovery)

1. Time a vet typing a routine consult note into their PIMS today, then time the
   same note with AI Veterinary. Is the gain real without voice?
2. Do vets value missing-info prompts and traceability, or see them as friction?
3. Which PIMS do target clinics in DE/IT use, and are they getting bundled AI?
4. Would clinics pay €40–100/vet/month for this? Who decides: the owner or the group?
5. Is the Italian gap real? Interview Italian vets and search Italian vet forums.
6. Contact the Provet and ezyVet partner teams early, to learn the terms and whether
   free-text clinical note write-back is allowed.
