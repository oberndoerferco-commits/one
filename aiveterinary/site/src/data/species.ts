/**
 * Animal guide: curated, sourced content for the species profile pages (/animals/dog, /animals/guinea-pig, …).
 *
 * CONTENT RULE: nothing here is a new medical fact. Every go-now sign, key fact and care item is
 * quoted or closely paraphrased from a sentence that already exists in one of our articles, in
 * the same language, and names the source that article gives for it.
 *
 *   text    what the page shows (close paraphrase of the article sentence)
 *   sources source names as the article names them
 *   slug    the article (in that language) the sentence comes from; the page links to it
 *   anchor  a verbatim excerpt of the article (markdown emphasis removed) proving the sentence is there
 *   via     'text' when the article attributes the sentence inline; 'ref' when the attribution is
 *           the article's own topic-specific reference (e.g. "Pet Poison Helpline: Lilies")
 *
 * A language is simply left out of an item when that language's article has no matching sourced
 * sentence; the page then does not show the item in that language (no placeholders).
 * Checked by `node scripts/check-species.mjs` and asserted at build time in AnimalsFilter.astro.
 */
export type Lang = 'en' | 'it' | 'de';
/** Every article species except 'general', in the order the guide shows them. Route slug = key (/animals/guinea-pig). */
export const SPECIES = ['dog', 'cat', 'rabbit', 'guinea-pig', 'ferret', 'horse', 'bird', 'reptile'] as const;
export type SpeciesKey = (typeof SPECIES)[number];
/** Every species has a profile entry; most are still empty and fill in as sourced items are added. */
export type ProfileKey = SpeciesKey;
export interface Cited { text: string; sources: string[]; slug: string; anchor: string; via: 'text' | 'ref' }
export type Item = Partial<Record<Lang, Cited>>;
export interface Profile {
  key: ProfileKey;
  name: Record<Lang, string>;
  intro: Record<Lang, string>;
  mostRead: Record<Lang, string[]>;
  goNow: Item[];
  facts: Item[];
  care: Item[];
}

const t = (text: string, sources: string[], slug: string, anchor: string, via: 'text' | 'ref' = 'text'): Cited => ({ text, sources, slug, anchor, via });

/** The rabbit article that also covers guinea pigs (filed under species: rabbit). */
export const GUINEA_PIG_ARTICLE: Record<Lang, string> = {
  en: 'rabbit-guinea-pig-toxic-plants',
  it: 'piante-tossiche-coniglio-cavia',
  de: 'giftige-pflanzen-kaninchen-meerschweinchen',
};

export const PROFILES: Record<ProfileKey, Profile> = {
  dog: {
    key: 'dog',
    name: { en: 'Dogs', it: 'Cani', de: 'Hunde' },
    intro: {
      en: 'Everything this site has on dogs in one place: the signs that mean go now, key facts, every health topic and everyday care, each with its source.',
      it: 'Tutto quello che questo sito dice sui cani in un unico posto: i segni per correre dal veterinario, i fatti chiave, tutti gli argomenti di salute e la cura di ogni giorno, ognuno con la sua fonte.',
      de: 'Alles, was diese Seite über Hunde hat, an einem Ort: die Zeichen für sofort in die Praxis, wichtige Fakten, alle Gesundheitsthemen und die tägliche Pflege, jeweils mit Quelle.',
    },
    mostRead: {
      en: ['dog-ate-chocolate', 'dog-vomiting', 'dog-diarrhoea'],
      it: ['cane-ha-mangiato-cioccolato', 'dog-vomiting', 'dog-diarrhoea'],
      de: ['hund-schokolade-gefressen', 'dog-vomiting', 'dog-diarrhoea'],
    },
    goNow: [
      {
        en: t('After a sting: difficulty breathing, a face, lips or throat swelling quickly, vomiting, pale gums, hives or collapse can mean a severe allergic reaction. Never wait to see if the symptoms improve.', ['PDSA'], 'dog-bee-wasp-sting', 'the PDSA says "never wait to see if their symptoms improve"'),
        it: t('Dopo una puntura: difficoltà a respirare, muso, labbra o gola che si gonfiano rapidamente, vomito, gengive pallide, orticaria o collasso possono indicare una reazione allergica grave. Non aspettare mai che i sintomi migliorino.', ['PDSA'], 'cane-punto-da-ape', 'la PDSA raccomanda di non aspettare mai che i sintomi migliorino'),
        de: t('Nach einem Stich: Atemnot, eine rasch zunehmende Schwellung an Gesicht, Lefzen oder Hals, Erbrechen, blasses Zahnfleisch, Quaddeln oder ein Zusammenbruch können eine schwere allergische Reaktion bedeuten. Warten Sie nicht ab, ob es besser wird.', ['PDSA'], 'hund-bienenstich-wespenstich', 'Warten Sie nicht ab, ob es besser wird: Die PDSA, eine britische Tierhilfsorganisation, rät ausdrücklich davon ab.'),
      },
      {
        en: t('An unspayed female, usually 4 to 6 weeks after a season, who is lethargic, drinking much more, vomiting, has a discharge or a swelling belly: this can be pyometra, which can quickly progress to shock and death.', ['MSD Veterinary Manual'], 'dog-in-heat', 'The MSD Veterinary Manual warns that pyometra can quickly progress to shock and death'),
        it: t('Una cagna non sterilizzata, di solito 4-6 settimane dopo il calore, abbattuta, che beve molto, vomita, ha perdite o la pancia che si ingrossa: può essere una piometra, che può peggiorare rapidamente fino allo shock e alla morte.', ['MSD Veterinary Manual'], 'cagna-in-calore', "L'MSD Veterinary Manual spiega che i segni possono peggiorare rapidamente fino allo shock e alla morte"),
        de: t('Eine nicht kastrierte Hündin, meist 4 bis 6 Wochen nach der Läufigkeit, die matt ist, auffällig viel trinkt, erbricht, Ausfluss oder einen dicker werdenden Bauch hat: Das kann eine Pyometra sein, die sich rasch bis zum Schock verschlechtern und tödlich enden kann.', ['MSD Veterinary Manual'], 'huendin-laeufig', 'Eine Pyometra kann sich laut MSD Veterinary Manual rasch bis zum Schock verschlechtern und tödlich enden.'),
      },
      {
        en: t('After eating bones: vomiting, loss of appetite, tummy pain, diarrhoea and lethargy can mean a blocked stomach or intestine, an emergency that often needs surgery.', ['Cornell Riney Canine Health Center'], 'dog-ate-chicken-bones', 'calls these blockages emergencies that often need surgery'),
        it: t("Dopo aver mangiato ossa: vomito, perdita di appetito, dolore alla pancia, diarrea e abbattimento possono indicare un'ostruzione di stomaco o intestino, un'emergenza che spesso richiede la chirurgia.", ['Cornell Riney Canine Health Center'], 'cane-ha-mangiato-ossa-di-pollo', "definisce le ostruzioni un'emergenza che spesso richiede la rimozione chirurgica"),
        de: t('Nach dem Fressen von Knochen: Erbrechen, Appetitlosigkeit, Bauchschmerzen, Durchfall und Mattigkeit können eine Verlegung von Magen oder Darm bedeuten, ein Notfall, der meist eine Operation erfordert.', ['Cornell Riney Canine Health Center'], 'hund-hat-huehnerknochen-gefressen', 'bezeichnet einen Darmverschluss als Notfall, der meist eine Operation erfordert'),
      },
      {
        en: t('Your dog has eaten any grapes, raisins, sultanas or currants, even only a few and even if it seems completely well. Call a vet straight away; do not wait to see if signs develop.', ['Cornell University, Riney Canine Health Center'], 'dog-ate-grapes', 'call your vet or the nearest emergency clinic straight away. Do not wait to see if signs develop.', 'ref'),
        it: t('Il cane ha mangiato uva, uvetta, uva sultanina o uva di Corinto, anche poca: chiama subito il veterinario, senza aspettare i sintomi, perché le cure funzionano meglio quando sono rapide.', ['PDSA'], 'cane-ha-mangiato-uva', "la PDSA, un'importante associazione veterinaria britannica, raccomanda proprio di non attendere, perché le cure funzionano meglio quando sono rapide"),
        de: t('Ihr Hund hat Weintrauben, Rosinen, Sultaninen oder Korinthen gefressen, auch nur wenige Beeren und auch wenn er munter wirkt: Rufen Sie sofort in der Praxis an und warten Sie nicht ab, ob er krank wird.', ['Merck Veterinary Manual'], 'hund-hat-weintrauben-gefressen', 'Warten Sie nicht ab, ob Ihr Hund krank wird. Das gilt auch, wenn er nur wenige Beeren erwischt hat und munter wirkt.', 'ref'),
      },
      {
        en: t('After heat or exercise: heavy panting that will not settle, thick sticky drool, bright red, dark or very pale gums, wobbliness, vomiting or collapse. A dog with heatstroke needs cooling and a vet: start cooling at once.', ['PDSA'], 'heatstroke', 'A dog with heatstroke needs cooling and a vet.', 'ref'),
        it: t('Dopo il caldo o lo sforzo: ansima pesantemente e non si calma, saliva densa e appiccicosa, gengive rosso vivo, scure o molto pallide, barcolla, vomita o collassa. Un cane con un colpo di calore ha bisogno di essere raffreddato e di un veterinario: inizia subito a raffreddarlo.', ['PDSA'], 'heatstroke', 'Un cane con un colpo di calore ha bisogno di essere raffreddato e di un veterinario.', 'ref'),
        de: t('Nach Hitze oder Anstrengung: starkes Hecheln ohne Ruhe, dicker, zäher Speichel, hellrotes, dunkles oder sehr blasses Zahnfleisch, Wackeln, Erbrechen oder Zusammenbruch. Ein Hund mit Hitzschlag braucht Kühlung und einen Tierarzt: Beginnen Sie sofort mit dem Kühlen.', ['PDSA'], 'heatstroke', 'Ein Hund mit Hitzschlag braucht Kühlung und einen Tierarzt.', 'ref'),
      },
    ],
    facts: [
      {
        en: t("A dog's normal rectal temperature is 37.5–39.2 °C (99.5–102.5 °F).", ['MSD Veterinary Manual'], 'dog-fever', 'the normal rectal temperature of a dog is 37.5–39.2 °C'),
        it: t('La temperatura rettale normale del cane adulto è tra 37,5 e 39,2 °C: un cane a 38,5 °C non ha la febbre.', ['MSD Veterinary Manual'], 'cane-febbre', 'la temperatura rettale normale del cane adulto è tra 37,5 e 39,2 °C'),
        de: t('Die normale rektale Temperatur eines Hundes liegt bei 37,5 bis 39,2 °C.', ['MSD Veterinary Manual'], 'hund-fieber', 'eine normale rektale Temperatur von 37,5 bis 39,2 °C'),
      },
      {
        en: t('Most healthy dogs drink about 40 to 60 ml per kilogram of body weight a day, roughly 400 to 600 ml for a 10 kg dog; more than 100 ml per kilogram is considered too much.', ["Cornell's Riney Canine Health Center"], 'dog-drinking-a-lot', 'that means a 10 kg dog normally drinks roughly 400 to 600 ml a day'),
        it: t('Un cane beve circa 40-60 ml di acqua al giorno per ogni chilo di peso; si parla di sete eccessiva quando supera i 100 ml per chilo.', ['Cornell Riney Canine Health Center'], 'cane-beve-tanto', 'un cane beve circa 40-60 ml di acqua al giorno per ogni chilo di peso'),
        de: t('Gesunde Hunde trinken ungefähr 40 bis 60 Milliliter pro Kilogramm Körpergewicht am Tag; ab mehr als 100 Millilitern pro Kilogramm spricht man von krankhaft vermehrtem Trinken.', ['Riney Canine Health Center der Cornell University'], 'hund-trinkt-viel', 'ungefähr 40 bis 60 Milliliter pro Kilogramm Körpergewicht am Tag'),
      },
      {
        en: t('Bones are the most common foreign body stuck in a dog\'s gullet. Typical signs are drooling, gagging, difficulty swallowing and repeated attempts to swallow.', ['MSD Veterinary Manual'], 'dog-ate-chicken-bones', 'bones are the most common foreign body in the oesophagus'),
        it: t("Le ossa sono il corpo estraneo più comune nell'esofago. I segni tipici sono bava, conati, difficoltà a deglutire e tentativi ripetuti di deglutire.", ['MSD Veterinary Manual'], 'cane-ha-mangiato-ossa-di-pollo', 'le ossa sono il corpo estraneo esofageo più comune'),
        de: t('Knochen sind der häufigste Fremdkörper in der Speiseröhre des Hundes. Typische Zeichen sind Speicheln, Würgen, Schluckbeschwerden und wiederholte Schluckversuche.', ['MSD Veterinary Manual'], 'hund-hat-huehnerknochen-gefressen', 'sind Knochen der häufigste Fremdkörper in der Speiseröhre'),
      },
      {
        en: t('The interval between seasons is 4 to 13 months, about 7 months on average.', ['MSD Veterinary Manual'], 'dog-in-heat', 'The MSD Veterinary Manual gives an interval between seasons of 4 to 13 months'),
        it: t('Una cagna va in calore di solito una o due volte all\'anno, con un intervallo da 4 a 13 mesi, in media circa 7.', ['MSD Veterinary Manual'], 'cagna-in-calore', "secondo l'MSD Veterinary Manual va da 4 a 13 mesi, in media circa 7"),
        de: t('Der Abstand zwischen zwei Läufigkeiten liegt zwischen 4 und 13 Monaten, im Durchschnitt bei etwa 7 Monaten.', ['MSD Veterinary Manual'], 'huendin-laeufig', 'Der Abstand zwischen zwei Läufigkeiten liegt laut MSD Veterinary Manual zwischen 4 und 13 Monaten'),
      },
      {
        en: t('Inflammation of the outer ear canal (otitis externa) is the most common ear problem in dogs.', ['MSD Veterinary Manual'], 'dog-ear-infection', "The MSD Veterinary Manual says it's the most common ear problem in dogs."),
        it: t("L'otite esterna, l'infiammazione del condotto uditivo esterno, è il disturbo più comune del condotto uditivo nel cane.", ['MSD Veterinary Manual'], 'cane-otite', 'è il disturbo più comune del condotto uditivo nel cane'),
      },
    ],
    care: [
      {
        en: t('Never take water away from a dog that drinks a lot to control the problem; always leave fresh water out.', ['PDSA'], 'dog-drinking-a-lot', "The PDSA says you should never restrict your dog's water to control the problem."),
        it: t("Non limitare mai l'acqua a un cane che beve tanto per controllare il problema; lascia sempre a disposizione acqua fresca.", ['PDSA'], 'cane-beve-tanto', "La PDSA raccomanda di non limitare mai l'acqua per controllare il problema"),
      },
      {
        en: t("Don't use cotton buds to clean your dog's ears.", ['MSD Veterinary Manual'], 'dog-ear-infection', "No cotton buds. The MSD Veterinary Manual says they shouldn't be used for cleaning"),
        it: t('Niente cotton fioc per pulire le orecchie del cane.', ['MSD Veterinary Manual'], 'cane-otite', "Anche l'MSD Veterinary Manual sconsiglia di usarli."),
      },
      {
        en: t("Don't put home remedies such as vinegar mixtures in your dog's ears: they can make inflammation worse.", ['MSD Veterinary Manual'], 'dog-ear-infection', 'The MSD Veterinary Manual says they can make inflammation worse.'),
        it: t('Niente rimedi casalinghi come aceto, oli o polveri nelle orecchie: vanno evitati i rimedi che irritano.', ['MSD Veterinary Manual'], 'cane-otite', "L'MSD Veterinary Manual consiglia di evitare rimedi casalinghi che irritano."),
        de: t('Keine Hausmittel wie Essigmischungen oder Puder ins Ohr: Von reizenden Hausmitteln wird abgeraten.', ['MSD Veterinary Manual'], 'hund-ohrenentzuendung', 'Das MSD Veterinary Manual rät von reizenden Hausmitteln ab'),
      },
      {
        en: t('Remove any tick you see as soon as possible, to reduce the chance of disease.', ['ESCCAP'], 'dog-tick-removal', 'European parasite experts advise removing any tick you see as soon as possible, to reduce the chance of disease.'),
        it: t('Le zecche trasmettono le infezioni mentre si nutrono, e per molte malattie serve un po\' di tempo: prima togli la zecca, meglio è.', ['ESCCAP Italia'], 'zecca-cane-come-toglierla', 'Ogni ora conta: prima la togli, meglio è.'),
      },
    ],
  },

  cat: {
    key: 'cat',
    name: { en: 'Cats', it: 'Gatti', de: 'Katzen' },
    intro: {
      en: 'Everything this site has on cats in one place: the signs that mean go now, key facts, every health topic and everyday care, each with its source.',
      it: 'Tutto quello che questo sito dice sui gatti in un unico posto: i segni per correre dal veterinario, i fatti chiave, tutti gli argomenti di salute e la cura di ogni giorno, ognuno con la sua fonte.',
      de: 'Alles, was diese Seite über Katzen hat, an einem Ort: die Zeichen für sofort in die Praxis, wichtige Fakten, alle Gesundheitsthemen und die tägliche Pflege, jeweils mit Quelle.',
    },
    mostRead: {
      en: ['cat-straining-litter-box', 'cat-vomiting', 'cat-not-eating'],
      it: ['gatto-non-fa-pipi', 'cat-vomiting', 'cat-not-eating'],
      de: ['katze-blasenentzuendung', 'cat-vomiting', 'katze-frisst-nicht'],
    },
    goNow: [
      {
        en: t('Your cat keeps straining in the tray but passes no urine or only a few drops, especially a male cat. Being unable to pee is a life-threatening emergency: the time from complete blockage to death may be less than 24 to 48 hours.', ['PDSA', 'Cornell Feline Health Center'], 'cat-cystitis-stress', 'The PDSA calls being unable to pee "a life-threatening emergency". The Cornell Feline Health Center says the time from complete blockage to death may be less than 24 to 48 hours.'),
        it: t("Il gatto spinge in lettiera senza risultato, soprattutto se è maschio: può essere un'ostruzione dell'uretra, un'emergenza assoluta. Tra il blocco completo e la morte possono passare meno di 24-48 ore.", ['Cornell Feline Health Center'], 'gatto-stitico', 'Secondo il Cornell Feline Health Center, tra il blocco completo e la morte possono passare meno di 24-48 ore.'),
        de: t('Ihre Katze sitzt in der Toilette und presst, und es kommt kein Urin, vor allem bei Katern: Ein Harnröhrenverschluss ist ein absoluter Notfall. Ohne Behandlung kann eine Katze innerhalb von 24 bis 48 Stunden oder schneller sterben.', ['Cornell Feline Health Center'], 'katze-verstopfung', 'Ohne Behandlung kann eine Katze mit komplett verschlossener Harnröhre innerhalb von 24 bis 48 Stunden oder schneller sterben.', 'ref'),
      },
      {
        en: t('Your cat has chewed, licked or brushed against a lily (Lilium or daylily), including pollen on her fur or a drink from the vase water, even if she looks fine.', ['Pet Poison Helpline'], 'cat-toxic-foods-plants', 'has chewed, licked or brushed against a lily (Lilium or daylily), including pollen on her fur or a drink from the vase water, even if she looks fine', 'ref'),
        it: t("Il gatto ha morso, leccato o sfiorato un giglio (Lilium o emerocallide), anche solo polline sul pelo o acqua del vaso, anche se sembra stare bene.", ['Pet Poison Helpline'], 'alimenti-piante-tossiche-gatto', 'ha morso, leccato o sfiorato un giglio (Lilium o emerocallide), anche solo polline sul pelo o acqua del vaso, anche se sembra stare bene', 'ref'),
        de: t('Ihre Katze hat an einer Lilie (Lilium oder Taglilie) geknabbert, geleckt oder sich daran gerieben, auch nur Pollen im Fell oder ein Schluck Vasenwasser, selbst wenn sie munter wirkt.', ['Pet Poison Helpline'], 'giftige-lebensmittel-pflanzen-katze', 'an einer Lilie (Lilium oder Taglilie) geknabbert, geleckt oder sich daran gerieben hat, auch nur Pollen im Fell oder ein Schluck Vasenwasser, selbst wenn sie munter wirkt', 'ref'),
      },
      {
        en: t('Your cat is breathing with an open mouth, panting or struggling to breathe. Cats normally breathe through their nose; never wait to see if things improve.', ['PDSA'], 'cat-sneezing', 'Cats normally breathe through their nose, so mouth breathing is a sign of real trouble. The PDSA says never wait to see if things improve'),
        it: t('Il gatto respira a bocca aperta, ansima o fa fatica a respirare. Il gatto respira quasi sempre dal naso: respirare con la bocca indica un problema serio. Contatta subito il veterinario.', ['PDSA'], 'gatto-starnutisce', 'ricorda che il gatto respira quasi sempre dal naso: respirare con la bocca indica un problema serio'),
      },
    ],
    facts: [
      {
        en: t('Over 90% of cat flu cases are caused by feline herpesvirus and/or feline calicivirus.', ['International Cat Care'], 'cat-sneezing', 'over 90% of cases are caused by feline herpesvirus'),
        it: t("Oltre il 90% delle infezioni delle vie respiratorie alte del gatto (il \"raffreddore\" del gatto) è causato da due virus: l'herpesvirus felino e il calicivirus felino.", ['International Cat Care'], 'gatto-starnutisce', 'oltre il 90% di queste infezioni è causato da due virus'),
      },
      {
        en: t("Most healthy adult cats pass faeces once or twice a day. Call your vet if your cat hasn't pooped in more than 48 hours, has hard, dry stools or is straining.", ['Ontario Veterinary College'], 'cat-constipation', 'says most healthy adult cats pass faeces once or twice a day'),
        de: t('Hat Ihre Katze seit mehr als 48 Stunden keinen Kot abgesetzt oder presst sie deutlich, rufen Sie die Praxis an.', ['Ontario Veterinary College'], 'katze-verstopfung', 'dann rät das Ontario Veterinary College, die Praxis anzurufen'),
      },
      {
        en: t('Flea allergic dermatitis, a reaction to flea saliva, is one of the most common skin causes of over-grooming.', ['International Cat Care'], 'cat-hair-loss-patches', 'as one of the most common skin causes of over-grooming'),
        it: t("La dermatite allergica da pulci, una reazione alla saliva della pulce, è il problema della pelle più comune tra quelli che portano il gatto a leccarsi troppo.", ['International Cat Care'], 'gatto-perde-pelo-a-ciuffi', 'come il problema della pelle più comune tra quelli che portano il gatto a leccarsi troppo'),
        de: t('Die Flohspeichelallergie, eine Reaktion auf den Speichel von Flöhen, ist eine der häufigsten Hautursachen für übermäßiges Putzen.', ['International Cat Care'], 'katze-verliert-fell', 'eine der häufigsten Hautursachen für übermäßiges Putzen'),
      },
      {
        en: t('You may not see fleas even when they are there: cats often eat fleas while grooming.', ['International Cat Care'], 'cat-hair-loss-patches', 'cats often eat fleas while grooming'),
        it: t('Anche se non vedi pulci, possono esserci: i gatti spesso ingoiano le pulci mentre si puliscono.', ['International Cat Care'], 'gatto-perde-pelo-a-ciuffi', 'i gatti spesso ingoiano le pulci mentre si puliscono'),
        de: t('Vielleicht sehen Sie gar keine Flöhe: Katzen verschlucken Flöhe beim Putzen.', ['International Cat Care'], 'katze-verliert-fell', 'Katzen verschlucken Flöhe beim Putzen, so International Cat Care'),
      },
      {
        en: t('Episodes of stress cystitis often come on quickly and usually settle over 5 to 10 days, but they commonly come back.', ['International Cat Care'], 'cat-cystitis-stress', 'International Cat Care says episodes often come on quickly and usually settle over 5 to 10 days'),
      },
    ],
    care: [
      {
        en: t('Never use a dog flea product on your cat: some contain permethrin or related compounds that can kill cats, and even contact with a recently treated dog can be dangerous.', ['International Cat Care'], 'cat-hair-loss-patches', 'some contain permethrin or related compounds that can kill cats'),
        it: t('Non usare mai sul gatto un antiparassitario per cani: alcuni contengono permetrina o sostanze simili che possono uccidere un gatto, e anche il contatto con un cane appena trattato può essere pericoloso.', ['International Cat Care'], 'gatto-perde-pelo-a-ciuffi', 'contengono permetrina o sostanze simili che possono uccidere un gatto'),
        de: t('Verwenden Sie niemals ein Flohmittel für Hunde bei Ihrer Katze: Manche enthalten Permethrin oder verwandte Stoffe, die Katzen töten können, und schon der Kontakt mit einem frisch behandelten Hund kann gefährlich sein.', ['International Cat Care'], 'katze-verliert-fell', 'manche Permethrin oder verwandte Stoffe enthalten, die Katzen töten können'),
      },
      {
        en: t('95% of fleas are in the home, so treat your house as well as your cat.', ['International Cat Care'], 'cat-hair-loss-patches', '95% of fleas are in the home'),
        it: t('Se ci sono pulci, tratta tutti gli animali di casa e anche la casa: la maggior parte delle pulci vive nell\'ambiente.', ['International Cat Care'], 'gatto-perde-pelo-a-ciuffi', "perché la maggior parte delle pulci vive nell'ambiente"),
        de: t('95 % der Flöhe befinden sich in der Wohnung: Behandeln Sie die Wohnung mit, nicht nur die Katze.', ['International Cat Care'], 'katze-verliert-fell', '95 % der Flöhe in der Wohnung'),
      },
      {
        en: t('Put water in several bowls in different rooms, away from food and trays; shallow ceramic bowls, fountains or flavoured water can help.', ['International Cat Care'], 'cat-cystitis-stress', 'International Cat Care suggests shallow ceramic bowls, fountains or flavoured water.'),
      },
      {
        it: t('Lettiera pulita e facile da raggiungere: togli feci e urina almeno una volta al giorno e tieni almeno una lettiera per gatto più una.', ['Ontario Veterinary College'], 'gatto-stitico', "l'Ontario Veterinary College consiglia di togliere feci e urina almeno una volta al giorno"),
      },
      {
        en: t('Never use a human enema on a cat: phosphate-containing enemas can cause severe, potentially life-threatening salt imbalances.', ['MSD Veterinary Manual'], 'cat-constipation', 'phosphate-containing enemas must be avoided in cats'),
      },
    ],
  },

  rabbit: {
    key: 'rabbit',
    name: { en: 'Rabbits', it: 'Conigli', de: 'Kaninchen' },
    intro: {
      en: 'Everything this site has on rabbits in one place: the signs that mean go now, key facts, every health topic and everyday care, each with its source.',
      it: 'Tutto quello che questo sito dice sui conigli in un unico posto: i segni per correre dal veterinario, i fatti chiave, tutti gli argomenti di salute e la cura di ogni giorno, ognuno con la sua fonte.',
      de: 'Alles, was diese Seite über Kaninchen hat, an einem Ort: die Zeichen für sofort in die Praxis, wichtige Fakten, alle Gesundheitsthemen und die tägliche Pflege, jeweils mit Quelle.',
    },
    mostRead: {
      en: ['rabbit-not-eating', 'rabbit-overgrown-teeth', 'rabbit-diarrhoea'],
      it: ['rabbit-not-eating', 'coniglio-denti-lunghi', 'coniglio-diarrea'],
      de: ['rabbit-not-eating', 'kaninchen-zaehne', 'kaninchen-durchfall'],
    },
    goNow: [
      {
        en: t('Your rabbit has stopped eating or passed no droppings. Contact your vet now; do not wait for a set number of hours. 12 hours without food or droppings is the outer limit, not a time to wait for.', ['Rabbit Welfare Association', 'House Rabbit Society'], 'rabbit-not-eating', 'The Rabbit Welfare Association says to contact your vet now; the House Rabbit Society treats 12 hours without food or droppings as an emergency'),
        it: t('Il coniglio ha smesso di mangiare o non fa feci. Contatta subito il veterinario, senza aspettare un certo numero di ore: 12 ore senza cibo o senza feci sono il limite massimo, non un tempo da aspettare.', ['Rabbit Welfare Association', 'House Rabbit Society'], 'rabbit-not-eating', "La Rabbit Welfare Association dice di contattare subito il veterinario; la House Rabbit Society considera un'emergenza 12 ore senza cibo o senza feci"),
        de: t('Ihr Kaninchen hat aufgehört zu fressen oder setzt keinen Kot ab. Wenden Sie sich sofort an die Praxis und warten Sie keine Stundenzahl ab: 12 Stunden ohne Futter oder Kot sind die äußerste Grenze, keine Wartezeit.', ['Rabbit Welfare Association', 'House Rabbit Society'], 'rabbit-not-eating', 'Die Rabbit Welfare Association rät, sich sofort an die Tierarztpraxis zu wenden; die House Rabbit Society wertet 12 Stunden ohne Futter oder Kot als Notfall'),
      },
      {
        en: t('Watery or shapeless droppings and no normal hard pellets, especially with not eating, a bloated belly or signs of pain such as sitting hunched. Never wait to see if it improves.', ['PDSA'], 'rabbit-diarrhoea', 'you should never wait to see if it improves'),
        it: t('Feci liquide e niente più palline dure, soprattutto se non mangia, ha la pancia gonfia o mostra dolore, per esempio stando ingobbito. Non aspettare mai di vedere se migliora.', ['PDSA'], 'coniglio-diarrea', 'non bisogna mai aspettare di vedere se migliora da sola'),
        de: t('Wässriger oder breiiger Kot ohne normale runde Köttel, vor allem wenn Ihr Kaninchen nicht frisst, zusammengekauert sitzt oder einen aufgeblähten Bauch hat. Nie abwarten, ob es besser wird.', ['PDSA'], 'kaninchen-durchfall', 'nie abzuwarten, ob es besser wird'),
      },
      {
        en: t('You see fly eggs or even one maggot around its bottom (flystrike). Call your vet now; do not try to remove the maggots yourself or dunk your rabbit in water.', ['PDSA'], 'rabbit-diarrhoea', 'If you see even one maggot, call your vet now for an emergency appointment.'),
        it: t("Vedi uova di mosca o anche una sola larva intorno al sedere (miasi). Chiama subito il veterinario; non provare a togliere le larve da solo e non immergere il coniglio nell'acqua.", ['PDSA'], 'coniglio-diarrea', "Se vedi anche una sola larva, chiama subito il veterinario per un'emergenza."),
      },
    ],
    facts: [
      {
        en: t("All of a rabbit's teeth, front and back, keep growing throughout its life. Chewing, especially chewing hay, normally wears them down as fast as they grow.", ['MSD Veterinary Manual'], 'rabbit-overgrown-teeth', 'Chewing, especially chewing hay, normally wears them down as fast as they grow.'),
        it: t('Tutti i denti del coniglio, sia gli incisivi davanti sia i molari e premolari dietro, crescono per tutta la vita. Normalmente la masticazione li consuma alla stessa velocità con cui crescono.', ['Merck Veterinary Manual'], 'coniglio-denti-lunghi', 'sia gli incisivi davanti sia i molari e premolari dietro, crescono per tutta la vita'),
        de: t('Kaninchenzähne wachsen ein Leben lang nach, die Schneidezähne vorne ebenso wie die Backenzähne. Normalerweise werden sie beim Kauen im gleichen Maß abgenutzt, wie sie nachwachsen.', ['MSD Veterinary Manual'], 'kaninchen-zaehne', 'Kaninchenzähne wachsen ein Leben lang nach', 'ref'),
      },
      {
        en: t("A diet too low in fibre is the main cause of dental disease. Rabbits fed mainly on pellets instead of hay can develop overgrown teeth, because pellets don't wear the teeth down as well.", ['PDSA', 'MSD Veterinary Manual'], 'rabbit-overgrown-teeth', 'The PDSA names a low-fibre diet as the main cause of dental disease.'),
        it: t('Una dieta povera di fibre è la causa principale dei denti troppo lunghi. I conigli alimentati soprattutto con pellet possono sviluppare denti troppo lunghi, perché i pellet non consumano i denti come il fieno.', ['PDSA', 'Merck Veterinary Manual'], 'coniglio-denti-lunghi', 'perché i pellet non consumano i denti come il fieno'),
        de: t('Eine pelletlastige Ernährung ist ein Risiko für zu lange Zähne: Heu muss lange gekaut werden und nutzt die Zähne gut ab, Pellets und Körnerfutter werden dagegen schnell zerkleinert.', ['MSD Veterinary Manual'], 'kaninchen-zaehne', 'Das MSD Veterinary Manual nennt eine pelletlastige Ernährung als Risiko für zu lange Zähne.'),
      },
      {
        en: t("A rabbit that won't eat and has no droppings is an emergency: it should see a vet within the shortest possible time, and waiting until tomorrow will be too late.", ['Rabbit Welfare Association'], 'rabbit-overgrown-teeth', "A rabbit that won't eat and has no droppings is an emergency"),
        it: t("Un coniglio che non mangia e non fa palline è un'emergenza: deve vedere un veterinario il prima possibile, e aspettare il giorno dopo è troppo tardi.", ['Rabbit Welfare Association'], 'coniglio-denti-lunghi', "Un coniglio che non mangia e non fa palline è un'emergenza"),
        de: t('Ein Kaninchen, das nicht frisst und keinen Kot absetzt, ist ein Notfall: Es muss so schnell wie möglich in die Praxis, bis morgen zu warten ist zu spät.', ['Rabbit Welfare Association'], 'kaninchen-zaehne', 'Ein Kaninchen, das nicht frisst und keinen Kot absetzt, ist ein Notfall'),
      },
      {
        en: t('Soft, sticky droppings are often caecotrophs, a normal part of digestion that rabbits usually eat, and they are easily mistaken for diarrhoea. A rabbit only stops eating them when something is wrong, so book a vet visit.', ['PDSA'], 'rabbit-diarrhoea', 'The PDSA notes that caecotrophs are easily mistaken for diarrhoea.'),
        it: t("I ciecotrofi, le feci morbide e appiccicose che il coniglio di solito mangia, vengono facilmente scambiati per diarrea. Il coniglio smette di mangiarli solo se c'è qualcosa che non va.", ['PDSA'], 'coniglio-diarrea', 'i ciecotrofi vengono facilmente scambiati per diarrea'),
        de: t('Liegen gebliebener Blinddarmkot ist nicht lebensbedrohlich, echter Durchfall dagegen schon, weil das Kaninchen rasch Wasser und Salze verliert.', ['Textbook of Rabbit Medicine'], 'kaninchen-durchfall', 'Laut dem Lehrbuch Textbook of Rabbit Medicine ist liegen gebliebener Blinddarmkot nicht lebensbedrohlich.'),
      },
      {
        en: t('Inherited misalignment of the teeth (malocclusion) is one of the most common inherited problems in rabbits; it can show up as early as 3 to 8 weeks of age.', ['MSD Veterinary Manual'], 'rabbit-overgrown-teeth', 'The MSD Veterinary Manual calls it one of the most common inherited problems in rabbits.'),
        it: t('La malocclusione ereditaria è uno dei problemi ereditari più comuni del coniglio: i denti superiori e inferiori non combaciano. Può comparire già a 3-8 settimane di età.', ['Merck Veterinary Manual'], 'coniglio-denti-lunghi', 'uno dei problemi ereditari più comuni del coniglio'),
        de: t('Ein schiefer Biss (Malokklusion) ist eine der häufigsten erblichen Erkrankungen beim Kaninchen.', ['MSD Veterinary Manual'], 'kaninchen-zaehne', 'ist nach dem MSD Veterinary Manual eine der häufigsten erblichen Erkrankungen beim Kaninchen'),
      },
    ],
    care: [
      {
        en: t('Every day: hay or grass, ideally unlimited and at least a bundle as big as your rabbit; about one adult-sized handful of greens twice a day; just one tablespoon of nuggets; no muesli-style mixes; fresh water at all times.', ['PDSA'], 'rabbit-overgrown-teeth', 'The PDSA recommends, every day:'),
        it: t('Ogni giorno: fieno o erba a volontà, almeno un mucchio grande quanto il coniglio; una manciata da adulto di verdure due volte al giorno; solo un cucchiaio di pellet; niente muesli; acqua fresca sempre disponibile.', ['PDSA'], 'coniglio-denti-lunghi', 'La PDSA raccomanda ogni giorno:'),
      },
      {
        en: t('If you need to change the diet, do it gradually over 2 to 4 weeks.', ['PDSA'], 'rabbit-overgrown-teeth', 'the PDSA advises doing it gradually over 2 to 4 weeks'),
        it: t('Se devi cambiare alimentazione, fallo gradualmente, in 2-4 settimane.', ['PDSA'], 'coniglio-denti-lunghi', 'la PDSA consiglia di farlo gradualmente, in 2-4 settimane'),
      },
      {
        en: t('Check the front teeth at least once a week, and watch that your rabbit is eating, passing normal droppings and not losing weight.', ['PDSA'], 'rabbit-overgrown-teeth', 'check the front teeth at least once a week, as the PDSA suggests'),
        it: t('Guarda i denti davanti almeno una volta alla settimana, e controlla che il coniglio mangi, faccia palline normali e non perda peso.', ['PDSA'], 'coniglio-denti-lunghi', 'almeno una volta alla settimana, come suggerisce la PDSA'),
        de: t('Schauen Sie sich die Schneidezähne Ihres Kaninchens mindestens einmal pro Woche selbst an.', ['PDSA'], 'kaninchen-zaehne', 'Schauen Sie sich die Schneidezähne laut PDSA mindestens einmal pro Woche selbst an.'),
      },
      {
        en: t('Remove soiled litter and wet bedding at least once a day, and check every day that the bottom is clean and dry.', ['PDSA'], 'rabbit-diarrhoea', 'The PDSA also advises removing soiled litter and wet bedding at least once a day.'),
        it: t('Togli ogni giorno la lettiera sporca e bagnata, e controlla ogni giorno che il sedere sia pulito e asciutto.', ['PDSA'], 'coniglio-diarrea', 'La PDSA consiglia anche di togliere ogni giorno la lettiera sporca e bagnata.'),
      },
      {
        en: t("Don't give any medicine your vet hasn't prescribed, including human painkillers or leftover antibiotics: some antibiotics given by mouth can trigger serious gut disease in rabbits.", ['MSD Veterinary Manual'], 'rabbit-overgrown-teeth', 'some antibiotics given by mouth can trigger serious gut disease in rabbits'),
        it: t('Non dare farmaci per uso umano o per altri animali, né antibiotici avanzati: alcuni antibiotici dati per bocca possono scatenare nel coniglio una grave malattia intestinale.', ['Merck Veterinary Manual'], 'coniglio-diarrea', 'alcuni antibiotici dati per bocca possono scatenare nel coniglio una grave malattia intestinale'),
        de: t('Geben Sie nur, was die Praxis verordnet. Übrig gebliebene Antibiotika anderer Tiere sind tabu: Manche davon können bei Kaninchen lebensbedrohlichen Durchfall auslösen.', ['MSD Veterinary Manual'], 'kaninchen-zaehne', 'können manche davon bei Kaninchen lebensbedrohlichen Durchfall auslösen'),
      },
    ],
  },

  // Species added in October 2026. Their pages list every health topic (most urgent first); go-now signs,
  // key facts and care basics show once sourced items are added here, under the same rules as above.
  // `mostRead` is the card's "Start with" list; the card tops it up with the most urgent topics.
  'guinea-pig': {
    key: 'guinea-pig',
    name: { en: 'Guinea pigs', it: 'Cavie', de: 'Meerschweinchen' },
    intro: {
      en: 'Everything this site has on guinea pigs in one place: every health topic, the most urgent first.',
      it: 'Tutto quello che questo sito dice sulle cavie in un unico posto: tutti gli argomenti di salute, prima i più urgenti.',
      de: 'Alles, was diese Seite über Meerschweinchen hat, an einem Ort: alle Gesundheitsthemen, die dringendsten zuerst.',
    },
    mostRead: {
      en: ['guinea-pig-not-eating', GUINEA_PIG_ARTICLE.en],
      it: ['cavia-non-mangia', GUINEA_PIG_ARTICLE.it],
      de: ['meerschweinchen-frisst-nicht', GUINEA_PIG_ARTICLE.de],
    },
    goNow: [
      {
        en: t('Your guinea pig has stopped eating: a guinea pig that stops eating is at risk of a life-threatening problem called gut stasis.', ['PDSA'], 'guinea-pig-not-eating', 'The PDSA warns that a guinea pig that stops eating is at risk of a life-threatening problem called gut stasis'),
        it: t('La cavia ha smesso di mangiare: una cavia che smette di mangiare rischia un problema potenzialmente mortale, la stasi intestinale.', ['PDSA'], 'cavia-non-mangia', 'avverte che una cavia che smette di mangiare rischia un problema potenzialmente mortale, la stasi intestinale'),
        de: t('Ihr Meerschweinchen frisst nicht mehr: Futterverweigerung ist immer ein Notfall.', ['TVT'], 'meerschweinchen-frisst-nicht', 'Futterverweigerung stellt immer einen Notfall dar'),
      },
      {
        en: t('Its eating or drinking changes, or its droppings get fewer or stop: consult your vet immediately, because it could be seriously ill. Do not wait for a set number of hours.', ['RSPCA'], 'guinea-pig-not-eating', "The RSPCA advises consulting your vet immediately if your guinea pig's eating or drinking changes, or its droppings get fewer or stop"),
        it: t('Cambia il modo in cui mangia o beve, o le palline diminuiscono o spariscono: consulta subito il veterinario, potrebbe essere gravemente malata. Non aspettare un certo numero di ore.', ['RSPCA'], 'cavia-non-mangia', 'La RSPCA raccomanda di consultare subito il veterinario se cambia il modo in cui la cavia mangia o beve, o se le palline diminuiscono o spariscono'),
        de: t('Das Fress- oder Trinkverhalten ändert sich, oder es kommt weniger oder gar kein Kot mehr: Fragen Sie sofort die Tierarztpraxis, das Tier könnte ernsthaft krank sein. Warten Sie keine bestimmte Stundenzahl ab.', ['RSPCA'], 'meerschweinchen-frisst-nicht', 'Die britische Tierschutzorganisation RSPCA rät, sofort die Tierarztpraxis zu fragen, wenn sich das Fress- oder Trinkverhalten ändert oder weniger oder gar kein Kot mehr kommt'),
      },
    ],
    facts: [
      {
        en: t('Unusually for mammals, guinea pigs cannot make their own vitamin C, so it has to come from their food.', ['PDSA'], 'guinea-pig-vitamin-c', 'Unusually for mammals, guinea pigs cannot produce vitamin C, the PDSA explains, so they need it from their food'),
        it: t('Le cavie, cosa insolita per un mammifero, non possono produrre la vitamina C e devono assumerla con il cibo.', ['PDSA'], 'cavia-vitamina-c', 'spiega che le cavie, cosa insolita per un mammifero, non possono produrre la vitamina C e devono assumerla con il cibo'),
        de: t('Meerschweinchen können Vitamin C nicht selbst herstellen und leiden daher häufig an Skorbut.', ['TVT'], 'meerschweinchen-vitamin-c', 'Meerschweinchen können Vitamin C nicht selbst herstellen und leiden daher häufig an Skorbut'),
      },
      {
        en: t('Pneumonia is a leading cause of death in guinea pigs, especially young ones, and is usually caused by bacteria.', ['MSD Veterinary Manual'], 'guinea-pig-sneezing', 'The MSD Veterinary Manual says pneumonia is a leading cause of death in guinea pigs, especially young ones, and is usually caused by bacteria'),
        it: t('La polmonite è una delle principali cause di morte nelle cavie, soprattutto in quelle giovani, ed è di solito causata da batteri.', ['MSD Veterinary Manual'], 'cavia-starnutisce', 'spiega che la polmonite è una delle principali cause di morte nelle cavie, soprattutto in quelle giovani'),
        de: t('Die Lungenentzündung ist eine der häufigsten Todesursachen bei Meerschweinchen, vor allem bei jungen Tieren; meist stecken Bakterien dahinter.', ['MSD Veterinary Manual'], 'meerschweinchen-niest', 'Das MSD Veterinary Manual nennt die Lungenentzündung eine der häufigsten Todesursachen bei Meerschweinchen'),
      },
      {
        en: t("Guinea pigs' teeth keep growing throughout their lives. If they are not worn down, they can grow too long and cut the gums, cheeks and tongue.", ['PDSA'], 'guinea-pig-not-eating', "The PDSA explains that guinea pigs' teeth keep growing throughout their lives"),
        it: t('I denti delle cavie crescono per tutta la vita: se non si consumano, possono allungarsi troppo e ferire gengive, guance e lingua.', ['PDSA'], 'cavia-non-mangia', 'La PDSA spiega che i denti delle cavie crescono per tutta la vita.'),
        de: t('Meerschweinchenzähne wachsen ein Leben lang nach und nutzen sich vor allem beim Kauen von rohfaserhaltigem Grundfutter ab.', ['TVT'], 'meerschweinchen-frisst-nicht', 'Laut TVT nutzen sich die lebenslang wachsenden Zähne vor allem beim Kauen von rohfaserhaltigem Grundfutter ab'),
      },
    ],
    care: [],
  },

  ferret: {
    key: 'ferret',
    name: { en: 'Ferrets', it: 'Furetti', de: 'Frettchen' },
    intro: {
      en: 'Everything this site has on ferrets in one place: every health topic, the most urgent first.',
      it: 'Tutto quello che questo sito dice sui furetti in un unico posto: tutti gli argomenti di salute, prima i più urgenti.',
      de: 'Alles, was diese Seite über Frettchen hat, an einem Ort: alle Gesundheitsthemen, die dringendsten zuerst.',
    },
    mostRead: { en: [], it: [], de: [] },
    goNow: [],
    facts: [],
    care: [],
  },

  horse: {
    key: 'horse',
    name: { en: 'Horses', it: 'Cavalli', de: 'Pferde' },
    intro: {
      en: 'Everything this site has on horses in one place: every health topic, the most urgent first.',
      it: 'Tutto quello che questo sito dice sui cavalli in un unico posto: tutti gli argomenti di salute, prima i più urgenti.',
      de: 'Alles, was diese Seite über Pferde hat, an einem Ort: alle Gesundheitsthemen, die dringendsten zuerst.',
    },
    mostRead: { en: [], it: [], de: [] },
    goNow: [],
    facts: [],
    care: [],
  },

  bird: {
    key: 'bird',
    name: { en: 'Birds', it: 'Uccelli', de: 'Vögel' },
    intro: {
      en: 'Everything this site has on pet birds in one place: every health topic, the most urgent first.',
      it: 'Tutto quello che questo sito dice sugli uccelli da compagnia in un unico posto: tutti gli argomenti di salute, prima i più urgenti.',
      de: 'Alles, was diese Seite über Ziervögel hat, an einem Ort: alle Gesundheitsthemen, die dringendsten zuerst.',
    },
    mostRead: { en: [], it: [], de: [] },
    goNow: [],
    facts: [],
    care: [],
  },

  reptile: {
    key: 'reptile',
    name: { en: 'Reptiles', it: 'Rettili', de: 'Reptilien' },
    intro: {
      en: 'Everything this site has on reptiles in one place: every health topic, the most urgent first.',
      it: 'Tutto quello che questo sito dice sui rettili in un unico posto: tutti gli argomenti di salute, prima i più urgenti.',
      de: 'Alles, was diese Seite über Reptilien hat, an einem Ort: alle Gesundheitsthemen, die dringendsten zuerst.',
    },
    mostRead: { en: [], it: [], de: [] },
    goNow: [],
    facts: [],
    care: [],
  },
};

/**
 * Articles filed under another species that also cover this one: they are listed among its health
 * topics and counted on its card, besides the articles with that species.
 */
export const SHARED_TOPICS: Partial<Record<SpeciesKey, Record<Lang, string[]>>> = {
  'guinea-pig': { en: [GUINEA_PIG_ARTICLE.en], it: [GUINEA_PIG_ARTICLE.it], de: [GUINEA_PIG_ARTICLE.de] },
};

/** All article slugs this file points to, per language (used by the checks). */
export function referencedSlugs(lang: Lang): string[] {
  const out = new Set<string>([GUINEA_PIG_ARTICLE[lang]]);
  for (const s of Object.values(SHARED_TOPICS)) s?.[lang].forEach((x) => out.add(x));
  for (const p of Object.values(PROFILES)) {
    p.mostRead[lang].forEach((s) => out.add(s));
    for (const it of [...p.goNow, ...p.facts, ...p.care]) { const c = it[lang]; if (c) out.add(c.slug); }
  }
  return [...out];
}

export const GUIDE = {
  en: {
    title: 'Animals A–Z', desc: 'Fact sheets for the animals people keep, with the health topics for each, from veterinary sources. Every fact names its source.',
    intro: 'Fact sheets for the animals people keep, and the health topics for each: the signs that mean go now, common problems and good care. Every fact names its source.',
    find: 'Find an animal', findPh: 'Dog, hamster, budgie…', none: 'No animal matches “{q}”. Try another name, or search all articles below.', shown: '{n} of {t} animals shown',
    // A–Z fact sheets
    lexH: 'Fact sheets', lexCount: (n: number) => (n === 1 ? '1 animal' : `${n} animals`), view: 'View', viewAz: 'A–Z', viewGroups: 'By group', letters: 'Jump to a letter',
    // health hubs: one card per species with articles
    hubsH: 'Health topics by animal', hubsLead: 'Every health article for each animal, the most urgent first, plus go-now signs and care basics where our articles give a source for them.',
    cardParts: { goNow: 'go-now signs', topics: 'health topics', facts: 'key facts', care: 'care' }, startWith: 'Start with', soon: 'Coming soon',
    searchH: 'Search all articles', az: 'All articles, A to Z',
    stripH: 'What the animal pages give you',
    strip: [['Go-now signs', 'The signs that mean go to a vet now, at the top of the page.'], ['Fact sheet', 'Lifespan, size, diet and housing at a glance, each with its source.'], ['Health topics', 'Every article for that animal, emergencies first.'], ['Care basics', 'Everyday care, sourced like everything else.'], ['Health booklet', 'Keep vaccinations, medications and your vet\'s number on your phone.']],
    // animal page
    goNowH: 'Go now', goNowLead: 'Go to a vet now, and call ahead, if you see any of these.', emergencyLink: 'All emergency signs', factsH: 'Key facts', topicsH: 'Health topics', careH: 'Care basics',
    source: 'Source', read: 'Read', topicsLead: '{n} articles, the most urgent first.', topicsLeadOne: '1 article.', topicsNone: 'We have no health articles on this animal yet. If you are worried, call your vet.',
    bookletH: 'Keep your animal\'s health in one place', bookletP: 'Vaccinations, medications, microchip and your vet\'s number in one booklet, on your phone. Free, and it stays on your device.', bookletCta: 'Open the health booklet', otherH: 'Other animals', guide: 'Animals A–Z',
    urgency: { emergency: 'Go now', today: 'See a vet today', 'this-week': 'Book a visit this week', routine: 'Watch and ask at the next visit' },
    emergencyHref: '/emergency', booklet: '/passport',
  },
  it: {
    title: 'Animali dalla A alla Z', desc: 'Schede degli animali che teniamo in casa, con gli argomenti di salute per ognuno, da fonti veterinarie. Ogni fatto indica la sua fonte.',
    intro: 'Le schede degli animali che teniamo in casa e gli argomenti di salute per ognuno: i segni per correre dal veterinario, i problemi più comuni e la cura giusta. Ogni fatto indica la sua fonte.',
    find: 'Trova un animale', findPh: 'Cane, criceto, cocorita…', none: 'Nessun animale corrisponde a “{q}”. Prova un altro nome o cerca tra tutti gli articoli qui sotto.', shown: '{n} animali su {t}',
    lexH: 'Schede', lexCount: (n: number) => (n === 1 ? '1 animale' : `${n} animali`), view: 'Vista', viewAz: 'A–Z', viewGroups: 'Per gruppo', letters: 'Vai alla lettera',
    hubsH: 'Salute per animale', hubsLead: 'Tutti gli articoli di salute per ogni animale, prima i più urgenti, più i segni per correre dal veterinario e la cura di base dove i nostri articoli ne indicano la fonte.',
    cardParts: { goNow: 'segni per correre dal veterinario', topics: 'argomenti di salute', facts: 'fatti chiave', care: 'cura' }, startWith: 'Per iniziare', soon: 'In arrivo',
    searchH: 'Cerca in tutti gli articoli', az: 'Tutti gli articoli, dalla A alla Z',
    stripH: 'Cosa trovi nelle pagine degli animali',
    strip: [['Segni per correre dal veterinario', 'I segni per andare subito dal veterinario, in cima alla pagina.'], ['Scheda', 'Durata della vita, taglia, alimentazione e alloggio a colpo d\'occhio, ognuno con la sua fonte.'], ['Argomenti di salute', 'Tutti gli articoli su quell\'animale, prima le emergenze.'], ['Cura di base', 'La cura di ogni giorno, con le fonti come tutto il resto.'], ['Libretto sanitario', 'Vaccinazioni, farmaci e il numero del veterinario sul telefono.']],
    goNowH: 'Vai subito', goNowLead: 'Vai subito dal veterinario, telefonando prima, se vedi uno di questi segni.', emergencyLink: 'Tutti i segni di emergenza', factsH: 'Fatti chiave', topicsH: 'Argomenti di salute', careH: 'Cura di base',
    source: 'Fonte', read: 'Leggi', topicsLead: '{n} articoli, prima i più urgenti.', topicsLeadOne: '1 articolo.', topicsNone: 'Non abbiamo ancora articoli di salute su questo animale. Se sei preoccupato, chiama il veterinario.',
    bookletH: 'La salute del tuo animale in un unico posto', bookletP: 'Vaccinazioni, farmaci, microchip e il numero del veterinario in un solo libretto, sul telefono. Gratis, e resta sul tuo dispositivo.', bookletCta: 'Apri il libretto sanitario', otherH: 'Altri animali', guide: 'Animali dalla A alla Z',
    urgency: { emergency: 'Vai subito', today: 'Dal veterinario oggi', 'this-week': 'Prenota una visita questa settimana', routine: 'Osserva e chiedi alla prossima visita' },
    emergencyHref: '/it/emergency', booklet: '/it/passport',
  },
  de: {
    title: 'Tierlexikon', desc: 'Steckbriefe der Tiere, die Menschen halten, mit den Gesundheitsthemen zu jedem Tier, aus tierärztlichen Quellen. Jeder Fakt nennt seine Quelle.',
    intro: 'Steckbriefe der Tiere, die Menschen halten, und die Gesundheitsthemen zu jedem Tier: die Zeichen für sofort in die Praxis, häufige Probleme und gute Pflege. Jeder Fakt nennt seine Quelle.',
    find: 'Tier finden', findPh: 'Hund, Hamster, Wellensittich…', none: 'Kein Tier passt zu „{q}“. Versuchen Sie einen anderen Namen oder durchsuchen Sie unten alle Artikel.', shown: '{n} von {t} Tieren',
    lexH: 'Steckbriefe', lexCount: (n: number) => (n === 1 ? '1 Tier' : `${n} Tiere`), view: 'Ansicht', viewAz: 'A–Z', viewGroups: 'Nach Gruppe', letters: 'Zum Buchstaben springen',
    hubsH: 'Gesundheit nach Tierart', hubsLead: 'Alle Gesundheitsartikel je Tier, die dringendsten zuerst, dazu Notfallzeichen und Pflege-Grundlagen, wo unsere Artikel eine Quelle dafür nennen.',
    cardParts: { goNow: 'Notfallzeichen', topics: 'Gesundheitsthemen', facts: 'wichtige Fakten', care: 'Pflege' }, startWith: 'Zum Einstieg', soon: 'Demnächst',
    searchH: 'Alle Artikel durchsuchen', az: 'Alle Artikel von A bis Z',
    stripH: 'Was die Tierseiten bieten',
    strip: [['Notfallzeichen', 'Die Zeichen für sofort in die Praxis, ganz oben auf der Seite.'], ['Steckbrief', 'Lebenserwartung, Größe, Ernährung und Haltung auf einen Blick, jeweils mit Quelle.'], ['Gesundheitsthemen', 'Alle Artikel zu diesem Tier, Notfälle zuerst.'], ['Pflege-Grundlagen', 'Die tägliche Pflege, mit Quellen wie alles andere.'], ['Heimtierpass', 'Impfungen, Medikamente und die Nummer Ihrer Praxis auf dem Handy.']],
    goNowH: 'Sofort in die Praxis', goNowLead: 'Fahren Sie sofort in die Praxis und rufen Sie vorher an, wenn Sie eines dieser Zeichen sehen.', emergencyLink: 'Alle Notfallzeichen', factsH: 'Wichtige Fakten', topicsH: 'Gesundheitsthemen', careH: 'Pflege-Grundlagen',
    source: 'Quelle', read: 'Lesen', topicsLead: '{n} Artikel, die dringendsten zuerst.', topicsLeadOne: '1 Artikel.', topicsNone: 'Zu diesem Tier haben wir noch keine Gesundheitsartikel. Wenn Sie sich Sorgen machen, rufen Sie Ihre Praxis an.',
    bookletH: 'Die Gesundheit Ihres Tieres an einem Ort', bookletP: 'Impfungen, Medikamente, Mikrochip und die Nummer Ihrer Praxis in einem Pass, auf dem Handy. Kostenlos, und er bleibt auf Ihrem Gerät.', bookletCta: 'Heimtierpass öffnen', otherH: 'Andere Tiere', guide: 'Tierlexikon',
    urgency: { emergency: 'Sofort in die Praxis', today: 'Heute in die Praxis', 'this-week': 'Diese Woche einen Termin', routine: 'Beobachten, beim nächsten Besuch fragen' },
    emergencyHref: '/de/emergency', booklet: '/de/passport',
  },
} as const;

/** Extra names the find-an-animal filter accepts, per species card. */
export const ALIASES: Record<SpeciesKey, string> = {
  dog: 'dog dogs puppy puppies cane cani cucciolo hund hunde welpe',
  cat: 'cat cats kitten kittens gatto gatti gattino katze katzen kater kitten',
  rabbit: 'rabbit rabbits bunny coniglio conigli kaninchen hase',
  'guinea-pig': 'guinea pig guinea pigs cavy cavia cavie porcellino porcellini meerschweinchen',
  ferret: 'ferret ferrets furetto furetti frettchen',
  horse: 'horse horses pony donkey cavallo cavalli asino pferd pferde pony esel',
  bird: 'bird birds parrot budgie canary cockatiel uccello uccelli pappagallo cocorita canarino vogel vögel sittich papagei wellensittich kanarienvogel',
  reptile: 'reptile reptiles tortoise turtle lizard snake gecko rettile rettili tartaruga lucertola serpente geco reptil reptilien schildkröte eidechse schlange gecko',
};
