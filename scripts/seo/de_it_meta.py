"""Build German and Italian SEO titles/descriptions for active leather products (3 November 2026).
Input: src.json (id, title, mt, mtd, md, mdd) exported from translatableResources. Output: GraphQL mutations."""
import json, re, sys
src = json.load(open(sys.argv[1]))
B = " | Oberndörfer Milano"
C = {  # colour: (de, it)
 "Dark Green":("Dunkelgrün","Verde scuro"),"Grey":("Grau","Grigio"),"Yellow":("Gelb","Giallo"),"Blue":("Blau","Blu"),
 "Red":("Rot","Rosso"),"Green":("Grün","Verde"),"Black":("Schwarz","Nero"),"Turquoise & Black":("Türkis & Schwarz","Turchese e nero"),
 "Turquoise":("Türkis","Turchese"),"Orange":("Orange","Arancione"),"Brown":("Braun","Marrone"),"Dark Blue":("Dunkelblau","Blu scuro"),
 "Yellow and Brown":("Gelb & Braun","Giallo e marrone"),"Black and Yellow":("Schwarz & Gelb","Nero e giallo"),
 "Dark Green and Brown":("Dunkelgrün & Braun","Verde scuro e marrone"),"White and Blue":("Weiß & Blau","Bianco e blu"),
 "Cognac":("Cognac","Cognac"),"Light Brown":("Hellbraun","Marrone chiaro"),"Black/Khaki":("Schwarz oder Khaki","Nero o kaki"),
 "Chocolate":("Schokobraun","Cioccolato"),"Nude":("Nude","Nude"),"Lavender":("Lavendel","Lavanda"),"Pink":("Rosa","Rosa"),
 "Peach":("Pfirsich","Pesca"),"Purple":("Lila","Viola"),"Beige":("Beige","Beige"),"Multicolor Print":("Bunt bedruckt","Stampa multicolore"),
 "Light Blue":("Hellblau","Azzurro"),"Jeans Blue":("Jeansblau","Blu jeans"),"Pastel Blue":("Pastellblau","Azzurro pastello"),
 "Pastel Pink":("Pastellrosa","Rosa pastello"),"Navy Blue":("Marineblau","Blu navy"),"Cognac Suede":("Cognac-Wildleder","Camoscio cognac"),
 "Black Stud":("Schwarz mit Nieten","Nero con borchie"),"Black Classic":("Schwarz","Nero"),
}
def col(s):
    for k in sorted(C, key=len, reverse=True):
        if k.lower()==s.lower(): return C[k]
    raise KeyError(s)
def after_dash(t): return t.split(" - ",1)[1] if " - " in t else None
out = {}
for r in src:
    t, mt, pid = r["title"], r["mt"], r["id"]
    if t.startswith("Cotton Cap"): continue
    de = it = None
    if re.match(r"3-Place Watch Box", t) or "3-Watch Case" in mt:
        c = after_dash(t) or mt.split(" Leather Watch Box")[0]
        d,i = col(c)
        de=(f"Uhrenbox aus Leder für 3 Uhren – {d}", f"Uhrenbox für 3 Uhren in {d}, handgefertigt in Mailand aus italienischem Leder, mit weichem Futter für Ihre Uhren.")
        it=(f"Porta orologi in pelle per 3 orologi – {i}", f"Porta orologi per 3 orologi in {i.lower()}, fatto a mano a Milano in pelle italiana, con interno morbido per gli orologi.")
        if "Alcantara" in (r["md"] or ""):
            de=(de[0], f"Uhrenbox für 3 Uhren in {d} mit Alcantara-Futter, handgefertigt in Mailand.")
            it=(it[0], f"Porta orologi per 3 orologi in {i.lower()} con interno in Alcantara, fatto a mano a Milano.")
    elif t.startswith("8-Place XL"):
        de=("XL Uhrenbox aus Leder für 8 große Uhren","XL Uhrenbox für 8 große Uhren, handgefertigt in Mailand, mit 70-mm-Kissen für größere Gehäuse. Holzkern, italienisches Leder, Wildlederfutter.")
        it=("Porta orologi XL in pelle per 8 orologi grandi","Porta orologi XL per 8 orologi grandi, fatto a mano a Milano, con cuscini da 70 mm per casse più grandi. Anima in legno, pelle italiana, interno in suede.")
    elif t.startswith("8-Place Watch Box"):
        d,i = col(after_dash(t))
        if "Stud" in t:
            de=(f"Uhrenbox aus Leder für 8 Uhren – {d}","Uhrenbox für 8 Uhren aus schwarzem Saffiano-Leder, handgefertigt in Mailand: Holzkern, Samtfutter, Memory-Foam-Kissen, Messingnieten und -ecken.")
            it=(f"Porta orologi in pelle per 8 orologi – {i}","Porta orologi per 8 orologi in pelle Saffiano nera, fatto a mano a Milano: anima in legno, velluto, cuscini in memory foam, borchie e angoli in ottone.")
        else:
            de=(f"Uhrenbox aus Leder für 8 Uhren – {d}",f"Uhrenbox für 8 Uhren in {d}, handgefertigt in Mailand: Holzkern in italienischem Kalbsleder, Samtfutter, Memory-Foam-Kissen, Messingecken.")
            it=(f"Porta orologi in pelle per 8 orologi – {i}",f"Porta orologi per 8 orologi in {i.lower()}, fatto a mano a Milano: anima in legno in vitello italiano, velluto, cuscini in memory foam, angoli in ottone.")
    elif t.endswith("Leather Tray"):
        c = t.replace(" Leather Tray","").replace("White/Blue","White and Blue")
        d,i = col(c)
        de=(f"Taschenleerer aus Leder – {d}, handgefertigt in Italien",f"Taschenleerer aus italienischem Kalbsleder in {d}: ein fester Platz für Schlüssel, Geldbörse und Handy. Handgefertigt in Italien.")
        it=(f"Svuotatasche in pelle – {i}, fatto a mano in Italia",f"Svuotatasche in vitello italiano {i.lower()}: un posto fisso per chiavi, portafoglio e telefono. Fatto a mano in Italia.")
    elif t=="Blue Alligator Wallet":
        de=("Kartenetui aus Alligatorleder – Blau | Echtes Leder","Kartenetui aus echtem Alligatorleder in Blau, CITES-konform. Flach für die Vordertasche. In Italien von Hand genäht, auf Bestellung gefertigt.")
        it=("Portacarte in alligatore – Blu | Pelle autentica","Portacarte in vera pelle di alligatore blu, conforme CITES. Sottile, per la tasca davanti. Cucito a mano in Italia, su ordinazione.")
    elif t.startswith("Crocodile Wallet"):
        d,i = col(after_dash(t))
        de=(f"Geldbörse aus Krokodilleder – {d} | Echtes Leder",f"Geldbörse aus echtem Krokodilleder in {d}, CITES-konform. In Italien von Hand genäht und poliert. Flach, in kleinen Serien gefertigt.")
        it=(f"Portafoglio in coccodrillo – {i} | Pelle autentica",f"Portafoglio in vera pelle di coccodrillo {i.lower()}, conforme CITES. Cucito e rifinito a mano in Italia. Sottile, prodotto in piccole serie.")
    elif t=="Crocodile Passport Holder":
        de=("Reisepasshülle aus Krokodilleder – Grün | Echtes Leder","Reisepasshülle aus echtem Krokodilleder in Militärgrün, CITES-konform. Für Pass, Karten und Dokumente. Handgefertigt in Italien.")
        it=("Porta passaporto in coccodrillo – Verde | Pelle autentica","Porta passaporto in vera pelle di coccodrillo verde militare, conforme CITES. Per passaporto, carte e documenti. Fatto a mano in Italia.")
    elif t.startswith("Watch & Jewelry Box"):
        d,i = col(after_dash(t)); m_de = "Palladium" if "Palladium" in (r["md"] or "") else "Gold"; m_it = "palladio" if m_de=="Palladium" else "oro"
        de=(f"Uhren- und Schmuckbox aus Leder – {d}",f"Uhren- und Schmuckbox aus Kalbsleder in {d} mit Uhrenrolle im Inneren und Messing in {m_de}-Finish. Handgefertigt in Italien.")
        it=(f"Porta orologi e gioielli in pelle – {i}",f"Porta orologi e gioielli in vitello {i.lower()} con rotolo porta orologi interno e ottone finitura {m_it}. Fatto a mano in Italia.")
    elif t.startswith("The Mirror Handbag"):
        if "Ostrich" in t:
            de=("Handtasche mit Spiegel aus Straußenleder","Strukturierte Handtasche mit eingebautem Spiegel aus echtem Straußenleder, Palladium-Beschläge. In kleinen Serien in Italien handgefertigt.")
            it=("Borsa con specchio in pelle di struzzo","Borsa strutturata con specchio integrato in vera pelle di struzzo, finiture in palladio. Fatta a mano in Italia in piccole serie.")
        else:
            d,i = col(after_dash(t))
            de=(f"Handtasche mit Spiegel – {d} | Italienisches Leder","Strukturierte Lederhandtasche mit eingebautem Spiegel, Palladium-Verschluss mit Schloss und Kettenriemen. In Italien handgefertigt.")
            it=(f"Borsa con specchio – {i} | Pelle italiana","Borsa strutturata in pelle con specchio integrato, chiusura in palladio con lucchetto e tracolla a catena. Fatta a mano in Italia.")
    elif t=="Wine Holder Leather Box":
        de=("Weinträger aus Leder für zwei Flaschen","Weinträger für zwei Flaschen aus italienischem Nubuk-Kalbsleder, gefüttert, mit Riemen je Flasche, Messingnieten und -ecken. Handgefertigt in Italien.")
        it=("Porta vino in pelle per due bottiglie","Porta vino per due bottiglie in nabuk di vitello italiano, foderato, con cinghia per ogni bottiglia, borchie e angoli in ottone. Fatto a mano in Italia.")
    elif t.startswith("Nabuk Leather Jewelry Box"):
        d,i = col(after_dash(t))
        de=(f"Schmuckkasten aus Nubukleder – {d}",f"Schmuckkasten aus Nubukleder in {d} mit Alcantara-Futter und Fächern für Ringe, Ohrringe, Armbänder und Uhren. Handgefertigt in Italien.")
        it=(f"Portagioie in nabuk – {i}",f"Portagioie in nabuk {i.lower()} con interno in Alcantara e scomparti per anelli, orecchini, bracciali e orologi. Fatto a mano in Italia.")
    elif t=="Leather Jewelry Box - Beige & Brown":
        de=("Schmuckkasten aus Leder – Beige & Braun","Schmuckkasten aus Kalbsleder in Beige und Braun mit Alcantara-Futter. Handgefertigt in Italien.")
        it=("Portagioie in pelle – Beige e marrone","Portagioie in vitello beige e marrone con interno in Alcantara. Fatto a mano in Italia.")
    elif t=="Leather Necklace Box":
        de=("Kettenbox aus Leder mit Samtfutter","Kettenbox aus italienischem Kalbsleder mit goldfarbenen Nieten und Samtfutter. Handgefertigt in Italien, ein durchdachtes Geschenk.")
        it=("Porta collane in pelle con interno in velluto","Porta collane in vitello italiano con borchie dorate e interno in velluto. Fatto a mano in Italia, un regalo pensato.")
    elif t.startswith("Classic Leather Belt"):
        v = {"Brown":("Braun","Marrone"),"Handpainted":("Handbemalt","Dipinta a mano"),"Black, Round Buckle":("Schwarz, runde Schnalle","Nera, fibbia tonda"),"Black, Squared Buckle":("Schwarz, eckige Schnalle","Nera, fibbia quadrata")}
        k = re.split(r"\s*-\s*", t, 1)[1]; d,i = v[k]
        de=(f"Klassischer Ledergürtel – {d}","Klassischer Gürtel aus Vollnarbenleder mit Schnalle in Gunmetal. Handgefertigt in Italien, wird mit dem Tragen schöner.")
        it=(f"Cintura classica in pelle – {i}","Cintura classica in pelle pieno fiore con fibbia canna di fucile. Fatta a mano in Italia, migliora con l'uso.")
        if k=="Handpainted":
            de=(de[0],"Unikat: Gürtel aus Vollnarbenleder mit handbemalter Kante. Handgefertigt in Italien, keiner gleicht dem anderen.")
            it=(it[0],"Pezzo unico: cintura in pelle pieno fiore con bordo dipinto a mano. Fatta a mano in Italia, nessuna è uguale all'altra.")
    elif t=="Leather Belt Bag":
        de=("Gürteltasche aus Leder | Genarbtes Kalbsleder","Gürteltasche aus genarbtem Kalbsleder, an der Taille oder quer über die Brust getragen. Handgefertigt in Italien, mit Metallreißverschluss.")
        it=("Marsupio in pelle | Vitello martellato","Marsupio in vitello martellato, da portare in vita o a tracolla. Fatto a mano in Italia con zip in metallo lucido.")
    elif t=="Tote Leather Bag":
        de=("Tote Bag aus Leder, handgefertigt in Italien","Tote Bag aus Kalbsleder mit Baumwollfutter, handgefertigt in Italien. Strukturierte Form für jeden Tag.")
        it=("Borsa tote in pelle, fatta a mano in Italia","Borsa tote in vitello con fodera in cotone, fatta a mano in Italia. Silhouette strutturata per ogni giorno.")
    elif t=="Weekend Bag":
        de=("Weekender aus Leder | Graues italienisches Kalbsleder","Weekender aus grauem italienischem Kalbsleder mit verstärkten Griffen und verstellbarem Riemen. Handgefertigt in Italien, mit Baumwollfutter.")
        it=("Borsa weekend in pelle | Vitello italiano grigio","Borsa weekend in vitello italiano grigio con manici rinforzati e tracolla regolabile. Fatta a mano in Italia, foderata in cotone.")
    elif "Crochet Handbag" in t:
        d,i = col(after_dash(t)); mini = t.startswith("Mini")
        de=((("Mini-" if mini else "")+f"Häkelhandtasche – {d} | Handgemacht in Italien"), (f"Von Hand gehäkelte {'Mini-' if mini else ''}Handtasche in {d} mit goldfarbenem Kettenriemen. Handgemacht in Italien."))
        it=((("Mini borsa" if mini else "Borsa")+f" all'uncinetto – {i} | Fatta a mano in Italia"), (f"{'Mini borsa' if mini else 'Borsa'} all'uncinetto {i.lower()} lavorata a mano, con tracolla a catena dorata. Fatta a mano in Italia."))
    elif t=="Ostrich Mini Trunk Handbag":
        de=("Mini-Koffer-Handtasche aus Straußenleder","Mini-Koffer-Handtasche aus Straußenleder mit goldfarbenen Beschlägen. Echtes exotisches Leder, handgefertigt in Italien.")
        it=("Borsa mini baule in pelle di struzzo","Borsa mini baule in pelle di struzzo con finiture dorate. Vera pelle esotica, fatta a mano in Italia.")
    elif t=="Vault Bag":
        de=("Vault Bag | Koffertasche aus Leder","Strukturierte Ledertasche im Kofferstil mit abnehmbarem Riemen und Palladium-Beschlägen. Handgefertigt in Italien.")
        it=("Vault Bag | Borsa baule in pelle","Borsa in pelle strutturata a baule con tracolla removibile e finiture in palladio. Fatta a mano in Italia.")
    elif "Trax" in t:
        k = {"Necklace":("Kettenbox","Porta collane"),"Briefcase":("Aktentasche","Valigetta"),"Jewelry Box":("Schmuckbox","Portagioie"),"Gold Trunk":("Goldene Mini-Truhe","Mini baule oro")}
        key = next(x for x in k if t.startswith(x)); d,i = k[key]
        mat_de = "Kalbsleder" if key=="Gold Trunk" else "Vollnarbenleder"; mat_it = "Vitello" if key=="Gold Trunk" else "Pelle pieno fiore"
        de=(f"{d} x Trax NYC | Limitierte Edition",f"Limitierte {d} aus der Kollaboration Oberndörfer Milano x Trax NYC. {mat_de}, handgefertigt in Italien.")
        it=(f"{i} x Trax NYC | Edizione limitata",f"{i} in edizione limitata dalla collaborazione Oberndörfer Milano x Trax NYC. {mat_it}, fatto a mano in Italia.")
    elif t.startswith("Table Trunk"):
        blk = "Black" in t
        de=(("Lederkoffer als Couchtisch mit Fransen" + (" – Schwarz" if blk else "")),
            f"Reisekoffer nach alter Methode als niedriger Tisch, der sich öffnet: {'schwarzes ' if blk else ''}Vollnarben-Kalbsleder, Lederfransen, Palladium-Messing. 120 × 60 × 40 cm, auf Bestellung in Mailand.")
        it=(("Baule tavolino in pelle con frange" + (" – Nero" if blk else "")),
            f"Baule da viaggio costruito alla vecchia maniera come tavolino che si apre: vitello pieno fiore{' nero' if blk else ''}, frange in pelle, ottone palladiato. 120 × 60 × 40 cm, su ordinazione a Milano.")
    elif t=="Beauty Bag":
        de=("Kulturbeutel aus Leder | Beauty Bag","Beauty Bag aus schwarzem Kalbsleder mit Baumwollfutter und fester Form. Handgefertigt in Italien für Reise und Alltag.")
        it=("Beauty case in pelle","Beauty case in vitello nero con fodera in cotone e forma strutturata. Fatto a mano in Italia per il viaggio e ogni giorno.")
    elif t.startswith("SAC Alligator"):
        if "Himalaya" in t:
            de=("SAC Alligator – Himalaya | Rucksack aus Alligatorleder","Rucksack aus echtem Himalaya-Alligatorleder, CITES-konform. In Italien in äußerst begrenzter Stückzahl handgefertigt.")
            it=("SAC Alligatore – Himalaya | Zaino in alligatore","Zaino in vera pelle di alligatore Himalaya, conforme CITES. Fatto a mano in Italia in numero estremamente limitato.")
        else:
            d,i = col(after_dash(t))
            de=(f"SAC Alligator – {d} | Rucksack aus Alligatorleder",f"Rucksack aus echtem Alligatorleder in {d}, CITES-konform. In kleinen Serien in Italien handgefertigt.")
            it=(f"SAC Alligatore – {i} | Zaino in alligatore",f"Zaino in vera pelle di alligatore {i.lower()}, conforme CITES. Fatto a mano in Italia in piccole serie.")
    elif t.startswith("SAC - "):
        d,i = col(after_dash(t))
        de=(f"SAC – {d} | Rucksack aus Togo-Leder",f"Rucksack SAC aus Togo-Leder in {d} mit Palladium-Beschlägen, handgefertigt in Italien.")
        it=(f"SAC – {i} | Zaino in pelle Togo",f"Zaino SAC in pelle Togo {i.lower()} con finiture in palladio, fatto a mano in Italia.")
    elif t.startswith("Briefcase - "):
        d,i = col(after_dash(t))
        de=(f"Aktentasche – {d} | Togo-Leder",f"Aktentasche aus Togo-Leder in {d}, handgefertigt in Italien, mit Mikrofaserfutter und strukturierter Form.")
        it=(f"Valigetta – {i} | Pelle Togo",f"Valigetta in pelle Togo {i.lower()}, fatta a mano in Italia, con fodera in microfibra e silhouette strutturata.")
    elif t.startswith("BAG MODEL 017"):
        d,i = col(after_dash(t))
        de=(f"BAG MODEL 017 – {d} | Tote Bag aus Leder",f"Strukturierte Tote Bag aus Togo-Leder in {d}. BAG MODEL 017, handgefertigt in Italien für jeden Tag.")
        it=(f"BAG MODEL 017 – {i} | Borsa tote in pelle",f"Borsa tote strutturata in pelle Togo {i.lower()}. BAG MODEL 017, fatta a mano in Italia per ogni giorno.")
    elif t.endswith("Leather Coaster Set"):
        d,i = col(t.replace(" Leather Coaster Set",""))
        de=(f"Untersetzer aus Leder, 7er-Set – {d}",f"7 Untersetzer aus genarbtem Vollnarben-Kalbsleder in {d}, handgefertigt in Italien. Echtes Leder, rund zugeschnitten.")
        it=(f"Sottobicchieri in pelle, set da 7 – {i}",f"7 sottobicchieri in vitello pieno fiore martellato {i.lower()}, fatti a mano in Italia. Vera pelle, tagliati tondi.")
    elif t.endswith("Leather Pouf"):
        d,i = col(t.replace(" Leather Pouf",""))
        de=(f"Pouf aus Leder – {d} | Handgefertigt in Italien",f"Runder Pouf aus Kalbsleder in {d}, handgefertigt in Italien. Fußhocker, zusätzlicher Sitzplatz oder Blickfang.")
        it=(f"Pouf in pelle – {i} | Fatto a mano in Italia",f"Pouf rotondo in vitello {i.lower()}, fatto a mano in Italia. Poggiapiedi, seduta extra o pezzo d'arredo.")
    elif t.startswith("Leather Sofa"):
        d,i = col(after_dash(t))
        de=(f"Ledersofa – {d} | Vollnarben-Kalbsleder",f"Sofa aus Vollnarben-Kalbsleder in {d}, handgefertigt in Italien, mit Nubuk-Kissen und architektonischer Form.")
        it=(f"Divano in pelle – {i} | Vitello pieno fiore",f"Divano in vitello pieno fiore {i.lower()}, fatto a mano in Italia, con cuscini in nabuk e forma architettonica.")
    else:
        raise SystemExit("unmapped: "+t)
    out[pid] = (de, it)
E='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
parts=[]
for r in src:
    if r["id"] not in out: continue
    (dt,dd),(itt,itd) = out[r["id"]]
    tr=[]
    for loc,tt,dd2 in (("de",dt,dd),("it",itt,itd)):
        assert len(dd2)<=200, (dd2,len(dd2))
        tr.append('{locale:"%s",key:"meta_title",value:%s,translatableContentDigest:"%s"}'%(loc,json.dumps(tt+B,ensure_ascii=False),r["mtd"]))
        if r["mdd"]!=E: tr.append('{locale:"%s",key:"meta_description",value:%s,translatableContentDigest:"%s"}'%(loc,json.dumps(dd2,ensure_ascii=False),r["mdd"]))
    parts.append('p%s: translationsRegister(resourceId:"gid://shopify/Product/%s", translations:[%s]){ userErrors{ message } }'%(r["id"],r["id"],",".join(tr)))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
n=int(sys.argv[3])
for k in range(0,len(parts),n):
    open(sys.argv[2].replace('.json',f'_{k//n}.gql'),'w').write("mutation { "+" ".join(parts[k:k+n])+" }")
print(len(parts),"products")
