import json, collections, re
BANK = "revamp/bank/brainactive_p3_question_bank_production.json"
AUD = "revamp/bank/ha_audit_20260921.json"
NEW = "revamp/bank/ha_new_20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
aud = json.load(open(AUD, encoding="utf-8"))
newqs = json.load(open(NEW, encoding="utf-8"))
dels = set(k for k, x in aud.items() if x["verdict"] == "delete")
out = []
for q in d["questions"]:
    if q["id"] in dels:
        q = dict(q)
        q["qa_status"] = "rejected_too_simple"
        q["is_active"] = False
    out.append(q)
byid = set(q["id"] for q in out)
assert not (set(q["id"] for q in newqs) & byid), "id collision"
out.extend(newqs)
fps = collections.Counter((q["question"].strip().lower(), q["answer"]) for q in out if q.get("qa_status") != "rejected_duplicate")
dups = [fp for fp, n in fps.items() if n > 1]
print("total:", len(out), "new:", len(newqs), "rejected_too_simple:", sum(1 for q in out if q.get("qa_status") == "rejected_too_simple"))
print("dup fingerprints (non-rejected):", len(dups))
for fp in dups[:10]:
    print("DUP:", fp[0][:80], fp[1])
cjk = [q["id"] for q in out if re.search("[\u4e00-\u9fff]", q["question"] + q.get("explanation", ""))]
print("CJK questions:", len(cjk), cjk[:10])
json.dump({"meta": {"count": len(out), "source": "ha_purge_regen_20260921", "date": "2026-09-21", "deleted_ids": sorted(dels)}, "questions": out}, open("revamp/bank/brainactive_p3_question_bank_ha20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE revamp/bank/brainactive_p3_question_bank_ha20260921.json")

