#!/usr/bin/env python3
"""Ready to Wear (7 September 2026): the theme side of the new section.

Store side, done through the Admin API and not in this script: the automated collection
"Ready to Wear" (handle ready-to-wear; product type T-Shirt, Cap or Jacket, so anything typed
that way joins it on its own), its editorial line and image, the same three types added to the
"Products" catch-all, "Ready to Wear" in the main menu and the footer.

Theme side, produced here for the draft copy of the live theme:
- templates/collection.ready-to-wear.json: the collection page with its own hero (the woven neck
  label) and the same grid as every other collection.
- templates/product.ready-to-wear.json: the product page for cotton. Same page as leather, with
  the care row, the "made by hand" chapter and the made-to-order line written for a T-shirt or a
  cap instead of a hide.
- templates/index.json: "Ready to Wear" added to the Collections tabs on the home page.
- templates/list-collections.json: added to the collections page.

Re-runnable.
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
IMG = "shopify://shop_images/"
T = "theme/templates/"

# ---------- 1. the collection page ----------
h, d = load(T + "collection.json")  # the generic page, as the owner set it up for Ready to Wear on the live theme
hero = d["sections"][d["order"][0]]
# the owner's pick for this page (set on the live theme's generic collection template, 7 Sept 10:35)
for k in ("image_1", "background_image"):
    if k in hero["settings"]: hero["settings"][k] = IMG + "sewing-machine-in-use.jpg"
save(T + "collection.ready-to-wear.json", h, d)

# ---------- 2. the product page for cotton ----------
h, p = load(T + "product.json")
main = p["sections"]["main"]["blocks"]
care = find(main, "row_care")
for b in care["blocks"].values():
    if b["type"] == "text":
        b["settings"]["text"] = "<p>Wash cold, inside out, and dry flat. Iron on the reverse, away from the embroidery or the leather patch. A cap keeps its shape best on a shelf, not a hook.</p>"
made = find(main, "row_made")
for b in made["blocks"].values():
    if b["type"] == "custom-liquid":
        b["settings"]["custom_liquid"] = ("{%- assign lt = product.metafields.custom.lead_time.value -%}"
            "{%- if lt != blank -%}This piece is made to order. Lead time: {{ lt }}.{%- else -%}"
            "Pieces in stock are dispatched within two working days. A colour or size not shown can often be made: write to the atelier.{%- endif -%}")
row_details = find(main, "row_details")
for b in row_details["blocks"].values():
    if b["type"] == "custom-liquid":
        b["settings"]["custom_liquid"] = ("{%- assign mat = product.metafields.custom.materials_craft.value -%}"
            "<div style=\"font-size:0.9375rem;line-height:1.6\">{%- if mat != blank -%}<p>{{ mat }}</p>{%- else -%}"
            "<p>Cotton, cut and finished in Italy. The house mark is embroidered, or cut from calf leather, never printed.</p>{%- endif -%}"
            "{%- if product.metafields.custom.dimensions.value != blank -%}<p><strong>Fit</strong><br>{{ product.metafields.custom.dimensions.value }}</p>{%- endif -%}</div>")
eyebrow = find(main, "eyebrow_pdp")
if eyebrow:
    # a cap can also sit in Small Leather Goods; on this template the family is always Ready to Wear
    eyebrow["settings"]["custom_liquid"] = ("<p style=\"font-family:var(--font-subheading--family);font-size:0.75rem;letter-spacing:0.12em;"
        "text-transform:uppercase;color:rgba(28,23,20,0.6);margin:0\">Ready to Wear &middot; {{ product.type }}</p>")
atelier = find(main, "custom_liquid_atelier")
if atelier:
    atelier["settings"]["custom_liquid"] = "<p style=\"font-size:0.9375rem;color:rgba(28,23,20,0.7)\">Made in Italy, in small runs. When a colour or size sells out it is made again, not discontinued.</p>"
ch = p["sections"]["section_pdp_chapter"]["blocks"]
find(ch, "eyebrow")["settings"]["text"] = "<p>Made in Italy</p>"
find(ch, "text_craftHead")["settings"]["text"] = "<p>Cotton, made the way we make everything else</p>"
find(ch, "text_craftBody")["settings"]["text"] = ("<p>The T-shirts and caps come from the same house as the trunks and are held to the same habits: the cloth is washed before it is cut, the mark is embroidered in thread or cut from calf leather rather than printed on, and the label inside the neck is woven. Made in Italy, in small runs.</p>")
media = p["sections"]["section_pdp_chapter"]["blocks"].get("media")
if media and "image" in media.get("settings", {}):
    media["settings"]["image"] = IMG + "obm-tee-neck-label.jpg"
save(T + "product.ready-to-wear.json", h, p)

# ---------- 3. home: the Collections tabs ----------
h, i = load(T + "index.json")
tabs = i["sections"]["collection_list_4pRwyd"]
if "cat_rtw" not in tabs["blocks"]:
    src = tabs["blocks"]["cat_eyewear"]
    tabs["blocks"]["cat_rtw"] = copy.deepcopy(src)
    tabs["blocks"]["cat_rtw"]["settings"]["collection"] = "ready-to-wear"
    tabs["blocks"]["cat_rtw"]["settings"]["label"] = "Ready to Wear"
    tabs["block_order"].append("cat_rtw")
save(T + "index.json", h, i)

# ---------- 4. the collections page ----------
h, l = load(T + "list-collections.json")
cl = l["sections"]["collection_list_QRjthd"]["settings"]["collection_list"]
if "ready-to-wear" not in cl: cl.append("ready-to-wear")
save(T + "list-collections.json", h, l)
print("ready to wear pass done")
