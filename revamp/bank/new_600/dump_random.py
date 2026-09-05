import json, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 20260905)
pick = random.sample(d["questions"], 6)
for q in pick:
    print("=" * 90)
    print(q["id"], q["domain"], q["level"], "| ans:", q["answer"])
    print("Q:", q["question"])
    print("OPTS:", " / ".join(o["id"] + ") " + o["text"] for o in q["options"]))
    print("EXP:", q["explanation"])
