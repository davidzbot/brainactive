import json, re, random, collections
rng = random.Random(20260922)
NEW = json.load(open("revamp/bank/ha_new_20260921.json", encoding="utf-8"))
byid = {q["id"]: q for q in NEW}
SHAPES = [("triangle", 3), ("square", 4), ("pentagon", 5), ("hexagon", 6)]
SIZES = ["small", "large"]
COLOURS = ["red", "blue", "green"]
CYC = ["red", "blue", "green"]
def fdesc(f):
    s = f["size"] + " " + f["colour"] + " " + f["shape"]
    if f["dot"]:
        s += " with a dot"
    return s
def randfig():
    sh = rng.choice(SHAPES)[0]
    return {"size": rng.choice(SIZES), "colour": rng.choice(COLOURS), "shape": sh, "dot": rng.random() < 0.5}
def sides(f):
    return {"triangle": 3, "square": 4, "pentagon": 5, "hexagon": 6}[f["shape"]]
def shuffle_opts(texts, ans):
    order = list(range(4))
    rng.shuffle(order)
    opts = [{"id": "ABCD"[i], "text": str(texts[j])} for i, j in enumerate(order)]
    return opts, "ABCD"[order.index(ans)]
fixed = {}
def refit(qid, domain, topic, skill, arch, level, diff, q, texts, ans, expl, reason, tags):
    texts = [str(x) for x in texts]
    assert len(texts) == 4 and len(set(texts)) == 4
    opts, aid = shuffle_opts(texts, ans)
    old = byid[qid]
    old.update({"domain": domain, "topic": topic, "skill": skill, "archetype": arch, "level": level, "difficulty": diff, "question": q, "options": opts, "answer": aid, "explanation": expl, "reasoning": reason, "tags": tags})
    fixed[qid] = True
def t_shape_up(f):
    order = ["triangle", "square", "pentagon", "hexagon"]
    i = order.index(f["shape"])
    if i >= 3:
        return None
    g = dict(f)
    g["shape"] = order[i + 1]
    return g
def t_shape_dn(f):
    order = ["triangle", "square", "pentagon", "hexagon"]
    i = order.index(f["shape"])
    if i <= 0:
        return None
    g = dict(f)
    g["shape"] = order[i - 1]
    return g
def t_col1(f):
    g = dict(f)
    g["colour"] = CYC[(CYC.index(f["colour"]) + 1) % 3]
    return g
def t_col2(f):
    g = dict(f)
    g["colour"] = CYC[(CYC.index(f["colour"]) + 2) % 3]
    return g
def t_size(f):
    g = dict(f)
    g["size"] = "large" if f["size"] == "small" else "small"
    return g
def t_dot(f):
    g = dict(f)
    g["dot"] = not f["dot"]
    return g
TN2 = {id(t_shape_up): "gains one side", id(t_shape_dn): "loses one side", id(t_col1): "changes colour", id(t_col2): "changes colour", id(t_size): "changes size", id(t_dot): "gains or loses its dot"}
ANAIDS = [q["id"] for q in NEW if q["archetype"] == "figure_analogy"]
def gen_ana2(nt, level):
    for _ in range(2000):
        ts = rng.sample([t_shape_up, t_shape_dn, t_col1, t_col2, t_size, t_dot], nt)
        if t_col1 in ts and t_col2 in ts:
            continue
        f1 = randfig()
        if t_shape_up in ts and f1["shape"] == "hexagon":
            continue
        if t_shape_dn in ts and f1["shape"] == "triangle":
            continue
        f2 = f1
        for t in ts:
            f2 = t(f2)
        f3 = randfig()
        if t_shape_up in ts and f3["shape"] == "hexagon":
            continue
        if t_shape_dn in ts and f3["shape"] == "triangle":
            continue
        f4 = f3
        for t in ts:
            f4 = t(f4)
        if fdesc(f4) == fdesc(f3):
            continue
        cands = [fdesc(f4)]
        for t in ts:
            p = t(dict(f3))
            if p is not None and fdesc(p) not in cands:
                cands.append(fdesc(p))
        if fdesc(f3) not in cands:
            cands.append(fdesc(f3))
        if len(cands) < 4:
            continue
        cands = cands[:4]
        names = " and ".join(sorted(set(TN2[id(t)] for t in ts)))
        stem = "A " + fdesc(f1) + " changes into a " + fdesc(f2) + ". Using the same change, a " + fdesc(f3) + " changes into ___?"
        expl = "Work out the hidden change from the first pair: it " + names + ". Apply all of them to the new figure: a " + fdesc(f3) + " becomes a " + fdesc(f4) + "."
        return stem, cands, expl
    return None
n = 0
for qid in ANAIDS:
    old = byid[qid]
    nt = 3 if old["level"] == "Challenge" else 2
    for _ in range(50):
        r = gen_ana2(nt, old["level"])
        if not r:
            continue
        stem, cands, expl = r
        if len(set(cands)) == 4:
            break
    else:
        raise RuntimeError("ana regen failed " + qid)
    refit(qid, "pattern_abstract", "Pattern and Abstract", "5.4", "figure_analogy", old["level"], old["difficulty"], stem, cands, 0, expl, "Infer simultaneous transformations and apply all.", ["figure_analogy", "compound_rule"])
    n += 1
print("ana refit:", n)

def L(v):
    return chr(64 + v)
LEIDS = [q["id"] for q in NEW if q["archetype"] == "letter_patterns"]
GAPSET2 = [[3, 3, 3, 3], [4, 4, 4, 4], [2, 2, 2, 2], [2, 3, 2, 3], [3, -1, 3, -1], [4, -1, 4, -1], [3, 2, 3, 2], [1, 2, 3, 4], [2, 3, 4, 5]]
def gen_letter2(gaps, level):
    for _ in range(2000):
        grow = len(gaps) >= 2 and all(gaps[i+1] - gaps[i] == 1 for i in range(len(gaps) - 1))
        nxtgap = gaps[-1] + 1 if grow else gaps[0]
        smax = 26 - (sum(gaps) + nxtgap)
        if smax < 3:
            return None
        start = rng.randint(2, smax)
        vals = [start]
        for g in gaps:
            vals.append(vals[-1] + g)
        if min(vals) < 1 or max(vals) > 26:
            continue
        letters = [L(v) for v in vals]
        if len(set(letters)) < len(letters):
            continue
        nxt = vals[-1] + nxtgap
        if nxt < 1 or nxt > 26 or L(nxt) in letters:
            continue
        ans = L(nxt)
        pool = [L(nxt + dd) for dd in (1, -1, 2, -2, 3, -3, 4, -4)]
        opts = [ans]
        for c in pool:
            if len(opts) >= 4:
                break
            if c not in opts and c not in letters and "A" <= c <= "Z":
                opts.append(c)
        if len(opts) < 4:
            continue
        break
    else:
        return None
    stem = "A letter pattern goes: " + ", ".join(letters) + ", ___. What comes next?"
    seq = ", ".join(letters + [ans])
    gp = []
    for i in range(1, len(vals + [nxt])):
        dd = (vals + [nxt])[i] - (vals + [nxt])[i - 1]
        gp.append(("+" if dd >= 0 else "") + str(dd))
    expl = "Look at the jumps between letters: " + ", ".join(gp) + ". The jumps follow a repeating pattern, so the next jump gives " + ans + ". Full pattern: " + seq + "."
    return stem, opts, expl
n = 0
for i, qid in enumerate(LEIDS):
    old = byid[qid]
    gaps = GAPSET2[i % len(GAPSET2)]
    lvl = "Challenge" if len(set(gaps)) > 2 or max([abs(x) for x in gaps]) > 3 else "Think"
    for _ in range(50):
        r = gen_letter2(gaps, lvl)
        if r:
            break
    else:
        raise RuntimeError("letter regen failed " + qid)
    stem, opts, expl = r
    refit(qid, "verbal_reasoning", "Verbal Reasoning", "3.6", "letter_patterns", lvl, "hard" if lvl == "Challenge" else "medium", stem, opts, 0, expl, "Discover the hidden jump pattern.", ["letter_series", "hidden_rule"])
    n += 1
print("letter refit:", n)
BOYN = ["Ali", "Ben", "Cai", "Dan", "Eli", "Finn", "Gus", "Hari", "Ivan", "Jay"]
GIRLN = ["Amy", "Bella", "Cindy", "Diya", "Eva", "Fiona", "Gina", "Hana", "Iris", "Jia"]
THINGS = ["stickers", "marbles", "cards", "shells", "badges", "coins", "stamps", "buttons"]
CHIDS = [q["id"] for q in NEW if q["archetype"] == "chained_comparison"]
def gen_chain2():
    for _ in range(2000):
        names = rng.sample(BOYN + GIRLN, 4)
        t = rng.choice(THINGS)
        base = rng.randint(12, 30)
        diffs = [rng.randint(2, 8) * rng.choice([1, -1]) for _ in range(3)]
        counts = [base]
        for dd in diffs:
            counts.append(counts[-1] - dd)
        if min(counts) <= 0:
            continue
        if len(set(counts)) < 4:
            continue
        rels = []
        for i in range(3):
            if diffs[i] > 0:
                rels.append(names[i] + " has " + str(abs(diffs[i])) + " more " + t + " than " + names[i + 1])
            else:
                rels.append(names[i] + " has " + str(abs(diffs[i])) + " fewer " + t + " than " + names[i + 1])
        anch = rng.randint(0, 3)
        given = dict(zip(names, counts))
        ask = rng.choice(["most", "count"])
        if ask == "most":
            if list(counts).count(max(counts)) > 1:
                continue
            top = names[counts.index(max(counts))]
            stem = ". ".join(rels) + ". " + names[anch] + " has " + str(counts[anch]) + " " + t + ". Who has the most " + t + "?"
            expl = "Work along the chain from " + names[anch] + " (" + str(counts[anch]) + "): " + "; ".join(names[i] + " = " + str(counts[i]) for i in range(4)) + ". The most is " + top + "."
            return stem, names, names.index(top), expl, "Chain three comparisons from the known count."
        target = rng.choice([x for x in names if x != names[anch]])
        stem = ". ".join(rels) + ". " + names[anch] + " has " + str(counts[anch]) + " " + t + ". How many " + t + " does " + target + " have?"
        tv = given[target]
        cands = [str(tv), str(tv + diffs[0]), str(tv - diffs[0]), str(tv + 1)]
        if len(set(cands)) < 4:
            continue
        expl = "Work along the chain from " + names[anch] + " (" + str(counts[anch]) + "): " + "; ".join(names[i] + " = " + str(counts[i]) for i in range(4)) + ". So " + target + " has " + str(tv) + "."
        return stem, cands, 0, expl, "Chain three comparisons from the known count."
    return None
n = 0
for qid in CHIDS:
    old = byid[qid]
    for _ in range(100):
        r = gen_chain2()
        if r:
            break
    else:
        raise RuntimeError("chain regen failed " + qid)
    stem, texts, ans, expl, reason = r
    refit(qid, "numerical_reasoning", "Numerical Thinking", "1.4", "chained_comparison", "Think", "medium", stem, texts, ans, expl, reason, ["chain_comparison", "four_person"])
    n += 1
print("chain refit:", n)

ODDRULES = [
    ("ODD-A", "A figure has a dot exactly when it has an even number of sides.", lambda f: f["dot"] == (sides(f) % 2 == 0)),
    ("ODD-B", "A figure is small exactly when it is a triangle.", lambda f: (f["size"] == "small") == (f["shape"] == "triangle")),
    ("ODD-C", "A figure is blue exactly when it has more than 4 sides.", lambda f: (f["colour"] == "blue") == (sides(f) > 4)),
    ("ODD-D", "A figure has a dot exactly when it is large.", lambda f: f["dot"] == (f["size"] == "large")),
    ("ODD-E", "A figure is green exactly when it has 3 or 6 sides.", lambda f: (f["colour"] == "green") == (sides(f) in (3, 6))),
    ("ODD-F", "A figure has a dot exactly when it is large AND has an even number of sides.", lambda f: f["dot"] == (f["size"] == "large" and sides(f) % 2 == 0)),
]
ODIDS = [q["id"] for q in NEW if q["archetype"] == "figure_odd_one_rule"]
def gen_odd2(rule_id, rule_txt, pred, level):
    for _ in range(3000):
        figs = []
        seen = set()
        tries = 0
        while len(figs) < 4 and tries < 500:
            tries += 1
            f = randfig()
            dd = fdesc(f)
            if dd in seen:
                continue
            seen.add(dd)
            figs.append(f)
        vals = [pred(f) for f in figs]
        if sum(vals) != 3:
            continue
        odds = set()
        for _, _, p2 in ODDRULES:
            try:
                v2 = [p2(f) for f in figs]
            except Exception:
                continue
            if sum(v2) == 3:
                odds.add(v2.index(False))
        if len(odds) != 1:
            continue
        bad = vals.index(False)
        break
    else:
        return None
    letters = ["A", "B", "C", "D"]
    stem = "Four figures: " + ", ".join(letters[i] + " " + fdesc(figs[i]) for i in range(4)) + ". Three of them follow the same hidden rule, and one does not. Which figure does NOT belong?"
    expl = rule_txt + " Check each figure: " + " ".join(letters[i] + " " + fdesc(figs[i]) + (" follows the rule." if vals[i] else " breaks the rule.") for i in range(4)) + " So Figure " + letters[bad] + " is the odd one out."
    texts = ["Figure A", "Figure B", "Figure C", "Figure D"]
    return stem, texts, bad, expl, rule_id
n = 0
ri = 0
for qid in ODIDS:
    old = byid[qid]
    lvl = old["level"]
    for _ in range(20):
        rid, rtxt, pred = ODDRULES[ri % len(ODDRULES)]
        ri += 1
        if rid == "ODD-F" and lvl == "Explore":
            continue
        r = gen_odd2(rid, rtxt, pred, lvl)
        if r:
            break
    else:
        raise RuntimeError("odd regen failed " + qid)
    stem, texts, bad, expl, rid2 = r
    lv2 = "Think" if rid2 == "ODD-F" else lvl
    refit(qid, "pattern_abstract", "Pattern and Abstract", "5.3", "figure_odd_one_rule", lv2, "medium" if lv2 == "Think" else "easy", stem, texts, bad, expl, "Find the abstract SPONCS rule shared by three figures.", ["odd_one_out", rid2])
    n += 1
print("odd refit:", n)
for q in NEW:
    for o in q["options"]:
        if not isinstance(o["text"], str):
            o["text"] = str(o["text"])
print("coerced int options to str")

WNAMES = ["triangle", "square", "circle", "star", "diamond", "oval", "pentagon", "hexagon"]
seqn = [309]
extra = []
def nid2():
    seqn[0] += 1
    return "BA_P3_HA_%04d" % seqn[0]
def add2(q):
    extra.append(q)
def mk2(domain, topic, skill, arch, level, diff, q, texts, ans, expl, reason, tags):
    texts = [str(x) for x in texts]
    assert len(texts) == 4 and len(set(texts)) == 4
    opts, aid = shuffle_opts(texts, ans)
    return {"id": nid2(), "domain": domain, "topic": topic, "skill": skill, "archetype": arch, "level": level, "difficulty": diff, "question_type": "multiple_choice", "question": q, "options": opts, "answer": aid, "explanation": expl, "reasoning": reason, "tags": tags, "visual_required": False, "visual_spec": None, "image_path": None, "is_active": False, "qa_status": "validated_ha_20260921", "provenance": {"basis": "HA purge regen round2 2026-09-21", "regenerated": True}}
def gen_weight(heavy_ask, level):
    for _ in range(2000):
        shapes = rng.sample(WNAMES, 3)
        ws = rng.sample(range(2, 13) if level == "Think" else range(5, 20), 3)
        if len(set(ws)) < 3:
            continue
        w = dict(zip(shapes, ws))
        pairs = [(shapes[0], shapes[1]), (shapes[1], shapes[2]), (shapes[0], shapes[2])]
        rng.shuffle(pairs)
        stem = ". ".join("A " + a + " and a " + b + " together weigh " + str(w[a] + w[b]) for a, b in pairs) + ". "
        if heavy_ask:
            top = max(w, key=lambda k: w[k])
            stem += "Which shape is the heaviest?"
            texts = shapes + ["All weigh the same"]
            expl = "Add all three pair-weights: each shape is counted twice, so one of each weighs " + str(sum(ws)) + ". Then " + ", ".join(s + " = " + str(w[s]) for s in shapes) + ". The heaviest is the " + top + "."
            return mk2("numerical_reasoning", "Numerical Thinking", "1.3", "weight_system", level, "medium", stem, texts, shapes.index(top), expl, "Solve a 3-variable balance system by summing pairs.", ["weight_system", "balance"])
        ask = rng.choice(shapes)
        correct = w[ask]
        cands = [correct, correct + 1, correct - 1, correct + 2]
        others = [x for s2 in shapes if s2 != ask for x in [w[s2]]]
        cands[3] = others[0] if others[0] != correct else correct + 3
        if len(set(cands)) < 4 or min(cands) <= 0:
            continue
        stem += "How much does one " + ask + " weigh?"
        expl = "Add all three pair-weights: each shape is counted twice, so one of each weighs " + str(sum(ws)) + ". The other two shapes weigh " + str(sum(ws) - correct) + ", so one " + ask + " weighs " + str(sum(ws)) + " - " + str(sum(ws) - correct) + " = " + str(correct) + "."
        return mk2("numerical_reasoning", "Numerical Thinking", "1.3", "weight_system", level, "medium", stem, [str(c) for c in cands], 0, expl, "Solve a 3-variable balance system by summing pairs.", ["weight_system", "balance"])
    return None
n = 0
while n < 42:
    lvl = "Challenge" if n >= 30 else "Think"
    q = gen_weight(n % 2 == 0, lvl)
    if q:
        add2(q)
        n += 1
print("weight new:", n)
SENT_T = [
    ("box", "If a card belongs in {B}, then it has a star.", "Card {N} has no star.", "Card {N} does not belong in {B}", ["Card {N} belongs in {B}", "Card {N} has a star", "{B} throws away all its stars"]),
    ("mult", "If a number is a multiple of {M}, then it is even.", "{X} is not even.", "{X} is not a multiple of {M}", ["{X} is a multiple of {M}", "{X} is even", "{X} is half of {M}"]),
    ("ends", "If a number ends in 0, then it is a multiple of 5.", "{X} is not a multiple of 5.", "{X} does not end in 0", ["{X} ends in 0", "{X} is a multiple of 5", "{X} ends in 5"]),
]
def gen_sentence(kind, level):
    if kind == "contra":
        t = rng.choice(SENT_T)
        name, rule, given, correct, distract = t
        if name == "box":
            B = rng.choice(["Box A", "Box B", "the red tray", "the blue box"])
            N = rng.randint(5, 20)
            kw = {"B": B, "N": N}
        elif name == "mult":
            M = rng.choice([4, 6, 8, 10])
            X = rng.choice([x for x in [21, 27, 33, 35, 37, 41, 43, 45] if x % 2 == 1])
            kw = {"M": M, "X": X}
        else:
            X = rng.choice([37, 41, 53, 68, 74, 86])
            kw = {"X": X}
        stem = "Rule: " + rule.format(**kw) + " Given: " + given.format(**kw) + " What MUST be true?"
        texts = [correct.format(**kw)] + [dd.format(**kw) for dd in distract]
        expl = "Deny the result, deny the cause. " + given.format(**kw) + " So " + correct.format(**kw).lower() + "."
        return mk2("logical_reasoning", "Logical Thinking", "2.3", "conditional_contrapositive", level, "medium", stem, texts, 0, expl, "Use the contrapositive.", ["logic", "contrapositive"])
    a = rng.choice(BOYN + GIRLN)
    acts = rng.choice([("saves $10", "buys a model kit", "builds it on Sunday"), ("finishes homework early", "reads a book", "learns new words"), ("hears the bell", "lines up", "walks to class quietly")])
    if kind == "chainMT":
        stem = "If " + a + " " + acts[0] + ", " + a + " " + acts[1] + ". If " + a + " " + acts[1] + ", " + a + " " + acts[2] + ". Today " + a + " does NOT " + acts[2] + ". What MUST be true?"
        correct = a + " did NOT " + acts[0]
        texts = [correct, a + " " + acts[0], a + " " + acts[1], a + " " + acts[2]]
        expl = "Chain backwards: no final step means the middle step did not happen, so the first step did not happen. " + correct + "."
        return mk2("logical_reasoning", "Logical Thinking", "2.3", "conditional_contrapositive", "Challenge", "hard", stem, texts, 0, expl, "Chain two contrapositives.", ["logic", "chained_contrapositive"])
    stem = "If " + a + " " + acts[0] + ", " + a + " " + acts[1] + ". If " + a + " " + acts[1] + ", " + a + " " + acts[2] + ". Today " + a + " " + acts[0] + ". What MUST be true?"
    correct = a + " " + acts[2]
    texts = [correct, a + " does NOT " + acts[0], a + " does NOT " + acts[1], a + " does NOT " + acts[2]]
    expl = "Chain forwards: the first step happened, so the middle step happened, so the final step happened. " + correct + "."
    return mk2("logical_reasoning", "Logical Thinking", "2.3", "conditional_contrapositive", "Challenge", "hard", stem, texts, 0, expl, "Chain two rules forwards.", ["logic", "chained_affirm"])
n = 0
kinds = ["contra"] * 9 + ["chainMT"] * 3 + ["chainMP"] * 3
for kd in kinds:
    lvl = "Think" if kd == "contra" else "Challenge"
    q = gen_sentence(kd, lvl)
    add2(q)
    n += 1
print("sentence new:", n)
json.dump(NEW, open("revamp/bank/ha_new_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(extra, open("revamp/bank/ha_extra_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE updated ha_new (refits: %d) + ha_extra (%d)" % (len(fixed), len(extra)))

