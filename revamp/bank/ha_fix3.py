import json
NEW = "revamp/bank/ha_new_20260921.json"
newqs = json.load(open(NEW, encoding="utf-8"))
FIX = [" NOT saves| NOT save", " NOT buys| NOT buy", " NOT builds| NOT build", " NOT finishes| NOT finish", " NOT reads| NOT read", " NOT learns| NOT learn", " NOT hears| NOT hear", " NOT lines| NOT line", " NOT walks| NOT walk"]
n = 0
for q in newqs:
    for pair in FIX:
        a, b = pair.split("|")
        for f in ("question", "explanation"):
            if a in q[f]:
                q[f] = q[f].replace(a, b)
                n += 1
        for o in q["options"]:
            if a in o["text"]:
                o["text"] = o["text"].replace(a, b)
                n += 1
json.dump(newqs, open(NEW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("grammar replacements:", n)

