// Review integrity for owner articles.
//
//   node scripts/review.mjs check            (runs before every build)
//   node scripts/review.mjs sign <file> --by "Dr. Name, DVM" --reg "Ordine di Milano n. 1234" [--on 2026-10-20]
//   node scripts/review.mjs queue [--lang en|it|de]   (unreviewed articles, most urgent first; re-reviews due)
//   node scripts/review.mjs diff <file>               (what changed in a signed article since it was signed)
//
// "sign" records who reviewed an article, when, and a SHA-256 hash of everything a reader
// relies on (title, description, species, category, urgency, sources, body). "check" fails
// the build if a reviewed article has changed since it was signed, so no edit, human or AI,
// can slip in after the vet's sign-off (EU AI Act Art. 50 guidelines: the human-review
// exemption is lost by any later AI edit). Drafts are not affected.
// "queue" and "diff" only read: they never write a file.
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';

export const ROOT = 'src/content/animals';
export const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : p.endsWith('.md') ? [p] : []; });

export function parseText(raw, file = 'article') {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) throw new Error(`${file}: no frontmatter`);
  return { data: yaml.load(m[1]) ?? {}, body: m[2] };
}
export function parse(file) {
  return parseText(readFileSync(file, 'utf8'), file);
}
const iso = (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v ?? null);
export function contentHash({ data, body }) {
  const payload = { title: data.title, description: data.description, species: data.species, category: data.category, urgency: data.urgency ?? null, references: data.references ?? [], body: body.replace(/\r\n/g, '\n').trim() };
  return createHash('sha256').update(JSON.stringify(payload)).digest('hex');
}

// ---- helpers for queue, diff and scripts/reviewer-pack.mjs (read-only) ----

export const URGENCY_ORDER = ['emergency', 'today', 'this-week', 'routine', null];
export const urgencyRank = (u) => { const i = URGENCY_ORDER.indexOf(u ?? null); return i < 0 ? URGENCY_ORDER.length : i; };
export const isReviewed = (a) => !!(a.data.draft === false || a.data.reviewedBy);
/** Words a reviewer reads: the body without Markdown syntax, plus title and description. */
export function wordCount({ data, body }) {
  const text = [data.title, data.description, body.replace(/\]\([^)]*\)/g, ']').replace(/[#*_>`|[\]-]/g, ' ')].join(' ');
  return (text.match(/[\p{L}\p{N}][\p{L}\p{N}'’.,-]*/gu) ?? []).length;
}
/** Careful clinical reading at about 130 words a minute, plus 4 minutes for the checklist and sources. */
export const reviewMinutes = (words) => Math.ceil(words / 130) + 4;

/** Articles that need a vet: never reviewed, or past their next-review date. Most urgent first. */
export function reviewQueue(files, { lang, today = new Date().toISOString().slice(0, 10) } = {}) {
  const out = [];
  for (const file of files) {
    const a = parse(file);
    const l = a.data.lang ?? 'en';
    if (lang && l !== lang) continue;
    let reason = null;
    if (!isReviewed(a)) reason = 'unreviewed';
    else if (a.data.nextReview && iso(a.data.nextReview) < today) reason = `re-review due since ${iso(a.data.nextReview)}`;
    if (!reason) continue;
    const words = wordCount(a);
    out.push({ file, lang: l, title: a.data.title, urgency: a.data.urgency ?? null, species: a.data.species, words, minutes: reviewMinutes(words), reason });
  }
  return out.sort((x, y) => urgencyRank(x.urgency) - urgencyRank(y.urgency) || x.lang.localeCompare(y.lang) || x.file.localeCompare(y.file));
}

/** Line diff (longest common subsequence). Returns [{ op: ' ' | '-' | '+', a?, b?, text }], with 1-based line numbers. */
export function lineDiff(before, after) {
  const A = before.split('\n'), B = after.split('\n');
  const n = A.length, m = B.length;
  const L = Array.from({ length: n + 1 }, () => new Uint32Array(m + 1));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) L[i][j] = A[i] === B[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
  const ops = [];
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (A[i] === B[j]) { ops.push({ op: ' ', a: i + 1, b: j + 1, text: A[i] }); i++; j++; }
    else if (L[i + 1][j] >= L[i][j + 1]) { ops.push({ op: '-', a: i + 1, text: A[i] }); i++; }
    else { ops.push({ op: '+', b: j + 1, text: B[j] }); j++; }
  }
  while (i < n) { ops.push({ op: '-', a: i + 1, text: A[i] }); i++; }
  while (j < m) { ops.push({ op: '+', b: j + 1, text: B[j] }); j++; }
  return ops;
}
/** Changed lines with `context` unchanged lines around them; gaps shown as "…". */
export function formatDiff(ops, context = 2) {
  const keep = ops.map((o, k) => o.op !== ' ' || ops.slice(Math.max(0, k - context), k + context + 1).some((x) => x.op !== ' '));
  const lines = [];
  let gap = false;
  ops.forEach((o, k) => {
    if (!keep[k]) { gap = true; return; }
    if (gap && lines.length) lines.push('  …');
    gap = false;
    const num = o.op === '+' ? `   +${o.b}` : o.op === '-' ? `${o.a}-   ` : `${o.a}`;
    lines.push(`${o.op} ${String(num).padStart(8)} | ${o.text}`);
  });
  return lines.join('\n');
}
/** What a reader relies on, as text, field by field (the same fields contentHash covers). */
export function reviewedFields({ data, body }) {
  return {
    title: String(data.title ?? ''),
    description: String(data.description ?? ''),
    species: String(data.species ?? ''),
    category: String(data.category ?? ''),
    urgency: String(data.urgency ?? ''),
    references: (data.references ?? []).map((r) => `${r.title}${r.url ? ` <${r.url}>` : ''}`).join('\n'),
    body: body.replace(/\r\n/g, '\n').trim(),
  };
}
export function articleDiff(signed, current) {
  const s = reviewedFields(signed), c = reviewedFields(current);
  return Object.keys(s).filter((k) => s[k] !== c[k]).map((k) => ({ field: k, ops: lineDiff(s[k], c[k]) }));
}
/** The version of `file` that was signed with `hash`, found in git history (newest commit first). */
export function signedVersion(file, hash) {
  const git = (...args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'] });
  let commits = [];
  try { commits = git('log', '--format=%H', '--', file).split('\n').filter(Boolean); } catch { return null; }
  for (const c of commits) {
    let raw;
    try { raw = git('show', `${c}:./${file}`); } catch { continue; }
    try {
      const a = parseText(raw, `${c}:${file}`);
      if (a.data.reviewHash === hash && contentHash(a) === hash) return { commit: c, article: a };
    } catch { /* unparsable old version: keep looking */ }
  }
  return null;
}

// ---- command line ----

function main(argv) {
  const [cmd = 'check', file, ...rest] = argv;
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
  } else if (cmd === 'queue') {
    const args = [file, ...rest].filter((x) => x !== undefined);
    const li = args.indexOf('--lang');
    const lang = li >= 0 ? args[li + 1] : undefined;
    if (lang && !['en', 'it', 'de'].includes(lang)) { console.error('Usage: queue [--lang en|it|de]'); process.exit(2); }
    const q = reviewQueue(walk(ROOT), { lang });
    if (!q.length) { console.log(`Review queue: nothing to review${lang ? ` in ${lang}` : ''}.`); return; }
    let current;
    for (const r of q) {
      const u = r.urgency ?? 'no urgency set';
      if (u !== current) { const group = q.filter((x) => (x.urgency ?? 'no urgency set') === u); console.log(`\n${u.toUpperCase()} (${group.length} article(s), about ${Math.round(group.reduce((s, x) => s + x.minutes, 0) / 6) / 10} h)`); current = u; }
      console.log(`  ${r.lang}  ${r.file.padEnd(58)} ${String(r.words).padStart(5)} words  ~${String(r.minutes).padStart(2)} min${r.reason === 'unreviewed' ? '' : `  [${r.reason}]`}  ${r.title}`);
    }
    const mins = q.reduce((s, x) => s + x.minutes, 0);
    console.log(`\n${q.length} article(s) to review, about ${Math.round(mins / 6) / 10} hours in all. Sign one with: node scripts/review.mjs sign <file> --by "…" --reg "…"`);
  } else if (cmd === 'diff') {
    if (!file) { console.error('Usage: diff <file>'); process.exit(2); }
    const cur = parse(file);
    if (!cur.data.reviewHash) { console.log(`${file} has never been signed: nothing to compare with.`); return; }
    if (cur.data.reviewHash === contentHash(cur)) { console.log(`${file}: unchanged since it was signed by ${cur.data.reviewedBy} on ${iso(cur.data.reviewedOn)}.`); return; }
    const found = signedVersion(file, cur.data.reviewHash);
    if (!found) { console.error(`${file} changed since signing, but the signed version is not in git history (it was signed and edited before a commit). Ask the reviewer to check the current text and sign again.`); process.exit(1); }
    console.log(`${file}: changes since it was signed by ${cur.data.reviewedBy} on ${iso(cur.data.reviewedOn)} (signed text from commit ${found.commit.slice(0, 10)}).`);
    for (const d of articleDiff(found.article, cur)) console.log(`\n== ${d.field} ==\n${formatDiff(d.ops)}`);
    console.log('\nLine numbers: left = signed version, right = current version (body: counted from its first line of text).');
  } else { console.error(`Unknown command ${cmd}`); process.exit(2); }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main(process.argv.slice(2));
