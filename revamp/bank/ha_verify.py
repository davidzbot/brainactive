import json, sys
sys.path.insert(0, "revamp/bank")
from ha_db import msql
bank = json.load(open("revamp/bank/brainactive_p3_question_bank_ha20260921.json", encoding="utf-8"))
byid = {q["id"]: q for q in bank["questions"]}
fix9 = ["BA_P3_0533", "BA_P3_0549", "BA_P3_0552", "BA_P3_0553", "BA_P3_0571", "BA_P3_0582", "BA_P3_0659", "BA_P3_G112", "BA_P3_0323"]
Q = chr(39)
st, data = msql("select id, explanation from public.brainactive_questions where id in (" + ", ".join(Q + i + Q for i in fix9) + ");")
print(st, "rows:", len(data))
bad = 0
for r in data:
    if r["explanation"] != byid[r["id"]]["explanation"]:
        print("MISMATCH:", r["id"])
        bad += 1
print("explanation mismatches:", bad)
st, data = msql("select id, domain, topic, skill, level, question, options, answer, is_active, qa_status from public.brainactive_questions where id in (" + Q + "BA_P3_HA_0001" + Q + ", " + Q + "BA_P3_HA_0205" + Q + ", " + Q + "BA_P3_HA_0310" + Q + ");")
for r in data:
    j = byid[r["id"]]
    ok = r["question"] == j["question"] and r["options"] == j["options"] and r["answer"] == j["answer"] and r["is_active"] is True
    print(r["id"], "match=" + str(ok), r["qa_status"])

