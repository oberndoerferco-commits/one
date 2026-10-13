/**
 * Demo: notes in → report out.
 *   npm run demo                         → uses the Luna fixture (offline)
 *   npm run demo -- --claude "notes…"    → runs the model (needs ANTHROPIC_API_KEY)
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClinicalRecord, PatientHeader } from '../schema.js';
import { normalizeNotes } from '../normalize.js';
import { validateAll, requiredMissing } from '../validators.js';
import { ClaudeExtractor, FixtureExtractor } from '../extract.js';
import { renderConsultReport } from '../render.js';

const here = dirname(fileURLToPath(import.meta.url));
const luna = JSON.parse(readFileSync(join(here, '..', '..', 'eval', 'cases', '001-luna-vomiting.json'), 'utf8'));
const useClaude = process.argv.includes('--claude');
const notesArg = process.argv.slice(2).filter((a) => !a.startsWith('--')).join(' ');
const notes = normalizeNotes(notesArg || luna.notes);
const header = PatientHeader.parse(luna.header);

const extractor = useClaude ? new ClaudeExtractor() : new FixtureExtractor({ [normalizeNotes(luna.notes)]: luna.fixture_record });
const res = await extractor.extract({ notes, header });
const record = ClinicalRecord.parse(res.record);
const findings = validateAll(record, notes, header);

console.log('--- NOTES ---\n' + notes + '\n');
console.log('--- REPORT (' + res.model + ') ---\n' + renderConsultReport(record, header, 'en') + '\n');
console.log('--- CHECKS ---');
console.log(findings.length ? findings.map((f) => `${f.severity.toUpperCase()} ${f.rule} ${f.field}: ${f.message}`).join('\n') : 'No findings. Nothing on the page that was not in the notes.');
console.log('Needed before approval: ' + (requiredMissing(record, 'consult_report').join(', ') || 'nothing'));
