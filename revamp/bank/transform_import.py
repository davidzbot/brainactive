import json, re, glob, os
from collections import Counter

prod = json.load(open('brainactive_p3_question_bank_production.json', encoding='utf-8'))['questions']

DOMAIN_TOPIC = {
    'numerical_reasoning': 'Numerical Thinking',
    'logical_reasoning': 'Logical Thinking',
    'pattern_abstract': 'Pattern & Abstract',
    'visual_spatial': 'Visual & Spatial',
    'verbal_reasoning': 'Verbal Reasoning',
    'problem_solving': 'Problem Solving',
}

def esc(s):
    return str(s).replace("'", "''")

rows = []
val_errors = []
for q in prod:
    dom = q['domain']
    if dom not in DOMAIN_TOPIC:
        val_errors.append(('bad_domain', q['id'], dom)); continue
    topic = DOMAIN_TOPIC[dom]
    opts = q['options']
    if len(opts) != 4 or len(set(o['id'] for o in opts)) != 4:
        val_errors.append(('bad_options', q['id'])); continue
    if q['answer'] not in [o['id'] for o in opts]:
        val_errors.append(('answer_not_in_options', q['id'])); continue
    vs = q.get('visual_spec')
    vs_sql = ("'%s'::jsonb" % json.dumps(vs, ensure_ascii=False).replace("'", "''")) if vs else 'NULL'
    img = q.get('image_path')
    img_sql = ("'%s'" % esc(img)) if img else 'NULL'
    tags = q.get('tags') or []
    tags_sql = "ARRAY[%s]" % ",".join("'%s'" % esc(t) for t in tags) if tags else "ARRAY[]::text[]"
    is_active = False  # candidate import; not served until reviewed/activated
    rows.append({
        'id': q['id'],
        'domain': dom,
        'topic': topic,
        'skill': q['skill'],
        'archetype': q.get('archetype',''),
        'level': q['level'],
        'difficulty': q['difficulty'],
        'question_type': q.get('question_type','multiple_choice'),
        'question': q['question'],
        'options': opts,
        'answer': q['answer'],
        'explanation': q['explanation'],
        'reasoning': q.get('reasoning') or '',
        'tags': tags,
        'visual_required': bool(q.get('visual_required')),
        'visual_spec': vs,
        'image_path': img,
        'is_active': is_active,
        'qa_status': q.get('qa_status'),
    })

print('Transformed rows:', len(rows), '| validation errors:', len(val_errors))
for e in val_errors[:20]:
    print('  ', e)

# Save canonical JSON
json.dump(rows, open('import_questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE import_questions.json')

# Generate SQL INSERTs
sql_lines = []
sql_lines.append("-- BrainActive candidate questions import (candidates; is_active=FALSE).")
sql_lines.append("-- Run AFTER 20260829000000_brainactive_schema.sql has created the tables.\n")
for r in rows:
    opts_json = json.dumps(r['options'], ensure_ascii=False).replace("'", "''")
    vs_sql = ("'%s'::jsonb" % json.dumps(r['visual_spec'], ensure_ascii=False).replace("'", "''")) if r['visual_spec'] else 'NULL'
    img_sql = ("'%s'" % esc(r['image_path'])) if r['image_path'] else 'NULL'
    tags_sql = "ARRAY[%s]" % ",".join("'%s'" % esc(t) for t in r['tags']) if r['tags'] else "ARRAY[]::text[]"
    sql = (
        "INSERT INTO public.brainactive_questions "
        "(id, domain, topic, skill, archetype, level, difficulty, question_type, question, options, answer, explanation, reasoning, tags, visual_required, visual_spec, image_path, is_active) VALUES ("
        f"'{esc(r['id'])}', '{esc(r['domain'])}', '{esc(r['topic'])}', '{esc(r['skill'])}', '{esc(r['archetype'])}', "
        f"'{esc(r['level'])}', '{esc(r['difficulty'])}', '{esc(r['question_type'])}', '{esc(r['question'])}', "
        f"'{opts_json}'::jsonb, '{esc(r['answer'])}', '{esc(r['explanation'])}', '{esc(r['reasoning'])}', "
        f"{tags_sql}, {str(r['visual_required']).lower()}, {vs_sql}, {img_sql}, {str(r['is_active']).lower()});"
    )
    sql_lines.append(sql)
open('import_questions.sql', 'w', encoding='utf-8').write("\n".join(sql_lines))
print('WROTE import_questions.sql (%d inserts)' % len(rows))

# Image upload batch (supabase CLI)
img_lines = []
present = set(os.path.splitext(os.path.basename(f))[0] for ext in ('svg','png') for f in glob.glob('images/*.'+ext))
for r in rows:
    if r['visual_required'] and r['id'] in present:
        fn = None
        for ext in ('svg','png'):
            p = 'images/%s.%s' % (r['id'], ext)
            if os.path.exists(p):
                fn = p; break
        if fn:
            img_lines.append('supabase storage upload brainactive-assets "%s" "p3/%s"' % (fn, os.path.basename(fn)))
open('upload_images.bat', 'w', encoding='utf-8').write("\n".join(img_lines))
print('WROTE upload_images.bat (%d image uploads)' % len(img_lines))

# Summary
print('Topic dist:', dict(Counter(r['topic'] for r in rows)))
print('is_active all FALSE:', all(not r['is_active'] for r in rows))
