"""Activate only pass-only BrainActive questions and reject fail-only rows."""
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

PROJECT = "mqpunjvdrkqvionsjosl"
TABLE = "brainactive_questions"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/{TABLE}"
KEY = os.environ["BA_SR"]
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
ROOT = os.path.dirname(os.path.abspath(__file__))
BANKDIR = os.path.join(ROOT, "bank")
CANONICAL = os.path.join(BANKDIR, "brainactive_p3_question_bank_production.json")
RESDIR = os.path.join(BANKDIR, "qa_batches")
PAGE_SIZE = 100


def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, headers=HEAD, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            text = response.read().decode()
            return response.status, (json.loads(text) if text else None)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode(errors="replace")


def load_json(path):
    with open(path, "rb") as source:
        raw = source.read()
    for encoding in ("utf-8", "latin-1"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"Could not decode JSON: {path}")


def fetch_all_rows():
    rows = []
    offset = 0
    while True:
        status, data = req("GET", f"{BASE}?select=id,is_active,qa_status&limit={PAGE_SIZE}&offset={offset}")
        if status >= 400:
            raise RuntimeError(f"Question fetch failed: {status} {data}")
        page = data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += len(page)


def load_candidate_ids():
    raw = load_json(CANONICAL)
    questions = raw.get("questions", raw) if isinstance(raw, dict) else raw
    ids = [str(question["id"]).strip().lower() for question in questions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Canonical production bank contains duplicate IDs")
    return set(ids)


def load_verdicts():
    passed, failed = set(), set()
    for filename in glob.glob(os.path.join(RESDIR, "results_*.json")):
        results = load_json(filename)
        if not isinstance(results, list):
            raise RuntimeError(f"QA result file is not a list: {filename}")
        for result in results:
            qid = str(result.get("id", "")).strip().lower()
            if not qid:
                raise RuntimeError(f"QA result without an id: {filename}")
            is_failed = (
                result.get("match") is False
                or bool(result.get("gep_issue"))
                or (result.get("explanation_quality") and result.get("explanation_quality") != "good")
            )
            (failed if is_failed else passed).add(qid)
    return passed, failed


def patch_ids(ids, db, payload):
    failures = []
    for qid in sorted(ids):
        db_id = db[qid]["id"]
        status, response = req("PATCH", f"{BASE}?id=eq.{quote(db_id)}", payload)
        if status >= 400:
            failures.append((qid, status, response))
            print(f"PATCH FAIL {qid}: {status} {str(response)[:200]}")
        time.sleep(0.03)
    return failures


candidate_ids = load_candidate_ids()
pass_ids, fail_ids = load_verdicts()
approved = candidate_ids & pass_ids - fail_ids
rejected = candidate_ids & fail_ids - pass_ids
conflicts = candidate_ids & pass_ids & fail_ids
unassessed = candidate_ids - pass_ids - fail_ids

print(f"Canonical candidates: {len(candidate_ids)}")
print(f"Pass-only approved: {len(approved)}")
print(f"Fail-only rejected: {len(rejected)}")
print(f"Conflicts held inactive: {len(conflicts)}")
print(f"Unassessed held inactive: {len(unassessed)}")

rows = fetch_all_rows()
db = {row["id"].lower(): row for row in rows}
print(f"Fetched database rows across pages: {len(db)}")

managed = candidate_ids & set(db)
missing = candidate_ids - set(db)
if missing:
    print("Missing candidate IDs:", ", ".join(sorted(missing)))

activate_ids = approved & set(db)
reject_ids = rejected & set(db)
hold_ids = (conflicts | unassessed) & set(db)
print(f"Plan activate: {len(activate_ids)}")
print(f"Plan reject: {len(reject_ids)}")
print(f"Plan hold inactive: {len(hold_ids)}")

failures = []
failures.extend(patch_ids(activate_ids, db, {"is_active": True}))
failures.extend(patch_ids(reject_ids, db, {"is_active": False, "qa_status": "rejected"}))
failures.extend(patch_ids(hold_ids, db, {"is_active": False}))
if failures:
    print(f"Failed writes: {len(failures)}")
    sys.exit(1)

# Re-read all pages after writes and verify the managed state.
time.sleep(2)
final_rows = fetch_all_rows()
final = {row["id"].lower(): row for row in final_rows}
missing_active = sorted(qid for qid in activate_ids if not final.get(qid, {}).get("is_active"))
missing_rejected = sorted(
    qid for qid in reject_ids
    if final.get(qid, {}).get("is_active") or final.get(qid, {}).get("qa_status") != "rejected"
)
active_holds = sorted(qid for qid in hold_ids if final.get(qid, {}).get("is_active"))
if missing_active or missing_rejected or active_holds:
    print("Verification failed")
    print("Missing active:", ", ".join(missing_active))
    print("Missing rejected:", ", ".join(missing_rejected))
    print("Unexpected active holds:", ", ".join(active_holds))
    sys.exit(1)

active_count = sum(1 for row in final_rows if row.get("is_active") is True)
rejected_count = sum(1 for row in final_rows if row.get("qa_status") == "rejected")
print(f"FINAL total={len(final_rows)} active={active_count} rejected={rejected_count} held_inactive={len(hold_ids)}")
print("Activation verification complete.")
