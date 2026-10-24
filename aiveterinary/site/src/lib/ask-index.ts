import { getCollection } from 'astro:content';
import type { Lang } from './animals-i18n';

// Build-time map of article URL -> the article's own title, description, urgency and species.
// The home page "Ask" box looks up Pagefind results here so it only ever shows existing
// article data (Pagefind results do not carry urgency).
export type AskEntry = { t: string; d: string; u: string | null; s: string; c: string; draft: boolean };
const base = { en: '/animals', it: '/it/animals', de: '/de/animals' } as const;

export async function askIndex(lang: Lang): Promise<Record<string, AskEntry>> {
  const entries = (await getCollection('animals')).filter((e) => e.data.lang === lang);
  const out: Record<string, AskEntry> = {};
  for (const e of entries) {
    const slug = String(e.id).split('/').pop();
    out[`${base[lang]}/${slug}`] = { t: e.data.title, d: e.data.description, u: e.data.urgency ?? null, s: e.data.species, c: e.data.category, draft: e.data.draft };
  }
  return out;
}

export const askIndexResponse = async (lang: Lang) =>
  new Response(JSON.stringify(await askIndex(lang)), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
