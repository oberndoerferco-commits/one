# 29 · Installable app (PWA): offline booklet and emergency check

25 Oct 2026. The site in `site/` can be installed as an app and works offline: the health booklet, the emergency check and any page already read. There is no new dependency; the service worker is written by hand.

## 1. Files

| File | What it does |
|---|---|
| `site/public/sw.js` | The service worker. The build fills in its two placeholders (version, app-shell list). |
| `site/astro.config.mjs` → `pwaAfterBuild()` | Runs after `seoAfterBuild()` in `astro:build:done`. Reads `dist/`, writes the shell list and the version into `dist/sw.js`, and stops the build if a shell page is missing. |
| `site/src/pages/offline.astro`, `it/offline.astro`, `de/offline.astro` + `src/components/Offline.astro` | Offline page per language (noindex): you are offline, links to the booklet and the emergency check, "in an emergency call a vet directly", and a list of pages saved on this device. |
| `site/src/layouts/Base.astro` | Registration script (production builds only, https or localhost), the "new version" notice, the install button in the phone menu, and the install/iOS-hint logic. |
| `site/src/components/Passport.astro` | Install button and the iOS "Share → Add to Home Screen" hint, on the booklet page only. |
| `site/public/manifest.webmanifest` | `id`, `scope`, `start_url: /?source=pwa`, shortcuts. |
| `site/src/pages/privacy.astro` | One line under "Digital pet passport without an account". |

## 2. What is cached

| Cache | Contents | Strategy |
|---|---|---|
| `aiv-shell-<version>` | Installed up front: `/offline`, `/passport`, `/emergency` and the home page, each in EN/IT/DE (12 pages), plus every CSS, JS and font file those pages load, and the icons and manifest. About 28 files, 1.1 MB uncompressed. | Precache at install. |
| `aiv-pages` | Every page the user opens. Kept across deploys, at most 80 pages. | Network first. If the network fails, or takes more than 6 s and a saved copy exists, the saved copy is shown. Otherwise the offline page for the URL's language. |
| `aiv-assets-<version>` | Other same-origin files (styles, scripts, images, `ask-index.json`). | Cache first. The content-hashed `/_astro/*` files of the previous version are carried over on update, so pages saved earlier still have their styles offline. At most 250 entries. |
| `aiv-pagefind-<version>` | `/pagefind/*` search index. | Stale-while-revalidate. |

The shell list is not kept by hand: the build reads the shell pages' HTML for `href`/`src`, then the CSS for `url()` and the JS for imported chunks. Font subsets for other alphabets (Vietnamese, Cyrillic, Greek) are left out. `/can-eat` (220 KB per language) is not in the shell; like any other page it is saved when opened.

**Never cached:** anything that is not a GET (POST and so on), other origins (Supabase account sync, Cloudflare analytics), `Range` requests, `/sw.js`, and `/ocr/` (the 10 MB photo-reading engine; tesseract keeps its language data in IndexedDB itself). Responses marked `no-store` are not stored.

**Privacy.** The booklet lives in the page's `localStorage` (`aiveterinary.passport.v1`). The service worker never reads it and sends nothing anywhere. It stores only what the site itself serves.

## 3. How updates work

1. Each build hashes every file in `dist/` (path and content) into a 12-character version. A deploy that changes anything produces a new `sw.js`, and an identical build produces the same version.
2. The browser finds the new `sw.js` when a page is opened. A booklet left open in a tab also checks when the tab becomes visible again, at most once an hour. The new worker installs its shell in the background, then **waits**. There is no automatic `skipWaiting`.
3. Tabs controlled by the old version show a small notice: "A new version of AI Veterinary is available. Update now · Later". Only "Update now" activates the new worker (`SKIP_WAITING` message) and reloads **that tab**. Other tabs keep working on what they have. Nothing reloads while someone is typing in the booklet, and the booklet's own `pagehide` save runs before the reload.
4. If the user never clicks, the new version takes over the next time all tabs of the site are closed.
5. On activation, caches from older versions are deleted (`aiv-shell-*`, `aiv-assets-*`, `aiv-pagefind-*`). Hashed `/_astro/*` files are carried over first. `aiv-pages` is kept.

Cloudflare Pages serves `sw.js` with `max-age=0, must-revalidate` by default, and browsers skip the HTTP cache for the worker script anyway, so no `_headers` rule is needed.

## 4. Install UI (no pop-ups)

- **Chromium and Android:** `beforeinstallprompt` is caught in `<head>` (this suppresses the browser's own mini-infobar). The page then shows a discreet "Install the app" button in two places: on the booklet page under the privacy ticks, and in the phone menu sheet. After the prompt has been used, the button hides.
- **iOS:** on the booklet page only, a short localized hint, "tap Share, then Add to Home Screen". It can be dismissed with ×, which is remembered in `localStorage` (`aiveterinary.iosInstallHint`, read and written in try/catch).
- **Already installed:** all install UI is hidden when `display-mode: standalone` matches or `navigator.standalone` is true.

**Manifest.** `id: "/"` keeps the app identity the old manifest had (it had no `id`, so the identity was its `start_url` `/`). `start_url: "/?source=pwa"` does not affect canonical or hreflang, because both are written at build time from the path. The service worker ignores the query string for pages. Shortcuts: My booklet (`/passport`), Is it urgent? (`/emergency`), Can my pet eat that? (`/can-eat`).

**Language.** There is a single manifest. Its name, "AI Veterinary", is the brand in every language, but the shortcut labels are English only. Per-language manifests would mean three installs of the same app, and the manifest `translations` member is not supported by browsers yet. No screenshots are included; they are only needed for Chrome's richer install sheet.

## 5. How to test

```sh
cd site && npm run build && npm run check:seo
npx astro preview --port <free port> --host 127.0.0.1   # localhost counts as a secure origin
```

In Chrome DevTools: Application → Service workers, Cache storage, Manifest (installability). Then Network → Offline.

**Automated checks run on 25 Oct 2026** (Playwright 1.56, Chromium). The scripts are in the session scratchpad, not in the repo.

- The worker registers and controls the page. The shell holds 28 entries.
- Offline, in EN/IT/DE: the booklet opens styled, with its data. The emergency check opens. A previously read article opens. An unvisited URL gives the offline page in the right language, which lists the saved pages.
- A booklet edit made offline is saved and survives a reload.
- All cached URLs are same-origin.
- Update: a rebuild with a changed file gives a new version. The notice appears while the user types in the booklet, with no reload. The new worker waits. "Update now" reloads once, the old caches are gone, the new shell holds the changed file, and the booklet data is intact.
- Chromium installability, in a non-incognito profile: no manifest errors, no installability errors, and a real `beforeinstallprompt` fires and shows the button.
- axe-core: 0 violations on the 3 offline pages, the 3 booklet pages and the phone menu sheet, in light and dark, with the install button, the iOS hint and the notice forced visible. No horizontal overflow at 320 px.

**Testing tip:** in Playwright, `context.setOffline(true)` does not reliably reach the service worker's own `fetch()`. Set `PW_EXPERIMENTAL_SERVICE_WORKER_NETWORK_EVENTS=1` and also stop the preview server for the offline phase. Otherwise "unvisited" pages still load from the network. Lighthouse dropped its PWA category in v12, so installability is checked with CDP (`Page.getInstallabilityErrors`) instead.

## 6. Limits

- **Safari storage.** Safari can delete a website's `localStorage` after 7 days without a visit. A home-screen app is exempt. This is one more reason to show the iOS hint on the booklet, and the "Back up" button remains the real safety net.
- The OCR photo import needs a connection the first time it is used.
- Pages read before an update remain offline with their old styles. The search index (`/pagefind`) works offline only for the files already fetched.
- The account sync (Supabase, when configured) is network-only. Edits made offline sync the next time the page is open online, as before.

## 7. Store apps (later)

The PWA is the base for both stores, so no second codebase is needed.

**Google Play: Trusted Web Activity (TWA).** Bubblewrap CLI or PWABuilder wraps the live site in a thin Android app that opens it in Chrome without browser UI.
- Needs `https://aiveterinary.org/.well-known/assetlinks.json` (Digital Asset Links) with the SHA-256 fingerprint of the Play App Signing key. Without it the app shows a URL bar.
- Content updates ship with the website. A new app build is needed only for the manifest, icons or the Android wrapper.
- Owner accounts:
  - A **Google Play Console developer account** (one-time USD 25, identity verification). As an organisation, this also needs a **D-U-N-S number**. A new personal account must run a closed test with 12+ testers for 14 days before going public.
  - The Play **Data safety** form and a privacy-policy URL.

**iOS App Store: Capacitor.** Capacitor wraps the built `dist/` (or the live URL) in a WKWebView app.
- Apple rejects bare website wrappers (App Review Guideline 4.2, minimum functionality). The app should carry native value: an offline booklet bundled in the app, camera scan, and local reminder notifications for vaccine due dates.
- Move the booklet from `localStorage` to Capacitor Preferences or SQLite in the app, so iOS cannot clear it under storage pressure.
- Owner accounts:
  - An **Apple Developer Program** membership (USD 99 per year). As an organisation, this needs a **D-U-N-S number** and a legal entity.
  - An **App Store Connect** app record with privacy "nutrition labels", a privacy-policy URL and a support URL.
  - A **Mac with Xcode** or a cloud macOS build service to build and sign the app.

Both store listings need the controller's name and address. That is the same gap as the `[Company name]` placeholder in the privacy page.
