// Fails the build if content cites a source whose terms forbid AI rewriting or repurposing.
// VCA Animal Hospitals' pages state: "The use of artificial intelligence or automated tools to rewrite,
// republish, adapt, or repurpose this content, in whole or in part, is prohibited." (checked 25 Oct 2026)
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const BANNED = [
  { name: 'VCA Animal Hospitals', re: /vcahospitals\.com|vca\s+animal\s+hospitals?|\bVCA\b/i },
];
const ROOTS = ['src/content', 'src/data'];

const files = [];
const walk = (dir) => {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p);
    else if (/\.(md|ts|json)$/.test(f)) files.push(p);
  }
};
ROOTS.forEach(walk);

const problems = [];
for (const f of files) {
  readFileSync(f, 'utf8').split('\n').forEach((line, i) => {
    for (const b of BANNED) if (b.re.test(line)) problems.push(`${f}:${i + 1}: cites ${b.name}`);
  });
}
if (problems.length) {
  console.error(problems.join('\n'));
  console.error(`source check: ${problems.length} citation(s) of banned sources`);
  process.exit(1);
}
console.log(`source check: ${files.length} files, no banned sources`);
