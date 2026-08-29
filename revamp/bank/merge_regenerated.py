import json, re
from collections import Counter

SKILLS = {'1.3','1.4','2.2','2.3','3.6','6.3','6.4','6.5','6.6'}

def load_utf8(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except UnicodeDecodeError:
        return json.load(open(path, encoding='cp1252'))

def easy_fix(q):
    for o in q['options']:
        if not isinstance(o['text'], str):
            o['text'] = str(o['text'])
    if q['skill'] in ('3.5', '3.7'):
        for o in q['options']:
            t = o['text'].strip()
            if re.fullmatch(r'[A-Za-z]+\d', t):
                o['text'] = re.sub(r'\d$', '', t)

def corruption_flags(q):
    flags = []
    sk = q['skill']
    for o in q['options']:
        t = o['text']
        if not isinstance(t, str):
            flags.append('option_text_not_string'); continue
        if sk == '3.6':
            if not re.fullmatch(r'[A-Za-z]', t.strip()):
                flags.append('letter_option_corrupted')
        elif sk in ('3.5','3.7'):
            if re.fullmatch(r'[A-Za-z]+\d', t.strip()):
                flags.append('name_option_corrupted')
            if re.search(r'[\[\]_^]', t):
                flags.append('symbol_in_option')
        else:
            if re.search(r'[\[\]_^]', t):
                flags.append('symbol_in_option')
    return list(set(flags))

# ---- load regenerated (already validated) ----
reg = load_utf8('regenerated_questions.json')
print('Regenerated:', len(reg))

# ---- rebuild production base from ORIGINAL bank + audit tracker ----
bank = load_utf8('brainactive_p3_question_bank.json')['questions']
tracker = load_utf8('deep_qa_tracker.json')
tmap = {t['id']: t for t in tracker}

base = []
used_ids = set()
maxn = 0
for q in bank:
    t = tmap.get(q['id'], {})
    gep = t.get('gep_quality', '?'); match = t.get('match', '?')
    q2 = dict(q); easy_fix(q2)
    corr = corruption_flags(q2)
    content_corr = [c for c in corr if c != 'option_text_not_string']
    unverifiable = (match == 'visual-dependent')
    ready = (gep in ('production','acceptable')) and (match != False) and (not content_corr) and (not unverifiable)
    if ready and q2.get('skill') not in SKILLS:
        # assign a clean sequential id to avoid any collision with regenerated ids
        maxn += 1
        q2['id'] = 'BA_P3_%04d' % maxn
        used_ids.add(q2['id'])
        base.append(q2)
print('Production base (excl. 9 skills, re-fixed):', len(base))

# ---- assign ids to regenerated from a live set ----
for q in reg:
    maxn += 1
    q['id'] = 'BA_P3_%04d' % maxn
    while q['id'] in used_ids:
        maxn += 1
        q['id'] = 'BA_P3_%04d' % maxn
    used_ids.add(q['id'])
    q['qa_status'] = 'regenerated_pending_ai1'
    q['image_path'] = None
    q['provenance'] = {'basis': 'Regenerated per GEMINI_REGENERATION_BRIEF.md', 'regenerated': True}
    q['production_ready'] = True
    q['qa_flags'] = ['regenerated_pending_ai1_review']

merged = base + reg
print('Merged total:', len(merged), 'unique ids:', len(used_ids))

# ---- final validation ----
bad = 0
for q in merged:
    sk = q['skill']
    for o in q['options']:
        t = o['text']
        if not isinstance(t, str): bad += 1; continue
        if sk == '3.6' and not re.fullmatch(r'[A-Za-z]', t.strip()): bad += 1
        if sk in ('3.5','3.7') and re.fullmatch(r'[A-Za-z]+\d', t.strip()): bad += 1
        if re.search(r'[\[\]_^]', t): bad += 1
        if '\ufffd' in t: bad += 1
    # answer in options
    if q['answer'] not in [o['id'] for o in q['options']]: bad += 1
print('Corrupted/invalid options in merged:', bad)

print('Per-skill:', dict(Counter(q['skill'] for q in merged)))
print('Level:', dict(Counter(q['level'] for q in merged)))
print('Domain:', dict(Counter(q['domain'] for q in merged)))

json.dump({'questions': merged, 'meta': {'note': 'Production bank; 9 skills regenerated per GEMINI_REGENERATION_BRIEF.md', 'count': len(merged)}},
          open('brainactive_p3_question_bank_production.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE brainactive_p3_question_bank_production.json (UTF-8)')
