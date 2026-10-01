# Klaviyo emails

`emails.mjs` holds the six emails (three welcome notes, two checkout follow-ups, the monthly
letter template) as content; `layout.mjs` is the shared frame in the house style. `node
build.mjs` writes them to `out/*.html` and, with `KLAVIYO_API_KEY` set, creates or updates the
templates in Klaviyo by name and writes `out/template-ids.json`. `node preview.mjs` renders
`out/*.png` with sample values for review. Nothing here sends an email: flows are created
switched off and the owner turns them on in Klaviyo.
