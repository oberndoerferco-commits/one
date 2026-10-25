// Share image for each article and animal page: dist/og/<lang>/<slug>.png (see src/lib/og.ts).
import type { APIRoute } from 'astro';
import { readFileSync } from 'node:fs';
import { allCards, cardFile } from '../../../lib/og';

export async function getStaticPaths() {
  return [...(await allCards()).keys()].map((id) => {
    const [lang, slug] = id.split('/');
    return { params: { lang, slug } };
  });
}

export const GET: APIRoute = async ({ params }) =>
  new Response(readFileSync(await cardFile(`${params.lang}/${params.slug}`)), { headers: { 'Content-Type': 'image/png' } });
