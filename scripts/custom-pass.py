#!/usr/bin/env python3
"""Custom & Limited Editions (page.custom-limited-editions.json): the commerce pass for the story page.

The page talked about four pieces and sent the visitor away to see them. Now it shows them: a framed
four-tile grid of the Trax NYC collection sits under the introduction, the hero is the Trax
photograph rather than the Trunks collection's, the slideshows lose the taped workshop shot, and the
page keeps one filled button (the enquiry form's Send). Re-runnable.
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

LINE = "#d3cabc"
EYEBROW = {"type_preset": "custom", "font": "var(--font-subheading--family)", "font_size": "0.75rem", "line_height": "normal",
           "letter_spacing": "loose", "case": "uppercase", "wrap": "pretty"}

def frame_card(card):
    card["settings"].update({"background_color": "", "border": "solid", "border_width": 1, "border_opacity": 100, "border_color": LINE,
                             "border_radius": 0, "padding-block-start": 0, "padding-block-end": 14, "padding-inline-start": 0, "padding-inline-end": 0,
                             "product_card_gap": 6})
    for k, b in card["blocks"].items():
        st = b["settings"]
        if b["type"] == "_product-card-gallery": st.update({"image_ratio": "square", "border": "none"})
        if b["type"] == "product-title": st.update({"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "1.125rem", "line_height": "tight", "letter_spacing": "normal", "case": "none", "wrap": "pretty", "background": False, "padding-block-start": 10, "padding-block-end": 0, "padding-inline-start": 12, "padding-inline-end": 12})
        if b["type"] == "price": st.update({"type_preset": "paragraph", "font": "var(--font-body--family)", "font_size": "0.875rem", "padding-inline-start": 12, "padding-inline-end": 12, "padding-block-end": 0})

_, idx = load("theme/templates/index.json")
GRID = copy.deepcopy(idx["sections"]["product_list_signature"])

p = "theme/templates/page.custom-limited-editions.json"; h, d = load(p)
S = d["sections"]

# hero: the Trax pieces on the bamboo mat (6000px), not the Trunks collection's case
hero = S["hero_pQ8mXz"]
hero["settings"]["image_1"] = "shopify://shop_images/IMG_3112.jpg"      # the hero section's image key is image_1
hero["settings"].pop("background_image", None)
link = find(hero["blocks"], "link")
if link: link["settings"].update({"label": "The four pieces", "link": "shopify://collections/oberndoerfer-traxnyc"})

# slideshows: the hero photograph leaves the second one; the taped workshop shot goes
s1 = S["slideshow_xEfEzn"]; s2 = S["slideshow_cjPwBa"]
if "slide_TNgdXd" in s1["blocks"]:
    closeup = s1["blocks"].pop("slide_TNgdXd"); s1["block_order"] = [k for k in s1["block_order"] if k != "slide_TNgdXd"]
    s2["blocks"]["slide_kWBxt9"] = closeup                     # IMG_2910 close-up replaces IMG_3112
    s2["blocks"].pop("slide_3CMd7G", None); s2["block_order"] = ["slide_YVDrKV", "slide_kWBxt9"]

# introduction keeps its words, loses the filled button (the grid follows)
intro = S["section_mePnPJ"]
intro["blocks"].pop("button_ThVC6C", None); intro["block_order"] = [k for k in intro["block_order"] if k != "button_ThVC6C"]
intro["settings"]["padding-block-end"] = 24

# the four pieces, as a framed grid
g = copy.deepcopy(GRID)
g["settings"].update({"collection": "oberndoerfer-traxnyc", "max_products": 4, "columns": 4, "columns_gap": 0, "rows_gap": 0,
                      "carousel_on_mobile": False, "mobile_columns": "2", "gap": 20, "padding-block-start": 8, "padding-block-end": 72})
hd = g["blocks"]["static-header"]
t = find(hd["blocks"], "product_list_text_sig01"); t["settings"].update(EYEBROW); t["settings"]["text"] = "<p>The four pieces, one example of each</p>"
b = find(hd["blocks"], "product_list_button_sig01"); b["settings"].update({"label": "Open the collection", "style_class": "button-unstyled"})
card = g["blocks"]["static-product-card"]
card["blocks"].pop("card_eyebrow", None); card["block_order"] = [k for k in card["block_order"] if k != "card_eyebrow"]
frame_card(card)
S["section_trax_pieces"] = g
if "section_trax_pieces" not in d["order"]:
    d["order"].insert(d["order"].index("section_mePnPJ") + 1, "section_trax_pieces")
save(p, h, d)
print("custom pass done")
