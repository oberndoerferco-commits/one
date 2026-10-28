# 28 · SEO and AI search: audit and fixes (EN/IT/DE)

Audit and implementation, 24–25 Oct 2026, for the Astro site in `site/`. The goal is the best realistic chance of ranking in Google (including AI Overviews) and of being cited by ChatGPT search, Perplexity, Gemini and Claude in English, Italian and German.

**Method.** Every best-practice rule used here was checked against a primary document opened on 24–25 Oct 2026 (§9). Where a document did not say something, this note says so rather than filling the gap from memory. Each change was measured on a local build, with the before and after numbers in §5. Nothing was committed.

---

## 0. Summary

**The #1 blocker is that the site is not live.** `aiveterinary.org` currently serves a **GoDaddy Website Builder placeholder** (response header `Server: DPS/2.0.0`; `/it` returns 404 from the placeholder). The Cloudflare Pages deploy in `site/README.md` has not happened yet. Until it does, Google, Bing and the AI crawlers can see none of the work below. No measurement here uses the live domain; all numbers come from local builds.

**Fixed in code (details in §1–§6):**
- **404 page.** Without a top-level `404.html`, Cloudflare Pages treats a site as a single-page app and answers every unknown URL with the home page (soft 404s). Added `src/pages/404.astro`.
- **`/it/` and `/de/`** returned 404. Added `public/_redirects` with 301s to `/it` and `/de`.
- **hreflang, noindex, structured data and sitemap are now derived** from the content collections and route files. New articles, species, lexicon entries and routes (e.g. `/can-eat/[species]`) are covered automatically. A post-build step checks everything against the pages actually built.
- **Empty animal-guide listings** (horse and bird in all three languages at HEAD) were indexable and in the sitemap. They are now `noindex`, out of the sitemap and out of hreflang until something is published there.
- **Structured data:**
  - Articles now carry a Google-supported `Article` node (MedicalWebPage alone is not one of Google's Article types), with all sources as `citation` and the animal as `about` with a Wikidata ID.
  - `reviewedBy` appears only on non-draft articles that name a reviewer.
  - The dead SearchAction markup was removed, and the Organization logo is now the 512 px PNG of the new two-paw mark.
- **Answer first.** On every article, the article's own summary is now the first text after the H1, and it is the LCP element.
- **robots.txt** now names every AI search and answer bot and every training bot explicitly. Everything stays allowed (§3.1).
- **llms.txt:**
  - Every article per language, with a one-line answer, its urgency verdict, source count and review status.
  - The animal guide pages and the animal lexicon.
  - An `Optional` section.
  - Any built page it would otherwise miss.
- **Internal links.** Fixed links from `/it` and `/de` to `/it/privacy` and `/de/privacy`, which don't exist. The species link on articles now appears only where a species page exists, and articles link to their lexicon entries.
- **Core Web Vitals.**
  - Layout shift came from web-font swaps; metric-matched fallback fonts fix it, and `ch` widths that changed with the font are now `em`.
  - A language banner pushed content down after first paint; its script now runs before the content below it is painted.
  - A WCAG 2.5.8 target-size failure on source links is fixed.
- **Titles.** Added `seoTitle` to all 65 articles whose titles were over 70 characters (Appendix A).
- **New `npm run check:seo`** (`scripts/seo-check.mjs`) checks a build for all of the above.

**Measured (390 px, details §5):**

| Page | Lighthouse before → after (perf · LCP · CLS) | Throttled browser before → after (LCP · CLS) |
|---|---|---|
| `/` | 98 · 2.0 s · 0.032 → **100 · 1.0 s · 0.004** | 756 ms · 0.029 → **528 ms · 0.004** |
| `/animals/dog-vomiting` | 92 · 1.8 s · **0.160** → **100 · 1.1 s · 0** | 744 ms · 0 → **500 ms · 0** |
| `/animals/dog` (animal guide) | 98 · 1.8 s · 0.006 → **100 · 0.9 s · 0** | 648 ms · 0 → **508 ms · 0** |
| `/it` | 91 · 2.0 s · **0.155** → **100 · 1.2 s · 0** | 780 ms · 0.029 → **568 ms · 0** |
| `/de/animals/hund-zittert` | 95 · 1.8 s · **0.111** → **100 · 1.1 s · 0** | 776 ms · 0 → **508 ms · 0** |

TBT is 0 ms on every page before and after. INP needs real users, so it will come from field data (§5).

**What only the owner can do (§7):**
1. Deploy and fix DNS.
2. Check Cloudflare's AI-bot settings, which override robots.txt.
3. Set up Search Console and Bing Webmaster Tools.
4. **Recruit veterinary reviewers.** All 224 articles are unreviewed AI-assisted drafts. For health topics this is the biggest thing holding rankings back (§4).
5. Earn links and mentions from veterinary sources.

---

## 1. Technical SEO

### 1.1 Titles and meta descriptions

**What the documents say.**
- Google: "there's no limit on how long a `<title>` element can be", but title links are cut "to fit the device width".
- Google also asks to "brand your titles concisely", to give each page distinct text and to avoid boilerplate.
- Meta descriptions have no length limit either, and snippets are truncated to the device width. "Identical or similar descriptions on every page of a site aren't helpful." [title-link, snippet]

**Before.** All titles and descriptions were unique, and all descriptions were 72–160 characters, because `Base.astro` shortens them at a word boundary at about 158. But 65 article titles were over 70 characters (EN 11, IT 20, DE 34), so their end would be cut off in results. The brand is appended only when the title is 52 characters or fewer, which is concise branding.

**Done.**
- **`seoTitle` added to all 65 articles**, only that frontmatter field. Each new value is at most 60 characters and unique, and keeps the article's own wording.
  - Three guinea-pig titles follow the owners' phrasing from `docs/27-search-demand-2026-10.md`, but only where the article uses those words, e.g. "wheezing".
- The 7 ferret articles were added after their writer committed them.
- `npm run check:seo` warns about any title over 70 characters and fails on duplicate titles.

**Now (real tree, 25 Oct):** no duplicate titles or descriptions, and no titles over 70 characters.

### 1.2 Canonical

Every indexable page has a self-referencing, absolute canonical without a trailing slash, and the same URL is in the sitemap and `og:url`. Noindex pages (404, empty listings) carry no canonical, no hreflang and no `og:url`. Default robots values are "index, follow" and "don't need to be specified" [special-tags], so indexable pages carry no robots meta at all.

### 1.3 hreflang

**What Google requires** [localized-versions]:
- "Each language version must list itself as well as all other language versions."
- "If two pages don't both point to each other, the tags will be ignored."
- `x-default` is the fallback.
- URLs must be fully qualified.
- Codes follow ISO 639-1.

**Before.**
- A hard-coded list of shared pages, and a regex of species that missed guinea-pig, ferret and reptile.
- Hreflang pointed at the empty horse and bird listings.
- Group translations (different slugs) were listed even if a file was missing.
- The sitemap had a second, smaller set of alternates (same-path pages only), so it disagreed with the HTML for the 30+ translation groups.

**Now** (`src/lib/seo.ts`, used by `Base.astro`):
- **Articles**: same slug in another language, or a pair in `TRANSLATION_GROUPS`, and only where that translation exists.
- **`/animals/<key>`**: an animal-guide listing (species or topic) and/or a lexicon entry, in the languages where it has content (its own articles, shared topics listed for it in `SHARED_TOPICS`, or a lexicon entry). A listing with nothing in it gets `noindex`. Other unknown pages are never noindexed by default.
- **Every other page**: worked out from the route files, so a page whose route exists in `src/pages/`, `src/pages/it/` and `src/pages/de/` is linked. This reproduces the old hard-coded list exactly, and also covers dynamic routes such as a future `can-eat/[species].astro`.
- `x-default` is the English version, or the first language if there is no English one.
- A route that knows its translations exactly can pass `alternates` to `Base`.

**After the build** (`seoAfterBuild` in `astro.config.mjs`):
- An alternate is kept only if its page was built, is indexable and links back. Otherwise it is removed from the page, with a warning in the build log.
- If a translation was not built, the language switcher and the "also available in" banner point to that language's home instead of a 404.
- A fixture test confirmed this. It used a food list where DE lacks one species, and a lexicon entry in EN and IT only.

**Result:** 0 hreflang errors on 343 pages (`check:seo` checks self-reference, x-default, targets, language and reciprocity).

### 1.4 Sitemap

**What the documents say.**
- Google uses `<lastmod>` "if it's consistently and verifiably accurate", and it should reflect "the last significant update".
- Google ignores `<priority>` and `<changefreq>`, and a sitemap should list only the preferred URL [build-sitemap].
- Bing calls lastmod "a key signal" and says it "should reflect the true last modification time of the page content" [bing-sitemaps].

**Before.** 267 URLs, 166 with `lastmod` (articles, from `updated`). The 6 empty listings were included, and alternates covered same-path pages only.

**Now:**
- Pages that are missing or noindex are removed.
- Each URL gets exactly the alternates its page declares.
- `lastmod` comes from the article's `updated` date (quoted dates are now accepted), or from the page's own `dateModified` (lexicon entries).
- Listing and tool pages have no lastmod, since no verifiable date exists.

**Counts.** HEAD plus these changes: 261 URLs, 166 with lastmod. Real tree on 25 Oct: 342 URLs (every page except the 404).

### 1.5 robots.txt

See §3.1 for the bot policy. Rules verified against Google's robots.txt document [robots-txt]:
- A group can repeat `user-agent` lines.
- A crawler obeys only the most specific matching group, and "user agent specific groups and global groups (`*`) are not combined". So every named group repeats `Allow: /`.
- The `Sitemap:` line must be a fully qualified URL.
- Nothing is disallowed: CSS, JS and the Pagefind index stay crawlable, as Google needs them for rendering.

### 1.6 404s and trailing slashes

- **404.** Cloudflare Pages: without a top-level `404.html`, "Pages assumes that you are deploying a single-page application" and serves the root for unmatched paths [cf-serving]. Every mistyped or deleted URL would have returned the home page with status 200: soft 404s and duplicate content.
  - `src/pages/404.astro` builds `404.html` with a short message in EN, IT and DE, links to the guide, symptoms, emergency check and home, and `noindex`.
  - Locally `astro preview` returns status 404 for unknown URLs. On Cloudflare, check after deploy (§7).
- **`/it/` and `/de/`.** With `build.format: 'file'` and `trailingSlash: 'never'`, the language homes are `it.html` and `de.html`, next to folders `it/` and `de/` that have no `index.html`. So `/it/` has nothing to serve.
  - Cloudflare's Pages documentation does not describe this case. Its Workers static-assets page says single files are served without a trailing slash and redirects `/file/` to `/file`, but it is a Workers page and not confirmed for Pages [cf-html-handling].
  - So I added `public/_redirects` with `/it/ /it 301` and `/de/ /de 301`. Pages applies redirects "before static assets are served" [cf-redirects]. Other `/x/` URLs need a check after deploy (§7).
  - `astro preview` ignores `_redirects`, so this can only be tested on Cloudflare.

### 1.7 Internal links

- Fixed: `/it` and `/de` linked to `/it/privacy` and `/de/privacy`, which don't exist (privacy is EN-only). The link is now `/privacy` (`src/components/Home.astro`).
- The animal guide `/animals` and `/animals/symptoms` are linked from the header on every page (85 pages per language).
- Species guide pages are linked from every article's header line. That species link now appears only when the species has a page, so a new species never produces a 404 link.
- When an article lists `animals:` (lexicon entries), its header also links to those entries in its language.
- `check:seo` finds no orphan pages and no broken internal links.

### 1.8 Breadcrumbs

- Articles show visible breadcrumbs (guide · topic · species). In the markup, the `BreadcrumbList` runs guide → topic → article.
  - The last item has no `item`, which Google allows: "If the breadcrumb is the last item in the breadcrumb trail, `item` is not required" [breadcrumb].
- New: any page below a menu page gets a two-level `BreadcrumbList`, named from the visible menu label of its parent. Examples: `/vets/data`, `/animals/dog`, lexicon entries and future `/can-eat/<species>` pages.
- Google says the feature is "available on desktop".

---

## 2. Structured data

**Rules verified:**
- **Article types.** "Article objects must be based on one of the following schema.org types: Article, NewsArticle, BlogPosting." There are "no required properties". Recommended are `author` (+`name`, `url`), `dateModified`, `datePublished`, `headline` and `image`. Authors shown on the page must be in the markup, as `Person` or `Organization` [article].
- **Truthful markup.** "Your structured data must be a true representation of the page content." Don't mark up content that is not visible, and don't mislead [sd-policies].
- **Fake authors.** Fake author profiles are deception [helpful-content].
- **Site name.** `WebSite` must be on the home page at the domain root. "Google Search does not support site names at the subdirectory level" [site-names].
- **Organization.** Put it on the home page or an About page. The logo must be at least 112×112 px, crawlable and in a format Google Images supports [organization].
- **FAQ rich result.** "no longer shown in Google Search results"; the documentation was removed on 15 Jun 2026, after a notice on 8 May 2026 [faqpage].
- **HowTo rich result.** Documentation removed in Sept 2023, as the result "is no longer shown" [faqpage changelog].
- **Sitelinks search box.** Removed from results on 21 Nov 2024. Leftover markup "won't cause issues", "there's no need" to remove it [sitelinks-searchbox].
- **schema.org.** `reviewedBy` and `lastReviewed` are WebPage properties, so they sit on the MedicalWebPage node, not the Article [schema-medicalwebpage].

**What each page now has:**

| Page | Nodes |
|---|---|
| Article | `MedicalWebPage` (name, description, inLanguage, dateModified, isPartOf, breadcrumb, mainEntity; `reviewedBy` and `lastReviewed` **only when the article is not a draft and names a reviewer**) + **`Article`**. |
| ↳ `Article` node | headline, description, inLanguage, `datePublished` only if the new optional frontmatter `published` is set (also shown on the page), dateModified, `author`, `publisher` with logo, `about`, articleSection, isAccessibleForFree, `citation` = every listed source (with URL where it has one). |
| ↳ `author` | The organisation, linked to `/about`. A named `Person` only if `author:` is set; none is invented. |
| ↳ `about` | The article's lexicon entries if it lists `animals:`, else its species, with Wikidata IDs (§2.1). |
| Article (continued) | + `BreadcrumbList`. |
| Lexicon entry (`/animals/<key>`) | `WebPage` with `about` (name, scientific name as `alternateName`, Wikidata where known), `dateModified`, `citation` (the entry's references), `publisher`, + `BreadcrumbList`. |
| `/` | `Organization` (name, url, 512 px PNG logo, email, description) + `WebSite` (site name; no SearchAction). |
| `/it`, `/de`, `/about`, `/it/about`, `/de/about` | `Organization`. |
| Other pages below a menu page | `BreadcrumbList`. |

**Deliberately not added:**
- `FAQPage` and `HowTo`: no rich result any more.
- `SearchAction`: retired.
- `speakable`, `Review` or ratings: not applicable, or would be fake.
- `MedicalCondition` nodes: they would assert clinical facts per entity that no vet has reviewed.
- Article `image`: the site has no article images, and the generic share card is not "representative" of each article. Add real images and the `image` property (§4).

**Validation.**
- The validator at validator.schema.org reported no errors for an article and the home page.
- `check:seo` parses every JSON-LD block on every page.
- Google's Rich Results Test needs a public URL, so run it after deploy (§7).

### 2.1 Wikidata IDs used for `about`

Looked up through the Wikidata API on 24 Oct 2026. My first guesses for guinea pig and ferret were wrong, which is why they were checked.

| Key | Item |
|---|---|
| dog | Q144 |
| cat | Q146 |
| rabbit | Q149017 (domestic rabbit) |
| guinea-pig | Q79803 |
| ferret | Q178973 (*Mustela putorius furo*) |
| horse | Q726 |
| bird | Q5113 |
| reptile | Q10811 |

Lexicon entries outside this list (budgie, hamster, …) get their scientific name but no `sameAs` until an ID is added to `WIKIDATA` in `src/lib/seo.ts`.

---

## 3. AI search and assistants

**Google AI Overviews and AI Mode.** "There are no additional requirements to appear in AI Overviews or AI Mode", and "you don't need to create new machine readable files, AI text files, or markup". A page has to be indexed and eligible for a snippet [ai-features]. So the work that matters for AI Overviews is the work in §1, §2 and §4. We use no snippet restrictions (`nosnippet`, `max-snippet`).

### 3.1 Crawler policy (`public/robots.txt`)

| Bot (token) | What it does, per its operator | Policy |
|---|---|---|
| Googlebot, Bingbot (`*`) | Search, incl. Google AI features | Allow |
| `OAI-SearchBot` | "Surfaces websites in ChatGPT's search features" [openai-bots] | **Allow** |
| `ChatGPT-User` | Visits a page when a user asks; "robots.txt rules may not apply" [openai-bots] | Allow |
| `PerplexityBot` | Shows and links sites in Perplexity results; "not used to crawl content for AI foundation models" [perplexity-bots] | **Allow** |
| `Perplexity-User` | User-requested fetch; "generally ignores robots.txt rules" [perplexity-bots] | Allow |
| `Claude-SearchBot` | Indexes for Claude's search results; blocking "may reduce your site's visibility" [anthropic-bots] | **Allow** |
| `Claude-User` | Fetches a page for a Claude user's question [anthropic-bots] | Allow |
| `GPTBot` | "Crawls content that may be used to train" OpenAI models; independent of OAI-SearchBot [openai-bots] | Allow (current default kept) |
| `ClaudeBot` | Collects content that may be used to train Anthropic models [anthropic-bots] | Allow (current default kept) |
| `Google-Extended` | Controls use for Gemini training and grounding; "does not impact a site's inclusion in Google Search" and is not a ranking signal. The page does not mention AI Overviews [google-crawlers] | Allow (current default kept) |
| `CCBot` | Common Crawl's open web archive [ccbot] | Allow (current default kept) |

**Training bots: why the default stays "allow".**
- The articles are free public-health information, and the site's purpose is to be the correct answer when an owner asks.
- Being in training data makes it more likely that models repeat our sourced, "call the vet" framing.
- Blocking them would not help rankings or citations. Each operator documents the training token as independent of its search or answer bot, and Google says the same for Google-Extended and Search.

**When to opt out.**
- If the owner wants out of training, change `Allow: /` to `Disallow: /` in the training group only. The comment in the file says so.
- One argument for opting out later: once vets have reviewed articles, the owner may want to control commercial reuse.

**Cloudflare can override this file** (§7, item 2):
- Its *managed robots.txt* "will prepend" its own rules to ours when enabled.
- *Block AI bots* blocks training crawlers at the edge.
- From 15 Sep 2026, new defaults block training and agent bots on pages with ads, while search stays allowed [cf-managed-robots, cf-block-ai-bots].

### 3.2 llms.txt

**What it is.** The llmstxt.org proposal: an H1, a blockquote summary, optional body text, then H2 sections of `- [name](url): notes` lists. An `## Optional` section holds secondary links [llmstxt]. No major search or answer engine documents reading it, and Google says no such file is needed. It costs nothing, so it stays, and it is now complete.

**What `/llms.txt` now lists:**
- How to read and cite the site, with review status.
- The tools in all three languages.
- The vet pages.
- **Animal guide** pages per language: only those that have content.
- **Every article per language**, as "title: one-line answer (urgency verdict; n sources; draft or reviewer; updated date)". Example:
  `- [My dog ate chocolate: …](…/animals/dog-ate-chocolate): Chocolate is toxic to dogs … (emergency: go to a vet now; 3 sources; draft, not yet vet-reviewed; updated 2026-10-19)`
- **Animal lexicon** per language, from the `lexicon` collection.
- **More pages**: any indexable built page not otherwise mentioned. This is how `/can-eat/<species>` pages will appear.
- **Optional**.

**Post-build check.** A list line whose link was not built is dropped, with a warning.

**Not built: `llms-full.txt` and `.md` copies of pages.**
- `llms-full.txt` is not in the proposal. Per-page `.md` copies are optional in it.
- With every article an unreviewed draft, a 1 MB+ dump would strip away the review-status context that each page shows.
- No engine documents using either.
- Revisit once articles are reviewed.

### 3.3 Answer first

**Order.** Every article now renders: breadcrumb line → H1 → **the article's own summary** (its `description`, the same text as the meta description) → draft and review status line → verdict card → body.

**Why.**
- An assistant or snippet that quotes "the first paragraph" now quotes the answer, not interface text.
- The draft disclosure stays above the verdict card.
- The summary is now the LCP element on article pages.
- The verdict card is unchanged. It still quotes the article's own "go now" list, and the body is untouched.

### 3.4 Stable heading anchors

- Section IDs are generated from the heading text at build time, e.g. `#zuerst-die-anzeichen-bei-denen-sie-sofort-fahren-sollten`, `#prima-di-tutto-quando-andare-subito-dal-veterinario`.
- They don't change unless the heading text changes. A reviewed article cannot change after sign-off (`scripts/review.mjs`), so its anchors are fixed too.
- Layout anchors are fixed: `#av-summary` (the answer, new), `#av-verdict-h`, `#av-sources`.
- `check:seo` fails on duplicate IDs; there are none.

---

## 4. Content signals (E-E-A-T, YMYL): an honest assessment

**What Google says** [helpful-content, gen-ai]:
- Of experience, expertise, authoritativeness and trust, "trust is most important". E-E-A-T is "not a specific ranking factor", but pages on topics that affect people's well-being (YMYL) are held to higher standards.
- Google asks whether "it's clear who created it", how it was produced and why. Pages should "carry a byline, where one might be expected", and bylines should lead to more information about the author.
- Fake creator profiles are deception.
- For AI-generated content: "manually factcheck and review all AI-generated content", including titles, descriptions and structured data. Disclosing how content was made is encouraged.
- Using AI to generate "many pages without adding value for users may violate" the scaled-content-abuse policy.

**Where the site stands (real tree, 25 Oct):**
- 224 articles in three languages: **all are `draft: true`, none has a reviewer, none has a named author or a publication date.**
- Every article except 4 test fixtures cites sources, and each discloses "Drafted with AI assistance … not yet reviewed by a veterinarian". This is honest and matches Google's disclosure advice.
- The structured data matches: the author is the organisation and there is no `reviewedBy`.

**What this means.**
- For owner health questions, the pages ranking today are mostly vet hospitals, vet schools and well-known publishers with named vets.
- Unreviewed, unsigned AI-assisted drafts from a new domain with no links are **unlikely to rank on competitive queries, or to be chosen as AI Overview sources, however clean the technical SEO**.
- The structure, tools, sources and three languages help, but they do not replace the trust signal.
- **The scaled-content risk grows** if drafts keep outpacing review. 224 drafts went up in about a week.

**Concrete fixes, in order of effect:**
1. **Veterinary review, starting with the emergency topics.**
   - Topics: chocolate, grapes, rat poison, chicken bones, bloat, a blocked male cat, heatstroke, horse colic, guinea pig not eating, then the highest-demand symptoms in `docs/27-search-demand-2026-10.md`.
   - One reviewer registered in each country is ideal: Ordine dei Medici Veterinari, Tierärztekammer, RCVS or Veterinary Council of Ireland.
   - The pipeline exists already: `node scripts/review.mjs sign` records `reviewedBy`, registration and date. The page, the provenance panel, llms.txt and the structured data switch automatically.
2. **A real profile page for each reviewer**, e.g. `/about/reviewers/<name>`, with qualifications, registration number and a link to the chamber's public register.
   - Then link the byline to it and add `url` (and `sameAs` to the register) to `reviewedBy` and `author`. Only real people.
3. **A named editor or publisher.** The Impressum and About pages should name the legal entity and the responsible person, and articles already link to the editorial policy ("How we write").
4. **Publication dates.** Set the new optional `published:` frontmatter, which is shown on the page and becomes `datePublished`.
5. **Original images.** Photos or diagrams (e.g. checking capillary refill or gum colour, a tick hook) with alt text. These improve the pages and enable the Article `image` property.
6. **Pace.**
   - Slow new drafts until review catches up, and merge near-duplicates.
   - If Search Console later shows many "Crawled – currently not indexed" articles, fold the weakest into stronger pages rather than add more.
7. **Links and mentions.** Vet schools, clinics that use the vet tools, breed clubs, rescue groups and local press in IT and DE. Add `sameAs` to the Organization once there are official profiles; there are none today.

---

## 5. Performance (Core Web Vitals)

**Method.**
- Local builds served by `astro preview` (gzip, no CDN), measured at **390 × 844 px, DPR 3, mobile**.
- *Lighthouse 12.8.2*: mobile form factor, default simulated throttling (slow 4G, 4× CPU), Chromium 1194.
- *Browser measurement*: Playwright and `PerformanceObserver` (FCP, LCP, layout shifts without input). Network throttled by DevTools to 150 ms RTT and 1.6 Mbit/s, 4× CPU slowdown, cold cache. Median of 5 runs.
- "Before" is a build of HEAD without these changes. "After" is HEAD plus these changes (other agents' unfinished work excluded).
- INP cannot be measured without users; TBT is 0 ms everywhere. Real numbers will come from the Search Console Core Web Vitals report and CrUX once the site has traffic.

**Lighthouse.** Performance · FCP · LCP · TBT · CLS. Accessibility is 100 everywhere after (the article was 96 before).

| Page | Before | After |
|---|---|---|
| `/` | 98 · 2.0 s · 2.0 s · 0 ms · 0.032 | **100 · 1.0 s · 1.0 s · 0 ms · 0.004** |
| `/animals/dog-vomiting` | 92 · 1.8 s · 1.8 s · 0 ms · **0.16** | **100 · 1.1 s · 1.1 s · 0 ms · 0** |
| `/animals/dog` | 98 · 1.8 s · 1.8 s · 0 ms · 0.006 | **100 · 0.9 s · 0.9 s · 0 ms · 0** |
| `/it` | 91 · 2.0 s · 2.0 s · 0 ms · **0.155** | **100 · 1.2 s · 1.2 s · 0 ms · 0** |
| `/de/animals/hund-zittert` | 95 · 1.8 s · 1.8 s · 0 ms · **0.111** | **100 · 1.1 s · 1.1 s · 0 ms · 0** |

**Throttled browser.** FCP = LCP · CLS.

| Page | Before | After |
|---|---|---|
| `/` | 756 ms · 0.029 | **528 ms · 0.004** |
| `/animals/dog-vomiting` | 744 ms · 0 | **500 ms · 0** |
| `/animals/dog` | 648 ms · 0 | **508 ms · 0** |
| `/it` | 780 ms · 0.029 | **568 ms · 0** |
| `/de/animals/hund-zittert` | 776 ms · 0 | **508 ms · 0** |

**What caused the shifts, and the fixes:**
1. **Font swap.** Plus Jakarta Sans and Fraunces load with `font-display: swap`. Text first painted in a fallback font of a different width re-wrapped when the web font arrived; on articles, the verdict list moved down.
   - `src/styles.css` now defines metric-matched fallback faces with `size-adjust` and ascent/descent overrides: Arial/Helvetica/Liberation Sans and Times for most systems, Roboto and Noto Serif for Android.
   - Ratios were measured in Chromium on mixed EN/IT/DE text. Real headings and paragraphs now differ by about 1 % between fallback and web font (median 1.007 headings, 1.003 body text).
2. **`ch` widths.** The home H1 used `max-width: 16ch`. `ch` is the width of "0" in the current font, so the box itself changed size at the swap: 3 lines became 2.
   - The four `ch` widths in `Home.astro` are now the equivalent `em` values, measured with the web fonts loaded, so the design is identical.
3. **Language banner.** "This page is also available in …" was inserted above `<main>` by a script at the end of the page, after first paint (CLS 0.1 on `/it` for an English browser). The script now runs right after the banner element, before the content below it is parsed.

**Tried and rejected: preloading the two font files.** Preloading made first paint and LCP about 220 ms *slower* under throttling, as 150 KB of fonts competed with the render-blocking CSS (976–1016 ms instead of about 750 ms). Once the fallbacks were matched, the preload bought nothing, so it was removed.

**Other checks:**
- There are no content images on these pages (icons are inline SVG), so image sizing does not apply.
- The two render-blocking stylesheets are small (12 KB + 3 KB compressed). FCP is now about 0.5 s throttled, so inlining them was not worth the extra page weight.
- Accessibility: axe-core reports **0 violations**, light and dark, at 390 px, on the article (EN/IT/DE), home (EN/IT/DE), animal guide, symptoms, empty listing, 404, About (EN/IT) and emergency pages.
  - One pre-existing failure was fixed: WCAG 2.5.8 target size on the article's source links.

---

## 6. How new pages are picked up (no list to edit)

| New thing | Sitemap | hreflang | Structured data | llms.txt |
|---|---|---|---|---|
| Article (any species) | yes, `lastmod` from `updated` | same slug in other languages, or a `TRANSLATION_GROUPS` pair | Article and MedicalWebPage, `about` from `animals:` or species | in its language's list, with verdict and status |
| Species added to `ANIMALS` in `animals-i18n.ts` | its listing, once it has content | languages with content | BreadcrumbList | Animal guide line |
| Lexicon entry `src/content/lexicon/[it/|de/]<key>.md` | yes, `lastmod` from `updated` | languages that have the entry | WebPage + about + citation + breadcrumb | Animal lexicon section |
| New route, e.g. `src/pages/{,it/,de/}can-eat/[species].astro` | yes | from the route files; checked after the build | BreadcrumbList from the parent's menu label | "More pages" with its title and description |

**`Base.astro` props:**
- `noindex`: e.g. drafts a route wants hidden.
- `alternates`: for routes that know their translations exactly.

**Checks:**
- `npm run build` runs the post-build step, with warnings in the log.
- `npm run check:seo` checks the built `dist/` and exits 1 on errors.

---

## 7. Owner checklist

1. **Deploy to Cloudflare Pages and point DNS there** (`site/README.md`), replacing the GoDaddy placeholder. Then check:
   - `curl -sI https://aiveterinary.org/it/` → `301`, `location: /it`.
   - `curl -sI https://aiveterinary.org/zz-nothing` → `404`, and the body is the 404 page, not the home page.
   - `curl -sI https://aiveterinary.org/about/` → a redirect to `/about`, or a 404. A 200 means a duplicate URL, so add a redirect rule.
   - `curl -sI https://www.aiveterinary.org/` → a 301 to `https://aiveterinary.org/`. Set a redirect rule for `www` if it is missing.
   - `/robots.txt`, `/sitemap-index.xml` and `/llms.txt` load and are the ones from this build.
2. **Cloudflare bot settings.**
   - In *AI Crawl Control* / *Security → Bots*, make sure search and answer bots are not blocked.
   - Decide on training bots, and keep *managed robots.txt* off (or matching), because it prepends its own rules [cf-managed-robots, cf-block-ai-bots].
3. **Google Search Console.**
   - Add a Domain property and verify it with DNS.
   - Submit `https://aiveterinary.org/sitemap-index.xml`. Google: submitting "might speed up your site's discovery" [search-console-start].
   - Use URL Inspection on the home, an article in each language and the guide.
   - Run the Rich Results Test on an article and a lexicon page.
   - Then review *Page indexing* monthly, and *Core Web Vitals* once there is enough traffic.
4. **Bing Webmaster Tools.**
   - Verify the site (it can import from Search Console) and submit the sitemap [bing-sitemaps].
   - Consider IndexNow: a key file at the root, then a POST with up to 10,000 URLs [indexnow]. Bing recommends it for fast updates.
5. **Veterinary reviewers**: §4, items 1–2. This is the most important item for rankings and AI citations.
6. **Links and mentions** (§4, item 7).
7. **Before deploying, make sure no test fixtures** (`zz-test-*.md`) are left in `src/content/`. There were some on 24 Oct; none are left on 25 Oct.
8. **`public/logo.png`** (Organization logo) is a copy of `public/icon-512.png`, the two-paw mark. Copy it again if the mark changes.

---

## 8. Notes for the other agents

- **Final check (25 Oct, 04:15):** the real tree builds 337 pages, 336 in the sitemap, and `check:seo` reports 0 errors and 3 warnings (the Passport h1s below).
- **Passport**: `/passport`, `/it/passport` and `/de/passport` each have two `<h1>` (the second is "Insurance claim: supporting information"). It's a warning, not an error; consider an `<h2>`.
- **Lexicon and food lists**:
  - Give each language its own translated `<title>`; `check:seo` fails on duplicate titles.
  - Use stable `id`s for the A–Z anchors (e.g. `id="a"`).
  - A route that knows its exact translations can pass `alternates` to `Base`.
- **Builds**: two `astro build` runs in the same project at the same time overwrite each other's temporary server bundle in `site/.astro/` and fail with "Cannot find module …/.astro/pages/…". Re-run one of them.
- **"Duplicate id … found" warnings** from the glob loader appear once after a content file changes (the old entry is still cached). They are harmless and gone on the next build.
- **Cache incident.** One of my fixture builds (24 Oct, about 23:44–23:47) shared `node_modules/.astro/data-store.json` and briefly left a test lexicon entry "hamster" in it. I removed it with the same serializer Astro uses (backup in the scratchpad). Later fixture builds used an isolated cache.

---

## 9. Sources (all opened 24–25 Oct 2026)

- [article] Google, Article structured data: <https://developers.google.com/search/docs/appearance/structured-data/article>
- [breadcrumb] Google, Breadcrumb: <https://developers.google.com/search/docs/appearance/structured-data/breadcrumb>
- [organization] Google, Organization: <https://developers.google.com/search/docs/appearance/structured-data/organization>
- [site-names] Google, Site names: <https://developers.google.com/search/docs/appearance/site-names>
- [faqpage] Google, FAQPage (deprecation notes and changelog): <https://developers.google.com/search/docs/appearance/structured-data/faqpage>
- [sitelinks-searchbox] Google Search Central Blog, "Farewell, Sitelinks Search Box": <https://developers.google.com/search/blog/2024/10/sitelinks-search-box>
- [sd-policies] Google, General structured data guidelines: <https://developers.google.com/search/docs/appearance/structured-data/sd-policies>
- [ai-features] Google, AI features and your website: <https://developers.google.com/search/docs/appearance/ai-features>
- [helpful-content] Google, Creating helpful, reliable, people-first content: <https://developers.google.com/search/docs/fundamentals/creating-helpful-content>
- [gen-ai] Google, Guidance on using generative AI content: <https://developers.google.com/search/docs/fundamentals/using-gen-ai-content>
- [title-link] Google, Influencing title links: <https://developers.google.com/search/docs/appearance/title-link>
- [snippet] Google, Snippets and meta descriptions: <https://developers.google.com/search/docs/appearance/snippet>
- [localized-versions] Google, Localized versions (hreflang): <https://developers.google.com/search/docs/specialty/international/localized-versions>
- [build-sitemap] Google, Build and submit a sitemap: <https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap>
- [robots-txt] Google, How Google interprets robots.txt: <https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt>
- [special-tags] Google, robots meta tag defaults: <https://developers.google.com/search/docs/crawling-indexing/special-tags>
- [google-crawlers] Google, Common crawlers (Google-Extended): <https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers>
- [search-console-start] Google, Get started with Search Console: <https://developers.google.com/search/docs/monitor-debug/search-console-start>
- [schema-medicalwebpage] schema.org, MedicalWebPage: <https://schema.org/MedicalWebPage>
- [openai-bots] OpenAI, Overview of OpenAI crawlers: <https://developers.openai.com/api/docs/bots>
- [perplexity-bots] Perplexity, Perplexity crawlers: <https://docs.perplexity.ai/guides/bots>
- [anthropic-bots] Anthropic, Does Anthropic crawl data from the web, and how can site owners block the crawler?: <https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler>
- [ccbot] Common Crawl, CCBot: <https://commoncrawl.org/ccbot>
- [llmstxt] The llms.txt proposal: <https://llmstxt.org/>
- [cf-serving] Cloudflare Pages, Serving Pages (404 and single-page apps): <https://developers.cloudflare.com/pages/configuration/serving-pages/>
- [cf-redirects] Cloudflare Pages, Redirects: <https://developers.cloudflare.com/pages/configuration/redirects/>
- [cf-html-handling] Cloudflare Workers static assets, HTML handling: <https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/>
- [cf-managed-robots] Cloudflare, Managed robots.txt: <https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/>
- [cf-block-ai-bots] Cloudflare, Block AI bots: <https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/>
- [bing-sitemaps] Bing Webmaster Blog, "Keeping Content Discoverable with Sitemaps in AI Powered Search" (Jul 2025): <https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/>. The Bing Webmaster Guidelines page itself renders only with JavaScript and could not be read.
- [indexnow] IndexNow documentation: <https://www.indexnow.org/documentation>
- Wikidata API (`wbgetentities`, `wbsearchentities`) for the IDs in §2.1.

---

## 10. Files changed

| File | Change |
|---|---|
| `site/src/lib/seo.ts` (new) | hreflang, noindex and page structured data, derived from the collections and route files; ORG, Wikidata map |
| `site/src/layouts/Base.astro` | uses `seo.ts`; `noindex` and `alternates` props; Organization and WebSite only where Google reads them; SearchAction removed; language banner script moved |
| `site/src/components/Article.astro` | Article + MedicalWebPage + BreadcrumbList graph; summary first; `published` date; species and lexicon links only where pages exist; source-list target size |
| `site/src/components/Home.astro` | privacy link fixed; `ch` → `em` widths |
| `site/src/styles.css` | metric-matched fallback font faces; font stacks |
| `site/src/pages/404.astro` (new) | trilingual 404, noindex |
| `site/src/pages/llms.txt.ts` | urgency, guide pages, lexicon, Optional |
| `site/astro.config.mjs` | `seoAfterBuild`: hreflang check, sitemap (noindex, alternates, lastmod), llms.txt check and sweep; quoted `updated` dates |
| `site/public/robots.txt` | explicit groups for search, answer and training bots |
| `site/public/_redirects` (new) | `/it/` and `/de/` → 301 |
| `site/public/logo.png` (new) | 512 px Organization logo (copy of `icon-512.png`) |
| `site/scripts/seo-check.mjs` (new), `site/package.json` | `npm run check:seo` |
| `site/src/content.config.ts` | optional `published` field (kept in the coordinator's later edit) |
| 65 article files | `seoTitle` added (that line only) |

---

## Appendix A: `seoTitle` values

Columns: language, file, length of the current title, the new `seoTitle`, its length, status.

| Lang | File | Title chars | seoTitle | Chars | Status |
|---|---|---|---|---|---|
| EN | `antibiotics-for-pets.md` | 89 | Antibiotics for dogs and cats: why to finish the course | 55 | applied |
| EN | `guinea-pig-sneezing.md` | 81 | Guinea pig sneezing or wheezing: when to worry | 46 | applied |
| EN | `horse-vital-signs.md` | 81 | Horse vital signs: normal temperature, pulse and breathing | 58 | applied |
| EN | `vaccinations-dogs-cats.md` | 81 | Dog and cat vaccinations in Europe: why boosters matter | 55 | applied |
| EN | `dog-tick-removal.md` | 78 | How to remove a tick from a dog, and diseases to watch for | 58 | applied |
| EN | `guinea-pig-vitamin-c.md` | 78 | Guinea pig vitamin C deficiency: scurvy signs and foods | 55 | applied |
| EN | `female-ferret-in-heat.md` | 76 | Female ferret in heat: why a jill shouldn't stay in season | 58 | applied |
| EN | `horse-colic.md` | 76 | Horse colic: signs and what to do until the vet arrives | 55 | applied |
| EN | `dog-fever.md` | 74 | Dog fever: taking the temperature and when to call the vet | 58 | applied |
| EN | `dog-ate-rat-poison.md` | 72 | Dog ate rat poison: act now, bleeding can start days later | 58 | applied |
| EN | `puppy-kitten-first-year.md` | 71 | Puppy or kitten first year: month-by-month health schedule | 58 | applied |
| IT | `it/vaccinations-dogs-cats.md` | 89 | Vaccini per cani e gatti in Europa: cosa coprono i richiami | 59 | applied |
| IT | `it/tiroide-cane-gatto.md` | 87 | Tiroide nel cane e nel gatto: segni, diagnosi e terapia | 55 | applied |
| IT | `it/gatto-stitico.md` | 85 | Gatto stitico: cause, cosa fare e quando è un'emergenza | 55 | applied |
| IT | `it/primo-anno-cucciolo-gattino.md` | 84 | Primo anno di cucciolo o gattino: la salute mese per mese | 57 | applied |
| IT | `it/parametri-vitali-cavallo.md` | 83 | Parametri vitali del cavallo: valori normali e misurazione | 58 | applied |
| IT | `it/poisoning-first-aid.md` | 83 | Animale avvelenato: i veleni più comuni e cosa fare subito | 58 | applied |
| IT | `it/heatstroke.md` | 81 | Colpo di calore nel cane: segni e cosa fare subito | 50 | applied |
| IT | `it/insulinoma-furetto-sintomi.md` | 80 | Insulinoma nel furetto: sintomi e quando è un'emergenza | 55 | applied |
| IT | `it/cavallo-tosse.md` | 79 | Cavallo con la tosse: cause e quando chiamare il veterinario | 60 | applied |
| IT | `it/furetto-femmina-in-calore.md` | 79 | Furetto femmina in calore: rischi e cosa fare | 45 | applied |
| IT | `it/furetto-perde-pelo.md` | 79 | Furetto che perde il pelo: è la malattia surrenalica? | 53 | applied |
| IT | `it/cane-punto-da-ape.md` | 78 | Cane punto da ape o vespa: primo soccorso e shock allergico | 59 | applied |
| IT | `it/antibiotici-animali.md` | 77 | Antibiotici a cane e gatto: perché finire il ciclo | 50 | applied |
| IT | `it/leishmaniosi-cane.md` | 76 | Leishmaniosi nel cane: primi sintomi e prevenzione | 50 | applied |
| IT | `it/sterilizzazione-cane-costo.md` | 76 | Sterilizzazione del cane: quanto costa e cosa include | 53 | applied |
| IT | `it/gatto-starnutisce.md` | 75 | Il gatto starnutisce: cause e quando preoccuparsi | 49 | applied |
| IT | `it/ansia-da-separazione-cane.md` | 73 | Ansia da separazione nel cane: segnali e cosa fare | 50 | applied |
| IT | `it/pappagallo-si-strappa-le-piume.md` | 73 | Pappagallo che si strappa le piume: muta, stress o malattia? | 60 | applied |
| IT | `it/cocorita-gonfia-dorme.md` | 72 | Cocorita gonfia che dorme sempre: è malata? | 43 | applied |
| IT | `it/quanto-costa-visita-veterinaria.md` | 72 | Quanto costa una visita veterinaria in Italia | 45 | applied |
| DE | `de/meerschweinchen-milben.md` | 92 | Meerschweinchen hat Milben oder verliert Haare: Ursachen | 56 | applied |
| DE | `de/hund-ohrenentzuendung.md` | 91 | Ohrenentzündung beim Hund: Anzeichen und Ursachen | 49 | applied |
| DE | `de/hund-trinkt-viel.md` | 88 | Hund trinkt viel: wie viel ist normal, wann zum Tierarzt? | 57 | applied |
| DE | `de/hund-milben.md` | 87 | Milben beim Hund: Räude, Demodex und Ohrmilben erkennen | 55 | applied |
| DE | `de/frettchen-insulinom-symptome.md` | 86 | Insulinom beim Frettchen: Symptome und Notfallzeichen | 53 | applied |
| DE | `de/hund-atmet-schnell-im-schlaf.md` | 86 | Hund atmet schnell im Schlaf: wann ist es ernst? | 48 | applied |
| DE | `de/kaninchen-zaehne.md` | 86 | Kaninchen Zähne zu lang: Anzeichen und Ursachen | 47 | applied |
| DE | `de/katze-blasenentzuendung.md` | 86 | Blasenentzündung bei der Katze: Symptome und Notfallzeichen | 59 | applied |
| DE | `de/katze-zahnstein.md` | 86 | Katze hat Zahnstein: Ursachen, Narkose und FORL erklärt | 55 | applied |
| DE | `de/hund-zecke-entfernen.md` | 83 | Zecke beim Hund entfernen: so geht es richtig | 45 | applied |
| DE | `de/diabetes-hund-katze.md` | 82 | Diabetes bei Hund und Katze: Anzeichen, Diagnose, Alltag | 56 | applied |
| DE | `de/katze-verstopfung.md` | 82 | Katze Verstopfung: wann ist es ein Notfall? | 43 | applied |
| DE | `de/hund-durchfall-mit-blut.md` | 81 | Hund hat Durchfall mit Blut: wann ist es ein Notfall? | 53 | applied |
| DE | `de/leptospirose-hund.md` | 81 | Leptospirose beim Hund: Anzeichen, Ansteckung, Impfung | 54 | applied |
| DE | `de/vitalwerte-pferd.md` | 81 | Vitalwerte beim Pferd: Temperatur, Puls und Atmung messen | 57 | applied |
| DE | `de/dog-vomiting.md` | 80 | Mein Hund erbricht: Ursachen und wann es ernst wird | 51 | applied |
| DE | `de/giftige-lebensmittel-hund.md` | 80 | Giftige Lebensmittel für Hunde: was tun im Ernstfall? | 53 | applied |
| DE | `de/frettchen-frisst-nicht-erbricht.md` | 78 | Frettchen frisst nicht oder erbricht: Darmverschluss? | 53 | applied |
| DE | `de/meerschweinchen-niest.md` | 78 | Meerschweinchen niest oder atmet schwer: wann zum Tierarzt? | 59 | applied |
| DE | `de/katze-niereninsuffizienz.md` | 77 | Niereninsuffizienz bei der Katze: Anzeichen, Stadien, Alltag | 60 | applied |
| DE | `de/tierarzt-kosten-got-2026.md` | 76 | Tierarztkosten 2026: So funktioniert die GOT | 44 | applied |
| DE | `de/wellensittich-aufgeplustert.md` | 76 | Wellensittich aufgeplustert: ist er krank? | 42 | applied |
| DE | `de/heatstroke.md` | 75 | Hitzschlag beim Hund: Anzeichen und sofortige Kühlung | 53 | applied |
| DE | `de/hund-arthrose.md` | 75 | Arthrose beim Hund: frühe Anzeichen und Hilfe im Alltag | 55 | applied |
| DE | `de/meerschweinchen-vitamin-c.md` | 75 | Vitamin-C-Mangel beim Meerschweinchen: Skorbut erkennen | 55 | applied |
| DE | `de/hund-hat-rattengift-gefressen.md` | 74 | Hund hat Rattengift gefressen: sofort handeln | 45 | applied |
| DE | `de/hund-hustet-und-wuergt.md` | 74 | Hund hustet und würgt: Ursachen und wann es eilt | 48 | applied |
| DE | `de/katze-pinkelt-ins-bett.md` | 74 | Katze pinkelt ins Bett: Ursachen finden statt schimpfen | 55 | applied |
| DE | `de/dog-diarrhoea.md` | 73 | Mein Hund hat Durchfall: wann wird es ernst? | 44 | applied |
| DE | `de/erstes-jahr-welpe-kitten.md` | 73 | Erstes Jahr mit Welpe oder Kitten: Gesundheitsplan | 50 | applied |
| DE | `de/frettchen-faehe-ranz.md` | 72 | Frettchen-Fähe in der Ranz: Warum Dauerranz gefährlich ist | 58 | applied |
| DE | `de/katze-fip.md` | 72 | FIP bei der Katze: Symptome und neue Behandlung | 47 | applied |
| DE | `de/wellensittich-durchfall.md` | 72 | Wellensittich hat Durchfall: wann wird es ernst? | 48 | applied |
| DE | `de/meerschweinchen-frisst-nicht.md` | 71 | Meerschweinchen frisst nicht mehr: warum das ein Notfall ist | 60 | applied |
