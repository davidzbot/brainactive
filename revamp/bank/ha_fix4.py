import json
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
byid = {q["id"]: q for q in d["questions"]}
CODES = {"BA_P3_0533": (2, "BOX"), "BA_P3_0549": (1, "CAT"), "BA_P3_0552": (2, "CAT"), "BA_P3_0553": (2, "MAP"), "BA_P3_0571": (2, "RED"), "BA_P3_0582": (3, "RED"), "BA_P3_0659": (1, "MAP")}
def shift(w, n):
    return "".join(chr(65 + (ord(c) - 65 + n) % 26) for c in w)
n = 0
for qid, (sh, w) in CODES.items():
    q = byid[qid]
    s = shift(w, sh)
    ans = s[::-1]
    rec = [o["text"] for o in q["options"] if o["id"] == q["answer"]][0]
    assert rec == ans, "code answer mismatch " + qid
    ex = "Shift each letter forward by " + str(sh) + " (A goes to " + chr(65 + sh) + "). " + w + " becomes " + s + ", then reverse to get " + ans + "."
    assert str(sh) in q["question"] and w in q["question"]
    q["explanation"] = ex
    n += 1
print("codes fixed:", n)
G112 = "Numbers greater than 50 get a red tag. 28 has no red tag, so 28 cannot be greater than 50."
assert byid["BA_P3_G112"]["answer"] == "B"
byid["BA_P3_G112"]["explanation"] = G112
E323 = "Dog, cat and fish are all animals. A book is not an animal, so book is the odd one out."
assert byid["BA_P3_0323"]["answer"] == "C"
byid["BA_P3_0323"]["explanation"] = E323
ALT = {"BA_P3_HA_0373": "+5 then -2. The next jump is -2: 18.", "BA_P3_HA_0382": "+5 then -2. The next jump is -2: 18.", "BA_P3_HA_0379": "+2 then +3. The next jump is +3: 23.", "BA_P3_HA_0385": "+2 then +3. The next jump is +3: 22."}
for qid, tail in ALT.items():
    q = byid[qid]
    ans = [o["text"] for o in q["options"] if o["id"] == q["answer"]][0]
    assert ans in tail, "alt tail mismatch " + qid
    q["explanation"] = "The jumps alternate " + tail
print("alt fixed:", len(ALT))
json.dump(d, open(BANK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")

