/**
 * Build-time data for the animal pages (Astro only: reads astro:content).
 *   - articles and lexicon entries per language
 *   - health topics per species (its articles plus SHARED_TOPICS) and per lexicon entry
 *   - which /animals/<key> pages exist and what each one is: an animal page (species profile and/or
 *     lexicon entry, merged on one URL) or a listing (topic, or a species with nothing in it yet)
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import { ANIMALS, slugOf, type Lang } from './animals-i18n';
import { ICONS, type IconKind } from './animal-icons';
import { LEX, type Group } from './lexicon';
import { PROFILES, SPECIES, SHARED_TOPICS, type SpeciesKey } from '../data/species';

export type Article = CollectionEntry<'animals'>;
export type LexEntry = CollectionEntry<'lexicon'>;
export const keyOf = (e: { id: string }) => slugOf(e.id);

const LOCALE = { en: 'en-GB', it: 'it-IT', de: 'de-DE' } as const;
export const collator = (lang: Lang) => new Intl.Collator(LOCALE[lang], { sensitivity: 'base', numeric: true });

// Both collections, read once per build. Astro warns on every read of an empty collection, and the
// lexicon starts empty, so repeated reads would flood the build log.
let cached: Promise<[Article[], LexEntry[]]> | undefined;
const load = () => Promise.all([getCollection('animals'), getCollection('lexicon')]);
const all = () => (import.meta.env.PROD ? (cached ??= load()) : load());

export const articlesIn = async (lang: Lang) => (await all())[0].filter((e) => e.data.lang === lang);
/** Lexicon entries in a language, sorted by their localized name. */
export const lexiconIn = async (lang: Lang) => {
  const c = collator(lang);
  return (await all())[1].filter((e) => e.data.lang === lang).sort((a, b) => c.compare(a.data.name, b.data.name));
};
export const entryOf = async (lang: Lang, key: string) => (await lexiconIn(lang)).find((e) => keyOf(e) === key);
/** Breed entries of an animal (entries whose `parent` is that key), sorted by their localized name. */
export const breedsOf = async (lang: Lang, key: string) => (await lexiconIn(lang)).filter((e) => e.data.parent === key);

const URGENCY = { emergency: 0, today: 1, 'this-week': 2, routine: 3 } as const;
/** Most urgent first, then by title. */
export const byUrgency = (lang: Lang) => {
  const c = collator(lang);
  return (a: Article, b: Article) => URGENCY[a.data.urgency ?? 'routine'] - URGENCY[b.data.urgency ?? 'routine'] || c.compare(a.data.title, b.data.title);
};

export const isSpecies = (key: string): key is SpeciesKey => (SPECIES as readonly string[]).includes(key);

/** Health topics of a species: articles with that species plus the shared ones, most urgent first. */
export async function speciesTopics(lang: Lang, key: SpeciesKey): Promise<Article[]> {
  const shared = new Set(SHARED_TOPICS[key]?.[lang] ?? []);
  return (await articlesIn(lang)).filter((e) => e.data.species === key || shared.has(keyOf(e))).sort(byUrgency(lang));
}

/** Species that have at least one health topic in this language, in guide order. */
export async function liveSpecies(lang: Lang): Promise<SpeciesKey[]> {
  const live: SpeciesKey[] = [];
  for (const k of SPECIES) if ((await speciesTopics(lang, k)).length) live.push(k);
  return live;
}

/**
 * Health topics for a lexicon entry: articles whose `animals` list names it, or else the articles of its
 * species. On a species page (key = species) both, merged.
 */
export async function entryTopics(lang: Lang, key: string, species?: SpeciesKey): Promise<Article[]> {
  const tagged = (await articlesIn(lang)).filter((e) => e.data.animals?.includes(key));
  const own = isSpecies(key) ? await speciesTopics(lang, key) : [];
  const fallback = !tagged.length && !own.length && species ? await speciesTopics(lang, species) : [];
  const seen = new Set<string>();
  return [...own, ...tagged, ...fallback].filter((e) => !seen.has(e.id) && !!seen.add(e.id)).sort(byUrgency(lang));
}

// Icon and card tint for a lexicon entry: its own face where one is drawn, else its species', else its group's.
const GROUP_ICON: Record<Group, IconKind> = { 'dogs-cats': 'dog', 'small-mammals': 'guinea-pig', birds: 'bird', reptiles: 'reptile', fish: 'fish', horses: 'horse', poultry: 'hen' };
const GROUP_TINT: Record<Group, string> = { 'dogs-cats': 'dog', 'small-mammals': 'guinea-pig', birds: 'bird', reptiles: 'reptile', fish: 'fish', horses: 'horse', poultry: 'poultry' };
const drawn = (k?: string): k is IconKind => !!k && k in ICONS && k !== 'general' && k !== 'paw';
export const iconOf = (key: string, group: Group, species?: string): IconKind => (drawn(key) ? key : drawn(species) ? species : GROUP_ICON[group]);
export const tintOf = (key: string, group: Group, species?: string) => (drawn(key) ? key : drawn(species) ? species : GROUP_TINT[group]);

/** Every /animals/<key> page in a language: species, topics, then lexicon entries (never over an article). */
export async function animalPaths(lang: Lang) {
  const t = ANIMALS[lang];
  const fixed = [...Object.keys(t.species), ...Object.keys(t.categories)];
  const articles = new Set((await articlesIn(lang)).map(keyOf));
  const extra = (await lexiconIn(lang)).map(keyOf).filter((k) => !fixed.includes(k) && k !== 'all' && !articles.has(k));
  return [...fixed, ...extra].map((filter) => ({ params: { filter } }));
}

const LISTING_DESC = {
  en: (label: string) => `${label}: plain-language articles for owners on symptoms, when to see a vet, care and prevention, from veterinary sources. Each one shows whether a vet has reviewed it.`,
  it: (label: string) => `${label}: articoli in parole semplici per i proprietari su sintomi, quando andare dal veterinario, cura e prevenzione, da fonti veterinarie. Ognuno indica se è già stato rivisto da un veterinario.`,
  de: (label: string) => `${label}: verständliche Artikel für Halter zu Symptomen, wann in die Praxis, Pflege und Vorbeugung, aus tierärztlichen Quellen. Jeder zeigt, ob er schon tierärztlich geprüft ist.`,
};

/**
 * What /animals/<key> shows in a language. An animal page when the key has a lexicon entry, or is a
 * species with at least one health topic; otherwise the plain listing (topics, empty species).
 */
export async function animalPage(lang: Lang, key: string) {
  const t = ANIMALS[lang];
  const entry = await entryOf(lang, key);
  const species = isSpecies(key) ? key : undefined;
  // A breed shows its own tagged articles plus its parent animal's health topics.
  const parent = entry?.data.parent ? await entryOf(lang, entry.data.parent) : undefined;
  const parentTopics = parent ? await entryTopics(lang, keyOf(parent), parent.data.species) : [];
  const own = entry ? await entryTopics(lang, key, parent ? undefined : entry.data.species) : species ? await speciesTopics(lang, species) : [];
  const seen = new Set<string>();
  const topics = [...own, ...parentTopics].filter((e) => !seen.has(e.id) && !!seen.add(e.id)).sort(byUrgency(lang));
  if (entry) return { kind: 'animal' as const, entry, parent, species, topics, title: parent ? LEX[lang].breedTitle(entry.data.name) : LEX[lang].title(entry.data.name, topics.length > 0), description: entry.data.description };
  if (species && topics.length) return { kind: 'animal' as const, entry, parent, species, topics, title: PROFILES[species].name[lang], description: PROFILES[species].intro[lang] };
  const label = (t.species as Record<string, string>)[key] ?? (t.categories as Record<string, readonly string[]>)[key]?.[0] ?? key;
  return { kind: 'listing' as const, entry, parent, species, topics, title: label, description: LISTING_DESC[lang](label) };
}
