import json, random
rng = random.Random(20260923)
NEW = "revamp/bank/ha_new_20260921.json"
newqs = json.load(open(NEW, encoding="utf-8"))
byid = {q["id"]: q for q in newqs}
def fit(x1, y1):
    f = []
    for n in range(0, 60):
        if x1 + n == y1:
            f.append(("add", n))
    for a in range(2, 12):
        if a * x1 == y1:
            f.append(("mul", a))
    for a in range(2, 6):
        for b in range(-12, 13):
            if b != 0 and a * x1 + b == y1:
                f.append(("dual", a, b))
    if x1 * x1 == y1:
        f.append(("sq",))
    return f
def app(r, x):
    if r[0] == "add":
        return x + r[1]
    if r[0] == "mul":
        return r[1] * x
    if r[0] == "dual":
        return r[1] * x + r[2]
    return x * x
def shuffle_opts(texts, ans):
    order = list(range(4))
    rng.shuffle(order)
    opts = [{"id": "ABCD"[i], "text": str(texts[j])} for i, j in enumerate(order)]
    return opts, "ABCD"[order.index(ans)]
IDS = ["BA_P3_HA_0205", "BA_P3_HA_0209", "BA_P3_HA_0216", "BA_P3_HA_0220", "BA_P3_HA_0222", "BA_P3_HA_0228"]
for qid in IDS:
    old = byid.get(qid)
    if old is None or old["archetype"] != "compound_rule_analogy":
        print("SKIP", qid, old["archetype"] if old else None)
        continue
    for _ in range(5000):
        a = rng.randint(2, 4)
        b = rng.choice([x for x in range(-9, 10) if x != 0])
        x1 = rng.randint(3, 9)
        x2 = rng.randint(2, 9)
        if x2 == x1:
            continue
        y1 = a * x1 + b
        y2 = a * x2 + b
        if y1 <= 0 or y2 <= 0 or y1 >= 100 or y2 >= 100:
            continue
        fr = fit(x1, y1)
        if ("dual", a, b) not in fr:
            continue
        bad = set()
        for r in fr:
            if r == ("dual", a, b):
                continue
            bad.add(app(r, x2))
        if y2 in bad:
            continue
        near = [y2 + 1, y2 - 1, y2 + 2, y2 - 2, y2 + a, y2 - a, y2 + 10, y2 - 10, y1]
        opts = [y2]
        for c in near:
            if len(opts) >= 4:
                break
            if c > 0 and c not in opts and c not in bad:
                opts.append(c)
        if len(opts) < 4:
            continue
        break
    else:
        raise RuntimeError("dual regen failed " + qid)
    op = "+" if b > 0 else "-"
    stem = str(x1) + " is to " + str(y1) + " as " + str(x2) + " is to ___?"
    expl = "Find the hidden two-step rule: x " + str(a) + " then " + op + " " + str(abs(b)) + ". Check: " + str(x1) + " x " + str(a) + " " + op + " " + str(abs(b)) + " = " + str(y1) + ". Apply it: " + str(x2) + " x " + str(a) + " " + op + " " + str(abs(b)) + " = " + str(y2) + "."
    o2, aid = shuffle_opts([str(o) for o in opts], 0)
    old.update({"question": stem, "options": o2, "answer": aid, "explanation": expl})
    print("refit", qid, stem, "->", y2)
json.dump(newqs, open(NEW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")

