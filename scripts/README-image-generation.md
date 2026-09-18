# Generating imagery with ChatGPT and Gemini

`scripts/genimage.py` is the bridge. Claude Code calls it through Bash, so once
the keys are set Claude can generate product and model imagery directly in a
session. You can run the identical command yourself.

## Setup, once

Two keys. Either one works on its own; set both to compare providers.

```bash
export OPENAI_API_KEY=sk-...   # platform.openai.com/api-keys
export GEMINI_API_KEY=...      # aistudio.google.com/apikey
```

For Claude Code on the web, put these in the environment's variables so they
load on every session. **Never commit them.**

Check it before spending anything:

```bash
scripts/genimage.py --prompt "test" --dry-run
```

## What each provider costs

There is no free OpenAI image API. New accounts get a one-off $5 credit, which
at low quality is several hundred images. Google does have a standing free
tier.

| Provider | Free allowance | Paid, per 1024x1024 image |
| --- | --- | --- |
| OpenAI `gpt-image-2` | $5 one-off credit for new accounts | $0.006 low, $0.053 medium, $0.211 high |
| Google `gemini-3.1-flash-image` | ~500 requests/day on the AI Studio free tier | ~$0.04 |
| Google `gemini-3-pro-image` | not on the free tier | ~$0.13 |

Draft at `--quality low`, then re-run the winner at `high`. Ten low-quality
drafts cost about six cents.

## Usage

```bash
# Text to image
scripts/genimage.py --prompt "..." --out shot.png

# Image to image: restage a real product photo. Repeat --ref up to 10 times.
scripts/genimage.py \
  --ref https://cdn.shopify.com/s/files/.../obm-lane-tray-black.jpg \
  --prompt "Same tray, unchanged. Relight on a marble sill." \
  --size 1536x1024 --quality high --out tray-black-marble.png

# Same brief through Gemini, to compare
scripts/genimage.py --provider gemini --prompt "..." --out gemini.png
```

Useful flags: `--size` (1024x1024, 1536x1024, 1024x1536, 1792x1024, 1024x1792),
`--quality` (low/medium/high), `-n` for several variants, `--model` to override,
`--debug` to dump the raw response, `--dry-run` to print the request and spend
nothing.

`--ref` takes a local path or a URL, so Shopify CDN links work directly. The
CDN is reachable from the sandbox.

## The rule that matters

**Always pass the real product photo with `--ref`.** Text-to-image invents a
watch box that does not exist: wrong hinge, wrong stitch count, wrong
proportions. Selling that is a legal problem, not just an aesthetic one. Use
generation to re-light and re-stage photographs you already own.

Model shots are the exception, since there is no reference to preserve. Keep
generated people well away from any claim about the product itself, and see
the disclosure note in `docs/image-prompt-pack.md`.
