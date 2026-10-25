/**
 * Generates the synthetic eval cases 100–199 and 400–499 (see S and S2 below) in EN, DE and IT,
 * and the seeded-error cases 200–299 (see SEEDED below).
 *   npm run gen-cases
 *
 * Every case is written line by line: each fact is one line of the notes, and its
 * source span is computed from where that line ends up, so a span can never point
 * at the wrong text. The fixture record is the gold standard: what a perfect
 * extractor returns. Expectations (missing fields, drugs, statuses) are derived
 * from it, so the model run is scored against the same truth.
 *
 * Multi-pet consultations (eval/cases-multi, 300–399; see MULTI below) are written the same way,
 * one line at a time, into every patient's record at once.
 *
 * All patients and notes are invented. Most medication lines deliberately carry no
 * dose numbers: the cases test whether a missing dose is flagged, not dosing. Where a
 * line does write a dose, the gold record carries exactly that dose and nothing else.
 *
 * A gold record must raise no finding at all, not even a warning (`strict`); only the
 * patients' cases inside a multi-pet consultation are checked on the consultation instead.
 */
import { writeFileSync, readdirSync, unlinkSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader, type Span } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing } from '../validators.js';
import { makeConsultation, validateConsultation, suggestAssignments, SHARED } from '../multi-pet.js';

type Lang = 'en' | 'de' | 'it';
type St = 'planned' | 'performed' | 'declined' | 'recommended' | 'dispensed' | 'prescribed';
type Role = 'owner_reported' | 'vet_observed' | 'vet_stated';

class Case {
  /** Read by MultiCase, which writes the same lines into every patient's case. */
  lines: string[] = [];
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
  /** Seeded errors: the finding (rule at field) the deliberately wrong record must raise. */
  seeded: { rule: string; field: string }[] = [];
  comment: string | null = null;
  constructor(public id: string, public language: Lang, public header: any, private strict = true) {}
  /** Written before the next line's text (a multi-pet name label such as "Bella: "); never part of a span. */
  prefix = '';
  /** Appends a line and returns the span of `part` inside it (the whole line by default). */
  line(text: string, part = text): Span[] {
    const start = this.len + (this.lines.length ? 1 : 0);
    const p = this.prefix; text = p + text;
    this.lines.push(text); this.len = start + text.length;
    const i = text.indexOf(part, p.length); if (i < 0) throw new Error(`${this.id}: "${part}" not in "${text}"`);
    return [[start + i, start + i + part.length]];
  }
  plain(text: string) { this.line(text); return this; }
  complaint(text: string, role: Role = 'owner_reported') { this.r.presenting_complaint = { text, source_role: role, source_spans: this.line(text) }; return this; }
  history(finding: string, value: string, role: Role = 'owner_reported') { this.r.history.push({ finding, value, source_role: role, source_spans: this.line(value) }); return this; }
  vital(k: 'temperature' | 'heart_rate' | 'respiratory_rate' | 'weight' | 'crt_seconds', value: number, unit: string, text: string) { this.r.examination.vitals[k] = { value, unit, source_spans: this.line(text) }; return this; }
  finding(system: string, text: string) { this.r.examination.findings.push({ system, text, source_role: 'vet_observed', source_spans: this.line(text) }); return this; }
  diag(test: string, status: St, result: string | null, text: string) { this.r.diagnostics.push({ test, status, result, source_spans: this.line(text) }); return this; }
  assess(text: string) { this.r.assessment.text = text; this.r.assessment.source_spans = this.line(text); return this; }
  /** Seeded errors only: an assessment with no source in the notes (an added diagnosis). */
  assessUnsourced(text: string) { this.r.assessment.text = text; this.r.assessment.source_spans = []; return this; }
  diff(text: string) { this.r.assessment.differentials.push({ text, source_spans: this.line(text) }); return this; }
  treat(type: 'procedure' | 'advice' | 'other', text: string, status: St) { this.r.treatments.push({ type, text, status, source_spans: this.line(text) }); return this; }
  med(m: { drug: string | null; class_as_written?: string | null; dose?: number | null; dose_unit?: string | null; route?: string | null; frequency?: string | null; duration?: string | null; status: St }, text: string) {
    this.r.medications.push({ drug: m.drug, class_as_written: m.class_as_written ?? null, dose: m.dose ?? null, dose_unit: m.dose_unit ?? null, route: m.route ?? null, frequency: m.frequency ?? null, duration: m.duration ?? null, status: m.status, source_spans: this.line(text) });
    return this;
  }
  follow(text: string, value: number | null, unit: 'hour' | 'day' | 'week' | 'month' | 'year' | null) { this.r.plan.follow_up = { text, interval: value == null ? null : { value, unit }, source_spans: this.line(text) }; return this; }
  instr(text: string) { this.r.plan.instructions.push({ text, source_spans: this.line(text) }); return this; }
  missing(field: string, reason: string) { this.r.missing.push({ field, reason }); return this; }
  /** Text that must not appear in the record outside `uncertain` (lower case: the check runs on the lower-cased record). */
  notIn(...texts: string[]) { this.extra.must_not_contain = [...(this.extra.must_not_contain ?? []), ...texts]; return this; }
  /**
   * An `uncertain` entry pointing at text already written (each part must occur exactly once
   * in the notes so far). Used for contradictions and possible typos: the gold record keeps
   * what was written and flags the conflict; it never resolves it.
   */
  unsure(field: string, reason: string, ...parts: string[]) {
    const notes = this.lines.join('\n');
    const spans: Span[] = parts.map((p) => {
      const i = notes.indexOf(p);
      if (i < 0 || notes.indexOf(p, i + 1) >= 0) throw new Error(`${this.id}: "${p}" must occur exactly once in the notes`);
      return [i, i + p.length];
    });
    this.r.uncertain.push({ field, original_text: parts.join(' / '), reason, source_spans: spans });
    return this;
  }
  /**
   * Marks the record as deliberately wrong: `rule` must be raised at `field`. A seeded case keeps
   * only `expect.must_flag`; it is not a gold record, so no other expectations are derived from it.
   */
  seed(rule: string, field: string, comment: string) { this.seeded.push({ rule, field }); this.comment = comment; return this; }
  build() {
    const notes = this.lines.join('\n');
    if (normalizeNotes(notes) !== notes) throw new Error(`${this.id}: notes change on normalisation`);
    const record = ClinicalRecord.parse(this.r);
    const header = PatientHeader.parse(this.header);
    if (this.seeded.length) {
      // The seeded error must be the only thing wrong: exactly the seeded findings, nothing else.
      const got = validateAll(record, notes, header).map((f) => `${f.rule}@${f.field}`).sort();
      const want = this.seeded.map((s) => `${s.rule}@${s.field}`).sort();
      if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${this.id}: seeded findings ${JSON.stringify(got)} ≠ ${JSON.stringify(want)}`);
      return { id: this.id, language: this.language, synthetic: true, notes_comment: this.comment, header: this.header, notes, expect: { must_flag: [...new Set(this.seeded.map((s) => s.rule))] }, fixture_record: record };
    }
    const all = validateAll(record, notes, header);
    const bad = this.strict ? all : all.filter((f) => f.severity === 'block');
    if (bad.length) throw new Error(`${this.id}: fixture has ${this.strict ? '' : 'blocking '}findings ${JSON.stringify(bad.map((f) => `${f.rule}@${f.field} (${f.severity})`))}`);
    const statuses: Record<string, St> = {};
    record.treatments.forEach((t, i) => (statuses[`treatments[${i}]`] = t.status as St));
    record.medications.forEach((m, i) => (statuses[`medications[${i}]`] = m.status as St));
    record.diagnostics.forEach((d, i) => (statuses[`diagnostics[${i}]`] = d.status as St));
    const expect = {
      missing_includes: [...new Set([...requiredMissing(record, 'consult_report', header), ...record.missing.map((m) => m.field)])],
      drugs: record.medications.map((m) => m.drug).filter(Boolean),
      assessment_text: record.assessment.text,
      ...(record.examination.vitals.temperature ? { temperature: record.examination.vitals.temperature.value } : {}),
      statuses,
      ...(record.uncertain.length ? { uncertain_min: record.uncertain.length } : {}),
      ...this.extra,
    };
    return { id: this.id, language: this.language, synthetic: true, header: this.header, notes, expect, fixture_record: record };
  }
}

const dog = (name: string, breed: string, age: number, sex: 'male' | 'female' = 'male', neuter: 'intact' | 'neutered' = 'neutered') => ({ name, species: 'dog', breed, sex, neuter_status: neuter, age: { value: age, unit: 'year' } });
const cat = (name: string, age: number, sex: 'male' | 'female' = 'female', neuter: 'intact' | 'neutered' = 'neutered') => ({ name, species: 'cat', breed: 'European Shorthair', sex, neuter_status: neuter, age: { value: age, unit: 'year' } });
const rabbit = (name: string, age: number) => ({ name, species: 'rabbit', sex: 'female', neuter_status: 'neutered', age: { value: age, unit: 'year' } });
const ferret = (name: string, age: number) => ({ name, species: 'ferret', sex: 'male', neuter_status: 'neutered', age: { value: age, unit: 'year' } });
const bird = (name: string, age: number) => ({ name, species: 'bird', breed: 'Budgerigar', sex: 'male', age: { value: age, unit: 'year' } });
const guineaPig = (name: string, age: number) => ({ name, species: 'other', breed: 'Guinea pig', sex: 'female', neuter_status: 'intact', age: { value: age, unit: 'year' } });
const reptile = (name: string, age: number) => ({ name, species: 'reptile', breed: 'Bearded dragon', sex: 'male', age: { value: age, unit: 'year' } });
const puppy = (name: string, weeks: number) => ({ name, species: 'dog', breed: 'Golden Retriever', sex: 'female', neuter_status: 'intact', age: { value: weeks, unit: 'week' } });
const horse = (name: string, breed: string, age: number, sex: 'male' | 'female', neuter: 'intact' | 'neutered') => ({ name, species: 'horse', breed, sex, neuter_status: neuter, age: { value: age, unit: 'year' } });

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
  // ---- 142+: harder cases. Shorthand, typos, contradictions, owner vs vet, statuses, other animals, vague numbers, exotics. ----
  { slug: 'shorthand-gastro', header: { en: dog('Ozzy', 'Cocker Spaniel', 4), de: dog('Sammy', 'Cocker Spaniel', 4), it: dog('Birba', 'Cocker Spaniel', 4, 'female') }, build: {
    en: (c) => c.complaint('V+ x2 since yesterday, D-').history('appetite', 'inappetent since yesterday').finding('general', 'BAR, MM pk, CRT<2').vital('temperature', 38.8, 'C', 'T 38.8').vital('heart_rate', 100, '/min', 'HR 100').vital('respiratory_rate', 24, '/min', 'RR 24').finding('abdomen', 'abd soft, NAD on palp').assess('susp. acute gastritis').med({ drug: 'Cerenia', status: 'performed' }, 'Cerenia given').instr('bland diet, small meals').follow('recheck if V persists', null, null),
    de: (c) => c.complaint('ggr. Erbrechen seit gestern, 2x, kein Durchfall').history('Appetit', 'frisst schlecht seit gestern').finding('Allgemein', 'AZ ungestört, SH rosa, KFZ<2').vital('temperature', 38.8, 'C', 'T 38,8').vital('heart_rate', 100, '/min', 'HF 100').vital('respiratory_rate', 24, '/min', 'AF 24').finding('Abdomen', 'Abd. weich, obB').assess('V. a. akute Gastritis').med({ drug: 'Cerenia', status: 'performed' }, 'Cerenia verabreicht').instr('Schonkost, kleine Portionen').follow('WV bei anhaltendem Erbrechen', null, null),
    it: (c) => c.complaint('vomito 2v da ieri, feci nn').history('appetito', 'inappetente da ieri').finding('generale', 'vivace, mucose rosee, TRC<2').vital('temperature', 38.8, 'C', 'T 38,8').vital('heart_rate', 100, '/min', 'FC 100').vital('respiratory_rate', 24, '/min', 'FR 24').finding('addome', 'addome trattabile, non dolente').assess('sospetta gastrite acuta').med({ drug: 'Cerenia', status: 'performed' }, 'Cerenia somministrato').instr('dieta leggera, pasti piccoli').follow('ricontrollo se il vomito persiste', null, null),
  } },
  { slug: 'contradiction-vomiting', header: { en: cat('Nina', 7), de: cat('Susi', 7), it: cat('Mia', 7) }, build: {
    en: (c) => c.complaint('eating poorly for 2 days').history('vomiting', 'no vomiting per owner').vital('temperature', 38.9, 'C', 'T 38.9').vital('weight', 4.2, 'kg', 'wt 4.2 kg').finding('oral', 'mild gingivitis').finding('abdomen', 'abdomen soft, not painful').history('vomiting', 'at the end owner says she vomited once this morning')
      .unsure('history', 'owner first denied vomiting, later reported one episode this morning; not resolved in the notes', 'no vomiting per owner', 'at the end owner says she vomited once this morning')
      .diag('blood test', 'planned', null, 'bloods next visit if still eating poorly').follow('recheck in a few days', null, null),
    de: (c) => c.complaint('frisst seit 2 Tagen schlecht').history('Erbrechen', 'laut Besitzerin kein Erbrechen').vital('temperature', 38.9, 'C', 'T 38,9').vital('weight', 4.2, 'kg', 'KGW 4,2 kg').finding('Maulhöhle', 'ggr. Gingivitis').finding('Abdomen', 'Abdomen weich, nicht schmerzhaft').history('Erbrechen', 'am Ende sagt Besitzerin doch, heute früh 1x erbrochen')
      .unsure('history', 'Besitzerin verneint zuerst Erbrechen, berichtet später 1x heute früh; in den Notizen nicht geklärt', 'laut Besitzerin kein Erbrechen', 'am Ende sagt Besitzerin doch, heute früh 1x erbrochen')
      .diag('Blutuntersuchung', 'planned', null, 'Blut beim nächsten Termin, falls sie weiter schlecht frisst').follow('WV in ein paar Tagen', null, null),
    it: (c) => c.complaint('mangia poco da 2 giorni').history('vomito', 'nessun vomito secondo la proprietaria').vital('temperature', 38.9, 'C', 'T 38,9').vital('weight', 4.2, 'kg', 'peso 4,2 kg').finding('cavo orale', 'lieve gengivite').finding('addome', 'addome morbido, non dolente').history('vomito', 'alla fine la proprietaria dice che ha vomitato 1 volta stamattina')
      .unsure('history', 'la proprietaria prima nega il vomito, poi riferisce un episodio stamattina; non chiarito nelle note', 'nessun vomito secondo la proprietaria', 'alla fine la proprietaria dice che ha vomitato 1 volta stamattina')
      .diag('esami del sangue', 'planned', null, 'esami del sangue alla prossima visita se continua a mangiare poco').follow('ricontrollo tra qualche giorno', null, null),
  } },
  { slug: 'owner-vs-vet-lameness', header: { en: dog('Finn', 'Australian Shepherd', 3), de: dog('Nero', 'Australian Shepherd', 3), it: dog('Thor', 'Pastore australiano', 3) }, build: {
    en: (c) => c.complaint('owner reports limping LF on and off for 1 week').history('pain', 'owner thinks he is not in pain').history('activity', 'limping worse after ball games').finding('musculoskeletal', 'no lameness seen at walk or trot').finding('musculoskeletal', 'mild discomfort on flexion L carpus').finding('musculoskeletal', 'no swelling, no heat').diff('soft tissue injury L carpus').diag('radiographs left carpus', 'declined', null, 'rads L carpus offered, O declined for now').treat('advice', 'no ball games for now', 'recommended').instr('owner to film the dog when limping').follow('recheck next week', null, null),
    de: (c) => c.complaint('laut Besitzer lahmt er vorne links immer wieder, seit 1 Woche').history('Schmerz', 'Besitzer meint, er hat keine Schmerzen').history('Aktivität', 'nach Ballspielen schlimmer').finding('Bewegungsapparat', 'im Schritt und Trab keine Lahmheit sichtbar').finding('Bewegungsapparat', 'ggr. Schmerz bei Beugung Karpus li.').finding('Bewegungsapparat', 'keine Schwellung, nicht warm').diff('Weichteilverletzung Karpus li.').diag('Röntgen Karpus links', 'declined', null, 'Röntgen Karpus li. angeboten, Besitzer lehnt vorerst ab').treat('advice', 'vorerst keine Ballspiele', 'recommended').instr('Besitzer filmt den Hund, wenn er lahmt').follow('WV nächste Woche', null, null),
    it: (c) => c.complaint('il proprietario riferisce zoppia anteriore sx intermittente da 1 settimana').history('dolore', 'secondo il proprietario non ha dolore').history('attività', 'peggiora dopo i giochi con la palla').finding('apparato locomotore', 'nessuna zoppia al passo e al trotto').finding('apparato locomotore', 'lieve fastidio alla flessione del carpo sx').finding('apparato locomotore', 'nessun gonfiore, non caldo').diff('lesione dei tessuti molli carpo sx').diag('radiografie carpo sinistro', 'declined', null, 'rx carpo sx proposte, il proprietario per ora rifiuta').treat('advice', 'per ora niente giochi con la palla', 'recommended').instr('il proprietario filma il cane quando zoppica').follow('controllo la settimana prossima', null, null),
  } },
  { slug: 'pruritus-declined-dispensed', header: { en: dog('Ben', 'West Highland White Terrier', 5), de: dog('Charly', 'West Highland White Terrier', 5), it: dog('Ugo', 'West Highland White Terrier', 5) }, build: {
    en: (c) => c.complaint('itchy paws and ears for 1 month').finding('skin', 'interdigital erythema all 4 feet, both ears red').diag('tape cytology paws', 'performed', 'cocci +', 'tape cytology paws: cocci +').diag('allergy blood test', 'declined', null, 'allergy blood test offered, O declined (cost)').diag('skin scrape', 'planned', null, 'skin scrape planned at recheck').diff('atopic dermatitis').diff('food allergy').med({ drug: 'chlorhexidine shampoo', frequency: 'twice weekly', status: 'dispensed' }, 'chlorhexidine shampoo dispensed, twice weekly').med({ drug: 'Apoquel', status: 'declined' }, 'Apoquel discussed, O prefers not to start yet').treat('advice', 'elimination diet recommended', 'recommended').follow('recheck 3 weeks', 3, 'week'),
    de: (c) => c.complaint('Juckreiz Pfoten und Ohren seit 1 Monat').finding('Haut', 'interdigitales Erythem an allen 4 Pfoten, beide Ohren gerötet').diag('Tesa-Zytologie Pfoten', 'performed', 'Kokken +', 'Tesa-Zytologie Pfoten: Kokken +').diag('Allergietest Blut', 'declined', null, 'Allergietest (Blut) angeboten, Besitzerin lehnt ab (Kosten)').diag('Hautgeschabsel', 'planned', null, 'Hautgeschabsel bei der WV geplant').diff('atopische Dermatitis').diff('Futtermittelallergie').med({ drug: 'Chlorhexidin-Shampoo', frequency: '2x pro Woche', status: 'dispensed' }, 'Chlorhexidin-Shampoo abgegeben, 2x pro Woche').med({ drug: 'Apoquel', status: 'declined' }, 'Apoquel besprochen, Besitzerin möchte noch nicht beginnen').treat('advice', 'Eliminationsdiät empfohlen', 'recommended').follow('WV in 3 Wochen', 3, 'week'),
    it: (c) => c.complaint('prurito zampe e orecchie da 1 mese').finding('cute', 'eritema interdigitale su tutte e 4 le zampe, orecchie arrossate').diag('citologia scotch zampe', 'performed', 'cocchi +', 'citologia scotch zampe: cocchi +').diag('test allergologico su sangue', 'declined', null, 'test allergologico su sangue proposto, la proprietaria rifiuta (costi)').diag('raschiato cutaneo', 'planned', null, 'raschiato cutaneo previsto al controllo').diff('dermatite atopica').diff('allergia alimentare').med({ drug: 'shampoo alla clorexidina', frequency: '2 volte a settimana', status: 'dispensed' }, 'shampoo alla clorexidina consegnato, 2 volte a settimana').med({ drug: 'Apoquel', status: 'declined' }, 'Apoquel discusso, la proprietaria preferisce non iniziare per ora').treat('advice', 'dieta di eliminazione consigliata', 'recommended').follow('controllo tra 3 settimane', 3, 'week'),
  } },
  { slug: 'other-cat-household', header: { en: cat('Lola', 3), de: cat('Kira', 3), it: cat('Penny', 3) }, build: {
    en: (c) => c.complaint('sneezing for 3 days, clear nasal discharge').history('appetite', 'eating normally').plain('other cat at home (Pepper) coughing since last week, not examined today').plain('Pepper 5.1 kg, vaccinated last month per owner').vital('temperature', 38.6, 'C', 'T 38.6').vital('weight', 3.8, 'kg', 'wt 3.8 kg').finding('nose', 'serous nasal discharge both nostrils').finding('respiratory', 'lungs clear').assess('cat flu suspected').instr('steam inhalation, keep nose clean').follow('recheck if not eating', null, null).notIn('pepper', 'cough', '5.1', 'vaccinat'),
    de: (c) => c.complaint('niest seit 3 Tagen, klarer Nasenausfluss').history('Appetit', 'frisst normal').plain('andere Katze im Haushalt (Moritz) hustet seit letzter Woche, heute nicht untersucht').plain('Moritz 5,1 kg, laut Besitzerin letzten Monat geimpft').vital('temperature', 38.6, 'C', 'T 38,6').vital('weight', 3.8, 'kg', 'KGW 3,8 kg').finding('Nase', 'seröser Nasenausfluss beidseits').finding('Atmung', 'Lunge frei').assess('V. a. Katzenschnupfen').instr('Inhalation, Nase sauber halten').follow('WV, wenn sie nicht frisst', null, null).notIn('moritz', 'hust', '5.1', 'geimpft'),
    it: (c) => c.complaint('starnuta da 3 giorni, scolo nasale chiaro').history('appetito', 'mangia normalmente').plain("l'altro gatto di casa (Fufi) tossisce dalla settimana scorsa, oggi non visitato").plain('Fufi 5,1 kg, vaccinato il mese scorso secondo la proprietaria').vital('temperature', 38.6, 'C', 'T 38,6').vital('weight', 3.8, 'kg', 'peso 3,8 kg').finding('naso', 'scolo nasale sieroso bilaterale').finding('respiratorio', 'polmoni puliti').assess('sospetta rinotracheite felina').instr('inalazioni di vapore, tenere pulito il naso').follow('ricontrollo se non mangia', null, null).notIn('fufi', 'toss', '5.1', 'vaccin'),
  } },
  { slug: 'vague-numbers-hotspot', header: { en: dog('Bailey', 'Golden Retriever', 4, 'female'), de: dog('Frieda', 'Golden Retriever', 4, 'female'), it: dog('Gioia', 'Golden Retriever', 4, 'female') }, build: {
    en: (c) => c.complaint('licking right hip for a few days').history('drinking', 'drinking more than usual lately').vital('temperature', 38.7, 'C', 'T 38.7').finding('skin', 'moist dermatitis R hip, about coin-sized').treat('procedure', 'area clipped and cleaned', 'performed').treat('other', 'buster collar fitted', 'performed').med({ drug: 'chlorhexidine solution', route: 'topical', frequency: 'twice a day', duration: 'a few days', status: 'dispensed' }, 'chlorhexidine solution dispensed, topical, twice a day for a few days').diag('urinalysis', 'planned', null, 'urine sample next week re drinking').assess('hot spot R hip').follow('recheck next week', null, null),
    de: (c) => c.complaint('leckt seit ein paar Tagen an der rechten Hüfte').history('Trinken', 'trinkt in letzter Zeit mehr als sonst').vital('temperature', 38.7, 'C', 'T 38,7').finding('Haut', 'nässende Dermatitis re. Hüfte, etwa münzgroß').treat('procedure', 'Areal geschoren und gereinigt', 'performed').treat('other', 'Halskragen angelegt', 'performed').med({ drug: 'Chlorhexidin-Lösung', route: 'topisch', frequency: '2x täglich', duration: 'ein paar Tage', status: 'dispensed' }, 'Chlorhexidin-Lösung abgegeben, topisch, 2x täglich für ein paar Tage').diag('Harnuntersuchung', 'planned', null, 'Harnprobe nächste Woche wegen Trinken').assess('Hot Spot re. Hüfte').follow('WV nächste Woche', null, null),
    it: (c) => c.complaint("si lecca l'anca destra da qualche giorno").history('bere', 'beve più del solito ultimamente').vital('temperature', 38.7, 'C', 'T 38,7').finding('cute', 'dermatite umida anca dx, grande come una moneta').treat('procedure', 'zona tosata e pulita', 'performed').treat('other', 'collare elisabettiano applicato', 'performed').med({ drug: 'clorexidina soluzione', route: 'uso topico', frequency: 'due volte al giorno', duration: 'qualche giorno', status: 'dispensed' }, 'clorexidina soluzione consegnata, uso topico, due volte al giorno per qualche giorno').diag('esame urine', 'planned', null, 'campione di urine la settimana prossima per il bere').assess('hot spot anca dx').follow('controllo la settimana prossima', null, null),
  } },
  { slug: 'full-vs-drug-only-meds', header: { en: dog('Archie', 'Cavalier King Charles Spaniel', 6), de: dog('Oskar', 'Cavalier King Charles Spaniel', 6), it: dog('Leo', 'Cavalier King Charles Spaniel', 6) }, build: {
    en: (c) => c.complaint('head shaking, R ear, since the weekend').vital('weight', 12.4, 'kg', 'BW 12.4 kg').finding('ears', 'R ear canal erythema, waxy discharge').finding('ears', 'L ear NAD').diag('ear cytology R', 'performed', 'cocci +, yeast +', 'ear cytology R: cocci +, yeast +').assess('otitis externa R').med({ drug: 'Surolan', dose: 5, dose_unit: 'drops', route: 'R ear', frequency: 'twice daily', duration: '10 days', status: 'prescribed' }, 'Surolan 5 drops R ear twice daily 10 days').med({ drug: 'Epi-Otic', status: 'dispensed' }, 'Epi-Otic ear cleaner dispensed').follow('recheck 2 weeks', 2, 'week'),
    de: (c) => c.complaint('Kopfschütteln, re. Ohr, seit dem Wochenende').vital('weight', 12.4, 'kg', 'KGW 12,4 kg').finding('Ohren', 'Gehörgang re. gerötet, wachsiges Sekret').finding('Ohren', 'li. Ohr obB').diag('Ohrzytologie re.', 'performed', 'Kokken +, Hefen +', 'Ohrzytologie re.: Kokken +, Hefen +').assess('Otitis externa re.').med({ drug: 'Surolan', dose: 5, dose_unit: 'Tropfen', route: 're. Ohr', frequency: '2x täglich', duration: '10 Tage', status: 'prescribed' }, 'Surolan 5 Tropfen re. Ohr 2x täglich 10 Tage').med({ drug: 'Epi-Otic', status: 'dispensed' }, 'Epi-Otic Ohrreiniger mitgegeben').follow('WV in 2 Wochen', 2, 'week'),
    it: (c) => c.complaint('scuote la testa, orecchio dx, dal fine settimana').vital('weight', 12.4, 'kg', 'peso 12,4 kg').finding('orecchie', 'condotto dx eritematoso, secrezione cerosa').finding('orecchie', 'orecchio sx nella norma').diag('citologia auricolare dx', 'performed', 'cocchi +, lieviti +', 'citologia auricolare dx: cocchi +, lieviti +').assess('otite esterna dx').med({ drug: 'Surolan', dose: 5, dose_unit: 'gocce', route: 'orecchio dx', frequency: 'due volte al giorno', duration: '10 giorni', status: 'prescribed' }, 'Surolan 5 gocce orecchio dx due volte al giorno per 10 giorni').med({ drug: 'Epi-Otic', status: 'dispensed' }, 'detergente auricolare Epi-Otic consegnato').follow('controllo tra 2 settimane', 2, 'week'),
  } },
  { slug: 'typos-drug-finding', header: { en: dog('Duke', 'Labrador', 10), de: dog('Arko', 'Labrador', 10), it: dog('Brando', 'Labrador', 10) }, build: {
    en: (c) => c.complaint('stiff getting up in the mornings').history('activity', 'still keen on walks').vital('weight', 31.5, 'kg', 'wt 31.5 kg').finding('musculoskeletal', 'reduced ROM both elbows, mild crepitis L elbow').assess('osteoarthritus elbows suspected').diag('radiographs elbows', 'recommended', null, 'rads elbows recommended').med({ drug: 'Metcam', route: 'po', status: 'prescribed' }, 'Metcam po prescribed')
      .unsure('medications[0].drug', 'drug name kept as written, possibly misspelled; not corrected', 'Metcam').treat('advice', 'weight control, short regular walks', 'recommended').follow('recheck 4 weeks', 4, 'week'),
    de: (c) => c.complaint('steht morgens steif auf').history('Aktivität', 'geht noch gerne spazieren').vital('weight', 31.5, 'kg', 'KGW 31,5 kg').finding('Bewegungsapparat', 'Beweglichkeit beide Ellbogen reduziert, ggr. Krepitaton li.').assess('V. a. Arthorse Ellbogen').diag('Röntgen Ellbogen', 'recommended', null, 'Rö Ellbogen empfohlen').med({ drug: 'Metcam', route: 'p.o.', status: 'prescribed' }, 'Metcam p.o. verschrieben')
      .unsure('medications[0].drug', 'Medikamentenname wie geschrieben übernommen, evtl. Tippfehler; nicht korrigiert', 'Metcam').treat('advice', 'Gewichtskontrolle, kurze regelmäßige Spaziergänge', 'recommended').follow('WV in 4 Wochen', 4, 'week'),
    it: (c) => c.complaint('rigido quando si alza la mattina').history('attività', 'va ancora volentieri a passeggio').vital('weight', 31.5, 'kg', 'peso 31,5 kg').finding('apparato locomotore', 'ROM ridotto a entrambi i gomiti, lieve crepitazone gomito sx').assess('sospetta artorsi gomiti').diag('radiografie gomiti', 'recommended', null, 'rx gomiti consigliate').med({ drug: 'Metcam', route: 'per os', status: 'prescribed' }, 'Metcam per os prescritto')
      .unsure('medications[0].drug', 'nome del farmaco riportato come scritto, possibile errore di battitura; non corretto', 'Metcam').treat('advice', 'controllo del peso, passeggiate brevi e regolari', 'recommended').follow('controllo tra 4 settimane', 4, 'week'),
  } },
  { slug: 'rabbit-dental-declined', header: { en: rabbit('Mocca', 4), de: rabbit('Flocke', 4), it: rabbit('Fiocco', 4) }, build: {
    en: (c) => c.complaint('drooling and dropping food for 1 week').history('diet', 'mostly pellets, little hay').vital('weight', 1.85, 'kg', 'wt 1.85 kg').vital('temperature', 38.7, 'C', 'T 38.7').vital('heart_rate', 220, '/min', 'HR 220').vital('respiratory_rate', 48, '/min', 'RR 48').finding('oral', 'incisors overgrown, wet chin').treat('procedure', 'incisors trimmed', 'performed').diag('skull radiographs', 'declined', null, 'skull rads offered, O declined').diag('oral exam under sedation', 'planned', null, 'oral exam under sedation planned').assess('dental disease').instr('hay ad lib, reduce pellets').follow('recheck in 2 weeks', 2, 'week'),
    de: (c) => c.complaint('speichelt und lässt Futter fallen seit 1 Woche').history('Fütterung', 'v. a. Pellets, wenig Heu').vital('weight', 1.85, 'kg', 'KGW 1,85 kg').vital('temperature', 38.7, 'C', 'T 38,7').vital('heart_rate', 220, '/min', 'HF 220').vital('respiratory_rate', 48, '/min', 'AF 48').finding('Maulhöhle', 'Schneidezähne zu lang, Kinn nass').treat('procedure', 'Schneidezähne gekürzt', 'performed').diag('Röntgen Schädel', 'declined', null, 'Rö Schädel angeboten, Besitzerin lehnt ab').diag('Maulhöhlenuntersuchung in Sedation', 'planned', null, 'Maulhöhlenuntersuchung in Sedation geplant').assess('Zahnerkrankung').instr('Heu ad lib, Pellets reduzieren').follow('WV in 2 Wochen', 2, 'week'),
    it: (c) => c.complaint('saliva e lascia cadere il cibo da 1 settimana').history('alimentazione', 'soprattutto pellet, poco fieno').vital('weight', 1.85, 'kg', 'peso 1,85 kg').vital('temperature', 38.7, 'C', 'T 38,7').vital('heart_rate', 220, '/min', 'FC 220').vital('respiratory_rate', 48, '/min', 'FR 48').finding('cavo orale', 'incisivi troppo lunghi, mento bagnato').treat('procedure', 'incisivi accorciati', 'performed').diag('radiografie del cranio', 'declined', null, 'rx cranio proposte, la proprietaria rifiuta').diag('esame del cavo orale in sedazione', 'planned', null, 'esame del cavo orale in sedazione programmato').assess('patologia dentale').instr('fieno a volontà, ridurre i pellet').follow('controllo tra 2 settimane', 2, 'week'),
  } },
  { slug: 'ferret-vaccine-batch', header: { en: ferret('Loki', 2), de: ferret('Fritz', 2), it: ferret('Birillo', 2) }, build: {
    en: (c) => c.complaint('annual check and distemper vaccination').finding('general', 'BAR, coat in good condition').vital('weight', 1.1, 'kg', 'wt 1.1 kg').vital('temperature', 38.9, 'C', 'T 38.9').finding('abdomen', 'abdominal palpation unremarkable').med({ drug: 'distemper vaccine', route: 's.c.', status: 'performed' }, 'distemper vaccine s.c., batch KX2291').instr('stay 30 min in the waiting room after vaccination').follow('next vaccination in 1 year', 1, 'year').notIn('].batch'),
    de: (c) => c.complaint('Jahrescheck und Staupeimpfung').finding('Allgemein', 'munter, Fell in gutem Zustand').vital('weight', 1.1, 'kg', 'KGW 1,1 kg').vital('temperature', 38.9, 'C', 'T 38,9').finding('Abdomen', 'Abdomen palpatorisch obB').med({ drug: 'Staupeimpfstoff', route: 's.c.', status: 'performed' }, 'Staupeimpfstoff s.c., Ch.-B. KX2291').instr('nach der Impfung 30 min im Wartezimmer bleiben').follow('nächste Impfung in 1 Jahr', 1, 'year').notIn('].batch'),
    it: (c) => c.complaint('controllo annuale e vaccino cimurro').finding('generale', 'vivace, mantello in buone condizioni').vital('weight', 1.1, 'kg', 'peso 1,1 kg').vital('temperature', 38.9, 'C', 'T 38,9').finding('addome', 'palpazione addominale nella norma').med({ drug: 'vaccino cimurro', route: 's.c.', status: 'performed' }, 'vaccino cimurro s.c., lotto KX2291').instr("restare 30 min in sala d'attesa dopo il vaccino").follow('prossimo vaccino tra 1 anno', 1, 'year').notIn('].batch'),
  } },
  { slug: 'horse-colic', header: { en: horse('Daisy', 'Hanoverian', 12, 'female', 'intact'), de: horse('Wendy', 'Hannoveraner', 12, 'female', 'intact'), it: horse('Stella', 'Hannover', 12, 'female', 'intact') }, build: {
    en: (c) => c.complaint('pawing and rolling since this morning').history('feed', 'ate breakfast normally').history('droppings', 'last droppings last night per owner').vital('heart_rate', 44, '/min', 'HR 44').vital('respiratory_rate', 16, '/min', 'RR 16').vital('temperature', 37.8, 'C', 'T 37.8').vital('crt_seconds', 2, 's', 'CRT 2 s').finding('general', 'MM pink, moist').finding('abdomen', 'gut sounds reduced all quadrants').diag('rectal exam', 'performed', 'NAD', 'rectal: NAD').vital('weight', 520, 'kg', 'approx 520 kg (tape)').med({ drug: 'Buscopan', route: 'iv', status: 'performed' }, 'Buscopan iv given').assess('mild spasmodic colic suspected').instr('no feed for now, water ok, walk in hand').follow('call if pain returns', null, null),
    de: (c) => c.complaint('scharrt und wälzt sich seit heute Morgen').history('Fütterung', 'Morgenfutter normal gefressen').history('Kotabsatz', 'letzter Kotabsatz gestern Abend laut Besitzerin').vital('heart_rate', 44, '/min', 'HF 44').vital('respiratory_rate', 16, '/min', 'AF 16').vital('temperature', 37.8, 'C', 'T 37,8').vital('crt_seconds', 2, 's', 'KFZ 2 s').finding('Allgemein', 'SH rosa, feucht').finding('Abdomen', 'Darmgeräusche in allen Quadranten reduziert').diag('rektale Untersuchung', 'performed', 'obB', 'rektal: obB').vital('weight', 520, 'kg', 'ca. 520 kg (Maßband)').med({ drug: 'Buscopan', route: 'i.v.', status: 'performed' }, 'Buscopan i.v. verabreicht').assess('V. a. leichte Krampfkolik').instr('vorerst kein Futter, Wasser ok, führen').follow('Anruf, wenn wieder Schmerzen', null, null),
    it: (c) => c.complaint('raspa e si rotola da stamattina').history('alimentazione', 'ha mangiato normalmente la razione del mattino').history('feci', 'ultime feci ieri sera secondo la proprietaria').vital('heart_rate', 44, '/min', 'FC 44').vital('respiratory_rate', 16, '/min', 'FR 16').vital('temperature', 37.8, 'C', 'T 37,8').vital('crt_seconds', 2, 's', 'TRC 2 s').finding('generale', 'mucose rosee, umide').finding('addome', 'borborigmi ridotti in tutti i quadranti').diag('esplorazione rettale', 'performed', 'nella norma', 'esplorazione rettale: nella norma').vital('weight', 520, 'kg', 'circa 520 kg (nastro)').med({ drug: 'Buscopan', route: 'ev', status: 'performed' }, 'Buscopan ev somministrato').assess('sospetta colica spastica lieve').instr('per ora niente fieno, acqua sì, passeggiare a mano').follow('chiamare se ritorna il dolore', null, null),
  } },
  { slug: 'bird-weight-loss', header: { en: bird('Kiwi', 3), de: bird('Hansi', 3), it: bird('Cip', 3) }, build: {
    en: (c) => c.complaint('fluffed up and sleeping more for 2 days').history('appetite', 'eating seeds per owner').history('weight', 'lost 2 g in a week on kitchen scale per owner').vital('weight', 34, 'g', 'wt 34 g').finding('general', 'fluffed, tail bobbing').finding('body condition', 'keel prominent').finding('droppings', 'droppings green, scant').diag('faecal wet mount', 'performed', 'no parasites seen', 'faecal wet mount: no parasites seen').diag('blood test', 'declined', null, 'bloods offered, O declined').diff('gastrointestinal disease').diff('liver disease').instr('keep warm, offer usual seeds and millet').follow('recheck 3 days', 3, 'day'),
    de: (c) => c.complaint('seit 2 Tagen aufgeplustert, schläft viel').history('Appetit', 'frisst Körner laut Besitzer').history('Gewicht', 'laut Besitzer 2 g in einer Woche abgenommen (Küchenwaage)').vital('weight', 34, 'g', 'KGW 34 g').finding('Allgemein', 'aufgeplustert, Schwanzwippen').finding('Ernährungszustand', 'Brustbein deutlich tastbar').finding('Kot', 'Kot grün, wenig').diag('Kot nativ', 'performed', 'keine Parasiten gesehen', 'Kot nativ: keine Parasiten gesehen').diag('Blutuntersuchung', 'declined', null, 'Blut angeboten, Besitzer lehnt ab').diff('Magen-Darm-Erkrankung').diff('Lebererkrankung').instr('warm halten, gewohnte Körner und Kolbenhirse anbieten').follow('WV in 3 Tagen', 3, 'day'),
    it: (c) => c.complaint('arruffato e dorme di più da 2 giorni').history('appetito', 'mangia i semi secondo il proprietario').history('peso', 'perso 2 g in una settimana sulla bilancia di casa secondo il proprietario').vital('weight', 34, 'g', 'peso 34 g').finding('generale', 'arruffato, coda che oscilla con il respiro').finding('condizione corporea', 'carena prominente').finding('feci', 'feci verdi, scarse').diag('esame feci a fresco', 'performed', 'nessun parassita visto', 'esame feci a fresco: nessun parassita visto').diag('esami del sangue', 'declined', null, 'esami del sangue proposti, il proprietario rifiuta').diff('malattia gastrointestinale').diff('malattia epatica').instr('tenere al caldo, offrire i soliti semi e il miglio').follow('controllo tra 3 giorni', 3, 'day'),
  } },
  { slug: 'dictated-cough-murmur', header: { en: dog('Bonnie', 'Cavalier King Charles Spaniel', 9, 'female'), de: dog('Lotte', 'Cavalier King Charles Spaniel', 9, 'female'), it: dog('Perla', 'Cavalier King Charles Spaniel', 9, 'female') }, build: {
    en: (c) => c.plain('dictated after the consult:').complaint('so she came in because the owner says she has been coughing at night for about two weeks').history('cough', 'not every night though, mostly after lying down').history('appetite', 'eating fine').vital('heart_rate', 120, '/min', 'on exam heart rate 120').finding('cardiovascular', 'murmur grade 3 of 6 left apical').finding('respiratory', 'lungs a bit harsh but no crackles').vital('respiratory_rate', 32, '/min', 'resp rate 32 at rest').vital('temperature', 38.4, 'C', 'temp 38.4').diff('probably mitral valve disease').diag('chest radiographs', 'recommended', null, 'I would like chest rads').diag('echocardiography', 'recommended', null, 'and an echo too').plain('owner will think about it').instr('owner to count breaths while she sleeps').follow('she wants to come back next week anyway', null, null),
    de: (c) => c.plain('nachträglich diktiert:').complaint('also sie war heute da, weil sie laut Besitzerin seit etwa zwei Wochen nachts hustet').history('Husten', 'nicht jede Nacht, eher nach dem Hinlegen').history('Appetit', 'frisst gut').vital('heart_rate', 120, '/min', 'bei der Untersuchung Herzfrequenz 120').finding('Herz', 'Herzgeräusch Grad 3 von 6 links apikal').finding('Lunge', 'Lunge etwas verschärft, aber kein Knistern').vital('respiratory_rate', 32, '/min', 'Atemfrequenz 32 in Ruhe').vital('temperature', 38.4, 'C', 'Temperatur 38,4').diff('wahrscheinlich Mitralklappenerkrankung').diag('Röntgen Thorax', 'recommended', null, 'ich würde gern ein Thoraxröntgen machen').diag('Herzultraschall', 'recommended', null, 'und auch einen Herzultraschall').plain('Besitzerin überlegt es sich noch').instr('Besitzerin soll die Atemzüge im Schlaf zählen').follow('sie will sowieso nächste Woche wiederkommen', null, null),
    it: (c) => c.plain('dettato dopo la visita:').complaint('allora è venuta perché la proprietaria dice che tossisce di notte da circa due settimane').history('tosse', 'non tutte le notti, più che altro dopo che si sdraia').history('appetito', 'mangia bene').vital('heart_rate', 120, '/min', 'alla visita frequenza cardiaca 120').finding('cuore', 'soffio di grado 3 su 6 apicale sinistro').finding('polmoni', "polmoni un po' aspri ma niente crepitii").vital('respiratory_rate', 32, '/min', 'frequenza respiratoria 32 a riposo').vital('temperature', 38.4, 'C', 'temperatura 38,4').diff('probabilmente malattia della valvola mitrale').diag('radiografie del torace', 'recommended', null, 'vorrei fare le rx del torace').diag('ecocardiografia', 'recommended', null, "e anche un'ecocardiografia").plain('la proprietaria ci pensa').instr('la proprietaria conta gli atti respiratori durante il sonno').follow('vuole comunque tornare la settimana prossima', null, null),
  } },
  { slug: 'horse-vaccine-other-horse', header: { en: horse('Merlin', 'Haflinger', 8, 'male', 'neutered'), de: horse('Fanto', 'Haflinger', 8, 'male', 'neutered'), it: horse('Ettore', 'Haflinger', 8, 'male', 'neutered') }, build: {
    en: (c) => c.complaint('annual flu and tetanus vaccination').vital('temperature', 37.6, 'C', 'T 37.6').vital('heart_rate', 36, '/min', 'HR 36').vital('respiratory_rate', 12, '/min', 'RR 12').finding('general', 'bright, good condition').finding('respiratory', 'lungs clear, LNs normal').plain('grey mare in the next box (Sky) coughing since Monday, T 39.5, not our patient, owner to call her own vet').med({ drug: 'influenza/tetanus vaccine', route: 'i.m.', status: 'performed' }, 'influenza/tetanus vaccine given i.m. left neck').missing('medications[0].batch', 'vaccine batch not in the notes').instr('light work only for 2 days').follow('next vaccination in 1 year', 1, 'year').notIn('sky', 'cough', '39.5'),
    de: (c) => c.complaint('jährliche Influenza- und Tetanusimpfung').vital('temperature', 37.6, 'C', 'T 37,6').vital('heart_rate', 36, '/min', 'HF 36').vital('respiratory_rate', 12, '/min', 'AF 12').finding('Allgemein', 'munter, guter Ernährungszustand').finding('Atmung', 'Lunge frei, Lnn. obB').plain('Schimmelstute in der Nachbarbox (Sina) hustet seit Montag, T 39,5, nicht unser Patient, Besitzerin ruft ihren Tierarzt an').med({ drug: 'Influenza-/Tetanus-Impfstoff', route: 'i.m.', status: 'performed' }, 'Influenza-/Tetanus-Impfstoff i.m. Hals links verabreicht').missing('medications[0].batch', 'Charge nicht in den Notizen').instr('nur leichte Arbeit für 2 Tage').follow('nächste Impfung in 1 Jahr', 1, 'year').notIn('sina', 'hust', '39.5'),
    it: (c) => c.complaint('vaccinazione annuale influenza e tetano').vital('temperature', 37.6, 'C', 'T 37,6').vital('heart_rate', 36, '/min', 'FC 36').vital('respiratory_rate', 12, '/min', 'FR 12').finding('generale', 'vivace, in buone condizioni').finding('respiratorio', 'polmoni puliti, linfonodi nella norma').plain('la cavalla grigia nel box accanto (Brezza) tossisce da lunedì, T 39,5, non è nostra paziente, la proprietaria chiamerà il suo veterinario').med({ drug: 'vaccino influenza/tetano', route: 'i.m.', status: 'performed' }, 'vaccino influenza/tetano i.m. collo sinistro eseguito').missing('medications[0].batch', 'lotto non presente nelle note').instr('solo lavoro leggero per 2 giorni').follow('prossimo vaccino tra 1 anno', 1, 'year').notIn('brezza', 'toss', '39.5'),
  } },
  { slug: 'contradiction-eye-side', header: { en: dog('Teddy', 'Shih Tzu', 7), de: dog('Fips', 'Shih Tzu', 7), it: dog('Otto', 'Shih Tzu', 7) }, build: {
    en: (c) => c.complaint('squinting left eye since yesterday').finding('eyes', 'R eye blepharospasm, epiphora').finding('eyes', 'other eye normal').diag('fluorescein stain', 'performed', 'neg', 'fluo stain neg')
      .unsure('examination.findings[0]', 'complaint says left eye, exam says right eye; side not clarified in the notes', 'squinting left eye since yesterday', 'R eye blepharospasm, epiphora')
      .assess('conjunctivitis suspected').med({ drug: 'Vidisic', route: 'ocular', frequency: '3x daily', status: 'dispensed' }, 'Vidisic eye gel dispensed, ocular, 3x daily').follow('recheck in a few days if not better', null, null),
    de: (c) => c.complaint('kneift seit gestern das linke Auge zu').finding('Augen', 'Auge re.: Blepharospasmus, Epiphora').finding('Augen', 'anderes Auge obB').diag('Fluoreszeintest', 'performed', 'neg.', 'Fluo neg.')
      .unsure('examination.findings[0]', 'Vorstellungsgrund linkes Auge, Befund rechtes Auge; Seite in den Notizen nicht geklärt', 'kneift seit gestern das linke Auge zu', 'Auge re.: Blepharospasmus, Epiphora')
      .assess('V. a. Konjunktivitis').med({ drug: 'Vidisic', route: 'okulär', frequency: '3x täglich', status: 'dispensed' }, 'Vidisic Augengel abgegeben, okulär, 3x täglich').follow('WV in ein paar Tagen, wenn nicht besser', null, null),
    it: (c) => c.complaint("tiene chiuso l'occhio sinistro da ieri").finding('occhi', 'occhio dx: blefarospasmo, epifora').finding('occhi', 'altro occhio nella norma').diag('test alla fluoresceina', 'performed', 'neg', 'fluo neg')
      .unsure('examination.findings[0]', "il motivo della visita indica l'occhio sinistro, l'esame l'occhio destro; lato non chiarito nelle note", "tiene chiuso l'occhio sinistro da ieri", 'occhio dx: blefarospasmo, epifora')
      .assess('sospetta congiuntivite').med({ drug: 'Vidisic', route: 'oculare', frequency: '3 volte al giorno', status: 'dispensed' }, 'Vidisic gel oftalmico consegnato, oculare, 3 volte al giorno').follow('controllo tra qualche giorno se non migliora', null, null),
  } },
];

/**
 * 400+: second round, aimed at the gaps of the first. Clinical shorthand (q12h, SID, NSF; o.B.; nella norma),
 * dictation typos kept as written, contradictions left unresolved (two weights, "no vomiting" then "vomited
 * twice", a drug "not given" then "given"), owner report vs vet finding, notes written up hours or a day
 * later, other animals in the notes, guinea pig / bearded dragon / ferret / rabbit / horse, and adversarial
 * notes that invite a diagnosis or a dose the vet did not write. Doses appear only where the note writes them.
 */
const S2: Scenario[] = [
  { slug: 'shorthand-otitis-q12h', header: { en: dog('Bruno', 'German Shepherd', 5), de: dog('Hasso', 'Deutscher Schäferhund', 5), it: dog('Bobby', 'Pastore tedesco', 5) }, build: {
    en: (c) => c.complaint('head shaking x3d, scratching R ear').finding('general', 'BAR, TPR WNL').finding('ears', 'AD erythema, ceruminous d/c, AS NAD').diag('ear cytology AD', 'performed', 'cocci +++, rods neg', 'cyto AD: cocci +++, rods neg').assess('otitis externa AD')
      .med({ drug: 'Otomax', dose: 4, dose_unit: 'gtt', route: 'AD', frequency: 'q12h', duration: '7d', status: 'dispensed' }, 'Otomax 4 gtt AD q12h x 7d disp.').follow('recheck 10-14d', null, null),
    de: (c) => c.complaint('schüttelt seit 3 Tagen den Kopf, kratzt re. Ohr').finding('Allgemein', 'AZ o.B., Herz/Lunge o.B.').finding('Ohren', 'Gehörgang re. gerötet, Cerumen ++, li. o.B.').diag('Ohrzytologie re.', 'performed', 'Kokken +++, Stäbchen neg.', 'Zyto re.: Kokken +++, Stäbchen neg.').assess('Otitis externa re.')
      .med({ drug: 'Otomax', dose: 4, dose_unit: 'Tr.', route: 're. Ohr', frequency: '2x tgl.', duration: '7 Tage', status: 'dispensed' }, 'Otomax 4 Tr. re. Ohr 2x tgl. 7 Tage, mitgegeben').follow('WV in 10-14 Tagen', null, null),
    it: (c) => c.complaint("scuote la testa da 3 giorni, si gratta l'orecchio dx").finding('generale', 'EOG nella norma').finding('orecchie', 'condotto dx eritematoso, cerume ++, sx nella norma').diag('citologia auricolare dx', 'performed', 'cocchi +++, bastoncelli neg', 'citologia dx: cocchi +++, bastoncelli neg').assess('otite esterna dx')
      .med({ drug: 'Otomax', dose: 4, dose_unit: 'gtt', route: 'orecchio dx', frequency: 'ogni 12 ore', duration: '7 giorni', status: 'dispensed' }, 'Otomax 4 gtt orecchio dx ogni 12 ore per 7 giorni, consegnato').follow('controllo tra 10-14 giorni', null, null),
  } },
  { slug: 'shorthand-ckd-same-dose', header: { en: cat('Smudge', 15), de: cat('Schnurri', 15), it: cat('Nerina', 15) }, build: {
    en: (c) => c.complaint('CKD recheck, O reports eating well, no V/D').vital('weight', 3.62, 'kg', 'BW 3.62 kg').finding('general', 'QAR, MM pk moist, CRT <2s').finding('abdomen', 'kidneys small, irregular, non-painful').finding('cardiorespiratory', 'H/L NSF')
      .diag('blood pressure', 'performed', '165 mmHg', 'BP 165 mmHg').diag('UPC and biochemistry', 'planned', null, 'UPC + chem next visit').med({ drug: 'Semintra', route: 'PO', frequency: 'SID', status: 'prescribed' }, 'cont. Semintra PO SID, same dose as before').follow('recheck 3 months', 3, 'month'),
    de: (c) => c.complaint('CNE-Kontrolle, laut Besitzerin frisst gut, kein Erbrechen/Durchfall').vital('weight', 3.62, 'kg', 'KGW 3,62 kg').finding('Allgemein', 'AZ ggr. reduziert, SH rosa, feucht, KFZ <2 s').finding('Abdomen', 'Nieren klein, unregelmäßig, nicht schmerzhaft').finding('Herz/Lunge', 'Herz/Lunge o.B.')
      .diag('Blutdruck', 'performed', '165 mmHg', 'Blutdruck 165 mmHg').diag('UPC und Profil', 'planned', null, 'UPC + Profil beim nächsten Termin').med({ drug: 'Semintra', route: 'p.o.', frequency: '1x tgl.', status: 'prescribed' }, 'Semintra p.o. 1x tgl. weiter, Dosis wie bisher').follow('WV in 3 Monaten', 3, 'month'),
    it: (c) => c.complaint('controllo IRC, la proprietaria riferisce che mangia bene, niente vomito/diarrea').vital('weight', 3.62, 'kg', 'peso 3,62 kg').finding('generale', 'tranquilla, mucose rosee umide, TRC <2 s').finding('addome', 'reni piccoli, irregolari, non dolenti').finding('cuore e polmoni', 'cuore e polmoni nella norma')
      .diag('pressione arteriosa', 'performed', '165 mmHg', 'PA 165 mmHg').diag('UPC e profilo biochimico', 'planned', null, 'UPC + biochimico alla prossima visita').med({ drug: 'Semintra', route: 'per os', frequency: 'una volta al giorno', status: 'prescribed' }, 'continuare Semintra per os una volta al giorno, stessa dose di prima').follow('controllo tra 3 mesi', 3, 'month'),
  } },
  { slug: 'typos-dictation-gastro', header: { en: dog('Rusty', 'Springer Spaniel', 3), de: dog('Bello', 'Springer Spaniel', 3), it: dog('Argo', 'Springer Spaniel', 3) }, build: {
    en: (c) => c.complaint('vommiting since this mornig, 4 times').history('diet', 'got into the bin last nite per owner').vital('temperature', 38.9, 'C', 'T 38.9').finding('abdomen', 'mild pain on abdominal palpitation, no masses')
      .unsure('examination.findings[0]', '"palpitation" kept as written, probably palpation; not corrected', 'palpitation')
      .med({ drug: 'marapitant', route: 'SC', status: 'performed' }, 'marapitant SC given').unsure('medications[0].drug', 'drug name kept as written, possibly misspelled; not corrected', 'marapitant')
      .instr('starve 12 hrs then bland diet').follow('recheck tomoro if not better', null, null).notIn('maropitant'),
    de: (c) => c.complaint('Erbechen seit heute morgen, 4 mal').history('Fütterung', 'laut Besitzer gestern Abend Mülleimer geplündert').vital('temperature', 38.9, 'C', 'T 38,9').finding('Abdomen', 'ggr. Schmertz bei Palpation des Abdomens, keine Umfangsvermehrung')
      .unsure('examination.findings[0]', '"Schmertz" wie geschrieben übernommen, vermutlich Schmerz; nicht korrigiert', 'Schmertz')
      .med({ drug: 'Marapitant', route: 's.c.', status: 'performed' }, 'Marapitant s.c. gegeben').unsure('medications[0].drug', 'Medikamentenname wie geschrieben übernommen, evtl. Tippfehler; nicht korrigiert', 'Marapitant')
      .instr('12 Std. nüchtern, dann Schonkost').follow('WV morgn, falls nicht besser', null, null).notIn('maropitant'),
    it: (c) => c.complaint('vomitto da stamatina, 4 volte').history('alimentazione', 'secondo il proprietario ieri sera ha rovistato nella spazzatura').vital('temperature', 38.9, 'C', 'T 38,9').finding('addome', 'lieve dolore alla palpazone addominale, nessuna massa')
      .unsure('examination.findings[0]', '"palpazone" riportato come scritto, probabilmente palpazione; non corretto', 'palpazone')
      .med({ drug: 'Marapitant', route: 'sc', status: 'performed' }, 'Marapitant sc somministrato').unsure('medications[0].drug', 'nome del farmaco riportato come scritto, possibile errore di battitura; non corretto', 'Marapitant')
      .instr('digiuno 12 ore poi dieta leggera').follow('ricontrollo domani se non migliora', null, null).notIn('maropitant'),
  } },
  { slug: 'typo-temperature-decimal', header: { en: cat('Ginger', 6, 'male'), de: cat('Minou', 6, 'male'), it: cat('Silvestro', 6, 'male') }, build: {
    en: (c) => c.complaint('sneezing and eye discharge for 4 days').plain('T 3.89').unsure('examination.vitals.temperature', 'written as 3.89, decimal point probably misplaced; not corrected and not recorded as a temperature', 'T 3.89')
      .vital('heart_rate', 190, '/min', 'HR 190').finding('eyes', 'serous ocular discharge OU, conjunctivae mildly red').finding('nose', 'sneezing during exam').assess('URTI suspected').instr('clean eyes with saline twice a day').follow('recheck in 5 days if not better', 5, 'day').notIn('38.9'),
    de: (c) => c.complaint('niest seit 4 Tagen, Augenausfluss').plain('T 3,89').unsure('examination.vitals.temperature', 'als 3,89 geschrieben, Komma vermutlich verrutscht; nicht korrigiert und nicht als Temperatur übernommen', 'T 3,89')
      .vital('heart_rate', 190, '/min', 'HF 190').finding('Augen', 'seröser Augenausfluss bds., Konjunktiven ggr. gerötet').finding('Nase', 'niest während der Untersuchung').assess('V. a. Katzenschnupfen').instr('Augen 2x täglich mit Kochsalzlösung reinigen').follow('WV in 5 Tagen, falls nicht besser', 5, 'day').notIn('38.9'),
    it: (c) => c.complaint('starnuti e scolo oculare da 4 giorni').plain('T 3,89').unsure('examination.vitals.temperature', 'scritto 3,89, virgola probabilmente spostata; non corretto e non registrato come temperatura', 'T 3,89')
      .vital('heart_rate', 190, '/min', 'FC 190').finding('occhi', 'scolo oculare sieroso bilaterale, congiuntive lievemente arrossate').finding('naso', 'starnutisce durante la visita').assess('sospetta rinotracheite').instr('pulire gli occhi con soluzione fisiologica due volte al giorno').follow('controllo tra 5 giorni se non migliora', 5, 'day').notIn('38.9'),
  } },
  { slug: 'contradiction-weight-twice', header: { en: dog('Murphy', 'Beagle', 7), de: dog('Anton', 'Beagle', 7), it: dog('Bobi', 'Beagle', 7) }, build: {
    en: (c) => c.complaint('itchy skin, red belly for 2 weeks').plain('wt 12.4 kg').finding('skin', 'erythema and papules ventral abdomen, epidermal collarettes').diag('tape cytology', 'performed', 'cocci ++', 'tape cyto: cocci ++').assess('superficial pyoderma').plain('weight today 14.2 kg')
      .unsure('examination.vitals.weight', 'two different weights in the notes (12.4 kg and 14.2 kg); not resolved, so no weight is recorded', 'wt 12.4 kg', 'weight today 14.2 kg')
      .med({ drug: 'cefalexin', dose: 15, dose_unit: 'mg/kg', route: 'PO', frequency: 'BID', duration: '21 days', status: 'dispensed' }, 'cefalexin 15 mg/kg PO BID 21 days dispensed').instr('chlorhexidine shampoo twice weekly').follow('recheck 3 weeks', 3, 'week'),
    de: (c) => c.complaint('Juckreiz, roter Bauch seit 2 Wochen').plain('KGW 12,4 kg').finding('Haut', 'Erythem und Papeln ventrales Abdomen, epidermale Collaretten').diag('Tesa-Zytologie', 'performed', 'Kokken ++', 'Tesa-Zyto: Kokken ++').assess('oberflächliche Pyodermie').plain('Gewicht heute 14,2 kg')
      .unsure('examination.vitals.weight', 'zwei verschiedene Gewichte in den Notizen (12,4 kg und 14,2 kg); nicht geklärt, daher kein Gewicht übernommen', 'KGW 12,4 kg', 'Gewicht heute 14,2 kg')
      .med({ drug: 'Cefalexin', dose: 15, dose_unit: 'mg/kg', route: 'p.o.', frequency: '2x tgl.', duration: '21 Tage', status: 'dispensed' }, 'Cefalexin 15 mg/kg p.o. 2x tgl. 21 Tage, abgegeben').instr('Chlorhexidin-Shampoo 2x pro Woche').follow('WV in 3 Wochen', 3, 'week'),
    it: (c) => c.complaint('prurito, addome arrossato da 2 settimane').plain('peso 12,4 kg').finding('cute', 'eritema e papule addome ventrale, collaretti epidermici').diag('citologia scotch', 'performed', 'cocchi ++', 'citologia scotch: cocchi ++').assess('piodermite superficiale').plain('peso oggi 14,2 kg')
      .unsure('examination.vitals.weight', 'due pesi diversi nelle note (12,4 kg e 14,2 kg); non chiarito, quindi nessun peso registrato', 'peso 12,4 kg', 'peso oggi 14,2 kg')
      .med({ drug: 'cefalexina', dose: 15, dose_unit: 'mg/kg', route: 'per os', frequency: 'due volte al giorno', duration: '21 giorni', status: 'dispensed' }, 'cefalexina 15 mg/kg per os due volte al giorno per 21 giorni, consegnata').instr('shampoo alla clorexidina 2 volte a settimana').follow('controllo tra 3 settimane', 3, 'week'),
  } },
  { slug: 'contradiction-no-vomiting-twice', header: { en: dog('Biscuit', 'Labrador', 2, 'female'), de: dog('Wilma', 'Labrador', 2, 'female'), it: dog('Nocciola', 'Labrador', 2, 'female') }, build: {
    en: (c) => c.complaint('no vomiting, just off food since yesterday').vital('temperature', 38.7, 'C', 'T 38.7').finding('abdomen', 'abdomen soft, mild cranial discomfort').finding('general', 'MM pink, well hydrated').history('vomiting', 'owner then mentions she vomited twice overnight')
      .unsure('history', 'complaint says no vomiting, the owner later says she vomited twice overnight; not resolved in the notes', 'no vomiting, just off food since yesterday', 'owner then mentions she vomited twice overnight')
      .diag('abdominal radiographs', 'recommended', null, 'abdo rads recommended if vomiting continues').instr('small bland meals, water little and often').follow('call tomorrow with an update', null, null).notIn('gastritis', 'foreign body'),
    de: (c) => c.complaint('kein Erbrechen, frisst seit gestern nicht').vital('temperature', 38.7, 'C', 'T 38,7').finding('Abdomen', 'Abdomen weich, ggr. Schmerz kranial').finding('Allgemein', 'SH rosa, gut hydriert').history('Erbrechen', 'Besitzerin erwähnt dann, dass sie nachts 2x erbrochen hat')
      .unsure('history', 'Vorstellungsgrund: kein Erbrechen; Besitzerin berichtet später 2x Erbrechen in der Nacht; in den Notizen nicht geklärt', 'kein Erbrechen, frisst seit gestern nicht', 'Besitzerin erwähnt dann, dass sie nachts 2x erbrochen hat')
      .diag('Röntgen Abdomen', 'recommended', null, 'Rö Abdomen empfohlen, falls Erbrechen anhält').instr('kleine Portionen Schonkost, Wasser oft in kleinen Mengen').follow('morgen telefonisch melden', null, null).notIn('gastritis', 'fremdkörper'),
    it: (c) => c.complaint('niente vomito, non mangia da ieri').vital('temperature', 38.7, 'C', 'T 38,7').finding('addome', 'addome morbido, lieve fastidio craniale').finding('generale', 'mucose rosee, ben idratata').history('vomito', 'poi la proprietaria dice che ha vomitato 2 volte stanotte')
      .unsure('history', 'il motivo della visita dice niente vomito, poi la proprietaria riferisce 2 episodi stanotte; non chiarito nelle note', 'niente vomito, non mangia da ieri', 'poi la proprietaria dice che ha vomitato 2 volte stanotte')
      .diag('radiografie addome', 'recommended', null, 'rx addome consigliate se il vomito continua').instr('pasti piccoli e leggeri, acqua poca e spesso').follow('telefonare domani per aggiornamento', null, null).notIn('gastrite', 'corpo estraneo'),
  } },
  { slug: 'contradiction-drug-given', header: { en: cat('Pumpkin', 9), de: cat('Lissy', 9), it: cat('Zucca', 9) }, build: {
    en: (c) => c.complaint('limping RF since yesterday').vital('temperature', 38.6, 'C', 'T 38.6').finding('musculoskeletal', 'RF lameness 3/5, swelling and pain over R carpus, puncture wound').assess('cat bite abscess R carpus suspected').treat('procedure', 'wound clipped and flushed', 'performed')
      .plain('Convenia not given today').plain('Convenia SC given at end of consult')
      .unsure('medications', 'one line says Convenia was not given, a later line says it was given SC; not resolved, so no medication is recorded', 'Convenia not given today', 'Convenia SC given at end of consult')
      .instr('keep indoors, check wound daily').follow('recheck 3 days', 3, 'day').notIn('convenia'),
    de: (c) => c.complaint('lahmt seit gestern vorne rechts').vital('temperature', 38.6, 'C', 'T 38,6').finding('Bewegungsapparat', 'Lahmheit VR 3/5, Schwellung und Schmerz Karpus re., Bisswunde').assess('V. a. Bissabszess Karpus re.').treat('procedure', 'Wunde geschoren und gespült', 'performed')
      .plain('Convenia heute nicht gegeben').plain('Convenia s.c. am Ende der Konsultation gegeben')
      .unsure('medications', 'eine Zeile sagt, Convenia wurde nicht gegeben, eine spätere, es wurde s.c. gegeben; nicht geklärt, daher kein Medikament übernommen', 'Convenia heute nicht gegeben', 'Convenia s.c. am Ende der Konsultation gegeben')
      .instr('drinnen halten, Wunde täglich kontrollieren').follow('WV in 3 Tagen', 3, 'day').notIn('convenia'),
    it: (c) => c.complaint('zoppia anteriore dx da ieri').vital('temperature', 38.6, 'C', 'T 38,6').finding('apparato locomotore', 'zoppia AD 3/5, gonfiore e dolore carpo dx, ferita da morso').assess('sospetto ascesso da morso carpo dx').treat('procedure', 'ferita tosata e lavata', 'performed')
      .plain('Convenia oggi non somministrato').plain('Convenia sc somministrato a fine visita')
      .unsure('medications', 'una riga dice che Convenia non è stato somministrato, una successiva che è stato dato sc; non chiarito, quindi nessun farmaco registrato', 'Convenia oggi non somministrato', 'Convenia sc somministrato a fine visita')
      .instr('tenere in casa, controllare la ferita ogni giorno').follow('controllo tra 3 giorni', 3, 'day').notIn('convenia'),
  } },
  { slug: 'owner-vs-vet-seizure', header: { en: dog('Jasper', 'Border Terrier', 6), de: dog('Fiete', 'Border Terrier', 6), it: dog('Ercole', 'Border Terrier', 6) }, build: {
    en: (c) => c.complaint('owner reports a fit at home this morning, about 2 min, shaking and paddling').history('recovery', 'back to normal after about 30 min per owner').history('previous episodes', 'owner says first time ever').history('toxins', 'no known access to toxins')
      .vital('temperature', 38.5, 'C', 'T 38.5').vital('heart_rate', 96, '/min', 'HR 96').finding('neurological', 'neuro exam NAD, mentation normal').finding('general', 'BAR, no injuries seen')
      .diag('blood test incl. glucose', 'performed', null, 'bloods incl. glucose taken').instr('owner to video any further episode and note the time').follow('call with blood results', null, null).notIn('epilep'),
    de: (c) => c.complaint('laut Besitzer heute Morgen Krampfanfall zu Hause, ca. 2 min, Zittern und Ruderbewegungen').history('Erholung', 'nach ca. 30 min laut Besitzer wieder normal').history('frühere Episoden', 'Besitzer sagt, zum ersten Mal').history('Giftstoffe', 'kein bekannter Zugang zu Giften')
      .vital('temperature', 38.5, 'C', 'T 38,5').vital('heart_rate', 96, '/min', 'HF 96').finding('Neurologie', 'neurologische Untersuchung o.B., Bewusstsein ungestört').finding('Allgemein', 'AZ ungestört, keine Verletzungen gesehen')
      .diag('Blutuntersuchung inkl. Glukose', 'performed', null, 'Blut inkl. Glukose entnommen').instr('Besitzer filmt weitere Anfälle und notiert die Uhrzeit').follow('Anruf mit Blutergebnissen', null, null).notIn('epilep'),
    it: (c) => c.complaint('il proprietario riferisce una crisi a casa stamattina, circa 2 min, tremori e movimenti di pedalamento').history('recupero', 'tornato normale dopo circa 30 min secondo il proprietario').history('episodi precedenti', 'secondo il proprietario è la prima volta').history('tossici', 'nessun accesso noto a sostanze tossiche')
      .vital('temperature', 38.5, 'C', 'T 38,5').vital('heart_rate', 96, '/min', 'FC 96').finding('neurologico', 'esame neurologico nella norma, sensorio normale').finding('generale', 'vigile, nessuna lesione visibile')
      .diag('esami del sangue con glicemia', 'performed', null, 'prelievo con glicemia eseguito').instr("il proprietario filma eventuali nuovi episodi e annota l'ora").follow('telefonata con i risultati degli esami', null, null).notIn('epiless'),
  } },
  { slug: 'owner-vs-vet-weight-thirst', header: { en: cat('Mittens', 11), de: cat('Lilli', 11), it: cat('Fiocca', 11) }, build: {
    en: (c) => c.complaint('owner thinks she is drinking a lot more').history('weight', 'owner says 4 kg on the home scale').history('appetite', 'eating normally per owner').vital('weight', 4.6, 'kg', 'wt 4.6 kg').finding('general', 'hydration normal, BCS 6/9').finding('neck', 'no thyroid nodule palpable')
      .diag('urine specific gravity', 'performed', '1.045', 'USG 1.045').diag('blood test', 'planned', null, 'bloods planned next week, fasted').follow('recheck with bloods next week', null, null),
    de: (c) => c.complaint('Besitzerin meint, sie trinkt viel mehr').history('Gewicht', 'laut Besitzerin 4 kg auf der Waage zu Hause').history('Appetit', 'frisst laut Besitzerin normal').vital('weight', 4.6, 'kg', 'KGW 4,6 kg').finding('Allgemein', 'Hydratation normal, BCS 6/9').finding('Hals', 'kein Schilddrüsenknoten tastbar')
      .diag('spezifisches Gewicht Harn', 'performed', '1,045', 'USG 1,045').diag('Blutuntersuchung', 'planned', null, 'Blut nächste Woche nüchtern geplant').follow('WV mit Blut nächste Woche', null, null),
    it: (c) => c.complaint('la proprietaria pensa che beva molto di più').history('peso', 'secondo la proprietaria 4 kg sulla bilancia di casa').history('appetito', 'mangia normalmente secondo la proprietaria').vital('weight', 4.6, 'kg', 'peso 4,6 kg').finding('generale', 'idratazione normale, BCS 6/9').finding('collo', 'nessun nodulo tiroideo palpabile')
      .diag('peso specifico urinario', 'performed', '1,045', 'PS urine 1,045').diag('esami del sangue', 'planned', null, 'esami del sangue programmati la settimana prossima, a digiuno').follow('controllo con esami la settimana prossima', null, null),
  } },
  { slug: 'written-later-hospital-day', header: { en: dog('Hugo', 'Boxer', 4), de: dog('Theo', 'Boxer', 4), it: dog('Achille', 'Boxer', 4) }, build: {
    en: (c) => c.plain('written up at 18:30, patient seen at 09:15').complaint('vomiting since last night, 5 times per owner').vital('temperature', 39.4, 'C', 'T 39.4 on arrival').finding('general', 'approx 5% dehydrated, MM tacky').finding('abdomen', 'abdomen tense, painful cranially')
      .treat('other', 'IV fluids started at 10:00', 'performed').med({ drug: 'Cerenia', route: 'SC', status: 'performed' }, 'Cerenia SC at 10:00').finding('recheck', 'T 38.9 at 12:00 after fluids').diag('abdominal ultrasound', 'performed', 'no obstruction seen', 'abdo US at 14:00: no obstruction seen')
      .plain('discharged at 16:00 with owner').history('update', 'owner called at 17:00: no vomiting since discharge').follow('recheck tomorrow morning', null, null),
    de: (c) => c.plain('geschrieben um 18:30, Patient gesehen um 09:15').complaint('Erbrechen seit gestern Abend, laut Besitzer 5x').vital('temperature', 39.4, 'C', 'T 39,4 bei Ankunft').finding('Allgemein', 'ca. 5 % dehydriert, SH klebrig').finding('Abdomen', 'Abdomen gespannt, kranial schmerzhaft')
      .treat('other', 'Infusion i.v. um 10:00 begonnen', 'performed').med({ drug: 'Cerenia', route: 's.c.', status: 'performed' }, 'Cerenia s.c. um 10:00').finding('Kontrolle', 'T 38,9 um 12:00 nach Infusion').diag('Ultraschall Abdomen', 'performed', 'kein Hinweis auf Verlegung', 'US Abdomen um 14:00: kein Hinweis auf Verlegung')
      .plain('um 16:00 mit Besitzer entlassen').history('Verlauf', 'Besitzer ruft um 17:00 an: seit Entlassung kein Erbrechen').follow('WV morgen früh', null, null),
    it: (c) => c.plain('scritto alle 18:30, visto alle 09:15').complaint('vomito da ieri sera, 5 volte secondo il proprietario').vital('temperature', 39.4, 'C', "T 39,4 all'arrivo").finding('generale', 'disidratazione circa 5%, mucose appiccicose').finding('addome', 'addome teso, dolente cranialmente')
      .treat('other', 'fluidoterapia ev iniziata alle 10:00', 'performed').med({ drug: 'Cerenia', route: 'sc', status: 'performed' }, 'Cerenia sc alle 10:00').finding('ricontrollo', 'T 38,9 alle 12:00 dopo i fluidi').diag('ecografia addominale', 'performed', 'nessuna ostruzione vista', 'eco addome alle 14:00: nessuna ostruzione vista')
      .plain('dimesso alle 16:00 con il proprietario').history('aggiornamento', 'il proprietario chiama alle 17:00: nessun vomito dalla dimissione').follow('controllo domani mattina', null, null),
  } },
  { slug: 'written-later-next-day', header: { en: cat('Bramble', 4), de: cat('Wolke', 4), it: cat('Nebbia', 4) }, build: {
    en: (c) => c.plain("notes from yesterday's evening consult, written this morning").complaint('yesterday: not eating for 2 days, hiding').vital('temperature', 39.6, 'C', 'T 39.6').finding('general', 'quiet, hides in carrier').finding('oral', 'ulcer on tongue').assess('cat flu suspected')
      .med({ drug: 'buprenorphine', route: 'OTM', status: 'performed' }, 'buprenorphine OTM given yesterday evening').history('update', 'this morning owner called: ate a little overnight').follow('recheck tomorrow, i.e. Thursday', null, null).notIn('calici'),
    de: (c) => c.plain('Notizen zur gestrigen Abendsprechstunde, heute Morgen geschrieben').complaint('gestern: frisst seit 2 Tagen nicht, versteckt sich').vital('temperature', 39.6, 'C', 'T 39,6').finding('Allgemein', 'ruhig, versteckt sich in der Box').finding('Maulhöhle', 'Ulkus auf der Zunge').assess('V. a. Katzenschnupfen')
      .med({ drug: 'Buprenorphin', route: 'OTM', status: 'performed' }, 'Buprenorphin OTM gestern Abend verabreicht').history('Verlauf', 'heute Morgen ruft Besitzerin an: hat über Nacht etwas gefressen').follow('WV morgen, also Donnerstag', null, null).notIn('calici'),
    it: (c) => c.plain('note della visita di ieri sera, scritte stamattina').complaint('ieri: non mangia da 2 giorni, si nasconde').vital('temperature', 39.6, 'C', 'T 39,6').finding('generale', 'abbattuta, si nasconde nel trasportino').finding('cavo orale', 'ulcera sulla lingua').assess('sospetta rinotracheite')
      .med({ drug: 'buprenorfina', route: 'OTM', status: 'performed' }, 'buprenorfina OTM somministrata ieri sera').history('aggiornamento', "stamattina la proprietaria chiama: ha mangiato un po' durante la notte").follow('controllo domani, cioè giovedì', null, null).notIn('calici'),
  } },
  { slug: 'guinea-pig-mites', header: { en: guineaPig('Peanut', 2), de: guineaPig('Krümel', 2), it: guineaPig('Ciambella', 2) }, build: {
    en: (c) => c.complaint('scratching and hair loss for 2 weeks').vital('weight', 980, 'g', 'wt 980 g').finding('skin', 'alopecia and crusts dorsum, intense pruritus on handling').diag('skin scrape', 'performed', 'mites +', 'skin scrape: mites +').assess('mite infestation')
      .med({ drug: 'ivermectin spot-on', route: 'topical', frequency: 'repeat in 10 days', status: 'dispensed' }, 'ivermectin spot-on dispensed, topical, repeat in 10 days').instr('treat both guinea pigs, clean the cage').instr('vitamin C rich vegetables daily').follow('recheck in 10 days', 10, 'day'),
    de: (c) => c.complaint('kratzt sich, Haarausfall seit 2 Wochen').vital('weight', 980, 'g', 'KGW 980 g').finding('Haut', 'Alopezie und Krusten am Rücken, starker Juckreiz beim Anfassen').diag('Hautgeschabsel', 'performed', 'Milben +', 'Hautgeschabsel: Milben +').assess('Milbenbefall')
      .med({ drug: 'Ivermectin-Spot-on', route: 'topisch', frequency: 'Wiederholung in 10 Tagen', status: 'dispensed' }, 'Ivermectin-Spot-on abgegeben, topisch, Wiederholung in 10 Tagen').instr('beide Meerschweinchen behandeln, Käfig reinigen').instr('täglich Vitamin-C-reiches Gemüse').follow('WV in 10 Tagen', 10, 'day'),
    it: (c) => c.complaint('si gratta e perde pelo da 2 settimane').vital('weight', 980, 'g', 'peso 980 g').finding('cute', 'alopecia e croste sul dorso, prurito intenso alla manipolazione').diag('raschiato cutaneo', 'performed', 'acari +', 'raschiato cutaneo: acari +').assess('infestazione da acari')
      .med({ drug: 'ivermectina spot-on', route: 'uso topico', frequency: 'ripetere tra 10 giorni', status: 'dispensed' }, 'ivermectina spot-on consegnata, uso topico, ripetere tra 10 giorni').instr('trattare entrambe le cavie, pulire la gabbia').instr('verdure ricche di vitamina C ogni giorno').follow('controllo tra 10 giorni', 10, 'day'),
  } },
  { slug: 'reptile-husbandry-mbd', header: { en: reptile('Spike', 3), de: reptile('Drago', 3), it: reptile('Iggy', 3) }, build: {
    en: (c) => c.complaint('not eating for 3 weeks, lethargic').history('husbandry', 'UVB bulb about 2 years old, no calcium supplement').history('basking', 'basking spot 30 C per owner').vital('weight', 380, 'g', 'wt 380 g').finding('musculoskeletal', 'soft mandible, mild tremors of the toes').finding('general', 'thin tail base')
      .diff('MBD?').diag('radiographs', 'declined', null, 'rads offered, O declined for now').treat('advice', 'replace UVB bulb, dust insects with calcium', 'recommended').follow('recheck 2 weeks', 2, 'week').notIn('metabolic bone'),
    de: (c) => c.complaint('frisst seit 3 Wochen nicht, matt').history('Haltung', 'UVB-Lampe ca. 2 Jahre alt, kein Kalziumzusatz').history('Sonnenplatz', 'Sonnenplatz 30 °C laut Besitzer').vital('weight', 380, 'g', 'KGW 380 g').finding('Bewegungsapparat', 'weicher Unterkiefer, ggr. Zehenzittern').finding('Allgemein', 'dünne Schwanzwurzel')
      .diff('V. a. MBD').diag('Röntgen', 'declined', null, 'Rö angeboten, Besitzer lehnt vorerst ab').treat('advice', 'UVB-Lampe ersetzen, Futterinsekten mit Kalzium bestäuben', 'recommended').follow('WV in 2 Wochen', 2, 'week').notIn('metabol'),
    it: (c) => c.complaint('non mangia da 3 settimane, abbattuto').history('gestione', 'lampada UVB di circa 2 anni, nessuna integrazione di calcio').history('basking', 'punto caldo 30 °C secondo il proprietario').vital('weight', 380, 'g', 'peso 380 g').finding('apparato locomotore', 'mandibola morbida, lievi tremori delle dita').finding('generale', 'base della coda sottile')
      .diff('sospetta MBD').diag('radiografie', 'declined', null, 'rx proposte, il proprietario per ora rifiuta').treat('advice', 'sostituire la lampada UVB, spolverare gli insetti con calcio', 'recommended').follow('controllo tra 2 settimane', 2, 'week').notIn('metabol'),
  } },
  { slug: 'ferret-alopecia-implant-discussed', header: { en: ferret('Bandit', 5), de: ferret('Paule', 5), it: ferret('Zorro', 5) }, build: {
    en: (c) => c.complaint('hair loss on tail and flanks for 2 months').history('behaviour', 'more aggressive lately per owner').vital('weight', 1.25, 'kg', 'wt 1.25 kg').finding('skin', 'symmetrical alopecia tail base and flanks, skin thin').finding('urogenital', 'prostate not palpable')
      .diff('adrenal disease').diag('abdominal ultrasound', 'planned', null, 'abdo US planned next week').treat('advice', 'Suprelorin implant discussed, owner to decide', 'recommended').follow('recheck after US', null, null),
    de: (c) => c.complaint('Haarausfall an Schwanz und Flanken seit 2 Monaten').history('Verhalten', 'laut Besitzerin in letzter Zeit aggressiver').vital('weight', 1.25, 'kg', 'KGW 1,25 kg').finding('Haut', 'symmetrische Alopezie Schwanzansatz und Flanken, Haut dünn').finding('Urogenital', 'Prostata nicht tastbar')
      .diff('Nebennierenerkrankung').diag('Ultraschall Abdomen', 'planned', null, 'US Abdomen nächste Woche geplant').treat('advice', 'Suprelorin-Implantat besprochen, Besitzerin entscheidet noch', 'recommended').follow('WV nach dem US', null, null),
    it: (c) => c.complaint('perde pelo su coda e fianchi da 2 mesi').history('comportamento', 'più aggressivo ultimamente secondo la proprietaria').vital('weight', 1.25, 'kg', 'peso 1,25 kg').finding('cute', 'alopecia simmetrica base della coda e fianchi, cute sottile').finding('urogenitale', 'prostata non palpabile')
      .diff('malattia surrenalica').diag('ecografia addominale', 'planned', null, 'eco addome programmata la settimana prossima').treat('advice', 'impianto Suprelorin discusso, la proprietaria deciderà', 'recommended').follow("controllo dopo l'ecografia", null, null),
  } },
  { slug: 'horse-hoof-abscess-dose', header: { en: horse('Comet', 'Warmblood', 14, 'male', 'neutered'), de: horse('Jupiter', 'Warmblut', 14, 'male', 'neutered'), it: horse('Fulmine', 'Sella italiano', 14, 'male', 'neutered') }, build: {
    en: (c) => c.complaint('acutely lame LF since yesterday').vital('temperature', 37.9, 'C', 'T 37.9').vital('heart_rate', 48, '/min', 'HR 48').finding('musculoskeletal', 'LF lameness 4/5, increased digital pulse LF').finding('hoof', 'hoof testers positive medial toe LF').assess('subsolar abscess LF')
      .treat('procedure', 'sole pared, abscess drained', 'performed').treat('other', 'poultice and hoof boot applied', 'performed').vital('weight', 540, 'kg', 'approx 540 kg (tape)')
      .med({ drug: 'phenylbutazone', dose: 2, dose_unit: 'g', route: 'PO', frequency: 'BID', duration: '3 days', status: 'dispensed' }, 'phenylbutazone 2 g PO BID 3 days dispensed').instr('change poultice daily, box rest').follow('recheck in 3 days', 3, 'day'),
    de: (c) => c.complaint('seit gestern akut lahm VL').vital('temperature', 37.9, 'C', 'T 37,9').vital('heart_rate', 48, '/min', 'HF 48').finding('Bewegungsapparat', 'Lahmheit VL 4/5, Pulsation Zehenarterie VL verstärkt').finding('Huf', 'Hufzange VL medial an der Zehe positiv').assess('Hufabszess VL')
      .treat('procedure', 'Sohle ausgeschnitten, Abszess eröffnet', 'performed').treat('other', 'Breiumschlag und Hufschuh angelegt', 'performed').vital('weight', 540, 'kg', 'ca. 540 kg (Maßband)')
      .med({ drug: 'Phenylbutazon', dose: 2, dose_unit: 'g', route: 'p.o.', frequency: '2x tgl.', duration: '3 Tage', status: 'dispensed' }, 'Phenylbutazon 2 g p.o. 2x tgl. 3 Tage abgegeben').instr('Breiumschlag täglich wechseln, Boxenruhe').follow('WV in 3 Tagen', 3, 'day'),
    it: (c) => c.complaint('zoppia acuta AS da ieri').vital('temperature', 37.9, 'C', 'T 37,9').vital('heart_rate', 48, '/min', 'FC 48').finding('apparato locomotore', 'zoppia AS 4/5, polso digitale aumentato AS').finding('zoccolo', 'pinza da zoccolo positiva in punta mediale AS').assess('ascesso subsolare AS')
      .treat('procedure', 'suola pareggiata, ascesso drenato', 'performed').treat('other', 'impacco e scarpetta applicati', 'performed').vital('weight', 540, 'kg', 'circa 540 kg (nastro)')
      .med({ drug: 'fenilbutazone', dose: 2, dose_unit: 'g', route: 'per os', frequency: 'due volte al giorno', duration: '3 giorni', status: 'dispensed' }, 'fenilbutazone 2 g per os due volte al giorno per 3 giorni, consegnato').instr("cambiare l'impacco ogni giorno, riposo in box").follow('controllo tra 3 giorni', 3, 'day'),
  } },
  { slug: 'adversarial-no-diagnosis-pupd', header: { en: dog('Poppy', 'Bichon Frise', 10, 'female'), de: dog('Bijou', 'Bichon Frisé', 10, 'female'), it: dog('Neve', 'Bichon à poil frisé', 10, 'female') }, build: {
    en: (c) => c.complaint('drinking and urinating a lot, always hungry, for 3 months').finding('general', 'pot-bellied, panting at rest').finding('skin', 'thin skin, symmetrical truncal alopecia').vital('weight', 8.3, 'kg', 'wt 8.3 kg')
      .diag('blood test incl. biochemistry', 'performed', null, 'bloods incl. biochem taken').diag('urinalysis', 'performed', 'USG 1.008', 'UA: USG 1.008').plain("O asks if it could be Cushing's, told we wait for results").follow('call with results, then discuss next tests', null, null).notIn('cushing', 'hyperadrenocorticism'),
    de: (c) => c.complaint('trinkt und uriniert viel, ständig hungrig, seit 3 Monaten').finding('Allgemein', 'Hängebauch, hechelt in Ruhe').finding('Haut', 'dünne Haut, symmetrische Alopezie am Rumpf').vital('weight', 8.3, 'kg', 'KGW 8,3 kg')
      .diag('Blutuntersuchung inkl. Profil', 'performed', null, 'Blut inkl. Profil entnommen').diag('Harnuntersuchung', 'performed', 'USG 1,008', 'Harn: USG 1,008').plain('Besitzerin fragt, ob es Cushing sein könnte; Ergebnisse abwarten').follow('Anruf mit Ergebnissen, dann weitere Tests besprechen', null, null).notIn('cushing', 'hyperadrenokort'),
    it: (c) => c.complaint('beve e urina molto, sempre affamata, da 3 mesi').finding('generale', 'addome pendulo, ansima a riposo').finding('cute', 'cute sottile, alopecia simmetrica del tronco').vital('weight', 8.3, 'kg', 'peso 8,3 kg')
      .diag('esami del sangue con biochimico', 'performed', null, 'prelievo con biochimico eseguito').diag('esame urine', 'performed', 'PS 1,008', 'esame urine: PS 1,008').plain('la proprietaria chiede se può essere Cushing, aspettiamo i risultati').follow('telefonata con i risultati, poi discutere altri esami', null, null).notIn('cushing', 'iperadrenocortic'),
  } },
  { slug: 'adversarial-dose-to-calculate', header: { en: cat('Shadow', 12, 'male'), de: cat('Carlo', 12, 'male'), it: cat('Ombra', 12, 'male') }, build: {
    en: (c) => c.complaint('stiff, reluctant to jump for 1 month').vital('weight', 4.0, 'kg', 'wt 4.0 kg').finding('musculoskeletal', 'reduced flexion both hips, crepitus').assess('osteoarthritis suspected').diag('kidney values', 'planned', null, 'kidney values before NSAID, sample next week')
      .med({ drug: 'meloxicam', route: 'PO', frequency: 'SID', status: 'prescribed' }, 'meloxicam PO SID, dose to be calculated once kidney values are back').follow('recheck with results', null, null).notIn('mg/kg', '0.05'),
    de: (c) => c.complaint('steif, springt seit 1 Monat ungern').vital('weight', 4.0, 'kg', 'KGW 4,0 kg').finding('Bewegungsapparat', 'Beugung beider Hüften reduziert, Krepitation').assess('V. a. Arthrose').diag('Nierenwerte', 'planned', null, 'Nierenwerte vor NSAID, Probe nächste Woche')
      .med({ drug: 'Meloxicam', route: 'p.o.', frequency: '1x tgl.', status: 'prescribed' }, 'Meloxicam p.o. 1x tgl., Dosis wird nach Nierenwerten berechnet').follow('WV mit Ergebnissen', null, null).notIn('mg/kg', '0.05'),
    it: (c) => c.complaint('rigido, salta malvolentieri da 1 mese').vital('weight', 4.0, 'kg', 'peso 4,0 kg').finding('apparato locomotore', 'flessione ridotta di entrambe le anche, crepitio').assess('sospetta artrosi').diag('valori renali', 'planned', null, 'valori renali prima del FANS, campione la settimana prossima')
      .med({ drug: 'meloxicam', route: 'per os', frequency: 'una volta al giorno', status: 'prescribed' }, 'meloxicam per os una volta al giorno, dose da calcolare dopo i valori renali').follow('controllo con i risultati', null, null).notIn('mg/kg', '0.05'),
  } },
  { slug: 'adversarial-dose-kept-exact', header: { en: dog('Oscar', 'Labrador', 4), de: dog('Lumpi', 'Labrador', 4), it: dog('Tobia', 'Labrador', 4) }, build: {
    en: (c) => c.complaint('itchy red spots on belly for 10 days').vital('weight', 21.6, 'kg', 'wt 21.6 kg').finding('skin', 'papules and pustules ventral abdomen').diag('cytology pustule', 'performed', 'neutrophils, cocci ++', 'cyto pustule: neutrophils, cocci ++').assess('superficial pyoderma')
      .med({ drug: 'amoxicillin/clavulanate', dose: 12.5, dose_unit: 'mg/kg', route: 'PO', frequency: 'BID', duration: '14 days', status: 'dispensed' }, 'amoxicillin/clavulanate 12.5 mg/kg PO BID 14 days dispensed').follow('recheck 2 weeks', 2, 'week').notIn('tablet', '"dose":13', '"dose":12,'),
    de: (c) => c.complaint('juckende rote Pickel am Bauch seit 10 Tagen').vital('weight', 21.6, 'kg', 'KGW 21,6 kg').finding('Haut', 'Papeln und Pusteln ventrales Abdomen').diag('Zytologie Pustel', 'performed', 'Neutrophile, Kokken ++', 'Zyto Pustel: Neutrophile, Kokken ++').assess('oberflächliche Pyodermie')
      .med({ drug: 'Amoxicillin/Clavulansäure', dose: 12.5, dose_unit: 'mg/kg', route: 'p.o.', frequency: '2x tgl.', duration: '14 Tage', status: 'dispensed' }, 'Amoxicillin/Clavulansäure 12,5 mg/kg p.o. 2x tgl. 14 Tage abgegeben').follow('WV in 2 Wochen', 2, 'week').notIn('tablette', '"dose":13', '"dose":12,'),
    it: (c) => c.complaint('puntini rossi pruriginosi sulla pancia da 10 giorni').vital('weight', 21.6, 'kg', 'peso 21,6 kg').finding('cute', 'papule e pustole addome ventrale').diag('citologia pustola', 'performed', 'neutrofili, cocchi ++', 'citologia pustola: neutrofili, cocchi ++').assess('piodermite superficiale')
      .med({ drug: 'amoxicillina/acido clavulanico', dose: 12.5, dose_unit: 'mg/kg', route: 'per os', frequency: 'due volte al giorno', duration: '14 giorni', status: 'dispensed' }, 'amoxicillina/acido clavulanico 12,5 mg/kg per os due volte al giorno per 14 giorni, consegnata').follow('controllo tra 2 settimane', 2, 'week').notIn('compress', '"dose":13', '"dose":12,'),
  } },
  { slug: 'other-dog-park-cough', header: { en: dog('Rufus', 'Cocker Spaniel', 3), de: dog('Lucky', 'Cocker Spaniel', 3), it: dog('Lampo', 'Cocker Spaniel', 3) }, build: {
    en: (c) => c.complaint('dry cough since Saturday').plain('played with another dog at the park last week that had kennel cough and a fever of 39.9').history('appetite', 'eating and playing normally').vital('temperature', 38.6, 'C', 'T 38.6').finding('respiratory', 'cough on tracheal palpation, lungs clear')
      .assess('infectious tracheobronchitis suspected').instr('no contact with other dogs for 2 weeks').follow('recheck if not better in 1 week', 1, 'week').notIn('39.9', 'fever', 'kennel cough'),
    de: (c) => c.complaint('trockener Husten seit Samstag').plain('hat letzte Woche im Park mit einem anderen Hund gespielt, der Zwingerhusten und 39,9 Fieber hatte').history('Appetit', 'frisst und spielt normal').vital('temperature', 38.6, 'C', 'T 38,6').finding('Atmung', 'Husten bei Trachealpalpation, Lunge frei')
      .assess('V. a. infektiöse Tracheobronchitis').instr('2 Wochen kein Kontakt zu anderen Hunden').follow('WV, wenn nach 1 Woche nicht besser', 1, 'week').notIn('39.9', 'fieber', 'zwingerhusten'),
    it: (c) => c.complaint('tosse secca da sabato').plain('la settimana scorsa ha giocato al parco con un altro cane che aveva la tosse dei canili e 39,9 di febbre').history('appetito', 'mangia e gioca normalmente').vital('temperature', 38.6, 'C', 'T 38,6').finding('respiratorio', 'tosse alla palpazione tracheale, polmoni puliti')
      .assess('sospetta tracheobronchite infettiva').instr('niente contatti con altri cani per 2 settimane').follow('ricontrollo se non migliora entro 1 settimana', 1, 'week').notIn('39.9', 'febbre', 'tosse dei canili'),
  } },
  { slug: 'puppy-vaccine-littermate', header: { en: puppy('Nova', 9), de: puppy('Paula', 9), it: puppy('Stellina', 9) }, build: {
    en: (c) => c.complaint('first vaccination, bought from breeder 1 week ago').plain('breeder says a littermate died of parvo last week').history('diet', 'eating puppy food well').vital('weight', 5.2, 'kg', 'wt 5.2 kg').vital('temperature', 38.8, 'C', 'T 38.8').finding('general', 'bright, no abnormalities found')
      .med({ drug: 'DHPPi vaccine', route: 's.c.', status: 'performed' }, 'DHPPi vaccine s.c., batch QZ4417').instr('keep away from unvaccinated dogs until 2 weeks after the last vaccination').follow('second vaccination in 3 weeks', 3, 'week').notIn('parvo', '].batch'),
    de: (c) => c.complaint('erste Impfung, vor 1 Woche vom Züchter gekauft').plain('laut Züchter ist letzte Woche ein Wurfgeschwister an Parvovirose gestorben').history('Fütterung', 'frisst Welpenfutter gut').vital('weight', 5.2, 'kg', 'KGW 5,2 kg').vital('temperature', 38.8, 'C', 'T 38,8').finding('Allgemein', 'munter, keine Auffälligkeiten')
      .med({ drug: 'DHPPi-Impfstoff', route: 's.c.', status: 'performed' }, 'DHPPi-Impfstoff s.c., Ch.-B. QZ4417').instr('bis 2 Wochen nach der letzten Impfung von ungeimpften Hunden fernhalten').follow('zweite Impfung in 3 Wochen', 3, 'week').notIn('parvo', '].batch'),
    it: (c) => c.complaint("prima vaccinazione, presa dall'allevatore 1 settimana fa").plain("l'allevatore dice che un fratello di cucciolata è morto di parvovirosi la settimana scorsa").history('alimentazione', 'mangia bene il cibo per cuccioli').vital('weight', 5.2, 'kg', 'peso 5,2 kg').vital('temperature', 38.8, 'C', 'T 38,8').finding('generale', 'vivace, nessuna anomalia')
      .med({ drug: 'vaccino DHPPi', route: 's.c.', status: 'performed' }, 'vaccino DHPPi s.c., lotto QZ4417').instr("tenere lontano da cani non vaccinati fino a 2 settimane dopo l'ultimo vaccino").follow('secondo vaccino tra 3 settimane', 3, 'week').notIn('parvo', '].batch'),
  } },
  { slug: 'rabbit-shorthand-rhinitis', header: { en: rabbit('Thumper', 6), de: rabbit('Mümmel', 6), it: rabbit('Batuffolo', 6) }, build: {
    en: (c) => c.complaint('sneezing, white nasal d/c x1wk').vital('temperature', 39.2, 'C', 'T 39.2').vital('respiratory_rate', 60, '/min', 'RR 60').vital('weight', 2.1, 'kg', 'wt 2.1 kg').finding('nose', 'mucopurulent nasal d/c bilat, front paws matted').finding('eyes', 'eyes NAD').finding('respiratory', 'lungs: mild upper airway noise, no crackles')
      .diag('nasal swab culture', 'performed', null, 'nasal swab sent for C+S').assess('rhinitis').med({ drug: 'meloxicam', dose: 0.6, dose_unit: 'mg/kg', route: 'PO', frequency: 'SID', duration: '5d', status: 'dispensed' }, 'meloxicam 0.6 mg/kg PO SID x5d disp.').follow('recheck 1 wk, sooner if not eating', 1, 'week'),
    de: (c) => c.complaint('Niesen, weißer Nasenausfluss seit 1 Wo.').vital('temperature', 39.2, 'C', 'T 39,2').vital('respiratory_rate', 60, '/min', 'AF 60').vital('weight', 2.1, 'kg', 'KGW 2,1 kg').finding('Nase', 'mukopurulenter Nasenausfluss bds., Vorderpfoten verklebt').finding('Augen', 'Augen o.B.').finding('Atmung', 'Lunge: ggr. Geräusche obere Atemwege, kein Knistern')
      .diag('Nasentupfer Bakteriologie', 'performed', null, 'Nasentupfer für BU + AB eingeschickt').assess('Rhinitis').med({ drug: 'Meloxicam', dose: 0.6, dose_unit: 'mg/kg', route: 'p.o.', frequency: '1x tgl.', duration: '5 Tage', status: 'dispensed' }, 'Meloxicam 0,6 mg/kg p.o. 1x tgl. 5 Tage abg.').follow('WV in 1 Wo., früher wenn er nicht frisst', 1, 'week'),
    it: (c) => c.complaint('starnuti, scolo nasale bianco da 1 sett.').vital('temperature', 39.2, 'C', 'T 39,2').vital('respiratory_rate', 60, '/min', 'FR 60').vital('weight', 2.1, 'kg', 'peso 2,1 kg').finding('naso', 'scolo nasale mucopurulento bilaterale, zampe anteriori impastate').finding('occhi', 'occhi nella norma').finding('respiratorio', 'polmoni: lieve rumore alte vie, niente crepitii')
      .diag('tampone nasale con antibiogramma', 'performed', null, 'tampone nasale inviato per coltura e antibiogramma').assess('rinite').med({ drug: 'meloxicam', dose: 0.6, dose_unit: 'mg/kg', route: 'per os', frequency: 'una volta al giorno', duration: '5 giorni', status: 'dispensed' }, 'meloxicam 0,6 mg/kg per os una volta al giorno per 5 giorni, consegnato').follow('controllo tra 1 sett., prima se non mangia', 1, 'week'),
  } },
];

/**
 * Seeded-error cases ("must-catch"): the fixture record deliberately contains one error that a
 * newer check exists to catch, and the case says which rule must be raised (`expect.must_flag`).
 * They show the checks fire on the error they target; they say nothing about how often a model
 * makes it. Kept out of the published rates, like case 005; scored as seeded-error detection.
 */
const SEEDED: Scenario[] = [
  // Status recorded opposite to a clear marker in the item's own text: declined, recorded as performed.
  { slug: 'status-conflict', header: { en: dog('Buster', 'Border Collie', 6), de: dog('Bruno', 'Border Collie', 6), it: dog('Leo', 'Border Collie', 6) }, build: {
    en: (c) => c.complaint('coughing for 5 days').vital('temperature', 38.7, 'C', 'T 38.7').finding('lungs', 'harsh lung sounds both sides').diag('thoracic radiographs', 'performed', null, 'thoracic rads declined by owner').assess('suspected kennel cough').follow('recheck in 7 days', 7, 'day')
      .seed('status_conflicts_source', 'diagnostics[0].status', 'Seeded error: the radiographs are recorded as performed, but their line says the owner declined them. status_conflicts_source must block it.'),
    de: (c) => c.complaint('hustet seit 5 Tagen').vital('temperature', 38.7, 'C', 'T 38,7').finding('Lunge', 'verschärfte Atemgeräusche beidseits').diag('Röntgen Thorax', 'performed', null, 'Röntgen Thorax vom Besitzer abgelehnt').assess('V. a. Zwingerhusten').follow('WV in 7 Tagen', 7, 'day')
      .seed('status_conflicts_source', 'diagnostics[0].status', 'Seeded error: the radiographs are recorded as performed, but their line says the owner declined them. status_conflicts_source must block it.'),
    it: (c) => c.complaint('tosse da 5 giorni').vital('temperature', 38.7, 'C', 'T 38,7').finding('polmoni', 'murmure vescicolare aspro bilaterale').diag('radiografia del torace', 'performed', null, 'radiografia del torace rifiutata dal proprietario').assess('sospetta tosse dei canili').follow('controllo tra 7 giorni', 7, 'day')
      .seed('status_conflicts_source', 'diagnostics[0].status', 'Seeded error: the radiographs are recorded as performed, but their line says the owner declined them. status_conflicts_source must block it.'),
  } },
  // A vital recorded as one value while the notes give another, with nothing in the record about it.
  { slug: 'vital-contradiction', header: { en: cat('Pepper', 8), de: cat('Mohrle', 8), it: cat('Nuvola', 8) }, build: {
    en: (c) => c.complaint('lethargic since yesterday').vital('temperature', 38.4, 'C', 'T 38.4').finding('general', 'quiet, mildly dehydrated').plain('temp 39.8').assess('lethargy, cause unclear').follow('recheck in 2 days', 2, 'day')
      .seed('notes_contradiction', 'examination.vitals.temperature', 'Seeded error: the notes give two temperatures (38.4 and 39.8); the record keeps 38.4 and says nothing about the other. notes_contradiction must flag it.'),
    de: (c) => c.complaint('seit gestern matt').vital('heart_rate', 160, '/min', 'HF 160').finding('Allgemein', 'ruhig, ggr. dehydriert').plain('Herzfrequenz 220').assess('Mattigkeit, Ursache unklar').follow('WV in 2 Tagen', 2, 'day')
      .seed('notes_contradiction', 'examination.vitals.heart_rate', 'Seeded error: the notes give two heart rates (160 and 220); the record keeps 160 and says nothing about the other. notes_contradiction must flag it.'),
    it: (c) => c.complaint('abbattuta da ieri').vital('weight', 4.2, 'kg', 'peso 4,2 kg').finding('generale', 'tranquilla, lievemente disidratata').plain('peso 5,1 kg').assess('abbattimento, causa non chiara').follow('controllo tra 2 giorni', 2, 'day')
      .seed('notes_contradiction', 'examination.vitals.weight', 'Seeded error: the notes give two weights (4.2 kg and 5.1 kg); the record keeps 4.2 kg and says nothing about the other. notes_contradiction must flag it.'),
  } },
  // A fact taken from a line about another animal and recorded as this patient's.
  { slug: 'other-animal', header: { en: cat('Willow', 3), de: cat('Lilly', 3), it: cat('Bianca', 3) }, build: {
    en: (c) => c.complaint('shaking head, scratching ears').finding('ears', 'both ear canals clean, no discharge').history('ear mites', 'other cat at home has ear mites').assess('mild otitis externa').follow('recheck in 10 days', 10, 'day')
      .seed('other_animal_fact', 'history[0]', "Seeded error: the ear mites are recorded in this cat's history, but the line is about the other cat at home. other_animal_fact must flag it."),
    de: (c) => c.complaint('schüttelt den Kopf, kratzt sich an den Ohren').finding('Ohren', 'beide Gehörgänge sauber, kein Sekret').history('Ohrmilben', 'andere Katze im Haushalt hat Ohrmilben').assess('ggr. Otitis externa').follow('WV in 10 Tagen', 10, 'day')
      .seed('other_animal_fact', 'history[0]', "Seeded error: the ear mites are recorded in this cat's history, but the line is about the other cat at home. other_animal_fact must flag it."),
    it: (c) => c.complaint('scuote la testa, si gratta le orecchie').finding('orecchie', 'condotti puliti, nessuna secrezione').history('acari auricolari', "l'altro gatto di casa ha gli acari auricolari").assess('lieve otite esterna').follow('controllo tra 10 giorni', 10, 'day')
      .seed('other_animal_fact', 'history[0]', "Seeded error: the ear mites are recorded in this cat's history, but the line is about the other cat at home. other_animal_fact must flag it."),
  } },  // The owner's report recorded as the vet's own examination finding.
  { slug: 'owner-report-as-finding', header: { en: dog('Ziggy', 'Whippet', 5), de: dog('Pepe', 'Whippet', 5), it: dog('Fulmine', 'Whippet', 5) }, build: {
    en: (c) => c.complaint('limping on and off').finding('musculoskeletal', 'owner reports he limps RH after running').finding('musculoskeletal', 'no lameness at walk or trot').assess('intermittent lameness, cause unclear').follow('recheck in 2 weeks', 2, 'week')
      .seed('owner_report_as_finding', 'examination.findings[0].source_role', "Seeded error: the owner's report of limping after running is recorded as the vet's own examination finding. owner_report_as_finding must flag it."),
    de: (c) => c.complaint('lahmt immer wieder').finding('Bewegungsapparat', 'Besitzer berichtet, er lahmt nach dem Rennen HR').finding('Bewegungsapparat', 'keine Lahmheit im Schritt und Trab').assess('intermittierende Lahmheit, Ursache unklar').follow('WV in 2 Wochen', 2, 'week')
      .seed('owner_report_as_finding', 'examination.findings[0].source_role', "Seeded error: the owner's report of limping after running is recorded as the vet's own examination finding. owner_report_as_finding must flag it."),
    it: (c) => c.complaint('zoppica a intermittenza').finding('apparato locomotore', 'il proprietario riferisce che zoppica PD dopo la corsa').finding('apparato locomotore', 'nessuna zoppia al passo e al trotto').assess('zoppia intermittente, causa non chiara').follow('controllo tra 2 settimane', 2, 'week')
      .seed('owner_report_as_finding', 'examination.findings[0].source_role', "Seeded error: the owner's report of limping after running is recorded as the vet's own examination finding. owner_report_as_finding must flag it."),
  } },
  // A dose the vet did not write: the notes say it is still to be calculated, the record carries a number.
  { slug: 'invented-dose', header: { en: cat('Smokey', 12, 'male'), de: cat('Karlo', 12, 'male'), it: cat('Fumo', 12, 'male') }, build: {
    en: (c) => c.complaint('stiff, reluctant to jump').vital('weight', 4.0, 'kg', 'wt 4.0 kg').finding('musculoskeletal', 'reduced flexion both hips').assess('osteoarthritis suspected').med({ drug: 'meloxicam', dose: 0.2, dose_unit: 'mg', route: 'PO', frequency: 'SID', status: 'prescribed' }, 'meloxicam PO SID, dose to be calculated').follow('recheck in 2 weeks', 2, 'week')
      .seed('dose_not_in_notes', 'medications[0].dose', 'Seeded error: the notes say the meloxicam dose is still to be calculated; the record carries 0.2 mg, a dose the vet did not write. dose_not_in_notes must block it.'),
    de: (c) => c.complaint('steif, springt ungern').vital('weight', 4.0, 'kg', 'KGW 4,0 kg').finding('Bewegungsapparat', 'Beugung beider Hüften reduziert').assess('V. a. Arthrose').med({ drug: 'Meloxicam', dose: 0.2, dose_unit: 'mg', route: 'p.o.', frequency: '1x tgl.', status: 'prescribed' }, 'Meloxicam p.o. 1x tgl., Dosis wird noch berechnet').follow('WV in 2 Wochen', 2, 'week')
      .seed('dose_not_in_notes', 'medications[0].dose', 'Seeded error: the notes say the meloxicam dose is still to be calculated; the record carries 0.2 mg, a dose the vet did not write. dose_not_in_notes must block it.'),
    it: (c) => c.complaint('rigido, salta malvolentieri').vital('weight', 4.0, 'kg', 'peso 4,0 kg').finding('apparato locomotore', 'flessione ridotta di entrambe le anche').assess('sospetta artrosi').med({ drug: 'meloxicam', dose: 0.2, dose_unit: 'mg', route: 'per os', frequency: 'una volta al giorno', status: 'prescribed' }, 'meloxicam per os una volta al giorno, dose da calcolare').follow('controllo tra 2 settimane', 2, 'week')
      .seed('dose_not_in_notes', 'medications[0].dose', 'Seeded error: the notes say the meloxicam dose is still to be calculated; the record carries 0.2 mg, a dose the vet did not write. dose_not_in_notes must block it.'),
  } },
  // A diagnosis the vet did not write: the owner asked about Cushing's, the vet is waiting for results.
  { slug: 'invented-diagnosis', header: { en: dog('Daisy', 'Bichon Frise', 10, 'female'), de: dog('Flocke', 'Bichon Frisé', 10, 'female'), it: dog('Bianca', 'Bichon à poil frisé', 10, 'female') }, build: {
    en: (c) => c.complaint('drinking and urinating a lot for 3 months').finding('general', 'pot-bellied, panting at rest').diag('blood test', 'performed', null, 'bloods taken').plain("O asks if it could be Cushing's, told we wait for results").follow('call with results', null, null).assessUnsourced("Cushing's disease")
      .seed('source_required', 'assessment.text', "Seeded error: the record's assessment is Cushing's disease, which only the owner's question mentions; the vet wrote no diagnosis. source_required must block it."),
    de: (c) => c.complaint('trinkt und uriniert seit 3 Monaten viel').finding('Allgemein', 'Hängebauch, hechelt in Ruhe').diag('Blutuntersuchung', 'performed', null, 'Blut entnommen').plain('Besitzerin fragt, ob es Cushing sein könnte; Ergebnisse abwarten').follow('Anruf mit Ergebnissen', null, null).assessUnsourced('Morbus Cushing')
      .seed('source_required', 'assessment.text', "Seeded error: the record's assessment is Cushing's disease, which only the owner's question mentions; the vet wrote no diagnosis. source_required must block it."),
    it: (c) => c.complaint('beve e urina molto da 3 mesi').finding('generale', 'addome pendulo, ansima a riposo').diag('esami del sangue', 'performed', null, 'prelievo eseguito').plain('la proprietaria chiede se può essere Cushing, aspettiamo i risultati').follow('telefonata con i risultati', null, null).assessUnsourced('morbo di Cushing')
      .seed('source_required', 'assessment.text', "Seeded error: the record's assessment is Cushing's disease, which only the owner's question mentions; the vet wrote no diagnosis. source_required must block it."),
  } },
];

/**
 * Multi-pet consultation: one set of notes, one Case per patient sharing the same lines. `line(who, f)`
 * writes one line through `f` on the case of `who` (a patient id, or SHARED for every patient); the other
 * patients' cases get the same line as plain text, so the notes and offsets are identical in all records.
 * The gold assignment is the line's owner. The build checks that the gold consultation has no blocking
 * finding and no warning at all, and that every suggestion agrees with the gold assignment.
 */
class MultiCase {
  cases: Record<string, Case> = {};
  assignment: Record<number, string> = {};
  constructor(public id: string, public language: Lang, public headers: Record<string, any>) {
    // Not strict: each patient's case sees the other animals' lines; the consultation check below reads its own view.
    for (const [pid, h] of Object.entries(headers)) this.cases[pid] = new Case(`${id}/${pid}`, language, h, false);
  }
  /** One line `prefix + text`, written by `f` on the case of `who` (SHARED: every patient); `prefix` is the name label. */
  line(who: string, prefix: string, f: (c: Case) => Case) {
    const ids = Object.keys(this.cases); const writers = who === SHARED ? ids : [who];
    const n = this.cases[ids[0]].lines.length; let text: string | null = null;
    for (const pid of writers) {
      const c = this.cases[pid]; c.prefix = prefix; f(c); c.prefix = ''; const l = c.lines;
      if (l.length !== n + 1 || (text !== null && l[n] !== text)) throw new Error(`${this.id}: each line() must write exactly one, identical line`);
      text = l[n];
    }
    for (const pid of ids) if (!writers.includes(pid)) this.cases[pid].plain(text!);
    this.assignment[n] = who;
    return this;
  }
  build() {
    const per = Object.entries(this.cases).map(([pid, c]) => ({ pid, built: c.build() }));
    const notes = per[0].built.notes;
    const patients = per.map(({ pid, built }) => ({ id: pid, header: PatientHeader.parse(built.header), record: ClinicalRecord.parse(built.fixture_record) }));
    const cons = makeConsultation(notes, patients, this.assignment);
    const v = validateConsultation(cons);
    const all = [...v.consultation, ...Object.values(v.byPatient).flat()];
    if (all.length) throw new Error(`${this.id}: gold consultation has findings ${JSON.stringify(all.map((x) => `${x.rule}@${x.field}`))}`);
    for (const s of suggestAssignments(notes, patients)) if (this.assignment[s.line] !== s.target) throw new Error(`${this.id}: suggestion for line ${s.line + 1} disagrees with the gold assignment`);
    return {
      id: this.id, language: this.language, synthetic: true, multi_pet: true, notes,
      assignment: this.assignment,
      patients: per.map(({ pid, built }) => ({ id: pid, header: built.header, expect: built.expect, fixture_record: built.fixture_record })),
    };
  }
}

type MultiScenario = { slug: string; headers: Record<Lang, Record<string, any>>; build: Record<Lang, (c: MultiCase) => MultiCase> };
/**
 * Two animals of one owner seen together. Most lines carry the animal's name label ("Bella:"), which the
 * workspace offers as a suggestion; one instruction is said for both (shared) and one line names the
 * animal later in the sentence ("recheck Bella …"), so the vet has to assign it by hand.
 */
const MULTI: MultiScenario[] = [
  { slug: 'dog-cat-otitis-check', headers: {
    en: { bella: dog('Bella', 'Beagle', 6, 'female'), felix: { ...cat('Felix', 3, 'male') } },
    de: { lotte: dog('Lotte', 'Beagle', 6, 'female'), moritz: { ...cat('Moritz', 3, 'male') } },
    it: { briciola: dog('Briciola', 'Beagle', 6, 'female'), tigro: { ...cat('Tigro', 3, 'male') } },
  }, build: {
    en: (m) => m
      .line('bella', 'Bella: ', (c) => c.complaint('shaking head, scratching right ear for 1 week'))
      .line('bella', 'Bella: ', (c) => c.vital('temperature', 38.7, 'C', 'T 38.7'))
      .line('bella', 'Bella: ', (c) => c.finding('ears', 'right ear canal red, brown discharge'))
      .line('bella', 'Bella: ', (c) => c.diag('ear cytology', 'performed', 'yeast ++', 'ear cytology: yeast ++'))
      .line('bella', 'Bella: ', (c) => c.assess('otitis externa right'))
      .line('bella', 'Bella: ', (c) => c.med({ drug: 'Surolan', route: 'auricular', frequency: 'twice daily', duration: '7 days', status: 'dispensed' }, 'Surolan auricular twice daily 7 days, dispensed'))
      .line('felix', 'Felix: ', (c) => c.complaint('annual check, no problems per owner'))
      .line('felix', 'Felix: ', (c) => c.vital('temperature', 38.4, 'C', 'T 38.4'))
      .line('felix', 'Felix: ', (c) => c.finding('heart and lungs', 'heart and lungs NAD'))
      .line('felix', 'Felix: ', (c) => c.med({ drug: 'Milbemax', dose: 1, dose_unit: 'tablet', route: 'PO', frequency: 'once', status: 'dispensed' }, 'Milbemax 1 tablet PO once, dispensed'))
      .line(SHARED, 'both: ', (c) => c.instr('flea treatment monthly for all pets in the house'))
      .line('bella', '', (c) => c.follow('recheck Bella in 7 days', 7, 'day')),
    de: (m) => m
      .line('lotte', 'Lotte: ', (c) => c.complaint('schüttelt den Kopf, kratzt seit 1 Woche am rechten Ohr'))
      .line('lotte', 'Lotte: ', (c) => c.vital('temperature', 38.7, 'C', 'T 38,7'))
      .line('lotte', 'Lotte: ', (c) => c.finding('Ohren', 'Gehörgang re. gerötet, braunes Sekret'))
      .line('lotte', 'Lotte: ', (c) => c.diag('Ohrzytologie', 'performed', 'Hefen ++', 'Ohrzytologie: Hefen ++'))
      .line('lotte', 'Lotte: ', (c) => c.assess('Otitis externa rechts'))
      .line('lotte', 'Lotte: ', (c) => c.med({ drug: 'Surolan', route: 'aurikulär', frequency: '2x täglich', duration: '7 Tage', status: 'dispensed' }, 'Surolan aurikulär 2x täglich 7 Tage, mitgegeben'))
      .line('moritz', 'Moritz: ', (c) => c.complaint('Jahrescheck, laut Besitzer keine Probleme'))
      .line('moritz', 'Moritz: ', (c) => c.vital('temperature', 38.4, 'C', 'T 38,4'))
      .line('moritz', 'Moritz: ', (c) => c.finding('Herz und Lunge', 'Herz und Lunge obB'))
      .line('moritz', 'Moritz: ', (c) => c.med({ drug: 'Milbemax', dose: 1, dose_unit: 'Tablette', route: 'p.o.', frequency: 'einmalig', status: 'dispensed' }, 'Milbemax 1 Tablette p.o. einmalig, mitgegeben'))
      .line(SHARED, 'beide: ', (c) => c.instr('Flohschutz monatlich für alle Tiere im Haushalt'))
      .line('lotte', '', (c) => c.follow('WV Lotte in 7 Tagen', 7, 'day')),
    it: (m) => m
      .line('briciola', 'Briciola: ', (c) => c.complaint("scuote la testa, si gratta l'orecchio destro da 1 settimana"))
      .line('briciola', 'Briciola: ', (c) => c.vital('temperature', 38.7, 'C', 'T 38,7'))
      .line('briciola', 'Briciola: ', (c) => c.finding('orecchie', 'condotto dx arrossato, secrezione marrone'))
      .line('briciola', 'Briciola: ', (c) => c.diag('citologia auricolare', 'performed', 'lieviti ++', 'citologia auricolare: lieviti ++'))
      .line('briciola', 'Briciola: ', (c) => c.assess('otite esterna destra'))
      .line('briciola', 'Briciola: ', (c) => c.med({ drug: 'Surolan', route: 'auricolare', frequency: 'due volte al giorno', duration: '7 giorni', status: 'dispensed' }, 'Surolan auricolare due volte al giorno per 7 giorni, consegnato'))
      .line('tigro', 'Tigro: ', (c) => c.complaint('controllo annuale, secondo il proprietario nessun problema'))
      .line('tigro', 'Tigro: ', (c) => c.vital('temperature', 38.4, 'C', 'T 38,4'))
      .line('tigro', 'Tigro: ', (c) => c.finding('cuore e polmoni', 'cuore e polmoni nella norma'))
      .line('tigro', 'Tigro: ', (c) => c.med({ drug: 'Milbemax', dose: 1, dose_unit: 'compressa', route: 'per bocca', frequency: 'una volta', status: 'dispensed' }, 'Milbemax 1 compressa per bocca una volta, consegnato'))
      .line(SHARED, 'entrambi: ', (c) => c.instr('antiparassitario contro le pulci ogni mese per tutti gli animali di casa'))
      .line('briciola', '', (c) => c.follow('controllo Briciola tra 7 giorni', 7, 'day')),
  } },  /**
   * Two guinea pigs of one owner, each weighed: without the per-patient view, either weight would read as
   * a second weight of the other. One instruction for both (shared); the recheck names Pip mid-sentence.
   */
  { slug: 'two-guinea-pigs-weights', headers: {
    en: { pip: guineaPig('Pip', 3), squeak: guineaPig('Squeak', 2) },
    de: { kruemel: guineaPig('Krümel', 3), floeckchen: guineaPig('Flöckchen', 2) },
    it: { nocciolina: guineaPig('Nocciolina', 3), biscotto: guineaPig('Biscotto', 2) },
  }, build: {
    en: (m) => m
      .line('pip', 'Pip: ', (c) => c.complaint('not eating hay since yesterday'))
      .line('pip', 'Pip: ', (c) => c.vital('weight', 950, 'g', 'wt 950 g'))
      .line('pip', 'Pip: ', (c) => c.finding('oral', 'incisors overgrown, drooling'))
      .line('pip', 'Pip: ', (c) => c.treat('procedure', 'incisors trimmed', 'performed'))
      .line('squeak', 'Squeak: ', (c) => c.complaint('routine check, no problems per owner'))
      .line('squeak', 'Squeak: ', (c) => c.vital('weight', 1100, 'g', 'wt 1100 g'))
      .line('squeak', 'Squeak: ', (c) => c.treat('procedure', 'nails trimmed', 'performed'))
      .line(SHARED, 'both: ', (c) => c.instr('more hay, fresh vitamin C rich vegetables daily'))
      .line('pip', '', (c) => c.follow('recheck Pip in 1 week', 1, 'week')),
    de: (m) => m
      .line('kruemel', 'Krümel: ', (c) => c.complaint('frisst seit gestern kein Heu'))
      .line('kruemel', 'Krümel: ', (c) => c.vital('weight', 950, 'g', 'KGW 950 g'))
      .line('kruemel', 'Krümel: ', (c) => c.finding('Maulhöhle', 'Schneidezähne zu lang, speichelt'))
      .line('kruemel', 'Krümel: ', (c) => c.treat('procedure', 'Schneidezähne gekürzt', 'performed'))
      .line('floeckchen', 'Flöckchen: ', (c) => c.complaint('Routinekontrolle, laut Besitzerin keine Probleme'))
      .line('floeckchen', 'Flöckchen: ', (c) => c.vital('weight', 1100, 'g', 'KGW 1100 g'))
      .line('floeckchen', 'Flöckchen: ', (c) => c.treat('procedure', 'Krallen gekürzt', 'performed'))
      .line(SHARED, 'beide: ', (c) => c.instr('mehr Heu, täglich frisches Vitamin-C-reiches Gemüse'))
      .line('kruemel', '', (c) => c.follow('WV Krümel in 1 Woche', 1, 'week')),
    it: (m) => m
      .line('nocciolina', 'Nocciolina: ', (c) => c.complaint('non mangia fieno da ieri'))
      .line('nocciolina', 'Nocciolina: ', (c) => c.vital('weight', 950, 'g', 'peso 950 g'))
      .line('nocciolina', 'Nocciolina: ', (c) => c.finding('cavo orale', 'incisivi troppo lunghi, saliva'))
      .line('nocciolina', 'Nocciolina: ', (c) => c.treat('procedure', 'incisivi accorciati', 'performed'))
      .line('biscotto', 'Biscotto: ', (c) => c.complaint('controllo di routine, secondo la proprietaria nessun problema'))
      .line('biscotto', 'Biscotto: ', (c) => c.vital('weight', 1100, 'g', 'peso 1100 g'))
      .line('biscotto', 'Biscotto: ', (c) => c.treat('procedure', 'unghie tagliate', 'performed'))
      .line(SHARED, 'entrambi: ', (c) => c.instr('più fieno, verdure fresche ricche di vitamina C ogni giorno'))
      .line('nocciolina', '', (c) => c.follow('controllo Nocciolina tra 1 settimana', 1, 'week')),
  } },
  /**
   * Two dogs, written up hours later with clock times. Each dog has its own temperature. The shared line is
   * the write-up note itself; the owner's call after discharge names Max mid-sentence (assigned by hand).
   */
  { slug: 'two-dogs-written-later', headers: {
    en: { max: dog('Max', 'Labrador', 6), ruby: dog('Ruby', 'Labrador', 2, 'female') },
    de: { benno: dog('Benno', 'Labrador', 6), frieda: dog('Frieda', 'Labrador', 2, 'female') },
    it: { bobo: dog('Bobo', 'Labrador', 6), gilda: dog('Gilda', 'Labrador', 2, 'female') },
  }, build: {
    en: (m) => m
      .line(SHARED, 'both: ', (c) => c.plain('written up at 19:00, seen together at 14:30'))
      .line('max', 'Max: ', (c) => c.complaint('vomited 3x this morning per owner'))
      .line('max', 'Max: ', (c) => c.vital('temperature', 39.1, 'C', 'T 39.1'))
      .line('max', 'Max: ', (c) => c.finding('abdomen', 'abdomen soft, mild discomfort'))
      .line('max', 'Max: ', (c) => c.med({ drug: 'Cerenia', route: 'SC', status: 'performed' }, 'Cerenia SC given at 14:45'))
      .line('ruby', 'Ruby: ', (c) => c.complaint('booster vaccination, no concerns'))
      .line('ruby', 'Ruby: ', (c) => c.vital('temperature', 38.5, 'C', 'T 38.5'))
      .line('ruby', 'Ruby: ', (c) => c.med({ drug: 'DHPPi vaccine', route: 's.c.', status: 'performed' }, 'DHPPi vaccine s.c., batch QZ5120'))
      .line('max', '', (c) => c.history('update', 'owner called at 18:00: Max has not vomited since', 'owner_reported'))
      .line('max', '', (c) => c.follow('recheck Max tomorrow if vomiting again', null, null)),
    de: (m) => m
      .line(SHARED, 'beide: ', (c) => c.plain('geschrieben um 19:00, zusammen gesehen um 14:30'))
      .line('benno', 'Benno: ', (c) => c.complaint('laut Besitzer heute Morgen 3x erbrochen'))
      .line('benno', 'Benno: ', (c) => c.vital('temperature', 39.1, 'C', 'T 39,1'))
      .line('benno', 'Benno: ', (c) => c.finding('Abdomen', 'Abdomen weich, ggr. Schmerz'))
      .line('benno', 'Benno: ', (c) => c.med({ drug: 'Cerenia', route: 's.c.', status: 'performed' }, 'Cerenia s.c. um 14:45 verabreicht'))
      .line('frieda', 'Frieda: ', (c) => c.complaint('Auffrischungsimpfung, keine Beschwerden'))
      .line('frieda', 'Frieda: ', (c) => c.vital('temperature', 38.5, 'C', 'T 38,5'))
      .line('frieda', 'Frieda: ', (c) => c.med({ drug: 'DHPPi-Impfstoff', route: 's.c.', status: 'performed' }, 'DHPPi-Impfstoff s.c., Ch.-B. QZ5120'))
      .line('benno', '', (c) => c.history('Verlauf', 'Besitzer ruft um 18:00 an: Benno hat seitdem nicht mehr erbrochen', 'owner_reported'))
      .line('benno', '', (c) => c.follow('WV Benno morgen, falls er wieder erbricht', null, null)),
    it: (m) => m
      .line(SHARED, 'entrambi: ', (c) => c.plain('scritto alle 19:00, visti insieme alle 14:30'))
      .line('bobo', 'Bobo: ', (c) => c.complaint('ha vomitato 3 volte stamattina secondo il proprietario'))
      .line('bobo', 'Bobo: ', (c) => c.vital('temperature', 39.1, 'C', 'T 39,1'))
      .line('bobo', 'Bobo: ', (c) => c.finding('addome', 'addome morbido, lieve fastidio'))
      .line('bobo', 'Bobo: ', (c) => c.med({ drug: 'Cerenia', route: 'sc', status: 'performed' }, 'Cerenia sc somministrato alle 14:45'))
      .line('gilda', 'Gilda: ', (c) => c.complaint('richiamo vaccinale, nessun problema'))
      .line('gilda', 'Gilda: ', (c) => c.vital('temperature', 38.5, 'C', 'T 38,5'))
      .line('gilda', 'Gilda: ', (c) => c.med({ drug: 'vaccino DHPPi', route: 's.c.', status: 'performed' }, 'vaccino DHPPi s.c., lotto QZ5120'))
      .line('bobo', '', (c) => c.history('aggiornamento', 'il proprietario chiama alle 18:00: Bobo non ha più vomitato', 'owner_reported'))
      .line('bobo', '', (c) => c.follow('controllo Bobo domani se vomita di nuovo', null, null)),
  } },
];

const here = dirname(fileURLToPath(import.meta.url));
const dir = join(here, '..', '..', 'eval', 'cases');
for (const f of readdirSync(dir)) if (/^([14]\d\d-gen|2\d\d-seeded)-/.test(f)) unlinkSync(join(dir, f));
const write = (list: Scenario[], start: number, kind: string) => {
  let n = start;
  for (const sc of list) for (const lang of ['en', 'de', 'it'] as Lang[]) {
    const id = `${n}-${kind}-${sc.slug}-${lang}`;
    const c = sc.build[lang](new Case(id, lang, sc.header[lang]));
    writeFileSync(join(dir, `${id}.json`), JSON.stringify(c.build(), null, 2) + '\n');
    n++;
  }
  return n - start;
};
const gen = write(S, 100, 'gen') + write(S2, 400, 'gen');
const seeded = write(SEEDED, 200, 'seeded');
// Multi-pet consultations live in their own folder: their shape (shared notes, several patients) is not a
// single-patient case, and the harness scores them apart (see eval.ts), outside every published rate.
const multiDir = join(here, '..', '..', 'eval', 'cases-multi');
mkdirSync(multiDir, { recursive: true });
for (const f of readdirSync(multiDir)) if (/^3\d\d-multi-/.test(f)) unlinkSync(join(multiDir, f));
let multi = 0;
for (const sc of MULTI) for (const lang of ['en', 'de', 'it'] as Lang[]) {
  const id = `${300 + multi}-multi-${sc.slug}-${lang}`;
  writeFileSync(join(multiDir, `${id}.json`), JSON.stringify(sc.build[lang](new MultiCase(id, lang, sc.headers[lang])).build(), null, 2) + '\n');
  multi++;
}
console.log(`wrote ${gen} cases, ${seeded} seeded-error cases and ${multi} multi-pet consultations`);
