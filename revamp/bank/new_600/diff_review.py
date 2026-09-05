"""Compare upload file vs pristine part files: did reviewer change options/answers/questions?"""
import json, glob, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

parts = {}
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    for q in json.load(open(fn, encoding="utf-8")):
        parts[q["question"].strip()] = q

up = json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))["questions"]
print("upload n =", len(up))

missing, opt_diff, ans_diff, expl_diff = [], [], [], []
for q in up:
    p = parts.get(q["question"].strip())
    if not p:
        missing.append(q["id"])
        continue
    po = [(o["id"], o["text"]) for o in p["options"]]
    uo = [(o["id"], o["text"]) for o in q["options"]]
    if po != uo:
        opt_diff.append(q["id"])
    if p["answer"] != q["answer"]:
        ans_diff.append((q["id"], p["id"], p["answer"], q["answer"]))
    if (p["explanation"] or "").strip() != (q["explanation"] or "").strip():
        expl_diff.append(q["id"])

print("questions missing from parts:", len(missing), missing[:5])
print("option-text/order diffs:", len(opt_diff), opt_diff[:10])
print("answer diffs:", len(ans_diff))
for a in ans_diff[:20]:
    print("  ", a)
print("explanation diffs:", len(expl_diff))
