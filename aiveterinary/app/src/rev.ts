import type { ClinicalRecord, PatientHeader } from './schema.js';
import type { Dispensing, VisitContext } from './country.js';

/**
 * Italian REV (Ricetta Veterinaria Elettronica) draft.
 *
 * A checklist the vet transcribes into the official system (vetinfo.it / the REV
 * app or their PIMS's accredited integration). It is never submitted by us and
 * it is not a prescription. Every value comes from the approved record, the
 * patient header or the VisitContext the vet entered; anything else is `null`
 * and listed in `missing`. No AIC lookup, no inferred prescription type,
 * repeatability, deroga or diagnosis code: those are chosen in the official
 * system. Field names follow the REV PET web-service spec (see docs/17-rev-payload.md).
 *
 * The REV number and PIN exist only after the vet issues the prescription in
 * the official system. They can be passed in `issued` to print them on the
 * owner's reminder; this module stores nothing.
 */

/** Official sources the field rules come from. Accessed 2026-10-23. */
export const REV_SOURCES = {
  dm_2019: { title: 'D.M. 8 febbraio 2019, Disciplinare tecnico §4.4.1 (GU SG n. 89 del 15-4-2019)', url: 'https://www.gazzettaufficiale.it/eli/id/2019/04/15/19A02527/sg' },
  ws_pet: { title: 'Specifiche tecniche Web Services REV – Emissione Ricetta PET, v1.1.1 r1.7 (28/08/2025) e v1.1 r1.6', url: 'https://www.ricettaveterinariaelettronica.it/softwarehouse.html' },
  manuale: { title: 'Manuale operativo – La prescrizione medico-veterinaria elettronica, v2.0 (aprile 2019), §6.3', url: 'https://www.ricettaveterinariaelettronica.it/documenti/manuale%20operativo/Manuale%20Operativo.pdf' },
  help_emissione: { title: 'vetinfo.it Help – Emissione ricetta (PET ed equidi NDPA)', url: 'https://www.vetinfo.it/help/farmaco/help/emissionericetta' },
  home: { title: 'ricettaveterinariaelettronica.it – Inizia da qui', url: 'https://www.ricettaveterinariaelettronica.it/' },
  dlgs_218_28: { title: 'D.Lgs. 7 dicembre 2023, n. 218, art. 28 (Prescrizione veterinaria)', url: 'https://www.gazzettaufficiale.it/eli/id/2024/01/03/23G00225/sg' },
  dlgs_218_37: { title: 'D.Lgs. 7 dicembre 2023, n. 218, art. 37 (Cessione dei medicinali veterinari)', url: 'https://www.gazzettaufficiale.it/eli/id/2024/01/03/23G00225/sg' },
  guida_ndpa: { title: 'Guida allo scarico dalle giacenze per animali NDPA', url: 'https://www.ricettaveterinariaelettronica.it/documenti/manuale%20operativo/guida_scarico_giacenze_ndpa.pdf' },
} as const;
export type RevSource = keyof typeof REV_SOURCES;
export const REV_SOURCES_ACCESSED = '2026-10-23';

/** Typed slot for what the official system returns after issuing. Not persisted by this module. */
export type RevIssued = { numero?: string | null; pin?: string | null };

export type RevRequirement = 'obbligatorio' | 'condizionale' | 'facoltativo';
export type RevMissing = { field: string; reason: string; requirement: RevRequirement; source: RevSource };
/** Where a value came from: a path into `{ record, header, ctx, issued }`. */
export type RevProvenance = { field: string; path: string; value: string | number | boolean };

export type RevLine = {
  medication_index: number;
  /** presrigaFlTipoMedicinale (N con AIC, S galenico, O omeopatico, E estero…): selected in the system. */
  tipo_medicinale: null;
  farmaco_come_scritto: string | null;   // the record's drug, as the vet wrote it
  denominazione: string | null;          // presrigaProdDenominazione: product as on the pack (dispensing record)
  aic: string | null;                    // presrigaProdAic
  confezione: string | null;             // presrigaProdConfezione
  quantita_come_scritta: string | null;  // dispensing quantity as entered
  numero_confezioni: number | null;      // presrigaQuantitativo: only when the vet entered the quantity in packs
  posologia: string | null;              // presrigaPosologia: dose, route, frequency joined from the record
  durata_come_scritta: string | null;    // presrigaDurataTrattamento (the WS wants a number; transcribe from this)
  ripetibile: null;                      // presrigaFlRipetibile: the system decides from the AIC; never inferred
  malattia_cronica: null;                // presrigaFlMalattiaCronica
  antimicrobico: true | null;            // from the vet's dispensing flag; the system also derives it from the AIC
  profilassi_metafilassi: null;          // presrigaProfilassiMetafilassiCodice: chosen in the system
  giustificazione_note: string | null;   // presrigaGiustificazioneNote: the vet's antibiotic justification
  deroga: null;                          // prescapoDerogaCodice: never inferred
  note: null;                            // presrigaNote
};

export type RevStockDischarge = {
  medication_index: number;
  farmaco_come_scritto: string | null;
  denominazione: string | null;
  aic: string | null;
  confezione: string | null;
  quantita_come_scritta: string | null;
  motivo_scarico: null; // selected in the Registro di carico/scarico
};

export type RevExcluded = { medication_index: number; drug: string | null; status: string; reason: string; source: RevSource | null };

export type RevDraft = {
  format: 'aiveterinary.rev-draft/1';
  is_prescription: false;
  tipo_ricetta: null; // e.g. "Prescrizione Veterinaria PET ed equidi NDPA": chosen in the system
  veterinario: { nome: string | null; iscrizione_albo: string | null; codice_fiscale: null };
  struttura: null;
  proprietario: { codice_fiscale: string | null; nome_completo: string | null };
  animale: { nome: string | null; specie: string | null; identificativo: string | null; codice_azienda: null };
  diagnosi: string | null;
  righe: RevLine[];
  cessioni_da_scorta: RevStockDischarge[];
  escluse: RevExcluded[];
  emessa: { numero: string | null; pin: string | null };
  missing: RevMissing[];
  warnings: { text: string; source: RevSource }[];
  provenance: RevProvenance[];
};

const PACK_UNIT = /^(packs?|packages?|confezion[ei]|conf\.?|scatol[ae]|packung(en)?|pckg?\.?)$/i;

const text = (v: string | null | undefined) => (v == null || v.trim() === '' ? null : v);

export function buildRevDraft(record: ClinicalRecord, header: PatientHeader, ctx: VisitContext, issued: RevIssued = {}): RevDraft {
  if (ctx.country !== 'IT') throw new Error('The REV draft applies to Italy only (ctx.country must be IT).');
  const missing: RevMissing[] = [];
  const provenance: RevProvenance[] = [];
  const warnings: RevDraft['warnings'] = [];
  const miss = (field: string, reason: string, requirement: RevRequirement, source: RevSource) => missing.push({ field, reason, requirement, source });
  /** Take a value, recording its path, or record it as missing. */
  const take = <T extends string | number | boolean>(field: string, path: string, value: T | null | undefined): T | null => {
    if (value == null || (typeof value === 'string' && value.trim() === '')) return null;
    provenance.push({ field, path, value });
    return value;
  };

  /* --- Ricetta: general data ---------------------------------------- */
  miss('tipo_ricetta', 'Tipo di ricetta da scegliere nel sistema (es. Prescrizione Veterinaria PET ed equidi NDPA)', 'obbligatorio', 'help_emissione');

  const veterinario = {
    nome: take('veterinario.nome', 'ctx.author.name', ctx.author.name),
    iscrizione_albo: take('veterinario.iscrizione_albo', 'ctx.author.registration', ctx.author.registration),
    codice_fiscale: null,
  } as const;
  if (!veterinario.nome) miss('veterinario.nome', 'Veterinario prescrittore', 'obbligatorio', 'dm_2019');
  if (!veterinario.iscrizione_albo) miss('veterinario.iscrizione_albo', 'Numero di iscrizione all\'albo (identifica il veterinario nel sistema)', 'obbligatorio', 'dm_2019');
  miss('veterinario.codice_fiscale', 'Codice fiscale del veterinario: coincide con l\'utente autenticato nel sistema', 'obbligatorio', 'ws_pet');
  miss('struttura', 'Struttura veterinaria presso cui si emette la ricetta', 'facoltativo', 'help_emissione');

  const proprietario = {
    codice_fiscale: take('proprietario.codice_fiscale', 'ctx.owner.tax_id', ctx.owner.tax_id),
    nome_completo: take('proprietario.nome_completo', 'ctx.owner.name', ctx.owner.name),
  };
  if (!proprietario.codice_fiscale) miss('proprietario.codice_fiscale', 'Identificativo fiscale (codice fiscale o partita IVA) del proprietario o detentore', 'obbligatorio', 'dm_2019');
  if (!proprietario.nome_completo) miss('proprietario.nome_completo', 'Nome e cognome del proprietario o detentore (richiesti se non già registrato nel sistema)', 'obbligatorio', 'dm_2019');
  else miss('proprietario.nome_cognome', 'Il sistema chiede nome e cognome in campi separati: trascriverli dal nome completo', 'condizionale', 'ws_pet');

  const animale = {
    nome: take('animale.nome', 'header.name', header.name),
    specie: take('animale.specie', 'header.species', header.species),
    identificativo: take('animale.identificativo', 'ctx.microchip', ctx.microchip),
    codice_azienda: null,
  } as const;
  if (!animale.identificativo) miss('animale.identificativo', 'Identificativo dell\'animale (microchip) ove previsto dall\'anagrafe; per il cane il sistema segnala l\'assenza', 'condizionale', 'ws_pet');
  if (header.species === 'horse') {
    miss('animale.codice_azienda', 'Equidi NDPA: codice aziendale del luogo di detenzione obbligatorio', 'obbligatorio', 'manuale');
    warnings.push({ text: 'Equide: verificare se DPA o NDPA; per gli equidi DPA si usa un altro tipo di ricetta', source: 'manuale' });
  }

  const diagnosi = take('diagnosi', 'record.assessment.text', record.assessment.text);
  if (!diagnosi) miss('diagnosi', 'Diagnosi (il sistema la chiede come codice dall\'elenco delle diagnosi)', 'condizionale', 'dm_2019');
  else miss('diagnosi.codice', 'Codice diagnosi da scegliere nell\'elenco del sistema (testo del veterinario riportato sopra)', 'facoltativo', 'ws_pet');

  /* --- Medicinali ---------------------------------------------------- */
  const righe: RevLine[] = [];
  const cessioni: RevStockDischarge[] = [];
  const escluse: RevExcluded[] = [];
  const dispensingFor = (i: number) => {
    const k = ctx.dispensings.findIndex((d) => d.medication_index === i);
    return k < 0 ? null : { d: ctx.dispensings[k] as Dispensing, k };
  };

  record.medications.forEach((m, i) => {
    const mp = `record.medications[${i}]`;
    if (m.status === 'performed') {
      escluse.push({ medication_index: i, drug: m.drug, status: m.status, reason: 'Somministrato in struttura: non va su una ricetta per il proprietario. Se il prodotto proviene da una scorta registrata, registrare lo scarico nel Registro di carico/scarico.', source: 'guida_ndpa' });
      return;
    }
    if (m.status !== 'prescribed' && m.status !== 'dispensed') {
      escluse.push({ medication_index: i, drug: m.drug, status: m.status, reason: m.status === 'declined' ? 'Rifiutato dal proprietario' : 'Non prescritto né consegnato', source: null });
      return;
    }
    const found = dispensingFor(i);
    const dp = found ? `ctx.dispensings[${found.k}]` : null;
    const d = found?.d ?? null;
    const qtyText = d?.quantity ? `${d.quantity.value} ${d.quantity.unit}` : null;

    if (m.status === 'dispensed') {
      const f = `cessioni_da_scorta[${cessioni.length}]`;
      const c: RevStockDischarge = {
        medication_index: i,
        farmaco_come_scritto: take(`${f}.farmaco_come_scritto`, `${mp}.drug`, m.drug),
        denominazione: dp ? take(`${f}.denominazione`, `${dp}.product`, d?.product) : null,
        aic: dp ? take(`${f}.aic`, `${dp}.authorisation_number`, d?.authorisation_number) : null,
        confezione: dp ? take(`${f}.confezione`, `${dp}.pack`, d?.pack) : null,
        quantita_come_scritta: null,
        motivo_scarico: null,
      };
      if (qtyText && dp) { c.quantita_come_scritta = qtyText; provenance.push({ field: `${f}.quantita_come_scritta`, path: `${dp}.quantity`, value: qtyText }); }
      if (!c.denominazione) miss(`${f}.denominazione`, 'Medicinale consegnato come sulla confezione', 'obbligatorio', 'dlgs_218_37');
      if (!c.quantita_come_scritta) miss(`${f}.quantita`, 'Quantitativo da scaricare (confezioni o unità)', 'obbligatorio', 'guida_ndpa');
      miss(`${f}.motivo_scarico`, 'Motivo di scarico da scegliere nel registro', 'obbligatorio', 'guida_ndpa');
      cessioni.push(c);
      return;
    }

    const f = `righe[${righe.length}]`;
    const line: RevLine = {
      medication_index: i,
      tipo_medicinale: null,
      farmaco_come_scritto: take(`${f}.farmaco_come_scritto`, `${mp}.drug`, m.drug),
      denominazione: dp ? take(`${f}.denominazione`, `${dp}.product`, d?.product) : null,
      aic: dp ? take(`${f}.aic`, `${dp}.authorisation_number`, d?.authorisation_number) : null,
      confezione: dp ? take(`${f}.confezione`, `${dp}.pack`, d?.pack) : null,
      quantita_come_scritta: null,
      numero_confezioni: null,
      posologia: null,
      durata_come_scritta: take(`${f}.durata_come_scritta`, `${mp}.duration`, m.duration),
      ripetibile: null,
      malattia_cronica: null,
      antimicrobico: null,
      profilassi_metafilassi: null,
      giustificazione_note: null,
      deroga: null,
      note: null,
    };
    if (qtyText && dp && d?.quantity) {
      line.quantita_come_scritta = qtyText;
      provenance.push({ field: `${f}.quantita_come_scritta`, path: `${dp}.quantity`, value: qtyText });
      if (PACK_UNIT.test(d.quantity.unit.trim())) line.numero_confezioni = take(`${f}.numero_confezioni`, `${dp}.quantity.value`, d.quantity.value);
    }
    // Posologia: the vet's own dose, route and frequency, joined; each part keeps its path.
    const parts: string[] = [];
    if (m.dose != null) {
      const dose = `${m.dose}${m.dose_unit ? ` ${m.dose_unit}` : ''}`;
      provenance.push({ field: `${f}.posologia`, path: `${mp}.dose`, value: m.dose });
      if (m.dose_unit) provenance.push({ field: `${f}.posologia`, path: `${mp}.dose_unit`, value: m.dose_unit });
      parts.push(dose);
    }
    for (const k of ['route', 'frequency'] as const) {
      const v = text(m[k]);
      if (v) { parts.push(v); provenance.push({ field: `${f}.posologia`, path: `${mp}.${k}`, value: v }); }
    }
    line.posologia = parts.length ? parts.join(', ') : null;

    if (d?.is_antibiotic === true) {
      line.antimicrobico = take(`${f}.antimicrobico`, `${dp}.is_antibiotic`, true);
      line.giustificazione_note = take(`${f}.giustificazione_note`, `${dp}.antibiotic_justification`, d.antibiotic_justification);
      miss(`${f}.profilassi_metafilassi`, 'Antimicrobico: indicare terapia, profilassi o metafilassi (codice del sistema)', 'obbligatorio', 'ws_pet');
      miss(`${f}.giustificazione`, 'Antimicrobico non in terapia: giustificazione (codice; note obbligatorie se ALTRO)', 'condizionale', 'ws_pet');
    }
    if (d?.is_controlled) warnings.push({ text: `Riga ${righe.length + 1}: segnato come stupefacente. La REV non si applica ai medicinali con AIC contenenti stupefacenti e psicotropi (DPR 309/1990): verificare la ricetta cartacea`, source: 'home' });
    if (line.aic && !/^\d{9}$/.test(line.aic)) warnings.push({ text: `Riga ${righe.length + 1}: l'AIC inserito non ha 9 cifre come richiesto dal sistema; ricontrollare sulla confezione`, source: 'ws_pet' });

    if (!line.farmaco_come_scritto && !line.denominazione) miss(`${f}.denominazione`, 'Medicinale da prescrivere', 'obbligatorio', 'dm_2019');
    else if (!line.denominazione) miss(`${f}.denominazione`, 'Denominazione del medicinale come nel prontuario del sistema', 'obbligatorio', 'ws_pet');
    if (!line.aic) miss(`${f}.aic`, 'Codice AIC (per medicinali con AIC; galenici, omeopatici ed esteri si descrivono)', 'condizionale', 'ws_pet');
    if (line.numero_confezioni == null) miss(`${f}.numero_confezioni`, 'Quantitativo prescritto in numero di confezioni', 'obbligatorio', 'ws_pet');
    if (!line.posologia) miss(`${f}.posologia`, 'Posologia', 'obbligatorio', 'ws_pet');
    else if (m.dose == null || !text(m.frequency)) miss(`${f}.posologia`, 'Posologia incompleta: manca dose o frequenza nella cartella', 'obbligatorio', 'dm_2019');
    if (!line.durata_come_scritta) miss(`${f}.durata`, 'Durata del trattamento (obbligatoria salvo malattia cronica)', 'condizionale', 'ws_pet');
    miss(`${f}.tipo_medicinale`, 'Tipo di medicinale (con AIC, galenico, omeopatico, estero…) da scegliere nel sistema', 'obbligatorio', 'ws_pet');
    miss(`${f}.deroga`, 'Uso in deroga sì/no (codice deroga; note obbligatorie per deroga "altro motivo")', 'obbligatorio', 'ws_pet');
    righe.push(line);
  });

  /* --- After issuing ------------------------------------------------- */
  const numero = take('emessa.numero', 'issued.numero', issued.numero) ?? take('emessa.numero', 'ctx.prescription_number', ctx.prescription_number);
  const pin = take('emessa.pin', 'issued.pin', issued.pin);

  return {
    format: 'aiveterinary.rev-draft/1',
    is_prescription: false,
    tipo_ricetta: null,
    veterinario,
    struttura: null,
    proprietario,
    animale,
    diagnosi,
    righe,
    cessioni_da_scorta: cessioni,
    escluse,
    emessa: { numero, pin },
    missing,
    warnings,
    provenance,
  };
}

/* ------------------------------------------------------------------ */
/* Plain-text checklist for transcription into the REV system.        */

const SPECIE_IT: Record<string, string> = { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', ferret: 'furetto', horse: 'cavallo', bird: 'uccello', reptile: 'rettile', other: 'altro' };
const REQ_MARK: Record<RevRequirement, string> = { obbligatorio: '▲', condizionale: '△', facoltativo: '·' };

export function renderRevDraftText(draft: RevDraft, _lang: 'it' = 'it'): string {
  const v = (x: string | number | null | undefined) => (x == null || x === '' ? '▲ da inserire' : String(x));
  const out: string[] = [];
  out.push('BOZZA DA TRASCRIVERE — NON È UNA RICETTA');
  out.push('Promemoria per la Ricetta Veterinaria Elettronica. Nulla è stato inviato al sistema: la ricetta si emette solo nel sistema ufficiale.');
  out.push('Tipo di ricetta, tipo di medicinale, ripetibilità, deroga e codice diagnosi si scelgono nel sistema.');
  out.push('');
  out.push('[ ] Veterinario');
  out.push(`    Nome: ${v(draft.veterinario.nome)}`);
  out.push(`    Iscrizione all'albo: ${v(draft.veterinario.iscrizione_albo)}`);
  out.push('[ ] Proprietario / detentore');
  out.push(`    Codice fiscale: ${v(draft.proprietario.codice_fiscale)}`);
  out.push(`    Nome e cognome: ${v(draft.proprietario.nome_completo)}`);
  out.push('[ ] Animale');
  out.push(`    Nome: ${v(draft.animale.nome)}`);
  out.push(`    Specie: ${draft.animale.specie ? SPECIE_IT[draft.animale.specie] ?? draft.animale.specie : v(null)}`);
  out.push(`    Microchip / identificativo: ${v(draft.animale.identificativo)}`);
  out.push(`[ ] Diagnosi (testo del veterinario): ${v(draft.diagnosi)}`);
  out.push('');
  if (!draft.righe.length) out.push('Nessun medicinale prescritto in questa cartella.');
  draft.righe.forEach((r, n) => {
    out.push(`[ ] Medicinale ${n + 1}: ${r.denominazione ?? r.farmaco_come_scritto ?? v(null)}`);
    if (r.denominazione && r.farmaco_come_scritto && r.denominazione !== r.farmaco_come_scritto) out.push(`    Come scritto in cartella: ${r.farmaco_come_scritto}`);
    out.push(`    AIC: ${v(r.aic)}`);
    if (r.confezione) out.push(`    Confezione: ${r.confezione}`);
    out.push(`    Numero confezioni: ${r.numero_confezioni ?? (r.quantita_come_scritta ? `▲ da inserire (quantità inserita: ${r.quantita_come_scritta})` : v(null))}`);
    out.push(`    Posologia: ${v(r.posologia)}`);
    out.push(`    Durata del trattamento: ${v(r.durata_come_scritta)}`);
    if (r.antimicrobico) {
      out.push('    Antimicrobico: sì — indicare terapia, profilassi o metafilassi nel sistema');
      out.push(`    Giustificazione: ${v(r.giustificazione_note)}`);
    }
  });
  if (draft.cessioni_da_scorta.length) {
    out.push('');
    out.push('Consegnati dalla scorta (non vanno sulla ricetta): registrare lo scarico entro 7 giorni (art. 37 D.Lgs. 218/2023)');
    for (const c of draft.cessioni_da_scorta) {
      out.push(`[ ] ${c.denominazione ?? c.farmaco_come_scritto ?? v(null)} — AIC: ${v(c.aic)} — quantità: ${v(c.quantita_come_scritta)} — motivo di scarico: da scegliere nel registro`);
    }
  }
  if (draft.escluse.length) {
    out.push('');
    out.push('Non riportati nella bozza:');
    for (const e of draft.escluse) out.push(`- ${e.drug ?? 'medicinale senza nome'}: ${e.reason}`);
  }
  if (draft.warnings.length) {
    out.push('');
    out.push('Attenzione:');
    for (const w of draft.warnings) out.push(`- ${w.text}`);
  }
  const todo = draft.missing.filter((m) => m.requirement !== 'facoltativo');
  if (todo.length) {
    out.push('');
    out.push('Da completare (▲ obbligatorio, △ se applicabile):');
    for (const m of todo) out.push(`${REQ_MARK[m.requirement]} ${m.field}: ${m.reason}`);
  }
  out.push('');
  out.push('Dopo l\'emissione nel sistema (da consegnare al proprietario per la farmacia):');
  out.push(`    Numero ricetta: ${draft.emessa.numero ?? '________________'}`);
  out.push(`    PIN: ${draft.emessa.pin ?? '____'}`);
  return out.join('\n');
}
