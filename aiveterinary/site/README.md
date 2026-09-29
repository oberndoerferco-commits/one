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
| `src/pages/` | Pages: home, about, newsletter, privacy, `animals/`, `vets/` |
| `src/content/animals/*.md` | Animal-health articles (one file each) |
| `src/content.config.ts` | Article fields and allowed values |
| `src/layouts/Base.astro` | Header, footer, `<head>` |
| `src/styles.css` | All styling; colour tokens at the top, dark mode included |
| `public/` | Favicon and static files |

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
