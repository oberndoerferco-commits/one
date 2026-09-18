#!/usr/bin/env python3
"""
Generate images through OpenAI (ChatGPT) or Google (Gemini) from the command line.

This is the bridge that lets Claude Code call ChatGPT and Gemini for imagery.
Claude runs it through Bash; you can run the same command yourself.

Setup
-----
    export OPENAI_API_KEY=sk-...        # platform.openai.com/api-keys
    export GEMINI_API_KEY=...           # aistudio.google.com/apikey

Examples
--------
    # Text to image, OpenAI
    scripts/genimage.py --prompt "a black leather valet tray on oak" --out shot.png

    # Image to image: restage a real product photo (repeat --ref up to 10x)
    scripts/genimage.py \
        --ref https://cdn.shopify.com/.../obm-lane-tray-black.jpg \
        --prompt "Same tray, unchanged. Relight on a marble sill, morning light." \
        --out tray-black-marble.png

    # Same brief through Gemini, for comparison
    scripts/genimage.py --provider gemini --prompt "..." --out gemini.png

    # Show the request without spending anything
    scripts/genimage.py --prompt "..." --dry-run
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import re
import sys
import time

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("This script needs the 'requests' package:  pip install requests")


OPENAI_BASE = "https://api.openai.com/v1"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

DEFAULT_OPENAI_MODEL = "gpt-image-2"
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-image"

# size -> aspect ratio, for providers that take a ratio rather than pixels
RATIOS = {
    "1024x1024": "1:1",
    "1536x1024": "3:2",
    "1024x1536": "2:3",
    "1792x1024": "16:9",
    "1024x1792": "9:16",
    "auto": "1:1",
}

IMAGE_MAGIC = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"RIFF", "webp"),
    (b"GIF8", "gif"),
)

MAX_REFS = 10
TIMEOUT = 300


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def load_ref(ref: str) -> tuple[str, bytes, str]:
    """Return (filename, bytes, mimetype) for a local path or an http(s) URL."""
    if ref.startswith(("http://", "https://")):
        resp = requests.get(ref, timeout=60)
        resp.raise_for_status()
        name = os.path.basename(ref.split("?", 1)[0]) or "reference.png"
        mime = resp.headers.get("content-type", "").split(";")[0].strip()
        if not mime.startswith("image/"):
            mime = mimetypes.guess_type(name)[0] or "image/png"
        return name, resp.content, mime

    path = pathlib.Path(ref).expanduser()
    if not path.is_file():
        raise SystemExit(f"reference not found: {ref}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return path.name, path.read_bytes(), mime


def sniff_ext(blob: bytes) -> str:
    for magic, ext in IMAGE_MAGIC:
        if blob.startswith(magic):
            return ext
    return "png"


def looks_like_image(blob: bytes) -> bool:
    return any(blob.startswith(magic) for magic, _ in IMAGE_MAGIC)


def harvest_images(payload) -> list[bytes]:
    """Walk an arbitrary JSON response and pull out every base64 image it holds.

    Providers keep moving these fields around between API versions, so we look
    for any base64 string that decodes to something with image magic bytes
    rather than hardcoding one path through the response.
    """
    found: list[bytes] = []

    def visit(node) -> None:
        if isinstance(node, dict):
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
        elif isinstance(node, str) and len(node) > 512:
            candidate = node
            # tolerate data: URLs and url-safe base64
            if candidate.startswith("data:"):
                candidate = candidate.split(",", 1)[-1]
            if not re.fullmatch(r"[A-Za-z0-9+/_\-\s]*={0,2}", candidate):
                return
            try:
                blob = base64.b64decode(candidate + "=" * (-len(candidate) % 4),
                                        altchars=b"-_" if "-" in candidate or "_" in candidate else None)
            except Exception:
                return
            if looks_like_image(blob):
                found.append(blob)

    visit(payload)
    return found


def write_images(blobs: list[bytes], out: str | None, provider: str) -> list[str]:
    if not blobs:
        raise SystemExit("the API returned no image data (run with --debug to see the response)")

    written: list[str] = []
    if out:
        base = pathlib.Path(out).expanduser()
    else:
        pathlib.Path("generated").mkdir(exist_ok=True)
        base = pathlib.Path("generated") / f"{provider}-{int(time.time())}.png"

    base.parent.mkdir(parents=True, exist_ok=True)

    for index, blob in enumerate(blobs):
        ext = sniff_ext(blob)
        if len(blobs) == 1:
            target = base.with_suffix(base.suffix or f".{ext}")
        else:
            target = base.with_name(f"{base.stem}-{index + 1}{base.suffix or '.' + ext}")
        target.write_bytes(blob)
        written.append(str(target))
    return written


def fail(resp: requests.Response) -> None:
    hint = ""
    if resp.status_code == 401:
        hint = "  (check the API key is set and still valid)"
    elif resp.status_code == 429:
        hint = "  (rate limited, or the account is out of credit)"
    elif resp.status_code == 400:
        hint = "  (often a rejected prompt, or an unsupported size/quality for this model)"
    raise SystemExit(f"{resp.status_code} from the API{hint}\n{resp.text[:2000]}")


# --------------------------------------------------------------------------
# providers
# --------------------------------------------------------------------------

def run_openai(args, refs) -> list[bytes]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key and not args.dry_run:
        raise SystemExit("OPENAI_API_KEY is not set. Get one at platform.openai.com/api-keys")

    model = args.model or DEFAULT_OPENAI_MODEL
    headers = {"Authorization": f"Bearer {key}"}

    if refs:
        url = f"{OPENAI_BASE}/images/edits"
        data = {"model": model, "prompt": args.prompt, "n": str(args.n)}
        if args.size != "auto":
            data["size"] = args.size
        if args.quality != "auto":
            data["quality"] = args.quality

        if args.dry_run:
            log(f"POST {url}\n  multipart fields: {json.dumps(data, indent=2)}")
            log(f"  images: {[name for name, _, _ in refs]}")
            return []

        files = [("image[]", (name, blob, mime)) for name, blob, mime in refs]
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=TIMEOUT)
    else:
        url = f"{OPENAI_BASE}/images/generations"
        body = {"model": model, "prompt": args.prompt, "n": args.n}
        if args.size != "auto":
            body["size"] = args.size
        if args.quality != "auto":
            body["quality"] = args.quality

        if args.dry_run:
            log(f"POST {url}\n{json.dumps(body, indent=2)}")
            return []

        resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)

    if resp.status_code >= 400:
        fail(resp)

    payload = resp.json()
    if args.debug:
        log(json.dumps(payload, indent=2)[:4000])

    blobs: list[bytes] = []
    for item in payload.get("data", []):
        if item.get("b64_json"):
            blobs.append(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            blobs.append(requests.get(item["url"], timeout=120).content)
    return blobs or harvest_images(payload)


def run_gemini(args, refs) -> list[bytes]:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key and not args.dry_run:
        raise SystemExit("GEMINI_API_KEY is not set. Get one at aistudio.google.com/apikey")

    model = args.model or DEFAULT_GEMINI_MODEL
    ratio = RATIOS.get(args.size, "1:1")
    headers = {"x-goog-api-key": key or "", "Content-Type": "application/json"}

    # Current endpoint first, then the older generateContent shape. Google has
    # moved these around; trying both keeps the script working across versions.
    attempts = [
        (
            f"{GEMINI_BASE}/interactions",
            {
                "model": model,
                "input": (
                    [{"type": "text", "text": args.prompt}]
                    + [
                        {"type": "image", "mime_type": mime,
                         "data": base64.b64encode(blob).decode()}
                        for _, blob, mime in refs
                    ]
                ),
                "response_format": {"type": "image", "aspect_ratio": ratio},
            },
        ),
        (
            f"{GEMINI_BASE}/models/{model}:generateContent",
            {
                "contents": [
                    {
                        "parts": (
                            [{"text": args.prompt}]
                            + [
                                {"inline_data": {"mime_type": mime,
                                                 "data": base64.b64encode(blob).decode()}}
                                for _, blob, mime in refs
                            ]
                        )
                    }
                ],
                "generationConfig": {"responseModalities": ["IMAGE"]},
            },
        ),
    ]

    if args.dry_run:
        url, body = attempts[0]
        log(f"POST {url}\n{json.dumps(body, indent=2)[:1500]}")
        return []

    last: requests.Response | None = None
    for url, body in attempts:
        resp = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
        if resp.status_code < 400:
            payload = resp.json()
            if args.debug:
                log(json.dumps(payload, indent=2)[:4000])
            blobs = harvest_images(payload)
            if blobs:
                return blobs
        last = resp
        if resp.status_code in (401, 403, 429):
            break  # auth or quota: the other endpoint will not help

    if last is not None:
        fail(last)
    return []


# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate images via OpenAI (ChatGPT) or Google (Gemini).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--provider", choices=["openai", "gemini"], default="openai")
    parser.add_argument("--prompt", help="the image brief")
    parser.add_argument("--prompt-file", help="read the brief from a file instead")
    parser.add_argument("--ref", action="append", default=[],
                        help="reference image, local path or URL; repeatable")
    parser.add_argument("--out", help="output file (default: generated/<provider>-<ts>.png)")
    parser.add_argument("--size", default="1024x1024",
                        choices=sorted(RATIOS.keys()))
    parser.add_argument("--quality", default="medium",
                        choices=["auto", "low", "medium", "high"])
    parser.add_argument("--model", help="override the model id")
    parser.add_argument("-n", type=int, default=1, help="how many images (OpenAI only)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the request and exit without calling the API")
    parser.add_argument("--debug", action="store_true", help="dump the raw response")
    args = parser.parse_args()

    if args.prompt_file:
        args.prompt = pathlib.Path(args.prompt_file).expanduser().read_text().strip()
    if not args.prompt:
        parser.error("give a brief with --prompt or --prompt-file")

    if len(args.ref) > MAX_REFS:
        parser.error(f"at most {MAX_REFS} reference images")

    refs = [load_ref(r) for r in args.ref]
    if refs:
        log(f"loaded {len(refs)} reference image(s): {', '.join(n for n, _, _ in refs)}")

    runner = run_openai if args.provider == "openai" else run_gemini
    blobs = runner(args, refs)

    if args.dry_run:
        log("dry run: nothing was sent, nothing was spent")
        return

    written = write_images(blobs, args.out, args.provider)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
