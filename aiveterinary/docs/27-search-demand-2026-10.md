# What pet owners search for: demand by species and language (EN/IT/DE)

As of 24 October 2026. The strongest demand in all three languages is the **"can my pet eat X?"** question. It is the largest cluster for every species with enough data, and the site answers it only partially: the toxic-food lists cover what is bad, while owners mostly ask about everyday fruit and vegetables such as banana, watermelon, tomato, cucumber, melon and peach. The second-strongest pattern is **"my pet ate / swallowed something"**: a long tail of objects (socks, plastic, corn cobs, string, hair ties) and household substances that the four existing "ate X" articles do not cover. For the new species, demand is high in English, solid in German and thin in Italian. German horse, guinea-pig and tortoise searches are as specific as English ones. Italian autocomplete often returns 0–2 completions for exotic health terms. **Tortoise hibernation** is the clearest seasonal opportunity right now: it is a top cluster in all three languages in late October.

Autocomplete shows what people type and how they phrase it. It does not show volume. Scores below compare topics within one species and language, not across them.

## Method

1. **Google autocomplete** (`suggestqueries.google.com/complete/search?client=firefox`). 208 seed entries across 9 species and 3 languages, in the owners' own phrasing ("my dog", "dog ate", "can dogs eat", "il mio cane", "cane ha mangiato", "il cane può mangiare", "mein Hund", "Hund hat", "dürfen Hunde", plus species nouns such as cavia, Meerschweinchen, cavallo, Pferd, pappagallino, Wellensittich, furetto, Frettchen, tartaruga, Landschildkröte, Bartagame, geco leopardino, Leopardgecko, Königspython). Locales were en-GB and en-US, it-IT, and de-DE and de-AT. The 79 most important seeds got a–z suffixes in the primary locale (en-GB, it-IT, de-DE). After that, 118 targeted probes checked topics the seeds did not reach (for example "hufrehe", "laminite cavallo", "rabbit flystrike", "wellensittich legenot"). For those, the evidence is the **completion depth** (how many of the 10 slots are filled). In total there were 2,520 requests (58 empty) returning 23,601 suggestions, fetched on 24 Oct 2026 at about 0.3–1 request/s. The raw JSON is in the scratchpad at `/tmp/claude-0/-home-user-one/6e9bfa3a-6269-5d29-95e9-19ab20e08690/scratchpad/seo/autocomplete/`, with the scripts in `../scripts/` and the aggregates in `../agg.json`, `../clusters.json` and `../probes.txt`.
2. **Scoring.** Each suggestion earns (10 − position)/10 every time it appears. The weight is 1.0 under a plain seed and 0.5 under an a–z suffix seed. A cluster's score is the sum over its distinct queries, written in the tables as *score/queries*. Suggestions are kept only if they name the species, and obvious noise is dropped (breeds, films, games, "for sale", translations, "snake plant", "tortoiseshell cat"). The remaining suggestions are assigned to about 90 topic clusters by keyword rules in all three languages. 56% of the kept suggestions fall into a cluster; most of the rest are breed, media and brand queries.
3. **Intent.** Each cluster is tagged *worry/emergency* (something is wrong or was eaten), *care/how-to*, *food safety* ("can X eat Y") or *behaviour*.
4. **Google Trends was blocked.** On 24 Oct 2026 the explore API returned HTTP 429 on every attempt, with and without a session cookie. Only the generic daily-trends RSS answered, and it cannot compare terms. **No Trends data is used.**
5. **Coverage.** Every cluster was checked against the titles of `site/src/content/animals/*.md`, `it/*.md` and `de/*.md`, and marked covered, partial (the topic sits inside a broader article) or **gap**.

## Limits

- **Autocomplete is a popularity signal, not a volume.** It is filtered, partly personalised and recency-weighted. It hides some sensitive completions and favours queries with many variants. The a–z expansion strongly favours list-shaped topics such as "can dogs eat [food]", so the food-safety cluster is inflated relative to single-phrase topics like "dog panting". The ordering *within* a cluster is more reliable than the gap *between* clusters.
- **Scores are not comparable across languages or species.** IT and DE return fewer and shorter completions for niche topics. That partly reflects lower demand and partly thinner data. de-AT and en-US got base seeds only.
- **Rule misses.** German puts the verb last ("Hund hat Plastik gefressen"), so some swallowed-object queries landed in the generic "ate something" cluster in DE. The gap tables give hand counts for these.
- **Seasonality.** The data were fetched in late October, which lifts hibernation (letargo, Winterstarre), autumn fruit (Zwetschgen, castagne), and lowers summer topics such as heatstroke and stings.
- **US results leak into en-GB** (Zyn nicotine pouches, skunks, edibles). We discount US-only items for an EU site.
- **The seed list shapes what is seen.** The probes partly correct for this, but there may be clusters nobody seeded.
- **Published studies** come mostly from the US and UK, and several are commercial PR with undisclosed methods. They corroborate direction, not size.

## Published evidence (each source opened)

| Date | Source | What it found | Weight |
|---|---|---|---|
| 17 Nov 2025 | Prestige study, reported by [Swansea Bay News](https://swanseabaynews.com/?p=107702) (UK, method not disclosed) | Monthly "can dogs eat…" searches: strawberries 24,000, bananas 20,000, pineapple 17,000, apples and tomatoes 16,000, blueberries 15,000, watermelon 12,000, cheese 11,000 … chocolate 2,400 | Matches the autocomplete order (bananas, watermelon, strawberries and tomatoes lead). Commercial source. |
| 21 Apr 2025 | [MetLife Pet Insurance](https://www.metlifepetinsurance.com/pet-health-across-america/) (US, Google Trends Jan 2024–Jan 2025, plus a survey of 1,227 owners) | Top dog ailment searches: Cushing's, parvovirus, cancer. Top cat ailment searches: parasites, FeLV, FIV | Disease-name searches; US only |
| Jun 2024 | Springer, Lund, Corr, Sandøe, [Frontiers in Veterinary Science 11:1417927](https://pmc.ncbi.nlm.nih.gov/articles/PMC11223573/) (AT/DK/UK owners, N = 2,117) | 31.7% never search before a vet visit and 37.0% never after; owners who search do so more **before** the consultation; 55.2% use general vet-information websites | Peer-reviewed, EU. Supports "before the visit" triage content |
| 29 Nov 2023 | PetLab analysis, reported by [Four States Homepage](https://digital-release.fourstateshomepage.com/?p=1692793) (US, Google Trends and Keyword Planner, 120+ terms) | Ear infection is the top dog-health search in 33 of 50 states; then pancreatitis (~829/100k), parvovirus (~647/100k), diarrhoea (~636/100k), ticks (~537/100k) | Commercial, US |
| 3 Mar 2021 | Valdez, [Animals 11(3):676](https://pmc.ncbi.nlm.nih.gov/articles/PMC8001315/) (Google Trends 2004–2020) | The bearded dragon is "by far" the most-searched pet reptile and leads in Germany and Austria; the **leopard gecko leads in Italy** | Peer-reviewed. Matches our IT data, where geco leopardino outweighs pogona |
| 1 Nov 2019 | Webbox Naturals via [Pet Business World](https://www.petbusinessworld.co.uk/trade-news/other-trades/worried-pet-owners-turn-to-dr-google.html) (UK) | Top "how to" questions are behavioural: puppy biting 6,600/month, barking 3,600, puppy training 3,600; cats "how to pet a cat" 480 | Old and commercial; behaviour, not health |

No Google Year in Search edition from 2022–2025 has a pet-health list relevant here, so it is not used. No reputable IT- or DE-language "most googled pet questions" study was found.

## Ranked topics per species and language

Each cell shows the topic, then *score/distinct queries*, then coverage. Topics marked **gap** have no article in that language. "Partial" means the topic sits inside a broader article. Unmarked topics are covered. The top "can it eat" foods for each language are listed after the tables.

### Dogs

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 86/260 (partial) | "Can it eat X?" food safety 75/244 (partial) | "Can it eat X?" food safety 162/491 (partial) |
| 2 | Ate something (long tail) 31/123 **gap** | Ate something (long tail) 37/119 **gap** | Diarrhoea 20/32 |
| 3 | Behaviour (licking, biting, noises) 27/81 (partial) | Behaviour (licking, biting, noises) 30/98 (partial) | Ate something (long tail) 17/60 **gap** |
| 4 | Diarrhoea 21/24 | Itching / licking paws 13/28 | Eats grass / poop 16/27 |
| 5 | Itching / licking paws 20/38 | Not eating 12/26 | Behaviour (licking, biting, noises) 13/40 (partial) |
| 6 | Vomiting yellow/white foam 16/25 | Vomiting yellow/white foam 11/26 | Not eating 10/15 |
| 7 | Vomiting 14/28 | Limping / leg problems 10/26 | Poop questions 10/21 (partial) |
| 8 | Not eating 11/23 | Breathing fast / panting 8/26 | Vomiting yellow/white foam 9/15 |
| 9 | Swallowed object 11/32 **gap** | Vomiting 8/25 | Itching / licking paws 5/18 |
| 10 | Limping / leg problems 10/18 | Ate grapes/raisins 7/7 | Fleas / mites / lice 5/8 (partial) |
| 11 | Blood in stool 9/11 | Sleep / snoring 7/21 **gap** | Vomiting 5/13 |
| 12 | Ate grapes/raisins 9/20 | Swallowed object 6/18 **gap** | Ears (warm, itchy, mites) 4/13 |

### Cats

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 86/262 (partial) | "Can it eat X?" food safety 63/193 (partial) | "Can it eat X?" food safety 84/247 (partial) |
| 2 | Behaviour (licking, biting, noises) 51/148 **gap** | Behaviour (licking, biting, noises) 30/81 **gap** | Behaviour (licking, biting, noises) 16/46 **gap** |
| 3 | Ate something (long tail) 46/159 **gap** | Vomiting 16/44 | Vomiting 14/31 |
| 4 | Sneezing / runny nose 20/26 | Not eating 9/23 | Not eating 14/14 |
| 5 | Vomiting 17/33 | Eye problems 8/25 **gap** | Diarrhoea 13/20 |
| 6 | Swallowed object 15/37 **gap** | Hair/feather loss, dandruff, moult 7/19 | Vomiting yellow/white foam 11/13 (partial) |
| 7 | Peeing outside the litter box / indoors 10/17 **gap** | Diarrhoea 6/16 | Sneezing / runny nose 9/22 |
| 8 | Vomiting yellow/white foam 10/12 (partial) | Ate something (long tail) 6/9 **gap** | Ate something (long tail) 8/29 **gap** |
| 9 | Not eating 8/14 | Sleep / snoring 5/20 **gap** | Ears (warm, itchy, mites) 7/15 **gap** |
| 10 | Sleep / snoring 6/17 **gap** | Breathing fast / panting 5/18 **gap** | Hair/feather loss, dandruff, moult 5/10 |
| 11 | Ate human medicine 5/19 (partial) | Sneezing / runny nose 5/14 | Eye problems 5/15 **gap** |
| 12 | Teeth / mouth / drooling / beak 5/11 **gap** | Limping / leg problems 5/17 **gap** | Worms 4/9 (partial) |

### Rabbits

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 87/260 (partial) | "Can it eat X?" food safety 61/178 (partial) | "Can it eat X?" food safety 77/236 (partial) |
| 2 | Behaviour (licking, biting, noises) 18/41 **gap** | Not eating 5/10 | Not eating 12/13 |
| 3 | Not eating 13/17 | Lifespan / age 3/6 **gap** | Housing / enclosure / cage 5/16 **gap** |
| 4 | Poop questions 6/11 (partial) | Keeping one as a pet (care guide) 3/10 **gap** | Sneezing / runny nose 5/8 **gap** |
| 5 | Sneezing / runny nose 5/6 **gap** | Smell / odour 2/4 **gap** | Diarrhoea 5/5 |
| 6 | Dying / died suddenly 5/13 **gap** | Housing / enclosure / cage 2/8 **gap** | Ears (warm, itchy, mites) 4/7 **gap** |
| 7 | Housing / enclosure / cage 4/8 **gap** | Behaviour (licking, biting, noises) 2/6 **gap** | Behaviour (licking, biting, noises) 3/7 **gap** |
| 8 | Diarrhoea 4/3 | Ears (warm, itchy, mites) 1/5 **gap** | Keeping one as a pet (care guide) 2/5 **gap** |
| 9 | Eye problems 3/6 **gap** | Eye problems 1/5 **gap** | Toxic plants 2/7 |
| 10 | Nails / hooves / grooming 3/12 **gap** | Dying / died suddenly 1/4 **gap** | Lifespan / age 2/2 **gap** |

### Guinea pigs

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 86/259 (partial) | "Can it eat X?" food safety 11/20 (partial) | "Can it eat X?" food safety 74/218 (partial) |
| 2 | Behaviour (licking, biting, noises) 20/46 **gap** | Not eating 3/7 **gap** | Not eating 11/11 **gap** |
| 3 | Not eating 11/17 **gap** | Lifespan / age 2/3 **gap** | Housing / enclosure / cage 9/21 **gap** |
| 4 | Dying / died suddenly 8/16 **gap** | Behaviour (licking, biting, noises) 2/8 **gap** | Diarrhoea 5/5 **gap** |
| 5 | Housing / enclosure / cage 8/19 **gap** | Housing / enclosure / cage 2/8 **gap** | Sneezing / runny nose 4/5 **gap** |
| 6 | Sneezing / runny nose 6/8 **gap** | Smell / odour 1/2 **gap** | Keeping one as a pet (care guide) 2/5 **gap** |
| 7 | Eye problems 5/12 **gap** | Vaccination / costs 1/3 **gap** | Behaviour (licking, biting, noises) 2/8 **gap** |
| 8 | Diarrhoea 4/4 **gap** | Eye problems 1/4 **gap** | Drinking/peeing a lot 2/2 **gap** |
| 9 | Lifespan / age 4/7 **gap** | Weight (thin/fat) 1/3 **gap** | Hair/feather loss, dandruff, moult 2/4 **gap** |
| 10 | Lumps / swelling 4/6 **gap** | Eggs / pregnancy / heat 1/6 **gap** | Dying / died suddenly 2/2 **gap** |

### Horses

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 82/247 **gap** | "Can it eat X?" food safety 6/10 **gap** | Limping / leg problems 13/29 **gap** |
| 2 | Limping / leg problems 9/13 **gap** | Colic 4/9 **gap** | "Can it eat X?" food safety 13/17 **gap** |
| 3 | Colic 7/13 **gap** | Limping / leg problems 4/9 **gap** | Colic 10/15 **gap** |
| 4 | Coughing / gagging 5/11 **gap** | Behaviour (licking, biting, noises) 2/3 **gap** | Diarrhoea 10/14 **gap** |
| 5 | Not eating 5/7 **gap** | Nails / hooves / grooming 1/3 **gap** | Ate something (long tail) 6/23 **gap** |
| 6 | Diarrhoea 4/5 **gap** | Lifespan / age 1/3 **gap** | Sneezing / runny nose 5/12 **gap** |
| 7 | Behaviour (licking, biting, noises) 3/8 **gap** | Lumps / swelling 1/2 **gap** | Behaviour (licking, biting, noises) 5/16 **gap** |
| 8 | Eats grass / poop 2/5 **gap** | Teeth / mouth / drooling / beak 0/2 **gap** | Lumps / swelling 4/11 **gap** |
| 9 | Sneezing / runny nose 2/4 **gap** | Dying / died suddenly 0/2 **gap** | Fever / warm ears / dry nose 3/11 **gap** |
| 10 | Nails / hooves / grooming 2/7 **gap** | Not drinking 0/1 **gap** | Eye problems 3/11 **gap** |

### Pet birds

| # | EN | IT | DE |
|---|---|---|---|
| 1 | budgie: "Can it eat X?" food safety 80/243 **gap** | cockatiel: Behaviour (licking, biting, noises) 6/15 **gap** | budgie: "Can it eat X?" food safety 13/19 **gap** |
| 2 | parrot: "Can it eat X?" food safety 17/29 **gap** | parrot: Behaviour (licking, biting, noises) 4/10 **gap** | budgie: Diarrhoea 6/6 **gap** |
| 3 | parrot: Behaviour (licking, biting, noises) 8/26 **gap** | budgie: Behaviour (licking, biting, noises) 4/6 **gap** | budgie: Housing / enclosure / cage 5/10 **gap** |
| 4 | budgie: Behaviour (licking, biting, noises) 6/12 **gap** | cockatiel: Eggs / pregnancy / heat 2/9 **gap** | budgie: Behaviour (licking, biting, noises) 3/6 **gap** |
| 5 | budgie: Dying / died suddenly 4/3 **gap** | canary: Limping / leg problems 2/6 **gap** | canary: Keeping one as a pet (care guide) 3/6 **gap** |
| 6 | budgie: Lethargic / fluffed up / sleeping a lot 4/5 **gap** | canary: Behaviour (licking, biting, noises) 2/7 **gap** | budgie: Hair/feather loss, dandruff, moult 3/5 **gap** |
| 7 | parrot: Vomiting 3/5 **gap** | budgie: Lifespan / age 2/3 **gap** | cockatiel: Housing / enclosure / cage 3/8 **gap** |
| 8 | parrot: Eggs / pregnancy / heat 3/9 **gap** | cockatiel: Lifespan / age 1/2 **gap** | canary: "Can it eat X?" food safety 3/7 **gap** |
| 9 | parrot: Dying / died suddenly 3/8 **gap** | cockatiel: Housing / enclosure / cage 1/4 **gap** | cockatiel: "Can it eat X?" food safety 3/9 **gap** |
| 10 | parrot: Teeth / mouth / drooling / beak 3/10 **gap** | cockatiel: "Can it eat X?" food safety 1/6 **gap** | cockatiel: Keeping one as a pet (care guide) 2/3 **gap** |

### Ferrets

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 16/24 **gap** | Shaking / trembling 1/1 **gap** | Keeping one as a pet (care guide) 3/5 **gap** |
| 2 | Behaviour (licking, biting, noises) 13/23 **gap** | "Can it eat X?" food safety 1/3 **gap** | Housing / enclosure / cage 3/10 **gap** |
| 3 | Vomiting 8/8 **gap** | Smell / odour 1/3 **gap** | Diarrhoea 2/2 **gap** |
| 4 | Diarrhoea 5/5 **gap** | Keeping one as a pet (care guide) 1/2 **gap** | Shaking / trembling 2/1 **gap** |
| 5 | Sneezing / runny nose 5/5 **gap** | Vaccination / costs 0/1 **gap** | "Can it eat X?" food safety 2/6 **gap** |
| 6 | Housing / enclosure / cage 5/15 **gap** | Housing / enclosure / cage 0/2 **gap** | Smell / odour 1/2 **gap** |
| 7 | Fleas / mites / lice 4/3 **gap** | Legal status 0/1 **gap** | Lifespan / age 1/2 **gap** |
| 8 | Lethargic / fluffed up / sleeping a lot 4/6 **gap** | Lifespan / age 0/1 **gap** | Itching / licking paws 0/2 **gap** |

### Reptiles

| # | EN | IT | DE |
|---|---|---|---|
| 1 | bearded dragon: "Can it eat X?" food safety 81/242 **gap** | tortoise: "Can it eat X?" food safety 10/27 **gap** | tortoise: "Can it eat X?" food safety 14/16 **gap** |
| 2 | tortoise: "Can it eat X?" food safety 15/25 **gap** | tortoise: Hibernation / brumation 8/20 **gap** | tortoise: Hibernation / brumation 12/18 **gap** |
| 3 | leopard gecko: "Can it eat X?" food safety 14/17 **gap** | tortoise: Lifespan / age 3/6 **gap** | leopard gecko: Housing / enclosure / cage 7/20 **gap** |
| 4 | leopard gecko: Housing / enclosure / cage 12/32 **gap** | tortoise: Housing / enclosure / cage 3/9 **gap** | tortoise: Keeping one as a pet (care guide) 7/15 **gap** |
| 5 | bearded dragon: Housing / enclosure / cage 11/30 **gap** | tortoise: Eggs / pregnancy / heat 2/9 **gap** | tortoise: Housing / enclosure / cage 6/17 **gap** |
| 6 | tortoise: Hibernation / brumation 10/18 **gap** | bearded dragon: Housing / enclosure / cage 2/8 **gap** | leopard gecko: Keeping one as a pet (care guide) 4/8 **gap** |
| 7 | tortoise: Not eating 8/18 **gap** | bearded dragon: "Can it eat X?" food safety 2/5 **gap** | snake: Housing / enclosure / cage 3/4 **gap** |
| 8 | tortoise: Lethargic / fluffed up / sleeping a lot 6/10 **gap** | tortoise: Keeping one as a pet (care guide) 2/4 **gap** | snake: Is it venomous? 3/3 **gap** |
| 9 | tortoise: Housing / enclosure / cage 5/18 **gap** | tortoise: Not eating 2/7 **gap** | tortoise: Shell problems 3/9 **gap** |
| 10 | leopard gecko: Not eating 5/5 **gap** | leopard gecko: "Can it eat X?" food safety 2/4 **gap** | tortoise: Cold / winter outdoors 2/8 **gap** |
| 11 | tortoise: Shell problems 5/10 **gap** | tortoise: Smell / odour 2/3 **gap** | snake: Keeping one as a pet (care guide) 2/2 **gap** |
| 12 | tortoise: Behaviour (licking, biting, noises) 4/12 **gap** | leopard gecko: Eggs / pregnancy / heat 1/6 **gap** | leopard gecko: "Can it eat X?" food safety 2/6 **gap** |

### Hamsters (optional)

| # | EN | IT | DE |
|---|---|---|---|
| 1 | "Can it eat X?" food safety 12/15 **gap** | "Can it eat X?" food safety 5/11 **gap** | "Can it eat X?" food safety 12/18 **gap** |
| 2 | Behaviour (licking, biting, noises) 7/10 **gap** | Eye problems 2/6 **gap** | Housing / enclosure / cage 6/14 **gap** |
| 3 | Housing / enclosure / cage 6/9 **gap** | Housing / enclosure / cage 2/6 **gap** | Behaviour (licking, biting, noises) 4/10 **gap** |
| 4 | Dying / died suddenly 3/4 **gap** | Behaviour (licking, biting, noises) 2/6 **gap** | Lifespan / age 3/7 **gap** |
| 5 | Lethargic / fluffed up / sleeping a lot 2/3 **gap** | Lifespan / age 1/5 **gap** | Keeping one as a pet (care guide) 3/7 **gap** |
| 6 | Smell / odour 2/6 **gap** | Lethargic / fluffed up / sleeping a lot 1/1 **gap** | Dying / died suddenly 2/2 **gap** |

**What the "can it eat" clusters actually ask about** (highest-scoring foods, in order):

- Dog: EN bananas, watermelon, strawberries, tomatoes, apples, blueberries, cucumber, grapes, pineapple. IT melone, pesca, banana, uva, anguria, cetriolo, castagne, prugna, carne di maiale. DE Wassermelone, Tomaten, Banane, Birne, Nektarinen, Zwetschgen, Pfirsich, Paprika.
- Cat: EN watermelon, cheese, bananas, eggs, chocolate, blueberries, peanut butter. IT uovo, crocchette del cane, prosciutto cotto, melone, formaggio, yogurt, tonno. DE Wassermelone, Käse, Eier, **Milch**, Bananen, Joghurt, Gurken, Hundefutter.
- Rabbit: EN tomatoes, watermelon, celery, cucumber, grapes, apples, cabbage. IT cetriolo, pesca, uva, basilico, melone, semi di girasole, zucchine. DE Paprika, Zucchini, Tomaten, Wassermelone, Gurken, Kohlrabi, Rucola.
- Guinea pig: EN grapes, tomatoes, watermelon, celery, strawberries, apples. DE Zucchini, Tomaten, Wassermelone, Weintrauben, Paprika. IT rucola, anguria, cetriolo (thin).
- Horse: EN cucumbers, watermelon, bananas, grapes. DE Birnen, Gurken, Wassermelone, Äpfel, Bananen. IT melone, pesca, cetrioli.
- Budgie: EN bananas, watermelon, strawberries, grapes, apples. DE Wassermelone, Bananen, Paprika, Tomaten, Petersilie.
- Bearded dragon: EN cucumbers, watermelon, carrots, tomatoes, grapes, spinach. Tortoise: EN tomatoes, carrots, celery; IT carota, cetriolo, rucola; DE Gurken, Tomaten, Äpfel, Paprika.
- Ferret: cat food, dog food, eggs, tuna, fruit. Hamster: strawberries, grapes, carrots, bananas, cheese; DE Paprika, Tomaten, Äpfel.

## Gaps for dogs, cats and rabbits

### Per language: the top uncovered topics

| Species | EN | IT | DE |
|---|---|---|---|
| Dog | Safe fruit and veg A–Z; swallowed an object (tampon, sock, corn cob, plastic); eats grass or poop; panting or breathing fast; xylitol; human medicines (ibuprofen, melatonin) | Fruit and veg A–Z; "cane ha ingerito plastica / calzino / corpo estraneo" (probe 10/10); red eyes ("cane ha occhi rossi"); eats grass or poop ("cane mangia erba e vomita", 10/10); toad, slug or mushroom ("ha mangiato rospo / lumaca / funghi"); twitching in sleep ("spasmi mentre dorme") | Obst und Gemüse A–Z; Plastik, Unterhose or Maiskolben gefressen; Flöhe – was tun? (10/10); Xylit gefressen (10/10, "wann Symptome"); Blähungen (10/10); warme/heiße Ohren |
| Cat | Food A–Z; ate string, a hair tie or plastic; peeing outside the litter box (10/10); eye infection (10/10); drooling; behaviour changes (sudden biting, staring) | Food A–Z (uovo, crocchette del cane, prosciutto); "gatto ha un occhio chiuso / che lacrima" (8/25); pipì fuori dalla lettiera (10/10); respira con la bocca aperta; tosse / "qualcosa in gola"; zoppica | Darf die Katze Milch, Käse, Eier …? A–Z; Katze hat warme Ohren / Fieber (7/15); rotes oder tränendes Auge (10/10); Flöhe – was tun?; sabbert; Entwurmen (partial only) |
| Rabbit | Food A–Z; sneezing / snuffles; vaccinations against myxomatosis and RHD (10/10); "died suddenly" (an RHD pointer); head tilt (10/10); flystrike (10/10); bloat (10/10) | Cosa può mangiare il coniglio A–Z; vaccino (10/10); testa storta (5/10); pancia gonfia (6/10); miasi (5/10); "coniglio nano quanto vive" (care) | Was dürfen Kaninchen essen A–Z; Schnupfen (5/8); Impfung RHD/Myxomatose (10/10); kalte/warme Ohren; Fliegenmaden (10/10); Trommelsucht (6/10); Außengehege im Winter |

### Top 10 gaps overall (dogs, cats, rabbits)

Ranked by cluster score, how many languages show the topic and probe depth. The suggested titles reuse the most frequent completions.

| # | Gap | Evidence | EN title | IT title | DE title |
|---|---|---|---|---|---|
| 1 | Dog fruit and veg A–Z (safe, careful, never) | Top cluster in all 3 (86/260, 75/244, 162/491); Prestige volumes agree | Can dogs eat bananas, watermelon or tomatoes? Fruit and vegetables from A to Z | Il cane può mangiare melone, pesca o banana? Frutta e verdura dalla A alla Z | Darf mein Hund Wassermelone, Tomaten oder Banane essen? Obst und Gemüse von A bis Z |
| 2 | Cat food A–Z | Top cluster in all 3 (86/262, 63/193, 84/247) | Can cats eat cheese, eggs or watermelon? Human foods from A to Z | Il gatto può mangiare uovo, prosciutto cotto o crocchette del cane? | Dürfen Katzen Milch, Käse oder Eier? Lebensmittel von A bis Z |
| 3 | Rabbit food A–Z (beyond the toxic list) | Top cluster in all 3 (87/260, 61/178, 77/236) | Can rabbits eat tomatoes, celery or cucumber? Safe vegetables and fruit | Il coniglio può mangiare cetriolo, pesca o basilico? Cosa sì e cosa no | Dürfen Kaninchen Paprika, Zucchini oder Tomaten essen? |
| 4 | Dog swallowed an object | EN 11/32; IT 6/18 plus probe 10/10; DE 3/9 (hand count: Plastik, Unterhose, Alufolie, Maiskolben) | My dog swallowed a sock, plastic or a corn cob: what to do now | Il cane ha ingerito plastica, un calzino o un corpo estraneo: cosa fare | Hund hat Plastik, Socke oder Maiskolben gefressen: was jetzt? |
| 5 | Cat ate string, a hair tie or plastic | EN 15/37; IT 4/11; DE 2/7 (hand count: Plastik, Haargummi, Gummiband) | My cat ate string or a hair tie: why it can be an emergency | Il gatto ha ingerito un filo o un elastico: quando è un'emergenza | Katze hat Faden, Haargummi oder Plastik gefressen: was tun? |
| 6 | Cat peeing outside the litter box (DE already covered) | EN 10/17 plus probe 10/10; IT probe 10/10 | Cat peeing outside the litter box: medical causes first | Il gatto fa la pipì fuori dalla lettiera: cause e cosa fare | (covered by katze-pinkelt-ins-bett) |
| 7 | Rabbit vaccinations (myxomatosis, RHD1/RHD2) | Probes 10/10 in all 3 ("cost", "wie oft", "fai da te"); "my rabbit died suddenly" 5/13 | Rabbit vaccinations: myxomatosis and RHD, how often and what they cost | Vaccino del coniglio: mixomatosi e malattia emorragica, ogni quanto | Kaninchen impfen: RHD und Myxomatose, wie oft und was es kostet |
| 8 | Cat eye problems (closed, watering, red) | IT 8/25; DE 5/15; probes 10/10 in all 3 | Cat eye infection or a watery eye: when to see the vet | Il gatto ha un occhio chiuso o che lacrima: cause e quando preoccuparsi | Katze hat ein tränendes oder rotes Auge: was steckt dahinter? |
| 9 | Dog panting / breathing fast (IT already covered) | EN 6/17 plus probe 10/10; DE probe 10/10 ("ständig", "nachts") | Dog panting a lot, even at rest: causes and when it's an emergency | (covered by cane-respira-male) | Hund hechelt ständig, auch nachts: wann es ernst ist |
| 10 | Fleas: what to do now (beyond prevention) | DE dog 5/8 plus probe 10/10, DE cat 3/6; EN "dog has fleas what to do" | My dog or cat has fleas: what to do today and how to clear the home | Il cane o il gatto ha le pulci: cosa fare subito e in casa | Hund oder Katze hat Flöhe: was tun? Behandlung und Wohnung |

Next in line: xylitol as its own article (EN and DE, 10/10 "Symptome"), dog eats grass or poop in EN and IT (DE is covered), rabbit sneezing / snuffles (EN, DE), rabbit head tilt and flystrike, cat fever / warm ears (DE, IT), and dog constipation (probes 9–10/10 in all 3).

## New species: the best first articles

The new species have no articles beyond the shared toxic-plants page (rabbits and guinea pigs) and the travel page (ferrets). Each list is ranked by evidence across the three languages. Probe depth is given as n/10.

### Guinea pigs (EN strong, DE strong, IT weak)

| # | Article | Evidence | EN | IT | DE |
|---|---|---|---|---|---|
| 1 | Food A–Z and vitamin C | Top cluster EN 86/259, DE 74/218, IT 11/20; vitamin C probe EN/DE 10/10, IT 2 | Can guinea pigs eat grapes, tomatoes or cucumber? Food A–Z and vitamin C | Cosa può mangiare la cavia? Frutta, verdura e vitamina C | Was dürfen Meerschweinchen essen? Obst, Gemüse und Vitamin C |
| 2 | Not eating (an emergency) | EN 11/17, DE 11/11 (incl. "nach Zahnkorrektur"), IT 3/7 | My guinea pig is not eating: why it's urgent | La cavia non mangia: perché è urgente | Meerschweinchen frisst nicht mehr: wann es ein Notfall ist |
| 3 | Sneezing, wheezing, runny nose | EN 6/8, probe "wheezing" 10/10; DE Schnupfen 4/5 | Guinea pig sneezing or wheezing: cold or pneumonia? | La cavia starnutisce o respira con fatica: cosa fare | Meerschweinchen hat Schnupfen oder röchelt: was tun? |
| 4 | Mites, itching, hair loss | Probes EN 10/10, DE 10/10, IT 1; DE "verliert Haare" 2/4 | Guinea pig mites and hair loss: signs and treatment | Acari nella cavia: pelo che cade e prurito | Meerschweinchen hat Milben oder verliert Haare |
| 5 | Bladder stones / blood in urine | EN 2.5/4, probe 10/10 ("surgery cost"); DE probe 10/10 ("OP Kosten", "einschläfern"); IT 1 | Guinea pig blood in urine or bladder stones: signs and treatment | Cavia con sangue nelle urine o calcoli: cosa fare | Meerschweinchen Blasenstein: Anzeichen, OP und Kosten |
| 6 | Diarrhoea and eye problems | Diarrhoea DE 5/5, EN 4/4; cloudy/watery eye EN 5/12 | Guinea pig diarrhoea / cloudy eye | Cavia con diarrea / occhio opaco | Meerschweinchen hat Durchfall / trübes Auge |

### Horses (EN and DE strong, IT moderate)

| # | Article | Evidence | EN | IT | DE |
|---|---|---|---|---|---|
| 1 | Colic: signs and what to do while waiting for the vet | EN 7/13, IT 4.5/9 (top health cluster), DE 10/15 ("Anzeichen", "was tun", "äppelt aber") | Horse colic: signs and what to do until the vet arrives | Colica nel cavallo: sintomi e cosa fare in attesa del veterinario | Kolik beim Pferd: Anzeichen und was tun, bis die Tierärztin kommt |
| 2 | Lameness (including hoof abscess) | DE top cluster 13/29 ("lahmt vorne ohne äußere Anzeichen", "plötzlich"), EN 9/13, IT 4/9 ("zoppo anteriore") | Horse suddenly lame: hoof abscess or something serious? | Cavallo zoppo all'improvviso: ascesso o qualcosa di grave? | Pferd lahmt plötzlich vorne: Hufgeschwür oder mehr? |
| 3 | Laminitis | Probes EN 10/10, IT "laminite cavallo" 9/10, DE "Hufrehe" 10/10; seasonal (spring grass) | Laminitis in horses: early signs and first steps | Laminite nel cavallo: primi segni e cosa fare | Hufrehe beim Pferd: erste Anzeichen und Sofortmaßnahmen |
| 4 | Diarrhoea and free faecal water | DE 10/14, probe "Kotwasser" 10/10; EN 4/5 | Horse diarrhoea or faecal water: causes and when to call | Diarrea nel cavallo: cause e quando chiamare | Pferd hat Durchfall oder Kotwasser: Ursachen und was hilft |
| 5 | Food safety and poisonous plants | EN 82/247; DE 13/17 plus "Jakobskreuzkraut gefressen"; IT 6/10 | Can horses eat apples, bananas or cucumber? And plants that poison horses | Il cavallo può mangiare melone o pesca? E le piante tossiche | Dürfen Pferde Birnen, Äpfel oder Gurken? Und welche Pflanzen giftig sind |
| 6 | Cough, nasal discharge, strangles | EN cough 5/11; DE Nasenausfluss/-bluten 5/12; probes strangles 10/10, Druse 10/10, adenite 6/10 | Horse coughing or a runny nose: allergy, infection or strangles? | Cavallo con tosse o scolo nasale: adenite e altre cause | Pferd hustet oder hat Nasenausfluss: Druse oder Allergie? |

Strong second wave: Cushing's (PPID; probes 10/10 in all 3), sweet itch (Sommerekzem / dermatite estiva, 9–10/10) and mud fever (Mauke, 10/10).

### Pet birds: budgies, canaries, parrots, cockatiels (EN strong, DE moderate, IT mostly care and sexing)

| # | Article | Evidence | EN | IT | DE |
|---|---|---|---|---|---|
| 1 | Budgie / parrot food A–Z | EN budgie 80/243, parrot 17/29; DE budgie 13/19; IT "calopsite cosa mangia" (thin) | Can budgies eat bananas, watermelon or strawberries? Safe and unsafe foods | Cosa può mangiare il pappagallino (e la calopsite)? | Was dürfen Wellensittiche essen? Obst und Gemüse von A bis Z |
| 2 | Fluffed up and sleepy: a sick bird | EN "fluffed up" probe 10/10 (and "tail bobbing", "breathing heavy"); DE "aufgeplustert" 10/10 | Budgie fluffed up and sleeping a lot: signs of illness | Pappagallino gonfio e assonnato: quando è malato | Wellensittich aufgeplustert und schläft viel: ist er krank? |
| 3 | Feather loss: moult or plucking? | EN plucking probe 10/10, parrot 2/9; DE Mauser 3/5 plus canary and cockatiel; IT "perde / si strappa le piume" | Feather loss in budgies and parrots: moult or plucking? | Il pappagallo perde le piume: muta o autodeplumazione? | Wellensittich verliert Federn: Mauser oder Rupfen? |
| 4 | Egg laying and egg binding | EN parrot 3/9 ("laid an egg without a mate"); DE "Legenot" 9/10; IT calopsite uova 2.5/9 | My bird laid an egg: what to do, and the signs of egg binding | La calopsite ha fatto l'uovo: cosa fare e quando è urgente | Wellensittich hat Eier gelegt: was tun, und Anzeichen von Legenot |
| 5 | Diarrhoea and abnormal droppings | DE budgie 6/6; EN parrot "watery poop" 2/7 | Budgie or parrot with watery droppings: when to worry | Feci liquide nel pappagallino: quando preoccuparsi | Wellensittich hat Durchfall: was tun? |
| 6 | Mites and beak or claw overgrowth | Mites probes EN 10/10, DE 10/10, IT 0; DE "Schnabel zu lang"; IT "canarino unghie lunghe" | Budgie mites and an overgrown beak | Canarino con unghie lunghe e becco storto | Wellensittich: Milben und zu langer Schnabel |

### Ferrets (EN only; IT and DE demand is very thin)

| # | Article | Evidence | EN | IT | DE |
|---|---|---|---|---|---|
| 1 | What ferrets can eat | EN 16/24 (cat food, dog food, eggs, tuna, fruit); DE Ernährung 2/6; IT 1/3 | Can ferrets eat cat food, eggs or fruit? A ferret diet guide | Cosa mangia il furetto? | Frettchen Ernährung: was dürfen sie fressen? |
| 2 | Vomiting and diarrhoea | EN vomiting 8/8, diarrhoea 5/5 ("green diarrhea"); DE 2/2 | Ferret vomiting or green diarrhoea: causes and when to go | Furetto con vomito o diarrea | Frettchen hat Durchfall oder erbricht |
| 3 | Lethargy and weakness (insulinoma) | EN lethargy 4/6, insulinoma probe 10/10; IT 2; DE 2 | Ferret lethargic or weak: insulinoma and other causes | Furetto debole e apatico: insulinoma | Frettchen schlapp: Insulinom erkennen |
| 4 | Hair loss (adrenal disease) | Probe EN 10/10; DE 2; IT 0 | Ferret losing hair: adrenal disease explained | Furetto che perde pelo: malattia surrenale | Frettchen verliert Fell: Nebennierenerkrankung |
| 5 | Vaccination (distemper, rabies for travel) | Probes EN 10/10, DE 5/10 ("Staupe", "Tollwut", "Kosten"), IT 2/10; links to travelling-eu-pets | Ferret vaccinations: distemper and rabies | Vaccini del furetto | Frettchen impfen: Staupe und Tollwut, Kosten |

### Reptiles (EN strong; DE moderate and very tortoise-heavy; IT tortoise and leopard gecko)

| # | Article | Evidence | EN | IT | DE |
|---|---|---|---|---|---|
| 1 | Tortoise hibernation (seasonal: now) | Top non-food cluster in all 3: EN 10/18, IT 8/20 ("in appartamento", "o morta"), DE 12/18 ("ab wann", "Kühlschrank"); probes 10/10 | Tortoise hibernation: when to start, the fridge method and health checks first | Letargo della tartaruga di terra: quando, come e i controlli prima | Winterstarre bei Landschildkröten: ab wann, Kühlschrank und Gesundheitscheck |
| 2 | Tortoise not eating, eyes closed or swollen (including after hibernation) | EN not eating 8/18 plus lethargy 6/10; IT "occhi chiusi e non mangia" 10/10; DE "Augen verklebt / geschwollen" 10/10 | Tortoise not eating or keeping its eyes closed: when to see a vet | La tartaruga non mangia e tiene gli occhi chiusi: cosa fare | Schildkröte frisst nicht oder hat geschwollene Augen |
| 3 | Bearded dragon diet | EN 81/242; IT "pogona cosa mangia" 2/5 | Can bearded dragons eat cucumber, carrots or fruit? Diet guide | Cosa mangia la pogona? | Bartagame Ernährung: was dürfen sie fressen? |
| 4 | Tortoise diet | EN 15/25, IT 10/27 ("tartaruga di terra cosa mangia"), DE 14/16 | What can tortoises eat? Tomatoes, cucumber and the weeds they need | Cosa mangia la tartaruga di terra? Cosa sì e cosa no | Was dürfen Landschildkröten fressen? |
| 5 | UVB, calcium and metabolic bone disease (bearded dragon, leopard gecko) | Enclosure clusters EN 11–12/30; MBD probes EN 10/10 (beardie and gecko); DE "Calcium / Rachitis" | Metabolic bone disease in reptiles: UVB and calcium mistakes to avoid | Malattia metabolica delle ossa: UVB e calcio per pogona e geco | Rachitis bei Reptilien: UV-Licht und Kalzium richtig |
| 6 | Leopard gecko not eating or stuck shed | EN 5/5 plus stuck-shed probe 10/10; IT "non mangia" and "muta" 7/10 each; DE "frisst nicht", "Häutungsprobleme" | Leopard gecko not eating or with stuck shed | Geco leopardino non mangia o ha problemi di muta | Leopardgecko frisst nicht oder hat Häutungsprobleme |

Also strong: ball python not eating (EN 10/10, DE 6/10, IT 3/10) and tortoise shell problems (soft shell, pyramiding: EN 5/10, DE 3/9). In Italy the leopard gecko outweighs the bearded dragon, which matches Valdez 2021.

### Hamsters (optional)

Demand is mostly care: food (EN 12/15, DE 12/18, IT 5/11), cage, biting and lifespan. The health topics with depth are **wet tail** (EN 10/10; DE 0) and **"hibernating or dead?"** (EN 10/10; IT "criceto letargo o morto" 9/10). If hamsters are added, start with: (1) What can hamsters eat? (2) Hamster not moving: torpor or dead? (3) Wet tail.
