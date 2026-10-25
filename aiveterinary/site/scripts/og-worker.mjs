// Worker for scripts/og-render.mjs: renders its share of the cards into the cache, then reports back.
import { workerData, parentPort } from 'node:worker_threads';
import { renderTo } from './og-render.mjs';

for (const { card, file } of workerData) await renderTo(card, file);
parentPort.postMessage(workerData.length);
