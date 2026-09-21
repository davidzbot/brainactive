import json, collections
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
qs = d["questions"]
issues = []
ids = [q["id"] for q in qs]
if len(ids) != len(set(ids)):
    issues.append("duplicate ids")
live = [q for q in qs if not str(q.get("qa_status", "")).startswith("rejected")]
REQ = ["id", "domain", "skill", "archetype", "level", "question_type", "question", "options", "answer", "explanation", "reasoning", "visual_required", "visual_spec", "image_path", "tags", "qa_status"]
for q in live:
    for f in REQ:
        if f not in q:
            issues.append((q["id"], "missing " + f))
    if len(q["options"]) != 4:
        issues.append((q["id"], "options != 4"))
    oids = [o["id"] for o in q["options"]]
    if len(set(oids)) != 4:
        issues.append((q["id"], "dup option ids"))
    if q["answer"] not in oids:
        issues.append((q["id"], "answer not in options"))
    if any(not isinstance(o["text"], str) for o in q["options"]):
        issues.append((q["id"], "non-string option"))
    if len(set(str(o["text"]).strip().lower() for o in q["options"])) < 4:
        issues.append((q["id"], "dup option texts"))
    if q["level"] not in ("Explore", "Think", "Challenge", "Master"):
        issues.append((q["id"], "bad level"))
    if q["visual_required"] and not q.get("visual_spec"):
        issues.append((q["id"], "visual no spec"))
    if q["visual_required"] and not q.get("image_path"):
        issues.append((q["id"], "visual no image"))
fps = collections.Counter((q["question"].strip().lower(), q["answer"]) for q in live)
dups = [x for x in fps.values() if x > 1]
print("total:", len(qs), "live:", len(live), "dup-fp:", len(dups), "issues:", len(issues))
for i in issues[:20]:
    print("ISSUE:", i)
print("VALIDATION", "PASS" if not issues and not dups else "FAIL")

