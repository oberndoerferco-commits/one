# aiveterinary.org — website

Static site built with [Astro](https://astro.build). Content is Markdown; no
database, no cookies, free to host.

## Run locally

```bash
cd aiveterinary/site
npm install
npm run dev        # http://localhost:4321
npm run build      # output in dist/
```

## Where things live

| Path | What |
|---|---|
| `src/pages/` | Pages: home, about, newsletter, privacy, `passport` (local-first digital pet passport), `animals/`, `vets/` |
| `src/content/animals/*.md` | Animal-health articles (one file each) |
| `src/content.config.ts` | Article fields and allowed values |
| `src/layouts/Base.astro` | Header, footer, `<head>` |
| `src/styles.css` | All styling; colour tokens at the top, dark mode included |
| `public/` | Favicon and static files |
| `src/components/{EmergencyCheck,ChocolateCheck,FoodCheck,VaccinePlanner}.astro` | Owner tools: fixed rules from named sources, no AI; each cites its source on the page |
| `src/pages/llms.txt.ts` | `/llms.txt` for AI assistants: what the site is, how to cite it, every article with its review and source status |
| `scripts/og.mjs` | Renders the share images `public/og.png`, `og-it.png`, `og-de.png` from the live styles (run with the preview server up) |

## Writing an article

Create `src/content/animals/<slug>.md`:

```yaml
---
title: "My dog is vomiting: what it can mean and when to worry"
description: "One or two sentences shown in listings and search results."
species: dog          # dog | cat | rabbit | horse | bird | general
category: symptoms    # symptoms | conditions | medications | travel | first-aid | care
urgency: today        # emergency | today | this-week | routine (optional)
updated: 2026-09-29
seoTitle: "Short title for the browser tab and search results"   # optional, max 70 characters
references:           # the sources the article is based on; every URL opened and checked
  - title: "MSD Veterinary Manual: Page title"
    url: "https://www.msdvetmanual.com/…"
draft: true           # true until a vet has reviewed it
reviewedBy: "Dr. Name Surname, DVM"   # set when draft becomes false
reviewedOn: 2026-10-05
---
```

Rules that keep the site trustworthy:

- `draft: true` shows a "Draft, awaiting veterinary review" badge. Set it to
  `false` only after a named vet has read and approved the text.
- No diagnoses, no doses. Explain, prepare, and point to the vet.
- Every symptom article starts with the "go now" signs.
- Headings are the questions owners ask ("When should I take my cat to the vet?"),
  each followed by a one-sentence answer taken from that section.
- Every article lists its `references`; an article without them says
  "sources are still to be added" on the page and in `/llms.txt`.

## Free hosting

1. Push this repo to GitHub.
2. **Cloudflare Pages** (free): New project → connect the repo → root
   directory `aiveterinary/site`, build command `npm run build`, output
   `dist`. Add the custom domain `aiveterinary.org` in the Pages settings and
   point the domain's DNS at Cloudflare as instructed.
3. Alternatively **GitHub Pages** with the Astro GitHub Action; set `site` in
   `astro.config.mjs` accordingly.

## Newsletter (free tier)

Create an account with a free newsletter service (Buttondown, MailerLite and
Brevo all have free tiers), take its form action URL, and set it as
`PUBLIC_NEWSLETTER_ACTION` in the hosting provider's environment variables.
The form already sends `email` and `audience` (`owner` or `vet`).

## Ask box AI answer

`PUBLIC_ASK_AI` (default off): with `true`, the home page question box also asks the Cloudflare Pages Function `functions/api/ask.ts` for an AI answer written only from our articles, labelled "AI answer based on our articles", and the hero kicker reads "Your AI vet assistant". It needs the secret `ANTHROPIC_API_KEY` in the Pages environment; without the key the function answers 503 and the box silently keeps its Pagefind answer. Optional: `ASK_MODEL` (default `claude-opus-5-5`), `ASK_EFFORT` (`low`, default). To switch it on: set both variables in Cloudflare Pages (Settings → Environment variables, Production), then redeploy. The function runs only on Cloudflare Pages, not on GitHub Pages. Design, safety rules, cost and the dashboard rate-limit TODO: `../docs/31-ai-answer.md`. Tests: `npm test`.

**For the lawyer** (shown only when the flag is on, wording to be checked): the privacy line under the box ("Your question is sent to our AI provider to write the answer. We don’t store it." and the IT/DE versions in `src/components/AskBox.astro`, `privacyAI`), the first item of "What happens to what you type" and the "Question box" item in `src/components/Home.astro`, and the "Questions in the question box" section plus the processor entry in `src/pages/privacy.astro` (bracketed placeholders for the provider, its retention and transfer safeguards). Points to check are listed in `../docs/31-ai-answer.md` §7.

## Signing a vet review

When a veterinarian has checked an article and approves it:

```
node scripts/review.mjs sign src/content/animals/it/cane-febbre.md --by "Dott.ssa Nome Cognome, DVM" --reg "Ordine di Milano n. 1234"
```

This sets `draft: false`, the reviewer, the review date, the next review date (one year later) and a hash of the title, summary, sources and text. Every build runs `node scripts/review.mjs check` first and fails if a reviewed article changed after sign-off, so no later edit (human or AI) can appear under a vet's name. To change a reviewed article, edit it and have it reviewed and signed again.
