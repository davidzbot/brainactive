import json, os, re, glob

rows = json.load(open('import_questions.json', encoding='utf-8'))
req = ['id','domain','topic','skill','archetype','level','difficulty','question_type',
       'question','options','answer','explanation','tags','visual_required','image_path','is_active']
miss = [r['id'] for r in rows if any(k not in r for k in req)]
empty = [r['id'] for r in rows if not r['question'] or not r['answer'] or not r['explanation']]
bad = 0
for r in rows:
    ids = [o['id'] for o in r['options']]
    if set(ids) != {'A','B','C','D'}: bad += 1; continue
    if r['answer'] not in ids: bad += 1
    if not all('text' in o for o in r['options']): bad += 1
print('Rows:', len(rows), '| missing col:', len(miss), '| empty core:', len(empty), '| bad opts/ans:', bad)

lines = [l.strip() for l in open('upload_images.bat', encoding='utf-8') if l.strip()]
missingfiles = 0
for l in lines:
    m = re.search(r'"([^"]+)"', l)
    if m and not os.path.exists(m.group(1)):
        missingfiles += 1
print('image batch lines:', len(lines), '| missing files:', missingfiles)

# verify every visual_required row has an image_path and a real file
present = set(os.path.splitext(os.path.basename(f))[0] for ext in ('svg','png') for f in glob.glob('images/*.'+ext))
vis = [r for r in rows if r['visual_required']]
vis_ok = [r for r in vis if r['image_path'] and r['id'] in present]
print('visual_required:', len(vis), '| with image_path+file:', len(vis_ok), '| broken:', len(vis)-len(vis_ok))
