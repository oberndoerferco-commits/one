# Competitor teardown: their promises, their systems, and how we beat them

Research date: 2026-09-29.
- **Scope:** 30+ products in four groups: US standalone scribes, other standalone scribes, European scribes, and AI built into practice systems (PIMS). Plus what vets actually say, and the published evidence from human medicine.
- **Sources:** public sources only, with a link for every claim.
- **Gaps:** Reddit and some trade-press pages couldn't be reached, and most user quotes come from app stores, Trustpilot and VIN News.
- **Before quoting publicly,** re-check any quote or price on the live page.

This builds on `01-competitive-analysis.md`, which it updates in §9.

---

## 1. Summary

**What the market promises:** "hours back every day", "99.8% accurate", "notes done before the next appointment".

**What users actually report:**
- invented drug names and vaccines;
- a male dog recorded as pregnant because the owner was;
- one patient's details in another patient's record;
- owners' words recorded as the vet's findings;
- failed uploads that lose the whole consultation;
- "1.5–2 hours after every shift combing through SOAPs".

**What independent evidence shows:**
- **Time saved is modest.** About 16 minutes per 8 hours of patient care in the largest human-medicine study ([JAMA 2026](https://jamanetwork.com/journals/jama/fullarticle/2847319)).
- **Omissions are the most common error; invented content is the most dangerous.**
- **Vendors disclose almost nothing.** Veterinary generative/ambient AI products scored a mean **1.8%** on a 2026 transparency audit ([Front Vet Sci](https://doi.org/10.3389/fvets.2026.1761038)).

**Where no competitor publicly competes:**
1. Typed shorthand as the primary input.
2. A guarantee that no drug or number appears unless the vet typed it.
3. A visible source for every sentence.
4. Missing-information flags before sign-off.
5. One approved record that every document is generated from.
6. Native German and Italian output.
7. A published quality measure for the notes themselves.

That is where AI Veterinary should compete. It should not compete on transcription.

---

## 2. What competitors promise, and how much evidence stands behind it

| Promise | Who | Evidence behind it |
|---|---|---|
| "99.8% accuracy" | HappyDoc ([site](https://happydoc.ai/)) | **Defined as an edit rate**: notes edited in ~1 of 500 visits ([blog](https://happydoc.ai/blog/what-is-accuracy-for-ai-scribes-and-why-does-it-matter)). This measures how often vets edit, not whether the note is correct. |
| "81% error reduction on medications" | ScribbleVet ([Instinct](https://instinct.vet/products/scribblevet/)) | No method. The baseline is generic speech-to-text, not other scribes. |
| "95% accuracy", "better than a human" | ReportAssistant ([VetZ](https://www.vetz.de/ki-dokumentation-herausforderungen-vor-dem-einsatz-im-praxisalltag/)) | No method. |
| "98% accuracy on vocabulary", "100% completeness" | Vetomatic ([blog](https://vetomatic.com/blog/automatiser-comptes-rendus-veterinaires)) | No method. |
| "2+ hours saved per day" | VetRec, HappyDoc, CoVet, Vetnio | Vendor surveys only. |
| "20 min per visit", "70–90% less after-hours time" | VetGeni ([proof](https://www.vetgeni.com/proof)) | "Qualitative feedback" pilots, no sample size. |
| "Six extra hours a week" | Covetrus ([AI page](https://covetrus.com/covetrus-platform/covetrus-ai/)) | "Internal usage data". |
| "Records done in under a minute" | Otto, ScribbleVet (~1 min) | ScribbleVet's own help centre says "a couple minutes", up to 5 ([help](https://intercom.help/scribblevet-help-center/en/articles/14811698-how-to-start-scribbling)). |
| "Release gates", VetBench validation | VetGeni ([validation](https://www.vetgeni.com/validation)) | Real structure, but **19 test cases**, and it tests the Q&A assistant, **not the notes**. It states that no independent evaluation has been done. |
| CE Class IIa, ISO 13485/27001, 375,000-note evaluation | Tandem Health ([ai-info](https://tandemhealth.ai/ai-info)) | **The strongest evidence in the market.** But it is human-medicine data, not veterinary. |
| "Nothing stored without your approval" | Provet, Tandem, Petleo, Vetigen | A process claim. None publishes an audit trail. |
| "No invented diagnoses, medications or dosages" | VetScribe (NL) ([site](https://vetscribe.nl/)) | Marketing text, no mechanism described. **Philosophically the closest to us.** |

**Lesson:** accuracy claims are the category's weakest point. A published, defined, repeatable quality measure would be new.

---

## 3. How their systems actually work

Almost every product follows the same pattern:

```
consent → record (phone/laptop/watch) → upload → wait 30 s–5 min
→ AI note from transcript → vet reads the whole note → edit / regenerate
→ copy-paste, browser extension, or (few) API write-back into the PIMS
→ optional: client email / discharge / referral generated from the note or transcript
```

| | Typical today | Notable exceptions |
|---|---|---|
| Input | Ambient audio; dictation | Typed input only as a side door: VetGeni "paste your SOAP", Squako, CoVet "free type" additions, VetRec after-the-fact dictation |
| Consent | Required on every recording (ScribbleVet, VetRec, ezyVet) | Provet leaves it to local law |
| Review | Read the whole note; free-text edits | Scribenote keeps revisions with diffs ([docs](https://docs.scribenote.com/en/articles/8931645-note-history)); ezyVet has "Mark as complete" |
| Error handling | Edit, or regenerate the whole note | Scribenote: reprocessing **overwrites manual edits** ([docs](https://docs.scribenote.com/en/articles/10305591-editing-a-note)) |
| Missing info | The vet listens back to the audio (Scribenote's official advice, [docs](https://docs.scribenote.com/en/articles/9307016-my-note-is-missing-information)) | None found that flags it automatically |
| Medication | Transcribed; sometimes misheard | Digitail "SOAP Verification" checks dose, allergy and contraindication (top plan) ([help](https://help.digitail.io/en/articles/10027948-tails-ai-assistant-soap-verification)). ScribbleVet shows Plumb's drug information but explicitly **no** dose or interaction check ([help](https://intercom.help/scribblevet-help-center/en/articles/14794820-plumb-s-in-scribblevet)). VetGeni **adds** reference doses. |
| Source links | Transcript or audio playback at best | Instinct Document Summary links each finding to a PDF page ([blog](https://instinct.vet/blog/instinct-emr-ai-features/)) |
| Owner documents | Generated from transcript or note | Heidi case study: a vet pastes the AI transcription into client emails ([case](https://www.heidihealth.com/en-us/customers/veterinarian-charles-kuntz)) |
| Languages | English note output is common | Scribenote and ScribbleVet: notes in **English only**; VetRec: German in beta, no Italian; CoVet: 11 languages, translations not reviewed |
| PIMS | Chrome extensions, copy-paste | API write-back: HappyDoc (AVImark, Cornerstone), VetRec (several US), CoVet (ezyVet, now IDEXX-owned). **No US scribe lists an EU PIMS.** |
| Audio retention | 0 h to 90 days | Scribenote keeps transcripts indefinitely; Vetomatic keeps audio 7 days; ScribbleVet deletes audio after 90 days |

---

## 4. What vets actually experience (ranked pains)

Sources: VIN News, app stores, Trustpilot, BVA/AAVSB/RCVS, and peer-reviewed human-medicine studies.

| # | Pain | Evidence |
|---|---|---|
| 1 | **Invented or wrong drugs, doses, vaccines** | "listing drug names … I've never heard of or used and listing vaccines administered that are inappropriate" (ScribbleVet [App Store](https://apps.apple.com/us/app/scribblevet-the-ai-scribe/id6461720107?see-all=reviews)); "the AI would invent new drug names" ([VIN](https://news.vin.com/doc/?id=12903793)) |
| 2 | **Signing without reading** (automation bias) | "If nine out of 10 records are correct, you are going to get lazy about reading them" ([VIN](https://news.vin.com/doc/?id=12903793)); 82% of UK vets worry about AI "used without follow-up checks" ([BVA](https://www.vettimes.com/news/vets/wellbeing-at-work/fifth-of-vets-already-using-ai-daily-bva-survey)); PawfectNotes homepage testimonial: "I don't even review the notes for many appointments anymore" |
| 3 | **AI diagnoses mistaken for the vet's** | AAVSB: "Providing a diagnosis is a veterinary-restricted task by law … that was just a diagnosis that the AI made" ([VIN](https://news.vin.com/doc/?id=12903793)) |
| 4 | **Omissions** | "It likes to leave the assessment field blank" (Talkatoo, [Software Advice](https://www.softwareadvice.com/speech-recognition/talkatoo-profile/)); omissions are the most common error in human studies ([npj Digit Med](https://www.nature.com/articles/s41746-025-01670-7)) |
| 5 | **Owner's words recorded as the vet's findings** | "the subjective entry will confuse my observations with the clients" (Talkatoo, [GetApp](https://www.getapp.com/emerging-technology-software/a/talkatoo/)) |
| 6 | **Wrong patient or cross-patient facts** | pregnant male dog; "inserted information from one patient into a different patient's record" ([VIN](https://news.vin.com/doc/?id=12903793)) |
| 7 | **Editing takes longer than writing** | "1.5–2 hours after every shift meticulously combing through SOAPs … it cost me time" (CoVet, [Trustpilot](https://www.trustpilot.com/review/co.vet)) |
| 8 | **Wordiness, "AI voice"** | "Excessive usage of irrelevant remarks"; "I hope this message finds you well" |
| 9 | **AI edits wipe sections** | "AI assistant would wipe out entire sections of template" (ScribbleVet); reprocessing overrides edits (Scribenote) |
| 10 | **Lost work** | "About 50% of my cases fail to upload … now you have no recollection" (CoVet, [Google Play](https://play.google.com/store/apps/details?id=co.vet&hl=en_US)) |
| 11 | **Recording consent and recordings as legal exposure** | "can be used to substantiate a complaint" (VIN general counsel) |
| 12 | **Data ownership and training use** | Scribenote's free tier can't opt out of data sharing ([docs](https://docs.scribenote.com/en/articles/11499058-what-is-the-difference-between-scribenote-free-and-scribenote-pro)) |
| 13 | **Noise, barking, accents, multi-pet** | "When a dog is barking … it cuts out the entire conversation" ([VIN](https://news.vin.com/doc/?id=12903793)) |
| 14 | **Getting notes into the PIMS** | integration is the most-praised feature where it exists |
| 15 | **Billing and cancellation friction** | "Can't seem to cancel this"; Petleo 3-month notice; DicmaVet annual lock-in |

**What they love, and what we must match:**
- going home on time ("I got my life back!");
- good owner letters;
- being able to remember what the owner said or declined;
- ER vets writing records afterwards from a description.

**The evidence base from human medicine:**

| Study | Finding |
|---|---|
| JAMA 2026, n = 8,581 | −16 min of documentation per 8 h, no effect on after-hours time |
| NEJM AI randomised trial | 2–10% time savings; 15% of assigned physicians never used it |
| JMIR 2026, 356 notes | omissions 18%, invented content 11.5%, **5.3% of notes had serious-risk errors**, 14.9% of notes signed unedited, edit rates ranged 1.9–69.3% between physicians |
| npj Digit Med | invented content 1.47% / omission 3.45% per sentence, cut below human rates **by refining prompts and workflows** |

**Lesson:** promise "done before you leave", not "hours saved". Design the review so it's hard to skip.

---

## 5. Competitor by competitor

### US standalone scribes

| Product | Promise | Reality | Weak spot | How we beat it |
|---|---|---|---|---|
| **ScribbleVet** (Instinct, since Jan 2026) | "Type less. Heal more."; 81% fewer medication errors; ~1 min | Audio in, English notes out; translation only into ES/FR; extension breaks on ezyVet's new interface; $40 for 150 notes or $150–200/vet | Invented drug/vaccine complaints; Plumb's panel shows drug info but doesn't check it | "Every drug and number on this page was typed by you", with a visible check; native DE/IT |
| **VetRec** | "#1 AI scribe"; 2+ h/day; 20,000 users | Strongest product in the US: 30+ templates, referral letters, 12 PIMS, GDPR claim, $99–150/vet | German in beta, no Italian; no EU hosting region named; owner documents from transcript + notes; regeneration reruns the whole note | EU-hosted with the region named; Italian and German fully supported; owner documents only from the approved record |
| **HappyDoc** | "99.8% accuracy"; 2+ h/day; 18× return on investment | 2-way AVImark/Cornerstone; from $119 per clinic; openly US-focused | "Accuracy" = edit rate; upsell-driven ("care gaps") | Publish a real quality measure; source view |
| **Scribenote** (a16z) | "1–2 h day one, 50+ h month one" | Best version history (revisions + diffs); **English-only output**; US data; free tier trains on data; reprocessing overwrites edits | Missing info = "listen to the audio" | Native DE/IT output; never lose an edit; automatic missing-info list; no training on any tier |
| **Otto** | "$0.80/day"; write-back | Only writes back into the PIMS through Otto's own platform; US only | Not relevant in the EU | — |

### Other standalone scribes

| Product | Promise | Reality | Weak spot | How we beat it |
|---|---|---|---|---|
| **CoVet** (**acquired by IDEXX 16 Sep 2026**, [IDEXX](https://ir.idexx.com/news-events/press-releases/detail/417/idexx-laboratories-acquires-covetai-to-advance-veterinary-workflow-intelligence)) | 2+ h/day; 11 languages incl. DE/IT; ISO 27001 | Strong certifications; data processed in several regions incl. US; Trustpilot 4.6 | "Got dumber"; upload failures; translation with no review; now owned by IDEXX | Vendor-neutral and EU-only; translations the vet checks side by side |
| **VetGeni** | Wiley drug database; "release gates" | US-hosted, no company SOC 2; English only; 19-case benchmark on its Q&A assistant, not its notes | **Adds reference doses into notes**, the opposite of our rule | Publish a proper validation of the notes (hundreds of cases, DE/IT/EN); "the AI never adds a dose" |
| **PawfectNotes** | 41 languages, 19 PIMS incl. easyVET/Vetera, from $29 | Most direct price/language rival in DE; "Set Your Own Normal" can fill in normal findings | Homepage testimonial praises *not reviewing*; thin trust documentation | Only record normal findings the vet wrote; published processor list; EU region |
| **Talkatoo** | "#1 on Capterra" (4.7/221) | Dictation heritage; copy-paste only; weak on drug names | No EU or language offering | Text-first for vets who "type anyway" |
| **Tandem Health** (Stockholm) | CE Class IIa, ISO 13485/27001, 375k-note study | **Strongest trust stack in Europe**; €125/user; vet partners VetFamily (10,000 clinics); easyVET integration "not live" | A human-medicine product adapted to vets; audio only | Built for vets (species, owner/patient split, dose/kg), about ⅓ of its price, easyVET/Vetera export before them; consider medical-device regulation early |
| **Heidi** | ~1 h/day, "83% less burnout" | €50–80; EU data; generalist; learns abbreviations | No vet PIMS; transcripts pasted into client emails | Owner documents only from the approved record |
| **ScribVet** | "Seconds, not hours", 50+ languages | Low transparency (no privacy policy found) | Trust | Trust documentation alone beats it |

### European scribes

| Product | Promise | Reality | Weak spot | How we beat it |
|---|---|---|---|---|
| **Vetnio** (YC, Stockholm) | "Europe's leading copilot"; 2 h/day | Evidensia partner; EU data; Provet/Animana extension; behind VET4.0/SnapVET | Pricing not published; no Italian customer support; copies each vet's writing style and suggests doses | The "anti-copilot": nothing the vet didn't write |
| **Petleo.ai** (Munich; Nordhealth owns 19.26%) | "Sie sprechen, die KI dokumentiert" | Vetera, VET7, TPV, Provet, VetStar plus a "Bubble" overlay for other systems; from €79 | **3-month notice**; legal basis is owner consent; transcript kept; no translation | No audio means no consent needed; cancel monthly; translations |
| **ReportAssistant** (easyVET/vetOS) | "Betriebssystem für KI" (operating system for AI), 95% accuracy, 300+ practices | Strongest in Germany inside easyVET; hosted in Germany; many document types | Pricing not published; accuracy unaudited; no typed input; no owner translations | Don't fight inside easyVET; win Vetera/VET7/TPV clinics and cross-border practices |
| **Curala** (Innsbruck) | 60+ languages, EU, no audio kept | €0–85 with transparent per-consult pricing; export only | Generalist; translates *into* German only | Vet depth; owner documents out of German into IT/TR/EN… |
| **VET7.AI** | "In Sekunden zum Arztbrief" (a letter in seconds) | Native to VET7.well; letters in DE/EN; orders and invoices | Only useful to VET7 customers | Multilingual owner output |
| **Squako / Vetomatic / ReqVet / DicmaVet** (FR/BE) | 1 h/day, 50%, 98%… | SOAP or compte rendu (report), French, EU/HDS hosting (French health-data certification), audio kept 24 h to 7 days | Single language; paid integration add-ons; annual lock-in | Later market: match €49, include referral letters and translations |
| **VetScribe** (NL) | "No invented medications or dosages" | Dutch; 22 templates; Frankfurt servers; €49–89 | Only one market | Watch as a benchmark: same philosophy, published mechanism wins |
| **Italy** | — | **No dedicated Italian veterinary scribe found.** LAIKA (Turin) includes a scribe inside a diagnosis tool, sold via Vets On Line / dr.veto | — | First native Italian documentation assistant; partner with Vets On Line/LAIKA rather than compete |

### AI built into PIMS

| System | Promise | Reality | Weak spot | How we beat it |
|---|---|---|---|---|
| **Provet (Nordhealth)**: main EU threat | "AI agents do the work" | Scribe £30/$40 per seat; summaries and discharge included on every plan without limits; AI Actions put items on chart + invoice; read-only **MCP** (Sept 2026); ships monthly | Only works inside Provet; model not disclosed; discharge may be single-outpatient only; CEO calls standalone scribes "point solutions [that] could go away" | Don't fight inside Provet. **Partner:** read context via MCP/API, add multi-document governance, translation and referral letters |
| **Covetrus Pulse** | "Six extra hours/week", free | Most complete visit bundle; North America only; Scripts drives pharmacy sales | Opaque about models and safety | Not our market |
| **ezyVet (IDEXX)** | "Meaningful time savings" | Still a **US pilot**; incompatible with templates; documents CoVet write-back | Slow; IDEXX now owns CoVet | Partner route through IDEXX (proven for scribes) |
| **Digitail** | Tails AI; VIP standalone | SOAP Verification (dose/allergy); discloses its model providers; VIP syncs to Digitail only | Best AI only on the top plan | Medication integrity on every plan and in every document |
| **Instinct, Vetspire, Shepherd** | various | US; English; iOS-centric | — | Not our market |
| **QVET ESCRIBA** (Spain) | Free scribe in the leading Spanish PIMS | Free and built in | — | Avoid Spain early |

---

## 6. What AI Veterinary will do better: 12 commitments

Each commitment answers a documented pain or gap. Together they are the product's positioning.

| # | Commitment | Answers | How it works (spec reference) |
|---|---|---|---|
| 1 | **Nothing on the page you didn't write.** No drug, dose, route, frequency, duration, number, test result or diagnosis appears unless it's in the vet's input or approved record. | Pains 1, 3, 6; VetGeni/Vetnio add doses | Structured extraction with a source for every field + code validators; medication tables rendered by code (architecture §4) |
| 2 | **Every sentence shows its source.** Click a sentence to see the bullet it came from; anything without a source is highlighted. | Pain 2; no competitor links note sentences | `source_spans` on every field; UX §4 |
| 3 | **Missing information is flagged before sign-off**, never silently left blank or invented. Checklists per visit type (vaccination: batch/lot, site; surgery: anaesthetic protocol; dose given → weight present). | Pain 4; Scribenote's "listen to the audio" | `missing[]` + visit-type rules; approval blocked until resolved or marked "not recorded" |
| 4 | **Who said it and whether it happened.** Every fact tagged *owner-reported / vet-observed / planned / performed / declined*. | Pain 5; the KP "planned → performed" error | New `source_role` and `status` fields (MVP §6) |
| 5 | **Patient facts are locked.** Species, sex, neuter status and reproductive status come from the patient header, never from the prose. Multi-pet visits: the vet assigns each bullet to a patient. | Pain 6 (pregnant male dog) | Patient master data; unassigned bullets flagged |
| 6 | **AI suggestions never enter the record.** The assessment and diagnosis fields hold only what the vet entered. | Pain 3; AAVSB; RCVS "must not be wholly delegated"; Italian AI law "human critical thinking must prevail" | MVP safety rule 6; provenance tag *scribed* vs *generated* |
| 7 | **A review that's hard to skip, but fast.** A summary "what the AI added vs what you typed" before approval; risky items (meds, numbers, diagnoses) need their own confirmation; routine prose is one keystroke. | Pain 2; 14.9% of notes signed unedited in the JMIR study | Approval screen (UX §3–4) |
| 8 | **One approved record → every document.** Report, SOAP, discharge, owner instructions, referral letter and translations are generated only from the signed record. Amendments flag the documents that came from it. | VetRec/Heidi generate from transcripts; no competitor documents this chain | Architecture §3.2 |
| 9 | **Edits are never lost.** Regenerating is per section, shows a diff, and never overwrites the vet's text. Full version history. | Pain 9; Scribenote overwrite | Immutable versions |
| 10 | **Text-first, no audio.** Nothing to record, so no consent step, no barking or accent problems, near-instant processing, tiny uploads that don't fail. Built for shorthand, abbreviations and after-the-fact entry. | Pains 10, 11, 13; ER vets writing afterwards | MVP §4 |
| 11 | **Genuinely European.** EU-only hosting with named region and subprocessors, no training on any tier, monthly cancellation, native DE/IT/EN output, owner documents in the owner's language with medication copied exactly, export for Vetera/easyVET/VET7/Provet/Italian systems. | Pains 12, 15; English-only output (Scribenote, ScribbleVet); German in beta (VetRec); no Italian tool | Security model; pricing |
| 12 | **A published quality page.** Named releases with fixed minimum scores that can only rise (VetGeni's format), but tested on *our documents*: ≥ 300 cases in DE/IT/EN; unsourced-sentence rate, medication/number mismatch (target 0), omission recall, translation fidelity; an outside vet panel; the gaps stated honestly. | Transparency score of 1.8%; "99.8%" = edit rate | Eval suite (architecture §4.5) |

### Also do

- **Terse clinical style by default.** Learn the clinic's house style from approved notes, ban filler phrases, and keep a separate, warm register for owners (pain 8).
- **Local autosave with visible sync status.** Typed input is never lost (pain 10).
- **Transparent euro pricing,** self-serve cancellation, free seats for nurses and reception (pain 15).
- **In-app proof of value:** time from notes to approval, and the vet's own edit ratio.

---

## 7. Where we will be weaker (and what to do)

| Weakness | Mitigation |
|---|---|
| Vets must type; no ambient capture | Target vets who already type shorthand, ER/after-the-fact records, shared rooms, owners who object to recording. **Measure first** (MVP §9 step 0). Later: optional vet-only dictation that becomes bullets, with no stored audio. |
| No integration into bundled-AI systems (Provet, Pulse) | Partner: Provet MCP/API for reading context, ezyVet partner programme. Position as a governance layer *alongside* built-in scribes; accept their output as another input. |
| No phone, receptionist or drug-reference products | Out of scope; stay focused on documentation. |
| Small scale, no social proof | Pilot results published on the quality page; vet advisory board; Italian first-mover story. |
| Tandem's medical-device certification | Get a regulatory opinion early: documentation-only intended use, no diagnosis, keeps us outside medical-device scope (to confirm with counsel). |

---

## 8. Claims we can make, and claims we must not make

**We can make these (once the evaluation proves them):**
- "Nothing in your record that you didn't write."
- "Every sentence shows where it came from."
- "No recording, no audio, no consent form."
- "Your data stays in the EU and never trains AI."
- "Native German and Italian."

**We must not make these:**
- Accuracy percentages without a published method.
- "Saves 2 hours a day" before we measure it. Use our pilot's median time-to-approval instead.
- Any compliance or certification claim before the assessment is done.
- "Replaces your scribe or PIMS".

---

## 9. Corrections to `01-competitive-analysis.md`

- **CoVet** was acquired by **IDEXX** on 16 Sep 2026 ([IDEXX IR](https://ir.idexx.com/news-events/press-releases/detail/417/idexx-laboratories-acquires-covetai-to-advance-veterinary-workflow-intelligence)).
- **Provet pricing is now public** ([provet.com/pricing](https://www.provet.com/pricing)):
  - Core: $99/vet + $249 platform fee
  - Pro: $129/vet + $299 platform fee
  - AI Scribe ("Clinical Agent"): $40 / £30 per seat
  - Summaries and discharge: included
  - A read-only MCP launched in Sept 2026
- **VET4.0 KI-Befunddokumentation is Vetnio** delivered through SnapVET ([vet40.de](https://www.vet40.de/news/befunddokumentation-mit-ki/)).
- **Add to the competitor list:**
  - Tandem Health (CE IIa, €125/user, VetFamily partnership)
  - VetScribe (NL)
  - QVET ESCRIBA (ES)
  - LAIKA (IT)
  - VetGenius (BE)
- **Scribenote and ScribbleVet** produce notes in English only. **VetRec's** German is in beta and it has no Italian.
