/** Labels for the animal-information section, per language. Article content lives in src/content/animals/<lang>/. */
export type Lang = 'en' | 'it';

export const ANIMALS = {
  en: {
    base: '/animals', visitBrief: '/visit-brief', title: 'Animal information',
    desc: 'Plain-language animal-health information for owners, reviewed by veterinarians.',
    lead: 'Written for owners, checked by vets. Each article says who reviewed it and when. If something needs a veterinarian, the article says so at the top, not at the bottom.',
    prepare: 'Prepare for a vet visit →',
    emergency: '<strong>Emergency?</strong> Collapse, difficulty breathing, severe bleeding, a bloated hard belly, seizures that don\'t stop, poisoning, or a cat that cannot urinate: go to a veterinary clinic now. Call ahead so they can prepare.',
    byTopic: 'By topic', byAnimal: 'By animal', latest: 'Latest', articles: 'articles', draft: 'Draft, awaiting vet review',
    nothing: 'Nothing here yet. Articles are being written and reviewed; check back soon or <a href="/newsletter">subscribe</a> to hear when they\'re published.',
    reviewedBy: 'Reviewed by', updated: 'Updated', draftLong: 'Draft, awaiting veterinary review', whenToSee: 'When to see a vet:',
    footer: 'This article is general information and cannot take your animal\'s history, breed or medications into account. It is not a diagnosis and does not replace an examination. If you are worried, call your vet; they would rather hear from you early.',
    urgency: {
      emergency: 'This can be an emergency. If you are seeing it now, contact a veterinary clinic immediately.',
      today: 'See a vet today. This is not usually an emergency, but it should not wait.',
      'this-week': 'Book a vet appointment this week if it continues or gets worse.',
      routine: 'Routine information. Mention it at your next visit if you have questions.',
    },
    species: { dog: 'Dogs', cat: 'Cats', rabbit: 'Rabbits & small mammals', horse: 'Horses', bird: 'Birds', general: 'All animals' },
    categories: {
      symptoms: ['Symptoms', 'What a sign can mean and when to call a vet'],
      conditions: ['Conditions', 'Common diagnoses explained plainly'],
      medications: ['Medications', 'What a prescribed drug is for and how to give it'],
      'first-aid': ['First aid & emergencies', 'What to do right now, and what not to do'],
      travel: ['Travel & paperwork', 'Passports, microchips, moving between countries'],
      care: ['Everyday care', 'Feeding, vaccinations, the routine things'],
    },
    locale: 'en-GB',
  },
  it: {
    base: '/it/animals', visitBrief: '/it/visit-brief', title: 'Informazioni sugli animali',
    desc: 'Informazioni sulla salute degli animali in linguaggio semplice, per i proprietari, riviste da veterinari.',
    lead: 'Scritte per i proprietari, controllate dai veterinari. Ogni articolo indica chi lo ha rivisto e quando. Se serve un veterinario, l\'articolo lo dice all\'inizio, non alla fine.',
    prepare: 'Prepara la visita dal veterinario →',
    emergency: '<strong>Emergenza?</strong> Collasso, difficoltà a respirare, sanguinamento grave, addome gonfio e duro, convulsioni che non si fermano, avvelenamento, o un gatto che non riesce a urinare: vai subito in una clinica veterinaria. Telefona prima, così possono prepararsi.',
    byTopic: 'Per argomento', byAnimal: 'Per animale', latest: 'Ultimi articoli', articles: 'articoli', draft: 'Bozza, in attesa di revisione veterinaria',
    nothing: 'Ancora niente qui. Gli articoli sono in scrittura e revisione; torna presto o <a href="/newsletter">iscriviti</a> per sapere quando saranno pubblicati.',
    reviewedBy: 'Rivisto da', updated: 'Aggiornato', draftLong: 'Bozza, in attesa di revisione veterinaria', whenToSee: 'Quando andare dal veterinario:',
    footer: 'Questo articolo è un\'informazione generale e non può tenere conto della storia, della razza o dei farmaci del tuo animale. Non è una diagnosi e non sostituisce una visita. Se sei preoccupato, chiama il tuo veterinario: preferisce sentirti presto.',
    urgency: {
      emergency: 'Può essere un\'emergenza. Se la stai vedendo adesso, contatta subito una clinica veterinaria.',
      today: 'Vai dal veterinario oggi. Di solito non è un\'emergenza, ma non deve aspettare.',
      'this-week': 'Prenota una visita questa settimana se continua o peggiora.',
      routine: 'Informazione di routine. Parlane alla prossima visita se hai domande.',
    },
    species: { dog: 'Cani', cat: 'Gatti', rabbit: 'Conigli e piccoli mammiferi', horse: 'Cavalli', bird: 'Uccelli', general: 'Tutti gli animali' },
    categories: {
      symptoms: ['Sintomi', 'Cosa può significare un segno e quando chiamare il veterinario'],
      conditions: ['Malattie', 'Le diagnosi più comuni spiegate in modo semplice'],
      medications: ['Farmaci', 'A cosa serve un farmaco prescritto e come somministrarlo'],
      'first-aid': ['Primo soccorso ed emergenze', 'Cosa fare subito, e cosa non fare'],
      travel: ['Viaggi e documenti', 'Passaporti, microchip, spostamenti tra paesi'],
      care: ['Cura quotidiana', 'Alimentazione, vaccinazioni, le cose di routine'],
    },
    locale: 'it-IT',
  },
} as const;

/** Article id without the language folder: 'it/dog-vomiting' → 'dog-vomiting'. */
export const slugOf = (id: string) => id.replace(/^[a-z]{2}\//, '');
