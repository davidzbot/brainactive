"""Independently verify arithmetic claims (a op b = c) inside all explanations.
Reads the merged upload JSON + production JSON (local mirrors of DB)."""
import json, re, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

OPMAP = {"+": "+", "-": "-", "\u2212": "-", "x": "*", "\u00d7": "*",
         "/": "/", "\u00f7": "/", "*": "*"}

# full chains with precedence: a op b op c ... = d (integers/decimals)
PAT = re.compile(r"(?<!\d)(\d+(?:\.\d+)?(?:\s*[+\-x\u2212\u00d7*/\u00f7]\s*\d+(?:\.\d+)?)+)\s*=\s*(\d+(?:\.\d+)?)(?!\d)")


def py_expr(s):
    for u, py in [("\u2212", "-"), ("\u00d7", "*"), ("\u00f7", "/"), ("x", "*")]:
        s = s.replace(u, py)
    if not re.fullmatch(r"[\d\s+\-*/.()]+", s):
        return None
    try:
        return float(eval(s, {"__builtins__": {}}, {}))
    except Exception:
        return None


NUMCHAIN = r"\d+(?:\.\d+)?(?:\s*[+\-x\u2212\u00d7*/\u00f7]\s*\d+(?:\.\d+)?)*"
CHAIN_PAT = re.compile(r"(?<!\d)(" + NUMCHAIN + r"(?:\s*=\s*" + NUMCHAIN + r")+)(?!\d)")
PAREN_EXT = re.compile(r"(\([^()]+\)\s*[+\-x\u2212\u00d7*/\u00f7]\s*)+$")
LEFT_VAR = re.compile(r"([A-Za-z]\s*[+\-x\u2212\u00d7*/\u00f7=]\s*|[A-Za-z]{2,}\s*)$")
RIGHT_WORD = re.compile(r"^\s*(squared|cubed)\b")


def check_file(path):
    d = json.load(open(path, encoding="utf-8"))
    qs = d["questions"] if isinstance(d, dict) else d
    bad, checked = [], 0
    for q in qs:
        text = q.get("explanation", "")
        for m in CHAIN_PAT.finditer(text):
            chain = m.group(1)
            # extend left through balanced parens: (4x2)+1 = 9
            pre = text[:m.start()]
            pm = PAREN_EXT.search(pre)
            if pm:
                chain = pm.group(1) + chain
                pre = pre[:pm.start()]
            # skip variable/word equations: B + 6 = 24, week 2 = 20, A = 4/6
            if LEFT_VAR.search(pre[-12:]):
                continue
            # skip continuation fragments: ", +4 = 16" (full chain checked separately)
            if re.search(r"[+\-x\u2212\u00d7*/\u00f7]\s*$", pre[-12:].strip()):
                continue
            if RIGHT_WORD.match(text[m.end():m.end() + 12]):
                continue
            parts = [p.strip() for p in re.split(r"\s*=\s*", chain)]
            vals = [py_expr(p) for p in parts]
            if any(v is None for v in vals):
                continue
            checked += 1
            after = text[m.end():m.end() + 16]
            rem = re.match(r"\s*remainder\s+(\d+)", after)
            if rem and len(vals) == 2:
                # integer division with remainder: 26 / 4 = 6 remainder 2
                raw = parts[0]
                for u, py in [("\u2212", "-"), ("\u00d7", "*"), ("\u00f7", "/"), ("x", "*")]:
                    raw = raw.replace(u, py)
                nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", raw)]
                if len(nums) == 2 and nums[1] != 0 and \
                   int(nums[0] // nums[1]) == int(vals[1]) and \
                   int(nums[0] % nums[1]) == int(rem.group(1)):
                    continue
                bad.append((q["id"], chain + f" remainder {rem.group(1)}"))
                continue
            if any(abs(vals[i] - vals[i + 1]) > 1e-9 for i in range(len(vals) - 1)):
                bad.append((q["id"], chain))
    return checked, bad


total_bad = []
for fn in ["brainactive_new_600_upload.json", os.path.join("..", "brainactive_p3_question_bank_production.json")]:
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        print("skip", fn)
        continue
    checked, bad = check_file(p)
    print(f"{os.path.basename(p)}: {checked} equations checked, {len(bad)} FAILED")
    for qid, eq in bad[:30]:
        print(f"  FAIL {qid}: {eq}")
    total_bad.extend(bad)
print("TOTAL FAILURES:", len(total_bad))
