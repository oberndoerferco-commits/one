// node --test scripts/review.test.mjs
// Runs scripts/review.mjs in a throwaway folder (its own git repo), never on the real articles.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { contentHash, parseText, lineDiff, formatDiff, reviewQueue, wordCount, reviewMinutes } from './review.mjs';

const SCRIPT = fileURLToPath(new URL('./review.mjs', import.meta.url));
const article = ({ title = 'Dog vomiting', urgency = 'today', lang = 'en', body = '## First, the signs that mean go now\n\n- collapse\n- blood in vomit\n\nMore text.\n' } = {}) =>
  `---\ntitle: "${title}"\ndescription: "What to do."\nspecies: dog\ncategory: symptoms\n${urgency ? `urgency: ${urgency}\n` : ''}updated: 2026-10-01\ndraft: true\nlang: ${lang}\nreferences:\n  - title: "WSAVA guideline"\n    url: "https://wsava.org/"\n---\n\n${body}`;

function sandbox() {
  const dir = mkdtempSync(join(tmpdir(), 'review-test-'));
  mkdirSync(join(dir, 'src/content/animals/it'), { recursive: true });
  const run = (...args) => spawnSync(process.execPath, [SCRIPT, ...args], { cwd: dir, encoding: 'utf8' });
  const git = (...args) => execFileSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@example.org', ...args], { cwd: dir, encoding: 'utf8' });
  return { dir, run, git, put: (p, s) => writeFileSync(join(dir, p), s), get: (p) => readFileSync(join(dir, p), 'utf8'), done: () => rmSync(dir, { recursive: true, force: true }) };
}

test('hash covers what a reader relies on, not housekeeping fields', () => {
  const a = parseText(article());
  const b = parseText(article().replace('updated: 2026-10-01', 'updated: 2026-11-01'));
  const c = parseText(article({ urgency: 'emergency' }));
  assert.equal(contentHash(a), contentHash(b));
  assert.notEqual(contentHash(a), contentHash(c));
});

test('sign then check passes; any later edit fails the check', () => {
  const s = sandbox();
  try {
    const f = 'src/content/animals/dog-vomiting.md';
    s.put(f, article());
    assert.equal(s.run('check').status, 0);
    const signed = s.run('sign', f, '--by', 'Dr. Test, DVM', '--reg', 'Ordine di Milano n. 1', '--on', '2026-10-20');
    assert.equal(signed.status, 0, signed.stderr);
    const fm = s.get(f);
    assert.match(fm, /draft: false/);
    assert.match(fm, /reviewedOn: '?2026-10-20'?/);
    assert.match(fm, /nextReview: '?2027-10-20'?/);
    assert.match(fm, /reviewerRegistration: Ordine di Milano n. 1/);
    assert.equal(s.run('check').status, 0);
    s.put(f, fm.replace('- collapse', '- collapse or fainting'));
    const bad = s.run('check');
    assert.equal(bad.status, 1);
    assert.match(bad.stderr, /changed after review by Dr. Test, DVM on 2026-10-20/);
  } finally { s.done(); }
});

test('queue lists unreviewed articles, emergency first, and skips signed ones', () => {
  const s = sandbox();
  try {
    s.put('src/content/animals/a-routine.md', article({ title: 'Routine', urgency: 'routine' }));
    s.put('src/content/animals/b-emergency.md', article({ title: 'Emergency', urgency: 'emergency' }));
    s.put('src/content/animals/it/c-oggi.md', article({ title: 'Oggi', urgency: 'today', lang: 'it' }));
    s.put('src/content/animals/d-none.md', article({ title: 'None', urgency: null }));
    s.put('src/content/animals/e-signed.md', article({ title: 'Signed', urgency: 'emergency' }));
    assert.equal(s.run('sign', 'src/content/animals/e-signed.md', '--by', 'Dr. T').status, 0);
    const out = s.run('queue');
    assert.equal(out.status, 0, out.stderr);
    const order = ['Emergency', 'Oggi', 'Routine', 'None'].map((t) => out.stdout.indexOf(t));
    assert.ok(order.every((x, i) => x >= 0 && (i === 0 || x > order[i - 1])), out.stdout);
    assert.ok(!out.stdout.includes('Signed'));
    const it = s.run('queue', '--lang', 'it');
    assert.match(it.stdout, /Oggi/);
    assert.ok(!it.stdout.includes('Routine'));
  } finally { s.done(); }
});

test('queue also lists signed articles past their next-review date', () => {
  const s = sandbox();
  try {
    const f = 'src/content/animals/old.md';
    s.put(f, article({ title: 'Old one' }));
    s.run('sign', f, '--by', 'Dr. T', '--on', '2020-01-01');
    const q = reviewQueue([join(s.dir, f)], { today: '2026-10-25' });
    assert.equal(q.length, 1);
    assert.match(q[0].reason, /re-review due since 2021-01-01/);
  } finally { s.done(); }
});

test('diff shows the change since signing, read from git history', () => {
  const s = sandbox();
  try {
    const f = 'src/content/animals/dog-vomiting.md';
    s.put(f, article());
    s.git('init', '-q');
    s.run('sign', f, '--by', 'Dr. Test, DVM', '--on', '2026-10-20');
    s.git('add', '.');
    s.git('commit', '-qm', 'signed');
    assert.match(s.run('diff', f).stdout, /unchanged since it was signed by Dr. Test, DVM on 2026-10-20/);
    s.put(f, s.get(f).replace('- blood in vomit', '- blood in the vomit'));
    s.git('commit', '-qam', 'edit');
    const d = s.run('diff', f);
    assert.equal(d.status, 0, d.stderr);
    assert.match(d.stdout, /== body ==/);
    assert.match(d.stdout, /- +4- +\| - blood in vomit/);
    assert.match(d.stdout, /\+ +\+4 \| - blood in the vomit/);
    assert.ok(!d.stdout.includes('== title =='));
    assert.equal(s.run('check').status, 1); // diff never re-signs
  } finally { s.done(); }
});

test('lineDiff and formatDiff', () => {
  const ops = lineDiff('a\nb\nc', 'a\nB\nc\nd');
  assert.deepEqual(ops.filter((o) => o.op !== ' ').map((o) => o.op + o.text), ['-b', '+B', '+d']);
  assert.match(formatDiff(ops), /- +2- +\| b/);
});

test('word count and time estimate', () => {
  const a = parseText(article({ body: 'One two three [four](https://x.org) **five**.\n' }));
  assert.equal(wordCount(a), 2 + 3 + 5); // title + description + body
  assert.equal(reviewMinutes(130), 5);
  assert.equal(reviewMinutes(131), 6);
});
