"""Six emails in the style of the Canva 'Cream and Brown Minimalist Fashion Email Newsletter':
brown bar, logo on cream, full-bleed photograph with a serif white line, cream body, pill button,
two photo tiles with serif labels. Copy from docs/email-drafts.md. One file per email."""
import html, os
CDN = "https://cdn.shopify.com/s/files/1/0758/8387/2581/files/"
def img(name, w=1200): return f"{CDN}{name}?width={w}"
LOGO = "https://www.oberndoerferco.com/cdn/shop/files/MILANO_13_x_4_cm_-6.svg?height=120&v=1785325361"
BAR, CREAM, INK, BROWN, MUTED, TILEBG = "#5f4534", "#efebe6", "#2b2320", "#6b4b36", "#7d7069", "#e3ddd5"

CSS = f"""
body{{margin:0;background:{TILEBG};font-family:Inter,'Helvetica Neue',Helvetica,Arial,sans-serif;color:{INK};-webkit-font-smoothing:antialiased}}
.wrap{{max-width:600px;margin:0 auto;background:{CREAM}}}
.bar{{height:26px;background:{BAR}}}
.logo{{padding:30px 0 26px;text-align:center}} .logo img{{height:40px}}
.hero{{position:relative;height:520px;background-size:cover;background-position:center}}
.hero .tint{{position:absolute;inset:0;background:rgba(72,50,34,.42)}}
.hero .h{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:0 56px;text-align:center}}
.hero h1{{font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-weight:400;color:#fff;font-size:44px;line-height:1.12;margin:0;letter-spacing:-0.01em;text-wrap:balance}}
.body{{padding:44px 56px 8px;text-align:center}}
.body p{{font-size:16px;line-height:1.7;margin:0 0 18px}}
.body p.left{{text-align:left}}
.eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};margin:0 0 14px}}
.btn{{display:inline-block;background:{BROWN};color:#fff !important;text-decoration:none;font-size:16px;font-weight:600;padding:16px 38px;border-radius:999px;margin:8px 0 40px}}
.piece{{display:flex;gap:16px;align-items:center;text-align:left;border-top:1px solid #d9d2c8;border-bottom:1px solid #d9d2c8;padding:18px 0;margin:8px 0 30px}}
.piece img{{width:76px;height:76px;object-fit:cover;background:#e9e8e3}}
.piece .t{{font-size:13px;letter-spacing:.08em;text-transform:uppercase}} .piece .s{{font-size:13px;color:{MUTED};margin-top:4px}}
.tiles{{display:flex;gap:16px;padding:0 36px 44px;background:linear-gradient({CREAM} 0 40%,{TILEBG} 40% 100%)}}
.tile{{flex:1;position:relative;height:330px;background-size:cover;background-position:center;text-decoration:none;overflow:hidden}}
.tile:after{{content:'';position:absolute;inset:auto 0 0 0;height:55%;background:linear-gradient(rgba(40,28,20,0) 0%,rgba(40,28,20,.62) 100%)}}
.tile span{{z-index:1;position:absolute;left:24px;bottom:22px;font-family:'Playfair Display',Georgia,serif;color:#fff;font-size:28px;text-shadow:0 1px 8px rgba(0,0,0,.35)}}
.foot{{background:{TILEBG};padding:8px 40px 36px;text-align:center;font-size:12px;color:{MUTED};line-height:1.7}}
.foot a{{color:{MUTED}}}
"""

def email(fname, title, hero, headline, paras, button, tiles, piece=None, eyebrow=None, preview=""):
    ps = "".join(f'<p class="{"left" if len(paras)>2 else ""}">{p}</p>' for p in paras)
    piece_html = "" if not piece else f'<div class="piece"><img src="{img(piece[0],240)}" alt=""><div><div class="t">{piece[1]}</div><div class="s">{piece[2]}</div></div></div>'
    tiles_html = "".join(f'<a class="tile" href="#" style="background-image:url({img(t[0],700)})"><span>{t[1]}</span></a>' for t in tiles)
    eb = f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else ""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div style="display:none;max-height:0;overflow:hidden">{preview}</div>
<div class="wrap">
  <div class="bar"></div>
  <div class="logo"><img src="{LOGO}" alt="Oberndörfer Milano"></div>
  <div class="hero" style="background-image:url({img(hero,1200)})"><div class="tint"></div><div class="h"><h1>{headline}</h1></div></div>
  <div class="body">{eb}{ps}{piece_html}<a class="btn" href="#">{button}</a></div>
  <div class="tiles">{tiles_html}</div>
  <div class="foot">Oberndörfer Milano · Milan, Italy · info@oberndoerferco.com<br><a href="#">Unsubscribe</a> · <a href="#">View in browser</a></div>
</div></body></html>"""
    open(f"out/{fname}.html","w").write(doc)

os.makedirs("out", exist_ok=True)
email("1a-abandoned-1h", "Your piece is still with us", "oberndoerfer-trunk-hardware-detail.jpg",
  "Your piece is still with us.",
  ["You left the Table Trunk in your cart. Nothing has moved: it is held for you, and the price you saw is the price it stays.",
   "Every piece is made by hand in our ateliers around Milan, so there is no rush on our side and no reason to hurry on yours. If a question stopped you, reply to this email and a person in the atelier will answer, usually within one working day."],
  "Return to your cart", [("oberndoerfer-about-craft-detail.jpg","Materials"),("gift_boxes.heic","Delivery")],
  piece=("obm-lane-ostrich-mini-trunk.jpg","Table Trunk - Black","Made to order · Free DHL Express, worldwide · 14 days to return"),
  preview="Nothing has moved. It is held for you.")
email("1b-abandoned-2d", "A note from the atelier", "oberndoerfer-cle-atelier-bench.jpg",
  "A note from the atelier.",
  ["The piece you looked at is still in your cart. Three things people ask us before they decide, in case one of them is yours.",
   "<strong>Where the leather comes from.</strong> Full-grain hides from tanneries in Italy, France and Germany. The hardware is solid brass, finished in palladium or gold.",
   "<strong>How it travels.</strong> Free with DHL Express, wherever you are, in a box made by hand in Italy. Fourteen days from delivery to return it if it is not right.",
   "<strong>Whether it can be made yours.</strong> Most pieces can be made in another hide or colour, or marked with initials. Reply and tell us what you have in mind."],
  "Return to your cart", [("obm-lane-sac-black.jpg","Bags"),("oberndoerfer-trunk-hardware-detail.jpg","Trunks")],
  preview="In case a question stopped you.")
email("2a-welcome", "You are on the list", "Artisan.jpg",
  "You are on the list.",
  ["When a new piece opens on pre-order, you will hear before it is shown on the site, and you will be able to order first. Once a month, one letter from the atelier: a piece, a commission, a photograph from the bench. That is all.",
   "If you would like to know how the pieces are made, the next two letters cover it. If you would rather just wait for the pre-orders, that is fine too."],
  "See what is made now", [("obm-lane-sac-black.jpg","Bags"),("obm-lane-ostrich-mini-trunk.jpg","Trunks")],
  eyebrow="Welcome", preview="What that means, and what it does not.")
email("2b-materials", "What it is made of", "oberndoerfer-about-craft-detail.jpg",
  "What it is made of, and who makes it.",
  ["Every piece starts from the same two questions: what is this material, and who is making it by hand.",
   "<strong>The leather</strong> is full-grain, from tanneries in Italy, France and Germany: the outer layer of the hide, left uncorrected, so the grain you see is the grain the animal had. It takes on a patina rather than wearing out.",
   "<strong>The hardware</strong> is solid brass, finished in palladium or gold, chosen because it can be repaired and re-plated in twenty years rather than replaced.",
   "<strong>The making</strong> happens in small ateliers around Milan, to order, in small batches. There is no factory floor and no stock room."],
  "Materials & Craftsmanship", [("oberndoerfer-trunk-hardware-detail.jpg","Hardware"),("oberndoerfer-cle-workshop-trunks.jpg","The atelier")],
  eyebrow="Handmade in Milan", preview="Two questions we ask of every piece.")
email("2c-miramare", "The trunk that became a table", "oberndoerfer-aol-lobby.jpg",
  "The trunk that became a table.",
  ["The first piece we made for a room rather than a person was a trunk, built for Miramare The Palace in Sanremo, on the Ligurian coast. It was meant to travel. It stayed, and became a table, and the hotel's public rooms are furnished with what followed.",
   "Our pieces are on show there now, and for sale. If you are on the coast, it is the best way to see the work before deciding on anything. Everything else is on the site, made to order and sent free with DHL Express."],
  "Where to find us", [("oberndoerfer-aol-ensemble.jpg","Art of Living"),("obm-hoodie-om-grey-back-v2.jpg","Ready to Wear")],
  eyebrow="Miramare The Palace, Sanremo", preview="Where the house began, and where the pieces are now.")
email("3-october-letter", "From the atelier, October", "obm-hoodie-om-grey-back-v2.jpg",
  "From the atelier, October.",
  ["One letter a month, as promised. This is the first.",
   "<strong>Three hoodies, on pre-order.</strong> The wordmark at the chest, the interlocking O and M across the back, and the star lattice, on a heavyweight cotton hoodie in grey, black or white. Made in Italy in a small run; order today and it ships the moment the run arrives. You are reading this before it is shown on the site.",
   "<strong>A trunk in progress.</strong> [One paragraph from the bench, written by the house each month.]",
   "<strong>The box.</strong> A piece leaves Milan wrapped in something made much the same way it was: boxes, labels and tags made by hand in Italy."],
  "The hoodies", [("obm-hoodie-lattice-black-back-v2.jpg","Hoodies"),("gift_boxes.heic","The Art of Packaging")],
  eyebrow="October 2026", preview="Three hoodies, one trunk, and a box.")
print(sorted(os.listdir("out")))
