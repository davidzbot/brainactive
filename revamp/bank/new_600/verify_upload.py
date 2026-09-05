"""Paginated verification of the new-600 upload (PostgREST caps pages at 100)."""
import json, os, io, sys, urllib.request
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
PUB = f"https://{PROJECT}.supabase.co/storage/v1/object/public/brainactive-assets"
KEY = os.environ["BA_SR"]
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

qs = json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))["questions"]

got = {}
offset = 0
while True:
    url = (f"{BASE}?select=id,image_path,qa_status,is_active&order=id"
           f"&limit=100&offset={offset}")
    req = urllib.request.Request(url, headers=HEAD)
    page = json.loads(urllib.request.urlopen(req).read().decode())
    if not page:
        break
    for r in page:
        got[r["id"]] = r
    offset += len(page)

want = {q["id"]: q for q in qs}
missing = [i for i in want if i not in got]
print(f"DB total rows: {len(got)}; new-600 present: {len(want) - len(missing)}/600")
print("missing:", missing[:10])

bad_status = [i for i in want if i in got and got[i].get("qa_status") != "validated_new600_20260905"]
print("wrong qa_status:", len(bad_status), bad_status[:5])
active = [i for i in want if i in got and got[i].get("is_active") is True]
print("unexpectedly active:", len(active), active[:5])

visual = [q for q in qs if q.get("image_path")]
bad_img = [q["id"] for q in visual if got.get(q["id"], {}).get("image_path") != q["image_path"]]
print(f"wrong image_path: {len(bad_img)} {bad_img}")

pub_fail = []
for q in visual:
    rq = urllib.request.Request(f"{PUB}/{q['image_path']}", method="GET")
    try:
        with urllib.request.urlopen(rq) as resp:
            resp.read(1)
            assert 200 <= resp.status < 300
    except Exception:
        pub_fail.append(q["id"])
print(f"public asset failures: {len(pub_fail)} {pub_fail}")

ok = not missing and not bad_status and not active and not bad_img and not pub_fail
print("VERIFY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
