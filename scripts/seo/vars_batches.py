"""Turn deit.json + src.json into (document, variables) batches for translationsRegister."""
import json, sys
src={r["id"]:r for r in json.load(open(sys.argv[1]))}; out=json.load(open(sys.argv[2])); n=int(sys.argv[3])
E='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'; B=" | Oberndörfer Milano"
ids=list(out)
for b in range(0,len(ids),n):
    chunk=ids[b:b+n]; doc=[]; var={}; defs=[]
    for k,pid in enumerate(chunk):
        r=src[pid]; (dt,dd),(itt,itd)=out[pid]; tr=[]
        for loc,tt,ds in (("de",dt,dd),("it",itt,itd)):
            tr.append({"locale":loc,"key":"meta_title","value":tt+B,"translatableContentDigest":r["mtd"]})
            if r["mdd"]!=E: tr.append({"locale":loc,"key":"meta_description","value":ds,"translatableContentDigest":r["mdd"]})
        var[f"t{k}"]=tr; defs.append(f"$t{k}:[TranslationInput!]!")
        doc.append(f'a{k}: translationsRegister(resourceId:"gid://shopify/Product/{pid}", translations:$t{k}){{ userErrors{{ message }} }}')
    q="mutation("+",".join(defs)+"){ "+" ".join(doc)+" }"
    json.dump({"query":q,"variables":var},open(f"{sys.argv[4]}_{b//n}.json","w"),ensure_ascii=False)
