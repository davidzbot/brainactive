"""Final QA on brainactive_new_600_upload.json (post-restore)."""
import json, os, io, sys, re
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ud = json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))
qs = ud["questions"]
errs, warns = [], []

print("n =", len(qs))
ids = [q["id"] for q in qs]
if len(set(ids)) != 600:
    errs.append("duplicate ids")
if min(ids) != "BA_P3_1840" or max(ids) != "BA_P3_2439":
    errs.append(f"id range wrong: {min(ids)}..{max(ids)}")
if set(q.get("qa_status") for q in qs) != {"validated_new600_20260905"}:
    errs.append("qa_status wrong")

for q in qs:
    if len(q.get("options", [])) != 4 or [o.get("id") for o in q["options"]] != list("ABCD"):
        errs.append(f"{q['id']}: options")
    if len({o.get("text", '').strip() for o in q["options"]}) != 4:
        errs.append(f"{q['id']}: dup option text")
    if q.get("answer") not in "ABCD":
        errs.append(f"{q['id']}: answer")
    for f in ["domain", "topic", "skill", "level", "question", "explanation", "reasoning"]:
        if not q.get(f):
            errs.append(f"{q['id']}: empty {f}")
    e = q.get("explanation", "")
    if re.search(r"\d\?|\? (clockwise|anticlockwise)|midpoint \?|\(\w[^)]*\?\)", e):
        errs.append(f"{q['id']}: possible ? corruption: {e[:120]}")

# unicode health: expect arrows/multiplication present somewhere
n_arrow = sum(1 for q in qs if "→" in q.get("explanation", ""))
n_times = sum(1 for q in qs if "×" in q.get("explanation", ""))
n_div = sum(1 for q in qs if "÷" in q.get("explanation", ""))
n_chk = sum(1 for q in qs if "✓" in q.get("explanation", ""))
print(f"unicode health: arrows={n_arrow} times={n_times} div={n_div} checks={n_chk}")

# images
imgs = [(q["id"], q["image_path"]) for q in qs if q.get("image_path")]
print("image refs:", len(imgs))
for qid, ip in imgs:
    if not ip.startswith("p3/BA_P3_") or not ip.endswith(".svg"):
        errs.append(f"{qid}: bad image_path {ip}")
    if not os.path.exists(os.path.join(HERE, "..", "images", os.path.basename(ip))):
        # reviewer copied with BA_P3 names; check
        errs.append(f"{qid}: svg missing in bank/images")

# dupes vs production
prod = json.load(open(os.path.join(HERE, "..", "brainactive_p3_question_bank_production.json"),
                      encoding="utf-8"))["questions"]
pset = {re.sub(r"\s+", " ", q.get("question", "").lower()).strip() for q in prod}
exact = sum(1 for q in qs
            if re.sub(r"\s+", " ", q.get("question", "").lower()).strip() in pset)
print("exact dupes vs production:", exact)
if exact:
    errs.append(f"{exact} exact dupes")

print("answer dist:", dict(Counter(q.get("answer") for q in qs)))
print(f"\nERRORS: {len(errs)}")
for e in errs[:30]:
    print("  E:", e[:200])
sys.exit(1 if errs else 0)
