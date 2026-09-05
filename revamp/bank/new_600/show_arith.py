import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PAT = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)\s*([+\-x\u2212\u00d7*/\u00f7])\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)(?!\d)")
up = {q["id"]: q for q in json.load(
    open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json",
         encoding="utf-8"))["questions"]}
prod = {q["id"]: q for q in json.load(
    open(r"C:\Projects\brainactive-android\revamp\bank\brainactive_p3_question_bank_production.json",
         encoding="utf-8"))["questions"]}
for qid in sys.argv[1:]:
    q = up.get(qid) or prod.get(qid)
    print("=" * 90)
    print(qid, "| ans:", q["answer"])
    print("Q:", q["question"][:200])
    print("EXP:", q["explanation"][:700])
