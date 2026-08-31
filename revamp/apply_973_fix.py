import json, os, urllib.request, urllib.error, time
from urllib.parse import quote
PROJECT="mqpunjvdrkqvionsjosl"
TABLE="brainactive_questions"
KEY=os.environ["BA_SR"]
BASE=f"https://{PROJECT}.supabase.co/rest/v1/{TABLE}"
HEAD={"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
db=json.load(open(r"C:\Projects\brainactive-android\revamp\bank\db_973_fixed.json",encoding="utf-8"))
# build duplicate set
from collections import defaultdict
qm=defaultdict(list)
for q in db:
    qm[q["question"].strip()].append(q["id"])
fail_ids=set()
for k,arr in qm.items():
    if len(arr)>1:
        arr.sort()
        for dup in arr[1:]:
            fail_ids.add(dup)
print(f"fail duplicates {len(fail_ids)}")
def req(method,url,body=None):
    data=json.dumps(body).encode() if body else None
    r=urllib.request.Request(url,data=data,headers=HEAD,method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
# patch all
for q in db:
    payload={
        "topic": q["topic"],
        "options": q["options"],
        "is_active": q["id"] not in fail_ids,
        "qa_status": "validated_fix_20260831" if q["id"] not in fail_ids else "rejected_duplicate"
    }
    # also include explanation/image if needed but already correct
    st,txt=req("PATCH", f"{BASE}?id=eq.{quote(q['id'])}", payload)
    if st>=400:
        print(q["id"], st, txt[:200])
    time.sleep(0.02)
print("done patch")
# verify app query
import urllib.request as ur
# call function via anon key? use service_role to test
url=f"https://{PROJECT}.supabase.co/functions/v1/brainactive-get-questions?mode=quick_test&limit=100"
headers={"apikey":os.environ.get("SUPABASE_ANON_KEY",""), "Authorization":f"Bearer {os.environ.get('SUPABASE_ANON_KEY','')}"}
# fallback use anon from request.ts
anon="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xcHVuanZkcmtxdmlvbnNqb3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0NTk5MTYsImV4cCI6MjA5MjAzNTkxNn0.65Yda6PICedefQLGex5OuS1IOFNeJaHgBuG3mGfoI3s"
headers={"apikey":anon,"Authorization":f"Bearer {anon}"}
req2=urllib.request.Request(url, headers=headers)
try:
    with ur.urlopen(req2) as r:
        print("app query status", r.status)
        data=json.loads(r.read().decode())
        print("app returned", len(data.get("data",[])) if isinstance(data,dict) else len(data))
        if isinstance(data,dict) and "data" in data:
            print("sample ids", [x["id"] for x in data["data"][:3]])
except Exception as e:
    print("app query failed", e)
