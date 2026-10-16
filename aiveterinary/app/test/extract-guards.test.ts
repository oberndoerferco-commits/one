import { describe, it, expect } from 'vitest';
import { SpendGuard, SpendLimitReached, Limiter, costUsd, ClaudeExtractor } from '../src/extract.js';

describe('extractor guards', () => {
  it('prices a call from its usage, cache reads at a tenth', () => {
    expect(costUsd('claude-opus-5-5', { input_tokens: 1_000_000, output_tokens: 0 })).toBeCloseTo(4);
    expect(costUsd('claude-opus-5-5', { input_tokens: 0, output_tokens: 1_000_000 })).toBeCloseTo(20);
    expect(costUsd('claude-opus-5-5', { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 1_000_000 })).toBeCloseTo(0.2);
  });
  it('refuses new calls once the limit is reached', () => {
    const g = new SpendGuard(0.01);
    g.assertRoom(); g.add('claude-opus-5-5', { input_tokens: 2000, output_tokens: 200 });
    expect(g.spentUsd).toBeCloseTo(0.012); expect(() => g.assertRoom()).toThrow(SpendLimitReached);
  });
  it('the extractor checks the limit before importing the SDK or calling anything', async () => {
    const x = new ClaudeExtractor('claude-opus-5-5', { maxUsd: 0 });
    await expect(x.extract({ notes: 'T 38.5', header: { name: 'A', species: 'dog' } })).rejects.toThrow(SpendLimitReached);
  });
  it('keeps at most N requests in flight', async () => {
    const l = new Limiter(2); let now = 0, peak = 0;
    const job = () => l.run(async () => { now++; peak = Math.max(peak, now); await new Promise((r) => setTimeout(r, 10)); now--; });
    await Promise.all([job(), job(), job(), job(), job()]);
    expect(peak).toBe(2);
  });
});
