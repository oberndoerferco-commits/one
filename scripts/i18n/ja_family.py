"""Build translationsRegister mutations for product families that share one text with a colour swapped in.
usage: python3 ja_family.py FAMILY.json > mutation.graphql
FAMILY.json: {"items":[{"id","colour_ja","digests":{key:digest}}], "fields":{key: template with {c}}}
"""
import json, sys
f = json.load(open(sys.argv[1]))
parts = []
for i, it in enumerate(f["items"]):
    tr = []
    for key, tpl in f["fields"].items():
        if key not in it["digests"]: continue
        v = tpl.replace("{c}", it["colour_ja"])
        tr.append('{locale:"ja", key:"%s", value:%s, translatableContentDigest:"%s"}' % (key, json.dumps(v, ensure_ascii=False), it["digests"][key]))
    parts.append('p%d: translationsRegister(resourceId:"%s", translations:[%s]){ userErrors{ message } }' % (i, it["id"], ",".join(tr)))
print("mutation {\n" + "\n".join(parts) + "\n}")
