import json, sys
sys.path.insert(0, "revamp/bank")
from ha_db import msql
Q = chr(39)
dels4 = ["BA_P3_0010", "BA_P3_0036", "BA_P3_0032", "BA_P3_0077", "BA_P3_0213", "BA_P3_0218", "BA_P3_0269", "BA_P3_ADD_0044"]
holds = ["BA_P3_0003", "BA_P3_0056", "BA_P3_0124", "BA_P3_0140", "BA_P3_0154", "BA_P3_0161", "BA_P3_0170", "BA_P3_0171", "BA_P3_0172", "BA_P3_0175", "BA_P3_0191", "BA_P3_0216", "BA_P3_0251", "BA_P3_0262", "BA_P3_ADD_0006", "BA_P3_ADD_0016", "BA_P3_ADD_0017", "BA_P3_ADD_0018", "BA_P3_ADD_0019", "BA_P3_ADD_0020", "BA_P3_ADD_0036", "BA_P3_ADD_0037", "BA_P3_ADD_0038", "BA_P3_ADD_0039", "BA_P3_ADD_0040", "BA_P3_ADD_0090", "BA_P3_ADD_0091"]
fix9 = ["BA_P3_0533", "BA_P3_0549", "BA_P3_0552", "BA_P3_0553", "BA_P3_0571", "BA_P3_0582", "BA_P3_0659", "BA_P3_G112", "BA_P3_0323"]
ids = dels4 + holds + fix9
q = "select id, qa_status, is_active from public.brainactive_questions where id in (" + ", ".join(Q + i + Q for i in ids) + ");"
st, data = msql(q)
print(st, "rows:", len(data))
for r in data:
    print(r["id"], r["qa_status"], "active=" + str(r["is_active"]))
json.dump(data, open("revamp/bank/ha_db_affected.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

