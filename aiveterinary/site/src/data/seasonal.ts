/**
 * Seasonal alerts: short warnings that change with the month and the country, shown on the home page
 * ("This month") and on /seasonal (+ /it, /de).
 *
 * CONTENT RULE: every alert paraphrases its references and adds no facts of its own. Timing that differs
 * by region is only stated the way the source states it ("in Tuscany …", "in southern Europe …").
 * No doses and no product names. Sources were read on the date in SEASONAL_CHECKED.
 *
 *   months     1–12, the months in which the alert is shown
 *   countries  'it' (Italy), 'de-at-ch' (Germany, Austria, Switzerland) or 'all' (shown for every country)
 *   except     countries where an 'all' alert is replaced by a country-specific one
 *   species    keys used across the site (src/lib/animals-i18n.ts)
 *   level      'danger' (can be life-threatening) or 'caution'
 *   article    per language, the slug of our article (src/content/animals/<lang>/<slug>.md, EN at the root)
 *   tool       optional site tool path without language prefix (e.g. '/chocolate')
 *
 * Checked by `node scripts/check-seasonal.mjs` (part of `npm run build`).
 */
export type Lang = 'en' | 'it' | 'de';
export type Country = 'it' | 'de-at-ch' | 'all';
export type SeasonalLevel = 'danger' | 'caution';
export type SeasonalSpecies = 'dog' | 'cat' | 'rabbit' | 'guinea-pig' | 'ferret' | 'horse' | 'bird' | 'reptile';
export interface SeasonalAlert {
  id: string;
  months: number[];
  countries: Country[];
  except?: Country[];
  species: SeasonalSpecies[];
  level: SeasonalLevel;
  title: Record<Lang, string>;
  text: Record<Lang, string>;
  article?: Partial<Record<Lang, string>>;
  tool?: string;
  references: { title: string; url: string }[];
}

export const SEASONAL_CHECKED = '2026-10-25';
export const COUNTRIES: Country[] = ['it', 'de-at-ch', 'all'];
export const COUNTRY_OF_LANG: Record<Lang, Country> = { en: 'all', it: 'it', de: 'de-at-ch' };

/** Is this alert shown for the chosen country? An 'all' alert shows everywhere except where replaced. */
export const showsIn = (a: SeasonalAlert, c: Country) =>
  a.countries.includes(c) || (a.countries.includes('all') && !(a.except ?? []).includes(c));

const PDSA_WINTER = { title: 'PDSA: Winter advice to keep your pet safe through the cold season', url: 'https://www.pdsa.org.uk/press-office/latest-news/pdsa-s-winter-advice-to-keep-your-pet-safe-through-the-cold-season' };
const PDSA_HEAT = { title: 'PDSA Pet Health Hub: Heatstroke in dogs', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/heatstroke-in-dogs' };
const ESCCAP_IT = { title: 'ESCCAP, Linea guida 5 (traduzione italiana): Controllo delle malattie trasmesse da vettori nel cane e nel gatto', url: 'https://www.esccap.org/uploads/docs/jojw6bze_ESCCAP_GL_05_ita.pdf' };

export const SEASONAL: SeasonalAlert[] = [
  {
    id: 'processionary',
    months: [2, 3, 4, 5],
    countries: ['it'],
    species: ['dog'],
    level: 'danger',
    title: { en: 'Pine processionary caterpillars', it: 'Processionaria del pino', de: 'Pinien-Prozessionsspinner' },
    text: {
      en: 'In Tuscany, the Region reports that pine processionary larvae finish developing between late February and the first half of May, depending on conditions, and then come down the trunk in long lines. Their stinging hairs can cause skin and allergic reactions in people and warm-blooded animals, so keep your dog away from the lines and the nests.',
      it: 'In Toscana la Regione segnala che le larve della processionaria del pino completano lo sviluppo tra fine febbraio e la prima metà di maggio, secondo le condizioni ambientali, e poi scendono lungo il tronco in lunghe file. I loro peli urticanti possono provocare reazioni cutanee e allergiche in persone e animali a sangue caldo: tieni il cane lontano dalle file e dai nidi.',
      de: 'In der Toskana meldet die Region, dass die Larven des Pinien-Prozessionsspinners je nach Witterung zwischen Ende Februar und der ersten Maihälfte ausgewachsen sind und dann in langen Reihen den Stamm herabwandern. Ihre Brennhaare können bei Menschen und warmblütigen Tieren Haut- und allergische Reaktionen auslösen: Halten Sie Ihren Hund von den Raupen und Nestern fern.',
    },
    article: { it: 'processionaria-cane' },
    references: [
      { title: 'Regione Toscana: La Processionaria del Pino, un insetto che può recare danni (opuscolo)', url: 'https://www.regione.toscana.it/documents/10180/11270546/Processionariadelpino_161224.pdf/c432e228-4d98-4822-b4f1-bc859e39d26c' },
      { title: 'Regione Toscana: In arrivo i mesi della processionaria del pino', url: 'https://www.regione.toscana.it/-/in-arrivo-i-mesi-della-processionaria-del-pino-1' },
    ],
  },
  {
    id: 'sandflies-leishmaniosis',
    months: [4, 5, 6, 7, 8, 9, 10, 11],
    countries: ['it'],
    species: ['dog'],
    level: 'caution',
    title: { en: 'Sandflies and leishmaniosis', it: 'Flebotomi e leishmaniosi', de: 'Sandmücken und Leishmaniose' },
    text: {
      en: 'ESCCAP’s Italian guideline says the sandfly season in endemic areas varies from year to year and region to region, but as a general rule runs from April to November. It advises protecting dogs with repellent products throughout that period and keeping them in protected rooms at dawn and dusk; ask your vet which product suits your dog.',
      it: 'Secondo la linea guida ESCCAP in italiano, la stagione dei flebotomi nelle aree endemiche varia da anno ad anno e da regione a regione, ma come regola generale va da aprile a novembre. Consiglia di proteggere il cane con repellenti per tutto il periodo e di tenerlo in locali protetti all’alba e al tramonto; chiedi al veterinario quale prodotto è adatto.',
      de: 'Laut der italienischen ESCCAP-Leitlinie schwankt die Sandmückensaison in Endemiegebieten von Jahr zu Jahr und von Region zu Region, reicht aber in der Regel von April bis November. Sie rät, Hunde in dieser Zeit mit Repellentien zu schützen und sie in der Morgen- und Abenddämmerung in geschützten Räumen zu halten; welches Mittel passt, sagt Ihre Praxis.',
    },
    article: { it: 'leishmaniosi-cane' },
    references: [ESCCAP_IT],
  },
  {
    id: 'heartworm',
    months: [4, 5],
    countries: ['it'],
    species: ['dog'],
    level: 'caution',
    title: { en: 'Heartworm: the prevention season starts', it: 'Filariosi: inizia la stagione della prevenzione', de: 'Herzwurm: die Vorbeugesaison beginnt' },
    text: {
      en: 'Heartworm (Dirofilaria) is spread by mosquitoes. For southern Europe, ESCCAP’s Italian guideline says monthly prevention in dogs should start in May and continue until November or mid-December; ask your vet now about a plan.',
      it: 'La filariosi (Dirofilaria) è trasmessa dalle zanzare. Per il sud Europa, la linea guida ESCCAP in italiano indica che la prevenzione mensile nel cane dovrebbe iniziare a maggio e continuare fino a novembre o metà dicembre; chiedi ora al veterinario un piano.',
      de: 'Herzwürmer (Dirofilaria) werden durch Stechmücken übertragen. Für Südeuropa nennt die italienische ESCCAP-Leitlinie eine monatliche Vorbeugung beim Hund ab Mai bis November oder Mitte Dezember; fragen Sie jetzt Ihre Praxis nach einem Plan.',
    },
    references: [ESCCAP_IT],
  },
  {
    id: 'ticks-dach',
    months: [3, 4, 5, 6, 7, 8, 9, 10, 11],
    countries: ['de-at-ch'],
    species: ['dog', 'cat'],
    level: 'caution',
    title: { en: 'Tick season', it: 'Stagione delle zecche', de: 'Zeckensaison' },
    text: {
      en: 'ESCCAP Germany says the common tick is especially active in spring (March to June) and autumn (September to November), and where the ornate dog tick occurs there is a risk almost all year round. ESCCAP Switzerland gives roughly March to November as the main tick season; check your dog or cat regularly and ask your vet about tick protection.',
      it: 'ESCCAP Germania indica che la zecca dei boschi è particolarmente attiva in primavera (da marzo a giugno) e in autunno (da settembre a novembre); dove è presente la zecca Dermacentor il rischio c’è quasi tutto l’anno. ESCCAP Svizzera indica come stagione principale circa marzo–novembre: controlla spesso cane e gatto e chiedi al veterinario come proteggerli.',
      de: 'ESCCAP Deutschland zufolge ist der Gemeine Holzbock besonders im Frühjahr (März bis Juni) und Herbst (September bis November) aktiv; wo die Buntzecke vorkommt, besteht mehr oder weniger ganzjährig ein Befallsrisiko. ESCCAP Schweiz nennt ca. März bis November als Zeckenhauptsaison: Untersuchen Sie Hund und Katze regelmäßig und fragen Sie Ihre Praxis nach Zeckenschutz.',
    },
    article: { en: 'dog-tick-removal', it: 'zecca-cane-come-toglierla', de: 'hund-zecke-entfernen' },
    references: [
      { title: 'ESCCAP Deutschland: Tipps gegen Zecken', url: 'https://esccap.de/tipps-gegen-zecken' },
      { title: 'ESCCAP Schweiz: Schema zur Bekämpfung von Zecken und Flöhen bei Hund und Katze', url: 'https://www.esccap.org/uploads/docs/d5rysgla_ESCCAP_CH_SchemaEkto_HundKatze_d_def_210121.pdf' },
    ],
  },
  {
    id: 'ticks',
    months: [4, 5, 6, 7, 8, 9],
    countries: ['all'],
    except: ['de-at-ch'],
    species: ['dog'],
    level: 'caution',
    title: { en: 'Ticks are active', it: 'Zecche attive', de: 'Zecken sind aktiv' },
    text: {
      en: 'PDSA says ticks are most active in the warmer months and are common in long grass, woodland and areas with lots of wildlife. Stick to paths, check your dog regularly after walks, and ask your vet about tick protection if you live in a high-risk area.',
      it: 'Secondo la PDSA le zecche sono più attive nei mesi caldi e sono comuni nell’erba alta, nei boschi e nelle zone con molta fauna selvatica. Resta sui sentieri, controlla spesso il cane dopo le passeggiate e, se vivi in una zona a rischio, chiedi al veterinario come proteggerlo.',
      de: 'Laut PDSA sind Zecken in den warmen Monaten am aktivsten und häufig in hohem Gras, im Wald und in wildreichen Gegenden. Bleiben Sie auf den Wegen, suchen Sie Ihren Hund nach Spaziergängen regelmäßig ab und fragen Sie in Risikogebieten Ihre Praxis nach Zeckenschutz.',
    },
    article: { en: 'dog-tick-removal', it: 'zecca-cane-come-toglierla', de: 'hund-zecke-entfernen' },
    references: [{ title: 'PDSA Pet Health Hub: Ticks on dogs', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/ticks-on-dogs' }],
  },
  {
    id: 'heatstroke',
    months: [6, 7, 8],
    countries: ['all'],
    species: ['dog'],
    level: 'danger',
    title: { en: 'Heat and heatstroke', it: 'Caldo e colpo di calore', de: 'Hitze und Hitzschlag' },
    text: {
      en: 'PDSA says nearly three quarters of heatstroke cases in dogs develop during play and exercise. Walk your dog in the cool of the early morning or evening, always give shade and water, and get to a vet quickly if your dog may be overheating.',
      it: 'Secondo la PDSA quasi tre quarti dei colpi di calore nel cane avvengono durante il gioco e l’attività fisica. Porta fuori il cane al fresco del mattino presto o della sera, dagli sempre ombra e acqua e, se pensi che si stia surriscaldando, vai subito dal veterinario.',
      de: 'Laut PDSA entstehen fast drei Viertel der Hitzschläge bei Hunden beim Spielen und Toben. Gehen Sie früh morgens oder abends in der Kühle spazieren, sorgen Sie immer für Schatten und Wasser und fahren Sie schnell in die Praxis, wenn Ihr Hund überhitzt sein könnte.',
    },
    article: { en: 'heatstroke', it: 'heatstroke', de: 'heatstroke' },
    references: [PDSA_HEAT],
  },
  {
    id: 'hot-car',
    months: [6, 7, 8],
    countries: ['all'],
    species: ['dog'],
    level: 'danger',
    title: { en: 'Never leave a dog in the car', it: 'Mai il cane in auto', de: 'Kein Hund im geparkten Auto' },
    text: {
      en: 'PDSA: never leave your dog in a car on a warm day, not even for a few minutes, in the shade or with the windows open. Baden-Württemberg’s animal-welfare officer warns that a parked car can become a deadly trap at outside temperatures just under 20 °C, and short-nosed breeds are at risk from 15 °C.',
      it: 'PDSA: non lasciare mai il cane in auto in una giornata calda, nemmeno per pochi minuti, all’ombra o con i finestrini aperti. La garante per la tutela degli animali del Baden-Württemberg avverte che un’auto parcheggiata può diventare una trappola mortale già con temperature esterne appena sotto i 20 °C, e per le razze a muso corto il rischio c’è già da 15 °C.',
      de: 'Laut BLV kann die Temperatur im Auto so stark ansteigen, dass Hunden nach kurzer Zeit schwere Herz- und Kreislaufstörungen bis hin zum tödlichen Hitzschlag drohen. Die Landestierschutzbeauftragte Baden-Württemberg warnt: Schon knapp unter 20 °C Außentemperatur kann ein geparktes Auto zur tödlichen Falle werden, für kurzschnäuzige Rassen bereits ab 15 °C.',
    },
    article: { en: 'heatstroke', it: 'heatstroke', de: 'heatstroke' },
    references: [
      PDSA_HEAT,
      { title: 'Land Baden-Württemberg: Keine Hunde im Auto zurücklassen (Pressemitteilung)', url: 'https://www.baden-wuerttemberg.de/de/service/presse/pressemitteilung/pid/keine-hunde-im-auto-zuruecklassen' },
      { title: 'Staat Freiburg (mit Genehmigung des BLV): Hitze in Fahrzeugen, tödliche Gefahr für Tiere', url: 'https://www.fr.ch/de/ilfd/lsvw/news/hitze-in-fahrzeugen-toedliche-gefahr-fuer-tiere' },
    ],
  },
  {
    id: 'blue-green-algae',
    months: [6, 7, 8],
    countries: ['all'],
    species: ['dog'],
    level: 'danger',
    title: { en: 'Blue-green algae in still water', it: 'Alghe blu-verdi nelle acque ferme', de: 'Blaualgen in stehenden Gewässern' },
    text: {
      en: 'Blue-green algae grow best in warm weather, so PDSA says poisonings are more likely in the summer months. Keep your dog out of still or slow-flowing water with green-blue scum or streaks, and call your vet straight away if your dog may have been exposed.',
      it: 'Le alghe blu-verdi crescono meglio con il caldo, e per la PDSA le intossicazioni sono più probabili nei mesi estivi. Non far entrare né bere il cane in acque ferme o lente con schiuma o striature verde-blu, e chiama subito il veterinario se potrebbe esserne venuto a contatto.',
      de: 'Blaualgen wachsen am besten bei warmem Wetter; laut PDSA sind Vergiftungen deshalb in den Sommermonaten wahrscheinlicher. Lassen Sie Ihren Hund nicht in stehendes oder langsam fließendes Wasser mit grün-blauem Schaum oder Schlieren und rufen Sie sofort die Praxis an, wenn er Kontakt hatte.',
    },
    article: { en: 'poisoning-first-aid', it: 'poisoning-first-aid', de: 'poisoning-first-aid' },
    references: [{ title: 'PDSA Pet Health Hub: Blue-green algae poisoning in dogs', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/blue-green-algae-poisoning-in-dogs' }],
  },
  {
    id: 'flystrike',
    months: [6, 7, 8],
    countries: ['all'],
    species: ['rabbit'],
    level: 'danger',
    title: { en: 'Flystrike in rabbits', it: 'Miasi nel coniglio', de: 'Fliegenmadenbefall beim Kaninchen' },
    text: {
      en: 'PDSA says flystrike is more common in the warm summer months, when flies are most active. Check your rabbits every day, especially around the bottom, and remove droppings, urine and wet bedding at least once a day.',
      it: 'Secondo la PDSA la miasi è più frequente nei mesi caldi d’estate, quando le mosche sono più attive. Controlla i conigli ogni giorno, soprattutto intorno al sederino, e togli feci, urina e lettiera bagnata almeno una volta al giorno.',
      de: 'Laut PDSA ist Fliegenmadenbefall in den warmen Sommermonaten häufiger, wenn Fliegen am aktivsten sind. Kontrollieren Sie Ihre Kaninchen täglich, vor allem am Hinterteil, und entfernen Sie Kot, Urin und nasse Einstreu mindestens einmal am Tag.',
    },
    references: [{ title: 'PDSA Pet Health Hub: Flystrike in rabbits', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/flystrike-in-rabbits' }],
  },
  {
    id: 'tortoise-hibernation',
    months: [10],
    countries: ['all'],
    species: ['reptile'],
    level: 'caution',
    title: { en: 'Getting tortoises ready for hibernation', it: 'Preparare la tartaruga al letargo', de: 'Landschildkröten auf die Winterstarre vorbereiten' },
    text: {
      en: 'The German Federal Chamber of Veterinarians (BTK) says that as the days grow shorter and colder in October, European tortoises slow down, eat less and should be prepared for hibernation. It advises a vet check first, including a faecal test for parasites, then reducing light and temperature gradually over about three weeks.',
      it: 'La Camera federale dei veterinari tedeschi (BTK) spiega che a ottobre, con giornate più corte e fredde, le tartarughe di terra europee rallentano, mangiano meno e vanno preparate al letargo. Consiglia prima una visita veterinaria con esame delle feci per i parassiti, poi di ridurre luce e temperatura gradualmente in circa tre settimane.',
      de: 'Die Bundestierärztekammer (BTK) erklärt: Wenn die Tage im Oktober kürzer und kälter werden, werden Europäische Landschildkröten träger, fressen weniger und sollten auf die Überwinterung vorbereitet werden. Wichtig ist vorher ein Kontrollbesuch in der Praxis mit Kotuntersuchung auf Parasiten; danach Licht und Temperatur schrittweise über etwa drei Wochen reduzieren.',
    },
    article: { en: 'tortoise-hibernation', it: 'tartaruga-di-terra-letargo', de: 'schildkroete-winterstarre' },
    references: [{ title: 'Bundestierärztekammer: Ein Winterbett im Kühlschrank, Tipps zur Überwinterung von Landschildkröten (2012)', url: 'https://www.bundestieraerztekammer.de/presse/archiv/2012/PM_33_2012_Schildkroetenrichtigueberwintern.pdf' }],
  },
  {
    id: 'antifreeze',
    months: [10, 11, 12, 1, 2, 3],
    countries: ['all'],
    species: ['dog', 'cat'],
    level: 'danger',
    title: { en: 'Antifreeze is deadly', it: 'L’antigelo è letale', de: 'Frostschutzmittel ist tödlich' },
    text: {
      en: 'Antifreeze tastes sweet and is very poisonous to dogs and cats; the MSD Veterinary Manual says that in colder climates most cases happen in autumn, winter and early spring. If your pet may have licked any, PDSA says to get them to a vet straight away, without waiting for symptoms.',
      it: 'L’antigelo ha un sapore dolce ed è molto velenoso per cani e gatti; il Manuale Veterinario MSD indica che nei climi più freddi la maggior parte dei casi avviene in autunno, inverno e inizio primavera. Se il tuo animale potrebbe averne leccato, la PDSA dice di portarlo subito dal veterinario, senza aspettare i sintomi.',
      de: 'Frostschutzmittel schmeckt süß und ist für Hunde und Katzen sehr giftig; laut MSD Veterinary Manual treten in kälteren Klimazonen die meisten Fälle im Herbst, Winter und frühen Frühjahr auf. Hat Ihr Tier womöglich davon geleckt, rät die PDSA, sofort in die Praxis zu fahren und nicht auf Symptome zu warten.',
    },
    article: { en: 'poisoning-first-aid', it: 'poisoning-first-aid', de: 'poisoning-first-aid' },
    references: [
      { title: 'MSD Veterinary Manual (Pet Owner Version): Ethylene Glycol (Antifreeze) Poisoning', url: 'https://www.msdvetmanual.com/special-pet-topics/poisoning/ethylene-glycol-antifreeze-poisoning' },
      PDSA_WINTER,
    ],
  },
  {
    id: 'road-salt',
    months: [12, 1, 2],
    countries: ['all'],
    species: ['dog'],
    level: 'caution',
    title: { en: 'Road salt and grit on paws', it: 'Sale e ghiaino sulle zampe', de: 'Streusalz an den Pfoten' },
    text: {
      en: 'PDSA warns that the salt and grit used on winter roads can irritate paws. After a walk on salted or gritted ground, wash your dog’s paws when you get home.',
      it: 'La PDSA avverte che il sale e il ghiaino sparsi sulle strade d’inverno possono irritare le zampe. Dopo una passeggiata su strade trattate, lava le zampe al cane appena rientri.',
      de: 'Die PDSA warnt, dass Streusalz und Splitt im Winter die Pfoten reizen können. Waschen Sie Ihrem Hund nach Spaziergängen auf gestreuten Wegen zu Hause die Pfoten.',
    },
    references: [PDSA_WINTER],
  },
  {
    id: 'cats-and-cars',
    months: [12, 1, 2],
    countries: ['all'],
    species: ['cat'],
    level: 'caution',
    title: { en: 'Cats under the bonnet', it: 'Gatti nel cofano', de: 'Katzen unter der Motorhaube' },
    text: {
      en: 'PDSA notes that in cold, wet weather cats often shelter under cars or climb inside the bonnet to a warm engine. Check under the bonnet and give it a good knock before you start the car.',
      it: 'La PDSA ricorda che con il freddo e la pioggia i gatti si riparano spesso sotto le auto o si infilano nel cofano, vicino al motore caldo. Controlla sotto il cofano e dagli qualche colpo prima di avviare l’auto.',
      de: 'Die PDSA weist darauf hin, dass Katzen bei kaltem, nassem Wetter oft unter Autos Schutz suchen oder in den Motorraum zum warmen Motor klettern. Schauen Sie unter die Motorhaube und klopfen Sie kräftig darauf, bevor Sie losfahren.',
    },
    references: [PDSA_WINTER],
  },
  {
    id: 'small-pets-cold',
    months: [12, 1, 2],
    countries: ['all'],
    species: ['rabbit', 'guinea-pig'],
    level: 'caution',
    title: { en: 'Rabbits and guinea pigs in the cold', it: 'Conigli e cavie al freddo', de: 'Kaninchen und Meerschweinchen bei Kälte' },
    text: {
      en: 'PDSA says small pets such as rabbits and guinea pigs feel the cold and are very sensitive to sudden drops in temperature. If they live outdoors, move them to a sheltered, draught-free place such as a shed or a car-free garage, with plenty of deep, dry bedding.',
      it: 'Secondo la PDSA i piccoli animali come conigli e cavie soffrono il freddo e sono molto sensibili ai cali improvvisi di temperatura. Se vivono all’aperto, spostali in un luogo riparato e senza correnti d’aria, come un capanno o un garage senza auto, con tanta lettiera asciutta e profonda.',
      de: 'Laut PDSA spüren Kleintiere wie Kaninchen und Meerschweinchen die Kälte und reagieren sehr empfindlich auf plötzliche Temperaturstürze. Leben sie draußen, bringen Sie sie an einen geschützten, zugfreien Ort wie einen Schuppen oder eine Garage ohne Auto, mit reichlich tiefer, trockener Einstreu.',
    },
    references: [PDSA_WINTER],
  },
  {
    id: 'christmas-plants',
    months: [12],
    countries: ['all'],
    species: ['dog', 'cat'],
    level: 'caution',
    title: { en: 'Festive plants', it: 'Piante delle feste', de: 'Weihnachtspflanzen' },
    text: {
      en: 'PDSA says festive favourites such as holly, ivy and poinsettia are toxic to pets if they eat them. Keep them out of your pet’s reach.',
      it: 'La PDSA ricorda che piante tipiche delle feste come agrifoglio, edera e stella di Natale sono tossiche per gli animali se le mangiano. Tienile fuori dalla loro portata.',
      de: 'Laut PDSA sind festliche Pflanzen wie Stechpalme, Efeu und Weihnachtsstern giftig für Haustiere, wenn sie davon fressen. Stellen Sie sie außer Reichweite.',
    },
    article: { en: 'cat-toxic-foods-plants', it: 'alimenti-piante-tossiche-gatto', de: 'giftige-lebensmittel-pflanzen-katze' },
    references: [PDSA_WINTER],
  },
  {
    id: 'chocolate-holidays',
    months: [3, 4, 12],
    countries: ['all'],
    species: ['dog'],
    level: 'danger',
    title: { en: 'Chocolate at Easter and Christmas', it: 'Cioccolato a Pasqua e Natale', de: 'Schokolade an Ostern und Weihnachten' },
    text: {
      en: 'Chocolate is poisonous to dogs, and PDSA advises taking particular care at festive times such as Easter and Christmas. If your dog has eaten some, use our chocolate check or call your vet.',
      it: 'Il cioccolato è velenoso per il cane, e la PDSA consiglia di fare particolare attenzione nei periodi di festa come Pasqua e Natale. Se il cane ne ha mangiato, usa il nostro controllo cioccolato o chiama il veterinario.',
      de: 'Schokolade ist für Hunde giftig, und die PDSA rät, an Festtagen wie Ostern und Weihnachten besonders aufzupassen. Hat Ihr Hund davon gefressen, nutzen Sie unseren Schokoladen-Check oder rufen Sie Ihre Praxis an.',
    },
    article: { en: 'dog-ate-chocolate', it: 'cane-ha-mangiato-cioccolato', de: 'hund-schokolade-gefressen' },
    tool: '/chocolate',
    references: [
      { title: 'PDSA Pet Health Hub: Chocolate poisoning in dogs', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/chocolate-poisoning' },
      { title: 'MSD Veterinary Manual: Chocolate Toxicosis in Animals', url: 'https://www.msdvetmanual.com/toxicology/food-hazards/chocolate-toxicosis-in-animals' },
    ],
  },
  {
    id: 'fireworks',
    months: [12],
    countries: ['all'],
    species: ['dog', 'cat', 'bird'],
    level: 'caution',
    title: { en: 'Fireworks at New Year', it: 'Botti di Capodanno', de: 'Feuerwerk an Silvester' },
    text: {
      en: 'Walk dogs while it is still light and keep them on a lead, bring cats in before dark and lock the cat flap, and give every pet a den to hide in (PDSA). The BTK adds: keep dogs on the lead from the day before New Year’s Eve, cover bird cages, and see a vet in good time if your animal is very anxious.',
      it: 'Porta fuori il cane finché c’è luce e tienilo al guinzaglio, fai rientrare il gatto prima del buio e chiudi la gattaiola, e offri a ogni animale una tana dove nascondersi (PDSA). La BTK aggiunge: cane al guinzaglio già dal giorno prima di Capodanno, gabbie degli uccelli coperte e, se l’animale è molto pauroso, una visita dal veterinario per tempo.',
      de: 'Gehen Sie mit dem Hund im Hellen und an der Leine, holen Sie Katzen vor der Dunkelheit herein und schließen Sie die Katzenklappe, und bieten Sie jedem Tier ein Versteck (PDSA). Die BTK rät: Hunde schon am Tag vor Silvester nicht mehr von der Leine lassen, Vogelkäfige abdecken und bei sehr ängstlichen Tieren rechtzeitig die Praxis fragen.',
    },
    references: [
      { title: 'PDSA Pet Health Hub: Dogs and fireworks', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/dogs-and-fireworks' },
      { title: 'PDSA Pet Health Hub: Cats and fireworks', url: 'https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/cats-and-fireworks' },
      { title: 'Bundestierärztekammer: Bello unter Böllerstress, Tipps für die Silvesternacht (2012)', url: 'https://www.bundestieraerztekammer.de/presse/archiv/2012/PM_45_12_Silvester.pdf' },
    ],
  },
];
