"""Rebuild the FAQ and care-guide structured data from the pages' own accordion rows (11 September 2026).

The owner prefers the writing on the live theme, so the search-result answers must be the page's
words and nothing else. Input: the live theme's templates/page.faq.json and
templates/page.leather-care.json (pull them from the theme first). Output: the two snippets in
theme/snippets/, ready to upload. All-capital rows are set in sentence case so the results read
normally; a short list of proper nouns keeps their capitals.
"""
import json, re, html, sys

PROPER = ["DHL Express", "DHL", "Oberndörfer Milano", "Oberndörfer", "Italy", "Italian", "Milan", "Milano",
          "Europe", "CITES", "Sanremo", "New York", "France", "Germany"]

def load(n):
    raw = open(n).read(); m = re.match(r"^\s*/\*.*?\*/\s*", raw, flags=re.S)
    return json.loads(raw[m.end():] if m else raw)

def clean(s):
    s = re.sub(r"<(br|/li|/p|/h[1-6]|/div)[^>]*>", " ", s); s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"\s*:\s*(?=[A-Za-z])", ": ", s); s = re.sub(r"\s+", " ", s).strip()
    letters = [c for c in s if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.8:
        s = s.lower(); s = re.sub(r"(^|[.!?]\s+)([a-zà-ÿ])", lambda m: m.group(1) + m.group(2).upper(), s)
        for p in PROPER: s = re.sub(re.escape(p), p, s, flags=re.I)
        s = re.sub(r"\bi\b", "I", s)
    return s

def rows(t):
    out = []
    def walk(bl):
        for b in bl.values():
            if b["type"] == "_accordion-row":
                q = clean(b["settings"].get("heading", ""))
                a = " ".join(clean(c["settings"].get("text", "")) for c in b.get("blocks", {}).values() if c["type"] == "text")
                if q and a: out.append((q, a))
            walk(b.get("blocks", {}))
    for s in t["sections"].values(): walk(s.get("blocks", {}))
    return out

def snippet(name, page_handle, qa, note):
    L = ["{% comment %}", f"  Oberndoerfer Milano - FAQPage structured data for /pages/{page_handle} (11 September 2026).",
         f"  {note}", "  Rendered from snippets/meta-tags.liquid. Nothing here is visible on the page.", "{% endcomment %}", "{%- liquid"]
    for i, (q, a) in enumerate(qa, 1):
        L.append(f"  assign q{i} = {json.dumps(q, ensure_ascii=False)}"); L.append(f"  assign a{i} = {json.dumps(a, ensure_ascii=False)}")
    L += ["-%}", '<script type="application/ld+json">', '  {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [']
    for i in range(1, len(qa) + 1):
        L.append(f'    {{"@type": "Question", "name": {{{{ q{i} | json }}}}, "acceptedAnswer": {{"@type": "Answer", "text": {{{{ a{i} | json }}}}}}}}' + ("," if i < len(qa) else ""))
    L += ["  ]}", "</script>"]
    open(name, "w").write("\n".join(L) + "\n"); print(name, len(qa), "questions")

src = sys.argv[1] if len(sys.argv) > 1 else "."
snippet("theme/snippets/oberndoerfer-faq-schema.liquid", "faq", rows(load(f"{src}/page.faq.json")),
        "The questions and answers are the page's own accordion rows, word for word (all-capital rows set in sentence case so the results read normally). Edit the page and re-run scripts/seo-schemas.py to refresh.")
snippet("theme/snippets/oberndoerfer-care-schema.liquid", "leather-care-guide", rows(load(f"{src}/page.leather-care.json")),
        "The questions and answers are the page's own accordion rows, word for word. Edit the page and re-run scripts/seo-schemas.py to refresh.")
