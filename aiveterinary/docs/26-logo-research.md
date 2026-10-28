# 26 · Logo research: AI Veterinary (aiveterinary.org)

Research brief, 24 Oct 2026. Covers what logos vet and pet-health brands use, what makes a good and registrable logo, and design directions for AI Veterinary.

**Method.** I opened each homepage with `curl -sSL -A 'Mozilla/5.0 … Chrome/120'` (or WebFetch when curl was blocked) and read the logo from the page source: `<img>` alt text and file names, inline SVG `<symbol>`s, favicon links, theme-color meta tags and hex colours in the CSS. I rendered the logo files the page referenced, in a scratch folder outside the repo, so I could describe the motif. No logo files were saved in the repo. All pages were accessed on **2026-10-24**. Where a detail couldn't be seen, the brief says **"not visible"**.

**Our starting point.** The current brand is teal `#14655e` on cream `#fbf7f2` with ink `#12304a`, Fraunces headings, Plus Jakarta Sans text, drawn animal illustrations and a red emergency button. The current favicon (`site/public/favicon.svg`) is **a white paw print on a teal circle**. Part 1 shows this sits squarely in the most crowded motif in the category.

---

## Part 1: What logos vet and pet-health brands use

### 1.1 Brand-by-brand (34 brands checked, 30 described)

| # | Brand (type) | URL opened | Motif | Colours seen | Wordmark |
|---|---|---|---|---|---|
| 1 | **AniCura** (EU clinic group) | anicura.de, anicura.it, anicuragroup.com | **Animal silhouette.** A geometric seated bear/dog-like animal with a drop-shaped nose and a cat on its back, solid fill (`favicon.svg`, `logo-anicura-horizontal.svg`). Also a brand "eyes" glyph (`/svg/brand/eyes.svg`). | Navy `#0e235c` (mask-icon colour); accent `#ebbc4e` in CSS | **Serif**, mixed case "AniCura" |
| 2 | **IVC Evidensia** (EU clinic group) | ivcevidensia.com, ivcevidensia.de | **Animal silhouettes.** A horse, dog and cat running along a curved swoosh line above the name (`logo-ivc-evidensia-white.svg`). The favicon is "IVC / EVI" split by a green wave. | Header logo white on a dark background; green wave in the favicon. Brand hex not visible in the CSS. | Sans, ALL CAPS "IVC EVIDENSIA" |
| 3 | **Medivet** (UK) | medivetgroup.com (www.medivet.co.uk redirects here) | **Monogram.** A pink "M" with a small inverted triangle notch under the centre, like a nose (inline symbol `svg-logoPartners`). | Pink `#d73a60` M, blue `#294597` text | Rounded sans, mixed case "Medivet & Partners" |
| 4 | **Vets for Pets** (UK, CVS/Pets at Home network) | vets4pets.com | **Wordmark only.** Two-colour words; the "P" of Pets has a small leaf-like flick (`vets-for-pets_logo_core-green-and-dark-teal_rgb-1.png`). | Dark teal plus bright green (`#00aa28` in CSS) | Heavy rounded sans, mixed case |
| 5 | **VCA Animal Hospitals** (US, Mars) | vcahospitals.com | **Abstract.** Three small rotated squares (diamonds) in purple, light blue and coral above "animal hospitals" (`vca-animal-hospital-logo.svg`). | Navy wordmark, purple/cyan/coral diamonds | Bold geometric sans, lowercase "vca" |
| 6 | **Banfield Pet Hospital** (US, Mars) | banfield.com | **Cross plus animal silhouette.** An orange plus-shaped cross with white dog and cat profiles cut into it (`Banfield-Pet-Hospital-logo.svg`). | Orange | Sans, "Banfield" mixed case, "PET HOSPITAL" caps |
| 7 | **Mars Veterinary Health** | marsveterinary.com | **Wordmark only** (`mvh-logo.png`) | Royal blue "MARS", red "Veterinary Health" | Sans: "MARS" caps, the rest mixed case |
| 8 | **CVS Group** (UK) | cvsukltd.co.uk | **Wordmark only** (`cvs-logo.svg`) | Bright blue | Bold sans, mixed case "CVS Veterinary Group" |
| 9 | **Ca' Zampa** (IT clinic network) | cazampa.it | **Animal silhouettes in an arch.** A dog and cat drawn in a single red outline inside an arched frame (`Logo-orizzontale_cliniche_veterinarie_rosso.png`). | Red `#e33f33` (dominant CSS colour, 293 uses); `#d3e5e9` light blue support | Condensed sans ("Sofia Sans Condensed" in CSS), ALL CAPS "CA' ZAMPA" with "Cliniche Veterinarie" below |
| 10 | **TiHo Hannover** (DE vet university) | tiho-hannover.de | **Seal / crest.** A round seal with an owl on a shield, ringed by "STIFTUNG TIERÄRZTLICHE HOCHSCHULE HANNOVER" (`logo-tiho.svg`). | Blue `#006ab3` on white | Serif caps set around the seal |
| 11 | **LMU München, vet faculty** (DE). The Kleintierklinik site wouldn't load, so this is the faculty page. | vetmed.lmu.de | **Monogram block.** A green square with white "LMU", next to a green box holding the full name (`Logo_LMU.svg`). | Green / white | Sans, caps |
| 12 | **Bundestierärztekammer** (DE federal vet chamber) | bundestieraerztekammer.de | **Monogram plus Aesculapian staff.** Black "BTK" where the T is a staff with a snake (`logo-btk-xl.png`). | Black monogram, green `#427a3d` text (also the theme-color) | Sans; full name in mixed case |
| 13 | **PDSA** (UK charity) | pdsa.org.uk | **Wordmark only.** Two-colour lowercase "pdsa" with the tagline "THE VET CHARITY FOR PETS IN NEED" (`pdsa_logo_main.png`). | Teal `#00bcb4` "pd", pink "sa" | Rounded sans, lowercase |
| 14 | **RSPCA** (UK charity) | rspca.org.uk | **Wordmark with a full stop**, "RSPCA."; the favicon puts it inside a thin circle on a blue square (`favicon.svg`). | Cream `#fff2e2` on royal blue `#2622f7`; deep purple `#260071` in CSS | Heavy grotesque sans, CAPS |
| 15 | **FirstVet** (SE/EU tele-vet) | firstvet.com | **Video camera containing a cross.** A blue rounded video-camera shape with a plus/cross cut out (`apple-touch-icon.png`). Header wordmark not visible: no logo `<img>` or SVG in the server HTML. | Blue `#0061ff` | not visible |
| 16 | **Vetster** (CA/US tele-vet) | vetster.com | **Abstract "V" chevron** (`vetster-logo-dark.svg`) | Hot-pink V, navy `#11294c` text | Bold sans, mixed case |
| 17 | **Joii Pet Care** (UK tele-vet) | joiipetcare.com | **Lettermark with motion marks.** "joii" in rounded lowercase with three short curved strokes by the "j" (inline SVG `joii-header-logo`). | Muted blue `#344d80` | Rounded geometric sans, lowercase |
| 18 | **Pawp** (US tele-vet) | pawp.com | **Character face.** A pink circle with a winking pet face (`webclip-pawp.png`, wordmark SVG). | Pink circle, black wordmark; purple `#4e519d` in CSS | Geometric sans, lowercase "pawp" |
| 19 | **Dutch** (US tele-vet) | dutch.com | **Monogram.** A black calligraphic serif "D" on yellow (`favicon-BC85xQlj.svg`). Full wordmark not visible (server HTML has none). | Yellow / black; green `#69cc67` in CSS | not visible |
| 20 | **Petriage** (US triage/telehealth) | petriage.com | **Speech bubble plus cross.** A red speech bubble with a white plus cross (`Petriage-Logo.svg`). | Red plus black | Sans, lowercase "petriage" |
| 21 | **Figo** (US insurer) | figopetinsurance.com | **Wordmark with a pet tag.** "FIGO" where the O becomes a collar ring holding a shield-shaped tag (`figo-logo-light.svg`). | Cream on deep teal `#01313d`; mint tag `#95e6e2`; lime `#e6f972` accent | Light geometric sans, CAPS; site serif is "ivypresto" |
| 22 | **AGILA** (DE insurer) | agila.de | **Animal heads in a circle.** Line-art dog and cat heads in a ring (`logo.png`). | Blue `#004ea0` | Thin sans, CAPS "AGILA" with "Haustierversicherung" below |
| 23 | **Petplan** (UK insurer, Allianz) | petplan.co.uk | **Wordmark only** (`petplan_logo.svg`) | Blue | Bold italic sans, mixed case |
| 24 | **Allianz Tierversicherung** (DE insurer) | allianz.de/recht-und-eigentum/tierversicherung/ | **Abstract corporate eagle.** Stylised vertical bars in a ring next to the wordmark (`allianz-logo.svg`); no pet motif. | Blue `#003781` | Bold sans, mixed case |
| 25 | **Zoetis** (animal health) | zoetis.com | **Wordmark with a swoosh** underline (`zoetis_logo.svg`) | Orange | Lowercase, slanted rounded sans |
| 26 | **MSD Animal Health** | msd-animal-health.com (via WebFetch; logo PNG fetched) | **Abstract symbol.** A teal circular mark with cut-out shapes, plus "MSD Animal Health" (`MSD_tcm247-226478.png`). | Teal symbol, dark slate text | Sans; "MSD" caps |
| 27 | **IDEXX** (diagnostics) | idexx.com | **Wordmark only.** "IDEXX" in heavy caps cut by horizontal stripes (`logo-white.…svg`). | White on dark `#30353e` (theme-color); blue `#0b76f0` in CSS | Extended sans, CAPS |
| 28 | **TASSO** (DE pet registry) | tasso.net | **Paw print in a letter.** A red "TASSO" where the final O holds a yellow paw (`tasso-logo.svg`). | Red / yellow | Sans, CAPS |
| 29 | **FINDEFIX** (DE registry, Deutscher Tierschutzbund) | findefix.com | **Line-drawn animal.** A lime single-line dog/cat figure behind the word, with a small blue heart at the chest (`Findefix_website_Logo_rgb_2.svg`). | Grey wordmark, lime line, blue heart | Sans, CAPS |
| 30 | **Europetnet** (EU registry network) | europetnet.org (redirect from .com) | **Wordmark only.** "EUROPETNET" with "PET" bold (`EPN-logo.png`). | White logo on dark; cyan `#00baf2` in CSS | Rounded sans, CAPS |

**Opened but unusable, or not opened (no description given):**
- **Blue Cross** (bluecross.org.uk): 403 from both curl and WebFetch.
- **Boehringer Ingelheim Animal Health**: an Incapsula bot challenge page (212 bytes) on `/animal-health` and `/de`.
- **Prima** (prima.it): 403.
- **I‑Vet** (i-vet.it): connection failed / 503. `ivet.it` is an empty "Index of /".
- **LMU Kleintierklinik** (lmu-kleintierklinik.de and the vetmed sub-domain): 502 from the proxy, so the faculty page was used instead.
- **Chewy Vet Care**: 404 on the vet-care URL and 429 on the homepage.
- **AniCura via anicura.com**: this opened **an unrelated US pet-skincare shop ("Anicura Natural Pet Solutions USA")**, not the AniCura clinic group. That is a small reminder that `.com` collisions happen even for big EU brands. AniCura is described from anicura.de, .it and anicuragroup.com instead.

### 1.2 What's crowded

Counted over the 30 brands above:

| Motif | Count | Who |
|---|---|---|
| **Wordmark only** (no symbol) | 10 | Vets for Pets, Mars VH, CVS, PDSA, RSPCA, Petplan, Zoetis, IDEXX, Europetnet, plus Allianz as a corporate case |
| **Dog/cat silhouette or line art** | 7 | AniCura, IVC Evidensia, Banfield, Ca' Zampa, AGILA, FINDEFIX, plus Pawp's face |
| **Cross / plus** | 3 | Banfield (orange cross), FirstVet (blue plus in a camera), Petriage (**white cross on red**) |
| **Paw print** | 1 here, and very common in the wider category | TASSO; **also our own current favicon** |
| **Heart** | 1 | FINDEFIX |
| **Monogram / letter** | 5 | Medivet, Dutch, LMU, BTK, Joii |
| **Speech bubble** | 1 | Petriage, combined with a cross |
| **Abstract symbol** | 4 | VCA diamonds, Vetster V, MSD, Allianz |
| **Seal / crest / staff** | 2 | TiHo, BTK (Aesculapian staff) |
| **Pet tag / collar** | 1 | Figo |

**Colour crowding.**
- **Blue/navy** is the default (AniCura, VCA, CVS, Mars, AGILA, Petplan, Allianz, Vetster, FirstVet, TiHo, Joii).
- **Teal/green** is the second cluster: PDSA teal, Vets for Pets green/teal, MSD teal, BTK green, LMU green, Figo deep teal, and **AI Veterinary teal `#14655e`**.
- **Red/orange** is used by Ca' Zampa, TASSO, Banfield and Zoetis; Petriage pairs red with a white cross.
- **Pink** is the "friendly tele-vet" signal: Vetster, Pawp, Medivet, PDSA.
- **Cream/off-white backgrounds** are now common among the premium brands (Figo `#fbf6f1`, RSPCA `#fff2e2`), the same cream we use.

**Type crowding.**
- Rounded or geometric **sans** in lowercase or mixed case is the norm.
- Only **AniCura** (serif "AniCura") and **TiHo** (serif seal) use a serif in the logo. **Dutch** uses a calligraphic serif letter, and Figo uses a serif only on its site, not in the logo.

### 1.3 Where there is open space

1. **A serif wordmark with a crafted detail.** Almost nobody here uses one (AniCura is the exception, and it's institutional navy). We already use Fraunces, a soft, characterful serif. Few brands in the set occupy this space, and it reads as "editorial and trustworthy" rather than "app".
2. **Symbols about *guidance* rather than *the animal*.** No brand in the set shows "direction / next step / signal" (an arrow, a waypoint, a three-level indicator). Every symbol is either the animal (paw, silhouette, face), medicine (cross, staff) or abstract. Our promise, "know what to do: go now / today / watch", is a **decision**, and that's unclaimed.
3. **A booklet, page or record motif.** No pet-health logo in the set references the record or booklet, yet the local-first health booklet is a core product.
4. **Teal plus warm accent on cream, *without* a cross or paw.** Teal alone is shared with PDSA, MSD and Figo. A teal mark with a distinctive *shape* (not paw, cross or heart) would still separate us. Red must stay reserved for the emergency button (see 2.3).
5. **A monochrome-first mark.** Several brands depend on two colours to read: PDSA, Vets for Pets, Mars, Medivet. A mark that's fully legible in one colour is more robust and themes better (Android/iOS tinted icons, dark mode).

---

## Part 2: What makes a good logo

### 2.1 Sources opened

| Source | What it says (quoted or summarised from the page) |
|---|---|
| **NN/g, "Icon Usability"** (Aurora Harley, 27 Jul 2014), nngroup.com/articles/icon-usability/ | Few icons are universally recognised, and hearts and stars have inconsistent meanings. Quote: "a text label must be present alongside an icon to clarify its meaning in that particular context". Quote: "Test the icons for recognizability: ask people what they expect the icons to stand for." It also recommends retesting memorability after a couple of weeks. |
| **Apple HIG, "App icons"** (read via Apple's documentation JSON for developer.apple.com/design/human-interface-guidelines/app-icons) | "Embrace simplicity in your icon design. Simple icons tend to be easiest for people to understand and recognize." It asks you to express one concept "in a simple, unique way with a minimal number of shapes". "Include text only when it's essential to your experience or brand. Text in icons doesn't support accessibility or localization…" It mentions that "a mnemonic like the first letter of your app's name can help". Icon Composer annotates "default, dark, and mono appearance variants". Prefer vector (SVG/PDF). |
| **Android Developers, "Adaptive icons"** (developer.android.com/develop/ui/views/launch/icon_design_adaptive) | "If you want to support user theming of app icons, provide a single layer for the monochrome version of the icon." "Starting with Android 16 QPR 2, Android automatically themes app icons for apps that don't provide their own." The logo should be at least 48×48 dp and must not exceed the 66×66 dp safe zone inside 108×108 dp layers. |
| **Google Search Central, "Favicon in search results"** (developers.google.com/search/docs/appearance/favicon-in-search) | "Your favicon must be a square (1:1 aspect ratio) that's at least 8x8px. … we recommend using a favicon that's larger than 48x48px". The favicon should be "visually representative of your website's brand", and its "URL must be stable". |
| **W3C, Understanding SC 1.4.3 Contrast (Minimum)** (w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Logotypes: "Text that is part of a logo or brand name has no contrast requirement." Body text 4.5:1, large text 3:1. |
| **W3C, Understanding SC 1.4.11 Non-text Contrast** (via WebFetch) | 3:1 for UI components and graphics, but "Logos are exempted from contrast requirements". That exemption does **not** cover logos the author deliberately shows in low contrast. |
| **Vistaprint "How to Design a Logo: The Ultimate Guide"** (the old 99designs blog URL now redirects to vistaprint.com/hub/how-to-design-logo) | "Don't give in to the clichés of your industry. A dentist doesn't need to have a tooth in their logo…" "Simplicity is key for a memorable (and printable) logo." Its checklist asks: "Is it versatile? … Does it set you apart from your competitors?" |
| **EUIPO Common Practice CP3: Distinctiveness of figurative marks containing descriptive/non-distinctive words** (practice paper PDF on euipo.europa.eu, as adopted by the BiH IP Institute) | A figurative element is non-distinctive if it is "a true-to-life portrayal of the goods and services" or "a symbolic/stylised portrayal … that does not depart significantly from the common representation". Elements with a "direct link with the characteristics of the goods and services" don't add distinctiveness "unless it is sufficiently stylised". Descriptive words combined with "simple geometric shapes such as points, lines … circles, triangles, squares" are "unlikely to be acceptable", especially as a frame or border. |
| **EUIPO Guidelines, Part B §4 ch. 9, Art. 7(1)(h)/(i) EUTMR** (2017 draft PDF on euipo.europa.eu; the current consolidated version wasn't opened) | The protected list includes "the symbols protected under the Geneva Conventions … the red cross, the red crescent and the red crystal emblems and their names". Examples include an EUTM **cancelled** because it "clearly contains the emblem of the Red Cross on a white background". Traditional crosses (Templar, Maltese) are not treated as imitations. |
| **Germany, § 125 OWiG** (gesetze-im-internet.de/owig_1968/__125.html) | Unauthorised use of "das Wahrzeichen des roten Kreuzes auf weißem Grund" or the names "Rotes Kreuz"/"Genfer Kreuz" is an administrative offence. Signs "die ihnen zum Verwechseln ähnlich sind" (confusingly similar) are treated the same, and the offence carries a fine. |
| **UK, Geneva Conventions Act 1957 s.6** (legislation.gov.uk) | It is not lawful, without the Secretary of State's authority, to use "for any purpose whatsoever" a red cross with equal arms on a white ground. The section also covers the red crescent, the red crystal, and the protocol's medical identification signals. |
| **Italy: Croce Rossa Italiana leaflet "Tutelare l'Emblema"** (cri.it/wp-content/uploads/2023/04/Pieghevole_Emblema.pdf) | Misuse means "qualsiasi utilizzo non autorizzato di una croce rossa su fondo bianco". Typical examples are "marchi commerciali o loghi … kit di primo soccorso, ambulatori medici". "Anche l'utilizzo di un simbolo simile alla croce rossa è da considerarsi un abuso", i.e. imitation by shape and/or colour. The statute itself (L. 740/1912 on normattiva.it) couldn't be opened. |
| **ICRC blog "What are the provisions of IHL governing the use and protection of the emblem?"** (blogs.icrc.org/ilot/2017/08/14/…) | "Any use of the emblem, during armed conflict or in peacetime, that is not expressly authorized by IHL constitutes misuse". Misuse includes **imitation** (a sign that "by its shape and/or colour, may cause confusion") and **usurpation** by "commercial enterprises, medical establishments or pharmacies". |
| **Canva Content License Agreement** (canva.com/policies/content-license-agreement/; canva.com returns 403 to curl/WebFetch, so read through the r.jina.ai text mirror of that URL) | **§9 Prohibited uses, item 2:** "You definitely can't do these things with any free or Pro Content on Canva: … use any of the Content as part of a trade-mark, design-mark, trade-name, business name or service mark (excluding fonts)". **§9 item 13:** no "claiming ownership of, or exclusive rights to, the Content". **§2 / Pro licence:** both licences are "non-exclusive". **§9 item 7(e):** no use of Content depicting people "in advertisements or promotional materials for pharmaceutical or healthcare, herbal or medical products". The mirror didn't show a "last updated" date. |

### 2.2 Checklist for the AI Veterinary mark

Score every candidate against this list. Anything failing a **must** is out.

**Must**
1. **Simple.** One idea, made of a minimal number of shapes (Apple HIG). It should be possible to draw from memory after one look.
2. **Works at 16 px.** The symbol alone must read as a 16×16 favicon and a 32 px tab icon, and fit inside Android's 66 dp safe zone. No hairlines, no text inside the symbol, no detail smaller than about 2 px at 32 px.
3. **One colour.** It must work in solid ink, in solid white on teal, and as a single-layer monochrome (Android themed icons, iOS tinted/mono, fax, embroidery, stamps on the printed booklet).
4. **Dark mode.** It must work on `#12304a` ink and on near-black. The teal needs a lighter dark-mode variant, because `#14655e` on dark backgrounds is low-contrast. WCAG exempts logos, but don't rely on that for the *UI around* the logo.
5. **Not a protected or forbidden sign.**
   - No red cross on white, and nothing **confusingly similar by shape or colour**: no red plus, no white plus on red (DE §125(3) OWiG; CRI "imitazione"; ICRC "imitation").
   - No Swiss coat of arms (also covered by §125(2) OWiG).
   - No red crescent or red crystal.
   - **Implication:** the plus/cross is legally risky in red and **semantically crowded** in any colour (Banfield, FirstVet, Petriage). Avoid it entirely, and keep our red strictly for the emergency button.
6. **Registrable.** The figurative element must not be a true-to-life or only lightly stylised dog, cat, paw or stethoscope for vet services (CP3). Don't rely on a plain circle or square frame around descriptive words (CP3). "AI Veterinary" as words is likely to be judged descriptive for vet-information services, so **distinctiveness has to come from the symbol and the letterforms**. That needs a trade-mark attorney's check before filing (EUTM or national DE/IT).
7. **No Canva or stock elements in the mark.** Canva §9(2) forbids using Content in a trade mark (fonts excepted). Any template-made logo can't be owned or enforced. The same applies to icon-pack and stock-vector motifs, which are licensed non-exclusively.

**Should**
8. **Distinct from the set in 1.1.** Avoid paw, heart, cross, dog/cat silhouette, pink face and a plain wordmark in blue. Do the "squint test": put the mark at 32 px next to the 30 favicons and check that it can't be mistaken for any of them.
9. **Meaning tied to the promise.** It should say *clarity → a decision → calm*, i.e. "know what to do", not "AI" and not "medicine".
10. **Reads well in EN, IT and DE.**
    - Don't add words in the mark itself.
    - In sans fonts, **"AI" can be misread as "Al" (A + lowercase L)**. Set it in Fraunces, where the capital I has serifs, or add a slight space or weight difference.
    - Italian uses "IA" and German uses "KI" for AI, so "AI" reads as an English term in both. That's acceptable but not native; don't build puns on it.
    - Any extra syllable or initials need checking for unwanted meanings in all three languages before use.
11. **Recognisable and tested.** Run the NN/g method: ask 5–8 owners per language what the symbol stands for, then recheck memorability two weeks later. Always pair the symbol with the wordmark in navigation (NN/g: labels).
12. **Durable.** Vector source (SVG), stable favicon URL (Google), no trend effects (gradients or glass belong in the app-icon layer, not the core mark).

---

## Part 3: Implications and directions for AI Veterinary

### 3.1 Design directions (ranked)

1. **"Three-step signal" mark.**
   - Three stacked or stepped bars or dots of decreasing weight, a quiet nod to *go now / today / watch*, drawn in teal as a single shape.
   - **Why it stands out:** nobody in the set encodes a decision. It ties to the core triage feature, is purely geometric yet specific enough to be stylised (CP3), and survives 16 px and one colour.
   - **Watch out:** don't make it a traffic light. Red/amber/green reads as alarm and would collide with the emergency-button red.
2. **Fraunces wordmark with one custom detail.**
   - "AI Veterinary" set in Fraunces SOFT, with one owned detail: a soft ear-shaped terminal on the "y", or the dot/counter of a letter shaped like a small leaf or tick.
   - **Why:** serif wordmarks are nearly unused (only AniCura and TiHo). It's already our display face, it fixes the "Al/AI" ambiguity, and it reads editorial and trustworthy.
   - **Weakness:** it needs a separate symbol for the favicon (see 1, 3 or 4).
3. **Open-booklet mark.**
   - Two facing pages forming a soft shape; the gutter could suggest an ear or a calm "V".
   - **Why:** it references the local-first health booklet. No competitor uses a record or book motif, it's not a depiction of the animal (registrable), and it bridges owners and vets, since documentation is the vet-side product too.
4. **Waypoint / "next step" arrow.**
   - A rounded chevron or path marker that turns a corner, meaning "here's where you go next".
   - **Why:** it claims direction and guidance. It's distinct from Vetster's V (pink, sharp) as long as it's rounded, teal and asymmetric.
5. **Monogram "av" in Fraunces.**
   - A ligature of lowercase *a* and *v*, where the v's arms read faintly as alert ears.
   - **Why:** Apple notes a first-letter mnemonic helps recognition. It's a strong favicon and a custom ligature, so ownable; the ear hint stays abstract enough to avoid the "stylised animal" trap.
   - **Check:** it must not resemble Vetster's V or Medivet's M-with-nose; test it side by side.
6. **Speech-mark / quotation-mark ear.**
   - An opening quotation mark shaped so it also reads as a pet's ear: "plain language" plus animal, in one stroke.
   - **Why:** Petriage uses a speech bubble, but with a cross and in red. A quote-mark without a bubble or cross is different and ties to "pet health in plain language" (the home title in all three languages).
7. **Teal-on-cream "badge" system for print and booklet.**
   - Whichever symbol wins, define a solid teal tile version (white symbol) and an ink line version. Use the warm accent `#ffb400` / coral only as a tiny secondary dot, never as a second required colour.
   - **Why:** it keeps the mark monochrome-first, which sets us apart from the many brands that depend on two colours (PDSA, Mars, Medivet, Vets for Pets).
8. **Keep the drawn animals *out* of the logo and *in* the illustrations.**
   - The friendly illustrations already give warmth and animal presence. The logo can then be the calm, geometric anchor.
   - This also avoids the crowded silhouette cluster (AniCura, IVC, Banfield, Ca' Zampa, AGILA, FINDEFIX).

### 3.2 Avoid

- **Paw prints**, including the current favicon. It's the category's most generic sign and is weak under CP3 as a stylised depiction tied to pet services. Replace it.
- **Any cross or plus**, red or otherwise. Red or white-on-red is legally restricted (DE §125 OWiG, UK GCA s.6, IT/CRI, EUTMR 7(1)(h)/(i) practice), and any colour is crowded (Banfield, FirstVet, Petriage).
- Hearts, stethoscopes, the Aesculapian staff (signals a licensed professional body like BTK; misleading for an info site) and the caduceus.
- **"AI" clichés:** robot heads, sparkles/✦, circuit brains, chat bubbles with dots. They make it look like a chatbot that replaces the vet, the exact tension noted in `docs/06-brand.md`.
- **Red as a brand colour.** Red stays reserved for the emergency button so "red = go now" keeps its meaning.
- **Canva templates, icon-pack glyphs and stock vectors** anywhere in the mark (Canva §9(2)).
- **Text inside the symbol**, gradients in the core mark, and two-colour dependence.

### 3.3 The name: does "AI" help or hurt trust?

Only survey data I opened:

- **RSPCA / Scottish SPCA / Ulster SPCA, Animal Kindness Index 2026** (YouGov; 5,797 UK adults plus 1,189 children; rspca.org.uk/whatwedo/latest/kindnessindex/2026 and the report PDF).
  - "One-tenth (10%) of pet owners now seek advice and support around looking after their pet from artificial intelligence sources, such as ChatGPT, Gemini, Claude and Perplexity", while "vets (64%) still remain the primary source of advice".
  - Among AI users, the top use is checking "symptoms when pets are unwell (62%)".
  - The report calls this "a significant concern", citing "'hallucinations', where systems present incorrect or misleading information as fact", especially "in urgent or stressful situations".
  - The index page frames AI as "emerging as a new concern".
- **Talker Research for Darwin's pet food** (2,000 pet owners; country not stated in the article; Talker News article "What recommendations are pet parents getting from AI?", 31 Aug 2026, via chronicleonline.com).
  - 43% have used AI tools for pet health or nutrition information, and 54% of those asked about symptoms or illness.
  - "71 percent … say veterinarians remain their most trusted source … compared to just 14 percent who rely primarily on AI tools." "When advice conflicts, 64 percent say they follow their vet, while only 12 percent side with AI."
  - Note: commissioned by a pet-food brand.

**Reading.**
- "AI" in the name is **a clarity win and a trust cost** with owners. Owners are using AI, and the RSPCA's 10% is rising enough to be flagged, but they trust vets far more. The most visible UK animal charity is publicly framing AI pet advice as a risk.
- Our content (vet-reviewed triage, "go now" escalation) is the *answer* to that concern. The name, though, makes people assume the opposite until they read further.

**Implications.**
- (a) The logo should carry **no AI iconography**. Let the symbol say *guidance and calm* and let the serif wordmark say *editorial and trustworthy*.
- (b) Pair the name with a visible reassurance line in all three languages: who reviews the content, and "we tell you when to go to the vet".
- (c) Visually de-emphasise "AI" in the wordmark: same weight as the rest, with no colour pop on "AI".
- (d) Keep a fallback. If owner testing shows a trust drop, a symbol-led identity lets the owner site lean on the mark while "AI Veterinary" remains the company/vet-tool name. That's a naming decision to test with owners, not one to make internally.

---

## Part 4: Trade-mark note on the final logo (25 Oct 2026)

The owner chose concept D2: two white paw prints walking up and to the right on a coral tile, with "AI Veterinary" and the tagline (`docs/06-brand.md`, "Logo"). §3.2 above advised against paw prints. This note says plainly what the choice means for protection. It is not legal advice, and no clearance search has been run yet.

### The symbol on its own is weakly distinctive

- **Paw prints are among the most common signs in the pet sector.** Pet shops, food brands, insurers and registries all use them (TASSO in Part 1), and so did our old favicon.
- **CP3 (quoted in Part 2.1) gives little weight to standard drawings.** It treats a stylised picture that "does not depart significantly from the common representation" of the services as non-distinctive. Our prints are cleanly drawn, but they are still recognisably ordinary paw prints.
- **The tile adds little.** It is a plain rounded square. CP3 says descriptive words combined with "simple geometric shapes", squares among them, are "unlikely to be acceptable".
- **What is ours is the combination:** two prints turned 22° and walking diagonally, the particular pad drawing, and the coral tile. At best that is narrow protection of a look. It cannot stop anyone else from using paw prints.

### The words are descriptive

Regulation (EU) 2017/1001 (EUTMR), Article 7(1), lists signs that "shall not be registered", including:

- **(b)** "trade marks which are devoid of any distinctive character";
- **(c)** "trade marks which consist exclusively of signs or indications which may serve, in trade, to designate the kind, quality, quantity, intended purpose, value, geographical origin or the time of production of the goods or of rendering of the service, or other characteristics of the goods or service".

How these apply to us:

- **(c), descriptive.** For veterinary information services, "AI Veterinary" names the kind of service: veterinary information made with AI. A word mark that only describes the service also has no distinctive character, so expect **(b)** to be raised alongside **(c)**. That is our reading; the lawyer confirms it.
- **Art. 7(2): German and Italian readers don't help.** Refusal applies "notwithstanding that the grounds of non-registrability obtain in only part of the Union". English is an official language in Ireland and Malta, and "AI" is widely understood across the EU. So the fact that German and Italian say "KI" and "IA" does not rescue the words.
- **Art. 7(3): a later route through use.** Grounds (b), (c) and (d) "shall not apply if the trade mark has become distinctive in relation to the goods or services for which registration is requested as a consequence of the use which has been made of it". That needs proof of substantial use and is years away.

### What would be filed

- **The combined figurative mark:** the coral tile with the two prints, plus "AI Veterinary" in its drawn letterforms (the horizontal lockup, probably without the tagline). The tagline "Know what to do for your animal" is a promotional phrase with little distinctiveness of its own.
- **Protection would be narrow.** It would cover the overall look, not the words and not paw prints in general. Others could still use "AI" and "veterinary" in their own get-up.
- **Classes** are for the lawyer to set. The likely candidates are 44 (veterinary information), 42 (software for veterinary teams) and 9 (an app).
- **Colour or black and white:** decide with the lawyer.

### Before filing

1. **Clearance search** in EUIPO eSearch plus, TMview and the national registers (DPMA, UIBM):
   - figurative marks with paw prints in the planned classes, especially two or more prints on a tile or square;
   - word searches for "AI Vet", "AI Veterinary", "VetAI" and close variants.

   This is the Article 8(1)(b) risk: on opposition by the owner of an earlier mark, our application is refused "if, because of its identity with, or similarity to, the earlier trade mark and the identity or similarity of the goods or services covered by the trade marks there exists a likelihood of confusion on the part of the public in the territory in which the earlier trade mark is protected".
2. **The lawyer's view** on Article 7 for the combined mark, on the class list, and on whether to file an EUTM or national DE/IT marks first.
3. **Keep the evidence.** Keep the dated drawing files (`site/public/logo-*.svg`), the design canvas and its brand sheet as evidence of authorship and first use.

**Bottom line.** A registration would protect our particular look, not paws and not the name. Real distinctiveness has to come from use: the same mark, coral tile and wordmark everywhere, across the site, the booklet and the vet tools.

*Source:* Regulation (EU) 2017/1001 of the European Parliament and of the Council of 14 June 2017 on the European Union trade mark (codification), OJ L 154, 16.6.2017, p. 1, Articles 7 and 8, read on EUR-Lex (CELEX 32017R1001) on 25 Oct 2026. Quotations are from that text.

---

## Not opened, or opened only indirectly

- **Brand homepages:** Blue Cross (403), Boehringer Ingelheim (bot challenge), Prima (403), I‑Vet (connection failure / 503), LMU Kleintierklinik (502), Chewy Vet Care (404/429).
- **Canva:** canva.com pages return 403 to curl and WebFetch. The Content License Agreement was read through the r.jina.ai text mirror of the official URL; the "licensing explained" and Learn pages couldn't be opened.
- **Apple HIG:** the HTML page is JavaScript-only, so it was read through Apple's documentation JSON for the same page.
- **Legal texts:**
  - EUR-Lex (Reg. 2017/1001, Art. 7) returned a WAF 202 with an empty body on 24 Oct, so Parts 1–3 take the Article 7 wording from the EUIPO PDFs. On 25 Oct the page opened in a headless browser, which runs the site's check page; Part 4 quotes Articles 7 and 8 from it.
  - The current consolidated EUIPO Guidelines web version wasn't opened; the 2017 draft chapter 9 PDF was used.
  - ICRC IHL database (GC I arts. 44/53) returned empty JS pages.
  - ICRC 5kze8s returned 403 or a redirect.
  - normattiva.it (L. 740/1912) reset the connection.
- **Survey and design articles:** petfoodindustry.com (403), vnonline.co.uk and mrcvs.co.uk (connection reset), Smashing Magazine (no matching article found / 404), NN/g favicon article (404), Material 3 icon guidance (JS-rendered, not parsed, not cited).

*Not legal advice. Before filing a mark or finalising the symbol, have an EU trade-mark attorney run clearance (EUIPO eSearch, TMview, DPMA, UIBM) against the final design.*
