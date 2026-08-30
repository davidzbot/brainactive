"""Upload only mechanically QA-passed BrainActive gap-fill candidates.

The script is fail-closed: candidates are inserted inactive, assets are uploaded and
publicly checked, then and only then are all passed candidates activated.
"""
import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import quote

PROJECT = "mqpunjvdrkqvionsjosl"
TABLE = "brainactive_questions"
BUCKET = "brainactive-assets"
KEY = os.environ["BA_SR"]
BASE = f"https://{PROJECT}.supabase.co/rest/v1/{TABLE}"
STORAGE = f"https://{PROJECT}.supabase.co/storage/v1/object"
PUBLIC = f"{STORAGE}/public/{BUCKET}"
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATE = os.path.join(BANK_DIR, "gapfill_candidates.json")
QA = os.path.join(BANK_DIR, "gapfill_qa_results.json")
IMAGE_DIR = os.path.join(BANK_DIR, "gapfill_images")
PAGE_SIZE = 100
DOMAIN_TOPIC = {
    "numerical_reasoning": "Numerical Thinking",
    "logical_reasoning": "Logical Thinking",
    "verbal_reasoning": "Verbal Reasoning",
    "visual_spatial": "Visual & Spatial",
    "pattern_abstract": "Pattern & Abstract",
    "problem_solving": "Problem Solving",
}


def request(method, url, body=None, headers=None, raw=False):
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, headers=headers or HEAD, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read() if raw else response.read().decode()
            return response.status, content if raw else (json.loads(content) if content else None)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode(errors="replace")


def fetch_all():
    rows = []
    offset = 0
    while True:
        status, page = request("GET", f"{BASE}?select=id,is_active,qa_status,image_path&limit={PAGE_SIZE}&offset={offset}")
        if status >= 400:
            raise RuntimeError(f"DB fetch failed: {status} {page}")
        page = page or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += len(page)


def public_ok(path):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{PUBLIC}/{path}")) as response:
            response.read(1)
            return 200 <= response.status < 300
    except urllib.error.HTTPError:
        return False


candidates = json.load(open(CANDIDATE, encoding="utf-8"))["questions"]
qa = json.load(open(QA, encoding="utf-8"))
if qa.get("status") != "PASS" or qa.get("failed") != 0 or qa.get("passed") != len(candidates):
    raise RuntimeError("Gap-fill QA is not a clean PASS; no writes performed")
if len({q["id"] for q in candidates}) != len(candidates):
    raise RuntimeError("Gap-fill candidate IDs are not unique")

rows = {row["id"]: row for row in fetch_all()}
missing = [q for q in candidates if q["id"] not in rows]
existing_candidate_ids = [q["id"] for q in candidates if q["id"] in rows]
print(f"QA-passed candidates: {len(candidates)}")
print(f"Already in DB: {len(existing_candidate_ids)}; to insert: {len(missing)}")

for q in missing:
    row = {
        "id": q["id"],
        "domain": q["domain"],
        "topic": DOMAIN_TOPIC[q["domain"]],
        "skill": q["skill"],
        "archetype": q["archetype"],
        "level": q["level"],
        "difficulty": q["difficulty"],
        "question_type": q["question_type"],
        "question": q["question"],
        "options": q["options"],
        "answer": q["answer"],
        "explanation": q["explanation"],
        "reasoning": q.get("reasoning", ""),
        "tags": q.get("tags", []),
        "visual_required": bool(q.get("visual_required")),
        "visual_spec": q.get("visual_spec"),
        "image_path": None,
        "is_active": False,
        "qa_status": "gapfill_qa_passed",
    }
    status, response = request("POST", BASE, [row], {**HEAD, "Prefer": "return=minimal"})
    if status >= 400:
        raise RuntimeError(f"Insert failed for {q['id']}: {status} {response}")

visual = [q for q in candidates if q.get("visual_required")]
for q in visual:
    local = os.path.join(IMAGE_DIR, f"{q['id']}.svg")
    if not os.path.exists(local):
        raise RuntimeError(f"Missing rendered asset: {q['id']}")
    storage_path = f"p3/{q['id']}.svg"
    with open(local, "rb") as image:
        status, response = request(
            "POST",
            f"{STORAGE}/{BUCKET}/{storage_path}",
            image.read(),
            {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "image/svg+xml", "x-upsert": "true"},
        )
    if status >= 400:
        raise RuntimeError(f"Asset upload failed for {q['id']}: {status} {response}")
    status, response = request("PATCH", f"{BASE}?id=eq.{quote(q['id'])}", {"image_path": storage_path})
    if status >= 400:
        raise RuntimeError(f"Image path update failed for {q['id']}: {status} {response}")

# Confirm every visual asset is publicly readable before activation.
failed_assets = [q["id"] for q in visual if not public_ok(f"p3/{q['id']}.svg")]
if failed_assets:
    raise RuntimeError("Public asset verification failed: " + ", ".join(failed_assets))

for q in candidates:
    status, response = request("PATCH", f"{BASE}?id=eq.{quote(q['id'])}", {"is_active": True})
    if status >= 400:
        raise RuntimeError(f"Activation failed for {q['id']}: {status} {response}")
    time.sleep(0.02)

final = {row["id"]: row for row in fetch_all()}
missing_final = [q["id"] for q in candidates if q["id"] not in final]
not_active = [q["id"] for q in candidates if not final.get(q["id"], {}).get("is_active")]
wrong_paths = [q["id"] for q in visual if final.get(q["id"], {}).get("image_path") != f"p3/{q['id']}.svg"]
if missing_final or not_active or wrong_paths:
    raise RuntimeError(f"Final verification failed: missing={missing_final}, inactive={not_active}, wrong_paths={wrong_paths}")
print(f"Inserted: {len(missing)}")
print(f"Activated: {len(candidates)}")
print(f"Visual assets verified: {len(visual)}")
print("Gap-fill upload and activation complete.")
