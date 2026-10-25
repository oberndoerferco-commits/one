import type { APIRoute, GetStaticPaths } from 'astro';
import { getCollection } from 'astro:content';
import { articleChunks, type Chunk } from '../lib/ask-ai/chunks';
import { SHARED_TOPICS } from '../data/species';

// Heading-level passages of every article in one language, for the AI answer (functions/api/ask.ts,
// docs/31-ai-answer.md). Built to dist/ask-chunks-en.json, -it.json and -de.json. Public data: the same
// text as the articles. The function reads it from the static assets; nothing else uses it.
export const getStaticPaths: GetStaticPaths = () => ['en', 'it', 'de'].map((lang) => ({ params: { lang } }));

export const GET: APIRoute = async ({ params }) => {
  const lang = params.lang as 'en' | 'it' | 'de';
  const entries = (await getCollection('animals')).filter((e) => e.data.lang === lang);
  const chunks: Chunk[] = entries
    .sort((a, b) => (a.id < b.id ? -1 : 1))
    .flatMap((e) => { const slug = String(e.id).split('/').pop()!; return articleChunks({
      slug,
      title: e.data.title,
      description: e.data.description,
      body: e.body ?? '',
      urgency: e.data.urgency ?? null,
      draft: e.data.draft,
      species: e.data.species,
      also: Object.entries(SHARED_TOPICS).filter(([, v]) => v?.[lang].includes(slug)).map(([k]) => k),
    }); });
  return new Response(JSON.stringify(chunks), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
