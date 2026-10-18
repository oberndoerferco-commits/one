# Owner-facing AI pet health products outside continental Europe (US, UK, Canada, Australia, global apps): state as of 2026-10-18

Method note: every page below was opened on 2026-10-18 unless another date is given. App Store ratings and review counts come from Apple's public iTunes Search/Lookup API. Recent-review distributions come from Apple's customer-review RSS feed (the "most recent 100" reviews per app). Peer-reviewed abstracts were read through the Europe PMC REST API and are linked by DOI. Several sites blocked automated access (HTTP 403/429). They are listed under Gaps and were not described from search snippets. The shared web-search budget ran out near the end, so some lines of enquiry (lawsuits, certifications, Google Play counts) are incomplete and flagged as such.

## 1. What each product actually does (symptom checker, triage chat, live vet chat/video, records, reminders, insurance tie-ins, wearables)

### Takeaway
Very few leading owner-facing products use AI for clinical triage in a substantive way.
- **Joii / Vet-AI (UK, now also marketed to the US)** is the stand-out. It runs a vet-supervised, Gemini-based LLM triage chat, and insurers such as Waggel distribute it for free.
- **Petriage** is a legacy "AI-driven" statistical symptom checker tied to clinic telehealth, and its public site looks dormant.
- **Device-data assistants** form a growing second group: Maven Companion (Oct 2026), PETKIT Kitbo (Aug 2026), Petcube, Furbo and TTcare.

Most big US/UK services are human-vet telehealth or membership businesses that use AI on the vet side or for customer service, not for owner triage: Vetster, FirstVet, Pawp, Dutch, Airvet, Chewy/PetMD, VCA, Petco. A long tail of indie "AI vet" apps launched in 2025–26 has almost no ratings.

### Cited Findings

**Joii Pet Care (Vet-AI Ltd, Leeds, UK)**
- **App features:** 24/7 video consultations with UK-registered vets. A free "pet symptom checker developed by vets" that can "identify 160 common conditions". Photo upload before the consult, a treatment plan saved to the app, and vet-recommended products delivered. "Joii vets resolve nearly 70% of issues they see via video consultation" — [Joii, App Store GB listing](https://apps.apple.com/gb/app/joii-pet-care/id1436958921) (accessed 2026-10-18)
- **Homepage:** advertises "24/7 vet chat – replies in ≅ 4mins", a free symptom checker ("over 160 common conditions"), image/video upload for vets, and "Smart AI-powered triage, book anytime". It shows a video-analysis "Mobility Score 84/100" mock-up.
- **US expansion:** the homepage now carries US-facing copy ("Real time video or chat with a US vet", "Connect live with a US-licensed vet", "Typical vet consultation $75-150" vs "Joii vet consultation From $0") — [Joii homepage](https://www.joiipetcare.com/) (accessed 2026-10-18)
- **AI architecture (vendor-reported):** a multi-agent design with a "'receptionist' AI for initial triage, specialist agents for common conditions, and full clinician oversight". It is said to be trained on >400,000 vet video consultations and "over 4 billion data points", and to handle 12,000+ real-world interactions a month. Functions listed: emergency detection before a consult, pre-consult summaries for vets, and 24/7 advice in the Joii app ("465,000+ registered owners") — [VetClick, Vet-AI press release, 2025-09-23](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **Technology stack:** Gemini plus text embeddings and RAG over past consultations, with built-in classification models that alert owners "if their pet needs immediate in-clinic care". Planned: Vertex AI Agent Engine Memory Bank so the app can "remember a pet's entire care history". The case study cites "over 570k registered pets in the UK" — [Google Cloud customer story: Vet-AI](https://cloud.google.com/customers/vet-ai) (undated; accessed 2026-10-18)
- **Evolution and roadmap:** Joii was "originally built on a decision tree" and moved to AI over about 18 months. Consult transcripts (via AssemblyAI) form the RAG backbone. Next steps are specialist agents (e.g., gastroenteritis), image/video analysis of skin conditions, and long-term memory — [Diginomica, 2025-11-13](https://diginomica.com/how-vet-ai-deployed-ai-pet-healthcare-10-weeks-without-hallucinations)
- **Insurer distribution (Waggel):** Waggel offers a Joii-powered "AI-powered veterinary triage service", free to all its customers. It runs 24/7, covers ">130 common illnesses and conditions", and escalates to vet video, with an average virtual wait of about 10 minutes — [Waggel blog, 2026-08-09](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies); [Insurance Edge, 2026-08-12](https://insurance-edge.net/2026/08/12/waggel-is-using-ai-vet-triage-services-to-save-pets-lives/)

**Petriage (US)**
- **Owner features:** a free "Petriage Analysis" and free pet profile. Owners can connect with their family vet (video, messaging, photo/video sharing). "Petriage Live" is a 24/7 veterinary nurse helpline, plus an online pharmacy.
- **Clinic features:** express check-in, eConsult, eCheck (remote monitoring) and Petriage Rx. The tool is described as an "AI-driven teletriage tool". The page carries a "© 2021" footer — [Petriage homepage](https://www.petriage.com/) (accessed 2026-10-18)
- **How it works (2021, older):** "statistical algorithms" turn owner inputs into a triage recommendation. A subscribing practice is "automatically alerted" and can start async or video telemedicine, with Stripe payments built in. US patent issued 2021-02-23 — [LifeLearn blog, 2021-03-03](https://www.lifelearn.com/2021/03/03/petriage-earns-patent-for-pet-symptom-checker/)
- **No current App Store presence:** an App Store search for "Petriage" (US, 2026-10-18) returned no Petriage app, only unrelated games — [iTunes Search API result](https://itunes.apple.com/search?term=Petriage&entity=software&country=us)

**Vetster (Toronto; CA/US/UK)**
- **Service:** a marketplace of vets offering 24/7 messaging or video, vet profiles with reviews, records storage, triage, second opinions, OTC product suggestions and care plans. "20+ species treated".
- **No owner-facing AI:** the homepage mentions no symptom checker or AI triage — [Vetster homepage](https://vetster.com/en) (accessed 2026-10-18)
- **Vet-facing AI only:** Vetster's AI tool is "AI Scribe", built into the platform for veterinarians. It "has helped vets complete charting in 5 minutes or less" — [Vetster, "Can ChatGPT be trusted for pet health advice?", 2026-06-18](https://vetster.com/en/wellness/can-chat-gpt-be-trusted-for-pet-health)
- **Plans:** "Get ongoing care for $10/month or book a single appointment". Prescriptions "where available" — [Vetster, App Store US](https://apps.apple.com/us/app/vetster-online-vets-24-7/id1551831515) (accessed 2026-10-18)

**FirstVet (Swedish-origin; UK and US apps)**
- **UK service:** video vet calls described as "a complement to, not a replacement for in-clinic care". Free for customers of 17 listed insurance partners (ManyPets, LV=, RSPCA, Napo, Revolut, Petsure and others) — [FirstVet UK pricing page](https://firstvet.com/uk/pricing-information) (accessed 2026-10-18)
- **No AI on the UK homepage:** it mentions no AI features (symptom checker, assistant or triage) and claims "1 million" video calls — [FirstVet UK homepage](https://firstvet.com/uk/) (accessed 2026-10-18)
- **Scope:** the app positions itself for "non-emergency questions and concerns", including horses — [FirstVet, App Store GB](https://apps.apple.com/gb/app/firstvet/id1349241101)

**Pawp (US)**
- **Membership:** 24/7 access to vet professionals with "unlimited, on-demand visits", ongoing care plans and personalised recommendations, by text and video chat. No AI features are described — [Pawp homepage](https://pawp.com/) (accessed 2026-10-18)
- **Emergency Protection add-on:** "up to $3,000 for one unexpected, life-threatening medical situation annually", once per year for one pet, for up to 6 pets, with a 14-day waiting period — [Pawp Help Center, 2026-07-16](https://help.pawp.com/en/articles/8609903-the-emergency-fund-add-on)
- **Walmart+ bundle:** the Pawp base membership "is included for free in your Walmart+ membership" — [Pawp Help Center, 2026-07-21](https://help.pawp.com/en/articles/10008059-how-does-pawp-s-emergency-protection-work-for-walmart-members)

**Dutch (US)**
- **Service:** licensed vets who diagnose and prescribe. Unlimited calls, messaging and follow-ups for up to 5 pets. About 10-minute video consults, with prescriptions shipped in about 1–3 business days. At-home lab test kits. "Treats 90% of health conditions" / ">150 issues".
- **Limits and staffing:** in-person care is needed for emergencies, stitches, bloodwork, imaging and surgery. The page says Dutch employs no vet techs or nurses. No AI features are described — [Dutch homepage](https://www.dutch.com/) (accessed 2026-10-18)
- **Membership extras:** the membership page adds "Longevity treatment plans" and "Advice on whether you need to go to the ER or urgent care" — [Dutch membership plans](https://www.dutch.com/pages/membership-plans) (accessed 2026-10-18)

**Chewy / PetMD (US)**
- **Modern Animal acquisition:** Chewy agreed to buy Modern Animal, which has "29 owned clinics, 24/7 virtual care, and a high-retention membership model" and "over 100,000 member families". The deal scales Chewy Vet Care "from 18 to 47 locations" — [Chewy press release via Nasdaq, 2026-04-08](https://www.nasdaq.com/press-release/chewy-acquire-modern-animal-accelerating-evolution-fully-integrated-healthcare)
- **Free vet chat:** the PetMD site header offers "Chat free with Chewy's vet team" — [PetMD homepage](https://www.petmd.com/) (accessed 2026-10-18)
- **PetMD Symptom Checker (2023):** a vet-designed questionnaire, not marketed as AI. "Our team of veterinarians identified over 50 of the most common symptoms and combinations." It leads to a summary of possible causes, "when you should call your vet", and links to pay for care or chat with a Chewy vet — [dvm360, 2023-10-09](https://www.dvm360.com/view/online-pet-symptom-checker-tool-now-available); current tool page [PetMD Symptom Checker](https://www.petmd.com/symptom-checker)

**VCA (Mars)**
- **Owner offer:** the myVCA app offers "Live Chat anytime, day or night", prescription and food refills, vaccine tracking and booking. A "CareClub Access Plan" offers "Unlimited Exams for $19.99/mo". No AI claims appear on the homepage — [VCA homepage](https://vcahospitals.com/) (accessed 2026-10-18)
- **App listing:** "24/7 Live Chat with Licensed Veterinary Professionals" plus health-care and medication reminders — [myVCA, App Store CA](https://apps.apple.com/ca/app/myvca/id1172429469)

**Petco Vital Care (US)** — older source (2023)
- **Programme:** 24 million subscribers were unified into Vital Care Core (free) and Vital Care Premier (paid). Premier includes "unlimited routine vet exams at a Petco vet or vet of choice". The app offers reminders and a membership dashboard — [Petco press release via Nasdaq, 2023-01-30](https://www.nasdaq.com/press-release/petco-unifies-customer-memberships-under-vital-care-program-for-an-integrated)
- **No AI found:** none was identified (see Gaps).

**Zoetis Petcare (US)**
- **Programme:** Petcare Rewards (points on Zoetis product purchases, redeemable toward vet care), "The Pack" app and "vet-approved resources". No AI claims — [Zoetis Petcare](https://www.zoetispetcare.com/) (accessed 2026-10-18)
- **The Pack app:** tracking of exercise, grooming, training and activities, a visual diary, records "in one place" and a medication log — [The Pack by Zoetis, App Store US](https://apps.apple.com/us/app/the-pack-by-zoetis/id1633459819)

**IDEXX Vello and PetDesk (practice-owned owner apps)**
- **Vello:** owners use an app or a "secure, password-free web portal" to book, view records, download vaccination history and request refills. AI appears only in Vello's Digital Forms and Surveys builder ("AI prompts and upload tools") — [Vello by IDEXX](https://software.idexx.com/vello) (accessed 2026-10-18)
- **PetDesk:** reminders and texting, online booking, loyalty, PIMS-integrated phones, a pet-parent app and "AI-powered SOAP notes" (vet-facing). Claims "over 12,000 veterinary practices" — [PetDesk](https://petdesk.com/) (accessed 2026-10-18)

**Airvet (US)**
- **Service:** "partners with workplaces to give employees 24/7 on-demand access to virtual vet care" by video and chat. Claims to have helped ">250,000 pet parents" — [Airvet, App Store US](https://apps.apple.com/us/app/airvet-for-pet-parents/id1448478595). The website could not be loaded (see Gaps).

**Wearables, cameras and device-data AI (global)**
- **Maven Pet Companion:** launched 2026-10-13 as an AI pet assistant inside the Maven app, available to all subscribers. It reads collar-sensor vitals, sleep, activity and behaviour ("up to 25 million data points per day") against each dog's baseline. Maven claims 125,000+ "proactive health insights". The press release mentions no staffed vet team — [Maven Pet paid press release via Yahoo Finance, 2026-10-13](https://finance.yahoo.com/healthcare/articles/dog-parents-ask-ai-dogs-195300108.html)
- **PETKIT Kitbo:** launched 2026-08-18. It combines litter-box, fountain and feeder data with "natural-language, multi-turn conversations" and produces "health reports… that pet parents can share with their vet". However, "select Kitbo AI features are expected to launch by the end of 2026" — [PETKIT blog, 2026-08-30](https://www.petkit.com/blogs/blog/kitbo-petkits-ai-powered-pet-health-assistant-for-smarter-pet-care)
- **Petcube:** the app offers "AI-powered answers about your pet's health, behavior, food, and training", chat with licensed vets, a Health Check questionnaire, a journal, reminders and device alerts — [Petcube, App Store US](https://apps.apple.com/us/app/petcube/id720151500)
- **Furbo:** the camera app markets an "AI-powered Furbo Nanny" — [Furbo, App Store US](https://apps.apple.com/us/app/id999707163). The AI Health Checker help page could not be loaded (see Gaps).
- **TTcare (AI For Pet, Korea):** "an AI homecare app for pets… from simple phone clips". It also offers TTcare Vet (clinic decision support), an equine product and an on-device vision SDK. Milestones: CES 2025 Innovation Awards in two categories, 1st place in startup pitching at the 2025 London Vet Show, and a PoC agreement with Nestlé (Jan 2026) — [AI For Pet](https://www.aiforpet.com/en) (accessed 2026-10-18)
- **Felcana (UK):** describes "the only clinical-grade pet activity monitor". The app was last updated 2022-02-07 and has 13 ratings — [Felcana, App Store GB](https://apps.apple.com/gb/app/felcana/id1328461371)

**Indie "AI vet" / symptom-checker apps (2025–26)**
- **Vetify** (released 2026-04-03): "INSTANT AI DIAGNOSIS… expert-level insights in seconds". 0 ratings — [App Store](https://apps.apple.com/app/id6761506524)
- **PetNexa** (released 2026-03-06): "An AI vet in your pocket". 0 ratings — [App Store](https://apps.apple.com/us/app/id6756158864)
- **PetCare AI** (PetCare AI Pty Ltd, released 2026-06-20): "clear urgency level with practical next steps… not a replacement for veterinary care". 0 ratings — [App Store](https://apps.apple.com/app/id6775739913)
- **TriageTail** (released 2026-03-20): urgency levels "Monitor, Urgent, or Emergency". Cases are saved locally, two consultations are free, then premium. 0 US ratings — [App Store](https://apps.apple.com/app/id6760662686)
- **PawLine** (released 2026-02-08): 5.0 from 36 ratings — [App Store](https://apps.apple.com/app/id6758164151)
- **PetGpt:** 0 ratings, last updated 2025-03-02 — [App Store](https://apps.apple.com/us/app/petgpt/id6639584645)
- **Dr.Tail ("24/7 AI Vet Care"):** AI preventive-care plans, records and "24/7 Vet-Related Support" — [App Store](https://apps.apple.com/us/app/dr-tail-24-7-ai-vet-care/id1591575192)

### Inferences
- The realistic best-in-class benchmark for an owner-facing AI triage experience is Joii/Vet-AI. It combines an LLM triage layer, RAG over its own consult transcripts, emergency classifiers, a 24/7 human-vet fallback, pre-consult summaries for vets, and insurer-funded free access. A content-plus-triage EU site will be compared with that combination.
- In the US, "AI" in the leading brands is mostly invisible to owners: vet scribes (Vetster, PetDesk), form builders (Vello), and, per unverified reports, customer-service bots (Chewy). Owner-facing AI there comes mainly from device makers and small app studios.
- Device-data assistants (Maven, Kitbo, Petcube) show a 2026 trend: pet-specific memory and baselines plus a shareable summary for the vet. That is a feature an owner site can copy without hardware, for example owner-logged symptoms and a timeline exported as a pre-visit brief.

### Gaps
- No primary data was obtained on Fuzzy (status unknown), "Bark/Woof" health AI (the BARK app found is a subscription-box app, not health), or Chewy's reported customer-service assistant "Kai". The MarketBeat page I opened contained no transcript, so the Kai claim is search-snippet-only and unverified.
- Could not load Chewy's "Connect with a Vet" page (HTTP 429), Airvet's website (429), Petco's Vital Care page (403) or Furbo's AI Health Checker help page (403). Their current feature details are not verified.
- The Modern Animal deal closing (reported as 2026-05-21, $399.8M) comes only from a search snippet of Chewy's 10-Q. My direct fetch returned an empty file.
- No Australian- or Canadian-specific AI owner products were verified (an App Store AU search for "VetChat" did not surface a VetChat app).

## 2. How products present the AI (labelling, human-in-the-loop, disclaimers, emergency escalation, triage phrasing, sources/authorship)

### Takeaway
Presentation splits into three styles:
1. **Explicitly labelled AI with a human vet always one tap away.** Joii/Waggel: "Smart AI-powered triage", "AI-powered vet assistant", "60 vets online".
2. **Vet-built questionnaires not marketed as AI.** PetMD; Petriage's statistical "AI-driven" checker.
3. **Indie apps that brand themselves "AI vet" or "instant AI diagnosis"** with thin disclaimers.

Emergency escalation is usually phrased as an instruction to attend or call a vet now. Few products show an explicit "not for emergencies" disclaimer on the homepage. Content sites that do show vet authorship (PetMD, Vetster) do not publish an AI-use policy.

### Cited Findings
**Labelling and human-in-the-loop**
- **Joii/Vet-AI:** labels the feature as AI ("Smart AI-powered triage") while stating "Every consultation is handled by real, licensed vets" — [Joii homepage](https://www.joiipetcare.com/) (accessed 2026-10-18)
- **Waggel:** consistently labels the service as AI ("AI-powered vet assistant", "Joii's AI model") — [Waggel blog, 2026-08-09](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies)
- **Vet-AI human-in-the-loop claims:**
  - "we always have 60 vets online and whenever advice cannot be given or it is not grounded in truth, we bring them straight in"
  - no model is launched "without running it in what we call 'ghost mode'… with all the medical sign-off"
  - triage interactions are tracked for factuality, integrity, safety, readability and empathy
  - Source: [Diginomica, 2025-11-13](https://diginomica.com/how-vet-ai-deployed-ai-pet-healthcare-10-weeks-without-hallucinations)
- **Weekly case review:** "Every case handled by Vet-AI's platform is reviewed weekly by veterinary teams" — [VetClick, 2025-09-23](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **AI as vet assistant:** a Joii vet testimonial on the homepage says "The AI assistant saved me so much time", referring to pre-collected history — [Joii homepage](https://www.joiipetcare.com/)

**Emergency escalation phrasing**
- **Joii-powered (Waggel):** for difficulty breathing, collapse, severe lethargy or seizures, the system "instantly advises them to attend a veterinary practice without waiting for a routine consultation". In a cat ant-poison case, the owner was told "to call her vet immediately". The article itself contains no explicit medical disclaimer — [Waggel blog, 2026-08-09](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies)
- **Petriage:** four levels, "Non-threatening", "Worrisome", "Urgent" and "Emergency", with recommendations for scheduling the next vet visit. No veterinary disclaimer appears on the homepage — [Petriage homepage](https://www.petriage.com/) (accessed 2026-10-18)
- **Petriage (2021):** the range also included "seek medical advice". A quoted Google Play review says "It told us we had 24 hours to have him looked at", showing time-window phrasing — [LifeLearn, 2021-03-03](https://www.lifelearn.com/2021/03/03/petriage-earns-patent-for-pet-symptom-checker/)
- **PetMD Symptom Checker:** ends on a summary of "possible causes, when you should call your vet", plus links to pay for care or chat with a Chewy vet — [dvm360, 2023-10-09](https://www.dvm360.com/view/online-pet-symptom-checker-tool-now-available)
- **Indie apps:**
  - TriageTail: a "conservative read on urgency" with "Monitor, Urgent, or Emergency" — [App Store](https://apps.apple.com/app/id6760662686)
  - PetCare AI: a "clear urgency level with practical next steps… not a replacement for veterinary care" — [App Store](https://apps.apple.com/app/id6775739913)
  - Vetify: markets "INSTANT AI DIAGNOSIS" — [App Store](https://apps.apple.com/app/id6761506524)
  - PetNexa: "An AI vet in your pocket" — [App Store](https://apps.apple.com/us/app/id6756158864)
- **Human telehealth framing:**
  - FirstVet: vets "can help you decide whether an issue is an emergency" and "will always refer you to a clinic if needed" — [FirstVet UK](https://firstvet.com/uk/). The app is aimed at "non-emergency questions" — [App Store GB](https://apps.apple.com/gb/app/firstvet/id1349241101)
  - Dutch: lists "Advice on whether you need to go to the ER or urgent care" — [Dutch membership plans](https://www.dutch.com/pages/membership-plans)
  - Pawp: invites owners to "seek advice for urgent and emergency issues" — [App Store](https://apps.apple.com/us/app/pawp-24-7-vet-pet-care/id1594794194). Its homepage carries no emergency disclaimer — [Pawp](https://pawp.com/) (accessed 2026-10-18)
  - Joii: says its RCVS-registered vets "will always tell you if you need to see your local practice for in-person care" — [App Store GB](https://apps.apple.com/gb/app/joii-pet-care/id1436958921)

**Sources and vet authorship on content**
- **PetMD:**
  - "All new content… is written or reviewed by a veterinarian or subject matter expert" (DVM/VMD, licensed).
  - Authors and reviewers are named, with links to bios; "at least two editors" review each piece, followed by another round of medical review; review dates are published.
  - Content is sourced to "peer-reviewed journals, medical textbooks". Positions on contested topics are set with AVMA and the Chewy Veterinary Advisory Panel.
  - The page contains no statement about AI-generated content.
  - Source: [PetMD Editorial Guidelines](https://www.petmd.com/editorial-guidelines) (accessed 2026-10-18)
- **Vetster:** articles show "Researched by: The Vetster Editorial Team" and "Verified by: Dr. Jo Myers", with published and updated dates (2026-06-18 / 2026-06-20). There is no broader editorial policy on the page — [Vetster article](https://vetster.com/en/wellness/can-chat-gpt-be-trusted-for-pet-health)
- **Zoetis:** labels resources "Vet-Approved". Its footer disclaimer says information is "for educational purposes only and is not intended to replace discussions with an animal healthcare professional" — [Zoetis Petcare](https://www.zoetispetcare.com/)

### Inferences
- **Labelling:** no leading product hides that a feature is AI. Best practice in 2026 is explicit labelling plus a visible, immediate human fallback. Indie "AI diagnosis" branding contradicts the professional norm that clinical decisions are not wholly delegated to AI (see the RCVS advice in section 5) and is a differentiation opportunity for a vet-reviewed site.
- **Triage phrasing:** the common pattern is 3–5 urgency tiers. Action-and-time phrasing ("attend a practice now", "within 24 hours", "call your vet immediately") is more useful than bare labels. No product shown publishes its tier definitions or error rates.
- **AI policy:** even PetMD, the strongest editorial example, has no AI-content policy on its editorial page. A published AI-use and review policy (who reviewed, when, sources, model limits) would be a clear point of difference.

### Gaps
- Joii's in-app wording for each triage outcome (beyond the emergency case) could not be verified: the symptom-checker page URLs from search results returned 404. Its in-app disclaimers were not inspected.
- Furbo's AI Health Checker presentation (search snippets claim "three possible diagnoses with confidence levels") is unverified because the page was blocked.

## 3. Trust signals (named vets and credentials, ratings and review counts, certifications, validation studies, editorial policies)

### Takeaway
The strongest trust signals in the field are regulatory registration and named clinicians: Joii shows its RCVS practice number and vets' RCVS numbers; Dutch names its CMO and vets with years of experience. These come with app-store ratings in the 4.6–4.97 range and a PetMD-style editorial policy.

No owner-facing AI product has a peer-reviewed validation. Vet-AI's "81% clinical accuracy" is a vendor-run blind review of 48 simulated conversations. Petriage's accuracy claims are self-reported. No SOC 2, ISO 27001/42001 or HIPAA-style claims were seen on the pages opened.

### Cited Findings
**Named vets and registration**
- **Joii:** the footer shows "A registered RCVS Vet Practice (7499851)", names three vets with RCVS numbers (e.g., "Nicholas Garside BVetMed MRCVS (RCVS number 7130236)"), and names VioVet as POM-V dispenser with its RCVS practice number — [Joii homepage](https://www.joiipetcare.com/) (accessed 2026-10-18)
- **Dutch:** profiles four vets with years of experience and names Chief Medical Officer Dr. Kate Elden. Badges: "LegitScript certified", BBB accredited, Inc. 5000, Trustpilot — [Dutch homepage](https://www.dutch.com/) (accessed 2026-10-18)
- **Pawp:** "Licensed, Registered, Certified Veterinarians, Nurses, and Technicians… Minimum 5+ years of clinical experience". No individual vets are named on the homepage — [Pawp](https://pawp.com/)
- **FirstVet:** "All of our vets are UK registered and have 3+ years of experience" — [App Store GB](https://apps.apple.com/gb/app/firstvet/id1349241101)

**Ratings and review counts**

| Product | Store | Rating (count) | Source |
|---|---|---|---|
| Joii Pet Care | App Store GB | 4.94 (5,933) | [link](https://apps.apple.com/gb/app/joii-pet-care/id1436958921) |
| FirstVet | App Store GB | 4.97 (15,114) | [link](https://apps.apple.com/gb/app/firstvet/id1349241101) |
| FirstVet | App Store US | 4.74 (467) | [link](https://apps.apple.com/us/app/firstvet/id1349241101) |
| Vetster | App Store US | 4.57 (2,839) | [link](https://apps.apple.com/us/app/vetster-online-vets-24-7/id1551831515) |
| Vetster | App Store CA | 4.72 (899) | [link](https://apps.apple.com/ca/app/vetster-online-vets-24-7/id1551831515) |
| Pawp | App Store US | 4.87 (14,934) | [link](https://apps.apple.com/us/app/pawp-24-7-vet-pet-care/id1594794194) |
| Dutch Vet | App Store US | 4.66 (773); app released 2026-03-10 | [link](https://apps.apple.com/us/app/id6745529739) |
| Airvet | App Store US | 4.93 (11,209) | [link](https://apps.apple.com/us/app/airvet-for-pet-parents/id1448478595) |
| myVCA | App Store CA | 4.83 (1,420) | [link](https://apps.apple.com/ca/app/myvca/id1172429469) |
| Chewy | App Store US | 4.91 (1,208,952) | [link](https://apps.apple.com/us/app/chewy-pet-care-pharmacy/id1149449468) |
| Petco | App Store US | 4.74 (419,346) | [link](https://apps.apple.com/us/app/petco-the-pet-parents-partner/id1368715736) |
| PetDesk | App Store US | 4.86 (507,690) | [link](https://apps.apple.com/us/app/id631377773) |
| The Pack by Zoetis | App Store US | 4.88 (9,992) | [link](https://apps.apple.com/us/app/the-pack-by-zoetis/id1633459819) |
| IDEXX Vello | App Store US | 4.41 (22) | [link](https://apps.apple.com/us/app/id6471983227) |
| Petcube | App Store US | 3.66 (1,035) | [link](https://apps.apple.com/us/app/petcube/id720151500) |
| Dr.Tail | App Store US | 4.77 (683) | [link](https://apps.apple.com/us/app/dr-tail-24-7-ai-vet-care/id1591575192) |
| Maven | App Store US | 4.67 (98) | [link](https://apps.apple.com/us/app/id1635378840) |
| Furbo | App Store US | 4.79 (5,569) | [link](https://apps.apple.com/us/app/id999707163) |
| PETKIT | App Store US | 4.59 (20,750) | [link](https://apps.apple.com/us/app/id994053492) |

All figures accessed 2026-10-18 via Apple's API.

**Self-reported ratings and satisfaction claims**
- **Joii:** "4.9 ★ on App Store (5.9k reviews)" and "4.4 ★ on Google Play (3k reviews)" — [Joii homepage](https://www.joiipetcare.com/)
- **Vetster:** Google 4.9 and Trustpilot 4.8 with no counts, and a "97%" resolution rate with no methodology — [Vetster](https://vetster.com/en)
- **FirstVet:** "4.9 App Store rating" and "98% Happy pet parents" — [FirstVet UK](https://firstvet.com/uk/)
- **Dutch:** "4.7 with 4k+ reviews" — [Dutch](https://www.dutch.com/)
- **Petcube:** its site claims "4.3/5 (19,143 ratings)", against a 3.66 App Store rating — [Petcube](https://petcube.com/)

**Validation claims (vendor)**
- **Vet-AI benchmark:**
  - In "blind testing conducted in April 2025, UK vets reviewed 48 simulated pet-owner conversations" from Vet-AI's model, Gemini 2.0 and ChatGPT 4.0.
  - Clinical accuracy: Vet-AI 81%, Gemini 69%, ChatGPT 50%. Correct "triage stops": 81% vs 75% vs 56%.
  - Vet-AI calls this "independent benchmarking", but it was announced by Vet-AI itself (author field "Vet-AI").
  - Source: [VetClick, 2025-09-23](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **Google Cloud case study:** "81% clinical accuracy", "Reduces vet consultation times by 8%" and "94% customer satisfaction score" — [Google Cloud](https://cloud.google.com/customers/vet-ai). This differs from the "95% satisfaction" in the [VetClick release](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **Petriage:** the model is "continuously validated by a team of veterinarians". The homepage's patent-news link URL contains the phrase "99-plus accurate", but the visible page states no figure — [Petriage](https://www.petriage.com/)
- **Maven:** "built with veterinarians" and "clinically validated", with figures attributed to "Maven Pet internal data, 2026" in a paid press release — [Yahoo Finance, 2026-10-13](https://finance.yahoo.com/healthcare/articles/dog-parents-ask-ai-dogs-195300108.html)

**Editorial policy**
- **PetMD:** see section 2. Its homepage claims "100+ Expert Vets" and "6k+ Reviewed articles" — [PetMD](https://www.petmd.com/); [Editorial Guidelines](https://www.petmd.com/editorial-guidelines)

**Peer-reviewed validation of owner-facing veterinary symptom checkers is essentially absent**
- **2020 baseline (older):** "little to no peer-reviewed research has been published regarding animal symptom checkers" — [Stans 2020, Open Vet J](https://doi.org/10.4314/ovj.v10i1.1)
- **2026 methodology paper:** validates an expert-knowledge veterinary symptom checker only on synthetic dialogues (about 550 diseases each for dogs and cats). It reports "full convergence under ideal conditions (100%)" and notes that "clinical and user studies" are still needed — [Löwe & Löwe, Vet Res Commun, 2026-05-25](https://doi.org/10.1007/s11259-026-11263-8)
- **2026 systematic survey:** of AI in veterinary digital health, 22 included studies. It cites "insufficient external validation" and "the absence of prospective real-world clinical evaluation" — [Polapragada, Front Vet Sci, 2026-07-30](https://doi.org/10.3389/fvets.2026.1853395)

### Inferences
- **Credentials:** publishing a practice registration number, named reviewing vets with registration numbers and dated reviews is the trust ceiling seen in this market. An EU site can match it with national-register numbers per reviewer.
- **Validation:** no competitor publishes a reproducible validation of its owner-facing triage. A published protocol with results — sensitivity for emergencies, over-triage rate, test set, vet panel, model version and date — would be unique. Wong et al. (section 5) provide a ready-made comparison design (waiting-time categories and agreement against vets).
- **Inconsistent metrics:** marketing numbers are often inconsistent within the same company, which an evidence-led competitor can exploit by publishing dated, consistent metrics:
  - Joii: 420k+ pet parents (homepage) vs 465,000+ registered owners (2025 release)
  - Vet-AI satisfaction: 94% vs 95%
  - Dutch: 600k+ members vs 900,000+ pet parents
  - Vetster: "50 countries" vs CA/US/GB service
  - FirstVet partner count: 16 / 17 / "over 20"

### Gaps
- No SOC 2, ISO 27001, ISO 42001 or HIPAA-like claims were seen on any page opened. However, privacy policies, terms and security pages were not systematically reviewed because the search budget ran out, so absence is not confirmed.
- Google Play rating counts were not collected, apart from Joii's self-reported figure.
- Petriage's ">97% accurate" figure appears only in search snippets of a press release that I did not open.

## 4. Pricing and business model (numbers and dates)

### Takeaway
Owner-facing pet telehealth outside continental Europe is funded in four main ways:
1. **Insurer-funded free access**, dominant in the UK: FirstVet with 17 partners, Joii with Animal Friends, ASDA Money, Purely Pets and Waggel.
2. **Consumer memberships** of roughly $10–$20 a month: Dutch $199/yr, Vetster $10/mo, VCA CareClub $19.99/mo, Petco Premier $19.99/mo.
3. **Retailer or employer bundling:** Pawp inside Walmart+, free Chewy vet chat, Airvet via employers.
4. **Practice-paid software** that is free to owners: Vello $249/mo per practice, PetDesk.

Pay-per-consult UK prices are £24–£36 (FirstVet) or £28 (Joii). AI triage itself is free everywhere it is offered and acts as a funnel into consults, products or insurance.

### Cited Findings
**UK pay-per-consult and insurer access**
- **FirstVet UK:** "Weekdays 9 am to 6 pm: £24"; "Out of hours: £36". "Available 24 hours a day, 365 days a year". Free for customers of 17 insurance partners, with no deductible and no effect on premium — [FirstVet UK pricing information](https://firstvet.com/uk/pricing-information) (accessed 2026-10-18)
- **Joii UK:** "£28 for a video vet consultation (or free if your pet is insured with one of our partners). No extra charges for night calls". "Unlimited vet calls for partner insurance customers including Animal Friends Insurance, ASDA Money, Purely Pets and Waggel" — [App Store GB](https://apps.apple.com/gb/app/joii-pet-care/id1436958921) (accessed 2026-10-18)
- **Joii US-facing copy:** "Joii vet consultation From $0", against "Typical vet consultation $75-150" — [Joii homepage](https://www.joiipetcare.com/)
- **Waggel:** the Joii-powered AI triage is "free to all Waggel customers". The CEO says Waggel was "one of the first insurers to offer this technology as part of our cover" — [Waggel blog, 2026-08-09](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies)

**US memberships**
- **Dutch:**
  - Annual plan "$17/mo, billed $199 today", or Klarna 4 × $50; a promo code gives $60 off.
  - Up to 5 pets, "Free prescription delivery" ("Rx ships free"), 20% off flea and tick, $25 off a product order. Medication costs are separate.
  - Marketed comparison: "Average exam cost $0 vs $160" and "$650 savings per year vs. other vets".
  - Not insurance; itemised invoices are provided for insurer reimbursement.
  - Sources: [Dutch membership plans](https://www.dutch.com/pages/membership-plans); [Dutch homepage](https://www.dutch.com/) (accessed 2026-10-18)
- **Vetster:** "Get ongoing care for $10/month or book a single appointment" — [App Store US](https://apps.apple.com/us/app/vetster-online-vets-24-7/id1551831515). Recent 1★ reviews cite a "$120" charge and an extra fee "bringing the total to about double" — [Apple RSS reviews, Vetster US](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1551831515/sortby=mostrecent/json) (accessed 2026-10-18)
- **Pawp:**
  - The homepage gives no price, only "an annual membership" and "Risk-free cancellation at anytime" — [Pawp](https://pawp.com/) (accessed 2026-10-18)
  - Emergency Protection is an "optional coverage plan" worth up to $3,000 a year. If the base membership is cancelled, it keeps billing to the end of the membership year — [Pawp Help Center, 2026-07-16](https://help.pawp.com/en/articles/8609903-the-emergency-fund-add-on)
  - The base membership is free inside Walmart+ — [Pawp Help Center, 2026-07-21](https://help.pawp.com/en/articles/10008059-how-does-pawp-s-emergency-protection-work-for-walmart-members)
- **VCA CareClub Access Plan:** "Unlimited Exams for $19.99/mo.*" — [VCA](https://vcahospitals.com/) (accessed 2026-10-18)
- **Petco Vital Care Premier (2023):** $19.99 per month per cat or dog, including "unlimited routine vet exams at a Petco vet or vet of choice". $9.99 per month for companion animals. Annual commitment required — [Petco via Nasdaq, 2023-01-30](https://www.nasdaq.com/press-release/petco-unifies-customer-memberships-under-vital-care-program-for-an-integrated)
- **Chewy:** free vet chat ("Chat free with Chewy's vet team") — [PetMD](https://www.petmd.com/). The Modern Animal acquisition adds a membership model with "over 100,000 member families" and over $125M annualised revenue — [Chewy via Nasdaq, 2026-04-08](https://www.nasdaq.com/press-release/chewy-acquire-modern-animal-accelerating-evolution-fully-integrated-healthcare)

**Employer, practice-paid and device models**
- **Airvet:** employer-benefit model — [App Store US](https://apps.apple.com/us/app/airvet-for-pet-parents/id1448478595)
- **IDEXX Vello:** "a flat monthly fee of $249" per practice, with "no cost to pet owners"; optional postcards cost $1.10 each — [Vello by IDEXX](https://software.idexx.com/vello) (accessed 2026-10-18)
- **Devices and subscriptions:**
  - Maven: annual subscription $167.92 including hardware — [Yahoo Finance, 2026-10-13](https://finance.yahoo.com/healthcare/articles/dog-parents-ask-ai-dogs-195300108.html)
  - Petcube Care: "starting from $5.99/mo" — [Petcube](https://petcube.com/) (accessed 2026-10-18)
  - TriageTail: two free consultations, then premium — [App Store](https://apps.apple.com/app/id6760662686)
  - PetCare AI: "Free to start" — [App Store](https://apps.apple.com/app/id6775739913)
- **Petriage:** free to owners; practices subscribe and are alerted (2021) — [LifeLearn, 2021-03-03](https://www.lifelearn.com/2021/03/03/petriage-earns-patent-for-pet-symptom-checker/)

**Context: owner willingness to pay** (German sample, so continental and indicative only)
- "video consultations are more likely to be accepted, while text-based services are often expected to be free" (404 owners) — [Karsch et al., Front Vet Sci, 2026-01-22](https://doi.org/10.3389/fvets.2026.1731577)

### Inferences
- **Free triage is the norm:** AI triage is a free entry point everywhere it is offered. Revenue comes from what follows: consults, prescriptions and products, insurer contracts, retail ecosystems. An EU site planning to charge for AI triage alone would be out of line with the market. Free triage plus a paid or insurer-funded vet consult or pre-visit brief fits it.
- **UK price anchor:** a human vet video call costs £24–£36. Owners insured with partners get unlimited calls free, which sets a high bar for any paid UK or Ireland offer.

### Gaps
- Pawp's base membership price and add-on price were not verified from a page I could open. Search snippets claim a $19/mo Emergency Protection add-on, a grandfathered $24/mo plan and roughly $99/yr base membership (third-party).
- Vetster per-appointment prices (set by vets) were not verified.
- Airvet's current consumer price is unknown; the $30/session figure in a 2021 article was not opened.
- Chewy "Connect with a Vet" eligibility rules could not be loaded.

## 5. Documented weaknesses, errors, regulatory actions, complaints, and accuracy studies (incl. LLMs on veterinary questions, 2023–2026)

### Takeaway
**Peer-reviewed evidence (2023–2026)** shows general LLMs can:
- reach 77–93% on exams and complex diagnostic packets;
- catch 80–90% of critical canine emergencies;
- but over-triage around 60% of non-urgent cases, misjudge low-risk patients (ASA 1 overestimated), give unreliable pain scores from photos, and change answers with small wording changes.

**Vendor tests** (Vet-AI, Vetster) find ChatGPT hallucinating, skipping urgency assessment and making medication errors. The only owner-facing AI benchmark is vendor-run.

**Complaints:** the most frequent documented problems with owner-facing services are operational, not AI errors. They include US state licensing limits on prescribing, billing and cancellation friction, pharmacy delays, insurer-account linking failures, and an owner-perceived "always go to the vet" over-triage (Joii, 2024).

**Regulation:** no regulatory actions or lawsuits were found in the sources opened. The RCVS (April 2026) says clinical decisions "must not be wholly delegated to AI".

### Cited Findings
**Peer-reviewed and preprint evaluations (headline numbers)**
- **Emergency triage (Wong et al., Veterinary Record, online 2025-12-04):** retrospective canine ER cases triaged into waiting-time categories of 0, 15, 30–60, 120 and 240 min by three vets, two nurses, ChatGPT-3.5 and ChatGPT-4.0.
  - ChatGPT correctly prioritised "80%–90% of critical cases, but over-triaged around 60% of non-urgent cases as requiring immediate attention".
  - ChatGPT's performance was "comparable to that of nurses".
  - Using ChatGPT to flag "0 minutes" cases alongside nurses raised sensitivity to 95%.
  - Authors warn of "increased pressure on emergency clinics".
  - Source: [Wong et al. 2025, doi:10.1002/vetr.6126](https://doi.org/10.1002/vetr.6126)
- **Diagnostic packets (İlgün et al., Veterinary Journal, 2026-07-10):** 38 dogs and cats with splenic disease, given standardised multimodal case packets.
  - Exact-diagnosis accuracy: experts 92.1% / 89.5%, ChatGPT-5 76.3%, Gemini 1.5 Pro 71.1%, novices 57.9% / 52.6%.
  - Malignancy AUC: Expert-1 0.97, ChatGPT-5 0.86.
  - Source: [doi:10.1016/j.tvjl.2026.106776](https://doi.org/10.1016/j.tvjl.2026.106776)
- **Anaesthetic risk (Okur et al., Veterinary Record, 2026-05-12):** 225 feline and canine cases.
  - ASA classification accuracy: ChatGPT-5 53.3%, ChatGPT-4o 46.7%, Gemini 2.5 Pro 30.7%.
  - "ASA 1 cases were frequently misclassified, mainly due to ASA overestimation".
  - "expert oversight remains essential".
  - Source: [doi:10.1002/vetr.70741](https://doi.org/10.1002/vetr.70741)
- **Pain scoring (Ngai et al., Scientific Reports, 2025-12-09):** ChatGPT, Gemini, Claude and Perplexity each scored 50 cat facial images twice with the Feline Grimace Scale.
  - All chatbots showed positive bias, meaning they underestimated scores. Only Claude had acceptable bias.
  - "Most chatbots showed poor agreement and could have compromised analgesia".
  - Source: [doi:10.1038/s41598-025-27404-z](https://doi.org/10.1038/s41598-025-27404-z)
- **Client handouts (Novak et al., JVIM, 2026):** ChatGPT-3.5 handouts on canine diabetes mellitus, IMHA and feline IBD were rated by ACVIM-SAIM diplomates and 50 pet owners. Owners reported greater understanding. Conclusion: "Although some refinement is warranted, ChatGPT-3.5 was able to successfully generate client educational handouts" — [doi:10.1093/jvimsj/aalaf058](https://doi.org/10.1093/jvimsj/aalaf058)
- **Exam questions (Alonso Sousa et al., Front Vet Sci, 2025-08-26):** nine LLMs on 250 veterinary final-exam MCQs.
  - ChatGPT o1 Pro 90.4%, ChatGPT 4.5 90.8%, Kimi 1.5 64.8%.
  - Performance was lower on image-based and harder questions.
  - Source: [doi:10.3389/fvets.2025.1616566](https://doi.org/10.3389/fvets.2025.1616566)
- **Japanese licensing exam (Kako et al., Scientific Reports, 2026-02-16):** OpenAI o3 scored 92.9% overall on the Japanese National Veterinary Licensing Examination, passing all sections — [doi:10.1038/s41598-026-37300-9](https://doi.org/10.1038/s41598-026-37300-9)
- **Collapsing dogs (Abani et al., Front Vet Sci, 2023-10-10, opinion article with a small case test):**
  - ChatGPT's diagnoses changed when "grammar and choice of words… were slightly modified", and adding exam findings sometimes worsened them.
  - Paroxysmal dyskinesia was rarely identified (one of five cases).
  - Warns that ChatGPT's "personalized and plausible sounding reply… can be misleading" for owners.
  - Source: [Frontiers](https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2023.1245168/full)
- **Remote-prescribing audit (Smith et al., Veterinary Evidence, 2022, older):** a UK telemedicine app audit of 21,383 video consults (Apr–Oct 2020).
  - 16.6% resulted in a POM-V/POM prescription, with a mild adverse-event rate of 0.8% (30/3,541).
  - Antibacterials were prescribed in 5.88% of consults, 99.3% of them first-line.
  - 89% of known outcomes were complete or the expected response.
  - Source: [doi:10.18849/ve.v7i2.553](https://doi.org/10.18849/ve.v7i2.553)

**Vendor tests of general chatbots**
- **Vet-AI benchmark:** ChatGPT 4.0 scored 50% clinical accuracy and 56% correct triage stops in Vet-AI's 48-conversation blind review, against Vet-AI's 81% / 81% — [VetClick, 2025-09-23](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **Vetster test:** a Vetster vet put 10 commonly searched questions to ChatGPT while logged out. Problems found:
  - it "hallucinated the cat was a Bengal";
  - it moved to home remedies before establishing urgency ("Consider the risk of spending the next 24 hours trying home suggestions");
  - it gave overconfident vomiting advice and black-and-white toxic-food claims;
  - it wrongly called acetaminophen universally unsafe for dogs while missing combination-product risks.
  - Vetster also notes ChatGPT "wasn't entirely wrong on most answers".
  - Source: [Vetster, 2026-06-18](https://vetster.com/en/wellness/can-chat-gpt-be-trusted-for-pet-health)

**App-store complaints** (Apple's most recent 100 reviews per app, accessed 2026-10-18; lifetime averages remain high, see section 3)
- **Pawp** (2025-11-29 to 2026-10-15): 44 × 1★, 6 × 2★, 47 × 5★. Themes:
  - a vet no-show for a scheduled slot;
  - Walmart+ account linking failures;
  - "doesn't even provide a phone number";
  - "Advertised availability of prescription online just to redirect to a local vet";
  - "cannot legally provide services in many states";
  - billing continuing after a pet died;
  - a rigid symptom list that "doesn't allow you to type in a specific issue".
  - Source: [Apple RSS, Pawp](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1594794194/sortby=mostrecent/json)
- **Vetster US** (2025-05-01 to 2026-10-15): 52 × 1★, 7 × 2★, 33 × 5★. Themes:
  - no prescription because the vet was not licensed in the owner's state;
  - "Misleading Pricing — Ended Up Costing Double";
  - "Impossible to cancel subscription";
  - one owner wrote that the vet could "only provide the same information that you can find online if you check with ChatGPT".
  - Source: [Apple RSS, Vetster](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1551831515/sortby=mostrecent/json)
- **Dutch** (n=96, 2026-03-16 to 2026-10-12): 29 × 1★, 56 × 5★. Themes:
  - medication shipping taking over a week;
  - confusion over annual vs monthly billing and prescriptions not included;
  - refill friction;
  - no doctor available in Louisiana;
  - a vet who "jumped to the worst case scenario".
  - Source: [Apple RSS, Dutch](https://itunes.apple.com/us/rss/customerreviews/page=1/id=6745529739/sortby=mostrecent/json)
- **Joii GB** (2022-07-15 to 2026-08-22): 13 × 1★, 81 × 5★. Themes:
  - insurer-policy linking failures (Animal Friends);
  - "Every single time the app says 'go see the vet'. It's pointless" (2024-07-30), an owner-perceived over-triage complaint;
  - a video vet who misread a cat in heat as injured (2023-11-16).
  - Source: [Apple RSS, Joii](https://itunes.apple.com/gb/rss/customerreviews/page=1/id=1436958921/sortby=mostrecent/json)
- **FirstVet GB** (2025-01-16 to 2026-10-15): 95 × 5★, 3 × 1★. All negative reviews concern insurance-verification or server errors at sign-up — [Apple RSS, FirstVet](https://itunes.apple.com/gb/rss/customerreviews/page=1/id=1349241101/sortby=mostrecent/json)
- **Airvet** (2026-04-07 to 2026-10-12): 98 × 5★, 1 × 1★ ("Rude vet") — [Apple RSS, Airvet](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1448478595/sortby=mostrecent/json)
- **Petcube** (2023-11-20 to 2026-10-11): 54 × 1★, 21 × 2★. Themes:
  - crashes on iOS 27;
  - recording gaps and GPS inaccuracy;
  - a privacy incident: "There's a camera connected under my username but somehow it was connecting to someone else's home camera" (2026-04-21).
  - Source: [Apple RSS, Petcube](https://itunes.apple.com/us/rss/customerreviews/page=1/id=720151500/sortby=mostrecent/json)
- **Maven** (n=23): complaints about pairing, battery life ("only lasts maybe 2 days"), "$20 a month" subscription and no phone support — [Apple RSS, Maven](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1635378840/sortby=mostrecent/json)
- **Dr.Tail** (older, 2022): questions unanswered for days ("over 72 hours", "10 days") — [Apple RSS, Dr.Tail](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1591575192/sortby=mostrecent/json)

**Professional regulation (UK)**
- **RCVS advice (agreed April 2026):**
  - "Professional and clinical decision making must not be wholly delegated to AI".
  - Vets and nurses "remain responsible for their decision to use the tool".
  - Users need "sufficient understanding of the subject matter".
  - Confidentiality and Data Protection Act 2018 / UK GDPR apply.
  - "Where AI tools are used [to] generate clinical records, the output should be manually verified".
  - The advice applies the existing Code rather than creating "additional, onerous obligations".
  - Source: [RCVS Standards and advice spring 2026 update](https://www.rcvs.org.uk/veterinary-professionals/conduct-and-guidance/resources-and-updates/standards-and-advice-spring-2026-update) (accessed 2026-10-18)
- **VetCT white paper (2023, older):** called for "proactive and pre-emptive regulation" of AI. Its survey found over a third of respondents had little understanding of AI and only 10% "comprehensive" knowledge. Respondents worried about clients "trusting AI over veterinary professionals" — [Vet Times, 2023](https://www.vettimes.com/news/business/digital/ai-rules-vital-to-build-trust-new-report-warns)
- **Theoretical risk:** a 2026 theoretical review flags "authority delegation" and automation bias in veterinary decision-making — [Eryol, Front Vet Sci, 2026-07-15](https://doi.org/10.3389/fvets.2026.1861384)

**Owner behaviour and risk (survey; sponsored)**
- **Survey basics:** Talker Research for Darwin's pet food, 2,000 owners, fieldwork 2026-04-22 to 04-28.
- **Usage:** 43% have used tools like ChatGPT for pet health or nutrition, averaging seven times a week. Topics: nutrition 55%, symptoms or illness 54%.
- **Trust:** 71% say vets are their most trusted source; 14% rely mainly on AI. When advice conflicts, 64% follow the vet and 12% follow the AI.
- **Behaviour change:** 59% changed care based on AI.
- **Side effects:** 30% say AI made them more worried; half sometimes feel unsure after researching online.
- **Accuracy:** only 11% name response accuracy as a top trust factor.
- Source: [Talker Research, 2026-08-31](https://talkerresearch.com/3-in-5-say-ai-recommendations-changed-how-they-care-for-their-pet/)

### Inferences
- **Calibrated triage:** the documented LLM failure mode in triage is over-triage, and owners notice and resent it ("every single time… go see the vet"). A best-in-class tool needs calibrated tiers with time windows and reasons, plus published sensitivity and over-triage rates. Pushing everything to "urgent" adds load to emergency clinics, as Wong et al. warn.
- **Robustness to wording:** answers change with small wording changes (Abani) and models hallucinate signalment (Vetster test). Structured intake (species, age, key red flags) before free text, and showing the facts the AI used, are sensible mitigations.
- **Images:** photo-based assessment such as pain or skin is not reliable in general chatbots (Ngai). Any image feature should be framed as "share with your vet", not as scoring.
- **Operations:** most real-world complaints are operational (licensing, prescriptions, billing, support). An EU site that does not prescribe avoids several of these. It must still give honest scope statements (what it cannot do, where) and frictionless cancellation if it sells memberships.
- **Owner behaviour:** heavy, frequent use of general chatbots for symptoms is the status quo the site competes with. Vet-reviewed answers with clear escalation are its value over ChatGPT.

### Gaps
- No lawsuits, class actions or regulator actions (FTC, state boards, ASA/CMA) against these companies were found. A targeted search could not be run because the web-search budget was exhausted, so this is not evidence of absence.
- Search snippets reported, but I did not open:
  - an RSPCA survey finding "10% of pet owners are routinely using AI";
  - a 2025 AAVSB white paper stating chatbots must not offer diagnoses or treatment plans to clients;
  - the RCVS/Digital Practice "Veterinary AI Transparency Alliance" draft framework (23 principles, consulted June–July 2026). Its BEVA news link redirected to an index page.
- The full JVIM handout numbers (diplomate accuracy ratings) were not retrieved; only the abstract was.
- Inter-veterinarian agreement in Wong et al. (kappa 0.49–0.66) appears only in a search snippet of the Sydney repository record, which returned HTTP 403.
- No peer-reviewed evaluation of a named commercial owner-facing pet symptom checker (Joii, Petriage, PetMD, Furbo, etc.) was found.

## 6. Features that appear to drive adoption and retention

### Takeaway
The features with the clearest adoption evidence are:
- free-at-point-of-use 24/7 access through a payer the owner already has (insurer, retailer membership, employer, own practice);
- very short time to a human (about 4-minute chat replies, about 10-minute video waits);
- reminders, records and booking tied to the owner's own practice (PetDesk alone has about 508k App Store ratings);
- memberships bundling unlimited consults with savings.

AI's role in adoption is so far evidenced only by vendor metrics: Joii's 12,000+ AI interactions a month and 4,700+ flagged emergencies, and Maven's 125,000 insights. 2026 launches emphasise pet-specific memory and baselines.

### Cited Findings
**Paid-by-someone-else distribution**
- **UK insurers:** FirstVet is free for 17 partner insurers' customers — [FirstVet pricing](https://firstvet.com/uk/pricing-information). Joii is unlimited for partner insurers — [App Store GB](https://apps.apple.com/gb/app/joii-pet-care/id1436958921). Waggel's AI triage has flagged ">4,700 potentially life-threatening emergencies" since July 2025 and issued ">400 emergency recommendations" in the month before publication — [Waggel, 2026-08-09](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies)
- **Walmart+:** includes Pawp's base membership — [Pawp Help Center, 2026-07-21](https://help.pawp.com/en/articles/10008059-how-does-pawp-s-emergency-protection-work-for-walmart-members)
- **Chewy:** offers free vet chat — [PetMD](https://www.petmd.com/)
- **Airvet:** distributed through employers, ">250,000 pet parents" — [App Store](https://apps.apple.com/us/app/airvet-for-pet-parents/id1448478595)

**Speed to a human**
- **Joii:** "24/7 vet chat – replies in ≅ 4mins" — [Joii homepage](https://www.joiipetcare.com/)
- **Waggel/Joii:** average virtual vet wait of about 10 minutes — [Waggel](https://www.waggel.co.uk/blog/post/ai-helps-fast-track-pet-emergencies)
- **Dutch:** "Get care with a 10-minute call" — [Dutch membership plans](https://www.dutch.com/pages/membership-plans)
- **Wait times as a churn driver:** Pawp and Dutch 1★ reviews cite no-shows and week-long waits — [Apple RSS, Pawp](https://itunes.apple.com/us/rss/customerreviews/page=1/id=1594794194/sortby=mostrecent/json); [Apple RSS, Dutch](https://itunes.apple.com/us/rss/customerreviews/page=1/id=6745529739/sortby=mostrecent/json)

**Practice-linked reminders and records**
- **PetDesk:** 4.86 from 507,690 App Store ratings; "over 12,000 veterinary practices" — [App Store](https://apps.apple.com/us/app/id631377773); [PetDesk](https://petdesk.com/)
- **IDEXX Vello:** reports a "5.4% increase in wellness visit revenue and a 8.2% increase in diagnostic revenue". One practice's fecal samples rose "from under five per week to more than five per day" after automating client communication — [Vello by IDEXX](https://software.idexx.com/vello) (vendor case data)
- **myVCA:** reminders plus 24/7 live chat, 4.83 (1,420, CA) — [App Store CA](https://apps.apple.com/ca/app/myvca/id1172429469)
- **The Pack by Zoetis:** records, medication logging and rewards, 4.88 (9,992) — [App Store](https://apps.apple.com/us/app/the-pack-by-zoetis/id1633459819)

**Memberships and loyalty**
- **Modern Animal:** described as a "high-retention membership model" with "over 100,000 member families"; Chewy expects a "15–20% uplift in net sales per active customer" for the vet network — [Chewy via Nasdaq, 2026-04-08](https://www.nasdaq.com/press-release/chewy-acquire-modern-animal-accelerating-evolution-fully-integrated-healthcare)
- **Petco (2023):** "existing Pals members who have unlocked 'perk' benefits… increase their Petco visits by 50% and spend 40% more". Vital Care members get app reminders and a "monthly wellness checklist" — [Petco via Nasdaq, 2023-01-30](https://www.nasdaq.com/press-release/petco-unifies-customer-memberships-under-vital-care-program-for-an-integrated)
- **Dutch scale claims:** "600k+ Dutch members" ([membership page](https://www.dutch.com/pages/membership-plans)) vs "900,000+ pet parents" ([homepage](https://www.dutch.com/))

**AI-specific engagement (vendor-reported)**
- **Vet-AI:** "12,000+ real-world interactions every month"; "465,000+ registered owners with a 95% satisfaction rating" — [VetClick, 2025-09-23](https://www.vetclick.com/news/vet-ais-proprietary-llm-outperforms-gemini-and-chatgpt-in-independent-veterinary-benchmarking-p11439.php)
- **Google Cloud case study:** an 8% reduction in vet consultation times thanks to triage — [Google Cloud](https://cloud.google.com/customers/vet-ai)
- **Maven:** "125,000 proactive health insights delivered to date", most often ear, skin and allergy changes — [Yahoo Finance, 2026-10-13](https://finance.yahoo.com/healthcare/articles/dog-parents-ask-ai-dogs-195300108.html)
- **PETKIT:** the app claims "over 6 million pet parents worldwide" — [App Store](https://apps.apple.com/us/app/id994053492). Kitbo adds AI Q&A over device data and vet-shareable health reports — [PETKIT, 2026-08-30](https://www.petkit.com/blogs/blog/kitbo-petkits-ai-powered-pet-health-assistant-for-smarter-pet-care)

**Personalisation and memory (2025–26)**
- **Joii:** plans long-term memory so the app can "remember a pet's entire care history" — [Google Cloud](https://cloud.google.com/customers/vet-ai)
- **Petcube:** builds advice from a pet profile and "Health Check" — [App Store](https://apps.apple.com/us/app/petcube/id720151500)
- **TriageTail:** stores case history to "bring the details with you to the vet" — [App Store](https://apps.apple.com/app/id6760662686)

**Owner requirements (literature)**
- A 2025 review screened 955 publications and extracted "10 requirements to mHealth applications for animal owners from 13 publications". It frames triage decision support ("how urgent their animal needs to be examined") as a key use — [Haase et al., BMC Vet Res, 2025-03-21](https://doi.org/10.1186/s12917-025-04658-3)

### Inferences
- **Distribution beats features:** adoption leaders win on who pays and how fast a human appears. An EU-first site should pursue insurer or practice partnerships, or bundle the AI with a quick route to a real vet (partner telehealth or the owner's own practice), rather than compete on AI features alone.
- **Retention features to copy:** pet profile and timeline, reminders (vaccines, parasites, meds), shareable visit summaries or pre-visit briefs, and follow-up check-ins after a triage episode. The evidence is mostly vendor data, but it is consistent across companies.
- **Validated triage as a moat:** no competitor can show independent proof that its triage changes outcomes. A site that publishes outcome follow-ups (e.g., what owners did and what the vet found) could differentiate on evidence rather than marketing claims.

### Gaps
- No independent (non-vendor) data on retention or churn for any product in scope was found.
- No public data was found on how often AI triage users convert to paid consults, or what share of flagged emergencies were confirmed by a vet. Waggel's 4,700 figure is unadjudicated.
- Google Play install counts were not collected.
