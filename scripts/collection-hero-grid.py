#!/usr/bin/env python3
"""Collection pages: the photographic hero and four tiles across.

The 5 September commerce pass rebuilt these pages and the owner preferred the originals, so
they were restored (see scripts/commerce-pass.py, where the rebuild loop is off). Two pieces
of that pass were then asked for back, and only those two:

  1. the hero — the home page's hero section with a photograph of the family, "Collection" as
     the eyebrow, the collection title as the h1 and its own line beneath, in place of the
     plain "Collection heading" text section;
  2. four tiles across on desktop (three between 750 and 989px), by a style rule, since
     Horizon's card sizes give three or five and nothing between.

Everything else stays as restored: framed cards, tiles touching, the grid full width, the
card blocks and their type in the order they were. Re-runnable.
"""
import json, copy, glob, pathlib

def load(f):
    s = open(f).read(); i = s.index("\n{") + 1
    return s[:i], json.loads(s[i:])
def save(f, h, d):
    open(f, "w").write(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")

_, idx = load("theme/templates/index.json")
HOME_HERO = copy.deepcopy(idx["sections"]["hero_jVaWmY"])

EYEBROW = {"type_preset": "custom", "font": "var(--font-subheading--family)", "font_size": "0.75rem",
           "line_height": "normal", "letter_spacing": "loose", "case": "uppercase", "wrap": "pretty"}

# a text block's dynamic source may carry only one Liquid filter, and the line needs two
LINE_LIQUID = ("{%- assign c = closest.collection -%}"
               "{%- assign line = c.metafields.custom.editorial_line.value | default: c.description | strip_html -%}"
               "{%- if line != blank -%}<p style=\"font-family:var(--font-body--family);font-size:1rem;"
               "line-height:1.5;max-width:52ch;color:#f2ede6;margin:0\">{{ line }}</p>{%- endif -%}")

GRID_CSS = ("<style>@media screen and (min-width:990px){.product-grid--grid{--product-grid-columns-desktop:repeat(4,1fr)!important}}"
            "@media screen and (min-width:750px) and (max-width:989px){.product-grid--grid{--product-grid-columns-desktop:repeat(3,1fr)!important}}</style>")

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

def hero_for(name):
    hero = copy.deepcopy(HOME_HERO)
    hero["name"] = "Collection hero"
    hero["settings"].update({
        "background_image": "shopify://shop_images/" + HERO_IMAGES[name],
        "section_width": "page-width", "section_height": "custom", "section_height_custom": 62,
        "horizontal_alignment_flex_direction_column": "flex-start",
        "vertical_alignment_flex_direction_column": "flex-end", "gap": 24,
        "background_media": "image", "background_color": "", "background_image_position": "cover",
        "toggle_overlay": True, "overlay_style": "gradient", "overlay_color": "#1c171499",
        "gradient_direction": "to top", "padding-block-start": 32, "padding-block-end": 72})
    base = hero["blocks"]["text_heroHead"]
    eyebrow = copy.deepcopy(base); eyebrow["settings"].update(EYEBROW)
    eyebrow["settings"].update({"text": "<p>Collection</p>", "text_color": "#e5e0d7", "width": "fit-content"})
    title = copy.deepcopy(base)
    title["settings"].update({"text": "<h1>{{ closest.collection.title }}</h1>", "text_color": "#fbf9f6",
                              "font_size": "2.5rem", "line_height": "tight", "width": "fit-content"})
    line = {"type": "custom-liquid", "settings": {"custom_liquid": LINE_LIQUID, "padding-block-start": 0,
            "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}
    css = {"type": "custom-liquid", "settings": {"custom_liquid": GRID_CSS, "padding-block-start": 0,
           "padding-block-end": 0, "padding-inline-start": 0, "padding-inline-end": 0}, "blocks": {}}
    hero["blocks"] = {"eyebrow": eyebrow, "title": title, "line": line, "css": css}
    hero["block_order"] = ["eyebrow", "title", "line", "css"]
    return hero

for f in sorted(glob.glob("theme/templates/collection*.json")):
    name = pathlib.Path(f).name
    h, d = load(f)
    first = d["order"][0]
    d["sections"][first] = hero_for(name)          # replaces the heading section, or an earlier hero
    save(f, h, d)
    print("hero + four across:", name)
