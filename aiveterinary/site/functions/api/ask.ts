// Cloudflare Pages Function: POST /api/ask -> AI answer from our own articles.
// Everything except the SDK call lives in src/lib/ask-ai/core.ts (tested in test/ask-ai.test.ts).
// Design, safety rules, cost and how to switch it on: docs/31-ai-answer.md.
//
// Secrets: ANTHROPIC_API_KEY comes only from the Pages project's environment variables (encrypted),
// never from source. Without it this returns 503 {disabled: true} and the site keeps its Pagefind answer.
// Optional: ASK_MODEL (default claude-opus-5-5), ASK_EFFORT (low | medium | high, default low).
//
// Privacy: the question is sent to the model provider to write the answer and is not logged or stored here.
//
// TODO(owner, Cloudflare dashboard): add abuse protection before announcing the feature. Either
//   - a WAF rate-limiting rule on the zone (Security -> WAF -> Rate limiting rules) for
//     "URI Path equals /api/ask", e.g. a few requests per minute per IP, action Block; or
//   - Turnstile: create a widget, add its site key to AskBox.astro and verify the token here with
//     the secret key (https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).
// Also set a monthly spend limit on the API key in the Claude Console. None of this is configured in code.
import Anthropic from '@anthropic-ai/sdk';
import { handleAsk, type CreateMessage, type Lang } from '../../src/lib/ask-ai/core';
import type { Chunk } from '../../src/lib/ask-ai/chunks';

interface Env {
  ANTHROPIC_API_KEY?: string;
  ASK_MODEL?: string;
  ASK_EFFORT?: string;
  /** Static assets of this Pages project (the built site). */
  ASSETS: { fetch: (input: Request | string | URL) => Promise<Response> };
}

type Context = { request: Request; env: Env };

// The passage index of each language, kept for the life of the worker isolate.
const chunkCache = new Map<Lang, Promise<Chunk[]>>();

function loader(env: Env, requestUrl: string) {
  return (lang: Lang): Promise<Chunk[]> => {
    let p = chunkCache.get(lang);
    if (!p) {
      p = env.ASSETS.fetch(new URL(`/ask-chunks-${lang}.json`, requestUrl)).then((r) => {
        if (!r.ok) throw new Error(`chunks ${r.status}`);
        return r.json() as Promise<Chunk[]>;
      });
      p.catch(() => chunkCache.delete(lang));
      chunkCache.set(lang, p);
    }
    return p;
  };
}

const makeClient = (apiKey: string): CreateMessage => {
  // 25 s per attempt, one retry (the SDK retries 408/409/429/5xx and connection errors).
  const client = new Anthropic({ apiKey, timeout: 25_000, maxRetries: 1 });
  return (params) => client.beta.messages.create(params);
};

export const onRequest = (context: Context): Promise<Response> =>
  handleAsk(context.request, {
    apiKey: context.env.ANTHROPIC_API_KEY,
    model: context.env.ASK_MODEL,
    effort: context.env.ASK_EFFORT,
    makeClient,
    loadChunks: loader(context.env, context.request.url),
  });
