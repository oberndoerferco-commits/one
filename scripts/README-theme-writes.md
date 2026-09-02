# Writing large theme files without hand-typing them

`themeFilesUpsert` with `body.type = TEXT` means pasting the whole file inline.
For 40–90 KB templates that is slow and easy to get wrong (a dropped line
went unnoticed once). The cheap, exact route:

1. `stagedUploadsCreate` — resource `FILE`, mimeType `application/json`,
   httpMethod `POST`. Returns a target `url`, a `resourceUrl`, and form
   `parameters`.
2. `curl -F <each parameter> -F "file=@local.json;type=application/json" <url>`
   — expect HTTP 201. The staged bucket is reachable from the sandbox even
   though cdn.shopify.com is not.
3. `themeFilesUpsert` with `body: { type: URL, value: <resourceUrl> }`.
   It runs as a background `job`; poll `job(id:) { done }`, then confirm the
   theme file `size` equals the local byte count.

Do **not** route through `fileCreate` — the resulting cdn.shopify.com URL is
silently rejected by the upsert (job completes, nothing written).
