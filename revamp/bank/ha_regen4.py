import json, random
rng = random.Random(20260924)
NEW = json.load(open("revamp/bank/ha_new_20260921.json", encoding="utf-8"))
byid = {q["id"]: q for q in NEW}
seqn = [370]
extra = json.load(open("revamp/bank/ha_extra_20260921.json", encoding="utf-8"))
def nid():
    seqn[0] += 1
    while ("BA_P3_HA_%04d" % seqn[0]) in byid or any(q["id"] == ("BA_P3_HA_%04d" % seqn[0]) for q in extra):
        seqn[0] += 1
    return "BA_P3_HA_%04d" % seqn[0]
def shuffle_opts(texts, ans):
    order = list(range(4))
    rng.shuffle(order)
    opts = [{"id": "ABCD"[i], "text": str(texts[j])} for i, j in enumerate(order)]
    return opts, "ABCD"[order.index(ans)]
def mk(domain, topic, skill, arch, level, diff, q, texts, ans, expl, reason, tags):
    texts = [str(x) for x in texts]
    assert len(texts) == 4 and len(set(texts)) == 4
    opts, aid = shuffle_opts(texts, ans)
    return {"id": nid(), "domain": domain, "topic": topic, "skill": skill, "archetype": arch, "level": level, "difficulty": diff, "question_type": "multiple_choice", "question": q, "options": opts, "answer": aid, "explanation": expl, "reasoning": reason, "tags": tags, "visual_required": False, "visual_spec": None, "image_path": None, "is_active": False, "qa_status": "validated_ha_20260921", "provenance": {"basis": "HA purge regen round3 figseq 2026-09-21", "regenerated": True}}
def g_inter():
    s = rng.randint(2, 5)
    vals = [s]
    for _ in range(6):
        vals.append(vals[-1] * 2 if len(vals) % 2 == 1 else vals[-1] + 1)
    ans = vals[-1] * 2
    stem = "Find the next number: " + ", ".join(map(str, vals)) + ", ___?"
    cands = [ans, ans + 1, ans - 1, vals[-1] + 1]
    expl = "Alternate two steps: times 2, then plus 1. Next is " + str(vals[-1]) + " x 2 = " + str(ans) + "."
    return mk("pattern_abstract", "Pattern and Abstract", "5.1", "figure_sequence", "Think", "medium", stem, cands, 0, expl, "Spot two alternating rules.", ["sequence", "interleaved"])
def g_fibgap():
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
    expl = "Add neighbours: " + str(vals[hide - 2]) + " + " + str(vals[hide - 1]) + " = " + str(ans) + ". Check: " + str(vals[hide - 1]) + " + " + str(ans) + " = " + str(vals[hide + 1]) + "."
    return mk("pattern_abstract", "Pattern and Abstract", "5.1", "figure_sequence", "Challenge", "hard", stem, cands, 0, expl, "Use the addition rule to fill the gap.", ["sequence", "fibonacci_gap"])
def g_alt():
    s = rng.randint(3, 9)
    p, q = rng.choice([(3, -1), (4, -2), (5, -2), (2, 3)])
    vals = [s]
    for i in range(5):
        vals.append(vals[-1] + (p if i % 2 == 0 else q))
    nxt = vals[-1] + (p if 5 % 2 == 0 else q)
    stem = "Find the next number: " + ", ".join(map(str, vals)) + ", ___?"
    cands = [nxt, nxt + 1, nxt - 1, nxt + 2]
    expl = "The jumps alternate " + ("+" if p >= 0 else "") + str(p) + " then " + str(q) + ". The next jump is +" + str(p) + ": " + str(nxt) + "."
    return mk("pattern_abstract", "Pattern and Abstract", "5.1", "figure_sequence", "Think", "medium", stem, cands, 0, expl, "Spot the alternating jumps.", ["sequence", "alternating_jumps"])
made = 0
i = 0
fps = set((q["question"].strip().lower(), q["answer"]) for q in NEW + extra)
while made < 14:
    q = [g_inter, g_fibgap, g_alt][i % 3]()
    i += 1
    fp = (q["question"].strip().lower(), q["answer"])
    if fp in fps:
        continue
    fps.add(fp)
    extra.append(q)
    made += 1
json.dump(extra, open("revamp/bank/ha_extra_20260921.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("seq new:", made)

