import json, os, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
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
up_path = os.path.join(HERE, "brainactive_new_600_upload.json")
ud = json.load(open(up_path, encoding="utf-8"))
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        q["image_path"] = f"p3/{ASSIGN[q['id']]}"
        q["visual_required"] = True
        if not q.get("visual_spec"):
            q["visual_spec"] = {"type": "diagram", "note": "see image"}
json.dump(ud, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("upload JSON mirrored")
text2svg = {}
for q in ud["questions"]:
    if q["id"] in ASSIGN:
        text2svg[q["question"].strip()] = ASSIGN[q["id"]]
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    qs = json.load(open(fn, encoding="utf-8"))
    dirty = False
    for q in qs:
        hit = text2svg.get(q["question"].strip())
        if hit:
            q["image_path"] = f"p3/{hit}"
            q["visual_required"] = True
            if not q.get("visual_spec"):
                q["visual_spec"] = {"type": "diagram", "note": "see image"}
            dirty = True
    if dirty:
        json.dump(qs, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("mirrored", base)
for svg in sorted(set(ASSIGN.values())):
    src = os.path.join(HERE, "..", "images", svg)
    dst = os.path.join(HERE, "images", svg)
    if os.path.abspath(src) != os.path.abspath(dst):
        open(dst, "wb").write(open(src, "rb").read())
print("DONE")
