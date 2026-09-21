import json, sys, os, urllib.request, urllib.error
sys.path.insert(0, "revamp/bank")
from ha_db import PROJECT, SR, msql
Q39 = chr(39)
BUCKET = "brainactive-assets"
STORAGE = "https://" + PROJECT + ".supabase.co/storage/v1/object"
PUB = STORAGE + "/public/" + BUCKET
def sreq(method, url, body=None, ctype="application/json"):
    h = {"apikey": SR, "Authorization": "Bearer " + SR}
    if ctype:
        h["Content-Type"] = ctype
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
step = sys.argv[1] if len(sys.argv) > 1 else "all"
if step in ("all", "images"):
    six = ["BA_P3_ADD_0047", "BA_P3_ADD_0048", "BA_P3_ADD_0049", "BA_P3_ADD_0050", "BA_P3_ADD_0091", "BA_P3_ADD_0092"]
    for qid in six:
        local = "revamp/bank/images/" + qid + ".svg"
        body = open(local, "rb").read()
        st, _ = sreq("POST", STORAGE + "/" + BUCKET + "/p3/" + qid + ".svg", body=body, ctype="image/svg+xml")
        if st in (200, 201):
            pass
        else:
            st2, _ = sreq("PUT", STORAGE + "/" + BUCKET + "/p3/" + qid + ".svg", body=body, ctype="image/svg+xml")
            st = st2
        print("upload", qid, st)
        rq = urllib.request.Request(PUB + "/p3/" + qid + ".svg", method="GET")
        try:
            with urllib.request.urlopen(rq, timeout=60) as resp:
                print("public", qid, resp.status)
        except urllib.error.HTTPError as e:
            print("public FAIL", qid, e.code)
if step in ("all", "mig1"):
    sql = open("supabase/migrations/20260921000000_brainactive_ha_purge_regen.sql", encoding="utf-8").read()
    stmts = [x.strip() for x in sql.split(";\n") if x.strip() and not x.strip().startswith("--")]
    ups = [x + ";" for x in stmts if x.lstrip().lower().startswith("update")]
    ins = [x + ";" for x in stmts if x.lstrip().lower().startswith("insert")]
    print("updates:", len(ups), "inserts:", len(ins))
    for u in ups:
        st, data = msql(u)
        print("upd", st, str(data)[:120])
        assert st == 201, data
    for i in range(0, len(ins), 40):
        st, data = msql(" ".join(ins[i:i + 40]))
        print("ins batch", i, st, str(data)[:120])
        assert st == 201, data
if step in ("all", "mig2"):
    sql = open("supabase/migrations/20260921010000_brainactive_ha_qa_round2.sql", encoding="utf-8").read()
    st, data = msql(sql)
    print("mig2", st, str(data)[:300])
    assert st == 201, data
if step in ("all", "activate"):
    bank = json.load(open("revamp/bank/brainactive_p3_question_bank_ha20260921.json", encoding="utf-8"))
    ha = sorted(q["id"] for q in bank["questions"] if q.get("qa_status") == "validated_ha_20260921")
    print("HA to activate:", len(ha))
    for i in range(0, len(ha), 80):
        chunk = ha[i:i + 80]
        q = "update public.brainactive_questions set is_active = true, updated_at = now() where id in (" + ", ".join(Q39 + x + Q39 for x in chunk) + ") and qa_status = " + Q39 + "validated_ha_20260921" + Q39 + ";"
        st, data = msql(q)
        print("act", i, st, str(data)[:120])
        assert st == 201, data
print("APPLY DONE", step)

