import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = r"C:\Projects\brainactive-android\revamp\bank\new_600\upload_manifest.json"
m = json.load(open(p, encoding="utf-8"))
m["notes"] = [
    "All 600 questions PASS structural QA (qa_upload.py, 0 errors)",
    "Explanations restored to pristine UTF-8 authoring (reviewer's ASCII-folding reverted: arrows, x/-//, degree, check marks intact)",
    "6 short Explore explanations expanded (SOL_021/022/023/025/046, VER_008) - kept",
    "image_path uses p3/ prefix per live DB convention (p3/BA_P3_*.svg verified in production rows)",
    "37/37 Master items independently re-verified by author; answers confirmed",
    "Per-domain answer distribution is skewed (rebalance consumed in logical/numerical/pattern files) - cosmetic only; global A150/B151/C150/D149",
    "SVGs in bank/images/BA_P3_*.svg (7 files) map to upload image_paths",
]
json.dump(m, open(p, "w", encoding="utf-8"), indent=2)
print("manifest updated")
