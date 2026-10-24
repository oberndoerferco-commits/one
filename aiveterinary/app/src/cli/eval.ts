/**
 * Evaluation harness.
 *   npm run eval            → fixture mode: validates the fixture records and checks expectations (offline)
 *   AIVET_EXTRACTOR=claude npm run eval → runs the model on each case, then validates (needs ANTHROPIC_API_KEY)
 *
 * Exit code 1 if any blocking finding appears on a case that is not marked fixture_must_fail, or a
 * seeded-error case (`expect.must_flag`) does not raise the rule(s) it names.
 */
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing, type Finding } from '../validators.js';
import { ClaudeExtractor, FixtureExtractor, type Extractor, PROMPT_VERSION } from '../extract.js';
import { renderConsultReport } from '../render.js';
import { makeConsultation, validateConsultation, suggestAssignments, setLine, SHARED } from '../multi-pet.js';
import { wilson, scoreFacts, scoreMissingFlags, scoreSeeded, pct } from '../metrics.js';

const here = dirname(fileURLToPath(import.meta.url));
const defaultCasesDir = join(here, '..', '..', 'eval', 'cases');
const defaultMultiDir = join(here, '..', '..', 'eval', 'cases-multi');
const defaultOutDir = join(here, '..', '..', 'eval', 'results');

type Case = { id: string; language: string; header: unknown; notes: string; expect: any; fixture_record?: unknown };

export async function runEval(extractorName = process.env.AIVET_EXTRACTOR ?? 'fixture', verbose = process.argv.includes('--verbose'), { casesDir = defaultCasesDir, outDir = defaultOutDir, quiet = false, multiDir = undefined as string | null | undefined }: { casesDir?: string; outDir?: string; quiet?: boolean; multiDir?: string | null } = {}) {
  // Multi-pet consultations are read from their own folder, by default only alongside the default cases.
  if (multiDir === undefined) multiDir = casesDir === defaultCasesDir ? defaultMultiDir : null;
  const log = (...a: unknown[]) => { if (!quiet) console.log(...a); };
  const files = readdirSync(casesDir).filter((f) => f.endsWith('.json')).sort();
  const cases: Case[] = files.map((f) => JSON.parse(readFileSync(join(casesDir, f), 'utf8')));
  const fixtures = Object.fromEntries(cases.filter((c) => c.fixture_record).map((c) => [normalizeNotes(c.notes), c.fixture_record]));
  const extractor: Extractor = extractorName === 'claude' ? new ClaudeExtractor() : new FixtureExtractor(fixtures);

  let failures = 0; const rows: string[] = []; const falseFlags: string[] = [];
  const totals = { facts: 0, unsupportedFacts: 0, scored: 0, casesWithBlock: 0, cases: 0, blocks: 0, warns: 0, unsourced: 0, drugMismatch: 0, missRecall: 0, missTotal: 0, flagsRaised: 0, flagsCorrect: 0, input_tokens: 0, output_tokens: 0 };
  /** Seeded-error cases: scored only as seeded-error detection, their findings counted apart. */
  const seededTotals = { cases: 0, errors: 0, caught: 0, blocks: 0, warns: 0 };
  for (const c of cases) {
    // Seeded-error cases test the checks on a record with a planted error; a model builds its own
    // record, so in a model run they say nothing and are skipped.
    if (extractorName !== 'fixture' && Array.isArray(c.expect?.must_flag) && c.expect.must_flag.length) continue;
    const notes = normalizeNotes(c.notes);
    const header = PatientHeader.parse(c.header);
    let findings: Finding[] = []; let note = '';
    try {
      const res = await extractor.extract({ notes, header, language: c.language });
      const record = ClinicalRecord.parse(res.record);
      findings = validateAll(record, notes, header);
      if (res.usage) { totals.input_tokens += res.usage.input_tokens; totals.output_tokens += res.usage.output_tokens; }
      const blocks = findings.filter((f) => f.severity === 'block');
      const mustFail = !!c.expect?.fixture_must_fail;
      const mustFlag: string[] | undefined = c.expect?.must_flag;
      const seeded = Array.isArray(mustFlag) && mustFlag.length > 0;
      // expectations
      const problems: string[] = [];
      if (seeded) {
        const s = scoreSeeded(mustFlag, findings);
        seededTotals.cases++; seededTotals.errors += s.seeded; seededTotals.caught += s.caught;
        for (const r of s.missed) problems.push(`seeded error not caught: rule ${r} not raised`);
        if (s.stray_blocks.length) problems.push(`blocking finding(s) besides the seeded error: ${s.stray_blocks.join(', ')}`);
      } else if (mustFail) {
        for (const r of c.expect.expected_rules ?? []) if (!findings.some((f) => f.rule === r)) problems.push(`expected rule ${r} not raised`);
      } else {
        if (blocks.length) problems.push(`${blocks.length} blocking finding(s): ${blocks.map((b) => b.rule + '@' + b.field).join(', ')}`);
        const miss = new Set([...record.missing.map((m) => m.field), ...requiredMissing(record, 'consult_report', header)]);
        for (const m of c.expect?.missing_includes ?? []) { totals.missTotal++; if (miss.has(m)) totals.missRecall++; else problems.push(`missing flag not raised: ${m}`); }
        const mf = scoreMissingFlags(miss, c.expect?.missing_includes ?? []);
        totals.flagsRaised += mf.raised; totals.flagsCorrect += mf.correct;
        if (mf.false_flags.length) falseFlags.push(`${c.id}: ${mf.false_flags.join(', ')}`);
        const drugs = record.medications.map((m) => m.drug).filter(Boolean);
        for (const d of drugs) if (!(c.expect?.drugs ?? []).some((x: string) => x.toLowerCase() === String(d).toLowerCase())) { totals.drugMismatch++; problems.push(`unexpected drug ${d}`); }
        if (c.expect?.assessment_text !== undefined && (record.assessment.text ?? null) !== c.expect.assessment_text) problems.push(`assessment "${record.assessment.text}" ≠ expected "${c.expect.assessment_text}"`);
        if (c.expect?.temperature !== undefined && record.examination.vitals.temperature?.value !== c.expect.temperature) problems.push(`temperature ${record.examination.vitals.temperature?.value} ≠ ${c.expect.temperature}`);
        const json = JSON.stringify({ ...record, uncertain: [] }).toLowerCase();
        for (const [path, st] of Object.entries(c.expect?.statuses ?? {})) {
          const m = /^(\w+)\[(\d+)\]$/.exec(path); const item = m ? (record as any)[m[1]]?.[Number(m[2])] : undefined;
          if (!item) problems.push(`statuses: ${path} not found`); else if (item.status !== st) problems.push(`statuses: ${path} is ${item.status}, expected ${st}`);
        }
        for (const bad of c.expect?.must_not_contain ?? []) if (json.includes(bad)) problems.push(`record contains forbidden text "${bad}" outside 'uncertain'`);
        if (c.expect?.uncertain_min && record.uncertain.length < c.expect.uncertain_min) problems.push(`expected ≥${c.expect.uncertain_min} uncertain entries`);
      }
      // Must-fail fixtures are deliberately wrong; they test the checks and are kept out of the published rates.
      // Seeded-error cases are deliberately wrong too: their findings are counted apart, so blocking/warnings/
      // unsourced keep meaning "on the answer-key records (plus case 005)".
      totals.cases++;
      if (seeded) { seededTotals.blocks += blocks.length; seededTotals.warns += findings.length - blocks.length; }
      else {
        if (!mustFail) { const sc = scoreFacts(record, findings); totals.facts += sc.facts; totals.unsupportedFacts += sc.unsupported; totals.scored++; if (blocks.length) totals.casesWithBlock++; }
        totals.blocks += blocks.length; totals.warns += findings.length - blocks.length;
        totals.unsourced += findings.filter((f) => f.rule === 'source_required' || f.rule === 'span_invalid').length;
      }
      const ok = problems.length === 0;
      if (!ok) failures++;
      rows.push(`${ok ? 'PASS' : 'FAIL'}  ${c.id}${mustFail ? ' (must-fail fixture)' : seeded ? ' (seeded error)' : ''}${problems.length ? '\n      - ' + problems.join('\n      - ') : ''}`);
      if (verbose) { rows.push(renderConsultReport(record, header, (c.language as any) ?? 'en').split('\n').map((l) => '      ' + l).join('\n')); rows.push('      findings: ' + JSON.stringify(findings)); }
    } catch (e: any) {
      failures++; totals.cases++; note = e?.message ?? String(e);
      rows.push(`FAIL  ${c.id}\n      - error: ${note}`);
    }
  }
  const multi = extractorName === 'fixture' && multiDir ? runMulti(multiDir) : null;
  if (multi) failures += multi.failed;
  log(`AI Veterinary eval — extractor=${extractor.name} prompt=${PROMPT_VERSION}\n`);
  log(rows.join('\n'));
  if (multi?.rows.length) log(multi.rows.join('\n'));
  // machine-readable result for the public quality page (site/src/pages/vets/quality.astro)
  mkdirSync(outDir, { recursive: true });
  const metrics = {
    attribution: wilson(totals.facts - totals.unsupportedFacts, totals.facts),
    unsupported_content: wilson(totals.unsupportedFacts, totals.facts),
    cases_with_blocking_finding: wilson(totals.casesWithBlock, totals.scored),
    missing_field_detection: wilson(totals.missRecall, totals.missTotal),
    missing_flag_precision: wilson(totals.flagsCorrect, totals.flagsRaised),
    seeded_error_detection: wilson(seededTotals.caught, seededTotals.errors),
  };
  const result = { metrics, run_at: new Date().toISOString(), extractor: extractor.name, prompt: PROMPT_VERSION, cases: totals.cases, failed: failures, blocking: totals.blocks, warnings: totals.warns, unsourced: totals.unsourced, drug_mismatch: totals.drugMismatch, missing_recall: totals.missTotal ? totals.missRecall / totals.missTotal : null, false_missing_flags: falseFlags, seeded: { cases: seededTotals.cases, errors: seededTotals.errors, caught: seededTotals.caught, blocking: seededTotals.blocks, warnings: seededTotals.warns }, languages: [...new Set(cases.map((c) => c.language))].sort(), per_case: rows.filter((r) => /^(PASS|FAIL)/.test(r)).map((r) => ({ id: r.slice(6).split('\n')[0].replace(/ \((must-fail fixture|seeded error)\)$/, ''), pass: r.startsWith('PASS') })), ...(multi ? { multi_pet: multi.summary } : {}) };
  writeFileSync(join(outDir, `${extractor.name}.json`), JSON.stringify(result, null, 2) + '\n');
  log(`\nattribution ${pct(metrics.attribution)}\nunsupported content ${pct(metrics.unsupported_content)}\ncases with a blocking finding ${pct(metrics.cases_with_blocking_finding)}\nmissing-field detection ${pct(metrics.missing_field_detection)}\nmissing-flag precision ${pct(metrics.missing_flag_precision)}\nseeded-error detection ${pct(metrics.seeded_error_detection)}`);
  if (falseFlags.length && verbose) log('flags raised but not expected:\n  ' + falseFlags.join('\n  '));
  if (multi) log(`multi-pet consultations (apart, not in the counts or rates above): ${multi.summary.cases} cases, ${multi.summary.failed} failed, ${multi.summary.patients} patients, cross-patient probes caught ${multi.summary.probes_caught}/${multi.summary.probes}`);
  log(`\n${totals.cases} cases, ${failures} failed. blocking=${totals.blocks} warnings=${totals.warns} unsourced=${totals.unsourced} drug-mismatch=${totals.drugMismatch} missing-recall=${totals.missTotal ? Math.round((100 * totals.missRecall) / totals.missTotal) + '%' : 'n/a'}${totals.input_tokens ? ` tokens in/out=${totals.input_tokens}/${totals.output_tokens}` : ''}${seededTotals.cases ? ` (seeded-error cases apart: ${seededTotals.cases} cases, blocking=${seededTotals.blocks} warnings=${seededTotals.warns})` : ''}`);
  return failures;
}

/**
 * Multi-pet consultations (eval/cases-multi): shared notes, several patients, the vet's gold line
 * assignment. Fixture mode only (the extractor structures one patient at a time). Each case passes when
 *  - no patient has a blocking finding and there is no consultation-level finding (validateConsultation);
 *  - each patient's drugs, statuses, assessment and temperature match its own expectations;
 *  - every name-label suggestion agrees with the gold assignment;
 *  - probe: for each patient, moving one of its fact lines to another patient raises wrong_animal_line.
 * Scored apart: not in `cases`, `per_case` or any rate; summarised under `multi_pet`.
 */
function runMulti(dir: string) {
  let files: string[] = [];
  try { files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort(); } catch { return null; }
  const rows: string[] = []; const summary = { cases: 0, failed: 0, patients: 0, blocking: 0, warnings: 0, probes: 0, probes_caught: 0, per_case: [] as { id: string; pass: boolean }[] };
  for (const f of files) {
    const c = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    const problems: string[] = [];
    try {
      const notes = normalizeNotes(c.notes);
      if (notes !== c.notes) problems.push('notes change on normalisation (spans would shift)');
      const patients = c.patients.map((p: any) => ({ id: p.id, header: PatientHeader.parse(p.header), record: ClinicalRecord.parse(p.fixture_record) }));
      const cons = makeConsultation(notes, patients, c.assignment);
      const v = validateConsultation(cons);
      for (const x of v.consultation) problems.push(`consultation: ${x.rule}@${x.field}`);
      for (const p of c.patients) {
        const fs = v.byPatient[p.id]; const rec = patients.find((x: any) => x.id === p.id)!.record;
        summary.blocking += fs.filter((x) => x.severity === 'block').length; summary.warnings += fs.filter((x) => x.severity === 'warn').length;
        for (const x of fs.filter((y) => y.severity === 'block')) problems.push(`${p.id}: blocking ${x.rule}@${x.field}`);
        const drugs = rec.medications.map((m: any) => m.drug).filter(Boolean);
        for (const d of drugs) if (!(p.expect?.drugs ?? []).some((x: string) => x.toLowerCase() === String(d).toLowerCase())) problems.push(`${p.id}: unexpected drug ${d}`);
        if (p.expect?.assessment_text !== undefined && (rec.assessment.text ?? null) !== p.expect.assessment_text) problems.push(`${p.id}: assessment differs`);
        if (p.expect?.temperature !== undefined && rec.examination.vitals.temperature?.value !== p.expect.temperature) problems.push(`${p.id}: temperature differs`);
        for (const [path, st] of Object.entries(p.expect?.statuses ?? {})) {
          const m = /^(\w+)\[(\d+)\]$/.exec(path); const item = m ? (rec as any)[m[1]]?.[Number(m[2])] : undefined;
          if (item?.status !== st) problems.push(`${p.id}: statuses ${path}`);
        }
        // probe: one of this patient's own lines handed to another patient must block this patient's record
        const own = Object.entries(cons.assignment).find(([, t]) => t === p.id); const other = patients.find((x: any) => x.id !== p.id);
        if (own && other) {
          summary.probes++;
          const moved = { ...cons, assignment: setLine(notes, patients, cons.assignment, Number(own[0]), other.id) };
          if (validateConsultation(moved).byPatient[p.id].some((x) => x.rule === 'wrong_animal_line')) summary.probes_caught++;
          else problems.push(`${p.id}: line ${Number(own[0]) + 1} moved to ${other.id} not caught`);
        }
      }
      for (const sg of suggestAssignments(notes, patients)) if (cons.assignment[sg.line] !== sg.target) problems.push(`suggestion for line ${sg.line + 1} (${sg.target}) disagrees with the assignment (${cons.assignment[sg.line] ?? 'none'})`);
      if (!Object.values(cons.assignment).includes(SHARED)) problems.push('no shared line');
      summary.patients += patients.length;
    } catch (e: any) { problems.push(`error: ${e?.message ?? e}`); }
    summary.cases++; if (problems.length) summary.failed++;
    summary.per_case.push({ id: c.id, pass: !problems.length });
    rows.push(`${problems.length ? 'FAIL' : 'PASS'}  ${c.id} (multi-pet)${problems.length ? '\n      - ' + problems.join('\n      - ') : ''}`);
  }
  return { rows, summary, failed: summary.failed };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  runEval().then((f) => process.exit(f ? 1 : 0));
}
