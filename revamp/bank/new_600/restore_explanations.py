"""Restore pristine unicode explanations; keep the 6 legitimately expanded ones."""
import json, glob, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
KEEP_FIXED = {"NEW_SOL_021", "NEW_SOL_022", "NEW_SOL_023",
              "NEW_SOL_025", "NEW_SOL_046", "NEW_VER_008"}
FIXED = {
    "NEW_SOL_021": "Ali started with 10 marbles and gave away 3. To find how many Ali has now, subtract: 10 - 3 = 7. Ali has 7 marbles left.",
    "NEW_SOL_022": "Mei started with 15 stickers and received 5 more from her brother. To find the new total, add: 15 + 5 = 20. Mei now has 20 stickers.",
    "NEW_SOL_023": "The box started with 20 apples and 8 were sold (taken away). To find how many remain, subtract: 20 - 8 = 12. There are 12 apples left.",
    "NEW_SOL_025": "Sara ran in two parts: first 60 metres, then 25 more metres. To find the total distance, add both parts: 60 + 25 = 85 m. Sara ran 85 metres in total.",
    "NEW_SOL_046": "The pins form rows of 1, 2, 3 and 4. To find the total, add all rows: 1 + 2 + 3 + 4 = 10. There are 10 pins in total.",
    "NEW_VER_008": "Each letter is converted to its position in the alphabet (P=16, I=9, G=7), then added together: 16 + 9 + 7 = 32. PIG is coded as 32.",
}

parts = {}
for fn in sorted(glob.glob(os.path.join(HERE, "new_*.json"))):
    base = os.path.basename(fn)
    if base.startswith(("fix_", "patch", "rebalance", "qa_")) or "brainactive_new" in base:
        continue
    for q in json.load(open(fn, encoding="utf-8")):
        parts[q["question"].strip()] = q

# 1) staging file
sp = os.path.join(HERE, "brainactive_new_600_20260905.json")
sd = json.load(open(sp, encoding="utf-8"))
restored = kept = 0
for q in sd["questions"]:
    p = parts.get(q["question"].strip())
    assert p, q["id"]
    if p["id"] in KEEP_FIXED:
        # re-apply the improved explanation (staging currently has corrupted one)
        q["explanation"] = FIXED[p["id"]]
        kept += 1
    else:
        q["explanation"] = p["explanation"]
        restored += 1
json.dump(sd, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"staging: restored {restored}, kept improved {kept}")

# 2) upload file (match by question text; keep IDs/options/answers/paths)
up_path = os.path.join(HERE, "brainactive_new_600_upload.json")
ud = json.load(open(up_path, encoding="utf-8"))
restored = kept = 0
for q in ud["questions"]:
    p = parts.get(q["question"].strip())
    assert p, q["id"]
    if p["id"] in KEEP_FIXED:
        q["explanation"] = FIXED[p["id"]]
        kept += 1
    else:
        q["explanation"] = p["explanation"]
        restored += 1
json.dump(ud, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"upload: restored {restored}, kept improved {kept}")
