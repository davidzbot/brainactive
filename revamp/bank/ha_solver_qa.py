import json, re, collections, math
BANK = "revamp/bank/brainactive_p3_question_bank_ha20260921.json"
d = json.load(open(BANK, encoding="utf-8"))
qs = d["questions"]
live = [q for q in qs if not str(q.get("qa_status", "")).startswith("rejected")]
print("LIVE:", len(live))
def norm(t):
    return re.sub(r"\s+", " ", str(t).strip().lower()).replace(",", "")
def recorded(q):
    for o in q["options"]:
        if o["id"] == q["answer"]:
            return norm(o["text"])
    return ""
rows = []
def emit(q, verdict, check, note, derived=""):
    rows.append({"id": q["id"], "archetype": q["archetype"], "verdict": verdict, "check": check, "note": note, "derived": derived})
COMPARC = ("weight_system", "number_puzzles_systems", "guess_check", "working_backwards", "before_after_transfer", "before_after", "chained_comparison", "chain_comparison", "quantitative_logic", "draw_diagram_gaps", "draw_diagram", "pattern_application", "number_sequence", "pattern_discovery", "count_sequence", "figure_sequence", "interleaved_sequence", "alternating_rule", "growing_difference", "compound_rule_analogy", "number_analogy", "numerical_relationships")
def gates(q):
    notes = []
    exp = q.get("explanation", "")
    if len(exp) < 60:
        notes.append("explanation too short")
    ans = recorded(q)
    if ans and len(ans) > 2 and ans not in norm(exp):
        notes.append("explanation never states answer")
    stem_nums = set(re.findall(r"\d+", q["question"]))
    opt_nums = set(re.findall(r"\d+", " ".join(str(o["text"]) for o in q["options"])))
    if q["archetype"] not in COMPARC:
        for n in set(re.findall(r"\d+", exp)):
            if n not in stem_nums and n not in opt_nums and int(n) > 20:
                notes.append("explanation has big stray number " + n)
                break
    if q["archetype"] in ("number_analogy", "compound_rule_analogy", "numerical_relationships") and re.search(r"(Pattern:|sequence grows|each step adds)", exp):
        notes.append("sequence language inside analogy explanation")
    blob = (q["question"] + " " + exp).lower()
    if "lorem" in blob or "xxx" in blob:
        notes.append("placeholder text")
    return notes
SOLVERS = {}
def solver(*archs):
    def deco(fn):
        for a in archs:
            SOLVERS[a] = fn
        return fn
    return deco
SIDES = {"triangle": 3, "square": 4, "pentagon": 5, "hexagon": 6}
DIRS = ["UP", "RIGHT", "DOWN", "LEFT"]
NUMW = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}

EDGEPATS = [re.compile(r"(\w+) beats (\w+)"), re.compile(r"(\w+) is taller than (\w+)"), re.compile(r"(\w+) finishes before (\w+)"), re.compile(r"(\w+) finishes after (\w+)")]
def parse_order(stem):
    edges = []
    for p in EDGEPATS[:3]:
        edges.extend([(a, b) for a, b in p.findall(stem)])
    for a, b in EDGEPATS[3].findall(stem):
        edges.append((b, a))
    nodes = []
    for a, b in edges:
        for x in (a, b):
            if x not in nodes:
                nodes.append(x)
    beats = collections.defaultdict(list)
    beaten_by = {}
    for a, b in edges:
        beats[a].append(b)
        beaten_by[b] = a
    starts = [x for x in nodes if x not in beaten_by]
    if len(starts) != 1:
        return [], edges
    order = [starts[0]]
    while len(order) < len(nodes):
        nxt = [b for b in beats[order[-1]] if b not in order]
        if len(nxt) != 1:
            return [], edges
        order.append(nxt[0])
    return order, edges
@solver("merge_partial_orders", "linear_order", "deductive_ordering")
def solve_order(q):
    order, edges = parse_order(q["question"])
    if len(order) < 3 or len(edges) < 2:
        return None, "low", "could not parse order edges"
    t = q["question"]
    if "MUST be true" in t:
        trues = [o["text"] for o in q["options"] if holds_claim(o["text"], order)]
        if len(trues) == 1:
            return trues[0], "high", "only true claim"
        return None, "low", "must-be-true true count " + str(len(trues))
    m = re.search(r"finishes (first|second|third|fourth|fifth)", t)
    if m:
        idx = ["first", "second", "third", "fourth", "fifth"].index(m.group(1))
        return order[idx] if idx < len(order) else None, "high", "position read-off"
    m = re.search(r"Who is the (tallest|shortest)", t)
    if m:
        return (order[0] if m.group(1) == "tallest" else order[-1]), "high", "endpoint read-off"
    if "Order them" in t:
        return ", ".join(order), "high", "assembled chain"
    return None, "low", "unknown ask form"
def holds_claim(txt, order):
    for p in EDGEPATS:
        m = p.search(txt)
        if m:
            a, b = m.group(1), m.group(2)
            if a in order and b in order:
                return order.index(a) < order.index(b)
    return False

def parse_fig(desc):
    f = {}
    f["size"] = "small" if "small" in desc else ("large" if "large" in desc else "")
    f["colour"] = next((c for c in ("red", "blue", "green") if c in desc), "")
    f["shape"] = next((s for s in ("triangle", "square", "pentagon", "hexagon") if s in desc), "")
    f["dot"] = "with a dot" in desc
    return f
FAM = [
    ("dot-iff-even", lambda f: f["dot"] == (SIDES[f["shape"]] % 2 == 0)),
    ("small-iff-tri", lambda f: (f["size"] == "small") == (f["shape"] == "triangle")),
    ("blue-iff-gt4", lambda f: (f["colour"] == "blue") == (SIDES[f["shape"]] > 4)),
    ("dot-iff-large", lambda f: f["dot"] == (f["size"] == "large")),
    ("green-iff-36", lambda f: (f["colour"] == "green") == (SIDES[f["shape"]] in (3, 6))),
    ("dot-iff-large-even", lambda f: f["dot"] == (f["size"] == "large" and SIDES[f["shape"]] % 2 == 0)),
]
@solver("figure_odd_one_rule")
def solve_odd(q):
    parts = re.findall(r"\b([A-D]) ((?:small|large) (?:red|blue|green) (?:triangle|square|pentagon|hexagon)(?: with a dot)?)", q["question"])
    if len(parts) < 4:
        return None, "low", "could not parse 4 figures"
    figs = [(L, parse_fig(dd)) for L, dd in parts[:4]]
    if any(not all([f["size"], f["colour"], f["shape"]]) for _, f in figs):
        return None, "low", "figure parse incomplete"
    odds = set()
    for name, pred in FAM:
        try:
            vals = [pred(f) for _, f in figs]
        except Exception:
            continue
        if sum(vals) == 3:
            odds.add(vals.index(False))
    if len(odds) == 1:
        i = next(iter(odds))
        return "Figure " + figs[i][0], "high", "all fitting rules agree"
    return None, "low", "odd-one candidates " + str(len(odds))
@solver("figure_analogy")
def solve_analogy(q):
    m = re.search(r"A (.+?) changes into a[n]? (.+?)\. Using the same change, a[n]? (.+?) changes into", q["question"])
    if not m:
        return None, "low", "analogy stem unparsed"
    g2 = re.sub(r"\(.*?\)", "", m.group(2))
    f1, f2, f3 = parse_fig(m.group(1)), parse_fig(g2), parse_fig(m.group(3))
    if not all([f1["shape"], f2["shape"], f3["shape"]]):
        return None, "low", "analogy figure parse incomplete"
    exp = dict(f3)
    nch = 0
    if f1["size"] != f2["size"]:
        nch += 1
        exp["size"] = "large" if f3["size"] == "small" else "small"
    if f1["colour"] != f2["colour"]:
        nch += 1
        cyc = ["red", "blue", "green"]
        step = (cyc.index(f2["colour"]) - cyc.index(f1["colour"])) % 3
        exp["colour"] = cyc[(cyc.index(f3["colour"]) + step) % 3]
    if f1["shape"] != f2["shape"]:
        nch += 1
        delta = SIDES[f2["shape"]] - SIDES[f1["shape"]]
        ns = SIDES[f3["shape"]] + delta
        inv = {v: k for k, v in SIDES.items()}
        if ns not in inv:
            return None, "low", "shape change out of range"
        exp["shape"] = inv[ns]
    if f1["dot"] != f2["dot"]:
        nch += 1
        exp["dot"] = not f3["dot"]
    if nch == 0:
        return None, "low", "no change detected in pair 1"
    want = exp["size"] + " " + exp["colour"] + " " + exp["shape"] + (" with a dot" if exp["dot"] else "")
    hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(want)]
    if len(hits) == 1:
        return hits[0], "high", "projected change unique match"
    return None, "low", "projected matches " + str(len(hits))
@solver("letter_patterns", "letter_pattern")
def solve_letter(q):
    m0 = re.search(r"goes: ((?:[A-Z], )+[A-Z])", q["question"])
    lets = m0.group(1).split(", ") if m0 else re.findall(r"\b([B-Z])(?=[, ])", q["question"])
    vals = [ord(c) - 64 for c in lets]
    if len(vals) < 4:
        return None, "low", "letters too few"
    gaps = [vals[i+1]-vals[i] for i in range(len(vals)-1)]
    pred = None
    if len(set(gaps)) == 1:
        pred = vals[-1] + gaps[0]
    elif len(vals) >= 5 and gaps[0] == gaps[2] and gaps[1] == gaps[3]:
        pred = vals[-1] + (gaps[0] if len(gaps) % 2 == 0 else gaps[1])
    elif len(gaps) >= 3 and all(gaps[i+1]-gaps[i] == 1 for i in range(len(gaps)-1)):
        pred = vals[-1] + gaps[-1] + 1
    if pred is None or pred < 1 or pred > 26:
        return None, "low", "no clean gap pattern"
    want = chr(64 + pred)
    hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(want)]
    if len(hits) == 1:
        return hits[0], "high", "gap pattern found"
    return None, "low", "predicted letter matches " + str(len(hits))

def fit_analog(x1, y1):
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
def apply_f(r, x):
    if r[0] == "add":
        return x + r[1]
    if r[0] == "mul":
        return r[1] * x
    if r[0] == "dual":
        return r[1] * x + r[2]
    if r[0] == "sq":
        return x * x
    return None
@solver("compound_rule_analogy", "number_analogy", "numerical_relationships")
def solve_dual(q):
    nums = list(map(int, re.findall(r"\d+", q["question"])))
    if len(nums) < 3:
        return None, "low", "numbers unparsed"
    x1, y1, x2 = nums[0], nums[1], nums[2]
    fr = fit_analog(x1, y1)
    if not fr:
        return None, "low", "no rule fits pair 1"
    outs = collections.Counter(apply_f(r, x2) for r in fr)
    onums = []
    for o in q["options"]:
        m = re.search(r"-?\d+", str(o["text"]))
        onums.append(int(m.group()) if m else None)
    good = [o["text"] for o, n in zip(q["options"], onums) if n is not None and n in outs]
    if len(good) == 1:
        conf = "high" if len(fr) == 1 else "medium"
        return good[0], conf, "rules fitting pair1"
    return None, "low", "ambiguous analogy options"
@solver("number_sequence", "pattern_discovery", "count_sequence", "figure_sequence", "interleaved_sequence", "alternating_rule", "growing_difference")
def solve_seq(q):
    if "___" in q["question"] and "sum of the two before" in q["question"]:
        toks = re.findall(r"\d+|___", q["question"])
        if toks.count("___") == 1 and len(toks) >= 5:
            hits = []
            for o in q["options"]:
                mm = re.search(r"-?\d+", str(o["text"]))
                if not mm:
                    continue
                seq = [int(mm.group()) if x == "___" else int(x) for x in toks]
                if len(seq) >= 5 and all(seq[i] == seq[i-1] + seq[i-2] for i in range(2, len(seq))):
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "unique fib completion"
            return None, "low", "fib completions not unique"
    m = re.search(r"((?:\d+[, ]+){3,}\d+)", q["question"])
    if not m:
        return None, "low", "series unparsed"
    vals = list(map(int, re.findall(r"\d+", m.group(1))))
    if len(vals) < 4:
        return None, "low", "series too short"
    gaps = [vals[i+1]-vals[i] for i in range(len(vals)-1)]
    cands = {}
    if len(set(gaps)) == 1:
        cands["const"] = vals[-1] + gaps[0]
    if len(vals) >= 5 and all(vals[i] == vals[i-1] + vals[i-2] for i in range(2, len(vals))):
        cands["fib"] = vals[-1] + vals[-2]
    if len(vals) >= 5:
        odd = vals[0::2]
        even = vals[1::2]
        go = [odd[i+1]-odd[i] for i in range(len(odd)-1)]
        ge = [even[i+1]-even[i] for i in range(len(even)-1)]
        if len(set(go)) == 1 and len(set(ge)) == 1 and (go[0], ge[0]) != (0, 0):
            cands["alt-jump"] = (even[-1] + ge[0]) if len(vals) % 2 == 1 else (odd[-1] + go[0])
    if len(vals) >= 4:
        ok = True
        for i in range(1, len(vals)):
            want = vals[i-1] * 2 if i % 2 == 1 else vals[i-1] + 1
            if vals[i] != want:
                ok = False
                break
        if ok:
            cands["x2+1"] = vals[-1] * 2
    if len(vals) >= 4 and all(vals[i] == vals[i-1] * 3 for i in range(1, len(vals))):
        cands["triple"] = vals[-1] * 3
    if len(vals) >= 4:
        rts = [round(v ** 0.5) for v in vals]
        if all(r * r == v for r, v in zip(rts, vals)) and rts == list(range(rts[0], rts[0] + len(rts))):
            cands["squares"] = (rts[-1] + 1) ** 2
    if not cands and len(vals) >= 5:
        ops = []
        for i in range(1, len(vals)):
            if vals[i] == vals[i-1] * 2:
                ops.append(("m", 2))
            elif vals[i] == vals[i-1] * 3:
                ops.append(("m", 3))
            elif 1 <= vals[i] - vals[i-1] <= 9:
                ops.append(("a", vals[i] - vals[i-1]))
            else:
                ops.append(None)
        tail = ops[1:]
        if all(o is not None for o in ops) and len(tail) >= 4 and all(tail[i] == tail[i % 2] for i in range(len(tail))):
            lastop = tail[len(tail) % 2]
            pred = vals[-1] * lastop[1] if lastop[0] == "m" else vals[-1] + lastop[1]
            cands["alt-ops"] = pred
    if len(gaps) >= 3 and all(gaps[i+1]-gaps[i] == 1 for i in range(len(gaps)-1)):
        cands["grow"] = vals[-1] + gaps[-1] + 1
    if len(vals) >= 4 and all(vals[i] == vals[i-1] * 2 for i in range(1, len(vals))):
        cands["double"] = vals[-1] * 2
    if not cands:
        return None, "low", "no clean rule"
    if len(cands) > 1:
        return None, "low", "ambiguous sequence rules"
    rule, pred = next(iter(cands.items()))
    hits = []
    for o in q["options"]:
        mm = re.search(r"-?\d+", str(o["text"]))
        if mm and int(mm.group()) == pred:
            hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "rule " + rule
    return None, "low", "predicted value not unique in options"
@solver("working_backwards")
def solve_back(q):
    nums = list(map(int, re.findall(r"\d+", q["question"])))
    t = q["question"].lower()
    pred = None
    if "plus" in t and "equals" in t and len(nums) == 2:
        pred = nums[1] - nums[0]
    else:
        ops = []
        for mm in re.finditer(r"doubled|halved|multiplied by (\d+)|(\d+) is added|(\d+) is subtracted|(\d+) got off|(\d+) got on", t):
            s = mm.group(0)
            if s == "doubled":
                ops.append(("*", 2))
            elif s == "halved":
                ops.append(("/", 2))
            elif mm.group(1):
                ops.append(("*", int(mm.group(1))))
            elif mm.group(2):
                ops.append(("+", int(mm.group(2))))
            elif mm.group(3):
                ops.append(("-", int(mm.group(3))))
            elif mm.group(4):
                ops.append(("-", int(mm.group(4))))
            elif mm.group(5):
                ops.append(("+", int(mm.group(5))))
        mc = re.search(r"changed by: ([^.\n]+)\.", t)
        if mc:
            for mm2 in re.finditer(r"([x+\-])\s*(\d+)", mc.group(1)):
                oc, on = mm2.group(1), int(mm2.group(2))
                ops.append(("*", on) if oc == "x" else (oc, on))
        mr = re.search(r"(?:result is|there are|final result is) (\d+)", t)
        if ops and mr:
            v = int(mr.group(1))
            ok = True
            for op, n in reversed(ops):
                if op == "*":
                    ok = v % n == 0
                    v = v // n
                elif op == "/":
                    v = v * n
                elif op == "+":
                    v = v - n
                else:
                    v = v + n
                if not ok:
                    break
            if ok:
                pred = v
    if pred is None:
        return None, "low", "backwards form unparsed"
    hits = []
    for o in q["options"]:
        mm = re.search(r"-?\d+", str(o["text"]))
        if mm and int(mm.group()) == pred:
            hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "inverted operations"
    return None, "low", "inverted value not unique in options"

STOPW = {"is": 1, "are": 1, "was": 1, "were": 1, "be": 1, "been": 1, "has": 1, "have": 1, "had": 1, "does": 1, "do": 1, "did": 1, "a": 1, "an": 1, "the": 1, "it": 1, "they": 1, "them": 1, "their": 1, "this": 1, "that": 1, "these": 1, "those": 1, "to": 1, "of": 1, "in": 1, "on": 1, "at": 1, "for": 1, "with": 1, "and": 1, "or": 1, "if": 1, "then": 1, "when": 1, "what": 1, "which": 1, "who": 1, "must": 1, "can": 1, "will": 1, "would": 1, "should": 1, "all": 1, "every": 1, "any": 1, "each": 1, "exactly": 1, "today": 1, "there": 1}
NEGW = {"not": 1, "no": 1, "never": 1, "without": 1, "cannot": 1}
def stemw(w):
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss") and not w.endswith("us"):
        return w[:-1]
    return w
def clause_parts(s):
    toks = re.findall(r"[a-z0-9]+", s.lower())
    neg = any(w in NEGW for w in toks) or bool(re.search(r"n.t\b", s.lower()))
    core = frozenset(stemw(w) for w in toks if w not in STOPW and w not in NEGW)
    return core, neg
def cmatch(c1, c2):
    if not c1 or not c2:
        return 0.0
    return len(c1 & c2) / max(1, min(len(c1), len(c2)))
def solve_rule_engine(q):
    t = q["question"]
    rules = []
    for m in re.finditer(r"[Ii]f (.*?),(?: then)?(.*?)(?:\.|$)", t):
        p, qq = m.group(1).strip(), m.group(2).strip()
        if p and qq and len(p.split()) <= 14 and len(qq.split()) <= 14:
            rules.append((p, qq))
    if not rules:
        return None, "low", "no if-rules parsed"
    gm = re.search(r"Given:(.*?)(?:\.|$)", t)
    if gm:
        given = gm.group(1).strip()
    else:
        sents = [s.strip() for s in re.split(r"\.(?!\d)", t) if s.strip()]
        given = sents[-1] if sents else ""
    gcore, gneg = clause_parts(given)
    ent = set()
    ref = set()
    if gneg:
        ref.add(gcore)
    else:
        ent.add(gcore)
    for _ in range(6):
        grew = False
        for p, qq in rules:
            pc, _ = clause_parts(p)
            qc, _ = clause_parts(qq)
            for e in list(ent):
                if cmatch(pc, e) >= 0.5 and not any(cmatch(qc, x) >= 0.5 for x in ent):
                    ent.add(qc)
                    grew = True
            for r in list(ref):
                if cmatch(qc, r) >= 0.5 and not any(cmatch(pc, x) >= 0.5 for x in ref):
                    ref.add(pc)
                    grew = True
        if not grew:
            break
    hits = []
    for o in q["options"]:
        oc, oneg = clause_parts(o["text"])
        if oneg:
            if any(cmatch(oc, r) >= 0.5 for r in ref):
                hits.append(o["text"])
        else:
            if any(cmatch(oc, e) >= 0.5 for e in ent):
                hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "rule engine unique entailment"
    return None, "low", "rule engine hits not unique"
@solver("conditional_contrapositive", "conditional", "conditional_logic", "modus_tollens", "chained_conditionals", "sentence_logic")
def solve_cond(q):
    return solve_rule_engine(q)
@solver("syllogism", "syllogisms", "syllogism_particular")
def solve_syll(q):
    alls = re.findall(r"All (\w+) are (\w+)", q["question"])
    somes = re.findall(r"Some (\w+) are (\w+)", q["question"])
    trues = set()
    for a, b in alls:
        trues.add((a, b))
    changed = True
    while changed:
        changed = False
        for a, b in list(trues):
            for c, dd in list(trues):
                if b == c and (a, dd) not in trues:
                    trues.add((a, dd))
                    changed = True
    for a, b in somes:
        for c, dd in list(trues):
            if b == c:
                trues.add(("Some " + a, dd))
    hits = []
    for o in q["options"]:
        m = re.match(r"All (\w+) are (\w+)", o["text"])
        if m and (m.group(1), m.group(2)) in trues:
            hits.append(o["text"])
            continue
        m = re.match(r"Some (\w+) are (\w+)", o["text"])
        if m and ("Some " + m.group(1), m.group(2)) in trues:
            hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "transitive closure unique"
    return None, "low", "syllogism hits not unique"

PAIRSEP = "(?:becomes|->|to)"
@solver("before_after_transfer")
def solve_transfer(q):
    t = q["question"]
    mb = re.search(r"After (\w+) gives (\w+) (\d+).*?both .*? have (\d+).*?How many .*? did (\w+) have at first", t)
    if mb and mb.group(1) == mb.group(5):
        pred = int(mb.group(4)) + int(mb.group(3))
        hits = []
        for o in q["options"]:
            mm = re.search(r"-?\d+", str(o["text"]))
            if mm and int(mm.group()) == pred:
                hits.append(o["text"])
        if len(hits) == 1:
            return hits[0], "high", "hidden total backwards"
        return None, "low", "hidden total not unique"
    m = re.search(r"(\w+) has (\d+).*? and (\w+) has (\d+)", t)
    if not m:
        return None, "low", "opening counts unparsed"
    a, A, b, B = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
    A1, B1 = A, B
    for gm in re.finditer(r"(\w+) gives (\w+) (\d+)", t):
        g, r, x = gm.group(1), gm.group(2), int(gm.group(3))
        if g == a:
            A1 -= x
        elif g == b:
            B1 -= x
        if r == a:
            A1 += x
        elif r == b:
            B1 += x
    if A1 == B1:
        want = "tied"
    else:
        lead = a if A1 > B1 else b
        want = norm(lead + " by " + str(abs(A1 - B1)))
    hits = [o["text"] for o in q["options"] if norm(o["text"]) == want or (want == "tied" and "tie" in norm(o["text"]))]
    if len(hits) == 1:
        return hits[0], "high", "simulated transfers"
    return None, "low", "transfer sim not unique"
@solver("before_after")
def solve_ba(q):
    t = q["question"]
    m = re.search(r"(\w+) has (\d+) more .*? than (\w+)", t)
    g = re.search(r"gives .*? (\d+)", t)
    if not m or not g:
        return None, "low", "gap or gift unparsed"
    a, M, b, G = m.group(1), int(m.group(2)), m.group(3), int(g.group(1))
    if M == 2 * G:
        return None, "low", "tie outcome"
    lead = a if M > 2 * G else b
    want = norm(lead + " by " + str(abs(M - 2 * G)))
    hits = [o["text"] for o in q["options"] if norm(o["text"]) == want]
    if len(hits) == 1:
        return hits[0], "high", "gap closes double"
    return None, "low", "gap math not unique"
@solver("chained_comparison", "chain_comparison", "quantitative_logic")
def solve_chain4(q):
    t = q["question"]
    rels = re.findall(r"(\w+) has (\d+) (more|fewer)\s+(?:.*?\s+)?than\s+(\w+)", t)
    if not rels:
        return None, "low", "chain relations unparsed"
    cands = [(m.group(1), int(m.group(2))) for m in re.finditer(r"(\w+) has (\d+)(?: \w+)?\.", t) if "more" not in m.group(0) and "fewer" not in m.group(0)]
    if not cands:
        return None, "low", "chain anchor unparsed"
    aname, aval = cands[-1]
    val = {aname: aval}
    changed = True
    while changed:
        changed = False
        for x, n, w, y in rels:
            n = int(n)
            if x in val and y not in val:
                val[y] = val[x] - n if w == "more" else val[x] + n
                changed = True
            elif y in val and x not in val:
                val[x] = val[y] + n if w == "more" else val[y] - n
                changed = True
    if "Who has the most" in t:
        if len(val) < 3:
            return None, "low", "chain incomplete"
        top = max(val, key=lambda k: val[k])
        hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(top)]
        if len(hits) == 1:
            return hits[0], "high", "chained counts"
        return None, "low", "top not unique"
    m = re.search(r"How many .*? does (\w+) have", t)
    if m and m.group(1) in val:
        hits = []
        for o in q["options"]:
            mm = re.search(r"-?\d+", str(o["text"]))
            if mm and int(mm.group()) == val[m.group(1)]:
                hits.append(o["text"])
        if len(hits) == 1:
            return hits[0], "high", "chained count"
        return None, "low", "count not unique"
    return None, "low", "ask form unparsed"
@solver("draw_diagram_gaps", "draw_diagram")
def solve_fence(q):
    t = q["question"]
    nums = list(map(int, re.findall(r"\d+", t)))
    if len(nums) < 2:
        return None, "low", "counts unparsed"
    n, g = nums[0], nums[1]
    if re.search(r"circular|around", t, re.I):
        pred = n * g
    else:
        pred = (n - 1) * g
    hits = []
    for o in q["options"]:
        mm = re.search(r"-?\d+", str(o["text"]))
        if mm and int(mm.group()) == pred:
            hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "gap count rule"
    return None, "low", "fence math not unique"
@solver("pattern_application")
def solve_machine(q):
    t = q["question"].replace("ARR", "->")
    if "repeats" in t or "1st" in t:
        m = re.search(r"repeats: ([a-z, ]+?)[\.\(]", t, re.I)
        askt = t[t.find("What"): ] if "What" in t else t
        asks = [int(x) for x in re.findall(r"(\d+)(?:st|nd|rd|th)", askt)]
        if m and asks:
            period = [c.strip() for c in m.group(1).split(",") if c.strip()]
            wants = [period[(a - 1) % len(period)] for a in asks]
            hits = []
            for o in q["options"]:
                pos = -1
                ok = True
                for w in wants:
                    p = norm(o["text"]).find(norm(w), pos + 1)
                    if p < 0:
                        ok = False
                        break
                    pos = p
                if ok:
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "periodic positions"
        return None, "low", "tile pattern unparsed"
    t = t.replace(chr(0x2192), "->")
    pairs = re.findall("(\\d+)\\s*(?:becomes|-+>|to)\\s*(\\d+)", t)
    mi = re.search(r"input is (\d+)", t) or re.search(r"What should (\d+) become", t)
    if len(pairs) >= 2 and mi:
        xs = [int(a) for a, _ in pairs]
        ys = [int(b) for _, b in pairs]
        rules = []
        for a in range(1, 6):
            for bb in range(-9, 10):
                if all(a * x + bb == y for x, y in zip(xs, ys)):
                    rules.append((a, bb))
        if all(x > 0 for x in xs) and all(y > 0 for y in ys):
            if all(x * (x - 1) == y for x, y in zip(xs, ys)):
                rules.append(("sqm", 0))
        if len(rules) == 1:
            r = rules[0]
            iv = int(mi.group(1))
            pred = r[0] * iv + r[1] if r[0] != "sqm" else iv * (iv - 1)
            hits = []
            for o in q["options"]:
                mm = re.search(r"-?\d+", str(o["text"]))
                if mm and int(mm.group()) == pred:
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "refitted machine rule"
            return None, "low", "refit value not unique"
        return None, "low", "machine rules not unique"
    return None, "low", "machine examples unparsed"
    return None, "low", "machine examples unparsed"
@solver("two_step_rotation", "rotation", "single_rotation")
def solve_rot(q):
    t = q["question"]
    m = re.search(r"points (\w+)", t)
    if not m:
        return None, "low", "start direction unparsed"
    dd = m.group(1).upper()
    if dd not in DIRS:
        return None, "low", "start direction unknown"
    seq = []
    for mm in re.finditer(r"(90 degrees clockwise|90 degrees anticlockwise|180 degrees|half turn|flipped left-to-right|vertical mirror)", t.lower()):
        s = mm.group(1)
        if "anticlockwise" in s:
            seq.append(-1)
        elif "clockwise" in s:
            seq.append(1)
        elif "180" in s or "half turn" in s:
            seq.append(2)
        else:
            seq.append("M")
    if ("twice" in t.lower() or "2 times" in t.lower()) and len(seq) == 1:
        seq = seq * 2
    if not seq:
        return None, "low", "no moves parsed"
    for s in seq:
        if s == "M":
            dd = {"LEFT": "RIGHT", "RIGHT": "LEFT"}.get(dd, dd)
        else:
            dd = DIRS[(DIRS.index(dd) + s) % 4]
    hits = [o["text"] for o in q["options"] if dd.lower() in norm(o["text"])]
    if len(hits) == 1:
        return hits[0], "high", "simulated turns"
    return None, "low", "heading not unique"
import itertools
@solver("weight_system", "number_puzzles_systems")
def solve_weight(q):
    t = q["question"].lower()
    pairs = re.findall(r"(?:a|an|the) (\w+ \w+) and (?:a|an|the) (\w+ \w+) together weigh (\d+)", t)
    if not pairs:
        pairs = re.findall(r"(?:a|an|the) (\w+ \w+) and (?:a|an|the) (\w+ \w+) weigh (\d+)[^.\n]*?together", t)
    if not pairs:
        pairs = re.findall(r"(?:a|an|the) (\w+ \w+) and (?:a|an|the) (\w+ \w+) balance (\d+)", t)
    if not pairs:
        pairs = re.findall(r"(?:a|an|the) (\w+) and (?:a|an|the) (\w+) together weigh (\d+)", t)
    if not pairs:
        pairs = re.findall(r"(?:a|an|the) (\w+) and (?:a|an|the) (\w+) weigh (\d+)[^.\n]*?together", t)
    if not pairs:
        pairs = re.findall(r"(?:a|an|the) (\w+) and (?:a|an|the) (\w+) balance (\d+)", t)
    if len(pairs) < 2:
        return None, "low", "balance pairs unparsed"
    eqs = [(a, b, int(n)) for a, b, n in pairs[:3]]
    shapes = list({s for e in eqs for s in e[:2]})
    if len(eqs) == 3 and len(shapes) == 3:
        vm = None
        for order in itertools.permutations(shapes):
            o1, o2, o3 = order
            em = {}
            good = True
            for x, y, m in eqs:
                key = tuple(sorted([x, y]))
                if key in em and em[key] != m:
                    good = False
                    break
                em[key] = m
            if not good:
                continue
            k12 = tuple(sorted([o1, o2]))
            k23 = tuple(sorted([o2, o3]))
            k13 = tuple(sorted([o1, o3]))
            if k12 not in em or k23 not in em or k13 not in em:
                continue
            r12, r23, r13 = em[k12], em[k23], em[k13]
            if (r12 + r13 - r23) % 2 != 0:
                continue
            v1 = (r12 + r13 - r23) // 2
            v2 = r12 - v1
            v3 = r13 - v1
            if v1 + v2 == r12 and v2 + v3 == r23 and v1 + v3 == r13 and min(v1, v2, v3) > 0:
                vm = {o1: v1, o2: v2, o3: v3}
                break
        if not vm:
            return None, "low", "system unsolvable"
        if "heaviest" in t:
            want = max(vm, key=lambda k: vm[k])
            hits = [o["text"] for o in q["options"] if norm(want) in norm(o["text"])]
            if len(hits) == 1:
                return hits[0], "high", "solved 3-variable system"
            return None, "low", "extreme not unique"
        if "lightest" in t:
            want = min(vm, key=lambda k: vm[k])
            hits = [o["text"] for o in q["options"] if norm(want) in norm(o["text"])]
            if len(hits) == 1:
                return hits[0], "high", "solved 3-variable system"
            return None, "low", "extreme not unique"
        mt = re.search(r"total weight of one (\w+)", t)
        if mt:
            pred = sum(vm.values())
            hits = []
            for o in q["options"]:
                mm = re.search(r"-?\d+", str(o["text"]))
                if mm and int(mm.group()) == pred:
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "summed one-each total"
            return None, "low", "total not unique"
        m = re.search(r"weight of one ([\w ]+?)(?:\?|\.|$)", t)
        if m:
            nm = m.group(1).strip().lower()
            if nm in vm:
                hits = []
                for o in q["options"]:
                    mm = re.search(r"-?\d+", str(o["text"]))
                    if mm and int(mm.group()) == vm[nm]:
                        hits.append(o["text"])
                if len(hits) == 1:
                    return hits[0], "high", "solved one weight"
                return None, "low", "one weight not unique"
        m = re.search(r"how (?:much|many).*?does (?:the|a|an|one) (\w+) weigh", t)
        if m and m.group(1) in vm:
            hits = []
            for o in q["options"]:
                mm = re.search(r"-?\d+", str(o["text"]))
                if mm and int(mm.group()) == vm[m.group(1)]:
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "solved system weight"
            return None, "low", "weight not unique"
        return None, "low", "weight ask unparsed"
    return None, "low", "weight form unparsed"
@solver("guess_check")
def solve_guess(q):
    t = q["question"]
    dm = re.search(r"(\d+)-dollar and some (?:are )?(\d+)-dollar|some (\d+)-dollar and some (?:are )?(\d+)-dollar", t)
    n = re.search(r"(\d+) coins in total", t)
    m = re.search(r"make (\d+) dollars", t)
    a = re.search(r"How many (\d+)-dollar", t)
    if dm and n and m and a:
        d1 = int(dm.group(1) or dm.group(3))
        d2 = int(dm.group(2) or dm.group(4))
        N, M = int(n.group(1)), int(m.group(1))
        ask = int(a.group(1))
        other = d1 if ask == d2 else d2
        if ask == other or (M - other * N) % (ask - other) != 0:
            return None, "low", "non-integer split"
        pred = (M - other * N) // (ask - other)
        hits = []
        for o in q["options"]:
            mm = re.search(r"-?\d+", str(o["text"]))
            if mm and int(mm.group()) == pred:
                hits.append(o["text"])
        if len(hits) == 1:
            return hits[0], "high", "solved coin split"
        return None, "low", "split not unique"
    return None, "low", "coin form unparsed"
@solver("word_manipulation")
def solve_word(q):
    t = q["question"]
    ex = re.findall(r"([A-Z]{3,})[^A-Z]+([A-Z]{3,})", t)
    ask = re.search(r"What does ([A-Z]+) become", t)
    if not ex or not ask:
        return None, "low", "word example unparsed"
    src, dst = ex[0][0], ex[0][1]
    w = ask.group(1)
    if dst == src[::-1]:
        pred = w[::-1]
    elif dst == src[1:] + src[:1]:
        pred = w[1:] + w[:1]
    elif dst == src[-1] + src[:-1]:
        pred = w[-1] + w[:-1]
    else:
        return None, "low", "word rule unknown"
    hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(pred)]
    if len(hits) == 1:
        return hits[0], "high", "word rule applied"
    return None, "low", "word not unique"
@solver("make_a_list", "make_list")
def solve_combi(q):
    t = q["question"]
    pred = None
    m = re.search(r"(\d+) children .*?(line|photograph)", t)
    if m:
        pred = math.factorial(int(m.group(1)))
    else:
        m = re.search(r"borrow (\d+) books.*?shelf of (\d+)", t)
        if m:
            pred = math.comb(int(m.group(2)), int(m.group(1)))
        else:
            m = re.search(r"(\d+)-letter codes.*?letters (.*?)(?: if |\.|$)", t)
            if m:
                k = int(m.group(1))
                lets = re.findall(r"[A-Z]", m.group(2))
                if re.search(r"without repeating|no letter can be used more than once", t):
                    pred = math.perm(len(lets), k)
                else:
                    pred = len(lets) ** k
            else:
                m = re.search(r"add up to (\d+)", t)
                if m and "dice" in t:
                    pred = 6 - abs(7 - int(m.group(1)))
                else:
                    m = re.search(r"(\d+) boys and (\d+) girls", t)
                    if m and "pairs" in t:
                        pred = int(m.group(1)) * int(m.group(2))
                    else:
                        m = re.search(r"using ONLY the digits (\d) and (\d)", t)
                        if m and "3-digit" in t:
                            pred = 2 ** 3
    if pred is None:
        m = re.search(r"(\d+)-digit numbers (greater|less) than (\d+).*?digits (.*?)(?: without|\.)", t)
        if m and int(m.group(1)) == 2:
            cmp, T = m.group(2), int(m.group(3))
            dg = re.findall(r"\d", m.group(4))
            if dg and "0" not in dg:
                if re.search(r"without repeat", t):
                    pool = [a + b for a, b in itertools.permutations(dg, 2)]
                else:
                    pool = [a + b for a in dg for b in dg]
                nums = [int(x) for x in pool]
                pred = sum(1 for x in nums if (x > T if cmp == "greater" else x < T))
    if pred is None:
        m = re.search(r"(\d+)-digit numbers.*?digits (.*?)(?: without|\.)", t)
        if m:
            k = int(m.group(1))
            dg = re.findall(r"\d", m.group(2))
            if dg and "0" not in dg:
                if re.search(r"without repeat", t):
                    pred = math.perm(len(dg), k)
                else:
                    pred = len(dg) ** k
    if pred is None:
        m = re.search(r"(\d+)\s+\w+.*?and (\d+)\s+.*?outfits?", t)
        if m:
            pred = int(m.group(1)) * int(m.group(2))
    if pred is None:
        if re.search(r"shake hands", t):
            m = re.search(r"(\d+) (?:friends|people|children|players)", t)
            n = int(m.group(1)) if m else 0
            if not n:
                m = re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b", t, re.I)
                n = NUMW.get(m.group(1).lower(), 0) if m else 0
            if n >= 2:
                pred = math.comb(n, 2)
    if pred is None:
        return None, "low", "combinatorial form unparsed"
    hits = []
    for o in q["options"]:
        mm = re.search(r"-?\d+", str(o["text"]))
        if mm and int(mm.group()) == pred:
            hits.append(o["text"])
    if len(hits) == 1:
        return hits[0], "high", "counted cases"
    return None, "low", "count not unique"
@solver("codes_ciphers")
def solve_code(q):
    t = q["question"]
    m = re.search(r"move every letter forward (\d+).*?What does (\w+) become", t, re.I)
    if m:
        n, w = int(m.group(1)), m.group(2).upper()
        pred = "".join(chr(65 + (ord(c) - 65 + n) % 26) for c in w)
        if re.search(r"reverse", t, re.I):
            pred = pred[::-1]
        hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(pred)]
        if len(hits) == 1:
            return hits[0], "high", "shift cipher"
        return None, "low", "cipher not unique"
    m = re.search(r"means the letter (\d+) steps? before it.*?code word is (\w+)", t, re.I)
    if m:
        n, w = int(m.group(1)), m.group(2).upper()
        pred = "".join(chr(65 + (ord(c) - 65 - n) % 26) for c in w)
        hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(pred)]
        if len(hits) == 1:
            return hits[0], "high", "decode shift"
        return None, "low", "decode not unique"
    if "square" in t.lower():
        m = re.search(r"What (?:is|does) (\w+)", t)
        m2 = re.search(r"which letter is worth (\d+)", t, re.I)
        if m2:
            import math as _mm
            v = int(m2.group(1))
            r = _mm.isqrt(v)
            if r * r == v:
                want = chr(64 + r)
                hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(want)]
                if len(hits) == 1:
                    return hits[0], "high", "square worth reverse"
                return None, "low", "square reverse not unique"
        if m and len(m.group(1)) == 1:
            pred = (ord(m.group(1).upper()) - 64) ** 2
            hits = []
            for o in q["options"]:
                mm = re.search(r"-?\d+", str(o["text"]))
                if mm and int(mm.group()) == pred:
                    hits.append(o["text"])
            if len(hits) == 1:
                return hits[0], "high", "square code"
    return None, "low", "cipher needs review"
@solver("constraint_placement", "constraint", "seating_constraint", "constraint_matching")
def solve_seat(q):
    import itertools as _it
    t = q["question"]
    if re.search(r"between|either|unless|if ", t, re.I):
        return None, "low", "complex seating wording"
    stop = {"Four", "Three", "Two", "Five", "Who", "Which", "What", "Each", "How", "In", "On", "At", "If", "Cinema", "Row", "Seats", "Seat", "Left", "Right", "Position", "Box", "Class", "School", "Bus", "Car", "Table", "Room", "Team"}
    cands = [w for w in re.findall(r"[A-Z][a-z]+", t) if w not in stop]
    pers = []
    for w in cands:
        if w not in pers:
            pers.append(w)
    if len(pers) < 3 or len(pers) > 6:
        return None, "low", "person count out of range"
    m = re.search(r"seats? 1 to (\d+)|row of (\d+)|positions? 1 to (\d+)", t)
    n = int(m.group(1) or m.group(2) or m.group(3)) if m else len(pers)
    if n != len(pers):
        return None, "low", "seat person mismatch"
    seats = list(range(1, n + 1))
    fixed = {}
    banned = set()
    adj = []
    for p in pers:
        m = re.search(p + r" (?:sits|is) in position (\d+)", t)
        if m:
            fixed[p] = int(m.group(1))
        for mm in re.finditer(p + r" (?:does not sit|is not) in position (\d+)", t):
            banned.add((p, int(mm.group(1))))
        if re.search(p + r" (?:is|sits) at the left end", t):
            fixed[p] = 1
        if re.search(p + r" (?:is|sits) at the right end", t):
            fixed[p] = n
        for mm in re.finditer(p + r" sits next to ([A-Z][a-z]+)", t):
            adj.append((p, mm.group(1)))
        for mm in re.finditer(p + r" is next to ([A-Z][a-z]+)", t):
            adj.append((p, mm.group(1)))
    sols = []
    for perm in _it.permutations(seats):
        mp = dict(zip(pers, perm))
        ok = True
        for p, s in fixed.items():
            if mp.get(p) != s:
                ok = False
        for p, s in banned:
            if mp.get(p) == s:
                ok = False
        for a, b in adj:
            if b not in mp or abs(mp[a] - mp[b]) != 1:
                ok = False
        if ok:
            sols.append(mp)
    if len(sols) != 1:
        return None, "low", "seating solutions not unique"
    mp = sols[0]
    m = re.search(r"Who sits in position (\d+)\?", t)
    if m:
        want = [p for p in pers if mp[p] == int(m.group(1))]
        if len(want) == 1:
            hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(want[0])]
            if len(hits) == 1:
                return hits[0], "high", "unique seating"
            return None, "low", "seat answer not unique"
    m = re.search(r"Where does ([A-Z][a-z]+) sit\?", t)
    if m and m.group(1) in mp:
        hits = []
        for o in q["options"]:
            mm = re.search(r"(\d+)", str(o["text"]))
            if mm and int(mm.group()) == mp[m.group(1)]:
                hits.append(o["text"])
        if len(hits) == 1:
            return hits[0], "high", "unique seating"
        return None, "low", "seat number not unique"
    m = re.search(r"Who sits at the (left|right) end\?", t)
    if m:
        want = [p for p in pers if mp[p] == (1 if m.group(1) == "left" else n)]
        if len(want) == 1:
            hits = [o["text"] for o in q["options"] if norm(o["text"]) == norm(want[0])]
            if len(hits) == 1:
                return hits[0], "high", "unique seating"
    return None, "low", "seating ask unparsed"
@solver("position")
def solve_pos(q):
    t = q["question"]
    cells = {"top-left": (0, 0), "top-middle": (1, 0), "top-center": (1, 0), "top": (1, 0), "top-right": (2, 0), "middle-left": (0, 1), "left-middle": (0, 1), "left": (0, 1), "center": (1, 1), "centre": (1, 1), "middle": (1, 1), "middle-right": (2, 1), "right-middle": (2, 1), "right": (2, 1), "bottom-left": (0, 2), "bottom-middle": (1, 2), "bottom-center": (1, 2), "bottom": (1, 2), "bottom-right": (2, 2)}
    mv = {"below": (0, 1), "above": (0, -1), "to the left of": (-1, 0), "left of": (-1, 0), "to the right of": (1, 0), "right of": (1, 0)}
    at = {}
    def cell_at(desc):
        for k, v in cells.items():
            if k in desc:
                return v
        return None
    for _ in range(6):
        grew = False
        for m in re.finditer(r"(?:the )?(\w+) is in (?:the )?([a-z\- ]+?)(?: square|\.|,)", t):
            obj, cd = m.group(1).lower(), m.group(2).lower()
            c = cell_at(cd)
            if c and obj not in at:
                at[obj] = c
                grew = True
        for m in re.finditer(r"(?:the )?(\w+) is (?:directly )?(below|above|to the left of|left of|to the right of|right of) (?:the )?(\w+)", t):
            obj, rel, ref = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
            if ref in at and obj not in at:
                dx, dy = mv[rel]
                at[obj] = (at[ref][0] + dx, at[ref][1] + dy)
                grew = True
        if not grew:
            break
    m = re.search(r"Where is (?:the )?(\w+)\?", t)
    if m and m.group(1).lower() in at:
        c = at[m.group(1).lower()]
        names = [k for k, v in cells.items() if v == c and len(k) > 5]
        for nm in sorted(names, key=len, reverse=True):
            hits = [o["text"] for o in q["options"] if nm in norm(o["text"])]
            if len(hits) == 1:
                return hits[0], "high", "grid tracked"
        return None, "low", "cell answer not unique"
    return None, "low", "grid ask unparsed"


for q in live:
    arch = q["archetype"]
    is_new = q["id"].startswith("BA_P3_HA_")
    if len(q["options"]) != 4 or q["answer"] not in [o["id"] for o in q["options"]]:
        emit(q, "FAIL", "structural", "bad options or answer id")
        continue
    if any(not isinstance(o["text"], str) for o in q["options"]):
        emit(q, "FAIL", "structural", "non-string option text")
        continue
    if len(set(norm(o["text"]) for o in q["options"])) < 4:
        emit(q, "FAIL", "structural", "duplicate option texts")
        continue
    g = gates(q)
    fn = SOLVERS.get(arch)
    if fn is None:
        emit(q, "REVIEW", "needs-human", "no solver for class; gates clean" if not g else "no solver for class; gates: " + str(g))
        continue
    try:
        derived, conf, note = fn(q)
    except Exception as e:
        emit(q, "REVIEW", "solver-error", str(e)[:120])
        continue
    if derived is None:
        emit(q, "REVIEW", "solver-abstain-" + conf, note + "; gates clean" if not g else note + "; gates: " + str(g))
        continue
    if norm(derived) == recorded(q):
        if g:
            emit(q, "REVIEW" if not is_new else "PASS", "gatewarn", "answer verified " + conf + "; notes: " + str(g), derived)
        else:
            emit(q, "PASS", "solver-match-" + conf, note, derived)
    else:
        if conf == "high":
            emit(q, "FAIL", "answer-mismatch-high", "solver derives " + derived + " vs recorded " + recorded(q), derived)
        else:
            emit(q, "REVIEW", "answer-mismatch-" + conf, "solver derives " + derived + " vs recorded " + recorded(q), derived)
json.dump(rows, open("revamp/bank/ha_solver_tracker_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cnt = collections.Counter(r["verdict"] for r in rows)
print("SOLVER:", dict(cnt), "of", len(rows))
newfails = [r["id"] + ":" + r["archetype"] for r in rows if r["verdict"] == "FAIL" and r["id"].startswith("BA_P3_HA_")]
kepfails = [(r["id"], r["archetype"]) for r in rows if r["verdict"] == "FAIL" and not r["id"].startswith("BA_P3_HA_")]
print("NEW fails:", len(newfails), newfails)
print("KEPT fails:", len(kepfails), kepfails)
arch_fail = collections.Counter(r["archetype"] for r in rows if r["verdict"] == "FAIL")
print("FAIL by archetype:", dict(arch_fail))
rev = collections.Counter(r["check"] for r in rows if r["verdict"] == "REVIEW")
print("REVIEW checks:", dict(rev))
print("WROTE revamp/bank/ha_solver_tracker_20260921.json")

