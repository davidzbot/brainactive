import json, collections
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
byid = {q["id"]: q for q in d["questions"]}
DELS4 = ["BA_P3_0010", "BA_P3_0036", "BA_P3_0032", "BA_P3_0077", "BA_P3_0213", "BA_P3_0218", "BA_P3_0269", "BA_P3_ADD_0044"]
HOLD = ["BA_P3_0003", "BA_P3_0056", "BA_P3_0124", "BA_P3_0140", "BA_P3_0154", "BA_P3_0161", "BA_P3_0170", "BA_P3_0171", "BA_P3_0172", "BA_P3_0175", "BA_P3_0191", "BA_P3_0216", "BA_P3_0251", "BA_P3_0262", "BA_P3_ADD_0006", "BA_P3_ADD_0016", "BA_P3_ADD_0017", "BA_P3_ADD_0018", "BA_P3_ADD_0019", "BA_P3_ADD_0020", "BA_P3_ADD_0036", "BA_P3_ADD_0037", "BA_P3_ADD_0038", "BA_P3_ADD_0039", "BA_P3_ADD_0040", "BA_P3_ADD_0090", "BA_P3_ADD_0091"]
for k in DELS4:
    assert k in byid, k
    byid[k]["qa_status"] = "rejected_too_simple"
    byid[k]["is_active"] = False
for k in HOLD:
    assert k in byid, k
    assert not str(byid[k].get("qa_status", "")).startswith("rejected"), k
    byid[k]["qa_status"] = "needs_option_fix_20260921"
GOOD_ST = ("validated_fix_20260831", "validated_baseline_v041", "validated_ha_20260921")
act = sorted(q["id"] for q in d["questions"] if q.get("qa_status") in GOOD_ST)
print("activate:", len(act))
live = [q for q in d["questions"] if not str(q.get("qa_status", "")).startswith("rejected")]
print("live:", len(live), "holds:", sum(1 for q in live if q["qa_status"] == "needs_option_fix_20260921"))
d["meta"]["finalize"] = {"date": "2026-09-21", "activate": len(act), "hold": 27, "deleted_r4": 8}
json.dump(d, open(BANK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"activate": act}, open("revamp/bank/ha_activate_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved bank + activate list")

