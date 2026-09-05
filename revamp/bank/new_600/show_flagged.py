import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open(r'C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_20260905.json', encoding='utf-8') as f:
    data = json.load(f)

ids = ['NEW_SOL_021','NEW_SOL_022','NEW_SOL_023','NEW_SOL_025','NEW_SOL_046','NEW_VER_008']
for q in data['questions']:
    if q['id'] in ids:
        print(f"--- {q['id']} ---")
        print(f"Q: {q['question']}")
        for o in q['options']:
            print(f"  {o['id']}: {o['text']}")
        print(f"Answer: {q['answer']}")
        print(f"Explanation: {q['explanation']}")
        print()
