import json, os, io, sys, urllib.request
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
ud = json.load(open(os.path.join(HERE, "brainactive_new_600_upload.json"), encoding="utf-8"))
q = next(x for x in ud["questions"] if x["id"] == "BA_P3_2366")
body = json.dumps({"question": q["question"], "options": q["options"],
                   "answer": q["answer"], "explanation": q["explanation"]}).encode()
req = urllib.request.Request(f"{BASE}?id=eq.BA_P3_2366", data=body, headers=dict(HEAD), method="PATCH")
with urllib.request.urlopen(req) as resp:
    print("PATCH status:", resp.status)
# read back
req = urllib.request.Request(f"{BASE}?select=id,question,answer,options,explanation&id=eq.BA_P3_2366", headers=HEAD)
row = json.loads(urllib.request.urlopen(req).read().decode())[0]
assert row["question"] == q["question"] and row["answer"] == "C"
assert row["options"] == q["options"] and row["explanation"] == q["explanation"]
print("read-back verified: C) H only correct answer")
