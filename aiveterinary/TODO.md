# AI Veterinary — the backlog

The living to-do list. Research behind it: `docs/12-gaps-and-ideas.md`.
Everything costs €0 unless marked €. Legend:

- **Value** ★★★ must-have · ★★ strong · ★ nice
- **Effort** S (hours) · M (days) · L (weeks)
- **Only us** = no competitor has it, fits "nothing you didn't write"
- **Me** = Claude builds it in this repo · **You** = needs a person, an account or a signature

---

## 0. Done

- [x] Research: competitors, PIMS market, user complaints, costs, teardown, gaps (docs 01, 07, 08, 12)
- [x] Architecture, MVP spec, UX, security model, brand, roadmap, owner-accounts design, processing register (docs 02–06, 09–11)
- [x] Website: home, about, vets, research, quality, newsletter, privacy + terms drafts, sitemap, robots, social image, CI
- [x] 13 vet-reviewable articles × EN/IT/DE (39 drafts)
- [x] Digital pet passport (local-first, backup/restore/print) × EN/IT/DE; optional account sync coded and dormant
- [x] Pre-visit brief × EN/IT/DE, prefilled from the passport
- [x] Vet tool core: record schema, validators, EN/DE/IT renderer, model adapter, eval harness, 15 tests, CI
- [x] Workspace preview × EN/IT/DE on synthetic cases
- [x] Public quality page fed by the eval results

---

## 1. Launch blockers — **You** (none can be done from the repo)

- [ ] **GitHub**: confirm `oberndoerferco-commits` is yours or create an account; merge `claude/modest-dirac-s1uvdm`
- [ ] **Cloudflare Pages**: connect the repo (root `aiveterinary/site`, build `npm run build`, output `dist`); add `aiveterinary.org`
- [ ] **GoDaddy**: nameservers to Cloudflare or CNAME; check `.com/.de/.it`; 2FA on
- [ ] **Company details** for Impressum/privacy/terms: legal name, address, VAT/tax id, register, contact email (DE §5 DDG; IT D.Lgs 70/2003)
- [ ] **Newsletter provider** (free tier, **double opt-in on**, EU-hosted): paste form URL into `PUBLIC_NEWSLETTER_ACTION`
- [ ] **Supabase** free project in Frankfurt; paste URL + anon key; run `site/supabase/schema.sql`
- [ ] **Lawyer, one hour** (€): privacy, terms, Impressum, AI-disclosure wording — before real sign-ups
- [ ] **Two vets** (ideally one IT, one DE) who will put name + Ordine/Kammer number on reviewed articles and try `/it/vets/workspace`
- [ ] **Anthropic API key** when the model should run on the eval set (cents per case)
- [ ] **Ten questions** your vets hear most from owners (to prioritise articles)

## 2. Legal and trust musts — **Me**, as soon as company details exist

- [x] Impressum page skeleton in EN/IT/DE with bracketed placeholders — You: fill in company details (DE §5 DDG; IT D.Lgs 70/2003)
- [x] Rename passport wording: "digital health booklet / libretto sanitario digitale / digitaler Heimtierpass (inoffiziell)", one line "does not replace the official EU passport or registry entries" — S ★★★
- [x] AI-disclosure line on every AI output and on the pre-visit brief (AI Act Art. 50; L. 132/2025) — S ★★★
- [ ] Cookie banner only if a non-essential cookie ever appears; Garante-compliant (reject = accept prominence) — S ★★
- [x] Newsletter double opt-in: confirmation line on the form; the flow and consent log live in the provider (You: switch double opt-in on when connecting it)
- [x] Article author + reviewer block with chamber/Ordine registration number, "reviewed on / next review", numbered references — S ★★★ (trust differentiator)
- [x] Editorial policy, corrections policy, conflict-of-interest and funding page — S ★★
- [x] "Informativa uso IA" template for Italian vets; AVV/DPA template for German practices (Art. 28) — drafts in docs/legal, lawyer review before use — S ★★★
- [x] Public DPA, subprocessor list, retention policy page for the vet tool — S ★★★ (only Curala/Tandem/Petleo are clear today)
- [x] Accessibility pass to WCAG 2.2 AA (automated axe audit on 11 pages: 0 violations after the contrast fix; manual keyboard/screen-reader pass still open) — M ★★

## 3. Website and content — **Me**

### Articles (drafts; vets review)
- [x] Cost explainers, highest intent: **"Tierarzt Kosten Tabelle 2026 (GOT)"**, **"Kastration Hund Kosten 2026"**, **"Quanto costa una visita veterinaria"**, "sterilizzazione cane costo" — M ★★★
- [x] **Italian top-40** — all 40 covered as of 17 Oct 2026 (drafts, pending vet review) — L ★★★
- [x] **German top-40** — all 40 covered as of 17 Oct 2026 (drafts, pending vet review; StIKo Vet guideline cited is the 2019 edition, check for a newer one) — L ★★★
- [x] Conditions and medications categories: diabetes, CKD/thyroid, antibiotics, NSAIDs in EN/IT/DE (more condition and drug-class pages still open)
- [x] A–Z index, species hubs, "share with your vet" button, print stylesheet for articles — S ★★
- [x] Illustrations (own SVG faces, hero scene, loader; design system in docs/06 and research in docs/13) — M ★
- [x] **Source audit of every article** (19 Oct 2026): each of the 166 articles checked claim by claim against its own cited sources; contradictions fixed, unsupported claims removed, every reference URL opened; duplicate DE "Katze frisst nicht" pages merged
- [x] Cross-language consistency of triage thresholds in all 46 translation groups (19 Oct 2026): stricter, source-backed rule applied in every language
- [ ] **For the reviewing vet** (no source settles these): tick removal urgency (IT "today" vs EN/DE "routine"); home weighing interval for CKD cats (EN monthly, IT every 2 weeks, DE weekly); fever after a recent operation (DE go-now vs EN same day); DE cat diarrhoea lacks "won't drink"
- [ ] Ministero della Salute pages (browser wall) and StIKo Vet Leitlinie 6th edition (Thieme bot wall) could not be opened; cited via Gazzetta Ufficiale / FLI table instead — check by hand
- [ ] Translate privacy/terms into IT/DE after the lawyer pass (research and quality pages done in IT/DE)
- [x] Vet-facing landing pages per country: /de/vets with TÄHAV §13/§15/§16 and GOT §7, /it/vets with REV, consenso, preventivo, SINAC (sources cited)

### Site mechanics
- [x] `hreflang` links between language versions; language auto-suggest bar (once per device) — S ★★
- [x] Cookie-free analytics: Cloudflare Web Analytics beacon loads only when PUBLIC_CF_ANALYTICS_TOKEN is set (You: create the site in Cloudflare and set the token) — S ★★
- [x] Search (static index, Pagefind) — S ★★
- [x] Open-graph image (one PNG for the site; per-article images still open) — S ★

## 4. Owner side — **Me**

### Passport (local-first) — value against the #1 complaint, data lock-in
- [x] Rename + "your data stays yours: free, no lock-in, export anytime" statement on the page — S ★★★
- [x] **Import from photo of the paper passport, libretto, Impfpass** (on-device OCR, self-hosted engine and EN/IT/DE data, user ticks and edits each field; chip + vaccinations with dates and batch). PDF import still open — L ★★★ *only us in EU*
- [x] **Reminders** v1: upcoming-dates panel in the booklet + .ics calendar export with 7-day alarm (country-aware intervals and email reminders still open) — M ★★★
- [x] **Share a read-only report**: print/PDF of the booklet, emergency card and claim pack (expiring link once accounts exist)
- [x] **Emergency card**: printable credit-card size, two copies, from booklet data (Wallet pass still open) — M ★★ *only us*
- [x] **Lost-pet mode** v1: A4 poster from booklet data with photo, description, last seen, phone (QR flyer, registry checklist, Europetnet link still open) — M ★★ *registry-aware: only us*
- [x] **Registry navigator** (/registry in EN/IT/DE with sourced tables for IT, DE, AT, CH, FR; a few regional deadlines flagged as secondary-source) — S ★★ *only us*
- [x] **Travel checklist per destination** under Reg. 2026/131: residents-only passport, 5-pet cap, tapeworm FI/IE/MT/NO/UK 24–120 h, rabies titre for unlisted countries, puppy age — done: `/travel` EN/IT/DE — M ★★★
- [x] Chip-number validation (15-digit ISO, manufacturer prefix) — S ★
- [x] Weight log with chart and body-condition score — S ★★
- [x] Symptom diary (date, note) in the booklet, last entries pulled into the pre-visit brief (photo per entry still open) — M ★★
- [x] Puppy/kitten first-year schedule; senior-care checklist — S ★★
- [x] Toxic foods and plants offline reference (dog, cat, rabbit) — S ★★
- [x] Insurance claim pack printed from the booklet (identity, chip, policy, visits, medications, conditions, blanks for invoice and onset) — per-insurer formats and invoice photo still open
- [x] End-of-life module: quality-of-life scale, decision aid, after-death checklist incl. deregistration — S ★★
- [x] Multilingual print labels (EN/DE/IT; FR still open) so the booklet reads abroad — S ★★
- [x] Backup to own cloud via the browser save dialog where supported (encrypted export still open) — M ★★
- [ ] Multi-owner/family sharing; pet-sitter mode (time-boxed, meds + feeding + emergency only) — L ★★ (needs accounts)
- [ ] Owner accounts live (needs Supabase) → sync, email reminders, share links — M ★★★

### Pre-visit brief
- [x] Species-specific question sets (cat urinary, rabbit gut, senior) — S ★★
- [x] Send to clinic by email/PDF (done); accept at the vet side as *owner-reported* input with its own provenance tag still open — M ★★★ *only us: brief flows into the record as "owner says"*

## 5. Vet tool — **Me**

### Correctness first
- [ ] Grow the eval set to **300 cases × EN/DE/IT** (shorthand, typos, contradictions, multi-pet, dictated-later notes), written with vets — L ★★★
- [ ] Run the model on the set (needs key), publish numbers on `/vets/quality` — S ★★★
- [x] **Country field packs** as missing-flags: DE (TÄHAV: product, ZNR, batch, quantity, dose/route/duration, antibiotic justification), IT (owner codice fiscale, microchip, lot on vaccines, consent "modi e tempi", REV number), CH (antibiotic → IS ABV fields), AT (TAMG fields) — M ★★★ *only us*
- [x] Add structured fields: microchip, owner tax/ID, product code + batch + pack + quantity/unit, author, consent — S ★★★
- [x] Adversarial cases (4 of 6 scenario types in the eval: pregnancy, dose not given, was vs planned, decimal commas + compound names; other pet and multi-pet still open) — M ★★★
- [ ] External vet panel review of 50 outputs (names on the quality page) — **You** + M ★★★

### Documents from the approved record (each S–M unless noted)
- [x] Owner summary and referral letter rendered from the approved record (discharge and the AniCura/TiHo/LMU referral field alignment still open)
- [x] **Prescription per dispensed Rx drug (Art. 105(5))** rendered from record + visit context with flags for keeper, chip, product, quantity, vet (PDF/letterhead still open)
- [ ] **Italian REV payload** from the medication table; store number + PIN ★★★ *only us*
- [x] **Preventivo / Kostenvoranschlag** skeleton from planned items with empty price cells, GOT no./factor columns (DE) and the IT legal note (clinic price list × items still open)
- [x] **Consent form** rendered per planned procedure with the FNOVI/chamber elements as sections the vet completes; risks never pre-written (procedure-specific variants: anaesthesia, euthanasia, hospitalisation, AMA still open)
- [ ] **Insurance-ready invoice annotation** (diagnosis, chip, DOB/breed, GOT no. + factor) and **claim pack** per insurer ★★★ *only us*
- [x] Vaccination entry rendered from the record with batch/site/validity from the dispensing record, flags when absent (booklet import and reminder hand-off still open)
- [x] Surgery/anaesthesia record with required-field checklist (ASA, protocol, monitoring values, implants) ★★★
- [x] **Text-first dental chart** from typed Triadan findings; unmarked teeth shown as not recorded, never as healthy
- [x] Home-care schedule (calendar of doses) rendered from the medication table ★★
- [x] Callback / phone-call note (typed) (`app/src/letters.ts`); email-to-record still open ★★
- [x] History recap of the patient's own approved records, every line linked (`app/src/history.ts`) ★★
- [x] Euthanasia record + condolence letter from vet-entered facts (`app/src/letters.ts`) ★
- [x] Controlled-drugs register entry prepared from the dispensing record (monthly check reminder still open)
- [ ] Registry export (AT Heimtierdatenbank, IT anagrafe dataset) ★★
- [ ] Dog-bite report letter (CH, IT) ★
- [ ] Third-country certificate pre-fill from record ★
- [x] Antibiotic structured block rendered per marked antibiotic (IS ABV push via BLV REST and HI-Tier 2029 still open)
- [x] Lab-result explanation for owners from vet-entered interpretation only ★★

### Editor and review features
- [x] **Provenance badge** on every document (AI-added 0 / vet fields n / not recorded n) — S ★★★ *only us*
- [x] Owner-reported vs vet-observed toggle with distinct rendering — S ★★★ *only us*
- [x] **Declined-care register** (signed paragraph + per-patient log) — S ★★★ *only us*
- [x] Medication reconciliation ticks before sign-off; cross-document identity check across report, owner letter (both languages), referral and prescription
- [x] "Not recorded" as a first-class printed value — S ★★★ *only us*
- [x] Amendment propagation map: every document remembers its version; after an amendment the stale ones are listed (`app/src/versions.ts`)
- [x] Bilingual owner letter (EN/IT/DE) with the medication rows checked identical across every document (TR/AR/UK still open)
- [x] Snippets / dot-phrases: clinic-written, expand only on a typed trigger, before structuring so spans still hold (`expandSnippets`)
- [x] Clinic abbreviation + glossary manager — S ★★★
- [~] Template builder: clinic-required fields done (flags only, `app/src/clinic-required.ts`); sections, order, per-vet defaults and specialty sets (derm, ortho, dental, ophtho, cardio, exotics, equine) still to do — M ★★
- [ ] Multi-pet consultation UI (assign bullets, split documents, one owner letter) — M ★★
- [x] Image attachment (stored, referenced, never interpreted) — S ★★
- [x] Nurse draft → vet co-sign with stamp and audit — S ★★★
- [x] Time-to-approval counter shown on approval (clinic median on the quality page needs stored data)
- [ ] Optional vet-only dictation → bullets, audio discarded immediately, shown as the vet's own input — M ★★
- [~] Mobile layout done (two-column controls, phone bar with status and Approve, enabled only after the report end was on screen); local autosave waits for real note entry — M ★★
- [x] Handouts: matching articles suggested from the assessment, linked, never inserted

### Getting it into the practice software
- [ ] **Export formats** tested against Vetera, easyVET, VET7, Provet Cloud, dr.veto, VetsGo free-text fields — M ★★★ (per-field S/O/A/P copy and JSON export with approval details done in `app/src/export.ts`; still to test in each real PIMS)
- [ ] Browser helper (extension) that pastes sections into the right fields and **reads the patient header to lock patient facts** — L ★★★
- [ ] Provet MCP read (history, meds) as context — M ★★
- [ ] Partner-programme applications: Provet, ezyVet, Covetrus; Petleo-style agreement with Vetera/Nordhealth; VetZ — **You** + L ★★

### Platform
- [x] Vet accounts (email link + MFA), clinic settings (letterhead, language, units, SOAP on/off, abbreviations) — M ★★★ (letterhead stored on the device, printed over every document; PDF export is the browser print)
- [x] Letterhead stored on the device, printed over every document; PDF via the browser print
- [x] Retention controls (auto-delete drafts/raw notes): rule in `app/src/retention.ts`, approved records never auto-deleted — immutable approved versions with amendment reason done in `versions.ts`
- [x] Clinic-owner analytics (time-to-approved, edit ratio, open flags) — no clinical text (`app/src/analytics.ts`) — S ★★
- [x] Rate limits, spend caps, prompt caching, model fallback — S ★★★
- [ ] Cross-tenant isolation test suite; pen test (€) and DPIA before real data — M ★★★
- [ ] SSO (Google/Microsoft) and multi-clinic groups — L ★ (later, for chains)

## 6. Go-to-market — mostly **You**, prepared by **Me**

- [ ] **Free tier for students, TFA/tecnici and nurses**; list as university "convenzione" — Me S, You: bvvd (bvvd@bvvd.de), IVSA Italy chapters, vmf, ATAV
- [x] **Willingness-to-pay survey** drafted in docs/14-gtm-kit.md — You: create the form and distribute
- [x] Editorial pitches drafted (DE/IT) in docs/14-gtm-kit.md — You send
- [ ] Congresses (walk the floor, poster via a university co-author): bpt-Kongress Hannover **19–21 Nov 2026**; VetMed Fellbach **5–6 Feb 2027**; bpt-INTENSIV Bielefeld **25–28 Feb 2027**; SCIVAC Rimini **4–6 Jun 2027**; ECVIM Rimini 23–25 Sep 2027
- [ ] Grants (€0 to apply): **Piemonte voucher digitalizzazione 22 Oct–15 Dec 2026** (if a Piedmont entity), **Smart&Start Italia** (rolling), **Unleashed by Purina** (~Jul 2027, wants vet tools), Leap Venture Studio cohort 11 (~Q1 2027), EXIST via a vet faculty, EIC 4 Nov 2026 / ~3 Feb 2027
- [ ] Insurer partnerships: Agila direct billing (claim-friendly export), Figo affiliate (disclosed) — Me prepares the export, You contact
- [ ] Clinic groups for a pilot: AniCura Italia (Medical Operations Manager), Ca'Zampa/BluVet, IVC Evidensia — You
- [ ] Shelters/breeders: passport as adoption handover; Tierheim/canile pilots — You
- [x] Launch checklist drafted in docs/14-gtm-kit.md — You run it

## 6b. From the October 2026 market research (docs/15-market-research-2026-10.md)

- [x] Review sign-off integrity check in the build (`site/scripts/review.mjs`)
- [x] Structured data (MedicalWebPage, BreadcrumbList) matching the visible page
- [x] "Is it an emergency?" check, saves to the symptom diary
- [x] Chocolate dose check for dogs (MSD figures, never says safe)
- [x] "Is anything wrong?" feedback box on articles (email only, nothing stored)
- [x] Lost or stolen passport steps on the travel pages
- [x] "Can my pet eat that?" lookup (ASPCA list, never says safe)
- [x] Per-field SOAP copy and JSON export in the vet workspace
- [x] Vet evaluation protocol: metrics with Wilson CIs (`app/src/metrics.ts`), 53 cases (42 generated), 20-case stopwatch protocol on the quality pages; the model run still needs the API key
- [x] Compliance kit drafts in docs/legal: Italian client notice, German owner notice (BTK Oct 2026), § 203 StGB undertaking, AVV (§ 203 error fixed), AI-literacy session — all need a lawyer's review
- [x] Search-shaped pass, Italian first: question H2s with one-sentence answers (58 articles), sharper titles, urgency-matched next step on every article; DE and EN done too (487 more headings, 397 sentences)
- [x] Vaccine planner (WSAVA 2024 tables + EU rabies travel rule, `app/src/vaccine-plan.ts`); saves planned dates to the booklet, never as vaccinations

## 7. Open research (unverified, confirm before building)

- [ ] CH GST retention rule for records; AMICUS vet duties; AT Standesregeln and bite-report duty
- [ ] IT: final text of D.Lgs 218/2023 on registering dispensing to pet owners; Sistema TS optionality for vets
- [ ] DE: Petplan/Barmenia/Allianz claim forms; HABS status between TASSO and FINDEFIX
- [ ] Whether a third-party SaaS may connect to Provet MCP on a clinic's behalf; ezyVet/Provet/Digitail free-text write-back permissions
- [ ] L. 132/2025 health-sector decrees adopted?
- [ ] Vet-forum complaints about Vetera/easyVET/Italian PIMS (needs interviews or group access)
