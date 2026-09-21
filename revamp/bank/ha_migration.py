import json
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
OUT = "supabase/migrations/20260921000000_brainactive_ha_purge_regen.sql"
print("part1 ok")

d = json.load(open(BANK, encoding="utf-8"))
qs = d["questions"]
Q39 = chr(39)
def sq(v):
    if v is None:
        return "NULL"
    return Q39 + str(v).replace(Q39, Q39 + Q39) + Q39
def jv(v):
    if v is None:
        return "NULL"
    return sq(json.dumps(v, ensure_ascii=False))
def arr(v):
    if not v:
        return "ARRAY[]::text[]"
    return "ARRAY[" + ", ".join(sq(x) for x in v) + "]"

rej = [(q["id"], q["qa_status"]) for q in qs if str(q.get("qa_status", "")).startswith("rejected") and q["qa_status"] not in ("rejected_duplicate",)]
print("reject updates:", len(rej))
from collections import Counter
print(Counter(s for _, s in rej))
lines = []
lines.append("-- BrainActive HA purge + regen (2026-09-21).")
lines.append("-- Marks 382 low-quality items rejected+inactive; inserts 380 solver-verified HA replacements as inactive candidates.")
lines.append("-- New items stay is_active=false until human review sign-off (standing gate). Serving set otherwise unchanged.")
lines.append("")
for st in ("rejected_too_simple", "rejected_duplicate_options", "rejected_wrong_answer"):
    ids = sorted(i for i, s in rej if s == st)
    if not ids:
        continue
    lines.append("update public.brainactive_questions")
    lines.append("set qa_status = " + sq(st) + ", is_active = false, updated_at = now()")
    lines.append("where id in (" + ", ".join(sq(i) for i in ids) + ")")
    lines.append("  and qa_status not like " + sq("rejected%") + ";")
    lines.append("")
new = [q for q in qs if q["id"].startswith("BA_P3_HA_")]
print("inserts:", len(new))
TOPIC = {"numerical_reasoning": "Numerical Thinking", "logical_reasoning": "Logical Thinking", "pattern_abstract": "Pattern and Abstract", "visual_spatial": "Visual and Spatial", "verbal_reasoning": "Verbal Reasoning", "problem_solving": "Problem Solving"}
for q in sorted(new, key=lambda x: x["id"]):
    cols = ["id", "domain", "topic", "skill", "archetype", "level", "difficulty", "question_type", "question", "options", "answer", "explanation", "reasoning", "visual_required", "visual_spec", "image_path", "tags", "is_active", "qa_status"]
    vals = [sq(q["id"]), sq(q["domain"]), sq(q.get("topic") or TOPIC[q["domain"]]), sq(q["skill"]), sq(q.get("archetype", "")), sq(q["level"]), sq(q.get("difficulty", "")), sq(q.get("question_type", "multiple_choice")), sq(q["question"]), jv(q["options"]), sq(q["answer"]), sq(q["explanation"]), sq(q.get("reasoning") or ""), "true" if q.get("visual_required") else "false", jv(q.get("visual_spec")), sq(q.get("image_path")), arr(q.get("tags") or []), "false", sq(q["qa_status"])]
    lines.append("insert into public.brainactive_questions (" + ", ".join(cols) + ") values (" + ", ".join(vals) + ") on conflict (id) do nothing;")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)

