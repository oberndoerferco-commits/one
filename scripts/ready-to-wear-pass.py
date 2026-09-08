#!/usr/bin/env python3
"""Ready to Wear (7 September 2026): the theme side of the new section.

Store side, done through the Admin API and not in this script: the automated collection
"Ready to Wear" (handle ready-to-wear; product type T-Shirt, Cap or Jacket, so anything typed
that way joins it on its own), its editorial line and image, the same three types added to the
"Products" catch-all, "Ready to Wear" in the main menu and the footer.

Theme side, produced here for the draft copy of the live theme:
- templates/collection.ready-to-wear.json: the collection page with its own hero (the sewing
  machine) and the same grid as every other collection.
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
# pre-order (8 Sept, the owner: "make the tshirts all preorder? their not avaible yet"): a product
# tagged "preorder" says so on its card. Stock is 0 with overselling allowed, so it can still be bought.
eb = d["sections"]["main"]["blocks"]["product-card"]["blocks"]["card_eyebrow"]["settings"]
if "preorder" not in eb["custom_liquid"]:
    eb["custom_liquid"] = eb["custom_liquid"].replace("{%- if p.title contains 'Trax' -%}",
        "{%- if p.tags contains 'preorder' -%}{%- assign lbl = 'Pre-order' -%}{%- elsif p.title contains 'Trax' -%}", 1)
# one card per colour (7 Sept evening, the owner: "make it possible that also the white tee is seen
# in collection page"): a script in the hero's css block clones a card for each further colour swatch,
# shows that colour's photograph and links to its variant. Source: theme/assets-src/obm-colour-cards.js.
js = open("theme/assets-src/obm-colour-cards.js").read().strip()
css = d["sections"]["section"]["blocks"]["css"]["settings"]
if "obm-colour-cards" not in css["custom_liquid"]:
    css["custom_liquid"] += "<script id=\"obm-colour-cards\">" + js + "</script>"
save(T + "collection.ready-to-wear.json", h, d)

# ---------- 2. the product page for cotton ----------
h, p = load(T + "product.json")
main = p["sections"]["main"]["blocks"]
# pre-order: a note above the buy button, the button reads "Pre-order", the made-to-order row says what happens
PREORDER_NOTE = ("{%- if product.tags contains 'preorder' -%}"
  "<div class=\"obm-preorder\" style=\"border-top:1px solid #d3cabc;border-bottom:1px solid #d3cabc;padding:14px 0;margin:4px 0 16px\">"
  "<p style=\"font-family:var(--font-subheading--family);font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;color:#1c1714;margin:0 0 6px\">Pre-order</p>"
  "<p style=\"font-size:0.9375rem;line-height:1.6;margin:0\">Not in stock yet. The first run is being made in Italy now. Order today and it ships the moment the run arrives. We will email you the shipping date.</p>"
  "</div>"
  "<script>(function(){function fix(){document.querySelectorAll('button[name=\"add\"], .sticky-add-to-cart__button').forEach(function(b){var w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT),n;while((n=w.nextNode())){if(n.nodeValue.trim()==='Add to cart'){n.nodeValue=n.nodeValue.replace('Add to cart','Pre-order');}}});}"
  "fix();new MutationObserver(fix).observe(document.body,{childList:true,subtree:true,characterData:true});})();</script>"
  "{%- endif -%}")
pd = main["product-details"]
# the gallery shows the chosen colour's photographs only (8 Sept, the owner: "in the white product
# page you can see a picture of the black tshirt front"). Needs the patched
# snippets/product-media-gallery-content.liquid, which groups a variant image with the media after it.
main["media-gallery"]["settings"]["hide_variants"] = True
# the size row: letters with a hairline under the chosen one, the way Jacquemus, Zegna and Loro Piana
# set it (8 Sept, the owner: "the size section looks basic")
PICKER_CSS = ("<style>"
 ".variant-option legend{font-family:var(--font-subheading--family);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:rgba(28,23,20,.6);margin:0 0 10px}"
 ".variant-option--buttons{display:flex;flex-wrap:wrap;gap:0 26px;row-gap:8px}"
 ".variant-option--buttons legend{width:100%;flex:0 0 100%}"
 ".variant-option--buttons .variant-option__button-label{position:relative;display:inline-flex;align-items:center;justify-content:flex-start;min-width:0;width:auto;height:auto;min-height:0;padding:0;margin:0;background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0}"
 ".variant-option--buttons .variant-option__button-label__pill{display:none!important}"
 ".variant-option--buttons .variant-option__button-label__text{font-family:var(--font-body--family);font-size:.875rem;letter-spacing:.08em;color:rgba(28,23,20,.5);padding:2px 0 6px;border-bottom:1px solid transparent;transition:color .15s,border-color .15s}"
 ".variant-option--buttons .variant-option__button-label:hover .variant-option__button-label__text{color:#1c1714}"
 ".variant-option--buttons .variant-option__button-label:has(input:checked) .variant-option__button-label__text{color:#1c1714;border-bottom-color:#1c1714}"
 ".variant-option--buttons .variant-option__button-label:has(input[data-option-available=\"false\"]) .variant-option__button-label__text{color:rgba(28,23,20,.3);text-decoration:line-through}"
 ".variant-option--buttons .variant-option__button-label:has(input:focus-visible) .variant-option__button-label__text{outline:1px solid #1c1714;outline-offset:4px}"
 "</style>")
if "obm_picker_css" not in pd["blocks"]:
    pd["blocks"]["obm_picker_css"] = {"type": "custom-liquid", "settings": {"custom_liquid": PICKER_CSS}, "blocks": {}}
    pd["block_order"].insert(pd["block_order"].index("variant_picker_R3rGDr"), "obm_picker_css")
else:
    pd["blocks"]["obm_picker_css"]["settings"]["custom_liquid"] = PICKER_CSS
if "preorder_note" not in pd["blocks"]:
    pd["blocks"]["preorder_note"] = {"type": "custom-liquid", "settings": {"custom_liquid": PREORDER_NOTE}, "blocks": {}}
    pd["block_order"].insert(pd["block_order"].index("buy_buttons_eYQEYi"), "preorder_note")
care = find(main, "row_care")
for b in care["blocks"].values():
    if b["type"] == "text":
        b["settings"]["text"] = "<p>Wash cold, inside out, and dry flat. Iron on the reverse, away from the embroidery or the leather patch. A cap keeps its shape best on a shelf, not a hook.</p>"
made = find(main, "row_made")
for b in made["blocks"].values():
    if b["type"] == "custom-liquid":
        b["settings"]["custom_liquid"] = ("{%- if product.tags contains 'preorder' -%}This piece is on pre-order. The first run is being made in Italy now. You pay today, and the piece ships the moment the run arrives. We will email you the shipping date, and you can cancel at any time before it ships.{%- else -%}"
            "{%- assign lt = product.metafields.custom.lead_time.value -%}"
            "{%- if lt != blank -%}This piece is made to order. Lead time: {{ lt }}.{%- else -%}"
            "Pieces in stock are dispatched within two working days. A colour or size not shown can often be made: write to the atelier.{%- endif -%}{%- endif -%}")
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
# the "Prefer a different leather, colour or lining?" line has no place under a T-shirt: the block goes
def drop_block(blocks, key):
    for k, b in list(blocks.items()):
        if k == key:
            del blocks[k]; return True
        if drop_block(b.get("blocks", {}), key):
            if key in b.get("block_order", []): b["block_order"].remove(key)
            return True
    return False
drop_block(main, "custom_liquid_atelier")
# the Colour option is linked to the store's Color swatches (7 Sept), so the picker draws them
def set_swatches(blocks):
    for b in blocks.values():
        if b["type"] == "variant-picker": b["settings"]["show_swatches"] = True
        set_swatches(b.get("blocks", {}))
set_swatches(main)
for sec in p["sections"].values():
    if "custom_liquid_atelier" in sec.get("block_order", []): sec["block_order"].remove("custom_liquid_atelier")
ch = p["sections"]["section_pdp_chapter"]["blocks"]
find(ch, "eyebrow")["settings"]["text"] = "<p>Made in Italy</p>"
find(ch, "text_craftHead")["settings"]["text"] = "<p>Cotton, made the way we make everything else</p>"
find(ch, "text_craftBody")["settings"]["text"] = ("<p>The T-shirts and caps come from the same house as the trunks and are held to the same habits: the cloth is washed before it is cut, the mark is embroidered in thread or cut from calf leather rather than printed on, and the label inside the neck is woven. Made in Italy, in small runs.</p>")
media = p["sections"]["section_pdp_chapter"]["blocks"].get("media")
if media and "image" in media.get("settings", {}):
    # the neck label was here first; the owner wants it off every T-shirt page (7 Sept), so the chapter
    # shows the sewing machine, the same photograph as the Ready to Wear hero
    media["settings"]["image"] = IMG + "sewing-machine-in-use.jpg"
save(T + "product.ready-to-wear.json", h, p)

# ---------- 2b. the generic product page: the leather line never shows on cotton ----------
h2, g = load(T + "product.json")
ga = find(g["sections"]["main"]["blocks"], "custom_liquid_atelier")
if ga and "product.type" not in ga["settings"]["custom_liquid"]:
    ga["settings"]["custom_liquid"] = ("{%- unless product.type == 'T-Shirt' or product.type == 'Cap' or product.type == 'Jacket' -%}"
        + ga["settings"]["custom_liquid"] + "{%- endunless -%}")
save(T + "product.json", h2, g)

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
