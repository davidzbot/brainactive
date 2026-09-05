import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
PROJECT = "mqpunjvdrkqvionsjosl"
BASE = f"https://{PROJECT}.supabase.co/rest/v1/brainactive_questions"
KEY = os.environ.get("BA_SR", "")
HEAD = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
def req(method, url, body=None, headers=None):
    rh = dict(headers or HEAD)
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(url, data=data, headers=rh, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except Exception as e:
        return -1, str(e)


ASSIGN = {
    "BA_P3_2428": "BA_P3_2428.svg", "BA_P3_2429": "BA_P3_2429.svg",
    "BA_P3_2430": "BA_P3_2430.svg", "BA_P3_2435": "BA_P3_2435.svg",
    "BA_P3_2436": "BA_P3_2429.svg", "BA_P3_2438": "BA_P3_2438.svg",
    "BA_P3_2439": "BA_P3_2439.svg", "BA_P3_2395": "BA_P3_2395.svg",
    "BA_P3_2396": "BA_P3_2395.svg", "BA_P3_2397": "BA_P3_2395.svg",
    "BA_P3_2398": "BA_P3_2395.svg", "BA_P3_2381": "BA_P3_2381.svg",
    "BA_P3_2400": "BA_P3_2400.svg",
}
import time
fails = []
for qid, svg in sorted(ASSIGN.items()):
    s, r = req("PATCH", f"{BASE}?id=eq.{qid}", {"image_path": f"p3/{svg}"})
    print(qid, s)
    if s != 204:
        fails.append((qid, s, r[:150]))
    time.sleep(0.05)
print("FAILS:", fails)
