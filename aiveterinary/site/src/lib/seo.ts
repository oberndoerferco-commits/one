/**
 * Search metadata for every page, derived from the content collections and the route files, so new
 * articles, lexicon entries and routes get hreflang, noindex and structured data without editing a list.
 * Used by src/layouts/Base.astro (all pages) and src/components/Article.astro (articles). After the build,
 * astro.config.mjs (sitemapFromPages) checks the result against the pages that were actually built.
 */
import { getCollection } from 'astro:content';
import { ANIMALS } from './animals-i18n';
import { TRANSLATION_GROUPS } from './translations';
import { SHARED_TOPICS } from '../data/species';

export type Lang = 'en' | 'it' | 'de';
export const LANGS: Lang[] = ['en', 'it', 'de'];
export const SITE = 'https://aiveterinary.org';
export const ORG_ID = `${SITE}/#org`;
export const WEBSITE_ID = `${SITE}/#website`;
export const prefix = (l: string) => (l === 'en' ? '' : `/${l}`);
const keyOf = (id: string) => String(id).split('/').pop()!;

// Both collections, read once per build (in dev on every call, so edits show up). Astro logs a warning on
// each read of an empty collection; reading once keeps the build log readable while the lexicon is empty.
let cached: ReturnType<typeof read> | undefined;
const read = () => Promise.all([getCollection('animals'), getCollection('lexicon')]);
export const collections = () => (import.meta.env.PROD ? (cached ??= read()) : read());

/** The publisher, as shown on the About page. Used inline (publisher) and on the home and About pages. */
export const ORG = {
  '@type': 'Organization', '@id': ORG_ID, name: 'AI Veterinary', url: `${SITE}/`,
  logo: { '@type': 'ImageObject', url: `${SITE}/logo.png`, width: 512, height: 512 },
};

/** Wikidata items for animals (looked up on wikidata.org), to say unambiguously which animal a page is about. */
export const WIKIDATA: Record<string, string> = {
  dog: 'Q144', cat: 'Q146', rabbit: 'Q149017', 'guinea-pig': 'Q79803', ferret: 'Q178973', horse: 'Q726', bird: 'Q5113', reptile: 'Q10811',
};
export const wikidata = (key: string) => (WIKIDATA[key] ? `https://www.wikidata.org/wiki/${WIKIDATA[key]}` : undefined);

// Route files as language + pattern: src/pages/it/can-eat/[species].astro → it, /can-eat/*.
interface Route { lang: Lang; segs: string[]; pattern: string }
const ROUTES: Route[] = Object.keys(import.meta.glob('../pages/**/*.astro')).map((f) => {
  let p = f.replace(/^\.\.\/pages/, '').replace(/\.astro$/, '').replace(/\/index$/, '');
  const lang = (/^\/(it|de)(?=\/|$)/.exec(p)?.[1] ?? 'en') as Lang;
  p = p.replace(/^\/(it|de)(?=\/|$)/, '');
  const segs = p.split('/').filter(Boolean).map((s) => (s.startsWith('[...') ? '**' : s.startsWith('[') ? '*' : s));
  return { lang, segs, pattern: `/${segs.join('/')}` };
});
const fits = (segs: string[], path: string[]): boolean =>
  segs[0] === '**' ? path.length >= 1 && (segs.length === 1 || path.some((_, i) => fits(segs.slice(1), path.slice(i + 1))))
  : !segs.length ? !path.length
  : !!path.length && (segs[0] === '*' || segs[0] === path[0]) && fits(segs.slice(1), path.slice(1));
const rank = (r: Route) => r.segs.map((s) => (s === '**' ? 0 : s === '*' ? 1 : 2)).join('');
/** Languages that have the same route as the one serving `basePath` in `lang` (same file path or pattern). */
export function routeLangs(basePath: string, lang: Lang): Lang[] {
  const path = basePath.split('/').filter(Boolean);
  const best = ROUTES.filter((r) => r.lang === lang && fits(r.segs, path)).sort((a, b) => rank(b).localeCompare(rank(a)) || b.segs.length - a.segs.length)[0];
  return best ? LANGS.filter((l) => ROUTES.some((r) => r.lang === l && r.pattern === best.pattern)) : [];
}

export interface PageSeo {
  kind: 'article' | 'lexicon' | 'listing' | 'page';
  noindex: boolean;
  /** hreflang set, [lang, path]; empty when the page has no translation (or is noindex). */
  alternates: [Lang, string][];
  /** Page-level structured data nodes (articles add their own in Article.astro). */
  graph: Record<string, unknown>[];
}

/**
 * hreflang, noindex and structured data for a page. `labels` maps paths to the visible link labels
 * of the header and footer menus, which name the parent page in breadcrumbs.
 */
export async function pageSeo(path: string, lang: Lang, page: { title: string; description: string; labels: Map<string, string> }): Promise<PageSeo> {
  const basePath = path.replace(/^\/(it|de)(?=\/|$)/, '').replace(/^\/$/, '');
  const url = new URL(path === '/' ? '/' : path, SITE).href;
  const [articles, lexicon] = await collections();
  const articleIn = (l: Lang, slug: string) => articles.some((e) => e.data.lang === l && keyOf(e.id) === slug);
  const lexiconIn = (l: Lang, key: string) => lexicon.find((e) => e.data.lang === l && keyOf(e.id) === key);
  // A listing has content when an article is filed under it, or a shared topic is listed for it (SHARED_TOPICS).
  const hasListing = (l: Lang, key: string) => articles.some((e) => e.data.lang === l && (e.data.species === key || e.data.category === key || (SHARED_TOPICS as any)[key]?.[l]?.includes(keyOf(e.id))));
  const at = (l: Lang) => `${prefix(l)}${basePath}` || '/';
  const isStatic = ROUTES.some((r) => r.lang === lang && r.pattern === (basePath || '/') && !r.segs.some((s) => s.includes('*')));
  const key = isStatic ? undefined : /^\/animals\/([a-z0-9-]+)$/.exec(basePath)?.[1];
  const isFilterKey = !!key && (key in ANIMALS.en.species || key in ANIMALS.en.categories);

  let kind: PageSeo['kind'] = 'page';
  let langs: [Lang, string][] = [];
  if (key && !isFilterKey && articleIn(lang, key)) {
    // Articles: translations share the slug, or are paired in TRANSLATION_GROUPS under different slugs.
    kind = 'article';
    const group = TRANSLATION_GROUPS.find((g) => g[lang] === key);
    langs = group ? LANGS.filter((l) => group[l] && articleIn(l, group[l]!)).map((l) => [l, `${prefix(l)}/animals/${group[l]}`])
      : LANGS.filter((l) => articleIn(l, key)).map((l) => [l, at(l)]);
  } else if (key && (isFilterKey || lexiconIn(lang, key))) {
    // /animals/<key>: an animal-guide listing (species or topic) and/or a lexicon entry. It has content in a
    // language when that language has articles for it, a curated profile, or a lexicon entry.
    kind = lexiconIn(lang, key) ? 'lexicon' : 'listing';
    langs = LANGS.filter((l) => (isFilterKey && hasListing(l, key)) || !!lexiconIn(l, key)).map((l) => [l, at(l)]);
  } else {
    langs = routeLangs(basePath, lang).map((l) => [l, at(l)]);
  }
  // Only an animal-guide listing with nothing in it is kept out of search; other pages never are by default.
  const noindex = kind === 'listing' && !langs.some(([l]) => l === lang);
  const alternates = noindex || langs.length < 2 ? [] : langs;

  // Structured data: a lexicon entry is a page about one animal; any other page below a menu page gets a
  // breadcrumb from that parent. Articles build their own (Article.astro).
  const graph: Record<string, unknown>[] = [];
  const parentPath = path.replace(/\/[^/]+$/, '');
  const parentLabel = /^(\/(it|de))?\/?$/.test(parentPath) ? undefined : page.labels.get(parentPath);
  const crumb = parentLabel && kind !== 'article' && !noindex ? {
    '@type': 'BreadcrumbList', '@id': `${url}#breadcrumb`,
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: parentLabel, item: new URL(parentPath, SITE).href },
      { '@type': 'ListItem', position: 2, name: page.title },
    ],
  } : null;
  const entry = kind === 'lexicon' && key ? lexiconIn(lang, key) : undefined;
  if (entry && !noindex) {
    const d = entry.data;
    graph.push({
      '@type': 'WebPage', '@id': url, url, name: page.title, description: page.description, inLanguage: lang,
      isPartOf: { '@id': WEBSITE_ID }, ...(crumb ? { breadcrumb: { '@id': crumb['@id'] } } : {}),
      dateModified: d.updated.toISOString().slice(0, 10),
      about: { '@type': 'Thing', name: d.name, ...(d.scientific ? { alternateName: d.scientific } : {}), ...(wikidata(key!) ? { sameAs: wikidata(key!) } : {}) },
      publisher: ORG,
      citation: d.references.map((r) => ({ '@type': 'CreativeWork', name: r.title, url: r.url })),
    });
  }
  if (crumb) graph.push(crumb);
  return { kind, noindex, alternates, graph };
}
