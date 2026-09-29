import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const animals = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/animals' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    species: z.enum(['dog', 'cat', 'rabbit', 'horse', 'bird', 'general']),
    category: z.enum(['symptoms', 'conditions', 'medications', 'travel', 'first-aid', 'care']),
    urgency: z.enum(['emergency', 'today', 'this-week', 'routine']).optional(),
    reviewedBy: z.string().optional(),
    reviewedOn: z.coerce.date().optional(),
    updated: z.coerce.date(),
    lang: z.enum(['en', 'de', 'it']).default('en'),
    draft: z.boolean().default(false),
  }),
});

export const collections = { animals };
