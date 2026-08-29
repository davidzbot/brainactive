import json, re

reg = json.load(open('regenerated_questions.json', encoding='utf-8'))
LET = {c: i+1 for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
INV = {v: k for k, v in LET.items()}

def letter_after(text_seq, rule_text):
    seq = [LET[c] for c in re.findall(r'[A-Z]', text_seq)]
    if len(seq) < 2:
        return None
    m = re.search(r'(?:moves|adds?|plus|forward by)\s*(\d+)', rule_text, re.I)
    if m:
        step = int(m.group(1)); nxt = seq[-1] + step
        return INV[((nxt-1) % 26)+1]
    if re.search(r'grows by 1', rule_text, re.I):
        gaps = [seq[i+1]-seq[i] for i in range(len(seq)-1)]
        nxt = seq[-1] + gaps[-1] + 1
        return INV[((nxt-1) % 26)+1]
    return None

def verify_13(q):
    pairs = re.findall(r'(triangle|square|circle) and a (triangle|square|circle) together weigh (\d+)', q['question'], re.I)
    if len(pairs) != 3:
        return None
    shset, pairvals = set(), {}
    for a,b,val in pairs:
        a,b = a.lower(), b.lower(); shset.update([a,b]); pairvals[(a,b)] = int(val); pairvals[(b,a)] = int(val)
    total = sum(int(p[2]) for p in pairs)//2
    weights = {}
    for s in shset:
        opp = [k for k in pairvals if s not in k][0]
        weights[s] = total - pairvals[opp]
    ask = re.search(r'(heaviest|lightest)', q['question'], re.I).group(1).lower()
    ans = max(weights, key=weights.get) if ask=='heaviest' else min(weights, key=weights.get)
    return ans.capitalize()

def verify_14(q, want='max'):
    txt = q['question']; vals = {}; rels = []
    for m in re.finditer(r'([A-Z][a-z]+) has (\d+)(?!\s*(?:more|fewer))', txt):
        vals[m.group(1)] = int(m.group(2))
    for m in re.finditer(r'([A-Z][a-z]+) has (\d+) more [a-z]+ than ([A-Z][a-z]+)', txt):
        rels.append((m.group(1), m.group(3), int(m.group(2))))
    for m in re.finditer(r'([A-Z][a-z]+) has (\d+) fewer [a-z]+ than ([A-Z][a-z]+)', txt):
        rels.append((m.group(1), m.group(3), -int(m.group(2))))
    changed = True
    while changed and rels:
        changed = False
        for x,y,n in list(rels):
            if y in vals and x not in vals:
                vals[x] = vals[y] + n; changed = True; rels.remove((x,y,n))
            elif x in vals and y not in vals:
                vals[y] = vals[x] - n; changed = True; rels.remove((x,y,n))
    if not vals:
        return None
    return (max if want=='max' else min)(vals, key=vals.get)

def opt_name(q):
    ids = [o['id'] for o in q['options']]
    t = q['options'][ids.index(q['answer'])]['text']
    m = re.search(r'[A-Z][a-z]+', t)
    return m.group(0) if m else t

def ans_text(q):
    ids = [o['id'] for o in q['options']]
    return q['options'][ids.index(q['answer'])]['text']

mism = []
checked = 0
for q in reg:
    sk = q['skill']
    if sk == '1.3':
        exp = verify_13(q); checked += 1
        if exp and exp.lower() != opt_name(q).lower(): mism.append(('1.3', q.get('id'), exp, opt_name(q)))
    elif sk == '1.4':
        want = 'min' if re.search(r'fewest|least', q['question'], re.I) else 'max'
        exp = verify_14(q, want); checked += 1
        if exp and exp != opt_name(q): mism.append(('1.4', q.get('id'), exp, opt_name(q)))
    elif sk == '3.6':
        m = re.search(r'goes:\s*([A-Z,\s]+?)\.?\s*([A-Za-z0-9+ \-]+?)\.?\s*What', q['question'])
        if m:
            exp = letter_after(m.group(1), m.group(2)); checked += 1
            if exp and exp != ans_text(q): mism.append(('3.6', q.get('id'), exp, ans_text(q)))

print('Mechanically verified (1.3/1.4/3.6):', checked, 'questions')
print('Mismatches:', len(mism))
for mm in mism[:40]:
    print('  ', mm)
