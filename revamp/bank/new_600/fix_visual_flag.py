import json, os, io, sys, time, urllib.request
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

ud = json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))
targets = [q["id"] for q in ud["questions"] if q.get("image_path")]
print(f"rows with image_path in file: {len(targets)}")
fails = []
for qid in sorted(targets):
    url = f"{BASE}?id=eq.{qid}"
    req = urllib.request.Request(url, data=json.dumps({"visual_required": True}).encode(),
                                 headers=dict(HEAD), method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            assert 200 <= resp.status < 300
            resp.read()
    except Exception as e:
        fails.append((qid, str(e)[:100]))
        print("FAIL", qid, str(e)[:100])
    time.sleep(0.05)
print("FAILS:", fails)

# verify
ok = 0
for qid in sorted(targets):
    url = f"{BASE}?select=id,visual_required,image_path&id=eq.{qid}"
    req = urllib.request.Request(url, headers=HEAD)
    r = json.loads(urllib.request.urlopen(req).read().decode())[0]
    good = r["visual_required"] is True and (r["image_path"] or "").startswith("p3/")
    ok += good
    if not good:
        print("BAD", qid, r)
    time.sleep(0.02)
print(f"{ok}/{len(targets)} live with diagrams")
