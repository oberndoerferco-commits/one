"""5 Sept 2026 — the identity applied to collection pages and the product page.

Collection: a hero in the site grammar (editorial image or collection image, eyebrow,
Marcellus h1, one line), four cards across on the page ground with Marcellus titles and
no quick-add, and a close band that points to the atelier.
Product: eyebrow (family · leather) over the title, one filled button, the atelier link
under it, the facts list replaced by accordions in the house voice, a chapter on the making
below the buy box, and four recommendations across.
Re-runnable; run from the repo root after identity-pass.py.
"""
import json, re, copy, pathlib, glob
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
EYEBROW = {"type_preset": "custom", "font": "var(--font-subheading--family)", "font_size": "0.75rem",
           "line_height": "normal", "letter_spacing": "loose", "case": "uppercase", "wrap": "pretty"}
STATEMENT = {"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "2rem",
             "line_height": "normal", "letter_spacing": "normal", "case": "none", "wrap": "balance"}

_, idx = load("theme/templates/index.json")
CLOSE_SEC = copy.deepcopy(idx["sections"]["section_5IfLBc"])           # statement + link, centred
_, about = load("theme/templates/page.about-us.json")
CHAPTER = copy.deepcopy(about["sections"]["section_about_journey"])      # media-with-content chapter
_, bsp = load("theme/templates/page.bespoke.json")
LINK = copy.deepcopy(find(bsp["sections"]["media_with_content_Cj4MHU"]["blocks"], "button_nzW68w"))

# ---------- theme settings: no quick-add icon on cards ----------
p = "theme/config/settings_data.json"; h, d = load(p)
d["current"]["quick_add"] = False; d["current"]["mobile_quick_add"] = False
save(p, h, d)

# ---------- collection hero, as liquid so it follows the collection ----------
HERO_LIQUID = (
"{%- assign c = collection -%}{%- assign img = c.metafields.custom.editorial_image.value | default: c.image -%}"
"{%- assign line = c.metafields.custom.editorial_line.value | default: c.description | strip_html -%}"
"<style>.obm-chero{position:relative;width:100%;min-height:62svh;display:flex;align-items:flex-end;overflow:hidden;background:#1c1714}"
".obm-chero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}"
".obm-chero::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(28,23,20,.6),rgba(28,23,20,0) 60%)}"
".obm-chero__c{position:relative;z-index:1;width:100%;max-width:var(--page-width,1360px);margin:0 auto;padding:0 40px 40px;color:#fbf9f6}"
".obm-chero__e{font-family:var(--font-subheading--family);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#e5e0d7;margin:0 0 10px}"
".obm-chero__t{font-family:var(--font-heading--family);font-weight:400;font-size:2.5rem;line-height:1.1;margin:0;color:#fbf9f6}"
".obm-chero__l{font-family:var(--font-body--family);font-size:1rem;max-width:52ch;color:#f2ede6;margin:12px 0 0}"
"@media (max-width:749px){.obm-chero{min-height:56svh}.obm-chero__c{padding:0 16px 28px}.obm-chero__t{font-size:2rem}}</style>"
"<div class=\"obm-chero\">{%- if img != blank -%}{{ img | image_url: width: 2600 | image_tag: loading: 'eager', alt: c.title, class: '' }}{%- endif -%}"
"<div class=\"obm-chero__c\"><p class=\"obm-chero__e\">Collection</p><h1 class=\"obm-chero__t\">{{ c.title }}</h1>"
"{%- if line != blank -%}<p class=\"obm-chero__l\">{{ line }}</p>{%- endif -%}</div></div>")

HERO_IMAGES = {
  "collection.json": "obm-coll-featured.jpg",
  "collection.bags.json": "oberndoerfer-about-craft-detail.jpg",
  "collection.trunks.json": "oberndoerfer-cle-case-gold-hardware.jpg",
  "collection.home-accessories.json": "oberndoerfer-aol-ensemble.jpg",
  "collection.travel.json": "A1603CD8-9169-4741-81AE-31BBD21B10CC.jpg",
  "collection.small-leather-goods.json": "oberndoerfer-cle-brass-fittings.jpg",
  "collection.new-in.json": "obm-coll-newin.jpg",
  "collection.sunglasses.json": "manufacture-polishing-sunglasses.jpg",
  "collection.featured-products.json": "obm-coll-featured.jpg",
  "collection.collections-2.json": "obm-coll-trunks.jpg",
  "collection.oberndorfer-x-trax-nyc.json": "obm-coll-trunks.jpg",
}
HOME_HERO = copy.deepcopy(idx["sections"]["hero_jVaWmY"])
LINE_LIQUID = ("{%- assign c = closest.collection -%}{%- assign line = c.metafields.custom.editorial_line.value | default: c.description | strip_html -%}"
               "{%- if line != blank -%}<p style=\"font-family:var(--font-body--family);font-size:1rem;line-height:1.5;max-width:52ch;color:#f2ede6;margin:0\">{{ line }}</p>{%- endif -%}")
GRID_CSS = ("<style>@media screen and (min-width:990px){.product-grid--grid{--product-grid-columns-desktop:repeat(4,1fr)!important}}"
            "@media screen and (min-width:750px) and (max-width:989px){.product-grid--grid{--product-grid-columns-desktop:repeat(3,1fr)!important}}</style>")

# ---------- the frame (owner: "I liked the frame around products, it's easier to understand", Miu Miu's grid) ----------
LINE = "#d3cabc"
def frame_card(card, eyebrow_margin=True):
    """A card as a framed tile: one hairline around it, tiles touching, image edge to edge, text inset."""
    card["settings"].update({"background_color": "", "border": "solid", "border_width": 1, "border_opacity": 100, "border_color": LINE,
                             "border_radius": 0, "padding-block-start": 0, "padding-block-end": 14, "padding-inline-start": 0, "padding-inline-end": 0,
                             "product_card_gap": 6})
    for k, b in card["blocks"].items():
        st = b["settings"]
        if b["type"] == "_product-card-gallery": st.update({"image_ratio": "square", "border": "none"})
        if b["type"] == "product-title": st.update({"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "1.125rem", "line_height": "tight", "letter_spacing": "normal", "case": "none", "wrap": "pretty", "background": False, "padding-block-start": 10, "padding-block-end": 0, "padding-inline-start": 12, "padding-inline-end": 12})
        if b["type"] == "price": st.update({"type_preset": "paragraph", "font": "var(--font-body--family)", "font_size": "0.875rem", "padding-inline-start": 12, "padding-inline-end": 12, "padding-block-end": 0})
        if b["type"] == "swatches": st.update({"hide_padding": False, "product_swatches_padding_top": 6, "product_swatches_padding_bottom": 0, "product_swatches_padding_left": 12, "product_swatches_padding_right": 12})
        if b["type"] == "custom-liquid" and "assign lbl" in st.get("custom_liquid", ""):
            st["custom_liquid"] = st["custom_liquid"].replace("margin:0 0 8px;", "margin:10px 12px 8px;").replace("margin:10px 12px 8px;min-height", "margin:10px 12px 8px;min-height")

SWATCHES = {"type": "swatches", "settings": {"product_swatches_alignment": "flex-start", "product_swatches_alignment_mobile": "flex-start", "hide_padding": False,
            "product_swatches_padding_top": 6, "product_swatches_padding_bottom": 0, "product_swatches_padding_left": 12, "product_swatches_padding_right": 12}, "blocks": {}}

def rebuild_collection(f):
    h, d = load(f)
    S = d["sections"]
    name = pathlib.Path(f).name
    # hero: the home-page hero section, with this collection's photograph and its own words
    hero = copy.deepcopy(HOME_HERO)
    hero["settings"].update({"background_image": "shopify://shop_images/" + HERO_IMAGES[name], "section_height": "custom", "section_height_custom": 62,
                             "toggle_overlay": True, "overlay_style": "gradient", "overlay_color": "#1c171499", "gradient_direction": "to top"})
    hb = hero["blocks"]
    eyebrow = copy.deepcopy(hb["text_heroHead"]); eyebrow["settings"].update(EYEBROW); eyebrow["settings"].update({"text": "<p>Collection</p>", "text_color": "#e5e0d7", "width": "fit-content"})
    title = copy.deepcopy(hb["text_heroHead"]); title["settings"].update({"text": "<h1>{{ closest.collection.title }}</h1>", "text_color": "#fbf9f6", "font_size": "2.5rem", "line_height": "tight"})
    # the line is liquid: a text block's dynamic source may carry only one filter, and we need default + strip_html
    line = {"type": "custom-liquid", "settings": {"custom_liquid": LINE_LIQUID, "padding-block-start": 0, "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}
    css = {"type": "custom-liquid", "settings": {"custom_liquid": GRID_CSS, "padding-block-start": 0, "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}
    hero["blocks"] = {"eyebrow": eyebrow, "title": title, "line": line, "css": css}; hero["block_order"] = ["eyebrow", "title", "line", "css"]
    first = d["order"][0]
    S[first] = hero
    if "section_editorial" in S:
        del S["section_editorial"]; d["order"] = [o for o in d["order"] if o != "section_editorial"]
    # grid: four across on the page ground
    main = S["main"]
    main["settings"].update({"layout_type": "grid", "product_card_size": "medium", "mobile_product_card_size": "small",
                             "product_grid_width": "centered", "columns_gap_horizontal": 0, "columns_gap_vertical": 0,
                             "padding-block-start": 24, "padding-block-end": 48})
    card = main["blocks"]["product-card"]
    frame_card(card)
    filt = main["blocks"].get("filters")
    if filt: filt["settings"].update({"enable_grid_density": False})
    # close band
    if "section_close" not in S:
        cl = copy.deepcopy(CLOSE_SEC)
        t = find(cl["blocks"], "text_close01"); t["settings"].update(STATEMENT); t["settings"]["font_size"] = "1.5rem"
        t["settings"]["text"] = "<p>Looking for a leather, a colour or a size you don\u2019t see? Most of what we make is made to order.</p>"
        b = find(cl["blocks"], "button_close01"); b["settings"].update({"style_class": "button-unstyled", "label": "Write to the atelier", "link": "shopify://pages/contact"})
        cl["settings"].update({"padding-block-start": 64, "padding-block-end": 80, "background_color": "{{ settings.color_palette.color2 }}"})
        S["section_close"] = cl; d["order"].append("section_close")
    save(f, h, d)

# 5 September, later the same day: the owner preferred the collection pages as they were
# (three across, framed cards, the text header rather than a photograph). The templates were
# restored from commit 0860a59 and this loop is off. Do not re-enable without asking.
#
# for f in sorted(glob.glob("theme/templates/collection*.json")):
#     rebuild_collection(f)

# ---------- product page ----------
p = "theme/templates/product.json"; h, d = load(p)
main = d["sections"]["main"]; det = main["blocks"]["product-details"]; B = det["blocks"]

EYEBROW_LIQUID = (
"{%- assign p = product -%}{%- assign fam = '' -%}{%- for c in p.collections -%}{%- unless c.handle == 'new-in' or c.handle == 'signature-pieces' or c.handle == 'featured-products' or c.handle == 'collections-2' or c.handle == 'collections' -%}{%- assign fam = c.title -%}{%- break -%}{%- endunless -%}{%- endfor -%}"
"{%- assign t = p.title | downcase -%}{%- assign leather = '' -%}"
"{%- if t contains 'ostrich' -%}{%- assign leather = 'Ostrich' -%}{%- elsif t contains 'crocodile' -%}{%- assign leather = 'Crocodile' -%}{%- elsif t contains 'alligator' -%}{%- assign leather = 'Alligator' -%}{%- elsif t contains 'nabuk' -%}{%- assign leather = 'Nabuk calf' -%}{%- elsif t contains 'saffiano' -%}{%- assign leather = 'Saffiano calf' -%}{%- elsif t contains 'togo' or p.description contains 'Togo' -%}{%- assign leather = 'Togo calf' -%}{%- endif -%}"
"{%- if p.title contains 'Trax' -%}{%- assign fam = 'Limited edition' -%}{%- endif -%}"
"<p style=\"font-family:var(--font-subheading--family);font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;color:rgba(28,23,20,0.6);margin:0\">{{ fam }}{% if fam != '' and leather != '' %} &middot; {% endif %}{{ leather }}</p>")

B["eyebrow_pdp"] = {"type": "custom-liquid", "settings": {"custom_liquid": EYEBROW_LIQUID, "padding-block-start": 0, "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}
# title group: title in Marcellus (h2 preset already), price in body size
find(B, "price_tVjtKg")["settings"].update({"type_preset": "paragraph"})
find(B, "group_icgrde")["settings"]["gap"] = 8
# atelier line stays, styled as the site's text link line
B["custom_liquid_atelier"]["settings"]["custom_liquid"] = (
"<p style=\"font-size:0.9375rem;color:rgba(28,23,20,0.75);margin:4px 0 0;line-height:1.5\">Prefer a different leather, colour or lining? Most pieces can be made to order. "
"<a href=\"/pages/contact?piece={{ product.handle }}\" style=\"color:inherit;text-decoration:underline;text-underline-offset:0.2em\">Write to the atelier</a>.</p>")

# accordions in the house voice
acc = B["accordion_info"]; rows = acc["blocks"]
def row(rid, heading, html=None, liquid=None):
    r = copy.deepcopy(rows["row_care"]); r["settings"]["heading"] = heading
    inner = next(iter(r["blocks"].values())); inner["settings"]["text"] = html or ""
    if liquid:
        r["blocks"] = {"liquid": {"type": "custom-liquid", "settings": {"custom_liquid": liquid, "padding-block-start": 0, "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}}
        r["block_order"] = ["liquid"]
    return r
DETAILS = ("{%- assign mat = product.metafields.custom.materials_craft.value -%}{%- assign dim = product.metafields.custom.dimensions.value -%}{%- assign fits = product.metafields.custom.what_fits.value -%}"
"<div style=\"font-size:0.9375rem;line-height:1.6\">{%- if mat != blank -%}<p>{{ mat }}</p>{%- else -%}<p>Cut, stitched and finished by hand in ateliers around Milan. Full-grain hides from family tanneries in Italy, France and Germany; solid brass hardware.</p>{%- endif -%}"
"{%- if dim != blank -%}<p><strong>Dimensions</strong><br>{{ dim }}</p>{%- endif -%}{%- if fits != blank -%}<p><strong>What fits inside</strong><br>{{ fits }}</p>{%- endif -%}"
"{%- if dim == blank -%}<p>Interior and exterior measurements on request.</p>{%- endif -%}</div>")
MADE = ("{%- assign lt = product.metafields.custom.lead_time.value -%}<div style=\"font-size:0.9375rem;line-height:1.6\">"
"{%- if lt != blank -%}<p>This piece is made to order. Lead time: {{ lt }}.</p>{%- else -%}<p>Pieces in stock leave within days. Made to order, leather goods and boxes take 4–6 weeks; furniture 1–2 months.</p>{%- endif -%}"
"<p>Initials or a monogram can be hot-stamped in gold, silver or blind. A different leather, colour or lining can be made to order; nothing is cut until you have approved it. <a href=\"/pages/personalization\" style=\"color:inherit;text-decoration:underline\">How a commission works</a>.</p></div>")
new_rows = {
  "row_details": row("row_details", "Details", liquid=DETAILS),
  "row_delivery": row("row_delivery", "Delivery and returns",
      "<p>Free worldwide with DHL Express. Pieces in stock are delivered in 7–14 days.</p><p>Returns within 14 days of delivery, unused and in their original condition. Personalised and bespoke pieces cannot be returned. <a href=\"/policies/refund-policy\">Return policy</a> · <a href=\"/policies/shipping-policy\">Shipping policy</a>.</p>"),
  "row_made": row("row_made", "Made to order and personalisation", liquid=MADE),
  "row_repairs": row("row_repairs", "Repairs",
      "<p>Whatever we make, we repair. <a href=\"/pages/contact\">Send a photograph</a> and we quote before any work begins.</p>"),
  "row_care": row("row_care", "Care",
      "<p>A dry cloth, a dust bag and a stable room are most of it. The rest is in <a href=\"/pages/leather-care-guide\">Leather Care</a>.</p>"),
}
pack = copy.deepcopy(rows.get("row_gifting") or rows["row_packaging"]); pack["settings"]["heading"] = "Packaging and gifts"
find(pack["blocks"], "text_gifting")["settings"]["text"] = (find(pack["blocks"], "text_gifting") and 1) and "<p>Every piece leaves in a box made in Italy. Add a message at checkout and we write it by hand; a gift receipt on request.</p>"
new_rows["row_packaging"] = pack
acc["blocks"] = new_rows; acc["block_order"] = list(new_rows.keys())

# remove the facts list and the loose specs line (now inside Details)
for gone in ("group_trust_signals", "liquid_specs"):
    B.pop(gone, None)
det["block_order"] = ["breadcrumbs_pdp", "eyebrow_pdp", "group_icgrde", "divider_VJhene", "variant_picker_R3rGDr", "buy_buttons_eYQEYi", "custom_liquid_atelier", "text_aEtTtq", "accordion_info"]
det["settings"]["gap"] = 28

# chapter on the making, below the buy box
if "section_pdp_chapter" not in d["sections"]:
    ch = copy.deepcopy(CHAPTER)
    ch["settings"].update({"media_position": "left", "background_color": "{{ settings.color_palette.color2 }}"})
    find(ch["blocks"], "media")["settings"]["image"] = "shopify://shop_images/oberndoerfer-cle-atelier-bench.jpg"
    c = ch["blocks"]["content"]; grp = find(c["blocks"], "group_craftGrp")
    e = copy.deepcopy(find(grp["blocks"], "text_craftHead")); e["settings"].update(EYEBROW); e["settings"]["text"] = "<p>Made by hand</p>"
    find(grp["blocks"], "text_craftHead")["settings"].update({"type_preset": "h3", "text": "<p>Cut, stitched and finished around Milan</p>"})
    find(grp["blocks"], "text_craftBody")["settings"]["text"] = "<p>Every piece is made in small workshops we chose after visiting them, from hides we can trace to the tannery. The method is the one used for a trunk; only the scale changes. Whatever we make, we repair.</p>"
    lk = copy.deepcopy(LINK); lk["settings"].update({"label": "Materials and craftsmanship", "link": "shopify://pages/materials-craftsmanship", "style_class": "button-unstyled"})
    grp["blocks"] = {"eyebrow": e, "text_craftHead": grp["blocks"]["text_craftHead"], "text_craftBody": grp["blocks"]["text_craftBody"], "link": lk}
    grp["block_order"] = ["eyebrow", "text_craftHead", "text_craftBody", "link"]
    d["sections"]["section_pdp_chapter"] = ch
    d["order"].insert(1, "section_pdp_chapter")

# recommendations: four across, Marcellus head, card titles in Marcellus
rec = d["sections"]["product_recommendations_qggXJq"]
rec["type"] = "oberndoerfer-recommendations"          # sections/oberndoerfer-recommendations.liquid: the theme section, minus the crochet bags
rec["settings"].update({"columns": 4, "mobile_columns": "2", "columns_gap": 0, "rows_gap": 0, "gap": 24, "padding-block-start": 64, "padding-block-end": 64})
find(rec["blocks"], "text_cbcgyb")["settings"].update({"type_preset": "h3", "text": "<p>You may also like</p>"})
rc = find(rec["blocks"], "static-product-card")
if "swatches_recs" not in rc["blocks"]:
    rc["blocks"]["swatches_recs"] = copy.deepcopy(SWATCHES); rc["block_order"].append("swatches_recs")
frame_card(rc)
save(p, h, d)

# ---------- home product lists: the same tiles ----------
p = "theme/templates/index.json"; h, d = load(p)
for k, S in d["sections"].items():
    if S["type"] == "product-list":
        S["settings"].update({"columns_gap": 0, "rows_gap": 0})
        frame_card(S["blocks"]["static-product-card"])
save(p, h, d)
print("commerce pass done")
