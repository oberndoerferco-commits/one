import json
src={p['id']:p for p in json.load(open('ja/src.json'))}
TRAYS={ # id: (en lead adjective phrase, de colour, it colour)
'8625501503813':('brown','braun','marrone'),
'8625514578245':('dark blue','dunkelblau','blu scuro'),
'8625517429061':('yellow and brown','gelb-braun','giallo e marrone'),
'8625603772741':('dark green','dunkelgrün','verde scuro'),
'8625605509445':('black and yellow','schwarz-gelb','nero e giallo'),
'8625607835973':('dark green and brown','dunkelgrün-braun','verde scuro e marrone'),
'8625609670981':('red','rot','rosso'),
'8625609965893':('white and blue','weiß-blau','bianco e blu'),
'8625613340997':('black','schwarz','nero'),
}
COAST={'16045606666565':('brown','braunen','marroni'),'16046416396613':('black','schwarzen','neri'),
'16046928953669':('blue','blauen','blu'),'16046961852741':('orange','orangen','arancioni')}
out={}
for i,(en,de,it) in TRAYS.items():
    first=src[i]['body'].split('</p>')[0]+'</p>'
    out[i]={'en': first+
"<p>A valet tray is the first thing you reach for when you come home: keys, wallet, watch, rings, coins and earbuds go in one place instead of across the dresser. In German it is called a Taschenleerer, in Italian a svuotatasche.</p>"
"<p>Leather is kinder to a watch case or a phone screen than wood, metal or ceramic, and calf leather softens and deepens in colour with use. It works on a hallway console, a bedside table or a desk.</p>"
"<h3>Questions</h3>"
"<p><strong>How do I care for it?</strong> Wipe it with a soft, dry cloth. Keep it away from water and long direct sunlight; if it gets wet, let it dry naturally, away from a radiator.</p>"
"<p><strong>Is it a good gift?</strong> Yes: it is used every day, suits any interior and fits men and women alike.</p>"
"<p>Handmade in Italy.</p>",
'de':f"<p>Dieser Taschenleerer aus Kalbsleder in {de.title()} gibt Schlüsseln, Geldbörse und Handy einen festen Platz – nichts liegt mehr verstreut auf der Kommode oder verschwindet unter einem Stapel.</p>"
"<p>Ein Taschenleerer – auf Englisch Valet Tray, auf Italienisch Svuotatasche – ist das Erste, wonach man beim Heimkommen greift: Schlüssel, Geldbörse, Uhr, Ringe, Münzen und Kopfhörer landen an einem Ort.</p>"
"<p>Leder schont Uhrengehäuse und Handydisplay besser als Holz, Metall oder Keramik, und Kalbsleder wird mit der Zeit weicher und tiefer im Ton. Passt auf die Flurkommode, den Nachttisch oder den Schreibtisch.</p>"
"<h3>Fragen</h3>"
"<p><strong>Wie pflege ich ihn?</strong> Mit einem weichen, trockenen Tuch abwischen. Von Wasser und langer direkter Sonne fernhalten; wird er nass, langsam und nicht an der Heizung trocknen lassen.</p>"
"<p><strong>Ist er ein gutes Geschenk?</strong> Ja: Er wird jeden Tag benutzt, passt zu jeder Einrichtung und eignet sich für Männer wie Frauen.</p>"
"<p>Handgefertigt in Italien.</p>",
'it':f"<p>Questo svuotatasche in vitello {it} dà a chiavi, portafoglio e telefono un posto fisso – niente più oggetti sparsi sul comò o persi sotto una pila.</p>"
"<p>Lo svuotatasche – in inglese valet tray, in tedesco Taschenleerer – è la prima cosa che si usa rientrando a casa: chiavi, portafoglio, orologio, anelli, monete e auricolari in un unico posto.</p>"
"<p>La pelle protegge la cassa dell'orologio e lo schermo del telefono meglio di legno, metallo o ceramica, e il vitello si ammorbidisce e si scurisce con l'uso. Sta bene su una consolle d'ingresso, un comodino o una scrivania.</p>"
"<h3>Domande</h3>"
"<p><strong>Come si cura?</strong> Con un panno morbido e asciutto. Tenerlo lontano dall'acqua e dal sole diretto prolungato; se si bagna, lasciarlo asciugare naturalmente, lontano dal termosifone.</p>"
"<p><strong>È un buon regalo?</strong> Sì: si usa ogni giorno, si adatta a ogni arredamento e va bene per uomo e donna.</p>"
"<p>Fatto a mano in Italia.</p>"}
for i,(en,de,it) in COAST.items():
    out[i]={'en': src[i]['body']+
"<h3>Questions</h3>"
"<p><strong>Do leather coasters work with cold drinks?</strong> Yes. Full-grain calf takes the condensation from a cold glass and keeps the table beneath dry. Wipe off standing water with a dry cloth.</p>"
"<p><strong>How do I care for them?</strong> Wipe with a soft cloth and let them dry flat. Over time the leather darkens slightly – that patina is part of real leather.</p>"
"<p><strong>Is a set a good gift?</strong> Yes – for a housewarming, a host or anyone who has everything. Seven pieces cover a dinner table or a bar.</p>",
'de':f"<p>Sieben Untersetzer aus genarbtem Vollnarben-Kalbsleder in {de[:-2].title()}. Jeder ist sauber rund geschnitten und dicht genug, um flach zu liegen und ein nasses Glas zu tragen, ohne den Tisch darunter zu markieren. Nichts ist aufgeklebt und nichts beschichtet: Das Leder selbst ist der Untersetzer.</p>"
"<p>Für Couchtisch, Schreibtisch oder Bar. Handgefertigt in Italien, in Schwarz, Braun, Blau und Orange.</p>"
"<h3>Fragen</h3>"
"<p><strong>Funktionieren Lederuntersetzer bei kalten Getränken?</strong> Ja. Vollnarbiges Kalbsleder nimmt das Kondenswasser eines kalten Glases auf und hält den Tisch trocken. Stehendes Wasser mit einem trockenen Tuch abwischen.</p>"
"<p><strong>Wie pflege ich sie?</strong> Mit einem weichen Tuch abwischen und flach trocknen lassen. Mit der Zeit dunkelt das Leder leicht nach – diese Patina gehört zu echtem Leder.</p>"
"<p><strong>Ist das Set ein gutes Geschenk?</strong> Ja – zum Einzug, für Gastgeber oder für jemanden, der schon alles hat. Sieben Stück reichen für eine Tafel oder eine Bar.</p>",
'it':f"<p>Sette sottobicchieri {it} in vitello pieno fiore martellato. Ognuno è un tondo pulito, abbastanza denso da restare piatto e reggere un bicchiere bagnato senza segnare il tavolo. Niente colla, niente rivestimenti: è la pelle stessa il sottobicchiere.</p>"
"<p>Per il tavolino, la scrivania, il bar. Fatti a mano in Italia, in nero, marrone, blu e arancione.</p>"
"<h3>Domande</h3>"
"<p><strong>I sottobicchieri in pelle vanno bene con le bevande fredde?</strong> Sì. Il vitello pieno fiore assorbe la condensa di un bicchiere freddo e tiene asciutto il tavolo. Asciugare l'acqua in eccesso con un panno asciutto.</p>"
"<p><strong>Come si curano?</strong> Con un panno morbido, lasciandoli asciugare in piano. Col tempo la pelle si scurisce leggermente: è la patina della vera pelle.</p>"
"<p><strong>Un set è un buon regalo?</strong> Sì – per una casa nuova, per chi ospita o per chi ha già tutto. Sette pezzi bastano per una tavola o un bar.</p>"}
json.dump(out,open('seo2/bodies.json','w'),ensure_ascii=False,indent=1)
# mutation
q='mutation{'+' '.join(f'p{n}: productUpdate(product:{{id:"gid://shopify/Product/{i}", descriptionHtml:{json.dumps(v["en"],ensure_ascii=False)}}}){{ userErrors{{ message }} }}' for n,(i,v) in enumerate(out.items()))+'}'
open('seo2/m_en.graphql','w').write(q); print(len(q))
