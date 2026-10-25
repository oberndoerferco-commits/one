# Launch guide: from repository to aiveterinary.org

Today aiveterinary.org shows a GoDaddy Website Builder placeholder, so nothing in this repository is visible to people, Google or AI assistants yet. This guide takes about 30–45 minutes. Everything happens in your own accounts; no secret ever goes into the repository.

Screens change; if a button has moved, follow Cloudflare's own Pages documentation for the same step.

## 1. Merge the work (GitHub, 2 minutes)

The site lives on branch `claude/modest-dirac-s1uvdm` (pull request #1). Either merge the pull request into `main`, or in step 2 choose that branch as the production branch for now.

## 2. Create the Cloudflare Pages project (10 minutes)

1. Create a free Cloudflare account (turn on two-factor login).
2. In the dashboard: **Workers & Pages → Create → Pages → Connect to Git**, authorise GitHub and pick the repository `oberndoerferco-commits/one`.
3. Build settings:
   - Production branch: `main` (or the branch above)
   - Root directory: `aiveterinary/site`
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Environment variable: `NODE_VERSION` = `22`
4. Optional environment variables (Settings → Environment variables), each only when you have the value:
   - `PUBLIC_CF_ANALYTICS_TOKEN`: Cloudflare Web Analytics token (cookie-free visit counts)
   - `PUBLIC_NEWSLETTER_ACTION`: form URL from your newsletter provider (double opt-in on)
   - `PUBLIC_ASK_AI`: leave unset until a real AI answer endpoint exists
5. Save and deploy. The first build runs every content check (reviews, species, lexicon, foods, banned sources) before Astro builds; if one fails, the log names the file.
6. Open the `*.pages.dev` address Cloudflare gives you and click through: home, an article, Animals A–Z, Can my pet eat, the booklet, Italian and German.

## 3. Connect the domain (15 minutes plus waiting)

A bare domain (aiveterinary.org without www) on Cloudflare Pages needs the domain's DNS to be managed by Cloudflare.

1. In Cloudflare: **Add a site → aiveterinary.org → Free plan**. Cloudflare shows two nameservers.
2. In GoDaddy: **My Products → aiveterinary.org → DNS → Nameservers → Change → Enter my own nameservers**, paste the two from Cloudflare, save. Turn off the GoDaddy Website Builder site so it no longer publishes.
3. Wait until Cloudflare shows the domain as active (minutes to a day).
4. In the Pages project: **Custom domains → Set up a custom domain** → `aiveterinary.org`, then again for `www.aiveterinary.org`.
5. Make `www` redirect to the bare domain (Cloudflare Rules → Redirect Rules, or Bulk Redirects), because the site's canonical addresses are `https://aiveterinary.org/...`.

## 4. Check the live site (10 minutes)

- `https://aiveterinary.org/it/` returns a 301 to `/it` (from `public/_redirects`), same for `/de/`.
- An unknown address (e.g. `/does-not-exist`) shows the 404 page with status 404.
- `https://www.aiveterinary.org/` redirects to `https://aiveterinary.org/`.
- `/about/` (with trailing slash) does not answer as a second copy of `/about`.
- `/robots.txt`, `/sitemap-index.xml` and `/llms.txt` load.
- On a phone: the browser offers to install the app; the booklet works offline after one visit.
- Cloudflare **Security → Bots / AI crawl settings**: make sure they do not block search and answer bots (Googlebot, Bingbot, OAI-SearchBot, PerplexityBot, Claude-SearchBot). Cloudflare's settings act before our robots.txt.

## 5. Tell the search engines (10 minutes)

1. **Google Search Console**: add a *Domain* property for aiveterinary.org (verify with the DNS record it shows, added in Cloudflare DNS), submit `https://aiveterinary.org/sitemap-index.xml`, and use URL Inspection on the home page and two articles.
2. **Bing Webmaster Tools**: import from Search Console or add the site, submit the same sitemap (Bing also feeds several AI assistants).
3. Run Google's Rich Results Test on one article and one Animals A–Z page.

## 6. Before real sign-ups or marketing

- Company details for the Impressum/legal pages, and the lawyer's hour (privacy, terms, AI disclosure).
- Two vets (one IT, one DE) reviewing and signing articles, starting with the emergency topics (`node scripts/review.mjs sign`, see the site README).
- A trade-mark search (EUIPO, DPMA, UIBM) before registering the name and logo; see docs/26.

Background for every step: docs/28 (SEO and AI search) and docs/29 (the installable app).
