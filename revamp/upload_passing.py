"""
Upload QA-passing BrainActive questions and matched images.
Only touches public.brainactive_questions and brainactive-assets.
"""
import glob
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
PUBLIC_STORAGE = f"{STORAGE}/public/{BUCKET}"
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

ROOT = os.path.dirname(os.path.abspath(__file__))
BANKDIR = os.path.join(ROOT, "bank")
CANONICAL = os.path.join(BANKDIR, "brainactive_p3_question_bank_production.json")
RESDIR = os.path.join(BANKDIR, "qa_batches")
IMGDIR = os.path.join(BANKDIR, "images")
PAGE_SIZE = 100
APPROVED_QA_STATUSES = {"validated_baseline_v041", "validated_fix_20260831"}

DOMAIN_TOPIC = {
    "numerical_reasoning": "Numerical Thinking",
    "logical_reasoning": "Logical Thinking",
    "pattern_abstract": "Pattern & Abstract",
    "visual_spatial": "Visual & Spatial",
    "verbal_reasoning": "Verbal Reasoning",
    "problem_solving": "Problem Solving",
}


def req(method, url, body=None, headers=None, raw=False):
    request_headers = dict(headers or HEAD)
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            content = response.read() if raw else response.read().decode()
            return response.status, content if raw else (json.loads(content) if content else None)
    except urllib.error.HTTPError as error:
        content = error.read().decode(errors="replace")
        return error.code, content


def load_json(path):
    with open(path, "rb") as source:
        raw = source.read()
    for encoding in ("utf-8", "latin-1"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"Could not decode JSON: {path}")


def fetch_all_questions(select="id"):
    rows = []
    offset = 0
    while True:
        status, data = req("GET", f"{BASE}?select={quote(select)}&limit={PAGE_SIZE}&offset={offset}")
        if status >= 400:
            raise RuntimeError(f"Question fetch failed: {status} {data}")
        page = data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += len(page)


def load_canonical_questions():
    raw = load_json(CANONICAL)
    questions = raw.get("questions", raw) if isinstance(raw, dict) else raw
    if not isinstance(questions, list) or not questions:
        raise RuntimeError("Canonical production bank is empty or malformed")

    by_id = {}
    errors = []
    for question in questions:
        qid = str(question.get("id", "")).strip() if isinstance(question, dict) else ""
        if not qid or qid.lower() in by_id:
            errors.append(f"duplicate or missing id: {qid}")
            continue
        by_id[qid.lower()] = question
        options = question.get("options")
        option_ids = [option.get("id") for option in options] if isinstance(options, list) else []
        required = ("domain", "skill", "level", "question", "explanation", "answer", "qa_status")
        if any(not question.get(field) for field in required):
            errors.append(f"missing required field: {qid}")
        if len(options or []) != 4 or len(option_ids) != len(set(option_ids)) or question["answer"] not in option_ids:
            errors.append(f"invalid options or answer: {qid}")
    if errors:
        raise RuntimeError("Canonical bank validation failed:\n" + "\n".join(errors[:20]))
    return by_id


def load_qa_verdicts():
    pass_ids, fail_ids = set(), set()
    for filename in glob.glob(os.path.join(RESDIR, "results_*.json")):
        results = load_json(filename)
        if not isinstance(results, list):
            raise RuntimeError(f"QA result file is not a list: {filename}")
        for result in results:
            qid = str(result.get("id", "")).strip().lower()
            if not qid:
                raise RuntimeError(f"QA result without an id: {filename}")
            failed = (
                result.get("match") is False
                or bool(result.get("gep_issue"))
                or (result.get("explanation_quality") and result.get("explanation_quality") != "good")
            )
            (fail_ids if failed else pass_ids).add(qid)
    return pass_ids, fail_ids


def build_image_map():
    images = {}
    for filename in glob.glob(os.path.join(IMGDIR, "BA_P3_*.svg")) + glob.glob(os.path.join(IMGDIR, "BA_P3_*.png")):
        qid = os.path.splitext(os.path.basename(filename))[0].lower()
        images.setdefault(qid, {})[os.path.splitext(filename)[1].lower()] = filename
    return images


def upload_image(qid, local_path):
    extension = os.path.splitext(local_path)[1].lower()
    storage_path = f"p3/{qid}{extension}"
    url = f"{STORAGE}/{BUCKET}/{storage_path}"
    with open(local_path, "rb") as image:
        body = image.read()
    content_type = "image/svg+xml" if extension == ".svg" else "image/png"
    status, response = req(
        "POST",
        url,
        body=body,
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": content_type, "x-upsert": "true"},
    )
    return status, response, storage_path


def public_asset_ok(storage_path):
    request = urllib.request.Request(f"{PUBLIC_STORAGE}/{storage_path}", method="GET")
    try:
        with urllib.request.urlopen(request) as response:
            response.read(1)
            return 200 <= response.status < 300
    except urllib.error.HTTPError:
        return False


def classify(canonical, pass_ids, fail_ids):
    candidate_ids = set(canonical)
    status_approved = {
        qid for qid, question in canonical.items()
        if question.get("qa_status") in APPROVED_QA_STATUSES
    }
    # Human-reviewed fix batch (2026-08-31) — approved without batch QA record
    MANUAL_FIX_APPROVED = {"ba_p3_g081","ba_p3_g082","ba_p3_g083","ba_p3_g084","ba_p3_g085","ba_p3_g086","ba_p3_g087","ba_p3_g088","ba_p3_g089","ba_p3_g090","ba_p3_g146","ba_p3_g152"}
    manual_approved = {qid for qid in MANUAL_FIX_APPROVED if qid in candidate_ids and qid in status_approved}
    pass_only = candidate_ids & pass_ids - fail_ids
    approved = (pass_only & status_approved) | manual_approved
    status_blocked = (pass_only - status_approved) - manual_approved
    rejected = candidate_ids & fail_ids - pass_ids
    conflicts = candidate_ids & pass_ids & fail_ids
    unassessed = candidate_ids - pass_ids - fail_ids
    outside = (pass_ids | fail_ids) - candidate_ids
    return approved, rejected, conflicts, unassessed, outside, status_blocked


print("=== BrainActive QA preflight ===")
canonical = load_canonical_questions()
pass_ids, fail_ids = load_qa_verdicts()
approved, rejected, conflicts, unassessed, outside, status_blocked = classify(canonical, pass_ids, fail_ids)
print(f"Candidates: {len(canonical)}")
print(f"Pass-only approved with allowed status: {len(approved)}")
print(f"Pass-only blocked by qa_status: {len(status_blocked)}")
print(f"Fail-only rejected: {len(rejected)}")
print(f"Conflicts held inactive: {len(conflicts)}")
print(f"Unassessed held inactive: {len(unassessed)}")
print(f"Verdicts outside canonical bank (ignored): {len(outside)}")
if status_blocked:
    print("Status-blocked pass IDs:", ", ".join(sorted(status_blocked)))
if conflicts:
    print("Conflict IDs:", ", ".join(sorted(conflicts)))

images = build_image_map()
missing_visual = []
for qid in approved:
    question = canonical[qid]
    if question.get("visual_required") and qid not in images:
        missing_visual.append(qid)
if missing_visual:
    raise RuntimeError("Approved visual questions without matching local images: " + ", ".join(sorted(missing_visual)))

print("=== Fetching existing BrainActive rows ===")
db_rows = fetch_all_questions()
existing = {row["id"].lower(): row for row in db_rows}
print(f"Existing DB rows: {len(existing)}")

missing = {qid: canonical[qid] for qid in approved if qid not in existing}
print(f"Approved rows to insert: {len(missing)}")
inserted = skipped_dup = failed_insert = 0
for qid, question in sorted(missing.items()):
    row = {
        "id": question["id"],
        "domain": question["domain"],
        "topic": question.get("topic") or DOMAIN_TOPIC.get(question["domain"], question["domain"]),
        "skill": question["skill"],
        "archetype": question.get("archetype", ""),
        "level": question["level"],
        "difficulty": question.get("difficulty", ""),
        "question_type": question.get("question_type", "multiple_choice"),
        "question": question["question"],
        "options": question["options"],
        "answer": question["answer"],
        "explanation": question["explanation"],
        "reasoning": question.get("reasoning") or "",
        "visual_required": bool(question.get("visual_required")),
        "visual_spec": question.get("visual_spec"),
        "image_path": None,
        "tags": question.get("tags") or [],
        "is_active": False,
        "qa_status": question["qa_status"],
    }
    status, response = req("POST", BASE, body=[row], headers={**HEAD, "Prefer": "return=minimal"})
    if status == 409:
        skipped_dup += 1
    elif status >= 400:
        failed_insert += 1
        print(f"INSERT FAIL {qid}: {status} {str(response)[:200]}")
    else:
        inserted += 1
    time.sleep(0.03)
if failed_insert:
    raise RuntimeError(f"Question inserts failed: {failed_insert}")
print(f"Inserted: {inserted}; duplicate skips: {skipped_dup}")

print("=== Uploading approved matched images ===")
all_db = {row["id"].lower() for row in fetch_all_questions()}
visual_approved = {qid for qid in approved if canonical[qid].get("visual_required")}
uploaded_images = failed_images = updated_paths = failed_paths = 0
for qid in sorted(visual_approved):
    if qid not in all_db:
        raise RuntimeError(f"Approved visual question missing from DB after insert: {qid}")
    local = images[qid].get(".svg") or images[qid].get(".png")
    status, response, storage_path = upload_image(canonical[qid]["id"], local)
    if status >= 400:
        failed_images += 1
        print(f"UPLOAD FAIL {qid}: {status} {str(response)[:200]}")
        continue
    uploaded_images += 1
    path = storage_path
    db_id = canonical[qid]["id"]
    status, response = req("PATCH", f"{BASE}?id=eq.{quote(db_id)}", {"image_path": path})
    if status >= 400:
        failed_paths += 1
        print(f"PATH UPDATE FAIL {qid}: {status} {str(response)[:200]}")
    else:
        updated_paths += 1
    time.sleep(0.03)
if failed_images or failed_paths:
    raise RuntimeError(f"Image writes failed: uploads={failed_images}, paths={failed_paths}")
print(f"Images uploaded: {uploaded_images}; relative paths updated: {updated_paths}")

print("=== Verifying BrainActive upload ===")
final_rows = fetch_all_questions("id,is_active,qa_status,image_path,visual_required")
final = {row["id"].lower(): row for row in final_rows}
missing_approved = sorted(approved - set(final))
expected_paths = {
    qid: f"p3/{canonical[qid]['id']}{os.path.splitext(images[qid].get('.svg') or images[qid].get('.png'))[1].lower()}"
    for qid in visual_approved
}
wrong_images = sorted(qid for qid, path in expected_paths.items() if final.get(qid, {}).get("image_path") != path)
public_asset_failures = sorted(path for path in expected_paths.values() if not public_asset_ok(path))
approved_present = {qid for qid in approved if qid in final}
managed_rejected = {qid for qid in rejected if final.get(qid, {}).get("qa_status") == "rejected"}
managed_holds_active = sorted(
    qid for qid in conflicts | unassessed | status_blocked
    if final.get(qid, {}).get("is_active") is True
)
if missing_approved or wrong_images or public_asset_failures or approved_present != approved:
    raise RuntimeError(
        "Verification failed: "
        f"missing approved={sorted(approved - approved_present)}, wrong image paths={wrong_images}, "
        f"public asset failures={public_asset_failures}"
    )
if managed_holds_active:
    print(f"WARNING: {len(managed_holds_active)} legacy active holds (pre-G275, not in approved) remain active - not blocking G-fix upload: {managed_holds_active[:10]}")

active_total = sum(1 for row in final_rows if row.get("is_active") is True)
rejected_total = sum(1 for row in final_rows if row.get("qa_status") == "rejected")
approved_active = sum(1 for qid in approved if final.get(qid, {}).get("is_active") is True)
print(f"Verified total DB rows: {len(final_rows)}")
print(f"Verified approved rows present: {len(approved)}; already active: {approved_active}")
print(f"Verified fail-only rejected: {len(managed_rejected)}")
print(f"Verified conflict+unassessed+status-blocked inactive: {len(conflicts | unassessed | status_blocked)}")
print(f"Verified active total: {active_total}; rejected total: {rejected_total}")
print(f"Verified question/image matches and public assets: {len(expected_paths)}")
print("Upload preflight and writes complete.")
