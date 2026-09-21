import json, re, random, collections
rng = random.Random(20260921)
BANK = "revamp/bank/brainactive_p3_question_bank_production.json"
AUD = "revamp/bank/ha_audit_20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
qs = d["questions"]
byid = {q["id"]: q for q in qs}
aud = json.load(open(AUD, encoding="utf-8"))
kept = [byid[k] for k, x in aud.items() if x["verdict"] == "keep"]
dels = [k for k, x in aud.items() if x["verdict"] == "delete"]
fps = set((q["question"].strip().lower(), q["answer"]) for q in kept)
newqs = []
seqn = [0]
def nid():
    seqn[0] += 1
    return "BA_P3_HA_%04d" % seqn[0]
def shuffle_opts(texts, ans):
    order = list(range(4))
    rng.shuffle(order)
    opts = [{"id": "ABCD"[i], "text": texts[j]} for i, j in enumerate(order)]
    return opts, "ABCD"[order.index(ans)]
def mkitem(domain, topic, skill, arch, level, diff, q, texts, ans, expl, reason, tags):
    assert len(texts) == 4 and len(set(texts)) == 4 and texts[ans] not in texts[:ans] + texts[ans+1:]
    opts, aid = shuffle_opts(texts, ans)
    return {"id": nid(), "domain": domain, "topic": topic, "skill": skill, "archetype": arch, "level": level, "difficulty": diff, "question_type": "multiple_choice", "question": q, "options": opts, "answer": aid, "explanation": expl, "reasoning": reason, "tags": tags, "visual_required": False, "visual_spec": None, "image_path": None, "is_active": False, "qa_status": "validated_ha_20260921", "provenance": {"basis": "HA purge regen 2026-09-21, GEP GA and CogAT archetypes", "regenerated": True}}
def add(q):
    fp = (q["question"].strip().lower(), q["answer"])
    if fp in fps:
        return False
    fps.add(fp)
    newqs.append(q)
    return True
BOYN = ["Ali", "Ben", "Cai", "Dan", "Eli", "Finn", "Gus", "Hari", "Ivan", "Jay"]
GIRLN = ["Amy", "Bella", "Cindy", "Diya", "Eva", "Fiona", "Gina", "Hana", "Iris", "Jia"]

SHAPES = [("triangle", 3), ("square", 4), ("pentagon", 5), ("hexagon", 6)]
SIZES = ["small", "large"]
COLOURS = ["red", "blue", "green"]
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
ODDRULES = [
    ("ODD-A", "A figure has a dot exactly when it has an even number of sides.", lambda f: f["dot"] == (sides(f) % 2 == 0)),
    ("ODD-B", "A figure is small exactly when it is a triangle.", lambda f: (f["size"] == "small") == (f["shape"] == "triangle")),
    ("ODD-C", "A figure is blue exactly when it has more than 4 sides.", lambda f: (f["colour"] == "blue") == (sides(f) > 4)),
    ("ODD-D", "A figure has a dot exactly when it is large.", lambda f: f["dot"] == (f["size"] == "large")),
    ("ODD-E", "A figure is green exactly when it has 3 or 6 sides.", lambda f: (f["colour"] == "green") == (sides(f) in (3, 6))),
    ("ODD-F", "A figure has a dot exactly when it is large AND has an even number of sides.", lambda f: f["dot"] == (f["size"] == "large" and sides(f) % 2 == 0)),
]
def gen_odd(rule_id, rule_txt, pred, level):
    for _ in range(200):
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
        if sum(vals) == 3:
            break
    else:
        return None
    bad = vals.index(False)
    letters = ["A", "B", "C", "D"]
    stem = "Four figures: " + ", ".join(letters[i] + " " + fdesc(figs[i]) for i in range(4)) + ". Three of them follow the same hidden rule, and one does not. Which figure does NOT belong?"
    expl = rule_txt + " Check each figure: " + " ".join(letters[i] + " " + fdesc(figs[i]) + (" follows the rule." if vals[i] else " breaks the rule.") for i in range(4)) + " So Figure " + letters[bad] + " is the odd one out."
    texts = ["Figure A", "Figure B", "Figure C", "Figure D"]
    return mkitem("pattern_abstract", "Pattern and Abstract", "5.3", "figure_odd_one_rule", level, "medium" if level == "Think" else "easy", stem, texts, bad, expl, "Find the abstract SPONCS rule shared by three figures.", ["odd_one_out", rule_id])
made = {"odd": 0}
ri = 0
while made["odd"] < 53:
    rid, rtxt, pred = ODDRULES[ri % len(ODDRULES)]
    lvl = "Explore" if made["odd"] < 20 and rid != "ODD-F" else "Think"
    if rid == "ODD-F":
        lvl = "Think"
    q = gen_odd(rid, rtxt, pred, lvl)
    ri += 1
    if q and add(q):
        made["odd"] += 1
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
def t_colour(f):
    g = dict(f)
    others = [c for c in COLOURS if c != f["colour"]]
    g["colour"] = rng.choice(others)
    return g
def t_size(f):
    g = dict(f)
    g["size"] = "large" if f["size"] == "small" else "small"
    return g
def t_dot(f):
    g = dict(f)
    g["dot"] = not f["dot"]
    return g
TNAMES = {id(t_shape_up): "gains one side", id(t_shape_dn): "loses one side", id(t_colour): "changes colour", id(t_size): "changes size", id(t_dot): "gains or loses its dot"}
def gen_analogy(nt, level):
    for _ in range(300):
        ts = rng.sample([t_shape_up, t_shape_dn, t_colour, t_size, t_dot], nt)
        f1 = randfig()
        if t_shape_up in ts and f1["shape"] == "hexagon":
            continue
        if t_shape_dn in ts and f1["shape"] == "triangle":
            continue
        f2 = f1
        ok = True
        for t in ts:
            f2 = t(f2)
            if f2 is None:
                ok = False
                break
        if not ok:
            continue
        f3 = randfig()
        if t_shape_up in ts and f3["shape"] == "hexagon":
            continue
        if t_shape_dn in ts and f3["shape"] == "triangle":
            continue
        f4 = f3
        for t in ts:
            f4 = t(f4)
        if f4 is None:
            continue
        cands = [fdesc(f4)]
        partials = []
        for t in ts:
            g = f3
            g = t(g)
            if g is not None:
                partials.append(fdesc(g))
        partials.append(fdesc(f3))
        for p in partials:
            if p not in cands:
                cands.append(p)
        if len(cands) < 4:
            extra = fdesc(randfig())
            if extra not in cands:
                cands.append(extra)
        if len(cands) < 4 or fdesc(f4) == fdesc(f3):
            continue
        cands = cands[:4]
        break
    else:
        return None
    names = " and ".join(sorted(set(TNAMES[id(t)] for t in ts)))
    stem = "A " + fdesc(f1) + " changes into a " + fdesc(f2) + ". Using the same change, a " + fdesc(f3) + " changes into ___?"
    expl = "Work out the hidden change from the first pair: it " + names + ". Apply both to the new figure: a " + fdesc(f3) + " becomes a " + fdesc(f4) + "."
    return mkitem("pattern_abstract", "Pattern and Abstract", "5.4", "figure_analogy", level, "hard" if level == "Challenge" else "medium", stem, cands, 0, expl, "Infer two simultaneous transformations and apply both.", ["figure_analogy", "compound_rule"])
made["ana"] = 0
while made["ana"] < 50:
    nt = 3 if made["ana"] >= 35 else 2
    lvl = "Challenge" if nt == 3 else "Think"
    q = gen_analogy(nt, lvl)
    if q and add(q):
        made["ana"] += 1

def gen_order(n, form, level):
    names = rng.sample(BOYN + GIRLN, n)
    order = names[:]
    rng.shuffle(order)
    clues = []
    for i in range(n - 1):
        clues.append(order[i] + " beats " + order[i + 1])
    rng.shuffle(clues)
    head = "Five runners race. " if n == 5 else "Four runners race. "
    stem0 = head + ". ".join(clues) + ". "
    if form == "full":
        stem = stem0 + "Order them from fastest to slowest."
        correct = ", ".join(order)
        d1 = list(order)
        d1[0], d1[1] = d1[1], d1[0]
        d2 = list(order)
        d2[-2], d2[-1] = d2[-1], d2[-2]
        d3 = list(reversed(order))
        texts = [correct, ", ".join(d1), ", ".join(d2), ", ".join(d3)]
        expl = "Link the clues into one chain: " + " beats ".join(order) + ". So the order from fastest to slowest is " + correct + "."
        return mkitem("logical_reasoning", "Logical Thinking", "2.1", "merge_partial_orders", level, "hard" if n == 5 else "medium", stem, texts, 0, expl, "Merge separate clues into one complete order.", ["ordering", "merge_orders"])
    if form == "position":
        pos = rng.choice([1, 2] if n == 4 else [1, 2, 3])
        words = ["first", "second", "third", "fourth", "fifth"]
        stem = stem0 + "Who finishes " + words[pos] + "?"
        texts = [order[pos]] + [x for x in order if x != order[pos]][:3]
        expl = "Link the clues into one chain: " + " beats ".join(order) + ". The " + words[pos] + " finisher is " + order[pos] + "."
        return mkitem("logical_reasoning", "Logical Thinking", "2.1", "merge_partial_orders", level, "medium", stem, texts, 0, expl, "Merge separate clues, then read off one position.", ["ordering", "merge_orders"])
    a, b = order[0], order[-1]
    mid = order[1]
    stem = stem0 + "Which of these MUST be true?"
    texts = [a + " beats " + b, b + " beats " + a, b + " beats " + mid, mid + " beats " + a]
    expl = "Link the clues into one chain: " + " beats ".join(order) + ". Since " + a + " is ahead of everyone, " + a + " beats " + b + " must be true. The other three reverse the real order."
    return mkitem("logical_reasoning", "Logical Thinking", "2.1", "merge_partial_orders", level, "medium", stem, texts, 0, expl, "Merge clues, then test each claim.", ["ordering", "must_be_true"])
made["ord"] = 0
oi = 0
while made["ord"] < 48:
    n = 5 if made["ord"] >= 30 else 4
    form = ["full", "position", "must"][oi % 3]
    lvl = "Challenge" if n == 5 else "Think"
    oi += 1
    q = gen_order(n, form, lvl)
    if q and add(q):
        made["ord"] += 1
THINGS = ["stickers", "marbles", "cards", "shells", "badges", "coins", "stamps", "buttons"]
def gen_transfer_double():
    for _ in range(200):
        a, b = rng.sample(BOYN + GIRLN, 2)
        t = rng.choice(THINGS)
        A = rng.randint(20, 50)
        B = rng.randint(10, 40)
        if A == B:
            continue
        X = rng.randint(3, 9)
        Y = rng.randint(1, X - 1)
        if X > A:
            continue
        A1 = A - X + Y
        B1 = B + X - Y
        if A1 == B1 or A1 < 0 or B1 < 0:
            continue
        lead = a if A1 > B1 else b
        marg = abs(A1 - B1)
        forget = abs((A - X) - (B + X))
        wrong_lead = b if A1 > B1 else a
        cands = [lead + " by " + str(marg), wrong_lead + " by " + str(marg), lead + " by " + str(forget), "Tied"]
        if len(set(cands)) < 4 or forget == marg or forget == 0:
            continue
        break
    else:
        return None
    stem = a + " has " + str(A) + " " + t + " and " + b + " has " + str(B) + " " + t + ". " + a + " gives " + b + " " + str(X) + " " + t + ", then " + b + " gives " + a + " " + str(Y) + " " + t + ". Now who has more " + t + ", and by how many?"
    expl = "After the first gift: " + a + " has " + str(A - X) + ", " + b + " has " + str(B + X) + ". After the second gift: " + a + " has " + str(A1) + ", " + b + " has " + str(B1) + ". So " + lead + " has more by " + str(marg) + "."
    return mkitem("problem_solving", "Problem Solving", "6.3", "before_after_transfer", "Think", "medium", stem, cands, 0, expl, "Track two transfers step by step.", ["before_after", "two_transfers"])
def gen_transfer_back():
    for _ in range(200):
        a, b = rng.sample(BOYN + GIRLN, 2)
        t = rng.choice(THINGS)
        M = rng.randint(15, 40)
        X = rng.randint(3, 12)
        A = M + X
        B = M - X
        if B <= 0:
            continue
        cands = [str(A), str(M), str(B), str(A + X)]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    stem = "After " + a + " gives " + b + " " + str(X) + " " + t + ", both of them have " + str(M) + " " + t + ". How many " + t + " did " + a + " have at first?"
    expl = a + " gave some away and still has " + str(M) + ", so at first " + a + " had " + str(M) + " + " + str(X) + " = " + str(A) + ". Check: " + b + " received " + str(X) + " to reach " + str(M) + ", so " + b + " started with " + str(B) + "."
    return mkitem("problem_solving", "Problem Solving", "6.3", "before_after_transfer", "Challenge", "hard", stem, cands, 0, expl, "Work backwards from the equal end state.", ["before_after", "hidden_total"])
made["tr"] = 0
while made["tr"] < 27:
    q = gen_transfer_back() if made["tr"] >= 18 else gen_transfer_double()
    if q and add(q):
        made["tr"] += 1

def gen_fence_straight():
    for _ in range(200):
        n = rng.randint(5, 12)
        g = rng.randint(2, 6)
        t = rng.choice(["fence posts", "trees", "lamps", "flag poles"])
        ans = (n - 1) * g
        trap = n * g
        cands = [str(ans) + " m", str(trap) + " m", str((n - 2) * g) + " m", str((n + 1) * g) + " m"]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    stem = str(n) + " " + t + " are planted in a straight line, " + str(g) + " m apart. How long is the line from the first " + t.split()[-1] + " to the last?"
    expl = str(n) + " posts make " + str(n - 1) + " gaps of " + str(g) + " m. Total length is " + str(n - 1) + " x " + str(g) + " = " + str(ans) + " m. Counting posts instead of gaps gives the trap answer " + str(trap) + " m."
    return mkitem("problem_solving", "Problem Solving", "6.4", "draw_diagram_gaps", "Think", "medium", stem, cands, 0, expl, "Count gaps, not posts: gaps = posts - 1.", ["fencepost", "straight_line"])
def gen_fence_circle():
    for _ in range(200):
        n = rng.randint(6, 12)
        g = rng.randint(2, 8)
        place = rng.choice([("bushes", "pond"), ("trees", "running track"), ("flower pots", "roundabout"), ("lamps", "circular park")])
        ans = n * g
        cands = [str(ans) + " m", str((n - 1) * g) + " m", str((n + 1) * g) + " m", str(n * (g + 1)) + " m"]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    stem = str(n) + " " + place[0] + " are spaced equally around a circular " + place[1] + ", with " + str(g) + " m between each adjacent pair. What is the total distance around the " + place[1] + "?"
    expl = "Around a circle there is no first or last post, so gaps = posts = " + str(n) + ". Total is " + str(n) + " x " + str(g) + " = " + str(ans) + " m."
    return mkitem("problem_solving", "Problem Solving", "6.4", "draw_diagram_gaps", "Think", "medium", stem, cands, 0, expl, "Around a circle, gaps = posts.", ["fencepost", "circle"])
def gen_fence_both():
    for _ in range(200):
        n = rng.randint(5, 10)
        g = rng.randint(2, 5)
        ans = (n - 1) * g
        cands = [str(ans) + " m", str(n * g) + " m", str(2 * ans) + " m", str((n - 1) * (g + 1)) + " m"]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    stem = str(n) + " trees are planted on EACH side of a straight path, " + str(g) + " m apart. How long is the path?"
    expl = "Each side has " + str(n) + " trees, so each side has " + str(n - 1) + " gaps of " + str(g) + " m. Path length is " + str(n - 1) + " x " + str(g) + " = " + str(ans) + " m on either side."
    return mkitem("problem_solving", "Problem Solving", "6.4", "draw_diagram_gaps", "Challenge", "hard", stem, cands, 0, expl, "Each side separately: gaps = trees - 1.", ["fencepost", "both_sides"])
made["fe"] = 0
while made["fe"] < 26:
    k = made["fe"]
    q = gen_fence_both() if k >= 18 else (gen_fence_circle() if k % 2 else gen_fence_straight())
    if q and add(q):
        made["fe"] += 1
def fits_rules(x1, y1):
    outs = {}
    for a in range(2, 5):
        for b in range(-9, 10):
            if b == 0:
                continue
            if a * x1 + b == y1:
                outs[("dual", a, b)] = True
    for n in range(1, 30):
        if x1 + n == y1:
            outs[("add", n)] = True
    for a in range(2, 10):
        if a * x1 == y1:
            outs[("mul", a)] = True
    if x1 * x1 == y1:
        outs[("sq",)] = True
    return outs
def gen_dual():
    for _ in range(500):
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
        fr = fits_rules(x1, y1)
        if ("dual", a, b) not in fr:
            continue
        bad = set()
        for r in fr:
            if r == ("dual", a, b):
                continue
            if r[0] == "dual":
                bad.add(r[1] * x2 + r[2])
            elif r[0] == "add":
                bad.add(x2 + r[1])
            elif r[0] == "mul":
                bad.add(r[1] * x2)
            elif r[0] == "sq":
                bad.add(x2 * x2)
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
        return None
    op = "+" if b > 0 else "-"
    stem = str(x1) + " is to " + str(y1) + " as " + str(x2) + " is to ___?"
    expl = "Find the hidden two-step rule: x " + str(a) + " then " + op + " " + str(abs(b)) + ". Check: " + str(x1) + " x " + str(a) + " " + op + " " + str(abs(b)) + " = " + str(y1) + ". Apply it: " + str(x2) + " x " + str(a) + " " + op + " " + str(abs(b)) + " = " + str(y2) + "."
    return mkitem("numerical_reasoning", "Numerical Thinking", "1.2", "compound_rule_analogy", "Think", "medium", stem, [str(o) for o in opts], 0, expl, "Discover a two-step rule and apply it.", ["number_analogy", "dual_rule"])
made["du"] = 0
while made["du"] < 24:
    q = gen_dual()
    if q and add(q):
        made["du"] += 1

def L(v):
    return chr(64 + v)
def gen_letter(gaps, level):
    for _ in range(300):
        start = rng.randint(6, 14)
        vals = [start]
        for g in gaps:
            vals.append(vals[-1] + g)
        if min(vals) < 1 or max(vals) > 26:
            continue
        letters = [L(v) for v in vals]
        if len(set(letters)) < len(letters):
            continue
        nxt = vals[-1] + gaps[len(vals) - 1] if len(vals) - 1 < len(gaps) else vals[-1] + gaps[(len(vals) - 1) % len(gaps)]
        if nxt < 1 or nxt > 26:
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
        d = (vals + [nxt])[i] - (vals + [nxt])[i - 1]
        gp.append(("+" if d >= 0 else "") + str(d))
    expl = "Look at the jumps between letters: " + ", ".join(gp) + ". The jumps follow a repeating pattern, so the next jump gives " + ans + ". Full pattern: " + seq + "."
    return mkitem("verbal_reasoning", "Verbal Reasoning", "3.6", "letter_patterns", level, "hard" if level == "Challenge" else "medium", stem, opts, 0, expl, "Discover the hidden jump pattern.", ["letter_series", "hidden_rule"])
made["le"] = 0
GAPSET = [[2, 3], [3, -1], [4, -2], [3, 1], [2, 1], [3, 2], [2, 3, 4], [1, 2, 3], [3, -1, 4, -1], [2, -1, 3, -1]]
while made["le"] < 20:
    gaps = GAPSET[made["le"] % len(GAPSET)]
    lvl = "Challenge" if len(gaps) > 2 else "Think"
    q = gen_letter(gaps, lvl)
    if q and add(q):
        made["le"] += 1
def gen_chain4():
    for _ in range(300):
        names = rng.sample(BOYN + GIRLN, 4)
        t = rng.choice(THINGS)
        base = rng.randint(12, 30)
        diffs = [rng.randint(2, 8) * rng.choice([1, -1]) for _ in range(3)]
        if all(dd > 0 for dd in diffs) or all(dd < 0 for dd in diffs):
            pass
        counts = [base]
        for dd in diffs:
            counts.append(counts[-1] + dd)
        if min(counts) <= 0:
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
            top = names[counts.index(max(counts))]
            stem = ". ".join(rels) + ". " + names[anch] + " has " + str(counts[anch]) + " " + t + ". Who has the most " + t + "?"
            expl = "Work along the chain from " + names[anch] + " (" + str(counts[anch]) + "): " + "; ".join(names[i] + " = " + str(counts[i]) for i in range(4)) + ". The most is " + top + "."
            q = mkitem("numerical_reasoning", "Numerical Thinking", "1.4", "chained_comparison", "Think", "medium", stem, names, names.index(top), expl, "Chain three comparisons from the known count.", ["chain_comparison", "four_person"])
        else:
            target = rng.choice([n for n in names if n != names[anch]])
            stem = ". ".join(rels) + ". " + names[anch] + " has " + str(counts[anch]) + " " + t + ". How many " + t + " does " + target + " have?"
            tv = given[target]
            cands = [str(tv), str(tv + diffs[0]), str(tv - diffs[0]), str(tv + 1)]
            if len(set(cands)) < 4:
                continue
            expl = "Work along the chain from " + names[anch] + " (" + str(counts[anch]) + "): " + "; ".join(names[i] + " = " + str(counts[i]) for i in range(4)) + ". So " + target + " has " + str(tv) + "."
            q = mkitem("numerical_reasoning", "Numerical Thinking", "1.4", "chained_comparison", "Think", "medium", stem, cands, 0, expl, "Chain three comparisons from the known count.", ["chain_comparison", "four_person"])
        break
    else:
        return None
    return q
made["ch"] = 0
while made["ch"] < 17:
    q = gen_chain4()
    if q and add(q):
        made["ch"] += 1
MRULES = [("x3-2", lambda n: 3 * n - 2, "times 3, minus 2"), ("x2+5", lambda n: 2 * n + 5, "times 2, plus 5"), ("x4-3", lambda n: 4 * n - 3, "times 4, minus 3"), ("x3+4", lambda n: 3 * n + 4, "times 3, plus 4"), ("sq-1", lambda n: n * n - n, "multiply by one less")]
def gen_machine():
    for _ in range(300):
        rid, fn, words = rng.choice(MRULES)
        xs = [1, 2, 3]
        ys = [fn(x) for x in xs]
        if min(ys) <= 0 or len(set(ys)) < 3:
            continue
        inp = rng.randint(6, 12)
        ans = fn(inp)
        near = [ans + 1, ans - 1, ans + 2, ans - 2, ans + 3, fn(inp) + 1]
        opts = [ans]
        for c in near:
            if len(opts) >= 4:
                break
            if c > 0 and c not in opts and c not in ys:
                opts.append(c)
        if len(opts) < 4:
            continue
        break
    else:
        return None
    dev = rng.choice(["number machine", "transformer", "puzzle box", "calculation device"])
    stem = "A " + dev + " changes numbers with a secret rule: " + ", ".join(str(x) + " becomes " + str(y) for x, y in zip(xs, ys)) + ". If the input is " + str(inp) + ", what number comes out?"
    expl = "Find the secret rule: " + words + ". Check: " + "; ".join(str(x) + " -> " + str(fn(x)) for x in xs) + ". Apply it: " + str(inp) + " -> " + str(ans) + "."
    return mkitem("problem_solving", "Problem Solving", "6.6", "pattern_application", "Think", "medium", stem, [str(o) for o in opts], 0, expl, "Discover the secret two-step rule.", ["function_machine", rid])
made["ma"] = 0
while made["ma"] < 11:
    q = gen_machine()
    if q and add(q):
        made["ma"] += 1

def gen_contra_simple():
    for _ in range(200):
        kind = rng.choice(["box", "mult5", "ends0", "bird"])
        if kind == "box":
            box = rng.choice(["Box A", "Box B", "the red tray", "the blue box"])
            n = rng.randint(5, 20)
            stem = "Rule: If a card belongs in " + box + ", then it has a star. Given: Card " + str(n) + " has no star. What MUST be true?"
            correct = "Card " + str(n) + " does not belong in " + box
            texts = [correct, "Card " + str(n) + " belongs in " + box, "Card " + str(n) + " has a star", box + " has no cards with stars"]
            expl = "The rule says belonging needs a star. Card " + str(n) + " has no star, so it cannot belong in " + box + "."
        elif kind == "mult5":
            x = rng.choice([37, 41, 53, 68, 74, 86])
            stem = "Rule: If a number ends in 0, then it is a multiple of 5. Given: " + str(x) + " is not a multiple of 5. What MUST be true?"
            correct = str(x) + " does not end in 0"
            texts = [correct, str(x) + " ends in 0", str(x) + " is a multiple of 5", str(x) + " ends in 5"]
            expl = "Ending in 0 forces a multiple of 5. Since " + str(x) + " is not a multiple of 5, it cannot end in 0."
        elif kind == "ends0":
            x = rng.choice([43, 57, 61, 79, 83, 97])
            stem = "Rule: If a number is a multiple of 4, then it is even. Given: " + str(x) + " is not even. What MUST be true?"
            correct = str(x) + " is not a multiple of 4"
            texts = [correct, str(x) + " is a multiple of 4", str(x) + " is even", "All odd numbers end in " + str(x % 10)]
            expl = "Multiples of 4 are always even. Since " + str(x) + " is not even, it cannot be a multiple of 4."
        else:
            stem = "Rule: If an animal is a bird, then it has feathers. Given: A dolphin has no feathers. What MUST be true?"
            correct = "A dolphin is not a bird"
            texts = [correct, "A dolphin is a bird", "A dolphin has feathers", "No sea animal is a bird"]
            expl = "Birds must have feathers. A dolphin has none, so a dolphin cannot be a bird."
        if len(set(texts)) < 4:
            continue
        break
    else:
        return None
    return mkitem("logical_reasoning", "Logical Thinking", "2.3", "conditional_contrapositive", "Think", "medium", stem, texts, 0, expl, "Use the contrapositive: deny the result, deny the cause.", ["logic", "contrapositive"])
def gen_contra_chain():
    a, b = rng.sample(BOYN + GIRLN, 2)
    t = rng.choice([("saves $10", "buys a model kit", "builds it on Sunday"), ("finishes homework early", "reads a book", "learns new words"), ("hears the bell", "lines up", "walks to class quietly")])
    stem = "If " + a + " " + t[0] + ", " + a + " " + t[1] + ". If " + a + " " + t[1] + ", " + a + " " + t[2] + ". Today " + a + " does NOT " + t[2] + ". What MUST be true?"
    correct = a + " did NOT " + t[0]
    texts = [correct, a + " " + t[0], a + " " + t[1], a + " " + t[2]]
    expl = "Chain the rules backwards: no final step means the middle step did not happen, which means the first step did not happen either. So " + a + " did NOT " + t[0] + "."
    return mkitem("logical_reasoning", "Logical Thinking", "2.3", "conditional_contrapositive", "Challenge", "hard", stem, texts, 0, expl, "Chain two contrapositives backwards.", ["logic", "chained_contrapositive"])
made["co"] = 0
while made["co"] < 10:
    q = gen_contra_chain() if made["co"] >= 6 else gen_contra_simple()
    if q and add(q):
        made["co"] += 1
DIRS = ["UP", "RIGHT", "DOWN", "LEFT"]
def turn(d, steps):
    return DIRS[(DIRS.index(d) + steps) % 4]
def mirrorV(d):
    return {"LEFT": "RIGHT", "RIGHT": "LEFT"}.get(d, d)
def gen_rot():
    for _ in range(200):
        d = rng.choice(DIRS)
        nmoves = rng.choice([2, 2, 3])
        moves = []
        dd = d
        for _ in range(nmoves):
            m = rng.choice(["cw90", "ccw90", "half", "mirror"])
            moves.append(m)
            if m == "cw90":
                dd = turn(dd, 1)
            elif m == "ccw90":
                dd = turn(dd, -1)
            elif m == "half":
                dd = turn(dd, 2)
            else:
                dd = mirrorV(dd)
        if dd == d:
            continue
        words = {"cw90": "turns 90 degrees clockwise", "ccw90": "turns 90 degrees anticlockwise", "half": "turns 180 degrees", "mirror": "is flipped left-to-right in a vertical mirror"}
        stem = "An arrow points " + d + ". It " + ", then it ".join(words[m] for m in moves) + ". Which way does it point now?"
        first = moves[0]
        d_first = turn(d, 1) if first == "cw90" else (turn(d, -1) if first == "ccw90" else (turn(d, 2) if first == "half" else mirrorV(d)))
        last_flip = {"cw90": "ccw90", "ccw90": "cw90", "half": "half", "mirror": "mirror"}[moves[-1]]
        dw = d
        for m in moves[:-1] + [last_flip]:
            dw = turn(dw, 1) if m == "cw90" else (turn(dw, -1) if m == "ccw90" else (turn(dw, 2) if m == "half" else mirrorV(dw)))
        cands = [dd, d_first, dw, turn(dd, 1)]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    expl = "Track it step by step starting from " + d + ": " + " -> ".join([d] + [cands[0]] ) + ". Applying each move in order lands on " + dd + "."
    expl = "Track it step by step starting from " + d + ". Applying each of the " + str(nmoves) + " moves in order lands on " + dd + "."
    return mkitem("visual_spatial", "Visual and Spatial", "4.1", "two_step_rotation", "Think", "medium", stem, cands, 0, expl, "Apply each turn or mirror in order.", ["rotation", "multi_step"])
made["ro"] = 0
while made["ro"] < 10:
    q = gen_rot()
    if q and add(q):
        made["ro"] += 1

def gen_seq_inter():
    s = rng.randint(2, 5)
    vals = [s]
    for _ in range(6):
        vals.append(vals[-1] * 2 if len(vals) % 2 == 1 else vals[-1] + 1)
    ans = vals[-1] * 2
    stem = "Find the next number: " + ", ".join(map(str, vals)) + ", ___?"
    cands = [ans, ans + 1, ans - 1, vals[-1] + 1]
    expl = "Alternate two steps: times 2, then plus 1. " + " -> ".join(map(str, vals)) + ": each odd step doubles, each even step adds 1. Next is " + str(vals[-1]) + " x 2 = " + str(ans) + "."
    return mkitem("numerical_reasoning", "Numerical Thinking", "1.1", "interleaved_sequence", "Think", "medium", stem, cands, 0, expl, "Spot two alternating rules.", ["sequence", "interleaved"])
def gen_seq_fib():
    a = rng.randint(1, 4)
    b = rng.randint(a + 1, a + 4)
    vals = [a, b]
    for _ in range(5):
        vals.append(vals[-1] + vals[-2])
    hide = 4
    ans = vals[hide]
    shown = ["___" if i == hide else str(v) for i, v in enumerate(vals)]
    stem = "Each number is the sum of the two before it: " + ", ".join(shown) + ". What is the missing number?"
    cands = [ans, ans + 1, ans - 1, ans + 2]
    expl = "Add neighbours: " + str(vals[hide - 2]) + " + " + str(vals[hide - 1]) + " = " + str(ans) + ". Check forward: " + str(vals[hide - 1]) + " + " + str(ans) + " = " + str(vals[hide + 1]) + "."
    return mkitem("numerical_reasoning", "Numerical Thinking", "1.1", "alternating_rule", "Challenge", "hard", stem, cands, 0, expl, "Use the addition rule to fill the gap.", ["sequence", "fibonacci_gap"])
def gen_seq_alt():
    s = rng.randint(3, 9)
    p, q = rng.choice([(3, -1), (4, -2), (5, -2)])
    vals = [s]
    for i in range(5):
        vals.append(vals[-1] + (p if i % 2 == 0 else q))
    nxt = vals[-1] + (p if 5 % 2 == 0 else q)
    stem = "Find the next number: " + ", ".join(map(str, vals)) + ", ___?"
    cands = [nxt, nxt + 1, nxt - 1, vals[-1] + p]
    expl = "The jumps alternate " + ("+" if p >= 0 else "") + str(p) + " then " + str(q) + ". Last jump was " + str(q) + ", so the next jump is " + ("+" if p >= 0 else "") + str(p) + ": " + str(vals[-1]) + " gives " + str(nxt) + "."
    return mkitem("numerical_reasoning", "Numerical Thinking", "1.1", "interleaved_sequence", "Think", "medium", stem, cands, 0, expl, "Spot the alternating jumps.", ["sequence", "alternating_jumps"])
made["sq"] = 0
si = 0
while made["sq"] < 6:
    q = [gen_seq_inter, gen_seq_fib, gen_seq_alt][si % 3]()
    si += 1
    if q and add(q):
        made["sq"] += 1
def gen_ba():
    for _ in range(200):
        a, b = rng.sample(BOYN + GIRLN, 2)
        t = rng.choice(THINGS)
        M = rng.randint(4, 20)
        G = rng.randint(1, 10)
        if M == 2 * G:
            continue
        A = 20 + M
        B = 20
        A1 = A - G
        B1 = B + G
        marg = abs(A1 - B1)
        lead = a if A1 > B1 else b
        other = b if A1 > B1 else a
        cands = [lead + " by " + str(marg), other + " by " + str(marg), lead + " by " + str(M), "Tied"]
        if len(set(cands)) < 4:
            continue
        break
    else:
        return None
    stem = a + " has " + str(M) + " more " + t + " than " + b + ". " + a + " gives " + b + " " + str(G) + " " + t + ". Now who has more " + t + ", and by how many?"
    expl = "Start: " + a + " leads by " + str(M) + ". The gift moves " + str(G) + " each way, closing the gap by " + str(2 * G) + ". New gap is " + str(marg) + " to " + lead + "."
    return mkitem("problem_solving", "Problem Solving", "6.3", "before_after", "Think", "medium", stem, cands, 0, expl, "One gift closes the gap twice over.", ["before_after", "gap_closes_double"])
made["ba"] = 0
while made["ba"] < 6:
    q = gen_ba()
    if q and add(q):
        made["ba"] += 1
def gen_bw():
    k = rng.randint(2, 3)
    c = rng.randint(4, 12)
    start = rng.randint(4, 12)
    res = k * start + c
    stem = "A number is multiplied by " + str(k) + ", then " + str(c) + " is added, and the result is " + str(res) + ". What was the starting number?"
    cands = [start, start + 1, start - 1, (res + c) // k if (res + c) % k == 0 and (res + c) // k != start else start + 2]
    expl = "Undo backwards: subtract first (" + str(res) + " - " + str(c) + " = " + str(res - c) + "), then divide (" + str(res - c) + " / " + str(k) + " = " + str(start) + "). Check forward: " + str(start) + " x " + str(k) + " + " + str(c) + " = " + str(res) + "."
    return mkitem("problem_solving", "Problem Solving", "6.1", "working_backwards", "Think", "medium", stem, cands, 0, expl, "Undo each step in reverse.", ["working_backwards", "two_step"])
q = gen_bw()
if q and add(q):
    pass
print("NEW:", len(newqs), dict(collections.Counter(x["archetype"] for x in newqs)))
print("NEW by domain:", dict(collections.Counter(x["domain"] for x in newqs)))
ids = [x["id"] for x in newqs]
assert len(ids) == len(set(ids)), "dup new ids"
assert not (set(ids) & set(byid)), "collision with bank ids"
json.dump(newqs, open("revamp/bank/ha_new_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE revamp/bank/ha_new_20260921.json")

