# Go-to-market kit — drafts to send (14 Oct 2026)

Everything here is ready to copy. Replace the bracketed placeholders. Send
from your own address; replies should reach a person, not a form.

## 1. Willingness-to-pay survey for vets (DE/IT)

Run it as a free Google Form or Tally form, one page, under three minutes.
Target: 30 answers per country before pricing is published. Distribute via
the Ordini/Kammer newsletters, the podcasts below, and the pilot clinics.

Questions (answer type in brackets):

1. Country and practice type [IT / DE / AT / CH; small animal / mixed / equine / referral]
2. Number of veterinarians in the practice [1 / 2–3 / 4–8 / 9+]
3. Practice-management software in use [free text]
4. Minutes per day you personally spend typing records after consultations [<15 / 15–30 / 30–60 / 60+]
5. Where that typing happens [during the consult / between consults / after hours / at home]
6. Have you tried an AI scribe or dictation tool? [no / tried, stopped / using one: which]
7. If you stopped: why? [recording consent / accuracy / price / language / integration / other]
8. For a text-first assistant that turns your notes into a finished, approved record and the owner letter, with nothing on the page you did not write, what monthly price per vet feels fair? [free only / 15 / 29 / 39 / 59 / 79 €]
9. At what price would it be too expensive to consider? [same scale]
10. Which single document costs you the most time? [consultation report / discharge / referral letter / owner instructions / prescription / insurance paperwork / estimate]
11. Must-have before you would trust it [check all: EU hosting / no training on my data / works without integration / native German or Italian / shows the source of every sentence / a public accuracy report]
12. Would you join a four-week pilot with a free account and give feedback? [yes: email / no]

Report the medians of 8 and 9 per country on `/vets/quality` once there are 30 answers.

## 2. Editorial pitches

Keep each under 150 words. One ask, one link, no attachments.

### DE: Vetline "Praxismanagement", Vetjournal "Praxismanager"

Betreff: Gastbeitrag: Warum die meisten KI-Scribes in der Tierarztpraxis am Einverständnis scheitern

Sehr geehrte Redaktion,

ich baue mit praktizierenden Tierärztinnen und Tierärzten ein Dokumentationswerkzeug, das bewusst ohne Mikrofon auskommt: Notizen tippen, strukturierten Befund prüfen, freigeben. Dabei haben wir mehr als dreißig KI-Scribes und die Erfahrungen von Praxen damit untersucht. Das Ergebnis ist ein Gastbeitrag von rund 900 Wörtern: welche Hürden Aufzeichnung, DSGVO und TÄHAV-Dokumentation in der Praxis wirklich setzen, und was ein textbasierter Ansatz anders macht. Kein Produkttext, Quellen genannt, Belege verlinkt.

Passt das in Ihre Rubrik Praxismanagement? Ich schicke gern den Entwurf.

Mit freundlichen Grüßen
[Name], aiveterinary.org

### IT: vetjournal.it, newsletter degli Ordini

Oggetto: Proposta di articolo: documentazione clinica e IA, cosa chiede davvero la L. 132/2025 al veterinario

Gentile redazione,

sto sviluppando insieme a veterinari in attività uno strumento di documentazione che non registra audio: il veterinario scrive poche righe, rivede la cartella strutturata e la approva. Abbiamo analizzato più di trenta sistemi di "AI scribe" e le esperienze degli studi che li usano. Propongo un articolo di circa 900 parole su cosa richiedono davvero la L. 132/2025 e l'AI Act al professionista che usa l'IA nella documentazione, con fonti citate. Nessun contenuto promozionale.

Può interessare a vetjournal.it? Invio volentieri la bozza.

Cordiali saluti
[Nome], aiveterinary.org

### Podcasts

- FutureVetBusiness (DE): pitch the "no microphone" angle and the public quality page; offer a 20-minute conversation, no slides.
- Che Razza di Podcast (IT): pitch the owner side first (libretto, riepilogo per la visita), the vet tool second.

## 3. Free tier for students, TFA/tecnici and nurses

Terms to publish on `/vets` once the tool opens:

- Free for life for veterinary students, TFA (DE), tecnici veterinari (IT) and veterinary nurses, on proof of enrolment or employment, renewed yearly.
- Same product, same limits as the paid plan, except that documents are watermarked "training use" until a licensed vet co-signs.
- Universities and schools can list it as a convenzione; we ask for nothing in return except feedback.

Contacts to write to (from the backlog): bvvd (bvvd@bvvd.de), IVSA Italy chapters, vmf, ATAV.

## 4. Launch checklist (owner side)

Day 0, before announcing:
- [ ] Merge, Cloudflare Pages, nameservers, HTTPS green, `/sitemap-index.xml` reachable.
- [ ] Company details in `/privacy` and the Impressum.
- [ ] Newsletter provider connected (`PUBLIC_NEWSLETTER_ACTION`) with double opt-in on.
- [ ] Cloudflare Web Analytics token set (`PUBLIC_CF_ANALYTICS_TOKEN`), cookie-free.
- [ ] Search Console: verify property, submit sitemap, set hreflang check.
- [ ] One vet reviewer has signed at least five articles, one per species.
- [ ] Open Graph preview checked on WhatsApp, LinkedIn and X.

Day 1:
- [ ] Post in two owner communities per country (Facebook groups for dog and cat owners in Milan/Berlin/Vienna, Reddit r/dogs, r/cats with the mod's permission).
- [ ] Ordini/Kammer newsletters: the vet-side pitch above.
- [ ] Product Hunt: owner side only, "free digital pet health booklet that lives on your phone", screenshots from `docs/13-design-research.md` style.

Week 1:
- [ ] Reply to every correction email within 48 hours; log changes at the bottom of the article.
- [ ] Review Search Console queries; write the next ten articles from real queries.

## 5. Pilot agreement, one page

- Four weeks, up to three clinics per country, free.
- The clinic uses synthetic or de-identified notes in weeks 1–2, real notes in weeks 3–4 under the AVV/DPA (`docs/legal/`).
- We deliver: the workspace, the country field pack for their country, weekly 30-minute call, export of everything at the end.
- They deliver: ten documents per week with a one-line verdict each, and permission to quote anonymised feedback on `/vets/quality`.
- Either side can stop at any time; data is deleted within 30 days of a stop.
