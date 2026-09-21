import json, collections
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
keep = [q for q in d["questions"] if not str(q.get("qa_status", "")).startswith("rejected")]
drop = [q for q in d["questions"] if str(q.get("qa_status", "")).startswith("rejected")]
print("keep:", len(keep), "drop:", len(drop))
print(dict(collections.Counter(q["qa_status"] for q in drop)))
live = [q for q in keep if q.get("qa_status") != "needs_option_fix_20260921"]
print("activatable:", len(live))
d["questions"] = keep
d["meta"]["purged_rejected"] = {"date": "2026-09-21", "dropped": len(drop), "note": "rejected rows hard-deleted from DB and removed from bank; full record in git history and ha_audit_20260921.json"}
d["meta"]["count"] = len(keep)
json.dump(d, open(BANK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved, bank rows:", len(keep))

