#!/usr/bin/env python3
"""Home (index.json): the two copy blocks the owner disliked, rewritten in the About voice.

Owner, 6 September, on "MADE TO ORDER / Every piece is also a starting point…" and
"THE HOUSE / Made in ateliers around Milan…": "how can we improve writing, i dont like it a lot".
7 September: "recheck writings in the website" after the About story was settled.

Text only. The owner's photographs, layout and every other block on the home page are untouched.
Re-runnable.
"""
import json

def load(f):
    s = open(f).read(); i = s.index("\n{") + 1
    return s[:i], json.loads(s[i:])
def save(f, h, d):
    open(f, "w").write(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def texts(blocks, out):
    for k, b in blocks.items():
        if b["type"] == "text": out[k] = b["settings"]
        texts(b.get("blocks", {}), out)
def P(*paras): return "".join(f"<p>{p}</p>" for p in paras)

p = "theme/templates/index.json"; h, d = load(p)
S = d["sections"]

# ---------- Made to order: what happens after you choose, in the order it happens ----------
t = {}; texts(S["section_PaekVn"]["blocks"], t)
for k, st in t.items():
    x = st["text"]
    if "MADE TO ORDER" in x.upper() and len(x) < 40:
        st["text"] = "<p>MADE TO ORDER</p>"
    elif "starting point" in x or "cut until" in x:
        # one block carries the head and the paragraph; keep whatever tag the head uses
        import re
        m = re.match(r"<(h\d|p)[^>]*>", x); tag = m.group(1) if m else "h2"
        st["text"] = (f"<{tag}>Nothing is cut until it is yours.</{tag}>"
                      + P("Choose the hide, the colour and the lining on a piece you already like, or tell us about a room. It is made after you order it, by the same hands that make everything else, and it takes the time it takes: four to six weeks for a bag or a box, longer for a sofa."))

# ---------- The house: the journey, in three sentences, pointing at About ----------
t = {}; texts(S["media_with_content_REm8Na"]["blocks"], t)
for k, st in t.items():
    x = st["text"]
    if "The house" in x and len(x) < 40:
        st["text"] = "<p>The house</p>"
    elif "ateliers around Milan" in x and len(x) < 80 or "journey through Italy" in x:
        st["text"] = "<p>It began with a journey through Italy.</p>"
    elif "Full-grain hides from family tanneries" in x or "take the word off the label" in x or "learned the trade" in x:
        # 7 September, second pass: the owner's "this text can be improved" on the first version
        st["text"] = P("We went looking for what lies behind the words Made in Italy and found it in small workshops around Milan, with artisans who learned the trade from their grandparents. They make everything we sell, by hand, stud by stud.")

save(p, h, d)
print("home copy pass done")
