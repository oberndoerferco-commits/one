"""3 Sept 2026 — visual design + writing-style pass on the story pages of the Claude theme.

House style applied here (documented in docs/website-design-review.html):
  * eyebrow   = Inter 12px, uppercase, loose tracking (text block, custom preset)
  * chapter   = Marcellus 32px, sentence case (h3 preset; type_font_h3 -> heading)
  * chapters vertically centred, not stretched top-to-bottom
  * one primary button per page; chapter calls-to-action are text links
Run from the repo root. Idempotent.
"""
import json, re, copy, pathlib

HDR = re.compile(r"(/\*.*?\*/\s*)", re.S)

def load(p):
    s = pathlib.Path(p).read_text()
    m = HDR.match(s)
    return (m.group(1) if m else ""), json.loads(s[m.end():] if m else s)

def save(p, hdr, d):
    pathlib.Path(p).write_text(hdr + json.dumps(d, indent=2, ensure_ascii=False) + "\n")

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

def set_text(d, sid, bid, text):
    b = find(d["sections"][sid]["blocks"], bid); b["settings"]["text"] = text

def restyle(d, sid, bid, style):
    b = find(d["sections"][sid]["blocks"], bid); b["settings"].update(style)

def centre_chapters(d):
    for sid, sec in d["sections"].items():
        if sec["type"] == "media-with-content":
            c = sec["blocks"].get("content")
            if c: c["settings"]["vertical_alignment_flex_direction_column"] = "center"

# ---------- theme settings: h3 becomes a Marcellus heading ----------
p = "theme/config/settings_data.json"; h, d = load(p)
d["current"]["type_font_h3"] = "heading"
save(p, h, d)

# ---------- About us ----------
p = "theme/templates/page.about-us.json"; h, d = load(p)
centre_chapters(d)
set_text(d, "section_about_journey", "text_craftHead", "<p>A journey before the first piece</p>")
set_text(d, "media_with_content_a7znjk", "text_9nrqUG", "<p>The hide, accounted for</p>")
set_text(d, "section_about_bridge", "text_craftHead", "<p>From the trunk to the room</p>")
for sid, bid in [("media_with_content_a7znjk", "text_MRPdFD"), ("section_about_bridge", "text_craftCap")]:
    restyle(d, sid, bid, EYEBROW)
save(p, h, d)

# ---------- Art of Living ----------
p = "theme/templates/page.art-of-living.json"; h, d = load(p)
centre_chapters(d)
set_text(d, "section_aol_commission", "head", "<p>It began with our trunks in the lobby</p>")
set_text(d, "section_aol_materials", "head", "<p>Full-grain calf. Solid brass in palladium.</p>")
for sid in ("section_aol_commission", "section_aol_materials"): restyle(d, sid, "cap", EYEBROW)
for sid in ("section_aol_open", "section_aol_dark"): restyle(d, sid, "eyebrow", EYEBROW)
save(p, h, d)

# ---------- Materials & Craftsmanship ----------
p = "theme/templates/page.materials-craftsmanship.json"; h, d = load(p)
centre_chapters(d)
heads = {"section_mat_leathers": "Full-grain, left as it grew", "section_mat_exotics": "Crocodile, alligator, ostrich",
         "section_mat_hardware": "Solid brass, in palladium or gold", "section_mat_making": "The ateliers around Milan"}
for sid, t in heads.items():
    set_text(d, sid, "head", f"<p>{t}</p>"); restyle(d, sid, "cap", EYEBROW)
for sid, sec in d["sections"].items():
    if "eyebrow" in sec.get("blocks", {}): restyle(d, sid, "eyebrow", EYEBROW)
save(p, h, d)

# ---------- The Art of Packaging ----------
p = "theme/templates/page.the-art-of-packaging.json"; h, d = load(p)
centre_chapters(d)
set_text(d, "section_pack_made", "head", "<p>Boxes, labels and tags, held to the same standard</p>")
restyle(d, "section_pack_made", "cap", EYEBROW)
for sid, sec in d["sections"].items():
    if "eyebrow" in sec.get("blocks", {}): restyle(d, sid, "eyebrow", EYEBROW)
save(p, h, d)

# ---------- Leather care: the dek is a statement, not a chapter head ----------
p = "theme/templates/page.leather-care.json"; h, d = load(p)
restyle(d, "section_8rFnYR", "text_cff8d8", dict(STATEMENT, font_size="1.25rem"))
save(p, h, d)

# ---------- Bespoke ----------
p = "theme/templates/page.bespoke.json"; h, d = load(p)
centre_chapters(d)
chapters = [
    ("media_with_content_Cj4MHU", "text_G4zHLD", "text_7AQYhF", "text_YAThXt", "button_nzW68w",
     "Leather goods", "Leather goods, to your measure",
     "Bags, trunks, travel pieces, wallets and belts, in the hide, lining, hardware and dimensions you choose. "
     "A watch trunk is cut to the watches you own; a briefcase to the papers you carry."),
    ("media_with_content_nQWcyA", "text_YdkETc", "text_epnAKD", "text_qyRnVW", "button_ytbXGM",
     "Furniture", "Furniture, to the measure of the room",
     "Sofas, armchairs, poufs and tables in full-grain leather, made to fit the room they will stand in. "
     "The method is the one we use for a trunk; only the scale changes. The lobby of the Miramare began as one such conversation."),
    ("media_with_content_zVCMPY", "text_RpqiEn", "text_reXW3e", "text_NMgbdW", "button_XCAV9b",
     "Jewellery", "Jewellery, to your drawing",
     "Rings, bracelets and necklaces made to your drawing, or to ours. Cast, set and finished by hand in Milan, "
     "in the metals and stones you choose."),
]
for sid, cap, head, body, btn, capt, headt, bodyt in chapters:
    c = find(d["sections"][sid]["blocks"], cap); c["settings"].update(EYEBROW); c["settings"]["text"] = f"<p>{capt}</p>"
    hb = find(d["sections"][sid]["blocks"], head); hb["settings"]["type_preset"] = "h3"; hb["settings"]["text"] = f"<p>{headt}</p>"
    find(d["sections"][sid]["blocks"], body)["settings"]["text"] = f"<p>{bodyt}</p>"
    b = find(d["sections"][sid]["blocks"], btn); b["settings"]["style_class"] = "button-unstyled"; b["settings"]["label"] = "Begin a commission"

# "What we bring to it": a centred statement like the opening one
w = find(d["sections"]["section_hgPEK7"]["blocks"], "text_MBqUTP")
w["settings"].update(STATEMENT); w["settings"]["text"] = "<p>What we bring to it</p>"; w["settings"]["width"] = "100%"; w["settings"]["alignment"] = "center"

# How a commission works — a new four-step section modelled on the timing strip
close = d["sections"]["section_FRT4RP"]
strip = close["blocks"]["group_timing_strip"]
step_tpl = strip["blocks"]["timing_leather"]
steps = [
    ("01 · The conversation", "Write to us, call, or come and see us in Sanremo or New York. Tell us the piece, what it will hold or where it will stand, and who it is for."),
    ("02 · The drawing", "We send a drawing with dimensions, hide and lining samples, the hardware and a price. Nothing is cut until you have approved them."),
    ("03 · The making", "The piece is cut, stitched and finished by hand in ateliers around Milan. We send photographs as it takes shape. A bespoke piece is made for you alone and cannot be returned."),
    ("04 · The delivery", "Packed in a box made in Italy and sent insured, anywhere. Whatever we make, we repair: send a photograph and we quote per piece."),
]
sec = copy.deepcopy(close)
sec["settings"]["background_color"] = "{{ settings.color_palette.background }}"
sec["settings"]["padding-block-start"] = 72; sec["settings"]["padding-block-end"] = 72
sec["blocks"] = {}
head = copy.deepcopy(w); head["settings"]["text"] = "<p>How a commission works</p>"
sec["blocks"]["head"] = head
row = copy.deepcopy(strip); row["blocks"] = {}
row["settings"]["vertical_alignment"] = "flex-start"; row["settings"]["gap"] = 40
for i, (n, t) in enumerate(steps, 1):
    g = copy.deepcopy(step_tpl); g["settings"]["horizontal_alignment"] = "flex-start"; g["settings"]["horizontal_alignment_flex_direction_column"] = "flex-start"; g["settings"]["gap"] = 12
    num = g["blocks"]["text_duration"]; num["settings"].update(EYEBROW); num["settings"]["text"] = f"<p>{n}</p>"; num["settings"]["alignment"] = "left"
    body = g["blocks"]["text_label"]; body["settings"]["type_preset"] = "rte"; body["settings"]["text"] = f"<p>{t}</p>"; body["settings"]["alignment"] = "left"; body["settings"]["width"] = "100%"; body["settings"]["max_width"] = "normal"
    g["blocks"] = {"num": num, "body": body}; g["block_order"] = ["num", "body"]
    row["blocks"][f"step_{i}"] = g
row["block_order"] = [f"step_{i}" for i in range(1, 5)]
sec["blocks"]["steps"] = row; sec["block_order"] = ["head", "steps"]
d["sections"]["section_process"] = sec
if "section_process" not in d["order"]:
    d["order"].insert(d["order"].index("section_hgPEK7"), "section_process")

# The choices — sentence case, house voice
ch = find(d["sections"]["section_JRRjMP"]["blocks"], "text_cBpFEM"); ch["settings"].update(STATEMENT); ch["settings"]["text"] = "<p>The choices</p>"
acc = d["sections"]["section_JRRjMP"]["blocks"]["accordion_nHzCXk"]["blocks"]
copy_ = {
  "accordion_row_ckeaED": ("Leathers and linings",
    "<p>Calf, goat and suede from family tanneries in Italy, France and Germany, in the colours we keep every year and the ones we add each season. Printed and embossed grains on request. Crocodile, alligator and ostrich come with CITES papers.</p><p>Linings in suede, Alcantara, smooth nappa or canvas.</p>"),
  "accordion_row_bDx9nJ": ("Initials, monograms and marks",
    "<p>Initials or a monogram are hot-stamped in gold or silver foil, or blind. A logo or a drawing is stamped digitally. You see a proof before anything touches the leather.</p>"),
  "accordion_row_HfL3rc": ("Hardware",
    "<p>Solid brass, galvanised in gold, palladium or black PVD. The locks, corners, feet and studs are the same pieces we use on the trunks.</p>"),
  "accordion_row_WNVVCa": ("Where it is made",
    "<p>Every piece is cut, stitched and finished by hand in ateliers around Milan, by people we chose after visiting them. The hide is documented from tannery to bench; papers for exotic leathers are available on request.</p>"),
}
for rid, (heading, text) in copy_.items():
    acc[rid]["settings"]["heading"] = heading
    next(iter(acc[rid]["blocks"].values()))["settings"]["text"] = text

# Timing strip and close band
for gid, dur, lab in [("timing_leather", "4–6 weeks", "Leather goods and boxes"), ("timing_furniture", "1–2 months", "Furniture"), ("timing_commission", "4–6 months", "Complex commissions")]:
    g = strip["blocks"][gid]
    g["blocks"]["text_duration"]["settings"].update(dict(STATEMENT, font_size="1.5rem")); g["blocks"]["text_duration"]["settings"]["text"] = f"<p>{dur}</p>"
    g["blocks"]["text_label"]["settings"].update(EYEBROW); g["blocks"]["text_label"]["settings"]["text"] = f"<p>{lab}</p>"
cl = find(close["blocks"], "text_JmceR6")
cl["settings"]["text"] = ("<h2>Begin a commission</h2><p>Tell us what you have in mind: the piece, the room, or the person it is for. "
                          "We reply personally, with materials, dimensions and a realistic timeline. For anything urgent, write to info@oberndoerferco.com.</p>")
save(p, h, d)
print("done")

# ---------- Art of Living: captions under the three pieces (checked against the photographs) ----------
p = "theme/templates/page.art-of-living.json"; h, d = load(p)
sec = d["sections"]["section_aol_pieces"]
cap_src = find(d["sections"]["section_aol_commission"]["blocks"], "cap")
captions = {"p1": "The trunk that became a table", "p2": "The sofa under the arch", "p3": "Armchairs by the piano"}
for gid, text in captions.items():
    g = sec["blocks"][gid]
    if "cap" not in g["blocks"]:
        c = copy.deepcopy(cap_src); c["settings"].update(EYEBROW); c["settings"]["text"] = f"<p>{text}</p>"
        c["settings"]["padding-block-start"] = 12
        g["blocks"]["cap"] = c
        g["block_order"] = [k for k in g["block_order"] if k != "cap"] + ["cap"]
        g["settings"]["content_direction"] = "column"; g["settings"]["gap"] = 0
        g["settings"]["horizontal_alignment_flex_direction_column"] = "flex-start"
save(p, h, d)
print("captions done")
