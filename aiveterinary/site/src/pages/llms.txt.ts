import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

// A plain-text map of the site for AI assistants (llmstxt.org format), rebuilt with every
// deploy so article lists and review status never go stale.
const SITE = 'https://aiveterinary.org';
const slugOf = (id: string) => id.split('/').pop()!;
const base = { en: '/animals', it: '/it/animals', de: '/de/animals' } as const;
const LANG = { en: 'English', it: 'Italiano', de: 'Deutsch' } as const;

export const GET: APIRoute = async () => {
  const entries = await getCollection('animals');
  const lines: string[] = [];
  lines.push('# AI Veterinary');
  lines.push('');
  lines.push('> Free, EU-first pet-health information for owners in English, Italian and German, a local-first digital health booklet, and a documentation assistant for veterinarians that only structures what the vet wrote. Not a diagnosis service: every page tells owners to contact a veterinarian when in doubt.');
  lines.push('');
  lines.push('How to read and cite this site:');
  lines.push('- Articles marked "draft" were written with AI assistance from the cited sources and are NOT yet reviewed by a veterinarian. Articles marked "reviewed" name the reviewing vet and the review date; a build check refuses any change to a reviewed article after sign-off.');
  lines.push('- Every article lists its sources. Prefer quoting the source and the review status together.');
  lines.push('- The tools (emergency check, chocolate dose, food lookup, vaccine planner) are fixed rules from named sources, not AI. None of them ever says an animal is safe.');
  lines.push('- In an emergency the only correct advice is to contact a veterinary clinic now.');
  lines.push('');
  lines.push('## About');
  lines.push(`- [Editorial policy](${SITE}/editorial): how articles are drafted, sourced, reviewed and corrected, and who is responsible`);
  lines.push(`- [About](${SITE}/about): who runs the site and why`);
  lines.push(`- [Privacy](${SITE}/privacy): no tracking cookies; the health booklet stays on the owner's device`);
  lines.push('');
  lines.push('## Tools for owners');
  for (const [l, p] of [['en', ''], ['it', '/it'], ['de', '/de']] as const) {
    lines.push(`- [Is it an emergency? (${LANG[l]})](${SITE}${p}/emergency): tick the signs; result is go now, see a vet today, or watch with a deadline`);
    lines.push(`- [Chocolate dose check for dogs (${LANG[l]})](${SITE}${p}/chocolate): MSD Veterinary Manual figures, arithmetic shown`);
    lines.push(`- [Can my pet eat that? (${LANG[l]})](${SITE}${p}/can-eat): ASPCA list of people foods to avoid`);
    lines.push(`- [Puppy and kitten vaccine planner (${LANG[l]})](${SITE}${p}/vaccine-planner): WSAVA 2024 tables and the EU rabies travel rule`);
    lines.push(`- [Health booklet (${LANG[l]})](${SITE}${p}/passport) and [pre-visit brief](${SITE}${p}/visit-brief): kept on the owner's device`);
    lines.push(`- [Travelling with a pet in Europe (${LANG[l]})](${SITE}${p}/travel)`);
  }
  lines.push('');
  lines.push('## For veterinarians');
  lines.push(`- [Overview](${SITE}/vets): text-first documentation assistant; the vet types notes, approves the structured record, then documents are generated; nothing appears that the vet did not write`);
  lines.push(`- [Quality](${SITE}/vets/quality): test set, published rates with 95 % confidence intervals, a repeatable 20-case stopwatch test`);
  lines.push(`- [Data and law](${SITE}/vets/data): GDPR roles, subprocessors, EU AI Act Article 50, professional secrecy`);
  lines.push(`- [Workspace preview](${SITE}/vets/workspace): try it on synthetic patients`);
  for (const l of ['en', 'it', 'de'] as const) {
    const list = entries.filter((e) => e.data.lang === l).sort((a, b) => a.data.title.localeCompare(b.data.title, l));
    lines.push('');
    lines.push(`## Articles (${LANG[l]}, ${list.length})`);
    for (const e of list) {
      const status = e.data.draft ? 'draft, not yet vet-reviewed' : `reviewed by ${e.data.reviewedBy}${e.data.reviewedOn ? ` on ${e.data.reviewedOn.toISOString().slice(0, 10)}` : ''}`;
      lines.push(`- [${e.data.title}](${SITE}${base[l]}/${slugOf(e.id)}): ${e.data.description} (${status}; updated ${e.data.updated.toISOString().slice(0, 10)})`);
    }
  }
  return new Response(lines.join('\n') + '\n', { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
