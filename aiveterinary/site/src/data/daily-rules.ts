/**
 * Daily check: questions per species and the warning rules shown in the health booklet (Passport.astro).
 *
 * CONTENT RULE: a warning exists only where one of our own articles states it. Each rule names the
 * article in every language and gives a short label that paraphrases that article's sentence without
 * adding facts. No diagnosis wording: the page prefixes go-now labels with "Our article says this can be
 * an emergency:" and always adds "This is not a diagnosis. If you are worried, call your vet."
 *
 *   species  booklet species keys (the values stored in the passport: 'Dog', 'Guinea pig', ...)
 *   level    'go-now' (red), 'today' (amber), 'watch' (neutral)
 *   when     any-of list; inside one entry every named question must have one of the listed answers
 *   days     the condition must hold on this many consecutive logged days, ending on the checked day (default 1)
 *   article  per language: slug of the article (src/content/animals/<lang>/<slug>.md, EN at the root)
 *            and an anchor, a verbatim excerpt of that article (markdown emphasis removed) the label comes from
 *   label    per language, what the banner shows after the level prefix
 *
 * Checked by `node scripts/check-daily-rules.mjs` (part of `npm run build`).
 */
export type Lang = 'en' | 'it' | 'de';
export type Q = 'eat' | 'drink' | 'poo' | 'pee' | 'strain' | 'energy' | 'vomit';
export type Level = 'go-now' | 'today' | 'watch';
export interface DailyRule {
  id: string;
  species: string[];
  level: Level;
  when: Partial<Record<Q, string[]>>[];
  days?: number;
  article: Record<Lang, { slug: string; anchor: string }>;
  label: Record<Lang, string>;
}

/** Stored answer values per question (the passport keeps these English keys; labels below are per language). */
export const ANSWERS: Record<Q, string[]> = {
  eat: ['normal', 'less', 'none', 'more'],
  drink: ['normal', 'less', 'none', 'more'],
  poo: ['normal', 'less', 'none', 'more'],
  pee: ['normal', 'less', 'none', 'more'],
  strain: ['no', 'yes'],
  energy: ['normal', 'less', 'weak'],
  vomit: ['no', 'once', 'several'],
};
export const QUESTION_ORDER: Q[] = ['eat', 'drink', 'poo', 'pee', 'strain', 'energy', 'vomit'];

/**
 * Questions asked per booklet species. An empty list means no daily check card (fish).
 * Birds: droppings, no separate urine question. Reptiles: a reduced set. Rabbits, guinea pigs,
 * hamsters and horses are not asked about vomiting.
 */
export const SPECIES_QUESTIONS: Record<string, Q[]> = {
  Dog: ['eat', 'drink', 'poo', 'pee', 'energy', 'vomit'],
  Cat: ['eat', 'drink', 'poo', 'pee', 'strain', 'energy', 'vomit'],
  Ferret: ['eat', 'drink', 'poo', 'pee', 'energy', 'vomit'],
  Rabbit: ['eat', 'drink', 'poo', 'pee', 'energy'],
  'Guinea pig': ['eat', 'drink', 'poo', 'pee', 'energy'],
  Hamster: ['eat', 'drink', 'poo', 'pee', 'energy'],
  Horse: ['eat', 'drink', 'poo', 'pee', 'energy'],
  Bird: ['eat', 'drink', 'poo', 'energy', 'vomit'],
  Reptile: ['eat', 'poo', 'energy'],
  Fish: [],
};
export const DEFAULT_QUESTIONS: Q[] = ['eat', 'drink', 'poo', 'pee', 'energy', 'vomit'];
export const questionsFor = (species: string | undefined): Q[] => SPECIES_QUESTIONS[species ?? ''] ?? DEFAULT_QUESTIONS;

/** Species whose droppings question says "Droppings" (EN) / "Köttel" (DE) instead of "Poo" / "Kot". */
export const DROPPINGS = ['Rabbit', 'Guinea pig', 'Hamster', 'Horse', 'Bird', 'Reptile'];
export const QUESTION_LABELS: Record<Lang, Record<Q, string> & { droppings: string }> = {
  en: { eat: 'Eating', drink: 'Drinking', poo: 'Poo', droppings: 'Droppings', pee: 'Urine', strain: 'Straining in the litter tray', energy: 'Energy', vomit: 'Vomiting' },
  it: { eat: 'Mangia', drink: 'Beve', poo: 'Feci', droppings: 'Feci (palline)', pee: 'Urina', strain: 'Si sforza nella lettiera', energy: 'Energia', vomit: 'Vomito' },
  de: { eat: 'Fressen', drink: 'Trinken', poo: 'Kot', droppings: 'Kot (Köttel)', pee: 'Urin', strain: 'Pressen auf der Katzentoilette', energy: 'Energie', vomit: 'Erbrechen' },
};
export const questionLabel = (lang: Lang, q: Q, species?: string) => (q === 'poo' && DROPPINGS.includes(species ?? '') ? QUESTION_LABELS[lang].droppings : QUESTION_LABELS[lang][q]);
export const ANSWER_LABELS: Record<Lang, Record<string, string>> = {
  en: { normal: 'Normal', less: 'Less', none: 'None', more: 'More', no: 'No', yes: 'Yes', once: 'Once', several: 'Several times', weak: 'Very weak / collapsed' },
  it: { normal: 'Normale', less: 'Meno', none: 'Niente', more: 'Di più', no: 'No', yes: 'Sì', once: 'Una volta', several: 'Più volte', weak: 'Molto debole / collassato' },
  de: { normal: 'Normal', less: 'Weniger', none: 'Gar nicht', more: 'Mehr', no: 'Nein', yes: 'Ja', once: 'Einmal', several: 'Mehrmals', weak: 'Sehr schwach / zusammen\u00ADgebrochen' },
};

const RABBIT = { en: 'rabbit-not-eating', it: 'rabbit-not-eating', de: 'rabbit-not-eating' };
const GUINEA = { en: 'guinea-pig-not-eating', it: 'cavia-non-mangia', de: 'meerschweinchen-frisst-nicht' };
const CAT_URINE = { en: 'cat-straining-litter-box', it: 'gatto-non-fa-pipi', de: 'katze-blasenentzuendung' };
const CAT_EAT = { en: 'cat-not-eating', it: 'cat-not-eating', de: 'katze-frisst-nicht' };
const CAT_VOMIT = { en: 'cat-vomiting', it: 'cat-vomiting', de: 'cat-vomiting' };
const DOG_EAT = { en: 'dog-not-eating', it: 'dog-not-eating', de: 'dog-not-eating' };
const DOG_VOMIT = { en: 'dog-vomiting', it: 'dog-vomiting', de: 'dog-vomiting' };
const FERRET_WEAK = { en: 'ferret-weak-wobbly-collapsed', it: 'insulinoma-furetto-sintomi', de: 'frettchen-insulinom-symptome' };
const FERRET_EAT = { en: 'ferret-not-eating-vomiting', it: 'furetto-non-mangia-vomita', de: 'frettchen-frisst-nicht-erbricht' };
const BIRD = { en: 'budgie-fluffed-up', it: 'cocorita-gonfia-dorme', de: 'wellensittich-aufgeplustert' };
const REPTILE = { en: 'reptile-not-eating', it: 'rettile-non-mangia', de: 'reptil-frisst-nicht' };
const HORSE = { en: 'horse-colic', it: 'colica-cavallo', de: 'kolik-pferd' };

const art = (slugs: Record<Lang, string>, en: string, it: string, de: string): DailyRule['article'] => ({ en: { slug: slugs.en, anchor: en }, it: { slug: slugs.it, anchor: it }, de: { slug: slugs.de, anchor: de } });
const OFF = ['less', 'none'];
const VOMITED = ['once', 'several'];

export const RULES: DailyRule[] = [
  // ---- Rabbit (rabbit-not-eating: "Do not wait for a set number of hours") ----
  { id: 'rabbit-eat-none', species: ['Rabbit'], level: 'go-now', when: [{ eat: ['none'] }],
    article: art(RABBIT, 'has stopped eating, or you are not sure when it last ate', "ha smesso di mangiare, o non sai con certezza quando ha mangiato l'ultima volta", 'aufgehört hat zu fressen oder Sie nicht sicher sind, wann es zuletzt gefressen hat'),
    label: { en: 'a rabbit that has stopped eating. Do not wait for a set number of hours.', it: 'un coniglio che ha smesso di mangiare. Non aspettare un certo numero di ore.', de: 'ein Kaninchen, das aufgehört hat zu fressen. Warten Sie keine bestimmte Stundenzahl ab.' } },
  { id: 'rabbit-poo', species: ['Rabbit'], level: 'go-now', when: [{ poo: ['none', 'less'] }],
    article: art(RABBIT, 'has passed no droppings, or far fewer and smaller droppings than usual', 'non ha fatto feci, o ne ha fatte molte meno e più piccole del solito', 'keinen Kot abgesetzt hat oder deutlich weniger und kleinere Köttel als sonst'),
    label: { en: 'no droppings, or far fewer and smaller droppings than usual.', it: 'niente feci, o feci molto meno numerose e più piccole del solito.', de: 'kein Kot oder deutlich weniger und kleinere Köttel als sonst.' } },
  { id: 'rabbit-weak', species: ['Rabbit'], level: 'go-now', when: [{ energy: ['weak'] }],
    article: art(RABBIT, 'is very still, floppy, cold to the touch, or unresponsive', 'è molto immobile, molle, freddo al tatto, o non risponde', 'sehr still, schlaff, kalt anzufassen oder nicht ansprechbar ist'),
    label: { en: 'a rabbit that is very still, floppy, cold to the touch or unresponsive.', it: 'un coniglio molto immobile, molle, freddo al tatto o che non risponde.', de: 'ein Kaninchen, das sehr still, schlaff, kalt anzufassen oder nicht ansprechbar ist.' } },
  { id: 'rabbit-eat-less', species: ['Rabbit'], level: 'today', when: [{ eat: ['less'] }],
    article: art(RABBIT, 'is eating less than usual, or only picking at favourites and leaving hay', 'mangia meno del solito, o becchetta solo i cibi preferiti e lascia il fieno', 'weniger frisst als sonst oder nur an Lieblingsfutter pickt und das Heu liegen lässt'),
    label: { en: 'a rabbit eating less than usual, or only picking at favourites and leaving hay.', it: 'un coniglio che mangia meno del solito, o becchetta solo i cibi preferiti e lascia il fieno.', de: 'ein Kaninchen, das weniger frisst als sonst oder nur an Lieblingsfutter pickt und das Heu liegen lässt.' } },
  { id: 'rabbit-drink', species: ['Rabbit'], level: 'today', when: [{ drink: ['less', 'none', 'more'] }],
    article: art(RABBIT, 'is drinking much more or much less', 'beve molto di più o molto di meno', 'deutlich mehr oder deutlich weniger trinkt'),
    label: { en: 'a rabbit drinking much more or much less than usual.', it: 'un coniglio che beve molto di più o molto di meno.', de: 'ein Kaninchen, das deutlich mehr oder deutlich weniger trinkt.' } },
  { id: 'rabbit-quiet', species: ['Rabbit'], level: 'today', when: [{ energy: ['less'] }],
    article: art(RABBIT, 'is quieter than normal, or hiding', 'è più silenzioso del normale, o si nasconde', 'ruhiger ist als normal oder sich versteckt'),
    label: { en: 'a rabbit that is quieter than normal, or hiding.', it: 'un coniglio più silenzioso del normale, o che si nasconde.', de: 'ein Kaninchen, das ruhiger ist als normal oder sich versteckt.' } },

  // ---- Guinea pig (guinea-pig-not-eating) ----
  { id: 'guinea-eat-none', species: ['Guinea pig'], level: 'go-now', when: [{ eat: ['none'] }],
    article: art(GUINEA, 'has stopped eating, or you are not sure when it last ate', "non mangia più, o non sai con certezza quando ha mangiato l'ultima volta", 'nicht mehr frisst oder Sie nicht sicher sind, wann es zuletzt gefressen hat'),
    label: { en: 'a guinea pig that has stopped eating. Do not wait for a set number of hours.', it: 'una cavia che non mangia più. Non aspettare un certo numero di ore.', de: 'ein Meerschweinchen, das nicht mehr frisst. Warten Sie keine bestimmte Stundenzahl ab.' } },
  { id: 'guinea-poo', species: ['Guinea pig'], level: 'go-now', when: [{ poo: ['none', 'less'] }],
    article: art(GUINEA, 'is passing fewer droppings than usual, or none at all', 'fa meno palline del solito, o nessuna', 'weniger Kot absetzt als sonst oder gar keinen'),
    label: { en: 'fewer droppings than usual, or none at all.', it: 'meno palline del solito, o nessuna.', de: 'weniger Kot als sonst oder gar keiner.' } },
  { id: 'guinea-drink-none', species: ['Guinea pig'], level: 'go-now', when: [{ drink: ['none'] }],
    article: art(GUINEA, 'has stopped drinking, or has severe diarrhoea', 'non beve più, o ha una diarrea forte', 'nicht mehr trinkt oder starken Durchfall hat'),
    label: { en: 'a guinea pig that has stopped drinking.', it: 'una cavia che non beve più.', de: 'ein Meerschweinchen, das nicht mehr trinkt.' } },
  { id: 'guinea-weak', species: ['Guinea pig'], level: 'go-now', when: [{ energy: ['weak'] }],
    article: art(GUINEA, 'is weak, very quiet, or hiding more than usual', 'è debole, molto più tranquilla del solito o resta nascosta', 'schwach ist, sich kaum bewegt, auffällig ruhig ist oder sich versteckt'),
    label: { en: 'a guinea pig that is weak, very quiet or hiding more than usual.', it: 'una cavia debole, molto più tranquilla del solito o che resta nascosta.', de: 'ein Meerschweinchen, das schwach ist, sich kaum bewegt oder auffällig ruhig ist.' } },
  { id: 'guinea-change', species: ['Guinea pig'], level: 'go-now', when: [{ eat: ['less'] }, { drink: ['less', 'more'] }],
    article: art(GUINEA, "The RSPCA advises consulting your vet immediately if your guinea pig's eating or drinking changes", 'La RSPCA raccomanda di consultare subito il veterinario se cambia il modo in cui la cavia mangia o beve', 'rät, sofort die Tierarztpraxis zu fragen, wenn sich das Fress- oder Trinkverhalten ändert'),
    label: { en: 'a change in eating or drinking. The RSPCA advises contacting your vet immediately.', it: 'un cambiamento nel modo in cui mangia o beve. La RSPCA raccomanda di consultare subito il veterinario.', de: 'eine Änderung beim Fressen oder Trinken. Die RSPCA rät, sofort die Tierarztpraxis zu fragen.' } },

  // ---- Cat ----
  { id: 'cat-urine', species: ['Cat'], level: 'go-now', when: [{ pee: ['none'] }, { strain: ['yes'] }],
    article: art(CAT_URINE, 'makes repeated trips to the tray and passes little or no urine', 'entra e esce dalla lettiera molte volte, si mette in posizione, spinge, e non esce nulla o escono solo poche gocce', 'immer wieder die Toilette aufsucht, presst und kein oder nur tropfenweise Urin kommt'),
    label: { en: 'repeated trips to the litter tray passing little or no urine, especially in a male cat. If you cannot tell whether it is wee or poo, treat it as the bladder.', it: 'il gatto entra ed esce dalla lettiera, spinge e non esce nulla o solo poche gocce, soprattutto se è maschio. Nel dubbio, trattalo come un\'emergenza.', de: 'immer wieder auf der Katzentoilette, Pressen, und es kommt kein oder nur tropfenweise Urin, vor allem bei einem Kater. Im Zweifel gilt die Harnröhre.' } },
  { id: 'cat-eat-2d', species: ['Cat'], level: 'go-now', when: [{ eat: ['none'] }], days: 2,
    article: art(CAT_EAT, 'has eaten nothing at all for two days, even if it otherwise seems normal', 'non ha mangiato niente per due giorni, anche se per il resto sembra', 'seit zwei Tagen gar nichts gefressen hat, auch wenn sie sonst'),
    label: { en: 'a cat that has eaten nothing at all for two days, even if it otherwise seems normal.', it: 'un gatto che non ha mangiato niente per due giorni, anche se per il resto sembra normale.', de: 'eine Katze, die seit zwei Tagen gar nichts gefressen hat, auch wenn sie sonst normal wirkt.' } },
  { id: 'cat-vomit-water', species: ['Cat'], level: 'go-now', when: [{ vomit: ['several'], drink: ['none'] }],
    article: art(CAT_VOMIT, 'vomits several times in a few hours and cannot keep water down', "vomita più volte in poche ore e non trattiene nemmeno l'acqua", 'innerhalb weniger Stunden mehrfach erbricht und kein Wasser bei sich behalten kann'),
    label: { en: 'a cat that vomits several times in a few hours and cannot keep water down.', it: "un gatto che vomita più volte in poche ore e non trattiene nemmeno l'acqua.", de: 'eine Katze, die innerhalb weniger Stunden mehrfach erbricht und kein Wasser bei sich behält.' } },
  { id: 'cat-vomit-weak', species: ['Cat'], level: 'go-now', when: [{ vomit: VOMITED, energy: ['weak'] }],
    article: art(CAT_VOMIT, 'is very weak, flat, hiding, or breathing with an open mouth', 'è molto debole, steso, si nasconde, o respira a bocca aperta', 'sehr schwach ist, flach daliegt, sich versteckt oder mit offenem Maul atmet'),
    label: { en: 'a vomiting cat that is very weak, flat or hiding.', it: 'un gatto che vomita ed è molto debole, steso o si nasconde.', de: 'eine Katze, die erbricht und sehr schwach ist, flach daliegt oder sich versteckt.' } },
  { id: 'cat-eat-none', species: ['Cat'], level: 'today', when: [{ eat: ['none'] }],
    article: art(CAT_EAT, 'if your cat has eaten nothing for 24 hours', 'se il tuo gatto non ha mangiato nulla da 24 ore', '24 Stunden gar nichts gefressen: heute einen Termin'),
    label: { en: 'a cat that has eaten nothing for 24 hours.', it: 'un gatto che non ha mangiato nulla da 24 ore.', de: 'eine Katze, die 24 Stunden gar nichts gefressen hat.' } },
  { id: 'cat-eat-less-2d', species: ['Cat'], level: 'today', when: [{ eat: OFF }], days: 2,
    article: art(CAT_EAT, 'if your cat has eaten very little for 48 hours', 'se il tuo gatto ha mangiato pochissimo da 48 ore', 'als vorsichtige Regel ebenfalls heute anrufen, wenn das seit 48 Stunden so geht'),
    label: { en: 'as a cautious rule, a cat that has eaten very little for 48 hours.', it: 'per prudenza, un gatto che ha mangiato pochissimo da 48 ore.', de: 'als vorsichtige Regel eine Katze, die seit 48 Stunden deutlich weniger frisst.' } },
  { id: 'cat-vomit-several', species: ['Cat'], level: 'today', when: [{ vomit: ['several'] }],
    article: art(CAT_VOMIT, 'your cat vomits more than once', 'il tuo gatto vomita più di una volta', 'Ihre Katze mehr als einmal erbricht'),
    label: { en: 'a cat that vomits more than once.', it: 'un gatto che vomita più di una volta.', de: 'eine Katze, die mehr als einmal erbricht.' } },
  { id: 'cat-vomit-2d', species: ['Cat'], level: 'today', when: [{ vomit: VOMITED }], days: 2,
    article: art(CAT_VOMIT, 'it continues on and off for more than 24 hours', 'continua a intermittenza per più di 24 ore', 'es über mehr als 24 Stunden immer wieder auftritt'),
    label: { en: 'vomiting that continues on and off for more than 24 hours.', it: 'vomito che continua a intermittenza per più di 24 ore.', de: 'Erbrechen, das über mehr als 24 Stunden immer wieder auftritt.' } },

  // ---- Dog ----
  { id: 'dog-no-food-water', species: ['Dog'], level: 'go-now', when: [{ eat: ['none'], drink: ['none'] }],
    article: art(DOG_EAT, 'has not eaten or drunk anything for 24 hours: the MSD Veterinary Manual lists this among the reasons to see a vet immediately', "non mangia né beve nulla da 24 ore: l'MSD Veterinary Manual lo mette tra i motivi per andare subito dal veterinario", 'seit 24 Stunden weder gefressen noch getrunken hat: Das MSD Veterinary Manual zählt das zu den Gründen, sofort in die Praxis zu gehen'),
    label: { en: 'a dog that has not eaten or drunk anything for 24 hours. The MSD Veterinary Manual lists this among the reasons to see a vet immediately.', it: "un cane che non mangia né beve nulla da 24 ore. L'MSD Veterinary Manual lo mette tra i motivi per andare subito dal veterinario.", de: 'ein Hund, der seit 24 Stunden weder gefressen noch getrunken hat. Das MSD Veterinary Manual zählt das zu den Gründen, sofort in die Praxis zu gehen.' } },
  { id: 'dog-eat-2d', species: ['Dog'], level: 'go-now', when: [{ eat: ['none'] }], days: 2,
    article: art(DOG_EAT, 'See your vet very quickly if your dog has eaten nothing for more than 24 hours', 'Fallo vedere al veterinario molto presto se non mangia nulla da più di 24 ore', 'Sehr bald in die Praxis, wenn er seit mehr als 24 Stunden gar nichts gefressen hat'),
    label: { en: 'a dog that has eaten nothing for more than 24 hours should see a vet very quickly.', it: 'un cane che non mangia nulla da più di 24 ore va fatto vedere al veterinario molto presto.', de: 'ein Hund, der seit mehr als 24 Stunden gar nichts gefressen hat, gehört sehr bald in die Praxis.' } },
  { id: 'dog-off-weak', species: ['Dog'], level: 'go-now', when: [{ eat: OFF, energy: ['weak'] }],
    article: art(DOG_EAT, 'suddenly collapses or seems very weak', "collassa all'improvviso o sembra molto debole", 'plötzlich zusammenbricht oder sehr schwach wirkt'),
    label: { en: 'a dog that is off its food and collapses or seems very weak.', it: 'un cane che non mangia e collassa o sembra molto debole.', de: 'ein Hund, der nicht frisst und zusammenbricht oder sehr schwach wirkt.' } },
  { id: 'dog-off-vomit', species: ['Dog'], level: 'go-now', when: [{ eat: OFF, vomit: ['several'] }],
    article: art(DOG_EAT, 'is vomiting again and again', 'vomita ripetutamente', 'immer wieder erbricht'),
    label: { en: 'a dog that is off its food and vomiting again and again.', it: 'un cane che non mangia e vomita ripetutamente.', de: 'ein Hund, der nicht frisst und immer wieder erbricht.' } },
  { id: 'dog-vomit-water', species: ['Dog'], level: 'go-now', when: [{ vomit: ['several'], drink: ['none'] }],
    article: art(DOG_VOMIT, 'vomits repeatedly and cannot keep water down', "vomita ripetutamente e non trattiene nemmeno l'acqua", 'wiederholt erbricht und kein Wasser bei sich behalten kann'),
    label: { en: 'a dog that vomits repeatedly and cannot keep water down.', it: "un cane che vomita ripetutamente e non trattiene nemmeno l'acqua.", de: 'ein Hund, der wiederholt erbricht und kein Wasser bei sich behalten kann.' } },
  { id: 'dog-vomit-weak', species: ['Dog'], level: 'go-now', when: [{ vomit: VOMITED, energy: ['weak'] }],
    article: art(DOG_VOMIT, 'is very weak, disoriented, or collapses', 'è molto debole, disorientato, o collassa', 'sehr schwach oder desorientiert ist oder zusammenbricht'),
    label: { en: 'a vomiting dog that is very weak, disoriented or collapses.', it: 'un cane che vomita ed è molto debole, disorientato o collassa.', de: 'ein Hund, der erbricht und sehr schwach oder desorientiert ist oder zusammenbricht.' } },
  { id: 'dog-eat-none', species: ['Dog'], level: 'today', when: [{ eat: ['none'] }],
    article: art(DOG_EAT, 'the MSD Veterinary Manual advises seeing a vet within 24 hours', "l'MSD Veterinary Manual consiglia di farlo vedere entro 24 ore", 'Das MSD Veterinary Manual rät, ihn innerhalb von 24 Stunden vorzustellen'),
    label: { en: 'a dog that has lost its appetite, even with no other signs. The MSD Veterinary Manual advises seeing a vet within 24 hours.', it: "un cane che ha perso l'appetito, anche senza altri segni. L'MSD Veterinary Manual consiglia di farlo vedere entro 24 ore.", de: 'ein Hund ohne Appetit, auch ohne andere Krankheitszeichen. Das MSD Veterinary Manual rät, ihn innerhalb von 24 Stunden vorzustellen.' } },
  { id: 'dog-off-quiet', species: ['Dog'], level: 'today', when: [{ eat: OFF, energy: ['less'] }],
    article: art(DOG_EAT, 'your dog is quiet, grumpy, or sleeping much more than usual', 'il tuo cane è spento, scontroso, o dorme molto più del solito', 'Ihr Hund ruhig oder mürrisch ist oder viel mehr schläft als sonst'),
    label: { en: 'a dog that is off its food and quiet, grumpy or sleeping much more than usual.', it: 'un cane che non mangia ed è spento, scontroso o dorme molto più del solito.', de: 'ein Hund, der nicht frisst und ruhig oder mürrisch ist oder viel mehr schläft als sonst.' } },
  { id: 'dog-vomit-several', species: ['Dog'], level: 'today', when: [{ vomit: ['several'] }],
    article: art(DOG_VOMIT, 'your dog vomits more than once, or keeps vomiting', 'il tuo cane vomita più di una volta, o continua a vomitare', 'Ihr Hund mehr als einmal erbricht oder weiter erbricht'),
    label: { en: 'a dog that vomits more than once, or keeps vomiting.', it: 'un cane che vomita più di una volta, o continua a vomitare.', de: 'ein Hund, der mehr als einmal erbricht oder weiter erbricht.' } },
  { id: 'dog-vomit-2d', species: ['Dog'], level: 'today', when: [{ vomit: VOMITED }], days: 2,
    article: art(DOG_VOMIT, 'it continues for more than 24 hours', 'continua per più di 24 ore', 'es länger als 24 Stunden anhält'),
    label: { en: 'vomiting that continues for more than 24 hours.', it: 'vomito che continua per più di 24 ore.', de: 'Erbrechen, das länger als 24 Stunden anhält.' } },
  { id: 'dog-skip-meal', species: ['Dog'], level: 'watch', when: [{ eat: ['less'], drink: ['normal', 'more'], energy: ['normal'], vomit: ['no'] }],
    article: art(DOG_EAT, 'A healthy adult dog that skips one meal but is bright, drinking and behaving normally can usually be watched for a day', 'Un cane adulto sano che salta un pasto ma è vivace, beve e si comporta normalmente può di solito essere osservato per un giorno', 'Ein gesunder erwachsener Hund, der eine Mahlzeit auslässt, aber munter ist, trinkt und sich normal verhält, kann meist einen Tag lang beobachtet werden'),
    label: { en: 'a healthy adult dog that skips a meal but is bright, drinking and behaving normally can usually be watched for a day.', it: 'un cane adulto sano che salta un pasto ma è vivace, beve e si comporta normalmente può di solito essere osservato per un giorno.', de: 'ein gesunder erwachsener Hund, der eine Mahlzeit auslässt, aber munter ist, trinkt und sich normal verhält, kann meist einen Tag lang beobachtet werden.' } },

  // ---- Ferret ----
  { id: 'ferret-weak', species: ['Ferret'], level: 'go-now', when: [{ energy: ['weak'] }],
    article: art(FERRET_WEAK, 'has collapsed, is unresponsive, or is very hard to wake', 'è collassato, non reagisce o fai molta fatica a svegliarlo', 'zusammengebrochen ist, nicht reagiert oder sich kaum wecken lässt'),
    label: { en: 'a ferret that is weak, wobbly or has collapsed, is unresponsive or very hard to wake. Do not wait to see whether it passes.', it: 'un furetto debole, che barcolla o è collassato, non reagisce o fai molta fatica a svegliarlo. Non aspettare che passi.', de: 'ein Frettchen, das schwach ist, taumelt oder zusammengebrochen ist, nicht reagiert oder sich kaum wecken lässt. Warten Sie nicht ab, ob es vorbeigeht.' } },
  { id: 'ferret-eat-drink', species: ['Ferret'], level: 'go-now', when: [{ eat: ['none'] }, { drink: ['none'] }],
    article: art(FERRET_EAT, 'has eaten nothing, or drunk nothing, for 24 hours', 'non ha mangiato niente, o non ha bevuto, da 24 ore', 'seit 24 Stunden nichts gefressen oder nichts getrunken hat'),
    label: { en: 'a ferret that has eaten nothing, or drunk nothing, for 24 hours.', it: 'un furetto che non ha mangiato niente, o non ha bevuto, da 24 ore.', de: 'ein Frettchen, das seit 24 Stunden nichts gefressen oder nichts getrunken hat.' } },
  { id: 'ferret-poo', species: ['Ferret'], level: 'go-now', when: [{ poo: ['none', 'less'] }],
    article: art(FERRET_EAT, 'has passed no poo or much less than usual', 'non fa feci o ne fa molte meno del solito', 'keinen Kot oder viel weniger als sonst absetzt'),
    label: { en: 'a ferret that has passed no poo or much less than usual.', it: 'un furetto che non fa feci o ne fa molte meno del solito.', de: 'ein Frettchen, das keinen Kot oder viel weniger als sonst absetzt.' } },
  { id: 'ferret-eat-less', species: ['Ferret'], level: 'today', when: [{ eat: ['less'] }],
    article: art(FERRET_EAT, 'A ferret that is eating less needs a vet the same day', 'Un furetto che mangia meno va visto in giornata', 'Ein Frettchen, das weniger frisst, gehört noch am selben Tag in die Praxis'),
    label: { en: 'a ferret that is eating less needs a vet the same day.', it: 'un furetto che mangia meno va visto in giornata.', de: 'ein Frettchen, das weniger frisst, gehört noch am selben Tag in die Praxis.' } },
  { id: 'ferret-vomit-2d', species: ['Ferret'], level: 'today', when: [{ vomit: VOMITED }], days: 2,
    article: art(FERRET_EAT, 'for vomiting or diarrhoea that lasts more than 24 hours', 'per vomito o diarrea che durano più di 24 ore', 'bei Erbrechen oder Durchfall, die länger als 24 Stunden dauern'),
    label: { en: 'vomiting that lasts more than 24 hours. The MSD Veterinary Manual advises seeing a vet within 24 hours.', it: "vomito che dura più di 24 ore. L'MSD Veterinary Manual indica una visita entro 24 ore.", de: 'Erbrechen, das länger als 24 Stunden dauert. Das MSD Veterinary Manual rät zur Untersuchung innerhalb von 24 Stunden.' } },

  // ---- Bird ----
  { id: 'bird-stop', species: ['Bird'], level: 'go-now', when: [{ eat: ['none'] }, { drink: ['none'] }, { poo: ['less', 'none'] }],
    article: art(BIRD, 'has stopped eating or drinking, or passes far fewer droppings than usual', 'non mangia o non beve più, oppure fa molte meno feci del solito', 'nicht mehr frisst oder trinkt oder viel weniger Kot absetzt als sonst'),
    label: { en: 'a bird that has stopped eating or drinking, or passes far fewer droppings than usual.', it: 'un uccello che non mangia o non beve più, oppure fa molte meno feci del solito.', de: 'ein Vogel, der nicht mehr frisst oder trinkt oder viel weniger Kot absetzt als sonst.' } },
  { id: 'bird-weak', species: ['Bird'], level: 'go-now', when: [{ energy: ['weak'] }],
    article: art(BIRD, 'is huddled, weak or unresponsive, or lying on the cage floor', 'sta rannicchiato, debole o non reagisce, oppure è sdraiato sul fondo della gabbia', 'zusammengekauert, schwach oder teilnahmslos ist oder am Käfigboden liegt'),
    label: { en: 'a bird that is huddled, weak or unresponsive, or lying on the cage floor.', it: 'un uccello rannicchiato, debole o che non reagisce, oppure sdraiato sul fondo della gabbia.', de: 'ein Vogel, der zusammengekauert, schwach oder teilnahmslos ist oder am Käfigboden liegt.' } },
  { id: 'bird-fluffed', species: ['Bird'], level: 'go-now', when: [{ energy: ['less'], eat: ['less'] }],
    article: art(BIRD, 'is fluffed up and sleepy and also eating less', 'è gonfio e assonnato e in più mangia meno', 'aufgeplustert und müde ist und dazu weniger frisst'),
    label: { en: 'a bird that is fluffed up and sleepy and also eating less.', it: 'un uccello gonfio e assonnato che in più mangia meno.', de: 'ein Vogel, der aufgeplustert und müde ist und dazu weniger frisst.' } },

  // ---- Reptile ----
  { id: 'reptile-weak', species: ['Reptile'], level: 'go-now', when: [{ eat: OFF, energy: ['weak'] }],
    article: art(REPTILE, 'is weak or unresponsive, or cannot walk or lift its body off the ground', 'è debole o non reagisce, oppure non riesce a camminare o a sollevare il corpo da terra', 'schwach ist oder kaum reagiert, nicht laufen oder den Körper nicht vom Boden heben kann'),
    label: { en: 'a reptile that is not eating and is weak or unresponsive, or cannot walk or lift its body off the ground.', it: 'un rettile che non mangia ed è debole o non reagisce, oppure non riesce a camminare o a sollevare il corpo da terra.', de: 'ein Reptil, das nicht frisst und schwach ist oder kaum reagiert, nicht laufen oder den Körper nicht vom Boden heben kann.' } },
  { id: 'reptile-eat', species: ['Reptile'], level: 'watch', when: [{ eat: OFF, energy: ['normal', 'less'] }],
    article: art(REPTILE, 'snakes often refuse food before a shed', 'i serpenti spesso rifiutano il cibo prima della muta', 'Schlangen verweigern vor der Häutung oft das Futter'),
    label: { en: 'a reptile eating less can be normal at times, for example before a shed or in the winter slowdown, but a reptile that is losing weight or seems unwell needs a vet.', it: 'un rettile che mangia meno a volte è normale, per esempio prima della muta o nel riposo invernale, ma un rettile che perde peso o sembra stare male va portato dal veterinario.', de: 'ein Reptil, das weniger frisst, kann zeitweise normal sein, etwa vor der Häutung oder in der Winterruhe; ein Reptil, das abnimmt oder krank wirkt, gehört aber in die Praxis.' } },

  // ---- Horse (horse-colic: "go now" means phone your vet now) ----
  { id: 'horse-eat-poo', species: ['Horse'], level: 'go-now', when: [{ eat: OFF }, { poo: ['less', 'none'] }],
    article: art(HORSE, 'eats less or nothing, or passes fewer droppings, none at all, or droppings that look different', 'mangia meno o non mangia, fa meno letame, non ne fa affatto o lo fa di consistenza diversa', 'weniger oder gar nicht frisst, weniger, keinen oder veränderten Kot absetzt'),
    label: { en: 'a horse that eats less or nothing, or passes fewer droppings or none at all. With a horse, this means phoning your vet now, at night too.', it: 'un cavallo che mangia meno o non mangia, fa meno letame o non ne fa affatto. Con un cavallo significa chiamare subito il veterinario, anche di notte.', de: 'ein Pferd, das weniger oder gar nicht frisst oder weniger oder keinen Kot absetzt. Beim Pferd heißt das: jetzt die Tierärztin oder den Tierarzt anrufen, auch nachts.' } },
  { id: 'horse-dull', species: ['Horse'], level: 'go-now', when: [{ energy: ['less', 'weak'] }],
    article: art(HORSE, 'is dull, lies down more than usual or stands with its head low', 'è abbattuto, sta sdraiato più del solito o tiene la testa bassa', 'matt ist, mehr liegt als sonst oder den Kopf tief hält'),
    label: { en: 'a horse that is dull, lies down more than usual or stands with its head low. With a horse, this means phoning your vet now.', it: 'un cavallo abbattuto, che sta sdraiato più del solito o tiene la testa bassa. Con un cavallo significa chiamare subito il veterinario.', de: 'ein Pferd, das matt ist, mehr liegt als sonst oder den Kopf tief hält. Beim Pferd heißt das: jetzt die Praxis anrufen.' } },
];

export const LEVEL_ORDER: Level[] = ['go-now', 'today', 'watch'];

/** ISO date `n` days before `iso` (calendar arithmetic on the date string, no time zone involved). */
export const daysBefore = (iso: string, n: number) => { const d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() - n); return d.toISOString().slice(0, 10); };

type RuleLike = Pick<DailyRule, 'species' | 'level' | 'when' | 'days'>;
/**
 * Rules triggered on `date` given the animal's logged checks (rows with a `date` key), most urgent first.
 * A rule with `days: n` needs a matching check on each of the n consecutive days ending on `date`.
 * Takes the rule list as an argument so the booklet can pass its own language's copy.
 */
export function evaluateRules<R extends RuleLike>(rules: R[], species: string | undefined, checks: Record<string, string>[], date: string): R[] {
  const byDate = new Map(checks.map((c) => [c.date, c]));
  const matches = (r: R, c: Record<string, string> | undefined) => !!c && r.when.some((w) => Object.entries(w).every(([q, vals]) => (vals as string[]).includes(c[q])));
  return rules.filter((r) => r.species.includes(species ?? ''))
    .filter((r) => Array.from({ length: r.days ?? 1 }, (_, i) => byDate.get(daysBefore(date, i))).every((c) => matches(r, c)))
    .sort((a, b) => LEVEL_ORDER.indexOf(a.level) - LEVEL_ORDER.indexOf(b.level));
}
export const evaluate = (species: string | undefined, checks: Record<string, string>[], date: string) => evaluateRules(RULES, species, checks, date);
