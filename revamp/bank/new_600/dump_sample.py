import json, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
skip = set("""BA_P3_2116 BA_P3_1925 BA_P3_2433 BA_P3_2365 BA_P3_2162 BA_P3_2327""".split())
masters = {q["id"] for q in d["questions"] if q["level"] == "Master"}
pool = [q for q in d["questions"] if q["id"] not in skip and q["id"] not in masters]
random.seed(int(sys.argv[1]))
for q in random.sample(pool, 20):
    print("=" * 90)
    print(q["id"], q["domain"], q["level"], "| ans:", q["answer"])
    print("Q:", q["question"][:220])
    print("OPTS:", " / ".join(o["id"] + ") " + o["text"] for o in q["options"]))
    print("EXP:", q["explanation"][:400])
