// Review integrity for owner articles.
//
//   node scripts/review.mjs check            (runs before every build)
//   node scripts/review.mjs sign <file> --by "Dr. Name, DVM" --reg "Ordine di Milano n. 1234" [--on 2026-10-20]
//
// "sign" records who reviewed an article, when, and a SHA-256 hash of everything a reader
// relies on (title, description, species, category, urgency, sources, body). "check" fails
// the build if a reviewed article has changed since it was signed, so no edit, human or AI,
// can slip in after the vet's sign-off (EU AI Act Art. 50 guidelines: the human-review
// exemption is lost by any later AI edit). Drafts are not affected.
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import yaml from 'js-yaml';

const ROOT = 'src/content/animals';
const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : p.endsWith('.md') ? [p] : []; });

function parse(file) {
  const raw = readFileSync(file, 'utf8');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) throw new Error(`${file}: no frontmatter`);
  return { data: yaml.load(m[1]) ?? {}, body: m[2] };
}
const iso = (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v ?? null);
export function contentHash({ data, body }) {
  const payload = { title: data.title, description: data.description, species: data.species, category: data.category, urgency: data.urgency ?? null, references: data.references ?? [], body: body.replace(/\r\n/g, '\n').trim() };
  return createHash('sha256').update(JSON.stringify(payload)).digest('hex');
}

const [cmd = 'check', file, ...rest] = process.argv.slice(2);
if (cmd === 'check') {
  const problems = [];
  let reviewed = 0;
  for (const f of walk(ROOT)) {
    const a = parse(f);
    const isReviewed = a.data.draft === false || a.data.reviewedBy;
    if (!isReviewed) continue;
    reviewed++;
    if (!a.data.reviewedBy || !a.data.reviewedOn) problems.push(`${f}: marked as reviewed but reviewer or date is missing`);
    else if (!a.data.reviewHash) problems.push(`${f}: reviewed but never signed (run: node scripts/review.mjs sign ${f} --by "…")`);
    else if (a.data.reviewHash !== contentHash(a)) problems.push(`${f}: changed after review by ${a.data.reviewedBy} on ${iso(a.data.reviewedOn)}. Revert the change or have it reviewed and signed again.`);
  }
  if (problems.length) { console.error('Review check failed:\n- ' + problems.join('\n- ')); process.exit(1); }
  console.log(`Review check: ${reviewed} reviewed article(s) unchanged since sign-off.`);
} else if (cmd === 'sign') {
  const arg = (k) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : undefined; };
  const by = arg('--by'); if (!file || !by) { console.error('Usage: sign <file> --by "Dr. Name, DVM" [--reg "…"] [--on YYYY-MM-DD]'); process.exit(2); }
  const a = parse(file);
  const on = arg('--on') ?? new Date().toISOString().slice(0, 10);
  const next = new Date(on); next.setFullYear(next.getFullYear() + 1);
  Object.assign(a.data, { draft: false, reviewedBy: by, reviewedOn: on, nextReview: next.toISOString().slice(0, 10), reviewHash: contentHash(a) });
  if (arg('--reg')) a.data.reviewerRegistration = arg('--reg');
  for (const k of Object.keys(a.data)) if (a.data[k] instanceof Date) a.data[k] = iso(a.data[k]);
  writeFileSync(file, `---\n${yaml.dump(a.data, { lineWidth: -1 })}---\n${a.body}`);
  console.log(`Signed ${file}: reviewed by ${by} on ${on}.`);
} else { console.error(`Unknown command ${cmd}`); process.exit(2); }
