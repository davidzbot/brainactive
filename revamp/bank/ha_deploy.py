import json, sys, urllib.request, urllib.error
sys.path.insert(0, "revamp/bank")
from ha_db import PROJECT, SR
URL = "https://api.supabase.com/v1/projects/" + PROJECT + "/database/query"
def sql(query):
    body = json.dumps({"query": query}).encode()
    r = urllib.request.Request(URL, data=body, headers={"Authorization": "Bearer " + SR, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]
if __name__ == "__main__":
    st, data = sql("select count(*) as n from public.brainactive_questions;")
    print(st, str(data)[:200])

