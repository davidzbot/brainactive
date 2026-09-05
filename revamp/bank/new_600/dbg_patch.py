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
    "BA_P3_2411": "BA_P3_2411.svg", "BA_P3_2412": "BA_P3_2411.svg",
    "BA_P3_2421": "BA_P3_2411.svg", "BA_P3_2423": "BA_P3_2411.svg",
    "BA_P3_2424": "BA_P3_2411.svg",
    "BA_P3_2345": "BA_P3_2345.svg", "BA_P3_2350": "BA_P3_2345.svg",
    "BA_P3_2356": "BA_P3_2345.svg", "BA_P3_2361": "BA_P3_2345.svg",
    "BA_P3_2375": "BA_P3_2345.svg",
    "BA_P3_2388": "BA_P3_2388.svg", "BA_P3_2389": "BA_P3_2388.svg",
    "BA_P3_2390": "BA_P3_2388.svg", "BA_P3_2391": "BA_P3_2388.svg",
    "BA_P3_2392": "BA_P3_2388.svg", "BA_P3_2393": "BA_P3_2388.svg",
    "BA_P3_2062": "BA_P3_2062.svg",
    "BA_P3_2058": "BA_P3_2058.svg",
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
