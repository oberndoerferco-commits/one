// Build-time: split an article's Markdown into heading-level passages for the AI answer
// (functions/api/ask.ts). Pure: no Astro imports, so it is unit-tested directly.
// Written to dist/ask-chunks-<lang>.json by src/pages/ask-chunks-[lang].json.ts.

export type Urgency = 'emergency' | 'today' | 'this-week' | 'routine';

/** One passage. `id` is unique per language file; `slug` is the article's URL slug. */
export type Chunk = {
  id: string;
  slug: string;
  title: string;
  heading: string;
  text: string;
  urgency: Urgency | null;
  draft: boolean;
  species: string;
  /** Other species the article also covers (SHARED_TOPICS in src/data/species.ts). */
  also?: string[];
};

export type ArticleInput = {
  slug: string;
  title: string;
  description: string;
  body: string;
  urgency: Urgency | null;
  draft: boolean;
  species: string;
  also?: string[];
};

/** Longest passage text; a longer section is split at paragraph breaks. */
export const MAX_CHUNK_CHARS = 1600;

/** Markdown to plain text: links keep their text, emphasis, images, HTML and code fences go. */
export function mdToText(md: string): string {
  return md
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/(^|[\s(])[*_]([^*_\n]+)[*_](?=[\s).,;:!?]|$)/g, '$1$2')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/^\s{0,3}>\s?/gm, '')
    .replace(/^\s*[-*+]\s+/gm, '- ')
    .replace(/^\s*\|?[-:| ]+\|[-:| ]*$/gm, '')
    .replace(/\|/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .replace(/ *\n */g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function splitLong(text: string): string[] {
  if (text.length <= MAX_CHUNK_CHARS) return [text];
  const parts: string[] = [];
  let cur = '';
  for (const para of text.split(/\n\n+/)) {
    if (cur && cur.length + para.length + 2 > MAX_CHUNK_CHARS) { parts.push(cur); cur = ''; }
    if (para.length > MAX_CHUNK_CHARS) {
      // A single huge paragraph: cut at sentence ends.
      for (const s of para.split(/(?<=[.!?])\s+/)) {
        if (cur && cur.length + s.length + 1 > MAX_CHUNK_CHARS) { parts.push(cur); cur = ''; }
        cur = cur ? `${cur} ${s}` : s;
      }
    } else cur = cur ? `${cur}\n\n${para}` : para;
  }
  if (cur) parts.push(cur);
  return parts;
}

/**
 * One passage per `##` section (with its `###` subsections), plus the text before the first
 * heading. The description always opens the first passage so every article has a summary chunk.
 */
export function articleChunks(a: ArticleInput): Chunk[] {
  const sections: { heading: string; md: string }[] = [];
  let heading = a.title;
  let buf: string[] = [];
  const flush = () => { sections.push({ heading, md: buf.join('\n') }); buf = []; };
  for (const line of a.body.split('\n')) {
    const m = /^##\s+(.+?)\s*#*\s*$/.exec(line);
    if (m && !line.startsWith('###')) { flush(); heading = mdToText(m[1]); continue; }
    buf.push(line.replace(/^#{3,6}\s+(.+)$/, '$1:'));
  }
  flush();
  const out: Chunk[] = [];
  sections.forEach((s, i) => {
    let text = mdToText(s.md);
    if (i === 0) text = [a.description, text].filter(Boolean).join('\n\n');
    if (!text) return;
    splitLong(text).forEach((t, j) => {
      out.push({ id: `${a.slug}#${out.length}`, slug: a.slug, title: a.title, heading: s.heading + (j ? ` (${j + 1})` : ''), text: t, urgency: a.urgency, draft: a.draft, species: a.species, ...(a.also?.length ? { also: a.also } : {}) });
    });
  });
  return out;
}
