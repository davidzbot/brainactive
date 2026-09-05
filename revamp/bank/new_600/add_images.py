"""Upload 9 new SVGs to p3/ bucket path and set image_path on 13 rows."""
import json, os, io, sys, time, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "..", "images")
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
STORAGE = f"https://{PROJECT}.supabase.co/storage/v1/object/brainactive-assets"
PUB = f"https://{PROJECT}.supabase.co/storage/v1/object/public/brainactive-assets"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

ASSIGN = {
    "BA_P3_2428": "BA_P3_2428.svg",
    "BA_P3_2429": "BA_P3_2429.svg",
    "BA_P3_2430": "BA_P3_2430.svg",
    "BA_P3_2435": "BA_P3_2435.svg",
    "BA_P3_2436": "BA_P3_2429.svg",
    "BA_P3_2438": "BA_P3_2438.svg",
    "BA_P3_2439": "BA_P3_2439.svg",
    "BA_P3_2395": "BA_P3_2395.svg",
    "BA_P3_2396": "BA_P3_2395.svg",
    "BA_P3_2397": "BA_P3_2395.svg",
    "BA_P3_2398": "BA_P3_2395.svg",
    "BA_P3_2381": "BA_P3_2381.svg",
    "BA_P3_2400": "BA_P3_2400.svg",
}


def req(method, url, body=None, headers=None):
    rh = dict(headers or HEAD)
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(url, data=data, headers=rh, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except Exception as e:
        return -1, str(e)


uploaded = set()
for svg in sorted(set(ASSIGN.values())):
    local = os.path.join(IMGDIR, svg)
    assert os.path.exists(local), local
    with open(local, "rb") as f:
        body = f.read()
    s, r = req("POST", f"{STORAGE}/p3/{svg}", body=body,
               headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                        "Content-Type": "image/svg+xml", "x-upsert": "true"})
    print(f"svg {svg}: {s}")
    assert s in (200, 201), r
    uploaded.add(svg)
    time.sleep(0.03)

fails = []
for qid, svg in sorted(ASSIGN.items()):
    s, r = req("PATCH", f"{BASE}?id=eq.{qid}", {"image_path": f"p3/{svg}"})
    if s >= 400 or s < 0:
        fails.append((qid, s, r[:100]))
        print(f"PATH FAIL {qid}: {s}")
    time.sleep(0.02)
print("path fails:", fails)

pub_fail = []
for qid, svg in sorted(ASSIGN.items()):
    rq = urllib.request.Request(f"{PUB}/p3/{svg}", method="GET")
    try:
        with urllib.request.urlopen(rq) as resp:
            assert 200 <= resp.status < 300
            resp.read(1)
    except Exception:
        pub_fail.append(qid)
print("public failures:", pub_fail)

# mirror into local upload JSON + part files
up_path = os.path.join(HERE, "brainactive_new_600_upload.json")
ud = json.load(open(up_path, encoding="utf-8"))
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        q["image_path"] = f"p3/{ASSIGN[q['id']]}"
        q["visual_required"] = True
        if not q.get("visual_spec"):
            q["visual_spec"] = {"type": "diagram", "note": "see image"}
json.dump(ud, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("upload JSON mirrored")

import glob
text2ba = {}
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        text2ba[q["question"].strip()] = (q["id"], ASSIGN[q["id"]])
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    qs = json.load(open(fn, encoding="utf-8"))
    dirty = False
    for q in qs:
        hit = text2ba.get(q["question"].strip())
        if hit:
            _, svg = hit
            q["image_path"] = f"p3/{svg}"
            q["visual_required"] = True
            if not q.get("visual_spec"):
                q["visual_spec"] = {"type": "diagram", "note": "see image"}
            dirty = True
    if dirty:
        json.dump(qs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("mirrored", base)
print("DONE")
