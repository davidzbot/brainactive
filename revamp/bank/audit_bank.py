# -*- coding: utf-8 -*-
"""
Independent auditor for the BrainActive P3 High Ability local question bank.

For EVERY question it checks:
  C1) structural: exactly 4 options, answer letter valid & maps to an existing option,
      options distinct.
  C2) consistency: the correct option text appears in explanation/reasoning.
  C3) independent re-derivation by PARSING the question text (not the generator) for the
      computable families, compared to the stored answer.
  C4) verbal A/B/C compliance counts (report only).

Outputs a summary to stdout and writes audit_findings.json.

NO DB / NO Supabase / NO production code. Read-only over the bank JSON.
"""
import json
import os
import re
import math

ROOT = r"C:\Projects\brainactive-android\revamp"
BANK = os.path.join(ROOT, "bank", "brainactive_p3_question_bank.json")
OUT = os.path.join(ROOT, "bank", "audit_findings.json")

SHAPES = ["triangle", "square", "circle"]


def load():
    return json.load(open(BANK))


# ---------------------------------------------------------------------------
# helper
# ---------------------------------------------------------------------------
def correct_text(q):
    ans = q.get("answer")
    for o in q.get("options", []):
        if o.get("id") == ans:
            return o.get("text")
    return None


# ---------------------------------------------------------------------------
# C1 structural
# ---------------------------------------------------------------------------
def check_structural(q):
    issues = []
    opts = q.get("options", [])
    opt_ids = [o.get("id") for o in opts]
    if len(opts) != 4:
        issues.append("options != 4 (%d)" % len(opts))
    if len(set(opt_ids)) != len(opt_ids):
        issues.append("duplicate option ids")
    ans = q.get("answer")
    if ans not in opt_ids:
        issues.append("answer letter %s not in options %s" % (ans, opt_ids))
    texts = [o.get("text") for o in opts]
    if len(set(texts)) != len(texts):
        issues.append("options not distinct")
    return issues


# ---------------------------------------------------------------------------
# C2 consistency
# ---------------------------------------------------------------------------
def check_consistency(q):
    # Only flag short options (<=2 words) that should appear verbatim. Longer options are
    # routinely paraphrased in the explanation, so requiring a verbatim match yields false alarms.
    ct = (correct_text(q) or "")
    if len(ct.split()) > 2:
        return []
    blob = (q.get("explanation", "") + " " + q.get("reasoning", "")).lower()
    # normalise punctuation/spaces for a fair substring test
    norm = lambda s: " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())
    if norm(ct) not in norm(blob):
        return ["correct option text '%s' not found in explanation/reasoning" % ct]
    return []


# ---------------------------------------------------------------------------
# number sequence models (1.1)
# ---------------------------------------------------------------------------
def m_arith(t):
    if len(t) < 3:
        return None
    d = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    if all(x == d[0] for x in d):
        return t[-1] + d[0]
    return None


def m_geo(t):
    if len(t) < 3:
        return None
    if 0 in t:
        return None
    r = t[1] // t[0]
    if t[0] * r != t[1]:
        return None
    for i in range(len(t) - 1):
        if t[i + 1] != t[i] * r:
            return None
    return t[-1] * r


def m_fib(t):
    if len(t) < 4:
        return None
    for i in range(2, len(t)):
        if t[i] != t[i - 1] + t[i - 2]:
            return None
    return t[-1] + t[-2]


def m_square(t):
    if len(t) < 3:
        return None
    roots = []
    for x in t:
        if x < 0:
            return None
        s = int(math.isqrt(x))
        if s * s != x:
            return None
        roots.append(s)
    for i in range(len(roots) - 1):
        if roots[i + 1] != roots[i] + 1:
            return None
    return (roots[-1] + 1) ** 2


def m_grow(t):
    if len(t) < 3:
        return None
    d = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    if len(d) < 2:
        return None
    for i in range(1, len(d)):
        if d[i] != d[i - 1] + 1:
            return None
    return t[-1] + d[-1] + 1


def m_inter(t):
    if len(t) < 6:
        return None
    even_idx = t[0::2]
    odd_idx = t[1::2]
    if len(even_idx) < 3 or len(odd_idx) < 3:
        return None
    de = [even_idx[i + 1] - even_idx[i] for i in range(len(even_idx) - 1)]
    do = [odd_idx[i + 1] - odd_idx[i] for i in range(len(odd_idx) - 1)]
    if not all(x == de[0] for x in de):
        return None
    if not all(x == do[0] for x in do):
        return None
    if de[0] == do[0]:
        return None  # uniform arithmetic, not genuinely woven
    nidx = len(t)
    if nidx % 2 == 0:
        return even_idx[-1] + de[0]
    return odd_idx[-1] + do[0]


def m_alt(t):
    if len(t) < 6:
        return None
    add = t[1] - t[0]
    mul = None
    for i in range(len(t) - 1):
        if i % 2 == 0:
            if t[i + 1] != t[i] + add:
                return None
        else:
            if t[i] == 0:
                return None
            if t[i + 1] % t[i] != 0:
                return None
            if mul is None:
                mul = t[i + 1] // t[i]
            if t[i + 1] != t[i] * mul:
                return None
    if mul is None:
        return None
    last_i = len(t) - 2
    if last_i % 2 == 0:
        return t[-1] * mul
    return t[-1] + add


def deriv_num_seq(q):
    qtext = q.get("question", "")
    head = qtext.split("___?")[0]
    nums = [int(x) for x in re.findall(r"-?\d+", head)]
    if len(nums) < 3:
        return ("unverified", "too few numbers")
    stored = correct_text(q)
    try:
        target = int(stored)
    except Exception:
        return ("unverified", "answer not int")
    models = [("arith", m_arith(nums)), ("geo", m_geo(nums)), ("fib", m_fib(nums)),
              ("square", m_square(nums)), ("grow", m_grow(nums)),
              ("interleaved", m_inter(nums)), ("alt_add_mul", m_alt(nums))]
    fits = [(n, p) for n, p in models if p is not None]
    if not fits:
        return ("unverified", "no model fits the visible terms")
    mismatch = [n for n, p in fits if p != target]
    if mismatch:
        return ("mismatch", "stored %s but model(s) %s predict %s" % (
            target, mismatch, [p for n, p in fits if n in mismatch]))
    preds = set(p for n, p in fits)
    if len(preds) > 1:
        return ("ambiguous", "models fit with different predictions: %s" % fits)
    return ("ok", "")


# ---------------------------------------------------------------------------
# 1.2 number analogy
# ---------------------------------------------------------------------------
def deriv_num_analogy(q):
    nums = [int(x) for x in re.findall(r"-?\d+", q.get("question", ""))]
    if len(nums) < 3:
        return ("unverified", "need 3 numbers")
    a, b, c = nums[0], nums[1], nums[2]
    try:
        target = int(correct_text(q))
    except Exception:
        return ("unverified", "answer not int")
    cands = set()
    cands.add(c + (b - a))
    if a != 0 and b % a == 0:
        cands.add(c * (b // a))
    if b == a * a:
        cands.add(c * c)
    for m in range(2, 9):
        cands.add(c * m + (b - a * m))
        cands.add(c * m - (a * m - b))
    if target in cands:
        return ("ok", "")
    return ("mismatch", "stored %s; candidate rules give %s" % (target, sorted(cands)))


# ---------------------------------------------------------------------------
# 1.3 weight system
# ---------------------------------------------------------------------------
def deriv_weight(q):
    pairs = re.findall(r"(triangle|square|circle) and a (triangle|square|circle) together weigh (\d+)", q.get("question", ""))
    if len(pairs) != 3:
        return ("unverified", "could not parse 3 pairs")
    v = [int(p[2]) for p in pairs]
    tot = (v[0] + v[1] + v[2]) // 2
    w = {}
    for s in SHAPES:
        np = [p for p in pairs if s not in (p[0], p[1])][0]
        w[s] = tot - int(np[2])
    ask = re.search(r"Which shape is (heaviest|lightest)\?", q.get("question", ""))
    if not ask:
        return ("unverified", "could not parse heaviest/lightest")
    if ask.group(1) == "heaviest":
        ans = max(w, key=w.get)
    else:
        ans = min(w, key=w.get)
    if ans.lower() == (correct_text(q) or "").lower():
        return ("ok", "")
    return ("mismatch", "stored %s; computed %s (weights %s)" % (correct_text(q), ans, w))


# ---------------------------------------------------------------------------
# 1.4 chained comparison
# ---------------------------------------------------------------------------
def deriv_chain(q):
    text = q.get("question", "")
    more = re.search(r"(\w+) has (\d+) more than (\w+)", text)
    fewer = re.search(r"(\w+) has (\d+) fewer than (\w+)", text)
    base = re.search(r"(\w+) has (\d+)\.", text)
    if not (more and fewer and base):
        return ("unverified", "could not parse chain")
    a, off1, b = more.group(1), int(more.group(2)), more.group(3)
    off2 = int(fewer.group(2))
    c = base.group(1)
    val = int(base.group(2))
    cv = val
    bv = val - off2
    av = bv + off1
    vals = {c: cv, b: bv, a: av}
    top = max(vals, key=vals.get)
    if top == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; computed %s (vals %s)" % (correct_text(q), top, vals))


# ---------------------------------------------------------------------------
# 2.1 ordering
# ---------------------------------------------------------------------------
def deriv_order(q):
    text = q.get("question", "")
    edges = []
    edges += [(a, b) for a, b in re.findall(r"(\w+) is taller than (\w+)", text)]
    edges += [(a, b) for a, b in re.findall(r"(\w+) beats (\w+)", text)]
    for a, b in re.findall(r"(\w+) is shorter than (\w+)", text):
        edges.append((b, a))  # y is taller than x
    for a, b, c in re.findall(r"(\w+) and (\w+) are taller than (\w+)", text):
        edges.append((a, c)); edges.append((b, c))
    if not edges:
        return ("unverified", "no order edges parsed")
    nodes = set()
    for a, b in edges:
        nodes.add(a); nodes.add(b)
    adj = {n: set() for n in nodes}
    indeg = {n: 0 for n in nodes}
    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b); indeg[b] += 1
    order = []
    remaining = set(nodes)
    unique = True
    while remaining:
        zeros = [n for n in remaining if indeg[n] == 0]
        if len(zeros) != 1:
            unique = False
            break
        n = zeros[0]
        order.append(n)
        remaining.discard(n)
        for m in adj[n]:
            indeg[m] -= 1
    if not unique or len(order) != len(nodes):
        return ("ambiguous", "order not uniquely determined by the clues (edges %s)" % edges)
    stored = correct_text(q)
    tl = text.lower()
    if re.search(r"who is the shortest|which is the shortest|the shortest\?", tl):
        exp = order[-1]
        if exp == stored:
            return ("ok", "")
        return ("mismatch", "stored %s; shortest is %s (order %s)" % (stored, exp, order))
    if "order them" in tl or "tallest to shortest" in tl or "fastest to slowest" in tl:
        exp = ", ".join(order)
        if exp == stored:
            return ("ok", "")
        return ("mismatch", "stored %s; order is %s" % (stored, exp))
    return ("unverified", "ordering question form not recognised")


# ---------------------------------------------------------------------------
# 2.3 conditional
# ---------------------------------------------------------------------------
def deriv_cond(q):
    text = q.get("question", "")
    num = re.search(r"The number (\d+) is NOT blue", text)
    if num:
        n = num.group(1)
        exp = q.get("explanation", "")
        if n not in exp:
            return ("mismatch", "explanation hardcodes a different number than the question (%s not in explanation)" % n)
        if "not even" in (correct_text(q) or "").lower():
            return ("ok", "")
        return ("mismatch", "stored %s; contrapositive gives 'It is not even'" % correct_text(q))
    if "it is hot" in text.lower() and "we swim" in text.lower() and "we are happy" in text.lower():
        if correct_text(q) == "We are happy":
            return ("ok", "")
        return ("mismatch", "stored %s; chained conditionals give 'We are happy'" % correct_text(q))
    return ("unverified", "conditional form not parsed")


# ---------------------------------------------------------------------------
# 3.3 codes / ciphers
# ---------------------------------------------------------------------------
def shiftf(ch, k):
    return chr((ord(ch) - 65 + k) % 26 + 65)


def deriv_code(q):
    text = q.get("question", "")
    if "reverse the whole word" in text:
        m = re.search(r"forward (\d+) places \(A->(\w)", text)
        wm = re.search(r"What does (\w+) become\?", text)
        if not (m and wm):
            return ("unverified", "two-step parse fail")
        k = int(m.group(1)); word = wm.group(1)
        enc = "".join(shiftf(c, k) for c in word)
        pred = enc[::-1]
        if pred == correct_text(q):
            return ("ok", "")
        return ("mismatch", "stored %s; two-step gives %s" % (correct_text(q), pred))
    if "SQUARE of its place" in text or "worth the SQUARE" in text:
        m = re.search(r"worth (\d+)\?", text)
        if not m:
            return ("unverified", "square parse fail")
        val = int(m.group(1))
        s = int(math.isqrt(val))
        if s * s != val:
            return ("mismatch", "stored %s; %d not a perfect square" % (correct_text(q), val))
        pred = chr(64 + s)
        if pred == correct_text(q):
            return ("ok", "")
        return ("mismatch", "stored %s; square gives %s" % (correct_text(q), pred))
    if "moves forward" in text:
        m = re.search(r"forward (\d+) \(A->(\w)", text)
        wm = re.search(r"How is (\w+) written\?", text)
        if not (m and wm):
            return ("unverified", "shift_enc parse fail")
        k = int(m.group(1)); word = wm.group(1)
        pred = "".join(shiftf(c, k) for c in word)
        if pred == correct_text(q):
            return ("ok", "")
        return ("mismatch", "stored %s; shift+%d gives %s" % (correct_text(q), k, pred))
    if "steps before" in text:
        m = re.search(r"letter (\d+) steps before", text)
        wm = re.search(r"code word is (\w+)", text)
        if not (m and wm):
            return ("unverified", "shift_dec parse fail")
        k = int(m.group(1)); word = wm.group(1)
        pred = "".join(chr((ord(ch) - 65 - k) % 26 + 65) for ch in word)
        if pred == correct_text(q):
            return ("ok", "")
        return ("mismatch", "stored %s; decode gives %s" % (correct_text(q), pred))
    return ("unverified", "cipher form not parsed")


# ---------------------------------------------------------------------------
# 6.1 working backwards
# ---------------------------------------------------------------------------
def deriv_wb(q):
    m = re.search(r"changed by: (.*?)\. The final result is (\d+)", q.get("question", ""))
    if not m:
        return ("unverified", "work-backwards parse fail")
    ops = re.findall(r"([+x]) (\d+)", m.group(1))
    final = int(m.group(2))
    rev = final
    for op, k in reversed(ops):
        k = int(k)
        if op == "+":
            rev -= k
        else:
            if rev % k != 0:
                return ("mismatch", "stored %s; reverse not divisible by %d" % (correct_text(q), k))
            rev //= k
    if str(rev) == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; reverse-compute gives %d" % (correct_text(q), rev))


# ---------------------------------------------------------------------------
# 6.2 guess & check coins
# ---------------------------------------------------------------------------
def deriv_gc(q):
    m = re.search(r"There are (\d+) coins in total and they make (\d+) dollars", q.get("question", ""))
    if not m:
        return ("unverified", "coins parse fail")
    T = int(m.group(1)); Y = int(m.group(2))
    sols = [f for f in range(T + 1) if 5 * f + 2 * (T - f) == Y]
    if not sols:
        return ("mismatch", "stored %s; no solution exists for %d coins / %d dollars" % (correct_text(q), T, Y))
    if len(sols) > 1:
        return ("ambiguous", "multiple solutions %s" % sols)
    if str(sols[0]) == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; solution is %d" % (correct_text(q), sols[0]))


# ---------------------------------------------------------------------------
# 6.3 before-after
# ---------------------------------------------------------------------------
def deriv_ba(q):
    text = q.get("question", "")
    m = re.search(r"(\w+) has (\d+) more (?:marbles|stickers) than (\w+)", text)
    g = re.search(r"(\w+) gives (\w+) (\d+) sticker", text)
    if not (m and g):
        return ("unverified", "before-after parse fail")
    lead = int(m.group(2))
    move = int(g.group(3))
    gap = lead - 2 * move
    if gap > 0:
        pred = "%s, by %d" % (m.group(1), gap)
    elif gap < 0:
        pred = "%s, by %d" % (m.group(3), -gap)
    else:
        pred = "They are equal"
    if pred == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; computed %s" % (correct_text(q), pred))


# ---------------------------------------------------------------------------
# 6.4 draw a diagram
# ---------------------------------------------------------------------------
def deriv_draw(q):
    m = re.search(r"(\d+) trees are planted in a straight line, (\d+) metres apart", q.get("question", ""))
    if not m:
        return ("unverified", "draw parse fail")
    n = int(m.group(1)); gap = int(m.group(2))
    pred = (n - 1) * gap
    if str(pred) == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; computed %d" % (correct_text(q), pred))


# ---------------------------------------------------------------------------
# 6.5 make a list
# ---------------------------------------------------------------------------
def deriv_list(q):
    m = re.search(r"How many (\d+)-letter codes can you make using the letters ([A-Z,\s]+?) if you may", q.get("question", ""))
    if not m:
        return ("unverified", "list parse fail")
    length = int(m.group(1))
    letters = [x.strip() for x in m.group(2).split(",") if x.strip()]
    letters = [x for x in letters if re.match(r"^[A-Z]$", x)]
    if not letters:
        return ("unverified", "no letters parsed")
    pred = len(letters) ** length
    if str(pred) == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; %d^%d = %d" % (correct_text(q), len(letters), length, pred))


# ---------------------------------------------------------------------------
# 6.6 pattern application
# ---------------------------------------------------------------------------
def deriv_patapp(q):
    m = re.search(r"(\d+) -> (\d+), (\d+) -> (\d+), (\d+) -> (\d+)\. What should (\d+) become\?", q.get("question", ""))
    if not m:
        return ("unverified", "pattern-app parse fail")
    pts = [(int(m.group(i)), int(m.group(i + 1))) for i in (1, 3, 5)]
    x1, y1 = pts[0]
    x2, y2 = pts[1]
    if x2 == x1:
        return ("unverified", "same x")
    slope = (y2 - y1) // (x2 - x1)
    if (y2 - y1) % (x2 - x1) != 0:
        return ("unverified", "non-integer slope")
    intercept = y1 - slope * x1
    for x, y in pts:
        if slope * x + intercept != y:
            return ("mismatch", "rule %dx+%d fails at %d->%d" % (slope, intercept, x, y))
    N = int(m.group(7))
    pred = slope * N + intercept
    if str(pred) == correct_text(q):
        return ("ok", "")
    return ("mismatch", "stored %s; rule %dx+%d gives %d" % (correct_text(q), slope, intercept, pred))


# ---------------------------------------------------------------------------
# dispatch by skill
# ---------------------------------------------------------------------------
DERIV = {
    "1.1": deriv_num_seq,
    "1.2": deriv_num_analogy,
    "1.3": deriv_weight,
    "1.4": deriv_chain,
    "2.1": deriv_order,
    "2.3": deriv_cond,
    "3.3": deriv_code,
    "6.1": deriv_wb,
    "6.2": deriv_gc,
    "6.3": deriv_ba,
    "6.4": deriv_draw,
    "6.5": deriv_list,
    "6.6": deriv_patapp,
}


def main():
    bank = load()
    qs = bank["questions"]
    c1 = []
    c2 = []
    mismatches = []
    ambiguous = []
    unverified = []
    deriv_examples = []
    by_skill_unverified = {}

    for q in qs:
        qid = q.get("id")
        s = check_structural(q)
        if s:
            c1.append((qid, s))
        k = check_consistency(q)
        if k:
            c2.append((qid, k))
        fn = DERIV.get(q.get("skill"))
        if fn:
            try:
                status, detail = fn(q)
            except Exception as e:
                status, detail = "unverified", "exception: %s" % e
            if status == "ok":
                continue
            elif status == "mismatch":
                mismatches.append((qid, q.get("skill"), detail))
                deriv_examples.append((qid, "mismatch", detail))
            elif status == "ambiguous":
                ambiguous.append((qid, q.get("skill"), detail))
                deriv_examples.append((qid, "ambiguous", detail))
            else:
                unverified.append(qid)
                by_skill_unverified[q.get("skill")] = by_skill_unverified.get(q.get("skill"), 0) + 1
        else:
            unverified.append(qid)

    # verbal A/B/C report
    from collections import Counter
    ver = Counter(q.get("skill") for q in qs if q.get("domain") == "verbal_reasoning")
    v37 = sum(1 for q in qs if q.get("skill") == "3.7")

    summary = {
        "total": len(qs),
        "c1_structural_fails": len(c1),
        "c2_consistency_fails": len(c2),
        "mismatches": len(mismatches),
        "ambiguous": len(ambiguous),
        "unverified_by_skill": len(unverified),
        "unverified_by_skill_breakdown": by_skill_unverified,
        "verbal_3_7_count": v37,
        "verbal_skill_counts": dict(ver),
    }

    print("=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    print("Total questions:        %d" % len(qs))
    print("C1 structural fails:    %d" % len(c1))
    print("C2 consistency fails:   %d" % len(c2))
    print("C3 mismatches:          %d" % len(mismatches))
    print("C3 ambiguous:           %d" % len(ambiguous))
    print("Unverified (by skill):  %d" % len(unverified))
    print("  breakdown:            %s" % by_skill_unverified)
    print("Verbal 3.7 (B) count:  %d (cap ~10)" % v37)
    print("Verbal skill counts:    %s" % dict(ver))

    if c1:
        print("\n-- C1 structural fails (first 20) --")
        for x in c1[:20]:
            print("  ", x)
    if c2:
        print("\n-- C2 consistency fails (first 20) --")
        for x in c2[:20]:
            print("  ", x)
    if mismatches:
        print("\n-- MISMATCHES (all) --")
        for x in mismatches:
            print("  ", x)
    if ambiguous:
        print("\n-- AMBIGUOUS (all) --")
        for x in ambiguous:
            print("  ", x)

    findings = {
        "summary": summary,
        "c1": c1,
        "c2": c2,
        "mismatches": mismatches,
        "ambiguous": ambiguous,
        "unverified": unverified,
    }
    json.dump(findings, open(OUT, "w"), indent=2)
    print("\nWrote %s" % OUT)


if __name__ == "__main__":
    main()
