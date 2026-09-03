"""Rewrites product descriptions in the house voice.
Reads the storefront products feed (prods.json), writes:
  docs/product-descriptions-after.json  - what was applied, by handle
  products.jsonl                         - bulk productUpdate variables
Products already in the house voice are left untouched (see KEEP note at end)."""
import json,re,sys
SRC=sys.argv[1]; OUT_JSONL=sys.argv[2]; OUT_JSON=sys.argv[3]
d=json.load(open(SRC))['products']
by_title={p['title']:p for p in d}
new={}  # handle -> html
def P(*paras): return "".join(f"<p>{x}</p>" for x in paras if x)
def col(title):
    m=re.search(r' - ([^-]+)$',title); return m.group(1).strip() if m else ''
def low(c): return c.lower().replace('&','and')
MADE="Made by hand in our ateliers around Milan."
for p in d:
    t=p['title']; ty=p['product_type']; c=col(t); h=p['handle']
    # ---- Briefcase
    if t.startswith('Briefcase - '):
        new[h]=P(f"A briefcase in {low(c)} Togo calf, the grained leather we use where a bag is handled every day: it resists scratching and takes on depth rather than wear. The form is structured, so it stands on its own and keeps its line when it is full.",
          "One main compartment, lined in soft microfibre, holds a laptop, documents and the day's things without a maze of pockets. Two rolled handles, cut from the same hide.",
          MADE,"Dimensions: L 40 × H 28 × D 9 cm")
    # ---- Coasters
    elif t.endswith('Leather Coaster Set'):
        cc=t.replace(' Leather Coaster Set','').lower()
        new[h]=P(f"Seven coasters cut from pebbled full-grain calf in {cc}. Each is a clean round, dense enough to sit flat and take a wet glass without marking the table beneath. Nothing is glued to them and nothing coats them: the leather is the coaster.",
          "For a coffee table, a desk, a bar. Made by hand in Italy, in black, brown, blue and orange.")
    # ---- Poufs
    elif t.endswith('Leather Pouf'):
        cc=t.replace(' Leather Pouf','').lower()
        new[h]=P(f"A round pouf upholstered in {cc} calf leather, made by hand in Italy. A footstool first, a seat when a room fills, and something to leave beside a chair the rest of the time. The leather is smooth and dense, chosen to be sat on daily and to gain a patina rather than lose its finish.",
          "Also made in black, brown, orange and navy blue, and in other leathers to order.")
    # ---- Leather Watch Box (3 watches, studs, Alcantara)
    elif t.startswith('Leather Watch Box - '):
        suede='Suede' in c; cname=low(c.replace(' Suede',''))
        skin=f"{cname} suede calf, softer to the hand than our grained boxes" if suede else f"{cname} grained calf"
        new[h]=P(f"A box for three watches in {skin}. Each watch sits in its own cushioned slot lined in Alcantara, the material we use wherever a case back must not be scratched and a watch must not slip. Silver-tone studs run along every edge; they reinforce the corners as much as they mark them. The hardware is solid brass galvanised in palladium, so it does not tarnish.",
          "It sits on a dresser or a nightstand and closes securely enough to travel inside a larger bag. Made by hand in Italy, in nine colours.")
    # ---- BAG MODEL 017
    elif t.startswith('BAG MODEL 017 - '):
        new[h]=P(f"The 017 is a large tote in {low(c)} Togo calf, the finely grained leather we use where a bag is carried daily: it resists scratching and deepens with use rather than wearing. The handle is not attached but formed, two curved panels rising out of the body, and the sides taper toward the base so the bag stands with a sculptural line.",
          "Inside, one open space with no compartments in the way, sized for everything a day needs. Made by hand in Italy in small batches.",
          "Dimensions: 39 × 32 × 14.5 cm")
    # ---- SAC (Togo)
    elif t.startswith('SAC - '):
        new[h]=P(f"SAC is a compact backpack in {low(c)} grained Togo calf, cut to the size of a day's carry and nothing more. Inside it is fully lined in smooth goat leather: a lining that lasts as long as the exterior, where most bags fail first, and a quiet contrast to the grain outside. The closure is a palladium-finished brass fitting.",
          "The straps are made to work two ways, so the same bag is worn on the back or carried across the body. Made by hand in Italy in small batches.",
          "Dimensions: L 19 × H 28 × D 9 cm")
    # ---- SAC Alligator / Himalaya
    elif t.startswith('SAC Alligator - ') or t.startswith('SAC Himalaya Alligator'):
        him=t.startswith('SAC Himalaya')
        skin=("SAC in Himalaya alligator. The hide is American alligator, Alligator mississippiensis, from licensed farms in Louisiana and Florida, sourced and traded under CITES; the Himalaya finish is dyed by hand from white at the centre to taupe at the edges, and no two hides grade the same way."
              if him else f"SAC in {low(c)} alligator: American alligator, Alligator mississippiensis, from licensed farms in Louisiana and Florida, sourced and traded under CITES. Each hide is selected by hand and carries its own scale pattern, so the bag you receive exists in this exact form once. The skin is dyed through in a single colour.")
        new[h]=P(skin+" The lining is smooth goat leather, the hardware palladium-finished brass, the strap a single flat shoulder strap.",
          "Alligator is among the most durable exotic skins there are, which is why it has been used for fine leather goods for over a century: it does not crack or peel, and it ages well. Made by hand in Italy in very small numbers.",
          "Dimensions: L 19 × H 28 × D 9 cm",
          "On delivery: every order in alligator requires CITES export documentation, a legal requirement for exotic leather. Please allow up to four weeks from the order date for the paperwork to be completed and shipping confirmed. Documentation travels with the piece and is available on request.")
    # ---- Table Trunk
    elif t.startswith('Table Trunk'):
        skin="black full-grain calf with black nubuck details" if c=='Black' else "orange full-grain calf with blue nubuck details"
        new[h]=P(f"The Table Trunk is a travel trunk built to the old method and put to a new use: a low table that opens. The body is wrapped in {skin}, finished with leather fringes along the base, and closes on solid brass hardware galvanised in palladium. Inside, a compartment lined in natural cotton canvas: storage that disappears when the lid is down.",
          "Every element, from the hand-stitched hide to the hardware, is made by hand in our ateliers around Milan. The same trunk stands in the lobby of the Miramare in Sanremo; see <a href=\"/pages/oberndorfer-x-miramare-sanremo\">Art of Living</a>.",
          "Dimensions: 120 × 60 × 40 cm. Made to order; other leathers, colours and dimensions on request.")
    # ---- Sofa
    elif t.startswith('Leather Sofa - '):
        new[h]=P(f"A sofa in {low(c)} full-grain calf, made entirely by hand in Italy: the frame, the upholstery and the finishing, by the same ateliers that make our trunks. The form is architectural, with wide arms, a low profile and deep seats. The body is pebbled calf, dense enough to keep its structure and to gain character rather than lose it. The cushions are nubuck, the same hide buffed to a fine nap, so the contrast is felt more than seen.",
          "Made to order, to your dimensions and in the leather and colour you choose; we also make for yachts and private aircraft. Write to info@oberndoerferco.com to begin.")
    # ---- Trax NYC
    elif t=='Briefcase x Trax NYC':
        new[h]=P("A briefcase made with the New York jeweller Trax NYC, built to carry pieces of value discreetly and to present them well when it is opened. Full-grain calf outside; red Alcantara inside, the lining a jeweller asks for because it will not scratch metal or stone. The hardware is solid brass galvanised in gold, and the form is structured, so it stands and keeps its shape however it is packed.",
          MADE+" One example exists; once it is sold it will not be made again.")
    elif t=='Jewelry Box x Trax Nyc':
        new[h]=P("A small jewellery trunk made with Trax NYC, for rings, chains and the pieces that travel with their owner. Full-grain calf outside, red Alcantara inside, with fitted compartments so nothing touches anything else. The hardware is solid brass galvanised in gold. It is made for a dresser, a boutique counter or a private showing, and it closes securely for the journey between them.",
          MADE+" One example exists; once it is sold it will not be made again.")
    elif t=='Necklace Box x Trax NYC':
        new[h]=P("A necklace trunk made with Trax NYC for collectors and dealers who carry high-value pieces to private showings: a presentation case and a strongbox in one. Full-grain calf outside, red Alcantara inside, so chains and settings rest on nap rather than a hard surface. The hardware is solid brass galvanised in gold.",
          MADE+" One example exists; once it is sold it will not be made again.")
    elif t=='Gold Trunk mini x Trax Nyc':
        new[h]=P("A mini trunk in calf leather with solid brass hardware galvanised in gold and an Alcantara lining, made with Trax NYC. It is the trunk Trax uses for its gold giveaways: small enough to carry, built like the large ones, and lined so that what it holds is protected. For jewellery, watches, or anything worth keeping close.",
          "Dimensions: L 25 × H 14 × W 8 cm. "+MADE+" One example exists; once it is sold it will not be made again.")
    # ---- Jewelry boxes
    elif t.startswith('Leather Jewelry Box'):
        new[h]=P("A jewellery box in beige and brown calf, lined in Alcantara so that nothing inside is scratched by what holds it. Separate compartments keep rings, earrings, bracelets and watches apart; nothing tangles. The clasp is solid metal finished in gold.",
          "Made by hand in Italy. A proper home for a collection, or the start of one.")
    elif t.startswith('Nabuk Leather Jewelry Box - '):
        new[h]=P(f"A jewellery box in {low(c)} Nabuk, the calf we buff to a fine, velvety nap: soft to the hand outside, and lined in Alcantara inside so that nothing is scratched by what holds it. Separate compartments keep rings, earrings, bracelets and watches apart; nothing tangles. The clasp is solid metal finished in gold.",
          "Made by hand in Italy. A proper home for a collection, or the start of one.")
    # ---- Sunglasses
    elif ty=='Sunglasses':
        S={
        'Black Geometric Sunglasses':("An angular, mid-profile frame in glossy black acetate: the classic structured shape with its corners sharpened.","solid dark"),
        'Black Oversized Square Sunglasses':("A large square frame in glossy black acetate, with the presence that only an oversized lens gives.","solid dark"),
        'Black Rectangle Sunglasses':("A mid-profile rectangular frame in jet black acetate: the shape that works on most faces and with most clothes.","solid dark"),
        'Black Slim Rectangle Sunglasses':("A low, slim rectangular frame in glossy black acetate, the lightest silhouette in the collection.","gradient grey"),
        'Black Square Sunglasses':("A mid-profile square frame in glossy black acetate, square without being severe.","solid dark"),
        'Green Rectangle Sunglasses':("A rectangular frame in transparent bottle-green acetate, an alternative to black or tortoise that reads almost neutral until the light comes through it.","solid dark"),
        'Grey Square Sunglasses':("A square frame in transparent crystal-grey acetate, the lightest colour in the collection and the quietest.","gradient grey"),
        'Tortoise Rectangle Sunglasses':("A rectangular frame in dark tortoise acetate, the pattern deep in the material rather than printed on it.","solid dark"),
        'Tortoise Square Sunglasses':("A square frame in dark tortoise acetate, the pattern deep in the material rather than printed on it.","gradient brown"),
        'Narcos Glasses - Bottle Green':("The Narcos is a heavy-gauge aviator with a geometric double bridge, here in hand-polished transparent bottle-green acetate: a frame with the weight and character of the 1980s, cut with more precision than the decade managed. The core wire is exposed through the crystal acetate, and the hinges are heavy multi-barrel.","solid rich brown, chosen for the depth they give to colour and contrast against the green frame"),
        'Narcos Glasses - Smoke Grey':("The Narcos is a heavy-gauge aviator with a geometric double bridge, here in hand-polished transparent smoke-grey acetate: a frame with the weight and character of the 1980s, cut with more precision than the decade managed. The core wire is visible through the crystal acetate, and the hinges are heavy multi-barrel.","gradient smoke, deep at the top and clear at the base"),
        }
        if t in S:
            shape,lens=S[t]
            hinge="" if t.startswith('Narcos') else " The hinges are reinforced multi-barrel, with a core wire running through the temples."
            new[h]=P(shape+" Cut and polished by hand in Italy from organic cellulose acetate."+hinge,
              f"The lenses are German Zeiss CR-39, {lens}: full UVA and UVB protection, an anti-reflective coating, and colour rendered as it is.",
              "Each pair comes in a hard case with a microfibre cloth and a certificate of origin.")
        else: print("sunglasses not matched:",t)
json.dump({h:new[h] for h in sorted(new)},open(OUT_JSON,'w'),indent=1,ensure_ascii=False)
with open(OUT_JSONL,'w') as f:
    for p in d:
        if p['handle'] in new: f.write(json.dumps({"input":{"id":f"gid://shopify/Product/{p['id']}","descriptionHtml":new[p['handle']]}},ensure_ascii=False)+"\n")
print(len(new),"products rewritten;",len(d)-len(new),"kept as they are")
import collections; print(collections.Counter(by_title[t]['product_type'] for t in by_title if by_title[t]['handle'] in new))
