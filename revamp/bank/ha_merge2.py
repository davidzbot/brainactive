import json, collections, re
BASE = "revamp/bank/brainactive_p3_question_bank_production.json"
AUD = "revamp/bank/ha_audit_20260921.json"
TRK = "revamp/bank/ha_solver_tracker_20260921.json"
NEW = "revamp/bank/ha_new_20260921.json"
EXT = "revamp/bank/ha_extra_20260921.json"
OUT = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BASE, encoding="utf-8"))
aud = json.load(open(AUD, encoding="utf-8"))
trk = json.load(open(TRK, encoding="utf-8"))
newqs = json.load(open(NEW, encoding="utf-8"))
extqs = json.load(open(EXT, encoding="utf-8"))
dels1 = set(k for k, x in aud.items() if x["verdict"] == "delete")
dels1 = set(k for k, x in aud.items() if x["verdict"] == "delete")
dels2 = json.load(open("revamp/bank/ha_dels2_20260921.json", encoding="utf-8"))
dels3 = json.load(open("revamp/bank/ha_dels3_20260921.json", encoding="utf-8"))
for k in dels3:
    dels2[k] = "rejected_too_simple"
print("dels1:", len(dels1), "dels2:", len(dels2), collections.Counter(dels2.values()))
newmap = {q["id"]: q for q in newqs}
assert len(newmap) == 309
extids = [q["id"] for q in extqs]
assert len(extids) == 71 and len(set(extids)) == 71
out = []
for q in d["questions"]:
    qid = q["id"]
    if qid in dels1:
        q = dict(q)
        q["qa_status"] = "rejected_too_simple"
        q["is_active"] = False
    elif qid in dels2:
        q = dict(q)
        q["qa_status"] = dels2[qid]
        q["is_active"] = False
    out.append(q)
byid = set(q["id"] for q in out)
taken = set(byid) | set(newmap)
nextn = 367
for q in extqs:
    if q["id"] in taken:
        while ("BA_P3_HA_%04d" % nextn) in taken:
            nextn += 1
        q["id"] = "BA_P3_HA_%04d" % nextn
        taken.add(q["id"])
        nextn += 1
    else:
        taken.add(q["id"])
json.dump(extqs, open(EXT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
extids = [q["id"] for q in extqs]
assert not (set(newmap) & byid), "refit id collision"
assert not (set(extids) & taken - set(q["id"] for q in extqs)), "extra id collision"
assert not (set(newmap) & set(extids)), "new-extra collision"
final = out + [newmap[k] for k in sorted(newmap)] + extqs
live = [q for q in final if q.get("qa_status") not in ("rejected_duplicate", "rejected_too_simple", "rejected_duplicate_options", "rejected_wrong_answer")]
print("total:", len(final), "live:", len(live))
fps = collections.Counter((q["question"].strip().lower(), q["answer"]) for q in live)
dups = [fp for fp, n in fps.items() if n > 1]
print("dup fingerprints:", len(dups))
for fp in dups[:5]:
    print("DUP:", fp[0][:70], fp[1])
cjk = [q["id"] for q in live if re.search("[\u4e00-\u9fff]", q["question"] + q.get("explanation", ""))]
print("CJK:", len(cjk))
lv = collections.Counter(q["level"] for q in live)
dm = collections.Counter(q["domain"] for q in live)
print("levels:", dict(lv))
print("domains:", dict(dm))
rej = collections.Counter(q["qa_status"] for q in final if q.get("qa_status", "").startswith("rejected"))
print("rejected:", dict(rej))
meta = {"count": len(final), "live": len(live), "source": "ha_purge_regen_20260921_r2", "date": "2026-09-21", "deleted_r1": sorted(dels1), "deleted_r2": dels2}
json.dump({"meta": meta, "questions": final}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)

