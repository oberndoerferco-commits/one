/**
 * Share images (Open Graph, 1200×630) for article and animal pages, built into dist/og/<lang>/<slug>.png
 * by src/pages/og/[lang]/[slug].png.ts and rendered by scripts/og-render.mjs. Base.astro points og:image
 * at the page's own card when there is one (ogImageFor), otherwise at the site default.
 *
 * Article cards: title, verdict (urgency label in the article's language, as on the page), species face,
 * review status. Animal cards (lexicon entries, breeds, species hubs): name, scientific name, face.
 */
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { ANIMALS, type Lang } from './animals-i18n';
import { ICONS } from './animal-icons';
import { LEX } from './lexicon';
import { articlesIn, animalPage, animalPaths, iconOf, tintOf, keyOf } from './animal-data';

export type OgCard =
  | { kind: 'article'; lang: Lang; title: string; urgency: string; verdict: string; icon: string; tint: string; status: string }
  | { kind: 'animal'; lang: Lang; name: string; scientific?: string; eyebrow?: string; icon: string; tint: string; status: string };

const LANGS: Lang[] = ['en', 'it', 'de'];
// Same labels as the verdict card on the page (S.verdict in src/components/Article.astro).
const VERDICT: Record<Lang, Record<string, string>> = {
  en: { emergency: 'Go now', today: 'See a vet today', 'this-week': 'Book a visit this week', routine: 'Watch and ask at the next visit' },
  it: { emergency: 'Vai subito', today: 'Dal veterinario oggi', 'this-week': 'Prenota una visita questa settimana', routine: 'Osserva e chiedi alla prossima visita' },
  de: { emergency: 'Sofort in die Praxis', today: 'Heute in die Praxis', 'this-week': 'Diese Woche einen Termin', routine: 'Beobachten, beim nächsten Besuch fragen' },
};
const DRAFT: Record<Lang, string> = { en: 'Draft', it: 'Bozza', de: 'Entwurf' };
const status = (lang: Lang, draft: boolean, reviewedBy?: string) =>
  draft || !reviewedBy ? `${DRAFT[lang]} · ${LEX[lang].draftNot}` : `${ANIMALS[lang].reviewedBy} ${reviewedBy}`;

/** The card for /<lang>/animals/<slug>, with its alt text (the title), or null when the page has none. */
export async function cardFor(lang: Lang, slug: string): Promise<{ card: OgCard; alt: string } | null> {
  const article = (await articlesIn(lang)).find((e) => keyOf(e) === slug);
  if (article) {
    const d = article.data;
    const kind = d.species === 'general' ? 'dog' : d.species;
    const urgency = d.urgency ?? 'this-week';
    return {
      alt: d.title,
      card: { kind: 'article', lang, title: d.title, urgency, verdict: VERDICT[lang][urgency], icon: ICONS[kind] ?? ICONS.paw, tint: d.species, status: status(lang, d.draft, d.reviewedBy) },
    };
  }
  if (!(await animalPaths(lang)).some((p) => p.params.filter === slug)) return null;
  const page = await animalPage(lang, slug);
  if (page.kind !== 'animal') return null;
  const d = page.entry?.data;
  const name = d?.name ?? page.title;
  // The rest of the page title as a kicker ("fact sheet and health", "health problems, lifespan, fact sheet").
  const eyebrow = page.title.startsWith(`${name}: `) ? page.title.slice(name.length + 2) : undefined;
  return {
    alt: page.title,
    card: {
      kind: 'animal', lang, name, eyebrow,
      ...(d?.scientific ? { scientific: d.scientific } : {}),
      icon: ICONS[d ? iconOf(slug, d.group, d.species) : slug] ?? ICONS.paw,
      tint: d ? tintOf(slug, d.group, d.species) : slug,
      status: d ? status(lang, d.draft) : ANIMALS[lang].title,
    },
  };
}

/** og:image URL path and alt text for a page path, or null to use the site default. */
export async function ogImageFor(path: string) {
  const m = /^(?:\/(it|de))?\/animals\/([^/]+)$/.exec(path);
  if (!m) return null;
  const lang = (m[1] ?? 'en') as Lang;
  const c = await cardFor(lang, m[2]);
  return c ? { url: `/og/${lang}/${m[2]}.png`, alt: c.alt } : null;
}

let all: Promise<Map<string, OgCard>> | undefined;
/** Every card, keyed "<lang>/<slug>". */
export function allCards() {
  return (all ??= (async () => {
    const out = new Map<string, OgCard>();
    for (const lang of LANGS) {
      const slugs = [...(await articlesIn(lang)).map(keyOf), ...(await animalPaths(lang)).map((p) => p.params.filter)];
      for (const slug of slugs) {
        const c = await cardFor(lang, slug);
        if (c) out.set(`${lang}/${slug}`, c.card);
      }
    }
    return out;
  })());
}

// The renderer is plain Node (worker threads, native resvg), loaded from scripts/ at run time rather
// than bundled by Vite, so the build and its workers share one module and one cache key.
const renderer = () => import(/* @vite-ignore */ pathToFileURL(join(process.cwd(), 'scripts/og-render.mjs')).href);

let rendered: Promise<Map<string, string>> | undefined;
/** PNG file (in the render cache) for a card id. A build renders all cards at once; dev only the one asked for. */
export async function cardFile(id: string): Promise<string> {
  const r = await renderer();
  if (!import.meta.env.PROD) {
    const card = (await allCards()).get(id)!;
    return (await r.renderAll(new Map([[id, card]]))).files.get(id);
  }
  rendered ??= (async () => {
    const cards = await allCards();
    const res = await r.renderAll(cards);
    console.log(`og cards: ${cards.size} images, ${res.rendered} rendered in ${(res.ms / 1000).toFixed(1)} s, ${res.cached} from cache`);
    return res.files;
  })();
  return (await rendered).get(id)!;
}
