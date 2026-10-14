# Design research: benchmark of owner and vet sites (14 Oct 2026)

Method: each page fetched with its linked CSS; fonts read from `@font-face`
and `font-family`, palettes from hex frequency, radii and button CSS from the
stylesheets; structure and copy from the rendered page. Dalma's SVG animals
were downloaded and rasterised to study construction.

Could not load: tails.com (bot challenge). Redirects followed: digitail.io →
digitail.com, provet.cloud → provet.com, co-vet.ai → co.vet, petleo.com →
vet.petleo.net, curala.de → curala.at. "happyvet" is dead; HappyDoc
(happydoc.ai) used instead. "Tandem" resolves to tandemhealth.ai (human
medicine, integrates vet PMS).

## 1. What each site does

| Site | Fonts | Palette | Hero | Visuals | Trust pattern |
|---|---|---|---|---|---|
| petmd.com | Gordita, Roboto/Work Sans | #1C49C4 blue, #121212, #BD2848, #EBF2FF, #FCFCFC | "Welcome to PetMD" + search, article grid | Stock photos | "For Pets. By Vets."; byline "Alison Birken, DVM" with photo; related cards carry the credential; "Was this article helpful?" |
| vcahospitals.com | Avenir, Lato | #164994, #2D2B26, #0059B3, #3EC4E4 | Title + search | Photos | Multi-author byline with DVM, "Last updated on…", disclaimer |
| smalldoorvet.com | Adonis (serif), Gibson | #EA7927 orange, #2F3A49, cream #FDFAF4 | "Exceptional Veterinary Care in NYC, DC, and Boston." + "Book Now" | Photos, one flat cat | AAHA badge, Newsweek, press logos, reviews |
| bondvet.com | Sailec, Inter | #10365A navy, #FF4D4D coral, peach tints | Banner + "Book Now" | Photos | Newsweek badge, Google reviews |
| vetster.com | DM Sans, Inter | #2563EB, #111827, #FF48A8 | "Stop stressing about your pet's health…" + "Talk to a vet" | App screenshots | 4.9 Google / 4.8 Trustpilot, 97 % resolution, named Dr reviews |
| pawp.com | Aeonik Pro | #4E519D indigo, #161414, pill 50px | "Talk to someone you can trust, anytime." | Photos, phone mockups | Media logos; vet credentials spelled out |
| dalma.co | Roslindale Display (serif, 52–62px/1.0), Buenos Aires | #4E68F6, #030C6C navy, #FFB400, #FAC6E3 | "Couvrez-les d'amour, on couvre tout le reste." + "Mon devis en 1 min" | Own two-colour SVG animals | Three store ratings, "60 000 animaux assurés", Trustpilot |
| figopetinsurance.com | IvyPresto (serif 3.5rem/1.1), IvyEpic | #01313D teal, cream #FBF6F1, mint, lime, pills | "Pet Insurance Designed by Pet People" | Photos | Newsweek, Wirecutter, Trustpilot |
| lemonade.com/pet | Lato, Merriweather, Dancing Script accent | #FF0083, #282828, #2AD5BD | "Pet insurance with…" + "Check our prices" | Photos | Store stars |
| firstvet.com/uk | Maison Neue, Obviously Narrow | #005AED, #E76E47, cream #FEFAF4, sage #D3E1C0 | "Your online vet clinic" + 3 bullets + "Book an appointment" | Photos, line icons | 4.9 App Store, 1 million calls, 98 % happy, insurer logos; article byline "Dr Emma Bower, Veterinarian", dates, reading time, TOC |
| petplan.co.uk | Allianz Neo, Montserrat | Allianz blues | "Join the UK's No.1 pet insurer" + proof bullets | Photos, line icons | 97 % of claims paid, 18,260 Trustpilot reviews, Defaqto |
| digitail.com | DM Sans, Caveat accent | #053E4A, #C0D5D9, #F6F6F5, #4B61E2, radius 30px | "The all-in-one software for better veterinary care." + "Book a Demo" | Screenshots | "Trusted by over 10,000 veterinarians", "4.8 #1 Top-Rated", KPI cards |
| scribenote.com | Inter Tight, Inter, Satoshi | #6366F1 indigo, #1E1B4B, #FAFAFA, 20px cards, 100px pills | "AI for veterinarians who love practicing, not paperwork." + "Get Started for Free" | Soft flat illustration: pastel SOAP panels, dog and cat peeking, closed happy eyes | "6000+ veterinarians", testimonials "Dr X, DVM", SOC 2 + ISO 42001 badges, $79/mo/DVM |
| vet.petleo.net (DE) | Fraunces + Karla | ink #0B3B45, teal #3BA4B3, #EDF5F7, coral #FF758C | "Die digitale Plattform für die moderne Tiermedizin." with hand-drawn underline + "Demo buchen" | Screenshots, paw decorations | "Von Tierärzten, für Tierärzte.", clinic logos, EU servers, "ab 39 €" |
| provet.com | Armin Grotesk | #09122A, #3559C7, #9068FE | "Practice management, built for the AI agent era." | Screenshots | "20M+ pets, 55,000+ professionals", ISO 27001 |
| ezyvet.com | EzySans, Caveat | #00337F, #0B6F5E, #F5F5F2, pills | "Built for the way veterinary work actually happens." | Photos, screenshots | "7,000+ practices", "Backed by IDEXX" |
| vetrec.io | Plus Jakarta Sans + DM Sans | #215FED, #0B1430, #FAC503, cream #F8F4EC | "The Best AI Scribe For Veterinary Professionals." + "Try VetRec For Free"; chips "14 Day Free Trial · No Credit Card · 24/7 Support" | Screenshots | Logo wall, SOC 2 / GDPR / HIPAA |
| co.vet | Plus Jakarta Sans + Rubik | #00A3E8, #002D4F, pills | "The Veterinary AI Copilot" + "Try for free" | Screenshots | Named DVM quote, ISO 27001 / SOC 2 / GDPR, 11 languages |
| happydoc.ai | Fraunces (SOFT 100, 3.5rem/600) + Plus Jakarta Sans | #183B56, #32BBC1, #D2F3F5, #FEE7CC, #F9BE19 | "The world's best veterinary AI scribe and assistant" + "Book a Demo" | Screenshots | "99.8 % accuracy", stars |
| curala.at (AT/DE) | Inter Variable + JetBrains Mono | #4A4DFF, #0F172A, #27C4C9, bg #F6F3EF, radius 14px | "KI-Dokumentation … Mehr Zeit fürs Wesentliche" + chips "DSGVO-konform · Server in Innsbruck/EU · kein KI-Training" + "Kostenlos starten" | Photos, screenshots | Chips in hero, press logos, "Tanya Mayer, Tierärztin", free tier; informal "du" |
| tandemhealth.ai/de | Martina Plantijn (serif) + Die Grotesk | #0D0D0D, warm greys, lime | "Ihr KI-Assistent für jeden Schritt der Versorgung" + "Demo buchen" | Video, portraits | MDR IIa, ISO 13485/27001/42001, "Daten in der EU"; formal "Sie" |
| tandem.vet (US clinic) | Suisse Intl | #606060, #F5F5F5, pastel tints, radius 12–24px | "Your vet care companion" + "Book Now" | 3D illustrations | "Trusted by hundreds of families" |

## 2. Shared patterns a zero-budget static site can copy

1. Serif display + grotesk body is the premium signal on both sides (Dalma, Figo, Small Door, HappyDoc, Petleo, Tandem). H1 52–64 px at line-height 1.0–1.1, weight 600–700.
2. Warm off-white page, never pure white; white reserved for cards.
3. One deep ink + one saturated accent + two or three pastel tints. Ink for headings and illustration outlines, never `#000`.
4. Pill or 12 px buttons, 44–48 px tall, bold 14–16 px; primary filled, secondary outline; hover lifts 1–2 px.
5. Cards: 16–24 px radius, 1 px tinted border or flat tint fill, no resting shadow.
6. Sticky nav: 4–5 items + one filled CTA + one text link; language switcher on vet sites.
7. Hero = headline + one-sentence sub + primary CTA + 3 proof chips, two columns, visual right.
8. Ratings or numbers strip under the hero; with no ratings, only counts you can defend.
9. Section rhythm: hero → proof → three steps → feature rows → testimonials → FAQ → closing CTA. Section padding 96–120 px desktop.
10. Trust wording, owner side: byline "Name, DVM", "Last updated", reading time, TOC. Vet side: compliance chips in hero and badges in footer, "built by vets", testimonials titled "Dr X, DVM".
11. CTA phrasing: owner side imperative + benefit; vet side risk-free trial + "Book a demo". Never "Learn more" as primary.
12. One hand-drawn accent on a clean system is enough (Petleo underline, Caveat on Digitail).

## 3. Animal illustration rules (Dalma SVGs, Scribenote, Duolingo guidance)

- Build from rounded primitives, no pointed corners; 15–70 shapes per figure.
- Outline weight 2.5–3 % of figure height, one weight everywhere; or no outline with 10–15 % darker tones.
- Eye diameter 18–22 % of head width, at or just below the vertical midline, one eye-width apart; pupil covers 60–70 % with one highlight upper-left. Pill eyes, not ovals.
- Nose ≈ 25 % of eye size at 65–70 % head height; mouth a single "w"/smile; closed happy eyes are the cheapest expressive variant.
- Ears: dog floppy rounded flaps, one forward in the second colour; cat upright rounded triangles ~35 % of head height with inner-ear accent; rabbit long pills 1.2× head height.
- Head ≈ 40–50 % of total height for a sitting pose; limbs as pills; flat pill shadow beneath; one or two four-point sparkles as the only decoration.
- Palette discipline: one outline ink, one accent, one warm highlight, white.

## 4. Direction adopted for aiveterinary.org

See `06-brand.md` for the implemented tokens. Summary: Fraunces + Plus Jakarta
Sans; cream page, navy-teal ink, teal accent, coral and warm yellow for
decoration only; pill buttons; bordered cards without shadow; sticky nav with
one CTA; two-column hero with own SVG illustration on owner pages and trust
chips on vet pages; proof strip with only defensible claims; species-first
navigation; FAQ accordion; owner tone informal where the language allows, vet
tone formal.
