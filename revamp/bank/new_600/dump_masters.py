import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
ms = [q for q in d["questions"] if q["level"] == "Master"]
which = sys.argv[1] if len(sys.argv) > 1 else "all"
sel = ms if which == "all" else [q for q in ms if q["id"] in which.split(",")]
for q in sel:
    print("=" * 100)
    print(q["id"], "| answer:", q["answer"])
    print("Q:", q["question"])
    print("OPTS:", " / ".join(f"{o['id']}) {o['text']}" for o in q["options"]))
    print("EXP:", q["explanation"])
