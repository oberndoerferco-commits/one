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
    "We set out with one question: what does Italian craftsmanship actually mean, once you take the word off the label? To find out, we went to the people who still practise it, leather artisans who learned the craft from their grandparents, and began to watch what really lies behind the words Made in Italy.",
    "What they showed us became the house. Not a brand built around a name, but a way of working we could see was worth keeping, and a promise to keep it before mass production makes it disappear.")

# ---------- 2. the journey chapter, beside the owner's photograph ----------
j = S["section_about_journey"]
find(j["blocks"], "text_craftHead")["settings"]["text"] = "<p>What we learned on the road</p>"
find(j["blocks"], "text_craftBody")["settings"]["text"] = P(
    "The journey began at the tanneries, family-run, in Italy, France and Germany, where a hide is still turned over and judged by hand before anyone agrees a price. It ended in the small workshops around Milan, where a trunk is built stud by stud and a bag is cut, stitched and finished by the same pair of hands.",
    "In between we watched, we asked, and we learned. When the journey was over we stayed, and began working alongside the people who had taught us. They still make everything we sell.")

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
    "Because that is what craftsmanship turned out to be: nothing you could print on a swing tag, but a hundred small decisions made the same way every time. The hide chosen for the piece rather than the price. The stitch that holds on its own, with no glue behind it. The hour spent on an edge most people will never look at.",
    "Underneath those decisions we kept finding the same three things, and they became the three things this house stands for.")

# ---------- 4. the three values, in the facts row ----------
f = S["section_about_facts"]
find(f["blocks"], "text_6pYzpC")["settings"]["text"] = "<p>HERITAGE</p>"
find(f["blocks"], "text_AFybWJ")["settings"]["text"] = P("The methods came to us from people who learned them from people, in workshops that have been doing this for longer than we have been alive. We invented none of it. We went to learn it, and we keep it.")
find(f["blocks"], "text_8JNP4n")["settings"]["text"] = "<p>QUALITY</p>"
find(f["blocks"], "text_LWwGLH")["settings"]["text"] = P("Full-grain hides from tanneries we have stood in. Solid brass where others use plated zinc. Linings cut and glued by hand. Nothing that will look tired in five years, and whatever we make, we repair.")
find(f["blocks"], "text_y3qQXc")["settings"]["text"] = "<p>ATTENTION TO DETAIL</p>"
find(f["blocks"], "text_rbMHBf")["settings"]["text"] = P("The things you notice on the tenth day, not the first: a stitch count kept even where no one will look, a lock that closes with the right sound, an edge that reads as one line rather than three.")

# ---------- 5. why it matters now (new chapter) ----------
band("section_about_why", "Why now", "The workshops are fewer every year.",
    "Those habits are the reason the house exists, and the reason it exists now. Much of what is sold as Italian leather today is made quickly and in volume, far from the hands it is named after. The workshops that still do it slowly are small, and each year there are fewer. When one closes, what it knew closes with it.",
    "So we work with them, pay for the time a thing takes, and make in small numbers so that it stays worth their while. That is not a marketing position. It is the point of the house.")

# ---------- 6. how a piece is made (new chapter, before Sanremo) ----------
band("section_about_making", "The making", "Every piece passes through the same hands.",
    "What that looks like, piece by piece: the hide is chosen by eye and by hand at the tannery, then cut so the grain runs the way the piece will be used, with nothing wasted that could have been a smaller piece.",
    "The seams that take the strain are stitched by hand, so a thread that wears one day can be replaced without the seam giving way. The hardware comes last: solid brass, galvanised in gold, palladium or black. It is the part you touch every day, so it is the part we refuse to save money on.")

# ---------- 6b. Sanremo: a bridge from the making to the room ----------
b = find(S["section_about_bridge"]["blocks"], "text_craftBody")["settings"]
if "The same hands" not in b["text"]:
    b["text"] = "<p>The same hands, and the same habits, now make rooms. " + b["text"].lstrip()[3:] if b["text"].lstrip().startswith("<p>") else "<p>The same hands, and the same habits, now make rooms.</p>" + b["text"]

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
