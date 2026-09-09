"""Fix BA_P3_2366 double-answer: A and H both survive a left-right mirror. Use K instead."""
import json, os, io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

NEW_Q = "Which capital letter looks the same in a left-right mirror: K, F, H, R?"
NEW_OPTS = [{"id": "A", "text": "K"}, {"id": "B", "text": "F"},
            {"id": "C", "text": "H"}, {"id": "D", "text": "R"}]
NEW_EXP_TAIL = ("H is symmetric left-to-right: its mirror image is still H. "
                "K, F and R all change direction in the mirror.")

# upload JSON (DB mirror source of truth for text; keep tone opener already present)
up_path = os.path.join(HERE, "brainactive_new_600_upload.json")
ud = json.load(open(up_path, encoding="utf-8"))
for q in ud["questions"]:
    if q["id"] == "BA_P3_2366":
        assert "looks the same in a left-right mirror" in q["question"]
        q["question"] = NEW_Q
        q["options"] = NEW_OPTS
        assert q["answer"] == "C"
        # keep opener line, replace body
        lines = q["explanation"].split("\n")
        q["explanation"] = lines[0] + "\n\n" + NEW_EXP_TAIL
        print("upload fixed:", q["explanation"][:120])
json.dump(ud, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# part file (NEW_VIS_005? no - find by old question text)
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    qs = json.load(open(fn, encoding="utf-8"))
    dirty = False
    for q in qs:
        if "Which capital letter looks the same in a left-right mirror" in q["question"]:
            q["question"] = NEW_Q
            q["options"] = NEW_OPTS
            assert q["answer"] == "C"
            lines = q["explanation"].split("\n")
            q["explanation"] = lines[0] + "\n\n" + NEW_EXP_TAIL
            dirty = True
            print("part fixed:", base, q["id"])
    if dirty:
        json.dump(qs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# staging file
sp = os.path.join(HERE, "brainactive_new_600_20260905.json")
sd = json.load(open(sp, encoding="utf-8"))
for q in sd["questions"]:
    if "Which capital letter looks the same in a left-right mirror" in q["question"]:
        q["question"] = NEW_Q
        q["options"] = NEW_OPTS
        lines = q["explanation"].split("\n")
        q["explanation"] = lines[0] + "\n\n" + NEW_EXP_TAIL
        print("staging fixed:", q["id"])
json.dump(sd, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
