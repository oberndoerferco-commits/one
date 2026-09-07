#!/usr/bin/env python3
"""About us, redesigned (page.about-us.json): photograph-led, half the words.

Owner's brief, 7 September: keep what was liked in the story (the journey through Italy, the
artisans who learned from their grandparents, stud by stud, heritage / quality / attention to
detail, standing behind those values before mass production makes them disappear) but the page
"looks a bit full of text, no lifestyle, brand aesthetic is missing".

What this pass does
- Every chapter now has a photograph, and the photographs are the house in the world or at the
  bench: the Riviera terrace, the tannery, studs being set, the Chesterfield being buttoned, the
  trunks on the workbench, the Miramare daybed. No product cut-outs, no generated images.
- The copy is the same story cut to one paragraph per chapter (about 900 words become about 450).
- The house grammar from docs/identity.md throughout: full-bleed hero with the ink gradient and
  a bottom-left eyebrow and serif title, centred statements in Marcellus, captions under
  photographs, underlined links rather than boxes.
- "The hide, accounted for" (byproduct, CITES) moves off this page; Materials & Craftsmanship
  carries it and is linked from the making chapter.

Runs on the current template and is re-runnable.
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
IMG = "shopify://shop_images/"

p = "theme/templates/page.about-us.json"; h, d = load(p)
S = d["sections"]

# ---------- 1. hero: the bag on the Riviera terrace, not the stacked cases ----------
hero = S["hero_H8KLYr"]
# The Miramare lobby: the house's sofa, armchairs and trunk table in a real room. (The terrace
# trunk bag was tried first and rejected by the owner: it is already the Bags collection hero.)
hero["settings"].update({"image_1": IMG + "IMG_5642_8dccfc93-d5be-4a54-a4b3-062942ac0c1a.heic",
                         "custom_mobile_media": False})
hero["settings"].pop("image_1_mobile", None)
find(hero["blocks"], "eyebrow")["settings"]["text"] = "<p>About us</p>"
find(hero["blocks"], "title")["settings"]["text"] = "<h1>Leather, learned at the source.</h1>"

# ---------- 2. opening statement, centred, one paragraph ----------
o = S["section_about_open"]
o["settings"].update({"horizontal_alignment": "center",
                      "horizontal_alignment_flex_direction_column": "center",
                      "padding-block-start": 88, "padding-block-end": 80, "gap": 20})
find(o["blocks"], "text_ab_eyebrow")["settings"].update({"text": "<p>The house</p>", "alignment": "center"})
hd = find(o["blocks"], "text_ab_head")["settings"]
hd.update({"text": "<h2>It began with a journey through Italy.</h2>", "alignment": "center",
           "type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2rem",
           "line_height": "tight"})
dk = find(o["blocks"], "text_ab_dek")["settings"]
dk.update({"alignment": "center", "max_width": "narrow", "text_color": "",
           "text": P("We set out with one question: what does Italian craftsmanship actually mean, once you take the word off the label? To find out we went to the leather artisans who learned the craft from their grandparents, and began to watch what really lies behind the words Made in Italy. What they showed us became the house.")})

# ---------- 3. the journey, beside the brass emblem being brazed at the bench ----------
# (IMG_0306 looked like tannery hands at thumbnail size; at full size it is a jewellery casting
#  mould from the store's earlier life, so it is not used.)
j = S["section_about_journey"]
j["blocks"]["media"]["settings"]["image"] = IMG + "Custom.jpg"
j["settings"]["media_position"] = "left"
find(j["blocks"], "text_craftHead")["settings"]["text"] = "<p>What we learned on the road</p>"
find(j["blocks"], "text_craftBody")["settings"]["text"] = P(
    "It began at the tanneries, family-run, in Italy, France and Germany, where a hide is still turned over and judged by hand. It ended in the small workshops around Milan, where a trunk is built stud by stud. When the journey was over we stayed, and began working alongside the people who had taught us. They still make everything we sell.")

# ---------- 4. three photographs of the hands, captions beneath ----------
t = S["section_dpgtkK"]
t["settings"].update({"padding-block-start": 8, "padding-block-end": 72, "gap": 12})
trio = [("group_Jmc9kk", "image_group_Jmc9kk", "IMG_6188.jpg", "Studs, set one at a time"),
        ("group_DGcdwG", "image_group_DGcdwG", "Artisan.jpg", "At the bench, around Milan"),
        ("group_9TAxbE", "image_group_9TAxbE", "IMG_7959.jpg", "A Chesterfield, buttoned by hand")]
for g, im, f, cap in trio:
    grp = t["blocks"][g]
    grp["blocks"][im]["settings"].update({"image": IMG + f, "image_ratio": "portrait", "border_radius": 0})
    grp["blocks"]["cap"]["settings"]["text"] = f"<p>{cap}</p>"

# ---------- 5. the statement band: craftsmanship as habits, and the three values ----------
m = S["section_about_meaning"]
m["settings"].update({"background_color": "#e5e0d7", "horizontal_alignment": "center",
                      "horizontal_alignment_flex_direction_column": "center",
                      "padding-block-start": 88, "padding-block-end": 40, "gap": 20})
find(m["blocks"], "text_ab_eyebrow")["settings"].update({"text": "<p>Craftsmanship</p>", "alignment": "center"})
mh = find(m["blocks"], "text_ab_head")["settings"]
mh.update({"text": "<h2>It is not a label. It is a set of habits.</h2>", "alignment": "center",
           "type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2rem",
           "line_height": "tight"})
md = find(m["blocks"], "text_ab_dek")["settings"]
md.update({"alignment": "center", "max_width": "narrow", "text_color": "",
           "text": P("Nothing you could print on a swing tag: a hundred small decisions made the same way every time. The hide chosen for the piece rather than the price. The stitch that holds without glue behind it. The hour spent on an edge most people will never look at. Underneath them we kept finding the same three things.")})

f = S["section_about_facts"]
f["settings"].update({"background_color": "#e5e0d7", "padding-block-start": 24, "padding-block-end": 88, "gap": 40})
for g in ("group_gx6VCY", "group_h4WHUt", "group_JM6c4a"):
    grp = f["blocks"][g]
    grp["block_order"] = [k for k in grp["block_order"] if not k.startswith("icon_")]
    for k in list(grp["blocks"]):
        if k.startswith("icon_"): del grp["blocks"][k]
find(f["blocks"], "text_6pYzpC")["settings"]["text"] = "<p>HERITAGE</p>"
find(f["blocks"], "text_AFybWJ")["settings"]["text"] = P("Methods handed from one pair of hands to the next, in workshops older than we are. We invented none of it. We went to learn it, and we keep it.")
find(f["blocks"], "text_8JNP4n")["settings"]["text"] = "<p>QUALITY</p>"
find(f["blocks"], "text_LWwGLH")["settings"]["text"] = P("Full-grain hides from tanneries we have stood in. Solid brass where others use plated zinc. Whatever we make, we repair.")
find(f["blocks"], "text_y3qQXc")["settings"]["text"] = "<p>ATTENTION TO DETAIL</p>"
find(f["blocks"], "text_rbMHBf")["settings"]["text"] = P("The things you notice on the tenth day, not the first: an even stitch where no one looks, a lock that closes with the right sound.")

# ---------- 6. why now: a photograph of the workbench with the words on it ----------
w = S["section_about_why"]
w["settings"].update({"background_media": "image",
                      "background_image": IMG + "oberndoerfer-cle-workshop-trunks.jpg",
                      "background_image_position": "cover",
                      "toggle_overlay": True, "overlay_color": "#1c171499",
                      "overlay_style": "gradient", "gradient_direction": "to top",
                      "section_width": "page-width", "section_height": "custom", "section_height_custom": 72,
                      "vertical_alignment_flex_direction_column": "flex-end",
                      "horizontal_alignment": "flex-start", "horizontal_alignment_flex_direction_column": "flex-start",
                      "padding-block-start": 40, "padding-block-end": 48, "gap": 14})
find(w["blocks"], "text_ab_eyebrow")["settings"].update({"text": "<p>Why now</p>", "alignment": "left", "text_color": "#e5e0d7"})
wh = find(w["blocks"], "text_ab_head")["settings"]
wh.update({"text": "<h2>The workshops are fewer every year.</h2>", "alignment": "left",
           "type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2rem",
           "line_height": "tight", "text_color": "#fbf9f6", "wrap": "balance"})
wd = find(w["blocks"], "text_ab_dek")["settings"]
wd.update({"alignment": "left", "max_width": "narrow", "text_color": "#f2ede6",
           "text": P("Much of what is sold as Italian leather today is made quickly and in volume, far from the hands it is named after. The workshops that still do it slowly are small, and each year there are fewer. We work with them, pay for the time a thing takes, and make in small numbers, so that what they know does not disappear.")})

# ---------- 7. the making: photograph right, one paragraph, a link to Materials ----------
if S["section_about_making"]["type"] != "media-with-content":
    S["section_about_making"] = copy.deepcopy(S["section_about_bridge"])
mk = S["section_about_making"]
mk["settings"]["media_position"] = "right"
mk["blocks"]["media"]["settings"]["image"] = IMG + "oberndoerfer-trunk-hardware-detail.jpg"
find(mk["blocks"], "text_craftCap")["settings"]["text"] = "<p>THE MAKING</p>"
find(mk["blocks"], "text_craftHead")["settings"]["text"] = "<p>Every piece passes through the same hands</p>"
find(mk["blocks"], "text_craftBody")["settings"]["text"] = P(
    "The hide is chosen by eye and by hand at the tannery, then cut so the grain runs the way the piece will be used. The seams that take the strain are stitched by hand, so a worn thread can be replaced without the seam giving way. The hardware comes last: solid brass, galvanised in gold, palladium or black. It is the part you touch every day.")
find(mk["blocks"], "button_craftBtn")["settings"].update({"label": "Materials & Craftsmanship", "link": "/pages/materials-craftsmanship"})

# ---------- 8. Sanremo: the daybed under the arch ----------
b = S["section_about_bridge"]
b["settings"]["media_position"] = "left"
b["blocks"]["media"]["settings"]["image"] = IMG + "oberndoerfer-aol-daybed-arch.jpg"
find(b["blocks"], "text_craftCap")["settings"]["text"] = "<p>SANREMO</p>"
find(b["blocks"], "text_craftHead")["settings"]["text"] = "<p>From the trunk to the room</p>"
find(b["blocks"], "text_craftBody")["settings"]["text"] = P(
    "The same hands, and the same habits, now make rooms. The Miramare, a belle-époque palace above the Ligurian sea, lived with our trunks for a season, then asked us to make its furniture. Sofas, armchairs, poufs, and a trunk that became a table.")
find(b["blocks"], "button_craftBtn")["settings"].update({"label": "Art of Living", "link": "/pages/oberndorfer-x-miramare-sanremo"})

# ---------- 9. the close: the palace hall with the high-back chair, the line in white ----------
# (the lounge poufs and the calf hide macro were both tried here and rejected by the owner)
c = S["section_about_close"]
c["settings"].update({"background_image": IMG + "oberndoerfer-aol-lobby.jpg",
                      "toggle_overlay": True, "overlay_color": "#1c171499", "overlay_style": "gradient",
                      "gradient_direction": "to top", "section_height": "custom", "section_height_custom": 56,
                      "padding-block-start": 80, "padding-block-end": 80, "gap": 20})
find(c["blocks"], "text_close01")["settings"].update({"text_color": "#fbf9f6",
    "text": "<p>Made the old way, in small numbers, for people who notice the difference.</p>"})
find(c["blocks"], "button_close01")["settings"].update({"label": "Explore the collections", "link": "/collections/all",
    "style_class": "button-unstyled", "link_text_color": "#fbf9f6"})

# ---------- order: the hide chapter leaves this page ----------
S.pop("media_with_content_a7znjk", None)
d["order"] = ["main", "hero_H8KLYr", "section_about_open", "section_about_journey", "section_dpgtkK",
              "section_about_meaning", "section_about_facts", "section_about_why", "section_about_making",
              "section_about_bridge", "house_facts", "section_about_close"]
assert all(k in S for k in d["order"]), [k for k in d["order"] if k not in S]
save(p, h, d)
print("about design pass done")
