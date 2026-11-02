"""Ready-to-wear search demand from Google autocomplete (owner, 2 November).

Two signals per market (US/UK English, Germany, Italy):
- expansions: what Google suggests after a seed (what people actually type),
- prefix rank: the shortest prefix at which a phrase is suggested; the earlier it shows, the more it is searched.
Google Trends and Keyword Planner are not reachable from here, so these are relative signals, not volumes.
usage: python3 autocomplete-rtw.py OUT.json
"""
import json, sys, time, urllib.parse, urllib.request
def sug(q, hl, gl):
    u = "https://suggestqueries.google.com/complete/search?client=firefox&hl=%s&gl=%s&q=%s" % (hl, gl, urllib.parse.quote(q))
    for i in range(3):
        try:
            with urllib.request.urlopen(u, timeout=20) as r:
                return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:
            time.sleep(2 + 2 * i)
    return []
def prefix_rank(phrase, hl, gl):
    for n in range(2, len(phrase) + 1):
        p = phrase[:n]
        if phrase[n - 1] == " ": continue
        s = sug(p, hl, gl); time.sleep(0.25)
        if phrase in [x.lower() for x in s]:
            return n, s.index(next(x for x in s if x.lower() == phrase)) + 1
    return None, None

M = {
 "en-us": ("en", "us"), "en-gb": ("en", "gb"), "de": ("de", "de"), "it": ("it", "it")}
SEEDS = {
 "en": ["italian streetwear", "made in italy hoodie", "made in italy clothing", "italian clothing brands", "luxury hoodie",
        "luxury streetwear", "heavyweight hoodie", "blackletter hoodie", "gothic letter hoodie", "half zip", "quarter zip",
        "wide leg joggers", "wide leg sweatpants", "embroidered beanie", "luxury beanie", "check jacket", "luxury t shirt",
        "heavyweight t shirt", "old money", "quiet luxury", "monogram hoodie", "navy tracksuit", "matching sweatsuit"],
 "de": ["italienische mode", "italienische modemarken", "streetwear marken", "luxus hoodie", "hoodie made in italy",
        "half zip pullover", "troyer herren", "jogginghose weites bein", "jogginghose herren", "mütze", "beanie mütze",
        "oversized t shirt", "schweres t shirt", "jogginganzug herren", "old money"],
 "it": ["streetwear italiano", "brand streetwear italiani", "marchi streetwear", "felpa made in italy", "felpa con cappuccio",
        "felpa mezza zip", "pantaloni tuta", "pantaloni tuta larghi", "berretto", "cuffia", "tuta uomo", "t shirt oversize",
        "old money"],
}
PROBE = {  # phrase -> markets to prefix-rank (relative popularity)
 "en-us": ["italian streetwear", "italian clothing brands", "made in italy clothing", "luxury hoodie", "luxury streetwear",
           "heavyweight hoodie", "quarter zip", "half zip", "wide leg sweatpants", "wide leg joggers", "embroidered beanie",
           "heavyweight t shirt", "luxury t shirt", "quiet luxury", "old money outfits", "matching sweatsuit"],
 "de": ["italienische modemarken", "streetwear marken", "luxus hoodie", "half zip pullover", "troyer herren",
        "jogginghose weites bein", "beanie mütze", "schweres t shirt", "oversized t shirt", "jogginganzug herren"],
 "it": ["streetwear italiano", "brand streetwear italiani", "felpa mezza zip", "pantaloni tuta larghi", "felpa con cappuccio",
        "t shirt oversize", "cuffia uomo", "tuta uomo"],
}
out = {"expansions": {}, "prefix_rank": {}}
for lang, seeds in SEEDS.items():
    mkts = ["en-us", "en-gb"] if lang == "en" else [lang]
    for m in mkts:
        hl, gl = M[m]
        for s in seeds:
            out["expansions"].setdefault(m, {})[s] = sug(s, hl, gl); time.sleep(0.25)
for m, phrases in PROBE.items():
    hl, gl = M[m]
    for p in phrases:
        n, pos = prefix_rank(p, hl, gl)
        out["prefix_rank"].setdefault(m, {})[p] = {"chars_typed": n, "position": pos, "of_length": len(p)}
        print(m, p, n, pos, flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
