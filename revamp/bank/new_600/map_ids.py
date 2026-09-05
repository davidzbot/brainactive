import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open(r"C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_upload.json", encoding="utf-8"))
keys = ["folded in half so the top edge meets the bottom edge. A hole is punched in the top-right",
        "folded in half so the left edge meets the right edge. A hole is punched in the top-right",
        "folded in half so the bottom edge meets the top edge. A hole is punched in the bottom-left",
        "folded in half top-to-bottom, then in half left-to-right (a quarter",
        "folded in half left-to-right. A hole is punched in the top-right corner of the folded packet",
        "folded in half top-to-bottom, then in half left-to-right. A hole is punched in the middle",
        "then in half top-to-bottom again (one-eighth",
        "row of 4 squares P, Q, R, S with T above Q and U below R. When folded with Q at the front",
        "Which of these can fold into a closed cube? A) 5 squares",
        "Which of these nets CANNOT fold"]
for q in d["questions"]:
    for k in keys:
        if k in q["question"]:
            print(q["id"], "|", q["question"][:60])
            break
