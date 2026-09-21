import json, re, collections
BANK = "revamp/bank/brainactive_p3_question_bank_production.json"
d = json.load(open(BANK, encoding="utf-8"))
qs = d["questions"]
byid = {q["id"]: q for q in qs}
verdict = {}
def mark(qid, v, reason):
    verdict[qid] = {"verdict": v, "reason": reason}
active = [q for q in qs if q.get("qa_status") != "rejected_duplicate"]
for q in active:
    mark(q["id"], "keep", "passes HA bar or needs solver sample-check")
def R(rule, qids, reason):
    for qid in qids:
        if verdict[qid]["verdict"] == "keep":
            mark(qid, "delete", rule + ": " + reason)
R("R1", [q["id"] for q in active if q["archetype"] == "figure_odd_one_out"], "single-feature discrimination, GEP needs abstract SPONCS rule")
R("R2", [q["id"] for q in active if q["archetype"] == "linear_order" and q["id"] != "BA_P3_0060"], "order fully given, transcription not inference")
R("R3", [q["id"] for q in active if q["archetype"] == "figure_analogy" and q["id"] not in ("BA_P3_0025", "BA_P3_0087")], "single-attribute change stated in stem")
R("R4", [q["id"] for q in active if q["archetype"] == "letter_series"], "gap rule stated in stem, application not discovery")
def is_direct(q):
    t = q["question"]
    return "What can we conclude?" in t and re.search(r"Given: .* (is a|is an|is in|ends in|measures|contains|has) ", t)
R("R5", [q["id"] for q in active if q["archetype"] == "conditional_contrapositive" and is_direct(q)], "direct modus ponens read-off, not contrapositive")

def rule_of(q):
    m = re.search(r"Relation:\s*(.+?)\.", q.get("explanation", ""))
    return m.group(1).strip() if m else ""
def is_single_op(rule):
    return bool(re.match(r"^(x\d+|\+\d+|square the number)$", rule))
R("R6", [q["id"] for q in active if q["archetype"] == "number_analogy" and is_single_op(rule_of(q))], "single-operation rule on small numbers, HA needs dual-relation")
def apply_rule(rule, x):
    rl = rule.lower()
    if "square" in rl:
        return x * x
    m = re.match(r"x(\d+)\s*then\s*([+-])(\d+)", rl)
    if m:
        return x * int(m.group(1)) + (int(m.group(3)) if m.group(2) == "+" else -int(m.group(3)))
    m = re.match(r"x(\d+)$", rl)
    if m:
        return x * int(m.group(1))
    m = re.match(r"\+(\d+)$", rl)
    if m:
        return x + int(m.group(1))
    return None
wrong = []
for q in active:
    if q["archetype"] != "number_analogy":
        continue
    nums = list(map(int, re.findall(r"\d+", q["question"])))
    if len(nums) < 3:
        continue
    pred = apply_rule(rule_of(q), nums[2])
    if pred is None:
        continue
    ans_txt = next(o["text"] for o in q["options"] if o["id"] == q["answer"])
    m2 = re.search(r"-?\d+", ans_txt)
    if m2 and int(m2.group()) != pred:
        wrong.append(q["id"])
R("R6b", wrong, "recorded answer contradicts recomputed rule, wrong answer or explanation")
dbl = [q["id"] for q in active if q["archetype"] in ("figure_sequence", "count_sequence") and re.search(r"(2, ?4, ?8|1, ?2, ?4, ?8|3, ?6, ?12|4, ?8, ?16)", q["question"])]
R("R7", dbl[2:], "pure doubling dot-count, HA needs compound rules")
R("R8", [q["id"] for q in active if q["archetype"] in ("rotation", "single_rotation") and ("once" in q["question"].lower() or (q["question"].count("90 degrees") == 1 and "twice" not in q["question"].lower() and "2 times" not in q["question"].lower()))], "single 90-degree turn, HA needs multi-step")
R("R9", ["BA_P3_0044"], "one-step arithmetic, not heuristic")

from collections import defaultdict
mach = [q for q in active if q["archetype"] == "pattern_application" and re.search(r"(machine|transformer|box|device|processor)", q["question"], re.I)]
sig = defaultdict(list)
for q in mach:
    sig[rule_of(q) or q["question"][:40]].append(q["id"])
for s, ids in sig.items():
    R("R10", ids[2:], "near-identical machine-rule template swarm, keep 2 exemplars per rule")
def trim(arch, keep_n):
    items = [q["id"] for q in active if q["archetype"] == arch]
    R("R11", items[keep_n:], "routine-arithmetic template swarm, keep exemplars")
trim("before_after_transfer", 3)
trim("chain_comparison", 3)
trim("before_after", 2)
gaps = [q for q in active if q["archetype"] == "draw_diagram_gaps"]
circ = [q["id"] for q in gaps if re.search(r"circular|pond|track", q["question"], re.I)][:2]
line = [q["id"] for q in gaps if not re.search(r"circular|pond|track", q["question"], re.I)][:2]
R("R11", [q["id"] for q in gaps if q["id"] not in circ + line], "routine fencepost template swarm, keep 2 straight plus 2 circular")
dels = [k for k, v in verdict.items() if v["verdict"] == "delete"]
keeps = [k for k, v in verdict.items() if v["verdict"] == "keep"]
print("ACTIVE:", len(active), "DELETE:", len(dels), "KEEP:", len(keeps))
cnt = collections.Counter(verdict[k]["reason"].split(":")[0] for k in dels)
for k in sorted(cnt):
    print(k, cnt[k])
json.dump(verdict, open("revamp/bank/ha_audit_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
kd = collections.Counter(byid[k]["domain"] for k in keeps)
dd = collections.Counter(byid[k]["domain"] for k in dels)
print("KEEP by domain:", dict(kd))
print("DELETE by domain:", dict(dd))
print("WROTE revamp/bank/ha_audit_20260921.json")

mm = []
for q in active:
    if verdict[q["id"]]["verdict"] != "keep":
        continue
    if q["archetype"] != "number_analogy":
        continue
    stem_nums = set(re.findall(r"\d+", q["question"]))
    opt_nums = set(re.findall(r"\d+", " ".join(o["text"] for o in q["options"])))
    for n in set(re.findall(r"\d+", q.get("explanation", ""))):
        if n not in stem_nums and n not in opt_nums:
            mm.append(q["id"])
            break
R("R6c", mm, "explanation cites numbers absent from stem and options, copy-paste explanation")

dels = [k for k, v in verdict.items() if v["verdict"] == "delete"]
keeps = [k for k, v in verdict.items() if v["verdict"] == "keep"]
print("FINAL ACTIVE:", len(active), "DELETE:", len(dels), "KEEP:", len(keeps))
cnt = collections.Counter(verdict[k]["reason"].split(":")[0] for k in dels)
for k in sorted(cnt):
    print(k, cnt[k])
json.dump(verdict, open("revamp/bank/ha_audit_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE FINAL revamp/bank/ha_audit_20260921.json")

good11 = ["BA_P3_0124", "BA_P3_0140", "BA_P3_0154", "BA_P3_0161", "BA_P3_0170", "BA_P3_0171", "BA_P3_0172", "BA_P3_0191", "BA_P3_0216", "BA_P3_0262", "BA_P3_ADD_0006"]
for k in good11:
    verdict[k] = {"verdict": "keep", "reason": "dual-relation analogy, stray token is the rule constant only, solver to verify"}
for k in ["BA_P3_0181", "BA_P3_0183", "BA_P3_0190", "BA_P3_0246"]:
    verdict[k] = {"verdict": "delete", "reason": "R6c: copy-pasted sequence explanation in analogy item plus single-op rule"}
dels = [k for k, v in verdict.items() if v["verdict"] == "delete"]
keeps = [k for k, v in verdict.items() if v["verdict"] == "keep"]
print("CORRECTED DELETE:", len(dels), "KEEP:", len(keeps))
json.dump(verdict, open("revamp/bank/ha_audit_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
kd = collections.Counter(byid[k]["domain"] for k in keeps)
dd = collections.Counter(byid[k]["domain"] for k in dels)
print("KEEP by domain:", dict(kd))
print("DELETE by domain:", dict(dd))
print("WROTE CORRECTED revamp/bank/ha_audit_20260921.json")

