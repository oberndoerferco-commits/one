import json, subprocess, sys, os
targets = json.load(open("targets.json"))
want = sys.argv[1:]
res = {}
for t in targets:
    key = [p["value"] for p in t["parameters"] if p["name"] == "key"][0]
    fn = key.rsplit("/", 1)[1]                      # obm-tee-<name>-<colour>-<side>.jpg
    local = "out/" + fn.replace("obm-tee-", "")
    if want and not any(w in fn for w in want): continue
    if not os.path.exists(local): print("skip", local); continue
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}"]
    for p in t["parameters"]: cmd += ["-F", f'{p["name"]}={p["value"]}']
    cmd += ["-F", f"file=@{local};type=image/jpeg", t["url"]]
    code = subprocess.run(cmd, capture_output=True, text=True).stdout
    print(fn, code, flush=True); res[fn] = t["resourceUrl"]
json.dump(res, open("uploaded.json", "a") if False else open("uploaded-%s.json" % (want[0] if want else "all"), "w"), indent=1)
