# AI documentation and assistant tools for veterinarians in Europe (focus DACH and Italy), state as of 18 October 2026

Research method note: every page cited below was opened on 18 Oct 2026, either with a web fetch or by downloading the page directly with curl and extracting the text. Vendor statements are labelled as vendor claims. Partway through, the shared web-search budget ran out. After that, only known URLs could be opened, and new vendors (especially Italian AI start-ups) could no longer be discovered by search. This limit is repeated in the Gaps sections. Dates in brackets are publication or "updated" dates where the page shows one. Otherwise the date is the fetch date, 18 Oct 2026.

## 1. Products and features: what DACH and Italian practices can buy today (input, outputs, languages, hosting, pricing, free tier)

### Takeaway
DACH has four vet-specific AI documentation products that can be bought now:
- Petleo.ai (DE), built into Vetera
- Curala (AT), standalone and browser-based
- ReportAssistant AIQ (Berlin), also sold as VetZ/Mars's "vetOS intelliVET ReportAssistant" inside easyVET
- Provet's native AI Scribe. Provet is Nordhealth's cloud PMS, and its AI Scribe does not support German.

Italy has one native-PMS AI scribe that works in Italian (Provet). Every other Italian PMS I checked (Smart Vet, Vetincloud) has no AI. Tandem Health has a veterinary offering, but its DACH and Italian PMS integrations are "Not Live". Every product found records audio or dictation. None is text-first. None advertises sentence-level links from the output back to the source, and none advertises flags for missing required information.

### Cited Findings

#### Provet / Nordhealth (Finland; cloud PMS with native AI)
- Nordhealth's Q4 2025 investor presentation (3 Mar 2026) says it "Launched Provet Intelligence Q4: AI Scribe, AI Discharge Notes, AI Patient Histories". It also reports "Scaled to 13,500 veterinarians on Provet". — [Nordhealth Q4 2025 presentation (PDF)](https://mb.cision.com/Public/20636/4315670/90c4a8ad72cc7291.pdf)
- The same deck describes standalone AI scribes as "Feature, not platform … No workflow ownership → must plug into the PMS". Its 0–12-month roadmap item is "Native AI Scribe auto-generates SOAP notes + smart charge capture (catching missed billables) from voice". — [Nordhealth Q4 2025 presentation (PDF)](https://mb.cision.com/Public/20636/4315670/90c4a8ad72cc7291.pdf)
- German trade press dates the start of Nordhealth's AI Scribe for Provet Cloud to November 2025: "Nordhealth, Eigentümer von Vetera, bietet seit November 2025 einen AI Scribe für Provet Cloud an". — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)
- On 9 Jul 2026 Provet launched "AI Agents":
  - The "Clinical AI Agent, using Provet's AI Scribe, captures every measurement, diagnosis, medication, and charge spoken during the consultation."
  - "Ask Provet" answers operational questions.
  - "Provet MCP (coming soon)" was announced in the same release.
  - Scale claimed: more than 55,000 veterinary professionals, 45 countries, more than 3,000 clinics.
  — [Provet/Nordhealth press release, 9 Jul 2026](https://news.cision.com/nordhealth-oy/r/provet-launches-the-first-all-in-one-veterinary-pims-built-for-ai-agents,c4366240)
- By the Capital Markets Day (18 Aug 2026), Nordhealth said six agents were live: AI Scribe (Vet and Therapy), AI Billing ("1st to market", Vet), AI Reporting/MCP, Patient history, Discharge notes, and AI Form filler (Therapy). It also said "Scribe, automated billing and MCP are live today" in UK clinics. — [Nordhealth CMD / Q2 2026 presentation (PDF)](https://mb.cision.com/Public/20636/4384407/971605e4f2a0e9e0.pdf)
- Input is audio only (vendor). The blog (first published Sep 2025, updated 24 Jul 2026) says:
  - AI Scribe "listens to the consultation" and organises it into SOAP, narrative or custom templates.
  - Recording can be paused and resumed within 60 minutes.
  - Generation takes about 10–20 s for a 15-minute consult.
  - "The AI draft is never final until reviewed and edited by a veterinarian".
  - The summary and transcript are kept for 24 h unless added to the record.
  - Typing is presented as the task the tool replaces, not as an input.
  — [Provet blog, updated 24 Jul 2026](https://provet.com/blog/8-steps-to-get-started-with-ai-scribe-for-veterinarians)
- Mobile app: the phone records and the desktop consultation receives the transcript. The feature "is currently behind a feature flag and may not be available in all environments". "Transcriptions are stored on the mobile device for 24 hours". Farm and ambulatory vets can dictate throughout a visit. — [Provet help centre: AI Scribe in the mobile app](https://ticketportal.provetcloud.com/hc/en-gb/articles/26497043877020)
- **Languages: "English, Spanish, Swedish, Norwegian, Danish, Finnish, and Italian."** German is not listed (FAQ, page fetched 18 Oct 2026). — [Provet AI product page](https://www.provet.com/product/provet-ai); same list on the [Italian page](https://www.provet.com/it/prodotto/provet-ia)
- Provet has no German-language website: provet.com/de returned 404 on 18 Oct 2026. The Italian site is live, markets "Strumenti di AI nativi", and quotes a vet: "L'agente AI clinico mi fa risparmiare 3-5 minuti in ogni consulto". — [Provet Italia homepage](https://www.provet.com/it)
- Pricing (no date on page; no EUR shown): "Clinical Agent (AI scribe)" costs $40 or £30 per seat per month for unlimited use. The PMS itself:
  - Core: $99 per vet per month plus a $249 platform fee (GBP £139 + £139).
  - Pro: $129 plus $299 (GBP £159 + £199).
  — [Provet pricing](https://www.provet.com/pricing)
- Free tier (help centre, updated 19 Aug 2026): "30 minutes of dictation per user per month". AI Discharge Instructions and AI Patient History are unlimited without a seat. Seats are billed monthly, and local currency appears on the subscription page. — [Provet help centre: Clinical AI Pricing and Subscription](https://ticketportal.provetcloud.com/hc/en-gb/articles/25075068104476)

#### Petleo.ai (Petleo GmbH, Germany): AI documentation built into Vetera
- Input: "Starten Sie die Aufnahme im Behandlungsraum oder diktieren Sie im Nachgang – auch nachträglich, am Computer oder als App". So it takes a consultation recording or a dictation. Typing is not offered as an input.
- Output: structured notes in the practice's own templates, written into the Vetera patient record, plus an aftercare summary sent digitally to the owner (no owner account needed). "Jede Dokumentation lesen und geben Sie selbst frei, bevor sie in die Patientenakte übernommen wird."
- Price: "ab 79 € im Monat". Cancellable at any time with three months' notice, "inklusive Installation und Produktschulung".
- Above: [Petleo.ai product page](https://vet.petleo.net/en/petleo-ai)
- Price list: "Patientenaufnahme" €39, "Terminbuchung + Patientenaufnahme" €59 and "KI-Dokumentation" €79 per month. "Alle Preise netto pro Praxis und Monat", plus a one-off setup fee. No free trial; a 30-minute demo is offered. — [Petleo prices](https://vet.petleo.net/preise)
- Integrations named: Vetera, Vet7well, TPV-Systeme, Provet Cloud and VetStar. For other systems: "Ihre Praxissoftware ist nicht dabei? Dann ist die Petleo.ai Bubble Ihr Weg." — [Petleo.ai product page](https://vet.petleo.net/en/petleo-ai). The practices page calls "Bubble" a documentation assistant for "jede Praxissoftware". — [Petleo for practices](https://vet.petleo.net/en/tierarztpraxen)
- Trade press describes the Vetera workflow in five steps: start, choose template, record, AI creates the note in the Patientenkartei, vet corrects and releases. For other software Petleo offers a "Fenstermodus", a floating window from which the vet copies text. — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)
- Petleo's documented Vetera interface ("geprüfte Schnittstelle", "in wenigen Tagen einsatzbereit") covers appointments, master data, intake forms and consents flowing into the Vetera record. That page does not describe the AI-documentation data flow. — [Petleo × Vetera](https://vet.petleo.net/en/petleo-und-vetera)
- Petleo's blog lists a Petleo.ai article dated 20 Aug 2026 and partner pages "Petleo.ai × Vetera" and "Petleo.ai × VetStar". — [Petleo blog index](https://vet.petleo.net/en/blog/ki-in-der-tiermedizin---petleo-ist-vorreiter)

#### Curala (Gratwerk GmbH, Innsbruck, Austria): standalone, browser-based, multi-profession
- Input:
  - Live recording in the browser on PC, tablet or phone, with no installation.
  - Recording of online calls (Zoom, Teams, Meet), "Nur in Chrome-basierten Browsern am Computer".
  - Dictation after the treatment.
  - Typing is used for editing, not as an input.
- Outputs:
  - Befundaufzeichnung (sections: Anamnese, Untersuchungsbefund, Weiterführende Diagnostik, (Verdachts-)Diagnose, Therapie und Empfehlungen)
  - "Bericht für Tierhalter:innen"
  - "Arztbrief für Tierhalter:in"
  - Verlauf
  - Custom templates (SOAP possible)
  - Export by copy, DOCX, PDF or Markdown
- Languages: "Rund 60 Sprachen und Dialekte" with automatic detection and live translation into German. Translation goes into German, not into the owner's language. Speaker separation is "Beta".
- Above: [Curala for vet practices](https://www.curala.at/ki-dokumentation-tierarztpraxis)
- Pricing (EUR net, B2B only; the default view shows annual billing):
  - Free: €0, "10 Konsultationen / Monat", permanently, no card. The first 30 days are unrestricted.
  - Basic: €35 per user per month billed annually (€420/yr, −10%). 50 consultations, then €0.79 each.
  - Professional: €52 (€624/yr, −12%). 100 consultations, then €0.69 each.
  - Unlimited: €85 (€1,020/yr, −14%). Fair use up to 1,000 per month.
  - Paid tiers include a "Gratis-Mikrofon" and "AVV & Datenschutzerklärung inkl.".
  - Monthly-billed prices were not captured.
  — [Curala prices](https://www.curala.at/preise)
- Curala also targets human medicine, psychotherapy and therapy professions. It won the MutMacher Award 2026 ("Neustart"). — [Curala homepage](https://www.curala.at/)

#### ReportAssistant AIQ GmbH (Berlin) and VetZ/Mars "vetOS intelliVET ReportAssistant"
- ReportAssistant markets itself as "Das Betriebssystem für KI in der Tierarztpraxis": "in Deutschland gehostet", "Bei über 300 Tierarztpraxen und Kliniken im Einsatz". It was founded by veterinarian Dr. med. vet. Hannah-Sophie Braun with an AI developer. An AI phone assistant has a waiting list. — [ReportAssistant homepage](https://reportassistant.de/); [About us](https://reportassistant.de/ueber-uns/)
- Input: press record and speak freely on any device. Recording works offline, and processing runs once the device is back online.
- Output: "allgemeine SOAP oder genau passend zu Ihrem Untersuchungsgang". Use cases listed: OP-Berichte, Narkose- und Stationsprotokolle, owner conversations, and farm visits.
- Integration: "Verfügbar auch direkt in easyVET. Integrierbar in alle Praxismanagementsysteme über die offene vetOS API", or copy-paste into any PMS.
- Pricing: none published; a demo is offered.
- Above: [ReportAssistant KI-Dokumentation](https://reportassistant.de/ki-dokumentation/)
- Customer testimonials (vendor-selected): TION, "mindestens 50 %" less documentation; a cardiology referral practice says time per report "messbar halbiert". — [ReportAssistant homepage](https://reportassistant.de/)
- VetZ sells the same capability as "vetOS intelliVET ReportAssistant". The vet records the conversation, examination or findings and picks a document type. "Überweisungen, Besitzerbriefe und Rücküberweisungen entstehen per Klick … Ohne Copy & Paste." The page footer reads "vetOS™ ist eine Marke der VetZ GmbH, Tochtergesellschaft von Mars, Inc." — [vetOS intelliVET ReportAssistant](https://www.vetos.vet/intellivet-reportassistant/)
- Trade press says the intelliVET ReportAssistant produces a report, a referral letter and an owner letter "in sieben Sprachen, darunter Deutsch, Englisch und Französisch". It is available in Germany, Austria and Switzerland. ReportAssistant AIQ claims its technology captures "19 von 20 Angaben richtig" (vendor claim). — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)

#### Tandem Health (Sweden): veterinary use exists, but DACH and Italy integrations are not live
- On 9 Feb 2026 Tandem announced a partnership with VetFamily, a network of more than 10,000 clinics in eleven countries (countries not named). The initial rollout is Sweden, with more than 300 clinics. The tool captures the vet–owner conversation and drafts a note. "Audio is processed in real time and deleted after transcription". The clinician "reviews, edits, and approves everything". — [Tandem news, 9 Feb 2026](https://tandemhealth.ai/resources/news/over-10-000-veterinary-clinics-globally-one-shared-challenge-with-documentation)
- Integration pages (all dated 16 Oct 2026):
  - Vetera (Germany): "Integration status: Not Live", FAQ answer "No, not yet". — [Tandem × Vetera](https://tandemhealth.ai/product/integrations/vetera)
  - easyVET/VetZ (Germany primary; Austria and Switzerland): Not Live. — [Tandem × easyVET](https://tandemhealth.ai/product/integrations/easyvet)
  - dr.veto (France since 2012, Italy since 2015): Not Live. — [Tandem × dr.veto](https://tandemhealth.ai/product/integrations/dr-veto)
  - Gestorvet (Spain, more than 4,000 users): Live. — [Tandem × Gestorvet](https://tandemhealth.ai/product/integrations/gestorvet)
- Tandem says building an integration "typically takes anywhere from a few hours to a few weeks, depending on the systems provider". — [Tandem × Vetera](https://tandemhealth.ai/product/integrations/vetera)
- The /solutions/veterinary page linked from these pages returned HTTP 404 on 18 Oct 2026. No veterinary pricing or language list is published. On the human-medicine side, Tandem announced on 21 May 2026 that its scribe is "the first in Europe to reach EU MDR Class IIa", entered Italy via Humanitas on 9 Apr 2026, and raised $100M on 14 Sep 2026. — [Tandem news list](https://www.tandemhealth.ai/fr/news)

#### IDEXX (Animana in Europe; CoVet acquisition)
- The Animana page says "AI capabilities are built into Animana to save you time, from quick help when you need it to support during consultations". No speech-input details are given. — [IDEXX Animana (UK)](https://software.idexx.co.uk/software-animana/)
- On 16 Sep 2026 IDEXX acquired CoVetAI ("AI-native ambient listening"). CoVet is "Trusted by tens of thousands of users across North America, Europe, Australia and New Zealand". IDEXX will "continue to support other ambient scribe solutions and third-party integrations", and CoVet will keep integrating with non-IDEXX PMS. — [IDEXX release, Business Wire text via Finviz](https://finviz.com/news/392529/idexx-laboratories-acquires-covetai-to-advance-veterinary-workflow-intelligence). The Business Wire original returned 403.
- CoVet's own site: "used daily in practices across North America, Europe, and Australia", and claims "ISO 27001, SOC 2 Type 2, and GDPR". — [CoVet homepage](https://co.vet/)

#### Digitail (US/RO; PMS with Tails AI)
- A July 2024 blog post (older) describes Tails AI dictation in "multiple languages", a 20-minute recording limit, and discharge or education material "in the provider's or client's preferred language". — [Digitail blog, 9 Jul 2024](https://digitail.com/blog/digitail-introduces-upgrades-to-its-native-ai-assistant-tails-ai/)
- The current plans page lists Tails AI Scribe, AI Discharge Notes, Voice to Invoice and more, plus an "Open API & … 40+ integrations". Prices are not shown, there is no EUR, and digitail.com/de redirects to the English site. — [Digitail plans](https://digitail.com/plans/)

#### Italy: PMS without AI, and no native-Italian AI scribe found
- Smart Vet is an Italian cloud PMS (also sold in ES, in Italian for CH, and in LatAm):
  - Licence "€168*/12 Mesi" excluding VAT
  - REV issued "in meno di un minuto"
  - Sistema Tessera Sanitaria and e-invoicing
  - No AI features on the homepage
  — [Smart Vet](https://www.smartvet.it/)
- Smart Vet's Capterra listing claims "1 veterinario su 5 in Italia utilizza Smart Vet" (vendor claim). — [Capterra Italia: Smart Vet](https://www.capterra.it/software/193134/smart-vet)
- Vetincloud is "completamente integrato con … ricetta elettronica, Sistema TS e fatturazione elettronica"; AI is not mentioned. — [Capterra Italia: Vetincloud](https://www.capterra.it/software/161509/vet-in-cloud)
- Capterra's Italian veterinary directory lists mostly US products plus Adiuvet, Smart Vet, Provet and "Gestionale veterinario". — [Capterra Italia directory](https://www.capterra.it/directory/30617/veterinary/software)

#### US-headquartered scribes: European availability and languages only
- ScribbleVet: "Scribble can understand and write in English, Spanish, French, & other languages." — [ScribbleVet](https://www.scribblevet.com/)
- A July 2026 German "top 13" aggregator gives only USD prices and no EU-hosting data for any tool. Its only GDPR mention is VetRec ("SOC 2 Type II und DSGVO-konformer Datenverarbeitung"). This is a low-quality source. — [rework.com DE list, updated 17 Jul 2026](https://resources.rework.com/de/tools/ai-tools/best-ai-tools-for-veterinary-clinics-2026)

### Inferences
- **Nobody in this market is text-first.** Petleo.ai, Curala, ReportAssistant/intelliVET, Provet AI Scribe and Tandem all start from a microphone (conversation or dictation). Curala's dictation mode comes closest to "nothing the vet didn't say": it outputs "genau das …, was du gesagt hast, geglättet und lesbar, ohne inhaltliche Umformulierung" ([Curala for vets](https://www.curala.at/ki-dokumentation-tierarztpraxis)). A typed-notes-in, structured-record-out tool would be alone in its category in DACH and Italy.
- **German coverage of AI scribes inside a PMS is thin.**
  - Provet's scribe does not support German.
  - The Tandem integrations with Vetera and easyVET are not live.
  - That leaves Petleo (Vetera-centred) and ReportAssistant/intelliVET (easyVET/vetOS-centred, Mars-owned).
  - Curala is standalone, with copy/paste only.
- **Italy has close to no AI scribe of its own.** The only Italian-language native AI scribe found is Provet's. The largest local PMS (Smart Vet, which claims 20% of Italian vets, at €168 per year) has no AI.
- **Pricing anchors for a new entrant:**
  - Curala: €35–85 per user per month (annual billing), with a permanent free tier of 10 consultations.
  - Petleo: €79+ per practice per month.
  - Provet: $40/£30 per seat with 30 free minutes.
  - Nordhealth models AI at "€120" per location per month at full attach (see Q5).
- Owner letters in the owner's language are rare. Curala translates into German. intelliVET claims seven output languages. Digitail (2024) offered the client's preferred language. No DACH or Italian vendor advertises an owner letter in the owner's own language as a core feature.

### Gaps
- Curala, Petleo, ReportAssistant, vetOS and Tandem publish no figures for accuracy or hallucination rates.
- Not found in the search window (before the search budget ran out): any product called Vetsy, Vetyvet, Scribbie, Dictavet or VetsGo as a European vet scribe. Searches turned up only a UK telehealth "Vetsy" and a Spanish "Vetsmate", neither verified. Not found: a FirstVet internal AI tool, a German-language Dragon/Nuance veterinary product, or AI features in VET7.well, dr.veto, VetStar, TPV, ANIMALoffice, Vetinf, VetSet, WinVet.net, inBehandlung or Diana Software.
- Search ran out before I could find Italian-native AI documentation start-ups or "Assistente IA" features from Italian vendors (GestiVet, Veterinaria Facile, Fenice, Vetsoft and others). This gap should be closed with fresh searches.
- Not verified: VetRec's German-language support, and the European language coverage of Digitail and CoVet (beyond "Europe" usage claims).
- Tandem: veterinary pricing, the VetFamily country list (whether it includes DE, AT, CH or IT), and veterinary languages are not public.
- Group tools: IVC Evidensia appears as a Provet customer (testimonial on [Provet Italia](https://www.provet.com/it)). No public description found of group-wide AI scribes at AniCura, Evidensia/IVC or other Mars clinics in DACH or Italy.

## 2. Compliance, accuracy and recording-consent claims (GDPR/DSGVO, AVV/DPA, server location, no-training, ISO, MDR/AI Act; § 201 StGB, Austria, Swiss nDSG)

### Takeaway
EU-only hosting is claimed by the small DACH vendors (Curala: Innsbruck plus EU LLM servers; Petleo: Germany and France; ReportAssistant: Germany). The biggest native player, Provet, uses US-headquartered LLM sub-processors (Anthropic, OpenAI) and UK speech-to-text. ReportAssistant's privacy policy allows anonymised data to be used for AI training and transferred outside the EEA. Every vendor relies on the vet reviewing the draft. No vendor publishes accuracy metrics. Recording consent is a real criminal-law issue in all three DACH countries, with Switzerland the strictest. Vet AI is outside the MDR, which covers human medical devices only.

### Cited Findings

#### Vendor compliance claims
- **Curala:**
  - "Die Speicherung erfolgt in Innsbruck, die Verarbeitung durch Sprachmodelle auf Servern innerhalb der EU".
  - "Audio wird in Echtzeit verarbeitet und nicht gespeichert (Zero Retention)".
  - "Gespräche werden nicht zum Trainieren von KI-Modellen verwendet" (also binding on its service providers).
  - AVV included free of charge; sub-processor list on request to datenschutz@curala.at.
  - LLM providers not named; no ISO or AI Act statement.
  — [Curala Daten & Sicherheit](https://www.curala.at/daten-und-sicherheit)
- **Petleo.ai:**
  - "Gespeichert wird ausschließlich in Deutschland und Frankreich"
  - "einwilligungsbasiert nach Art. 6 Abs. 1 lit. a DSGVO"
  - "Auftragsverarbeitung nach Art. 4 Nr. 8 DSGVO"
  - "Aufnahmen werden nicht zum Training von KI genutzt"
  - Sub-processors and retention not disclosed.
  — [Petleo.ai](https://vet.petleo.net/en/petleo-ai)
- **ReportAssistant:**
  - Marketing: "Alle Daten werden auf deutschen Servern gehostet". — [ReportAssistant KI-Dokumentation](https://reportassistant.de/ki-dokumentation/)
  - Its privacy policy is broader. Data are stored "grundsätzlich auf Servern innerhalb des EWR" and "vor Übermittlung an Dienstleister bzw. Server außerhalb des EWR anonymisiert". It also lists as a processing purpose the "Anonymisierung Ihrer personenbezogenen Daten, um die anonymisierten Daten … zu nutzen, um die KI zu trainieren". — [ReportAssistant Datenschutz](https://reportassistant.de/datenschutz/)
- **Provet:**
  - ISO 27001:2022 (via Nordhealth Finland Oy) and "Seguiamo gli standard GDPR ovunque, non solo nell'UE". — [Provet sicurezza dati](https://www.provet.com/it/prodotto/sicurezza-dati)
  - Sub-processors:
    - Amazon Web Services EMEA (main data, EU)
    - "Anthropic (Claude) … AI language models … USA / EU"
    - "OpenAI Ireland … EU (if EU data residency is enabled for a given project) United States (if EU residency is not enabled; SCCs apply)"
    - "Speechmatics … speech-to-text … Primary processing in the UK"
    — [Provet third-party data processors](https://www.provet.com/legal/third-party-data-processors)
  - The DPA grants Nordhealth a licence to compile anonymised, aggregated customer data for benchmarking and reports. — [Provet data processing terms (IT)](https://www.provet.com/it/legale/termini-per-il-trattamento-dei-dati)
- **Provet's regulatory position:** "AI Scribe, AI Actions, Ask Provet, Provet MCP – sono strumenti di documentazione, analisi e flusso di lavoro. Non formulano diagnosi cliniche". It promises to adapt "se la normativa dell'UE si estenderà fino a coprire l'IA diagnostica veterinaria". — [Provet MCP blog (IT)](https://www.provet.com/it/blog/provet-mcp-dati-clinica-ia)
- **Tandem (vet):** "Audio is processed in real time and deleted after transcription. No complete audio recordings are stored. Clinical notes are not linked to patient identities." — [Tandem news, 9 Feb 2026](https://tandemhealth.ai/resources/news/over-10-000-veterinary-clinics-globally-one-shared-challenge-with-documentation)
- **CoVet:** claims ISO 27001, SOC 2 Type 2 and GDPR. — [CoVet](https://co.vet/)

#### Accuracy handling (vendor statements and evidence)
- Curala:
  - The interface warns "Curala kann Fehler machen".
  - The FAQ says Curala "ist ausdrücklich darauf ausgelegt, nichts zu ergänzen. Jede Vorlage weist die KI an, ausschließlich aus dem Transkript zu arbeiten, und vor der Ausgabe wird der Entwurf noch einmal mit dem Transkript abgeglichen". It also says "Ganz ausschließen lässt sich ein Fehler bei keiner KI".
  - One veterinarian testimonial calls the reports "fast immer korrekt, folgerichtig und komplett".
  — [Curala for vets](https://www.curala.at/ki-dokumentation-tierarztpraxis)
- Provet: claims it "captures terminology accurately" but warns that numeric errors (misheard digits) are common. "Nothing is stored permanently without your approval." — [Provet blog](https://provet.com/blog/8-steps-to-get-started-with-ai-scribe-for-veterinarians). Also: "Always review AI responses before making a clinical decision." — [Provet help centre](https://ticketportal.provetcloud.com/hc/en-gb/articles/26497043877020)
- Independent evidence, as summarised in German trade press:
  - "Eine begutachtete Studie zur Zeitersparnis oder Fehlerquote mithörender KI in Tierarztpraxen existiert bisher nicht (Stand September 2026)".
  - A March 2026 audit in Frontiers in Veterinary Science (Brundage 2026) of 71 North American veterinary AI products found that only about 2 in 100 generative-AI vendors had a peer-reviewed efficacy study, and nearly two-thirds published no accuracy metric at all.
  - The AAVSB (March 2025) names three error types: invented content, carry-over from earlier cases, and wrong post-operative instructions. It recommends labelling AI-generated entries.
  - A human-medicine study found invented content in nearly a third of AI notes, against a fifth of physician notes (Palm et al. 2025).
  — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)

#### Recording consent and data-protection law
- **Germany, § 201 StGB:** "Mit Freiheitsstrafe bis zu drei Jahren oder mit Geldstrafe wird bestraft, wer unbefugt … das nichtöffentlich gesprochene Wort eines anderen auf einen Tonträger aufnimmt". Attempt is also punishable. — [§ 201 StGB](https://www.gesetze-im-internet.de/stgb/__201.html)
- **German trade-press guidance:**
  - "Die Praxis muss deshalb vor dem Aufnahmestart die Zustimmung des Tierhalters einholen". Petleo collects consent "per QR-Code" and notes it in the record.
  - The KBV's "Praxiswissen KI" (2025) treats patient consent as a precondition for conversation-recording systems.
  - An Art. 28 GDPR AVV is "in der Regel" needed.
  - Processing locations and any third-country providers should be checked.
  - The BTK provides templates for consent, privacy notices and the record of processing activities.
  — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)
- **Real clinic practice in Germany:** Tierklinik Dr. Trillig's owner form (PDF dated 7 Apr 2026) discloses "KI-gestützte Module, die … Audio-, Text- und Bilddaten analysieren". It says owner data or chip numbers may be "an die KI übermittelt", that the intermediate data are "spätestens nach 48 Stunden automatisch gelöscht", and that providers act under Art. 28. The owner ticks a box: "Ich habe die vorstehenden Informationen zur auditiven Dokumentation … zur Kenntnis genommen und verstanden". — [Tierklinik Trillig AGB/DSGVO (PDF)](https://www.tierklinik-trillig.de/wp-content/uploads/2026/04/2.-AGB-DSGVO.pdf)
- **Vendor consent positions:**
  - Curala: tell the owner before the treatment; the owner signs a consent at reception for "mitlaufende Dokumentation". "Die Stimme und die Angaben der Halter:innen sind personenbezogene Daten". — [Curala for vets](https://www.curala.at/ki-dokumentation-tierarztpraxis)
  - ReportAssistant: "vor der Aufnahme eine klare Einwilligung der Tierhalter*innen". — [ReportAssistant](https://reportassistant.de/ki-dokumentation/)
  - Provet: has no built-in consent step. Clinics should follow local law and their professional body; Provet suggests a consent script, signage and wording in appointment reminders. — [Provet blog](https://provet.com/blog/8-steps-to-get-started-with-ai-scribe-for-veterinarians)
- **Austria, § 120 StGB:**
  - (1) Using a recording device to learn "von einer nicht öffentlichen und nicht zu seiner Kenntnisnahme bestimmten Äußerung eines anderen" carries up to 1 year or 720 day-fines.
  - (2) It is equally punishable to make the recording of a non-public utterance accessible to a third party "ohne Einverständnis des Sprechenden".
  - Prosecution only with the victim's authorisation.
  — [RIS § 120 StGB](https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10002296&Paragraf=120)
- **Switzerland, Art. 179ter StGB** (version of 1 Oct 2026): "Wer als Gesprächsteilnehmer ein nichtöffentliches Gespräch, ohne die Einwilligung der andern daran Beteiligten, auf einen Tonträger aufnimmt … wird, auf Antrag, mit Freiheitsstrafe bis zu einem Jahr oder Geldstrafe bestraft". — [Swiss StGB (Fedlex)](https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/54/757_781_799/20261001/de/html/fedlex-data-admin-ch-eli-cc-54-757_781_799-20261001-de-html.html)
- **Swiss nDSG** (status 7 Jul 2025):
  - Art. 9 allows processors only if the controller ensures data security. Sub-processing needs prior approval.
  - Art. 16 restricts transfers abroad to adequate countries or those with safeguards.
  - Art. 19 sets the duty to inform.
  - Art. 61 fines private persons up to CHF 250,000 for intentional breaches, including transfers abroad without safeguards or using a processor without the Art. 9 conditions.
  - Art. 62 covers breaches of professional secrecy.
  — [nDSG (Fedlex)](https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2022/491/20250707/de/html/fedlex-data-admin-ch-eli-cc-2022-491-20250707-de-html-1.html)

#### AI Act, MDR, Italian AI decree
- **EU AI Act Art. 50:** providers of AI systems "intended to interact directly with natural persons" must ensure people are informed. Generative systems must mark synthetic text, audio and image output "in a machine-readable format". Applies from 2 Aug 2026. — [AI Act Art. 50](https://artificialintelligenceact.eu/article/50/)
- **AI Act Art. 4:** "Providers and deployers of AI systems shall take measures to support the development of AI literacy of their staff". — [AI Act Art. 4](https://artificialintelligenceact.eu/article/4/)
- **MDR:** "'medical device' means any instrument, apparatus, appliance, software … intended by the manufacturer to be used … for human beings". Veterinary documentation software therefore falls outside the MDR, while human scribes such as Tandem's go for Class IIa. — [MDR 2017/745 (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0745); [Tandem news list](https://www.tandemhealth.ai/fr/news)
- **Italy, D.lgs. 7 ottobre 2026, n. 179** (GU 8 Oct 2026; in force 23 Oct 2026):
  - Adapts Italian law to the AI Act.
  - Art. 51 reserves a share of the three-yearly ECM training obligation for AI. The share is to be fixed within 6 months, i.e. by 23 Apr 2027.
  - Art. 47 adds AI literacy for professional orders.
  - AgID is the notifying authority and ACN the market-surveillance authority.
  - Fines go up to €35M or 7% for prohibited practices.
  — [Vet33, 14 Oct 2026](https://www.vet33.it/attivita-professionale/4461/intelligenza-artificiale-nuove-regole-dal-23-ottobre-cosa-cambia-per-i-veterinari.html)
- FNOVI comments on the decree: "la responsabilità professionale non può essere delegata o trasferita a un sistema automatizzato". — [FNOVI, 14 Oct 2026](https://fnovi.it/node/52102)

### Inferences
- **"EU-hosted" is a real point of difference against Provet.** Provet's LLMs (Anthropic, OpenAI) are US-headquartered, its EU residency is conditional, and its speech-to-text runs in the UK. Against Curala, Petleo and ReportAssistant the claim is shared. There, the stronger levers are no audio at all, no training, and a named sub-processor list. ReportAssistant's training on anonymised data is a contrast point.
- **No microphone removes the consent problem.** All the cited laws (§ 201 StGB, § 120 öStGB, Art. 179ter chStGB) target audio recording. A text-first tool sidesteps the consent step, the QR-code workflow and the reception forms that competitors and clinics (Trillig) need. Swiss Art. 179ter even criminalises a participant recording without consent. Whether passing audio to a cloud processor counts as "making accessible to a third party" under § 120(2) öStGB is a legal question for counsel; this is not a legal conclusion.
- **There is no accuracy evidence base.** As of Sep 2026 there is no peer-reviewed vet evidence, and two-thirds of vendors publish no accuracy metric. A tool that links each sentence to its source and refuses to add content would answer the AAVSB's named error types (invented content, carry-over) directly. It would also support labelling AI entries, which AAVSB recommends.
- **"Adds nothing" is not unique; showing the source is.** Curala already claims it is "ausdrücklich darauf ausgelegt, nichts zu ergänzen" and re-checks drafts against the transcript. So "adds nothing" alone does not set a product apart. No vendor page I read offers sentence-level provenance the vet can see and click through to the source. Nor does any offer flags for missing required fields.
- **Transparency duties apply.** AI Act Art. 50 (from Aug 2026) and Italy's D.lgs. 179/2026 make transparency and AI literacy a live topic for vets in Q4 2026. An "AI-assisted, vet-approved" label plus an audit trail fits the new duties.

### Gaps
- Not checked: the official text of D.lgs. 179/2026 or Italy's Legge 132/2025. The details above rely on Vet33 and FNOVI summaries.
- Swiss FDPIC (EDÖB) and Austrian DSB guidance specific to AI scribes was not found. Swiss and Austrian vet-chamber positions on recording are unknown.
- Hosting and sub-processors are not published for vetOS/intelliVET, Petleo (LLM vendor) or Tandem's vet product.
- Not opened: the original BTK Musterberufsordnung, the KBV "Praxiswissen KI" and the Frontiers/Brundage audit. They are cited only via Vetline.

## 3. Country-specific documentation: TÄHAV, GOT, REV, EU pet passport, Swiss TAMV

### Takeaway
The rules are concrete and recently changed. Germany's TÄHAV was reissued and has applied since 1 Jan 2025. GOT 2022 sets minimum invoice contents. Italy's REV is a national web-service system. Swiss TAMV requires dispensing records and IS ABV antibiotic reporting. PMS vendors (easyVET, Smart Vet, Vetincloud) handle these as PMS functions. No AI documentation vendor I checked says it drafts TÄHAV prescriptions or records, GOT positions, REV drafts, passport vaccination entries or TAMV records from the consultation.

### Cited Findings
- **TÄHAV (new version) in force 1 Jan 2025.** It replaces the 2009 version. — [TÄHAV § 21](https://www.gesetze-im-internet.de/t_hav_2025/__21.html); table of contents (§ 13 Antibiogrammpflicht, § 15 Dokumentation über Erwerb, Abgabe und Anwendung, § 16 Allgemeine Dokumentationspflichten, § 17 Übermittlung an den Tierhalter): [TÄHAV index](https://www.gesetze-im-internet.de/t_hav_2025/index.html)
- **TÄHAV § 15:**
  - Food-producing animals: for both Abgabe and Anwendung, the vet must "unverzüglich eine tierärztliche Verschreibung nach Artikel 105 Absatz 5 der Verordnung (EU) 2019/6" produce, which "dient gleichzeitig als tierärztliche Behandlungsanweisung nach § 44 Absatz 2 des Tierarzneimittelgesetzes".
  - Non-food animals: a Verschreibung is required when prescription-only medicines are dispensed.
  - Proof of Abgabe and Anwendung means "Aufzeichnungen im Tagebuch der Praxis oder in der Patientenkartei".
  — [TÄHAV § 15](https://www.gesetze-im-internet.de/t_hav_2025/__15.html)
- **TÄHAV § 16:** electronic records are allowed, but they must stay readable for the whole retention period and "unveränderlich". — [TÄHAV § 16](https://www.gesetze-im-internet.de/t_hav_2025/__16.html)
- **TÄHAV § 17:** the prescription goes to the owner on paper or electronically, with verifiable authenticity, and must carry "Nicht zur Vorlage in der Apotheke bestimmt!". — [TÄHAV § 17](https://www.gesetze-im-internet.de/t_hav_2025/__17.html)
- **TÄHAV § 13 Antibiogrammpflicht:**
  - Also covers single dogs, cats and horses when the vet re-purposes a drug under Art. 112(1)(a,b) of Reg. 2019/6, or uses 3rd/4th-generation cephalosporins, fluoroquinolones or colistin.
  - If no antibiogram is made, a Nachweis with the reasons is required.
  — [TÄHAV § 13](https://www.gesetze-im-internet.de/t_hav_2025/__13.html)
- **GOT 2022** (in force 22 Nov 2022). An invoice must contain at least:
  - the date of the service
  - the Tierart
  - "die Diagnose oder den Grund der Konsultation"
  - each service with its GOT item number
  - the amount
  - VAT
  — [GOT § 7](https://www.gesetze-im-internet.de/got_2022/__7.html); [GOT § 12](https://www.gesetze-im-internet.de/got_2022/__12.html)
- **GOT emergency service:** fees ×2 up to ×4, plus a €50 "Notdienstgebühr". — [GOT § 4](https://www.gesetze-im-internet.de/got_2022/__4.html)
- **Italy, REV:**
  - Replaces paper prescriptions (ricetta rossa, bianca ripetibile and non ripetibile, medicated feed). Introduced by legge 20 novembre 2017, n. 167.
  - Includes the type "Prescrizione Veterinaria per PET ed equidi NDPA".
  - Each prescription has a PIN; the system includes a Registro Elettronico dei Trattamenti.
  - Narcotics stay on paper.
  - Run by the Ministero della Salute, with technical management by IZS Abruzzo e Molise.
  — [Ricetta Veterinaria Elettronica](https://www.ricettaveterinariaelettronica.it/)
- **REV for software houses:** they can apply for web-service access ("Modulo richiesta accesso ai Web Services"). There are web services for "Medici Veterinari, studi e ambulatori", and newer documents cover "OAuth e Autenticazione SPID". — [REV Software House page](https://www.ricettaveterinariaelettronica.it/softwarehouse.html)
- **Switzerland, TAMV** (status 25 Nov 2025):
  - Art. 27: every dispensing of medicines for food-producing animals must record the trade name, quantity or dose, date, and owner name and address. Vets record this "in der Krankengeschichte des Tieres".
  - Art. 29: retention for 3 years.
  - Art. 35(2): vets must report prescription, dispensing and use of non-topical antibiotics "über das IS ABV".
  — [TAMV (Fedlex)](https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2004/592/20251125/de/html/fedlex-data-admin-ch-eli-cc-2004-592-20251125-de-html.html)
- **PMS-level support:**
  - easyVET: "TÄHAV-Modul, GOT-Liquidation, IDEXX-Schnittstelle". The same page describes the eRezept-Veterinär as "im Rollout". — [medizinio comparison (2026)](https://medizinio.de/software/praxis/tierarzt)
  - Smart Vet: REV "in meno di un minuto". — [Smart Vet](https://www.smartvet.it/)
  - Vetincloud: REV plus Sistema TS. — [Capterra IT](https://www.capterra.it/software/161509/vet-in-cloud)
- **AI-vendor touchpoints:**
  - Curala cites Austrian rules: § 16 Abs 2 and § 30 Abs 2 Tierärztegesetz, and § 66 Abs 2 Tierarzneimittelgesetz. — [Curala for vets](https://www.curala.at/ki-dokumentation-tierarztpraxis)
  - Trade press recommends "Pflichtfelder für Wirkstoff, Dosis und Dauer" in templates so that AI notes support "die aktuellen Nachweispflichten der Tierärztlichen Hausapothekenverordnung". It also notes the BTK Musterberufsordnung § 3 duty to record findings and measures and keep them for 5 years. — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)
  - Provet's AI Actions match diagnoses, medications, treatments and vitals to the practice catalogue for billing ("charge capture"). — [Provet blog](https://provet.com/blog/8-steps-to-get-started-with-ai-scribe-for-veterinarians)
  - Provet's German localisation is incomplete: "The gap is localisation, not capability". — [Nordhealth CMD (PDF)](https://mb.cision.com/Public/20636/4384407/971605e4f2a0e9e0.pdf)

### Inferences
- **There is a clear opening for country packs.** The German rules make specific fields mandatory: Wirkstoff/Arzneimittel, Menge/Dosis, Dauer, the Art. 105(5) prescription data, antibiogram reasons, and GOT item numbers with diagnosis or reason for consultation. A text-first tool that flags these as missing before the vet approves would deliver something no AI scribe currently advertises. The Vetline checklist ("Pflichtfelder für Wirkstoff, Dosis und Dauer") shows practices already want this.
- **The terminology has moved.** Since 2025 the German "Abgabebeleg" is effectively the "tierärztliche Verschreibung" under Art. 105(5) Reg. 2019/6, and it also serves as the Behandlungsanweisung for food-producing animals. Country-pack wording should use the 2025 TÄHAV terms.
- **REV:** issuing requires SPID or OAuth web services and an approval process. A documentation assistant could realistically prepare a REV draft (medicine, dose, duration, owner tax code and so on) for the vet to issue in their PMS. Issuing REVs itself would need a software-house accreditation.
- **TÄHAV § 16 demands unalterable electronic records.** This fits an approval step with an audit trail and versioning.

### Gaps
- No source found on EU pet passport (Reg. 576/2013) vaccination-entry support by any AI vendor.
- Not checked: the current status of a German veterinary e-prescription, or an Austrian equivalent (e.g. AT TAKG/TAMG documentation, the Austrian Tierarzneimittelgesetz text).
- Not verified at source: the REV mandatory date of 16 Apr 2019, which I saw only in a search snippet of an IZS press release.

## 4. How vets in DACH and Italy talk about these tools (trade press, conferences, surveys)

### Takeaway
German trade press has moved to a practical, sceptical "test it yourself" stance. Vetline's October 2026 piece is the reference: no peer-reviewed vet evidence, check AVV and processing locations, get consent, measure 20 cases. DACH vendors' founders appear in congress programmes and press columns. Italian coverage in October 2026 is dominated by the new AI decree and ECM training duties rather than by specific scribe products. The only European vet AI-adoption survey with numbers I could open is the UK BVA's (21% use AI, mostly for imaging and lab work). No bpt, BTK, ANMVI, FNOVI or FVE survey on AI with numbers was found.

### Cited Findings
- **Vetline (Schlütersche, publisher of the BMTW), 14 Oct 2026**, "Eine KI, die mitschreibt – wie groß ist die Zeitersparnis?":
  - Cites the Digitail/AAHA survey (n = 3,968, end of 2023, Gabor et al. 2025). "knapp vier von zehn" respondents already used AI for records and administration, and "Sieben von zehn" doubted its accuracy.
  - Names Petleo.ai/Vetera, vetOS intelliVET ReportAssistant, Covetrus Pulse (ambient documentation free since Jan 2025) and Provet AI Scribe (since Nov 2025).
  - Concludes the tests will show whether savings are closer to "den zehn Minuten aus der Werbung oder bei den 41 Sekunden aus der Studie" (the UCLA randomised trial in human medicine).
  - Gives a seven-point checklist: PMS interface, AVV and locations, consent via QR code, templates with mandatory fields, release and labelling, 20-case stopwatch test, team training.
  — [Vetline, 14 Oct 2026](https://www.vetline.de/eine-ki-die-mitschreibt-wie-gross-ist-die-zeitersparnis)
- **Vetion.de** runs a monthly column written by Petleo co-founders (Dr. Björn Becker, Magnus Kirschstein). It is vendor-authored. Its argument: "KI einzuführen ist kein technisches Problem. Es ist ein Führungsproblem". Anecdote: "Der erste Befundtext, der in drei Minuten fertig war statt in fünfzehn". — [Vetion column (undated)](https://www.vetion.de/warum-der-chef-meistens-das-groesste-hindernis-beim-einfuehren-von-ki-ist/)
- **bpt-Kongress 2025:**
  - Talk, Fri 28 Nov 2025, 15:05–15:25: "Einsatz einer KI-gesteuerten Spracherkennung zur zeitsparenden Erhebung von Befundberichten in der Schweinepraxis", Rolf Nathaus (Reken) and Hannah-Sophie Braun (Berlin, ReportAssistant founder). — [bpt-Kongress 2025 Vorträge](https://www.tieraerzteverband.de/fortbildung/kongress/2025/Programm/fachprogramm-vortraege.php)
  - Round table, Fri 28 Nov 2025: "Digitalisierung scheitert am Montagmorgen", led by Dr. Björn Becker. — [bpt-Kongress 2025 Berufspolitik](https://www.tieraerzteverband.de/fortbildung/kongress/2025/Programm/berufspolitik.php)
  - The 2026 congress runs 19–21 Nov 2026. No AI items were visible in the 2026 programme pages yet, and the bpt lists an "AK Digitalisierung". — [bpt-Kongress 2026](https://www.tieraerzteverband.de/fortbildung/kongress/2026/index.php)
- **Italy:**
  - Vet33 (Edra), 14 Oct 2026: the AI decree's ECM and training duties for vets. — [Vet33](https://www.vet33.it/attivita-professionale/4461/intelligenza-artificiale-nuove-regole-dal-23-ottobre-cosa-cambia-per-i-veterinari.html)
  - The Vet33 homepage also carries AI-diagnostics interviews (Zoetis) and Boehringer Ingelheim's "Eko Vet+ | CANINEBEAT AI" heart-murmur system arriving in Italy. No scribe-related headlines were visible. — [Vet33 homepage](https://www.vet33.it/)
  - FNOVI has a working group "Nuove tecnologie ed IA" and stresses validation, data protection and keeping professional judgement with the vet. — [FNOVI, 14 Oct 2026](https://fnovi.it/node/52102)
- **Surveys:**
  - BVA "Voice of the Veterinary Profession" (UK, reported 29 May 2025):
    - 21% of respondents use AI at work.
    - Uses: radiography 44%, lab 27%, client communications 11%, admin 7%.
    - "routine admin or note-taking" was a perceived benefit for 38%.
    - Concerns: results interpreted without context 83%, use without follow-up checks 82%, over-reliance 68%, data protection about a quarter.
    — [Vet Times, 29 May 2025](https://www.vettimes.com/news/vets/wellbeing-at-work/fifth-of-vets-already-using-ai-daily-bva-survey)
- **Practitioner voices in vendor materials:**
  - An Austrian vet on Curala: reports "fast immer korrekt". — [Curala](https://www.curala.at/ki-dokumentation-tierarztpraxis)
  - TION on ReportAssistant: "mindestens 50 %". — [ReportAssistant](https://reportassistant.de/)
  - Provet Italia: "3-5 minuti in ogni consulto". — [Provet Italia](https://www.provet.com/it)

### Inferences
- **The professional conversation in DACH is about proof.** People ask for evidence, consent and liability ("auf wen fällt eine falsche Dosierung in der Notiz zurück?"). Founders of competing DACH tools (Petleo, ReportAssistant) are the visible voices at the bpt congress and in trade columns. A newcomer would need its own evidence, such as a published 20-case time-and-error test, to be credible.
- **Italy is in a regulation and training phase.** AI-literacy ECM credits are due by April 2027. That creates an opening for an "explainable, source-linked" tool positioned as compliant, and for CPD-style content (webinars on verifying AI notes).

### Gaps
- Not found: any bpt, BTK, Bundestierärztekammer, ÖTK, GST/SVS, ANMVI, FNOVI or FVE survey with AI-adoption numbers. The FVE website failed with a TLS error, and the FVE VetSurvey 2023 PDF was not opened. No association homepage (BTK, bpt, ÖTK, GST, SCIVAC, ANMVI) showed AI items on 18 Oct 2026, apart from FNOVI.
- Wir sind Tierarzt, Deutsches Tierärzteblatt, the Austrian Vetjournal, La Settimana Veterinaria, ANMVI Oggi and Vetjournal.it: none showed AI-scribe headlines on homepages I could fetch, and deeper article search was impossible without web search. The SCIVAC programme was not checked.
- The Digitail/AAHA 2026 study is mentioned on digitail.com but was not opened (US data).

## 5. Market structure: which PMS dominate DACH and Italy, and whether they offer open APIs or partner programmes for third-party AI

### Takeaway
Germany is fragmented:
- Vetera (Nordhealth) holds about 12% of 9,500 small-animal locations, by Nordhealth's estimate.
- The main rivals are VetZ/easyVET (Mars), inBehandlung and Diana Software, plus a long tail (ANIMALoffice, VET7.well, Vetinf, VetSet, Vquadrat, WinVet.net).
- The five largest groups own only 4% of locations and run no single PMS.

Integration routes for a third-party AI:
- Provet's documented REST API, partner application process and read-only MCP
- Vetera's "open approach to third-party integration" and free one-click interfaces
- VetZ's vetOS API, which is aimed at PMS vendors and carries commissions
- Copy/paste or an overlay window, as Curala and Petleo's Bubble do

In Italy, Smart Vet claims a 20% share. The REV web services make Italian PMS integration a compliance step.

### Cited Findings
- **Nordhealth CMD, 18 Aug 2026** (management estimates):
  - Germany: "1,171 of 9,500 12%" of small-animal locations on Provet/Vetera. Key competitors: "VetZ · inBehandlung · Diana Software".
  - "Big 5 · 368 · 4%" of locations vs "Everyone else · 9,132 · 96%".
  - "All 5 of the largest groups run no single PMS today". "Many German groups run Provet in their other markets". "The gap is localisation, not capability".
  - German ARR €2.4M against a TAM of €80M.
  - Spain competitors: "QVet · WinVet · Smart Vet". UK: "ezyVet · IDEXX Animana · RoboVet".
  - Illustrative revenue per location at full attach: software €500, plus "AI €120", plus "Clinical conversations €120", plus payments. "AI priced against labor, not software".
  — [Nordhealth CMD (PDF)](https://mb.cision.com/Public/20636/4384407/971605e4f2a0e9e0.pdf)
- **Nordhealth, Q4 2025 deck:** DACH ARR growth in 2025 was 1.8%, against UK 35.5%, US 41.7% and Southern Europe 27.8%. "Large opportunity to localise Provet in DACH". — [Nordhealth Q4 2025 (PDF)](https://mb.cision.com/Public/20636/4315670/90c4a8ad72cc7291.pdf)
- **Nordhealth, 13 Aug 2025:** "Accelerating the localisation … Provet Cloud, into DACH markets" and "groundwork for migrating Vetera clients … onto Provet Cloud". — [Nordhealth release, 13 Aug 2025](https://news.cision.com/nordhealth-oy/r/nordhealth-to-accelerate-ai-development-and-dach-localisation,c4217671)
- **Vetera:**
  - "Über 2.000 Tierarztpraxen und Tierkliniken" and "Mehr als 18.000 Tierärzt:innen nutzen täglich unsere Software". Present in eight European countries and used by seven vet universities.
  - Partner logos include Petleo, IDEXX, BD Rowa and BFS. Testimonial: "Schnittstellen kostenfrei aktivierbar".
  — [Vetera homepage](https://www.vetera.net/)
  - When Nordhealth acquired Vetera (10 Mar 2022; older), it praised "an open approach to third-party integration". — [Nordhealth: acquires Vetera](https://nordhealth.com/news/nordhealth-acquires-vetera/)
- **VetZ / easyVET:**
  - VetZ GmbH is "Eine Tochtergesellschaft von Mars, Inc." — [VetZ homepage](https://www.vetz.de/)
  - The vetOS API is offered to PMS vendors: one API for "über 80 Laborgeräte, alle DICOM-Systeme und 32 Versandlabore" and AI services such as intelliVET ReportAssistant, with "Provision für jeden Abschluss". — [vetOS API](https://www.vetos.vet/vetos-api/)
  - easyVET claims "über 114.000 Anwender weltweit" (vendor claim, reported by a comparison site). — [medizinio (2026)](https://medizinio.de/software/praxis/tierarzt)
- **Long tail of DACH PMS (Curala's list):** ANIMALoffice, VET7.well and Vetera have Curala setup guides dated 03.10.2026; Vetinf, VetSet, Vquadrat Veterinär and WinVet.net are listed without guides. "Curala hat zu keinem Praxisverwaltungssystem (PVS) eine Schnittstelle". — [Curala Praxissoftware](https://www.curala.at/praxissoftware)
- **Provet's openness:**
  - "In 2015, Provet was the first with an open API". "A documented REST API. 150+ integrations. 100% data ownership". — [Provet release, 9 Jul 2026](https://news.cision.com/nordhealth-oy/r/provet-launches-the-first-all-in-one-veterinary-pims-built-for-ai-agents,c4366240)
  - The developer portal offers "Integrating Third Party Applications" plus an application form and developers@provet.com. — [Provet developers](https://developers.provetcloud.com/)
  - Provet MCP: "il primo e unico PIMS veterinario a offrire un MCP pubblico". It is read-only ("non può riscrivere nulla"), included in the Pro and Enterprise plans, and covers billing, debtors, payments, appointments, clients and patients, wellness plans, clinical activity and the catalogue. It works with Claude, ChatGPT, Gemini and Copilot. — [Provet MCP blog (IT)](https://www.provet.com/it/blog/provet-mcp-dati-clinica-ia)
- **Provet's positioning against standalone scribes:** its competitive matrix treats "AI SCRIBES" as lacking workflow ownership. "Independent. Provet sells software. Not lab equipment, not pharmacy distribution …" reads as an implicit contrast with Mars-owned VetZ and IDEXX. — [Nordhealth CMD (PDF)](https://mb.cision.com/Public/20636/4384407/971605e4f2a0e9e0.pdf); [Provet release](https://news.cision.com/nordhealth-oy/r/provet-launches-the-first-all-in-one-veterinary-pims-built-for-ai-agents,c4366240)
- **IDEXX's stance:** its ecosystem will "continue to support other ambient scribe solutions and third-party integrations". — [IDEXX/CoVet release via Finviz](https://finviz.com/news/392529/idexx-laboratories-acquires-covetai-to-advance-veterinary-workflow-intelligence)
- **Italy:**
  - Smart Vet claims "1 veterinario su 5 in Italia" (vendor claim). — [Capterra IT: Smart Vet](https://www.capterra.it/software/193134/smart-vet)
  - dr.veto has been sold in Italy since 2015. — [Tandem × dr.veto](https://tandemhealth.ai/product/integrations/dr-veto)
  - Provet is marketed in Italian. — [Provet Italia](https://www.provet.com/it)
  - The REV system exposes web services to software houses on request. — [REV Software House](https://www.ricettaveterinariaelettronica.it/softwarehouse.html)
- **Typical German PMS price ranges:**
  - On-premise: €2,000–8,000 one-off plus monthly costs.
  - SaaS: €80–200 per month.
  - Maintenance: 15–20% of list price per year.
  — [medizinio (2026)](https://medizinio.de/software/praxis/tierarzt)

### Inferences
- **Distribution in Germany:**
  - About 88% of small-animal locations are not on Vetera. VetZ/easyVET is Mars-owned and already bundles ReportAssistant via vetOS. Provet's scribe lacks German and Provet's German localisation is unfinished.
  - So the near-term route for an independent text-first tool is PMS-agnostic: an overlay or clipboard, export, or a Vetera interface, the way Petleo and Curala do it.
  - The Provet REST API and MCP are the most documented open interfaces. MCP is read-only, so writing records back would need the REST API and partner approval.
- **Strategy implied by Nordhealth's own deck.** It calls standalone scribes "a feature, not platform", and says they "must plug into the PMS". A text-first assistant should therefore present itself as complementary: a structured-record and compliance layer whose output drops cleanly into any PMS. It should not try to look like a rival PMS.
- **Italy:** the market is cheap (Smart Vet at €168 per year) and REV/Sistema TS-centric. A text-first tool would likely win on owner letters, REV-ready medication summaries and Italian-language records rather than on deep PMS integration. That would need partnerships with Smart Vet, Vetincloud, dr.veto or Provet.

### Gaps
- No independent market-share data for Austria, Switzerland or Italy. Smart Vet's 20% is a vendor claim. Nordhealth's German figures are its own estimates.
- Not found: whether Vetera, easyVET/VetZ, VET7.well or Smart Vet run a formal partner programme for third-party AI vendors, beyond Vetera's partner logos and the vetOS API offered to PMS vendors.
- Swiss PMS landscape (which vendors lead) and Austria-specific PMS shares were not found.
- inBehandlung and Diana Software (named by Nordhealth as German competitors) were not researched, nor whether they have AI features.
