import type { ApprovedVersion } from './versions.js';
import type { ClinicalRecord, Medication } from './schema.js';
import type { Lang } from './render.js';

/**
 * History recap: a short overview of a patient's own approved records.
 *
 * Nothing is summarised by a model and nothing is inferred. Every line is
 * copied from one approved version and ends with a reference to that visit and
 * version, so the vet can open the source. Only the latest approved version of
 * each visit is used; superseded versions are left out.
 */

export type Visit = Readonly<{ visit_id: string; date: string; versions: readonly ApprovedVersion[] }>;

const R = {
  en: { title: 'History recap', none: 'No approved records for this patient.', visits: 'Visits', weight: 'Weight over time', meds: 'Medication on record', declined: 'Declined by owner', open: 'Planned, not yet recorded as done', reason: 'Reason', assessment: 'Assessment', follow: 'Follow-up', note: 'Copied from approved records only. Each line links to its visit and version.' },
  de: { title: 'Verlaufsübersicht', none: 'Keine freigegebenen Einträge für diesen Patienten.', visits: 'Besuche', weight: 'Gewichtsverlauf', meds: 'Dokumentierte Medikation', declined: 'Vom Besitzer abgelehnt', open: 'Geplant, noch nicht als erledigt dokumentiert', reason: 'Grund', assessment: 'Beurteilung', follow: 'Kontrolle', note: 'Nur aus freigegebenen Einträgen übernommen. Jede Zeile verweist auf Besuch und Version.' },
  it: { title: 'Riepilogo della storia clinica', none: 'Nessuna cartella approvata per questo paziente.', visits: 'Visite', weight: 'Andamento del peso', meds: 'Terapie registrate', declined: 'Rifiutato dal proprietario', open: 'Pianificato, non ancora registrato come eseguito', reason: 'Motivo', assessment: 'Valutazione', follow: 'Controllo', note: 'Copiato solo da cartelle approvate. Ogni riga rimanda a visita e versione.' },
} satisfies Record<Lang, Record<string, string>>;

const S: Record<Lang, Record<Medication['status'], string>> = {
  en: { planned: 'planned', performed: 'given', declined: 'declined', recommended: 'recommended', dispensed: 'dispensed', prescribed: 'prescribed' },
  de: { planned: 'geplant', performed: 'verabreicht', declined: 'abgelehnt', recommended: 'empfohlen', dispensed: 'abgegeben', prescribed: 'verschrieben' },
  it: { planned: 'pianificato', performed: 'somministrato', declined: 'rifiutato', recommended: 'consigliato', dispensed: 'consegnato', prescribed: 'prescritto' },
};

const ref = (v: Visit, a: ApprovedVersion) => `[${v.date} · ${v.visit_id} v${a.version}]`;
const medText = (m: Medication) => [m.drug ?? m.class_as_written, m.dose !== null ? `${m.dose}${m.dose_unit ? ' ' + m.dose_unit : ''}` : null, m.route, m.frequency, m.duration].filter(Boolean).join(' · ');

/** The latest approved version of each visit, oldest visit first. */
export function latestPerVisit(visits: readonly Visit[]): { visit: Visit; v: ApprovedVersion }[] {
  return visits
    .filter((x) => x.versions.length)
    .map((visit) => ({ visit, v: [...visit.versions].sort((a, b) => b.version - a.version)[0] }))
    .sort((a, b) => a.visit.date.localeCompare(b.visit.date) || a.visit.visit_id.localeCompare(b.visit.visit_id));
}

export function renderHistoryRecap(visits: readonly Visit[], lang: Lang = 'en'): string {
  const t = R[lang];
  const rows = latestPerVisit(visits);
  const out: string[] = [`# ${t.title}`, '', `_${t.note}_`, ''];
  if (!rows.length) { out.push(t.none); return out.join('\n'); }

  out.push(`## ${t.visits}`);
  for (const { visit, v } of [...rows].reverse()) {
    const r: ClinicalRecord = v.record;
    const bits = [r.presenting_complaint?.text && `${t.reason}: ${r.presenting_complaint.text}`, r.assessment.text && `${t.assessment}: ${r.assessment.text}`].filter(Boolean);
    out.push(`- ${bits.join(' — ') || '—'} ${ref(visit, v)}`);
  }

  const weights = rows.map(({ visit, v }) => ({ visit, v, w: v.record.examination.vitals.weight })).filter((x) => x.w);
  if (weights.length) {
    out.push('', `## ${t.weight}`);
    for (const { visit, v, w } of weights) out.push(`- ${visit.date}: ${w!.value} ${w!.unit} ${ref(visit, v)}`);
  }

  const meds = rows.flatMap(({ visit, v }) => v.record.medications.filter((m) => m.status !== 'declined').map((m) => ({ visit, v, m })));
  if (meds.length) {
    out.push('', `## ${t.meds}`);
    for (const { visit, v, m } of meds.reverse()) out.push(`- ${medText(m)} (${S[lang][m.status]}) ${ref(visit, v)}`);
  }

  const declined = rows.flatMap(({ visit, v }) => [
    ...v.record.diagnostics.filter((d) => d.status === 'declined').map((d) => d.test),
    ...v.record.medications.filter((m) => m.status === 'declined').map((m) => m.drug ?? m.class_as_written ?? '—'),
  ].map((text) => ({ visit, v, text })));
  if (declined.length) {
    out.push('', `## ${t.declined}`);
    for (const { visit, v, text } of declined) out.push(`- ${text} ${ref(visit, v)}`);
  }

  // Planned in an earlier visit and not recorded as performed in any later one (same test name, case-insensitive).
  const open: { visit: Visit; v: ApprovedVersion; text: string }[] = [];
  rows.forEach(({ visit, v }, i) => {
    for (const d of v.record.diagnostics.filter((x) => x.status === 'planned' || x.status === 'recommended')) {
      const done = rows.slice(i + 1).some(({ v: later }) => later.record.diagnostics.some((x) => x.status === 'performed' && x.test.toLowerCase() === d.test.toLowerCase()));
      if (!done) open.push({ visit, v, text: d.test });
    }
  });
  const last = rows[rows.length - 1];
  if (last.v.record.plan.follow_up) open.push({ visit: last.visit, v: last.v, text: `${t.follow}: ${last.v.record.plan.follow_up.text}` });
  if (open.length) {
    out.push('', `## ${t.open}`);
    for (const { visit, v, text } of open) out.push(`- ${text} ${ref(visit, v)}`);
  }
  return out.join('\n');
}
