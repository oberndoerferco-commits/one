/**
 * Animal lexicon (src/content/lexicon): group and fact-sheet labels, display order, and the dose
 * pattern the fact sheets must never contain. Pure data with no runtime imports, because
 * scripts/check-lexicon.mjs loads it with Node as well as Astro.
 */
import type { Lang } from './animals-i18n';

/** Groups in the order the "By group" view shows them (same values as the collection schema). */
export const GROUPS = ['dogs-cats', 'small-mammals', 'birds', 'reptiles', 'fish', 'horses', 'poultry'] as const;
export type Group = (typeof GROUPS)[number];

/** Fact-sheet rows in display order (same values as the collection schema). */
export const FIELDS = ['lifespan', 'size', 'weight', 'coat', 'temperament', 'social', 'activity', 'diet', 'housing', 'temperature', 'teeth', 'handling', 'breed-health', 'vet', 'legal'] as const;
export type Field = (typeof FIELDS)[number];

/**
 * A dose in a fact value (mg, mcg/µg, ml/kg, IU and its Italian and German forms UI and I.E./IE).
 * Fact sheets describe the animal; doses belong to a vet, so the lexicon check rejects them.
 */
export const DOSE = /\d\s*(?:mg|mcg|[µμ]g)(?![\p{L}])|ml\s*\/\s*kg|\d\s*(?:IU|UI|I\.\s?E\.|IE)(?![\p{L}])/iu;

export const GROUP_LABEL: Record<Lang, Record<Group, string>> = {
  en: { 'dogs-cats': 'Dogs & cats', 'small-mammals': 'Small mammals', birds: 'Birds', reptiles: 'Reptiles', fish: 'Fish', horses: 'Horses', poultry: 'Poultry' },
  it: { 'dogs-cats': 'Cani e gatti', 'small-mammals': 'Piccoli mammiferi', birds: 'Uccelli', reptiles: 'Rettili', fish: 'Pesci', horses: 'Cavalli', poultry: 'Pollame' },
  de: { 'dogs-cats': 'Hunde & Katzen', 'small-mammals': 'Kleinsäuger', birds: 'Vögel', reptiles: 'Reptilien', fish: 'Fische', horses: 'Pferde', poultry: 'Geflügel' },
};

export const FIELD_LABEL: Record<Lang, Record<Field, string>> = {
  en: { lifespan: 'Lifespan', size: 'Size', weight: 'Weight', coat: 'Coat and grooming', temperament: 'Temperament', social: 'Social life', activity: 'Activity', diet: 'Diet', housing: 'Housing', temperature: 'Temperature', teeth: 'Teeth', handling: 'Handling', 'breed-health': 'Breed health', vet: 'Vet care', legal: 'Legal' },
  it: { lifespan: 'Durata della vita', size: 'Taglia', weight: 'Peso', coat: 'Mantello e toelettatura', temperament: 'Carattere', social: 'Vita sociale', activity: 'Attività', diet: 'Alimentazione', housing: 'Alloggio', temperature: 'Temperatura', teeth: 'Denti', handling: 'Come maneggiarlo', 'breed-health': 'Salute della razza', vet: 'Cure veterinarie', legal: 'Norme' },
  de: { lifespan: 'Lebenserwartung', size: 'Größe', weight: 'Gewicht', coat: 'Fell und Pflege', temperament: 'Wesen', social: 'Sozialverhalten', activity: 'Aktivität', diet: 'Ernährung', housing: 'Haltung', temperature: 'Temperatur', teeth: 'Zähne', handling: 'Umgang', 'breed-health': 'Rassetypische Gesundheit', vet: 'Tierärztliche Versorgung', legal: 'Rechtliches' },
};

/** Interface words for the entry page. Facts, names and sources always come from the entry itself. */
export const LEX = {
  en: {
    factSheet: 'Fact sheet', sources: 'Sources', source: 'Source', sci: 'Scientific name',
    draft: 'Draft written with AI assistance', draftNot: 'not yet reviewed by a vet', updated: 'Updated',
    nSources: (n: number) => (n === 1 ? '1 source' : `${n} sources`),
    title: (name: string, health: boolean) => `${name}: ${health ? 'fact sheet and health' : 'fact sheet'}`,
    breedTitle: (name: string) => `${name}: health problems, lifespan, fact sheet`,
    breeds: 'Breeds', breedsLead: (n: number) => `${n === 1 ? '1 breed' : `${n} breeds`} with their own fact sheet: lifespan, size, coat and the health problems the breed is known for.`,
    breedsOf: (parent: string, name: string) => ({ dog: 'Dog breeds', cat: 'Cat breeds' } as Record<string, string>)[parent] ?? `${name}: breeds`,
    nBreeds: (n: number) => (n === 1 ? '1 breed' : `${n} breeds`), breadcrumb: 'Breadcrumb',
  },
  it: {
    factSheet: 'Scheda', sources: 'Fonti', source: 'Fonte', sci: 'Nome scientifico',
    draft: "Bozza scritta con l'assistenza dell'IA", draftNot: 'non ancora rivista da un veterinario', updated: 'Aggiornato',
    nSources: (n: number) => (n === 1 ? '1 fonte' : `${n} fonti`),
    title: (name: string, health: boolean) => `${name}: ${health ? 'scheda e salute' : 'scheda'}`,
    breedTitle: (name: string) => `${name}: salute, durata della vita e scheda`,
    breeds: 'Razze', breedsLead: (n: number) => `${n === 1 ? '1 razza' : `${n} razze`} con la propria scheda: durata della vita, taglia, mantello e i problemi di salute noti della razza.`,
    breedsOf: (parent: string, name: string) => ({ dog: 'Razze di cani', cat: 'Razze di gatti' } as Record<string, string>)[parent] ?? `${name}: razze`,
    nBreeds: (n: number) => (n === 1 ? '1 razza' : `${n} razze`), breadcrumb: 'Percorso',
  },
  de: {
    factSheet: 'Steckbrief', sources: 'Quellen', source: 'Quelle', sci: 'Wissenschaftlicher Name',
    draft: 'Entwurf mit KI-Unterstützung', draftNot: 'noch nicht tierärztlich geprüft', updated: 'Aktualisiert',
    nSources: (n: number) => (n === 1 ? '1 Quelle' : `${n} Quellen`),
    title: (name: string, health: boolean) => `${name}: ${health ? 'Steckbrief und Gesundheit' : 'Steckbrief'}`,
    breedTitle: (name: string) => `${name}: Gesundheit, Lebenserwartung, Steckbrief`,
    breeds: 'Rassen', breedsLead: (n: number) => `${n === 1 ? '1 Rasse' : `${n} Rassen`} mit eigenem Steckbrief: Lebenserwartung, Größe, Fell und die bekannten Gesundheitsprobleme der Rasse.`,
    breedsOf: (parent: string, name: string) => ({ dog: 'Hunderassen', cat: 'Katzenrassen' } as Record<string, string>)[parent] ?? `${name}: Rassen`,
    nBreeds: (n: number) => (n === 1 ? '1 Rasse' : `${n} Rassen`), breadcrumb: 'Brotkrümelnavigation',
  },
} as const;

/** The A–Z heading an entry is listed under: first letter without accents (Ä → A); '#' for anything else. */
export const letterOf = (name: string) => {
  const c = name.normalize('NFD').replace(/[̀-ͯ]/g, '').charAt(0).toUpperCase();
  return c >= 'A' && c <= 'Z' ? c : '#';
};
