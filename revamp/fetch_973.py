import os, json, urllib.request, urllib.error
from urllib.parse import quote
import pathlib
PROJECT="mqpunjvdrkqvionsjosl"
TABLE="brainactive_questions"
KEY=os.environ["BA_SR"]
BASE=f"https://{PROJECT}.supabase.co/rest/v1/{TABLE}"
HEAD={"apikey":KEY,"Authorization":f"Bearer {KEY}"}
PAGE=100
rows=[]
offset=0
while True:
    url=f"{BASE}?select=*&order=id.asc&limit={PAGE}&offset={offset}"
    req=urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req) as r:
        data=json.loads(r.read().decode())
    rows.extend(data)
    print(f"fetched {len(data)} offset {offset} total {len(rows)}")
    if len(data)<PAGE:
        break
    offset+=len(data)
open(r"C:\Projects\brainactive-android\revamp\bank\db_973.json","w",encoding="utf-8").write(json.dumps(rows,ensure_ascii=False,indent=2))
print("wrote",len(rows))
