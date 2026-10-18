/**
 * Generates the synthetic eval cases 100–199 in EN, DE and IT.
 *   npx tsx src/cli/gen-cases.ts
 *
 * Every case is written line by line: each fact is one line of the notes, and its
 * source span is computed from where that line ends up, so a span can never point
 * at the wrong text. The fixture record is the gold standard: what a perfect
 * extractor returns. Expectations (missing fields, drugs, statuses) are derived
 * from it, so the model run is scored against the same truth.
 *
 * All patients and notes are invented. Medication lines deliberately carry no
 * dose numbers: the cases test whether a missing dose is flagged, not dosing.
 */
import { writeFileSync, readdirSync, unlinkSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader, type Span } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing } from '../validators.js';

type Lang = 'en' | 'de' | 'it';
type St = 'planned' | 'performed' | 'declined' | 'recommended' | 'dispensed' | 'prescribed';
type Role = 'owner_reported' | 'vet_observed' | 'vet_stated';

class Case {
  private lines: string[] = [];
  private len = 0;
  r: any = {
    schema_version: '0.2',
    patient: { name: null, species: null, breed: null, sex: null, neuter_status: null, age: null, weight: null },
    presenting_complaint: null, history: [],
    examination: { vitals: { temperature: null, heart_rate: null, respiratory_rate: null, weight: null, crt_seconds: null }, findings: [] },
    diagnostics: [], assessment: { text: null, differentials: [], source_spans: [] }, treatments: [], medications: [],
    plan: { follow_up: null, instructions: [] }, missing: [], uncertain: [],
  };
  extra: any = {};
  constructor(public id: string, public language: Lang, public header: any) {}
  /** Appends a line and returns the span of `part` inside it (the whole line by default). */
  line(text: string, part = text): Span[] {
    const start = this.len + (this.lines.length ? 1 : 0);
    this.lines.push(text); this.len = start + text.length;
    const i = text.indexOf(part); if (i < 0) throw new Error(`${this.id}: "${part}" not in "${text}"`);
    return [[start + i, start + i + part.length]];
  }
  plain(text: string) { this.line(text); return this; }
  complaint(text: string, role: Role = 'owner_reported') { this.r.presenting_complaint = { text, source_role: role, source_spans: this.line(text) }; return this; }
  history(finding: string, value: string, role: Role = 'owner_reported') { this.r.history.push({ finding, value, source_role: role, source_spans: this.line(value) }); return this; }
  vital(k: 'temperature' | 'heart_rate' | 'respiratory_rate' | 'weight', value: number, unit: string, text: string) { this.r.examination.vitals[k] = { value, unit, source_spans: this.line(text) }; return this; }
  finding(system: string, text: string) { this.r.examination.findings.push({ system, text, source_role: 'vet_observed', source_spans: this.line(text) }); return this; }
  diag(test: string, status: St, result: string | null, text: string) { this.r.diagnostics.push({ test, status, result, source_spans: this.line(text) }); return this; }
  assess(text: string) { this.r.assessment.text = text; this.r.assessment.source_spans = this.line(text); return this; }
  diff(text: string) { this.r.assessment.differentials.push({ text, source_spans: this.line(text) }); return this; }
  treat(type: 'procedure' | 'advice' | 'other', text: string, status: St) { this.r.treatments.push({ type, text, status, source_spans: this.line(text) }); return this; }
  med(m: { drug: string | null; class_as_written?: string | null; route?: string | null; frequency?: string | null; duration?: string | null; status: St }, text: string) {
    this.r.medications.push({ drug: m.drug, class_as_written: m.class_as_written ?? null, dose: null, dose_unit: null, route: m.route ?? null, frequency: m.frequency ?? null, duration: m.duration ?? null, status: m.status, source_spans: this.line(text) });
    return this;
  }
  follow(text: string, value: number | null, unit: 'hour' | 'day' | 'week' | 'month' | 'year' | null) { this.r.plan.follow_up = { text, interval: value == null ? null : { value, unit }, source_spans: this.line(text) }; return this; }
  instr(text: string) { this.r.plan.instructions.push({ text, source_spans: this.line(text) }); return this; }
  missing(field: string, reason: string) { this.r.missing.push({ field, reason }); return this; }
  notIn(...texts: string[]) { this.extra.must_not_contain = texts; return this; }
  build() {
    const notes = this.lines.join('\n');
    if (normalizeNotes(notes) !== notes) throw new Error(`${this.id}: notes change on normalisation`);
    const record = ClinicalRecord.parse(this.r);
    const header = PatientHeader.parse(this.header);
    const blocks = validateAll(record, notes, header).filter((f) => f.severity === 'block');
    if (blocks.length) throw new Error(`${this.id}: fixture has blocking findings ${JSON.stringify(blocks)}`);
    const statuses: Record<string, St> = {};
    record.treatments.forEach((t, i) => (statuses[`treatments[${i}]`] = t.status as St));
    record.medications.forEach((m, i) => (statuses[`medications[${i}]`] = m.status as St));
    const expect = {
      missing_includes: [...new Set([...requiredMissing(record, 'consult_report'), ...record.missing.map((m) => m.field)])],
      drugs: record.medications.map((m) => m.drug).filter(Boolean),
      assessment_text: record.assessment.text,
      ...(record.examination.vitals.temperature ? { temperature: record.examination.vitals.temperature.value } : {}),
      statuses, ...this.extra,
    };
    return { id: this.id, language: this.language, synthetic: true, header: this.header, notes, expect, fixture_record: record };
  }
}

const dog = (name: string, breed: string, age: number, sex: 'male' | 'female' = 'male', neuter: 'intact' | 'neutered' = 'neutered') => ({ name, species: 'dog', breed, sex, neuter_status: neuter, age: { value: age, unit: 'year' } });
const cat = (name: string, age: number, sex: 'male' | 'female' = 'female', neuter: 'intact' | 'neutered' = 'neutered') => ({ name, species: 'cat', breed: 'European Shorthair', sex, neuter_status: neuter, age: { value: age, unit: 'year' } });
const rabbit = (name: string, age: number) => ({ name, species: 'rabbit', sex: 'female', neuter_status: 'neutered', age: { value: age, unit: 'year' } });

type Scenario = { slug: string; build: Record<Lang, (c: Case) => Case>; header: Record<Lang, any> };
const S: Scenario[] = [
  { slug: 'lameness', header: { en: dog('Rex', 'Labrador', 5), de: dog('Balu', 'Labrador', 5), it: dog('Rocco', 'Labrador', 5) }, build: {
    en: (c) => c.complaint('lame right hind since 3 days').history('appetite', 'eating normally').vital('temperature', 38.6, 'C', 'T 38.6').finding('musculoskeletal', 'RH lameness grade 2/5, pain on stifle extension').assess('suspected cruciate injury RH').diag('radiographs right stifle', 'planned', null, 'rads R stifle planned under sedation next week').treat('advice', 'strict rest, lead walks only', 'recommended').follow('recheck 14 days', 14, 'day'),
    de: (c) => c.complaint('lahmt hinten rechts seit 3 Tagen').history('Appetit', 'frisst normal').vital('temperature', 38.6, 'C', 'T 38,6').finding('Bewegungsapparat', 'Lahmheit HR Grad 2/5, Schmerz bei Streckung Knie').assess('V. a. Kreuzbandriss HR').diag('Röntgen Knie rechts', 'planned', null, 'Röntgen Knie re. nächste Woche in Sedation geplant').treat('advice', 'strenge Ruhe, nur an der Leine', 'recommended').follow('WV in 14 Tagen', 14, 'day'),
    it: (c) => c.complaint('zoppia posteriore destra da 3 giorni').history('appetito', 'mangia normalmente').vital('temperature', 38.6, 'C', 'T 38,6').finding('apparato locomotore', 'zoppia PD grado 2/5, dolore all\'estensione del ginocchio').assess('sospetta rottura crociato PD').diag('radiografie ginocchio destro', 'planned', null, 'rx ginocchio dx in sedazione la prossima settimana').treat('advice', 'riposo assoluto, solo al guinzaglio', 'recommended').follow('controllo tra 14 giorni', 14, 'day'),
  } },
  { slug: 'otitis-cat', header: { en: cat('Mimi', 4), de: cat('Minka', 4), it: cat('Micia', 4) }, build: {
    en: (c) => c.complaint('scratching left ear for a week').finding('ears', 'left ear canal red, brown discharge').diag('ear cytology', 'performed', 'yeast ++', 'ear cytology: yeast ++').assess('otitis externa left').treat('procedure', 'ear flush left performed', 'performed').med({ drug: 'Surolan', route: 'auricular', frequency: 'twice daily', duration: '7 days', status: 'prescribed' }, 'Surolan auricular twice daily 7 days').follow('recheck 10 days', 10, 'day'),
    de: (c) => c.complaint('kratzt seit einer Woche am linken Ohr').finding('Ohren', 'Gehörgang li. gerötet, braunes Sekret').diag('Ohrzytologie', 'performed', 'Hefen ++', 'Ohrzytologie: Hefen ++').assess('Otitis externa links').treat('procedure', 'Ohrspülung li. durchgeführt', 'performed').med({ drug: 'Surolan', route: 'aurikulär', frequency: '2x täglich', duration: '7 Tage', status: 'prescribed' }, 'Surolan aurikulär 2x täglich 7 Tage').follow('WV in 10 Tagen', 10, 'day'),
    it: (c) => c.complaint('si gratta l\'orecchio sinistro da una settimana').finding('orecchie', 'condotto sx arrossato, secrezione marrone').diag('citologia auricolare', 'performed', 'lieviti ++', 'citologia auricolare: lieviti ++').assess('otite esterna sinistra').treat('procedure', 'lavaggio auricolare sx eseguito', 'performed').med({ drug: 'Surolan', route: 'auricolare', frequency: 'due volte al giorno', duration: '7 giorni', status: 'prescribed' }, 'Surolan auricolare due volte al giorno per 7 giorni').follow('controllo tra 10 giorni', 10, 'day'),
  } },
  { slug: 'diarrhoea-declined', header: { en: dog('Bella', 'Beagle', 3, 'female'), de: dog('Luna', 'Beagle', 3, 'female'), it: dog('Luna', 'Beagle', 3, 'female') }, build: {
    en: (c) => c.complaint('diarrhoea since yesterday, no vomiting').history('appetite', 'eating less').vital('temperature', 38.9, 'C', 'T 38.9').finding('abdomen', 'abdomen soft, mild discomfort').diag('faecal test', 'planned', null, 'faecal sample to bring tomorrow').diag('blood test', 'declined', null, 'bloods offered, owner declined').assess('acute diarrhoea').instr('bland diet 3 days, water always available').follow('call if not better in 48 hours', 48, 'hour'),
    de: (c) => c.complaint('Durchfall seit gestern, kein Erbrechen').history('Appetit', 'frisst weniger').vital('temperature', 38.9, 'C', 'T 38,9').finding('Abdomen', 'Abdomen weich, ggr. Schmerz').diag('Kotuntersuchung', 'planned', null, 'Kotprobe morgen mitbringen').diag('Blutuntersuchung', 'declined', null, 'Blutbild angeboten, Besitzer lehnt ab').assess('akuter Durchfall').instr('Schonkost 3 Tage, immer Wasser anbieten').follow('Anruf, wenn nach 48 Stunden nicht besser', 48, 'hour'),
    it: (c) => c.complaint('diarrea da ieri, nessun vomito').history('appetito', 'mangia meno').vital('temperature', 38.9, 'C', 'T 38,9').finding('addome', 'addome morbido, lieve fastidio').diag('esame feci', 'planned', null, 'campione di feci da portare domani').diag('esami del sangue', 'declined', null, 'esami del sangue proposti, il proprietario rifiuta').assess('diarrea acuta').instr('dieta leggera per 3 giorni, acqua sempre disponibile').follow('chiamare se non migliora in 48 ore', 48, 'hour'),
  } },
  { slug: 'cat-vaccine', header: { en: cat('Tiger', 2, 'male'), de: cat('Felix', 2, 'male'), it: cat('Romeo', 2, 'male') }, build: {
    en: (c) => c.complaint('annual vaccination, no concerns').finding('general', 'bright, good body condition').vital('heart_rate', 180, '/min', 'HR 180').med({ drug: 'RCP vaccine', route: 's.c.', status: 'performed' }, 'RCP vaccine given s.c. right flank').missing('medications[0].batch', 'vaccine batch not in the notes').follow('next vaccination in 1 year', 1, 'year'),
    de: (c) => c.complaint('jährliche Impfung, keine Beschwerden').finding('Allgemein', 'munter, guter Ernährungszustand').vital('heart_rate', 180, '/min', 'HF 180').med({ drug: 'RCP-Impfstoff', route: 's.c.', status: 'performed' }, 'RCP-Impfstoff s.c. rechte Flanke verabreicht').missing('medications[0].batch', 'Charge nicht in den Notizen').follow('nächste Impfung in 1 Jahr', 1, 'year'),
    it: (c) => c.complaint('vaccinazione annuale, nessun problema').finding('generale', 'vigile, buona condizione corporea').vital('heart_rate', 180, '/min', 'FC 180').med({ drug: 'vaccino trivalente RCP', route: 's.c.', status: 'performed' }, 'vaccino trivalente RCP s.c. fianco destro eseguito').missing('medications[0].batch', 'lotto non presente nelle note').follow('prossimo vaccino tra 1 anno', 1, 'year'),
  } },
  { slug: 'fleas', header: { en: dog('Max', 'Jack Russell', 6), de: dog('Max', 'Jack Russell', 6), it: dog('Pippo', 'Jack Russell', 6) }, build: {
    en: (c) => c.complaint('itching for 2 weeks, worse at the tail base').finding('skin', 'papules and hair loss at tail base, flea dirt on comb').assess('flea allergy dermatitis suspected').med({ drug: 'flea spot-on', route: 'topical', frequency: 'monthly', status: 'dispensed' }, 'flea spot-on dispensed, topical, monthly').instr('treat all pets in the household and wash bedding').follow('recheck 4 weeks', 4, 'week'),
    de: (c) => c.complaint('Juckreiz seit 2 Wochen, v. a. am Schwanzansatz').finding('Haut', 'Papeln und Haarverlust am Schwanzansatz, Flohkot im Kamm').assess('V. a. Flohallergiedermatitis').med({ drug: 'Floh-Spot-on', route: 'topisch', frequency: 'monatlich', status: 'dispensed' }, 'Floh-Spot-on abgegeben, topisch, monatlich').instr('alle Tiere im Haushalt behandeln, Liegeplätze waschen').follow('WV in 4 Wochen', 4, 'week'),
    it: (c) => c.complaint('prurito da 2 settimane, peggio alla base della coda').finding('cute', 'papule e alopecia alla base della coda, feci di pulce al pettine').assess('sospetta dermatite allergica da pulci').med({ drug: 'antiparassitario spot-on', route: 'topica', frequency: 'mensile', status: 'dispensed' }, 'antiparassitario spot-on consegnato, uso topico, mensile').instr('trattare tutti gli animali di casa e lavare le cucce').follow('controllo tra 4 settimane', 4, 'week'),
  } },
  { slug: 'rabbit-anorexia', header: { en: rabbit('Coco', 5), de: rabbit('Hoppel', 5), it: rabbit('Nuvola', 5) }, build: {
    en: (c) => c.complaint('not eating since this morning, few droppings').vital('temperature', 38.4, 'C', 'T 38.4').finding('abdomen', 'gut sounds reduced, stomach firm').diff('gastrointestinal stasis').diff('dental disease').diag('dental check', 'performed', 'molar spurs not seen', 'oral exam: molar spurs not seen').instr('syringe feeding critical care food, offer fresh hay').follow('recheck tomorrow morning', null, null),
    de: (c) => c.complaint('frisst seit heute Morgen nicht, wenig Kot').vital('temperature', 38.4, 'C', 'T 38,4').finding('Abdomen', 'Darmgeräusche reduziert, Magen fest').diff('gastrointestinale Stase').diff('Zahnerkrankung').diag('Zahnkontrolle', 'performed', 'keine Backenzahnspitzen gesehen', 'Maulhöhle: keine Backenzahnspitzen gesehen').instr('Päppelbrei mit der Spritze, frisches Heu anbieten').follow('WV morgen früh', null, null),
    it: (c) => c.complaint('non mangia da stamattina, poche feci').vital('temperature', 38.4, 'C', 'T 38,4').finding('addome', 'borborigmi ridotti, stomaco duro').diff('stasi gastrointestinale').diff('patologia dentale').diag('controllo dentale', 'performed', 'punte dei molari non viste', 'esame cavo orale: punte dei molari non viste').instr('alimentazione assistita con siringa, offrire fieno fresco').follow('controllo domani mattina', null, null),
  } },
  { slug: 'suture-removal', header: { en: dog('Nala', 'Mixed breed', 1, 'female'), de: dog('Emma', 'Mischling', 1, 'female'), it: dog('Kira', 'Meticcio', 1, 'female') }, build: {
    en: (c) => c.complaint('suture removal after spay 10 days ago').finding('wound', 'incision healed, no swelling').treat('procedure', 'sutures removed', 'performed').assess('uneventful healing'),
    de: (c) => c.complaint('Fäden ziehen nach Kastration vor 10 Tagen').finding('Wunde', 'Naht verheilt, keine Schwellung').treat('procedure', 'Fäden gezogen', 'performed').assess('komplikationslose Heilung'),
    it: (c) => c.complaint('rimozione punti dopo sterilizzazione 10 giorni fa').finding('ferita', 'incisione guarita, nessun gonfiore').treat('procedure', 'punti rimossi', 'performed').assess('guarigione regolare'),
  } },
  { slug: 'senior-weight-loss', header: { en: cat('Luna', 14), de: cat('Mausi', 14), it: cat('Pallina', 14) }, build: {
    en: (c) => c.complaint('losing weight over 3 months, drinking more').history('appetite', 'good appetite').vital('weight', 3.9, 'kg', 'weight 3.9 kg').finding('general', 'thin, coat unkempt').finding('neck', 'small nodule left thyroid area').diag('blood test incl. T4', 'performed', null, 'bloods incl. T4 taken today').diff('hyperthyroidism').diff('chronic kidney disease').follow('call with results', null, null),
    de: (c) => c.complaint('nimmt seit 3 Monaten ab, trinkt mehr').history('Appetit', 'guter Appetit').vital('weight', 3.9, 'kg', 'KGW 3,9 kg').finding('Allgemein', 'mager, Fell ungepflegt').finding('Hals', 'kleiner Knoten im Bereich Schilddrüse li.').diag('Blutuntersuchung inkl. T4', 'performed', null, 'Blut inkl. T4 heute entnommen').diff('Hyperthyreose').diff('chronische Nierenerkrankung').follow('Anruf mit Ergebnissen', null, null),
    it: (c) => c.complaint('perde peso da 3 mesi, beve di più').history('appetito', 'appetito buono').vital('weight', 3.9, 'kg', 'peso 3,9 kg').finding('generale', 'magra, mantello trascurato').finding('collo', 'piccolo nodulo zona tiroide sx').diag('esami del sangue con T4', 'performed', null, 'prelievo con T4 eseguito oggi').diff('ipertiroidismo').diff('malattia renale cronica').follow('telefonata con i risultati', null, null),
  } },
  { slug: 'dental-declined', header: { en: dog('Toby', 'Yorkshire Terrier', 9), de: dog('Bobby', 'Yorkshire Terrier', 9), it: dog('Briciola', 'Yorkshire Terrier', 9, 'female') }, build: {
    en: (c) => c.complaint('bad breath').finding('dental', 'heavy tartar, gingivitis, 108 mobile').assess('periodontal disease').treat('procedure', 'dental cleaning under anaesthesia recommended', 'recommended').treat('procedure', 'owner declined anaesthesia for now', 'declined').instr('daily tooth brushing'),
    de: (c) => c.complaint('Mundgeruch').finding('Zähne', 'hgr. Zahnstein, Gingivitis, 108 locker').assess('Parodontitis').treat('procedure', 'Zahnsanierung in Narkose empfohlen', 'recommended').treat('procedure', 'Besitzer lehnt Narkose vorerst ab', 'declined').instr('tägliches Zähneputzen'),
    it: (c) => c.complaint('alito cattivo').finding('denti', 'tartaro abbondante, gengivite, 108 mobile').assess('malattia parodontale').treat('procedure', 'detartrasi in anestesia consigliata', 'recommended').treat('procedure', 'il proprietario per ora rifiuta l\'anestesia', 'declined').instr('spazzolare i denti ogni giorno'),
  } },
  { slug: 'cough', header: { en: dog('Buddy', 'Border Collie', 2), de: dog('Rocky', 'Border Collie', 2), it: dog('Ares', 'Border Collie', 2) }, build: {
    en: (c) => c.complaint('honking cough for 4 days after boarding kennel').vital('temperature', 39.2, 'C', 'T 39.2').finding('respiratory', 'cough on tracheal palpation, lungs clear').assess('kennel cough suspected').instr('rest, no collar, harness only').follow('recheck in 7 days if not better', 7, 'day'),
    de: (c) => c.complaint('trockener Husten seit 4 Tagen nach Hundepension').vital('temperature', 39.2, 'C', 'T 39,2').finding('Atmung', 'Husten bei Trachealpalpation, Lunge frei').assess('V. a. Zwingerhusten').instr('Ruhe, kein Halsband, nur Geschirr').follow('WV in 7 Tagen, wenn nicht besser', 7, 'day'),
    it: (c) => c.complaint('tosse secca da 4 giorni dopo la pensione').vital('temperature', 39.2, 'C', 'T 39,2').finding('respiratorio', 'tosse alla palpazione tracheale, polmoni puliti').assess('sospetta tosse dei canili').instr('riposo, niente collare, solo pettorina').follow('controllo tra 7 giorni se non migliora', 7, 'day'),
  } },
  { slug: 'cystitis-cat', header: { en: cat('Oscar', 6, 'male'), de: cat('Leo', 6, 'male'), it: cat('Leone', 6, 'male') }, build: {
    en: (c) => c.complaint('straining in litter tray, small amounts of urine').finding('abdomen', 'bladder small, not painful').diag('urinalysis', 'performed', 'pH 6.5, blood +', 'UA: pH 6.5, blood +').assess('cystitis suspected, not blocked').instr('wet food, more water bowls').follow('come back at once if no urine', null, null),
    de: (c) => c.complaint('presst im Katzenklo, kleine Harnmengen').finding('Abdomen', 'Blase klein, nicht schmerzhaft').diag('Harnuntersuchung', 'performed', 'pH 6,5, Blut +', 'Harn: pH 6,5, Blut +').assess('V. a. Zystitis, nicht verlegt').instr('Nassfutter, mehr Wassernäpfe').follow('sofort kommen, wenn kein Harn', null, null),
    it: (c) => c.complaint('si sforza nella lettiera, piccole quantità di urina').finding('addome', 'vescica piccola, non dolente').diag('esame urine', 'performed', 'pH 6,5, sangue +', 'esame urine: pH 6,5, sangue +').assess('sospetta cistite, non ostruito').instr('cibo umido, più ciotole d\'acqua').follow('tornare subito se non urina', null, null),
  } },
  { slug: 'other-pet', header: { en: dog('Daisy', 'Poodle', 4, 'female'), de: dog('Lilly', 'Pudel', 4, 'female'), it: dog('Maya', 'Barboncino', 4, 'female') }, build: {
    en: (c) => c.complaint('vomited twice this morning').plain('owner says their other dog had diarrhoea last week').vital('temperature', 38.7, 'C', 'T 38.7').finding('abdomen', 'abdomen non-painful').assess('mild gastritis').instr('small meals for 2 days').notIn('diarrhoea'),
    de: (c) => c.complaint('heute Morgen 2x erbrochen').plain('Besitzerin erzählt, der andere Hund hatte letzte Woche Durchfall').vital('temperature', 38.7, 'C', 'T 38,7').finding('Abdomen', 'Abdomen nicht schmerzhaft').assess('leichte Gastritis').instr('kleine Mahlzeiten für 2 Tage').notIn('durchfall'),
    it: (c) => c.complaint('ha vomitato 2 volte stamattina').plain('la proprietaria dice che l\'altro cane ha avuto diarrea la settimana scorsa').vital('temperature', 38.7, 'C', 'T 38,7').finding('addome', 'addome non dolente').assess('gastrite lieve').instr('pasti piccoli per 2 giorni').notIn('diarrea'),
  } },
  { slug: 'planned-not-done', header: { en: dog('Milo', 'Golden Retriever', 8), de: dog('Benno', 'Golden Retriever', 8), it: dog('Zeus', 'Golden Retriever', 8) }, build: {
    en: (c) => c.complaint('lump on left flank noticed 2 weeks ago').finding('skin', 'soft mobile mass left flank, about 2 cm').diag('fine needle aspirate', 'planned', null, 'FNA at next visit').assess('lipoma suspected').follow('recheck 1 month', 1, 'month'),
    de: (c) => c.complaint('Knoten an der linken Flanke seit 2 Wochen bemerkt').finding('Haut', 'weiche verschiebliche Umfangsvermehrung li. Flanke, ca. 2 cm').diag('Feinnadelaspiration', 'planned', null, 'FNA beim nächsten Termin').assess('V. a. Lipom').follow('WV in 1 Monat', 1, 'month'),
    it: (c) => c.complaint('nodulo sul fianco sinistro notato 2 settimane fa').finding('cute', 'massa morbida mobile fianco sx, circa 2 cm').diag('agoaspirato', 'planned', null, 'agoaspirato alla prossima visita').assess('sospetto lipoma').follow('controllo tra 1 mese', 1, 'month'),
  } },
  { slug: 'eye-no-frequency', header: { en: cat('Bella', 3), de: cat('Lucy', 3), it: cat('Kitty', 3) }, build: {
    en: (c) => c.complaint('right eye red and squinting since yesterday').finding('eyes', 'conjunctiva right red, discharge clear').diag('fluorescein stain', 'performed', 'negative', 'fluorescein right eye negative').assess('conjunctivitis right').med({ drug: 'Isathal', route: 'ocular', duration: '7 days', status: 'prescribed' }, 'Isathal eye drops right eye for 7 days').follow('recheck in 1 week', 1, 'week'),
    de: (c) => c.complaint('rechtes Auge seit gestern rot und zugekniffen').finding('Augen', 'Konjunktiva re. gerötet, Sekret klar').diag('Fluoreszeintest', 'performed', 'negativ', 'Fluoreszein re. negativ').assess('Konjunktivitis rechts').med({ drug: 'Isathal', route: 'okulär', duration: '7 Tage', status: 'prescribed' }, 'Isathal Augentropfen re. für 7 Tage').follow('WV in 1 Woche', 1, 'week'),
    it: (c) => c.complaint('occhio destro rosso e socchiuso da ieri').finding('occhi', 'congiuntiva dx arrossata, secrezione chiara').diag('test alla fluoresceina', 'performed', 'negativo', 'fluoresceina occhio dx negativa').assess('congiuntivite destra').med({ drug: 'Isathal', route: 'oculare', duration: '7 giorni', status: 'prescribed' }, 'Isathal collirio occhio dx per 7 giorni').follow('controllo tra 1 settimana', 1, 'week'),
  } },
];

const here = dirname(fileURLToPath(import.meta.url));
const dir = join(here, '..', '..', 'eval', 'cases');
for (const f of readdirSync(dir)) if (/^1\d\d-gen-/.test(f)) unlinkSync(join(dir, f));
let n = 100;
for (const sc of S) for (const lang of ['en', 'de', 'it'] as Lang[]) {
  const id = `${n}-gen-${sc.slug}-${lang}`;
  const c = sc.build[lang](new Case(id, lang, sc.header[lang]));
  writeFileSync(join(dir, `${id}.json`), JSON.stringify(c.build(), null, 2) + '\n');
  n++;
}
console.log(`wrote ${n - 100} cases`);
