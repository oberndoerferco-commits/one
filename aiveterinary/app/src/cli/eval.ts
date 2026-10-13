/**
 * Evaluation harness.
 *   npm run eval            → fixture mode: validates the fixture records and checks expectations (offline)
 *   AIVET_EXTRACTOR=claude npm run eval → runs the model on each case, then validates (needs ANTHROPIC_API_KEY)
 *
 * Exit code 1 if any blocking finding appears on a case that is not marked fixture_must_fail.
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing, type Finding } from '../validators.js';
import { ClaudeExtractor, FixtureExtractor, type Extractor, PROMPT_VERSION } from '../extract.js';
import { renderConsultReport } from '../render.js';

const here = dirname(fileURLToPath(import.meta.url));
const casesDir = join(here, '..', '..', 'eval', 'cases');

type Case = { id: string; language: string; header: unknown; notes: string; expect: any; fixture_record?: unknown };

export async function runEval(extractorName = process.env.AIVET_EXTRACTOR ?? 'fixture', verbose = process.argv.includes('--verbose')) {
  const files = readdirSync(casesDir).filter((f) => f.endsWith('.json')).sort();
  const cases: Case[] = files.map((f) => JSON.parse(readFileSync(join(casesDir, f), 'utf8')));
  const fixtures = Object.fromEntries(cases.filter((c) => c.fixture_record).map((c) => [normalizeNotes(c.notes), c.fixture_record]));
  const extractor: Extractor = extractorName === 'claude' ? new ClaudeExtractor() : new FixtureExtractor(fixtures);

  let failures = 0; const rows: string[] = [];
  const totals = { cases: 0, blocks: 0, warns: 0, unsourced: 0, drugMismatch: 0, missRecall: 0, missTotal: 0, input_tokens: 0, output_tokens: 0 };
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
        const drugs = record.medications.map((m) => m.drug).filter(Boolean);
        for (const d of drugs) if (!(c.expect?.drugs ?? []).some((x: string) => x.toLowerCase() === String(d).toLowerCase())) { totals.drugMismatch++; problems.push(`unexpected drug ${d}`); }
        if (c.expect?.assessment_text !== undefined && (record.assessment.text ?? null) !== c.expect.assessment_text) problems.push(`assessment "${record.assessment.text}" ≠ expected "${c.expect.assessment_text}"`);
        if (c.expect?.temperature !== undefined && record.examination.vitals.temperature?.value !== c.expect.temperature) problems.push(`temperature ${record.examination.vitals.temperature?.value} ≠ ${c.expect.temperature}`);
        const json = JSON.stringify({ ...record, uncertain: [] }).toLowerCase();
        for (const bad of c.expect?.must_not_contain ?? []) if (json.includes(bad)) problems.push(`record contains forbidden text "${bad}" outside 'uncertain'`);
        if (c.expect?.uncertain_min && record.uncertain.length < c.expect.uncertain_min) problems.push(`expected ≥${c.expect.uncertain_min} uncertain entries`);
      }
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
  console.log(`\n${totals.cases} cases, ${failures} failed. blocking=${totals.blocks} warnings=${totals.warns} unsourced=${totals.unsourced} drug-mismatch=${totals.drugMismatch} missing-recall=${totals.missTotal ? Math.round((100 * totals.missRecall) / totals.missTotal) + '%' : 'n/a'}${totals.input_tokens ? ` tokens in/out=${totals.input_tokens}/${totals.output_tokens}` : ''}`);
  return failures;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  runEval().then((f) => process.exit(f ? 1 : 0));
}
