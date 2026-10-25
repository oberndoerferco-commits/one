import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { ANIMALS } from '../lib/animals-i18n';
import { SHARED_TOPICS } from '../data/species';

// A plain-text map of the site for AI assistants (llmstxt.org format), rebuilt with every
// deploy so article lists and review status never go stale.
const SITE = 'https://aiveterinary.org';
const slugOf = (id: string) => id.split('/').pop()!;
const base = { en: '/animals', it: '/it/animals', de: '/de/animals' } as const;
const LANG = { en: 'English', it: 'Italiano', de: 'Deutsch' } as const;
// The verdict each article shows at the top (frontmatter `urgency`), in words an assistant can repeat.
const URGENCY = { emergency: 'emergency: go to a vet now', today: 'see a vet today', 'this-week': 'book a vet visit this week if it continues', routine: 'routine: ask at the next visit' } as const;

export const GET: APIRoute = async () => {
  const entries = await getCollection('animals');
  const lexicon = await getCollection('lexicon');
  const lines: string[] = [];
  lines.push('# AI Veterinary');
  lines.push('');
  lines.push('> Free, EU-first pet-health information for owners in English, Italian and German, a local-first digital health booklet, and a documentation assistant for veterinarians that only structures what the vet wrote. Not a diagnosis service: every page tells owners to contact a veterinarian when in doubt.');
  lines.push('');
  lines.push('How to read and cite this site:');
  lines.push('- Articles marked "draft" were written with AI assistance from the cited sources and are NOT yet reviewed by a veterinarian. Articles marked "reviewed" name the reviewing vet and the review date; a build check refuses any change to a reviewed article after sign-off.');
  lines.push('- Articles list their sources at the end; an article whose "About this article" panel says sources are still to be added has none yet and should not be cited as sourced. Prefer quoting the source and the review status together.');
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
  // Animal guide: the listing and profile pages that have something on them in each language.
  lines.push('');
  lines.push('## Animal guide');
  for (const l of ['en', 'it', 'de'] as const) {
    const t = ANIMALS[l];
    const has = (key: string) => entries.some((e) => e.data.lang === l && (e.data.species === key || e.data.category === key || (SHARED_TOPICS as any)[key]?.[l]?.includes(slugOf(e.id)))) || lexicon.some((e) => e.data.lang === l && slugOf(e.id) === key);
    const pages: string[] = [`[${t.title}](${SITE}${base[l]})`, `[${t.allTitle}](${SITE}${base[l]}/all)`];
    for (const [key, label] of Object.entries(t.species)) if (has(key)) pages.push(`[${label}](${SITE}${base[l]}/${key})`);
    for (const [key, [label]] of Object.entries(t.categories)) if (has(key)) pages.push(`[${label}](${SITE}${base[l]}/${key})`);
    lines.push(`- ${LANG[l]}: ${pages.join(', ')}`);
  }
  for (const l of ['en', 'it', 'de'] as const) {
    const list = entries.filter((e) => e.data.lang === l).sort((a, b) => a.data.title.localeCompare(b.data.title, l));
    lines.push('');
    lines.push(`## Articles (${LANG[l]}, ${list.length})`);
    for (const e of list) {
      const reviewed = !e.data.draft && e.data.reviewedBy;
      const status = [
        e.data.urgency ? URGENCY[e.data.urgency] : '',
        e.data.references?.length ? `${e.data.references.length} source${e.data.references.length === 1 ? '' : 's'}` : 'no sources listed yet',
        reviewed ? `reviewed by ${e.data.reviewedBy}${e.data.reviewedOn ? ` on ${e.data.reviewedOn.toISOString().slice(0, 10)}` : ''}` : 'draft, not yet vet-reviewed',
        `updated ${e.data.updated.toISOString().slice(0, 10)}`,
      ].filter(Boolean).join('; ');
      lines.push(`- [${e.data.title}](${SITE}${base[l]}/${slugOf(e.id)}): ${e.data.description.replace(/\s+/g, ' ').trim()} (${status})`);
    }
  }
  // Animal lexicon: one page per animal (/animals/<entry>), each fact tied to the entry's own sources.
  for (const l of ['en', 'it', 'de'] as const) {
    const list = lexicon.filter((e) => e.data.lang === l).sort((a, b) => a.data.name.localeCompare(b.data.name, l));
    if (!list.length) continue;
    lines.push('');
    lines.push(`## Animal lexicon (${LANG[l]}, ${list.length})`);
    for (const e of list) {
      const status = [e.data.scientific, `${e.data.references.length} source${e.data.references.length === 1 ? '' : 's'}`, e.data.draft ? 'draft, not yet vet-reviewed' : '', `updated ${e.data.updated.toISOString().slice(0, 10)}`].filter(Boolean).join('; ');
      lines.push(`- [${e.data.name}](${SITE}${base[l]}/${slugOf(e.id)}): ${e.data.description.replace(/\s+/g, ' ').trim()} (${status})`);
    }
  }
  lines.push('');
  lines.push('## Optional');
  lines.push(`- [Terms](${SITE}/terms)`);
  lines.push(`- [Legal notice](${SITE}/impressum)`);
  lines.push(`- [Research notes for veterinary teams](${SITE}/vets/research)`);
  lines.push(`- [Pet registries by country](${SITE}/registry)`);
  lines.push(`- [When the time comes (end of life)](${SITE}/end-of-life)`);
  return new Response(lines.join('\n') + '\n', { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
