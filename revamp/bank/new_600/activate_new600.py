"""Activate BA_P3_1840-2439 (single bulk PATCH, fixed-width IDs sort lexicographically)."""
import json, os, io, sys, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

url = f"{BASE}?id=gte.BA_P3_1840&id=lte.BA_P3_2439"
req = urllib.request.Request(url, data=json.dumps({"is_active": True}).encode(),
                             headers={**HEAD, "Prefer": "return=minimal"}, method="PATCH")
with urllib.request.urlopen(req) as resp:
    resp.read()
    print("bulk PATCH status:", resp.status)

# verify
def count(qs):
    url = f"{BASE}?select=id&{qs}&limit=1"
    req = urllib.request.Request(url, headers={**HEAD, "Prefer": "count=exact"})
    with urllib.request.urlopen(req) as resp:
        resp.read()
        cr = resp.headers.get("Content-Range", "")
        return cr.split("/")[-1]

print("active in 1840-2439:", count("id=gte.BA_P3_1840&id=lte.BA_P3_2439&is_active=eq.true"))
print("total active:", count("is_active=eq.true"))
print("total rows:", count("select=id"))
