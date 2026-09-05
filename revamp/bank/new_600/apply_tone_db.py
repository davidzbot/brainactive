"""Apply teacher-tone normalization to ALL DB explanations + mirror to local JSONs.
Usage: apply_tone_db.py [--preview N] [--apply]   (needs BA_SR env for apply)
"""
import json, os, io, sys, time, urllib.request
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tone_explanations import normalize, OPENERS

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def fetch_all():
    rows, offset = [], 0
    while True:
        url = f"{BASE}?select=id,explanation&order=id&limit=100&offset={offset}"
        req = urllib.request.Request(url, headers=HEAD)
        page = json.loads(urllib.request.urlopen(req).read().decode())
        if not page:
            return rows
        rows.extend(page)
        offset += len(page)


def main():
    preview = "--preview" in sys.argv
    apply = "--apply" in sys.argv
    n = 5
    for a in sys.argv[1:]:
        if a.isdigit():
            n = int(a)
    rows = fetch_all()
    print(f"DB rows: {len(rows)}")
    plan = []
    for r in rows:
        new_text, changed = normalize(r["id"], r.get("explanation") or "")
        if changed:
            plan.append((r["id"], r.get("explanation") or "", new_text))
    print(f"to update: {len(plan)}")
    if preview:
        for qid, old, new in plan[:n]:
            print("=" * 70)
            print(qid, "\n--- OLD ---\n" + old[:400] + "\n--- NEW ---\n" + new[:600])
        return
    if not apply:
        print("pass --preview N or --apply")
        return
    ok = fail = 0
    for qid, old, new in plan:
        url = f"{BASE}?id=eq.{quote(qid)}"
        req = urllib.request.Request(url, data=json.dumps({"explanation": new}).encode(),
                                     headers=HEAD, method="PATCH")
        try:
            with urllib.request.urlopen(req) as resp:
                resp.read()
                ok += 1
        except Exception as e:
            fail += 1
            print(f"PATCH FAIL {qid}: {e}")
        time.sleep(0.02)
    print(f"patched: {ok}, failed: {fail}")

    # mirror into local JSONs by id
    newmap = {qid: new for qid, old, new in plan}
    for path in [os.path.join(HERE, "..", "brainactive_p3_question_bank_production.json"),
                 os.path.join(HERE, "brainactive_new_600_upload.json")]:
        d = json.load(open(path, encoding="utf-8"))
        qs = d["questions"] if isinstance(d, dict) else d
        c = 0
        for q in qs:
            if q.get("id") in newmap:
                q["explanation"] = newmap[q["id"]]
                c += 1
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"mirrored {c} into {os.path.basename(path)}")


main()
