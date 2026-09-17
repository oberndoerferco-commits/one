# Prompt library — Instagram and TikTok

Owner: `social-media-manager`. Compiled 17 September 2026.

Everything below is ready to run. Copy a prompt, set the model and ratio it
names, generate. Nothing publishes until the owner approves the exact asset and
the exact caption, and `creative-director` signs off the direction of a batch
before it is generated (house rule 7).

Three files work together:

- this file — the plan, the research it rests on, and the prompts
- `docs/handbook/social-log.md` — what was posted and what it did
- `CLAUDE.md` — voice, retire list, guardrails. All of it applies here.

---

## 1. The four-week posting plan

### The shape

Four posts a week. Sixteen posts in the month. Two reels, one carousel, one
still per week, plus stories on the days between.

| | Mon | Wed | Fri | Sun |
| --- | --- | --- | --- | --- |
| **Format** | Reel, 8–15s | Carousel, 5–7 slides | Reel, 20–40s | Still, 4:5 |
| **Job** | Discovery | Saves | Watch time | The grid |

### Why this shape and not another

**Reels carry discovery; we have no followers, so discovery is the whole job.**
Reels reach non-followers in a way nothing else on the platform does — reported
at 55% of Reels views coming from people who do not follow the account
([Vidico, 2026](https://vidico.com/news/instagram-reels-statistics/)). Metricool's
study of 24,364,803 posts from 375,118 accounts, published 16 June 2026, found
Reels generate "more than four times the interactions of single-image posts"
([Metricool, 16 Jun 2026](https://metricool.com/press-release-instagram-study-2026/)).

**Carousels are the save engine, and saves are how an expensive object gets
remembered.** Same Metricool study: carousels generate "nine times more saves
than single-image posts". Socialinsider's benchmark across 35M posts from
447,613 pages puts carousels marginally ahead of Reels on engagement rate —
0.50% vs 0.48% in Q2 2026 — and well ahead of images at 0.33%
([Socialinsider, 2026](https://www.socialinsider.io/social-media-benchmarks/instagram)).
A €34,250 table trunk is not an impulse. It is a save, then a return, then an
enquiry.

**The single image is no longer a default.** Metricool measured single-image
posts down 21.96% on reach, 25.41% on interactions and 45.98% on engagement
year on year. One still a week, and it earns its place by being the best thing
we made that week.

**Cadence.** Socialinsider's 2026 monthly medians are 8 Reels, 5 carousels and
7 images. TrueFuture Media (4 Feb 2026) puts the sustainable organic sweet spot
at "3-5 Reels per week"
([TrueFuture Media, 4 Feb 2026](https://www.truefuturemedia.com/articles/instagram-reels-reach-2026-business-growth-guide)).
Two a week is the low end on purpose: we would rather make them slowly, and a
thin week of good film beats a full week of filler. Consistency is the variable
that matters, not volume.

**Length.** Ranking runs on watch time, likes-per-reach and sends-per-reach —
the three signals Adam Mosseri has confirmed, with sends weighted more heavily
for content shown to people who do not follow you
([Highstyle summary of Mosseri, 2026](https://www.highstyle.ai/insights/instagram-reels-algorithm-2026)).
Completion beats duration: TrueFuture's guide states plainly that "a 10-second
Reel with 80% retention beats a 60-second Reel with 30% retention", and that
Reels over three minutes are not recommended to non-followers at all. So:
8–15s for the Monday hook, 20–40s for the Friday process film. Nothing over 60s
this month.

**Captions.** First 125 characters carry the hook because that is where the
"more" cut-off falls; the body runs 150–220 words
([Aibrify, 2026](https://aibrify.com/blog/how-to-write-instagram-captions-engagement-2026)).
That length suits this house — it is room enough to name the tannery, the year,
the lining, the number of hours. Institutions and numbers do the boasting.

**No hashtag stacking, and now there is data for it.** Metricool: posts using
hashtags see 31.70% fewer views and 33.89% fewer interactions. TrueFuture:
posts without hashtags achieved 23% higher reach. Three to five, specific,
used as categorisation only.

**Sound.** Mosseri's position in 2026 is that audio *relevance* is rated, not
trend membership. A trending track that has nothing to do with a Milanese
workbench is a negative signal, not a free ride. Default to the real recorded
sound of the work — a knife through hide, a brass catch closing. Craft ASMR is
a live, high-completion format on TikTok right now
([Lensgo, 2026](https://lensgo.ai/blog/ai-asmr-videos-trending-2026)), and it
is the one trend this house can join without pretending to be something else.

### The four weeks

**Week 1 — The material.** Establish what the house is made of before showing
what it sells. Crocodile scale, brass, floccato velvet, nubuck nap. Material
studies are abstract, so they are the safest possible place to generate freely
and the strongest possible opening for a house whose whole claim is material.
Prompts 1–4, 12, 14.

**Week 2 — The object.** The Mirror Handbag and the crocodile wallets. This is
the week the surreal campaign work runs — one signature image, one film. The
mirror in the lid is the single most photographable idea in the catalogue and
nobody has used it. Prompts 5–8, 13.

**Week 3 — The room.** The €27,000 sofa and the €34,250 Table Trunk placed in
generated architecture. Commission tier does not sell from a grid; it sells
from a room a person wants to be in. Prompts 9–11, 15.

**Week 4 — The gift.** The €129 tray, the €395 3-Place Watch Box, the €350–€425
sunglasses. Entry tier, ahead of the gifting months. No discount language, no
countdown, no urgency — the house rule holds. Prompts 16–18, 20.

**Before Week 1, once:** the grid-of-nine launch (prompt 19). A profile with
nothing on it converts nobody. Nine tiles published in one sitting give the
account a spine before the first reel lands on anyone's feed.

**Stories, between posts.** Unedited fragments from the bench. The 2026
argument across every source is that over-produced material now reads as
suspect; stories are where the house is plainly, boringly real.

---

## 2. What the research actually says

Sources dated. Anything I could not date, or that predates March 2026, is
flagged as possibly stale.

### a) Formats and platform mechanics

| Finding | Figure | Source, date |
| --- | --- | --- |
| Reels vs single image, interactions | >4× | [Metricool, 16 Jun 2026](https://metricool.com/press-release-instagram-study-2026/) — 24.4M posts |
| Carousels vs single image, saves | 9× | Metricool, 16 Jun 2026 |
| Average Reel watch time | 8.5s, more than double YoY | Metricool, 16 Jun 2026 |
| Engagement by format, Q2 2026 | Carousel 0.50%, Reel 0.48%, Image 0.33% | [Socialinsider, 2026](https://www.socialinsider.io/social-media-benchmarks/instagram) — 35M posts, Jan–Dec 2025 data |
| Overall IG engagement | 0.48%, down 24% YoY | Socialinsider, 2026 |
| Hashtags | −31.70% views, −33.89% interactions | Metricool, 16 Jun 2026 |
| Ranking signals | watch time, likes/reach, sends/reach | [Mosseri, via Highstyle, 2026](https://www.highstyle.ai/insights/instagram-reels-algorithm-2026) |
| Reels over 3 min | not recommended to non-followers | Highstyle, 2026 |
| 3-second hold rate above 60% | 5–10× total reach vs below 40% | [TrueFuture Media, 4 Feb 2026](https://www.truefuturemedia.com/articles/instagram-reels-reach-2026-business-growth-guide) |
| Burned captions | +38% retention | TrueFuture Media, 4 Feb 2026 |

Note on the conflict: TrueFuture (Jan 2026) reports carousels at ~10.15%
engagement and Buffer's 52M-post study at 6.90% by reach — very different
numbers from Socialinsider's 0.50%. They are measuring against different
denominators (reach vs followers). The *ranking* is consistent across all of
them, and the ranking is what we act on. Do not quote any single figure as
fact without saying which denominator it uses — `performance-analyst` is the
only role permitted to state a number as fact anyway.

**TikTok.** The 2026 register there is "quiet flex" — calm, intentional,
aspirational rather than loud — and companion-format video (do-this-with-me)
is pulling disproportionate engagement
([Gain, 2026](https://blog.gainapp.com/tiktok-trends/)). Process content is
explicitly named as the format that works for makers. Craft ASMR is one of the
highest-growth categories on TikTok, Reels and Shorts, built around
high-completion short loops (Lensgo, 2026). *Possibly stale flag:* the TikTok
sources here are the weakest-dated in this file. Re-check before committing to
a TikTok push.

### b) What comparable houses are posting

Instagram blocks direct fetching, so post-level detail below comes from search
indexes and the brands' own journals, not from reading the feeds. Treat
follower counts as approximate and re-check before quoting.

| House | Handle | Scale | What they are doing |
| --- | --- | --- | --- |
| Serapian | [@serapianmilano](https://www.instagram.com/serapianmilano/) | ~78K, 709 posts | SS26 "The Chiaroscuro" with Bethan Laura Wood — Mosaico bags against Wood's furniture and rugs. Bio leads with the *invention* claim: "Inventor of the iconic Mosaico handcraft technique". ([Serapian journal](https://www.serapian.com/en-it/blogs/news/milan-fashion-week-spring-summer-26)) |
| Valextra | [@valextra](https://www.instagram.com/valextra/) | ~346K, 2,973 posts | SS26 "The Daily Touch", Iside Editor in Millepunte Soft leather and Senso suede. Campaigns named and archived on their own journal, then serialised to the feed. ([Valextra journal](https://www.valextra.com/en-us/journal/campaign-stories/ValextraSS26TheDailyTouch.html)) |
| Moynat | [@moynat](https://www.instagram.com/moynat/) | ~284K, ~254 posts | Very low post count for the follower base. Trunk-making craft, leather marquetry cut by hand. Leads on 1849 and Pauline Moynat's 1873 English Trunk — dates doing the boasting. ([Moynat journal](https://www.moynat.com/blogs/news/the-craft-of-contemporary-trunk-making-1)) |
| Poltrona Frau | [@poltronafrauofficial](https://www.instagram.com/poltronafrauofficial/) | ~344K | Salone del Mobile 2026 "True Over Time" — an argument for design that accumulates meaning rather than ageing. Showroom in a frescoed building, Via Manzoni 30. ([Creativehomex, 2026](https://creativehomex.com/salone-del-mobile-2026-poltrona-frau/)) |
| Baxter | [@_official_baxter](https://www.instagram.com/_official_baxter/) | — | Salone 2026 across three formats: Baxter Cinema, Baxter Journey, La Casa sul Lago. Between Milan and Como. ([Mohd](https://shop.mohd.it/en/news/salone-del-mobile.html)) |
| Frette | [@frette](https://www.instagram.com/frette/) | 2,381 posts | Bio is one line of institution: "A legacy woven. Since 1860. HOMES \| HOTELS \| YACHTS \| JETS." Founded 18 December 1860. ([Frette heritage](https://www.frette.com/en_US/our-heritage.html)) |
| Promemoria | — | — | Could not verify a current official handle or activity from open sources. Do not cite them until we can. |

**Independents at or near our scale — what we could copy tomorrow, free:**

- **Tanner Leatherstein** ([@tanner.leatherstein](https://www.instagram.com/tanner.leatherstein/), ~971K IG, ~2.3M across platforms) cuts luxury bags open on camera and prices the leather. One man, 25 years of tannery knowledge, a knife, and a table. No budget. He now advises Stow London as Director of Craftsmanship ([Yahoo/WWD, 2026](https://www.yahoo.com/news/articles/tiktok-tanner-leatherstein-joins-stow-190000995.html)). **The lesson for us: expertise, shown, is the cheapest content in the sector.** We can cut a hide. We know what a CITES tag means. Nobody in our tier is explaining it.
- **Portland Leather Goods** did its first six-figure TikTok Shop day off an affiliate blitz ([Modern Retail](https://www.modernretail.co/marketing/how-portland-leather-goods-did-1m-in-sales-in-20-days-on-tiktok-shop-thanks-to-an-affiliate-blitz/)). Not our model — volume house, wrong tier — but it proves TikTok is a sales channel, not just reach.
- **Del Giudice Roma**, **Bidinis Bags** (Florence), **Leather Craftsman Rome** — family workshops running Instagram as a window onto a bench. Small, unpolished, specific. This is the register a 269-piece house with inventory-of-one should recognise.

### c) AI-generated content in luxury, September 2026

**This is the most important section in the file, and it cuts both ways.**

**What is landing.** Surrealist CGI is now an established luxury Instagram
language, and Jacquemus wrote it: oversized bags gliding like trams through
Paris, a handbag sailing on Lake Como, bags-as-cars, cranes over Hong Kong.
Tod's, Isabel Marant and Victoria Beckham have followed
([BoF, "Why Surrealist Marketing Is Suddenly Everywhere"](https://www.businessoffashion.com/articles/marketing-pr/why-surrealist-marketing-is-suddenly-everywhere/);
[Tactic One case study](https://www.tacticone.co/blog/jacquemus-innovative-marketing-for-modern-luxury)).
Their FW26 "Le Palmier" ran as surreal social teasers with exaggerated
proportions built for a scrolling environment. **The thing that makes it work:
it is impossible. Nobody could mistake it for a photograph.**

**What is being punished.** Gucci drew sustained backlash for AI-generated
images promoting PRIMAVERA at Milan Fashion Week 2026 — models replaced, a
double-G logo on a satellite, and a widespread read that this was cost-cutting
dressed as creativity ([Outlook Luxe](https://luxe.outlookindia.com/fashion-beauty/couture/gucci-sparks-backlash-after-using-ai-models-for-milan-fashion-week-campaign)).
Valentino was attacked for AI that fused and distorted human bodies. Prada's
SS26 campaign produced unease rather than aspiration
([The Stylist Suitcase](http://thestylistsuitcase.com/articles/is-ai-antithetical-to-luxury-what-pradas-controversial-campaign-reveals-about-fashions-biggest-tension/)).
The criticism is always the same shape: *you are charging for the human hand
and removing the human.*

**The pattern.** Generated *strangeness* is read as authorship. Generated
*people* and generated *plausibility* are read as fraud. Everything in this
library sits on the first side of that line.

**What already reads dated.** The over-polished, over-sharp, perfectly-lit
2024–25 AI look. The counter-move is now standard: film grain searches up 31%,
motion blur up 15%, dust overlays and light leaks as finishing steps
([Artsflick, "The Anti-AI Aesthetic"](https://artsflick.com/blog/anti-ai-aesthetic/)).
The sharpest observation in any source I read: *"if brand photography looks
like it could have been generated, viewers will assume it was — the burden of
proof has flipped."* Practical fix, from the same body of work: anamorphic
lens, 24fps, and a light blur pass plus film grain at 2–3% intensity. Every
prompt below carries grain and lens language for this reason.

**Labelling — and this one is now law for us.** EU AI Act Article 50
transparency obligations apply from **2 August 2026**, with penalties up to
€15M or 3% of worldwide turnover
([European Commission, 29 Jul 2026](https://digital-strategy.ec.europa.eu/en/factpages/quick-facts-transparency-rules-ai-systems)).
A "deepfake" under Article 3(60) is AI-generated content resembling existing
persons, objects, places or events that "would falsely appear authentic".
Physically implausible content — the guidance names dragons and unaided human
flight — falls outside it. Where content is part of "an evidently artistic,
creative, satirical, fictional or analogous work", the obligation is lighter:
communicate the existence of generated content "in an appropriate manner that
does not hamper the display or enjoyment of the work"
([Article 50 guide, 14 May 2026](https://artificialintelligenceact.eu/transparency-rules-article-50/)).

An Italian house publishing to an EU audience is in scope. So:

1. Surreal work is out of deepfake scope by construction — it is not plausible.
   Say it is generated anyway, in the caption, because it is a taste signal.
2. Anything photoreal gets an explicit line. Not an apology — a credit.
3. Meta applies its own "AI info" label from C2PA/IPTC provenance metadata, and
   there is a mandatory disclosure requirement for realistic synthetic video
   and audio; undisclosed AI now risks reduced reach
   ([TechCrunch, 31 Aug 2026](https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/)).
   Do not try to strip metadata. Disclose first and let the label agree with us.

**House caption line, use verbatim:**

> Campaign image, generated. The pieces are made by hand in Italy.

### d) Instagram specs, current

From [HeyOrca, 24 Feb 2026](https://www.heyorca.com/blog/instagram-media-specs-best-practices-2026)
and [Buffer's size guide](https://buffer.com/resources/instagram-image-size/).

| Thing | Spec |
| --- | --- |
| Feed portrait (use this) | 1080 × 1350 px, 4:5 |
| Feed square | 1080 × 1080 px, 1:1 |
| Feed landscape | 1080 × 566 px, 1.91:1 |
| Feed image max file | 30 MB |
| Reel / Story | 1080 × 1920 px, 9:16 |
| Reel duration | 3s to 10 min. **Ours: never over 60s this month.** |
| Story duration | 3s to 60s per card |
| Reel cover | 1080 × 1920, 9:16 — keep everything that matters inside the centre square, because the grid crops to 1:1 and the feed to 4:5 |
| Video max file | 4 GB |
| Video spec | MP4 or MOV, H.264, 30fps, export 1080p |
| Carousel | first slide sets the crop for every other slide — build all slides at the same ratio |

**The 4:5 problem, and the fix.** Not every model we have outputs 4:5. These do
natively: `nano_banana_pro`, `nano_banana_2`, `cinematic_studio_2_5`,
`gpt_image_2_5`, `marketing_studio_image`, `recraft_v4_1`. These do **not**:
`soul_2`, `soul_cinematic`, `seedream_v4_5`, `seedream_v5_pro`, `flux_2`.
When a prompt below names a non-4:5 model, it says to generate at 3:4 and run
`reframe` to 4:5. Do not skip that step and let Instagram crop for you.

---

## 3. What Higgsfield actually gives us

Checked live on 17 September 2026 via `models_explore`, `presets_show` and
`get_workflow_instructions`. This is what exists, not what I assumed.

### Image models worth our time

| Model | Use it for | Ratios | Notes |
| --- | --- | --- | --- |
| `nano_banana_pro` | **The workhorse.** Photoreal material studies, product-in-scene, anything needing 4:5 | incl. 4:5 | `resolution` 1k/2k/4k, default 2k. Takes `image_references` |
| `nano_banana_2` | Faster sibling, same ratios, `is_inpaint` + mask support | incl. 4:5 | Default 1k — raise it |
| `cinematic_studio_2_5` | Cinema-grade stills, dramatic light | incl. 4:5, 21:9 | `resolution` up to 4k |
| `soul_cinematic` | **The surreal/stylised one.** Concept art, campaign strangeness | 1:1, 3:4, 9:16, 21:9 — **no 4:5** | `quality` 1.5k/2k |
| `seedream_v4_5` | Precise transformations, editing an existing shot | no 4:5 | up to ~6K at `quality: high` |
| `seedream_v5_pro` | Instruction-based editing, `is_inpaint`, `remove_bg` | no 4:5 | Best for "change only this" |
| `flux_2` | Hardest prompt adherence — long, clause-heavy prompts | no 4:5 | `variant` pro/flex/max |
| `gpt_image_2_5` | When type has to render correctly | incl. 4:5 | `quality` up to `max` |
| `flux_kontext` | Style transfer, context-aware edit | no 4:5 | |
| `recraft_v4_1` | Vector, logo, flat brand assets | incl. 4:5 | `model_type` selectable |

`soul_2` is tagged fashion/editorial/character and is the obvious reach for
campaign work — but it has no 4:5 and it is built around people. For a house
that does not put invented people in its imagery, `soul_cinematic` and
`nano_banana_pro` are the better pair.

### Video models worth our time

| Model | Duration | Ratios | Notes |
| --- | --- | --- | --- |
| `cinematic_studio_3_0` | 4–15s | incl. 9:16 | Best quality. `resolution` to 4k, `genre`, `generate_audio`. Takes `start_image` / `end_image` |
| `seedance_2_0` | 4–15s | incl. 9:16 | **Reference-driven.** `image_references`, `video_references`, `audio_references`, start/end frames, 4k, `genre`. This is the one that keeps a real product looking like itself |
| `cinematic_studio_video_v2` | 3–12s | incl. 9:16 | `speedramp` (slowmo/impact), `multi_shots`, `cfg_scale`. Good for a 3-shot reel opener in one job |
| `flux_3_video` | 5–20s | incl. 9:16 | Multi-frame, video continuation, synchronised audio |
| `wan2_6` | 5 / 10 / 15s | 16:9, 9:16, 1:1 | Open-weight, stylised, experimental — reach for it when you *want* strangeness |
| `minimax_h3` | 4–15s | incl. 9:16 | 2K only, `batch_size` up to 4 |
| `seedance1_5` | 4 / 8 / 12s | incl. 9:16 | Reliable motion, cheaper fallback |
| `marketing_studio_video` | 12–15s | incl. 9:16 | Ad-shaped. Probably wrong register for us |

### Presets: mostly not for us

`presets_show` returns ~64 image-to-video presets. **They are almost all built
around a person's selfie** — ORBIT 360, FLOAT SPIN, STICKER PEEL, SELFIE TWIN,
ACTION FIGURE, RED CARPET, K-pop broadcast templates, fighting-game loading
screens. Viral formats for creators, not for a maison.

Five are usable on an object:

| Preset | id | Why |
| --- | --- | --- |
| **CGI BREAKDOWN** | `6372c588-7ace-48e9-ad4c-6565c2d2f817` | Mesh → beauty pass, render layers cutting in sequence, turntable. **Declares itself as CGI.** Perfect for our labelling position |
| **3D RENDER** | `5a77643c-b6cc-4efd-bdc6-ab8ff48dfa82` | Orbiting a hyper-detailed model, rotating lights |
| **ORBIT 360** | `b31e4af9-b886-4582-a809-c44caf975d61` | Full orbit, subject still. Works on an object |
| **CLAY FIGURINE** | `cb8f0ef6-6f98-46a7-913e-77f9f275c8fd` | Two hands lift the subject out as matte clay. Surreal, hand-led |
| **SUMMER HAZE** | `94d1e8c6-6efd-4a8b-9dd6-014286918e26` | Lomo home-movie, light leaks, soft grain. The anti-AI finish, as a preset |

Run presets through `higgsfield_preset` with `preset_id` and one required
reference image. Only 16:9, 9:16, 1:1.

### Workflows available

`get_workflow_instructions` with no argument lists sixteen: `ad-multiplier`,
`brand-asset-creation`, `character-sheet`, `faceless-video`, `narrator`,
**`product-photoshoot`**, `subtitles`, `thumbnail-generation`,
`ugc-product-video`, `ugc-review-video`, `ugc-try-on-video`,
`ugc-tutorial-video`, `ugc-unboxing-video`, `ugc-website-video`,
`video-editing`, `website-builder-flow`.

Only two are relevant. **`product-photoshoot`** — load it before any real-piece
composite. **`video-editing`** — load it to cut and title a finished reel. The
UGC family is talking-head creator advertising and is the wrong register for
this house; do not reach for it because it is convenient.

### Supporting tools

`upscale_image`, `upscale_video`, `remove_background`, `reframe` (this is how
3:4 becomes 4:5), `outpaint_image`, `media_upload_widget` (the only way to get
a real product photograph in as a reference), `virality_predictor` (sanity
check, never a decision).

---

## 4. The hard line

From the role file, and it does not move:

> Never present a generated image as a photograph of a real piece a client can
> buy.

| Use | Generate? |
| --- | --- |
| Surreal campaign, atmosphere, abstract material study | Yes, freely |
| A room, a light, a landscape the piece sits inside | Yes |
| A real piece composited into a generated setting | Yes — **the piece must be its real photograph**, loaded via `media_upload_widget` and passed as `image_references` |
| The piece itself, rendered from scratch, shown as product | **No** |
| A product not in the catalogue | **No** |
| An invented client, stockist, celebrity or press moment | **No** |

Every prompt below is tagged **GENERATED** (fully synthetic, caption discloses)
or **COMPOSITE** (real product photograph required as reference). There is no
third category.

Real product photographs live on the Shopify CDN. Pull the exact one from
`search_products` → `featuredMedia.preview.image.url` and upload it. Never
describe a piece and hope the model draws it.

---

## 5. The prompts

### Group A — Material studies (Week 1)

Abstract, close, no product silhouette. The safest generation in the library
and the strongest opening the house has.

---

#### 1. Crocodile scale — the topography

**GENERATED** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still + carousel slide

```
Extreme macro of natural crocodile hide, filling the entire frame so no edge or
silhouette of any object is visible. The scale pattern is genuine and irregular
— large belly tiles toward the lower frame giving way to smaller, tighter scales
at the top, every tile a slightly different size and shape, the seams between
them soft and organic rather than stamped. Deep cognac brown with warm amber
where a single low raking light crosses the surface from the left at around
fifteen degrees, throwing real shadow into the valleys between scales. The
finish holds a low satin sheen, not a lacquer. Shot on a 100mm macro lens at
f/8, focus falling off gently at the top of the frame. Natural window light,
no fill, no reflector. Kodak Portra colour response, fine 35mm film grain at
around 2 percent, very slight anamorphic softening at the frame edges.
Absolutely no text, no logo, no hardware, no stitching, no product shape.
```

Why: opens the account on the material, not the object. The word that carries
it is *irregular* — the scale is natural, not embossed, and that is the claim
the catalogue actually makes about the €720 crocodile wallets.

If it disappoints: the common failure is a machine-regular pattern that reads
as embossed vinyl. Swap to `flux_2` at `variant: max`, 3:4, then `reframe` to
4:5 — Flux holds long clause-heavy prompts better. Or add: *"the scale
pattern is asymmetric and slightly distorted where the hide curved over the
animal's body; no two tiles are congruent."*

---

#### 2. Brass — palladium finish

**GENERATED** · `cinematic_studio_2_5` · 4:5 · `resolution: 4k` · feed still

```
Extreme macro of a solid brass fitting in a palladium finish, a cool silvered
grey with the density and weight of a solid metal rather than a plating. The
surface carries a fine circular brush pattern, catching a single soft light
source as a long elliptical highlight travelling across the frame diagonally.
Around the highlight the metal falls into a deep neutral grey, almost black at
the frame edges. A faint thumbprint sits on one facet, deliberately left. The
background is pure void black. Shot on a 100mm macro at f/11, half the frame in
crisp focus, the rest falling into shallow blur. Single-source studio light
through a large diffusion panel, no second light, no rim. Muted, restrained
colour, cool cast. Fine film grain at 2 percent. No text, no logo, no engraving,
no branding of any kind.
```

Why: the brass is real and specific — solid brass, palladium finish, named on
the Crocodile Belt and the Table Trunk. The thumbprint is the point: a hand was
here.

If it disappoints: brass often generates as yellow gold. Add *"the metal is
silver-grey, not yellow, not gold, not warm"* and drop to `soul_cinematic` at
3:4 for a more dramatic single-source read, then `reframe`.

---

#### 3. Floccato velvet — the interior

**GENERATED** · `nano_banana_pro` · 4:5 · `resolution: 4k` · carousel slide

```
Extreme macro of floccato velvet in a deep saturated colour, the flocked pile
standing dense and upright, catching light differently where it has been brushed
one way and then the other so the surface reads as two shades of the same
colour meeting along a soft diagonal. The nap is short and even, the texture
velvety rather than furry. A shallow moulded recess curves through the lower
third of the frame, its edge softened by the pile. Light falls from a single
high window at the left, raking across the nap so the standing fibres catch and
the laid fibres go dark. Shot on a 100mm macro at f/5.6, very shallow depth of
field, focus on the ridge where the two nap directions meet. Muted colour, no
saturation boost. Fine 35mm grain at 2 to 3 percent. No object, no watch, no
hardware, no text.
```

Why: floccato velvet lines the €395 3-Place Watch Box. It is a specific,
checkable material word — exactly the kind of thing that does the boasting when
adjectives cannot.

If it disappoints: velvet tends to render as fur. Add *"short flocked pile,
under one millimetre, like the inside of a jewellery case, not fur, not
carpet"*. Try `seedream_v4_5` at 3:4, `quality: high`.

---

#### 4. Nubuck nap — the buffed surface

**GENERATED** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

```
Extreme macro of Italian Nabuk calf leather buffed to a short nap, the surface
matte and slightly powdery, absorbing light instead of reflecting it. A hand has
drawn once across the nap from the lower right, leaving a paler track where the
fibres lie against their natural direction — the mark sits there and does not
recover. Warm sand-taupe, the colour deepening where the nap is undisturbed.
Light comes from a single large north window, soft and directionless, with no
specular highlight anywhere in the frame because the surface has no shine to
give. Shot on a 100mm macro at f/8. Natural light only, no studio strobe.
Restrained, desaturated colour. Fine 35mm film grain at 2 percent. No stitching,
no edge, no object silhouette, no text.
```

Why: the Wine Holder Leather Box is described in the catalogue as "Italian
Nabuk calf leather buffed to a short nap so the surface reads matte rather than
polished". That sentence is the prompt. The hand-drawn track is the honest
demonstration of what nubuck does — and it is a reel hook waiting to happen.

If it disappoints: it will probably come back too shiny. Add *"completely
matte, zero specular reflection, the surface is velvety and light-absorbing"*.

---

### Group B — The signature campaign (Week 2)

---

#### 5. The signature image — a wallet the size of a building

**GENERATED** · `soul_cinematic` · 3:4 → `reframe` to 4:5 · `quality: 2k` · feed still, the month's anchor

```
An impossible scale illusion in a real Milanese street. A single crocodile
leather card wallet in deep cognac stands upright at the height of a four-storey
building in a narrow street of ochre and grey Milanese facades, filling the gap
between two buildings the way a monument would. Its natural scale pattern is
legible even at architectural scale, each tile the size of a window, catching
early morning light. The street below is empty and wet from rain, reflecting the
object. Two shuttered shopfronts and a single parked bicycle give the scale
away. Shot from ground level on a 35mm anamorphic lens at f/4, slight barrel
distortion at the edges, the top of the object cut by the frame. Overcast dawn
light, cool blue-grey, one warm patch where sun breaks between the roofs. Shot
on 35mm film, visible grain at 3 percent, gentle halation on the highlights,
slight lens flare. Muted, almost monochrome palette apart from the cognac.
No people, no text, no signage, no logo.
```

Why: this is Jacquemus's grammar — object at impossible scale in a real city —
and it is the most copied idea in luxury social right now because it works and
costs nothing. It is also *explicitly implausible*, which puts it outside the
EU AI Act's deepfake definition by construction.

Caption line: `Campaign image, generated. The pieces are made by hand in Italy.`

If it disappoints: the scale illusion collapses if the model does not include
human-sized reference objects. Add *"a single café chair on the pavement for
scale"* and push the camera lower: *"camera at ankle height looking steeply
up"*. Alternative model: `flux_2` at `variant: max`, 3:4.

---

#### 6. The signature film — the same wallet, moving

**GENERATED** · `cinematic_studio_3_0` · 9:16 · 10s · `resolution: 1080p` · `genre: drama` · `generate_audio: false` · reel

Use the still from prompt 5 as `start_image`.

```
Slow continuous crane move rising from ground level up the face of a giant
crocodile leather wallet standing between two Milanese buildings, the scale
tiles passing the lens like the stonework of a facade. The camera keeps rising
past the top edge of the object and holds on the empty grey sky above it for
the final two seconds. No cuts. Anamorphic 35mm lens, shallow depth, slight
breathing in the focus. Overcast dawn, cool blue-grey, wet street below.
35mm film grain, gentle halation. No people, no text, no camera shake.
```

Why: one uninterrupted move, ten seconds, nothing to cut away from — built for
completion rate, which is the signal that matters. Generate audio separately or
lay a recorded atelier sound under it; model-generated audio on a silent
architectural shot tends to invent traffic.

If it disappoints: `cinematic_studio_video_v2` at 3–12s with
`speedramp: slowmo` and `cfg_scale: 0.8` for tighter prompt adherence.

---

#### 7. The Mirror Handbag — the mirror as the idea

**COMPOSITE** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

**Reference required:** the real photograph of The Mirror Handbag - Black
(€1,590) or Nude / Lavender / Pink / Blue (€1,675) from Shopify
`featuredMedia`, uploaded via `media_upload_widget`, passed as
`image_references`.

```
Place the handbag from the reference image, unchanged in every detail of its
shape, colour, leather grain, stitching and hardware, open on a pale plaster
ledge in a bare room. The lid is raised so the mirror set into its underside is
visible and doing its job: what the mirror returns is not the room but a
different room entirely — a corridor of warm lamplight receding far further
back than the physical space allows. The room itself is cool, empty, north-lit,
a single tall window out of frame to the left. Shot on an 85mm lens at f/2.8,
focus precisely on the mirror surface, the bag's near edge falling soft.
Natural light only. Muted colour, cool shadows, warm light living only inside
the mirror. Fine 35mm film grain at 2 percent. Do not alter, restyle,
recolour or redraw the bag in any way. No people, no reflection of a person in
the mirror, no text.
```

Why: a mirror built into the lid — genuinely useful, not decorative — is the
single most photographable detail in the catalogue and it is currently doing
nothing. A mirror that returns the wrong room is surreal without touching the
product, and the product stays a real photograph.

Caption: name the mirror, name the sheep leather, name the Alcantara interior.

If it disappoints: if the model restyles the bag, switch to `seedream_v5_pro`
with `is_inpaint: true` and mask everything except the mirror panel — that model
is built for "change only this". Never accept an output where the bag has
changed.

---

#### 8. The crocodile wallet, composited into weather

**COMPOSITE** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of Crocodile Wallet - Cognac,
Light Brown, Dark Blue, Turquoise, Black/Khaki or Chocolate (all €720).

```
Place the wallet from the reference image, entirely unchanged in shape, colour,
scale pattern, edge finish and stitching, resting flat on a slab of wet grey
Ligurian stone at the edge of the sea. Sea spray has just crossed the frame and
beads of water sit on the stone around the wallet but not on it. Behind, out of
focus, a grey-green Mediterranean under a low overcast sky. Late afternoon,
flat diffuse light, no sun. Shot on a 50mm lens at f/2, the wallet sharp and
everything beyond it dissolving. Cool desaturated palette, the wallet the only
warm thing in the frame. Shot on 35mm film, grain at 3 percent, slight
halation. Do not alter the wallet in any way. No people, no hands, no text.
```

Why: real object, generated weather. Exactly the permitted category. The
wallet is the only warm thing in a cold frame — a composition rule that makes
an object read as valuable without a single adjective.

If it disappoints: if the compositing edge looks pasted, run
`remove_background` on the product photograph first, then re-run. Or generate
the empty scene alone and composite in `seedream_v5_pro` with `is_inpaint`.

---

### Group C — Furniture in generated architecture (Week 3)

---

#### 9. The sofa in a room that does not exist

**COMPOSITE** · `cinematic_studio_2_5` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of Leather Sofa - Orange or Black
(€27,000).

```
Place the sofa from the reference image, unchanged in its proportions, leather
colour, surface texture, seams and feet, alone in a vast empty room with raw
lime-plaster walls and a bare concrete floor. The room is far too large for one
sofa, and that is the composition: the sofa sits slightly left of centre in the
lower third, with three quarters of the frame given to wall, floor and air. A
single tall arched window, out of frame to the right, throws one long
parallelogram of afternoon sun across the floor that stops just short of the
sofa's nearest foot. Dust hangs in the light. Shot on a 35mm lens at f/5.6 from
standing height. Natural light only, no fill. Warm ochre plaster against cool
shadow, restrained colour. Shot on 35mm film, grain at 2 percent, slight
vignette. Do not alter the sofa in any way. No people, no other furniture,
no art on the walls, no text.
```

Why: commission-tier pieces do not sell from a product grid. The room does the
selling. An empty room with one object also solves the practical problem that
we have no interiors photography and no budget to shoot any.

If it disappoints: if it fills the room with furniture, add *"the room is
completely empty apart from the sofa; no tables, no lamps, no rugs, no
plants"*. Try `nano_banana_pro` for tighter instruction-following.

---

#### 10. The Table Trunk, opened

**COMPOSITE** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of Table Trunk (orange or black
full-grain calf, palladium hardware, €34,250).

```
Place the table trunk from the reference image, unchanged in its leather colour,
grain, corner protection, strapping and metal hardware, standing closed at the
centre of a long empty gallery with a vaulted brick ceiling and a stone floor
worn smooth. The gallery recedes deep into the frame, arch after arch, lit only
by small high windows so the light falls in discrete pools and the far end goes
dark. The trunk sits in the nearest pool of light, its palladium fittings the
brightest points in the frame. Shot on a 28mm lens at f/8 from slightly above
floor level, one-point perspective straight down the gallery. Natural light
only. Cool grey-brown palette, the leather the only saturated colour. Shot on
35mm film, grain at 3 percent, deep natural vignette. Do not alter the trunk
in any way. No people, no crates, no text.
```

Why: a trunk built to the old method belongs in old architecture. The
one-point perspective reads as an institution — which is the register the house
is reaching for.

If it disappoints: for a stranger, more campaign-like read, generate the empty
gallery alone with `soul_cinematic` at 3:4, then composite the real trunk in
`seedream_v5_pro` with `is_inpaint: true`, then `reframe` to 4:5.

---

#### 11. The trunk, opening — the film

**COMPOSITE** · `seedance_2_0` · 9:16 · 8s · `resolution: 1080p` · `genre: drama` · `generate_audio: false` · reel

**Reference required:** two real photographs of the Table Trunk, closed and
open, as `start_image` and `end_image`. Pass the hero shot as
`image_references` to hold the identity.

```
The trunk stands closed in a dark vaulted gallery. Over eight seconds the lid
rises slowly on its hinges, and as it opens, warm light spills out from inside
the trunk onto the stone floor — far more light than the interior could
physically hold. The camera does not move. The lid stops fully open. No cuts.
Anamorphic 35mm lens, shallow depth, focus on the front edge of the lid.
Everything outside the trunk stays cold and dim. 35mm film grain, gentle
halation on the escaping light. No people, no hands, no text.
```

Why: light escaping an object is a completion-rate device — a viewer stays to
see what is inside. `seedance_2_0` is the reference-driven model in the roster;
it is the one that keeps a real product looking like itself across frames.

If it disappoints: `cinematic_studio_3_0` with the same start and end frames,
`genre: epic`, 10s.

---

### Group D — The hand at work (Week 1 and running)

---

#### 12. Hands, a knife, a hide

**GENERATED** · `cinematic_studio_3_0` · 9:16 · 12s · `resolution: 1080p` · `genre: drama` · `generate_audio: true` · reel

```
Overhead shot, camera locked off, of a worn wooden workbench. Two hands — adult,
unmanicured, a small old scar across one knuckle — hold a steel round knife and
draw it once, slowly and continuously, through a large panel of vegetable-tanned
leather. The cut opens behind the blade in a single clean line. The hands are
unhurried and the cut does not stop. Around the bench: a steel rule, a bone
folder, a scatter of offcuts, a chalk line already drawn on the hide. Light
comes from one high north window at the left, the rest of the workshop dark.
Shot on a 50mm lens at f/4 from directly above. Natural light only, no studio
light, no colour grade. Warm brown leather against cool grey light. Shot on
35mm film, grain at 3 percent, very slight handheld drift. No face, no
speaking, no text, no logo.
```

Why: process video is the most reliably engaging thing a maker can post — and
Tanner Leatherstein has built 2.3 million followers on almost exactly this
frame, with a knife and a table. Locked-off overhead, no face, one continuous
action: high completion by construction.

**Label it.** This one is photoreal and could pass for documentary footage.
Mandatory disclosure applies to realistic synthetic video. Caption must carry
the generated line, prominently.

If it disappoints: hands are still where these models fail — six fingers,
melting knuckles. Reduce to 8s, tighten to *"only the hands and the blade in
frame, the wrists cut by the frame edge"*, and try `seedance_2_0` at 8s, which
handles hands better. **Better still: film this one for real.** It costs a
phone, a window and an afternoon, and an unlabelled real hand beats a labelled
generated one every time.

---

#### 13. The mirror snapping shut — ASMR loop

**COMPOSITE** · `seedance_2_0` · 9:16 · 4s · `resolution: 1080p` · `generate_audio: true` · reel, looping

**Reference required:** real photograph of any Mirror Handbag, as
`image_references`.

```
Tight macro on the lid of the handbag from the reference image, unchanged in
colour, grain and hardware. Over four seconds the lid closes and the catch
engages with one precise mechanical click. The mirror inside flashes once as it
swings past the light and then is gone. The camera does not move. 100mm macro
lens at f/2.8, focus on the catch. Single soft side light, everything else dark.
Muted colour. Fine film grain. Loops seamlessly — the last frame matches the
first. Sound: only the leather compressing and the metal catch closing, close
and dry, no music, no room tone. No hands, no people, no text.
```

Why: craft ASMR is one of the highest-growth short-form categories right now
and it is built on seamless, repetitive, high-completion loops. Four seconds
that loop cleanly can be watched twenty times by one person, and watch time is
the first ranking signal.

If it disappoints: if the loop seams, generate 5s and trim in `video-editing`.
If the sound is wrong — and model-generated foley usually is — strip it and lay
a real recording of the actual catch. That fixes it permanently and costs
nothing.

---

#### 14. The stitch — locked macro

**GENERATED** · `cinematic_studio_video_v2` · 9:16 · 6s · `speedramp: slowmo` · `sound: off` · reel or story

```
Extreme macro, camera locked off, of a saddler's needle pulling waxed linen
thread through two layers of leather in a single slow stitch. The thread drags
through the hole with visible friction, the leather compressing slightly at the
entry point and releasing as the thread clears. Fingers enter the frame only at
the edges. One high side light, deep shadow everywhere else. 100mm macro at
f/4, focus locked on the needle's exit point. Muted warm brown against near
black. 35mm film grain at 3 percent. No face, no text, no music.
```

If it disappoints: `flux_3_video` at 5s with `generate_audio: false`, or shoot
it on a phone with a clip-on macro lens.

---

### Group E — The gift (Week 4)

---

#### 15. The pouf, placed

**COMPOSITE** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of Blue, Black, Brown or Orange
Leather Pouf (€595).

```
Place the pouf from the reference image, unchanged in colour, leather texture,
seams and proportions, alone at the foot of a tall window in an otherwise empty
room with bare boards and pale walls. Late afternoon sun comes through the
window at a low angle, throwing the window's frame as a long shadow across the
floor and up the side of the pouf. Nothing else is in the room. Shot on a 35mm
lens at f/4 from seated height. Natural light only. Warm light, cool shadow,
restrained palette. 35mm film grain at 2 percent. Do not alter the pouf in any
way. No people, no plants, no books, no text.
```

---

#### 16. The €129 tray, as a gift

**COMPOSITE** · `nano_banana_pro` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of any Leather Tray (€129) — Brown,
Dark Blue, Dark Green, Red, Black, White/Blue, Yellow and Brown, Black and
Yellow, or Dark Green and Brown.

```
Place the leather tray from the reference image, unchanged in colour, calf
leather texture, folded corners and proportions, on a dark walnut dresser in a
quiet hallway at the end of a day. In the tray: a single set of house keys on a
plain ring, and nothing else. Beside the tray on the dresser, a folded pair of
reading glasses. Light comes from one warm lamp out of frame to the right, low
and domestic, the rest of the hallway falling into dusk. Shot on a 50mm lens at
f/2, focus on the keys, the far edge of the dresser soft. Warm tungsten light
against cool blue evening shadow. 35mm film grain at 2 percent. Do not alter
the tray in any way. No people, no hands, no wrapping, no ribbon, no text.
```

Why: the tray is the cheapest way into this house, and the argument for it is
not luxury — it is that keys have somewhere to land. The keys and the reading
glasses do the work. No ribbon: gifting is implied by the domestic scene, not
announced. No discount language, no urgency, per house rules.

If it disappoints: if it adds wrapping paper or a bow, repeat the negatives and
add *"nothing is wrapped; this is a home, not a shop"*.

---

#### 17. The watch box, opened at night

**COMPOSITE** · `cinematic_studio_2_5` · 4:5 · `resolution: 4k` · feed still

**Reference required:** real photograph of a 3-Place Watch Box (€395) in Dark
Green, Grey, Yellow, Blue, Red or Green.

```
Place the watch box from the reference image, unchanged in leather colour,
proportions, lid and lining, open on a dark wooden bedside table. The three
floccato velvet slots are visible and all three are empty. A single low lamp
sits behind and to the left, so the velvet catches the light along the near
edge of each recess and goes black in the hollows. The room beyond is dark.
Shot on an 85mm lens at f/2.8, focus on the nearest slot. Warm lamplight, deep
shadow, very restrained colour. 35mm film grain at 2 percent. Do not alter
the box in any way. No watches, no people, no hands, no text.
```

Why: the empty slots are the invitation. A box shown full is furniture; a box
shown empty is a question. Floccato velvet and the wood core are the material
facts the caption should carry.

---

#### 18. Acetate and light — the sunglasses

**GENERATED** · `nano_banana_pro` · 4:5 · `resolution: 4k` · carousel slide

```
Extreme macro of a block of transparent bottle-green cellulose acetate, cut and
hand-polished, standing on a white surface with strong low sun passing straight
through it. The acetate throws a saturated green caustic across the surface
beyond it, sharp-edged where the block is polished and diffuse where it is cut.
Inside the material, faint darker striations are visible in the depth of the
block — the pattern lives in the material rather than on it. No frame shape, no
lens, no hinge, no spectacles; this is raw material only. Shot on a 100mm macro
at f/8. Hard direct sunlight, single source. Saturated green against bare white,
everything else neutral. 35mm film grain at 2 percent. No text, no logo.
```

Why: material-first for the eyewear, exactly as Group A is for the leather. The
frames are cut and polished by hand in Italy from organic cellulose acetate and
fitted with Zeiss lenses — both real, checkable facts, both doing more work than
any adjective. Pair with the real photographs of the Bottle Green Narcos (€425)
or Green Rectangle (€390).

---

### Group F — Structure

---

#### 19. The grid of nine — the launch

**Run before anything else.** Nine tiles, published in one sitting, so an
account that has never posted has a spine the moment the first reel lands.

Three by three, read as one image:

| | Left | Centre | Right |
| --- | --- | --- | --- |
| **Top** | Crocodile macro (prompt 1) | The signature image (prompt 5) | Brass macro (prompt 2) |
| **Middle** | Floccato velvet (prompt 3) | Mirror Handbag (prompt 7) | Nubuck nap (prompt 4) |
| **Bottom** | Acetate (prompt 18) | Table Trunk in the gallery (prompt 10) | The tray at dusk (prompt 16) |

Materials on the diagonals, objects down the centre column. Five generated, four
composited from real photographs.

**Build them all at 4:5, 1080 × 1350.** The grid crops to a square preview but
the post opens at 4:5, so compose so each tile survives a centre-square crop —
nothing important in the outer 12% of the frame.

To keep the nine looking like one hand, append this to every prompt in the set:

```
Consistent house treatment across the set: single-source natural light, one
direction only; muted desaturated palette with a single warm accent; 35mm film
grain at 2 to 3 percent; slight anamorphic edge softening; no text anywhere in
the frame; no logo; no people.
```

If they do not cohere: generate all nine on one model rather than mixing.
`nano_banana_pro` at 4:5 / 4k is the most consistent across subjects. For the
two that need `soul_cinematic`, run 3:4 and `reframe`.

---

#### 20. The reel opener — the house signature

**GENERATED** · `cinematic_studio_video_v2` · 9:16 · 3s · `multi_shots: false` · `sound: off` · use in front of every reel

```
Three seconds, one move. The frame opens in complete darkness. A single hard
edge of light travels from left to right across an unidentifiable leather
surface, raking low so the grain stands up as it passes and flattens again
behind it. The light reaches the right edge of the frame and the screen returns
to black. The camera does not move. Extreme macro, 100mm at f/5.6. Warm brown
in the light, pure black outside it. 35mm film grain at 3 percent. Absolutely
no text, no logo, no type.
```

Why: a three-second signature that is the same every time teaches a returning
viewer whose reel they are watching before any content arrives — and it holds
the 3-second window, where a hold rate above 60% is reported to deliver 5–10×
the reach of one below 40%.

Generate it once. Reuse it forever. Cut it in via the `video-editing` workflow.

---

#### 21. Seasonal — the months ahead

Three prompts, one per month, each a variation on Group A's material-first
grammar so the account does not change character for a season.

**October — the turn of the light.** `nano_banana_pro`, 4:5, 4k.

```
Extreme macro of cognac calf leather across which a low autumn sun falls
through a window, throwing the sharp shadow of a bare branch across the grain.
The shadow is crisp at one end and diffuse at the other. The leather is warm
and matte. Single-source low afternoon light from the left at a steep angle.
100mm macro at f/8. Warm amber against cool shadow. 35mm film grain at 2
percent. No object, no text.
```

**November — frost.** `cinematic_studio_2_5`, 4:5, 4k.

```
Extreme macro of a solid brass fitting in palladium finish, cold to the point
that a fine bloom of condensation has formed across one facet and is just
beginning to run. The metal reads silver-grey and unmistakably cold. Single
hard light from high left, deep neutral black elsewhere. 100mm macro at f/11.
Cold, almost blue-cast, near-monochrome. 35mm film grain at 2 percent. No
text, no logo.
```

**December — lamplight.** `nano_banana_pro`, 4:5, 4k.

```
Extreme macro of deep green floccato velvet lit by a single candle out of frame
to the right, the flame's movement visible as the light shifts unevenly across
the nap. The pile is dense and short. Everything beyond the reach of the flame
is black. 100mm macro at f/2.8, very shallow focus. Warm flickering tungsten
against black. 35mm film grain at 3 percent. No object, no hands, no text.
```

No countdown, no discount, no urgency, in any month. House rules hold through
the gifting season.

---

## 6. Real product reference

Pulled live from Shopify on 17 September 2026 via `search_products`. Use these
names, prices, colours and materials verbatim. Do not write from memory.

| Piece | Price | Material, as the catalogue states it | Status |
| --- | --- | --- | --- |
| Leather Tray — nine colourways | €129 | Calf leather | Active |
| 3-Place Watch Box — Dark Green, Grey, Yellow, Blue, Red, Green | €395 | Wood core, Italian leather outside, **floccato velvet** inside | Active |
| Watch & Jewelry Box — Turquoise, Brown, Orange | €619 | Calf leather, fitted watch roll inside | Active |
| Leather Pouf — Blue, Black, Brown, Orange | €595 | Calf leather, by hand in Italy | Active |
| Sunglasses — nine frames | €325–€425 | Hand-cut and polished organic cellulose acetate, **Zeiss lenses** | Active |
| Crocodile Wallet — Cognac, Light Brown, Dark Blue, Turquoise, Black/Khaki, Chocolate | €720 | Genuine crocodile, **scale pattern natural, not embossed**, CITES certified | Active |
| Crocodile Passport Holder — military green | €720 | Genuine crocodile, natural scale | Active |
| Blue Alligator Wallet | €765 | Genuine alligator, CITES certified | Active |
| Leather Watch Box — Black, Cognac, Jeans Blue | €1,110 | Grained calf, **Alcantara**-lined cushioned slots, three watches | Active |
| The Mirror Handbag — Black | €1,590 | Mirror built into the lid; sheep leather, Alcantara interior | Active |
| The Mirror Handbag — Nude, Lavender, Pink, Blue | €1,675 | As above | Active |
| Wine Holder Leather Box | €1,625 | **Italian Nabuk calf, buffed to a short nap** | Active |
| Vault Bag | €1,840 | Rigid form wrapped in calf leather | Active |
| Jewelry Box x **Trax NYC** | €1,930 | Full-grain calf outside, **red Alcantara** inside | Active |
| Leather Necklace Box | €2,190 | Rigid core, Italian calf, gold-tone studs set through the panels | Active |
| Gold Trunk mini x **Trax NYC** | €2,230 | Calf, solid brass galvanised in gold, Alcantara lining | Active |
| The Mirror Handbag in Ostrich | €3,825 | Ostrich, mirror in the lid | Active |
| Briefcase x **Trax NYC** | €5,125 | Full-grain calf | Active |
| Ostrich Mini Trunk Handbag | €6,298 | Genuine ostrich, natural quill pattern | Active |
| Necklace Box x **Trax NYC** | €7,560 | Presentation case and strongbox | Active |
| Leather Sofa — Orange, Black | €27,000 | Full-grain calf, frame and upholstery by hand in Italy | Active |
| Table Trunk — Orange, Black | €34,250 | Full-grain calf, **palladium hardware** | Active |

Almost all of these are inventory 1. Never write a caption that implies stock.

**Trax NYC is a real, named collaboration in the catalogue.** It is the only
institution this house currently has to point at. Use it — Frette says
"Official Purveyor to the Italian Royal Family, 1881"; we can say "the trunk
Trax NYC uses to carry pieces to private showings." Never invent a second one.

### Three flagged queries — checked, and all three are false alarms

The social brief raised three material doubts. `co-founder` verified each
against the live Admin API on 17 September 2026. **None of them stands.** The
copy is more precise than the query assumed, and no caption needs changing.

1. **The sofa is not a contradiction.** The description already distinguishes
   the two hides on the same piece: *"The body is pebbled calf… The cushions are
   nubuck, the same hide buffed to a fine nap, so the contrast is felt more than
   seen."* Full-grain calf for the body, nubuck for the cushions, and nubuck is
   that same calf buffed. The `nubuck sofa` tag is accurate for the cushions.
   Both €27,000 sofas, black and orange, read this way.

2. **Nabuk *is* calf.** Nabuk (nubuck) is calf buffed to a fine nap — it is a
   finish, not a different animal, so "Nabuk" and "calf" are not alternatives.
   The €1,930 box says so in its own first line: *"grey Nabuk, the calf we buff
   to a fine, velvety nap… lined in Alcantara inside."* Nabuk outside, Alcantara
   lining. Correct as written.

3. **The €3,389 watch box exists.** *8-Place XL Watch Box*, handle
   `premium-8-place-watchbox`, ACTIVE, €3,389. Its `materials_craft` is filled
   and unusually good — wood core, suede lining, 70mm pillows *"sized at 70mm,
   which is what a larger watch case needs to sit level rather than tipping
   against a pillow cut for a smaller diameter"*, solid brass palladium corners.
   Note it carries inventory 0 on CONTINUE, so it sells as made-to-order.

**The lesson for the house, not the writer.** Three doubts, three hours of
delay, zero real faults — because the material vocabulary is genuinely
specialist. Nabuk, floccato, Alcantara, pebbled calf and full-grain are
distinctions this catalogue makes correctly and most people would not.
`atelier-director` exists precisely so this check takes a minute rather than
blocking a batch: route material questions there first, and only escalate what
survives it.

## 7. Running order, first month

| | Post | Prompt | Format |
| --- | --- | --- | --- |
| **Day 0** | Grid of nine | 19 | 9 × still |
| W1 Mon | Crocodile scale, moving | 1 → animate via CGI BREAKDOWN preset | Reel 8s |
| W1 Wed | Four materials, named | 1, 2, 3, 4 | Carousel 5 |
| W1 Fri | Hands, knife, hide | 12 | Reel 12s |
| W1 Sun | Brass, palladium | 2 | Still 4:5 |
| W2 Mon | The mirror snapping shut | 13 | Reel 4s loop |
| W2 Wed | The Mirror Handbag, six ways | 7 + real photographs | Carousel 6 |
| W2 Fri | The signature film | 6 | Reel 10s |
| W2 Sun | The signature image | 5 | Still 4:5 |
| W3 Mon | The stitch | 14 | Reel 6s |
| W3 Wed | One room, one object | 9, 10, 15 | Carousel 5 |
| W3 Fri | The trunk, opening | 11 | Reel 8s |
| W3 Sun | The sofa in the empty room | 9 | Still 4:5 |
| W4 Mon | Acetate and light | 18 | Reel 8s |
| W4 Wed | Where keys land | 16 + tray colourways | Carousel 7 |
| W4 Fri | The watch box, opened at night | 17 | Reel 20s |
| W4 Sun | October, the turn of the light | 21 | Still 4:5 |

Every reel opens with prompt 20. Every fully generated asset carries the
disclosure line. Every caption passes `creative-director`; every material claim
passes `atelier-director`; nothing posts without the owner approving that exact
asset and that exact caption.

---

## 8. What worked

Empty. Fill it as results come in — prompt number, what it produced, what it
did. A prompt library that compounds is worth more than any single post. Log
batches to `docs/handbook/social-log.md`.

| Date | Prompt | Model | Result | Posted | Performance |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
