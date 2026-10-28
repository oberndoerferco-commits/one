// AI Veterinary service worker. Hand-written, no dependencies; docs/29-pwa.md explains it.
//
// The build (pwaAfterBuild in astro.config.mjs) replaces the two placeholders below in dist/sw.js with the
// app-shell file list and a content hash of the built site, so every deploy that changes anything installs a
// new worker with fresh caches. Unbuilt (public/sw.js, `astro dev`) the worker is never registered.
//
// Privacy: this worker only ever stores GET responses from this origin (pages, styles, scripts, fonts, the
// search index). The health booklet lives in the page's localStorage; the worker never reads it, never sends
// anything anywhere, and does not touch requests to other origins (the optional account sync goes straight to
// the network).
const VERSION = '__PWA_VERSION__';
const PRECACHE = /* __PWA_PRECACHE__ */ [];

const SHELL = `aiv-shell-${VERSION}`;      // app shell, installed up front, replaced on every deploy
const ASSETS = `aiv-assets-${VERSION}`;    // styles, scripts, fonts, images, data: cache-first
const SEARCH = `aiv-pagefind-${VERSION}`;  // /pagefind/*: stale-while-revalidate
const PAGES = 'aiv-pages';                 // pages the user opened: network-first, kept across deploys
const KEEP = [SHELL, ASSETS, SEARCH, PAGES];
const MAX_PAGES = 80, MAX_ASSETS = 250, MAX_SEARCH = 400;
const NAV_TIMEOUT = 6000; // on a very slow connection, show the saved copy instead of waiting longer

const langOf = (path) => (/^\/(it|de)(\/|$)/.exec(path)?.[1] ?? 'en');
const offlineUrl = (path) => ({ en: '/offline', it: '/it/offline', de: '/de/offline' })[langOf(path)];
// Pages are static: the query string never changes the HTML, so one copy per path.
const pageKey = (url) => url.origin + (url.pathname.replace(/\.html$/, '').replace(/(.)\/$/, '$1') || '/');

// A response that went through a redirect cannot answer a navigation in some browsers (Safari): copy it.
async function clean(res) {
  if (!res.redirected) return res;
  const body = await res.blob();
  return new Response(body, { status: res.status, statusText: res.statusText, headers: res.headers });
}
const cacheable = (res) => res && res.ok && res.type === 'basic' && !/no-store/.test(res.headers.get('Cache-Control') || '');

async function trim(name, max) {
  const cache = await caches.open(name);
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL);
    // cache: 'reload' skips the HTTP cache, so the shell is exactly this deploy's files.
    await Promise.all(PRECACHE.map(async (path) => {
      const res = await fetch(new Request(path, { cache: 'reload', credentials: 'same-origin' }));
      if (!res.ok) throw new Error(`precache ${path}: ${res.status}`);
      await cache.put(path, await clean(res));
    }));
    // No skipWaiting here: the new version waits until the user accepts the "new version" notice
    // (or every tab is closed), so a page is never swapped under someone filling in the booklet.
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    // Pages saved for offline reading may still point at the previous deploy's hashed files
    // (/_astro/*.css|js|woff2, immutable by name): carry those over before dropping the old caches.
    const assets = await caches.open(ASSETS);
    for (const name of names) {
      if (!name.startsWith('aiv-') || KEEP.includes(name)) continue;
      if (name.startsWith('aiv-shell-') || name.startsWith('aiv-assets-')) {
        const old = await caches.open(name);
        for (const req of await old.keys()) {
          if (!new URL(req.url).pathname.startsWith('/_astro/') || (await assets.match(req))) continue;
          const res = await old.match(req);
          if (res) await assets.put(req, res);
        }
      }
      await caches.delete(name);
    }
    await trim(ASSETS, MAX_ASSETS);
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

async function fromCache(key) {
  return (await caches.match(key, { ignoreSearch: true })) || undefined;
}

// Pages: network first, then the copy saved on an earlier visit (or in the shell), then the offline page.
async function page(event, url) {
  const key = pageKey(url);
  const saved = await fromCache(key);
  const network = fetch(event.request).then(async (res) => {
    if (cacheable(res) && !res.redirected) {
      const copy = res.clone();
      event.waitUntil(caches.open(PAGES).then((c) => c.put(key, copy)).then(() => trim(PAGES, MAX_PAGES)));
    }
    return res;
  });
  try {
    if (!saved) return await network;
    const timeout = new Promise((resolve) => setTimeout(() => resolve(saved), NAV_TIMEOUT));
    event.waitUntil(network.catch(() => {}));
    return await Promise.race([network, timeout]);
  } catch {
    return saved || (await fromCache(offlineUrl(url.pathname))) || new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  }
}

// Static files: the shell or the asset cache first; otherwise fetch and keep a copy.
async function asset(event) {
  const hit = await caches.match(event.request);
  if (hit) return hit;
  const res = await fetch(event.request);
  if (cacheable(res)) {
    const copy = res.clone();
    event.waitUntil(caches.open(ASSETS).then((c) => c.put(event.request, copy)).then(() => trim(ASSETS, MAX_ASSETS)));
  }
  return res;
}

// Search index: answer from the cache at once when possible and refresh it in the background.
async function search(event) {
  const cache = await caches.open(SEARCH);
  const hit = await cache.match(event.request);
  const network = fetch(event.request).then((res) => {
    if (cacheable(res)) event.waitUntil(cache.put(event.request, res.clone()).then(() => trim(SEARCH, MAX_SEARCH)));
    return res;
  });
  if (hit) { event.waitUntil(network.catch(() => {})); return hit; }
  return network;
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // Only same-origin GETs. POSTs, other origins (account sync, analytics) and partial requests pass through untouched.
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname === '/sw.js' || url.pathname.startsWith('/ocr/')) return; // the OCR engine (~10 MB) is not stored
  if (req.mode === 'navigate') { event.respondWith(page(event, url)); return; }
  if (url.pathname.startsWith('/pagefind/')) { event.respondWith(search(event)); return; }
  event.respondWith(asset(event));
});
