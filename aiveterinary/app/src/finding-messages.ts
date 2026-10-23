import type { Finding } from './validators.js';
import type { Lang } from './render.js';

/**
 * Finding messages in the workspace language (EN/DE/IT).
 *
 * Each finding carries its `rule` and a `params` object (the values its message quotes); the English
 * `message` built by the validators stays as it is (tests and the eval read it). findingMessage renders
 * the same message from per-rule templates in the requested language. Text quoted from the notes (and
 * drug names, units, values) is printed exactly as written by the vet; only the explanation is
 * translated. Enum values the English message prints as-is (species, sex, status, vital) are translated.
 */
export type FindingParams = Readonly<Record<string, string | number | boolean | readonly string[]>>;

type P = Record<string, any>;
type Template = (p: P) => string;

/** Every rule a validator in validators.ts or multi-pet.ts can raise. */
export const FINDING_RULES = [
  'source_required', 'span_invalid', 'number_not_in_notes', 'number_not_in_source', 'text_number_not_in_source',
  'drug_not_in_source', 'drug_not_in_notes', 'dose_not_in_notes', 'dose_not_in_source', 'unit_not_in_notes',
  'duration_not_in_notes', 'duration_not_in_source', 'route_not_in_source', 'frequency_not_in_source',
  'dose_without_drug', 'empty_source', 'patient_conflict', 'patient_plausibility', 'implausible_value',
  'derived_number_not_in_record', 'medication_missing_in_derived', 'status_conflicts_source', 'owner_report_as_finding',
  'notes_contradiction', 'other_animal_fact', 'wrong_animal_line', 'unassigned_line_fact', 'unassigned_line', 'label_mismatch',
] as const;
export type FindingRule = (typeof FINDING_RULES)[number];

const SPECIES: Record<Exclude<Lang, 'en'>, Record<string, string>> = {
  de: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vogel', reptile: 'Reptil', other: 'andere Tierart' },
  it: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altra specie' },
};
const SEX: Record<Exclude<Lang, 'en'>, Record<string, string>> = {
  de: { male: 'männlich', female: 'weiblich' },
  it: { male: 'maschio', female: 'femmina' },
};
const STATUS: Record<Exclude<Lang, 'en'>, Record<string, string>> = {
  de: { planned: 'geplant', performed: 'durchgeführt', declined: 'abgelehnt', recommended: 'empfohlen', dispensed: 'abgegeben', prescribed: 'verschrieben' },
  it: { planned: 'programmato', performed: 'eseguito', declined: 'rifiutato', recommended: 'consigliato', dispensed: 'dispensato', prescribed: 'prescritto' },
};
const VITAL: Record<Lang, Record<string, string>> = {
  en: { temperature: 'temperature', heart_rate: 'heart rate', respiratory_rate: 'respiratory rate', weight: 'weight', crt_seconds: 'CRT' },
  de: { temperature: 'Temperatur', heart_rate: 'Herzfrequenz', respiratory_rate: 'Atemfrequenz', weight: 'Gewicht', crt_seconds: 'KFZ' },
  it: { temperature: 'temperatura', heart_rate: 'frequenza cardiaca', respiratory_rate: 'frequenza respiratoria', weight: 'peso', crt_seconds: 'TRC' },
};
const tr = (table: Record<string, string>, v: unknown) => table[String(v)] ?? String(v);

/** Quotes around vet text: straight quotes in English (as the validators write), „…“ in German, «…» in Italian. */
const qde = (s: unknown) => `„${s}“`;
const qit = (s: unknown) => `«${s}»`;

const EN: Record<FindingRule, Template> = {
  source_required: (p) => (p.kind === 'assessment' ? 'Assessment has no source in the notes. The AI must not add a diagnosis.' : 'No source in the notes for this item.'),
  span_invalid: (p) => `Source span [${p.a},${p.b}] is outside the notes.`,
  number_not_in_notes: (p) => EN_NUMBER(p),
  number_not_in_source: (p) => EN_NUMBER(p),
  text_number_not_in_source: (p) => EN_NUMBER(p),
  drug_not_in_source: (p) => `"${p.drug}" is in the notes, but not in the text this medication points to ("${p.quote}").`,
  drug_not_in_notes: (p) => `"${p.drug}" is not in the notes.`,
  dose_not_in_notes: (p) => `Dose ${p.dose} is not in the notes.`,
  dose_not_in_source: (p) => `Dose ${p.dose} is in the notes, but not in the text this medication points to ("${p.quote}").`,
  unit_not_in_notes: (p) => `Unit "${p.unit}" was not written in the notes.`,
  duration_not_in_notes: (p) => `Duration "${p.duration}" contains a number not in the notes.`,
  duration_not_in_source: (p) => `Duration "${p.duration}": ${p.number} is not in the text this medication points to ("${p.quote}").`,
  route_not_in_source: (p) => `Route "${p.route}" is not written in the text this medication points to ("${p.quote}").`,
  frequency_not_in_source: (p) => `Frequency "${p.frequency}" is not written in the text this medication points to ("${p.quote}").`,
  dose_without_drug: () => 'A dose without a drug name.',
  empty_source: () => 'Medication has an empty source.',
  patient_conflict: (p) => (p.kind === 'species' ? `Notes imply species "${p.value}" but the patient is a ${p.expected}.`
    : p.kind === 'sex' ? `Notes imply sex "${p.value}" but the patient record says ${p.expected}.`
    : 'Pregnancy mentioned for a male patient. Check whether this refers to the owner or another animal.'),
  patient_plausibility: () => 'Heat/oestrus mentioned for a neutered patient.',
  implausible_value: (p) => (p.kind === 'temperature' ? `Temperature ${p.value} °C is outside the usual range for a ${p.species}. Typo?` : `${p.value} kg is unusually heavy for a cat.`),
  derived_number_not_in_record: (p) => `"${p.value}" is not in the approved record.`,
  medication_missing_in_derived: (p) => `Medication "${p.drug}" from the record is not mentioned.`,
  status_conflicts_source: (p) => `Recorded as "${p.status}", but the text this item points to says ${p.said} ("${p.quote}").`,
  owner_report_as_finding: (p) => `Recorded as the vet's finding, but the text it points to is the owner's report ("${p.quote}"). Move it to history or mark it owner-reported.`,
  notes_contradiction: (p) => `Notes give ${p.kept} and ${p.others.join(' and ')} for ${VITAL.en[p.vital] ?? p.vital}; the record keeps ${p.kept}. Check which is right.`,
  other_animal_fact: (p) => `This comes from a line about another animal ("${p.quote}"). Check it belongs to this patient.`,
  wrong_animal_line: (p) => `This comes from line ${p.line} ("${p.quote}"), which is assigned to ${p.owner}. It cannot be in ${p.patient}'s record.`,
  unassigned_line_fact: (p) => `This comes from line ${p.line} ("${p.quote}"), which is not assigned to an animal yet. Assign the line first.`,
  unassigned_line: (p) => `Line ${p.line} ("${p.quote}") is not assigned to an animal or marked shared.`,
  label_mismatch: (p) => `Line ${p.line} starts with "${p.label}:" but is assigned to ${p.shared ? 'all animals (shared)' : p.target}. Check the assignment.`,
};
function EN_NUMBER(p: P) {
  return p.kind === 'elsewhere' ? `The value ${p.value} is in the notes, but not in the text this item points to ("${p.quote}").` : `The value ${p.value} does not appear in the notes.`;
}

const DE_NUMBER = (p: P) => (p.kind === 'elsewhere'
  ? `Der Wert ${p.value} steht in den Notizen, aber nicht in der Textstelle, auf die dieser Eintrag verweist (${qde(p.quote)}).`
  : `Der Wert ${p.value} kommt in den Notizen nicht vor.`);
const DE_MED = 'in der Textstelle, auf die diese Medikation verweist';
const DE: Record<FindingRule, Template> = {
  source_required: (p) => (p.kind === 'assessment' ? 'Die Beurteilung hat keine Quelle in den Notizen. Die KI darf keine Diagnose ergänzen.' : 'Für diesen Eintrag gibt es keine Quelle in den Notizen.'),
  span_invalid: (p) => `Der Quellbereich [${p.a},${p.b}] liegt außerhalb der Notizen.`,
  number_not_in_notes: DE_NUMBER,
  number_not_in_source: DE_NUMBER,
  text_number_not_in_source: DE_NUMBER,
  drug_not_in_source: (p) => `${qde(p.drug)} steht in den Notizen, aber nicht ${DE_MED} (${qde(p.quote)}).`,
  drug_not_in_notes: (p) => `${qde(p.drug)} steht nicht in den Notizen.`,
  dose_not_in_notes: (p) => `Die Dosis ${p.dose} steht nicht in den Notizen.`,
  dose_not_in_source: (p) => `Die Dosis ${p.dose} steht in den Notizen, aber nicht ${DE_MED} (${qde(p.quote)}).`,
  unit_not_in_notes: (p) => `Die Einheit ${qde(p.unit)} steht nicht in den Notizen.`,
  duration_not_in_notes: (p) => `Die Behandlungsdauer ${qde(p.duration)} enthält eine Zahl, die nicht in den Notizen steht.`,
  duration_not_in_source: (p) => `Behandlungsdauer ${qde(p.duration)}: ${p.number} steht nicht ${DE_MED} (${qde(p.quote)}).`,
  route_not_in_source: (p) => `Die Applikationsart ${qde(p.route)} steht nicht ${DE_MED} (${qde(p.quote)}).`,
  frequency_not_in_source: (p) => `Die Häufigkeit ${qde(p.frequency)} steht nicht ${DE_MED} (${qde(p.quote)}).`,
  dose_without_drug: () => 'Eine Dosis ohne Arzneimittelnamen.',
  empty_source: () => 'Die Quelle dieser Medikation ist leer.',
  patient_conflict: (p) => (p.kind === 'species' ? `Die Notizen deuten auf die Tierart ${qde(tr(SPECIES.de, p.value))} hin, laut Patientendaten ist die Tierart jedoch ${tr(SPECIES.de, p.expected)}.`
    : p.kind === 'sex' ? `Die Notizen deuten auf das Geschlecht ${qde(tr(SEX.de, p.value))} hin, in den Patientendaten steht jedoch ${tr(SEX.de, p.expected)}.`
    : 'Trächtigkeit bei einem männlichen Patienten erwähnt. Prüfen Sie, ob sich dies auf die Tierhalterin bzw. den Tierhalter oder ein anderes Tier bezieht.'),
  patient_plausibility: () => 'Läufigkeit/Rolligkeit bei einem kastrierten Patienten erwähnt.',
  implausible_value: (p) => (p.kind === 'temperature' ? `Die Temperatur ${p.value} °C liegt außerhalb des üblichen Bereichs für die Tierart ${tr(SPECIES.de, p.species)}. Tippfehler?` : `${p.value} kg ist für eine Katze ungewöhnlich schwer.`),
  derived_number_not_in_record: (p) => `${qde(p.value)} steht nicht in der freigegebenen Dokumentation.`,
  medication_missing_in_derived: (p) => `Das Medikament ${qde(p.drug)} aus der Dokumentation wird nicht erwähnt.`,
  status_conflicts_source: (p) => `Erfasst als ${qde(tr(STATUS.de, p.status))}, aber die Textstelle, auf die dieser Eintrag verweist, lautet: ${tr(STATUS.de, p.said)} (${qde(p.quote)}).`,
  owner_report_as_finding: (p) => `Als tierärztlicher Befund erfasst, aber die Textstelle, auf die er verweist, ist eine Angabe der Tierhalterin bzw. des Tierhalters (${qde(p.quote)}). Verschieben Sie ihn in die Anamnese oder kennzeichnen Sie ihn als Halterangabe.`,
  notes_contradiction: (p) => `Die Notizen nennen für ${VITAL.de[p.vital] ?? p.vital} ${p.kept} und ${p.others.join(' und ')}; in der Dokumentation steht ${p.kept}. Prüfen Sie, welcher Wert stimmt.`,
  other_animal_fact: (p) => `Dies stammt aus einer Zeile über ein anderes Tier (${qde(p.quote)}). Prüfen Sie, ob es zu diesem Patienten gehört.`,
  wrong_animal_line: (p) => `Dies stammt aus Zeile ${p.line} (${qde(p.quote)}), die ${p.owner} zugeordnet ist. Es darf nicht in der Dokumentation von ${p.patient} stehen.`,
  unassigned_line_fact: (p) => `Dies stammt aus Zeile ${p.line} (${qde(p.quote)}), die noch keinem Tier zugeordnet ist. Ordnen Sie zuerst die Zeile zu.`,
  unassigned_line: (p) => `Zeile ${p.line} (${qde(p.quote)}) ist keinem Tier zugeordnet und nicht als gemeinsam markiert.`,
  label_mismatch: (p) => `Zeile ${p.line} beginnt mit ${qde(`${p.label}:`)}, ist aber ${p.shared ? 'allen Tieren (gemeinsam)' : p.target} zugeordnet. Prüfen Sie die Zuordnung.`,
};

const IT_NUMBER = (p: P) => (p.kind === 'elsewhere'
  ? `Il valore ${p.value} è nelle note, ma non nel testo a cui rimanda questa voce (${qit(p.quote)}).`
  : `Il valore ${p.value} non compare nelle note.`);
const IT_MED = 'nel testo a cui rimanda questo farmaco';
const IT: Record<FindingRule, Template> = {
  source_required: (p) => (p.kind === 'assessment' ? "La valutazione non ha una fonte nelle note. L'IA non deve aggiungere una diagnosi." : 'Nessuna fonte nelle note per questa voce.'),
  span_invalid: (p) => `L'intervallo di origine [${p.a},${p.b}] è fuori dalle note.`,
  number_not_in_notes: IT_NUMBER,
  number_not_in_source: IT_NUMBER,
  text_number_not_in_source: IT_NUMBER,
  drug_not_in_source: (p) => `${qit(p.drug)} è nelle note, ma non ${IT_MED} (${qit(p.quote)}).`,
  drug_not_in_notes: (p) => `${qit(p.drug)} non è nelle note.`,
  dose_not_in_notes: (p) => `La dose ${p.dose} non è nelle note.`,
  dose_not_in_source: (p) => `La dose ${p.dose} è nelle note, ma non ${IT_MED} (${qit(p.quote)}).`,
  unit_not_in_notes: (p) => `L'unità ${qit(p.unit)} non è scritta nelle note.`,
  duration_not_in_notes: (p) => `La durata ${qit(p.duration)} contiene un numero che non è nelle note.`,
  duration_not_in_source: (p) => `Durata ${qit(p.duration)}: ${p.number} non è ${IT_MED} (${qit(p.quote)}).`,
  route_not_in_source: (p) => `La via di somministrazione ${qit(p.route)} non è scritta ${IT_MED} (${qit(p.quote)}).`,
  frequency_not_in_source: (p) => `La frequenza ${qit(p.frequency)} non è scritta ${IT_MED} (${qit(p.quote)}).`,
  dose_without_drug: () => 'Una dose senza il nome del farmaco.',
  empty_source: () => 'Il farmaco ha una fonte vuota.',
  patient_conflict: (p) => (p.kind === 'species' ? `Le note indicano la specie ${qit(tr(SPECIES.it, p.value))}, ma secondo i dati del paziente la specie è ${tr(SPECIES.it, p.expected)}.`
    : p.kind === 'sex' ? `Le note indicano il sesso ${qit(tr(SEX.it, p.value))}, ma nei dati del paziente è indicato ${tr(SEX.it, p.expected)}.`
    : 'Gravidanza menzionata per un paziente maschio. Verifichi se si riferisce al proprietario o a un altro animale.'),
  patient_plausibility: () => 'Calore/estro menzionato per un paziente sterilizzato.',
  implausible_value: (p) => (p.kind === 'temperature' ? `La temperatura di ${p.value} °C è fuori dall'intervallo abituale per la specie ${tr(SPECIES.it, p.species)}. Errore di battitura?` : `${p.value} kg è un peso insolitamente alto per un gatto.`),
  derived_number_not_in_record: (p) => `${qit(p.value)} non è nella cartella clinica approvata.`,
  medication_missing_in_derived: (p) => `Il farmaco ${qit(p.drug)} della cartella clinica non è menzionato.`,
  status_conflicts_source: (p) => `Registrato come ${qit(tr(STATUS.it, p.status))}, ma il testo a cui rimanda questa voce indica: ${tr(STATUS.it, p.said)} (${qit(p.quote)}).`,
  owner_report_as_finding: (p) => `Registrato come reperto del veterinario, ma il testo a cui rimanda è quanto riferito dal proprietario (${qit(p.quote)}). Lo sposti nell'anamnesi o lo segni come riferito dal proprietario.`,
  notes_contradiction: (p) => `Per ${VITAL.it[p.vital] ?? p.vital} le note riportano ${p.kept} e ${p.others.join(' e ')}; la cartella clinica riporta ${p.kept}. Verifichi quale valore è corretto.`,
  other_animal_fact: (p) => `Questo proviene da una riga che riguarda un altro animale (${qit(p.quote)}). Verifichi che si riferisca a questo paziente.`,
  wrong_animal_line: (p) => `Questo proviene dalla riga ${p.line} (${qit(p.quote)}), assegnata a ${p.owner}. Non può comparire nella cartella clinica di ${p.patient}.`,
  unassigned_line_fact: (p) => `Questo proviene dalla riga ${p.line} (${qit(p.quote)}), non ancora assegnata a un animale. Assegni prima la riga.`,
  unassigned_line: (p) => `La riga ${p.line} (${qit(p.quote)}) non è assegnata a un animale né segnata come comune.`,
  label_mismatch: (p) => `La riga ${p.line} inizia con ${qit(`${p.label}:`)} ma è assegnata a ${p.shared ? 'tutti gli animali (comune)' : p.target}. Verifichi l'assegnazione.`,
};

export const FINDING_TEMPLATES: Record<Lang, Record<FindingRule, Template>> = { en: EN, de: DE, it: IT };

/**
 * The finding's message in `lang`. Falls back to the finding's own English `message` when the finding
 * carries no params or its rule has no template (e.g. a finding built outside the validators).
 */
export function findingMessage(f: Finding, lang: Lang = 'en'): string {
  if (!f.params) return f.message;
  const t = (FINDING_TEMPLATES[lang] ?? FINDING_TEMPLATES.en)[f.rule as FindingRule];
  return t ? t(f.params as P) : f.message;
}
