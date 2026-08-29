import json, os

bank = r'C:\Projects\brainactive-android\revamp\bank\brainactive_p3_question_bank_production.json'
imgdir = r'C:\Projects\brainactive-android\revamp\bank\images'
out = r'C:\Projects\brainactive-android\revamp\bank\upload_list.json'

d = json.load(open(bank, encoding='utf-8'))
qs = d['questions']
items = []
missing = []
for q in qs:
    if q.get('visual_required') and q.get('image_path'):
        ip = q['image_path']                 # e.g. p3/BA_P3_0017.svg
        base = os.path.basename(ip)
        local = os.path.join(imgdir, base)
        if os.path.exists(local):
            items.append({'local': local, 'dest': ip})
        else:
            missing.append(local)

json.dump(items, open(out, 'w', encoding='utf-8'), indent=0)
print('upload items:', len(items), '| missing:', len(missing))
for m in missing[:10]:
    print('  MISSING', m)
