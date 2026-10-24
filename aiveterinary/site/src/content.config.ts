import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const animals = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/animals' }),
  schema: z.object({
    title: z.string(),
    seoTitle: z.string().max(70).optional(),
    description: z.string(),
    species: z.enum(['dog', 'cat', 'rabbit', 'guinea-pig', 'ferret', 'horse', 'bird', 'reptile', 'general']),
    category: z.enum(['symptoms', 'conditions', 'medications', 'travel', 'first-aid', 'care']),
    urgency: z.enum(['emergency', 'today', 'this-week', 'routine']).optional(),
    animals: z.array(z.string()).optional(),     // lexicon entries this article is about (file names in src/content/lexicon)
    author: z.string().optional(),               // "Dr. Name, DVM"
    reviewedBy: z.string().optional(),           // "Dr. Name, DVM"
    reviewerRegistration: z.string().optional(), // "Ordine di Milano n. 1234" / "TÄK Berlin"
    reviewedOn: z.coerce.date().optional(),
    reviewHash: z.string().optional(),          // set by scripts/review.mjs sign
    nextReview: z.coerce.date().optional(),
    references: z.array(z.object({ title: z.string(), url: z.string().url().optional() })).optional(),
    published: z.coerce.date().optional(),     // first publication; shown on the page and used as datePublished
    updated: z.coerce.date(),
    lang: z.enum(['en', 'de', 'it']).default('en'),
    draft: z.boolean().default(false),
  }),
});

// Animal lexicon: one entry per animal people keep (EN at the root, it/ and de/ with the same file name).
// Every fact in the fact sheet points at one of the entry's own references.
const lexicon = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/lexicon' }),
  schema: z.object({
    name: z.string(),                            // "Guinea pig" / "Cavia" / "Meerschweinchen"
    plural: z.string(),                          // "Guinea pigs"
    scientific: z.string().optional(),           // "Cavia porcellus"
    group: z.enum(['dogs-cats', 'small-mammals', 'birds', 'reptiles', 'fish', 'horses', 'poultry']),
    species: z.enum(['dog', 'cat', 'rabbit', 'guinea-pig', 'ferret', 'horse', 'bird', 'reptile']).optional(), // articles listed as health topics
    description: z.string(),
    facts: z.array(z.object({
      field: z.enum(['lifespan', 'size', 'weight', 'social', 'activity', 'diet', 'housing', 'temperature', 'teeth', 'handling', 'vet', 'legal']),
      value: z.string(),
      ref: z.number().int().min(1),              // 1-based index into references
    })).min(1),
    references: z.array(z.object({ title: z.string(), url: z.string().url() })).min(1),
    updated: z.coerce.date(),
    lang: z.enum(['en', 'de', 'it']).default('en'),
    draft: z.boolean().default(true),
  }),
});

export const collections = { animals, lexicon };
