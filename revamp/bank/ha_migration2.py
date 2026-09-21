import json
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
OUT = "supabase/migrations/20260921010000_brainactive_ha_qa_round2.sql"
d = json.load(open(BANK, encoding="utf-8"))
byid = {q["id"]: q for q in d["questions"]}
Q39 = chr(39)
def sq(v):
    if v is None:
        return "NULL"
    return Q39 + str(v).replace(Q39, Q39 + Q39) + Q39
lines = []
lines.append("-- BrainActive HA QA round 2 (2026-09-21): round-2 rejects, option-fix holds, explanation repairs.")
lines.append("-- All touched rows end inactive except the 9 explanation repairs, which keep their active flag.")
lines.append("")
D4 = ["BA_P3_0010", "BA_P3_0036", "BA_P3_0032", "BA_P3_0077", "BA_P3_0213", "BA_P3_0218", "BA_P3_0269", "BA_P3_ADD_0044"]
lines.append("update public.brainactive_questions")
lines.append("set qa_status = " + sq("rejected_too_simple") + ", is_active = false, updated_at = now()")
lines.append("where id in (" + ", ".join(sq(i) for i in D4) + ")")
lines.append("  and qa_status not like " + sq("rejected%") + ";")
lines.append("")
HOLD = ["BA_P3_0003", "BA_P3_0056", "BA_P3_0124", "BA_P3_0140", "BA_P3_0154", "BA_P3_0161", "BA_P3_0170", "BA_P3_0171", "BA_P3_0172", "BA_P3_0175", "BA_P3_0191", "BA_P3_0216", "BA_P3_0251", "BA_P3_0262", "BA_P3_ADD_0006", "BA_P3_ADD_0016", "BA_P3_ADD_0017", "BA_P3_ADD_0018", "BA_P3_ADD_0019", "BA_P3_ADD_0020", "BA_P3_ADD_0036", "BA_P3_ADD_0037", "BA_P3_ADD_0038", "BA_P3_ADD_0039", "BA_P3_ADD_0040", "BA_P3_ADD_0090", "BA_P3_ADD_0091"]
lines.append("update public.brainactive_questions")
lines.append("set qa_status = " + sq("needs_option_fix_20260921") + ", is_active = false, updated_at = now()")
lines.append("where id in (" + ", ".join(sq(i) for i in HOLD) + ")")
lines.append("  and qa_status not like " + sq("rejected%") + ";")
lines.append("")
FIX9 = ["BA_P3_0533", "BA_P3_0549", "BA_P3_0552", "BA_P3_0553", "BA_P3_0571", "BA_P3_0582", "BA_P3_0659", "BA_P3_G112", "BA_P3_0323"]
for k in FIX9:
    q = byid[k]
    lines.append("update public.brainactive_questions")
    lines.append("set explanation = " + sq(q["explanation"]) + ", updated_at = now()")
    lines.append("where id = " + sq(k) + ";")
    lines.append("")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)

