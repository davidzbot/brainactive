"""Rotate option order to balance answer letters A/B/C/D ~150 each."""
import json, glob, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"NEW_VER_093", "NEW_VER_094", "NEW_VER_097"}

NEED_B_TO_A = 67
NEED_C_TO_D = 67
moved_b = moved_c = 0

for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    qs = json.load(open(fn, encoding="utf-8"))
    dirty = False
    for q in qs:
        if q.get("id") in SKIP:
            continue
        opts = q.get("options", [])
        if len(opts) != 4:
            continue
        if q.get("answer") == "B" and moved_b < NEED_B_TO_A:
            # rotate left: [B,C,D,A] -> correct now at A
            q["options"] = [opts[1], opts[2], opts[3], opts[0]]
            for i, L in enumerate("ABCD"):
                q["options"][i]["id"] = L
            q["answer"] = "A"
            moved_b += 1
            dirty = True
        elif q.get("answer") == "C" and moved_c < NEED_C_TO_D:
            # rotate right: [D,A,B,C] -> correct now at D
            q["options"] = [opts[3], opts[0], opts[1], opts[2]]
            for i, L in enumerate("ABCD"):
                q["options"][i]["id"] = L
            q["answer"] = "D"
            moved_c += 1
            dirty = True
    if dirty:
        json.dump(qs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("updated", base)
print(f"moved B->A: {moved_b}, C->D: {moved_c}")
