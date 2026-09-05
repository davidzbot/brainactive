"""QA the tone pass directly against live DB rows."""
import json, os, re, io, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tone_explanations import OPENERS

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

rows, offset = [], 0
while True:
    url = f"{BASE}?select=id,explanation&order=id&limit=100&offset={offset}"
    req = urllib.request.Request(url, headers=HEAD)
    page = json.loads(urllib.request.urlopen(req).read().decode())
    if not page:
        break
    rows.extend(page)
    offset += len(page)

print(f"rows: {len(rows)}")
errs = []
opener_count = {o: 0 for o in OPENERS}
for r in rows:
    e = r.get("explanation") or ""
    hit = [o for o in OPENERS if e.startswith(o)]
    if not hit:
        errs.append(f"{r['id']}: missing opener")
    else:
        opener_count[hit[0]] += 1
    if "\n\n\n" in e:
        errs.append(f"{r['id']}: triple newline")
    if e != e.strip():
        errs.append(f"{r['id']}: leading/trailing whitespace")
    if not e.strip():
        errs.append(f"{r['id']}: empty explanation")

print("opener distribution:")
for o, c in opener_count.items():
    print(f"  {c:5d}  {o}")
print(f"\nERRORS: {len(errs)}")
for e in errs[:20]:
    print("  E:", e[:160])
sys.exit(1 if errs else 0)
