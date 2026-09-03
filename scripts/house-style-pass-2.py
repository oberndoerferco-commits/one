"""3 Sept 2026 — house style on About us and Contact (same grammar as house-style-pass.py)."""
import json, re, copy, pathlib
HDR = re.compile(r"(/\*.*?\*/\s*)", re.S)
def load(p):
    s = pathlib.Path(p).read_text(); m = HDR.match(s)
    return (m.group(1) if m else ""), json.loads(s[m.end():] if m else s)
def save(p, h, d): pathlib.Path(p).write_text(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")
EYEBROW = {"type_preset": "custom", "font": "var(--font-subheading--family)", "font_size": "0.75rem",
           "line_height": "normal", "letter_spacing": "loose", "case": "uppercase", "wrap": "pretty"}
STATEMENT = {"type_preset": "custom", "font": "var(--font-heading--family)", "font_size": "1.5rem",
             "line_height": "normal", "letter_spacing": "normal", "case": "none", "wrap": "balance"}
def find(blocks, bid):
    for k, b in blocks.items():
        if k == bid: return b
        if b.get("blocks"):
            r = find(b["blocks"], bid)
            if r: return r

# templates for a step group and its two text blocks, taken from the Bespoke process row
_, bsp = load("theme/templates/page.bespoke.json")
STEP = bsp["sections"]["section_process"]["blocks"]["steps"]["blocks"]["step_1"]
ROW = bsp["sections"]["section_process"]["blocks"]["steps"]
def pair(eyebrow, body_html):
    g = copy.deepcopy(STEP)
    g["blocks"]["num"]["settings"]["text"] = f"<p>{eyebrow}</p>"
    g["blocks"]["body"]["settings"]["text"] = body_html
    return g

# ---------- About us ----------
p = "theme/templates/page.about-us.json"; h, d = load(p)
hero_cap = find(d["sections"]["hero_H8KLYr"]["blocks"], "text_FYmXW9"); hero_cap["settings"].update(EYEBROW)
find(d["sections"]["section_about_open"]["blocks"], "text_ab_eyebrow")["settings"].update(EYEBROW)
for bid in ("text_6pYzpC", "text_8JNP4n", "text_y3qQXc"):
    find(d["sections"]["section_about_facts"]["blocks"], bid)["settings"].update(EYEBROW)
for sid, bid in (("media_with_content_a7znjk", "button_sustain"), ("section_about_bridge", "button_craftBtn")):
    find(d["sections"][sid]["blocks"], bid)["settings"]["style_class"] = "button-unstyled"
find(d["sections"]["section_about_close"]["blocks"], "button_close01")["settings"]["style_class"] = "button"
cl = find(d["sections"]["section_about_close"]["blocks"], "text_close01")
cl["settings"].update(STATEMENT); cl["settings"]["text"] = "<p>Everything we make begins as an order, and is made for the person who placed it.</p>"
# captions under the three photographs
cap_src = copy.deepcopy(STEP["blocks"]["num"]); cap_src["settings"]["padding-block-start"] = 12
sec = d["sections"]["section_dpgtkK"]
for gid, text in {"group_Jmc9kk": "At the bench, fitting the hardware", "group_DGcdwG": "A trunk bag, carried", "group_9TAxbE": "Watch boxes, stacked"}.items():
    g = sec["blocks"][gid]
    if "cap" not in g["blocks"]:
        c = copy.deepcopy(cap_src); c["settings"]["text"] = f"<p>{text}</p>"
        g["blocks"]["cap"] = c; g["block_order"] = g["block_order"] + ["cap"]
        g["settings"]["vertical_alignment_flex_direction_column"] = "flex-start"; g["settings"]["gap"] = 0
sec["settings"]["padding-block-end"] = 24
save(p, h, d)

# ---------- Contact ----------
p = "theme/templates/page.contact.json"; h, d = load(p)
main = d["sections"]["main"]
title = main["blocks"]["title"]; title["settings"].update(EYEBROW); title["settings"]["text"] = "<h1>Contact</h1>"; title["settings"]["alignment"] = "left"
stmt = copy.deepcopy(title); stmt["settings"].update(STATEMENT); stmt["settings"]["font_size"] = "2rem"
stmt["settings"]["text"] = "<p>Write to us. A person in the atelier answers, usually within one working day.</p>"
stmt["settings"]["max_width"] = "normal"
main["blocks"] = {"title": title, "statement": stmt}; main["block_order"] = ["title", "statement"]
main["settings"]["padding-block-start"] = 72; main["settings"]["padding-block-end"] = 24
form = d["sections"]["form"]
form["settings"].update({"content_direction": "row", "vertical_on_mobile": True, "vertical_alignment": "flex-start", "gap": 64, "padding-block-start": 24, "padding-block-end": 96})
details = copy.deepcopy(ROW); details["settings"].update({"content_direction": "column", "gap": 32, "width": "fill", "horizontal_alignment_flex_direction_column": "flex-start", "vertical_alignment_flex_direction_column": "flex-start"})
details["blocks"] = {
  "email": pair("Email", '<p><a href="mailto:info@oberndoerferco.com">info@oberndoerferco.com</a><br>Orders, commissions, repairs, and anything you would like to know before you decide.</p>'),
  "phone": pair("Telephone", '<p><a href="tel:+491732489709">+49 173 2489709</a><br>Monday to Friday, 9 to 18, Central European Time.</p>'),
  "trade": pair("Trade and press", '<p>We sell directly, here. For wholesale, collaboration or press, write to the same address; our current collaborations are on the <a href="/pages/trax-nyc">Custom &amp; Limited Editions</a> page.</p>'),
  "see": pair("See the pieces", '<p>Miramare The Palace, Corso Matuzia 9, Sanremo<br>Trax NYC, 64 W 47th Street, New York<br><a href="/pages/where-to-find-us">Where to find us</a></p>'),
}
details["block_order"] = ["email", "phone", "trade", "see"]
cf = form["blocks"]["contact_form_UwiCkQ"]; cf["settings"]["width"] = "custom"; cf["settings"]["custom_width"] = 55
cf["blocks"]["submit-button"]["settings"]["label"] = "Send"
form["blocks"] = {"details": details, "contact_form_UwiCkQ": cf}; form["block_order"] = ["details", "contact_form_UwiCkQ"]
save(p, h, d)
print("about + contact done")

# ---------- fixes after the first render ----------
p = "theme/templates/page.about-us.json"; h, d = load(p)
for g in d["sections"]["section_dpgtkK"]["blocks"].values():
    g["settings"]["background_color"] = ""          # the dark group ground showed under the new captions
save(p, h, d)
p = "theme/templates/page.contact.json"; h, d = load(p)
main = d["sections"]["main"]
main["blocks"]["title"]["settings"]["text"] = "<p>Contact</p>"   # an h1 tag ignores the custom eyebrow size
st = main["blocks"]["statement"]["settings"]
st["type_preset"] = "h3"; st["text"] = "<h1>Write to us. A person in the atelier answers, usually within one working day.</h1>"
save(p, h, d)
print("fixes done")
