# Working notes for Claude

This repo holds the owner's Shopify theme (`theme/`) and client work such as product-photo sets
(`product-photos/<client>/`, logos in `brand/`). Client work never goes to the owner's own Shopify
store unless explicitly asked.

## Quality bar

- **Every image must be perfect.** Check each output at full size before showing it: leftover
  background, halos, specks/lint, tilt, colour cast, cut-off parts. "Mostly clean" is not done.
- **Consistency across a set:** one background, one framing, the same angle for the main image of
  every colour, matching brightness/colour of the same product across photos.
- **Real over fake.** Prefer a real photo of each colourway over recolouring when the material
  (e.g. patent gloss) cannot be reproduced convincingly. Say so instead of shipping a weaker fake.
- **Show choices, let the owner pick.** For selections, send numbered contact sheets
  (before/now, option A/B) early; the owner marks them up. Don't guess taste.
- **Product copy = facts only.** No marketing fluff, no mentions of image counts or UI internals.

## Photo job standard (do this every time)

1. **Full resolution is the default.** Ask for the camera originals (e.g. 24 MP HEIC/JPEG) at the
   start. Never build a set from phone/web-size copies (1920 px) without flagging it first.
2. **Inventory before editing:** download, de-duplicate by file hash (Drive exports often contain
   `IMG_x 2.JPG` / `IMG_x (1).JPG` copies), list what views exist per product/colour, and report
   gaps (e.g. "no open view of the pink clutch") before starting.
3. **Agree the structure first:** `product/colour/NN-view.jpg`, `01` = main image; confirm main-image
   angle and gallery order in one message, then build.
4. **Deliver:** 2048 × 2048 sRGB JPEG q95, no chroma subsampling; stone `#EDEAE4` (+ white version on
   request); an `_overview.jpg` contact sheet; README with source IMG numbers.

## Working within the container's limits (avoid crashes and long waits)

The cloud container has ~16 GB RAM, 4 CPUs, no GPU. Plan jobs around that instead of discovering it:

- **Background removal (rembg/BiRefNet):** run in ONE long-lived process that loads the model once;
  never several model processes in parallel (each takes 6–9 GB → OOM kills). Feed the model a
  ≤1600 px copy and upscale the mask to full size. Use `birefnet-general-lite` for bulk
  (~10 s/image); the full model only for hard cases. Cache masks to disk so reruns are free.
- **Process in batches of ~10–20 images** with progress written to a log, so a crash loses little
  and the owner can be told real progress. Before a job that takes >5 min, state the estimate.
- **Downloads:** list folder contents first (`gdown ... skip_download=True`), download only new
  files, 8 in parallel. Don't serial-download hundreds of duplicates.
- **Automatic background swaps on close-ups are risky** (they eat into leather/lining). Use a
  product mask AND a colour check, keep only background connected to the image border, and
  visually inspect every result; fall back to a tight crop that contains no background.

## Known tool limits (tell the owner up front)

- Cannot read the owner's computer (Desktop/Downloads) — this runs in the cloud.
- Google Drive connector here cannot list the owner's files; reading works via a public share
  link + `gdown`. It cannot upload large binaries — deliver zips instead.
- Files sent in chat are capped at 30 MB → split zips by product.
- No Dropbox connector unless the owner connects one.
