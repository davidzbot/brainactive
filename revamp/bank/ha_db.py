import json, os, urllib.request, urllib.error
PROJECT = "mqpunjvdrkqvionsjosl"
SR = os.environ["BA_SR"]
BASE = "https://" + PROJECT + ".supabase.co/rest/v1/brainactive_questions"
HEAD = {"apikey": SR, "Authorization": "Bearer " + SR, "Content-Type": "application/json"}
def req(method, url, body=None, headers=None):
    h = dict(headers or HEAD)
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            c = resp.read().decode()
            return resp.status, json.loads(c) if c else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]
def fetch_all(select="id,qa_status,is_active"):
    from urllib.parse import quote
    rows = []
    off = 0
    while True:
        st, data = req("GET", BASE + "?select=" + quote(select) + "&limit=200&offset=" + str(off))
        assert st == 200, (st, data)
        rows.extend(data)
        if len(data) < 200:
            return rows
        off += len(data)

PAT = os.environ.get("BA_PAT", "")
MURL = "https://api.supabase.com/v1/projects/" + PROJECT + "/database/query"
def msql(query):
    import urllib.error as _e
    body = json.dumps({"query": query}).encode()
    r = urllib.request.Request(MURL, data=body, headers={"Authorization": "Bearer " + PAT, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return resp.status, json.loads(resp.read().decode())
    except _e.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:800]

