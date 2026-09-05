"""Batch 2: upload 6 shared SVGs, set image_path on 18 rows, mirror files."""
import json, os, io, sys, time, glob, urllib.request

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
    "BA_P3_2411": "BA_P3_2411.svg", "BA_P3_2412": "BA_P3_2411.svg",
    "BA_P3_2421": "BA_P3_2411.svg", "BA_P3_2423": "BA_P3_2411.svg",
    "BA_P3_2424": "BA_P3_2411.svg",
    "BA_P3_2345": "BA_P3_2345.svg", "BA_P3_2350": "BA_P3_2345.svg",
    "BA_P3_2356": "BA_P3_2345.svg", "BA_P3_2361": "BA_P3_2345.svg",
    "BA_P3_2375": "BA_P3_2345.svg",
    "BA_P3_2388": "BA_P3_2388.svg", "BA_P3_2389": "BA_P3_2388.svg",
    "BA_P3_2390": "BA_P3_2388.svg", "BA_P3_2391": "BA_P3_2388.svg",
    "BA_P3_2392": "BA_P3_2388.svg", "BA_P3_2393": "BA_P3_2388.svg",
    "BA_P3_2062": "BA_P3_2062.svg",
    "BA_P3_2058": "BA_P3_2058.svg",
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


for svg in sorted(set(ASSIGN.values())):
    with open(os.path.join(IMGDIR, svg), "rb") as f:
        body = f.read()
    s, r = req("POST", f"{STORAGE}/p3/{svg}", body=body,
               headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                        "Content-Type": "image/svg+xml", "x-upsert": "true"})
    print(f"svg {svg}: {s}")
    assert s in (200, 201), r
    time.sleep(0.03)

fails = []
for qid, svg in sorted(ASSIGN.items()):
    s, r = req("PATCH", f"{BASE}?id=eq.{qid}", {"image_path": f"p3/{svg}"})
    print(qid, s)
    if s != 204:
        fails.append(qid)
    time.sleep(0.05)
print("PATCH fails:", fails)
assert not fails

pub_fail = []
for qid, svg in sorted(ASSIGN.items()):
    rq = urllib.request.Request(f"{PUB}/p3/{svg}", method="GET")
    try:
        with urllib.request.urlopen(rq) as resp:
            assert 200 <= resp.status < 300
    except Exception:
        pub_fail.append(qid)
print("public failures:", pub_fail)
assert not pub_fail

# mirror into upload JSON + part files
up_path = os.path.join(HERE, "brainactive_new_600_upload.json")
ud = json.load(open(up_path, encoding="utf-8"))
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        q["image_path"] = f"p3/{ASSIGN[q['id']]}"
        q["visual_required"] = True
        if not q.get("visual_spec"):
            q["visual_spec"] = {"type": "diagram", "note": "see image"}
json.dump(ud, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

text2svg = {}
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        text2svg[q["question"].strip()] = ASSIGN[q["id"]]
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    qs = json.load(open(fn, encoding="utf-8"))
    dirty = False
    for q in qs:
        hit = text2svg.get(q["question"].strip())
        if hit:
            q["image_path"] = f"p3/{hit}"
            q["visual_required"] = True
            if not q.get("visual_spec"):
                q["visual_spec"] = {"type": "diagram", "note": "see image"}
            dirty = True
    if dirty:
        json.dump(qs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("mirrored", base)

# mirror svg copies into staging images dir
for svg in sorted(set(ASSIGN.values())):
    src = os.path.join(IMGDIR, svg)
    dst = os.path.join(HERE, "images", svg)
    if os.path.abspath(src) != os.path.abspath(dst):
        open(dst, "wb").write(open(src, "rb").read())
print("DONE")
