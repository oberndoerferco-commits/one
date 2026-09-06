#!/usr/bin/env python3
"""About us (page.about-us.json): the story, built around the journey.

Owner's brief, 6 September: the story is that we travelled through Italy to learn from the
artisans and to learn what real Italian craftsmanship is; what we care about is the heritage
behind it, the quality, and the attention to detail; and we want to stand behind those values
before mass production makes them disappear. Not built around the founders. Longer, and more
relatable.

Text only. Every photograph on the page stays exactly where the owner put it. New chapters are
text sections cloned from the opening band. Re-runnable.
"""
import json, copy

def load(f):
    s = open(f).read(); i = s.index("\n{") + 1
    return s[:i], json.loads(s[i:])
def save(f, h, d):
    open(f, "w").write(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def find(blocks, key):
    if key in blocks: return blocks[key]
    for b in blocks.values():
        r = find(b.get("blocks", {}), key)
        if r: return r
def P(*paras): return "".join(f"<p>{p}</p>" for p in paras)

p = "theme/templates/page.about-us.json"; h, d = load(p)
S = d["sections"]

# ---------- 1. the opening band: the journey, and why the house exists ----------
o = S["section_about_open"]
find(o["blocks"], "text_ab_eyebrow")["settings"]["text"] = "<p>The house</p>"
find(o["blocks"], "text_ab_head")["settings"]["text"] = "<h2>It began with a journey through Italy.</h2>"
find(o["blocks"], "text_ab_dek")["settings"]["text"] = P(
    "We went to learn from the artisans who still make leather goods by hand, and to find out what real Italian craftsmanship is when the word is not on a label.",
    "We came back with a standard, and with a reason for the house to exist: to stand behind that way of working before mass production makes it disappear.")

# ---------- 2. the journey chapter, beside the owner's photograph ----------
j = S["section_about_journey"]
find(j["blocks"], "text_craftHead")["settings"]["text"] = "<p>What we learned on the road</p>"
find(j["blocks"], "text_craftBody")["settings"]["text"] = P(
    "We started in the tanneries, family-run, in Italy, France and Germany, where a hide is still judged by hand before it is bought. Then the small workshops around Milan, where a trunk is built rivet by rivet and a bag’s edge is painted and sanded until it reads as one line.",
    "We watched, asked, and were corrected. Then we stayed, and began to work alongside the people who had corrected us. Everything we make is still made with them.")

# ---------- 3. what craftsmanship turned out to be (new chapter) ----------
def band(key, eyebrow, head, *paras, pad=(72, 56)):
    if key not in S:
        S[key] = copy.deepcopy(S["section_about_open"])
    sec = S[key]
    find(sec["blocks"], "text_ab_eyebrow")["settings"]["text"] = f"<p>{eyebrow}</p>"
    find(sec["blocks"], "text_ab_head")["settings"]["text"] = f"<h2>{head}</h2>"
    find(sec["blocks"], "text_ab_dek")["settings"]["text"] = P(*paras)
    sec["settings"]["padding-block-start"], sec["settings"]["padding-block-end"] = pad
    return sec

band("section_about_meaning", "Craftsmanship", "It is not a label. It is a set of habits.",
    "Real Italian craftsmanship turned out to be nothing you could put on a swing tag. It is the hide chosen for the piece rather than the price. It is the stitch that holds on its own, without glue behind it. It is the hour spent on an edge that most people will never look at.",
    "Three things run through all of it, and they are the three things we care about.")

# ---------- 4. the three values, in the facts row ----------
f = S["section_about_facts"]
find(f["blocks"], "text_6pYzpC")["settings"]["text"] = "<p>HERITAGE</p>"
find(f["blocks"], "text_AFybWJ")["settings"]["text"] = P("Methods handed down in the workshops around Milan, from people who learned them from people. A trunk built the way trunks were always built. We did not invent any of it; we went to learn it, and we keep it.")
find(f["blocks"], "text_8JNP4n")["settings"]["text"] = "<p>QUALITY</p>"
find(f["blocks"], "text_LWwGLH")["settings"]["text"] = P("Full-grain hides from family tanneries we have visited. Solid brass, not plated zinc. Linings cut and glued by hand. Nothing that will look tired in five years, and everything we make, we repair.")
find(f["blocks"], "text_y3qQXc")["settings"]["text"] = "<p>ATTENTION TO DETAIL</p>"
find(f["blocks"], "text_rbMHBf")["settings"]["text"] = P("The things you notice on the tenth day, not the first. A stitch count kept even where no one will look. A lock that closes with the right sound. An edge that is one line, not three.")

# ---------- 5. why it matters now (new chapter) ----------
band("section_about_why", "Why now", "The workshops are fewer every year.",
    "Much of what is sold as Italian leather today is made quickly, in volume, far from the hands it is named after. The workshops that still do it the slow way are small, and there are fewer of them each year. When one closes, what it knew closes with it.",
    "We work with them, pay for the time a thing takes, and make in small numbers so that it stays worth their while. That is not a marketing position. It is the point of the house.")

# ---------- 6. how a piece is made (new chapter, before Sanremo) ----------
band("section_about_making", "The making", "Every piece passes through the same hands.",
    "The hide first: chosen by eye and hand at the tannery, then cut so that the grain runs the way the piece will be used.",
    "The edges next: painted, dried and sanded, then painted again, until the layers read as a single line.",
    "The stitching: stitched by hand where the piece takes its strain, so a thread that wears can be replaced without the seam giving way.",
    "The hardware last: solid brass, galvanised in gold, palladium or black. It is the part you touch every day, so it is the part we refuse to save money on.")

# ---------- 7. the close ----------
find(S["section_about_close"]["blocks"], "text_close01")["settings"]["text"] = "<p>Made the old way, in small numbers, for people who notice the difference.</p>"

# ---------- order ----------
want = ["main", "hero_H8KLYr", "section_about_open", "section_about_journey", "section_about_meaning",
        "section_dpgtkK", "section_about_facts", "section_about_why", "media_with_content_a7znjk",
        "section_about_making", "section_about_bridge", "house_facts", "section_about_close"]
assert set(want) == set(d["order"]) | {"section_about_meaning", "section_about_why", "section_about_making"}, set(d["order"])
d["order"] = want
save(p, h, d)
print("about pass done")
