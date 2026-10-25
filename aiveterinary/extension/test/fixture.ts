// Builds the approved export used by the tests, with the app's own code. `tsx test/fixture.ts` rewrites test/fixtures/approved-luna.json.
import { readFileSync, writeFileSync } from 'node:fs';
import { ClinicalRecord } from '../../app/src/schema.js';
import { approve } from '../../app/src/versions.js';
import { exportBundle } from '../../app/src/export.js';

export function lunaExport() {
  const c = JSON.parse(readFileSync(new URL('../../app/eval/cases/001-luna-vomiting.json', import.meta.url), 'utf8'));
  const record = ClinicalRecord.parse(c.fixture_record);
  const v = approve(record, 'Dr. Anna Test', '2026-10-20T10:00:00.000Z');
  return exportBundle(v, c.header, 'en', '2026-10-20T10:05:00.000Z', { [record.missing[0].field]: 'Not recorded' });
}

if (process.argv[1]?.endsWith('fixture.ts')) writeFileSync(new URL('fixtures/approved-luna.json', import.meta.url), JSON.stringify(lunaExport(), null, 2) + '\n');
