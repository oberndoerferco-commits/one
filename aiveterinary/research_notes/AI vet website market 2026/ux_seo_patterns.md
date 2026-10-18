# UX, content, search-visibility and technical patterns of leading pet-health information and AI-vet websites (EN / IT / DE), as of 18 October 2026

All observations are date-stamped 2026-10-18 (UTC). "Measured" figures come from my own scripted fetch of each page's raw HTML (curl). The script counted words in the main `<article>`/`<main>` element, H2/H3 headings, JSON-LD `@type`s, bylines, dates, sources, FAQ and triage wording. Word counts are approximate. Where the script could not isolate the article body, the figure is the whole page and is marked "(page)". Pages that refused automated access are named as such and were not analysed.

## 1. Search results for high-volume owner queries (EN/IT/DE): who ranks, what their pages look like, and what AI answers cite

### Takeaway
I could not observe Google results directly, because Google required JavaScript. On a non-Google engine with the region set (DuckDuckGo HTML, 18 Oct 2026), the top 10s mix three kinds of site: large brand or publisher hubs (PetMD, AKC, zooplus, Fressnapf, Purina, my-personaltrainer), vet or telehealth brands (PDSA, Vets Now, FirstVet, felmo, Pfotendoctor, webvet), and many small, recent niche sites. Among the niche sites are a single vet's own site (#1 for the Italian tick query) and a local clinic blog (#1 for "Katze frisst nicht"). The pages that win run about 1,000–2,500 words (median about 1,500 across 38 measured pages) and are built around H2 sections in the order "causes → what to do → when to see a vet". About half of the titles promise triage ("When to worry", "Is it an emergency?", "quando preoccuparsi", "Notfallzeichen"). I could not capture the AI answers (Google AI Overviews, Bing Copilot) or the sources they cite.

### Cited Findings

#### Method and date
- Searches ran on 2026-10-18 between 21:11 and 21:14 UTC through DuckDuckGo's HTML endpoint, with the region set to us-en, uk-en, it-it or de-de. Example: [DDG "cane vomita giallo", it-it](https://html.duckduckgo.com/html/?q=cane+vomita+giallo&kl=it-it). The requests left from a US-based proxy, so this is not a true Italian or German user's result page.
- Google returned a page that requires JavaScript ("enablejs") instead of results, so Google rankings and AI Overviews could not be read — [Google, hl=it gl=it](https://www.google.com/search?q=cane+vomita+giallo&hl=it&gl=it).
- Bing (mkt=en-US) gave relevant results for the first two queries — [Bing "dog vomiting yellow"](https://www.bing.com/search?q=dog+vomiting+yellow&mkt=en-US&setlang=en-US&cc=US&count=15), [Bing "cat not eating"](https://www.bing.com/search?q=cat+not+eating&mkt=en-US&setlang=en-US&cc=US&count=15). After that it returned unrelated results, for example Premier League fixtures for "dog limping" in en-GB — [Bing "dog limping" en-GB](https://www.bing.com/search?q=dog+limping&mkt=en-GB&setlang=en-GB&cc=GB&count=15). I treated this as bot throttling and discarded those Bing pages.

#### English (DuckDuckGo us-en unless noted)
- **"dog vomiting yellow"**: 1 The Spruce Pets · 2 PetMD "Why Is My Dog Throwing Up Yellow? Is It an Emergency?" · 3 webvet.com · 4 caninescape.com · 5 Dogster "(Vet Answer)" · 6 shepherdtips.com · 7 Dogs Naturally · 8 caninesandpups.com · 9 urgentvet.com · 10 PetMD "Dog Vomiting: Causes & When To See a Vet" — [DDG us-en](https://html.duckduckgo.com/html/?q=dog+vomiting+yellow&kl=us-en). Bing en-US gave almost the same order (Spruce Pets, PetMD, webvet, caninescape, Dogster…) — [Bing](https://www.bing.com/search?q=dog+vomiting+yellow&mkt=en-US&setlang=en-US&cc=US&count=15). In uk-en the same domains appear, plus dogdigestivehealth.com — [DDG uk-en](https://html.duckduckgo.com/html/?q=dog+vomiting+yellow&kl=uk-en).
- **"cat not eating"**: 1 PetMD · 2 cats.com · 3 webvet · 4 cats.com · 5 happycatathome.com · 6 Chewy · 7 PetsRadar ("A vet explains…") · 8 Embrace Pet Insurance · 9 thevetdesk.com ("10 Vet-Reviewed Reasons") · 10 WebMD — [DDG us-en](https://html.duckduckgo.com/html/?q=cat+not+eating&kl=us-en). uk-en adds poolervet.com, AnimalWised and petwiseuk.co.uk ("Vet-Approved Guide") — [DDG uk-en](https://html.duckduckgo.com/html/?q=cat+not+eating&kl=uk-en).
- **"dog ate chocolate"**: 1 AKC · 2 rescuedogs101 "(toxicity calculator)" · 3 Dogster "3 Vet-Approved Steps" · 4 PetMD "Dog Chocolate Toxicity Meter" · 5 wikiHow · 6 Cornell Riney Canine Health Center · 7 veterinarysecrets.com · 8 Vets Now · 9 safefoodfordogs.com · 10 veterinaryclinic.com "Chocolate Toxicity Calculator for Dogs" — [DDG us-en](https://html.duckduckgo.com/html/?q=dog+ate+chocolate&kl=us-en). In uk-en, PDSA is #4 — [DDG uk-en](https://html.duckduckgo.com/html/?q=dog+ate+chocolate&kl=uk-en). Three of the us-en top 10 are calculators or advertise one in the title.
- The Cornell chocolate page ranked #6 but returned **HTTP 404** when I opened it — [Cornell page](https://www.vet.cornell.edu/departments-centers-and-institutes/riney-canine-health-center/canine-health-topics/chocolate).
- **"dog limping"**: 1 maven.pet "(Vet Verified)" · 2 caninescape "(2026 Guide)" · 3 PetMD · 4 Dogster · 5 Preventive Vet · 6 vetmedguide.com · 7 petdogexpert.com · 8 yourvetonline.com · 9 webvet · 10 snouthive.com "(2026 Guide)" — [DDG us-en](https://html.duckduckgo.com/html/?q=dog+limping&kl=us-en). In uk-en, medpaw.co.uk is #3 and PDSA #5 — [DDG uk-en](https://html.duckduckgo.com/html/?q=dog+limping&kl=uk-en).

#### Italian (DuckDuckGo it-it)
- **"cane vomita giallo"**: 1 wamiz.it · 2 amoreaquattrozampe.it · 3 veterinari.it (pronto-soccorso wiki) · 4 advance-affinity.com/it (pet-food brand) · 5 dogmassageacademy.it · 6 santevet.it (pet insurer) · 7 salutecane.it · 8 vitadacane.it · 9 animalpedia.it · 10 ilmiocaneleggenda.it — [DDG](https://html.duckduckgo.com/html/?q=cane+vomita+giallo&kl=it-it).
- **"gatto non mangia"**: 1 amoreaquattrozampe.it · 2 monge.it (pet-food brand) · 3 and 5 my-personaltrainer.it/mypet · 4 gattichepassione.com · 6 and 9 miciogatto.it · 7 it.cats.com · 8 schesir.com (brand) · 10 tuttosuigatti.it — [DDG](https://html.duckduckgo.com/html/?q=gatto+non+mangia&kl=it-it).
- **"cane ha mangiato cioccolato"**: 1 my-personaltrainer.it · 2 purina.it · 3 wamiz.it · 4 fanpage.it/kodami · 5 amoreaquattrozampe.it · 6 advance-affinity · 7 vetmiranese.it (vet clinic) · 8 hundeo.com/it · 9 thewom.it · 10 petvitals.katreo.com "Calcolatore di tossicità" — [DDG](https://html.duckduckgo.com/html/?q=cane+ha+mangiato+cioccolato&kl=it-it).
- **"zecca cane come toglierla"**: 1 amicaveterinaria.com (a single vet's site) · 2 rimosvet.com (product maker) · 3 my-personaltrainer.it · 4 purina.it · 5 appuntisulblog.it · 6 salutecane.it "(2026)" · 7 wikihow.it · 8 alessandramagnani.it (vet) · 9 cazampa.it · 10 openfarma.it — [DDG](https://html.duckduckgo.com/html/?q=zecca+cane+come+toglierla&kl=it-it).

#### German (DuckDuckGo de-de)
- **"Katze frisst nicht"**: 1 kleintierpraxis-kornat.de (blog of a Paderborn small-animal clinic) · 2 zooplus Magazin · 3 rundumdiekatz.de · 4 petklar.de · 5 de.cats.com · 6 FOCUS Tierarzt · 7 FirstVet DE · 8 tierschutzinitiative-ohne-grenzen.de · 9 tier-ratgeber.com · 10 spatz.vet — [DDG](https://html.duckduckgo.com/html/?q=Katze+frisst+nicht&kl=de-de).
- **"Hund hat Schokolade gefressen"**: 1 felmo (mobile vet) · 2 Fressnapf Magazin · 3 tierischehelden.de · 4 Pfotendoctor (online vet) · 5 AniCura DE · 6 and 7 happyhunde.de · 8 vet-dogs.de · 9 dogcare24.de "mit Theobromin-Rechner" · 10 welpenknigge.de — [DDG](https://html.duckduckgo.com/html/?q=Hund+hat+Schokolade+gefressen&kl=de-de).
- **"Zecke entfernen Hund"**: 1 vetura.de · 2 zooplus · 3 Rover DE · 4 hundewissen-mit-kopf.de · 5 hundeo · 6 hundum-betreut.de · 7 a PDF version of the vetura article · 8 wamiz.de · 9 haustierguide.de · 10 dogssupreme.de "2026" — [DDG](https://html.duckduckgo.com/html/?q=Zecke+entfernen+Hund&kl=de-de).
- **"Hund erbricht gelb"**: DuckDuckGo returned no parseable results, apparently because of rate-limiting — [DDG](https://html.duckduckgo.com/html/?q=Hund+erbricht+gelb&kl=de-de) (see Gaps).

#### Title patterns across the top 10s
- **Triage promise in the title:**
  - "dog vomiting yellow": 5 of 10 ("Is It an Emergency?" ×2, "When to Worry" ×2, "When To See a Vet") — [DDG](https://html.duckduckgo.com/html/?q=dog+vomiting+yellow&kl=us-en)
  - "dog limping": 6 of 10 ("When to See a Vet", "When to Rest vs. See the Vet", "When To Call A Vet", "When to Worry and See a Vet") — [DDG](https://html.duckduckgo.com/html/?q=dog+limping&kl=us-en)
  - "cane vomita giallo": 6 of 10 ("quando preoccuparsi" ×5, "Quando è Pericoloso") — [DDG](https://html.duckduckgo.com/html/?q=cane+vomita+giallo&kl=it-it)
  - "Katze frisst nicht": 3 to 4 of 10 ("Soforthilfe im Notfall", "Notfallzeichen", "Warnzeichen", "Wann sollte man sich…") — [DDG](https://html.duckduckgo.com/html/?q=Katze+frisst+nicht&kl=de-de)
- **Expertise claims in the title:** "(Vet Answer)", "Vet-Approved", "Vet-Reviewed", "(Vet Verified)", "A vet explains…", "guida del veterinario" — [DDG EN](https://html.duckduckgo.com/html/?q=cat+not+eating&kl=us-en), [DDG limping](https://html.duckduckgo.com/html/?q=dog+limping&kl=us-en), [DDG IT tick](https://html.duckduckgo.com/html/?q=zecca+cane+come+toglierla&kl=it-it).
- **Year in the title:** "(2026 Guide)" (caninescape, snouthive), "(2026)" (salutecane ×2), "2026" (dogssupreme) — [DDG limping](https://html.duckduckgo.com/html/?q=dog+limping&kl=us-en), [DDG IT tick](https://html.duckduckgo.com/html/?q=zecca+cane+come+toglierla&kl=it-it), [DDG DE tick](https://html.duckduckgo.com/html/?q=Zecke+entfernen+Hund&kl=de-de).

#### What the top-ranking pages look like (measured 2026-10-18)
"Sources" means a visible references/Quellen/Fonti section. Types listed are JSON-LD unless marked "microdata".

| Page (query, rank) | ~Words | H2/H3 | Visible byline / reviewer | Visible date | Sources | FAQ | Schema (key types) | Other notable elements |
|---|---|---|---|---|---|---|---|---|
| [PetMD yellow bile](https://www.petmd.com/dog/general-health/dog-throwing-up-yellow-bile) (EN vomit #2) | 1,433 | 9/11 | "By Lauren Mick, LVT. Reviewed by Barri J. Morrison, DVM" | "Updated Jun. 25, 2024" (but JSON-LD dateModified 2026-05-12) | none found | yes | Article, FAQPage, BreadcrumbList, Person | "In This Article" table of contents; "Health Tools" navigation (Symptom Checker, Chocolate Toxicity, Healthy Weight) |
| [webvet yellow](https://www.webvet.com/dog-throwing-up-yellow/) (EN vomit #3) | 3,362 | 11/15 | "Medically reviewed by Dr. Pippa Elliott, BVMS MRCVS" | "Last reviewed Jun 23, 2026 · 9 min read" | editorial-process statement | yes | MedicalWebPage, MedicalAudience, Article, FAQPage, BreadcrumbList; lastReviewed | 8 `<details>` accordions, 2 tables; affiliate disclosure; sponsored telehealth box |
| [Dutch yellow](https://www.dutch.com/blogs/dogs/dog-throwing-up-yellow) (EN vomit, not in DDG top 10) | 2,593 | 4/12 | "Medically reviewed by Dr. Kate Elden, DVM"; JSON-LD author is "Inseev Content" | "Updated April, 2026" | "References" (cites PetMD and others) | yes | BlogPosting, FAQPage, SpeakableSpecification | "Key takeaway" box; repeated "Talk to a vet" calls to action |
| [PetMD cat not eating](https://www.petmd.com/cat/nutrition/cat-not-eating-what-to-do) (#1) | 1,687 | 7/13 | "By Jennifer Grota, DVM. Reviewed by Barri J. Morrison, DVM" | "Updated May 14, 2024" (JSON-LD 2025-08-29) | "References" (textbook) | no | Article, BreadcrumbList | — |
| [cats.com](https://cats.com/cat-not-eating-but-acting-normal) (#2) | 1,836 | 4/13 | "Written by Dr. Lizzie Youens BSc (Hons) BVSc MRCVS"; "Fact checked by Jackie Brown" (a senior content editor) | "Last updated Apr 22, 2025" | "View Sources" | yes (microdata) | NewsArticle/Article | hreflang in 7 languages including x-default |
| [Chewy](https://www.chewy.com/education/cat/food-and-nutrition/why-is-my-cat-not-eating) (#6) | 1,676 | 4/11 | "By Janelle Leeson. Reviewed by Dr. Barri J. Morrison" | "Updated May 11, 2026" | "Attributions" | yes | none found | "Key Takeaways"; 48 external script tags |
| [Embrace](https://www.embracepetinsurance.com/waterbowl/article/why-is-my-cat-not-eating) (#8) | 2,073 | 8/10 | "Written by Chyrle Bonk DVM" | "Updated Jul 1, 2026" | — | yes | BlogPosting; dateModified written as "7-1-2026" (not ISO 8601) | first H2: "First Thing First: How Long Has Your Cat Not Eaten?" |
| [WebMD](https://www.webmd.com/pets/cats/my-cat-wont-eat) (#10) | 1,937 | 7/4 | "Written by Hilary Parker · Medically Reviewed by Amy Flowers, DVM on September 10, 2026" | same | "Sources" and "Update History" | yes | none found | "Add WebMD as a Preferred Source" button |
| [AKC](https://www.akc.org/expert-advice/health/dog-ate-chocolate/) (chocolate #1) | 1,108 | 6/5 | "By AKC Staff" (no reviewer) | "Updated: Mar 09, 2026 \| 4 Minutes" | — | no | Article | links out to the Merck Vet Manual calculator |
| [PetMD Chocolate Toxicity Meter](https://www.petmd.com/dog/chocolate-toxicity) (#4) | 626 | 3/2 | none | none | none | no | none | interactive meter; Pet Poison Helpline number |
| [Vets Now chocolate](https://www.vets-now.com/pet-care-advice/dogs/dog-eaten-chocolate) (#8) | ~2,000 (page) | 28/3 | Dave Leicester ("Head of Telehealth at PawSquad"), Kenny Diamond | "Published on: 2 February 2017 · Updated on: 30 July 2026" | — | — | BlogPosting | links to its own calculator |
| [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning) (uk #4) | 1,268 | 13/2 | institutional: "Written by vets and vet nurses. This advice is for UK pets only." | "Published: January 2023" | — | — | none | contents list; "When to contact your vet"; video; infographic; feedback widget |
| [maven.pet limping](https://maven.pet/all-about-pets/pet-health/dog-behaviors/why-is-my-dog-limping/) (limping #1) | 1,381 | 10/7 | "Reviewed by Melita (Pet Health Content Lead)", while the title says "(Vet Verified)" | "Published: 2025-10-20 \| Updated: 2026-08-25" | none | no | Article | first-aid framing |
| [PetMD limping](https://www.petmd.com/dog/symptoms/why-is-my-dog-limping) (#3) | 2,051 | 11/10 | "By Jennifer Coates, DVM. Reviewed by Rhiannon Koehler, DVM" | "Updated Apr. 5, 2024" (JSON-LD 2025-10-16) | — | yes | Article, FAQPage | — |
| [PDSA limping](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/limping-and-stiffness-in-dogs) (uk #5) | 801 | 9/6 | institutional | "Published: July 2019" | — | — | none | — |
| [wamiz.it vomito giallo](https://wamiz.it/cane/consigli/19415/cosa-fare-se-il-cane-vomita-giallo-e-perche-accade) (IT #1) | 1,301 | 7/4 | author Nina Segatori; "Verificato da un professionista, Francesco Reina" | 26/02/21 shown at top; JSON-LD dateModified 2025-04-28 | — | yes ("Domande frequenti (FAQ)") | Article, FAQPage; reviewedBy (Person) | — |
| [amoreaquattrozampe vomito](https://www.amoreaquattrozampe.it/cani/salute/cane-vomito-giallo-cause-sintomi-e-trattamento/47719/) (IT #2) | 1,136 | 4/2 | Raffaella Lauretta (no credential shown) | JSON-LD 2022-05-10 | — | — | Article | "Indice dei contenuti"; "Aggiungi … alle fonti di google news" |
| [amoreaquattrozampe gatto](https://www.amoreaquattrozampe.it/gatti/gatto-non-mangia-7-cause-possibili-rimedi/39915/) (IT cat #1) | 1,327 | 9/7 | Francesca Ciardiello | JSON-LD 2019-04-15 | — | — | Article | a 2019 article still ranks #1 |
| [veterinari.it](https://www.veterinari.it/pronto-soccorso/wiki/vomito-cane-cause-rimedi-e-quando-preoccuparsi/) (IT vomit #3) | ~3,600 (page) | 16/31 | none clear | none | — | — | BreadcrumbList only | sits in a "pronto-soccorso" (first aid) wiki section |
| [monge.it](https://www.monge.it/il-gatto-non-mangia-piu-che-cosa-fare/) (IT cat #2) | 1,034 | 5/6 | author "roberto"; reviewedBy is the Organization "Monge.it" | JSON-LD 2026-09-09 | — | yes ("5 Domande frequenti") | Article; reviewedBy, lastReviewed | — |
| [my-personaltrainer mypet cioccolato](https://www.my-personaltrainer.it/mypet/cioccolato-cani.html) (IT chocolate #1) | 1,025 | 5/5 | "Team MyPersonalPet" | JSON-LD 2026-01-19 | — | — | Article | — |
| [purina.it cioccolata](https://www.purina.it/articoli/cani/alimentazione/consigli/i-cani-possono-mangiare-la-cioccolata) (#2) | ~2,150 (page) | — | "Scritto da Team Editoriale Purina" | "Febbraio 13, 2024 · 5 min di lettura" | — | — | Article | — |
| [amicaveterinaria.com zecca](https://amicaveterinaria.com/come-togliere-una-zecca/) (IT tick #1) | 2,718 | 18/8 | Valentina Chiapatti (the vet who runs the site) | JSON-LD 2026-07-01 | PubMed "bibliografia scientifica" | — | Article | 30 images, a video, WhatsApp consultation contact |
| [salutecane.it](https://www.salutecane.it/cane-vomita/) (IT vomit #7) | ~4,400 (page) | 12/17 | "Redazione SaluteCane" | "Aggiornato il 16 Ottobre 2026" | "Fonti" (cites studies) | yes | BlogPosting, FAQPage | "In breve" summary and "In questa guida" table of contents |
| [kleintierpraxis-kornat.de](https://kleintierpraxis-kornat.de/pages/blog/articles/katze-frisst-nicht-ursachen-appetitlosigkeit.html) (DE cat #1) | 427 | 6/1 | Dorothea Kornat, Tierärztin (JSON-LD jobTitle) | JSON-LD 2026-02-14 | — | yes ("Häufige Fragen") | BlogPosting, FAQPage, VeterinaryCare | 7 KB of HTML, 3 scripts; phone number and "Termin anfragen" |
| [zooplus Katze](https://www.zooplus.de/magazin/katze/katzengesundheit-pflege/appetitlosigkeit) (DE cat #2) | ~2,250 (page) | 9/15 | "Verfasst von Dr. Franziska G., Tierärztin" | "Zuletzt geändert 17/10/2026 · 7 min" | "Quellen:" | — | Article | — |
| [FirstVet DE](https://firstvet.com/de/artikel/katze-frisst-nicht) (DE cat #7) | 2,171 | 8/17 | "Autoren: Dr. Romina Pankow, Tierärztin · Prüfer: Dr. Sabrina Vogt, Tierärztin" | "Veröffentlicht: 23.8.2022" | — | yes ("Häufige Fragen (FAQ)") | Article | "Tierärztliche Videosprechstunde" call to action |
| [FOCUS Tierarzt](https://focus-tierarzt.de/magazin/katze-frisst-nicht-ursachen-und-was-zu-tun-ist) (DE cat #6) | 2,141 | 5/24 | author: Diplom-Biologin and science journalist; "Geprüft von … Medizinjournalistin" | "Veröffentlicht: 27.01.2022 · Aktualisiert: 23.04.2026" | "Quellen" | — | none (microdata Patient/Person) | 46 images |
| [spatz.vet](https://www.spatz.vet/de/ratgeber/katze-frisst-nicht-was-tun) (DE cat #10) | 2,030 | 10/3 | Sophie Neumann, "Tiermedizinische Expertin" | "Veröffentlicht am 23. Juli 2026 · Zuletzt aktualisiert am 9. September 2026" | "Quellen", including the 2022 ISFM consensus guidelines | — | Article | "Das Wichtigste in Kürze"; "Anzeichen, bei denen du sofort handeln musst, nicht erst morgen" |
| [felmo](https://felmo.de/hunderatgeber/mein-hund-hat-schokolade-gefressen) (DE chocolate #1) | 1,019 | 6/0 | — | JSON-LD datePublished 2026-10-14 | — | yes | Article, FAQPage | — |
| [Fressnapf](https://www.fressnapf.de/magazin/hund/gesundheit/hund-hat-schokolade-gefressen/) (#2) | 2,387 | 13/6 | no named author in JSON-LD | JSON-LD 2026-04-22 | "Quellen" | — | Article | hreflang de-AT, de-CH, de-DE, de-LU |
| [dogcare24](https://dogcare24.de/hundegesundheit/hund-hat-schokolade-gegessen/) (#9) | 2,284 | 12/24 | Andre Caspar, "Experte für Tierversicherungen" | "Aktualisiert am 1. Oktober 2026 · 10 Min. Lesezeit · 6 Quellen" | Quellen, including the Merck Vet Manual and USDA FoodData Central | yes | Article, FAQPage, Product, AggregateRating | "Schnell-Check" box, Theobromin-Rechner, 6 tables |
| [vetura.de](https://vetura.de/zecken-entfernen-hund/) (DE tick #1) | 2,438 | 9/16 | "Tierärztlich geprüft von Dr. med. vet. Ilse Ertl" | "Veröffentlicht: 14. März 2025 · Zuletzt aktualisiert: 18. September 2026" | numbered "Quellen und wissenschaftliche Studien" | yes | Article, FAQPage, OnlineStore, VeterinaryCare | the site also sells products |
| [hundeo Zecken](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen) (DE tick #5) | 1,218 | 4/12 | "Tierarzt Mag.med.vet. Emin Jasarevic" (author and reviewer) | "Aktualisiert: 30. Juli 2026 · 8 Min." | "Quelle … Stand: Juli 2026 … ESCCAP" | yes | MedicalWebPage, FAQPage, Speakable, VideoObject; reviewedBy, lastReviewed | video "Mit Kapiteln, Quellen und tierärztlich geprüften Hinweisen" |

- **Length distribution.** Across the 38 symptom or condition pages where the article body could be isolated, word counts ran from 427 (the Paderborn clinic, DE #1) to 3,362 (webvet), with a median of about 1,520. This is computed from the measurements in the table above and the leader pages in §2.
- **Pages that refused automated access:**
  - The Spruce Pets (EN vomit #1) returned HTTP 402 — [page](https://www.thesprucepets.com/dog-vomiting-yellow-bile-4846474)
  - Dogster returned HTTP 403 — [page](https://www.dogster.com/ask-the-vet/dog-vomiting-yellow/)
  - fanpage.it/Kodami returned HTTP 403 — [page](https://www.fanpage.it/kodami/cosa-succede-se-il-cane-mangia-del-cioccolato-rischi-sintomi-e-come-disintossicarlo/)

#### AI answers
- Bing's results page includes the Copilot Search interface configuration (for example the string "Copilot Search is unavailable. Try another query"), but no AI answer is rendered on the server. Answers load in the browser, so their cited sources could not be captured — [Bing "dog vomiting yellow"](https://www.bing.com/search?q=dog+vomiting+yellow&mkt=en-US&setlang=en-US&cc=US&count=15).
- **Pew Research, Google, US, March 2025** — [Pew](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/):
  - 18% of searches in the study produced an AI summary (12,593 of 68,879 unique searches).
  - Users clicked a traditional result on 8% of visits that had a summary, versus 15% without one.
  - Only 1% of visits clicked a link inside the summary.
  - Sessions ended on 26% of pages with a summary, versus 16% without.
  - Wikipedia, YouTube and Reddit were the most-cited sources (15% of AI-summary sources). .gov sites made up 6% of AI-summary sources, versus 2% of standard results.
  - Method: 900 US adults in the KnowledgePanel Digital browsing panel.

### Inferences
- In all three languages the top results reward the same page shape: an answer-first, triage-first structure in H2 sections, about 1,000–2,500 words, a vet byline, a visible date and an FAQ. Most aiveterinary articles already follow the "first: when to go now" pattern. For example, the built page [cat-straining-litter-box](file:///home/user/one/aiveterinary/site/dist/animals/cat-straining-litter-box.html) opens with the H2 "First: if it's a male cat, go now" and closes with "Sources".
- **Title formula.** The titles that win promise causes, action and triage together. Suggested per-locale patterns:
  - EN: "… causes, what to do and when to see a vet"
  - IT: "… cause, cosa fare e quando preoccuparsi"
  - DE: "… Ursachen, was tun und wann zum Tierarzt (Notfallzeichen)"
- **Italy looks like the softest market.** Several Italian #1–#3 pages carry no vet reviewer, no sources and dates from 2019–2022 (amoreaquattrozampe, my-personaltrainer). A dated, sourced Italian article reviewed by a medico veterinario has a credible way to stand out.
- **Small sites can rank, at least on a Bing-type index.** A 427-word clinic page ranks #1 for "Katze frisst nicht", and a single vet's site ranks #1 for the Italian tick query. Relevance and a clear answer appear to matter more than domain size there. This is not evidence about Google.
- **Calculators earn top-10 places.** For poison or ingestion queries ("dog ate chocolate"), pages that carry or advertise a calculator hold 3 of 10 places in EN, and calculator pages appear in IT (#10) and DE (#9).

### Gaps
- No Google results, AI Overviews or AI Mode answers were observable, and no ChatGPT or Perplexity answers either: Google requires JavaScript, and Bing's and DuckDuckGo's assistant answers are rendered client-side. So I cannot say which sources AI Overviews cite for these queries.
- The DuckDuckGo results are a single snapshot from a US-based connection. They are not Google rankings, and not a true Italian or German user's results.
- The DE query "Hund erbricht gelb" failed on DuckDuckGo. The session's built-in search tool is US-only, so its results could not stand in. They were also spam-heavy, including apparently hijacked domains on unrelated subjects, and were not used as ranking evidence. Two pages first seen there (Dutch, Omni Calculator IT) were opened and analysed in their own right.
- The web-search budget for this session ran out before every planned query could be run. Further SERP collection, such as with SISTRIX for DE or SEOZoom for IT, was not possible.

## 2. Leader page patterns: how they signal expertise (E-E-A-T), date content, show reviewers and handle emergencies

### Takeaway
The strongest sites put a two-person byline above the fold: a writer, then a named vet reviewer with post-nominals (DVM, BVMS MRCVS, Tierärztin, Dr. med. vet.). Next to it sits a visible "Updated" or "Last reviewed" date, and the page ends with a references list. Institutional charities (PDSA, RSPCA) instead use an institutional authority line ("Written by vets and vet nurses") and a "Published" month. Emergencies are handled with an early, explicitly labelled H2 ("When to contact your vet", "Never 'watch and wait'") rather than a decorative banner. Integrity varies more than polish does:

- dates shown on the page that disagree with the structured data (PetMD)
- identical "last changed" timestamps across articles (zooplus)
- "Vet Verified" claims whose named reviewer is not a vet (maven)
- JSON-LD authors that are an SEO-content label (Dutch)

### Cited Findings

#### English-language leaders
- **PetMD:**
  - Visible "By [writer, LVT/DVM]. Reviewed by [DVM] · Updated [date]", an "In This Article" table of contents, an FAQ block with FAQPage markup, and a "Health Tools" menu (Symptom Checker, Chocolate Toxicity, Healthy Weight, Veterinary Terms Guide) — [PetMD yellow bile](https://www.petmd.com/dog/general-health/dog-throwing-up-yellow-bile), [PetMD limping](https://www.petmd.com/dog/symptoms/why-is-my-dog-limping).
  - On all three PetMD articles measured, the visible "Updated" date (2024) is older than the JSON-LD `dateModified` (2025 or 2026) — [yellow bile](https://www.petmd.com/dog/general-health/dog-throwing-up-yellow-bile), [cat not eating](https://www.petmd.com/cat/nutrition/cat-not-eating-what-to-do), [limping](https://www.petmd.com/dog/symptoms/why-is-my-dog-limping).
  - PetMD pages carry a "Chat free with Chewy's vet team" banner, and the meter page's footer reads "Copyright 2026 Chewy" — [PetMD meter](https://www.petmd.com/dog/chocolate-toxicity).
- **VCA:**
  - Articles are question-led H3s ("What is vomiting?", "When should I be concerned about my dog's vomiting?", "How is vomiting treated?"), with "Last updated on Aug 14, 2026" and calls to action to book or find a hospital — [VCA vomiting](https://vcahospitals.com/know-your-pet/vomiting-in-dogs).
  - The authors are "Courtney Barnes, BSc, DVM; Krista Williams, BSc, DVM; Ernest Ward, DVM". The page states: "This content was written by LifeLearn Animal Health (LifeLearn Inc.) and is licensed to this practice" — syndicated content — [VCA vomiting](https://vcahospitals.com/know-your-pet/vomiting-in-dogs).
  - Only BreadcrumbList JSON-LD is present, with hreflang en-ca and en-us — [VCA vomiting](https://vcahospitals.com/know-your-pet/vomiting-in-dogs).
- **PDSA Pet Health Hub:**
  - No JSON-LD at all. Attribution is "Written by vets and vet nurses. This advice is for UK pets only.", with "Published: [month year]" (January 2023, October 2024, July 2019) — [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning), [PDSA vomiting](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs), [PDSA limping](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/limping-and-stiffness-in-dogs).
  - The vomiting page is built on H2s: "Contents · Overview · How to tell if your dog is feeling sick · What causes vomiting in dogs? · When to contact your vet · Treatment for vomiting · Home remedies for vomiting in dogs · Dog vomit colour chart · How to tell the difference between vomiting, retching and regurgitating · FAQs" — [PDSA vomiting](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs).
  - Pages end with a "Did you find this page useful?" feedback form. It asks whether the page clarified when a vet is needed and whether anything seems incorrect, and who the user is (pet owner, vet professional, researching) — [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning).
  - Pages carry promotions for the PDSA Pet Store and PDSA Pet Insurance — [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning).
- **RSPCA:**
  - The "Common dog poisons" page opens with the H2 "Never 'watch and wait'", then one H2 per poison (slug pellets, chocolate, NSAIDs, rodenticides, grapes and raisins, vitamin D), then "Find or call a vet" — [RSPCA poisons](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/poisoning/common).
  - There is no JSON-LD and no visible review date — [RSPCA poisons](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/poisoning/common).
- **MSD Veterinary Manual, pet-owner version:**
  - Pages are short (about 450–660 words) and written by named academic specialists with affiliation, e.g. "…DVM, DACVS, Veterinary Surgical Specialists, Spokane, WA". They show "Last updated: Dec 2025" or "Sept 2024" — [MSD lameness](https://www.msdvetmanual.com/dog-owners/bone-joint-and-muscle-disorders-of-dogs/lameness-in-dogs), [MSD vomiting](https://www.msdvetmanual.com/dog-owners/digestive-disorders-of-dogs/vomiting-in-dogs).
  - JSON-LD types are MedicalWebPage, MedicalCondition, SpeakableSpecification and Audience. Each page has 52 external script tags (Next.js) — [MSD vomiting](https://www.msdvetmanual.com/dog-owners/digestive-disorders-of-dogs/vomiting-in-dogs).
  - The hub links to quizzes and to an "essentialaccessibility.com" assistive app — [MSD dog owners](https://www.msdvetmanual.com/dog-owners).
- **Cornell Feline Health Center:**
  - Plain pages of about 560–690 words with no JSON-LD. The vomiting page says "Last updated 2021" — [Cornell vomiting](https://www.vet.cornell.edu/node/4030), [Cornell anorexia](https://www.vet.cornell.edu/node/4073).
  - Its topic index offers short FAQ-style pages (e.g. "Ticks and Your Cat – FAQs") and an "Emergency" link — [Cornell FHC topics](https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics).
- **webvet.com:** a site that appears to be new. Its symptom-checker JSON-LD shows datePublished 2026-06-20.
  - Pages carry a "Vet-Reviewed" label, "Medically reviewed by Dr. Pippa Elliott, BVMS MRCVS · Last reviewed Jun 23, 2026", and MedicalWebPage with lastReviewed and MedicalAudience markup — [webvet yellow](https://www.webvet.com/dog-throwing-up-yellow/).
  - It publishes an editorial process: "research from reputable veterinary and scientific sources, careful drafting, mandatory review of medical content by a credentialed veterinarian, and dated publication" — [webvet yellow](https://www.webvet.com/dog-throwing-up-yellow/).
  - It also shows an affiliate disclosure and a sponsored telehealth box ("Unlimited video calls and messaging with licensed vets…") — [webvet yellow](https://www.webvet.com/dog-throwing-up-yellow/), [webvet symptom checker](https://www.webvet.com/symptom-checker/).
- **Dutch blog:** visible "Medically reviewed by Dr. Kate Elden, DVM · Updated April, 2026", a "Key takeaway" box, an FAQ and a "References" list. The JSON-LD author is "Inseev Content" and there is no reviewedBy — [Dutch](https://www.dutch.com/blogs/dogs/dog-throwing-up-yellow).
- **WebMD (Pets):** "Written by … Medically Reviewed by Amy Flowers, DVM on September 10, 2026", a "Sources" list (Cornell Feline Health Center and others), an "Update History" link, and an "Add WebMD as a Preferred Source" button — [WebMD](https://www.webmd.com/pets/cats/my-cat-wont-eat).
- **cats.com:** "Written by Dr. … BVSc MRCVS" plus a separate "Fact checked by [editor]". It states that health content "is written by or reviewed by our team of veterinary experts", with a "View Sources" expander — [cats.com](https://cats.com/cat-not-eating-but-acting-normal).
- **maven.pet:** the title claims "(Vet Verified)", but the visible reviewer is "Melita (Pet Health Content Lead)" — [maven](https://maven.pet/all-about-pets/pet-health/dog-behaviors/why-is-my-dog-limping/).
- **FirstVet:**
  - The German article shows "Veröffentlicht: 23.8.2022 · Autoren: Dr. Romina Pankow, Tierärztin · Prüfer: Dr. Sabrina Vogt, Tierärztin", followed by an FAQ and a video-consultation call to action — [FirstVet DE](https://firstvet.com/de/artikel/katze-frisst-nicht).
  - The US article hub is paginated to page 40 and includes cost articles ("Dog Ownership Costs from Head to Tail") — [FirstVet US articles](https://firstvet.com/us/articles).
- **Vetster:** a symptom hub ("Dog health symptoms") with about 92 internal links to symptom pages and "See an online vet" calls to action — [Vetster symptoms](https://vetster.com/en/symptoms/dog).
- **Blue Cross** returned HTTP 403 to automated fetches and could not be analysed — [Blue Cross](https://www.bluecross.org.uk/advice/dog/health-and-injuries/chocolate-poisoning-in-dogs).

#### Italian
- **wamiz.it:** "Verificato da un professionista, Francesco Reina", mirrored in JSON-LD `reviewedBy` (Person, with an author page URL), plus a "Domande frequenti (FAQ)" block — [wamiz.it](https://wamiz.it/cane/consigli/19415/cosa-fare-se-il-cane-vomita-giallo-e-perche-accade).
- **amoreaquattrozampe.it:** writers' names without credentials, and articles from 2019 or 2022 that still rank #1–#2. Pages carry a "Aggiungi amoreaquattrozampe.it alle fonti di google news" prompt — [gatto](https://www.amoreaquattrozampe.it/gatti/gatto-non-mangia-7-cause-possibili-rimedi/39915/), [vomito](https://www.amoreaquattrozampe.it/cani/salute/cane-vomito-giallo-cause-sintomi-e-trattamento/47719/).
- **Brand team bylines:** "Scritto da Team Editoriale Purina" ([Purina IT](https://www.purina.it/articoli/cani/salute/parassiti/togliere-zecche-cane)), "Team MyPersonalPet" ([my-personaltrainer](https://www.my-personaltrainer.it/mypet/gatto-non-mangia-cause-cosa-fare.html)), and Monge's author "roberto" with reviewedBy set to the Organization ([Monge](https://www.monge.it/il-gatto-non-mangia-piu-che-cosa-fare/)).
- **Vet-run sites:** amicaveterinaria.com is written by the vet herself, links a PubMed "bibliografia scientifica", carries 30 images and a video, and offers WhatsApp contact — [amicaveterinaria](https://amicaveterinaria.com/come-togliere-una-zecca/).
- **"A cura di":** miciogatto uses "A cura di Elisa Bertoldi · Aggiornato al: 18 Dicembre 2024" — [miciogatto](https://www.miciogatto.it/alimentazione-gatto/problemi-alimentari/gattino-che-non-mangia-cosa-fare-assolutamente/).
- **veterinari.it** is a community and directory site whose owner content sits in a "pronto-soccorso" wiki. Only BreadcrumbList markup is present — [veterinari.it](https://www.veterinari.it/pronto-soccorso/wiki/vomito-cane-cause-rimedi-e-quando-preoccuparsi/), [home](https://www.veterinari.it/).
- **ANMVI:** the homepage exposed no owner-health links matching symptom or tool keywords — [ANMVI](https://www.anmvi.it/).
- **Royal Canin IT:**
  - The hub lists articles such as "Segnali di disturbi digestivi nel gatto", "Cosa non dare da mangiare ai gatti" and "Quanto costa mantenere un gatto" — [Royal Canin IT hub](https://www.royalcanin.com/it/cats/health-and-wellbeing).
  - The article pages returned HTTP 403 — [example](https://www.royalcanin.com/it/cats/health-and-wellbeing/what-foods-are-toxic-for-my-cat).

#### German
- **zooplus Magazin:** "Verfasst von [Name], Tierärztin · Zuletzt geändert [date] · [n] min", followed by a "Quellen:" list (textbooks, ESCCAP) — [zooplus Hund erbricht](https://www.zooplus.de/magazin/hund/hundegesundheit-pflege/hund-erbricht), [zooplus Zecken](https://www.zooplus.de/magazin/hund/hundegesundheit-pflege/zecken-entfernen-bei-hunden).
  - All three zooplus articles fetched on 2026-10-18 show the identical JSON-LD dateModified "2026-10-17T12:01:38" and the visible text "Zuletzt geändert 17/10/2026" — [Katze](https://www.zooplus.de/magazin/katze/katzengesundheit-pflege/appetitlosigkeit), [Hund erbricht](https://www.zooplus.de/magazin/hund/hundegesundheit-pflege/hund-erbricht), [Zecken](https://www.zooplus.de/magazin/hund/hundegesundheit-pflege/zecken-entfernen-bei-hunden).
- **German vet-review formulas:**
  - "Tierärztlich geprüft von Dr. med. vet. Ilse Ertl" — [vetura](https://vetura.de/zecken-entfernen-hund/)
  - "Geprüft von Tierarzt Mag.med.vet. Emin Jasarevic", with MedicalWebPage, reviewedBy and lastReviewed in JSON-LD — [hundeo](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen)
  - "Tierärztliche Qualitätssicherung", with "Datum der letzten Aktualisierung: November 2024" — [tiermedizinportal](https://www.tiermedizinportal.de/tierkrankheiten/hundekrankheiten/zecken-befall-beim-hund)
- **Reviewers who are not vets:**
  - FOCUS Tierarzt: "Geprüft von Yvonne Küster, Medizinjournalistin" — [FOCUS Tierarzt](https://focus-tierarzt.de/magazin/katze-frisst-nicht-ursachen-und-was-zu-tun-ist)
  - tierischehelden: "Inhalt nach redaktionellen Leitlinien verfasst und von unserem Expertenteam fachlich geprüft", with no named vet — [tierischehelden](https://www.tierischehelden.de/schokoladenvergiftung-beim-hund/)
  - dogcare24: authored by an insurance expert — [dogcare24](https://dogcare24.de/hundegesundheit/hund-hat-schokolade-gegessen/)
- **Disclaimer near the top:** "🩺 Dieser Ratgeber ersetzt keine tierärztliche Untersuchung" — [petklar](https://petklar.de/katze-frisst-nicht/).
- **Vetline is business-to-business** (practice management and clinical articles, e.g. "Eine KI, die mitschreibt – wie groß ist die Zeitersparnis?"), with a "Tierhalter-Ratgeber" form ("10 Fragen & Antworten") — [Vetline](https://vetline.de/).
- **tiermedizinportal** carries magazine pieces, quizzes ("Quiz: Magendrehung bei Hunden") and guideline explainers ("Leitlinie: Welche Impfungen sind für Hunde empfohlen?") — [tiermedizinportal](https://www.tiermedizinportal.de/).
- **Royal Canin DE** returned HTTP 403 — [page](https://www.royalcanin.com/de/dogs/health-and-wellbeing/vomiting-in-dogs).

#### Emergency handling patterns observed
- **Imperative H2 at the top:** "Never 'watch and wait'" — [RSPCA](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/poisoning/common).
- **Overview bullet plus a dedicated H2:** "If your dog has eaten chocolate, keep the packaging and call your vet immediately", then "When to contact your vet", with the advice to call the vet or the Animal PoisonLine without waiting for symptoms — [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning).
- **Header instruction plus a poison-line number:** "If your dog ate chocolate, contact your emergency vet immediately", with the Pet Poison Helpline 855-764-7661 — [PetMD meter](https://www.petmd.com/dog/chocolate-toxicity).
- **Time-threshold first:** the first H2 is "First Thing First: How Long Has Your Cat Not Eaten?" — [Embrace](https://www.embracepetinsurance.com/waterbowl/article/why-is-my-cat-not-eating).
- **Tiered urgency:** "Anzeichen, bei denen du sofort handeln musst, nicht erst morgen", under "Wann du die Tierärztin oder den Tierarzt rufen solltest" — [spatz.vet](https://www.spatz.vet/de/ratgeber/katze-frisst-nicht-was-tun). Also "When to Call the Vet · Puppies, Senior Dogs, and Other Special Cases" — [webvet](https://www.webvet.com/dog-throwing-up-yellow/).
- **Question heading:** "When should I be concerned about my dog's vomiting?" — [VCA](https://vcahospitals.com/know-your-pet/vomiting-in-dogs). Also "Wann ist tierärztliche Hilfe gefragt?" — [tiermedizinportal](https://www.tiermedizinportal.de/tierkrankheiten/hundekrankheiten/zecken-befall-beim-hund).
- **Visual triage aid:** a "Dog vomit colour chart" — [PDSA vomiting](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs).

#### Google's guidance that applies to these signals
- "Do bylines lead to further information about the author or authors involved…". The guide recommends adding bylines "where readers might expect it". It also asks: "Are you changing the date of pages to make them seem fresh when the content has not substantially changed?" (page last updated 2026-10-05) — [Google: helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- "While E-E-A-T itself isn't a specific ranking factor…"; "Of these aspects, trust is most important." For YMYL topics, "the content must be highly accurate and consistent with established expert consensus." — [Google: helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- "Your structured data must be a true representation of the page content." "Don't mark up content that is not visible to readers of the page." (page last updated 2026-07-10) — [Google: structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).
- The Article markup documentation (last updated 2026-09-08) shows `author` as a Person with a `url` pointing to a profile page, alongside datePublished and dateModified — [Google: Article](https://developers.google.com/search/docs/appearance/structured-data/article).

### Inferences
- **Byline and date block.** The bar to clear is: "Written by [Name] · Medically reviewed by [Dr Name, DVM / Medico Veterinario / Tierärztin] · Last reviewed [date]", with each name linking to a profile page that states credentials and registration. JSON-LD `author`, `reviewedBy` and `lastReviewed` should be kept identical to the visible text. A "next review due" date and a short "what changed" log (as in WebMD's "Update History") would go beyond PetMD, which shows stale visible dates.
- **Avoid two failure modes leaders show.** Do not auto-bump dates sitewide (the zooplus pattern; Google explicitly warns against freshness-faking). Do not let visible and structured dates diverge (PetMD). Also avoid "vet verified" labels unless a named vet actually reviewed the page.
- **Emergency design.** The leaders treat urgency as content structure, not decoration: an H2 or first block in plain imperative language, ideally tiered into "go now / call today / monitor 24 h". Poison pages should carry country-specific poison-line contacts per locale; the numbers must be verified before publishing.
- **Feedback form.** PDSA's "Did you find this page useful?" form can be copied on a static site. A simple form can also collect "anything incorrect?" reports, which strengthens the review loop and the E-E-A-T story.

### Gaps
- Blue Cross, Royal Canin (IT/DE), Dogster, The Spruce Pets and fanpage/Kodami blocked automated fetching, so their byline and schema patterns are not recorded.
- VCA's chocolate page was not located. A guessed URL returned 404 — [VCA guess](https://vcahospitals.com/know-your-pet/chocolate-toxicity-in-dogs).
- "Mio Cane / Il mio gatto"-type portals and Veterinario.it were not identified or checked, because the search budget ran out.
- ANMVI appears to have no owner-facing health content on its homepage. That is not confirmed beyond the homepage link scan.

## 3. Tools that attract and retain owners: who offers what, and the chocolate-calculator problem

### Takeaway
The tools leaders actually run are mostly lightweight:

- symptom checkers (PetMD, webvet, cats.com, Pawp)
- a chocolate toxicity calculator, the most common single tool across EN, IT and DE (PetMD, Vets Now, Merck/MSD, veterinaryclinic.com, rescuedogs101, Omni, PetVitals, dogcare24)
- "can my pet eat that?" and toxic-food lookups (webvet; Royal Canin IT articles)
- emergency or nearest-vet finders (Vets Now, RSPCA, Pfotendoctor, spatz.vet)
- life-expectancy and weight calculators (webvet, cats.com)

Vets Now and veterinaryclinic.com make their calculators embeddable, and both PDSA and AKC link out to a third-party calculator instead of building their own. That makes the calculator a link-earning asset. Calculators disagree on inputs and thresholds, and some give reassuring "negligible" outcomes. That is the core of the safety concern.

### Cited Findings

#### Who offers what (observed 2026-10-18)
| Site | Tools observed | Source |
|---|---|---|
| PetMD (Chewy) | "Health Tools": Symptom Checker ("Dog & Cat Symptom Checker"), Chocolate Toxicity Meter, Healthy Weight, Veterinary Terms Guide; "Chat free with Chewy's vet team" | [PetMD home](https://www.petmd.com/), [Symptom Checker](https://www.petmd.com/symptom-checker), [Meter](https://www.petmd.com/dog/chocolate-toxicity) |
| webvet | Symptom Checker ("Free Vet-Reviewed Tool", "Sponsored by…", "Pick the body area and the symptom you're seeing…", WebApplication JSON-LD); "Can My Pet Eat That?"; "My Pet Ate Something"; Rx Database; Dog Life Expectancy Calculator (196 breeds, per-breed sources); newsletter | [Symptom checker](https://www.webvet.com/symptom-checker/), [Life expectancy](https://www.webvet.com/tools/dog-life-expectancy-calculator/), [Home](https://www.webvet.com/) |
| cats.com | Cat Weight Calculator, Symptoms Checker, Cat Name Finder, Cat Forum (in navigation) | [cats.com](https://cats.com/cat-not-eating-but-acting-normal) |
| Pawp | "Try Pawp's Symptom Checker tool — for free. Check My Pet's Symptoms" inside articles | [Pawp](https://pawp.com/cat-not-eating-why-cat-refusing-to-eat-how-to-help/) |
| Vets Now (UK) | Dog chocolate calculator (embeddable); "Find an emergency vet" (page title: "60+ Out-of-hours Vet Clinics & Hospitals"; CollectionPage/ItemList JSON-LD) | [Calculator](https://dog-chocolate-calculator.vets-now.com/), [Finder](https://www.vets-now.com/find-an-emergency-vet) |
| PDSA | Links to Vets Now's calculator; "Dog vomit colour chart"; vet-services links | [PDSA chocolate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning), [PDSA vomiting](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs) |
| AKC | Links "chocolate toxicity calculator" to merckvetmanual.com/multimedia/clinical-calculator/chocolate-toxicity-calculator | [AKC](https://www.akc.org/expert-advice/health/dog-ate-chocolate/) |
| veterinaryclinic.com | Chocolate calculator with "Toxicity Thresholds" quick reference, case stories, "Embed This Calculator"; claims "Trusted since 2012 Used by millions worldwide"; HowTo + FAQPage + WebApplication JSON-LD | [Calculator](https://veterinaryclinic.com/chocolate/calc.html) |
| rescuedogs101 | Blog post built around a calculator, plus "Real Story: When Our Dog Ate Chocolate" | [Page](https://www.rescuedogs101.com/first-thing-dog-eats-chocolate/) |
| Omni Calculator (IT) | "Calcolatore per la Tossicità del Cioccolato per Cani" (author shown as "MD, PhD candidate"; FAQPage) | [Omni IT](https://www.omnicalculator.com/it/biologia/calcolatore-tossicita-cioccolato-cani) |
| PetVitals / Katreo (IT, 8 hreflang languages) | Chocolate calculator article plus "Altri strumenti gratuiti", including "Calcolatore vaccini per cuccioli"; SoftwareApplication JSON-LD | [PetVitals](https://petvitals.katreo.com/it/blog/cane-ha-mangiato-cioccolato-calcolatore-tossicita) |
| dogcare24 (DE, insurer) | "Theobromin-Rechner" inside the article, "Schnell-Check: Ist es gefährlich?", 6 tables | [dogcare24](https://dogcare24.de/hundegesundheit/hund-hat-schokolade-gegessen/) |
| hundeo (DE) | Navigation: "Tools · Futter-Finder · Rechner · Hundenamen" | [hundeo](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen) |
| Pfotendoctor (DE online vet) | "Notdienstfinder" (emergency-service finder) in navigation; "JETZT CHATTEN" | [Pfotendoctor](https://pfotendoctor.de/ratgeber/hund-schokolade-was-tun-wenn-der-hund-schokolade-gefressen-hat) |
| spatz.vet (DE) | Vet and clinic finder with ratings ("Am besten bewertete Tierarztpraxen…", "Häufig gesuchte Städte") | [spatz.vet](https://www.spatz.vet/de) |
| RSPCA | "Find or call a vet" | [RSPCA health](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health) |
| MSD Vet Manual / tiermedizinportal | Quizzes | [MSD](https://www.msdvetmanual.com/dog-owners), [tiermedizinportal](https://www.tiermedizinportal.de/) |
| Royal Canin IT / FirstVet US | Cost-of-ownership content (articles, not calculators) | [Royal Canin IT](https://www.royalcanin.com/it/cats/health-and-wellbeing), [FirstVet US](https://firstvet.com/us/articles) |

#### Chocolate calculators: inputs, thresholds and reassurance risk
- **Reference thresholds (MSD Veterinary Manual, professional version):**
  - Doses: mild signs at 20 mg/kg methylxanthines; cardiotoxic effects at 40–50 mg/kg; seizures at ≥60 mg/kg. The oral LD50 is reportedly 100–200 mg/kg, but "severe clinical signs and death may occur at much lower doses."
  - Content per chocolate type: cocoa powder 28.5 mg/g; baker's chocolate 15.5 mg/g; semisweet/dark 5.3–5.6 mg/g; milk chocolate 2.3 mg/g; white chocolate 0.04 mg/g.
  - Author: Cristine Hayes, DVM (ASPCA Animal Poison Control Center), peer-reviewed. Last updated February 2026.
  - [MSD chocolate toxicosis](https://www.msdvetmanual.com/toxicology/food-hazards/chocolate-toxicosis-in-animals)
- **Vets Now calculator:**
  - Inputs are 5 weight bands (Toy <5 kg … Giant >40 kg), 5 chocolate types (Milk, Mild Dark, Strong Dark, White, Cooking) and an amount slider from "Little" to "Lots" with **no units**. No mg/kg thresholds are stated.
  - Outputs: "Negligible" ("No symptoms are expected"; monitor for 24 h and contact a vet only if the dog seems unwell), "Mild to Moderate", or "Possible emergency" ("Even if your dog isn't showing symptoms, they may still need treatment immediately").
  - Calls to action change with risk: video consultation for low risk, "Find an Emergency Vet" or "Contact your vet immediately" for high risk.
  - It offers embed code.
  - [Vets Now calculator](https://dog-chocolate-calculator.vets-now.com/)
- **PetMD meter:** weight 1–250 lb, 6 chocolate types and an amount in ounces. No mg/kg thresholds, no formal disclaimer, no author, reviewer or date, and no references, but a header urging owners to contact an emergency vet immediately — [PetMD meter](https://www.petmd.com/dog/chocolate-toxicity).
- **Embedding and outbound links:** PDSA links to Vets Now's calculator rather than hosting one — [PDSA](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning). AKC links to Merck's clinical calculator — [AKC](https://www.akc.org/expert-advice/health/dog-ate-chocolate/). veterinaryclinic.com and Vets Now both offer embed code — [veterinaryclinic.com](https://veterinaryclinic.com/chocolate/calc.html), [Vets Now](https://dog-chocolate-calculator.vets-now.com/).

#### Funnels from tool to service
- **Vets Now:** calculator result → risk-matched next step (video consult, emergency-clinic finder, or "contact your vet") — [Vets Now calculator](https://dog-chocolate-calculator.vets-now.com/).
- **webvet:** a sponsored symptom checker plus a newsletter ("Vet-Reviewed Pet Health in Your Inbox") and "Make a plan for my pet" — [webvet home](https://www.webvet.com/), [symptom checker](https://www.webvet.com/symptom-checker/).
- **PetVitals (IT)** markets itself as "Un'app per la salute del tuo animale che funziona come un quaderno…" ("a pet-health app that works like a notebook…"), with free tools and app-store links. "PetVitals: cura animali con IA, salute e promemoria" — [PetVitals IT](https://petvitals.katreo.com/it).

### Inferences
- **A methylxanthine calculator is the highest-value tool to build first.** It fits a static, local-first site. It should use MSD thresholds, gram and kg inputs, chocolate-type content values and a conservative design: no "negligible, no action" outcome for puppies, small dogs, or unknown amount or type. It should always show the poison-line and vet contact for the user's locale and state "this is not a diagnosis". To beat Vets Now and PetMD it should also:
  - show the arithmetic (mg/kg)
  - carry a named vet reviewer, date and sources (MSD, ASPCA APCC)
  - offer embed code and a printable result that feeds the pre-visit brief
- **Second-wave tools that fit a static site:**
  - a "Can my pet eat that?" lookup over a static JSON file (foods and plants, species-specific), using the site's existing Pagefind
  - a vomit-colour or stool chart as an accessible graphic with a text alternative
  - a puppy and kitten vaccination planner that writes into the booklet (PetVitals has a "Calcolatore vaccini per cuccioli")
  - a rule-based symptom triage, by body area then symptom then red flags, linking into articles
- **PetVitals (Italian, multilingual, "AI", notebook-style health app)** is the closest observed competitor to aiveterinary's local-first booklet. Its free tools are its acquisition engine.

### Gaps
- I could not open any published critique of dose calculators by a veterinary body (e.g. VPIS, Animal PoisonLine, ASPCA, BSAVA) because the search budget ran out. The "controversy" above is inferred from differences in design and wording between calculators, not from a cited statement.
- No backlink data (Ahrefs or Semrush) was available, so "which tools are linked to most" is inferred only from embed offers and from outbound links on PDSA and AKC.
- Not opened: ASPCA's toxic-plant database, Italian or German toxic-plant lists, pet age calculators other than webvet's life-expectancy tool, cost calculators, and vaccination schedules from VCA, BSAVA or StIKo Vet.

## 4. Structured data, technical SEO and AI answer engines (Google, Bing/Copilot, ChatGPT, Perplexity)

### Takeaway
As of October 2026, Google offers no FAQ rich result: it was deprecated on 7 May 2026 and its documentation removed in June 2026. HowTo is also gone. Google says AI Overviews and AI Mode need no special schema, files, "chunking" or llms.txt. Its levers are crawlability, snippet eligibility, structured data that matches visible text, people-first "non-commodity" content, and a new Search Console "Search generative AI" control, which defaults to Include. Microsoft's Bing guidance, by contrast, does describe chunk-level selection and rewards descriptive headings, question-and-answer pairs, lists and tables, and answers not hidden in accordions. To appear in ChatGPT search a site must allow OAI-SearchBot, and for Perplexity, PerplexityBot. Most pet-health leaders allow all AI crawlers. A minority block training bots while allowing search bots, and three block PerplexityBot. Leaders still use FAQPage markup widely. MedicalWebPage, `reviewedBy` and `lastReviewed` are rarer and are a differentiator.

### Cited Findings

#### Google: current guidance on health content, generative AI content and spam
- **People-first content.** "Who, How, and Why": add bylines where readers expect them, and explain how content was produced, including any use of AI. YMYL content "must be highly accurate and consistent with established expert consensus". Do not change dates to look fresh. Last updated 2026-10-05 — [Google: helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- **Generative-AI content.** "It is critical to manually factcheck and review all AI-generated content for accuracy and trustworthiness before publishing." The review also covers titles, meta descriptions, structured data and alt text. Google suggests "providing more background information on how automation was used". Last updated 2026-10-01 — [Google: using gen-AI content](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content).
- **Scaled content abuse.** Examples include "Using generative AI tools or other similar tools to generate many pages without adding value for users". Page last updated 2026-08-28 — [Google: spam policies](https://developers.google.com/search/docs/essentials/spam-policies). On 15 May 2026 Google clarified that its spam policies also apply to generative-AI responses in Search — [Google: Search Central changelog](https://developers.google.com/search/updates).
- **AI optimization guide** (new on 15 May 2026, last updated 2026-07-10) — [Google: AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide):
  - The features are "rooted in our core Search ranking and quality systems" (RAG/grounding and query fan-out).
  - "Create valuable, non-commodity content…": a unique point of view and first-hand expertise. It warns that creating separate pages for fan-out query variations to manipulate rankings or AI responses "violates Google's scaled content abuse spam policy".
  - Mythbusting: you can ignore "LLMS.txt files and other 'special' markup" ("Google Search itself doesn't use them"), "Chunking" ("There's no ideal page length"), "Rewriting content just for AI systems", "Seeking inauthentic 'mentions'" and "Overfocusing on structured data" ("Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add").
  - Eligibility: a page must be indexed and snippet-eligible, and "a site must be included in Search generative AI features in Search Console".
  - Semantic HTML helps screen readers. Browser agents may interpret "the accessibility tree".
- **AI features doc** (last updated 2025-12-10). No additional requirements and "no special schema.org structured data". The best practices it lists:
  - allow crawling
  - make content findable through internal links
  - provide a good page experience
  - keep important content in text
  - support it with images and video
  - make "structured data matches the visible text"
  - Preview controls are `nosnippet`, `data-nosnippet`, `max-snippet` and `noindex`; Google-Extended is a separate control for other Google AI uses.
  - [Google: AI features](https://developers.google.com/search/docs/appearance/ai-features)
- **Search Console "Search generative AI" control:**
  - It includes or excludes a site's links and content from AI Overviews, AI Mode and generative-AI features in Discover. The default is "Include".
  - It is "not used as a ranking or inclusion signal affecting other parts of Search".
  - It rolled out worldwide by 31 August 2026.
  - [Google Search Console Help: Search generative AI control](https://support.google.com/webmasters/answer/16908024)
- **Generative AI performance report:** shows impressions for AI Overviews and AI Mode by page, country, date and device. It rolled out worldwide by 31 August 2026 — [Google Search Console Help: Generative AI performance report](https://support.google.com/webmasters/answer/16984139).
- **llms.txt.** Changelog, 15 June 2026: llms.txt files "aren't needed for Google Search (and won't negatively or positively impact your visibility or rankings), it's fine if you want to maintain these files for other services" — [Google: changelog](https://developers.google.com/search/updates).

#### Google: status of rich results
- **FAQ:**
  - 8 May 2026: "Deprecating the FAQ rich result feature … This feature will no longer appear in Google Search starting May 7, 2026."
  - 15 June 2026: "Removed documentation for the FAQ rich result feature … no longer shown in Google Search results."
  - Since 14 September 2023 it had been limited to "well-known, authoritative government and health websites".
  - [Google: changelog](https://developers.google.com/search/updates), [FAQ doc URL now redirects to the changelog](https://developers.google.com/search/docs/appearance/structured-data/faqpage)
- **HowTo:** the documentation URL redirects to the changelog anchor "#how-to-deprecation" — [HowTo doc URL](https://developers.google.com/search/docs/appearance/structured-data/how-to).
- **Search gallery** (last updated 2026-10-16) lists 25 features, including Article, Breadcrumb, Organization, Profile page, Q&A, Speakable, Video, Image metadata and Dataset. FAQ and HowTo are not listed — [Google: search gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery).
- **Features retired in 2025:** book actions, course info, estimated salary, ClaimReview, learning video, special announcement and vehicle listing (banners 12 June 2025; several documentation pages removed 9 September 2025) — [Google: changelog](https://developers.google.com/search/updates).
- **Preferred sources:**
  - Available globally for Top Stories. In AI Mode and AI Overviews, a preferred site's content can be "highlighted with a 'preferred' badge".
  - Eligibility requires the site to be "included in Search generative AI features in Search Console". "Only domain-level and subdomain-level sites are eligible."
  - A Google-hosted button (`news.google.com/swg/js/v1/publisher.js`) can be embedded. Last updated 2026-09-18 — [Google: preferred sources](https://developers.google.com/search/docs/appearance/preferred-sources).
  - WebMD uses it: "Add WebMD as a Preferred Source to see more of our trusted content across Google Search, AI Overviews, and AI Mode" — [WebMD](https://www.webmd.com/pets/cats/my-cat-wont-eat).

#### Microsoft (Bing/Copilot), OpenAI and Perplexity
- **Microsoft, "Optimizing Your Content for Inclusion in AI Search Answers"** (Krishna Madhavan, Bing, 8 October 2025) — [Microsoft Advertising blog](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers):
  - Assistants split pages into pieces and evaluate each for authority and relevance: "AI assistants don't read a page top to bottom like a person would."
  - Align the title, H1 and description, and use descriptive headings. "Direct questions with clear answers mirror the way people search." Use lists and tables.
  - JSON-LD "helps machines identify content types such as products, reviews, FAQs, and events".
  - Avoid long unbroken text, and "Don't hide important answers in tabs or expandable menus." Don't rely on PDFs or images for core information.
  - Selected content is "fresh, authoritative, structured, and semantically clear".
- **OpenAI crawlers** — [OpenAI: crawlers](https://developers.openai.com/api/docs/bots):
  - "OAI-SearchBot is used to surface websites in search results in ChatGPT's search features." "Sites that are opted out of OAI-SearchBot will not be shown in ChatGPT search answers."
  - GPTBot is for training, and "Each setting is independent of the others."
  - ChatGPT-User is for user-initiated fetches.
  - Changes take "~24 hours" to apply.
- **Perplexity crawlers** — [Perplexity: bots](https://docs.perplexity.ai/guides/bots):
  - PerplexityBot "is designed to surface and link websites in search results on Perplexity" and "is not used to crawl content for AI foundation models".
  - Perplexity-User "generally ignores robots.txt rules".
  - To appear in results, allow PerplexityBot and the published IP ranges.
- The Bing Webmaster Guidelines page rendered only its title to my fetch (it is built with JavaScript), so its text could not be read — [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a).

#### Schema actually used by leaders (JSON-LD found in raw HTML, 2026-10-18)
- **FAQPage is still common** despite the deprecation:
  - EN: PetMD (2 of 3 articles), webvet, Dutch, veterinaryclinic.com (also HowTo) — [PetMD](https://www.petmd.com/dog/general-health/dog-throwing-up-yellow-bile), [webvet](https://www.webvet.com/dog-throwing-up-yellow/), [Dutch](https://www.dutch.com/blogs/dogs/dog-throwing-up-yellow), [veterinaryclinic.com](https://veterinaryclinic.com/chocolate/calc.html)
  - IT: wamiz.it, salutecane, Omni — [wamiz](https://wamiz.it/cane/consigli/19415/cosa-fare-se-il-cane-vomita-giallo-e-perche-accade), [salutecane](https://www.salutecane.it/cane-vomita/), [Omni](https://www.omnicalculator.com/it/biologia/calcolatore-tossicita-cioccolato-cani)
  - DE: kornat, felmo, petklar, vetura, hundeo, dogcare24 — [kornat](https://kleintierpraxis-kornat.de/pages/blog/articles/katze-frisst-nicht-ursachen-appetitlosigkeit.html), [felmo](https://felmo.de/hunderatgeber/mein-hund-hat-schokolade-gefressen), [petklar](https://petklar.de/katze-frisst-nicht/), [vetura](https://vetura.de/zecken-entfernen-hund/), [hundeo](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen), [dogcare24](https://dogcare24.de/hundegesundheit/hund-hat-schokolade-gegessen/)
- **MedicalWebPage** appears only on MSD, webvet and hundeo — [MSD](https://www.msdvetmanual.com/dog-owners/digestive-disorders-of-dogs/vomiting-in-dogs), [webvet](https://www.webvet.com/dog-throwing-up-yellow/), [hundeo](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen). schema.org's MedicalWebPage carries `lastReviewed`, `reviewedBy`, `medicalAudience`, `specialty` and `aspect` — [schema.org MedicalWebPage](https://schema.org/MedicalWebPage).
- **`reviewedBy` in JSON-LD:** wamiz.it (Person), hundeo (Person), webvet, monge.it (an Organization, which is weak) — [wamiz](https://wamiz.it/cane/consigli/19415/cosa-fare-se-il-cane-vomita-giallo-e-perche-accade), [hundeo](https://www.hundeo.com/gesundheit/zeckenmittel/zecken-entfernen), [monge](https://www.monge.it/il-gatto-non-mangia-piu-che-cosa-fare/).
- **SpeakableSpecification:** MSD, Dutch, PetsRadar, hundeo, PetVitals — [MSD](https://www.msdvetmanual.com/dog-owners/digestive-disorders-of-dogs/vomiting-in-dogs), [PetsRadar](https://www.petsradar.com/advice/cats-not-eating).
- **No JSON-LD at all:** PDSA, RSPCA, Cornell FHC, PetMD's Chocolate Meter, AniCura DE (microdata breadcrumb only), FOCUS Tierarzt (microdata only), Chewy, WebMD — [PDSA](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs), [RSPCA](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/poisoning/common), [Cornell](https://www.vet.cornell.edu/node/4030), [AniCura](https://www.anicura.de/fuer-tierbesitzer/hund/wissensbank/hund-hat-schokolade-gegessen/).
- **Markup errors seen:** Embrace writes dates as "7-1-2026", which is not ISO 8601 — [Embrace](https://www.embracepetinsurance.com/waterbowl/article/why-is-my-cat-not-eating). dogcare24 puts Product and AggregateRating on a health article — [dogcare24](https://dogcare24.de/hundegesundheit/hund-hat-schokolade-gegessen/).

#### hreflang practice
- **Google's rules** (last updated 2026-09-21): "Each language version must list itself as well as all other language versions." Links must be bidirectional ("If two pages don't both point to each other, the tags will be ignored"). Add `x-default` for unmatched languages — [Google: localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions).
- **Observed on leaders:**
  - cats.com: de, en, es, fr, it, pt-BR, x-default — [cats.com](https://cats.com/cat-not-eating-but-acting-normal)
  - PetVitals: 8 languages — [PetVitals](https://petvitals.katreo.com/it/blog/cane-ha-mangiato-cioccolato-calcolatore-tossicita)
  - spatz.vet: de, en, x-default — [spatz.vet](https://www.spatz.vet/de/ratgeber/katze-frisst-nicht-was-tun)
  - Fressnapf: regional German variants de-AT, de-CH, de-DE, de-LU — [Fressnapf](https://www.fressnapf.de/magazin/hund/gesundheit/hund-hat-schokolade-gefressen/)
  - VCA: en-ca, en-us — [VCA](https://vcahospitals.com/know-your-pet/vomiting-in-dogs)
  - PetMD, PDSA, zooplus and FirstVet DE articles: none, although FirstVet runs many country sites — [FirstVet DE](https://firstvet.com/de/artikel/katze-frisst-nicht)
  - Apparent misconfigurations: an Italian wamiz.it page lists only de-DE — [wamiz](https://wamiz.it/cane/consigli/19415/cosa-fare-se-il-cane-vomita-giallo-e-perche-accade); RSPCA lists en-US plus x-default — [RSPCA](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/poisoning/common)
- **aiveterinary baseline:** the built article lists hreflang en, it and de with a canonical URL, but no x-default and no JSON-LD in that built file — [local build](file:///home/user/one/aiveterinary/site/dist/animals/cat-straining-litter-box.html).

#### AI-crawler policies and llms.txt among 40 pet-health domains
Parsed from each domain's live robots.txt (`https://<domain>/robots.txt`) and `/llms.txt` on 2026-10-18. "Block" means `Disallow: /` for that user agent; "partial" means path-level rules only.

- **No AI-specific full blocks (28 of 38 parseable):** petmd.com, vcahospitals.com, pdsa.org.uk, bluecross.org.uk, vet.cornell.edu, merckvetmanual.com, firstvet.com, vetster.com, akc.org, dogster.com, pawp.com, wamiz.it, amoreaquattrozampe.it, purina.it, amicaveterinaria.com, monge.it, royalcanin.com, zooplus.de, fressnapf.de, anicura.de, felmo.de, vetura.de, tiermedizinportal.de, kleintierpraxis-kornat.de. veterinari.it and maven.pet explicitly allow GPTBot and others. webvet.com and dogcare24.de have path-level rules only. Example: [petmd robots](https://www.petmd.com/robots.txt).
- **Training bots blocked, search bots allowed:**
  - [dutch.com](https://www.dutch.com/robots.txt) blocks GPTBot, ClaudeBot, Applebot-Extended, CCBot, Bytespider and meta-externalagent, and declares the Cloudflare "Content-Signal: search=yes,ai-input=yes,ai-train=no".
  - [hundeo.com](https://www.hundeo.com/robots.txt) blocks GPTBot, anthropic-ai, Google-Extended, CCBot, Bytespider and Amazonbot, while explicitly allowing OAI-SearchBot, ChatGPT-User, ClaudeBot and PerplexityBot.
- **Selective blocks:**
  - [rspca.org.uk](https://www.rspca.org.uk/robots.txt): GPTBot only
  - [cats.com](https://cats.com/robots.txt): GPTBot, anthropic-ai, CCBot
  - [webmd.com](https://www.webmd.com/robots.txt): GPTBot, ClaudeBot, CCBot
  - [petsradar.com](https://www.petsradar.com/robots.txt): Applebot-Extended, Bytespider, Amazonbot, meta
  - [chewy.com](https://www.chewy.com/robots.txt): Amazonbot
- **Broad blocks that include answer-engine bots:**
  - [thesprucepets.com](https://www.thesprucepets.com/robots.txt) blocks Claude and Perplexity search and user bots, Google-Extended and others; OpenAI bots have path-level rules only.
  - [my-personaltrainer.it](https://www.my-personaltrainer.it/robots.txt) blocks GPTBot, ClaudeBot, PerplexityBot, Google-Extended and more.
  - [focus-tierarzt.de](https://focus-tierarzt.de/robots.txt) blocks GPTBot, ClaudeBot, PerplexityBot and Google-Extended, but allows OAI-SearchBot.
  - None of the 38 fully blocked OAI-SearchBot.
- **llms.txt present on 8 of 40:** dutch.com, akc.org, webvet.com, maven.pet ("Generated by LLMs.txt Generator"), veterinari.it, zooplus.de, hundeo.com, dogcare24.de — e.g. [AKC llms.txt](https://www.akc.org/llms.txt), [zooplus llms.txt](https://www.zooplus.de/llms.txt). It is absent on PetMD, VCA, PDSA, MSD, Cornell, FirstVet and Vetster — e.g. [PetMD llms.txt (404)](https://www.petmd.com/llms.txt).

#### Core Web Vitals benchmarks and page-weight proxies
- **Thresholds:** LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1, measured at the 75th percentile and segmented by mobile and desktop. "INP became a stable Core Web Vital metric in 2024." Lab tools are "not a substitute for field measurement" — [web.dev Core Web Vitals](https://web.dev/articles/vitals).
- **Web Almanac 2025** — [HTTP Archive Web Almanac 2025: Performance](https://almanac.httparchive.org/en/2025/performance):
  - Good CWV on home pages: 45% mobile and 47% desktop. On secondary pages: 56% mobile and 61% desktop.
  - Good LCP: 62% of mobile pages and 74% of desktop.
  - An image is the LCP element on 76% of mobile pages.
- **Raw HTML size and external `<script src>` count** (my fetch; a proxy, not CWV):
  - PetMD articles: 36–50 KB and 7 scripts — [PetMD](https://www.petmd.com/dog/symptoms/why-is-my-dog-limping)
  - MSD: 37–39 KB and 52 — [MSD](https://www.msdvetmanual.com/dog-owners/digestive-disorders-of-dogs/vomiting-in-dogs)
  - Chewy: 175 KB and 48 — [Chewy](https://www.chewy.com/education/cat/food-and-nutrition/why-is-my-cat-not-eating)
  - Purina IT: 39–43 KB and 82–83 — [Purina IT](https://www.purina.it/articoli/cani/salute/parassiti/togliere-zecche-cane)
  - veterinari.it: 70 KB and 79 — [veterinari.it](https://www.veterinari.it/pronto-soccorso/wiki/vomito-cane-cause-rimedi-e-quando-preoccuparsi/)
  - kornat clinic (DE #1): 7 KB and 3 — [kornat](https://kleintierpraxis-kornat.de/pages/blog/articles/katze-frisst-nicht-ursachen-appetitlosigkeit.html)
  - aiveterinary built article: 21 KB, 1 script, no external JavaScript, no images — [local build](file:///home/user/one/aiveterinary/site/dist/animals/cat-straining-litter-box.html)

#### Studies of AI Overviews' impact (methodology published)
- **Ahrefs** (17 April 2025) — [Ahrefs](https://ahrefs.com/blog/ai-overviews-reduce-clicks/):
  - Position-1 CTR was 34.5% lower for keywords with an AI Overview than forecast. Actual CTR was 0.026, against a forecast of 0.040 based on non-AIO informational keywords.
  - Method: 300,000 keywords, desktop Search Console CTR, March 2024 versus March 2025. The study is correlational.
  - An editor's note says the study was re-run for 2026 at a separate URL, which I did not open.
- **Semrush** (updated 15 December 2025) — [Semrush](https://www.semrush.com/blog/semrush-ai-overviews-study/):
  - AI Overviews appeared on 6.49% of queries in January 2025, peaked at 24.61% in July 2025, and stood at 15.69% in November 2025 (about 16%).
  - For the same keywords before and after an AIO appeared, the zero-click rate fell from 33.75% to 31.53%.
  - Method: more than 10M keywords plus Datos clickstream data.
  - The page is internally inconsistent about the Health category and gives no Pets figure.

### Inferences
- **FAQ and HowTo markup.** Do not invest in FAQPage or HowTo markup expecting Google rich results; there are none. Keep the visible question-and-answer sections, because they match Microsoft's guidance and how readers scan, and use FAQPage JSON-LD only if wanted for other consumers. The markup that still has Google payoff or a credibility role is:
  - Article or MedicalWebPage, with `author` and `reviewedBy` as Persons whose `url` points to a ProfilePage, `datePublished`, `dateModified` and `lastReviewed`
  - BreadcrumbList
  - Organization
  - VideoObject or ImageObject where media exist
  All of it must match the visible text.
- **One page style that suits both Google and Bing.** Write normal, well-structured pages (Google: no chunking needed). Use descriptive question H2s with a direct answer in the first sentence or two, lists and tables for steps and thresholds, and keep critical triage text out of collapsed accordions (Microsoft). This reconciles the two vendors.
- **hreflang.** Add `x-default` (e.g. pointing to EN or a language chooser). Keep hreflang only on true translations, reciprocal, with each page listing itself. This is cheap and beats most leaders observed.
- **Crawler policy.** For a zero-budget site whose growth depends on answer engines, robots.txt should explicitly allow Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot and Claude-SearchBot/Claude-User. Decide separately on the training bots (GPTBot, Google-Extended, CCBot); blocking them does not remove the site from ChatGPT search. The current aiveterinary robots.txt is `User-agent: * Allow: /`, which already permits all of them — [aiveterinary robots.txt](file:///home/user/one/aiveterinary/site/public/robots.txt). An llms.txt is optional: Google ignores it, but 8 of 40 pet sites publish one, AKC and zooplus among them.
- **Search Console setup.** After verifying the site, confirm the "Search generative AI" setting is on Include and watch the Generative AI performance report. Consider the preferred-sources button only if Google's extra JavaScript is acceptable, since it adds a third-party script to an otherwise script-free page.
- **Performance.** A static Astro page of about 21 KB with no third-party JavaScript should already be lighter than any leader measured. The main CWV risk once images are added is LCP: images are the LCP element on 76% of mobile pages. Use responsive, sized, compressed images, preload any hero image, and keep cookie or consent tooling light.

### Gaps
- No field CWV data (CrUX) for leader URLs: the PageSpeed Insights API returned "Quota exceeded … Queries per day" for anonymous use — [PSI API](https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2Fwww.petmd.com%2Fdog%2Fgeneral-health%2Fdog-throwing-up-yellow-bile&strategy=mobile&category=performance). Lighthouse was not run locally.
- The Bing Webmaster Guidelines text was not readable, and the IndexNow documentation was not opened. Bing's own statements on AI-generated content come only via Microsoft's October 2025 blog post.
- msdvetmanual.com and vets-now.com returned robots.txt without parseable User-agent groups to my fetch, so their AI-crawler policy is unknown. The robots parsing was automated and may mis-handle unusual group syntax.
- I did not measure the share of AI-answer citations that pet-health domains get in Google AI Overviews, ChatGPT, Perplexity or Copilot. No such study was opened, and SISTRIX (DE) and SEOZoom (IT) data were not obtained.
- I did not open Ahrefs' 2026 re-run or any vertical breakdown for "Pets & Animals" or "Health".

## 5. Conversion, onboarding and accessibility (WCAG 2.2 AA; European Accessibility Act)

### Takeaway
Owner-facing telehealth and app sites convert with a single, short promise of reassurance ("24/7 online vet care", "Trusted vet care. Within minutes.", "Talk to someone you can trust, anytime.") and one dominant call to action ("Talk to a vet", "Get help now", "Hausbesuch buchen", "Jetzt Termin buchen"). Around it they place three-step "how it works" strips, prices or an insurer-coverage check, app-store badges, and social proof given as counts and ratings (900,000+ pet parents, 4.9/5, Trustpilot, "über 143 mobile Tierärzte"). Information sites convert through free tools and newsletters, not sign-up walls. Vet AI-scribe SaaS uniformly pairs "Book a demo" with a free trial or $0 tier, public pricing, a time-saved promise, and security badges (SOC 2, HIPAA, GDPR). On accessibility, WCAG 2.2 adds 9 success criteria (6 at levels A or AA). The EAA covers "e-commerce services" (consumer contracts) and exempts microenterprises providing services, so a free, non-transactional information site run by a microenterprise is likely outside its scope. WCAG 2.2 AA remains the sensible target.

### Cited Findings

#### Owner-facing telehealth, app and information homepages (2026-10-18)
- **Dutch** — [Dutch](https://www.dutch.com/):
  - H1 "24/7 online vet care for dogs and cats"; "We'll see your pets today, not in two weeks."; "Get care & prescriptions for 150+ pet issues"
  - Visible prices; app-store links; email inputs
  - Social proof: "900,000+ pet parents", "4k+ reviews"
  - FAQ accordions ("How much does Dutch cost?", "Are vets at Dutch licensed veterinarians?")
- **Vetster** — [Vetster](https://vetster.com/en):
  - H1 "Stop stressing about your pet's health with 24/7 online vet care"
  - Differentiator: "Only Vetster lets you choose the veterinarian who will treat your pet"
  - "Developed alongside vets, loved by pet parents"; app-store links; a LegitScript verification link
- **FirstVet US** — [FirstVet US](https://firstvet.com/us):
  - H1 "Woof there it is! Pet care in your pocket"
  - Three steps: "Set up your pet's profile → Book your appointment with the vet → Get the right advice and follow-up care"
  - Audience switch: "As a pet parent / As an employer / As an insurer"
  - Calls to action "Get help now", "Get started", "Talk to a vet"; prices such as "$15.99 per mo"
- **FirstVet DE** — [FirstVet DE](https://firstvet.com/de):
  - "In 3 einfachen Schritten zur tierärztlichen Videosprechstunde"
  - Insurer coverage: "Versichert bei einem unserer Versicherungspartner? Dann sind FirstVet Videosprec[hstunden …]"
  - "Tipp: Registriere dein Haustier noch heute"; app-store links
- **Pawp** — [Pawp](https://pawp.com/):
  - H1 "Talk to someone you can trust, anytime."
  - Calls to action "Get Started" and "Download app"
  - Testimonial as an H2: "Saved my best friend's life. Thank you so much Pawp!"
- **Joii (UK)** — [Joii](https://www.joiipetcare.com/):
  - H1 "Trusted vet care. Within minutes."; "Nearly 70% of cases our vets see are fully resolved online."
  - Coverage check: "Check if you're covered" / "Am I covered?"
  - Social proof: "420k+ pet parents", Trustpilot
- **felmo (DE mobile vet)** — [felmo](https://felmo.de/):
  - "Entspannte Hausbesuche vom Tierarzt"; postcode check "Finde raus, ob felmo auch zu dir nach Hause kommt!"
  - Call to action "Hausbesuch buchen"
  - Social proof: "4.9/5", "Unser Team mit über 143 mobilen Tierärzten"
- **Pfotendoctor (DE online vet)** — [Pfotendoctor](https://pfotendoctor.de/):
  - "Online-Tierarztbesuch per Smartphone"
  - Calls to action "Jetzt Termin buchen", "Sprechstunde buchen"
  - "Über 30 Tierärzte sind täglich für dich da"; Trustpilot; app-store links
- **PetVitals (IT, AI app)** — [PetVitals](https://petvitals.katreo.com/it):
  - H1 "La loro salute, sempre con te."; "Un'app per la salute del tuo animale che funziona come un quaderno…"
  - Call to action "Scopri le funzioni"; free tools; app-store links
- **webvet** — [webvet](https://www.webvet.com/):
  - H1 "Vet-Reviewed Pet Health, Without the Guesswork"
  - Newsletter "Vet-Reviewed Pet Health in Your Inbox" (email field); "Make a plan for my pet"
- **veterinari.it** — [veterinari.it](https://www.veterinari.it/):
  - Directory search ("Cerca il veterinario…"); "Entra nella Chat"; "ISCRIVITI ORA"
  - Social proof: "1.000+"
- **maven** — [maven](https://maven.pet/):
  - "A clinically validated pet health tracker"; "$13.99 /mo"
  - Social proof: "4.8 /5", "551 reviews"
- **PetMD** shows a persistent "Chat free with Chewy's vet team" banner above content — [PetMD symptom checker](https://www.petmd.com/symptom-checker).

#### Vet-facing AI scribe / practice-management SaaS (relevant to the vet documentation tool)
- **ScribbleVet** — [ScribbleVet](https://www.scribblevet.com/):
  - "Type less. Heal more."
  - "Book a demo" plus "Start your free trial"; 14-day trial; plans "Essential" and "Unleashed"
  - "Trusted by thousands of veterinarians"
- **Scribenote** — [Scribenote](https://www.scribenote.com/):
  - "AI for veterinarians who love practicing, not paperwork."; "Effortless notes in 3 simple steps"
  - "Get Started for Free" and "Book a Demo"; visible "$0", "$79 /mo" and "$99 /mo" tiers
  - "Join 6000+ veterinarians already using Scribenote."; SOC 2
- **CoVet** — [CoVet](https://co.vet/):
  - "Saving Pet Professionals More Than 2 Hours Every Day"
  - "Try for free", "Get a live demo", "See how it works"
  - SOC 2, GDPR and HIPAA badges
- **Talkatoo** — [Talkatoo](https://talkatoo.com/):
  - "Your Records Done Before Your Next Appointment"
  - "Talkatoo is the #1 rated AI scribe on Capterra. Trusted by 30,000+ veterinary pr[ofessionals]"
  - Demo-led ("Do a Demo Now", "Schedule a Demo")
- **Digitail** — [Digitail](https://digitail.com/):
  - "#1 rated veterinary software by thousands of veterinarians"
  - An on-page "Busy? Get an instant overview of this page:" summary feature; free demo
- **VetRec:** the homepage HTML contains no H1 or calls to action, because content is rendered client-side — [VetRec](https://vetrec.io/).
- The German trade press covers AI scribes for vets: "Eine KI, die mitschreibt – wie groß ist die Zeitersparnis?" — [Vetline](https://vetline.de/).

#### Accessibility: WCAG 2.2 and the European Accessibility Act
- **WCAG 2.2** (W3C Recommendation, 5 October 2023) adds 2.4.11 Focus Not Obscured (Minimum, AA), 2.4.12 (Enhanced, AAA), 2.4.13 Focus Appearance (AAA), 2.5.7 Dragging Movements (AA), 2.5.8 Target Size (Minimum, AA), 3.2.6 Consistent Help (A), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication (Minimum, AA) and 3.3.9 (Enhanced, AAA). It removes 4.1.1 Parsing — [W3C WAI: What's new in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/).
- **EAA scope (Directive (EU) 2019/882)** — [EUR-Lex 2019/882](https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng):
  - Covered services include "e-commerce services" (Art. 2(2)(f)), defined as "services provided at a distance, through websites and mobile device-based services by electronic means … at the individual request of a consumer with a view to concluding a consumer contract" (Art. 3(30)).
  - "Microenterprises providing services shall be exempt from complying with the accessibility requirements" (Art. 4(5)). A microenterprise has fewer than 10 persons and an annual turnover or balance sheet total of at most EUR 2 million (Art. 3(23)).
  - Services provided to consumers after 28 June 2025 are covered.
- **European Commission list of covered items:** computers and operating systems, ATMs and ticketing machines, smartphones, TV equipment, telephony, audiovisual media access, passenger transport, banking, e-books and e-commerce. The page does not mention general information websites — [European Commission: EAA](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en).
- **Germany (BFSG):**
  - Covers "Dienstleistungen im elektronischen Geschäftsverkehr" provided to consumers after 28 June 2025 — [BFSG §1](https://www.gesetze-im-internet.de/bfsg/__1.html).
  - Defines them as digital services offered over websites and apps "auf individuelle Anfrage eines Verbrauchers im Hinblick auf den Abschluss eines Verbrauchervertrags" (§2 Nr. 26), and defines a Kleinstunternehmen as fewer than 10 people and at most EUR 2 million (§2 Nr. 17) — [BFSG §2](https://www.gesetze-im-internet.de/bfsg/__2.html).
  - "Absatz 1 gilt nicht für Kleinstunternehmen, die Dienstleistungen anbieten oder erbringen." — [BFSG §3](https://www.gesetze-im-internet.de/bfsg/__3.html)
- **Accessibility and AI agents:** Google notes that semantic HTML helps screen readers, and that browser agents interpret "the accessibility tree" — [Google: AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

### Inferences
- **Owner funnel for aiveterinary (no-budget).** Lead each article and tool with the free action, then offer exactly one next step matched to risk, as Vets Now's calculator does:
  - high risk → "Call your vet now" plus locale poison or emergency contacts
  - moderate → "Prepare a pre-visit brief" (the existing feature)
  - low → "Track it in your pet's booklet"
  The booklet is local-first, so the honest sign-up-free promise ("no account needed, stays on your device") can become the hook, much as competitors use "kostenlos" and "free". An optional email capture works like webvet's newsletter.
- **Wording for each language.** Owners respond to imperative, reassuring calls to action: EN "Talk to a vet" / "Get help now"; DE "Jetzt …" or "… buchen" / "Registriere dein Haustier"; IT "Scopri …" / "Entra …". For a non-telehealth site, honest equivalents would be:
  - EN "Check if it's an emergency" · "Make a vet-visit brief" · "Start your pet's health booklet"
  - IT "Verifica se è un'urgenza" · "Prepara la scheda per il veterinario"
  - DE "Ist es ein Notfall?" · "Tierarztbesuch vorbereiten"
- **Honest social proof.** Use only true, verifiable proof: named reviewing vets with registrations, the number of vet-reviewed articles, and last-review dates. Never invent user counts. The leaders' proof is counts and ratings, but aiveterinary's credible equivalent is transparency about its reviewers.
- **Vet documentation tool.** It should match the SaaS norm: a one-line time-saved promise, a no-card free trial or $0 tier, "Book a demo", public pricing and explicit data-protection claims. GDPR and EU data residency would beat US-centric HIPAA badges for IT and DE vets. The homepage should render its value proposition in HTML; VetRec's client-side-only homepage is an anti-pattern for search.
- **EAA scope.** A free information site run by a microenterprise, with no consumer contract, likely falls outside the EAA and BFSG. Owner accounts or paid features could change that analysis, and this is not legal advice. Even so, WCAG 2.2 AA is low-cost on a static site. It also directly serves search and AI agents, through the accessibility tree and semantic HTML. The new criteria that matter most for aiveterinary:
  - 2.5.8 Target Size and 2.4.11 Focus Not Obscured, for sticky emergency banners and table-of-contents bars
  - 3.2.6 Consistent Help, a contact or emergency link in the same place on every page
  - 3.3.7 Redundant Entry and 3.3.8 Accessible Authentication, for booklet forms and any login (allow password managers or passwordless sign-in)

### Gaps
- In-app onboarding flows (after sign-up) were not observed, because they sit behind apps or JavaScript. No published conversion rates were found.
- I did not open the Italian EAA transposition (D.Lgs. 82/2022), the AgID guidance or the status of the EN 301 549 version (WCAG 2.2 alignment). The European Commission page does not mention EN 301 549.
- I ran no automated accessibility audit (e.g. axe) on leader sites. Only MSD's link to an "essentialaccessibility.com" assistive app was noted ([MSD](https://www.msdvetmanual.com/dog-owners)), with no evaluation of it.
- Some prices captured by pattern matching on the SaaS and telehealth homepages may belong to unrelated page elements. Verify them before quoting exact plan prices.
