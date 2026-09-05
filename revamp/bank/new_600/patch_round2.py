"""Round 2: clean VER_065 explanation; replace NUM_023 with non-colliding variant."""
import json, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

# --- VER_065 explanation rewrite (in new_verbal_p3.json) ---
p = os.path.join(HERE, "new_verbal_p3.json")
qs = json.load(open(p, encoding="utf-8"))
for q in qs:
    if q["id"] == "NEW_VER_065":
        q["explanation"] = ("Read odd and even positions separately. Odd positions "
                            "(1st, 3rd, 5th, 7th): A, Z, C, X — front letters step A\u2192C "
                            "while back letters step Z\u2192X. Even positions (2nd, 4th, 6th, 8th): "
                            "B, Y, D, then the back letter steps Y\u2192W. So the 8th letter is W.")
json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("VER_065 explanation cleaned")

# --- NUM_023 replacement (in new_numerical_p2.json) ---
p = os.path.join(HERE, "new_numerical_p2.json")
qs = json.load(open(p, encoding="utf-8"))
for i, q in enumerate(qs):
    if q.get("id") == "NEW_NUM_023":
        q["question"] = "Find the next number: 4, 7, 12, 19, 28, ___?"
        q["options"] = [{"id": "A", "text": "37"}, {"id": "B", "text": "38"},
                        {"id": "C", "text": "39"}, {"id": "D", "text": "40"}]
        q["answer"] = "C"
        q["explanation"] = ("Gaps: +3, +5, +7, +9. The gaps grow by 2 each time, "
                            "so the next gap is +11: 28 + 11 = 39.")
        qs[i] = q
        break
json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("NUM_023 replaced")
