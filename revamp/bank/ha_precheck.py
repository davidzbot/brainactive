import json, collections, sys
sys.path.insert(0, "revamp/bank")
from ha_db import fetch_all, req, BASE
rows = fetch_all()
print("DB rows:", len(rows))
print("qa_status:", dict(collections.Counter(r.get("qa_status") for r in rows)))
print("is_active true:", sum(1 for r in rows if r.get("is_active") is True))
bank = json.load(open("revamp/bank/brainactive_p3_question_bank_ha20260921.json", encoding="utf-8"))
bmap = {q["id"]: q for q in bank["questions"]}
dbids = set(r["id"] for r in rows)
bank_live = [q["id"] for q in bank["questions"] if not str(q.get("qa_status", "")).startswith("rejected")]
print("bank live:", len(bank_live), "missing from DB:", len([i for i in bank_live if i not in dbids]))
newids = [q["id"] for q in bank["questions"] if q["id"].startswith("BA_P3_HA_")]
print("new HA ids:", len(newids), "already in DB:", len([i for i in newids if i in dbids]))
rej = [q["id"] for q in bank["questions"] if str(q.get("qa_status", "")).startswith("rejected") and q["qa_status"] != "rejected_duplicate"]
in_db_active = [r["id"] for r in rows if r["id"] in set(rej) and r.get("is_active") is True]
print("rejected-but-active in DB:", len(in_db_active), in_db_active[:10])
act = json.load(open("revamp/bank/ha_activate_20260921.json", encoding="utf-8"))["activate"]
in_db_inactive = [i for i in act if i in dbids and not [r for r in rows if r["id"] == i][0].get("is_active")]
print("activate-list already-active:", len(act) - len(in_db_inactive) - len([i for i in act if i not in dbids]), "to-activate:", len(in_db_inactive), "not-in-db:", len([i for i in act if i not in dbids]))
six = ["BA_P3_ADD_0047", "BA_P3_ADD_0048", "BA_P3_ADD_0049", "BA_P3_ADD_0050", "BA_P3_ADD_0091", "BA_P3_ADD_0092"]
st, data = req("GET", BASE + "?select=id,image_path&id=in.(" + ",".join(six) + ")")
print("six image_paths:", data)

