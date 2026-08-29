import json, re, os, glob
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

def fix_image_prefix(p):
    if not p: return p
    if p.startswith('brainactive/'):
        return p[len('brainactive/'):]
    return p

# image filename set
img_files = set()
for ext in ('svg','png'):
    for f in glob.glob('images/*.'+ext):
        img_files.add(os.path.splitext(os.path.basename(f))[0])

# ---- rebuild base from ORIGINAL bank, KEEP original id ----
bank = load_utf8('brainactive_p3_question_bank.json')['questions']
tracker = load_utf8('deep_qa_tracker.json')
tmap = {t['id']: t for t in tracker}

base = []
for q in bank:
    t = tmap.get(q['id'], {})
    gep = t.get('gep_quality', '?'); match = t.get('match', '?')
    q2 = dict(q); easy_fix(q2)
    corr = corruption_flags(q2)
    content_corr = [c for c in corr if c != 'option_text_not_string']
    unverifiable = (match == 'visual-dependent')
    ready = (gep in ('production','acceptable')) and (match != False) and (not content_corr) and (not unverifiable)
    if ready and q2.get('skill') not in SKILLS:
        q2['image_path'] = fix_image_prefix(q2.get('image_path'))
        base.append(q2)
print('Base (original ids kept):', len(base))

# ---- regenerated: new ids ----
reg = load_utf8('regenerated_questions.json')
gi = 0
for q in reg:
    gi += 1
    q['id'] = 'BA_P3_G%03d' % gi
    q['qa_status'] = 'regenerated_pending_ai1'
    q['image_path'] = None
    q['provenance'] = {'basis': 'Regenerated per GEMINI_REGENERATION_BRIEF.md', 'regenerated': True}
    q['production_ready'] = True
    q['qa_flags'] = ['regenerated_pending_ai1_review']
print('Regenerated (new ids):', len(reg))

merged = base + reg
print('Merged total:', len(merged), 'unique ids:', len(set(q['id'] for q in merged)))

# ---- image coverage check ----
vis = [q for q in merged if q.get('visual_required')==True]
have = [q for q in vis if q['id'] in img_files]
print('visual_required:', len(vis), '| image present (by id):', len(have), '| MISSING:', len(vis)-len(have))
missing = [q['id'] for q in vis if q['id'] not in img_files]
print('Missing image ids (first 20):', missing[:20])

# ---- corruption / validity re-check ----
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
    if q['answer'] not in [o['id'] for o in q['options']]: bad += 1
print('Corrupted/invalid options:', bad)

print('Per-skill:', dict(Counter(q['skill'] for q in merged)))
print('qa_status:', dict(Counter(q.get('qa_status') for q in merged)))

json.dump({'questions': merged, 'meta': {'note': 'Production bank v2; base keeps original ids for image linkage; 9 skills regenerated', 'count': len(merged)}},
          open('brainactive_p3_question_bank_production.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE brainactive_p3_question_bank_production.json (UTF-8)')
