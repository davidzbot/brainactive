import json, sys
sys.path.insert(0, "revamp/bank")
from ha_db import msql
Q = chr(39)
st, data = msql("select id, qa_status, is_active from public.brainactive_questions where is_active = false;")
print(st, "inactive rows:", len(data))
import collections
print(dict(collections.Counter(r["qa_status"] for r in data)))
st2, data2 = msql("select id from public.brainactive_questions where is_active = true;")
print("active rows:", len(data2))
json.dump([r["id"] for r in data], open("revamp/bank/ha_purge_ids.json", "w", encoding="utf-8"))
print("wrote purge id list")

