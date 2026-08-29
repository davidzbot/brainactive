import json, re
from collections import Counter

bank = json.load(open('brainactive_p3_question_bank.json'))
tracker = json.load(open('deep_qa_tracker.json'))
tmap = {t['id']: t for t in tracker}

def easy_fix(q):
    fixed = []
    for o in q['options']:
        if not isinstance(o['text'], str):
            o['text'] = str(o['text'])
            fixed.append('cast_option_to_str')
    if q['skill'] in ('3.5', '3.7'):
        for o in q['options']:
            t = o['text'].strip()
            if re.fullmatch(r'[A-Za-z]+\d', t):
                o['text'] = re.sub(r'\d$', '', t)
                fixed.append('strip_trailing_digit')
    return fixed

def corruption_flags(q):
    flags = []
    sk = q['skill']
    for o in q['options']:
        t = o['text']
        if not isinstance(t, str):
            flags.append('option_text_not_string')
            continue
        if sk == '3.6':
            if not re.fullmatch(r'[A-Za-z]', t.strip()):
                flags.append('letter_option_corrupted')
        elif sk in ('3.5', '3.7'):
            if re.fullmatch(r'[A-Za-z]+\d', t.strip()):
                flags.append('name_option_corrupted')
            if re.search(r'[\[\]_^]', t):
                flags.append('symbol_in_option')
        else:
            if re.search(r'[\[\]_^]', t):
                flags.append('symbol_in_option')
    return list(set(flags))

prod = []
flagged = []
fix_counts = Counter()
for q in bank['questions']:
    t = tmap.get(q['id'], {})
    gep = t.get('gep_quality', '?')
    match = t.get('match', '?')
    q2 = dict(q)
    fixed = easy_fix(q2)
    for f in fixed:
        fix_counts[f] += 1
    corr = corruption_flags(q2)
    content_corr = [c for c in corr if c != 'option_text_not_string']
    unverifiable = (match == 'visual-dependent')
    reasons = []
    if gep not in ('production', 'acceptable'):
        reasons.append('not_production_quality:' + gep)
    if match == False:
        reasons.append('answer_mismatch')
    if content_corr:
        reasons.append('content_corruption:' + ','.join(content_corr))
    if unverifiable:
        reasons.append('needs_visual_review')
    if q.get('visual_required') == True and not unverifiable:
        reasons.append('has_visual_review_recommended')
    if fixed:
        reasons.append('easy_fixed:' + ','.join(set(fixed)))
    ready = (gep in ('production', 'acceptable')) and (match != False) and (not content_corr) and (not unverifiable)
    q2['production_ready'] = ready
    q2['qa_flags'] = reasons
    flagged.append(q2)
    if ready:
        prod.append(q2)

json.dump({'questions': flagged, 'meta': bank.get('meta', {})},
          open('brainactive_p3_question_bank_flagged.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'questions': prod, 'meta': bank.get('meta', {})},
          open('brainactive_p3_question_bank_production.json', 'w'), ensure_ascii=False, indent=1)

print('Easy fixes applied:', dict(fix_counts))
print('PRODUCTION bank:', len(prod))
print('By domain:', dict(Counter(q['domain'] for q in prod)))
print('By level:', dict(Counter(q['level'] for q in prod)))
pa = Counter('acceptable' if tmap.get(q['id'], {}).get('gep_quality') == 'acceptable' else 'production' for q in prod)
print('prod/acceptable:', dict(pa))
allr = Counter()
for q in flagged:
    for r in q['qa_flags']:
        allr[r.split(':')[0]] += 1
print('Filter reason counts:', dict(allr))
print('Filtered out:', 1000 - len(prod))
