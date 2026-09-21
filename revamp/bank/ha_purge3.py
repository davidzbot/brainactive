import json, sys
sys.path.insert(0, "revamp/bank")
from ha_db import msql
Q = chr(39)
purge = json.load(open("revamp/bank/ha_purge_ids.json", encoding="utf-8"))
print("to delete:", len(purge))
lines = []
lines.append("-- BrainActive purge unused questions (2026-09-21).")
lines.append("-- Hard-deletes 457 inactive rows: 430 rejected (too simple, duplicate options, wrong answer, duplicate) plus 27 option-fix holds.")
lines.append("-- Every deleted id was verified inactive and outside the 896-row activation set. Purge list: revamp/bank/ha_purge_ids.json.")
lines.append("")
for i in range(0, len(purge), 100):
    chunk = sorted(purge[i:i + 100])
    stmt = "delete from public.brainactive_questions where id in (" + ", ".join(Q + x + Q for x in chunk) + ") and is_active = false;"
    lines.append(stmt)
    st, data = msql(stmt)
    print("del batch", i, st, str(data)[:100])
    assert st == 201, data
open("supabase/migrations/20260921020000_brainactive_purge_unused.sql", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE migration")
st, data = msql("select count(*) as n from public.brainactive_questions;")
print("final count:", data)
st, data = msql("select qa_status, is_active, count(*) as n from public.brainactive_questions group by 1, 2 order by 3 desc;")
print(data)

