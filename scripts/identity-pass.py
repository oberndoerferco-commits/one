"""4 Sept 2026 — one identity across the Claude theme.

Applies the rules in docs/identity.md:
  * every page opens the same way: full-bleed photograph, ink gradient, eyebrow /
    Marcellus title / one underlined link, bottom left, in white
  * no photograph narrower than 1800px in a hero or a full-width row
  * eyebrows 12px tracked capitals; statements Marcellus 32px; chapter heads h3
  * one filled button per page; everything else an underlined text link
  * card eyebrow says the family of the piece in mixed grids and only the
    exceptions (Made to order / Limited edition / Exotic leather) on a collection page
Idempotent; run from the repo root after house-style-pass*.py.
"""
import json, re, copy, pathlib
HDR = re.compile(r"(/\*.*?\*/\s*)", re.S)
def load(p):
    s = pathlib.Path(p).read_text(); m = HDR.match(s)
    return (m.group(1) if m else ""), json.loads(s[m.end():] if m else s)
def save(p, h, d): pathlib.Path(p).write_text(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def find(blocks, bid):
    for k, b in blocks.items():
        if k == bid: return b
        if b.get("blocks"):
            r = find(b["blocks"], bid)
            if r: return r
def walk(blocks):
    for k, b in blocks.items():
        yield k, b
        if b.get("blocks"): yield from walk(b["blocks"])

WHITE, PALE, SAND = "#fbf9f6", "#f2ede6", "#e5e0d7"
INK_GRADIENT = "#1c171499"
EYEBROW = {"type_preset": "custom", "font": "var(--font-subheading--family)", "font_size": "0.75rem",
           "line_height": "normal", "letter_spacing": "loose", "case": "uppercase", "wrap": "pretty"}
STATEMENT = {"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2rem",
             "line_height": "normal", "letter_spacing": "normal", "case": "none", "wrap": "balance"}
TITLE = {"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2.5rem",
         "line_height": "tight", "letter_spacing": "normal", "case": "none", "wrap": "balance"}

# block templates, taken from the Bespoke hero (a hero we know renders)
_, bsp = load("theme/templates/page.bespoke.json")
BH = bsp["sections"]["hero_yF3ieQ"]["blocks"]
if "group_qigmjr" in BH:      # first run: the original Bespoke hero
    OUTER = copy.deepcopy(BH["group_qigmjr"]); INNER = copy.deepcopy(OUTER["blocks"]["group_9qfRTp"])
    TEXT = copy.deepcopy(INNER["blocks"]["text_3JBc47"])
else:                          # later runs: the hero this script built
    OUTER = copy.deepcopy(BH["hero"]); INNER = copy.deepcopy(OUTER["blocks"]["content"])
    TEXT = copy.deepcopy(INNER["blocks"]["title"])
LINK = copy.deepcopy(find(bsp["sections"]["media_with_content_Cj4MHU"]["blocks"], "button_nzW68w"))

def text_block(html, style, color, width="100%"):
    t = copy.deepcopy(TEXT); t["settings"].update(style)
    t["settings"].update({"text": html, "text_color": color, "width": width, "alignment": "left", "max_width": "normal"})
    return t

def hero_blocks(eyebrow, title, line=None, link=None):
    inner = copy.deepcopy(INNER); inner["blocks"] = {}; inner["block_order"] = []
    inner["settings"].update({"gap": 12, "width": "custom", "custom_width": 60, "width_mobile": "fill"})
    inner["blocks"]["eyebrow"] = text_block(f"<p>{eyebrow}</p>", EYEBROW, SAND)
    inner["blocks"]["title"] = text_block(f"<h1>{title}</h1>", TITLE, WHITE)
    inner["block_order"] = ["eyebrow", "title"]
    if line:
        inner["blocks"]["line"] = text_block(f"<p>{line}</p>", {"type_preset": "rte"}, PALE)
        inner["block_order"].append("line")
    if link:
        b = copy.deepcopy(LINK); b["settings"].update({"label": link[0], "link": link[1], "style_class": "button-unstyled", "link_text_color": WHITE})
        inner["blocks"]["link"] = b; inner["block_order"].append("link")
    outer = copy.deepcopy(OUTER); outer["blocks"] = {"content": inner}; outer["block_order"] = ["content"]
    outer["settings"].update({"horizontal_alignment": "flex-start", "vertical_alignment": "flex-end", "padding-block-end": 8})
    return {"hero": outer}, ["hero"]

def restyle_hero(sec, image=None):
    s = sec["settings"]
    s.update({"toggle_overlay": True, "overlay_style": "gradient", "overlay_color": INK_GRADIENT, "gradient_direction": "to top"})
    if image:
        s["image_1"] = image
        if s.get("custom_mobile_media"): s["image_1_mobile"] = image
    if s.get("section_height") == "large": s["section_height"] = "large"

def demote_h1(d, keep_sid):
    for sid, sec in d["sections"].items():
        if sid == keep_sid: continue
        for k, b in walk(sec.get("blocks", {})):
            t = b.get("settings", {}).get("text")
            if isinstance(t, str) and "<h1>" in t:
                b["settings"]["text"] = t.replace("<h1>", "<h2>").replace("</h1>", "</h2>")

def statements_to_2rem(d):
    for sid, sec in d["sections"].items():
        if sec["type"] == "hero": continue
        for k, b in walk(sec.get("blocks", {})):
            s = b.get("settings", {})
            if b["type"] == "text" and s.get("type_preset") == "custom" and s.get("font") == "var(--font-heading--family)" and s.get("font_size") == "1.5rem":
                s["font_size"] = "2rem"

PREFIX = "#shopify-section-template--31283375931717__"

HEROES = {
  "page.about-us.json": ("hero_H8KLYr", "shopify://shop_images/IMG_3535_dbf62bc4-2168-4b05-b2a5-40ce1a98f55a.heic",
      "About us", "Leather, learned at the source.", None, None),
  "page.art-of-living.json": ("hero_eAhQMJ", None,
      "Art of Living", "Furniture, made the way we make a trunk.", None, ("The Miramare commission", PREFIX + "section_aol_commission")),
  "page.bespoke.json": ("hero_yF3ieQ", None,
      "Bespoke", "Made to your measure.", "Trunks, bags, furniture and jewellery, drawn and made for one person.", ("How a commission works", PREFIX + "section_process")),
  "page.contact.json": ("hero_XnBQ36", "shopify://shop_images/oberndoerfer-cle-atelier-bench.jpg",
      "Contact", "Write to us.", None, None),
  "page.custom-limited-editions.json": ("hero_pQ8mXz", None,
      "Custom & Limited Editions", "One of each.", None, ("See the four pieces", "shopify://collections/oberndoerfer-traxnyc")),
  "page.leather-care.json": ("hero_kLcUbL", None,
      "Leather Care", "How a piece ages well.", None, None),
  "page.materials-craftsmanship.json": ("hero_mat", None,
      "Materials & Craftsmanship", "Full-grain hides and solid brass, by hand.", None, None),
  "page.the-art-of-packaging.json": ("hero_pack", None,
      "The Art of Packaging", "A box made in Italy, for a piece made in Italy.", None, None),
}
for fname, (sid, image, eyebrow, title, line, link) in HEROES.items():
    p = "theme/templates/" + fname; h, d = load(p)
    sec = d["sections"][sid]
    restyle_hero(sec, image)
    sec["blocks"], sec["block_order"] = hero_blocks(eyebrow, title, line, link)
    demote_h1(d, sid)
    statements_to_2rem(d)
    save(p, h, d)

# page-specific follow-ups so the hero and the opening do not say the same thing
p = "theme/templates/page.about-us.json"; h, d = load(p)
find(d["sections"]["section_about_open"]["blocks"], "text_ab_head")["settings"]["text"] = "<h2>The house began as a journey.</h2>"
row = d["sections"]["section_dpgtkK"]["blocks"]
find(row, "image_group_DGcdwG")["settings"]["image"] = "shopify://shop_images/A89E7596-F00C-44A3-BB43-71E6C645AEF7_2bca46fe-1783-41bb-982a-e71b06e7c3a2.jpg"
find(row, "cap") and None
for gid, cap in {"group_Jmc9kk": "At the bench, fitting the hardware", "group_DGcdwG": "The 017 tote, in black", "group_9TAxbE": "Watch boxes, stacked"}.items():
    row[gid]["blocks"]["cap"]["settings"]["text"] = f"<p>{cap}</p>"
find(row, "image_group_Jmc9kk")["settings"]["image"] = "shopify://shop_images/oberndoerfer-about-craft-detail.jpg"
save(p, h, d)

p = "theme/templates/page.art-of-living.json"; h, d = load(p)
find(d["sections"]["section_aol_open"]["blocks"], "head")["settings"]["text"] = "<h2>Objects for a room, made in Milan.</h2>"
save(p, h, d)

p = "theme/templates/page.contact.json"; h, d = load(p)
main = d["sections"]["main"]
main["blocks"].pop("title", None); main["block_order"] = [k for k in main["block_order"] if k != "title"]
st = main["blocks"]["statement"]["settings"]; st.update(STATEMENT); st["text"] = "<p>A person in the atelier answers, usually within one working day.</p>"
save(p, h, d)

p = "theme/templates/page.custom-limited-editions.json"; h, d = load(p)
find(d["sections"]["section_VUyT6E"]["blocks"], "text_LDkdGC")["settings"]["text"] = "<p>Some pieces we make once.</p>"
find(d["sections"]["section_VUyT6E"]["blocks"], "text_CLYKCg")["settings"]["text"] = "<p>A run of four for a jeweller in New York, a trunk built for one room, a colour we will not repeat. Made in the same ateliers as everything else, to the same standard. When they are gone, they are gone.</p>"
save(p, h, d)

# ---------- Home ----------
p = "theme/templates/index.json"; h, d = load(p)
hero = d["sections"]["hero_jVaWmY"]
hero["settings"].update({"toggle_overlay": True, "overlay_style": "gradient", "overlay_color": "#1c171480", "gradient_direction": "to top"})
hb = hero["blocks"]
if "eyebrow" not in hb:
    hb["eyebrow"] = text_block("<p>Trunks, bags and objects for the home</p>", EYEBROW, SAND, width="fit-content")
    hero["block_order"] = ["eyebrow"] + hero["block_order"]
hb["text_heroHead"]["settings"].update({"text": "<h1>Made by hand, around Milan.</h1>", "text_color": WHITE, "line_height": "tight"})
hb["button_heroBtn"]["settings"].update({"style_class": "button-unstyled", "link_text_color": WHITE, "label": "Discover the collections"})
d["sections"]["collection_list_4pRwyd"]["settings"]["heading"] = "Collections"
find(d["sections"]["section_PaekVn"]["blocks"], "button_aolLink")["settings"]["style_class"] = "button-unstyled"
find(d["sections"]["section_PaekVn"]["blocks"], "text_hYWtWG")["settings"].update(EYEBROW)
find(d["sections"]["section_homeliving_studio"]["blocks"], "button_hl")["settings"]["style_class"] = "button-unstyled"
m = d["sections"]["media_with_content_REm8Na"]["blocks"]
find(m, "text_craftCap")["settings"].update(EYEBROW); find(m, "text_craftCap")["settings"]["text"] = "<p>The house</p>"
find(m, "text_craftHead")["settings"].update({"type_preset": "h3", "text": "<p>Made in ateliers around Milan</p>"})
find(m, "text_craftBody")["settings"]["text"] = "<p>Full-grain hides from family tanneries in Italy, France and Germany, cut and stitched by hand in small workshops we chose after visiting them. The method is the one used for a trunk. Only the scale changes.</p>"
find(m, "button_craftBtn")["settings"].update({"style_class": "button-unstyled", "label": "About the house"})
d["sections"]["media_with_content_REm8Na"]["blocks"]["content"]["settings"]["vertical_alignment_flex_direction_column"] = "center"
for k, b in walk(d["sections"]["section_M8B9qT"]["blocks"]):
    if b["type"] == "text" and b["settings"].get("case") == "uppercase": b["settings"].update(EYEBROW)
find(d["sections"]["section_5IfLBc"]["blocks"], "button_close01")["settings"]["style_class"] = "button-unstyled"
save(p, h, d)

# ---------- Card eyebrow: family in mixed grids, exceptions only on a collection page ----------
def eyebrow_liquid(family):
    fam = ("{%- if lbl == '' -%}{%- for c in p.collections -%}{%- unless c.handle == 'new-in' or c.handle == 'signature-pieces' or c.handle == 'featured-products' or c.handle == 'collections-2' -%}"
           "{%- assign lbl = c.title -%}{%- break -%}{%- endunless -%}{%- endfor -%}{%- endif -%}") if family else ""
    return ("{%- assign p = closest.product -%}{%- assign lbl = '' -%}{%- if p.title contains 'Trax' -%}{%- assign lbl = 'Limited edition' -%}"
            "{%- elsif p.type == 'Furniture' or p.type == 'sofa' or p.type == 'Wine Case' or p.metafields.custom.lead_time != blank -%}{%- assign lbl = 'Made to order' -%}"
            "{%- elsif p.title contains 'Alligator' or p.title contains 'Crocodile' or p.title contains 'Ostrich' -%}{%- assign lbl = 'Exotic leather' -%}{%- endif -%}" + fam +
            "<p style=\"font-family:var(--font-subheading--family);font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:rgba(28,23,20,0.6);margin:0 0 8px;min-height:1em\">{{ lbl }}</p>")
import glob
for f in glob.glob("theme/templates/*.json"):
    if "BEFORE" in f: continue
    h, d = load(f); changed = False
    family = not pathlib.Path(f).name.startswith("collection")
    for sid, sec in d["sections"].items():
        for k, b in walk(sec.get("blocks", {})):
            if b["type"] == "custom-liquid" and "Handmade in Italy" in b["settings"].get("custom_liquid", "") or (b["type"] == "custom-liquid" and "assign lbl" in b["settings"].get("custom_liquid", "")):
                b["settings"]["custom_liquid"] = eyebrow_liquid(family); changed = True
    if changed: save(f, h, d)

# ---------- Header: menu and localisation in 12px tracked capitals ----------
p = "theme/sections/header-group.json"; h, d = load(p)
hs = d["sections"]["header_section"]
hs["blocks"]["header-menu"]["settings"]["type_font_primary_size"] = "0.75rem"
hs["settings"].update({"localization_font_size": "0.75rem", "actions_font_size": "0.75rem", "text_color_transparent_home": "#fbf9f6"})
save(p, h, d)
print("identity pass done")

# ---------- after the first render: same hero geometry everywhere, no repeated opening ----------
for fname, (sid, *_rest) in HEROES.items():
    p = "theme/templates/" + fname; h, d = load(p)
    s = d["sections"][sid]["settings"]
    s.update({"section_width": "page-width", "vertical_alignment_flex_direction_column": "flex-end",
              "horizontal_alignment_flex_direction_column": "flex-start", "custom_mobile_media": False})
    save(p, h, d)
p = "theme/templates/page.about-us.json"; h, d = load(p)
find(d["sections"]["section_about_open"]["blocks"], "text_ab_dek")["settings"]["text"] = "<p>We went to learn from the tanneries and artisans of Italy, then stayed to work alongside them. Everything we make is still made that way: by hand, around Milan, to order, in small numbers.</p>"
row = d["sections"]["section_dpgtkK"]["blocks"]
find(row, "image_group_Jmc9kk")["settings"]["image"] = "shopify://shop_images/oberndoerfer-cle-workshop-trunks.jpg"
row["group_Jmc9kk"]["blocks"]["cap"]["settings"]["text"] = "<p>Trunks in the workshop</p>"
save(p, h, d)
print("hero geometry unified")

# Leather Care: the page title under the hero was an Inter-bold h2; it becomes the statement
p = "theme/templates/page.leather-care.json"; h, d = load(p)
hd = d["sections"]["main"]["blocks"]["heading"]["settings"]
hd.update(STATEMENT); hd["text"] = "<p>Very little, done regularly.</p>"; hd["width"] = "100%"; hd["alignment"] = "left"
save(p, h, d)
