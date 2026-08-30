# -*- coding: utf-8 -*-
"""
Scale the BrainActive P3 High Ability bank from 100 to 1000.

Strategy (per the curriculum blueprint): deterministic, parameterized generators with
COMPUTED answers and auto-generated near-miss distractors, grounded in the researched
archetypes (GEP General Ability verbal/numerical, CogAT, UK 11+ VR/NVR, MOE 2026 HAL).
The 100 validated questions are kept as the seed; 900 are generated to reach 1000,
preserving the research-derived domain balance (18/18/16/16/20/12).

NO DB / NO Supabase / NO production code. JSON is the temporary source of truth.
All non-seed items are qa_status = ai_generated_not_approved (pending AI1 + human review).
"""
import json
import os
import random

ROOT = r"C:\Projects\brainactive-android\revamp"
BANK = os.path.join(ROOT, "bank", "brainactive_p3_question_bank.json")
SEED = json.load(open(BANK, encoding="cp1252"))
QUESTIONS_DIR = os.path.join(ROOT, "bank", "questions")

DOMAIN_TARGET = {
    "numerical_reasoning": 180,
    "logical_reasoning": 180,
    "verbal_reasoning": 160,
    "visual_spatial": 160,
    "pattern_abstract": 200,
    "problem_solving": 120,
}
DOMAIN_OF_SKILL = {
    "1.1": "numerical_reasoning", "1.2": "numerical_reasoning", "1.3": "numerical_reasoning", "1.4": "numerical_reasoning",
    "2.1": "logical_reasoning", "2.2": "logical_reasoning", "2.3": "logical_reasoning", "2.4": "logical_reasoning", "2.5": "logical_reasoning",
    "3.1": "verbal_reasoning", "3.2": "verbal_reasoning", "3.3": "verbal_reasoning", "3.4": "verbal_reasoning", "3.5": "verbal_reasoning", "3.6": "verbal_reasoning", "3.7": "verbal_reasoning",
    "4.1": "visual_spatial", "4.2": "visual_spatial", "4.3": "visual_spatial", "4.4": "visual_spatial", "4.5": "visual_spatial", "4.6": "visual_spatial",
    "5.1": "pattern_abstract", "5.2": "pattern_abstract", "5.3": "pattern_abstract", "5.4": "pattern_abstract",
    "6.1": "problem_solving", "6.2": "problem_solving", "6.3": "problem_solving", "6.4": "problem_solving", "6.5": "problem_solving", "6.6": "problem_solving",
}
ARCH = {
    "1.1": "number_sequence", "1.2": "number_analogy", "1.3": "weight_system", "1.4": "chained_comparison",
    "2.1": "linear_order", "2.2": "constraint", "2.3": "conditional", "2.4": "classification", "2.5": "syllogism",
    "3.1": "verbal_analogy", "3.2": "verbal_classification", "3.3": "codes_ciphers", "3.4": "word_manipulation", "3.5": "sentence_logic", "3.6": "letter_pattern", "3.7": "sentence_completion",
    "4.1": "rotation", "4.2": "reflection", "4.3": "cube_net", "4.4": "rotation_3d", "4.5": "position", "4.6": "transformation",
    "5.1": "figure_sequence", "5.2": "matrix", "5.3": "figure_odd_one_out", "5.4": "figure_analogy",
    "6.1": "working_backwards", "6.2": "guess_check", "6.3": "before_after", "6.4": "draw_diagram", "6.5": "make_list", "6.6": "pattern_application",
}
LEVEL_DIFF = {"Explore": "easy", "Think": "medium", "Challenge": "hard", "Master": "expert"}

RNG = random.Random(20260828)
USED_IDS = set(q["id"] for q in SEED["questions"])
_counter = 100


def next_id():
    global _counter
    while True:
        _counter += 1
        cand = "BA_P3_%04d" % _counter
        if cand not in USED_IDS:
            USED_IDS.add(cand)
            return cand


def decoys(pool, correct, n, rng):
    out = []
    p = [x for x in pool if x != correct]
    rng.shuffle(p)
    for x in p:
        if len(out) >= n:
            break
        if x not in out:
            out.append(x)
    # pad if pool too small
    pad = 1
    while len(out) < n:
        out.append("%s%d" % (correct, pad))
        pad += 1
    return out


# Shared figure vocabulary + transforms for pattern/visual generators (richer variety)
SHAPES = ["triangle", "square", "circle", "pentagon", "hexagon"]
COLOURS = ["red", "blue", "green"]
SIZES = ["small", "large"]


def _fig_desc(shape, colour=None, size=None, dot=False):
    parts = []
    if size:
        parts.append(size)
    if colour:
        parts.append(colour)
    parts.append(shape)
    if dot:
        parts.append("with a dot")
    return " ".join(parts)


def _apply(fig, attr):
    s, c, sz, d = fig
    if attr == "shape":
        return (SHAPES[(SHAPES.index(s) + 1) % len(SHAPES)], c, sz, d)
    if attr == "colour":
        return (s, COLOURS[(COLOURS.index(c) + 1) % len(COLOURS)], sz, d)
    if attr == "size":
        return (s, c, "large" if sz == "small" else "small", d)
    return (s, c, sz, not d)


def _rule_text(attr):
    return {
        "shape": "the shape changes to the next one in the cycle (triangle -> square -> circle -> pentagon -> hexagon -> triangle)",
        "colour": "the colour changes to the next one (red -> blue -> green -> red)",
        "size": "the size flips (small <-> large)",
        "dot": "a dot is added if missing, removed if present",
    }[attr]


def mk(domain, skill, level, question, correct, distractors, explanation, reasoning,
       tags, source, rng, visual_required=False, visual_spec=None):
    opts = [correct] + list(distractors[:3])
    # ensure 4 distinct
    seen = set()
    uniq = []
    for o in opts:
        if o not in seen:
            seen.add(o)
            uniq.append(o)
    while len(uniq) < 4:
        uniq.append("%s_%d" % (correct, len(uniq)))
    rng.shuffle(uniq)
    options = [{"id": chr(65 + i), "text": t} for i, t in enumerate(uniq)]
    answer = chr(65 + uniq.index(correct))
    qid = next_id()
    d = {
        "id": qid,
        "domain": domain,
        "skill": skill,
        "archetype": ARCH[skill],
        "level": level,
        "difficulty": LEVEL_DIFF[level],
        "question_type": "multiple_choice",
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "reasoning": reasoning,
        "visual_required": visual_required,
        "visual_spec": visual_spec,
        "image_path": ("brainactive/p3/%s.svg" % qid) if visual_required else None,
        "tags": tags,
        "qa_status": "ai_generated_not_approved",
        "provenance": {
            "basis": "BrainActive curriculum research (GEP GA / CogAT / UK 11+ VR-NVR archetypes)",
            "archetype": ARCH[skill],
            "source_inspiration": source,
            "original": True,
        },
    }
    return d


# =========================================================================
# NUMERICAL
# =========================================================================
def g_num_seq(rng):
    fam = rng.choice(["arith", "geo", "fib", "grow", "inter", "square"])
    if fam == "arith":
        a = rng.randint(2, 9); d = rng.randint(2, 9)
        k = rng.randint(4, 6); terms = [a + i * d for i in range(k)]
        ans = terms[-1] + d
        lvl = "Think"
        rule = "add %d each step" % d
        dec = decoys([str(terms[-1] + d + 1), str(terms[-1] - d), str(terms[-1] + 2 * d), str(terms[-2])], str(ans), 3, rng)
    elif fam == "geo":
        a = rng.randint(2, 5); r = rng.randint(2, 3)
        k = rng.randint(4, 5); terms = [a * (r ** i) for i in range(k)]
        ans = terms[-1] * r
        lvl = "Explore"
        rule = "multiply by %d" % r
        dec = decoys([str(terms[-1] + r), str(terms[-1] - a), str(terms[-2] * r), str(ans + 1)], str(ans), 3, rng)
    elif fam == "fib":
        a = rng.randint(1, 4); b = rng.randint(a + 1, a + 5)
        terms = [a, b]
        for _ in range(rng.randint(3, 5)):
            terms.append(terms[-1] + terms[-2])
        ans = terms[-1] + terms[-2]
        lvl = "Explore"
        rule = "each term is the sum of the two before it"
        dec = decoys([str(terms[-1] + terms[-2] + 1), str(terms[-1]), str(terms[-2]), str(ans + 2)], str(ans), 3, rng)
    elif fam == "grow":
        a = rng.randint(1, 5); gap = rng.randint(1, 4)
        terms = [a]; g = gap
        for _ in range(rng.randint(4, 6)):
            terms.append(terms[-1] + g); g += 1
        ans = terms[-1] + g
        lvl = "Think"
        rule = "the gap between terms grows by 1 each step"
        dec = decoys([str(terms[-1] + g - 1), str(terms[-1] + g + 1), str(terms[-1]), str(ans + 1)], str(ans), 3, rng)
    elif fam == "inter":
        a1 = rng.randint(1, 4); d1 = rng.randint(1, 3); a2 = rng.randint(2, 6); d2 = rng.randint(2, 4)
        seq = []; v1 = a1; v2 = a2
        for _ in range(4):
            seq.append(v1); seq.append(v2); v1 += d1; v2 += d2
        show = seq[:7]; ans = seq[7]
        lvl = "Think"
        rule = "two woven sequences: odd positions +%d, even positions +%d" % (d1, d2)
        dec = decoys([str(seq[6] + d1), str(seq[6] + d2), str(seq[5]), str(ans + 1)], str(ans), 3, rng)
        terms = show
    else:  # square
        n0 = rng.randint(1, 4); k = rng.randint(4, 5)
        terms = [(n0 + i) ** 2 for i in range(k)]
        ans = (n0 + k) ** 2
        lvl = "Think"
        rule = "the squares of %d, %d, %d, ..." % (n0, n0 + 1, n0 + 2)
        dec = decoys([str((n0 + k) ** 2 + 1), str((n0 + k - 1) ** 2), str(ans + 2), str(ans - 1)], str(ans), 3, rng)
    q = "Find the next number: " + ", ".join(str(t) for t in terms) + ", ___?"
    return mk("numerical_reasoning", "1.1", lvl, q, str(ans), dec,
              "The rule is: %s. So the next number is %s." % (rule, ans),
              "Finding the pattern in a number sequence.",
              ["p3", "high_ability", "numerical", "pattern"], "Deterministic generator 1.1 (%s)." % fam, rng)


def g_num_analogy(rng):
    fam = rng.choice(["add", "mul", "muladd", "mulsub", "square"])
    if fam == "add":
        a = rng.randint(2, 9); d = rng.randint(2, 9); b = a + d; c = rng.randint(2, 9); ans = c + d
        rule = "+%d" % d; lvl = "Explore"
    elif fam == "mul":
        a = rng.randint(2, 8); m = rng.randint(2, 4); b = a * m; c = rng.randint(2, 8); ans = c * m
        rule = "x%d" % m; lvl = "Explore"
    elif fam == "muladd":
        a = rng.randint(2, 8); m = rng.randint(2, 3); k = rng.randint(1, 5); b = a * m + k; c = rng.randint(2, 8); ans = c * m + k
        rule = "x%d then +%d" % (m, k); lvl = "Think"
    elif fam == "mulsub":
        a = rng.randint(2, 8); m = rng.randint(2, 3); k = rng.randint(1, 4); b = a * m - k; c = rng.randint(2, 8); ans = c * m - k
        rule = "x%d then -%d" % (m, k); lvl = "Think"
    else:
        a = rng.randint(2, 8); b = a * a; c = rng.randint(2, 8); ans = c * c
        rule = "square the number"; lvl = "Challenge"
    q = "%d is to %d as %d is to ___?" % (a, b, c)
    dec = decoys([str(c + (b - a)), str(c * 2), str(ans + (b - a)), str(ans - 1)], str(ans), 3, rng)
    return mk("numerical_reasoning", "1.2", lvl, q, str(ans), dec,
              "Relation: %s. %d -> %d, so %d -> %d." % (rule, a, b, c, ans),
              "Inferring a numerical relation and applying it.",
              ["p3", "high_ability", "numerical", "analogy"], "Deterministic generator 1.2.", rng)


def g_num_system(rng):
    # three shapes weights, ask heaviest/lightest
    a = rng.randint(2, 6); b = rng.randint(2, 6); c = rng.randint(2, 6)
    pairs = {"triangle": a, "square": b, "circle": c}
    # build three pair sums
    import itertools
    sh = ["triangle", "square", "circle"]
    combos = list(itertools.combinations(sh, 2))
    rng.shuffle(combos)
    s1, s2, s3 = combos[:3]
    v1 = pairs[s1[0]] + pairs[s1[1]]; v2 = pairs[s2[0]] + pairs[s2[1]]; v3 = pairs[s3[0]] + pairs[s3[1]]
    total = a + b + c
    # deduce each
    deduced = {s: total - (pairs[s1[0]] + pairs[s1[1]] + pairs[s2[0]] + pairs[s2[1]] + pairs[s3[0]] + pairs[s3[1]] - (a + b + c)) for s in sh}
    # simpler: each shape = total - sum of the other two via pairs; compute directly:
    w = {}
    # solve: we know three pair sums; sum all three = 2*(a+b+c) -> total=(v1+v2+v3)/2
    tot = (v1 + v2 + v3) // 2
    for s in sh:
        # find a pair not containing s
        other = [p for p in [s1, s2, s3] if s not in p][0]
        w[s] = tot - sum(pairs[x] for x in other)
    heaviest = max(w, key=w.get); lightest = min(w, key=w.get)
    ask = rng.choice(["heaviest", "lightest"])
    ans = heaviest if ask == "heaviest" else lightest
    q = "A %s and a %s together weigh %d. A %s and a %s together weigh %d. A %s and a %s together weigh %d. Which shape is %s?" % (
        s1[0], s1[1], v1, s2[0], s2[1], v2, s3[0], s3[1], v3, ask)
    dec = decoys([s for s in sh if s != ans], ans, 3, rng)
    return mk("numerical_reasoning", "1.3", "Think", q, ans, dec,
              "Add the three pair-weights: each shape counted twice = %d, so one of each = %d. The %s is %d, the %s is %d, the %s is %d; the %s is the %s." % (
                  v1 + v2 + v3, tot, sh[0], w[sh[0]], sh[1], w[sh[1]], sh[2], w[sh[2]], ask, ans),
              "Solving a small weight system by combining equations.",
              ["p3", "high_ability", "numerical", "deduction"], "Deterministic generator 1.3.", rng)


def g_num_chain(rng):
    names = rng.sample(["Ali", "Ben", "Cai", "Dan", "Ela", "Fox"], 3)
    base = rng.randint(8, 14)
    # chain: n0 base; build 3 people with offsets
    a, b, c = names
    off1 = rng.randint(2, 5); off2 = rng.randint(2, 5)
    # a has off1 more than b; b has off2 fewer than c -> c largest reference
    # set c = base; b = base - off2; a = b + off1
    cv = base; bv = base - off2; av = bv + off1
    vals = {c: cv, b: bv, a: av}
    top = max(vals, key=vals.get)
    q = "%s has %d more marbles than %s. %s has %d fewer than %s. %s has %d. Who has the most?" % (
        a, off1, b, b, off2, c, c, cv)
    dec = decoys([n for n in names if n != top], top, 3, rng)
    return mk("numerical_reasoning", "1.4", "Think", q, top, dec,
              "%s = %d. %s = %d - %d = %d. %s = %d + %d = %d. %s (%d) is the most." % (
                  c, cv, b, cv, off2, bv, a, bv, off1, av, top, av),
              "Chaining several comparisons into a full order.",
              ["p3", "high_ability", "numerical", "logic"], "Deterministic generator 1.4.", rng)


# =========================================================================
# LOGICAL
# =========================================================================
def g_log_order(rng):
    ent = rng.sample(["P", "Q", "R", "S", "T", "U"], 4)
    rng.shuffle(ent)
    # order[0] is fastest ... order[3] is slowest (the hidden true total order)
    order = list(ent)
    lvl = rng.choice(["Explore", "Think"])
    if lvl == "Explore":
        # two transitive clues over the first three -> shortest is fully determined
        a, b, c = order[0], order[1], order[2]
        q = "%s is taller than %s. %s is taller than %s. Who is the shortest?" % (a, b, b, c)
        ans = c
        dec = decoys([x for x in ent if x != c], c, 3, rng)
        return mk("logical_reasoning", "2.1", lvl, q, ans, dec,
                    "Taller order: %s > %s > %s, so %s is shortest." % (a, b, c, c),
                    "Building a linear order from transitive clues.",
                    ["p3", "high_ability", "logical", "ordering"], "Deterministic generator 2.1.", rng)
    else:
        # four runners, a fully-determined chain: a beats b, b beats c, c beats d -> a>b>c>d
        a, b, c, d = order[0], order[1], order[2], order[3]
        q = "Four runners race. %s beats %s. %s beats %s. %s beats %s. Order them from fastest to slowest." % (a, b, b, c, c, d)
        ans = ", ".join(order)
        dec = decoys([", ".join(rng.sample(order, len(order))) for _ in range(3)], ans, 3, rng)
        # ensure distractors differ
        dec = [x for x in dec if x != ans][:3]
        while len(dec) < 3:
            dec.append(", ".join(reversed(order)))
        return mk("logical_reasoning", "2.1", lvl, q, ans, dec,
                    "Chain the clues: %s beats %s, %s beats %s, %s beats %s, so %s > %s > %s > %s." % (
                        a, b, b, c, c, d, order[0], order[1], order[2], order[3]),
                    "Merging a fully-determined ordering chain.",
                    ["p3", "high_ability", "logical", "ordering"], "Deterministic generator 2.1.", rng)


def g_log_constraint(rng):
    people = rng.sample(["Ali", "Ben", "Cai", "Dee", "Eva"], 4)
    rng.shuffle(people)
    A, B, C, D = people[0], people[1], people[2], people[3]
    # Deterministic seating: A left end; B is next to A (seat 2); C at right end (seat 4);
    # remaining D is seat 3. Every seat is fixed by the clues.
    placement = [A, B, D, C]
    seat_labels = ["left end", "second from the left", "third from the left", "right end"]
    q = ("%s, %s, %s and %s sit in a row of four. %s is at the left end. "
         "%s sits next to %s. %s sits at the right end. " % (A, B, C, D, A, B, A, C))
    seat_idx = rng.randint(0, 3)
    ans = placement[seat_idx]
    q += "Who sits %s?" % seat_labels[seat_idx]
    dec = decoys([p for p in people if p != ans], ans, 3, rng)
    return mk("logical_reasoning", "2.2", "Think", q, ans, dec,
               "Seat 1 = %s (left end). %s sits next to %s, so seat 2 = %s. %s is at the right end "
               "(seat 4), so the only seat left for %s is seat 3. Therefore seat %d (%s) = %s." % (
                   A, B, A, B, C, D, seat_idx + 1, seat_labels[seat_idx], ans),
               "Placing fixed positions, then applying constraints to fix every seat.",
               ["p3", "high_ability", "logical", "constraint"], "Deterministic generator 2.2.", rng)


def g_log_cond(rng):
    if rng.random() < 0.5:
        n = rng.randint(11, 29)
        q = "If a number is even, it is coloured blue. The number %d is NOT blue. What can we conclude?" % n
        ans = "It is not even"
        dec = decoys(["It is even", "It is blue", "cannot tell"], ans, 3, rng)
        return mk("logical_reasoning", "2.3", "Think", q, ans, dec,
                    "Rule: even -> blue. %d is not blue, so by the contrapositive it is not even." % n,
                    "Using the contrapositive (must-be-true from a negation).",
                    ["p3", "high_ability", "logical", "deduction"], "Deterministic generator 2.3.", rng)
    else:
        q = "If it is hot, we swim. If we swim, we are happy. It is hot. What MUST be true?"
        ans = "We are happy"
        dec = decoys(["It is cold", "We do not swim", "We are sad", "We are outside"], ans, 3, rng)
        return mk("logical_reasoning", "2.3", "Challenge", q, ans, dec,
                   "Hot -> swim -> happy. Since it is hot, we swim and we are happy. The only MUST-be-true option is 'we are happy'.",
                   "Chaining two conditional rules to a conclusion.",
                   ["p3", "high_ability", "logical", "deduction"], "Deterministic generator 2.3.", rng)


def g_log_class(rng):
    # word odd-one-out by category
    cats = {
        "fruit": ["apple", "banana", "orange", "grape", "pear"],
        "animal": ["cat", "dog", "bird", "fish", "lion"],
        "colour": ["red", "blue", "green", "yellow", "pink"],
        "vehicle": ["car", "bus", "train", "boat", "plane"],
        "shape": ["circle", "square", "triangle", "rectangle", "oval"],
    }
    cat = rng.choice(list(cats))
    items = rng.sample(cats[cat], 3)
    out = rng.choice(["shoe", "spoon", "book", "clock", "key", "cup", "leaf", "table"])
    opts4 = items + [out]
    rng.shuffle(opts4)
    q = "Which word is the odd one out? " + "  ".join("%s %s" % (chr(65 + i), t) for i, t in enumerate(opts4))
    ans = out
    dec = decoys([t for t in opts4 if t != out], out, 3, rng)
    return mk("logical_reasoning", "2.4", "Think", q, ans, dec,
              "%s, %s and %s are all %s. %s does not belong to that group." % (items[0], items[1], items[2], cat, out),
              "Finding the category three share and the odd one.",
              ["p3", "high_ability", "logical", "classification"], "Deterministic generator 2.4.", rng)


def g_log_syll(rng):
    if rng.random() < 0.5:
        q = "All cats are animals. All animals are living things. Which MUST be true?"
        ans = "All cats are living things"
        dec = decoys(["All living things are cats", "All animals are cats", "Cats are not living"], ans, 3, rng)
        return mk("logical_reasoning", "2.5", "Think", q, ans, dec,
                   "Every cat is an animal and every animal is living, so every cat is living. The others reverse the rule.",
                   "Chaining set inclusions (transitive).",
                   ["p3", "high_ability", "logical", "syllogism"], "Deterministic generator 2.5.", rng)
    else:
        q = "Some squares are red. All red things are small. Which MUST be true?"
        ans = "Some squares are small"
        dec = decoys(["All squares are small", "All small things are squares", "No squares are small"], ans, 3, rng)
        return mk("logical_reasoning", "2.5", "Challenge", q, ans, dec,
                   "The red squares are squares AND red; all red things are small, so those squares are small. Thus SOME squares are small.",
                   "Chaining a particular with a universal quantifier without over-generalising.",
                   ["p3", "high_ability", "logical", "syllogism"], "Deterministic generator 2.5.", rng)


# =========================================================================
# VERBAL
# =========================================================================
ANALOGY_TRIPLES = [
    ("function", [("knife", "cut"), ("pen", "write"), ("brush", "paint"), ("key", "open"), ("spoon", "eat"), ("phone", "call")]),
    ("part-whole", [("leaf", "tree"), ("page", "book"), ("petal", "flower"), ("wheel", "car"), ("brick", "wall")]),
    ("category", [("red", "colour"), ("apple", "fruit"), ("cat", "animal"), ("circle", "shape"), ("car", "vehicle")]),
    ("antonym", [("hot", "cold"), ("big", "small"), ("happy", "sad"), ("open", "shut"), ("light", "dark")]),
    ("animal-sound", [("dog", "bark"), ("cat", "meow"), ("cow", "moo"), ("sheep", "baa"), ("duck", "quack")]),
    ("tool-action", [("ruler", "measure"), ("hammer", "hit"), ("scissors", "cut"), ("fork", "lift"), ("comb", "brush")]),
    ("object-location", [("fish", "water"), ("bird", "sky"), ("cow", "farm"), ("dog", "house"), ("star", "space")]),
]
VERB_CLASS_POOL = {
    "fruit": ["apple", "banana", "orange", "grape", "pear", "mango"],
    "animal": ["cat", "dog", "bird", "fish", "lion", "bear"],
    "colour": ["red", "blue", "green", "yellow", "pink", "brown"],
    "vehicle": ["car", "bus", "train", "boat", "plane", "bike"],
    "shape": ["circle", "square", "triangle", "rectangle", "oval", "diamond"],
}


def g_ver_analogy(rng):
    rel, pairs = rng.choice(ANALOGY_TRIPLES)
    rng.shuffle(pairs)
    a, b = pairs[0]
    c, d = pairs[1]
    q = "%s is to %s as %s is to ___?" % (a, b, c)
    dec = decoys([x for x in ["eat", "run", "sit", "sleep", "read", "jump", "sing", "walk"] if x != d], d, 3, rng)
    # make distractors relation-plausible: pick words from other relations
    alt = rng.choice([p[1] for r, ps in ANALOGY_TRIPLES if r != rel for p in ps if p[1] != d])
    if alt:
        dec[0] = alt
    return mk("verbal_reasoning", "3.1", "Think", q, d, dec,
              "Relation: %s. %s : %s, so %s : %s." % (rel, a, b, c, d),
              "Finding a relation (type: %s) and applying it." % rel,
              ["p3", "high_ability", "verbal", "analogy"], "Research-derived verbal analogy (GEP GA archetype).", rng)


def g_ver_class(rng):
    cat = rng.choice(list(VERB_CLASS_POOL))
    items = rng.sample(VERB_CLASS_POOL[cat], 3)
    out = rng.choice(["shoe", "spoon", "book", "clock", "key", "cup", "leaf", "chair", "table"])
    opts4 = items + [out]
    rng.shuffle(opts4)
    q = "Which word is the odd one out? " + "  ".join("%s %s" % (chr(65 + i), t) for i, t in enumerate(opts4))
    ans = out
    dec = decoys([t for t in opts4 if t != out], out, 3, rng)
    return mk("verbal_reasoning", "3.2", "Think", q, ans, dec,
              "%s, %s and %s are all %s. %s does not belong." % (items[0], items[1], items[2], cat, out),
              "Grouping words by meaning (semantic category).",
              ["p3", "high_ability", "verbal", "odd_one_out"], "Research-derived verbal classification (CogAT archetype).", rng)


def g_ver_code(rng):
    fam = rng.choice(["shift_enc", "shift_dec", "square"])
    if fam == "shift_enc":
        word = rng.choice(["CAT", "DOG", "SUN", "MAP", "BOX", "KEY", "PAN"])
        k = rng.randint(1, 3)
        enc = "".join(chr((ord(ch) - 65 + k) % 26 + 65) for ch in word)
        q = "In a code, each letter moves forward %d (A->%s...). How is %s written?" % (k, chr(65 + k), word)
        dec = decoys([enc[:-1] + chr((ord(word[-1]) - 65 - k) % 26 + 65), chr((ord(word[0]) - 65 + k + 1) % 26 + 65) + enc[1:], "X" + enc[1:], enc + "Z"], enc, 3, rng)
        return mk("verbal_reasoning", "3.3", "Explore", q, enc, dec,
                  "Shift each letter forward %d: %s -> %s." % (k, word, enc),
                  "Applying a simple letter shift.",
                  ["p3", "high_ability", "verbal", "cipher"], "Research-derived code (GEP decoding archetype).", rng)
    elif fam == "shift_dec":
        word = rng.choice(["CODE", "BLUE", "TIME", "STAR", "MOON", "FISH"])
        k = rng.randint(1, 3)
        code = "".join(chr((ord(ch) - 65 + k) % 26 + 65) for ch in word)
        q = "In a code, each letter means the letter %d steps before it (so the code letter is ahead). The code word is %s. What real word does it stand for?" % (k, code)
        dec = decoys([word[:-1] + "X", "Q" + word[1:], word + "S", "B" + word[1:]], word, 3, rng)
        return mk("verbal_reasoning", "3.3", "Think", q, word, dec,
                  "Each code letter is %d ahead, so shift back %d: %s -> %s." % (k, k, code, word),
                  "Reversing a letter shift to decode.",
                  ["p3", "high_ability", "verbal", "cipher"], "Research-derived code (GEP decoding archetype).", rng)
    else:
        letter = rng.choice(["E", "F", "G", "H", "D"])
        pos = ord(letter) - 64
        val = pos * pos
        q = "In a code, a letter is worth the SQUARE of its place (A=1, B=4, C=9...). Which letter is worth %d?" % val
        dec = decoys([chr(65 + pos + rng.randint(1, 3)), chr(65 + pos - 1 if pos > 1 else 2), "Y", "S"], letter, 3, rng)
        return mk("verbal_reasoning", "3.3", "Think", q, letter, dec,
                  "%d = %d squared, and %s is the %dth letter." % (val, pos, letter, pos),
                  "Discovering a square rule then mapping to a letter position.",
                  ["p3", "high_ability", "verbal", "cipher"], "Research-derived code (GEP letter-number archetype).", rng)


def g_ver_wordmanip(rng):
    fam = rng.choice(["move_first", "reverse"])
    if fam == "move_first":
        word = rng.choice(["TRAIN", "PLANT", "BREAD", "STONE", "CHALK", "FLAME"])
        ans = word[1:] + word[0]
        q = "In a code, CAT becomes ATC. The rule moves the FIRST letter to the END. What does %s become?" % word
        dec = decoys([word[-1] + word[:-1], word[1:] + word[0][0] + word[0], word[::-1], word + word[0]], ans, 3, rng)
        return mk("verbal_reasoning", "3.4", "Think", q, ans, dec,
                  "Move the first letter of %s to the end: %s." % (word, ans),
                  "Discovering a word-transformation rule and applying it.",
                  ["p3", "high_ability", "verbal", "word_manipulation"], "Research-derived word manipulation (GEP anagram archetype).", rng)
    else:
        word = rng.choice(["RATE", "TEAR", "STAR", "LIST", "PORT", "LANE"])
        ans = word[::-1]
        q = "In a code, the letters are reversed (CAT -> TAC). What does %s become?" % word
        dec = decoys([word[1:] + word[0], word[::-1][1:] + word[0], word + "X", word[:-1]], ans, 3, rng)
        return mk("verbal_reasoning", "3.4", "Think", q, ans, dec,
                  "Reverse the letters of %s: %s." % (word, ans),
                  "Discovering a reversal rule and applying it.",
                  ["p3", "high_ability", "verbal", "word_manipulation"], "Research-derived word manipulation.", rng)


def g_ver_sentlogic(rng):
    names = rng.sample(["Ali", "Ben", "Cai"], 3)
    a, b, c = names
    # build a 3-clue assignment
    acts = ["swimming", "cycling", "running"]
    rng.shuffle(acts)
    assign = {a: acts[0], b: acts[1], c: acts[2]}
    verb = {"swimming": "swims", "cycling": "cycles", "running": "runs"}
    base_verb = {"swimming": "swim", "cycling": "cycle", "running": "run"}
    clues = [f"{a} {verb[assign[a]]}.", f"{b} {verb[assign[b]]}.", f"{c} does not {base_verb[assign[c]]}."]
    # ask who does the remaining activity
    remaining = [x for x in acts if x not in [assign[a], assign[b]]][0]
    ans = c if assign[c] == remaining else [n for n in names if assign[n] == remaining][0]
    q = "Three friends each do a different activity: swimming, cycling, or running. " + " ".join(clues) + " Who is " + remaining + "?"
    dec = decoys([n for n in names if n != ans], ans, 3, rng)
    return mk("verbal_reasoning", "3.5", "Challenge", q, ans, dec,
              "From the clues, %s=%s and %s=%s, so %s=%s; therefore %s is %s." % (a, assign[a], b, assign[b], c, assign[c], ans, remaining),
              "Combining three clues into a unique assignment.",
              ["p3", "high_ability", "verbal", "logic"], "Research-derived verbal deduction (GEP logic archetype).", rng)


def g_ver_letterpat(rng):
    starts = {ch: i + 1 for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    # growing gap letter series
    start = rng.randint(0, 21)
    gaps = rng.choice([[2, 2, 2], [1, 2, 3], [3, 3, 3], [2, 3, 4]])
    seq = [start]
    for g in gaps:
        seq.append(seq[-1] + g)
    seq = [s for s in seq if 0 <= s < 26]
    if len(seq) < 4:
        return None
    ans = seq[-1] + gaps[-1]
    if ans >= 26:
        ans = seq[-1] - gaps[-1]
    letters = [chr(65 + s) for s in seq]
    q = "A letter pattern goes: " + ", ".join(letters) + ", ___. The gap grows by 1 each step. What comes next?"
    dec = decoys([chr(65 + (seq[-1] + gaps[-1] + 1 if ans < 26 else seq[-1] - 1)),
                  chr(65 + max(0, seq[-1] - gaps[-1])), chr(65 + min(25, seq[-1] + gaps[-1] + 2)), "Z"], chr(65 + ans), 3, rng)
    return mk("verbal_reasoning", "3.6", "Think", q, chr(65 + ans), dec,
              "Positions: " + ", ".join(str(s + 1) for s in seq) + ". Next gap is +%d -> %s." % (gaps[-1], chr(65 + ans)),
              "Finding a changing rule in a letter series.",
              ["p3", "high_ability", "verbal", "letter_pattern"], "Research-derived letter pattern (UK 11+ archetype).", rng)


def g_ver_cloze(rng):
    items = [
        ("The ground was wet, so we took our ___?", "umbrella", ["shoe", "book", "apple"]),
        ("It was dark, so we turned on the ___?", "light", ["door", "book", "cup"]),
        ("She was cold, so she put on a ___?", "coat", ["hat", "book", "spoon"]),
        ("He was hungry, so he ate a ___?", "sandwich", ["ball", "book", "key"]),
        ("It was raining, so we used a ___?", "umbrella", ["shoe", "bag", "cup"]),
        ("The sun was bright, so she wore ___?", "sunglasses", ["shoe", "book", "hat"]),
        ("We were lost, so we read a ___?", "map", ["book", "cup", "key"]),
        ("The plant was dry, so we gave it ___?", "water", ["sun", "book", "stone"]),
        ("He was tired, so he went to ___?", "sleep", ["eat", "read", "run"]),
        ("It was noisy, so she covered her ___?", "ears", ["eyes", "book", "hand"]),
    ]
    q, ans, dec = rng.choice(items)
    return mk("verbal_reasoning", "3.7", "Explore", q, ans, dec,
              "The cause (wet / dark / cold / ...) leads to the effect; the fitting word is '%s'." % ans,
              "Using sentence context (cause and effect) to pick the fitting word.",
              ["p3", "high_ability", "verbal", "sentence_completion", "vocab_dependent"], "Capped B-type (vocabulary + reasoning).", rng)


# =========================================================================
# VISUAL (4.x)
# =========================================================================
DIRS = ["up", "right", "down", "left"]


def _rot(start, steps):
    order = {"up": 0, "right": 1, "down": 2, "left": 3}
    name = {0: "up", 1: "right", 2: "down", 3: "left"}
    return name[(order[start] + steps) % 4]


def g_vis_rot(rng):
    start = rng.choice(DIRS); steps = rng.choice([1, 2, 3])
    ans = _rot(start, steps)
    q = "An arrow points %s. It is rotated 90 degrees clockwise %s. Which way does it point now?" % (
        start, "%d times" % steps if steps > 1 else "once")
    dec = decoys([d for d in DIRS if d != ans], ans, 3, rng)
    return mk("visual_spatial", "4.1", "Think" if steps > 1 else "Explore", q, ans, dec,
              "Each 90-degree clockwise turn moves the arrow one step: %s -> ... -> %s." % (start, ans),
              "Mentally rotating a shape.",
              ["p3", "high_ability", "spatial", "rotation"], "Deterministic visual 4.1.", rng,
              visual_required=True, visual_spec={"type": "rotation_sequence", "start": start, "steps": steps})


def g_vis_reflect(rng):
    pairs = [("p", "q"), ("d", "b"), ("b", "d"), ("q", "p")]
    s, r = rng.choice(pairs)
    q = "The letter '%s' is reflected in a vertical mirror (left-right flip). Which letter does the reflection look like?" % s
    dec = decoys([x for x in ["p", "q", "b", "d"] if x != r], r, 3, rng)
    return mk("visual_spatial", "4.2", "Think", q, r, dec,
              "A vertical mirror flips '%s' left-right so it looks like '%s'." % (s, r),
              "Mirror reflection across a vertical axis.",
              ["p3", "high_ability", "spatial", "reflection"], "Deterministic visual 4.2.", rng,
              visual_required=True, visual_spec={"type": "reflection", "axis": "vertical", "source": s, "result": r})


def g_vis_net(rng):
    letters = rng.sample(["A", "B", "C", "D", "E", "F"], 6)
    front = letters[0]; up = letters[1]; down = letters[2]; left = letters[3]; right = letters[4]; back = letters[5]
    layout = [["", up, ""], [left, front, right], ["", down, ""], ["", back, ""]]
    q = "A cube net: centre %s, with %s above, %s below, %s left, %s right, and %s below %s. Folded with %s as front, which square is the BACK face?" % (
        front, up, down, left, right, back, down, front)
    ans = back
    dec = decoys([x for x in letters if x != back], back, 3, rng)
    return mk("visual_spatial", "4.3", "Think", q, ans, dec,
              "Fold %s as front: %s=left, %s=right, %s=top, %s=bottom, and %s folds to the back. Back = %s." % (front, left, right, up, down, back, back),
              "Folding a net to find the opposite face.",
              ["p3", "high_ability", "spatial", "net"], "Deterministic visual 4.3.", rng,
              visual_required=True, visual_spec={"type": "cube_net", "layout": layout, "front": front, "back": back})


def g_vis_3d(rng):
    top_face = rng.choice(["dot", "star", "cross"])
    side_face = rng.choice([x for x in ["dot", "star", "cross"] if x != top_face])
    rot = rng.choice(["left 90", "right 90"])
    after = "right" if rot == "right 90" else "left"
    q = "A cube has a %s on its TOP face and a %s on its FRONT face. You rotate it 90 degrees to the %s around the vertical axis. Where is the %s now?" % (
        top_face, side_face, "right" if rot == "right 90" else "left", side_face)
    ans = after
    dec = decoys(["top", "front", "right" if after == "left" else "left"], after, 3, rng)
    return mk("visual_spatial", "4.4", "Challenge", q, ans, dec,
              "Rotating around the vertical axis to the %s turns the front face to the %s; the top stays on top." % ("right" if rot == "right 90" else "left", after),
              "3D rotation around the vertical axis.",
              ["p3", "high_ability", "spatial", "rotation", "challenge"], "Deterministic visual 4.4.", rng,
              visual_required=True, visual_spec={"type": "rotation_3d", "axis": "vertical", "marks": {"top": top_face, "front": side_face}, "rotation": rot, star_after: after} if False else
              {"type": "rotation_3d", "axis": "vertical", "marks": {"top": top_face, "front": side_face}, "rotation": rot, "star_after": after})


def g_vis_pos(rng):
    # grid positions described in text
    entities = rng.sample(["star", "circle", "square", "triangle"], 3)
    rng.shuffle(entities)
    a, b, c = entities
    q = "On a 3-by-3 grid: the %s is in the top-left square. The %s is directly below the %s. The %s is to the right of the %s. Where is the %s?" % (a, b, a, c, b, c)
    ans = "middle row, middle column"
    dec = decoys(["top-left", "bottom-right", "top-right", "bottom-left"], ans, 3, rng)
    return mk("visual_spatial", "4.5", "Explore" if rng.random() < 0.5 else "Think", q, ans, dec,
              "Top-left row1 col1; %s below = row2 col1; %s right of it = row2 col2 (middle row, middle column)." % (b, c),
              "Tracking grid positions from relative clues.",
              ["p3", "high_ability", "spatial", "position"], "Authored 4.5 (grid).", rng)


def g_vis_transform(rng):
    shapes = ["triangle", "square", "pentagon", "hexagon"]
    start = rng.randint(0, 2)
    seq = []
    for i in range(4):
        sh = shapes[(start + i) % len(shapes)]
        col = "red" if i % 2 == 0 else "blue"
        seq.append("%s %s(%d)" % (sh, col, 3 + i))
    ans = seq[-1]
    q = "Each step the shape gains one side AND its colour alternates red, blue, red... " + " -> ".join(seq[:-1]) + " -> ?"
    dec = decoys(["%s blue(%d)" % (shapes[(start + 3) % len(shapes)], 7),
                  "%s red(%d)" % (shapes[(start + 3) % len(shapes)], 6),
                  "%s blue(%d)" % (shapes[(start + 4) % len(shapes)], 6),
                  "circle"], ans, 3, rng)
    return mk("visual_spatial", "4.6", "Think", q, ans, dec,
              "Two rules: sides go +1 and colour alternates red/blue. Next = %s." % ans,
              "Continuing a two-feature transformation.",
              ["p3", "high_ability", "spatial", "transformation"], "Deterministic visual 4.6.", rng,
              visual_required=True, visual_spec={"type": "shape_transformation", "rule": "add one side AND alternate colour red/blue", "sequence": seq})


# =========================================================================
# PATTERN (5.x)
# =========================================================================
def g_pat_countseq(rng):
    fam = rng.choice(["double", "add"])
    if fam == "double":
        a = rng.randint(1, 4); k = rng.randint(4, 5); counts = [a * (2 ** i) for i in range(k)]
        ans = counts[-1] * 2
        rule = "double each group"
    else:
        a = rng.randint(1, 4); d = rng.randint(1, 3); k = rng.randint(4, 5); counts = [a + i * d for i in range(k)]
        ans = counts[-1] + d
        rule = "add %d each group" % d
    q = "Groups of dots: " + ", ".join(str(c) for c in counts) + ". How many dots come next?"
    dec = decoys([str(counts[-1] + d if fam != "double" else counts[-1] * 2 + 1), str(counts[-1]), str(counts[-2]), str(ans + 1)], str(ans), 3, rng)
    return mk("pattern_abstract", "5.1", "Explore" if fam == "double" else "Think", q, str(ans), dec,
              "Rule: %s. Next group = %d." % (rule, ans),
              "Continuing a count sequence.",
              ["p3", "high_ability", "pattern", "sequence"], "Deterministic visual 5.1.", rng,
              visual_required=True, visual_spec={"type": "count_sequence", "counts": counts, "next": ans})


def g_pat_matrix2(rng):
    attr = rng.choice(["shape", "colour", "size", "dot"])
    X = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    Y = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    fX = _apply(X, attr)
    fY = _apply(Y, attr)
    tl, tr, bl, br = _fig_desc(*X), _fig_desc(*fX), _fig_desc(*Y), _fig_desc(*fY)
    q = "Top-left is a %s. Top-right is the changed version. Bottom-left is a %s. Following the same change, what should the bottom-right be?" % (tl, bl)
    ans = br
    rule = _rule_text(attr)
    cells = [["a %s" % tl, "a %s" % tr], ["a %s" % bl, "?"]]
    dec = decoys([tl, tr, bl], ans, 3, rng)
    return mk("pattern_abstract", "5.2", "Explore" if attr in ("size", "dot") else "Think", q, ans, dec,
              "Rule across the row: %s. Apply to bottom-left -> %s." % (rule, ans),
              "Mapping a transformation across a 2x2 matrix.",
              ["p3", "high_ability", "pattern", "matrix"], "Deterministic visual 5.2.", rng,
              visual_required=True, visual_spec={"type": "analogy_matrix", "rows": 2, "cols": 2, "rule": rule, "cells": cells})


def g_pat_matrix3(rng):
    attrs = ["shape", "colour", "size", "dot"]
    row_attr = rng.choice(attrs)
    col_attr = rng.choice(attrs)
    while col_attr == row_attr:
        col_attr = rng.choice(attrs)
    base = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    full = [[None] * 3 for _ in range(3)]
    for r in range(3):
        for c in range(3):
            f = base
            for _ in range(r):
                f = _apply(f, row_attr)
            for _ in range(c):
                f = _apply(f, col_attr)
            full[r][c] = f
    display = [[_fig_desc(*full[r][c]) for c in range(3)] for r in range(3)]
    display[2][2] = "?"
    ans = _fig_desc(*full[2][2])
    q = "Complete the 3x3 matrix. DOWN each column: %s. ACROSS each row: %s. The bottom-right cell is ___?" % (
        _rule_text(col_attr), _rule_text(row_attr))
    dec = decoys([display[2][1], display[1][2], display[0][2]], ans, 3, rng)
    return mk("pattern_abstract", "5.2", "Think" if (row_attr in ("size", "dot") and col_attr in ("size", "dot")) else "Challenge",
              q, ans, dec,
              "Down the column %s; across the row %s. Bottom-right = %s." % (_rule_text(col_attr), _rule_text(row_attr), ans),
              "Completing a 3x3 matrix with row and column rules.",
              ["p3", "high_ability", "pattern", "matrix"], "Deterministic visual 5.2.", rng,
              visual_required=True, visual_spec={"type": "matrix_3x3", "cells": display, "col_rule": _rule_text(col_attr),
                 "row_rule": _rule_text(row_attr), "answer": ans})


def g_pat_odd(rng):
    dims = ["shape", "colour", "size", "dot"]
    dim = rng.choice(dims)
    base = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    odd = _apply(base, dim)
    items = [base, base, base, odd]
    rng.shuffle(items)
    ans = chr(65 + items.index(odd))
    descs = [_fig_desc(*it) for it in items]
    q = "Four figures: A %s, B %s, C %s, D %s. Which does not belong?" % tuple(descs)
    cands = [L for L in "ABCD" if L != ans]
    dec = decoys(cands, ans, 3, rng)
    return mk("pattern_abstract", "5.3", "Explore" if dim in ("size", "dot") else "Think", q, ans, dec,
              "Three of the four share the same %s; the odd one is %s." % (dim, ans),
              "Odd-one-out by %s." % dim,
              ["p3", "high_ability", "pattern", "odd_one_out"], "Deterministic visual 5.3.", rng,
              visual_required=True, visual_spec={"type": "odd_one_out", "dimension": dim, "items": [
                  {"id": L, "desc": d} for L, d in zip("ABCD", descs)]})


def g_pat_analogy(rng):
    attr = rng.choice(["shape", "colour", "size", "dot"])
    X = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    fX = _apply(X, attr)
    Y = (rng.choice(SHAPES), rng.choice(COLOURS), rng.choice(SIZES), rng.choice([True, False]))
    fY = _apply(Y, attr)
    q = "A %s changes into a %s (one attribute changes). Using the same change, a %s changes into a ___?" % (
        _fig_desc(*X), _fig_desc(*fX), _fig_desc(*Y))
    ans = _fig_desc(*fY)
    rule = _rule_text(attr)
    dec = decoys([_fig_desc(*X), _fig_desc(*fX), _fig_desc(*Y)], ans, 3, rng)
    return mk("pattern_abstract", "5.4", "Explore" if attr in ("size", "dot") else "Think", q, ans, dec,
              "Rule: %s. Apply to the second pair -> %s." % (rule, ans),
              "Mapping a transformation in a figure analogy.",
              ["p3", "high_ability", "pattern", "analogy"], "Deterministic visual 5.4.", rng,
              visual_required=True, visual_spec={"type": "shape_analogy", "rule": rule,
                 "pair1": {"%s" % _fig_desc(*X): _fig_desc(*fX)}, "pair2": {"%s" % _fig_desc(*Y): "?"}})


# =========================================================================
# PROBLEM SOLVING (6.x)
# =========================================================================
def g_ps_wb(rng):
    ops = rng.randint(2, 3)
    start = rng.randint(3, 9)
    val = start
    steps = []
    for _ in range(ops):
        if rng.random() < 0.5:
            k = rng.randint(2, 5); val = val + k; steps.append(("+", k))
        else:
            k = rng.randint(2, 4); val = val * k; steps.append(("x", k))
    result = val
    # reverse
    rev = result
    desc = []
    for op, k in reversed(steps):
        if op == "+":
            rev = rev - k; desc.append("before adding %d there were %d" % (k, rev))
        else:
            rev = rev // k; desc.append("before multiplying by %d it was %d" % (k, rev))
    q = "A number is changed by: " + "; ".join("%s %d" % s for s in steps) + ". The final result is %d. What was the starting number? Check by going forward." % result
    ans = rev
    dec = decoys([rev + 1, rev - 1, rev + 2, rev * 2], str(ans) if False else str(ans), 3, rng)
    return mk("problem_solving", "6.1", "Challenge" if ops == 3 else "Think", q, str(ans), dec,
              "Work backwards: " + "; ".join(desc) + ". Starting number = %d." % ans,
              "Working backwards through the steps and verifying.",
              ["p3", "high_ability", "heuristics", "working_backwards"], "Authored 6.1.", rng)


def g_ps_gc(rng):
    fives = rng.randint(1, 4); twos = 7 - fives
    # value check: 5*fives + 2*twos == 23? randomise target
    total_coins = rng.randint(6, 9)
    target = rng.randint(15, 30)
    # find a solution
    sol5 = None
    for f in range(0, total_coins + 1):
        t = total_coins - f
        if 5 * f + 2 * t == target:
            sol5 = f; break
    if sol5 is None:
        return None
    q = "Some coins are 2-dollar and some are 5-dollar. There are %d coins in total and they make %d dollars. How many 5-dollar coins are there?" % (total_coins, target)
    ans = sol5
    dec = decoys([sol5 + 1, sol5 - 1, sol5 + 2, 0], str(ans), 3, rng)
    return mk("problem_solving", "6.2", "Think", q, str(ans), dec,
              "Try %d five-dollar coins (= %d) and %d two-dollar coins (= %d). Total %d coins, %d dollars. Fits, so %d five-dollar coins." % (
                  sol5, 5 * sol5, total_coins - sol5, 2 * (total_coins - sol5), total_coins, target, sol5),
              "Systematic guess-and-check across a few cases.",
              ["p3", "high_ability", "heuristics", "guess_check"], "Authored 6.2.", rng)


def g_ps_ba(rng):
    lead = rng.randint(2, 5); move = rng.randint(1, 3)
    a = rng.randint(5, 12)
    unit = "sticker" if move == 1 else "stickers"
    q = "%s has %d more stickers than %s. %s gives %s %d %s. Now who has more stickers, and by how many?" % (
        "Amy", lead, "Ben", "Amy", "Ben", move, unit)
    gap = lead - 2 * move
    if gap > 0:
        ans = "Amy, by %d" % gap
    elif gap < 0:
        ans = "Ben, by %d" % (-gap)
    else:
        ans = "They are equal"
    dec = decoys(["Ben, by %d" % lead, "Amy, by %d" % (lead + move), "They are equal", "Ben, by 1"], ans, 3, rng)
    return mk("problem_solving", "6.3", "Think", q, ans, dec,
              "Originally %s leads by %d. Giving %d reduces the gap by %d (2 x %d), so the gap is now %d." % ("Amy", lead, move, 2 * move, move, gap),
              "Constant-difference under a transfer.",
              ["p3", "high_ability", "heuristics", "before_after"], "Authored 6.3.", rng)


def g_ps_patternapp(rng):
    # machine rule x3+1 applied to a far input
    n = rng.randint(7, 12)
    ans = n * 3 + 1
    q = "A machine uses this rule: 1 -> 4, 2 -> 7, 3 -> 10. What should %d become?" % n
    dec = decoys([str(n * 3), str(n * 3 - 1), str(n * 3 + 2), str(ans + 5)], str(ans), 3, rng)
    return mk("problem_solving", "6.6", "Explore", q, str(ans), dec,
              "Each output is the input x 3 + 1. So %d -> %d x 3 + 1 = %d." % (n, n, ans),
              "Discovering a rule, then applying it to a far case.",
              ["p3", "high_ability", "heuristics", "pattern_application"], "Authored 6.6.", rng)


def g_ps_draw(rng):
    n = rng.randint(4, 7)
    gap = rng.randint(2, 3)
    ans = (n - 1) * gap
    q = "%d trees are planted in a straight line, %d metres apart. How long is the row from the first tree to the last tree?" % (n, gap)
    dec = decoys([str(n * gap), str(n), str(ans + gap), str(ans - 1)], str(ans), 3, rng)
    return mk("problem_solving", "6.4", "Think", q, str(ans), dec,
              "Draw a diagram: %d trees have %d gaps between them. %d x %d = %d m." % (n, n - 1, n - 1, gap, ans),
              "Drawing a diagram to count the gaps, not the objects.",
              ["p3", "high_ability", "heuristics", "draw_diagram"], "Authored 6.4.", rng)


def g_ps_list(rng):
    letters = ["A", "B", "C"]
    rng.shuffle(letters)
    n = rng.choice([2, 3])
    L = letters[:n]
    total = len(L) ** len(L)
    # build list
    import itertools
    items = ["".join(p) for p in itertools.product(L, repeat=len(L))]
    q = "How many %d-letter codes can you make using the letters %s if you may repeat a letter?" % (len(L), ", ".join(L))
    ans = total
    dec = decoys([len(L) * (len(L) - 1), total + 1, total - 1, len(L)], str(ans), 3, rng)
    return mk("problem_solving", "6.5", "Think", q, str(ans), dec,
              "List them: " + ", ".join(items) + " = %d codes (%d choices for each of %d positions)." % (total, len(L), len(L)),
              "Making an organised list of all possibilities.",
              ["p3", "high_ability", "heuristics", "make_list"], "Authored 6.5.", rng)


# =========================================================================
# MASTER-TIER generators (expert: child must decide HOW to solve)
# =========================================================================
def g_num_master(rng):
    a = rng.randint(1, 4)
    add = rng.randint(2, 4)
    mul = rng.choice([2, 3])
    seq = [a]
    cur = a
    for i in range(6):
        if i % 2 == 0:
            cur += add
        else:
            cur *= mul
        seq.append(cur)
    show = seq[:6]
    ans = seq[6]
    q = "Find the next number: " + ", ".join(str(x) for x in show) + ", ___?"
    rule = "alternating rule: add %d, then multiply by %d, repeat" % (add, mul)
    dec = decoys([str(ans + add), str(ans * mul), str(seq[5]), str(ans - 1)], str(ans), 3, rng)
    return mk("numerical_reasoning", "1.1", "Master", q, str(ans), dec,
              "Rule: %s. The 7th term = %s." % (rule, ans),
              "Two-rule alternating number sequence (expert).",
              ["p3", "high_ability", "numerical", "pattern", "master"], "Authored 1.1 master.", rng)


def g_ps_master(rng):
    ops = rng.randint(2, 3)
    start = rng.randint(2, 6)
    val = start
    steps = []
    for _ in range(ops):
        if rng.random() < 0.5:
            k = rng.randint(2, 5)
            val += k
            steps.append(("+", k))
        else:
            k = rng.randint(2, 3)
            val *= k
            steps.append(("x", k))
    result = val
    rev = result
    desc = []
    for op, k in reversed(steps):
        if op == "+":
            rev -= k
            desc.append("before adding %d there were %d" % (k, rev))
        else:
            rev //= k
            desc.append("before multiplying by %d it was %d" % (k, rev))
    q = "A number is changed by: " + "; ".join("%s %d" % s for s in steps) + ". The final result is %d. What was the starting number?" % result
    ans = rev
    dec = decoys([rev + 1, rev - 1, rev + 2, rev * 2], str(ans), 3, rng)
    return mk("problem_solving", "6.1", "Master", q, str(ans), dec,
              "Work backwards: " + "; ".join(desc) + ". Starting number = %d." % ans,
              "Working backwards through several steps (expert).",
              ["p3", "high_ability", "heuristics", "working_backwards", "master"], "Authored 6.1 master.", rng)


def g_log_master(rng):
    situ = rng.choice(["sunny", "windy", "calm"])
    if situ == "sunny":
        ans, rule = "park", "if sunny then park"
    elif situ == "windy":
        ans, rule = "library", "if not sunny and windy then library"
    else:
        ans, rule = "home", "otherwise stay home"
    q = ("Rules: (1) If it is sunny, go to the park. (2) If it is NOT sunny AND it is windy, go to the library. "
         "(3) Otherwise, stay home. Today it is %s. Where do you go?" % situ)
    dec = decoys(["park", "library", "home", "visit a friend"], ans, 3, rng)
    return mk("logical_reasoning", "2.3", "Master", q, ans, dec,
              "Apply rules in order: %s. Outcome = %s." % (rule, ans),
              "Chained conditional reasoning (expert).",
              ["p3", "high_ability", "logic", "conditional", "master"], "Authored 2.3 master.", rng)


def g_ver_master(rng):
    shift = rng.randint(1, 3)
    word = rng.choice(["CAT", "DOG", "SUN", "MAP", "PEN", "BOX", "RED", "TOP"])
    enc = lambda ch: chr((ord(ch) - 65 + shift) % 26 + 65)
    enc_word = "".join(enc(c) for c in word)
    rev = enc_word[::-1]

    def enc_seq(w):
        return "".join(enc(c) for c in w)

    q = ("Secret code: move every letter forward %d places (A->%s), then reverse the whole word. "
         "What does %s become?" % (shift, chr((0 + shift) % 26 + 65), word))
    ans = rev
    dec = decoys([enc_word, word[::-1], enc_seq(word[::-1]), word], ans, 3, rng)
    return mk("verbal_reasoning", "3.3", "Master", q, ans, dec,
              "Shift: %s -> %s; reverse -> %s." % (word, enc_word, rev),
              "Two-step cipher (shift then reverse) — rule discovery (expert).",
              ["p3", "high_ability", "verbal", "code", "master"], "Authored 3.3 master.", rng)


# =========================================================================
# Registry + generation
# =========================================================================
GEN = {
    "numerical_reasoning": [g_num_seq, g_num_analogy, g_num_system, g_num_chain, g_num_master],
    "logical_reasoning": [g_log_order, g_log_cond, g_log_class, g_log_syll, g_log_constraint, g_log_master],
    "verbal_reasoning": [g_ver_analogy, g_ver_class, g_ver_code, g_ver_wordmanip, g_ver_sentlogic, g_ver_letterpat, g_ver_cloze, g_ver_master],
    "visual_spatial": [g_vis_rot, g_vis_reflect, g_vis_net, g_vis_3d, g_vis_pos, g_vis_transform],
    "pattern_abstract": [g_pat_countseq, g_pat_matrix2, g_pat_matrix3, g_pat_odd, g_pat_analogy],
    "problem_solving": [g_ps_wb, g_ps_gc, g_ps_ba, g_ps_patternapp, g_ps_draw, g_ps_list],
}
# cap verbal 3.7 (cloze) to keep vocabulary light
CAP = {"g_ver_cloze": 10}


def main():
    seed_qs = SEED["questions"]
    seed_counts = {}
    for q in seed_qs:
        seed_counts[q["domain"]] = seed_counts.get(q["domain"], 0) + 1
    need = {d: DOMAIN_TARGET[d] - seed_counts.get(d, 0) for d in DOMAIN_TARGET}
    print("seed counts:", seed_counts)
    print("need:", need)

    new_qs = []
    fingerprints = set()
    for q in seed_qs:
        fingerprints.add((q["question"].strip().lower(), q["answer"]))
    cap_used = {}
    rng = random.Random(20260829)
    for domain, target in need.items():
        gens = GEN[domain]
        attempts = 0
        made = 0
        while made < target and attempts < target * 40 + 200:
            attempts += 1
            g = RNG.choice(gens)
            gname = g.__name__
            if gname in CAP and cap_used.get(gname, 0) >= CAP[gname]:
                continue
            try:
                item = g(rng)
            except Exception as e:
                continue
            if item is None:
                continue
            fp = (item["question"].strip().lower(), item["answer"])
            if fp in fingerprints:
                continue
            # also avoid duplicating a seed fingerprint
            fingerprints.add(fp)
            cap_used[gname] = cap_used.get(gname, 0) + 1
            new_qs.append(item)
            made += 1
        print("  %s: made %d / %d (attempts %d)" % (domain, made, target, attempts))

    all_qs = seed_qs + new_qs
    bank = dict(SEED)
    bank["questions"] = all_qs
    bank["dataset"] = dict(SEED["dataset"])
    bank["dataset"]["version"] = "0.6-local"
    bank["dataset"]["question_count"] = len(all_qs)
    bank["dataset"]["composition"] = {
        "baseline_v041": 50,
        "verbal_extension_v05": 10,
        "new_generated": len(new_qs),
        "total": len(all_qs),
    }
    json.dump(bank, open(BANK, "w"), ensure_ascii=False, indent=2)
    print("TOTAL questions:", len(all_qs), "| new:", len(new_qs))
    from collections import Counter
    print("by domain:", dict(Counter(q["domain"] for q in all_qs)))


if __name__ == "__main__":
    main()
