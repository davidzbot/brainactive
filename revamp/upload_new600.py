"""
Upload the reviewed BrainActive new-600 bank.
Inserts into public.brainactive_questions with is_active=False,
uploads matched SVGs to brainactive-assets/p3/, sets image_path, verifies.
"""
import json
import os
import sys
import time
import io
import urllib.error
import urllib.request
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECT = "mqpunjvdrkqvionsjosl"
TABLE = "brainactive_questions"
BUCKET = "brainactive-assets"
KEY = os.environ["BA_SR"]
BASE = f"https://{PROJECT}.supabase.co/rest/v1/{TABLE}"
STORAGE = f"https://{PROJECT}.supabase.co/storage/v1/object"
PUBLIC_STORAGE = f"{STORAGE}/public/{BUCKET}"
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_JSON = os.path.join(ROOT, "bank", "new_600", "brainactive_new_600_upload.json")
IMGDIR = os.path.join(ROOT, "bank", "images")


def req(method, url, body=None, headers=None):
    rh = dict(headers or HEAD)
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(url, data=data, headers=rh, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            c = resp.read().decode()
            return resp.status, (json.loads(c) if c else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def fetch_ids():
    ids = set()
    offset = 0
    while True:
        s, data = req("GET", f"{BASE}?select=id&limit=100&offset={offset}")
        if s >= 400:
            raise RuntimeError(f"fetch failed: {s} {data}")
        if not data:
            return ids
        ids.update(r["id"] for r in data)
        offset += len(data)


print("=== Loading upload file ===")
qs = json.load(open(UPLOAD_JSON, encoding="utf-8"))["questions"]
print(f"Upload file: {len(qs)} questions")

print("=== Fetching existing IDs ===")
existing = fetch_ids()
print(f"DB rows: {len(existing)}")
todo = [q for q in qs if q["id"] not in existing]
print(f"To insert: {len(todo)} (already present: {len(qs) - len(todo)})")

print("=== Inserting (is_active=False) ===")
ins = dup = fail = 0
for q in todo:
    row = {
        "id": q["id"],
        "domain": q["domain"],
        "topic": q.get("topic") or q["domain"],
        "skill": q["skill"],
        "archetype": q.get("archetype", ""),
        "level": q["level"],
        "difficulty": q.get("difficulty", ""),
        "question_type": q.get("question_type", "multiple_choice"),
        "question": q["question"],
        "options": q["options"],
        "answer": q["answer"],
        "explanation": q["explanation"],
        "reasoning": q.get("reasoning") or "",
        "visual_required": bool(q.get("visual_required")),
        "visual_spec": q.get("visual_spec"),
        "image_path": None,
        "tags": q.get("tags") or [],
        "is_active": False,
        "qa_status": q.get("qa_status", "validated_new600_20260905"),
    }
    s, r = req("POST", BASE, body=[row], headers={**HEAD, "Prefer": "return=minimal"})
    if s == 409:
        dup += 1
    elif s >= 400:
        fail += 1
        print(f"INSERT FAIL {q['id']}: {s} {str(r)[:200]}")
    else:
        ins += 1
    time.sleep(0.03)
print(f"Inserted: {ins}; dup skips: {dup}; failed: {fail}")
if fail:
    raise RuntimeError(f"Inserts failed: {fail}")

print("=== Uploading SVGs ===")
visual = [q for q in qs if q.get("image_path")]
up_img = fail_img = 0
for q in sorted(visual, key=lambda x: x["id"]):
    local = os.path.join(IMGDIR, os.path.basename(q["image_path"]))
    if not os.path.exists(local):
        print(f"MISSING LOCAL SVG for {q['id']}: {local}")
        fail_img += 1
        continue
    with open(local, "rb") as f:
        body = f.read()
    s, r = req("POST", f"{STORAGE}/{BUCKET}/{q['image_path']}", body=body,
               headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                        "Content-Type": "image/svg+xml", "x-upsert": "true"})
    if s >= 400:
        fail_img += 1
        print(f"SVG UPLOAD FAIL {q['id']}: {s} {str(r)[:150]}")
    else:
        up_img += 1
    time.sleep(0.03)
print(f"SVGs uploaded: {up_img}; failed: {fail_img}")
if fail_img:
    raise RuntimeError("SVG uploads failed")

print("=== Setting image_path ===")
path_fail = 0
for q in sorted(visual, key=lambda x: x["id"]):
    s, r = req("PATCH", f"{BASE}?id=eq.{quote(q['id'])}", {"image_path": q["image_path"]})
    if s >= 400:
        path_fail += 1
        print(f"PATH FAIL {q['id']}: {s} {str(r)[:150]}")
print(f"image_path updates failed: {path_fail}")
if path_fail:
    raise RuntimeError("image_path updates failed")

print("=== Verifying ===")
s, rows = req("GET", f"{BASE}?select=id,image_path,qa_status,is_active&id=gte.BA_P3_1840&id=lte.BA_P3_2439&limit=700")
ids = {r["id"]: r for r in rows}
missing = [q["id"] for q in qs if q["id"] not in ids]
print(f"Present in range: {len(ids)}/600; missing: {len(missing)}")
bad_img = [q["id"] for q in visual if ids.get(q["id"], {}).get("image_path") != q["image_path"]]
print(f"Wrong image_path: {len(bad_img)} {bad_img[:5]}")
# public asset check
pub_fail = []
for q in visual:
    rq = urllib.request.Request(f"{PUBLIC_STORAGE}/{q['image_path']}", method="GET")
    try:
        with urllib.request.urlopen(rq) as resp:
            resp.read(1)
            assert 200 <= resp.status < 300
    except Exception:
        pub_fail.append(q["id"])
print(f"Public asset failures: {len(pub_fail)} {pub_fail[:5]}")
# unicode read-back check
s, sample = req("GET", f"{BASE}?select=id,explanation&id=eq.{qs[0]['id']}")
print("Sample explanation head:", (sample[0]["explanation"] if sample else "?")[:80])
if missing or bad_img or pub_fail:
    raise RuntimeError("Verification failed")
print("UPLOAD COMPLETE AND VERIFIED")
