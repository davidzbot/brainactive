import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
dom = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
qs = [q for q in d["questions"] if q["domain"] == dom][lo:hi]
for q in qs:
    print("=" * 90)
    print(q["id"], q["level"], "| ans:", q["answer"])
    print("Q:", q["question"])
    print("OPTS:", " / ".join(o["id"] + ") " + o["text"] for o in q["options"]))
    print("EXP:", q["explanation"])
