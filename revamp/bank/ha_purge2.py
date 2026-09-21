import json
purge = set(json.load(open("revamp/bank/ha_purge_ids.json", encoding="utf-8")))
bank = json.load(open("revamp/bank/brainactive_p3_question_bank_ha20260921.json", encoding="utf-8"))
brej = set(q["id"] for q in bank["questions"] if str(q.get("qa_status", "")).startswith("rejected"))
bhold = set(q["id"] for q in bank["questions"] if q.get("qa_status") == "needs_option_fix_20260921")
act = set(json.load(open("revamp/bank/ha_activate_20260921.json", encoding="utf-8"))["activate"])
print("purge:", len(purge), "bank-rejected:", len(brej), "bank-hold:", len(bhold))
print("purge == rejected+hold:", purge == (brej | bhold))
print("purge only-not-in-bank:", sorted(purge - brej - bhold)[:10])
print("purge intersect activate:", sorted(purge & act)[:10])

