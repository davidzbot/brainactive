import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open(r'C:\Projects\brainactive-android\revamp\bank\new_600\brainactive_new_600_20260905.json', encoding='utf-8') as f:
    data = json.load(f)

# Check image paths
vis = [q for q in data['questions'] if q.get('image_path')]
print(f"Questions with image_path: {len(vis)}")
for q in vis:
    print(f"  {q['id']}: {q['image_path']}")

# Check non-ASCII
non_ascii = 0
for q in data['questions']:
    for c in q.get('explanation', ''):
        if ord(c) > 127:
            non_ascii += 1
            break
print(f"\nQuestions with non-ASCII in explanation: {non_ascii}")

# Sample a few explanations to verify clean encoding
print("\nSample explanations:")
for q in data['questions'][4509:4515]:
    print(f"  {q['id']}: {q['explanation'][:100]}")
