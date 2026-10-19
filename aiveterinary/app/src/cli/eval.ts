/**
 * Evaluation harness.
 *   npm run eval            → fixture mode: validates the fixture records and checks expectations (offline)
 *   AIVET_EXTRACTOR=claude npm run eval → runs the model on each case, then validates (needs ANTHROPIC_API_KEY)
 *
 * Exit code 1 if any blocking finding appears on a case that is not marked fixture_must_fail.
 */
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing, type Finding } from '../validators.js';
import { ClaudeExtractor, FixtureExtractor, type Extractor, PROMPT_VERSION } from '../extract.js';
import { renderConsultReport } from '../render.js';
import { wilson, scoreFacts, scoreMissingFlags, pct } from '../metrics.js';

const here = dirname(fileURLToPath(import.meta.url));
const casesDir = join(here, '..', '..', 'eval', 'cases');

type Case = { id: string; language: string; header: unknown; notes: string; expect: any; fixture_record?: unknown };

export async function runEval(extractorName = process.env.AIVET_EXTRACTOR ?? 'fixture', verbose = process.argv.includes('--verbose')) {
  const files = readdirSync(casesDir).filter((f) => f.endsWith('.json')).sort();
  const cases: Case[] = files.map((f) => JSON.parse(readFileSync(join(casesDir, f), 'utf8')));
  const fixtures = Object.fromEntries(cases.filter((c) => c.fixture_record).map((c) => [normalizeNotes(c.notes), c.fixture_record]));
  const extractor: Extractor = extractorName === 'claude' ? new ClaudeExtractor() : new FixtureExtractor(fixtures);

  let failures = 0; const rows: string[] = []; const falseFlags: string[] = [];
  const totals = { facts: 0, unsupportedFacts: 0, scored: 0, casesWithBlock: 0, cases: 0, blocks: 0, warns: 0, unsourced: 0, drugMismatch: 0, missRecall: 0, missTotal: 0, flagsRaised: 0, flagsCorrect: 0, input_tokens: 0, output_tokens: 0 };
  for (const c of cases) {
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
      // expectations
      const problems: string[] = [];
      if (mustFail) {
        for (const r of c.expect.expected_rules ?? []) if (!findings.some((f) => f.rule === r)) problems.push(`expected rule ${r} not raised`);
      } else {
        if (blocks.length) problems.push(`${blocks.length} blocking finding(s): ${blocks.map((b) => b.rule + '@' + b.field).join(', ')}`);
        const miss = new Set([...record.missing.map((m) => m.field), ...requiredMissing(record, 'consult_report')]);
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
      if (!mustFail) { const sc = scoreFacts(record, findings); totals.facts += sc.facts; totals.unsupportedFacts += sc.unsupported; totals.scored++; if (blocks.length) totals.casesWithBlock++; }
      totals.cases++; totals.blocks += blocks.length; totals.warns += findings.length - blocks.length;
      totals.unsourced += findings.filter((f) => f.rule === 'source_required' || f.rule === 'span_invalid').length;
      const ok = problems.length === 0;
      if (!ok) failures++;
      rows.push(`${ok ? 'PASS' : 'FAIL'}  ${c.id}${mustFail ? ' (must-fail fixture)' : ''}${problems.length ? '\n      - ' + problems.join('\n      - ') : ''}`);
      if (verbose) { rows.push(renderConsultReport(record, header, (c.language as any) ?? 'en').split('\n').map((l) => '      ' + l).join('\n')); rows.push('      findings: ' + JSON.stringify(findings)); }
    } catch (e: any) {
      failures++; totals.cases++; note = e?.message ?? String(e);
      rows.push(`FAIL  ${c.id}\n      - error: ${note}`);
    }
  }
  console.log(`AI Veterinary eval — extractor=${extractor.name} prompt=${PROMPT_VERSION}\n`);
  console.log(rows.join('\n'));
  // machine-readable result for the public quality page (site/src/pages/vets/quality.astro)
  const outDir = join(here, '..', '..', 'eval', 'results'); mkdirSync(outDir, { recursive: true });
  const metrics = {
    attribution: wilson(totals.facts - totals.unsupportedFacts, totals.facts),
    unsupported_content: wilson(totals.unsupportedFacts, totals.facts),
    cases_with_blocking_finding: wilson(totals.casesWithBlock, totals.scored),
    missing_field_detection: wilson(totals.missRecall, totals.missTotal),
    missing_flag_precision: wilson(totals.flagsCorrect, totals.flagsRaised),
  };
  const result = { metrics, run_at: new Date().toISOString(), extractor: extractor.name, prompt: PROMPT_VERSION, cases: totals.cases, failed: failures, blocking: totals.blocks, warnings: totals.warns, unsourced: totals.unsourced, drug_mismatch: totals.drugMismatch, missing_recall: totals.missTotal ? totals.missRecall / totals.missTotal : null, false_missing_flags: falseFlags, languages: [...new Set(cases.map((c) => c.language))].sort(), per_case: rows.filter((r) => /^(PASS|FAIL)/.test(r)).map((r) => ({ id: r.slice(6).split('\n')[0].replace(' (must-fail fixture)', ''), pass: r.startsWith('PASS') })) };
  writeFileSync(join(outDir, `${extractor.name}.json`), JSON.stringify(result, null, 2) + '\n');
  console.log(`\nattribution ${pct(metrics.attribution)}\nunsupported content ${pct(metrics.unsupported_content)}\ncases with a blocking finding ${pct(metrics.cases_with_blocking_finding)}\nmissing-field detection ${pct(metrics.missing_field_detection)}\nmissing-flag precision ${pct(metrics.missing_flag_precision)}`);
  if (falseFlags.length && verbose) console.log('flags raised but not expected:\n  ' + falseFlags.join('\n  '));
  console.log(`\n${totals.cases} cases, ${failures} failed. blocking=${totals.blocks} warnings=${totals.warns} unsourced=${totals.unsourced} drug-mismatch=${totals.drugMismatch} missing-recall=${totals.missTotal ? Math.round((100 * totals.missRecall) / totals.missTotal) + '%' : 'n/a'}${totals.input_tokens ? ` tokens in/out=${totals.input_tokens}/${totals.output_tokens}` : ''}`);
  return failures;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  runEval().then((f) => process.exit(f ? 1 : 0));
}
