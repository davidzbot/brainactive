import json, sys
sys.path.insert(0, "revamp/bank")
from ha_db import msql
Q = chr(39)
act = json.load(open("revamp/bank/ha_activate_20260921.json", encoding="utf-8"))["activate"]
print("approved:", len(act))
st, data = msql("select id, qa_status, is_active from public.brainactive_questions where id in (" + ", ".join(Q + i + Q for i in act) + ");")
print(st, "approved present in DB:", len(data))
import collections
print(dict(collections.Counter((r["qa_status"], r["is_active"]) for r in data)))
present = set(r["id"] for r in data)
missing = [i for i in act if i not in present]
print("approved missing from DB:", len(missing))
newha = [i for i in missing if i.startswith("BA_P3_HA_")]
print("of which new HA:", len(newha), "kept-missing:", len(missing) - len(newha))
json.dump({"missing": missing}, open("revamp/bank/ha_activate_missing.json", "w", encoding="utf-8"))

