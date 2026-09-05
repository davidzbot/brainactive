"""Merge new_*.json parts -> brainactive_new_600_20260905.json + full QA."""
import json, glob, os, re, sys, io
import xml.dom.minidom as minidom

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

DOMAIN_TOPIC = {
    "numerical_reasoning": "Numerical Thinking",
    "logical_reasoning": "Logical Thinking",
    "pattern_abstract": "Pattern & Abstract",
    "visual_spatial": "Visual & Spatial",
    "verbal_reasoning": "Verbal Reasoning",
    "problem_solving": "Problem Solving",
}
LEVELS = {"Explore", "Think", "Challenge", "Master"}
DIFFS = {"easy", "medium", "hard"}
SCRATCH = ["wait,", " hmm", "bad item", "fixing", "let me", "recheck",
           "???", "todo", "fixme", "note to self", "scratch"]
SCRATCH_WORD = [r"\boops\b", r"\bwait\b", r"\bhmm\b"]

errors, warnings = [], []

# ---- load parts ----
parts = sorted(glob.glob(os.path.join(HERE, "new_*.json")))
all_qs = []
for p in parts:
    qs = json.load(open(p, encoding="utf-8"))
    assert isinstance(qs, list), p
    all_qs.extend(qs)
print(f"parts={len(parts)} total={len(all_qs)}")
if len(all_qs) != 600:
    errors.append(f"TOTAL != 600 (got {len(all_qs)})")

from collections import Counter
dc = Counter(q.get("domain") for q in all_qs)
print("per-domain:", dict(dc))
for d in DOMAIN_TOPIC:
    if dc.get(d, 0) != 100:
        errors.append(f"domain {d} has {dc.get(d,0)}, want 100")

# ---- per-question checks ----
ids = Counter()
qtexts = Counter()
for q in all_qs:
    qid = q.get("id", "?")
    ids[qid] += 1
    for f in ["id", "domain", "topic", "skill", "archetype", "level",
              "difficulty", "question_type", "question", "options",
              "answer", "explanation", "reasoning", "tags"]:
        if f not in q or q[f] in (None, "", []):
            errors.append(f"{qid}: missing/empty field {f}")
    if q.get("domain") in DOMAIN_TOPIC and q.get("topic") != DOMAIN_TOPIC[q["domain"]]:
        errors.append(f"{qid}: topic/domain mismatch")
    if q.get("level") not in LEVELS:
        errors.append(f"{qid}: bad level {q.get('level')}")
    if q.get("difficulty") not in DIFFS:
        errors.append(f"{qid}: bad difficulty")
    if q.get("question_type") != "multiple_choice":
        errors.append(f"{qid}: bad question_type")
    opts = q.get("options", [])
    if len(opts) != 4 or [o.get("id") for o in opts] != ["A", "B", "C", "D"]:
        errors.append(f"{qid}: options must be exactly A-D")
    else:
        texts = [str(o.get("text", "")).strip() for o in opts]
        if len(set(texts)) != 4:
            errors.append(f"{qid}: duplicate option texts {texts}")
        if any(not t for t in texts):
            errors.append(f"{qid}: empty option text")
        if q.get("answer") not in "ABCD":
            errors.append(f"{qid}: bad answer {q.get('answer')}")
    low = (q.get("question", "") + " " + q.get("explanation", "")).lower()
    for s in SCRATCH:
        if s in low:
            errors.append(f"{qid}: scratch marker '{s}' in text")
    for pat in SCRATCH_WORD:
        if re.search(pat, low):
            errors.append(f"{qid}: scratch word /{pat}/ in text")
    if q.get("visual_required") and not q.get("image_path"):
        warnings.append(f"{qid}: visual_required but no image_path")
    if q.get("image_path"):
        fn = os.path.join(HERE, "images", os.path.basename(q["image_path"]))
        if not os.path.exists(fn):
            errors.append(f"{qid}: image missing {fn}")
    qtexts[q.get("question", "").strip().lower()] += 1

dup_ids = [k for k, v in ids.items() if v > 1]
if dup_ids:
    errors.append(f"duplicate ids: {dup_ids}")
dup_q = [k for k, v in qtexts.items() if v > 1]
if dup_q:
    errors.append(f"duplicate question texts: {len(dup_q)}")

# answer distribution
ad = Counter(q.get("answer") for q in all_qs)
print("answer distribution:", dict(ad))

# level distribution per domain
for d in DOMAIN_TOPIC:
    lv = Counter(q["level"] for q in all_qs if q.get("domain") == d)
    print(f"  {d}: {dict(lv)}")

# ---- similarity vs production bank ----
prod = json.load(open(os.path.join(HERE, "..", "brainactive_p3_question_bank_production.json"),
                      encoding="utf-8"))["questions"]
def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()

prod_texts = [norm(q.get("question", "")) for q in prod]
prod_set = set(prod_texts)
exact_hits = 0
for q in all_qs:
    if norm(q.get("question", "")) in prod_set:
        exact_hits += 1
        errors.append(f"{q['id']}: EXACT duplicate of production question")
print(f"exact duplicates vs production: {exact_hits}")

def toks(s):
    return set(re.findall(r"[a-z0-9]+", s))
near = 0
for q in all_qs:
    a = toks(norm(q.get("question", "")))
    if not a:
        continue
    for p in prod_texts:
        b = toks(p)
        if not b:
            continue
        jac = len(a & b) / len(a | b)
        if jac > 0.85:
            near += 1
            warnings.append(f"{q['id']}: near-duplicate (jac={jac:.2f}): {q['question'][:60]}")
            break
print(f"near duplicates (jac>0.85) vs production: {near}")

# ---- svg validity ----
for f in glob.glob(os.path.join(HERE, "images", "*.svg")):
    try:
        minidom.parse(f)
    except Exception as e:
        errors.append(f"bad svg {os.path.basename(f)}: {e}")
print(f"svgs: {len(glob.glob(os.path.join(HERE, 'images', '*.svg')))} valid XML")

# ---- write merged file ----
out = {
    "meta": {"count": len(all_qs), "source": "new_600_20260905",
             "date": "2026-09-05",
             "note": "DRAFT - pending independent review + DB upload. 100/domain, MOE P3 HA / GEP-selection style."},
    "questions": all_qs,
}
out_path = os.path.join(HERE, "brainactive_new_600_20260905.json")
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", out_path, os.path.getsize(out_path), "bytes")

print(f"\nERRORS: {len(errors)}")
for e in errors[:50]:
    print("  E:", e[:220])
print(f"WARNINGS: {len(warnings)}")
for w in warnings[:20]:
    print("  W:", w[:200])
sys.exit(1 if errors else 0)
