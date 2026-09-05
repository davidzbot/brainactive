"""Verify DB rows 1840-2439 match the upload file (options/answers/stems/explainers)."""
import json, os, io, sys, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

want = {q["id"]: q for q in
        json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))["questions"]}

got = {}
offset = 0
while len(got) < 600:
    url = (f"{BASE}?select=id,domain,topic,skill,level,answer,options,question,explanation,image_path,is_active,qa_status"
           f"&id=gte.BA_P3_1840&id=lte.BA_P3_2439&order=id&limit=100&offset={offset}")
    req = urllib.request.Request(url, headers=HEAD)
    page = json.loads(urllib.request.urlopen(req).read().decode())
    if not page:
        break
    for r in page:
        got[r["id"]] = r
    offset += len(page)

print(f"fetched: {len(got)}/600")
errs = []
for qid, w in want.items():
    g = got.get(qid)
    if not g:
        errs.append(f"{qid}: MISSING in DB")
        continue
    if g["question"] != w["question"]:
        errs.append(f"{qid}: stem mismatch")
    if [(o["id"], o["text"]) for o in g["options"]] != [(o["id"], o["text"]) for o in w["options"]]:
        errs.append(f"{qid}: options mismatch")
    if g["answer"] != w["answer"]:
        errs.append(f"{qid}: answer mismatch DB={g['answer']} file={w['answer']}")
    if (g["explanation"] or "") != (w["explanation"] or ""):
        errs.append(f"{qid}: explanation mismatch")
    if (g["image_path"] or "") != (w["image_path"] or ""):
        errs.append(f"{qid}: image_path mismatch")
    if g.get("is_active") is not True:
        errs.append(f"{qid}: not active")
    if g.get("qa_status") != "validated_new600_20260905":
        errs.append(f"{qid}: qa_status wrong")

print(f"MISMATCHES: {len(errs)}")
for e in errs[:20]:
    print("  E:", e[:200])
sys.exit(1 if errs else 0)
