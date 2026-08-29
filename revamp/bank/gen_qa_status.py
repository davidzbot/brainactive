import json

d = json.load(open(r'C:\Projects\brainactive-android\revamp\bank\brainactive_p3_question_bank_production.json', encoding='utf-8'))
qs = d['questions']
rows = []
for q in qs:
    i = q['id']
    s = q.get('qa_status') or 'NULL'
    # id and status are safe identifiers (alnum/_); no embedded quotes
    rows.append("('%s', '%s')" % (i, s))

vals = ',\n'.join(rows)
sql = 'ALTER TABLE public.brainactive_questions ADD COLUMN IF NOT EXISTS qa_status text;\n'
sql += 'UPDATE public.brainactive_questions AS t SET qa_status = v.s\n'
sql += 'FROM (VALUES\n' + vals + '\n) AS v(id, s)\nWHERE t.id = v.id;\n'

out = r'C:\Projects\brainactive-android\revamp\bank\add_qa_status.sql'
open(out, 'w', encoding='utf-8').write(sql)
print('wrote', out, 'with', len(rows), 'value rows')
