# What we are missing, what we can do better, and ideas nobody has

Research date: 2026-10-13. Four deep-dives (vet paperwork per country, owner
apps and registries, feature parity against 14 scribes, go-to-market at €0),
all from public sources. Items marked *unverified* need a primary source or an
interview before we build on them. The backlog derived from this is `TODO.md`.

---

## 1. The big insight: the approved record is 90 % of every other document

Every country obliges vets to produce documents that repeat what is already in
the consultation note. Nobody in the market generates them from the record.

| Document / task | Where | Required by | Who types it today | Our opportunity |
|---|---|---|---|---|
| Prescription on **every** dispensed prescription drug for pets | DE (AT/CH similar) | §15(3) TÄHAV, Reg. 2019/6 Art. 105(5) | PIMS print, often skipped | Generate from the medication table, store PDF in the record |
| **Electronic prescription (REV)** | IT | DM 8.2.2019 | Vet on the ministry portal/app, PIN per prescription; data keyed 3× (REV, record, invoice) | Build the REV payload from the medication table; store number + PIN |
| **Antibiotic use reporting** | CH now (IS ABV, every antibiotic incl. dogs/cats; REST interface documented by BLV); DE/AT dogs & cats from data year 2029, first report Jan 2030 | TAMV / §61a TAMG / AT Mengenströme-VO | Re-keyed in a web app; yearly in DE/AT | Structured antibiotic block now; push to IS ABV / HI-Tier later |
| Controlled-drugs book (BtM-Buch, registro stupefacenti, BetmKV) | DE IT CH (AT unverified) | BtMVV §13 (monthly check, 3 y), DPR 309/90, BetmKV | Paper or separate module | Draft entry from anaesthesia/analgesia in the record; monthly check reminder |
| Vaccination with **batch/lot** | all | TÄHAV/TAMV/FNOVI | Handwritten batch | Scan label → record + passport page + reminder |
| EU pet-passport entries; issuing vet keeps a copy ≥3 y | EU | Reg. 576/2013 Art. 21/22 (successor rules 2026/131) | By hand | Print-ready passport entries + retention log |
| Microchip registration | AT (vet must enter since 1.1.2025), IT (accredited vets, same day in Lombardia) | Heimtierdatenbank, anagrafe regionale/SINAC | Separate portal | Export the registration dataset / pre-filled entry |
| **Written estimate** | IT (legal duty, L. 124/2017, itemised, incl. liability policy data); DE (written agreement when fee < 1× or > 3× GOT) | — | Manual | Plan → GOT positions / listino → estimate PDF |
| **Procedure-specific consent** (anaesthesia, euthanasia, hospitalisation, refusal, referral) | IT (FNOVI lists required content); DE/AT/CH practice | FNOVI linee di indirizzo; BGB/Berufsordnung | Generic printed form | Consent text from the plan with the FNOVI-required elements |
| Invoice that insurers accept | DE (Agila, HanseMerkur, Uelzener: diagnosis, chip, DOB/breed, GOT position + factor, no handwriting), IT (fattura with codice fiscale, itemised; Sistema TS) | insurer rules, UStG, L. 124/2017 | Reception, rejected often | Suggest GOT positions from the record, add diagnosis text, check codice fiscale |
| **Insurance claim pack** | DE IT | insurer rules (Agila 1 month, Poste 3 working days) | Owner/reception | One-click claim letter + record extract per insurer template |
| Referral letter | all | clinic forms (AniCura, TiHo, LMU: history, findings, meds with substance/dose/duration, diagnostics, question, urgency, attachments) | Free text | Align our referral letter to those field sets |
| Dog-bite report | CH (mandatory), IT (mandatory, 10-day observation) | cantonal forms / ASL | Rare, forms vary | Report letter from the note |
| Third-country health certificate | all | destination rules + Veterinäramt | Form hunting | Fill PDF templates from the record |
| Stock / batch ledger, yearly inventory | DE AT CH IT | TÄHAV §15/16, TAMG, TAMV 26–29, D.Lgs 193/2006 | Assistant | Consumption from the record → stock ledger |

**Fields to add to the record now** so these become possible: microchip number,
owner tax/ID number, product code (ZNR / AIC / UPD-PI) + batch + pack size +
quantity with unit, dose/route/duration (have), diagnosis text (have), author,
consent wording and time (IT Art. 32 "modi e tempi dell'informazione").

**Record-keeping duties as our missing-info checklist:** DE 5 years (chamber),
drug records 5 years, immutable electronic records (§16 TÄHAV); AT 5 years
(TAMG), pharmacy 7 years; IT 5 years, prudently 10 (FNOVI), cartella minimum:
owner name + codice fiscale, address, phone; patient name, species, breed, sex,
age, microchip; every visit dated; vaccinations with lot; adverse reactions;
separate surgery/anaesthesia sheets; CH 3 years for drug flow (TAMV), antibiotic
prescriptions in IS ABV.

Sources: TÄHAV (buzer.de/gesetze-im-internet), Reg. 2019/6, BTK DTBl 03/2026
on AB-Meldungen, BLV Fachinformation TAMV 2026, usp.gv.at Aufzeichnungspflicht,
FNOVI Codice Deontologico 2017 + Linee di indirizzo, agendadigitale on REV,
Agila/HanseMerkur/Uelzener claim leaflets, AniCura/TiHo/LMU referral forms.

---

## 2. Feature parity vs 14 scribes: where we stand

**Only we have (or will):** source link on every sentence, missing-info flags
that block approval, per-section diffs, immutable version history, regenerate
without losing edits, vet co-sign role, per-consultation audit log, named EU
region + subprocessors, no training on any tier, typed input as the primary
design.

**Everyone has and we lack:** phone-call capture (all US vendors), callback
note, record summary / history recap, dental charts (VetRec, ScribbleVet,
CoVet, HappyDoc, PawfectNotes), mobile apps, email/SMS sending, 30+ specialty
templates, custom template builder, PDF/prior-record upload, PIMS
extensions.

**Nobody has, and it fits our principles (build these):**
1. **Provenance badge** on every document: "0 values added by AI · 14 fields from the vet · 2 marked not recorded", machine-verified and printed.
2. **Owner-reported vs vet-observed** toggle in the editor with distinct rendering.
3. **Declined-care register**: every declined item collected into a signed "advised and declined" paragraph and a per-patient log (liability value in DE/IT).
4. **Pre-sign medication reconciliation** rendered by code: tick per cell, plus a cross-document check that the owner translation carries the identical table.
5. **"Not recorded" as a first-class value** that prints instead of silence.
6. **Keyboard-only review with a visible time budget**; publish the clinic's median time-to-approved.
7. **Country-aware mandatory field packs** (DE: antibiotic documentation, GOT; IT: REV reference, consent elements) as flags, never as generated content.
8. **Patient-fact lock from the digital passport / scanned EU passport**: header from the passport, prose cannot override it.
9. **Bilingual side-by-side owner letter** (DE/IT/EN, plus TR/AR/UK for owners) with the medication table re-rendered identically.
10. **Amendment propagation map**: after an amendment, every derived document shows "generated from v1 — regenerate?".
11. **Text-first dental chart** drawn by code from typed tooth findings (`108 FX3, 309 M`). All competitors do dental charts from audio; none from typed shorthand.
12. **Insurance claim letter** from the approved record. No vendor has it.

Deliberately not on the list: ambient capture of the owner conversation,
"learn my style" that fills in normals, AI treatment plans, dose suggestions
(VetGeni, Vetnio do this), care-gap upsell (HappyDoc), AI diagnosis/triage.

---

## 3. Owner side: what owners want and nobody does well

**Top complaints in owner-app reviews:** data lock-in (11pets charging to see
years of entries, per-pet fees, broken export; PetCoach delisted 2025 and data
gone), manual entry (clinic-fed apps PetDesk/Digitail score highest because
the clinic fills the record), subscription surprises and cancellation friction
(Tractive, Pawtrack, Dogo), photo-upload and password-manager bugs.

**Evidence of demand:** reminders for appointments and vaccinations 87 %
(PetDesk 2025 survey, vendor-sponsored), 97 % want alerts and 92 % would use an
app with a vet-compiled knowledge base, only 4 % use one today (Hungary 2025,
n=607). 71 % trust vets most; owners prefer vet-pointed online resources.

**Feature ideas ranked (value / effort / exists elsewhere):**
1. Vaccination, parasite and medication **reminders with country-aware intervals** (rabies validity per vaccine, tapeworm 24–120 h window). High / low / exists but not travel-aware.
2. **Share a read-only report** (link or PDF) for vet, sitter, kennel. High / low / partial.
3. **Import from a photo or PDF of the paper passport / libretto / Impfpass** (OCR → structured). Very high / medium-high / rare.
4. **Emergency card**, printable + Apple/Google Wallet pass. High / low / no wallet pass found anywhere.
5. **Lost-pet mode**: poster PDF, QR flyer, per-country registry checklist, Europetnet link. High / low / exists but not registry-aware.
6. **Registry navigator**: which registry am I in, move-country checklist (AT 1 month, CH 10 days, FR 8 days, IT 10 days). High / low / nobody.
7. Family sharing; pet-sitter mode (time-boxed, feeding + meds + emergency only).
8. Weight and body-condition tracking with alerts; symptom diary with photos feeding the pre-visit brief.
9. **Travel checklist per destination** under Reg. 2026/131 (EU residents only, 5-pet cap, tapeworm FI/IE/MT/NO/UK, rabies titre for unlisted countries). High / medium / partial.
10. Insurance claim helper (invoice + records + onset date into the insurer's format).
11. Puppy/kitten schedule; senior care plan; breed-risk screen linked to our articles.
12. Toxic foods and plants offline reference (explicit request in Red Cross app reviews); first-aid triage offline.
13. Chip-number check (15-digit ISO, manufacturer prefix) + Europetnet lookup link.
14. End-of-life module: quality-of-life scale, decision aids, after-death checklist incl. registry deregistration.
15. Backup to the owner's own cloud (iCloud/Drive/Nextcloud), encrypted export, "we never see it".
16. Multilingual record labels so the passport prints readable abroad.

**Registries:** IT regional anagrafi → SINAC (D.Lgs 134/2022), cats mandatory
in some regions from 2026 (FVG from 1 Jul 2026); DE no state registry, TASSO +
FINDEFIX voluntary ("gechipt ist nicht registriert"); AT Heimtierdatenbank
(vet enters since 2025); CH AMICUS (dogs) / ANIS (cats); FR I-CAD; UK multiple,
only Petlog on Europetnet. Europetnet is a router with no public API.

**EU passport:** Reg. 2026/131 applies from 22 Apr 2026; older passports
grandfathered partly to 2028 (2026/705); the Commission announced a two-year
assessment of a digital passport via the EU Digital Identity Wallet (Reg.
2026/1818). No official pilot exists. Our window: 2–3 years. Naming rule:
call ours "digital health booklet / libretto sanitario digitale / digitaler
Heimtierpass (inoffiziell)" and say it does not replace the official passport.

**Trust practices to copy (none of the big charity sites do all):** named vet
author *and* reviewer with chamber/Ordine registration number; "reviewed on /
next review" dates; numbered references to guidelines (WSAVA, ESCCAP); "when to
see a vet" box at the top; country scoping; non-commercial statement, no product
links in clinical text; public editorial, corrections and conflict-of-interest
policy; A–Z index; "share this with your vet".

---

## 4. Go-to-market at €0

**Search demand (Google autocomplete, 13 Oct 2026).** Italians type
"[animale] [sintomo] [qualificatore]" and "perché il mio cane…"; Germans type
"[Tier] [Symptom] was tun". Head terms: *cane vomita giallo*, *gatto vomita
schiuma bianca*, *gatto non mangia ma beve*, *cane diarrea con sangue*, *gatto
non fa pipì da 12 ore*, *cane trema senza motivo*, *cane zoppica*, *cane ha
mangiato cioccolato*, *leishmaniosi cane*, *processionaria cane*; *hund
durchfall was tun*, *hund erbricht gelb*, *katze erbricht schaum*, *katze frisst
nicht mehr*, *warum frisst mein hund gras*, *tierarzt kosten tabelle 2026*,
*kastration hund kosten 2026*, *hund giardien*, *katze blasenentzündung*,
*hitzschlag hund*. Cost pages (GOT 2026, tariffe veterinarie) are the highest-
intent non-symptom cluster in both languages. Italy-only topics (leishmaniosi,
processionaria, vaccini obbligatori, SINAC) are low-competition. The full 40+40
list is in `TODO.md`.

**Where vets gather:** bpt (7,046 members), BTK + 17 chambers, ÖTK, GST, ANMVI,
FNOVI, SCIVAC. Congresses: bpt-Kongress Hannover 19–21 Nov 2026; VetMed
Fellbach 5–6 Feb 2027; bpt-INTENSIV Bielefeld 25–28 Feb 2027; SCIVAC Rimini
4–6 Jun 2027; ECVIM Rimini 23–25 Sep 2027; Leipzig next 20–22 Jan 2028. No
start-up slots; free routes = poster via a university co-author, student
career corner, walk the floor. Media: Vetline "Praxismanagement", Vetjournal
"Praxismanager", vetjournal.it ufficio stampa, Ordini newsletters. Podcasts:
FutureVetBusiness (DE), Che Razza di Podcast (IT). Students: bvvd
(bvvd@bvvd.de), IVSA Italy chapters, university "convenzioni" lists. Nurses:
vmf (DE), ATAV (IT, >5,000). Insurers with vet-facing programmes: Agila (direct
billing), Figo (affiliate).

**Grants:** Smart&Start Italia (0 % loan up to 80 % of €100k–1.5M, rolling);
startup innovativa status; Piemonte voucher digitalizzazione (22 Oct–15 Dec
2026); EXIST (DE, via a vet faculty, €1–3k/month/person + €30k); aws Preseed
(AT); Unleashed by Purina (CHF 50k, next window ~Jul 2027, explicitly wants
vet professional tools); Leap Venture Studio ($200k, cohort 11 ~Q1 2027); EIC
Accelerator (4 Nov 2026 / ~3 Feb 2027). EIT Health is human-only.

**Pricing corridor:** €20–80 per vet per month; free tier is table stakes
(Scribenote free since Jul 2025). No DE/IT willingness-to-pay survey exists:
we should run one. Groups: AniCura Italia (~37 clinics, Medical Operations
Manager role), Ca'Zampa/BluVet (~45 sites), IVC Evidensia (central tech
decisions, research fund).

**Legal musts before launch (DE/IT/EU):**
- DE Impressum under **§5 DDG** (not TMG), Datenschutzerklärung, cookie consent only if non-essential cookies.
- IT: D.Lgs 70/2003 site information, Garante cookie rules (reject as prominent as accept, no cookie wall), **double opt-in** for the newsletter (Garante 330/2025, €45k fine without it).
- Health info: German HWG applies to animals (no healing promises, no drug advertising); Italian FNOVI advertising guidelines (reviewing vets' name, Ordine and number on each article; no hidden advertising).
- Italian AI law L. 132/2025: professionals must inform clients about AI use → ship an "informativa uso IA" template for Italian vets.
- EU AI Act Art. 50 (since 2 Aug 2026): anything interacting with owners must disclose it is AI; machine-readable marking of AI text by 2 Dec 2026.
- Vet tool = data processing on behalf of the clinic: Art. 28 agreement with every practice (template at sign-up).
- Not a medical device: MDR covers human use; veterinary documentation software is unregulated as a device. Keep it "documentation, not diagnosis".
- Don't call ours "the EU pet passport".
