"""3 Sept 2026 — house style on Custom & Limited Editions (page handle trax-nyc)."""
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
_, bsp = load("theme/templates/page.bespoke.json")
CAP = bsp["sections"]["section_process"]["blocks"]["steps"]["blocks"]["step_1"]["blocks"]["num"]

p = "theme/templates/page.custom-limited-editions.json"; h, d = load(p)
S = d["sections"]

def chapter(sid, head_bid, body_bid, eyebrow, head, body_html=None, centred=True):
    sec = S[sid]
    hb = find(sec["blocks"], head_bid); hb["settings"].update(STATEMENT); hb["settings"]["text"] = f"<p>{head}</p>"
    hb["settings"]["width"] = "100%"; hb["settings"]["alignment"] = "center" if centred else "left"
    bb = find(sec["blocks"], body_bid); bb["settings"]["width"] = "100%"; bb["settings"]["alignment"] = "center" if centred else "left"
    if body_html: bb["settings"]["text"] = body_html
    if eyebrow and "eyebrow" not in sec["blocks"]:
        e = copy.deepcopy(CAP); e["settings"]["text"] = f"<p>{eyebrow}</p>"; e["settings"]["width"] = "100%"; e["settings"]["alignment"] = "center" if centred else "left"
        sec["blocks"] = {"eyebrow": e, **sec["blocks"]}; sec["block_order"] = ["eyebrow"] + sec["block_order"]

# Opening statement
chapter("section_VUyT6E", "text_LDkdGC", "text_CLYKCg", None, "One of each")

# Trax NYC chapter + the page's one primary button
chapter("section_mePnPJ", "text_BGAWV7", "text_4J3W7D", "Trax NYC × Oberndörfer Milano", "Four designs, one example of each",
  "<p>Trax NYC is a custom jeweller in Manhattan’s Diamond District. We met over a practical problem: how to carry pieces of real value discreetly, and present them well the moment the case opens. The answer became a small line in full-grain calf, lined in red Alcantara, with solid brass galvanised in gold: a jewellery box, a necklace trunk, a briefcase and a mini trunk. Once a piece is sold, it is not made again.</p>")
find(S["section_mePnPJ"]["blocks"], "button_ThVC6C")["settings"]["label"] = "See the four pieces"

# Limited editions, without repeating the opening
chapter("section_pp74hq", "text_YBMhii", "text_3bBLbc", "Limited editions", "A fixed run, then nothing",
  "<p>Each edition is a small, fixed run. When the last piece is sold, the design is retired; it does not come back in a new colour or a second season. The current edition is the Trax NYC line, available at Trax NYC on 47th Street and here. New editions are announced on this page and in Letters from Milan.</p>")
S["section_pp74hq"]["settings"]["padding-block-start"] = 80; S["section_pp74hq"]["settings"]["padding-block-end"] = 24

# Materials and making, shortened to what the accordion does not say
chapter("section_trax_materials_lead", "text_trax_materials_lead_head", "text_trax_materials_lead_body", "Materials and making", "Calf, red Alcantara, brass in gold",
  "<p>The line is built the way we build a trunk: full-grain calf over a rigid case, the lining cut and glued by hand, the corners, studs and locks in solid brass galvanised in gold. Made in the ateliers around Milan, one piece at a time.</p>")
S["section_trax_materials_lead"]["settings"]["padding-block-start"] = 72

# Captions under the two photographs
sec = S["section_KHbMTA"]
for gid, text in {"group_zpU7Tr": "The crocodile case, in green", "group_cwMnda": "At the bench, in Milan"}.items():
    g = sec["blocks"][gid]
    if "cap" not in g["blocks"]:
        c = copy.deepcopy(CAP); c["settings"]["text"] = f"<p>{text}</p>"; c["settings"]["padding-block-start"] = 12
        g["blocks"]["cap"] = c; g["block_order"] = g["block_order"] + ["cap"]
        g["settings"]["vertical_alignment_flex_direction_column"] = "flex-start"; g["settings"]["horizontal_alignment_flex_direction_column"] = "flex-start"
        g["settings"]["gap"] = 0; g["settings"]["background_color"] = ""

# Details accordion: sentence case, no repetition
sec = S["section_trax_accordion"]
hd = find(sec["blocks"], "text_trax_acc_head"); hd["settings"].update(STATEMENT); hd["settings"]["text"] = "<p>The details</p>"
acc = sec["blocks"]["accordion_trax_main"]["blocks"]
rows = {
  "accordion_row_trax_materials": ("The four pieces",
    "<p>A jewellery box with fitted compartments, so nothing touches anything else; a necklace trunk that is a presentation case and a strongbox in one; a structured briefcase that stands and keeps its shape; and a mini trunk, 25 by 14 by 8 centimetres, the one Trax uses for its gold giveaways. Each in full-grain calf, lined in red Alcantara, with solid brass hardware galvanised in gold.</p>"),
  "accordion_row_trax_story": ("The collaboration",
    "<p>Trax NYC works in fine jewellery; we work in leather. The line sits where the two meet: cases built the way a jeweller thinks about presentation and security, made the way we make everything else, by hand, one piece at a time.</p>"),
  "accordion_row_trax_availability": ("Availability and enquiries",
    "<p>Each design exists as a single piece. When it is sold it is not made again. To ask about a piece, or about a future collaboration, use the form below or write to info@oberndoerferco.com.</p>"),
}
for rid, (heading, text) in rows.items():
    acc[rid]["settings"]["heading"] = heading
    next(iter(acc[rid]["blocks"].values()))["settings"]["text"] = text

# Enquire
sec = S["section_trax_contact"]
hd = find(sec["blocks"], "text_trax_contact_head")
hd["settings"]["text"] = "<h2>Enquire</h2><p>Write to us about a piece from the line, or about a collaboration of your own. A person in the atelier answers.</p>"
sb = sec["blocks"]["contact_form_trax"]["blocks"]["submit-button"]["settings"]; sb["label"] = "Send"; sb["style_class"] = "button-secondary"
save(p, h, d); print("custom done")
