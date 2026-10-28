# AI Veterinary PIMS helper (browser extension, prototype)

Pastes an **approved** AI Veterinary record into the S, O, A and P boxes of a
practice management system (PIMS) in the browser, after checking that the PIMS
shows the same patient. Manifest V3, Chromium first; Firefox 128+ should work
but has not been tried. UI in English, Italian and German (`_locales/`).

## Load it unpacked

```sh
cd extension
node build.mjs            # bundles src/*.ts into dist/ (uses the app's esbuild)
```

- **Chrome / Edge:** open `chrome://extensions`, switch on *Developer mode*,
  click *Load unpacked*, choose the `extension/` folder.
- **Firefox:** open `about:debugging#/runtime/this-firefox`, *Load Temporary
  Add-on*, choose `extension/manifest.json`.

Try it on the test page: `cd extension/test && python3 -m http.server 8765`,
then open `http://localhost:8765/fake-pims.html` (`?patient=Max` or
`?species=Katze` to see a blocked paste).

## How it is used

1. In the workspace, approve the record, then click **Copy for the browser
   helper** (next to *Download JSON with approval details*). This copies the same
   JSON as the download, from `app/src/export.ts`.
2. In the PIMS tab, click the extension icon and paste the JSON into the box
   (Ctrl+V), or click *Read clipboard*; the browser then asks once for clipboard
   access. The popup shows the patient, version and approver, or why it refuses.
3. **Map the fields, once per site.** Click *Map fields (click to pick)*. A
   banner on the page asks you to click, in order: the element showing the
   patient name, the element showing the species, then the S, O, A and P text
   boxes. While picking, your clicks go to the extension only, so no PIMS button
   fires. S/O/A/P must be multi-line text boxes (a `textarea` or an editable
   area). The mapping is stored in `chrome.storage.local` under the site's
   origin (for example `https://pims.example.com`), as CSS selectors: a unique
   id, a unique `name`, or a short element path. *Map again* or *Forget this
   site* replace it.
4. Click **Check patient and paste**. The extension reads the name and species
   from the mapped elements and compares them with the export:
   - the name must be identical apart from upper/lower case and spaces;
   - the species must be one of a fixed list of words for the export's species
     (`dog`: dog, canine, Hund, Hündin, Rüde, cane, cagna...; see
     `SPECIES_WORDS` in `src/core.ts`). Species *other* cannot be checked, so
     it is always blocked.

   On any mismatch nothing is pasted and the only button is *Cancel*. There is
   no override: open the right patient in the PIMS. It also stops, without
   pasting anything, if a mapped element is missing or a box already has text
   (it never overwrites).
5. Otherwise it fills the four boxes with the approved text exactly as
   exported: the native value setter, then `input` and `change` events, so
   React, Angular and Vue forms register the value. It never submits, clicks or
   presses keys. A summary (popup and page banner) lists which section went
   into which element and whether the box kept the text unchanged. **You check
   and save in the PIMS.**

## What "approved and not tampered" means here

The export format has **no signature**, and none was added. The extension
re-checks what the format carries, again in the page right before pasting:

- `format` is `aiveterinary.export/1`; `approved_by`, `approved_at`
  (a date), `version` ≥ 1, `ai_assisted: true`, `content_added_by_ai: 0` and a
  `fingerprint` are present; an amendment (`supersedes` set) has its reason;
- the record still gives the approval **fingerprint**, using the app's own
  function (`app/src/versions.ts`, FNV-1a over stable JSON);
- the four S/O/A/P texts are exactly what `soapFields()` in `app/src/export.ts`
  produces from that record (in EN, DE or IT), so an edited paste text is
  refused;
- the patient header has a name and a known species, and agrees with the
  record's own patient name/species when the record has them.

Limits of these checks: the fingerprint is a change-detection hash, not a
signature. Anyone who edits the record can recompute it (`versions.ts` says
so: tamper evidence comes from append-only storage on the server). The
patient header and the values the vet typed at approval
(`resolutions_at_approval`) are outside the fingerprint. The approved records
in the eval set never carry a patient name, so in practice an edited header is
not detected. The checks catch accidental edits and a draft pasted by mistake,
not a deliberate forgery. Real protection needs a signed export from the
server, once one exists. The export has no patient ID field either, so the lock
uses name and species only. A clinic number or microchip would make it much
stronger.

## Privacy

- **No network requests.** The code has no fetch, XHR, WebSocket or remote URL,
  and the extension pages' CSP sets `connect-src 'none'`. The end-to-end test
  intercepts every request and finds none from the extension.
- **Nothing leaves the browser.** The record is held only in the open popup and
  the page. It is never stored. The only thing stored (`chrome.storage.local`,
  this browser only) is the per-site mapping: selectors, no clinical text.
- **Minimal permissions:** `activeTab`, `scripting` and `storage`, plus
  `clipboardRead` as an *optional* permission that is requested only when you
  click *Read clipboard*. There are no host permissions, no background script
  and no content script declared in the manifest. Code is injected into the
  current tab only when you click *Map* or *Paste*.

## Tests

```sh
cd extension
npm test                 # vitest (app's): verification, patient check, locales, manifest, no network APIs
npm run test:e2e         # builds, then Playwright with the unpacked extension in headless Chromium
```

The end-to-end test loads a copy of the extension that has a fixed key and a
host permission for the fake page. Playwright cannot click the toolbar button,
which is what grants `activeTab` in real use, and the popup is told the target
tab with `?tab=`. It covers: picking the six elements by click (a non-text-box
pick is refused), pasting into all four boxes including the React-like
controlled one (whose component state must take the value; a naive
`el.value =` is shown to be wiped), no submit, a different name or species
blocked with only *Cancel*, no overwrite of existing text, unapproved and
edited exports refused in the popup and again in the page, and no network
requests. Clipboard reading is not covered, because the permission prompt
cannot be automated.

`test/fixtures/approved-luna.json` is built by `test/fixture.ts` with the app's
code, and a unit test fails if it no longer matches what the app exports.

## Limits

- **Untested on real PIMS.** Vetera, easyVET, VET7, Provet Cloud, dr.veto and
  others have not been tried. Rich-text editors (iframes, ProseMirror,
  CKEditor) may not take a plain `innerText` value. The summary then marks the
  box as changed, but it is not guaranteed. Generated ids (for example `:r3:`)
  or layout changes break the stored selectors, and you have to map again.
  Elements inside iframes or shadow DOM cannot be picked.
- The patient check needs elements that hold **just** the name and **just** the
  species. A header like "Luna (Rossi)" in one element will always block.
- **Chrome Web Store** (and Firefox Add-ons) publication needs the owner's
  developer account, a store listing and the privacy disclosures above. Until
  then, it can only be loaded unpacked.
- No icons yet. The browser shows a default letter icon.
