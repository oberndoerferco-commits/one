"""Pre-order on the older live theme ("NEW WEBSITE BUG FIX 1.2", Horizon 4.1.3), 8 September.

The owner put the older theme back live while the new one is still being fixed, and asked for the
T-shirt pre-order there too. This adds the same two pieces to that theme's generic templates
(the T-shirts' ready-to-wear template suffix does not exist on it, so they fall back to these):
a note above the buy button with the button relabelled "Pre-order", and a small "Pre-order"
line above the card photograph. Both only show on products tagged "preorder".

Input: templates/product.json and templates/collection.json pulled from the theme (the MCP
refuses writes to the live theme, so the output goes to a duplicate the owner publishes).
"""
import json, re, sys

def load(n):
    raw = open(n).read(); m = re.match(r"^\s*/\*.*?\*/\s*", raw, flags=re.S)
    return (m.group(0) if m else ""), json.loads(raw[m.end():] if m else raw)
def save(n, h, d): open(n, "w").write(h + json.dumps(d, indent=2, ensure_ascii=False) + "\n")

NOTE = ("{%- if product.tags contains 'preorder' -%}"
  "<div class=\"obm-preorder\" style=\"border-top:1px solid #d3cabc;border-bottom:1px solid #d3cabc;padding:14px 0;margin:4px 0 16px\">"
  "<p style=\"font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;margin:0 0 6px\">Pre-order</p>"
  "<p style=\"font-size:0.9375rem;line-height:1.6;margin:0\">Not in stock yet. The first run is being made in Italy now. Order today and it ships the moment the run arrives. We will email you the shipping date.</p>"
  "</div>"
  "<script>(function(){function fix(){document.querySelectorAll('button[name=\"add\"], .sticky-add-to-cart__button').forEach(function(b){var w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT),n;while((n=w.nextNode())){if(n.nodeValue.trim()==='Add to cart'){n.nodeValue=n.nodeValue.replace('Add to cart','Pre-order');}}});}"
  "fix();new MutationObserver(fix).observe(document.body,{childList:true,subtree:true,characterData:true});})();</script>"
  "{%- endif -%}")
EYE = ("{%- assign p = closest.product -%}{%- if p.tags contains 'preorder' -%}"
  "<p style=\"font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;opacity:0.6;margin:0 0 8px\">Pre-order</p>{%- endif -%}")

src = sys.argv[1] if len(sys.argv) > 1 else "."
h, p = load(f"{src}/product.json")
pd = p["sections"]["main"]["blocks"]["product-details"]
if "preorder_note" not in pd["blocks"]:
    pd["blocks"]["preorder_note"] = {"type": "custom-liquid", "settings": {"custom_liquid": NOTE}, "blocks": {}}
    buy = next(k for k, b in pd["blocks"].items() if b["type"] == "buy-buttons")
    pd["block_order"].insert(pd["block_order"].index(buy), "preorder_note")
save(f"{src}/product.new.json", h, p)

h, c = load(f"{src}/collection.json")
pc = c["sections"]["main"]["blocks"]["product-card"]
if "card_eyebrow" not in pc["blocks"]:
    pc["blocks"]["card_eyebrow"] = {"type": "custom-liquid", "settings": {"custom_liquid": EYE}, "blocks": {}}
    pc["block_order"].insert(0, "card_eyebrow")
save(f"{src}/collection.new.json", h, c)
