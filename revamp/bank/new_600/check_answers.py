import json
from collections import Counter

with open(r'C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_20260905.json', encoding='utf-8') as f:
    data = json.load(f)

# Check answer distribution for ALL domains
print("=== ANSWER DISTRIBUTION BY DOMAIN ===")
for domain in ["numerical_reasoning", "logical_reasoning", "pattern_abstract", "visual_spatial", "verbal_reasoning", "problem_solving"]:
    qs = [q for q in data['questions'] if q['domain'] == domain]
    answers = Counter(q['answer'] for q in qs)
    print(f"{domain}: {len(qs)} questions, answers: {dict(answers)}")

# Deep dive into numerical - show all answers in order
print("\n=== NUMERICAL SECTION - ALL ANSWERS IN ORDER ===")
num_qs = [q for q in data['questions'] if q['domain'] == 'numerical_reasoning']
for q in num_qs:
    opts = {o['id']: o['text'] for o in q['options']}
    print(f"{q['id']}: ans={q['answer']} ({opts[q['answer']]}), diff={q['difficulty']}, skill={q['skill']}")
